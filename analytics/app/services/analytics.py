import pandas as pd
import os
from typing import List, Dict
from app.interfaces.analytics_service import IAnalyticsService
from app.core.exceptions import DomainException
from app.core.config import settings

class AnalyticsService(IAnalyticsService):
    
    def get_zones(self, dataset_hash: str) -> List[Dict[str, str]]:
        # Primero busca la procesada, si no existe, la normal
        processed_file = os.path.join(settings.STORAGE_PATH, f"processed_{dataset_hash}.csv")
        base_file = os.path.join(settings.STORAGE_PATH, f"{dataset_hash}.csv")
        
        target_file = processed_file if os.path.exists(processed_file) else base_file
        
        if not os.path.exists(target_file):
             raise DomainException(f"Dataset {dataset_hash} not found in storage.", status_code=404)

        try:
            # Optimizamos lectura cargando solo las columnas de interes (usa lowercase por la transformacion HU-07)
            # Primero leemos 1 row solo para agarrar las caps exactas si no está procesado
            head = pd.read_csv(target_file, nrows=0)
            col_map = {c.lower().strip(): c for c in head.columns}
            
            dep_col = col_map.get("departamento", "departamento")
            mun_col = col_map.get("municipio", "municipio")

            df = pd.read_csv(target_file, usecols=[dep_col, mun_col])
            
            df = df.drop_duplicates()
            # Mapear a salida estandar
            df = df.rename(columns={dep_col: "departamento", mun_col: "municipio"})
            
            # Sort alpha
            df = df.sort_values(by=["departamento", "municipio"])
            
            return df.to_dict('records')
            
        except Exception as e:
            raise DomainException(f"Failed to extract zones: {str(e)}", status_code=500)
