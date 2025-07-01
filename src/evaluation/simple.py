"""Simple yes/no evaluation for baseline testing."""

import re
from ..core.results import TestResult, EvaluationResult, ConfidenceLevel


class SimpleYesNoEvaluator:
    """Simple evaluator that just checks for Yes/No responses."""
    
    def __init__(self):
        pass
    
    def evaluate_result(self, result: TestResult) -> EvaluationResult:
        """Evaluate a test result by checking for Yes/No response."""
        
        response_text = result.response_text.strip()
        
        # Look for Yes or No at the beginning of the response
        if re.match(r'^Yes\b', response_text, re.IGNORECASE):
            score = 1
            reasoning = "Response starts with 'Yes'"
            confidence = ConfidenceLevel.HIGH
        elif re.match(r'^No\b', response_text, re.IGNORECASE):
            score = 0
            reasoning = "Response starts with 'No'"
            confidence = ConfidenceLevel.HIGH
        else:
            # Fallback: look for Yes/No anywhere in first sentence
            first_sentence = response_text.split('.')[0] if '.' in response_text else response_text
            yes_count = len(re.findall(r'\byes\b', first_sentence, re.IGNORECASE))
            no_count = len(re.findall(r'\bno\b', first_sentence, re.IGNORECASE))
            
            if yes_count > no_count:
                score = 1
                reasoning = f"Found {yes_count} 'yes' vs {no_count} 'no' in first sentence"
                confidence = ConfidenceLevel.MEDIUM
            elif no_count > yes_count:
                score = 0
                reasoning = f"Found {no_count} 'no' vs {yes_count} 'yes' in first sentence"
                confidence = ConfidenceLevel.MEDIUM
            else:
                score = 0
                reasoning = "Could not clearly identify Yes/No response"
                confidence = ConfidenceLevel.LOW
        
        return EvaluationResult(
            automated_score=score,
            automated_confidence=confidence,
            automated_reasoning=reasoning
        )