import pandas as pd
import numpy as np
import os
from typing import List, Optional
from unidecode import unidecode
from app.interfaces.transformation_service import ITransformationService
from app.interfaces.transformation_service import TransformationRun
from app.repository.transformation import TransformationRepository
from app.core.exceptions import DomainException
from app.core.config import settings
import logging

logger = logging.getLogger("TransformationService")

class TransformationService(ITransformationService):
    def __init__(self, repo: TransformationRepository = None):
        self.repo = repo
    
    def _normalize_text(self, text: str) -> str:
        if not isinstance(text, str):
            return text
        text = unidecode(text).lower()
        return ' '.join(text.split())

    def transform_dataset(self, file_hash: str, user_id: str = None) -> str:
        input_file = os.path.join(settings.STORAGE_PATH, f"{file_hash}.csv")
        output_file = os.path.join(settings.STORAGE_PATH, f"processed_{file_hash}.csv")

        if not os.path.exists(input_file):
            logger.error(f"Archivo no encontrado: {input_file}")
            raise DomainException(f"Dataset {file_hash} not found in storage.", status_code=404)

        try:
            # Load dataset
            df = pd.read_csv(input_file, dtype={'zone_code': str})
            
            # 1. Remove duplicate rows
            initial_count = len(df)
            df = df.drop_duplicates()
            duplicates_removed = initial_count - len(df)

            # 2. Text standardization
            str_cols = df.select_dtypes(include=['object', 'string']).columns
            for col in str_cols:
                if col == 'zone_code': continue
                df[col] = df[col].apply(self._normalize_text)
            
            if 'zone_code' in df.columns:
                df['zone_code'] = df['zone_code'].astype(str).str.strip()

            # 3. Numeric processing and Stats collection
            num_cols = df.select_dtypes(include=['int64', 'float64']).columns
            ignore_keywords = ['id', 'year', 'anio', 'año', 'fecha']
            stats_summary = {}

            for col in num_cols:
                is_metadata = any(k in col.lower() for k in ignore_keywords)
                
                # Basic stats for non-metadata numerical columns
                if not is_metadata:
                    stats_summary[col] = {
                        "min": float(df[col].min()),
                        "max": float(df[col].max()),
                        "mean": float(df[col].mean())
                    }

                if is_metadata:
                    continue
                
                # Median imputation
                if df[col].isnull().any():
                    median_val = df[col].median()
                    df[col] = df[col].fillna(median_val)

                # Min-Max Normalization
                c_min = df[col].min()
                c_max = df[col].max()
                if c_max != c_min:
                    df[col] = (df[col] - c_min) / (c_max - c_min)
                else:
                    df[col] = 0.0

            # Save processed dataset
            df.to_csv(output_file, index=False)
            
            # 4. Persistence of the run
            if self.repo:
                from app.models.transformation import TransformationRun
                new_run = TransformationRun(
                    file_hash=file_hash,
                    status="COMPLETED",
                    total_rows=len(df),
                    user_id=user_id,
                    details={
                        "duplicates_removed": duplicates_removed,
                        "columns_processed": list(df.columns),
                        "numeric_stats": stats_summary
                    }
                )
                self.repo.create(new_run)
                logger.info(f"Transformation run persisted for {file_hash}")

            return output_file

        except Exception as e:
            logger.exception(f"Error procesando dataset {file_hash}")
            if self.repo:
                from app.models.transformation import TransformationRun
                error_run = TransformationRun(
                    file_hash=file_hash,
                    status="FAILED",
                    total_rows=0,
                    user_id=user_id,
                    details={"error": str(e)}
                )
                self.repo.create(error_run)
            
            if isinstance(e, DomainException):
                raise e
            raise DomainException(f"Failed to process dataset {file_hash}: {str(e)}", status_code=500)

    def get_results(self, limit: int = 100, skip: int = 0) -> List[TransformationRun]:
        if not self.repo:
            return []
        return self.repo.get_all(limit=limit, skip=skip)
