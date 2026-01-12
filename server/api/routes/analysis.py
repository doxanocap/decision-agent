from fastapi import APIRouter, HTTPException, status, BackgroundTasks, Depends, Request
from sqlalchemy.orm import Session
from uuid import UUID
import logging

from server.db.database import get_db
from server.schemas.decision import DecisionCreate, AnalysisResponse
from server.services.orchestrator import get_orchestrator
from server.repositories.decision_repository import DecisionRepository
from server.services.decision_service import get_decision_service
from server.core.auth import get_current_user

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/analyze", status_code=status.HTTP_202_ACCEPTED)
async def analyze_decision(
    request: Request,
    decision: DecisionCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    user_id: UUID = Depends(get_current_user)
):
    """
    Start decision analysis in background.
    Returns the decision_id immediately.

    Requires authentication (MVP: hardcoded user, Future: JWT from auth-api)
    """
    try:
        # 1. Create decision in DB with user_id
        service = get_decision_service(db)
        db_decision = service.create_new_decision(decision, user_id)
        
        # 2. Start background orchestration
        orchestrator = get_orchestrator()
        background_tasks.add_task(
            orchestrator.run_background_analysis, 
            db, 
            db_decision.id, 
            decision
        )
        
        return {
            "decision_id": db_decision.id,
            "status": "pending",
            "message": "Analysis started in background"
        }
    except Exception as e:
        logger.error(f"Failed to start analysis: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start analysis: {str(e)}"
        )


@router.get("/{decision_id}/status")
async def get_analysis_status(
    decision_id: UUID, 
    db: Session = Depends(get_db),
    user_id: UUID = Depends(get_current_user)
):
    """
    Check status and get results if completed.
    
    Only returns decisions owned by the authenticated user.
    """
    repo = DecisionRepository(db)
    db_decision = repo.get_by_id(decision_id)
    
    if not db_decision:
        raise HTTPException(status_code=404, detail="Decision not found")
    
    # Check ownership (важно для multi-user в будущем)
    if db_decision.user_id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return {
        "decision_id": decision_id,
        "status": db_decision.analysis_status,
        "results": {
            "ml_scores": db_decision.ml_scores,
            "llm_analysis": db_decision.llm_analysis,
            "retrieved_context": db_decision.retrieved_context
        } if db_decision.analysis_status in ["completed", "failed"] else None
    }


@router.get("/health")
async def health_check():
    """Check if analysis service is ready."""
    try:
        orchestrator = get_orchestrator()
        return {
            "status": "healthy",
            "ml_scoring": "ready",
            "llm_service": "ready",
            "rag_engine": "ready"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }
