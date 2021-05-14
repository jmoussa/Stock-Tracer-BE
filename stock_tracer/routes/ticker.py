from fastapi import APIRouter, Depends, HTTPException

# from typing import List
from sqlalchemy.orm import Session
from stock_tracer.database.database import get_db
from stock_tracer.database import crud, schemas

router = APIRouter()


@router.get("/tickers/historical/{ticker}", response_model=schemas.Ticker)
def create_user(ticker: str, db: Session = Depends(get_db)):
    db_ticker = crud.get_ticker_by_name(db, ticker=ticker)
    if db_ticker:
        return db_ticker
    else:
        return HTTPException(status_code=404, detail="Item not found")
