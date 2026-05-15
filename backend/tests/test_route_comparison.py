import unittest

from app.domain.enums import PreferenceMode, RouteMode
from app.models.routes import CompareRoutesRequest
from app.services.route_comparison import compare_routes
from app.services.scope import SUPPORTED_SCOPE_MESSAGE


def make_request(**overrides) -> CompareRoutesRequest:
    defaults = {
        "origin": "Union Square",
        "destination": "Chelsea",
        "departure_time": "22:30",
        "preference_mode": PreferenceMode.fastest,
        "avoid_long_walks": False,
        "avoid_transfers": False,
        "late_night_mode": False,
        "bad_weather_mode": False,
        "max_rideshare_cost": None,
    }
    defaults.update(overrides)
    return CompareRoutesRequest(**defaults)


class RouteComparisonTests(unittest.TestCase):
    def test_returns_all_route_card_labels(self):
        response = compare_routes(make_request())

        labels = {card.label for card in response.routeCards}

        self.assertTrue(response.supported)
        self.assertEqual(labels, {"Fastest", "Cheapest", "Least stressful", "Safety-aware"})

    def test_requested_preference_card_is_returned_first(self):
        response = compare_routes(make_request(preference_mode=PreferenceMode.safety_aware))

        self.assertEqual(response.routeCards[0].label, "Safety-aware")

    def test_unsupported_non_manhattan_route_returns_scope_message(self):
        response = compare_routes(make_request(origin="Times Square", destination="Brooklyn"))

        self.assertFalse(response.supported)
        self.assertEqual(response.scopeMessage, SUPPORTED_SCOPE_MESSAGE)
        self.assertEqual(response.routeCards, [])
        self.assertEqual(response.recommendations, [])
        self.assertEqual(response.allOptions, [])

    def test_lowercase_and_alias_inputs_match_mocked_route_pair(self):
        response = compare_routes(make_request(origin="time square", destination="wall st"))

        self.assertTrue(response.supported)
        self.assertEqual(response.routeCards[0].label, "Fastest")
        self.assertEqual(response.routeCards[0].mode, RouteMode.subway)

    def test_unknown_manhattan_route_uses_generic_fallback(self):
        response = compare_routes(make_request(origin="Empire State Building", destination="Battery Park"))

        self.assertTrue(response.supported)
        self.assertIsNone(response.scopeMessage)
        self.assertEqual(len(response.recommendations), 4)
        self.assertEqual(len(response.allOptions), 4)
        self.assertTrue(any("Demo" in reason for card in response.allOptions for reason in card.reasons))

    def test_generic_recognized_manhattan_routes_generate_all_four_modes(self):
        response = compare_routes(make_request(origin="Bryant Park", destination="Tribeca"))

        modes = {card.mode for card in response.allOptions}

        self.assertEqual(modes, {RouteMode.subway, RouteMode.walking, RouteMode.citi_bike, RouteMode.rideshare})

    def test_recommendations_and_all_options_both_exist(self):
        response = compare_routes(make_request(origin="Empire State Building", destination="Battery Park"))

        self.assertEqual(len(response.recommendations), 4)
        self.assertGreaterEqual(len(response.allOptions), 3)
        self.assertEqual(response.routeCards, response.recommendations)

    def test_max_rideshare_cost_filters_rideshare_options(self):
        response = compare_routes(make_request(max_rideshare_cost=10))

        modes = {card.mode for card in response.allOptions}

        self.assertNotIn(RouteMode.rideshare, modes)
        self.assertTrue(response.hiddenOptionsMessages)
        self.assertTrue(any("Rideshare hidden" in message for message in response.appliedPreferences))

    def test_all_options_always_include_available_modes(self):
        response = compare_routes(make_request(origin="Union Square", destination="Chelsea"))

        modes = {card.mode for card in response.allOptions}

        self.assertEqual(modes, {RouteMode.subway, RouteMode.walking, RouteMode.citi_bike, RouteMode.rideshare})

    def test_commuter_and_outer_borough_markers_stay_unsupported(self):
        for destination in ("Long Island", "New Jersey", "Queens", "Bronx", "Staten Island"):
            with self.subTest(destination=destination):
                response = compare_routes(make_request(origin="Penn Station", destination=destination))

                self.assertFalse(response.supported)
                self.assertEqual(response.scopeMessage, SUPPORTED_SCOPE_MESSAGE)


if __name__ == "__main__":
    unittest.main()
