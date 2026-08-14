from pathlib import Path
from typing import Literal

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from . import crud
from .algorithms import (
    binary_search_by_name,
    count_students_meeting_min_age,
    format_roster_report,
    insertion_sort_by_field,
)
from .database import Base, SessionLocal, engine
from .models import Course
from .seed_data import seed_if_empty
from .schemas import (
    CourseCreate,
    CourseRead,
    CourseUpdate,
    StudentCreate,
    StudentRead,
    StudentUpdate,
)


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5500"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Run once when FastAPI starts: create tables, then seed the fixed roster only if empty.
@app.on_event("startup")
def create_database_tables():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_if_empty(db)
    finally:
        db.close()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def student_to_dict(student):
    return {
        "id": student.id,
        "name": student.name,
        "email": student.email,
        "age": student.age,
    }


@app.post("/students/", response_model=StudentRead, status_code=status.HTTP_201_CREATED)
def create_student(student_data: StudentCreate, db: Session = Depends(get_db)):
    try:
        return crud.create_student(db, student_data)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A student with this email already exists.",
        )


@app.get("/students/", response_model=list[StudentRead])
def read_students(min_age: int | None = None, db: Session = Depends(get_db)):
    return crud.get_students(db, min_age)


@app.get("/students/sorted")
def read_sorted_students(
    by: Literal["age", "name"] = "age",
    db: Session = Depends(get_db),
):
    students = [student_to_dict(student) for student in crud.get_students(db)]
    return insertion_sort_by_field(students, by)


@app.get("/students/search")
def search_students(name: str, db: Session = Depends(get_db)):
    students = [student_to_dict(student) for student in crud.get_students(db)]
    students_by_name = sorted(students, key=lambda student: student["name"])
    student = binary_search_by_name(students_by_name, name)
    if student == -1:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")
    return student


@app.get("/students/report")
def get_student_report(min_age: int = 21, db: Session = Depends(get_db)):
    students = [student_to_dict(student) for student in crud.get_students(db)]
    return {
        "report": format_roster_report(students),
        "count_meeting_min_age": count_students_meeting_min_age(students, min_age),
    }


@app.get("/students/{student_id}/course-count")
def get_student_course_count(student_id: int, db: Session = Depends(get_db)):
    if crud.get_student(db, student_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")

    course_count = db.query(func.count(Course.id)).filter(Course.student_id == student_id).scalar()
    return {"student_id": student_id, "course_count": course_count}


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
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A student with this email already exists.",
        )
    if student is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")
    return student


@app.delete("/students/{student_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_student(student_id: int, db: Session = Depends(get_db)):
    if crud.delete_student(db, student_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")


@app.post("/courses/", response_model=CourseRead, status_code=status.HTTP_201_CREATED)
def create_course(course_data: CourseCreate, db: Session = Depends(get_db)):
    return crud.create_course(db, course_data)


@app.get("/courses/", response_model=list[CourseRead])
def read_courses(db: Session = Depends(get_db)):
    return crud.get_courses(db)


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
    course = crud.update_course(db, course_id, course_update)
    if course is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
    return course


@app.delete("/courses/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_course(course_id: int, db: Session = Depends(get_db)):
    if crud.delete_course(db, course_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")


frontend_directory = Path(__file__).resolve().parent.parent / "frontend"
app.mount("/", StaticFiles(directory=frontend_directory, html=True), name="frontend")
