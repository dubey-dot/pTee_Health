def test_get_insights(client):
    res = client.get("/api/v1/assessments/assessment-1/insights")
    assert res.status_code == 200
    body = res.json()
    assert body["assessmentId"] == "assessment-1"
    assert body["summary"]
    assert len(body["tags"]) >= 1


def test_get_insights_not_found(client):
    res = client.get("/api/v1/assessments/does-not-exist/insights")
    assert res.status_code == 404
