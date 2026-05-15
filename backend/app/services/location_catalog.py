from dataclasses import dataclass


@dataclass(frozen=True)
class DemoLocation:
    display_name: str
    latitude: float
    longitude: float
    aliases: tuple[str, ...] = ()


DEMO_LOCATIONS: tuple[DemoLocation, ...] = (
    DemoLocation("Penn Station", 40.7506, -73.9935, ("penn",)),
    DemoLocation("Times Square", 40.7580, -73.9855, ("time square", "times square")),
    DemoLocation("Grand Central", 40.7527, -73.9772, ("grand central terminal",)),
    DemoLocation("Washington Square Park", 40.7308, -73.9973, ("nyu",)),
    DemoLocation("Union Square", 40.7359, -73.9911, ("union sq",)),
    DemoLocation("Chelsea", 40.7465, -74.0014, ()),
    DemoLocation("Chelsea Market", 40.7424, -74.0060, ("chelsea market",)),
    DemoLocation("World Trade Center", 40.7127, -74.0134, ("wtc",)),
    DemoLocation("Wall Street", 40.7060, -74.0086, ("wall st",)),
    DemoLocation("Financial District", 40.7075, -74.0113, ("financial district", "fidi")),
    DemoLocation("SoHo", 40.7233, -74.0030, ("soho",)),
    DemoLocation("Tribeca", 40.7163, -74.0086, ("tribeca",)),
    DemoLocation("Columbus Circle", 40.7681, -73.9819, ("columbus circle",)),
    DemoLocation("Central Park South", 40.7651, -73.9741, ("central park",)),
    DemoLocation("Empire State Building", 40.7484, -73.9857, ("empire state",)),
    DemoLocation("Columbia University", 40.8075, -73.9626, ("columbia",)),
    DemoLocation("Bryant Park", 40.7536, -73.9832, ("bryant park",)),
    DemoLocation("Rockefeller Center", 40.7587, -73.9787, ("rockefeller", "rockefeller center")),
    DemoLocation("Flatiron Building", 40.7411, -73.9897, ("flatiron",)),
    DemoLocation("Battery Park", 40.7033, -74.0170, ("battery park",)),
)

LOCATION_LOOKUP: dict[str, DemoLocation] = {}
for location in DEMO_LOCATIONS:
    LOCATION_LOOKUP[location.display_name.strip().lower()] = location
    for alias in location.aliases:
        LOCATION_LOOKUP[alias.strip().lower()] = location


def normalize_location_query(value: str) -> str:
    return " ".join(value.strip().lower().split())


def resolve_demo_location(value: str) -> DemoLocation | None:
    return LOCATION_LOOKUP.get(normalize_location_query(value))


def canonical_location_name(value: str) -> str | None:
    location = resolve_demo_location(value)
    if location is None:
        return None
    return location.display_name


def get_demo_location_names() -> list[str]:
    return [location.display_name for location in DEMO_LOCATIONS]
