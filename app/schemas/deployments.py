from fastapi import FastAPI
from pydantic import BaseModel
from typing import Literal

class DeploymentCreateRequest(BaseModel):
    # Define any parameters needed for deployment creation
    model: str