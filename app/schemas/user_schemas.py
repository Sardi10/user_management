from builtins import ValueError, any, bool, str
from pydantic import BaseModel, EmailStr, Field, validator, root_validator
from typing import Optional, List
from datetime import datetime
from enum import Enum
from uuid import UUID, uuid4
import uuid
import re
from app.models.user_model import UserRole
from app.utils.nickname_gen import generate_nickname


def validate_url(url: Optional[str]) -> Optional[str]:
    if url is None:
        return url
    url_regex = r'^https?:\/\/[^\s/$.?#].[^\s]*$'
    if not re.match(url_regex, url):
        raise ValueError('Invalid URL format')
    return url

class UserBase(BaseModel):
    email: EmailStr = Field(..., example="john.doe@example.com")
    nickname: Optional[str] = Field(None, min_length=3, pattern=r'^[\w-]+$', example=generate_nickname())
    first_name: Optional[str] = Field(None, example="John")
    last_name: Optional[str] = Field(None, example="Doe")
    bio: Optional[str] = Field(None, example="Experienced software developer specializing in web applications.")
    profile_picture_url: Optional[str] = Field(None, example="https://example.com/profiles/john.jpg")
    linkedin_profile_url: Optional[str] =Field(None, example="https://linkedin.com/in/johndoe")
    github_profile_url: Optional[str] = Field(None, example="https://github.com/johndoe")
    role: UserRole

    _validate_urls = validator('profile_picture_url', 'linkedin_profile_url', 'github_profile_url', pre=True, allow_reuse=True)(validate_url)
 
    class Config:
        from_attributes = True

class UserCreate(UserBase):
    email: EmailStr = Field(..., example="john.doe@example.com")
    password: str = Field(..., example="Secure*1234")
    # registration clients shouldn’t need to pick a role:
    role: UserRole = Field(
        default=UserRole.ANONYMOUS,
        description="(automatically assigned) default to ANONYMOUS")

class UserUpdate(UserBase):
    email: Optional[EmailStr] = Field(None, example="john.doe@example.com")
    nickname: Optional[str] = Field(None, min_length=3, pattern=r'^[\w-]+$', example="john_doe123")
    first_name: Optional[str] = Field(None, example="John")
    last_name: Optional[str] = Field(None, example="Doe")
    bio: Optional[str] = Field(None, example="Experienced software developer specializing in web applications.")
    profile_picture_url: Optional[str] = Field(None, example="https://example.com/profiles/john.jpg")
    linkedin_profile_url: Optional[str] =Field(None, example="https://linkedin.com/in/johndoe")
    github_profile_url: Optional[str] = Field(None, example="https://github.com/johndoe")
    role: Optional[str] = Field(None, example="AUTHENTICATED")

    @root_validator(pre=True)
    def check_at_least_one_value(cls, values):
        if not any(values.values()):
            raise ValueError("At least one field must be provided for update")
        return values

class UserResponse(UserBase):
    id: uuid.UUID = Field(..., example=uuid.uuid4())
    email: EmailStr = Field(..., example="john.doe@example.com")
    nickname: Optional[str] = Field(None, min_length=3, pattern=r'^[\w-]+$', example=generate_nickname())    
    is_professional: Optional[bool] = Field(default=False, example=True)
    role: UserRole

class LoginRequest(BaseModel):
    email: str = Field(..., example="john.doe@example.com")
    password: str = Field(..., example="Secure*1234")

class ErrorResponse(BaseModel):
    error: str = Field(..., example="Not Found")
    details: Optional[str] = Field(None, example="The requested resource was not found.")

class UserListResponse(BaseModel):
    items: List[UserResponse] = Field(..., example=[{
        "id": uuid.uuid4(), "nickname": generate_nickname(), "email": "john.doe@example.com",
        "first_name": "John", "bio": "Experienced developer", "role": "AUTHENTICATED",
        "last_name": "Doe", "bio": "Experienced developer", "role": "AUTHENTICATED",
        "profile_picture_url": "https://example.com/profiles/john.jpg", 
        "linkedin_profile_url": "https://linkedin.com/in/johndoe", 
        "github_profile_url": "https://github.com/johndoe"
    }])
    total: int = Field(..., example=100)
    page: int = Field(..., example=1)
    size: int = Field(..., example=10)

class UserProfileDTO(BaseModel):
    id: UUID = Field(
        ..., 
        example="0923c31a-40d2-4e86-8b27-80542567acd8"
    )
    email: EmailStr = Field(
        ..., 
        example="john.doe@example.com"
    )
    nickname: Optional[str] = Field(
        None, 
        example="jolly_lion_664"
    )
    first_name: Optional[str] = Field(
        None, 
        example="John"
    )
    last_name: Optional[str] = Field(
        None, 
        example="Doe"
    )
    bio: Optional[str] = Field(
        None,
        example="Experienced software developer specializing in web applications."
    )
    profile_picture_url: Optional[str] = Field(
        None,
        example="https://example.com/profiles/john.jpg"
    )
    linkedin_profile_url: Optional[str] = Field(
        None,
        example="https://linkedin.com/in/johndoe"
    )
    github_profile_url: Optional[str] = Field(
        None,
        example="https://github.com/johndoe"
    )
    role: UserRole = Field(
        ..., 
        example="ANONYMOUS"
    )
    is_professional: bool = Field(
        ..., 
        example=False
    )
    professional_status_updated_at: Optional[datetime] = Field(
        None, 
        example=None
    )

    class Config:
        from_attributes = True

class UserProfileUpdate(BaseModel):
    first_name: Optional[str]
    last_name: Optional[str]
    bio: Optional[str]
    profile_picture_url: Optional[str]
    linkedin_profile_url: Optional[str]
    github_profile_url: Optional[str]

    @root_validator(pre=True)
    def at_least_one_field(cls, values):
        if not any(values.values()):
            raise ValueError("At least one field must be provided")
        return values