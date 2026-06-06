import enum
import uuid

from app.database import Base
from sqlalchemy import Column, DateTime, Enum, Integer, String, Index, ForeignKey
from datetime import datetime

class DeploymentStatus(enum.Enum):
    PROVISIONING = "provisioning"
    FAILED = "failed"
    ACTIVE = "active"
    TERMINATING = "terminating"
    FAILED_TERMINATION = "failed_termination"
    TERMINATED = "terminated"

class Deployment(Base):
    __tablename__ = "deployments"

    id = Column(Integer, primary_key=True, index=True)
    
    deployment_id = Column(String(36), unique=True, index=True, default=lambda: str(uuid.uuid4()))

    model = Column(String, index=True)
    
    status = Column(Enum(DeploymentStatus, name="deployment_status_enum"), default=DeploymentStatus.PROVISIONING)

    endpoint_url = Column(String, nullable=True)
    api_key = Column(String, nullable=True)

    # indices
    __table_args__ = (
        Index("idx_status", "status"),
        Index("idx_api_key", "api_key"),
        Index("idx_deployment_id", "deployment_id", unique=True),
    )

class DeploymentUsage(Base):
    __tablename__ = "deployment_usage"

    id = Column(Integer, primary_key=True, index=True)
    
    deployment_id = Column(ForeignKey("deployments.deployment_id"), index=True, nullable=False)

    api_key = Column(String, index=True)
    model = Column(String, index=True)
    input_tokens = Column(Integer, default=0)
    output_tokens = Column(Integer, default=0)

    timestamp = Column(DateTime, index=True, default=datetime.utcnow)
    # indices
    __table_args__ = (
        Index("idx_usage_deployment_id", "deployment_id"),
        Index("idx_usage_api_key", "api_key"),
    )