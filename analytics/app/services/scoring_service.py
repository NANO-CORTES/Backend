import httpx
from app.core.config import settings

class ScoringService:
    async def get_weights(self, config_id: str): # Cambiado a método de instancia
        async with httpx.AsyncClient() as client:
            # Esta URL viene de tu configuración de infraestructura
            response = await client.get(f"{settings.CONFIGURATION_SERVICE_URL}/{config_id}")
            if response.status_code != 200:
                raise Exception("No se pudo obtener la configuración de pesos")
            return response.json()

    def calculate_score(self, data: dict, weights: dict) -> float: # Agregado self
        # Implementación de tu fórmula de física/cálculo aplicada
        score = (
            (weights['w1'] * data['pob']) +
            (weights['w2'] * data['ingreso']) +
            (weights['w3'] * data['educacion']) -
            (weights['w4'] * data['competencia'])
        )
        return max(0.0, min(1.0, score))

    def get_level(self, score: float) -> str: # Agregado self
        if score > 0.7: return "Alta oportunidad"
        if score >= 0.4: return "Media oportunidad"
        return "Baja oportunidad"