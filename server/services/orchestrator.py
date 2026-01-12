from typing import Dict, List, Optional
from uuid import UUID
import logging

from sqlalchemy.orm import Session
from server.schemas.decision import DecisionCreate, AnalysisResponse
from server.repositories.decision_repository import DecisionRepository
from server.services.ml_scoring import get_ml_scoring
from server.services.llm_service import get_llm_service
from server.services.engine import engine

logger = logging.getLogger(__name__)


class OrchestratorService:
    def __init__(self):
        self.ml_scoring = get_ml_scoring()
        self.llm_service = get_llm_service()
        self.engine = engine

    def run_background_analysis(self, db: Session, decision_id: UUID, decision_data: DecisionCreate):
        """Executed in background. Coordinates services and updates DB."""
        repo = DecisionRepository(db)
        try:
            # 1. Update status to analyzing
            repo.update_analysis(decision_id, status="analyzing")
            
            # 2. VALIDATION GUARDRAILS - Check argument quality
            from server.services.argument_validator import ArgumentQualityValidator
            import uuid
            
            # Generate strict UUIDs for each argument (prevents logic swap)
            ml_input = []
            for i, arg in enumerate(decision_data.arguments):
                arg_id = str(uuid.uuid4())  # Unique ID for each argument
                ml_input.append({
                    "id": arg_id,
                    "text": arg.text,
                    "variant_name": arg.variant_name,
                    "type": arg.type
                })
            
            # Validate argument quality
            validation_result = ArgumentQualityValidator.validate_arguments(ml_input)
            
            if not validation_result['is_valid']:
                # Insufficient data - fail with clear message
                error_details = {
                    "error": "INSUFFICIENT_DATA",
                    "message": "Some arguments lack sufficient reasoning",
                    "invalid_arguments": validation_result['invalid_arguments'],
                    "quality_score": validation_result['quality_score']
                }
                repo.update_analysis(
                    decision_id,
                    status="failed",
                    llm_analysis=error_details
                )
                logger.warning(f"Analysis rejected for {decision_id}: {error_details}")
                return
            
            logger.info(f"Validation passed: {validation_result['valid_arguments']}/{validation_result['total_arguments']} arguments valid")
            
            # 3. ML Scoring (with absolute quality)
            try:
                logger.info(f"ML Scoring: {len(ml_input)} arguments")
                ml_scores = self.ml_scoring.score_arguments(ml_input, decision_data.context)
            except Exception as e:
                logger.error(f"ML Scoring failed: {str(e)}")
                error_details = {
                    "error": "ML_SCORING_FAILED",
                    "user_message": "Не удалось оценить качество аргументов. Попробуйте еще раз через минуту.",
                    "technical_details": str(e)
                }
                repo.update_analysis(decision_id, status="failed", llm_analysis=error_details)
                return
            
            # 4. RAG (graceful degradation if fails)
            retrieved_context = []
            try:
                query = f"{decision_data.context}\n" + "\n".join([a.text for a in decision_data.arguments])
                logger.info("RAG: Retrieving context")
                retrieved_context = self.engine.simple_retrieval(query, top_k=3)
            except Exception as e:
                logger.warning(f"RAG retrieval failed, continuing without context: {str(e)}")
                # Continue without RAG context - not critical
                retrieved_context = []
            
            # 5. LLM Analysis (with strict ID mapping)
            try:
                logger.info("LLM: Analyzing decision")
                reasoning_analysis = self.llm_service.analyze_decision(
                    decision_data, ml_scores, retrieved_context, ml_input
                )
            except Exception as e:
                logger.error(f"LLM Analysis failed: {str(e)}")
                
                # Check if it's an OpenAI API error
                error_message = str(e).lower()
                if "rate limit" in error_message or "quota" in error_message:
                    user_message = "ИИ перегружен запросами. Пожалуйста, попробуйте через минуту. 🕐"
                elif "timeout" in error_message or "timed out" in error_message:
                    user_message = "ИИ не успел обработать запрос. Попробуйте упростить аргументы или повторите попытку."
                elif "api key" in error_message or "authentication" in error_message:
                    user_message = "Проблема с доступом к ИИ. Мы уже работаем над решением. Попробуйте позже."
                else:
                    user_message = "ИИ временно недоступен. Попробуйте еще раз через минуту. 🔄"
                
                error_details = {
                    "error": "LLM_ANALYSIS_FAILED",
                    "user_message": user_message,
                    "technical_details": str(e)
                }
                repo.update_analysis(decision_id, status="failed", llm_analysis=error_details)
                return
            
            # 6. Indexing in Qdrant (graceful degradation if fails)
            try:
                logger.info("Indexing decision in Qdrant")
                self.engine.index_decision(str(decision_id), decision_data.context, ml_input)
            except Exception as e:
                logger.warning(f"Qdrant indexing failed, but analysis completed: {str(e)}")
                # Don't fail the entire analysis if indexing fails
            
            # 7. Save results
            repo.update_analysis(
                decision_id,
                status="completed",
                ml_scores=ml_scores,
                llm_analysis=reasoning_analysis.dict(),
                retrieved_context=retrieved_context
            )
            
            logger.info(f"Analysis completed for {decision_id}")
            
        except Exception as e:
            logger.error(f"Unexpected error in analysis: {str(e)}")
            error_details = {
                "error": "UNEXPECTED_ERROR",
                "user_message": "Произошла непредвиденная ошибка. Наша команда уже уведомлена. Попробуйте позже.",
                "technical_details": str(e)
            }
            repo.update_analysis(decision_id, status="failed", llm_analysis=error_details)


# Singleton
_orchestrator_instance = None

def get_orchestrator() -> OrchestratorService:
    global _orchestrator_instance
    if _orchestrator_instance is None:
        _orchestrator_instance = OrchestratorService()
    return _orchestrator_instance
