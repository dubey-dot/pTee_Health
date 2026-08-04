def test_list_notes_empty(client):
    res = client.get("/api/v1/assessments/assessment-1/notes")
    assert res.status_code == 200
    assert res.json() == []


def test_create_note_typed(client):
    res = client.post(
        "/api/v1/assessments/assessment-1/notes",
        json={"content": "Patient reports improved ROM since last visit."},
    )
    assert res.status_code == 201
    body = res.json()
    assert body["content"] == "Patient reports improved ROM since last visit."
    assert body["assessmentId"] == "assessment-1"
    assert body["source"] == "typed"
    assert body["createdAt"]

    listed = client.get("/api/v1/assessments/assessment-1/notes").json()
    assert len(listed) == 1


def test_create_note_voice_source(client):
    res = client.post(
        "/api/v1/assessments/assessment-1/notes",
        json={"content": "Note that pain reduced to 3 out of 10.", "source": "voice"},
    )
    assert res.status_code == 201
    assert res.json()["source"] == "voice"


def test_notes_ordered_oldest_first(client):
    client.post("/api/v1/assessments/assessment-1/notes", json={"content": "first"})
    client.post("/api/v1/assessments/assessment-1/notes", json={"content": "second"})

    listed = client.get("/api/v1/assessments/assessment-1/notes").json()
    assert [n["content"] for n in listed] == ["first", "second"]


def test_create_note_bumps_assessment_version(client):
    before = client.get("/api/v1/assessments/assessment-1").json()["version"]
    client.post("/api/v1/assessments/assessment-1/notes", json={"content": "x"})
    after = client.get("/api/v1/assessments/assessment-1").json()["version"]
    assert after == before + 1


def test_create_note_assessment_not_found(client):
    res = client.post(
        "/api/v1/assessments/does-not-exist/notes",
        json={"content": "x"},
    )
    assert res.status_code == 404
