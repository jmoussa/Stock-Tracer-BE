from fastapi import FastAPI
from stock_tracer.database.database import engine
from stock_tracer.database import models
from stock_tracer.routes import router as api_router

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


@app.get("/ping")
async def root():
    return {"message": "pong"}


app.include_router(api_router, prefix="/api")
