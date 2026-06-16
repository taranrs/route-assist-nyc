from dataclasses import replace
from math import asin, cos, radians, sin, sqrt

from app.domain.enums import RouteMode
from app.services.location_catalog import canonical_location_name, resolve_demo_location
from app.services.scoring import RouteOption


def _key(origin: str, destination: str) -> tuple[str, str]:
    origin_name = canonical_location_name(origin) or origin
    destination_name = canonical_location_name(destination) or destination
    return origin_name.strip().lower(), destination_name.strip().lower()


MOCK_ROUTE_LIBRARY: dict[tuple[str, str], list[RouteOption]] = {
    ("penn station", "washington square park"): [
        RouteOption("subway-penn-wsp", RouteMode.subway, 18, 2.90, 7, 1, 4, 3, 3, 3, 1, "1/2/3 to Christopher St with a short walk", subway_lines=("1", "2", "3")),
        RouteOption("walk-penn-wsp", RouteMode.walking, 39, 0, 39, 0, 0, 1, 5, 7, 0, "Direct walk down 7th Avenue"),
        RouteOption("bike-penn-wsp", RouteMode.citi_bike, 19, 4.79, 5, 0, 3, 4, 7, 4, 0, "Citi Bike via protected and shared lanes"),
        RouteOption("ride-penn-wsp", RouteMode.rideshare, 21, 24.50, 3, 0, 5, 7, 1, 1, 0, "Door-to-door rideshare through Midtown traffic"),
    ],
    ("times square", "wall street"): [
        RouteOption("subway-ts-wall", RouteMode.subway, 22, 2.90, 6, 0, 5, 4, 2, 2, 1, "R/W or 2/3 express downtown", subway_lines=("R", "W", "2", "3")),
        RouteOption("walk-ts-wall", RouteMode.walking, 82, 0, 82, 0, 0, 1, 8, 10, 0, "Long direct walk through Midtown and Lower Manhattan"),
        RouteOption("bike-ts-wall", RouteMode.citi_bike, 35, 4.79, 7, 0, 4, 6, 8, 5, 0, "Citi Bike down Broadway corridor"),
        RouteOption("ride-ts-wall", RouteMode.rideshare, 36, 42.00, 4, 0, 6, 9, 1, 1, 0, "Rideshare with heavy CBD congestion"),
    ],
    ("grand central", "columbia university"): [
        RouteOption("subway-gct-columbia", RouteMode.subway, 31, 2.90, 10, 1, 6, 3, 3, 4, 2, "Shuttle or 7 to 1 train uptown", subway_lines=("GS", "7", "1")),
        RouteOption("walk-gct-columbia", RouteMode.walking, 96, 0, 96, 0, 0, 1, 8, 11, 0, "Very long uptown walk"),
        RouteOption("bike-gct-columbia", RouteMode.citi_bike, 45, 4.79, 8, 0, 4, 5, 7, 5, 0, "Citi Bike using west-side connections"),
        RouteOption("ride-gct-columbia", RouteMode.rideshare, 34, 38.00, 3, 0, 5, 8, 1, 1, 0, "Rideshare via FDR or Central Park corridor"),
    ],
    ("union square", "chelsea"): [
        RouteOption("subway-usq-chelsea", RouteMode.subway, 14, 2.90, 8, 1, 4, 3, 2, 2, 1, "L train crosstown plus short walk", subway_lines=("L",)),
        RouteOption("walk-usq-chelsea", RouteMode.walking, 24, 0, 24, 0, 0, 1, 3, 4, 0, "Direct walk across 14th Street"),
        RouteOption("bike-usq-chelsea", RouteMode.citi_bike, 12, 4.79, 4, 0, 2, 3, 5, 3, 0, "Short Citi Bike ride west"),
        RouteOption("ride-usq-chelsea", RouteMode.rideshare, 16, 18.00, 2, 0, 4, 6, 1, 1, 0, "Short rideshare across town"),
    ],
    ("world trade center", "times square"): [
        RouteOption("subway-wtc-ts", RouteMode.subway, 24, 2.90, 8, 0, 4, 4, 2, 2, 1, "E train uptown", subway_lines=("E",)),
        RouteOption("walk-wtc-ts", RouteMode.walking, 78, 0, 78, 0, 0, 1, 8, 10, 0, "Long walk through Lower Manhattan and Midtown"),
        RouteOption("bike-wtc-ts", RouteMode.citi_bike, 38, 4.79, 7, 0, 4, 6, 8, 5, 0, "Citi Bike via Hudson River Greenway"),
        RouteOption("ride-wtc-ts", RouteMode.rideshare, 34, 39.00, 3, 0, 5, 9, 1, 1, 0, "Rideshare with high Midtown congestion"),
    ],
}


def get_mock_route_options(origin: str, destination: str) -> list[RouteOption]:
    direct_key = _key(origin, destination)
    reverse_key = _key(destination, origin)

    if direct_key in MOCK_ROUTE_LIBRARY:
        return _with_distance_metadata(MOCK_ROUTE_LIBRARY[direct_key], origin, destination)
    if reverse_key in MOCK_ROUTE_LIBRARY:
        return _with_distance_metadata(MOCK_ROUTE_LIBRARY[reverse_key], origin, destination)

    return generate_generic_manhattan_options(origin, destination)


def generate_generic_manhattan_options(origin: str, destination: str) -> list[RouteOption]:
    origin_location = resolve_demo_location(origin)
    destination_location = resolve_demo_location(destination)
    if origin_location is None or destination_location is None:
        return []

    distance = max(
        0.3,
        _haversine_miles(
            origin_location.latitude,
            origin_location.longitude,
            destination_location.latitude,
            destination_location.longitude,
        ),
    )
    complexity = _route_complexity(distance)
    complexity_label = _complexity_label(distance)
    walking_time = round(distance * 20)
    bike_time = round(distance * 10 + 7)
    subway_wait = 4 + complexity
    subway_transfers = 0 if distance < 2.0 else 1 if distance < 5.0 else 2
    subway_time = round(8 + distance * 5.4 + subway_wait + subway_transfers * 5)
    congestion = min(10, round(3 + distance * 1.15 + complexity))
    rideshare_time = round(7 + distance * 7.0 + congestion * 0.8)
    rideshare_cost = round(11 + distance * 5.6 + congestion * 1.35, 2)
    bike_cost = round(min(8.0, 4.0 + distance * 0.55), 2)

    return [
        RouteOption(
            "subway-generic",
            RouteMode.subway,
            subway_time,
            2.90,
            min(14, 5 + subway_transfers * 3),
            subway_transfers,
            subway_wait,
            max(2, complexity),
            2,
            2 + subway_transfers,
            subway_transfers,
            "Demo subway estimate using nearby Manhattan stations.",
            round(distance, 2),
            round(min(distance * 0.18 + 0.15 + subway_transfers * 0.08, 1.2), 2),
            0.0,
            0.0,
            round(subway_time / max(distance, 0.1), 1),
            True,
            complexity_label,
            "LOW" if subway_transfers == 0 and subway_wait <= 5 else "MEDIUM" if subway_transfers <= 1 else "HIGH",
            "Lower cost and weather protection, but station access, waits, and transfers can add complexity.",
            ("Base fare", "Station access walk", "Wait time", "Transfer complexity"),
        ),
        RouteOption(
            "walk-generic",
            RouteMode.walking,
            max(7, walking_time),
            0,
            max(7, walking_time),
            0,
            0,
            1,
            min(10, max(2, round(distance * 1.8))),
            min(10, max(2, round(distance * 2.4))),
            0,
            "Demo walking estimate based on approximate Manhattan distance.",
            round(distance, 2),
            round(distance, 2),
            0.0,
            0.0,
            round(60 / 20, 1),
            True,
            "LOW" if distance < 1.2 else "MEDIUM" if distance < 3.0 else "HIGH",
            None,
            "No fare or transfers, but all distance becomes walking exposure.",
            ("No cost", "Full walking distance", "Weather exposure", "Late-night walking exposure"),
        ),
        RouteOption(
            "bike-generic",
            RouteMode.citi_bike,
            max(9, bike_time),
            bike_cost,
            6,
            0,
            3,
            min(8, max(2, round(distance * 1.2))),
            min(10, max(3, round(distance * 1.7))),
            min(10, max(3, round(distance * 1.5))),
            0,
            "Demo Citi Bike estimate with unlock, dock, and short walk time.",
            round(distance, 2),
            0.25,
            round(distance * 1.05, 2),
            0.0,
            round(60 / 10, 1),
            True,
            complexity_label,
            None,
            "Fast for medium distances, but weather, docks, and late-night biking exposure matter.",
            ("Bike distance", "Dock access", "Weather exposure", "Late-night biking exposure"),
        ),
        RouteOption(
            "ride-generic",
            RouteMode.rideshare,
            max(9, rideshare_time),
            rideshare_cost,
            3,
            0,
            4,
            congestion,
            1,
            1,
            0,
            "Demo rideshare estimate with Manhattan congestion.",
            round(distance, 2),
            0.1,
            0.0,
            round(distance * 1.15, 2),
            round(distance / max(rideshare_time / 60, 0.1), 1),
            True,
            "LOW" if congestion <= 5 else "MEDIUM" if congestion <= 8 else "HIGH",
            None,
            "Lowest walking exposure, but higher cost and congestion variability.",
            ("Low walking exposure", "Congestion delay", "Higher estimated cost"),
        ),
    ]


def _with_distance_metadata(options: list[RouteOption], origin: str, destination: str) -> list[RouteOption]:
    origin_location = resolve_demo_location(origin)
    destination_location = resolve_demo_location(destination)
    if origin_location is None or destination_location is None:
        return options

    distance = round(
        max(
            0.3,
            _haversine_miles(
                origin_location.latitude,
                origin_location.longitude,
                destination_location.latitude,
                destination_location.longitude,
            ),
        ),
        2,
    )
    enriched: list[RouteOption] = []
    for option in options:
        if option.mode == RouteMode.walking:
            enriched.append(
                replace(
                    option,
                    distance_miles=distance,
                    walking_distance_miles=distance,
                    average_speed_mph=round(distance / max(option.travel_time_minutes / 60, 0.1), 1),
                    route_complexity="LOW" if distance < 1.5 else "MEDIUM" if distance < 4 else "HIGH",
                    mode_tradeoff_summary="No fare or transfers, but all distance becomes walking exposure.",
                    major_decision_factors=("No cost", "Full walking distance", "Weather exposure", "Late-night walking exposure"),
                )
            )
        elif option.mode == RouteMode.citi_bike:
            enriched.append(
                replace(
                    option,
                    distance_miles=distance,
                    walking_distance_miles=0.25,
                    biking_distance_miles=round(distance * 1.05, 2),
                    average_speed_mph=round(distance / max(option.travel_time_minutes / 60, 0.1), 1),
                    route_complexity=_complexity_label(distance),
                    mode_tradeoff_summary="Fast for medium distances, but weather, docks, and late-night biking exposure matter.",
                    major_decision_factors=("Bike distance", "Dock access", "Weather exposure", "Late-night biking exposure"),
                )
            )
        elif option.mode == RouteMode.rideshare:
            enriched.append(
                replace(
                    option,
                    distance_miles=distance,
                    walking_distance_miles=0.1,
                    driving_distance_miles=round(distance * 1.15, 2),
                    average_speed_mph=round(distance / max(option.travel_time_minutes / 60, 0.1), 1),
                    route_complexity="LOW" if option.congestion_score <= 5 else "MEDIUM" if option.congestion_score <= 8 else "HIGH",
                    mode_tradeoff_summary="Lowest walking exposure, but higher cost and congestion variability.",
                    major_decision_factors=("Low walking exposure", "Congestion delay", "Higher estimated cost"),
                )
            )
        else:
            enriched.append(
                replace(
                    option,
                    distance_miles=distance,
                    walking_distance_miles=round(min(distance * 0.18 + 0.15 + option.transfers * 0.08, 1.2), 2),
                    average_speed_mph=round(distance / max(option.travel_time_minutes / 60, 0.1), 1),
                    route_complexity=_complexity_label(distance),
                    station_complexity="LOW" if option.transfers == 0 and option.wait_time_minutes <= 5 else "MEDIUM" if option.transfers <= 1 else "HIGH",
                    mode_tradeoff_summary="Lower cost and weather protection, but station access, waits, and transfers can add complexity.",
                    major_decision_factors=("Base fare", "Station access walk", "Wait time", "Transfer complexity"),
                )
            )
    return enriched


def _haversine_miles(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    radius_miles = 3958.8
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    lat1_rad = radians(lat1)
    lat2_rad = radians(lat2)
    a = sin(dlat / 2) ** 2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlon / 2) ** 2
    return 2 * radius_miles * asin(sqrt(a))


def _route_complexity(distance_miles: float) -> int:
    if distance_miles < 1.5:
        return 1
    if distance_miles < 4.0:
        return 2
    return 3


def _complexity_label(distance_miles: float) -> str:
    if distance_miles < 1.5:
        return "LOW"
    if distance_miles < 4.0:
        return "MEDIUM"
    return "HIGH"
