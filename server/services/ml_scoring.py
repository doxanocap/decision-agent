"""
ML Scoring Service - Pairwise argument comparison using Cross-Encoder.
Returns relative strength scores (0-100) based on raw score normalization.
"""

from typing import Dict, List, Tuple
from sentence_transformers import CrossEncoder
import os
import itertools
import random
import math
import logging
from server.core.config import config

logger = logging.getLogger(__name__)


class MLScoring:
    MAX_ARGS_FULL = 6  # Full pairwise comparison limit
    MAX_PAIRS_SAMPLE = 20  # Random sampling if exceeded
    
    def __init__(self):
        print("Loading ML Scoring Model (Cross-Encoder)...")
        
        model_name = getattr(config, 'CROSS_ENCODER_MODEL', 'cross-encoder/ms-marco-MiniLM-L-12-v2')
        
        # Resolve relative paths from project root
        if model_name.startswith("./"):
            import pathlib
            # Use current working directory as project root
            # This works when running from project root with: python -m uvicorn server.main:app
            project_root = pathlib.Path.cwd()
            model_path = project_root / model_name.lstrip("./")
            
            if model_path.exists():
                model_name = str(model_path)
                print(f"✅ Using local model: {model_name}")
            else:
                print(f"⚠️ Local model not found at {model_path}.")
                print(f"   Searched in: {project_root}")
                print(f"   Falling back to HuggingFace: cross-encoder/ms-marco-MiniLM-L-12-v2")
                model_name = 'cross-encoder/ms-marco-MiniLM-L-12-v2'
        
        self.model = CrossEncoder(model_name, max_length=512)
        print(f"ML Scoring initialized with {model_name}")
    
    def _format_with_context(self, argument: str, context: str) -> str:
        return f"Context: {context}\nArgument: {argument}"
    
    def compare_arguments(self, arg_a: str, arg_b: str, context: str) -> Tuple[float, int]:
        """Compare two arguments in context. Returns (raw_score, winner)."""
        text_a = self._format_with_context(arg_a, context)
        text_b = self._format_with_context(arg_b, context)
        
        raw_score = self.model.predict([[text_a, text_b]])[0]
        winner = 1 if raw_score > 0 else 0
        
        return raw_score, winner
    
    def score_arguments(self, arguments: List[Dict[str, str]], context: str) -> Dict[str, float]:
        """
        Score arguments via pairwise comparison + absolute quality assessment.
        Formula: Final Score = (Comparative Score + Absolute Quality Score) / 2
        
        This prevents 100/0 scores for weak arguments that happen to be
        slightly better than each other.
        
        Args:
            arguments: [{id, text}, ...]
            context: decision context
            
        Returns:
            {argument_id: combined_score (0-100)}
        """
        if not arguments:
            return {}
        
        if len(arguments) == 1:
            # For single argument, use only absolute quality
            from server.services.argument_validator import ArgumentQualityValidator
            quality = ArgumentQualityValidator.assess_argument_quality(arguments[0]['text'])
            return {arguments[0]['id']: quality * 100}
        
        # 1. Comparative Scoring (pairwise comparison)
        scores_sum = {arg['id']: 0.0 for arg in arguments}
        comparison_count = {arg['id']: 0 for arg in arguments}
        
        # Generate pairs
        n = len(arguments)
        if n <= self.MAX_ARGS_FULL:
            pairs = list(itertools.combinations(range(n), 2))
        else:
            all_pairs = list(itertools.combinations(range(n), 2))
            pairs = random.sample(all_pairs, min(len(all_pairs), self.MAX_PAIRS_SAMPLE))
            print(f"⚠️ Sampling {len(pairs)} pairs from {n} arguments")
        
        # Pairwise comparisons
        for i, j in pairs:
            arg_a, arg_b = arguments[i], arguments[j]
            raw_score, _ = self.compare_arguments(arg_a['text'], arg_b['text'], context)
            
            # Normalize: tanh(x/5) maps [-5,+5] to [-1,+1]
            normalized = math.tanh(raw_score / 5.0)
            
            # Convert to [0,1] for each argument
            score_a = (normalized + 1) / 2
            score_b = 1 - score_a
            
            scores_sum[arg_a['id']] += score_a
            scores_sum[arg_b['id']] += score_b
            comparison_count[arg_a['id']] += 1
            comparison_count[arg_b['id']] += 1
        
        # Average comparative scores
        comparative_scores = {
            arg_id: scores_sum[arg_id] / comparison_count[arg_id] if comparison_count[arg_id] > 0 else 0.5
            for arg_id in scores_sum
        }
        
        # Normalize comparative scores to 0-100
        min_score = min(comparative_scores.values())
        max_score = max(comparative_scores.values())
        
        if max_score > min_score:
            comparative_scores_normalized = {
                arg_id: ((score - min_score) / (max_score - min_score)) * 100
                for arg_id, score in comparative_scores.items()
            }
        else:
            comparative_scores_normalized = {arg_id: 50.0 for arg_id in comparative_scores}
        
        # 2. Absolute Quality Scoring
        from server.services.argument_validator import ArgumentQualityValidator
        
        absolute_scores = {}
        for arg in arguments:
            quality = ArgumentQualityValidator.assess_argument_quality(arg['text'])
            absolute_scores[arg['id']] = quality * 100  # Convert to 0-100
        
        # 3. Zero-Shot Calibration (compare against dummy baseline)
        # If user's argument is weaker than "I just want it, no reason", force score down
        DUMMY_BASELINE = "I just want it, no reason"
        baseline_quality = ArgumentQualityValidator.assess_argument_quality(DUMMY_BASELINE)
        baseline_score = baseline_quality * 100  # Should be ~10-15
        
        # Calibrate absolute scores
        calibrated_absolute_scores = {}
        for arg_id, score in absolute_scores.items():
            if score < baseline_score:
                # Argument is weaker than baseline - force to 0-10 range
                calibrated_score = min(score, 10.0)
                logger.warning(f"Argument {arg_id[:8]}... scored below baseline ({score:.1f} < {baseline_score:.1f}), calibrated to {calibrated_score:.1f}")
            else:
                calibrated_score = score
            calibrated_absolute_scores[arg_id] = calibrated_score
        
        # 4. Combine scores (50% comparative + 50% calibrated absolute)
        final_scores = {}
        for arg_id in comparative_scores_normalized:
            comparative = comparative_scores_normalized[arg_id]
            absolute = calibrated_absolute_scores[arg_id]
            final_scores[arg_id] = (comparative + absolute) / 2
        
        return final_scores
    
    def score_arguments_by_variant(self, arguments: List[Dict[str, str]], context: str) -> Dict[str, float]:
        """Aggregate scores by variant name."""
        scores = self.score_arguments(arguments, context)
        
        variant_scores = {}
        variant_counts = {}
        
        for arg in arguments:
            variant = arg['variant_name']
            score = scores.get(arg['id'], 50.0)
            
            if variant not in variant_scores:
                variant_scores[variant] = 0.0
                variant_counts[variant] = 0
            
            variant_scores[variant] += score
            variant_counts[variant] += 1
        
        return {
            variant: variant_scores[variant] / variant_counts[variant]
            for variant in variant_scores
        }


# Singleton
_ml_scoring_instance = None

def get_ml_scoring() -> MLScoring:
    global _ml_scoring_instance
    if _ml_scoring_instance is None:
        _ml_scoring_instance = MLScoring()
    return _ml_scoring_instance
