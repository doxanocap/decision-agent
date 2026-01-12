from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict
from datetime import datetime
from uuid import UUID

class ArgumentBase(BaseModel):
    variant_name: str
    text: str
    type: str  # "pro" or "con"

class ArgumentResponse(ArgumentBase):
    id: UUID
    class Config:
        orm_mode = True

class VariantResponse(BaseModel):
    id: UUID
    name: str
    class Config:
        orm_mode = True

class DecisionCreate(BaseModel):
    context: str = Field(
        ..., 
        min_length=20, 
        max_length=5000,
        description="Decision context (20-5000 characters)"
    )
    variants: List[str] = Field(
        ..., 
        min_items=1, 
        max_items=5,
        description="Decision options (1-5 variants)"
    )
    selected_variant: Optional[str] = None
    arguments: List[ArgumentBase] = Field(
        ..., 
        min_items=1, 
        max_items=20,
        description="Arguments for variants (1-20 total)"
    )
    
    @validator('context')
    def validate_context_quality(cls, v):
        """Ensure context has minimum word count."""
        word_count = len(v.split())
        if word_count < 10:
            raise ValueError("Context must contain at least 10 words for meaningful analysis")
        return v.strip()
    
    @validator('variants')
    def validate_variants(cls, v):
        """Ensure variants are unique and non-empty."""
        if not v:
            raise ValueError("At least one variant is required")
        
        # Remove empty strings and strip whitespace
        cleaned = [var.strip() for var in v if var.strip()]
        
        if len(cleaned) != len(v):
            raise ValueError("Variants cannot be empty")
        
        # Check for duplicates
        if len(cleaned) != len(set(cleaned)):
            raise ValueError("Variant names must be unique")
        
        # Check length
        for var in cleaned:
            if len(var) > 100:
                raise ValueError("Variant name too long (max 100 characters)")
        
        return cleaned
    
    @validator('arguments')
    def validate_arguments(cls, v, values):
        """Ensure arguments are valid and match variants."""
        if not v:
            raise ValueError("At least one argument is required")
        
        # Check that each argument has text
        for arg in v:
            if not arg.text or not arg.text.strip():
                raise ValueError("Arguments cannot be empty")
            
            if len(arg.text) > 2000:
                raise ValueError("Argument text too long (max 2000 characters)")
            
            word_count = len(arg.text.split())
            if word_count < 5:
                raise ValueError("Each argument must contain at least 5 words")
        
        # Check that all arguments reference valid variants
        if 'variants' in values:
            variant_names = set(values['variants'])
            for arg in v:
                if arg.variant_name not in variant_names:
                    raise ValueError(f"Argument references unknown variant: {arg.variant_name}")
        
        return v

class DecisionUpdateOutcome(BaseModel):
    outcome: str
    selected_variant: Optional[str] = None

class DecisionResponse(BaseModel):
    id: UUID
    timestamp: datetime
    context: str
    selected_variant: Optional[str]
    outcome: Optional[str]
    
    variants: List[VariantResponse]
    arguments: List[ArgumentResponse]
    
    class Config:
        orm_mode = True

class ScoreDetails(BaseModel):
    """Detailed scoring breakdown for UI visualization."""
    logic_stability: float = Field(..., ge=0, le=1, description="How logically connected the argument is (0-1)")
    data_grounding: float = Field(..., ge=0, le=1, description="How much it relies on facts vs emotions (0-1)")
    historical_consistency: float = Field(..., ge=0, le=1, description="Alignment with user's past decisions (0-1)")


class SystemicInconsistency(BaseModel):
    """Detected contradiction with past decisions."""
    past_decision_id: Optional[str] = None
    past_statement: str
    current_statement: str
    conflict_description: str


class ReasoningAnalysis(BaseModel):
    argument_quality_comparison: Dict[str, str]
    alignment_with_model_scores: str
    detected_reasoning_patterns: str
    key_weak_points_to_reconsider: List[str]
    final_note: str
    
    # NEW: Confidence metadata for UI
    score_details: Optional[ScoreDetails] = None
    confidence_level: Optional[str] = Field(None, description="Overall confidence: 'high', 'medium', or 'low'")
    
    # NEW: Systemic inconsistency detection (RAG-based)
    systemic_inconsistencies: Optional[List[SystemicInconsistency]] = []


class AnalysisResponse(BaseModel):
    decision_id: UUID
    ml_scores: Dict[str, float]
    retrieved_context: List[str]
    analysis: ReasoningAnalysis
