from fastmcp import FastMCP
import requests
import base64

mcp = FastMCP("GitHub Explorer MCP")

OWNER = "RishikaBhatKuthyar"


def get_base_url(repo_name: str) -> str:
    return f"https://api.github.com/repos/{OWNER}/{repo_name}/contents"


def github_contents(repo_name: str, path: str = ""):
    base_url = get_base_url(repo_name)
    url = base_url if not path else f"{base_url}/{path}"
    response = requests.get(url, timeout=20)

    if response.status_code != 200:
        return None

    return response.json()


def collect_all_files(repo_name: str, path: str = ""):
    data = github_contents(repo_name, path)
    if data is None:
        return []

    all_files = []

    if isinstance(data, dict) and data.get("type") == "file":
        return [data.get("path")]

    for item in data:
        item_type = item.get("type")
        item_path = item.get("path", "")

        if item_type == "file":
            all_files.append(item_path)
        elif item_type == "dir":
            all_files.extend(collect_all_files(repo_name, item_path))

    return all_files


def get_readme_preview(repo_name: str) -> str:
    readme_candidates = ["README.md", "README.MD", "readme.md", "README"]

    for name in readme_candidates:
        content = read_file(repo_name, name)
        if not (
            content.startswith("GitHub API error")
            or content == "Path is not a file."
            or content == "Could not decode file content."
            or content == "Unsupported file encoding."
        ):
            lines = content.splitlines()[:5]
            return "\n".join(lines)

    return "README not found."


@mcp.tool()
def list_repos() -> str:
    """List all public repositories for the GitHub user."""
    url = f"https://api.github.com/users/{OWNER}/repos"
    response = requests.get(url, timeout=20)

    if response.status_code != 200:
        return f"GitHub API error: {response.status_code}"

    data = response.json()
    repo_names = [repo["name"] for repo in data]

    if not repo_names:
        return "No repositories found."

    return "\n".join(sorted(repo_names, key=str.lower))


@mcp.tool()
def list_files(repo_name: str, path: str = "") -> str:
    """List files and folders at a given path inside a GitHub repository."""
    data = github_contents(repo_name, path)

    if data is None:
        return "GitHub API error or repo/path not found."

    if isinstance(data, dict) and data.get("type") == "file":
        return data.get("path", "Single file returned")

    items = []
    for item in data:
        item_type = item.get("type", "unknown")
        item_path = item.get("path", "")
        items.append(f"{item_type}: {item_path}")

    return "\n".join(items) if items else "No files found."


@mcp.tool()
def list_all_files(repo_name: str) -> str:
    """List all files in a GitHub repository recursively."""
    files = collect_all_files(repo_name)

    if not files:
        return "No files found."

    return "\n".join(files)


@mcp.tool()
def read_file(repo_name: str, path: str) -> str:
    """Read the content of a file from a GitHub repository."""
    base_url = get_base_url(repo_name)
    url = f"{base_url}/{path}"
    response = requests.get(url, timeout=20)

    if response.status_code != 200:
        return f"GitHub API error: {response.status_code}"

    data = response.json()

    if data.get("type") != "file":
        return "Path is not a file."

    content = data.get("content", "")
    encoding = data.get("encoding", "")

    if encoding == "base64":
        try:
            return base64.b64decode(content).decode("utf-8")
        except Exception:
            return "Could not decode file content."

    return "Unsupported file encoding."


@mcp.tool()
def search_code(repo_name: str, keyword: str) -> str:
    """Search for a keyword across text files in a GitHub repository."""
    files = collect_all_files(repo_name)
    matches = []

    for path in files:
        content = read_file(repo_name, path)

        if (
            content.startswith("GitHub API error")
            or content == "Path is not a file."
            or content == "Could not decode file content."
            or content == "Unsupported file encoding."
        ):
            continue

        if keyword.lower() in content.lower():
            matches.append(path)

    if not matches:
        return "No matches found."

    return "\n".join(matches)


@mcp.tool()
def summarize_repo(repo_name: str) -> str:
    """Return a basic summary of a GitHub repository."""
    all_files = collect_all_files(repo_name)

    if not all_files:
        return "No files found or repo not accessible."

    root_data = github_contents(repo_name, "")
    top_level_items = []

    if isinstance(root_data, list):
        for item in root_data:
            item_type = item.get("type", "unknown")
            item_path = item.get("path", "")
            top_level_items.append(f"{item_type}: {item_path}")

    readme_preview = get_readme_preview(repo_name)

    summary = [
        f"Repository: {OWNER}/{repo_name}",
        f"Total files: {len(all_files)}",
        "",
        "Top-level contents:",
        "\n".join(top_level_items) if top_level_items else "No top-level items found.",
        "",
        "README preview:",
        readme_preview,
    ]

    return "\n".join(summary)


if __name__ == "__main__":
    mcp.run()