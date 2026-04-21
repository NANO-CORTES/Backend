from sqlalchemy import Column, String, Float, ForeignKey, DateTime, Integer
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base

class ScoreExecution(Base):
    __tablename__ = "score_executions"
    __table_args__ = {"schema": "analytics"}

    id = Column(String, primary_key=True, index=True) # execution_id único
    transformation_run_id = Column(String, nullable=False)
    configuration_id = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relación con los resultados
    scores = relationship("ZoneScore", back_populates="execution")

class ZoneScore(Base):
    __tablename__ = "zone_scores"
    __table_args__ = {"schema": "analytics"}

    id = Column(Integer, primary_key=True, autoincrement=True)
    execution_id = Column(String, ForeignKey("analytics.score_executions.id"))
    zone_id = Column(String, nullable=False)
    score_value = Column(Float, nullable=False) # Valor entre 0.0 y 1.0
    score_level = Column(String, nullable=False) # Alta, Media, Baja
    rank_position = Column(Integer, nullable=True) # Se llenará después del ranking

    execution = relationship("ScoreExecution", back_populates="scores")