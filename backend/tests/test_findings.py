def test_list_findings(client):
    res = client.get("/api/v1/assessments/assessment-1/findings")
    assert res.status_code == 200
    body = res.json()
    assert len(body) == 1
    assert body[0]["id"] == "pelvis-shift"


def test_create_finding(client):
    res = client.post(
        "/api/v1/assessments/assessment-1/findings",
        json={"tag": "JOINT", "label": "New Finding"},
    )
    assert res.status_code == 201
    body = res.json()
    assert body["label"] == "New Finding"
    assert body["assessmentId"] == "assessment-1"

    listed = client.get("/api/v1/assessments/assessment-1/findings").json()
    assert len(listed) == 2


def test_create_finding_assessment_not_found(client):
    res = client.post(
        "/api/v1/assessments/does-not-exist/findings", json={"tag": "JOINT", "label": "X"}
    )
    assert res.status_code == 404


def test_update_finding(client):
    res = client.patch("/api/v1/findings/pelvis-shift", json={"label": "Relabeled"})
    assert res.status_code == 200
    assert res.json()["label"] == "Relabeled"


def test_update_finding_not_found(client):
    res = client.patch("/api/v1/findings/does-not-exist", json={"label": "x"})
    assert res.status_code == 404


def test_delete_finding(client):
    res = client.delete("/api/v1/findings/pelvis-shift")
    assert res.status_code == 204

    listed = client.get("/api/v1/assessments/assessment-1/findings").json()
    assert listed == []


def test_delete_finding_not_found(client):
    res = client.delete("/api/v1/findings/does-not-exist")
    assert res.status_code == 404


def test_delete_finding_bumps_assessment_version(client):
    before = client.get("/api/v1/assessments/assessment-1").json()["version"]
    client.delete("/api/v1/findings/pelvis-shift")
    after = client.get("/api/v1/assessments/assessment-1").json()["version"]
    assert after == before + 1
