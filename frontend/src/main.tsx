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
  const [loading, setLoading] = React.useState(false);
  const [error, setError] = React.useState("");

  async function compareRoutes(event?: React.FormEvent) {
    event?.preventDefault();
    setLoading(true);
    setError("");

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

      setData(await compareRoutesRequest(payload));
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Something went wrong.");
    } finally {
      setLoading(false);
    }
  }

  React.useEffect(() => {
    void compareRoutes();
  }, []);

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
        {data?.scopeMessage && <div className="rounded-lg border border-amber-700 bg-amber-950/50 p-4 text-amber-100">{data.scopeMessage}</div>}
        {loading && <DashboardState title="Comparing route options..." body="Scoring mocked Manhattan choices by time, cost, walking, transfers, weather, congestion, and stress." />}
        {!loading && !error && data?.supported && data.routeCards.length === 0 && (
          <DashboardState title="No route cards available" body="Try one of the Manhattan example routes above." />
        )}
        {!loading && !error && !data && (
          <DashboardState title="Ready to compare" body="Enter a Manhattan origin and destination to see ranked route cards." />
        )}
        {!loading && data?.supported && data.routeCards.length > 0 && (
          <div className="grid gap-4 lg:grid-cols-4">
            {data.routeCards.map((route) => (
              <RouteCardView key={route.label} route={route} highlighted={route.label === preferenceLabels[data.requestedPreference]} />
            ))}
          </div>
        )}
      </section>
    </main>
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

function RouteCardView({ route, highlighted }: { route: RouteCard; highlighted: boolean }) {
  return (
    <article className={`rounded-lg border p-5 ${highlighted ? "border-emerald-400 bg-emerald-950/30" : "border-zinc-800 bg-zinc-900"}`}>
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="text-sm font-medium text-emerald-300">{route.label}</p>
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
        <Metric label="Cost" value={`$${route.estimatedCost.toFixed(2)}`} />
        <Metric label="Transfers" value={String(route.transfers)} />
        <Metric label="Walking" value={`${route.walkingMinutes} min`} />
        <Metric label="Stress" value={String(route.stressScore)} />
      </dl>

      <ul className="mt-5 space-y-2 text-sm leading-6 text-zinc-300">
        {route.reasons.map((reason) => (
          <li key={reason}>{reason}</li>
        ))}
      </ul>
    </article>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-md border border-zinc-800 bg-zinc-950 p-3">
      <dt className="text-xs text-zinc-500">{label}</dt>
      <dd className="mt-1 font-semibold text-zinc-100">{value}</dd>
    </div>
  );
}

ReactDOM.createRoot(document.getElementById("root")!).render(<App />);
