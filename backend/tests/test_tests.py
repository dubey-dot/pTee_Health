def test_list_tests_empty(client):
    res = client.get("/api/v1/assessments/assessment-1/tests")
    assert res.status_code == 200
    assert res.json() == []


def test_create_test(client):
    res = client.post(
        "/api/v1/assessments/assessment-1/tests",
        json={"type": "joint", "name": "Single leg bridge", "result": "Weak on right"},
    )
    assert res.status_code == 201
    body = res.json()
    assert body["name"] == "Single leg bridge"
    assert body["assessmentId"] == "assessment-1"

    listed = client.get("/api/v1/assessments/assessment-1/tests").json()
    assert len(listed) == 1


def test_create_test_assessment_not_found(client):
    res = client.post(
        "/api/v1/assessments/does-not-exist/tests",
        json={"type": "joint", "name": "x", "result": ""},
    )
    assert res.status_code == 404
