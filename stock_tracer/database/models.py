import datetime
from sqlalchemy import Boolean, Column, Integer, String, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from stock_tracer.database.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    financial_profile = Column(JSONB)


class Ticker(Base):
    __tablename__ = "tickers"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    resolution = Column(String, primary_key=True)
    name = Column(String)
    symbol = Column(String, primary_key=True)
    historical_data = Column(JSONB)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow)
