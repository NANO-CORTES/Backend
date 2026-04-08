import os
import shutil
from fastapi import FastAPI, UploadFile, File, HTTPException

app = FastAPI(title="Microservice Ingestion API")

STORAGE_PATH = "/app/storage"

@app.get("/")
def root():
    return {"message": "Ingestion service is running"}

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        if not os.path.exists(STORAGE_PATH):
            os.makedirs(STORAGE_PATH)
            
        file_path = os.path.join(STORAGE_PATH, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        return {
            "filename": file.filename,
            "path": file_path,
            "status": "success",
            "message": "File uploaded successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
