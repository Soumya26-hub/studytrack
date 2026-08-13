from pydantic import BaseModel, ConfigDict, Field, field_validator


class StudentCreate(BaseModel):
    name: str
    email: str
    age: int = Field(gt=0)

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        if "@" not in value:
            raise ValueError("email must contain @")
        return value


class StudentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: str
    age: int | None = None


class StudentUpdate(BaseModel):
    name: str | None = None
    email: str | None = None
    age: int | None = None


class CourseCreate(BaseModel):
    course_name: str
    credits: int = Field(ge=1, le=6)
    student_id: int


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
