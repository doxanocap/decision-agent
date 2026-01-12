"""
Argument Quality Validator - Guardrails for ML Pipeline
Prevents analysis of insufficient or low-quality input.
"""

import re
from typing import List, Dict, Tuple


class ArgumentQualityValidator:
    """Validates argument quality before ML/LLM processing."""
    
    MIN_ARGUMENT_LENGTH = 50  # characters
    MIN_WORD_COUNT = 10
    
    # Reasoning keywords (English and Russian)
    REASONING_KEYWORDS = [
        # English
        'because', 'since', 'therefore', 'thus', 'hence', 'so',
        'as a result', 'consequently', 'due to', 'given that',
        'considering', 'leads to', 'results in', 'causes',
        # Russian
        'потому что', 'так как', 'поэтому', 'следовательно',
        'в результате', 'из-за', 'благодаря', 'ведь'
    ]
    
    @classmethod
    def validate_argument(cls, text: str) -> Tuple[bool, str]:
        """
        Validate single argument quality.
        
        Returns:
            (is_valid, error_message)
        """
        text = text.strip()
        
        # Check minimum length
        if len(text) < cls.MIN_ARGUMENT_LENGTH:
            return False, f"Argument too short ({len(text)} chars, min {cls.MIN_ARGUMENT_LENGTH})"
        
        # Check word count
        word_count = len(text.split())
        if word_count < cls.MIN_WORD_COUNT:
            return False, f"Argument too brief ({word_count} words, min {cls.MIN_WORD_COUNT})"
        
        # Reasoning keywords check removed for MVP - too strict
        # text_lower = text.lower()
        # has_reasoning = any(keyword in text_lower for keyword in cls.REASONING_KEYWORDS)
        # 
        # if not has_reasoning:
        #     return False, "Argument lacks reasoning keywords (e.g., 'because', 'так как')"
        
        return True, ""
    
    @classmethod
    def validate_arguments(cls, arguments: List[Dict[str, str]]) -> Dict[str, any]:
        """
        Validate all arguments for a decision.
        
        Returns:
            {
                'is_valid': bool,
                'invalid_arguments': List[{variant, text, reason}],
                'quality_score': float  # 0-1
            }
        """
        invalid_args = []
        total_args = len(arguments)
        valid_count = 0
        
        for arg in arguments:
            is_valid, error_msg = cls.validate_argument(arg['text'])
            
            if not is_valid:
                invalid_args.append({
                    'variant': arg.get('variant_name', 'unknown'),
                    'text': arg['text'][:50] + '...' if len(arg['text']) > 50 else arg['text'],
                    'reason': error_msg
                })
            else:
                valid_count += 1
        
        quality_score = valid_count / total_args if total_args > 0 else 0
        
        return {
            'is_valid': len(invalid_args) == 0,
            'invalid_arguments': invalid_args,
            'quality_score': quality_score,
            'total_arguments': total_args,
            'valid_arguments': valid_count
        }
    
    @classmethod
    def assess_argument_quality(cls, text: str) -> float:
        """
        Assess individual argument quality (0-1 score).
        Used for absolute quality scoring in ML pipeline.
        
        Factors:
        - Length (longer = better, up to a point)
        - Reasoning keywords presence
        - Sentence structure (multiple sentences = better)
        """
        text = text.strip()
        score = 0.0
        
        # Length score (0-0.3)
        if len(text) >= 200:
            score += 0.3
        elif len(text) >= 100:
            score += 0.2
        elif len(text) >= cls.MIN_ARGUMENT_LENGTH:
            score += 0.1
        
        # Reasoning keywords (0-0.3)
        text_lower = text.lower()
        keyword_count = sum(1 for kw in cls.REASONING_KEYWORDS if kw in text_lower)
        if keyword_count >= 3:
            score += 0.3
        elif keyword_count >= 2:
            score += 0.2
        elif keyword_count >= 1:
            score += 0.1
        
        # Sentence structure (0-0.2)
        sentences = re.split(r'[.!?]+', text)
        sentence_count = len([s for s in sentences if s.strip()])
        if sentence_count >= 3:
            score += 0.2
        elif sentence_count >= 2:
            score += 0.1
        
        # Evidence markers (0-0.2)
        evidence_markers = ['data', 'research', 'study', 'evidence', 'example',
                           'данные', 'исследование', 'пример', 'факт']
        has_evidence = any(marker in text_lower for marker in evidence_markers)
        if has_evidence:
            score += 0.2
        
        
        return min(score, 1.0)  # Cap at 1.0
