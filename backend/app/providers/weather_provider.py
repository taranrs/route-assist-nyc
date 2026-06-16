from __future__ import annotations

import os
from dataclasses import dataclass

import requests

_OPENWEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"
_REQUEST_TIMEOUT = 5

_BAD_WEATHER_CODES: frozenset[int] = frozenset(
    [
        *range(200, 233),  # thunderstorm
        *range(300, 322),  # drizzle
        *range(500, 532),  # rain
        *range(600, 623),  # snow
        900, 901, 902, 905, 958, 959,  # extreme
    ]
)
_HIGH_WIND_MPH = 25.0


@dataclass(frozen=True)
class WeatherStatus:
    available: bool
    condition: str
    condition_code: int
    temperature_f: float
    wind_speed_mph: float
    is_bad_weather: bool

    @classmethod
    def unavailable(cls) -> WeatherStatus:
        return cls(
            available=False,
            condition="unknown",
            condition_code=800,
            temperature_f=65.0,
            wind_speed_mph=0.0,
            is_bad_weather=False,
        )


def get_weather(lat: float, lon: float) -> WeatherStatus:
    api_key = os.environ.get("OPENWEATHER_API_KEY")
    if not api_key:
        return WeatherStatus.unavailable()
    try:
        return _fetch_weather(lat, lon, api_key)
    except Exception:
        return WeatherStatus.unavailable()


def _fetch_weather(lat: float, lon: float, api_key: str) -> WeatherStatus:
    response = requests.get(
        _OPENWEATHER_URL,
        params={"lat": lat, "lon": lon, "appid": api_key, "units": "imperial"},
        timeout=_REQUEST_TIMEOUT,
    )
    response.raise_for_status()
    data = response.json()

    weather = data["weather"][0]
    condition_code: int = weather["id"]
    condition: str = weather["main"].lower()
    temp_f: float = data["main"]["temp"]
    wind_mph: float = data["wind"]["speed"]

    is_bad = condition_code in _BAD_WEATHER_CODES or wind_mph >= _HIGH_WIND_MPH

    return WeatherStatus(
        available=True,
        condition=condition,
        condition_code=condition_code,
        temperature_f=temp_f,
        wind_speed_mph=wind_mph,
        is_bad_weather=is_bad,
    )
