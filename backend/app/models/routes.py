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
    availabilityScore: float = 0.0
    finalStressScore: float
    safetyAwareScore: float


class ProviderStatus(BaseModel):
    mta_alerts_live: bool = False
    mta_alert_count: int = 0
    affected_subway_lines: list[str] = []
    citibike_live: bool = False
    origin_bikes_available: int | None = None
    destination_docks_available: int | None = None
    weather_live: bool = False
    weather_condition: str | None = None
    effective_bad_weather: bool = False


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
    providerStatus: ProviderStatus = Field(default_factory=ProviderStatus)
