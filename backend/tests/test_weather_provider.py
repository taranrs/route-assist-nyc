import os
import unittest
from unittest.mock import MagicMock, patch


def _make_weather_response(condition_id: int, condition_main: str, temp_f: float, wind_mph: float) -> dict:
    return {
        "weather": [{"id": condition_id, "main": condition_main, "description": condition_main.lower()}],
        "main": {"temp": temp_f, "feels_like": temp_f - 3, "humidity": 60},
        "wind": {"speed": wind_mph},
        "name": "New York",
    }


class WeatherProviderTests(unittest.TestCase):
    def setUp(self):
        os.environ["OPENWEATHER_API_KEY"] = "test-key"

    def tearDown(self):
        os.environ.pop("OPENWEATHER_API_KEY", None)

    def test_returns_unavailable_when_no_api_key(self):
        os.environ.pop("OPENWEATHER_API_KEY", None)

        from app.providers.weather_provider import get_weather

        result = get_weather(40.7580, -73.9855)

        self.assertFalse(result.available)
        self.assertFalse(result.is_bad_weather)

    @patch("app.providers.weather_provider.requests.get")
    def test_clear_weather_is_not_bad(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = _make_weather_response(800, "Clear", 72.0, 8.0)
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        from app.providers.weather_provider import get_weather

        result = get_weather(40.7580, -73.9855)

        self.assertTrue(result.available)
        self.assertFalse(result.is_bad_weather)
        self.assertEqual(result.condition, "clear")

    @patch("app.providers.weather_provider.requests.get")
    def test_rain_is_bad_weather(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = _make_weather_response(501, "Rain", 48.0, 12.0)
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        from app.providers.weather_provider import get_weather

        result = get_weather(40.7580, -73.9855)

        self.assertTrue(result.is_bad_weather)
        self.assertEqual(result.condition, "rain")

    @patch("app.providers.weather_provider.requests.get")
    def test_thunderstorm_is_bad_weather(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = _make_weather_response(211, "Thunderstorm", 60.0, 20.0)
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        from app.providers.weather_provider import get_weather

        result = get_weather(40.7580, -73.9855)

        self.assertTrue(result.is_bad_weather)

    @patch("app.providers.weather_provider.requests.get")
    def test_high_wind_triggers_bad_weather(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = _make_weather_response(800, "Clear", 65.0, 30.0)
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        from app.providers.weather_provider import get_weather

        result = get_weather(40.7580, -73.9855)

        self.assertTrue(result.is_bad_weather)
        self.assertGreaterEqual(result.wind_speed_mph, 25.0)

    @patch("app.providers.weather_provider.requests.get")
    def test_snow_is_bad_weather(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = _make_weather_response(601, "Snow", 28.0, 10.0)
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        from app.providers.weather_provider import get_weather

        result = get_weather(40.7580, -73.9855)

        self.assertTrue(result.is_bad_weather)
        self.assertEqual(result.condition, "snow")

    @patch("app.providers.weather_provider.requests.get")
    def test_returns_unavailable_on_http_error(self, mock_get):
        import requests as req

        mock_get.side_effect = req.exceptions.ConnectionError("timeout")

        from app.providers.weather_provider import get_weather

        result = get_weather(40.7580, -73.9855)

        self.assertFalse(result.available)
        self.assertFalse(result.is_bad_weather)

    @patch("app.providers.weather_provider.requests.get")
    def test_api_key_sent_as_param(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = _make_weather_response(800, "Clear", 70.0, 5.0)
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        from app.providers.weather_provider import get_weather

        get_weather(40.7580, -73.9855)

        call_kwargs = mock_get.call_args
        self.assertEqual(call_kwargs.kwargs["params"]["appid"], "test-key")
        self.assertEqual(call_kwargs.kwargs["params"]["units"], "imperial")


if __name__ == "__main__":
    unittest.main()
