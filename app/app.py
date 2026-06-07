from fastapi import FastAPI
from app import database, models
from app.api.v1 import router
from app.api import deployments, usage
from app.core.config import ENV

from app import models

app = FastAPI(title="MAAS API")


# all the authentication and authorization logic will go here
# middleware for authentication and authorization can be added here



# Include API routes
app.include_router(deployments.router)
app.include_router(usage.router)
app.include_router(router.router)

# Create tables
models.Base.metadata.create_all(bind=database.engine)