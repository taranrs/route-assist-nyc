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


@dataclass(frozen=True)
class ScoredRoute:
    option: RouteOption
    fastest_score: float
    cheapest_score: float
    stress_score: float
    safety_score: float


Selector = Callable[[ScoredRoute], float]

RANKING_SELECTORS: dict[PreferenceMode, Selector] = {
    PreferenceMode.fastest: lambda route: route.fastest_score,
    PreferenceMode.cheapest: lambda route: route.cheapest_score,
    PreferenceMode.least_stressful: lambda route: route.stress_score,
    PreferenceMode.safety_aware: lambda route: route.safety_score,
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
    )

    if avoid_long_walks:
        score += route.walking_minutes * 1.2
    if avoid_transfers:
        score += route.transfers * 12
    if bad_weather_mode:
        score += route.weather_penalty * 2.2
    else:
        score += route.weather_penalty
    if late_night_mode:
        score += route.late_night_walk_penalty * 2.5
    else:
        score += route.late_night_walk_penalty

    return round(score, 1)


def calculate_safety_score(
    route: RouteOption,
    *,
    late_night_mode: bool = False,
    bad_weather_mode: bool = False,
) -> float:
    score = (
        route.walking_minutes * 2.0
        + route.wait_time_minutes * 1.4
        + route.transfers * 5
        + route.congestion_score * 2.5
        + route.service_alert_penalty * 2
    )
    score += route.late_night_walk_penalty * (3.0 if late_night_mode else 1.2)
    score += route.weather_penalty * (2.5 if bad_weather_mode else 1.0)
    return round(score, 1)


def score_route(
    route: RouteOption,
    *,
    avoid_long_walks: bool = False,
    avoid_transfers: bool = False,
    late_night_mode: bool = False,
    bad_weather_mode: bool = False,
) -> ScoredRoute:
    stress_score = calculate_stress_score(
        route,
        avoid_long_walks=avoid_long_walks,
        avoid_transfers=avoid_transfers,
        late_night_mode=late_night_mode,
        bad_weather_mode=bad_weather_mode,
    )
    return ScoredRoute(
        option=route,
        fastest_score=route.travel_time_minutes + route.wait_time_minutes * 0.4,
        cheapest_score=route.estimated_cost + route.transfers * 0.25,
        stress_score=stress_score,
        safety_score=calculate_safety_score(
            route,
            late_night_mode=late_night_mode,
            bad_weather_mode=bad_weather_mode,
        ),
    )


def score_routes(
    routes: list[RouteOption],
    *,
    avoid_long_walks: bool = False,
    avoid_transfers: bool = False,
    late_night_mode: bool = False,
    bad_weather_mode: bool = False,
) -> list[ScoredRoute]:
    return [
        score_route(
            route,
            avoid_long_walks=avoid_long_walks,
            avoid_transfers=avoid_transfers,
            late_night_mode=late_night_mode,
            bad_weather_mode=bad_weather_mode,
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
