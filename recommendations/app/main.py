from fastapi import FastAPI

app = FastAPI(title="Microservice API")

@app.get("/")
def root():
    return {"message": "Service is running"}
