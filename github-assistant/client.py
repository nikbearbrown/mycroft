import subprocess
import json


def _extract_text(value):
    if isinstance(value, str):
        return value

    if isinstance(value, list):
        parts = [_extract_text(item) for item in value]
        return "\n".join(part for part in parts if part)

    if isinstance(value, dict):
        if isinstance(value.get("text"), str):
            return value["text"]

        for key in ("result", "content", "data", "value"):
            if key in value:
                extracted = _extract_text(value[key])
                if extracted:
                    return extracted

        return json.dumps(value)

    return str(value)


def _parse_json_maybe(output):
    output = output.strip()

    try:
        return json.loads(output)
    except json.JSONDecodeError:
        start = output.find("{")
        end = output.rfind("}")
        if start != -1 and end != -1 and end > start:
            try:
                return json.loads(output[start:end + 1])
            except json.JSONDecodeError:
                return None
        return None


def call_tool(tool_name, args=None):
    if args is None:
        args = {}

    if not isinstance(args, dict):
        return "Internal error: tool arguments must be a dictionary."

    command = [
        "fastmcp",
        "call",
        "--server-spec",
        "server.py",
        "--target",
        tool_name,
        "--input-json",
        json.dumps(args),
        "--json",
    ]

    result = subprocess.run(command, capture_output=True, text=True)
    output = result.stdout.strip() if result.stdout else result.stderr.strip()
    parsed = _parse_json_maybe(output)

    if parsed is None:
        return output.strip()

    if result.returncode != 0:
        error_text = _extract_text(parsed)
        return error_text.strip() if error_text else output.strip()

    result_text = _extract_text(parsed)
    return result_text.strip() if result_text else "No response."


def print_pretty_response(text):
    if not text:
        print("\nBot:\nNo response.")
        return

    lines = text.split("\n")
    print("\nBot:")
    for line in lines:
        if line.strip():
            print(f"- {line}")


def print_help():
    print("\nBot:")
    print("- list repos")
    print("- select repo <repo_name>")
    print("- current repo")
    print("- list files")
    print("- list all files")
    print("- read file <file_path>")
    print("- search code <keyword>")
    print("- summarize repo")
    print("- exit")


def main():
    selected_repo = None

    print("GitHub MCP Assistant 🚀")
    print("Type 'exit' anytime to quit.\n")

    while True:
        if not selected_repo:
            print("\nBot: Let's start by selecting a repository.")
            print("Bot: Fetching your repos...\n")

            repos = call_tool("list_repos")
            repo_list = repos.split("\n")

            for i, repo in enumerate(repo_list, 1):
                print(f"{i}. {repo}")

            user_input = input("\nEnter repo name: ").strip()

            if user_input.lower() == "exit":
                print("Bye!")
                break

            selected_repo = user_input
            print(f"\nBot: Selected repo → {selected_repo}")

        else:
            print(f"\nBot: You are working with '{selected_repo}'")
            print("What do you want to do?")
            print("1. List files")
            print("2. List all files")
            print("3. Read a file")
            print("4. Search code")
            print("5. Summarize repo")
            print("6. Change repo")
            print("7. Exit")

            choice = input("\nEnter choice (1-7): ").strip()

            if choice == "1":
                response = call_tool("list_files", {"repo_name": selected_repo})
                print_pretty_response(response)

            elif choice == "2":
                response = call_tool("list_all_files", {"repo_name": selected_repo})
                print_pretty_response(response)

            elif choice == "3":
                path = input("Enter file path (e.g. README.md): ").strip()
                response = call_tool("read_file", {"repo_name": selected_repo, "path": path})
                print_pretty_response(response)

            elif choice == "4":
                keyword = input("Enter keyword: ").strip()
                response = call_tool("search_code", {"repo_name": selected_repo, "keyword": keyword})
                print_pretty_response(response)

            elif choice == "5":
                response = call_tool("summarize_repo", {"repo_name": selected_repo})
                print_pretty_response(response)

            elif choice == "6":
                selected_repo = None

            elif choice == "7" or choice.lower() == "exit":
                print("Bye!")
                break

            else:
                print("Invalid choice. Try again.")


if __name__ == "__main__":
    main()
