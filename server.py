"""LiveLike Trivia MCP server.

Static docs (docs/*.md) tell a client AI how to build a trivia game end to end.
Three read-only live tools let it inspect a client's real CMS config and questions.
"""

import json
from pathlib import Path
from typing import Literal

import httpx
from fastmcp import FastMCP
from fastmcp.exceptions import ToolError

DOCS = Path(__file__).parent / "docs"

ENVS = {
    "production": {
        "arcade": "https://arcade-backend.livelikecdn.com",
        "livelike": "https://cf-blast.livelikecdn.com/api/v1/",
    },
    "staging": {
        "arcade": "https://arcade-staging-backend.livelikecdn.com",
        "livelike": "https://cf-blast-staging.livelikecdn.com/api/v1/",
    },
}
Env = Literal["production", "staging"]

Topic = Literal[
    "overview",
    "integration-questions",
    "sdk-init",
    "flow",
    "instance-resolution",
    "data-merge",
    "live-trivia",
    "apis/instance-list",
    "apis/instance-details",
    "apis/program-widgets",
    "apis/widget-interactions",
    "apis/widget-impression",
    "apis/submit-interaction",
    "apis/trivia-credit",
    "apis/game-completed",
    "screens/welcome",
    "screens/game",
    "screens/result",
]

mcp = FastMCP(
    "livelike-trivia",
    instructions=(
        "Builds a LiveLike Trivia game in the user's app. Always call start_trivia_integration first, "
        "ask the user the listed questions, then read the docs it points to with get_doc. "
        "Theming is out of scope: style the game natively in the user's app."
    ),
)


def read_doc(topic: str) -> str:
    return (DOCS / f"{topic}.md").read_text()


@mcp.tool
def start_trivia_integration() -> str:
    """START HERE. Returns the trivia overview, the questions you must ask the user before
    building (required IDs, welcome screen, score display, review, share), the end-to-end flow,
    and the list of doc topics to read next with get_doc."""
    return "\n\n---\n\n".join(read_doc(t) for t in ("overview", "integration-questions", "flow"))


@mcp.tool
def get_doc(topic: Topic) -> str:
    """Return one documentation page: SDK init, an API reference (apis/*), a screen spec
    (screens/*), data merge rules, instance resolution or live trivia timing."""
    return read_doc(topic)


async def get_json(url: str, headers: dict | None = None) -> dict:
    async with httpx.AsyncClient(timeout=20) as client:
        res = await client.get(url, headers=headers)
    if res.status_code >= 400:
        raise ToolError(f"GET {url} failed with {res.status_code}: {res.text[:300]}")
    return res.json()


def strip_whitelabel(instance: dict) -> dict:
    # Theme + translations are the client's job; keep them out of the AI's context.
    return {k: v for k, v in instance.items() if k != "whitelabel"}


@mcp.tool
async def list_instances(client_id: str, game_id: str, access_token: str, env: Env = "production") -> list[dict]:
    """Live, read-only. List every trivia instance of a game (theme removed), sorted by
    setting.schedule.publish_time. access_token is a LiveLike profile access token."""
    url = f"{ENVS[env]['arcade']}/v2/minigames/instances/{game_id}/list/?application_id={client_id}&all=yes"
    data = await get_json(url, {"Authorization": access_token})
    instances = [strip_whitelabel(i) for i in data.get("results", [])]
    return sorted(instances, key=lambda i: (i.get("setting") or {}).get("schedule", {}).get("publish_time") or "")


@mcp.tool
async def get_instance_details(client_id: str, game_id: str, instance_id: str, env: Env = "production") -> dict:
    """Live, read-only. Fetch one instance's CMS config (theme removed): program_id,
    setting.welcome, setting.results, setting.schedule."""
    url = f"{ENVS[env]['arcade']}/v2/minigames/{game_id}/{instance_id}/?application_id={client_id}"
    return strip_whitelabel(await get_json(url))


@mcp.tool
async def get_questions(program_id: str, env: Env = "production") -> list[dict]:
    """Live, read-only. Fetch the trivia questions (text-quiz widgets) of a program, with
    custom_data parsed from its JSON string and sorted by custom_data.sort_id."""
    data = await get_json(f"{ENVS[env]['livelike']}programs/{program_id}/widgets/?page_size=100")
    questions = data.get("results", [])
    for q in questions:
        if isinstance(q.get("custom_data"), str):
            q["custom_data"] = json.loads(q["custom_data"])
    return sorted(questions, key=lambda q: (q.get("custom_data") or {}).get("sort_id", 0))


# Vercel (and any ASGI host) serves this; serverless has no sticky sessions, so stateless.
app = mcp.http_app(stateless_http=True, json_response=True)

if __name__ == "__main__":
    mcp.run()
