from app.domain.enums import PreferenceMode, RouteMode
from app.models.routes import CompareRoutesRequest, CompareRoutesResponse, RouteCard
from app.providers.mock_routes import get_mock_route_options
from app.services.scope import SUPPORTED_SCOPE_MESSAGE, is_supported_manhattan_route
from app.services.scoring import RouteOption, ScoredRoute, score_routes, select_ranked_routes

LABELS = {
    PreferenceMode.fastest: "Fastest",
    PreferenceMode.cheapest: "Cheapest",
    PreferenceMode.least_stressful: "Least stressful",
    PreferenceMode.safety_aware: "Safety-aware",
}


def compare_routes(request: CompareRoutesRequest) -> CompareRoutesResponse:
    if not is_supported_manhattan_route(request.origin, request.destination):
        return CompareRoutesResponse(
            supported=False,
            scopeMessage=SUPPORTED_SCOPE_MESSAGE,
            requestedPreference=request.preference_mode,
            routeCards=[],
        )

    options = _apply_request_filters(get_mock_route_options(request.origin, request.destination), request)

    scored = score_routes(
        options,
        avoid_long_walks=request.avoid_long_walks,
        avoid_transfers=request.avoid_transfers,
        late_night_mode=request.late_night_mode,
        bad_weather_mode=request.bad_weather_mode,
    )
    ranked = select_ranked_routes(scored)

    ordered_preferences = [
        request.preference_mode,
        PreferenceMode.fastest,
        PreferenceMode.cheapest,
        PreferenceMode.least_stressful,
        PreferenceMode.safety_aware,
    ]
    seen: set[PreferenceMode] = set()
    cards: list[RouteCard] = []
    for preference in ordered_preferences:
        if preference in seen:
            continue
        seen.add(preference)
        cards.append(_to_route_card(preference, ranked[preference], request))

    return CompareRoutesResponse(
        supported=True,
        scopeMessage=None,
        requestedPreference=request.preference_mode,
        routeCards=cards,
    )


def _apply_request_filters(
    options: list[RouteOption],
    request: CompareRoutesRequest,
) -> list[RouteOption]:
    if request.max_rideshare_cost is None:
        return options

    return [
        option
        for option in options
        if option.mode != RouteMode.rideshare or option.estimated_cost <= request.max_rideshare_cost
    ]


def _to_route_card(
    preference: PreferenceMode,
    scored_route: ScoredRoute,
    request: CompareRoutesRequest,
) -> RouteCard:
    route = scored_route.option
    return RouteCard(
        label=LABELS[preference],
        mode=route.mode,
        estimatedTime=route.travel_time_minutes,
        estimatedCost=route.estimated_cost,
        transfers=route.transfers,
        walkingMinutes=route.walking_minutes,
        stressScore=scored_route.stress_score,
        reasons=_build_reasons(preference, scored_route, request),
    )


def _build_reasons(
    preference: PreferenceMode,
    scored_route: ScoredRoute,
    request: CompareRoutesRequest,
) -> list[str]:
    route = scored_route.option
    reasons = [route.summary]

    if preference == PreferenceMode.fastest:
        reasons.append(f"Lowest modeled travel time at {route.travel_time_minutes} minutes.")
    if preference == PreferenceMode.cheapest:
        reasons.append(f"Lowest modeled cost at ${route.estimated_cost:.2f}.")
    if preference == PreferenceMode.least_stressful:
        reasons.append(f"Lowest combined stress score at {scored_route.stress_score}.")
    if preference == PreferenceMode.safety_aware:
        reasons.append("Balances shorter walks, waits, transfers, weather, and late-night exposure.")

    if request.avoid_long_walks and route.walking_minutes <= 10:
        reasons.append("Keeps walking time short for the avoid-long-walks setting.")
    if request.avoid_transfers and route.transfers == 0:
        reasons.append("Avoids transfers for a simpler trip.")
    if request.bad_weather_mode and route.weather_penalty <= 3:
        reasons.append("Minimizes weather exposure.")
    if request.late_night_mode and route.late_night_walk_penalty <= 3:
        reasons.append("Reduces late-night walking exposure.")

    return reasons
