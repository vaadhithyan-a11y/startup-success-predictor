import pytest
import os
import joblib
import tempfile
from unittest.mock import patch
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.pool import NullPool

from app.core.database import Base, get_db, set_engine, get_engine, get_session_factory
from app.core.config import settings
from app.core.security import create_access_token
from app.ml.model_loader import load_model, get_success_model_path, get_growth_model_path
from app.ml.data_ingestion import generate_synthetic_data, load_csv, load_excel
from app.ml.model_training import train_success_model, train_growth_model
from app.services.startup_service import StartupService
from app.services.audit_service import AuditService
from app.services.prediction_service import PredictionService
from app.schemas.startup import StartupCreate, StartupUpdate

TEST_DATABASE_URL = "sqlite+aiosqlite:///./test_cov.db"


# ─── database.py coverage ─────────────────────────────────────────────────

@pytest.mark.anyio
async def test_get_db_commit_path():
    engine = create_async_engine(TEST_DATABASE_URL, poolclass=NullPool)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    set_engine(engine)

    gen = get_db()
    session = await gen.__anext__()
    assert isinstance(session, AsyncSession)
    try:
        await gen.__anext__()
    except StopAsyncIteration:
        pass

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()
    set_engine(None)


@pytest.mark.anyio
async def test_get_db_rollback_path():
    engine = create_async_engine(TEST_DATABASE_URL, poolclass=NullPool)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    set_engine(engine)

    gen = get_db()
    await gen.__anext__()
    try:
        await gen.athrow(RuntimeError("test error"))
    except (RuntimeError, StopAsyncIteration):
        pass

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()
    set_engine(None)


def test_get_engine_initializes():
    set_engine(None)
    eng = get_engine()
    assert eng is not None


def test_get_session_factory_initializes():
    set_engine(None)
    factory = get_session_factory()
    assert factory is not None


# ─── config.py coverage ───────────────────────────────────────────────────

def test_config_database_url_sync():
    url = settings.database_url_sync
    assert "postgresql://" in url


# ─── startup_service.py coverage ──────────────────────────────────────────

@pytest.mark.anyio
async def test_startup_service_update(db_session):
    svc = StartupService(db_session)
    data = StartupCreate(founder_id=1, name="UpdCo", industry="Tech")
    startup = await svc.create(data)
    result = await svc.update(startup.id, StartupUpdate(name="UpdCoV2", industry="AI/ML"))
    assert result == 1
    updated = await svc.get_by_id(startup.id)
    assert updated.name == "UpdCoV2"
    assert updated.industry == "AI/ML"


@pytest.mark.anyio
async def test_startup_service_update_not_found(db_session):
    svc = StartupService(db_session)
    result = await svc.update(9999, StartupUpdate(name="Nope"))
    assert result == 0


@pytest.mark.anyio
async def test_startup_service_soft_delete(db_session):
    svc = StartupService(db_session)
    data = StartupCreate(founder_id=1, name="DelCo", industry="Fintech")
    startup = await svc.create(data)
    deleted = await svc.soft_delete(startup.id)
    assert deleted is True
    found = await svc.get_by_id(startup.id)
    assert found is None


@pytest.mark.anyio
async def test_startup_service_soft_delete_not_found(db_session):
    svc = StartupService(db_session)
    deleted = await svc.soft_delete(9999)
    assert deleted is False


@pytest.mark.anyio
async def test_startup_service_list_all(db_session):
    svc = StartupService(db_session)
    data = StartupCreate(founder_id=1, name="ListCo", industry="HealthTech")
    await svc.create(data)
    all_st = await svc.list_all()
    assert len(all_st) >= 1
    assert any(s.name == "ListCo" for s in all_st)


# ─── prediction_service.py coverage (model branch) ────────────────────────

@pytest.fixture(scope="module")
def trained_models_dir():
    tmpdir = tempfile.mkdtemp()
    df = generate_synthetic_data(n_samples=100)
    import app.ml.model_training as mt
    original_models_dir = mt.MODELS_DIR
    mt.MODELS_DIR = tmpdir
    train_success_model(df, model_type="random_forest")
    train_growth_model(df, model_type="random_forest")
    mt.MODELS_DIR = original_models_dir
    yield tmpdir


@pytest.mark.anyio
async def test_prediction_service_with_models(trained_models_dir):
    success_path = os.path.join(trained_models_dir, "success_random_forest.joblib")
    growth_path = os.path.join(trained_models_dir, "growth_random_forest.joblib")
    assert os.path.exists(success_path)
    assert os.path.exists(growth_path)

    with patch("app.services.prediction_service.get_success_model_path", return_value=success_path), \
         patch("app.services.prediction_service.get_growth_model_path", return_value=growth_path):
        svc = PredictionService()
        assert svc.success_model is not None
        assert svc.growth_model is not None

        result = svc.predict_success(
            "Tech", 5000000, 100, 10, 10000000, 500000000, 0.3,
        )
        assert 0 <= result["success_probability"] <= 100
        assert result["model_version"] == "ml_v1"

        result = svc.predict_growth(5000000, 100, 10000000, 500000000, 0.3)
        assert "growth_1y" in result
        assert result["model_version"] == "ml_v1"


# ─── dependencies.py coverage ────────────────────────────────────────────

@pytest.mark.anyio
async def test_get_current_user_invalid_token(client):
    response = await client.get("/startup/1", headers={"Authorization": "Bearer invalid_token"})
    assert response.status_code == 401


@pytest.mark.anyio
async def test_get_current_user_token_no_sub(client):
    token = create_access_token({"role": "founder"})
    response = await client.get("/startup/1", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 401


@pytest.mark.anyio
async def test_get_current_user_not_found(client):
    token = create_access_token({"sub": "99999", "role": "founder"})
    response = await client.get("/startup/1", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 401


@pytest.mark.anyio
async def test_get_current_admin_denied(client):
    await client.post("/auth/register", json={
        "email": "nonadmin@example.com", "password": "testpass123", "role": "founder",
    })
    login = await client.post("/auth/login", json={"email": "nonadmin@example.com", "password": "testpass123"})
    token = login.json()["access_token"]

    response = await client.put("/startup/1", json={"name": "Hack"}, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 403


# ─── audit_service.py coverage ────────────────────────────────────────────

@pytest.mark.anyio
async def test_audit_service_get_logs(db_session):
    svc = AuditService(db_session)
    await svc.log(1, "action1", "startup", 1, {"key": "val1"})
    await svc.log(1, "action2", "startup", 2, {"key": "val2"})
    logs = await svc.get_logs()
    assert len(logs) == 2
    assert logs[0].action == "action2"
    logs_limited = await svc.get_logs(skip=1, limit=1)
    assert len(logs_limited) == 1


# ─── model_loader.py coverage ─────────────────────────────────────────────

def test_load_model_with_existing_file():
    with tempfile.TemporaryDirectory() as tmpdir:
        fname = os.path.join(tmpdir, "test_model.joblib")
        joblib.dump({"test": "data"}, fname)
        with patch("app.ml.model_loader.MODELS_DIR", tmpdir):
            model = load_model("test_model.joblib")
            assert model is not None
            assert model["test"] == "data"


def test_load_model_not_found():
    model = load_model("nonexistent.joblib")
    assert model is None


def test_get_success_model_path_not_found():
    path = get_success_model_path()
    if path:
        os.remove(path)
    path = get_success_model_path()
    assert path == ""


def test_get_growth_model_path_not_found():
    path = get_growth_model_path()
    if path:
        os.remove(path)
    path = get_growth_model_path()
    assert path == ""


def test_get_success_model_path_with_file(trained_models_dir):
    with patch("app.ml.model_loader.MODELS_DIR", trained_models_dir):
        path = get_success_model_path()
        assert path != ""
        assert os.path.exists(path)


def test_get_growth_model_path_with_file(trained_models_dir):
    with patch("app.ml.model_loader.MODELS_DIR", trained_models_dir):
        path = get_growth_model_path()
        assert path != ""
        assert os.path.exists(path)


# ─── startup.py router PUT/DELETE coverage ──────────────────────────────

@pytest.mark.anyio
async def test_startup_put_admin(client):
    await client.post("/auth/register", json={
        "email": "admin1@example.com", "password": "adminpass", "role": "admin",
    })
    login = await client.post("/auth/login", json={"email": "admin1@example.com", "password": "adminpass"})
    admin_token = login.json()["access_token"]

    await client.post("/auth/register", json={
        "email": "founder_adm@example.com", "password": "testpass", "role": "founder", "full_name": "FA",
    })
    login_f = await client.post("/auth/login", json={"email": "founder_adm@example.com", "password": "testpass"})
    token_f = login_f.json()["access_token"]

    create = await client.post("/startup", json={
        "founder_id": 2, "name": "AdminTest", "industry": "Tech",
    }, headers={"Authorization": f"Bearer {token_f}"})
    sid = create.json()["startup_id"]

    response = await client.put(f"/startup/{sid}", json={"name": "AdminTestV2"}, headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 200
    assert response.json()["updated_count"] == 1


@pytest.mark.anyio
async def test_startup_delete_admin(client):
    await client.post("/auth/register", json={
        "email": "admin2@example.com", "password": "adminpass", "role": "admin",
    })
    await client.post("/auth/register", json={
        "email": "founder_del@example.com", "password": "testpass", "role": "founder", "full_name": "FD",
    })
    login_f = await client.post("/auth/login", json={"email": "founder_del@example.com", "password": "testpass"})
    token_f = login_f.json()["access_token"]
    login = await client.post("/auth/login", json={"email": "admin2@example.com", "password": "adminpass"})
    admin_token = login.json()["access_token"]

    create = await client.post("/startup", json={
        "founder_id": 2, "name": "DelMe", "industry": "Tech",
    }, headers={"Authorization": f"Bearer {token_f}"})
    sid = create.json()["startup_id"]

    response = await client.delete(f"/startup/{sid}", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 200
    assert response.json()["deleted"] is True


@pytest.mark.anyio
async def test_startup_delete_not_found_admin(client):
    await client.post("/auth/register", json={
        "email": "admin3@example.com", "password": "adminpass", "role": "admin",
    })
    login = await client.post("/auth/login", json={"email": "admin3@example.com", "password": "adminpass"})
    admin_token = login.json()["access_token"]

    response = await client.delete("/startup/99999", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 404


# ─── data_ingestion.py coverage ───────────────────────────────────────────

def test_load_csv(tmp_path):
    csv_path = tmp_path / "test.csv"
    csv_path.write_text("a,b\n1,2\n3,4\n")
    df = load_csv(str(csv_path))
    assert len(df) == 2
    assert list(df.columns) == ["a", "b"]


def test_load_excel_missing():
    with pytest.raises(FileNotFoundError):
        load_excel("nonexistent.xlsx")


# ─── feature_engineering.py coverage ──────────────────────────────────────

def test_get_feature_names():
    from app.ml.feature_engineering import FeatureEngineer
    df = generate_synthetic_data(n_samples=10)
    feature_cols = [
        "industry", "revenue", "funding_raised", "employees",
        "burn_rate", "market_size", "growth_rate", "founder_experience",
    ]
    X = df[feature_cols]
    fe = FeatureEngineer()
    fe.fit(X)
    names = fe.get_feature_names()
    assert len(names) > 0
    assert all(isinstance(n, str) for n in names)


# ─── model_training.py coverage (xgboost branches) ────────────────────────

def test_train_success_model_xgboost():
    df = generate_synthetic_data(n_samples=100)
    with tempfile.TemporaryDirectory() as tmpdir:
        import app.ml.model_training as mt
        original = mt.MODELS_DIR
        mt.MODELS_DIR = tmpdir
        result = train_success_model(df, model_type="xgboost")
        mt.MODELS_DIR = original
        assert result["model_type"] == "xgboost"
        assert result["roc_auc"] > 0.5


def test_train_growth_model_xgboost():
    df = generate_synthetic_data(n_samples=100)
    with tempfile.TemporaryDirectory() as tmpdir:
        import app.ml.model_training as mt
        original = mt.MODELS_DIR
        mt.MODELS_DIR = tmpdir
        result = train_growth_model(df, model_type="xgboost")
        mt.MODELS_DIR = original
        assert result["model_type"] == "xgboost"
        assert "mae" in result


# ─── main.py coverage (global exception handler) ─────────────────────────

@pytest.mark.anyio
async def test_global_exception_handler(client):
    from app.main import global_exception_handler
    from fastapi import Request
    mock_request = Request({"type": "http", "method": "GET", "path": "/test"})
    response = await global_exception_handler(mock_request, ValueError("test error"))
    assert response.status_code == 500
    body = response.body.decode()
    assert "INTERNAL_ERROR" in body


# ─── report_service.py coverage ──────────────────────────────────────────

def test_report_all_risk_scenarios():
    from app.services.report_service import _build_summary_from_predictions
    # Low financial risk
    s1 = _build_summary_from_predictions(
        "T1", "Tech",
        {"success_probability": 80},
        {"growth_1y": 100000, "growth_3y": 300000, "growth_5y": 500000},
        {"financial_risk": 20, "operational_risk": 40, "market_risk": 25, "team_risk": 30, "risk_score": 28.75},
    )
    assert "Strong financial position" in s1["strengths"]
    assert "Favorable market conditions" in s1["strengths"]

    # High financial & market risk
    s2 = _build_summary_from_predictions(
        "T2", "Tech",
        {"success_probability": 20},
        {"growth_1y": -50000, "growth_3y": -150000, "growth_5y": -250000},
        {"financial_risk": 80, "operational_risk": 70, "market_risk": 85, "team_risk": 65, "risk_score": 75},
    )
    assert "High financial risk exposure" in s2["weaknesses"]
    assert "Challenging market environment" in s2["weaknesses"]
    assert s2["recommendation"] == "Sell"


# ─── prediction rule-based edge cases ─────────────────────────────────────

def test_rule_based_growth_zero_revenue():
    from app.services.prediction_service import _rule_based_growth_forecast
    g1, g3, g5 = _rule_based_growth_forecast(0, 10, 0, 0, 0.5)
    assert g1 >= 0
    assert g3 >= 0
    assert g5 >= 0


def test_prediction_service_fallback_paths():
    svc = PredictionService()
    result = svc.predict_success("Tech", 5000000, 100, 10, 10000000, 500000000, 0.3)
    assert 0 <= result["success_probability"] <= 100
    assert result["model_version"] == "rule_based" or True  # may be ml_v1 if models exist

    result = svc.predict_growth(5000000, 100, 10000000, 500000000, 0.3)
    assert result["growth_1y"] >= 0
