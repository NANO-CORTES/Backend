import pandas as pd
import os
import unicodedata
from app.interfaces.transformation_service import ITransformationService
from app.core.exceptions import DomainException
from app.core.config import settings

class TransformationService(ITransformationService):
    
    def _normalize_text(self, text: str) -> str:
        if not isinstance(text, str):
            return text
        # Remove accents
        text = ''.join(c for c in unicodedata.normalize('NFD', text) if unicodedata.category(c) != 'Mn')
        # Lowercase and strip extra spaces
        return ' '.join(text.lower().split())

    def transform_dataset(self, file_hash: str) -> str:
        input_file = os.path.join(settings.STORAGE_PATH, f"{file_hash}.csv")
        output_file = os.path.join(settings.STORAGE_PATH, f"processed_{file_hash}.csv")

        if not os.path.exists(input_file):
            raise DomainException(f"Dataset {file_hash} not found in storage.", status_code=404)

        try:
            df = pd.read_csv(input_file)

            # 1. Normalizar Strings (Tildes, lower, trim)
            str_cols = df.select_dtypes(include=['object', 'string']).columns
            for col in str_cols:
                df[col] = df[col].apply(self._normalize_text)

            # 2. Escalar Numericos (Min-Max 0-1) exceptuando posibles keys
            num_cols = df.select_dtypes(include=['int64', 'float64']).columns
            ignore_keywords = ['id', 'year', 'anio', 'año', 'fecha']
            
            for col in num_cols:
                if any(k in col.lower() for k in ignore_keywords):
                    continue
                # Min-Max Scaling
                c_min = df[col].min()
                c_max = df[col].max()
                if c_max != c_min: # Evitar división por 0
                    df[col] = (df[col] - c_min) / (c_max - c_min)
                else:
                    df[col] = 0 # O dejarlo igual
                    
            # Persistir
            df.to_csv(output_file, index=False)
            return output_file

        except Exception as e:
            if isinstance(e, DomainException):
                raise e
            raise DomainException(f"Failed to process dataset {file_hash}: {str(e)}", status_code=500)
