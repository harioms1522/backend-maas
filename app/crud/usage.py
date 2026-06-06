from app.models.deployment import DeploymentUsage
from sqlalchemy.orm import Session


async def log_deployment_usage(db: Session, deployment_id: str, api_key: str, model: str, input_tokens: int, output_tokens: int):
    usage_entry = DeploymentUsage(
        deployment_id=deployment_id,
        api_key=api_key,
        model=model,
        input_tokens=input_tokens,
        output_tokens=output_tokens
    )
    db.add(usage_entry)
    db.commit()