"""Test the MCP server WITHOUT any LLM: connect, discover tools, call them by hand."""
import asyncio
from contextlib import AsyncExitStack
from mcp_agent import connect_servers

async def main():
    async with AsyncExitStack() as stack:
        sessions, tools = await connect_servers(stack)
        for t in tools:
            print(f"TOOL: {t['name']}  inputs: {list(t['input_schema']['properties'])}")
        res = await sessions["search_flights"].call_tool(
            "search_flights", {"origin": "SFO", "destination": "JFK"})
        print("\nSEARCH RESULT (cheapest first):")
        for c in res.content:
            print(" ", c.text.replace("\n", " "))

asyncio.run(main())
