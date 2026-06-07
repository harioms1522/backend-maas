import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.app import app
from app.database import Base, get_db
from app.models.deployment import Deployment, DeploymentStatus


@pytest.fixture()
def client_and_db(tmp_path, monkeypatch):
    db_path = tmp_path / "test_state_machine.db"
    database_url = f"sqlite:///{db_path}"
    engine = create_engine(database_url, connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    Base.metadata.create_all(bind=engine)

    async def fake_deployment_background_task(*args, **kwargs):
        return None

    async def fake_delete_background_task(db, deployment_id):
        db.query(Deployment).filter(Deployment.deployment_id == deployment_id).update(
            {"status": DeploymentStatus.TERMINATED}
        )
        db.commit()
        return {"deployment_id": deployment_id, "status": DeploymentStatus.TERMINATED}

    monkeypatch.setattr("app.internal.deployments.deployment_background_task", fake_deployment_background_task)
    monkeypatch.setattr("app.internal.deployments.delete_deployment_background_task", fake_delete_background_task)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client, TestingSessionLocal

    app.dependency_overrides.clear()


def test_state_machine_enforcement_and_security_boundaries(client_and_db):
    client, session_factory = client_and_db
    create_response = client.post("/deployments/", json={"model": "gpt-4o-mini"})

    assert create_response.status_code == 201
    assert create_response.json()["status"] == "provisioning"
    assert "api_key" not in create_response.json()
    assert "endpoint_url" not in create_response.json()

    deployment_id = create_response.json()["deployment_id"]

    # The deployment is still provisioning at this point, so completions must be blocked.
    db = session_factory()
    try:
        deployment = db.query(Deployment).filter(Deployment.deployment_id == deployment_id).one()
        deployment.api_key = "owner-api-key"
        deployment.endpoint_url = "https://example.test"
        db.commit()
        db.refresh(deployment)
    finally:
        db.close()

    provisioning_response = client.post(
        f"/v1/{deployment_id}/completions",
        json={"prompt": "hello"},
        headers={"Authorization": "Bearer owner-api-key"},
    )
    assert provisioning_response.status_code == 409

    db = session_factory()
    try:
        deployment = db.query(Deployment).filter(Deployment.deployment_id == deployment_id).one()
        deployment.status = DeploymentStatus.READY
        db.commit()
    finally:
        db.close()

    missing_auth_response = client.post(
        f"/v1/{deployment_id}/completions",
        json={"prompt": "hello"},
    )
    assert missing_auth_response.status_code == 401

    other_key_response = client.post(
        f"/v1/{deployment_id}/completions",
        json={"prompt": "hello"},
        headers={"Authorization": "Bearer other-api-key"},
    )
    assert other_key_response.status_code == 403

    delete_response = client.delete(f"/deployments/{deployment_id}")
    assert delete_response.status_code == 200

    terminated_response = client.post(
        f"/v1/{deployment_id}/completions",
        json={"prompt": "hello"},
        headers={"Authorization": "Bearer owner-api-key"},
    )
    assert terminated_response.status_code == 409
