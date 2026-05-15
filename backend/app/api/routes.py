from fastapi import APIRouter

from app.models.routes import CompareRoutesRequest, CompareRoutesResponse
from app.services.route_comparison import compare_routes

router = APIRouter()


@router.post("/compare", response_model=CompareRoutesResponse)
def compare_route_options(payload: CompareRoutesRequest) -> CompareRoutesResponse:
    return compare_routes(payload)
