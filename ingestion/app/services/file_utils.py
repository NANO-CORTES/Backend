import hashlib
import io
import json
import os
import uuid

import pandas as pd
from fastapi import UploadFile

from app.core.config import settings
from app.core.exceptions import DomainException

ALLOWED_EXTENSIONS = {".csv", ".json"}
MAX_FILE_SIZE_MB   = 50
REQUIRED_COLUMNS   = ["zone_code", "zone_name"]
MAX_NULL_PERCENTAGE = 0.3


def validateExtension(filename: str) -> str:
    _, ext = os.path.splitext(filename.lower())
    if ext not in ALLOWED_EXTENSIONS:
        raise DomainException(
            f"Extensión no permitida: '{ext}'. Solo se aceptan: {sorted(ALLOWED_EXTENSIONS)}",
            status_code=400
        )
    return ext


def generateUniqueFileName(ext: str) -> str:
    return f"{uuid.uuid4().hex}{ext}"


def hashContent(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def processValidation(df: pd.DataFrame) -> tuple[int, int, int, list]:
    cols = [str(c).lower().strip() for c in df.columns]
    df.columns = cols

    errors = []
    for requiredCol in REQUIRED_COLUMNS:
        if requiredCol not in cols:
            errors.append(f"El dataset no contiene la columna requerida: '{requiredCol}'")

    if errors:
        raise DomainException(" ".join(errors), status_code=400)

    numericCols = df.select_dtypes(include=['number']).columns.tolist()
    if len(numericCols) < 3:
        raise DomainException(
            f"El dataset debe contener al menos 3 variables numéricas. Se encontraron: {len(numericCols)}",
            status_code=400
        )

    for requiredCol in REQUIRED_COLUMNS:
        nullRatio = df[requiredCol].isnull().sum() / len(df)
        if nullRatio > MAX_NULL_PERCENTAGE:
            raise DomainException(
                f"La columna '{requiredCol}' excede el límite de nulos permitido (30%). Actual: {nullRatio:.1%}",
                status_code=400
            )

    duplicatedCodes = df['zone_code'].duplicated(keep=False)
    if duplicatedCodes.any():
        errors.append(f"Se encontraron filas duplicadas en 'zone_code' (serán conservadas temporalmente o limpiadas en transformación).")

    validRecordCount = len(df.dropna(subset=REQUIRED_COLUMNS))
    invalidRecordCount = len(df) - validRecordCount

    # Extract unique zones
    uniqueZonesData = df.drop_duplicates(subset=['zone_code']).dropna(subset=['zone_code', 'zone_name'])
    zones = [
        {"zoneCode": str(row['zone_code']), "zoneName": str(row['zone_name'])}
        for _, row in uniqueZonesData.iterrows()
    ]

    return len(df), validRecordCount, invalidRecordCount, zones


def validateCsvContent(content: bytes) -> tuple[int, int, int, list]:
    try:
        df = pd.read_csv(io.BytesIO(content))
    except pd.errors.EmptyDataError:
        raise DomainException("El archivo CSV está vacío.", status_code=400)
    except Exception as e:
        raise DomainException(f"Error al parsear CSV: {str(e)}", status_code=400)

    return processValidation(df)


def validateJsonContent(content: bytes) -> tuple[int, int, int, list]:
    try:
        parsed = json.loads(content)
        df = pd.DataFrame(parsed)
    except json.JSONDecodeError as e:
        raise DomainException(f"El archivo JSON no es válido: {str(e)}", status_code=400)
    except Exception as e:
        raise DomainException(f"Error al procesar JSON a DataFrame: {str(e)}", status_code=400)

    if df.empty:
         raise DomainException("El archivo JSON está vacío o no contiene registros válidos.", status_code=400)

    return processValidation(df)


def saveToDisk(content: bytes, uniqueFileName: str) -> str:
    os.makedirs(settings.STORAGE_PATH, exist_ok=True)
    filePath = os.path.join(settings.STORAGE_PATH, uniqueFileName)
    with open(filePath, "wb") as f:
        f.write(content)
    return filePath


async def validateAndProcessFile(file: UploadFile) -> tuple[str, str, int, dict]:
    content = await file.read()

    fileSizeBytes = len(content)
    if fileSizeBytes > MAX_FILE_SIZE_MB * 1024 * 1024:
        raise DomainException(
            f"Archivo demasiado grande. Máximo permitido: {MAX_FILE_SIZE_MB} MB",
            status_code=400
        )

    ext = validateExtension(file.filename)
    fileHash = hashContent(content)

    if ext == ".csv":
        total, valid, invalid, zones = validateCsvContent(content)
    else:
        total, valid, invalid, zones = validateJsonContent(content)

    uniqueFileName = generateUniqueFileName(ext)
    saveToDisk(content, uniqueFileName)

    await file.seek(0)
    
    validationData = {
        "recordCount": total,
        "validRecordCount": valid,
        "invalidRecordCount": invalid,
        "zones": zones
    }

    return fileHash, uniqueFileName, fileSizeBytes, validationData
