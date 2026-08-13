from sqlalchemy.orm import Session

from .models import Course, Student
from .schemas import CourseCreate, CourseUpdate, StudentCreate, StudentUpdate


def create_student(db: Session, student_data: StudentCreate):
    student = Student(**student_data.model_dump())
    db.add(student)
    db.commit()
    db.refresh(student)
    return student


def get_students(db: Session, min_age: int | None = None):
    query = db.query(Student)
    if min_age is not None:
        query = query.filter(Student.age >= min_age)
    return query.all()


def get_student(db: Session, student_id: int):
    return db.query(Student).filter(Student.id == student_id).first()


def update_student(db: Session, student_id: int, student_update: StudentUpdate):
    student = get_student(db, student_id)
    if student is None:
        return None

    for field, value in student_update.model_dump(exclude_unset=True).items():
        setattr(student, field, value)

    db.commit()
    db.refresh(student)
    return student


def delete_student(db: Session, student_id: int):
    student = get_student(db, student_id)
    if student is None:
        return None

    db.delete(student)
    db.commit()
    return student


def create_course(db: Session, course_data: CourseCreate):
    course = Course(**course_data.model_dump())
    db.add(course)
    db.commit()
    db.refresh(course)
    return course


def get_courses(db: Session):
    return db.query(Course).all()


def get_course(db: Session, course_id: int):
    return db.query(Course).filter(Course.id == course_id).first()


def update_course(db: Session, course_id: int, course_update: CourseUpdate):
    course = get_course(db, course_id)
    if course is None:
        return None

    for field, value in course_update.model_dump(exclude_unset=True).items():
        setattr(course, field, value)

    db.commit()
    db.refresh(course)
    return course


def delete_course(db: Session, course_id: int):
    course = get_course(db, course_id)
    if course is None:
        return None

    db.delete(course)
    db.commit()
    return course
