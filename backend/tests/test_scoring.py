import unittest

from app.domain.enums import PreferenceMode, RouteMode
from app.services.scoring import RouteOption, calculate_stress_score, score_routes, select_ranked_routes


def make_route(**overrides):
    defaults = {
        "id": "test",
        "mode": RouteMode.subway,
        "travel_time_minutes": 20,
        "estimated_cost": 2.9,
        "walking_minutes": 6,
        "transfers": 1,
        "wait_time_minutes": 4,
        "congestion_score": 3,
        "weather_penalty": 2,
        "late_night_walk_penalty": 2,
        "service_alert_penalty": 1,
        "summary": "Test route",
    }
    defaults.update(overrides)
    return RouteOption(**defaults)


class ScoringTests(unittest.TestCase):
    def test_stress_score_increases_for_long_walk_preference(self):
        route = make_route(walking_minutes=30)

        normal_score = calculate_stress_score(route)
        avoid_walk_score = calculate_stress_score(route, avoid_long_walks=True)

        self.assertGreater(avoid_walk_score, normal_score)

    def test_stress_score_increases_for_bad_weather(self):
        route = make_route(weather_penalty=7)

        normal_score = calculate_stress_score(route)
        weather_score = calculate_stress_score(route, bad_weather_mode=True)

        self.assertGreater(weather_score, normal_score)

    def test_ranked_routes_select_expected_winners(self):
        fast_expensive = make_route(
            id="fast",
            mode=RouteMode.rideshare,
            travel_time_minutes=12,
            estimated_cost=35,
            walking_minutes=2,
            transfers=0,
            wait_time_minutes=8,
            congestion_score=9,
            service_alert_penalty=4,
        )
        cheap_slow = make_route(id="cheap", mode=RouteMode.walking, travel_time_minutes=45, estimated_cost=0, walking_minutes=45, transfers=0)
        calm = make_route(id="calm", travel_time_minutes=22, estimated_cost=2.9, walking_minutes=5, transfers=0, wait_time_minutes=2, congestion_score=1)

        ranked = select_ranked_routes(score_routes([fast_expensive, cheap_slow, calm]))

        self.assertEqual(ranked[PreferenceMode.fastest].option.id, "fast")
        self.assertEqual(ranked[PreferenceMode.cheapest].option.id, "cheap")
        self.assertEqual(ranked[PreferenceMode.least_stressful].option.id, "calm")


if __name__ == "__main__":
    unittest.main()
