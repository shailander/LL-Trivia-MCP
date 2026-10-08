# LiveLike Trivia MCP

An MCP server that gives an AI coding assistant everything it needs to build a LiveLike Trivia game in your
app: which APIs to call and when, what they return, how to initialise the LiveLike SDK, and how the
welcome, game and result screens behave.

You provide your **clientId** and **gameId** (and optionally an **instanceId** or **accessToken**), and answer a few
questions about the screens you want. The AI builds the game. Your CMS configuration drives the behaviour.
Theming is up to you: the docs deliberately leave out styling.

## Requirements

- [uv](https://docs.astral.sh/uv/) (it installs Python 3.10+ and the dependencies for you)

```bash
brew install uv        # or: curl -LsSf https://astral.sh/uv/install.sh | sh
```

## Run it

From this folder:

```bash
uv sync                                  # install dependencies (first time only)
uv run python test_server.py             # self-check: prints "ok: 18 docs, 5 tools"
uv run fastmcp dev server.py             # open the MCP Inspector in the browser to try the tools
```

You don't normally need to start the server yourself. Your AI client starts it (see below).

## Connect it to your AI client

In the examples below, replace `/path/to/trivia` with the absolute path to this folder.

### Claude Code

```bash
claude mcp add livelike-trivia -- uv run --directory /path/to/trivia python server.py
```

Check it with `claude mcp list`, or `/mcp` inside a session.

### Claude Desktop

Edit `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) or
`%APPDATA%\Claude\claude_desktop_config.json` (Windows), then restart Claude Desktop:

```json
{
  "mcpServers": {
    "livelike-trivia": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/trivia", "python", "server.py"]
    }
  }
}
```

### Cursor / VS Code / other MCP clients

Most clients use the same shape. In Cursor it goes in `.cursor/mcp.json`; in VS Code, in `.vscode/mcp.json` (VS Code uses `"servers"` instead of `"mcpServers"`):

```json
{
  "mcpServers": {
    "livelike-trivia": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/trivia", "python", "server.py"]
    }
  }
}
```

If the client can't find `uv`, use its full path (`which uv`).

### As a shared HTTP server (optional)

Run it once and let several people or clients connect over HTTP:

```bash
uv run fastmcp run server.py:mcp --transport http --host 0.0.0.0 --port 8000
```

Clients connect to `http://<host>:8000/mcp`. For example, in Claude Code:

```bash
claude mcp add --transport http livelike-trivia http://localhost:8000/mcp
```

The server has no authentication. Don't expose it on the public internet as-is.

## Use it

Once connected, ask your assistant something like:

> Integrate LiveLike trivia into this app. clientId `abc123`, gameId `xyz789`.

The assistant then:
1. calls `start_trivia_integration` and asks you about the welcome screen, feedback and points after each
   answer, final points, answer review and sharing,
2. optionally inspects your real CMS data with the live tools,
3. reads the relevant docs and builds the welcome → game → result flow.

## Tools

| Tool | What it does |
|---|---|
| `start_trivia_integration()` | Entry point: overview, the questions to ask you, end-to-end flow, list of doc topics |
| `get_doc(topic)` | Returns one doc page (SDK init, an API reference, a screen spec, …) |
| `list_instances(client_id, game_id, access_token, env)` | Live, read-only: the game's trivia instances (theme removed) |
| `get_instance_details(client_id, game_id, instance_id, env)` | Live, read-only: one instance's CMS settings and `program_id` |
| `get_questions(program_id, env)` | Live, read-only: the questions, parsed and sorted |

`env` is `production` (default) or `staging`. The live tools never write anything. Submitting answers
and the credit and game-completed calls are documented, but your app makes those calls itself.

## Project layout

```
server.py            all tools
docs/                the static documentation the tools return
  overview.md, integration-questions.md, sdk-init.md, flow.md,
  instance-resolution.md, data-merge.md, live-trivia.md
  apis/              one page per API
  screens/           welcome.md, game.md, result.md
test_server.py       self-check
```

## Editing the docs

The docs are plain Markdown and the tools serve them as-is, so editing a file is enough. To add a page,
create `docs/<topic>.md` and add `"<topic>"` to the `Topic` list in `server.py`. Then run
`uv run python test_server.py`, which fails if the list and the files disagree.

## Troubleshooting

| Problem | Fix |
|---|---|
| Client shows the server as failed or disconnected | Run `uv run --directory /path/to/trivia python server.py` in a terminal to see the error. Use absolute paths. |
| `uv: command not found` in the client | Use the full path to `uv` in `command`. |
| Live tool returns `... failed with 404` | Wrong `client_id`/`game_id`/`instance_id`, or the wrong `env` (staging vs production). |
| Live tool returns `401`/`403` on `list_instances` | `access_token` must be a valid LiveLike profile token for that client. |
