import pandas as pd
import os
from typing import List, Dict
from app.interfaces.analytics_service import IAnalyticsService
from app.core.exceptions import DomainException
from app.core.config import settings

class AnalyticsService(IAnalyticsService):
    
    def get_zones(self, dataset_hash: str) -> List[Dict[str, str]]:
        processed_file = os.path.join(settings.STORAGE_PATH, f"processed_{dataset_hash}.csv")
        base_file = os.path.join(settings.STORAGE_PATH, f"{dataset_hash}.csv")
        
        target_file = processed_file if os.path.exists(processed_file) else base_file
        
        if not os.path.exists(target_file):
             raise DomainException(f"Dataset {dataset_hash} not found in storage.", status_code=404)

        try:
            head = pd.read_csv(target_file, nrows=0)
            col_map = {c.lower().strip(): c for c in head.columns}
            
            dep_col = col_map.get("departamento", "departamento")
            mun_col = col_map.get("municipio", "municipio")

            df = pd.read_csv(target_file, usecols=[dep_col, mun_col])
            
            df = df.drop_duplicates()
            df = df.rename(columns={dep_col: "departamento", mun_col: "municipio"})

            df = df.sort_values(by=["departamento", "municipio"])
            
            return df.to_dict('records')
            
        except Exception as e:
            raise DomainException(f"Failed to extract zones: {str(e)}", status_code=500)
