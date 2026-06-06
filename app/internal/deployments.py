import uuid
import asyncio
import secrets

from sqlalchemy.orm import Session
from app.crud.deployment import create_deployment as create_deployment_crud, update_deployment_status
# import for creating a unique deployment ID, e.g. uuid
from app.schemas.deployments import DeploymentCreateRequest
from app.models.deployment import DeploymentStatus

from fastapi import BackgroundTasks

async def deployment_background_task(db: Session, deployment_id: str, model: str):
    # Simulate deployment creation time
    await asyncio.sleep(10)

    # generate random number to simulate success or failure
    # 1 fail out of 10
    if uuid.uuid4().int % 10 == 0:
        await update_deployment_status(
            db, 
            deployment_id, 
            DeploymentStatus.FAILED,
            endpoint_url=None,
            api_key=None
        )
        return {"deployment_id": deployment_id, "status": DeploymentStatus.FAILED}

    # Simulate deployment success
    await update_deployment_status(
        db, 
        deployment_id, 
        DeploymentStatus.ACTIVE,
        endpoint_url=f"https://{deployment_id}.maas.model",
        api_key = secrets.token_hex(32)  
    )
    return {"deployment_id": deployment_id, "status": DeploymentStatus.ACTIVE}

async def create_deployment(db: Session, background_tasks: BackgroundTasks, model: str):
    deployment_id = str(uuid.uuid4())
    await create_deployment_crud(db, deployment_id=deployment_id, model=model)

    # We can also use clery for background tasks 
    # or call some apis also which in turn will call our callback url to update the deployment status
    background_tasks.add_task(deployment_background_task, db, deployment_id, model)

    # 3. Return response safely to user immediately
    return {"deployment_id": deployment_id, "status": DeploymentStatus.PROVISIONING}