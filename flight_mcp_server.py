"""A Flight MCP server. It hides the three different airline APIs behind ONE standard interface.
Any MCP client (our agent, Claude Desktop, Cursor, Cline...) can discover and call these tools."""
import os
from mcp.server.fastmcp import FastMCP
import airlines

# Local default is stdio. On Railway set MCP_TRANSPORT=streamable-http and MCP_HOST=0.0.0.0 (it injects PORT).
mcp = FastMCP("flight-sim", host=os.environ.get("MCP_HOST", "127.0.0.1"), port=int(os.environ.get("PORT", 8000)))


@mcp.tool()
def search_flights(origin: str, destination: str) -> list[dict]:
    """Search Joy Air, Dra Air and Aeroggo for flights. Returns one normalised list."""
    results = []
    for f in airlines.joyair_api_flights(origin, destination):
        results.append({"airline": "Joy Air", "flight": f["flight_number"], "price_usd": f["price_usd"]})
    for f in airlines.draair_flights_list(origin, destination)["results"]:
        results.append({"airline": "Dra Air", "flight": f["flightNo"], "price_usd": f["fare"]["amount"]})
    for f in airlines.aeroggo_list_flights(origin, destination)["detailedFlights"]:
        results.append({"airline": "Aeroggo", "flight": f["flight"], "price_usd": f["cost"]})
    # # EXERCISE (Part 7): to include SkyBee, enable airlines.py first, then select these lines and toggle comments
    # # (Cmd+/ on Mac, Ctrl+/ on Windows). SkyBee prices are in cents, so normalise to dollars. Optionally add
    # # SkyBee to the docstring above: it is the tool description Claude reads.
    # for f in airlines.skybee_find(origin, destination)["trips"]:
    #     results.append({"airline": "SkyBee", "flight": f["id"], "price_usd": f["usd_cents"] / 100})
    return sorted(results, key=lambda r: r["price_usd"])


@mcp.tool()
def book_flight(airline: str, flight: str, passenger_name: str) -> dict:
    """Book a flight. Needs the airline and flight from search_flights, plus the passenger's full name."""
    if airline == "Joy Air":
        ref = airlines.joyair_api_book(flight, passenger_name)["booking_ref"]
    elif airline == "Dra Air":
        ref = airlines.draair_reserve(flight, passenger_name)["reservation"]["code"]
    elif airline == "Aeroggo":
        ref = airlines.aeroggo_book(flight, passenger_name)["confirmation"]
    # # EXERCISE (Part 7): to book SkyBee flights, select these lines and toggle comments (Cmd+/ or Ctrl+/).
    # elif airline == "SkyBee":
    #     ref = airlines.skybee_book(flight, passenger_name)["ticket"]
    else:
        return {"error": f"Unknown airline {airline!r}"}
    return {"status": "booked", "booking_reference": ref, "passenger": passenger_name}


if __name__ == "__main__":
    # stdio: the client launches this script and talks to it. streamable-http: the client connects to a URL.
    mcp.run(transport=os.environ.get("MCP_TRANSPORT", "stdio"))
