def test_get_diagnosis(client):
    res = client.get("/api/v1/assessments/assessment-1/diagnosis")
    assert res.status_code == 200
    assert res.json()["diagnosis"] == "Load-related right anterior knee pain"


def test_get_diagnosis_not_found(client):
    res = client.get("/api/v1/assessments/does-not-exist/diagnosis")
    assert res.status_code == 404


def test_update_diagnosis_action(client):
    res = client.patch("/api/v1/assessments/assessment-1/diagnosis", json={"action": "update"})
    assert res.status_code == 200
    body = res.json()
    assert body["diagnosisAction"] == "update"
    assert body["version"] == 2


def test_update_diagnosis_text(client):
    res = client.patch(
        "/api/v1/assessments/assessment-1/diagnosis", json={"diagnosis": "New diagnosis text"}
    )
    assert res.status_code == 200
    assert res.json()["diagnosis"] == "New diagnosis text"
