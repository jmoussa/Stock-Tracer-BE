from logging import getLogger
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from stock_tracer.database.database import get_db
from stock_tracer.database import crud, schemas, models
from stock_tracer.robinhood.rh import RobinhoodConnector
from stock_tracer.authentication.auth import get_current_active_user
from stock_tracer.config import config

logger = getLogger(__name__)
router = APIRouter()

# TODO: create endpoint and add to app state instead of keeping credentials tied to config
rh = RobinhoodConnector(config.robinhood["username"], config.robinhood["password"])


@router.get("/tickers/{ticker}")
def fetch_ticker(
    ticker: str,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    db_ticker = crud.get_ticker_by_name(db, ticker=ticker)
    if db_ticker is None:
        return HTTPException(status_code=404, detail="Item not found")
    return db_ticker


@router.get("/rh_historical")
def get_portfolio_historicals(
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    historical_data = rh.fetch_historicals()
    return historical_data


@router.get("/rh_portfolio")
def import_robinhood_portfoio(
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    res = rh.fetch_build_holdings()
    return res
