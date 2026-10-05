from pydantic import BaseModel, EmailStr, ConfigDict


class EmployeeBase(BaseModel):
    name: str
    email: EmailStr
    department: str
    salary: float


class EmployeeCreate(EmployeeBase):
    pass


class EmployeeUpdate(BaseModel):
    name: str | None = None
    email: EmailStr | None = None
    department: str | None = None
    salary: float | None = None


class EmployeeUserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: str
    phone: str | None = None
    position: str | None = None
    profile_image: str | None = None

    model_config = ConfigDict(from_attributes=True)


class EmployeeResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    department: str
    salary: float
    is_active: bool

    user: EmployeeUserResponse | None = None

    model_config = ConfigDict(from_attributes=True)