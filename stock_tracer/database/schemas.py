from typing import Optional
from pydantic import BaseModel
import datetime


class TickerBase(BaseModel):
    name: str
    resolution: str = "1y"
    symbol: Optional[str] = None
    sector: Optional[str] = None
    financial_profile: Optional[dict] = None


class TickerCreate(TickerBase):
    pass


class Ticker(TickerBase):
    id: int
    updated_at: datetime.datetime = datetime.datetime.utcnow().isoformat()

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    email: str
    financial_profile: dict


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    is_active: bool

    class Config:
        orm_mode = True
