import os
import time
import unittest
from unittest.mock import MagicMock, patch


def _build_feed_bytes(route_ids: list[str]) -> bytes:
    from google.transit import gtfs_realtime_pb2

    feed = gtfs_realtime_pb2.FeedMessage()
    feed.header.gtfs_realtime_version = "2.0"
    feed.header.timestamp = int(time.time())
    if route_ids:
        entity = feed.entity.add()
        entity.id = "alert-1"
        for route_id in route_ids:
            informed = entity.alert.informed_entity.add()
            informed.route_id = route_id
        entity.alert.header_text.translation.add().text = "Test alert"
    return feed.SerializeToString()


class MTAProviderTests(unittest.TestCase):
    def setUp(self):
        os.environ["MTA_API_KEY"] = "test-key"

    def tearDown(self):
        os.environ.pop("MTA_API_KEY", None)

    def test_returns_empty_when_no_api_key(self):
        os.environ.pop("MTA_API_KEY", None)

        from app.providers.mta_provider import get_subway_alerts

        result = get_subway_alerts()

        self.assertFalse(result.has_alerts)
        self.assertEqual(result.alert_count, 0)
        self.assertEqual(len(result.affected_route_ids), 0)

    @patch("app.providers.mta_provider.requests.get")
    def test_parses_affected_route_ids(self, mock_get):
        mock_response = MagicMock()
        mock_response.content = _build_feed_bytes(["A", "C", "E"])
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        from app.providers.mta_provider import get_subway_alerts

        result = get_subway_alerts()

        self.assertTrue(result.has_alerts)
        self.assertEqual(result.alert_count, 1)
        self.assertIn("A", result.affected_route_ids)
        self.assertIn("C", result.affected_route_ids)
        self.assertIn("E", result.affected_route_ids)

    @patch("app.providers.mta_provider.requests.get")
    def test_route_ids_are_uppercased(self, mock_get):
        mock_response = MagicMock()
        mock_response.content = _build_feed_bytes(["l", "n", "q"])
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        from app.providers.mta_provider import get_subway_alerts

        result = get_subway_alerts()

        self.assertIn("L", result.affected_route_ids)
        self.assertIn("N", result.affected_route_ids)

    @patch("app.providers.mta_provider.requests.get")
    def test_returns_empty_on_http_error(self, mock_get):
        import requests as req

        mock_get.side_effect = req.exceptions.ConnectionError("timeout")

        from app.providers.mta_provider import get_subway_alerts

        result = get_subway_alerts()

        self.assertFalse(result.has_alerts)
        self.assertEqual(result.alert_count, 0)

    @patch("app.providers.mta_provider.requests.get")
    def test_api_key_sent_in_header(self, mock_get):
        mock_response = MagicMock()
        mock_response.content = _build_feed_bytes([])
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        from app.providers.mta_provider import get_subway_alerts

        get_subway_alerts()

        call_kwargs = mock_get.call_args
        self.assertEqual(call_kwargs.kwargs["headers"]["x-api-key"], "test-key")

    @patch("app.providers.mta_provider.requests.get")
    def test_empty_feed_returns_no_alerts(self, mock_get):
        mock_response = MagicMock()
        mock_response.content = _build_feed_bytes([])
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        from app.providers.mta_provider import get_subway_alerts

        result = get_subway_alerts()

        self.assertFalse(result.has_alerts)
        self.assertEqual(result.alert_count, 0)


if __name__ == "__main__":
    unittest.main()
