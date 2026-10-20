import re

from pydantic import BaseModel, ConfigDict, Field, field_validator


EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def normalize_email(value: str) -> str:
    # Emails are compared case-insensitively, so store them lowercased.
    value = value.strip().lower()
    if not EMAIL_PATTERN.match(value):
        raise ValueError("email must be a valid address like name@example.com")
    return value


def normalize_name(value: str) -> str:
    value = value.strip()
    if not value:
        raise ValueError("name must not be empty")
    return value


class StudentCreate(BaseModel):
    name: str
    email: str
    age: int = Field(gt=0)

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        return normalize_name(value)

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        return normalize_email(value)


class StudentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: str
    age: int | None = None


class StudentUpdate(BaseModel):
    name: str | None = None
    email: str | None = None
    age: int | None = Field(default=None, gt=0)

    # Fields are optional to omit, but an explicit null is not a valid value.
    @field_validator("name", "email", "age", mode="before")
    @classmethod
    def reject_null(cls, value):
        if value is None:
            raise ValueError("field may be omitted but not set to null")
        return value

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        return normalize_name(value)

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        return normalize_email(value)


class StudentReport(BaseModel):
    report: str
    count_meeting_min_age: int


class CourseCount(BaseModel):
    student_id: int
    course_count: int


class CourseCreate(BaseModel):
    course_name: str
    credits: int = Field(ge=1, le=6)
    student_id: int

    @field_validator("course_name")
    @classmethod
    def validate_course_name(cls, value: str) -> str:
        return normalize_name(value)


class CourseRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    course_name: str
    credits: int
    student_id: int


class CourseUpdate(BaseModel):
    course_name: str | None = None
    credits: int | None = Field(default=None, ge=1, le=6)
    student_id: int | None = None

    @field_validator("course_name", "credits", "student_id", mode="before")
    @classmethod
    def reject_null(cls, value):
        if value is None:
            raise ValueError("field may be omitted but not set to null")
        return value

    @field_validator("course_name")
    @classmethod
    def validate_course_name(cls, value: str) -> str:
        return normalize_name(value)
