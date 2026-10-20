from contextlib import asynccontextmanager
from pathlib import Path
from typing import Literal

from fastapi import Depends, FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from . import crud
from .ai_service import cosine_similarity, mock_embed, note_embeddings, notes, summarize_notes
from .algorithms import (
    binary_search_by_name,
    count_students_meeting_min_age,
    format_roster_report,
    insertion_sort_by_field,
)
from .database import Base, SessionLocal, engine
from .seed_data import seed_if_empty
from .schemas import (
    CourseCount,
    CourseCreate,
    CourseRead,
    CourseUpdate,
    StudentCreate,
    StudentRead,
    StudentReport,
    StudentUpdate,
)


# Run once when FastAPI starts: create tables, then seed the fixed roster only if empty.
@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_if_empty(db)
    finally:
        db.close()
    yield


app = FastAPI(lifespan=lifespan)
# The dashboard is served from this app; CORS only matters when the frontend runs on Live Server.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5500"],
    allow_methods=["GET", "POST", "PATCH", "DELETE"],
    allow_headers=["Content-Type"],
)


# Pydantic schemas for AI endpoints
class SummarizeRequest(BaseModel):
    text: str


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def student_to_dict(student):
    return StudentRead.model_validate(student).model_dump()


def integrity_error_to_http(error: IntegrityError) -> HTTPException:
    # Only a UNIQUE violation means the email is taken; anything else is invalid data.
    if "UNIQUE" in str(error.orig):
        return HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A student with this email already exists.",
        )
    return HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        detail="The data violates a database constraint.",
    )


def ensure_student_exists(db: Session, student_id: int):
    if crud.get_student(db, student_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")


@app.post("/students/", response_model=StudentRead, status_code=status.HTTP_201_CREATED)
def create_student(student_data: StudentCreate, db: Session = Depends(get_db)):
    try:
        return crud.create_student(db, student_data)
    except IntegrityError as error:
        db.rollback()
        raise integrity_error_to_http(error)


@app.get("/students/", response_model=list[StudentRead])
def read_students(
    min_age: int | None = Query(None, ge=0),
    skip: int = Query(0, ge=0),
    limit: int | None = Query(None, ge=1),
    db: Session = Depends(get_db),
):
    return crud.get_students(db, min_age, skip, limit)


@app.get("/students/sorted", response_model=list[StudentRead])
def read_sorted_students(
    by: Literal["age", "name"] = "age",
    db: Session = Depends(get_db),
):
    students = [student_to_dict(student) for student in crud.get_students(db)]
    return insertion_sort_by_field(students, by)


@app.get("/students/search", response_model=StudentRead)
def search_students(name: str, db: Session = Depends(get_db)):
    students = [student_to_dict(student) for student in crud.get_students(db)]
    students_by_name = sorted(students, key=lambda student: student["name"])
    student = binary_search_by_name(students_by_name, name)
    if student == -1:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")
    return student


@app.get("/students/report", response_model=StudentReport)
def get_student_report(min_age: int = Query(21, ge=0), db: Session = Depends(get_db)):
    students = [student_to_dict(student) for student in crud.get_students(db)]
    return {
        "report": format_roster_report(students),
        "count_meeting_min_age": count_students_meeting_min_age(students, min_age),
    }


@app.get("/students/{student_id}/course-count", response_model=CourseCount)
def get_student_course_count(student_id: int, db: Session = Depends(get_db)):
    ensure_student_exists(db, student_id)
    return {"student_id": student_id, "course_count": crud.count_courses_for_student(db, student_id)}


@app.get("/students/{student_id}", response_model=StudentRead)
def read_student(student_id: int, db: Session = Depends(get_db)):
    student = crud.get_student(db, student_id)
    if student is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")
    return student


@app.patch("/students/{student_id}", response_model=StudentRead)
def update_student(
    student_id: int,
    student_update: StudentUpdate,
    db: Session = Depends(get_db),
):
    try:
        student = crud.update_student(db, student_id, student_update)
    except IntegrityError as error:
        db.rollback()
        raise integrity_error_to_http(error)
    if student is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")
    return student


@app.delete("/students/{student_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_student(student_id: int, db: Session = Depends(get_db)):
    if crud.delete_student(db, student_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")


@app.post("/courses/", response_model=CourseRead, status_code=status.HTTP_201_CREATED)
def create_course(course_data: CourseCreate, db: Session = Depends(get_db)):
    ensure_student_exists(db, course_data.student_id)
    return crud.create_course(db, course_data)


@app.get("/courses/", response_model=list[CourseRead])
def read_courses(
    skip: int = Query(0, ge=0),
    limit: int | None = Query(None, ge=1),
    db: Session = Depends(get_db),
):
    return crud.get_courses(db, skip, limit)


@app.get("/courses/{course_id}", response_model=CourseRead)
def read_course(course_id: int, db: Session = Depends(get_db)):
    course = crud.get_course(db, course_id)
    if course is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
    return course


@app.patch("/courses/{course_id}", response_model=CourseRead)
def update_course(
    course_id: int,
    course_update: CourseUpdate,
    db: Session = Depends(get_db),
):
    if course_update.student_id is not None:
        ensure_student_exists(db, course_update.student_id)
    course = crud.update_course(db, course_id, course_update)
    if course is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
    return course


@app.delete("/courses/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_course(course_id: int, db: Session = Depends(get_db)):
    if crud.delete_course(db, course_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")


# AI Assistant endpoints (Part 3)

@app.post("/assistant/summarize")
def summarize(request: SummarizeRequest):
    """
    Summarize study notes using offline mock AI.

    Request body: {"text": "<raw notes>"}

    Returns: {"topic": str, "key_points": list[str], "difficulty": str}

    No API key or network call required.
    """
    return summarize_notes(request.text)


@app.get("/assistant/search")
def search_notes(query: str = ""):
    """
    Semantic search over fixed notes dataset using mock embeddings.

    Query parameter: query=<text>

    Returns: list of notes with similarity scores, sorted by score descending.

    If query is empty or all zeros, returns all notes with 0.0 scores in original order.
    Never raises ZeroDivisionError.
    """
    query_vector = mock_embed(query)

    results = []
    for note, note_vector in zip(notes, note_embeddings):
        similarity = cosine_similarity(query_vector, note_vector)
        results.append(
            {
                "id": note["id"],
                "text": note["text"],
                "similarity": similarity,
            }
        )

    # Sort by similarity descending, but preserve original order for ties/zeros
    results.sort(key=lambda x: (-x["similarity"], x["id"]))

    return results


frontend_directory = Path(__file__).resolve().parent.parent / "frontend"
app.mount("/", StaticFiles(directory=frontend_directory, html=True), name="frontend")
