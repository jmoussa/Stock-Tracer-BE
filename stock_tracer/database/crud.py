from sqlalchemy.orm import Session
import datetime
from . import models, schemas
import yfinance as yf
import logging
from sqlalchemy.sql.expression import and_

logger = logging.getLogger(__name__)


def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def create_ticker_in_db(db: Session, ticker_name, historical_data, ticker_symbol, resolution):
    db_ticker = models.Ticker(
        name=ticker_name,
        symbol=ticker_symbol,
        historical_data=historical_data,
        resolution=resolution,
        updated_at=datetime.datetime.utcnow().isoformat(),
    )
    db.add(db_ticker)
    db.commit()
    db.refresh(db_ticker)
    return db_ticker


def remote_fetch_ticker(ticker: str, db: Session):
    logger.warning(f"Fetching {ticker}")
    ticker_obj = yf.Ticker(ticker)
    ticker_name = ticker_obj.info["shortName"]
    df = ticker_obj.history(period="ytd")
    df.index = df.index.astype("str")
    logger.warning(df)
    if not df.empty:
        db_ticker = create_ticker_in_db(db, ticker_name, df.to_dict("index"), ticker, "ytd")
        return db_ticker
    else:
        return {}


def get_ticker_by_name(db: Session, ticker: str = None):
    if ticker:
        since = datetime.datetime.utcnow() - datetime.timedelta(hours=1)
        db_entry = (
            db.query(models.Ticker)
            .filter(and_(models.Ticker.symbol == ticker, models.Ticker.updated_at < since))
            .first()
        )
        logger.warning(f"DB ENTRY: {db_entry}")
        if db_entry:
            return db_entry
        else:
            return remote_fetch_ticker(ticker, db)
    else:
        return db.query(models.Ticker).all()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate):
    # TODO: hashing
    fake_hashed_password = user.password + "notreallyhashed"
    db_user = models.User(
        email=user.email, hashed_password=fake_hashed_password, financial_profile=user.financial_profile
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_tickers(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Ticker).offset(skip).limit(limit).all()
