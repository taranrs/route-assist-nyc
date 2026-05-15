SUPPORTED_SCOPE_MESSAGE = (
    "RouteAssist NYC currently supports Manhattan routes. "
    "Outer borough and commuter route support coming later."
)

MANHATTAN_PLACES = {
    "penn station",
    "washington square park",
    "times square",
    "wall street",
    "grand central",
    "columbia university",
    "union square",
    "chelsea",
    "world trade center",
    "harlem",
    "central park",
    "soho",
    "flatiron",
    "upper west side",
    "upper east side",
}

OUT_OF_SCOPE_MARKERS = {
    "brooklyn",
    "queens",
    "bronx",
    "staten island",
    "new jersey",
    "hoboken",
    "jersey city",
    "long island",
    "newark",
    "path",
    "lirr",
    "nj transit",
}


def is_supported_manhattan_route(origin: str, destination: str) -> bool:
    origin_key = origin.strip().lower()
    destination_key = destination.strip().lower()
    combined = f"{origin_key} {destination_key}"

    if any(marker in combined for marker in OUT_OF_SCOPE_MARKERS):
        return False

    return origin_key in MANHATTAN_PLACES and destination_key in MANHATTAN_PLACES
