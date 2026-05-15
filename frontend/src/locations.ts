export type DemoLocation = {
  displayName: string;
  latitude: number;
  longitude: number;
  aliases: string[];
};

export const demoLocations: DemoLocation[] = [
  { displayName: "Penn Station", latitude: 40.7506, longitude: -73.9935, aliases: ["penn"] },
  { displayName: "Times Square", latitude: 40.758, longitude: -73.9855, aliases: ["time square", "times square"] },
  { displayName: "Grand Central", latitude: 40.7527, longitude: -73.9772, aliases: ["grand central terminal"] },
  { displayName: "Washington Square Park", latitude: 40.7308, longitude: -73.9973, aliases: ["nyu"] },
  { displayName: "Union Square", latitude: 40.7359, longitude: -73.9911, aliases: ["union sq"] },
  { displayName: "Chelsea", latitude: 40.7465, longitude: -74.0014, aliases: [] },
  { displayName: "Chelsea Market", latitude: 40.7424, longitude: -74.006, aliases: ["chelsea market"] },
  { displayName: "World Trade Center", latitude: 40.7127, longitude: -74.0134, aliases: ["wtc"] },
  { displayName: "Wall Street", latitude: 40.706, longitude: -74.0086, aliases: ["wall st"] },
  { displayName: "Financial District", latitude: 40.7075, longitude: -74.0113, aliases: ["financial district", "fidi"] },
  { displayName: "SoHo", latitude: 40.7233, longitude: -74.003, aliases: ["soho"] },
  { displayName: "Tribeca", latitude: 40.7163, longitude: -74.0086, aliases: ["tribeca"] },
  { displayName: "Columbus Circle", latitude: 40.7681, longitude: -73.9819, aliases: ["columbus circle"] },
  { displayName: "Central Park South", latitude: 40.7651, longitude: -73.9741, aliases: ["central park"] },
  { displayName: "Empire State Building", latitude: 40.7484, longitude: -73.9857, aliases: ["empire state"] },
  { displayName: "Columbia University", latitude: 40.8075, longitude: -73.9626, aliases: ["columbia"] },
  { displayName: "Bryant Park", latitude: 40.7536, longitude: -73.9832, aliases: ["bryant park"] },
  { displayName: "Rockefeller Center", latitude: 40.7587, longitude: -73.9787, aliases: ["rockefeller", "rockefeller center"] },
  { displayName: "Flatiron Building", latitude: 40.7411, longitude: -73.9897, aliases: ["flatiron"] },
  { displayName: "Battery Park", latitude: 40.7033, longitude: -74.017, aliases: ["battery park"] }
];

export function findLocationSuggestions(query: string, limit = 5): DemoLocation[] {
  const normalizedQuery = query.trim().toLowerCase();
  if (!normalizedQuery) {
    return [];
  }

  return demoLocations
    .filter((location) => {
      const searchableTerms = [location.displayName, ...location.aliases].map((term) => term.toLowerCase());
      return searchableTerms.some((term) => term.includes(normalizedQuery));
    })
    .slice(0, limit);
}
