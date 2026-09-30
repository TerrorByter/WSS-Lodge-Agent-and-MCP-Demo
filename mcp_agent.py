"""WITH MCP: the agent has an MCP *client*. It reads mcp_config.json, launches each server,
DISCOVERS the tools (names, inputs) from the server, and hands them to Claude. No per-airline code."""
import asyncio, json, sys
from contextlib import AsyncExitStack
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.client.streamable_http import create_mcp_http_client, streamable_http_client
from llm import client, MODEL

NEEDS_APPROVAL = {"book_flight"}   # side-effecting tools: a human must say yes


async def connect_servers(stack, config_path="mcp_config.json"):
    """Connect to every server in the config: launch it ("command") or dial it ("url", like Hermes' config).
    Returns {tool_name: session} and Claude-format tool schemas."""
    config = json.load(open(config_path))["mcpServers"]
    sessions, tools = {}, []
    for name, spec in config.items():
        if "url" in spec:
            http = await stack.enter_async_context(create_mcp_http_client(spec.get("headers")))
            read, write, _ = await stack.enter_async_context(streamable_http_client(spec["url"], http_client=http))
        else:
            command = sys.executable if spec["command"] == "python" else spec["command"]   # same interpreter as us, wherever it lives
            params = StdioServerParameters(command=command, args=spec.get("args", []))
            read, write = await stack.enter_async_context(stdio_client(params))
        session = await stack.enter_async_context(ClientSession(read, write))
        await session.initialize()
        for t in (await session.list_tools()).tools:          # <-- discovery
            sessions[t.name] = session
            tools.append({"name": t.name, "description": t.description, "input_schema": t.inputSchema})
    return sessions, tools


async def run_agent(task, config_path="mcp_config.json", max_steps=8):
    async with AsyncExitStack() as stack:
        sessions, tools = await connect_servers(stack, config_path)
        print("Discovered tools:", [t["name"] for t in tools])
        messages = [{"role": "user", "content": task}]

        for step in range(max_steps):
            kwargs = {"tools": tools} if tools else {}   # no servers configured -> no tools
            r = client.messages.create(model=MODEL, max_tokens=1024, messages=messages, **kwargs)
            if r.stop_reason != "tool_use":
                return "".join(b.text for b in r.content if b.type == "text")

            messages.append({"role": "assistant", "content": r.content})
            results = []
            for b in r.content:
                if b.type != "tool_use":
                    continue
                print(f"[step {step}] {b.name}({b.input})")
                if b.name in NEEDS_APPROVAL and input("  approve? [y/N] ").lower() != "y":
                    out = "Human declined."
                else:
                    res = await sessions[b.name].call_tool(b.name, b.input)
                    out = "".join(c.text for c in res.content if c.type == "text")
                results.append({"type": "tool_result", "tool_use_id": b.id, "content": out})
            messages.append({"role": "user", "content": results})
        return "Max steps reached."


if __name__ == "__main__":
    config = sys.argv[1] if len(sys.argv) > 1 else "mcp_config.json"   # e.g. python mcp_agent.py empty_config.json
    print(asyncio.run(run_agent(
        "Find flights from SFO to JFK and book the cheapest one for Jane Tan.", config)))
