from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Any
from datetime import datetime
from bson import ObjectId
from pydantic_core import core_schema

class PyObjectId:
    @classmethod
    def __get_pydantic_core_schema__(cls, _source_type, _handler):
        return core_schema.chain_schema([
            core_schema.str_schema(),
            core_schema.no_info_after_validator_function(cls.validate, core_schema.str_schema()),
        ])

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, _core_schema, _handler):
        return {'type': 'string'}

class User(BaseModel):
    user_id: int
    username: str
    first_name: str
    last_name: str = ""
    language: str = "english"
    phone: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    religion: Optional[str] = None
    city: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    bio: Optional[str] = None
    photos: List[str] = []
    is_active: bool = True
    coins: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)

class UserResponse(User):
    id: PyObjectId = Field(default_factory=ObjectId, alias="_id")
    
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )

class Like(BaseModel):
    user_id: int
    liked_user_id: int
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Message(BaseModel):
    from_user_id: int
    to_user_id: int
    message_text: str
    message_type: str = "text"
    media_file_id: Optional[str] = None
    is_read: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Block(BaseModel):
    user_id: int
    blocked_user_id: int
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Complaint(BaseModel):
    user_id: int
    reported_user_id: Optional[int] = None
    complaint_type: str
    complaint_text: str
    status: str = "pending"
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Payment(BaseModel):
    user_id: int
    package_name: str
    coins_amount: int
    price: float
    status: str = "pending"
    screenshot_file_id: str
    admin_notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    processed_at: Optional[datetime] = None
    processed_by: Optional[int] = None

class PaymentResponse(Payment):
    id: PyObjectId = Field(default_factory=ObjectId, alias="_id")
    
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class LoginRequest(BaseModel):
    username: str
    password: str

class StatsResponse(BaseModel):
    total_users: int
    active_users: int
    total_matches: int
    pending_payments: int
    user_growth: float
    active_growth: float
    matches_growth: float
    payments_growth: float

class DateRangeRequest(BaseModel):
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    range_type: str = "last7"

class ChartDataResponse(BaseModel):
    labels: List[str]
    data: List[int]

class PaymentUpdateRequest(BaseModel):
    status: str
    admin_notes: Optional[str] = None
    processed_by: int