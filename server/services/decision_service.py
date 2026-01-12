from sqlalchemy.orm import Session
from uuid import UUID
from typing import List, Optional

from server.repositories.decision_repository import DecisionRepository
from server.schemas.decision import DecisionCreate, DecisionUpdateOutcome, DecisionResponse

class DecisionService:
    def __init__(self, repository: DecisionRepository):
        self.repository = repository

    def create_new_decision(self, decision_data: DecisionCreate, user_id: UUID) -> DecisionResponse:
        """Create new decision for user."""
        # Future: Trigger Async ML Job here
        return self.repository.create(decision_data, user_id)

    def get_history(self, skip: int = 0, limit: int = 100, user_id: UUID = None) -> List[DecisionResponse]:
        """Get decision history, optionally filtered by user_id."""
        return self.repository.get_all(skip, limit, user_id)

    def get_decision_details(self, decision_id: UUID, user_id: UUID = None) -> Optional[DecisionResponse]:
        """Get decision details, optionally checking ownership."""
        decision = self.repository.get_by_id(decision_id)
        if decision and user_id and decision.user_id != user_id:
            return None  # Access denied
        return decision

    def record_outcome(self, decision_id: UUID, outcome_data: DecisionUpdateOutcome, user_id: UUID = None) -> Optional[DecisionResponse]:
        """Record outcome, optionally checking ownership."""
        decision = self.repository.get_by_id(decision_id)
        if decision and user_id and decision.user_id != user_id:
            return None  # Access denied
        return self.repository.update_outcome(decision_id, outcome_data)

# Dependency Injection Helper
def get_decision_service(db: Session) -> DecisionService:
    repo = DecisionRepository(db)
    return DecisionService(repo)
