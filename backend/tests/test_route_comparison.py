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

    def test_max_rideshare_cost_filters_rideshare_options(self):
        response = compare_routes(make_request(max_rideshare_cost=10))

        modes = {card.mode for card in response.routeCards}

        self.assertNotIn(RouteMode.rideshare, modes)


if __name__ == "__main__":
    unittest.main()
