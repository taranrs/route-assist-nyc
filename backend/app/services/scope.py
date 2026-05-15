from app.services.location_catalog import resolve_demo_location

SUPPORTED_SCOPE_MESSAGE = (
    "RouteAssist NYC currently supports Manhattan routes. "
    "Outer borough and commuter route support coming later."
)

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

    return resolve_demo_location(origin_key) is not None and resolve_demo_location(destination_key) is not None
