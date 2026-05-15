from enum import Enum


class PreferenceMode(str, Enum):
    fastest = "fastest"
    cheapest = "cheapest"
    least_stressful = "least_stressful"
    safety_aware = "safety_aware"


class RouteMode(str, Enum):
    subway = "subway"
    walking = "walking"
    citi_bike = "citi_bike"
    rideshare = "rideshare"
