def create_student(client, **overrides):
    payload = {"name": "Test Student", "email": "test.student@example.com", "age": 30}
    payload.update(overrides)
    return client.post("/students/", json=payload)


def test_create_and_read_student(client):
    response = create_student(client)
    assert response.status_code == 201
    student = response.json()
    assert client.get(f"/students/{student['id']}").json() == student


def test_duplicate_email_is_case_insensitive(client):
    response = create_student(client, email="ADITI.RAO@example.com")
    assert response.status_code == 409


def test_email_is_stored_lowercase(client):
    assert create_student(client, email="  New.Person@Example.COM ").json()["email"] == "new.person@example.com"


def test_invalid_email_rejected_on_create_and_update(client):
    assert create_student(client, email="no-at-sign").status_code == 422
    assert client.patch("/students/1", json={"email": "no-at-sign"}).status_code == 422


def test_blank_name_rejected(client):
    assert create_student(client, name="   ").status_code == 422


def test_patch_rejects_explicit_nulls(client):
    for field in ("name", "email", "age"):
        assert client.patch("/students/1", json={field: None}).status_code == 422
    # Sorting and reporting keep working because no null slipped in.
    assert client.get("/students/sorted?by=age").status_code == 200
    assert client.get("/students/report").status_code == 200


def test_patch_updates_only_sent_fields(client):
    before = client.get("/students/1").json()
    after = client.patch("/students/1", json={"age": 40}).json()
    assert after == {**before, "age": 40}


def test_patch_to_existing_email_conflicts(client):
    assert client.patch("/students/1", json={"email": "rohan.mehta@example.com"}).status_code == 409


def test_missing_student_returns_404(client):
    assert client.get("/students/9999").status_code == 404
    assert client.patch("/students/9999", json={"age": 20}).status_code == 404
    assert client.delete("/students/9999").status_code == 404


def test_min_age_filter_and_validation(client):
    ages = [s["age"] for s in client.get("/students/?min_age=22").json()]
    assert ages and all(age >= 22 for age in ages)
    assert client.get("/students/?min_age=-1").status_code == 422


def test_sorted_by_age_and_name(client):
    ages = [s["age"] for s in client.get("/students/sorted?by=age").json()]
    names = [s["name"] for s in client.get("/students/sorted?by=name").json()]
    assert ages == sorted(ages)
    assert names == sorted(names)


def test_search_found_and_not_found(client):
    assert client.get("/students/search?name=Kavya Nair").json()["email"] == "kavya.nair@example.com"
    assert client.get("/students/search?name=Nobody").status_code == 404


def test_report_counts_students_meeting_min_age(client):
    body = client.get("/students/report?min_age=21").json()
    assert body["count_meeting_min_age"] == 5
    assert "Aditi Rao <aditi.rao@example.com>" in body["report"]
