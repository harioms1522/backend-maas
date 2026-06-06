import enum
import uuid

from app.database import Base
from sqlalchemy import Column, Enum, Integer, String

class DeploymentStatus(enum.Enum):
    PROVISIONING = "provisioning"
    ACTIVE = "active"
    DELETED = "deleted"
    DELETING = "deleting"
    FAILED = "failed"
    FAILED_DELETION = "failed_deletion"

class Deployment(Base):
    __tablename__ = "deployments"

    id = Column(Integer, primary_key=True, index=True)
    
    deployment_id = Column(String(36), unique=True, index=True, default=lambda: str(uuid.uuid4()))

    model = Column(String, index=True)
    
    status = Column(Enum(DeploymentStatus, name="deployment_status_enum"), default=DeploymentStatus.PROVISIONING)

    endpoint_url = Column(String, nullable=True)
    api_key = Column(String, nullable=True)