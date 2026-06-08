import pytest
from httpx import AsyncClient, ASGITransport  # Fixed import here
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, update

from app.app import app
from app.database import Base, get_db
from app.models.deployment import Deployment, DeploymentStatus

# Tell pytest to handle async tests using anyio (or pytest-asyncio)
pytestmark = pytest.mark.anyio


@pytest.fixture()
async def client_and_db(tmp_path, monkeypatch):
    db_path = tmp_path / "test_state_machine.db"
    database_url = f"sqlite+aiosqlite:///{db_path}"

    engine = create_async_engine(database_url, connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    
    # Fixed: Added 'async with' instead of regular 'with'
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async def fake_deployment_background_task(*args, **kwargs):
        return None

    async def fake_delete_background_task(db: AsyncSession, deployment_id):
        await db.execute(
            update(Deployment)
            .where(Deployment.deployment_id == deployment_id)
            .values(status=DeploymentStatus.TERMINATED)
        )
        await db.commit()
        return {"deployment_id": deployment_id, "status": DeploymentStatus.TERMINATED}

    monkeypatch.setattr("app.internal.deployments.deployment_background_task", fake_deployment_background_task)
    monkeypatch.setattr("app.internal.deployments.delete_deployment_background_task", fake_delete_background_task)

    async def override_get_db():
        async with TestingSessionLocal() as db:
            yield db

    app.dependency_overrides[get_db] = override_get_db

    # Fixed: Using the standard ASGITransport provided by httpx
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as test_client:
        yield test_client, TestingSessionLocal

    app.dependency_overrides.clear()
    await engine.dispose()


async def test_state_machine_enforcement_and_security_boundaries(client_and_db):
    client, session_factory = client_and_db
    
    create_response = await client.post("/deployments/", json={"model": "gpt-4o-mini"})

    assert create_response.status_code == 201
    assert create_response.json()["status"] == "provisioning"
    assert "api_key" not in create_response.json()
    assert "endpoint_url" not in create_response.json()

    deployment_id = create_response.json()["deployment_id"]

    async with session_factory() as db:
        result = await db.execute(select(Deployment).filter(Deployment.deployment_id == deployment_id))
        deployment = result.scalar_one()
        deployment.api_key = "owner-api-key"
        deployment.endpoint_url = "https://example.test"
        await db.commit()

    provisioning_response = await client.post(
        f"/v1/{deployment_id}/completions",
        json={"prompt": "hello"},
        headers={"Authorization": "Bearer owner-api-key"},
    )
    assert provisioning_response.status_code == 409

    async with session_factory() as db:
        result = await db.execute(select(Deployment).filter(Deployment.deployment_id == deployment_id))
        deployment = result.scalar_one()
        deployment.status = DeploymentStatus.READY
        await db.commit()

    missing_auth_response = await client.post(
        f"/v1/{deployment_id}/completions",
        json={"prompt": "hello"},
    )
    assert missing_auth_response.status_code == 401

    other_key_response = await client.post(
        f"/v1/{deployment_id}/completions",
        json={"prompt": "hello"},
        headers={"Authorization": "Bearer other-api-key"},
    )
    assert other_key_response.status_code == 403

    delete_response = await client.delete(f"/deployments/{deployment_id}")
    assert delete_response.status_code == 200

    terminated_response = await client.post(
        f"/v1/{deployment_id}/completions",
        json={"prompt": "hello"},
        headers={"Authorization": "Bearer owner-api-key"},
    )
    assert terminated_response.status_code == 409