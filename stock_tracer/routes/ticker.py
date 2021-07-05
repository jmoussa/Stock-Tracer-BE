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


@router.post("/robinhood/info")
def get_robinhood_info(
    request: dict,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    rh = RobinhoodConnector(
        request["username"],
        request["password"],
        mfa_code=request.get("mfa_code", None),
    )

    if rh and rh.rh_conn is not None:
        logger.warning("Logged Into Robinhood - Fetching Info...")
        build_holdings = rh.fetch_build_holdings()
        transactions = rh.fetch_transactions()
        historicals = rh.fetch_historicals()
        robinhood_data = {
            "build_holdings": build_holdings,
            "transactions": transactions,
            "historicals": historicals,
        }
        return robinhood_data
    else:
        return {"message": "missing mfa"}
