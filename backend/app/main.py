from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router as routes_router

app = FastAPI(
    title="RouteAssist NYC API",
    version="0.1.0",
    description="Manhattan-only route decision engine MVP.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health_check() -> dict[str, str]:
    return {"status": "ok", "service": "routeassist-nyc"}


app.include_router(routes_router, prefix="/api/routes", tags=["routes"])
