from fastapi import APIRouter
from app.api.v1.endpoints import deployments

router = APIRouter(
    prefix="/api/v1",
    tags=["v1"],
)

router.include_router(
    prefix="/deployments",
    router=deployments.router,
)
