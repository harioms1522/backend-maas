from fastapi import FastAPI
from fastapi.concurrency import asynccontextmanager
from app import models
from app.api.v1 import router
from app.api import deployments, usage
from app.core.config import ENV
from app.database import engine

from app import models

# Define the lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)
        
    yield
    
    # ---- SHUTDOWN LOGIC ----
    await engine.dispose()

app = FastAPI(title="MAAS API", lifespan=lifespan)


# all the authentication and authorization logic will go here
# middleware for authentication and authorization can be added here



# Include API routes
app.include_router(deployments.router)
app.include_router(usage.router)
app.include_router(router.router)

# Create tables
# It was for sync session, now we are using async session, so we need to create tables in a different way
# models.Base.metadata.create_all(bind=database.engine)