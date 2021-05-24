from logging import getLogger
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from stock_tracer.database.database import get_db
from stock_tracer.database import crud, schemas, models
from stock_tracer.robinhood.rh import fetch_build_holdings
from stock_tracer.authentication.auth import get_current_active_user

logger = getLogger(__name__)
router = APIRouter()


@router.get("/tickers/historical/{ticker}", response_model=schemas.Ticker)
def fetch_ticker(ticker: str, db: Session = Depends(get_db)):
    db_ticker = crud.get_ticker_by_name(db, ticker=ticker)
    if db_ticker:
        return db_ticker
    else:
        return HTTPException(status_code=404, detail="Item not found")


@router.post("/rh_portfolio")
def import_robinhood_portfoio(
    form_data: dict,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    res = fetch_build_holdings(form_data["username"], form_data["password"])
    logger.warning(res)
    return res
