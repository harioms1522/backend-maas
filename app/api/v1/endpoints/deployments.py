import random
from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.internal.deployments import get_deployment as get_deployment_record, log_deployment_usage
from app.schemas.deployments import CompletionRequest, CompletionResponse

from app.internal.rate_limiters import InMemoryRateLimiterOnAPIKey
from app.api.v1.endpoints.helpers import get_api_key

router = APIRouter()

# rateLimiter
rate_limiter = InMemoryRateLimiterOnAPIKey(requests_per_minute=100)

async def require_deployment_access(
    deployment_id: str,
    api_key: Annotated[str, Depends(get_api_key)],
    db: Session = Depends(get_db),
):
    deployment = await get_deployment_record(db, deployment_id)

    if not deployment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Deployment not found")
    
    if deployment["api_key"] != api_key:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid API key")
    
    if deployment["status"] != "active":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Deployment is not active")


    return deployment


@router.post(
        "/{deployment_id}/completions", 
        status_code=200,
        dependencies=[Depends(rate_limiter)]
    )
async def create_completion_handler(
    deployment_id: str,
    request: CompletionRequest,
    db: Session = Depends(get_db),
    deployment: dict = Depends(require_deployment_access),
):
    input_tokens = round(len(request.prompt) / 4)
    output_tokens = random.randint(50, 200) 

    await log_deployment_usage(
        db,
        deployment_id=deployment["deployment_id"],
        api_key=deployment["api_key"],
        model=deployment["model"],
        input_tokens=input_tokens,
        output_tokens=output_tokens
    )

    return CompletionResponse(
        output="mocked response",
        input_tokens=input_tokens,
        output_tokens=output_tokens
    )
