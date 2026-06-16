from dataclasses import dataclass
from typing import Callable

from app.domain.enums import PreferenceMode, RouteMode


@dataclass(frozen=True)
class RouteOption:
    id: str
    mode: RouteMode
    travel_time_minutes: int
    estimated_cost: float
    walking_minutes: int
    transfers: int
    wait_time_minutes: int
    congestion_score: int
    weather_penalty: int
    late_night_walk_penalty: int
    service_alert_penalty: int
    summary: str
    distance_miles: float = 0.0
    walking_distance_miles: float = 0.0
    biking_distance_miles: float = 0.0
    driving_distance_miles: float = 0.0
    average_speed_mph: float = 0.0
    demo_estimate: bool = True
    route_complexity: str = "MEDIUM"
    station_complexity: str | None = None
    mode_tradeoff_summary: str = ""
    major_decision_factors: tuple[str, ...] = ()
    subway_lines: tuple[str, ...] = ()
    availability_penalty: int = 0


@dataclass(frozen=True)
class ScoredRoute:
    option: RouteOption
    fastest_score: float
    cheapest_score: float
    stress_score: float
    safety_aware_score: float
    score_breakdown: dict[str, float]
    major_penalties: tuple[str, ...] = ()


Selector = Callable[[ScoredRoute], float]

RANKING_SELECTORS: dict[PreferenceMode, Selector] = {
    PreferenceMode.fastest: lambda route: route.fastest_score,
    PreferenceMode.cheapest: lambda route: route.cheapest_score,
    PreferenceMode.least_stressful: lambda route: route.stress_score,
    PreferenceMode.safety_aware: lambda route: route.safety_aware_score,
}


def calculate_stress_score(
    route: RouteOption,
    *,
    avoid_long_walks: bool = False,
    avoid_transfers: bool = False,
    late_night_mode: bool = False,
    bad_weather_mode: bool = False,
) -> float:
    score = (
        route.travel_time_minutes * 0.8
        + route.walking_minutes * 1.1
        + route.transfers * 8
        + route.wait_time_minutes * 0.9
        + route.congestion_score * 4
        + route.service_alert_penalty * 1.5
        + route.availability_penalty * 2.0
    )

    if avoid_long_walks:
        score += route.walking_minutes * 2.8
    if avoid_transfers:
        score += route.transfers * 22
    if bad_weather_mode:
        weather_multiplier = 4.5 if route.mode in {RouteMode.walking, RouteMode.citi_bike} else 1.6
        score += route.weather_penalty * weather_multiplier
    else:
        score += route.weather_penalty
    if late_night_mode:
        late_night_multiplier = 5.0 if route.mode in {RouteMode.walking, RouteMode.citi_bike} else 1.8
        score += route.late_night_walk_penalty * late_night_multiplier
    else:
        score += route.late_night_walk_penalty

    return round(score, 1)


def calculate_score_breakdown(
    route: RouteOption,
    *,
    avoid_long_walks: bool = False,
    avoid_transfers: bool = False,
    late_night_mode: bool = False,
    bad_weather_mode: bool = False,
) -> dict[str, float]:
    time_score = route.travel_time_minutes * 0.8
    walking_score = route.walking_minutes * (3.9 if avoid_long_walks else 1.1)
    transfer_score = route.transfers * (30 if avoid_transfers else 8)
    wait_score = route.wait_time_minutes * 0.9
    congestion_score = route.congestion_score * 4
    service_alert_score = route.service_alert_penalty * 1.5
    availability_score = route.availability_penalty * 2.0

    if bad_weather_mode:
        weather_multiplier = 4.5 if route.mode in {RouteMode.walking, RouteMode.citi_bike} else 1.6
    else:
        weather_multiplier = 1
    weather_score = route.weather_penalty * weather_multiplier

    if late_night_mode:
        late_night_multiplier = 5.0 if route.mode in {RouteMode.walking, RouteMode.citi_bike} else 1.8
    else:
        late_night_multiplier = 1
    late_night_score = route.late_night_walk_penalty * late_night_multiplier

    final_score = (
        time_score
        + walking_score
        + transfer_score
        + wait_score
        + congestion_score
        + weather_score
        + late_night_score
        + service_alert_score
        + availability_score
    )

    return {
        "fastestScore": round(route.travel_time_minutes, 1),
        "cheapestScore": round(route.estimated_cost, 1),
        "timeScore": round(time_score, 1),
        "costScore": round(route.estimated_cost, 1),
        "walkingScore": round(walking_score, 1),
        "transferScore": round(transfer_score, 1),
        "waitScore": round(wait_score, 1),
        "congestionScore": round(congestion_score, 1),
        "weatherScore": round(weather_score, 1),
        "lateNightScore": round(late_night_score, 1),
        "serviceAlertScore": round(service_alert_score, 1),
        "availabilityScore": round(availability_score, 1),
        "finalStressScore": round(final_score, 1),
    }


def calculate_safety_aware_score(
    route: RouteOption,
    *,
    late_night_mode: bool = False,
    bad_weather_mode: bool = False,
    max_rideshare_cost: float | None = None,
) -> float:
    complexity_weight = {"LOW": 0, "MEDIUM": 8, "HIGH": 18}.get(route.route_complexity, 8)
    station_weight = {"LOW": 0, "MEDIUM": 5, "HIGH": 12}.get(route.station_complexity or "LOW", 0)
    score = (
        route.walking_distance_miles * 32
        + route.walking_minutes * 2.4
        + route.wait_time_minutes * 2.0
        + route.transfers * 14
        + complexity_weight
        + station_weight
        + route.congestion_score * 1.5
        + route.service_alert_penalty * 4
    )
    if late_night_mode:
        if route.mode == RouteMode.walking:
            score += route.walking_distance_miles * 55 + route.late_night_walk_penalty * 8
        elif route.mode == RouteMode.citi_bike:
            score += route.biking_distance_miles * 12 + route.late_night_walk_penalty * 7
        elif route.mode == RouteMode.subway:
            score += route.walking_minutes * 1.5 + route.wait_time_minutes * 2 + route.transfers * 10
        elif route.mode == RouteMode.rideshare:
            score -= 18 if route.walking_minutes <= 4 else 0

    if bad_weather_mode:
        if route.mode == RouteMode.walking:
            score += route.walking_distance_miles * 35 + route.weather_penalty * 8
        elif route.mode == RouteMode.citi_bike:
            score += route.biking_distance_miles * 15 + route.weather_penalty * 9
        else:
            score += route.weather_penalty * 1.5

    if route.mode == RouteMode.rideshare and max_rideshare_cost is not None:
        if route.estimated_cost <= max_rideshare_cost:
            score -= 20
        else:
            score += 80

    return round(score, 1)


def score_route(
    route: RouteOption,
    *,
    avoid_long_walks: bool = False,
    avoid_transfers: bool = False,
    late_night_mode: bool = False,
    bad_weather_mode: bool = False,
    max_rideshare_cost: float | None = None,
) -> ScoredRoute:
    score_breakdown = calculate_score_breakdown(
        route,
        avoid_long_walks=avoid_long_walks,
        avoid_transfers=avoid_transfers,
        late_night_mode=late_night_mode,
        bad_weather_mode=bad_weather_mode,
    )
    return ScoredRoute(
        option=route,
        fastest_score=route.travel_time_minutes,
        cheapest_score=route.estimated_cost,
        stress_score=score_breakdown["finalStressScore"],
        safety_aware_score=calculate_safety_aware_score(
            route,
            late_night_mode=late_night_mode,
            bad_weather_mode=bad_weather_mode,
            max_rideshare_cost=max_rideshare_cost,
        ),
        score_breakdown={
            **score_breakdown,
            "safetyAwareScore": calculate_safety_aware_score(
                route,
                late_night_mode=late_night_mode,
                bad_weather_mode=bad_weather_mode,
                max_rideshare_cost=max_rideshare_cost,
            ),
        },
        major_penalties=tuple(
            describe_major_penalties(
                route,
                avoid_long_walks=avoid_long_walks,
                avoid_transfers=avoid_transfers,
                late_night_mode=late_night_mode,
                bad_weather_mode=bad_weather_mode,
            )
        ),
    )


def score_routes(
    routes: list[RouteOption],
    *,
    avoid_long_walks: bool = False,
    avoid_transfers: bool = False,
    late_night_mode: bool = False,
    bad_weather_mode: bool = False,
    max_rideshare_cost: float | None = None,
) -> list[ScoredRoute]:
    return [
        score_route(
            route,
            avoid_long_walks=avoid_long_walks,
            avoid_transfers=avoid_transfers,
            late_night_mode=late_night_mode,
            bad_weather_mode=bad_weather_mode,
            max_rideshare_cost=max_rideshare_cost,
        )
        for route in routes
    ]


def select_ranked_routes(scored_routes: list[ScoredRoute]) -> dict[PreferenceMode, ScoredRoute]:
    if not scored_routes:
        raise ValueError("Cannot rank an empty route list.")

    return {
        preference: min(scored_routes, key=lambda route: (selector(route), route.option.id))
        for preference, selector in RANKING_SELECTORS.items()
    }


def describe_major_penalties(
    route: RouteOption,
    *,
    avoid_long_walks: bool = False,
    avoid_transfers: bool = False,
    late_night_mode: bool = False,
    bad_weather_mode: bool = False,
) -> list[str]:
    penalties: list[str] = []

    if avoid_long_walks and route.walking_minutes >= 12:
        penalties.append("Long walking penalty applied")
    if avoid_transfers and route.transfers > 0:
        penalties.append("Transfer penalty applied")
    if late_night_mode and route.mode in {RouteMode.walking, RouteMode.citi_bike}:
        penalties.append("Late-night walking exposure penalty applied")
    if bad_weather_mode and route.mode in {RouteMode.walking, RouteMode.citi_bike}:
        penalties.append("Bad weather biking/walking penalty applied")
    if route.congestion_score >= 7:
        penalties.append("High congestion increases modeled stress.")
    if route.service_alert_penalty >= 3:
        penalties.append("Service alert risk increases modeled stress.")
    if route.availability_penalty >= 2 and route.mode == RouteMode.citi_bike:
        penalties.append("Low Citi Bike availability detected near origin.")
    if route.availability_penalty >= 4 and route.mode == RouteMode.citi_bike:
        penalties.append("No bikes available — docking station may be empty.")

    return penalties
