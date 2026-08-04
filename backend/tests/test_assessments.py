def test_list_assessments_for_patient(client):
    res = client.get("/api/v1/patients/patient-1/assessments")
    assert res.status_code == 200
    assert any(a["id"] == "assessment-1" for a in res.json())


def test_create_assessment(client):
    res = client.post("/api/v1/patients/patient-1/assessments")
    assert res.status_code == 201
    body = res.json()
    assert body["patientId"] == "patient-1"
    assert body["status"] == "reviewing"
    assert body["version"] == 1


def test_create_assessment_patient_not_found(client):
    res = client.post("/api/v1/patients/does-not-exist/assessments")
    assert res.status_code == 404


def test_get_assessment(client):
    res = client.get("/api/v1/assessments/assessment-1")
    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "completed"
    assert body["confidence"] == 64


def test_get_assessment_not_found(client):
    res = client.get("/api/v1/assessments/does-not-exist")
    assert res.status_code == 404


def test_update_assessment_status_bumps_version(client):
    res = client.patch("/api/v1/assessments/assessment-1", json={"status": "reviewing"})
    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "reviewing"
    assert body["version"] == 2
