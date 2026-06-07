from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from app.database import get_db
from sqlalchemy.orm import Session

from app.schemas.deployments import DeploymentCreateRequest
from app.internal.deployments import create_deployment, get_deployment, delete_deployment
from app.models.deployment import DeploymentStatus

router = APIRouter(
    prefix="/deployments",
)


@router.get("/{deployment_id}")
async def get_deployment_handler(deployment_id: str, db: Session = Depends(get_db)):
    # Placeholder for actual deployment retrieval logic
    deployment = await get_deployment(db, deployment_id)
    if not deployment:
        raise HTTPException(status_code=404, detail="Deployment not found")
    
    return deployment


@router.post("/", status_code=201)
async def create_deployment_handler(
    deployment_data: DeploymentCreateRequest, 
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    model = deployment_data.model
    return await create_deployment(db, background_tasks, model=model)


@router.delete("/{deployment_id}")
async def delete_deployment_handler(deployment_id: str, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    # Placeholder for actual deployment deletion logic
    deployment = await get_deployment(db, deployment_id)
    print(deployment)
    if not deployment:
        raise HTTPException(status_code=404, detail="Deployment not found")
    if deployment["status"] in [DeploymentStatus.TERMINATED, DeploymentStatus.TERMINATING]:
        raise HTTPException(status_code=400, detail="Deployment is already being terminated or has been terminated")
    
    # Call the delete deployment function which will handle the deletion process
    await delete_deployment(db, background_tasks, deployment_id)
    return {"message": f"Deployment {deployment_id} deletion initiated"}