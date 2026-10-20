def create_course(client, **overrides):
    payload = {"course_name": "Algorithms", "credits": 4, "student_id": 1}
    payload.update(overrides)
    return client.post("/courses/", json=payload)


def test_create_course_and_count(client):
    assert create_course(client).status_code == 201
    assert client.get("/students/1/course-count").json() == {"student_id": 1, "course_count": 1}


def test_course_for_missing_student_rejected(client):
    assert create_course(client, student_id=9999).status_code == 404


def test_move_course_to_missing_student_rejected(client):
    course = create_course(client).json()
    assert client.patch(f"/courses/{course['id']}", json={"student_id": 9999}).status_code == 404


def test_credits_out_of_range_rejected(client):
    assert create_course(client, credits=0).status_code == 422
    assert create_course(client, credits=7).status_code == 422


def test_deleting_student_removes_their_courses(client):
    course = create_course(client).json()
    assert client.delete("/students/1").status_code == 204
    assert client.get(f"/courses/{course['id']}").status_code == 404


def test_course_patch_rejects_null(client):
    course = create_course(client).json()
    assert client.patch(f"/courses/{course['id']}", json={"course_name": None}).status_code == 422
