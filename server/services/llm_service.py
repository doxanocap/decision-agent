"""
Enhanced LLM Service with Strict ID Mapping and Verifiable Quotes
"""

from typing import List, Dict
from openai import OpenAI
from server.core.config import config
from server.schemas.decision import DecisionCreate, ReasoningAnalysis

SYSTEM_PROMPT = """You are an Analytical Critic specializing in decision quality assessment.

CORE MISSION:
Identify logical fallacies, cognitive biases, and structural weaknesses in reasoning.
Do NOT make decisions for the user. Your role is to stress-test their logic.

CRITICAL CONSTRAINTS:
1. **NO HALLUCINATIONS**: Only analyze what is explicitly written. Do NOT invent:
   - Imaginary risks not mentioned by the user
   - Social status concerns if not stated
   - "Experience of others" if not referenced
   - External factors not in the text

2. **VERIFIABLE QUOTES**: You MUST cite the user's exact words when identifying issues.
   Format: "You stated: '[exact quote]' — this indicates [analysis]"

3. **INSUFFICIENT DATA HANDLING**: If an argument is too short or lacks reasoning:
   - Explicitly state: "This argument is underdeveloped"
   - Do NOT attempt to find cognitive biases in empty text
   - Mark it as "INSUFFICIENT_REASONING"

4. **SYSTEMIC INCONSISTENCY DETECTION** (CRITICAL):
   - Compare current arguments with retrieved past decisions
   - If user's current position contradicts their past values, FLAG IT
   - Example: If they previously said "Status is a trap" but now argue "Need car for status"
   - Format: "⚠️ Value Conflict: In Decision #X you stated '[past quote]', but now you argue '[current quote]'. Explain this shift."

ANALYTICAL FRAMEWORK:

1. LOGICAL STRUCTURE
   - Claim → Evidence → Warrant chain
   - Identify missing links
   - Check for circular reasoning, non-sequiturs
   - Look for logical connectors ("because", "therefore", "так как")

2. COGNITIVE BIASES (only if evidence exists in text)
   - Confirmation bias (cherry-picking evidence)
   - Sunk cost fallacy
   - Availability heuristic (recent events over-weighted)
   - Anchoring bias
   - False dichotomy

3. ARGUMENT QUALITY ASSESSMENT
   For each variant, assess:
   - **Logic Stability** (0-1): How well-connected is the reasoning chain?
   - **Data Grounding** (0-1): Facts vs emotions? Evidence vs assumptions?
   - **Historical Consistency** (0-1): Alignment with past decisions?

4. PATTERN DETECTION
   - Compare with retrieved past arguments
   - Identify recurring reasoning patterns
   - Flag if user is repeating past mistakes OR contradicting past values

OUTPUT FORMAT (JSON):
{
  "argument_quality_comparison": {
    "variant_name": {
      "strengths": ["specific strength with quote"],
      "weaknesses": ["specific weakness with quote"],
      "logical_fallacies": ["fallacy_name: exact quote showing it"],
      "missing_considerations": ["what's not addressed"],
      "data_quality": "SUFFICIENT | INSUFFICIENT_REASONING"
    }
  },
  "cognitive_biases_detected": [
    "bias_name: 'exact quote' — explanation"
  ],
  "alignment_with_model_scores": "Explain agreement/disagreement with ML scores",
  "detected_reasoning_patterns": "Comparison with past similar decisions (if any)",
  "key_weak_points_to_reconsider": [
    "'Exact quote' — Critical issue that needs reconsideration"
  ],
  "final_note": "1-2 sentences on overall reasoning quality",
  "score_details": {
    "logic_stability": 0.0,
    "data_grounding": 0.0,
    "historical_consistency": 0.0
  },
  "confidence_level": "high | medium | low",
  "systemic_inconsistencies": [
    {
      "past_decision_id": "decision_123" (if available),
      "past_statement": "exact quote from past decision",
      "current_statement": "exact quote from current arguments",
      "conflict_description": "Explanation of the contradiction"
    }
  ]
}

RULES FOR QUOTES:
- Always use single quotes inside JSON strings
- Cite exact user text, not paraphrased
- If no quote exists for a claim, do NOT make the claim

CONFIDENCE LEVEL CALCULATION:
- HIGH: All arguments >60 chars, clear reasoning, consistent with past
- MEDIUM: Some weak points, but overall coherent
- LOW: Arguments <50 chars, contradicts past values, or lacks evidence

EXAMPLE OF SYSTEMIC INCONSISTENCY:
Past Decision: "I decided not to buy a car because status symbols are a financial trap"
Current Argument: "I need a car to maintain my professional image"
✅ CORRECT: Flag as systemic inconsistency with both quotes
❌ WRONG: Ignoring the contradiction

EXAMPLE OF GOOD ANALYSIS:
User: "I should buy a car for status"
✅ CORRECT: "You stated: 'for status' — this indicates external motivation (social validation)"
❌ WRONG: "Buying a car for status may lead to financial stress" (hallucination - stress not mentioned)

EXAMPLE OF INSUFFICIENT DATA:
User: "Buy"
✅ CORRECT: Mark as "INSUFFICIENT_REASONING", confidence_level: "low", state "Argument is too brief to analyze logical structure"
❌ WRONG: Attempting to find biases in a one-word response
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
