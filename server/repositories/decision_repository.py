from sqlalchemy.orm import Session
from uuid import UUID
from typing import List, Optional

from server.db.models import DecisionModel, VariantModel, ArgumentModel
from server.schemas.decision import DecisionCreate, DecisionUpdateOutcome

class DecisionRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, decision: DecisionCreate, user_id: UUID) -> DecisionModel:
        """Create decision for user."""
        # 1. Create Decision Root
        db_decision = DecisionModel(
            user_id=user_id,
            context=decision.context,
            selected_variant=decision.selected_variant
        )
        self.db.add(db_decision)
        self.db.flush() # Generate ID

        # 2. Create Variants
        for v_name in decision.variants:
            db_variant = VariantModel(decision_id=db_decision.id, name=v_name)
            self.db.add(db_variant)

        # 3. Create Arguments
        for arg in decision.arguments:
            db_arg = ArgumentModel(
                decision_id=db_decision.id,
                variant_name=arg.variant_name,
                text=arg.text,
                type=arg.type
            )
            self.db.add(db_arg)
        
        self.db.commit()
        self.db.refresh(db_decision)
        return db_decision

    def get_all(self, skip: int = 0, limit: int = 100, user_id: UUID = None) -> List[DecisionModel]:
        """Get all decisions, optionally filtered by user_id."""
        query = self.db.query(DecisionModel)
        if user_id:
            query = query.filter(DecisionModel.user_id == user_id)
        return query.order_by(DecisionModel.timestamp.desc())\
            .offset(skip)\
            .limit(limit)\
            .all()

    def get_by_id(self, decision_id: UUID) -> Optional[DecisionModel]:
        return self.db.query(DecisionModel).filter(DecisionModel.id == decision_id).first()

    def update_outcome(self, decision_id: UUID, outcome_data: DecisionUpdateOutcome) -> Optional[DecisionModel]:
        db_decision = self.get_by_id(decision_id)
        if db_decision:
            db_decision.outcome = outcome_data.outcome
            if outcome_data.selected_variant:
                db_decision.selected_variant = outcome_data.selected_variant
            self.db.commit()
            self.db.refresh(db_decision)
        return db_decision
    def update_analysis(
        self, 
        decision_id: UUID, 
        status: str,
        ml_scores: Optional[dict] = None,
        llm_analysis: Optional[dict] = None,
        retrieved_context: Optional[list] = None
    ) -> Optional[DecisionModel]:
        db_decision = self.get_by_id(decision_id)
        if db_decision:
            db_decision.analysis_status = status
            if ml_scores is not None:
                db_decision.ml_scores = ml_scores
            if llm_analysis is not None:
                db_decision.llm_analysis = llm_analysis
            if retrieved_context is not None:
                db_decision.retrieved_context = retrieved_context
            
            self.db.commit()
            self.db.refresh(db_decision)
        return db_decision
