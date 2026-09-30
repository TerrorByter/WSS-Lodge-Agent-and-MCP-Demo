"""Three fake airline APIs. Each has its own endpoint name, input names, and response shape,
just like in the video (/api/flights vs /flights-list vs list_flights)."""

# ---------- Joy Air: GET /api/flights ----------
def joyair_api_flights(origin: str, destination: str) -> list[dict]:
    return [
        {"flight_number": "JA101", "origin": origin, "destination": destination, "price_usd": 310},
        {"flight_number": "JA205", "origin": origin, "destination": destination, "price_usd": 275},
    ]

def joyair_api_book(flight_number: str, passenger_name: str) -> dict:
    return {"booking_ref": f"JOY-{flight_number}-7431", "passenger": passenger_name}


# ---------- Dra Air: GET /flights-list ----------
def draair_flights_list(src: str, dst: str) -> dict:
    return {"results": [
        {"flightNo": "DR330", "from": src, "to": dst, "fare": {"amount": 289, "currency": "USD"}},
    ]}

def draair_reserve(flightNo: str, pax: str) -> dict:
    return {"reservation": {"code": f"DRA-{flightNo}-9920", "pax": pax}}


# ---------- Aeroggo: POST list_flights ----------
def aeroggo_list_flights(start: str, finish: str) -> dict:
    return {"detailedFlights": [
        {"flight": "AG78", "start": start, "finish": finish, "cost": 342.50},
        {"flight": "AG91", "start": start, "finish": finish, "cost": 259.00},
    ]}

def aeroggo_book(flight: str, name: str) -> dict:
    return {"confirmation": f"AGO-{flight}-1188", "name": name}


# # ---------- EXERCISE (Part 7): SkyBee, a 4th airline with its own odd naming, and prices in CENTS ----------
# # To enable: select this whole block and toggle comments (Cmd+/ on Mac, Ctrl+/ on Windows).
# # Then do the matching step in flight_mcp_server.py (search into search_flights, book into book_flight).
# def skybee_find(leaving_from: str, going_to: str) -> dict:
#     return {"trips": [
#         {"id": "SB12", "usd_cents": 24900},
#     ]}

# def skybee_book(trip_id: str, traveller: str) -> dict:
#     return {"ticket": f"SKY-{trip_id}-5502", "traveller": traveller}
