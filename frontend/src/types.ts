export type PreferenceMode = "fastest" | "cheapest" | "least_stressful" | "safety_aware";

export type RouteMode = "subway" | "walking" | "citi_bike" | "rideshare";

export type ScoreBreakdown = {
  fastestScore: number;
  cheapestScore: number;
  timeScore: number;
  costScore: number;
  walkingScore: number;
  transferScore: number;
  waitScore: number;
  congestionScore: number;
  weatherScore: number;
  lateNightScore: number;
  serviceAlertScore: number;
  finalStressScore: number;
  safetyAwareScore: number;
};

export type CompareRoutesRequest = {
  origin: string;
  destination: string;
  departure_time: string;
  preference_mode: PreferenceMode;
  avoid_long_walks: boolean;
  avoid_transfers: boolean;
  late_night_mode: boolean;
  bad_weather_mode: boolean;
  max_rideshare_cost: number | null;
};

export type RouteCard = {
  routeId: string;
  label: string;
  mode: RouteMode;
  estimatedTime: number;
  estimatedCost: number;
  transfers: number;
  walkingMinutes: number;
  distanceMiles: number;
  walkingDistanceMiles: number;
  bikingDistanceMiles: number | null;
  drivingDistanceMiles: number | null;
  averageSpeedMph: number;
  demoEstimate: boolean;
  stressScore: number;
  fastestScore: number;
  cheapestScore: number;
  safetyAwareScore: number;
  baseEstimate: string;
  routeSummary: string;
  routeComplexity: string;
  stationComplexity: string | null;
  modeTradeoffSummary: string;
  majorDecisionFactors: string[];
  majorPenalties: string[];
  scoreBreakdown: ScoreBreakdown;
  reasons: string[];
  recommendationReason: string | null;
  runnerUpMode: RouteMode | null;
  runnerUpReason: string | null;
};

export type CompareRoutesResponse = {
  supported: boolean;
  scopeMessage: string | null;
  validationMessage: string | null;
  requestedPreference: PreferenceMode;
  recommendations: RouteCard[];
  allOptions: RouteCard[];
  appliedPreferences: string[];
  hiddenOptionsMessages: string[];
  routeCards: RouteCard[];
};
