"""
Enhanced LLM Service with Strict ID Mapping and Verifiable Quotes
"""

from typing import List, Dict
from openai import OpenAI
from server.core.config import config
from server.schemas.decision import DecisionCreate, ReasoningAnalysis

SYSTEM_PROMPT = """You are a multilingual Analytical Critic specializing in decision quality assessment.
**LANGUAGE RULE**: Always respond in the SAME language as the User's input context (e.g., if User writes in Russian, JSON values must be in Russian).

CORE MISSION:
Identify logical fallacies, cognitive biases, key risks, and "Systemic Inconsistencies" with past values.
Do NOT make decisions. Stress-test the user's logic.

CRITICAL INSTRUCTIONS:

1. **SYSTEMIC INCONSISTENCY DETECTION** (PRIORITY #1):
   - Compare "Arguments" (Current) with "Retrieved Context" (Archive).
   - **MANDATORY ALERT**: If a specific Path contradicts values/goals from the Context Archive, you MUST trigger a 'Systemic Inconsistency'.
   - **Direct Comparison**: Use exact quotes. "In Archive you said X, now you argue Y".
   - **No Mercy**: If user previously said "Living in country X is a dead end" and now argues "Remaining in country X offers stability" -> FLAG IT as a Value Conflict.

2. **PATH DIFFERENTIATION**:
   - Treat each Variant as a unique strategy. Do NOT conflate distinct geographic or career paths (e.g., "Kazakhstan" != "Italy").
   - If a path implies abandoning a stated ambition (found in Archive), mark it as "Strategic Regression".

3. **NO HALLUCINATIONS**:
   - Only analyze what is explicitly written.
   - Do NOT invent risks or "social pressure" if not in text.

4. **VERIFIABLE QUOTES**:
   - You MUST cite valid substrings from the user's text.
   - Format: "You stated: '[exact quote]'..."

ANALYTICAL FRAMEWORK:

1. **Quality Assessment**:
   - Logic Stability: Are claims supported by evidence?
   - Data Grounding: Relies on facts vs hope?
   - Historical Consistency: Aligns with past self?

2. **Pattern Recognition**:
   - Is the user repeating a past mistake (from Archive)?
   - Are they rationalizing a fear-based decision?

OUTPUT FORMAT (JSON):
{
  "argument_quality_comparison": {
    "variant_name": {
      "strengths": ["specific strength with quote"],
      "weaknesses": ["specific weakness with quote"],
      "logical_fallacies": [
        {
          "type": "Fallacy Name",
          "quote": "Exact quote",
          "explanation": "Explanation"
        }
      ],
      "missing_considerations": ["what's missing"],
      "data_quality": "SUFFICIENT | INSUFFICIENT_REASONING"
    }
  },
  "cognitive_biases_detected": [
    "bias name: 'quote' — explanation"
  ],
  "alignment_with_model_scores": "Explain agreement/disagreement with ML scores",
  "detected_reasoning_patterns": "Analysis of recurring themes or contradictions with Archive",
  "key_weak_points_to_reconsider": [
    "'Exact quote' — Critical issue"
  ],
  "final_note": "Summary of decision quality (in User's Language)",
  "score_details": {
    "logic_stability": 0.0-1.0,
    "data_grounding": 0.0-1.0,
    "historical_consistency": 0.0-1.0
  },
  "confidence_level": "high | medium | low",
  "systemic_inconsistencies": [
    {
      "past_decision_id": "decision_id_from_context" (if clear),
      "past_statement": "Exact quote from Retrieved Context (Archive)",
      "current_statement": "Exact quote from Current Argument",
      "conflict_description": "⚠️ Value Conflict: You previously stated [X], which directly contradicts your current argument [Y]. This suggests [implication]."
    }
  ]
}

RULES:
- JSON keys must remain English.
- JSON string values MUST be in the User's Language.
- Do not apologize or be polite. Be objective and direct.
"""

class LLMService:
    def __init__(self):
        if not config.OPENAI_API_KEY:
            print("⚠️ OPENAI_API_KEY not set")
        self.client = OpenAI(api_key=config.OPENAI_API_KEY)
        self.model = config.LLM_MODEL

    def analyze_decision(
        self, 
        decision: DecisionCreate, 
        ml_scores: Dict[str, float], 
        retrieved_context: List[str],
        ml_input: List[Dict[str, str]]  # NEW: Strict ID mapping
    ) -> ReasoningAnalysis:
        """
        Analyze decision with strict ID-based argument tracking.
        
        Args:
            decision: Decision data
            ml_scores: ML scores keyed by argument UUID
            retrieved_context: RAG results
            ml_input: List of {id, text, variant_name, type} with UUIDs
        """
        input_text = self._prepare_input_with_ids(decision, ml_scores, retrieved_context, ml_input)
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": input_text}
            ],
            response_format={"type": "json_object"}
        )
        
        return ReasoningAnalysis.parse_raw(response.choices[0].message.content)

    def _prepare_input_with_ids(
        self, 
        decision: DecisionCreate, 
        ml_scores: Dict[str, float], 
        retrieved_context: List[str],
        ml_input: List[Dict[str, str]]
    ) -> str:
        """
        Prepare input with strict ID mapping to prevent logic swap.
        
        Format:
        Arguments:
        {arg_uuid_1}: [Variant A] [PRO] "text..."
        {arg_uuid_2}: [Variant A] [CON] "text..."
        """
        parts = [f"Context: {decision.context}\n"]
        
        # Group arguments by variant for clarity
        variant_args = {}
        for arg_data in ml_input:
            variant = arg_data['variant_name']
            if variant not in variant_args:
                variant_args[variant] = []
            variant_args[variant].append(arg_data)
        
        parts.append("Arguments (keyed by ID):")
        for variant in decision.variants:
            parts.append(f"\n=== {variant} ===")
            args = variant_args.get(variant, [])
            for arg_data in args:
                arg_id = arg_data['id']
                arg_type = arg_data.get('type', 'essay').upper()
                text = arg_data['text']
                parts.append(f"{arg_id}: [{arg_type}] \"{text}\"")
        
        parts.append("\nML Scores (by argument ID):")
        for arg_id, score in ml_scores.items():
            parts.append(f"  {arg_id}: {score:.1f}/100")
        
        parts.append("\nPast Similar Arguments:")
        if retrieved_context:
            for i, ctx in enumerate(retrieved_context, 1):
                parts.append(f"  {i}. {ctx}")
        else:
            parts.append("  None")
        
        parts.append("\nIMPORTANT: Return analysis keyed by variant name, NOT by argument ID.")
        parts.append("Aggregate insights per variant, citing specific argument IDs when relevant.")
        
        return "\n".join(parts)


# Singleton
_llm_service_instance = None

def get_llm_service() -> LLMService:
    global _llm_service_instance
    if _llm_service_instance is None:
        _llm_service_instance = LLMService()
    return _llm_service_instance
