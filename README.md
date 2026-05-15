# RouteAssist NYC

RouteAssist NYC is a Manhattan-only route decision engine MVP. It compares subway, walking, Citi Bike, and rideshare options by modeled time, cost, transfers, walking distance, wait time, congestion, weather exposure, service alerts, late-night walking exposure, and stress.

It is not a Google Maps clone. The MVP focuses on ranking route choices by user intent: fastest, cheapest, least stressful, or safety-aware.

## Current Scope

Phase 1 and Phase 2 are implemented with mocked Manhattan route options only.

Supported example routes:

- Penn Station to Washington Square Park
- Times Square to Wall Street
- Grand Central to Columbia University
- Union Square to Chelsea
- World Trade Center to Times Square

Out-of-scope routes return:

> RouteAssist NYC currently supports Manhattan routes. Outer borough and commuter route support coming later.

The MVP intentionally does not support Long Island, New Jersey, LIRR, NJ Transit, PATH, commuter rail, or outer borough routing yet.

## Architecture

```text
backend/
  app/
    api/                 FastAPI route handlers
    models/              Pydantic request/response schemas
    providers/           Mock provider layer; future real API adapters live here
    services/            Scope checks, scoring, and comparison logic
  tests/                 Scoring tests

frontend/
  src/                   React TypeScript app
```

The backend keeps route scoring as pure Python functions in `backend/app/services/scoring.py`. Mock route data lives in `backend/app/providers/mock_routes.py`, which gives the project a clear place to swap in real providers later.

## Backend Setup

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

API endpoints:

- `GET /api/health`
- `POST /api/routes/compare`

Run tests:

```bash
cd backend
PYTHONPATH=. python3 -m unittest discover -s tests
```

## Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

The Vite dev server proxies `/api` requests to `http://127.0.0.1:8000`.

## Future Expansion Plan

- Replace mock providers with adapters for MTA GTFS/GTFS-Realtime, Citi Bike GBFS, OpenWeather, and Mapbox Directions.
- Add PostgreSQL/PostGIS for locations, route geometries, borough boundaries, and provider cache tables.
- Add Mapbox GL JS for map visualization after the ranking engine is stable.
- Expand scope from Manhattan to outer borough routes with explicit borough-aware service areas.
- Add commuter providers as separate modules for LIRR, NJ Transit, PATH, and other regional systems.
- Deploy with AWS ECS Fargate or Lambda/API Gateway, RDS PostgreSQL/PostGIS, and S3/CloudFront or Amplify.
