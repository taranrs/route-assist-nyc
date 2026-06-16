from __future__ import annotations

import os
from dataclasses import dataclass

import requests

MTA_ALERTS_URL = (
    "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/camsys%2Fsubway-alerts"
)
_REQUEST_TIMEOUT = 5


@dataclass(frozen=True)
class MTAAlertSummary:
    has_alerts: bool
    affected_route_ids: frozenset[str]
    alert_count: int

    @classmethod
    def empty(cls) -> MTAAlertSummary:
        return cls(has_alerts=False, affected_route_ids=frozenset(), alert_count=0)


def get_subway_alerts() -> MTAAlertSummary:
    api_key = os.environ.get("MTA_API_KEY")
    if not api_key:
        return MTAAlertSummary.empty()
    try:
        return _fetch_alerts(api_key)
    except Exception:
        return MTAAlertSummary.empty()


def _fetch_alerts(api_key: str) -> MTAAlertSummary:
    from google.transit import gtfs_realtime_pb2

    response = requests.get(
        MTA_ALERTS_URL,
        headers={"x-api-key": api_key},
        timeout=_REQUEST_TIMEOUT,
    )
    response.raise_for_status()

    feed = gtfs_realtime_pb2.FeedMessage()
    feed.ParseFromString(response.content)

    affected: set[str] = set()
    alert_count = 0

    for entity in feed.entity:
        if entity.HasField("alert"):
            alert_count += 1
            for informed in entity.alert.informed_entity:
                if informed.route_id:
                    affected.add(informed.route_id.upper())

    return MTAAlertSummary(
        has_alerts=alert_count > 0,
        affected_route_ids=frozenset(affected),
        alert_count=alert_count,
    )
