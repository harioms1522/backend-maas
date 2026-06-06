import uuid
import asyncio
import secrets
from sqlalchemy.orm import Session

from app.crud.deployment import create_deployment as create_deployment_crud, update_deployment_status, get_deployment as get_deployment_crud
from app.crud.usage import log_deployment_usage as log_deployment_usage_crud
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

async def delete_deployment_background_task(db: Session, deployment_id: str):
    # Simulate deployment deletion time
    await asyncio.sleep(10)

    # generate random number to simulate success or failure    # 1 fail out of 10
    if uuid.uuid4().int % 10 == 0:
        await update_deployment_status(
            db, 
            deployment_id, 
            DeploymentStatus.FAILED_TERMINATION
        )
        return {"deployment_id": deployment_id, "status": DeploymentStatus.FAILED_TERMINATION}

    # Simulate deployment deletion success
    await update_deployment_status(db, deployment_id=deployment_id, status=DeploymentStatus.TERMINATED)
    return {"deployment_id": deployment_id, "status": DeploymentStatus.TERMINATED}

async def create_deployment(db: Session, background_tasks: BackgroundTasks, model: str):
    deployment_id = str(uuid.uuid4())
    await create_deployment_crud(db, deployment_id=deployment_id, model=model)

    # We can also use clery for background tasks 
    # or call some apis also which in turn will call our callback url to update the deployment status
    background_tasks.add_task(deployment_background_task, db, deployment_id, model)

    # 3. Return response safely to user immediately
    return {"deployment_id": deployment_id, "status": DeploymentStatus.PROVISIONING}

async def get_deployment(db: Session, deployment_id: str):
    print(f"Fetching deployment with ID: {deployment_id}")
    deployment = await get_deployment_crud(db, deployment_id=deployment_id)
    if not deployment:
        return None
    
    return {
        "deployment_id": deployment.deployment_id,
        "model": deployment.model,
        "status": deployment.status.value,
        "endpoint_url": deployment.endpoint_url,
        "api_key": deployment.api_key
    }
    

# For delete also there will be some time in deletion process
# I am also simulating that with sleep here
async def delete_deployment(db: Session, background_tasks: BackgroundTasks, deployment_id: str):
    await update_deployment_status(
        db,
        deployment_id,
        DeploymentStatus.TERMINATING
    )

    background_tasks.add_task(delete_deployment_background_task, db, deployment_id)
    
    return {"message": f"Deployment {deployment_id} deletion initiated"}


async def log_deployment_usage(db: Session, deployment_id: str, api_key: str, model: str, input_tokens: int, output_tokens: int):
    # Placeholder for actual logging logic
    await log_deployment_usage_crud(
        db,
        deployment_id=deployment_id,
        api_key=api_key,
        model=model,
        input_tokens=input_tokens,
        output_tokens=output_tokens
    )

    return {"message": "Usage logged successfully"}