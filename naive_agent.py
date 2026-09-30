"""BEFORE MCP: one hand-written tool per airline. Every new airline means new adapter code."""
import airlines
from llm import client, MODEL

TOOLS = [
    {"name": "joyair_search", "description": "Search Joy Air flights.",
     "input_schema": {"type": "object", "properties": {"origin": {"type": "string"}, "destination": {"type": "string"}},
                      "required": ["origin", "destination"]}},
    {"name": "draair_search", "description": "Search Dra Air flights.",
     "input_schema": {"type": "object", "properties": {"src": {"type": "string"}, "dst": {"type": "string"}},
                      "required": ["src", "dst"]}},
    {"name": "aeroggo_search", "description": "Search Aeroggo flights.",
     "input_schema": {"type": "object", "properties": {"start": {"type": "string"}, "finish": {"type": "string"}},
                      "required": ["start", "finish"]}},
    # ...and 3 more book tools. Now imagine 300 airlines.
]
FUNCS = {"joyair_search": airlines.joyair_api_flights,
         "draair_search": airlines.draair_flights_list,
         "aeroggo_search": airlines.aeroggo_list_flights}


def run(task, max_steps=8):
    messages = [{"role": "user", "content": task}]
    for _ in range(max_steps):
        r = client.messages.create(model=MODEL, max_tokens=1024, tools=TOOLS, messages=messages)
        if r.stop_reason != "tool_use":
            return "".join(b.text for b in r.content if b.type == "text")
        messages.append({"role": "assistant", "content": r.content})
        results = [{"type": "tool_result", "tool_use_id": b.id, "content": str(FUNCS[b.name](**b.input))}
                   for b in r.content if b.type == "tool_use"]
        messages.append({"role": "user", "content": results})
    return "Max steps reached."


if __name__ == "__main__":
    print(run("Find me the cheapest flight from SFO to JFK across all airlines."))
