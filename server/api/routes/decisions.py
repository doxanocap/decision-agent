from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from server.db.database import get_db
from server.schemas.decision import DecisionResponse, DecisionUpdateOutcome
from server.services.decision_service import DecisionService, get_decision_service
from server.core.auth import get_current_user

router = APIRouter()

def get_service(db: Session = Depends(get_db)) -> DecisionService:
    return get_decision_service(db)

@router.get("/", response_model=List[DecisionResponse])
def get_history(
    skip: int = 0, 
    limit: int = 100, 
    service: DecisionService = Depends(get_service),
    user_id: UUID = Depends(get_current_user)
):
    """Get decision history for authenticated user."""
    return service.get_history(skip, limit, user_id)

@router.patch("/{decision_id}/outcome", response_model=DecisionResponse)
def update_outcome(
    decision_id: UUID, 
    outcome_data: DecisionUpdateOutcome, 
    service: DecisionService = Depends(get_service),
    user_id: UUID = Depends(get_current_user)
):
    """Record what actually happened after making a decision."""
    decision = service.record_outcome(decision_id, outcome_data, user_id)
    if decision is None:
        raise HTTPException(status_code=404, detail="Decision not found")
    return decision
