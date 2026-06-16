import React from "react";
import ReactDOM from "react-dom/client";
import { Bike, Car, Footprints, TrainFront, Umbrella, Moon, ArrowRight } from "lucide-react";
import { compareRoutesRequest } from "./api";
import { findLocationSuggestions } from "./locations";
import "./styles.css";
import type { CompareRoutesRequest, CompareRoutesResponse, PreferenceMode, RouteCard, RouteMode } from "./types";

const examples = [
  ["Penn Station", "Washington Square Park"],
  ["Times Square", "Wall Street"],
  ["Grand Central", "Columbia University"],
  ["Union Square", "Chelsea"],
  ["World Trade Center", "Times Square"]
];

const preferenceLabels: Record<PreferenceMode, string> = {
  fastest: "Fastest",
  cheapest: "Cheapest",
  least_stressful: "Least stressful",
  safety_aware: "Safety-aware"
};

const recommendationSubheads: Record<string, string> = {
  Fastest: "Best for speed",
  Cheapest: "Best for cost",
  "Least stressful": "Best for low stress",
  "Safety-aware": "Best for safety-aware preference"
};

const modeIcons: Record<RouteMode, React.ReactNode> = {
  subway: <TrainFront size={20} />,
  walking: <Footprints size={20} />,
  citi_bike: <Bike size={20} />,
  rideshare: <Car size={20} />
};

function App() {
  const [origin, setOrigin] = React.useState("Penn Station");
  const [destination, setDestination] = React.useState("Washington Square Park");
  const [departureTime, setDepartureTime] = React.useState("08:30");
  const [preferenceMode, setPreferenceMode] = React.useState<PreferenceMode>("fastest");
  const [avoidLongWalks, setAvoidLongWalks] = React.useState(true);
  const [avoidTransfers, setAvoidTransfers] = React.useState(false);
  const [lateNightMode, setLateNightMode] = React.useState(false);
  const [badWeatherMode, setBadWeatherMode] = React.useState(false);
  const [maxRideshareCost, setMaxRideshareCost] = React.useState("35");
  const [focusedLocationField, setFocusedLocationField] = React.useState<"origin" | "destination" | null>(null);
  const [data, setData] = React.useState<CompareRoutesResponse | null>(null);
  const [selectedRouteId, setSelectedRouteId] = React.useState<string | null>(null);
  const [loading, setLoading] = React.useState(false);
  const [error, setError] = React.useState("");

  async function compareRoutes(event?: React.FormEvent) {
    event?.preventDefault();
    setError("");

    const validationMessage = validateForm(origin, destination);
    if (validationMessage) {
      setData(null);
      setSelectedRouteId(null);
      setError(validationMessage);
      return;
    }

    setLoading(true);

    try {
      const payload: CompareRoutesRequest = {
        origin,
        destination,
        departure_time: departureTime,
        preference_mode: preferenceMode,
        avoid_long_walks: avoidLongWalks,
        avoid_transfers: avoidTransfers,
        late_night_mode: lateNightMode,
        bad_weather_mode: badWeatherMode,
        max_rideshare_cost: maxRideshareCost ? Number(maxRideshareCost) : null
      };

      const response = await compareRoutesRequest(payload);
      setData(response);
      setSelectedRouteId(response.recommendations[0]?.routeId ?? response.allOptions[0]?.routeId ?? null);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Something went wrong.");
    } finally {
      setLoading(false);
    }
  }

  React.useEffect(() => {
    void compareRoutes();
  }, []);

  const selectedRoute = React.useMemo(() => {
    if (!data || !selectedRouteId) {
      return null;
    }
    return [...data.recommendations, ...data.allOptions].find((route) => route.routeId === selectedRouteId) ?? null;
  }, [data, selectedRouteId]);

  return (
    <main className="min-h-screen bg-zinc-950 text-zinc-100">
      <section className="border-b border-zinc-800 bg-zinc-900">
        <div className="mx-auto grid max-w-7xl gap-8 px-5 py-8 lg:grid-cols-[0.95fr_1.25fr]">
          <div>
            <p className="text-sm font-semibold uppercase tracking-[0.18em] text-emerald-300">Manhattan MVP</p>
            <h1 className="mt-3 text-4xl font-semibold tracking-normal text-white md:text-5xl">RouteAssist NYC</h1>
            <p className="mt-4 max-w-xl text-base leading-7 text-zinc-300">
              Compare route choices by time, cost, transfers, walking exposure, weather, congestion, and stress.
            </p>
          </div>

          <form onSubmit={compareRoutes} className="rounded-lg border border-zinc-800 bg-zinc-950 p-5 shadow-2xl shadow-black/20">
            <div className="grid gap-4 md:grid-cols-2">
              <LocationField
                label="Origin"
                value={origin}
                focused={focusedLocationField === "origin"}
                onFocus={() => setFocusedLocationField("origin")}
                onBlur={() => setTimeout(() => setFocusedLocationField(null), 120)}
                onChange={setOrigin}
              />
              <LocationField
                label="Destination"
                value={destination}
                focused={focusedLocationField === "destination"}
                onFocus={() => setFocusedLocationField("destination")}
                onBlur={() => setTimeout(() => setFocusedLocationField(null), 120)}
                onChange={setDestination}
              />
              <label className="space-y-2">
                <span className="text-sm text-zinc-300">Departure time</span>
                <input className="control" type="time" value={departureTime} onChange={(event) => setDepartureTime(event.target.value)} />
              </label>
              <label className="space-y-2">
                <span className="text-sm text-zinc-300">Preference</span>
                <select className="control" value={preferenceMode} onChange={(event) => setPreferenceMode(event.target.value as PreferenceMode)}>
                  {Object.entries(preferenceLabels).map(([value, label]) => (
                    <option key={value} value={value}>{label}</option>
                  ))}
                </select>
              </label>
              <label className="space-y-2">
                <span className="text-sm text-zinc-300">Max rideshare cost</span>
                <input className="control" type="number" min="0" value={maxRideshareCost} onChange={(event) => setMaxRideshareCost(event.target.value)} />
              </label>
            </div>

            <div className="mt-5 grid gap-3 sm:grid-cols-2">
              <Toggle label="Avoid long walks" checked={avoidLongWalks} onChange={setAvoidLongWalks} />
              <Toggle label="Avoid transfers" checked={avoidTransfers} onChange={setAvoidTransfers} />
              <Toggle label="Late-night mode" checked={lateNightMode} onChange={setLateNightMode} icon={<Moon size={16} />} />
              <Toggle label="Bad weather mode" checked={badWeatherMode} onChange={setBadWeatherMode} icon={<Umbrella size={16} />} />
            </div>

            <div className="mt-5 flex flex-wrap items-center gap-3">
              <button className="inline-flex h-11 items-center gap-2 rounded-md bg-emerald-400 px-4 font-semibold text-zinc-950 transition hover:bg-emerald-300" type="submit">
                Compare <ArrowRight size={18} />
              </button>
              <div className="flex flex-wrap gap-2">
                {examples.map(([exampleOrigin, exampleDestination]) => (
                  <button
                    key={`${exampleOrigin}-${exampleDestination}`}
                    type="button"
                    className="rounded-md border border-zinc-700 px-3 py-2 text-xs text-zinc-300 hover:border-emerald-400 hover:text-white"
                    onClick={() => {
                      setOrigin(exampleOrigin);
                      setDestination(exampleDestination);
                    }}
                  >
                    {exampleOrigin} to {exampleDestination}
                  </button>
                ))}
              </div>
            </div>
          </form>
        </div>
      </section>

      <section className="mx-auto max-w-7xl px-5 py-8">
        <div className="mb-5 rounded-lg border border-sky-800 bg-sky-950/40 p-4 text-sm leading-6 text-sky-100">
          <span className="font-semibold text-white">Demo mode:</span> route times, costs, congestion, and availability are mocked estimates. Real Mapbox, MTA, Citi Bike, and weather data will be added later.
        </div>
        {error && <div className="rounded-lg border border-red-800 bg-red-950/50 p-4 text-red-100">{error}</div>}
        {data?.validationMessage && <div className="rounded-lg border border-amber-700 bg-amber-950/50 p-4 text-amber-100">{data.validationMessage}</div>}
        {data?.scopeMessage && <div className="rounded-lg border border-amber-700 bg-amber-950/50 p-4 text-amber-100">{data.scopeMessage}</div>}
        {loading && <DashboardState title="Comparing route options..." body="Scoring mocked Manhattan choices by time, cost, walking, transfers, weather, congestion, and stress." />}
        {!loading && !error && data?.supported && data.routeCards.length === 0 && (
          <DashboardState title="No route cards available" body="Try one of the Manhattan example routes above." />
        )}
        {!loading && !error && !data && (
          <DashboardState title="Ready to compare" body="Enter a Manhattan origin and destination to see ranked route cards." />
        )}
        {!loading && data?.supported && data.recommendations.length > 0 && (
          <div className="space-y-8">
            <PreferencesApplied preferences={data.appliedPreferences} />
            {selectedRoute && <SelectedRoutePanel route={selectedRoute} />}

            <ResultSection title="Recommended picks" subtitle="Category winners based on the current preference settings.">
              <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
                {data.recommendations.map((route) => (
                  <RouteCardView
                    key={route.label}
                    route={route}
                    highlighted={route.label === preferenceLabels[data.requestedPreference]}
                    selected={route.routeId === selectedRouteId}
                    onSelect={() => setSelectedRouteId(route.routeId)}
                    subtitle={recommendationSubheads[route.label]}
                  />
                ))}
              </div>
            </ResultSection>

            <ResultSection title="All route options" subtitle="Every available mocked mode for this Manhattan demo route.">
              {data.hiddenOptionsMessages.length > 0 && (
                <div className="mb-4 rounded-lg border border-amber-800 bg-amber-950/30 p-3 text-sm text-amber-100">
                  {data.hiddenOptionsMessages.map((message) => (
                    <p key={message}>{message}</p>
                  ))}
                </div>
              )}
              <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
                {data.allOptions.map((route) => (
                  <RouteCardView
                    key={route.mode}
                    route={route}
                    highlighted={false}
                    selected={route.routeId === selectedRouteId}
                    onSelect={() => setSelectedRouteId(route.routeId)}
                    subtitle="Available demo mode"
                  />
                ))}
              </div>
            </ResultSection>
          </div>
        )}
      </section>
    </main>
  );
}

function validateForm(origin: string, destination: string): string | null {
  if (!origin.trim() || !destination.trim()) {
    return "Please enter both an origin and a destination.";
  }
  if (origin.trim().toLowerCase() === destination.trim().toLowerCase()) {
    return "Origin and destination are the same. Choose two different Manhattan locations.";
  }
  return null;
}

function ResultSection({ title, subtitle, children }: { title: string; subtitle: string; children: React.ReactNode }) {
  return (
    <section>
      <div className="mb-4">
        <h2 className="text-xl font-semibold text-white">{title}</h2>
        <p className="mt-1 text-sm text-zinc-400">{subtitle}</p>
      </div>
      {children}
    </section>
  );
}

function PreferencesApplied({ preferences }: { preferences: string[] }) {
  if (preferences.length === 0) {
    return null;
  }

  return (
    <div className="rounded-lg border border-zinc-800 bg-zinc-900 p-4">
      <p className="font-semibold text-zinc-100">Preferences applied</p>
      <ul className="mt-2 grid gap-2 text-sm leading-6 text-zinc-300 md:grid-cols-2">
        {preferences.map((preference) => (
          <li key={preference}>{preference}</li>
        ))}
      </ul>
    </div>
  );
}

function SelectedRoutePanel({ route }: { route: RouteCard }) {
  return (
    <section className="rounded-lg border border-emerald-700 bg-emerald-950/20 p-5">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <p className="text-sm font-semibold text-emerald-300">Selected route details</p>
          <h2 className="mt-1 flex items-center gap-2 text-2xl font-semibold capitalize text-white">
            {modeIcons[route.mode]} {route.mode.replace("_", " ")}
          </h2>
          <p className="mt-2 text-sm text-zinc-300">{route.baseEstimate}</p>
        </div>
        <div className="grid grid-cols-2 gap-3 text-sm sm:grid-cols-5">
          <Metric label="Distance" value={`${route.distanceMiles.toFixed(1)} mi`} />
          <Metric label="Estimate" value={`${route.estimatedTime} min`} />
          <Metric label="Cost" value={`$${route.estimatedCost.toFixed(2)}`} />
          <Metric label="Walking" value={`${route.walkingDistanceMiles.toFixed(1)} mi`} />
          <Metric label="Transfers" value={String(route.transfers)} />
          <Metric label="Stress" value={String(route.stressScore)} />
        </div>
      </div>

      <div className="mt-5 grid gap-5 lg:grid-cols-[1fr_1.1fr]">
        <div>
          <div className="mb-5 rounded-md border border-zinc-800 bg-zinc-950/70 p-3 text-sm leading-6 text-zinc-300">
            <p className="font-semibold text-zinc-100">Route summary</p>
            <p className="mt-2">{route.routeSummary}</p>
            <p className="mt-2">{route.modeTradeoffSummary}</p>
            <p className="mt-2">
              Complexity: {route.routeComplexity}
              {route.stationComplexity ? `, station complexity: ${route.stationComplexity}` : ""}
            </p>
          </div>
          <p className="text-sm font-semibold text-zinc-100">Reasons</p>
          <ul className="mt-2 space-y-2 text-sm leading-6 text-zinc-300">
            {route.reasons.map((reason) => (
              <li key={reason}>{reason}</li>
            ))}
          </ul>
        </div>
        <ScoreDetails route={route} />
      </div>
    </section>
  );
}

function DashboardState({ title, body }: { title: string; body: string }) {
  return (
    <div className="rounded-lg border border-zinc-800 bg-zinc-900 p-6">
      <p className="font-semibold text-zinc-100">{title}</p>
      <p className="mt-2 text-sm leading-6 text-zinc-400">{body}</p>
    </div>
  );
}

function LocationField({
  label,
  value,
  focused,
  onFocus,
  onBlur,
  onChange
}: {
  label: string;
  value: string;
  focused: boolean;
  onFocus: () => void;
  onBlur: () => void;
  onChange: (value: string) => void;
}) {
  const suggestions = findLocationSuggestions(value);

  return (
    <label className="relative space-y-2">
      <span className="text-sm text-zinc-300">{label}</span>
      <input
        className="control"
        value={value}
        onBlur={onBlur}
        onChange={(event) => onChange(event.target.value)}
        onFocus={onFocus}
      />
      {focused && suggestions.length > 0 && (
        <div className="absolute z-20 mt-2 max-h-56 w-full overflow-auto rounded-md border border-zinc-700 bg-zinc-950 shadow-xl shadow-black/30">
          {suggestions.map((suggestion) => (
            <button
              key={suggestion.displayName}
              type="button"
              className="block w-full px-3 py-2 text-left text-sm text-zinc-200 hover:bg-zinc-800"
              onMouseDown={(event) => {
                event.preventDefault();
                onChange(suggestion.displayName);
              }}
            >
              {suggestion.displayName}
            </button>
          ))}
        </div>
      )}
    </label>
  );
}

function Toggle({ label, checked, onChange, icon }: { label: string; checked: boolean; onChange: (value: boolean) => void; icon?: React.ReactNode }) {
  return (
    <label className="flex min-h-11 items-center justify-between gap-3 rounded-md border border-zinc-800 bg-zinc-900 px-3 py-2">
      <span className="inline-flex items-center gap-2 text-sm text-zinc-200">{icon}{label}</span>
      <input className="h-5 w-5 accent-emerald-400" type="checkbox" checked={checked} onChange={(event) => onChange(event.target.checked)} />
    </label>
  );
}

function RouteCardView({
  route,
  highlighted,
  selected,
  onSelect,
  subtitle
}: {
  route: RouteCard;
  highlighted: boolean;
  selected: boolean;
  onSelect: () => void;
  subtitle: string;
}) {
  return (
    <article
      onClick={onSelect}
      onKeyDown={(event) => {
        if (event.key === "Enter" || event.key === " ") {
          event.preventDefault();
          onSelect();
        }
      }}
      role="button"
      tabIndex={0}
      className={`h-full cursor-pointer rounded-lg border p-5 text-left transition hover:border-emerald-500 ${selected ? "border-emerald-300 bg-emerald-950/40" : highlighted ? "border-emerald-500 bg-emerald-950/20" : "border-zinc-800 bg-zinc-900"}`}
    >
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="text-sm font-medium text-emerald-300">{route.label}</p>
          <p className="mt-1 text-xs text-zinc-400">{subtitle}</p>
          <h2 className="mt-1 flex items-center gap-2 text-xl font-semibold capitalize text-white">
            {modeIcons[route.mode]} {route.mode.replace("_", " ")}
          </h2>
        </div>
        <div className="rounded-md bg-zinc-950 px-3 py-2 text-right">
          <p className="text-2xl font-semibold">{route.estimatedTime}</p>
          <p className="text-xs text-zinc-400">minutes</p>
        </div>
      </div>

      <dl className="mt-5 grid grid-cols-2 gap-3 text-sm">
        <Metric label="Distance" value={`${route.distanceMiles.toFixed(1)} mi`} />
        <Metric label="Walk exposure" value={`${route.walkingDistanceMiles.toFixed(1)} mi`} />
        <Metric label="Cost" value={`$${route.estimatedCost.toFixed(2)}`} />
        <Metric label="Transfers" value={String(route.transfers)} />
        <Metric label="Stress" value={String(route.stressScore)} />
        <Metric label="Safety-aware" value={String(route.safetyAwareScore)} />
      </dl>

      {route.majorDecisionFactors.length > 0 && (
        <div className="mt-5 rounded-md border border-zinc-800 bg-zinc-950/60 p-3">
          <p className="text-xs font-semibold uppercase tracking-[0.12em] text-zinc-400">Major decision factors</p>
          <ul className="mt-2 space-y-1 text-sm leading-6 text-zinc-300">
            {route.majorDecisionFactors.map((factor) => (
              <li key={factor}>{factor}</li>
            ))}
          </ul>
        </div>
      )}

      {route.recommendationReason && <p className="mt-5 text-sm font-medium text-zinc-100">{route.recommendationReason}</p>}
      {route.runnerUpMode && route.runnerUpReason && (
        <p className="mt-2 text-sm leading-6 text-zinc-400">
          Runner-up: {route.runnerUpMode.replace("_", " ")}. {route.runnerUpReason}
        </p>
      )}

      {route.majorPenalties.length > 0 && (
        <div className="mt-5 rounded-md border border-amber-800 bg-amber-950/30 p-3">
          <p className="text-xs font-semibold uppercase tracking-[0.12em] text-amber-200">Major penalties</p>
          <ul className="mt-2 space-y-1 text-sm leading-6 text-amber-100">
            {route.majorPenalties.map((penalty) => (
              <li key={penalty}>{penalty}</li>
            ))}
          </ul>
        </div>
      )}

      <ScoreDetails route={route} compact />

      <ul className="mt-5 space-y-2 text-sm leading-6 text-zinc-300">
        {route.reasons.map((reason) => (
          <li key={reason}>{reason}</li>
        ))}
      </ul>
    </article>
  );
}

function ScoreDetails({ route, compact = false }: { route: RouteCard; compact?: boolean }) {
  const breakdown: Array<[string, number]> = [
    ["Fastest profile", route.scoreBreakdown.fastestScore],
    ["Cost profile", route.scoreBreakdown.cheapestScore],
    ["Safety-aware", route.scoreBreakdown.safetyAwareScore],
    ["Time", route.scoreBreakdown.timeScore],
    ["Cost", route.scoreBreakdown.costScore],
    ["Walking", route.scoreBreakdown.walkingScore],
    ["Transfers", route.scoreBreakdown.transferScore],
    ["Wait", route.scoreBreakdown.waitScore],
    ["Congestion", route.scoreBreakdown.congestionScore],
    ["Weather", route.scoreBreakdown.weatherScore],
    ["Late night", route.scoreBreakdown.lateNightScore],
    ["Alerts", route.scoreBreakdown.serviceAlertScore],
    ["Final stress", route.scoreBreakdown.finalStressScore]
  ];

  return (
    <details className={`${compact ? "mt-5" : ""} rounded-md border border-zinc-800 bg-zinc-950/70 p-3`} open={!compact}>
      <summary className="cursor-pointer text-sm font-semibold text-zinc-100">Score details</summary>
      <dl className="mt-3 grid grid-cols-2 gap-2 text-xs sm:grid-cols-3">
        {breakdown.map(([label, value]) => (
          <div key={label} className="rounded border border-zinc-800 bg-zinc-900 p-2">
            <dt className="text-zinc-500">{label}</dt>
            <dd className="mt-1 font-semibold text-zinc-100">{value}</dd>
          </div>
        ))}
      </dl>
    </details>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div className="min-w-0 rounded-md border border-zinc-800 bg-zinc-950 p-3">
      <dt className="text-xs text-zinc-500">{label}</dt>
      <dd className="mt-1 break-words font-semibold text-zinc-100">{value}</dd>
    </div>
  );
}

ReactDOM.createRoot(document.getElementById("root")!).render(<App />);
