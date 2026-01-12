from sqlalchemy import Column, String, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
from .database import Base

class DecisionModel(Base):
    __tablename__ = "decisions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)  # Owner of this decision
    context = Column(Text, nullable=False)
    selected_variant = Column(String, nullable=True) # Can be pending, then updated with actual choice
    timestamp = Column(DateTime, default=datetime.utcnow)
    outcome = Column(Text, nullable=True) # Actual result + reasoning added later
    
    
    # Analysis results
    analysis_status = Column(String, default="pending") # pending, analyzing, completed, failed
    ml_scores = Column(JSON, nullable=True)
    llm_analysis = Column(JSON, nullable=True)
    retrieved_context = Column(JSON, nullable=True)

    # Relationships
    variants = relationship("VariantModel", back_populates="decision", cascade="all, delete-orphan")
    arguments = relationship("ArgumentModel", back_populates="decision", cascade="all, delete-orphan")

class VariantModel(Base):
    __tablename__ = "decision_variants"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    decision_id = Column(UUID(as_uuid=True), ForeignKey("decisions.id"))
    name = Column(String, nullable=False)

    decision = relationship("DecisionModel", back_populates="variants")

class ArgumentModel(Base):
    __tablename__ = "decision_arguments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    decision_id = Column(UUID(as_uuid=True), ForeignKey("decisions.id"))
    variant_name = Column(String, nullable=False) # Denormalized for easier access
    text = Column(Text, nullable=False)
    type = Column(String, nullable=False) # "pro" or "con"

    decision = relationship("DecisionModel", back_populates="arguments")
