import os
from typing import Any

from anthropic import Anthropic
from dotenv import load_dotenv

from client import call_tool

MODEL_NAME = "claude-opus-4-6"

SYSTEM_PROMPT = (
    "You are a GitHub MCP assistant. Use tools when needed to answer questions about repositories, "
    "files, and code. If a tool is needed, call it with valid JSON input."
)

TOOLS = [
    {
        "name": "list_repos",
        "description": "List all public repositories for the configured GitHub owner.",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": [],
            "additionalProperties": False,
        },
    },
    {
        "name": "list_files",
        "description": "List files and folders at a given path in a repository.",
        "input_schema": {
            "type": "object",
            "properties": {
                "repo_name": {"type": "string", "description": "Repository name."},
                "path": {
                    "type": "string",
                    "description": "Optional path inside the repo.",
                    "default": "",
                },
            },
            "required": ["repo_name"],
            "additionalProperties": False,
        },
    },
    {
        "name": "list_all_files",
        "description": "List all files recursively in a repository.",
        "input_schema": {
            "type": "object",
            "properties": {
                "repo_name": {"type": "string", "description": "Repository name."}
            },
            "required": ["repo_name"],
            "additionalProperties": False,
        },
    },
    {
        "name": "read_file",
        "description": "Read the contents of a file from a repository.",
        "input_schema": {
            "type": "object",
            "properties": {
                "repo_name": {"type": "string", "description": "Repository name."},
                "path": {"type": "string", "description": "Path to a file in the repo."},
            },
            "required": ["repo_name", "path"],
            "additionalProperties": False,
        },
    },
    {
        "name": "search_code",
        "description": "Search for a keyword across repository files.",
        "input_schema": {
            "type": "object",
            "properties": {
                "repo_name": {"type": "string", "description": "Repository name."},
                "keyword": {"type": "string", "description": "Search keyword."},
            },
            "required": ["repo_name", "keyword"],
            "additionalProperties": False,
        },
    },
    {
        "name": "summarize_repo",
        "description": "Summarize a repository including top-level content and README preview.",
        "input_schema": {
            "type": "object",
            "properties": {
                "repo_name": {"type": "string", "description": "Repository name."}
            },
            "required": ["repo_name"],
            "additionalProperties": False,
        },
    },
]


def _content_to_message_blocks(content_blocks: list[Any]) -> list[dict[str, Any]]:
    blocks: list[dict[str, Any]] = []
    for block in content_blocks:
        if block.type == "text":
            blocks.append({"type": "text", "text": block.text})
        elif block.type == "tool_use":
            blocks.append(
                {
                    "type": "tool_use",
                    "id": block.id,
                    "name": block.name,
                    "input": block.input,
                }
            )
    return blocks


def run_agent_turn(user_query: str, conversation_history: list[dict[str, Any]], client: Anthropic) -> str:
    conversation_history.append({"role": "user", "content": user_query})

    while True:
        response = client.messages.create(
            model=MODEL_NAME,
            max_tokens=1200,
            system=SYSTEM_PROMPT,
            tools=TOOLS,
            messages=conversation_history,
        )

        conversation_history.append(
            {
                "role": "assistant",
                "content": _content_to_message_blocks(response.content),
            }
        )

        if response.stop_reason == "tool_use":
            tool_result_blocks = []
            for block in response.content:
                if block.type != "tool_use":
                    continue

                tool_name = block.name
                tool_args = block.input if isinstance(block.input, dict) else {}
                print(f"\n[tool] Calling {tool_name} with args={tool_args}")

                try:
                    tool_output = call_tool(tool_name, tool_args)
                except Exception as exc:
                    tool_output = f"Tool execution error: {exc}"

                tool_result_blocks.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": str(tool_output),
                    }
                )

            conversation_history.append({"role": "user", "content": tool_result_blocks})
            continue

        if response.stop_reason == "end_turn":
            text_parts = [block.text for block in response.content if block.type == "text"]
            return "\n".join(text_parts).strip() or "(No response.)"

        text_parts = [block.text for block in response.content if block.type == "text"]
        return "\n".join(text_parts).strip() or "(No response.)"


def main() -> None:
    load_dotenv()

    if not os.getenv("ANTHROPIC_API_KEY"):
        print("Set ANTHROPIC_API_KEY in your environment or .env before running this script.")
        return

    client = Anthropic()
    conversation_history: list[dict[str, Any]] = []

    print("GitHub MCP Agent Assistant")
    print("Type 'exit' to quit.\n")

    while True:
        user_query = input("You: ").strip()
        if user_query.lower() == "exit":
            print("Bye!")
            break

        if not user_query:
            continue

        try:
            answer = run_agent_turn(user_query, conversation_history, client)
            print(f"\nAssistant: {answer}\n")
        except KeyboardInterrupt:
            print("\nInterrupted.")
            break
        except Exception as exc:
            print(f"\nAssistant error: {exc}\n")


if __name__ == "__main__":
    main()
