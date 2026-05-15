export type PreferenceMode = "fastest" | "cheapest" | "least_stressful" | "safety_aware";

export type RouteMode = "subway" | "walking" | "citi_bike" | "rideshare";

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
  label: string;
  mode: RouteMode;
  estimatedTime: number;
  estimatedCost: number;
  transfers: number;
  walkingMinutes: number;
  stressScore: number;
  reasons: string[];
};

export type CompareRoutesResponse = {
  supported: boolean;
  scopeMessage: string | null;
  requestedPreference: PreferenceMode;
  routeCards: RouteCard[];
};
