from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from app.database import get_db
from sqlalchemy.orm import Session

from app.schemas.deployments import DeploymentCreateRequest
from app.internal.deployments import create_deployment, get_deployment, delete_deployment
from app.models.deployment import DeploymentStatus

router = APIRouter()


@router.post("/:deployment_id/completions", status_code=201)
async def create_deployment_handler(
    deployment_data: DeploymentCreateRequest, 
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    model = deployment_data.model
    return await create_deployment(db, background_tasks, model=model)
