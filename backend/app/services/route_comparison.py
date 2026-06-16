from app.domain.enums import PreferenceMode, RouteMode
from app.models.routes import CompareRoutesRequest, CompareRoutesResponse, RouteCard
from app.providers.mock_routes import get_mock_route_options
from app.services.location_catalog import canonical_location_name, normalize_location_query
from app.services.scope import SUPPORTED_SCOPE_MESSAGE, is_supported_manhattan_route
from app.services.scoring import RANKING_SELECTORS, RouteOption, ScoredRoute, score_routes, select_ranked_routes

LABELS = {
    PreferenceMode.fastest: "Fastest",
    PreferenceMode.cheapest: "Cheapest",
    PreferenceMode.least_stressful: "Least stressful",
    PreferenceMode.safety_aware: "Safety-aware",
}

RECOMMENDATION_REASONS = {
    PreferenceMode.fastest: "Recommended for speed",
    PreferenceMode.cheapest: "Recommended for cost",
    PreferenceMode.least_stressful: "Recommended for low stress",
    PreferenceMode.safety_aware: "Recommended for safety-aware preferences",
}


def compare_routes(request: CompareRoutesRequest) -> CompareRoutesResponse:
    validation_message = _validate_request(request)
    if validation_message:
        return CompareRoutesResponse(
            supported=False,
            scopeMessage=None,
            validationMessage=validation_message,
            requestedPreference=request.preference_mode,
            recommendations=[],
            allOptions=[],
            appliedPreferences=[],
            hiddenOptionsMessages=[],
            routeCards=[],
        )

    if not is_supported_manhattan_route(request.origin, request.destination):
        return CompareRoutesResponse(
            supported=False,
            scopeMessage=SUPPORTED_SCOPE_MESSAGE,
            validationMessage=None,
            requestedPreference=request.preference_mode,
            recommendations=[],
            allOptions=[],
            appliedPreferences=[],
            hiddenOptionsMessages=[],
            routeCards=[],
        )

    options, hidden_messages = _apply_request_filters(
        get_mock_route_options(request.origin, request.destination), request
    )

    scored = score_routes(
        options,
        avoid_long_walks=request.avoid_long_walks,
        avoid_transfers=request.avoid_transfers,
        late_night_mode=request.late_night_mode,
        bad_weather_mode=request.bad_weather_mode,
        max_rideshare_cost=request.max_rideshare_cost,
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
        cards.append(_to_recommendation_card(preference, ranked[preference], scored, request))

    all_options = [
        _to_option_card(scored_route, request)
        for scored_route in sorted(scored, key=lambda route: route.option.mode.value)
    ]

    return CompareRoutesResponse(
        supported=True,
        scopeMessage=None,
        validationMessage=None,
        requestedPreference=request.preference_mode,
        recommendations=cards,
        allOptions=all_options,
        appliedPreferences=_build_applied_preferences(request, hidden_messages),
        hiddenOptionsMessages=hidden_messages,
        routeCards=cards,
    )


def _apply_request_filters(
    options: list[RouteOption],
    request: CompareRoutesRequest,
) -> tuple[list[RouteOption], list[str]]:
    if request.max_rideshare_cost is None:
        return options, []

    filtered = [
        option
        for option in options
        if option.mode != RouteMode.rideshare or option.estimated_cost <= request.max_rideshare_cost
    ]
    hidden_messages = []
    if len(filtered) != len(options):
        hidden_messages.append(
            f"Rideshare over budget: hidden because estimated cost exceeds your max rideshare cost of ${request.max_rideshare_cost:.0f}."
        )
    return filtered, hidden_messages


def _to_recommendation_card(
    preference: PreferenceMode,
    scored_route: ScoredRoute,
    scored_routes: list[ScoredRoute],
    request: CompareRoutesRequest,
) -> RouteCard:
    route = scored_route.option
    runner_up = _runner_up_for(preference, scored_route, scored_routes)
    return RouteCard(
        routeId=f"{preference.value}-{route.id}",
        label=LABELS[preference],
        mode=route.mode,
        estimatedTime=route.travel_time_minutes,
        estimatedCost=route.estimated_cost,
        transfers=route.transfers,
        walkingMinutes=route.walking_minutes,
        distanceMiles=round(route.distance_miles, 1),
        walkingDistanceMiles=round(route.walking_distance_miles, 1),
        bikingDistanceMiles=round(route.biking_distance_miles, 1) if route.biking_distance_miles else None,
        drivingDistanceMiles=round(route.driving_distance_miles, 1) if route.driving_distance_miles else None,
        averageSpeedMph=route.average_speed_mph,
        demoEstimate=route.demo_estimate,
        stressScore=scored_route.stress_score,
        fastestScore=scored_route.fastest_score,
        cheapestScore=scored_route.cheapest_score,
        safetyAwareScore=scored_route.safety_aware_score,
        baseEstimate=_base_estimate(route),
        routeSummary=route.summary,
        routeComplexity=route.route_complexity,
        stationComplexity=route.station_complexity,
        modeTradeoffSummary=route.mode_tradeoff_summary,
        majorDecisionFactors=list(route.major_decision_factors),
        majorPenalties=list(scored_route.major_penalties),
        scoreBreakdown=scored_route.score_breakdown,
        reasons=_build_reasons(preference, scored_route, request),
        recommendationReason=_recommendation_reason(preference, scored_route, runner_up),
        runnerUpMode=runner_up.option.mode if runner_up else None,
        runnerUpReason=_runner_up_reason(preference, scored_route, runner_up),
    )


def _to_option_card(scored_route: ScoredRoute, request: CompareRoutesRequest) -> RouteCard:
    route = scored_route.option
    return RouteCard(
        routeId=f"option-{route.id}",
        label=route.mode.value.replace("_", " ").title(),
        mode=route.mode,
        estimatedTime=route.travel_time_minutes,
        estimatedCost=route.estimated_cost,
        transfers=route.transfers,
        walkingMinutes=route.walking_minutes,
        distanceMiles=round(route.distance_miles, 1),
        walkingDistanceMiles=round(route.walking_distance_miles, 1),
        bikingDistanceMiles=round(route.biking_distance_miles, 1) if route.biking_distance_miles else None,
        drivingDistanceMiles=round(route.driving_distance_miles, 1) if route.driving_distance_miles else None,
        averageSpeedMph=route.average_speed_mph,
        demoEstimate=route.demo_estimate,
        stressScore=scored_route.stress_score,
        fastestScore=scored_route.fastest_score,
        cheapestScore=scored_route.cheapest_score,
        safetyAwareScore=scored_route.safety_aware_score,
        baseEstimate=_base_estimate(route),
        routeSummary=route.summary,
        routeComplexity=route.route_complexity,
        stationComplexity=route.station_complexity,
        modeTradeoffSummary=route.mode_tradeoff_summary,
        majorDecisionFactors=list(route.major_decision_factors),
        majorPenalties=list(scored_route.major_penalties),
        scoreBreakdown=scored_route.score_breakdown,
        reasons=_build_option_reasons(scored_route, request),
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
        reasons.extend(_safety_aware_reasons(scored_route, request))

    if request.avoid_long_walks and route.walking_minutes <= 10:
        reasons.append("Keeps walking time short for the avoid-long-walks setting.")
    if request.avoid_transfers and route.transfers == 0:
        reasons.append("Avoids transfers for a simpler trip.")
    if request.bad_weather_mode and route.weather_penalty <= 3:
        reasons.append("Minimizes weather exposure.")
    if request.late_night_mode and route.late_night_walk_penalty <= 3:
        reasons.append("Reduces late-night walking exposure.")

    return reasons


def _safety_aware_reasons(
    scored_route: ScoredRoute,
    request: CompareRoutesRequest,
) -> list[str]:
    route = scored_route.option
    reasons = ["Balances reduced walking exposure, waits, transfers, weather, and late-night exposure."]
    if route.mode == RouteMode.rideshare:
        reasons.append("Reduces late-night walking exposure compared with walking and Citi Bike.")
        if request.max_rideshare_cost is None or route.estimated_cost <= request.max_rideshare_cost:
            reasons.append("Stays under your max rideshare cost." if request.max_rideshare_cost is not None else "Minimizes walking exposure in this demo estimate.")
    if route.mode == RouteMode.subway:
        if route.transfers == 0 and route.walking_distance_miles <= 0.5:
            reasons.append("Subway remains recommended because it is direct, short-walk, and lower cost.")
        elif route.transfers == 0:
            reasons.append("Avoids transfer complexity.")
    if route.mode in {RouteMode.walking, RouteMode.citi_bike} and (request.late_night_mode or request.bad_weather_mode):
        reasons.append("This mode still ranked well despite exposure penalties in the current settings.")
    return reasons


def _build_option_reasons(scored_route: ScoredRoute, request: CompareRoutesRequest) -> list[str]:
    route = scored_route.option
    reasons = [route.summary, "Demo estimate generated for side-by-side mode comparison."]
    if request.max_rideshare_cost is not None and route.mode == RouteMode.rideshare:
        reasons.append(f"Within your ${request.max_rideshare_cost:.0f} max rideshare cost.")
    return reasons


def _runner_up_for(
    preference: PreferenceMode,
    winner: ScoredRoute,
    scored_routes: list[ScoredRoute],
) -> ScoredRoute | None:
    selector = RANKING_SELECTORS[preference]
    ranked = sorted(scored_routes, key=lambda route: (selector(route), route.option.id))
    for route in ranked:
        if route.option.id != winner.option.id:
            return route
    return None


def _recommendation_reason(
    preference: PreferenceMode,
    winner: ScoredRoute,
    runner_up: ScoredRoute | None,
) -> str:
    prefix = RECOMMENDATION_REASONS[preference]
    if runner_up is None:
        return prefix
    return f"{prefix}: beat {runner_up.option.mode.value.replace('_', ' ')} on the category score."


def _runner_up_reason(
    preference: PreferenceMode,
    winner: ScoredRoute,
    runner_up: ScoredRoute | None,
) -> str | None:
    if runner_up is None:
        return None

    selector = RANKING_SELECTORS[preference]
    difference = round(selector(runner_up) - selector(winner), 1)
    return (
        f"{runner_up.option.mode.value.replace('_', ' ').title()} was runner-up, "
        f"trailing by {difference} modeled points."
    )


def _base_estimate(route: RouteOption) -> str:
    if route.distance_miles:
        return f"{route.distance_miles:.1f} mi distance-aware demo estimate"
    return "Static demo estimate"


def _build_applied_preferences(
    request: CompareRoutesRequest,
    hidden_messages: list[str],
) -> list[str]:
    applied: list[str] = []
    if request.avoid_long_walks:
        applied.append("Avoid long walks increased walking penalties.")
    if request.avoid_transfers:
        applied.append("Avoid transfers increased subway transfer penalties.")
    if request.late_night_mode:
        applied.append("Late-night mode increased walking and Citi Bike exposure penalties.")
    if request.bad_weather_mode:
        applied.append("Bad weather increased walking and Citi Bike exposure penalties.")
    if request.max_rideshare_cost is not None:
        applied.append(f"Max rideshare cost set to ${request.max_rideshare_cost:.0f}.")
    applied.extend(hidden_messages)
    return applied


def _validate_request(request: CompareRoutesRequest) -> str | None:
    if not request.origin.strip() or not request.destination.strip():
        return "Please enter both an origin and a destination."

    origin_name = canonical_location_name(request.origin)
    destination_name = canonical_location_name(request.destination)
    if origin_name and destination_name and origin_name == destination_name:
        return "Origin and destination are the same. Choose two different Manhattan locations."

    if normalize_location_query(request.origin) == normalize_location_query(request.destination):
        return "Origin and destination are the same. Choose two different Manhattan locations."

    return None
