from fastapi import APIRouter

from stock_tracer.routes.user import router as users_router
from stock_tracer.routes.ticker import router as ticker_router
from stock_tracer.routes.auth import router as auth_router

router = APIRouter()
router.include_router(users_router)
router.include_router(ticker_router)
router.include_router(auth_router)
