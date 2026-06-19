import pytest


class TestAuditService:
    @pytest.mark.anyio
    async def test_audit_log(self, db_session):
        from app.services.audit_service import AuditService
        svc = AuditService(db_session)
        entry = await svc.log(user_id=1, action="test_action", target_type="test", target_id=1, details={"key": "value"})
        assert entry.id > 0
        assert entry.action == "test_action"
        assert entry.details == {"key": "value"}


@pytest.mark.anyio
async def test_security_headers(client):
    response = await client.get("/health")
    assert "x-content-type-options" in response.headers
    assert response.headers["x-content-type-options"] == "nosniff"
    assert "x-frame-options" in response.headers
    assert "content-security-policy" in response.headers


@pytest.mark.anyio
async def test_cors_headers(client):
    response = await client.options("/health", headers={
        "Origin": "http://localhost:3000",
        "Access-Control-Request-Method": "GET",
    })
    assert "access-control-allow-origin" in response.headers
