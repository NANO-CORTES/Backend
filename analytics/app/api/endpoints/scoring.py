from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import uuid
from app.core.database import get_db
from app.schemas.scoring import ScoringRequest, ScoringResultResponse
from app.services.scoring_service import ScoringService
from app.repositories import scoring_repo # Importamos el archivo
from app.models.scoring import ScoreExecution, ZoneScore

# Definimos el nombre del router
router = APIRouter() 

@router.post("/execute", response_model=ScoringResultResponse)
async def execute_scoring(request: ScoringRequest, db: Session = Depends(get_db)):
    # 1. Validar configuración activa (Punto 6 de AC)
    service = ScoringService()
    weights = await service.get_weights(request.configuration_id)
    
    # 2. Generar ID único de ejecución (Punto 4 de AC)
    execution_id = str(uuid.uuid4())
    
    # 3. Obtener datos de zonas (Simulado)
    zones_data = [{"zone_id": "Z-01", "pob": 0.8, "ingreso": 0.6, "educacion": 0.7, "competencia": 0.2}]
    
    # IMPORTANTE: Usamos scoring_repo.ScoringRepository porque lo importamos como módulo
    repo = scoring_repo.ScoringRepository(db)
    
    new_execution = ScoreExecution(
        id=execution_id,
        transformation_run_id=request.transformation_run_id,
        configuration_id=request.configuration_id
    )
    
    results = []
    zone_scores_models = []
    
    for zone in zones_data:
        score_val = service.calculate_score(zone, weights)
        level = service.get_level(score_val)
        
        # Creamos el modelo para la base de datos
        zone_scores_models.append(ZoneScore(
            execution_id=execution_id,
            zone_id=zone["zone_id"],
            score_value=score_val,
            score_level=level
        ))
        
        # Estructura para la respuesta JSON (coincide con ZoneScoreResponse en schemas)
        results.append({
            "zone_id": zone["zone_id"],
            "score_value": score_val,
            "score_level": level,
            "rank_position": None
        })

    # Guardar en DB
    repo.save_full_execution(new_execution, zone_scores_models)
    
    return {
        "execution_id": execution_id,
        "transformation_run_id": request.transformation_run_id,
        "results": results
    }

@router.get("/results")
def get_scoring_results(execution_id: str, db: Session = Depends(get_db)):
    repo = scoring_repo.ScoringRepository(db)
    return repo.get_results_by_execution(execution_id)