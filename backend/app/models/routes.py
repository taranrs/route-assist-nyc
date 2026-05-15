from pydantic import BaseModel, Field

from app.domain.enums import PreferenceMode, RouteMode


class CompareRoutesRequest(BaseModel):
    origin: str = Field(..., min_length=2)
    destination: str = Field(..., min_length=2)
    departure_time: str = Field(..., description="Local departure time in HH:MM format")
    preference_mode: PreferenceMode = PreferenceMode.fastest
    avoid_long_walks: bool = False
    avoid_transfers: bool = False
    late_night_mode: bool = False
    bad_weather_mode: bool = False
    max_rideshare_cost: float | None = Field(default=None, ge=0)


class RouteCard(BaseModel):
    label: str
    mode: RouteMode
    estimatedTime: int
    estimatedCost: float
    transfers: int
    walkingMinutes: int
    stressScore: float
    baseEstimate: str
    majorPenalties: list[str]
    reasons: list[str]
    recommendationReason: str | None = None
    runnerUpMode: RouteMode | None = None
    runnerUpReason: str | None = None


class CompareRoutesResponse(BaseModel):
    supported: bool
    scopeMessage: str | None = None
    requestedPreference: PreferenceMode
    recommendations: list[RouteCard]
    allOptions: list[RouteCard]
    appliedPreferences: list[str]
    hiddenOptionsMessages: list[str] = []
    routeCards: list[RouteCard]
