# StudyTrack

StudyTrack is a small student roster project built with FastAPI, SQLite, and a plain JavaScript dashboard. It lets you add students, manage their courses, and try a few basic sorting and searching ideas on the roster.

## Project structure

- `backend/` contains the FastAPI app, SQLAlchemy models, Pydantic schemas, CRUD helpers, seed data, and algorithm functions.
- `frontend/` contains the dashboard HTML, CSS, and JavaScript.

## Running the project

StudyTrack uses single-process mode: FastAPI serves both the dashboard and the API. Open the dashboard at [http://localhost:8000/](http://localhost:8000/). The frontend calls the API with relative paths such as `/students/`, so it stays on the same server.

The project already uses a `venv` virtual-environment folder. If you need to create it again, run:

```powershell
py -m venv venv
```

Activate the environment and install the backend packages:

```powershell
.\venv\Scripts\Activate.ps1
.\venv\Scripts\python.exe -m pip install -r backend\requirements.txt
```

Start the app from the project root:

```powershell
.\venv\Scripts\python.exe -m uvicorn backend.main:app --reload
```

On first startup, StudyTrack creates its SQLite tables and adds the eight starter students. Seeding happens only when the Student table is empty, so restarting the app does not add duplicate students.

## Student API

### Create a student

`POST /students/` creates a student and returns `201 Created`.

Request body:

```json
{
  "name": "Anika Shah",
  "email": "anika.shah@example.com",
  "age": 20
}
```

Example response:

```json
{
  "id": 9,
  "name": "Anika Shah",
  "email": "anika.shah@example.com",
  "age": 20
}
```

### List students

`GET /students/` returns every student. `GET /students/?min_age=21` returns only students aged 21 or older.

### Get one student

`GET /students/{student_id}` returns one student. A missing ID returns `404 Not Found`.

### Update a student

`PATCH /students/{student_id}` updates only the fields included in the request. A missing ID returns `404 Not Found`.

Example request body:

```json
{
  "age": 21
}
```

### Delete a student

`DELETE /students/{student_id}` removes a student and returns `204 No Content`. A missing ID returns `404 Not Found`.

### Count a student's courses

`GET /students/{student_id}/course-count` returns the student ID and the number of course records linked to that student.

Example response:

```json
{
  "student_id": 1,
  "course_count": 0
}
```

## Course API

### Create a course

`POST /courses/` creates a course enrollment and returns `201 Created`. Credits must be from 1 through 6, and `student_id` must identify the owning student.

Request body:

```json
{
  "course_name": "Data Structures",
  "credits": 4,
  "student_id": 1
}
```

Example response:

```json
{
  "id": 1,
  "course_name": "Data Structures",
  "credits": 4,
  "student_id": 1
}
```

### List and get courses

`GET /courses/` returns every course. `GET /courses/{course_id}` returns one course, or `404 Not Found` when it does not exist.

### Update a course

`PATCH /courses/{course_id}` updates only the supplied fields. For example:

```json
{
  "credits": 5
}
```

It returns the updated course, or `404 Not Found` for an unknown course ID.

### Delete a course

`DELETE /courses/{course_id}` removes a course and returns `204 No Content`. An unknown course ID returns `404 Not Found`.

## Part 2 roster endpoints

### Sort students

`GET /students/sorted?by=age` sorts the roster by age using Insertion Sort. Use `GET /students/sorted?by=name` to sort alphabetically by name instead.

Example response begins like this for the seeded roster:

```json
[
  {
    "id": 4,
    "name": "Farhan Sheikh",
    "email": "farhan.sheikh@example.com",
    "age": 18
  }
]
```

### Search by name

`GET /students/search?name=Priya%20Iyer` finds an exact student name with Binary Search.

Example response:

```json
{
  "id": 5,
  "name": "Priya Iyer",
  "email": "priya.iyer@example.com",
  "age": 21
}
```

An unknown name returns `404 Not Found`.

### Create a roster report

`GET /students/report?min_age=21` returns a multi-line roster report and the number of students meeting the selected minimum age.

Example response:

```json
{
  "report": "[Age 22] Aditi Rao <aditi.rao@example.com>\n...",
  "count_meeting_min_age": 5
}
```

## Algorithm notes

Insertion Sort can take `O(n²)` time in the worst case because each item may need to move past many earlier items. Its best case is `O(n)` when the list is already sorted because the inner shifting loop does no work. Binary Search compares against the middle item and removes half of the remaining search range each time. It requires the list to be sorted by the field being searched, which is `name` in StudyTrack, or its left-versus-right decisions will not be reliable.

## Quick testing

After starting the app, try these URLs in a browser:

- [http://localhost:8000/students/sorted?by=age](http://localhost:8000/students/sorted?by=age) should begin with Farhan Sheikh, age 18.
- [http://localhost:8000/students/search?name=Priya%20Iyer](http://localhost:8000/students/search?name=Priya%20Iyer) should return Priya Iyer's record; changing the name to an unknown student should return `404 Not Found`.
- [http://localhost:8000/students/report?min_age=21](http://localhost:8000/students/report?min_age=21) should return `count_meeting_min_age` equal to 5.
