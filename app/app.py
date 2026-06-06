from fastapi import FastAPI
from app import database, models
from app.api.v1 import router
from app.core.config import ENV

from app import models

app = FastAPI(title="MAAS API")


# all the authentication and authorization logic will go here
# middleware for authentication and authorization can be added here


@app.get("/")
def hello_world():
    return {"message": "Hello, world!"}

# Include API routes
app.include_router(router.router)


# Create tables
models.Base.metadata.create_all(bind=database.engine)