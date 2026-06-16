import unittest
from unittest.mock import MagicMock, patch


def _make_station_info(stations: list[dict]) -> dict:
    return {"data": {"stations": stations}}


def _make_station_status(statuses: list[dict]) -> dict:
    return {"data": {"stations": statuses}}


TIMES_SQUARE_LAT = 40.7580
TIMES_SQUARE_LON = -73.9855


class CitiBikeProviderTests(unittest.TestCase):
    def _mock_responses(self, stations: list[dict], statuses: list[dict]):
        info_resp = MagicMock()
        info_resp.json.return_value = _make_station_info(stations)
        info_resp.raise_for_status = MagicMock()

        status_resp = MagicMock()
        status_resp.json.return_value = _make_station_status(statuses)
        status_resp.raise_for_status = MagicMock()

        return [info_resp, status_resp]

    @patch("app.providers.citibike_provider.requests.get")
    def test_finds_station_near_origin(self, mock_get):
        stations = [
            {
                "station_id": "s1",
                "name": "W 42 St & 8 Ave",
                "lat": TIMES_SQUARE_LAT + 0.001,
                "lon": TIMES_SQUARE_LON + 0.001,
            }
        ]
        statuses = [
            {
                "station_id": "s1",
                "num_bikes_available": 5,
                "num_ebikes_available": 2,
                "num_docks_available": 10,
            }
        ]
        mock_get.side_effect = self._mock_responses(stations, statuses)

        from app.providers.citibike_provider import get_citibike_status

        result = get_citibike_status(
            TIMES_SQUARE_LAT, TIMES_SQUARE_LON,
            40.7060, -74.0086,
        )

        self.assertTrue(result.found_origin)
        self.assertEqual(result.origin_bikes_available, 5)
        self.assertEqual(result.origin_ebikes_available, 2)
        self.assertEqual(result.origin_total_bikes, 7)

    @patch("app.providers.citibike_provider.requests.get")
    def test_no_station_found_when_too_far(self, mock_get):
        stations = [
            {
                "station_id": "s1",
                "name": "Far Away Station",
                "lat": 40.6000,
                "lon": -74.1000,
            }
        ]
        statuses = [{"station_id": "s1", "num_bikes_available": 5, "num_ebikes_available": 0, "num_docks_available": 5}]
        mock_get.side_effect = self._mock_responses(stations, statuses)

        from app.providers.citibike_provider import get_citibike_status

        result = get_citibike_status(TIMES_SQUARE_LAT, TIMES_SQUARE_LON, 40.7060, -74.0086)

        self.assertFalse(result.found_origin)
        self.assertEqual(result.origin_bikes_available, 0)

    @patch("app.providers.citibike_provider.requests.get")
    def test_returns_unavailable_on_http_error(self, mock_get):
        import requests as req

        mock_get.side_effect = req.exceptions.ConnectionError("timeout")

        from app.providers.citibike_provider import get_citibike_status

        result = get_citibike_status(TIMES_SQUARE_LAT, TIMES_SQUARE_LON, 40.7060, -74.0086)

        self.assertFalse(result.found_origin)
        self.assertFalse(result.found_destination)

    @patch("app.providers.citibike_provider.requests.get")
    def test_destination_docks_available(self, mock_get):
        stations = [
            {
                "station_id": "s1",
                "name": "Origin Station",
                "lat": TIMES_SQUARE_LAT + 0.0005,
                "lon": TIMES_SQUARE_LON + 0.0005,
            },
            {
                "station_id": "s2",
                "name": "Dest Station",
                "lat": 40.7060 + 0.0005,
                "lon": -74.0086 + 0.0005,
            },
        ]
        statuses = [
            {"station_id": "s1", "num_bikes_available": 3, "num_ebikes_available": 0, "num_docks_available": 5},
            {"station_id": "s2", "num_bikes_available": 0, "num_ebikes_available": 0, "num_docks_available": 8},
        ]
        mock_get.side_effect = self._mock_responses(stations, statuses)

        from app.providers.citibike_provider import get_citibike_status

        result = get_citibike_status(TIMES_SQUARE_LAT, TIMES_SQUARE_LON, 40.7060, -74.0086)

        self.assertTrue(result.found_destination)
        self.assertEqual(result.destination_docks_available, 8)

    @patch("app.providers.citibike_provider.requests.get")
    def test_station_missing_from_status_is_skipped(self, mock_get):
        stations = [
            {
                "station_id": "orphan",
                "name": "Orphan Station",
                "lat": TIMES_SQUARE_LAT + 0.001,
                "lon": TIMES_SQUARE_LON + 0.001,
            }
        ]
        statuses: list[dict] = []
        mock_get.side_effect = self._mock_responses(stations, statuses)

        from app.providers.citibike_provider import get_citibike_status

        result = get_citibike_status(TIMES_SQUARE_LAT, TIMES_SQUARE_LON, 40.7060, -74.0086)

        self.assertFalse(result.found_origin)


if __name__ == "__main__":
    unittest.main()
