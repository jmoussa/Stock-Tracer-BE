from fastapi import FastAPI
from stock_tracer.database.database import engine
from stock_tracer.database import models
from stock_tracer.routes import router as api_router
from fastapi.middleware.cors import CORSMiddleware

models.Base.metadata.create_all(bind=engine)
app = FastAPI()

origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/healthcheck")
async def root():
    return {"ping": "pong"}


app.include_router(api_router, prefix="/api")
