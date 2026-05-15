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

    def test_avoid_transfers_changes_subway_scores(self):
        route = make_route(transfers=2)

        normal_score = calculate_stress_score(route)
        avoid_transfer_score = calculate_stress_score(route, avoid_transfers=True)

        self.assertGreater(avoid_transfer_score, normal_score)

    def test_late_night_mode_penalizes_walking_and_biking_more_than_subway(self):
        subway = make_route(id="subway", mode=RouteMode.subway, late_night_walk_penalty=6)
        walking = make_route(id="walking", mode=RouteMode.walking, late_night_walk_penalty=6)
        bike = make_route(id="bike", mode=RouteMode.citi_bike, late_night_walk_penalty=6)

        subway_delta = calculate_stress_score(subway, late_night_mode=True) - calculate_stress_score(subway)
        walking_delta = calculate_stress_score(walking, late_night_mode=True) - calculate_stress_score(walking)
        bike_delta = calculate_stress_score(bike, late_night_mode=True) - calculate_stress_score(bike)

        self.assertGreater(walking_delta, subway_delta)
        self.assertGreater(bike_delta, subway_delta)

    def test_bad_weather_mode_penalizes_walking_and_biking_more_than_subway(self):
        subway = make_route(id="subway", mode=RouteMode.subway, weather_penalty=6)
        walking = make_route(id="walking", mode=RouteMode.walking, weather_penalty=6)
        bike = make_route(id="bike", mode=RouteMode.citi_bike, weather_penalty=6)

        subway_delta = calculate_stress_score(subway, bad_weather_mode=True) - calculate_stress_score(subway)
        walking_delta = calculate_stress_score(walking, bad_weather_mode=True) - calculate_stress_score(walking)
        bike_delta = calculate_stress_score(bike, bad_weather_mode=True) - calculate_stress_score(bike)

        self.assertGreater(walking_delta, subway_delta)
        self.assertGreater(bike_delta, subway_delta)

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

    def test_fastest_route_selection_uses_time_and_wait(self):
        faster_with_wait = make_route(id="short-wait-heavy", travel_time_minutes=10, wait_time_minutes=10)
        steadier = make_route(id="steady", travel_time_minutes=13, wait_time_minutes=0)

        ranked = select_ranked_routes(score_routes([faster_with_wait, steadier]))

        self.assertEqual(ranked[PreferenceMode.fastest].option.id, "steady")

    def test_cheapest_route_selection_uses_cost_and_transfer_penalty(self):
        free_with_many_transfers = make_route(id="free", estimated_cost=0, transfers=3)
        low_cost_direct = make_route(id="direct", estimated_cost=0.5, transfers=0)

        ranked = select_ranked_routes(score_routes([free_with_many_transfers, low_cost_direct]))

        self.assertEqual(ranked[PreferenceMode.cheapest].option.id, "direct")

    def test_safety_aware_route_selection_prioritizes_low_exposure(self):
        fast = make_route(
            id="fast",
            travel_time_minutes=8,
            estimated_cost=45,
            walking_minutes=15,
            wait_time_minutes=0,
            congestion_score=9,
            weather_penalty=5,
            late_night_walk_penalty=10,
            service_alert_penalty=5,
        )
        cheap = make_route(id="cheap", mode=RouteMode.walking, travel_time_minutes=50, estimated_cost=0, walking_minutes=50, transfers=0)
        calm = make_route(
            id="calm",
            travel_time_minutes=10,
            estimated_cost=3,
            walking_minutes=2,
            transfers=0,
            wait_time_minutes=0,
            congestion_score=0,
            weather_penalty=5,
            late_night_walk_penalty=5,
            service_alert_penalty=0,
        )
        safe = make_route(
            id="safe",
            travel_time_minutes=27,
            estimated_cost=8,
            walking_minutes=0,
            transfers=0,
            wait_time_minutes=0,
            congestion_score=0,
            weather_penalty=0,
            late_night_walk_penalty=0,
            service_alert_penalty=0,
        )

        ranked = select_ranked_routes(score_routes([fast, cheap, calm, safe]))

        self.assertEqual(ranked[PreferenceMode.fastest].option.id, "fast")
        self.assertEqual(ranked[PreferenceMode.cheapest].option.id, "cheap")
        self.assertEqual(ranked[PreferenceMode.least_stressful].option.id, "calm")
        self.assertEqual(ranked[PreferenceMode.safety_aware].option.id, "safe")

    def test_late_night_mode_increases_stress_penalty(self):
        route = make_route(late_night_walk_penalty=8)

        normal_score = calculate_stress_score(route)
        late_night_score = calculate_stress_score(route, late_night_mode=True)

        self.assertGreater(late_night_score, normal_score)


if __name__ == "__main__":
    unittest.main()
