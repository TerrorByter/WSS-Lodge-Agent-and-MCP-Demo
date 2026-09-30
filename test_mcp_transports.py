"""The same Flight MCP server must work over stdio (local) and streamable HTTP (Railway / Hermes)."""
import asyncio, json, os, socket, subprocess, sys, time
from contextlib import AsyncExitStack
from pathlib import Path

import pytest
from mcp_agent import connect_servers

ROOT = Path(__file__).parent


@pytest.fixture(autouse=True)
def _in_project_dir(monkeypatch):
    monkeypatch.chdir(ROOT)   # mcp_config.json launches "flight_mcp_server.py" relative to here


@pytest.fixture
def http_config(tmp_path):
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        port = s.getsockname()[1]
    env = {**os.environ, "MCP_TRANSPORT": "streamable-http", "PORT": str(port)}
    server = subprocess.Popen([sys.executable, "flight_mcp_server.py"], env=env,
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        for _ in range(100):
            try:
                socket.create_connection(("127.0.0.1", port), timeout=0.1).close()
                break
            except OSError:
                time.sleep(0.1)
        else:
            pytest.fail("HTTP server did not start")
        config = tmp_path / "http_config.json"
        config.write_text(json.dumps({"mcpServers": {"flight-sim": {"url": f"http://127.0.0.1:{port}/mcp"}}}))
        yield str(config)
    finally:
        server.terminate()
        server.wait()


@pytest.fixture(params=["stdio", "http"])
def config_path(request):
    return "mcp_config.json" if request.param == "stdio" else request.getfixturevalue("http_config")


def test_python_command_does_not_need_python_on_path(monkeypatch, tmp_path):
    monkeypatch.setenv("PATH", str(tmp_path))   # e.g. a Mac with only python3, or a venv kernel that isn't on PATH

    async def scenario():
        async with AsyncExitStack() as stack:
            _, tools = await connect_servers(stack, "mcp_config.json")
            assert {t["name"] for t in tools} == {"search_flights", "book_flight"}
    asyncio.run(scenario())


def test_discover_search_and_book(config_path):
    async def scenario():
        async with AsyncExitStack() as stack:
            sessions, tools = await connect_servers(stack, config_path)
            assert {t["name"] for t in tools} == {"search_flights", "book_flight"}
            found = await sessions["search_flights"].call_tool(
                "search_flights", {"origin": "SFO", "destination": "JFK"})
            prices = [json.loads(c.text)["price_usd"] for c in found.content]
            assert prices == sorted(prices)                    # cheapest first, even with the Part 7 airline enabled
            assert any("AG91" in c.text for c in found.content)
            booked = await sessions["book_flight"].call_tool(
                "book_flight", {"airline": "Joy Air", "flight": "JA205", "passenger_name": "Jane Tan"})
            assert "JOY-JA205-7431" in booked.content[0].text
    asyncio.run(scenario())
