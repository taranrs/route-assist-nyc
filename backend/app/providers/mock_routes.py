from app.domain.enums import RouteMode
from app.services.location_catalog import canonical_location_name
from app.services.scoring import RouteOption


def _key(origin: str, destination: str) -> tuple[str, str]:
    origin_name = canonical_location_name(origin) or origin
    destination_name = canonical_location_name(destination) or destination
    return origin_name.strip().lower(), destination_name.strip().lower()


MOCK_ROUTE_LIBRARY: dict[tuple[str, str], list[RouteOption]] = {
    ("penn station", "washington square park"): [
        RouteOption("subway-penn-wsp", RouteMode.subway, 18, 2.90, 7, 1, 4, 3, 3, 3, 1, "1/2/3 to Christopher St with a short walk"),
        RouteOption("walk-penn-wsp", RouteMode.walking, 39, 0, 39, 0, 0, 1, 5, 7, 0, "Direct walk down 7th Avenue"),
        RouteOption("bike-penn-wsp", RouteMode.citi_bike, 19, 4.79, 5, 0, 3, 4, 7, 4, 0, "Citi Bike via protected and shared lanes"),
        RouteOption("ride-penn-wsp", RouteMode.rideshare, 21, 24.50, 3, 0, 5, 7, 1, 1, 0, "Door-to-door rideshare through Midtown traffic"),
    ],
    ("times square", "wall street"): [
        RouteOption("subway-ts-wall", RouteMode.subway, 22, 2.90, 6, 0, 5, 4, 2, 2, 1, "R/W or 2/3 express downtown"),
        RouteOption("walk-ts-wall", RouteMode.walking, 82, 0, 82, 0, 0, 1, 8, 10, 0, "Long direct walk through Midtown and Lower Manhattan"),
        RouteOption("bike-ts-wall", RouteMode.citi_bike, 35, 4.79, 7, 0, 4, 6, 8, 5, 0, "Citi Bike down Broadway corridor"),
        RouteOption("ride-ts-wall", RouteMode.rideshare, 36, 42.00, 4, 0, 6, 9, 1, 1, 0, "Rideshare with heavy CBD congestion"),
    ],
    ("grand central", "columbia university"): [
        RouteOption("subway-gct-columbia", RouteMode.subway, 31, 2.90, 10, 1, 6, 3, 3, 4, 2, "Shuttle or 7 to 1 train uptown"),
        RouteOption("walk-gct-columbia", RouteMode.walking, 96, 0, 96, 0, 0, 1, 8, 11, 0, "Very long uptown walk"),
        RouteOption("bike-gct-columbia", RouteMode.citi_bike, 45, 4.79, 8, 0, 4, 5, 7, 5, 0, "Citi Bike using west-side connections"),
        RouteOption("ride-gct-columbia", RouteMode.rideshare, 34, 38.00, 3, 0, 5, 8, 1, 1, 0, "Rideshare via FDR or Central Park corridor"),
    ],
    ("union square", "chelsea"): [
        RouteOption("subway-usq-chelsea", RouteMode.subway, 14, 2.90, 8, 1, 4, 3, 2, 2, 1, "L train crosstown plus short walk"),
        RouteOption("walk-usq-chelsea", RouteMode.walking, 24, 0, 24, 0, 0, 1, 3, 4, 0, "Direct walk across 14th Street"),
        RouteOption("bike-usq-chelsea", RouteMode.citi_bike, 12, 4.79, 4, 0, 2, 3, 5, 3, 0, "Short Citi Bike ride west"),
        RouteOption("ride-usq-chelsea", RouteMode.rideshare, 16, 18.00, 2, 0, 4, 6, 1, 1, 0, "Short rideshare across town"),
    ],
    ("world trade center", "times square"): [
        RouteOption("subway-wtc-ts", RouteMode.subway, 24, 2.90, 8, 0, 4, 4, 2, 2, 1, "E train uptown"),
        RouteOption("walk-wtc-ts", RouteMode.walking, 78, 0, 78, 0, 0, 1, 8, 10, 0, "Long walk through Lower Manhattan and Midtown"),
        RouteOption("bike-wtc-ts", RouteMode.citi_bike, 38, 4.79, 7, 0, 4, 6, 8, 5, 0, "Citi Bike via Hudson River Greenway"),
        RouteOption("ride-wtc-ts", RouteMode.rideshare, 34, 39.00, 3, 0, 5, 9, 1, 1, 0, "Rideshare with high Midtown congestion"),
    ],
}


def get_mock_route_options(origin: str, destination: str) -> list[RouteOption]:
    direct_key = _key(origin, destination)
    reverse_key = _key(destination, origin)

    if direct_key in MOCK_ROUTE_LIBRARY:
        return MOCK_ROUTE_LIBRARY[direct_key]
    if reverse_key in MOCK_ROUTE_LIBRARY:
        return MOCK_ROUTE_LIBRARY[reverse_key]

    return [
        RouteOption("subway-generic", RouteMode.subway, 24, 2.90, 8, 1, 5, 4, 3, 3, 1, "Mock subway route using nearby Manhattan stations"),
        RouteOption("walk-generic", RouteMode.walking, 42, 0, 42, 0, 0, 1, 5, 7, 0, "Direct Manhattan walking route"),
        RouteOption("bike-generic", RouteMode.citi_bike, 22, 4.79, 6, 0, 3, 5, 7, 4, 0, "Mock Citi Bike route between nearby docks"),
        RouteOption("ride-generic", RouteMode.rideshare, 25, 28.00, 3, 0, 5, 7, 1, 1, 0, "Mock rideshare route with Manhattan congestion"),
    ]
