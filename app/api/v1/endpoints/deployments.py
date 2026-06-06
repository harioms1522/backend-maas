import random
from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.database import get_db
from app.internal.deployments import get_deployment as get_deployment_record, log_deployment_usage
from app.schemas.deployments import CompletionRequest, CompletionResponse

router = APIRouter()

# 1. Define the Bearer security scheme
security = HTTPBearer()

async def require_deployment_access(
    deployment_id: str,
    token: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    db: Session = Depends(get_db),
):
    authorization = token.credentials
    print(f"Authorization header: {authorization}")
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing or invalid Authorization header")

    api_key = authorization.split(" ", 1)[1].strip()
    deployment = await get_deployment_record(db, deployment_id)

    if not deployment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Deployment not found")

    if deployment["api_key"] != api_key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")

    return deployment


@router.post("/{deployment_id}/completions", status_code=200)
async def create_completion_handler(
    deployment_id: str,
    request: CompletionRequest,
    db: Session = Depends(get_db),
    deployment: dict = Depends(require_deployment_access),
):
    input_tokens = round(len(request.prompt) / 4)

    await log_deployment_usage(
        db,
        deployment_id=deployment["deployment_id"],
        api_key=deployment["api_key"],
        model=deployment["model"],
        input_tokens=input_tokens,
        output_tokens=random.randint(50, 200)
    )

    return CompletionResponse(
        output="mocked response",
        input_tokens=input_tokens,
        output_tokens=random.randint(50, 200),
    )
