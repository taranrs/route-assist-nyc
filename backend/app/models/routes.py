from pydantic import BaseModel, Field

from app.domain.enums import PreferenceMode, RouteMode


class CompareRoutesRequest(BaseModel):
    origin: str
    destination: str
    departure_time: str = Field(..., description="Local departure time in HH:MM format")
    preference_mode: PreferenceMode = PreferenceMode.fastest
    avoid_long_walks: bool = False
    avoid_transfers: bool = False
    late_night_mode: bool = False
    bad_weather_mode: bool = False
    max_rideshare_cost: float | None = Field(default=None, ge=0)


class ScoreBreakdown(BaseModel):
    fastestScore: float
    cheapestScore: float
    timeScore: float
    costScore: float
    walkingScore: float
    transferScore: float
    waitScore: float
    congestionScore: float
    weatherScore: float
    lateNightScore: float
    serviceAlertScore: float
    finalStressScore: float
    safetyAwareScore: float


class RouteCard(BaseModel):
    routeId: str
    label: str
    mode: RouteMode
    estimatedTime: int
    estimatedCost: float
    transfers: int
    walkingMinutes: int
    distanceMiles: float
    walkingDistanceMiles: float
    bikingDistanceMiles: float | None = None
    drivingDistanceMiles: float | None = None
    averageSpeedMph: float
    demoEstimate: bool
    stressScore: float
    fastestScore: float
    cheapestScore: float
    safetyAwareScore: float
    baseEstimate: str
    routeSummary: str
    routeComplexity: str
    stationComplexity: str | None = None
    modeTradeoffSummary: str
    majorDecisionFactors: list[str]
    majorPenalties: list[str]
    scoreBreakdown: ScoreBreakdown
    reasons: list[str]
    recommendationReason: str | None = None
    runnerUpMode: RouteMode | None = None
    runnerUpReason: str | None = None


class CompareRoutesResponse(BaseModel):
    supported: bool
    scopeMessage: str | None = None
    validationMessage: str | None = None
    requestedPreference: PreferenceMode
    recommendations: list[RouteCard]
    allOptions: list[RouteCard]
    appliedPreferences: list[str]
    hiddenOptionsMessages: list[str] = []
    routeCards: list[RouteCard]
