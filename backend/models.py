from sqlalchemy import CheckConstraint, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from database import Base


class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    age = Column(Integer)

    # A student can have many enrolled courses.
    courses = relationship("Course", back_populates="student")


class Course(Base):
    __tablename__ = "courses"
    __table_args__ = (
        # Keep credits within the supported course range at the database level.
        CheckConstraint("credits >= 1 AND credits <= 6", name="ck_course_credits_range"),
    )

    id = Column(Integer, primary_key=True, index=True)
    course_name = Column(String, nullable=False)
    credits = Column(Integer, nullable=False)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)

    # Each course enrollment belongs to one student.
    student = relationship("Student", back_populates="courses")
