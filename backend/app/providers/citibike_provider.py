from __future__ import annotations

import math
from dataclasses import dataclass

import requests

_STATION_INFO_URL = "https://gbfs.citibikenyc.com/gbfs/en/station_information.json"
_STATION_STATUS_URL = "https://gbfs.citibikenyc.com/gbfs/en/station_status.json"
_REQUEST_TIMEOUT = 4
_SEARCH_RADIUS_MILES = 0.35


@dataclass(frozen=True)
class CitiBikeStatus:
    found_origin: bool
    found_destination: bool
    origin_station_name: str | None
    origin_bikes_available: int
    origin_ebikes_available: int
    destination_station_name: str | None
    destination_docks_available: int

    @classmethod
    def unavailable(cls) -> CitiBikeStatus:
        return cls(
            found_origin=False,
            found_destination=False,
            origin_station_name=None,
            origin_bikes_available=0,
            origin_ebikes_available=0,
            destination_station_name=None,
            destination_docks_available=0,
        )

    @property
    def origin_total_bikes(self) -> int:
        return self.origin_bikes_available + self.origin_ebikes_available


def get_citibike_status(
    origin_lat: float,
    origin_lon: float,
    destination_lat: float,
    destination_lon: float,
) -> CitiBikeStatus:
    try:
        return _fetch_status(origin_lat, origin_lon, destination_lat, destination_lon)
    except Exception:
        return CitiBikeStatus.unavailable()


def _fetch_status(
    origin_lat: float,
    origin_lon: float,
    destination_lat: float,
    destination_lon: float,
) -> CitiBikeStatus:
    info_resp = requests.get(_STATION_INFO_URL, timeout=_REQUEST_TIMEOUT)
    info_resp.raise_for_status()
    status_resp = requests.get(_STATION_STATUS_URL, timeout=_REQUEST_TIMEOUT)
    status_resp.raise_for_status()

    stations: list[dict] = info_resp.json()["data"]["stations"]
    statuses: dict[str, dict] = {
        s["station_id"]: s for s in status_resp.json()["data"]["stations"]
    }

    origin_match = _nearest_station(stations, statuses, origin_lat, origin_lon)
    dest_match = _nearest_station(stations, statuses, destination_lat, destination_lon)

    return CitiBikeStatus(
        found_origin=origin_match is not None,
        found_destination=dest_match is not None,
        origin_station_name=origin_match["info"]["name"] if origin_match else None,
        origin_bikes_available=(
            origin_match["status"].get("num_bikes_available", 0) if origin_match else 0
        ),
        origin_ebikes_available=(
            origin_match["status"].get("num_ebikes_available", 0) if origin_match else 0
        ),
        destination_station_name=dest_match["info"]["name"] if dest_match else None,
        destination_docks_available=(
            dest_match["status"].get("num_docks_available", 0) if dest_match else 0
        ),
    )


def _nearest_station(
    stations: list[dict],
    statuses: dict[str, dict],
    lat: float,
    lon: float,
) -> dict | None:
    closest: dict | None = None
    closest_dist = float("inf")

    for station in stations:
        dist = _haversine_miles(lat, lon, station["lat"], station["lon"])
        if dist < closest_dist and dist <= _SEARCH_RADIUS_MILES:
            station_id = station["station_id"]
            if station_id in statuses:
                closest = {"info": station, "status": statuses[station_id]}
                closest_dist = dist

    return closest


def _haversine_miles(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 3958.8
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlon / 2) ** 2
    )
    return 2 * r * math.asin(math.sqrt(a))
