from fastapi.testclient import TestClient

from api.index import app


client = TestClient(app)


def test_vercel_adapter_health():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_vercel_adapter_version():
    response = client.get("/api/version")
    assert response.status_code == 200
    payload = response.json()
    assert payload["name"] == "JoyLab Agent OS"
    assert payload["version"] == "0.6.5"


def test_vercel_adapter_capabilities_exposes_governed_runtime():
    response = client.get("/api/capabilities")
    assert response.status_code == 200
    payload = response.json()
    assert payload["runtime"] == "governed-learning"
    assert "evidence-builder" in payload["capabilities"]
    assert "certification-gate" in payload["capabilities"]
    assert "crash-reconciliation" in payload["capabilities"]


def test_vercel_adapter_certification_policy_matches_core_defaults():
    response = client.get("/api/certification-policy")
    assert response.status_code == 200
    payload = response.json()
    assert payload["min_samples"] == 20
    assert payload["min_gold_cases"] == 10
    assert payload["min_confidence"] == 80.0
    assert payload["require_oos_pass"] is True
    assert payload["require_regression_pass"] is True
    assert payload["max_hard_gate_violations"] == 0


def test_dashboard_is_available_at_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "JoyLab Agent OS" in response.text
    assert "Evidence Pipeline" in response.text
    assert "Certification Gate" in response.text
