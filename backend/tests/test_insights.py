def test_get_insights_before_generation_returns_fallback(client):
    # Seeded assessment-1 has never had /diagnosis/generate run against it —
    # insights should be the "nothing generated yet" fallback, not empty/404.
    res = client.get("/api/v1/assessments/assessment-1/insights")
    assert res.status_code == 200
    body = res.json()
    assert body["assessmentId"] == "assessment-1"
    assert body["summary"]
    assert body["tags"] == []


def test_get_insights_not_found(client):
    res = client.get("/api/v1/assessments/does-not-exist/insights")
    assert res.status_code == 404
