def test_list_patients(client):
    res = client.get("/api/v1/patients")
    assert res.status_code == 200
    body = res.json()
    assert any(p["id"] == "patient-1" for p in body)


def test_get_patient(client):
    res = client.get("/api/v1/patients/patient-1")
    assert res.status_code == 200
    body = res.json()
    assert body["name"] == "Ankita Sharma"
    assert {"label": "Chief complaint", "value": "Right anterior knee pain"} in body["fields"]


def test_get_patient_not_found(client):
    res = client.get("/api/v1/patients/does-not-exist")
    assert res.status_code == 404


def test_create_patient(client):
    res = client.post("/api/v1/patients", json={"name": "New Patient", "age": 40})
    assert res.status_code == 201
    body = res.json()
    assert body["name"] == "New Patient"
    assert body["id"].startswith("patient-")
    assert body["id"] != "patient-1"


def test_update_patient(client):
    res = client.patch("/api/v1/patients/patient-1", json={"clinicalSummary": "Updated summary"})
    assert res.status_code == 200
    assert res.json()["clinicalSummary"] == "Updated summary"


def test_update_patient_not_found(client):
    res = client.patch("/api/v1/patients/does-not-exist", json={"clinicalSummary": "x"})
    assert res.status_code == 404
