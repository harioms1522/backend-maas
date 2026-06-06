from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from app.database import get_db
from sqlalchemy.orm import Session

from app.schemas.deployments import DeploymentCreateRequest
from app.internal.deployments import create_deployment

router = APIRouter(
    prefix="/deployments",
)


@router.get("/:deployment_id")
async def get_deployment(deployment_id: str, db: Session = Depends(get_db)):
    # Placeholder for actual deployment retrieval logic
    if deployment_id != "valid_id":
        raise HTTPException(status_code=404, detail="Deployment not found")
    return {"endpoint_url": deployment_id, "api_key": "active"}


@router.delete("/:deployment_id")
async def delete_deployment(deployment_id: str, db: Session = Depends(get_db)):
    # Placeholder for actual deployment deletion logic
    if deployment_id != "valid_id":
        raise HTTPException(status_code=404, detail="Deployment not found")
    return {"message": f"Deployment {deployment_id} deleted successfully"}


@router.post("/", status_code=201)
async def create_deployment_handler(
    deployment_data: DeploymentCreateRequest, 
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    model = deployment_data.model
    return await create_deployment(db, background_tasks, model=model)