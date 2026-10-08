import asyncio
from typing import get_args

from fastmcp import Client

from server import DOCS, Topic, mcp


async def main():
    topics = set(get_args(Topic))
    on_disk = {str(p.relative_to(DOCS).with_suffix("")) for p in DOCS.rglob("*.md")}
    assert topics == on_disk, f"Topic enum and docs/ differ: {topics ^ on_disk}"

    async with Client(mcp) as client:
        names = {t.name for t in await client.list_tools()}
        assert names == {"start_trivia_integration", "get_doc", "list_instances", "get_instance_details", "get_questions"}, names
        start = (await client.call_tool("start_trivia_integration", {})).content[0].text
        assert "clientId" in start and "gameId" in start
        for t in topics:
            assert (await client.call_tool("get_doc", {"topic": t})).content[0].text.strip(), t
    print(f"ok: {len(topics)} docs, {len(names)} tools")


asyncio.run(main())
