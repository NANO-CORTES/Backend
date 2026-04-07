from fastapi import FastAPI
from app.api import transform
from app.database import Base, engine

# Create the database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Microservice API - Transformation")

app.include_router(transform.router)

@app.get("/")
def root():
    return {"message": "Service is running"}
