from fastapi import FastAPI
from pydantic import BaseModel
from typing import Literal

class DeploymentCreateRequest(BaseModel):
    # Define any parameters needed for deployment creation
    model: str

class GetDeploymentResponse(BaseModel):
    deployment_id: str
    model: str
    status: str
    endpoint_url: str = None
    api_key: str = None