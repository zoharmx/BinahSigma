"""
Quality Validator for Binah-Σ Analysis Outputs

Prevents "well-structured garbage" by enforcing minimum quality standards
on LLM-generated content.
"""

from typing import List
from schemas import BinahSigmaResponse


class QualityValidator:
    """Validates that LLM outputs meet minimum quality standards"""

    # Generic phrases that indicate lazy/vague analysis
    FORBIDDEN_GENERIC_PHRASES = [
        "it depends",
        "consider all options",
        "evaluate carefully",
        "there are pros and cons",
        "further analysis needed",
        "consult with experts",
        "more research required",
        "case by case basis",
        "depends on the situation",
        "various factors to consider"
    ]

    # Minimum content requirements
    MIN_TENSIONS = 3
    MIN_CONSEQUENCES = 4
    MIN_RECOMMENDATION_LENGTH = 50
    MIN_EXPLANATION_LENGTH = 100

    # Placeholder content to reject
    PLACEHOLDER_VALUES = ["n/a", "none", "tbd", "todo", "placeholder", "unknown"]

    @classmethod
    def validate(cls, response: BinahSigmaResponse) -> None:
        """
        Validates response quality. Raises ValueError if quality is insufficient.

        Args:
            response: BinahSigmaResponse to validate

        Raises:
            ValueError: If quality standards are not met
        """
        errors = []

        # 1. Check for generic recommendations
        rec_lower = response.binah_recommendation.lower()
        for phrase in cls.FORBIDDEN_GENERIC_PHRASES:
            if phrase in rec_lower:
                errors.append(f"Generic phrase detected in recommendation: '{phrase}'")

        # 2. Check minimum depth of analysis
        if len(response.key_tensions) < cls.MIN_TENSIONS:
            errors.append(
                f"Insufficient tensions: {len(response.key_tensions)} < {cls.MIN_TENSIONS}"
            )

        if len(response.unintended_consequences) < cls.MIN_CONSEQUENCES:
            errors.append(
                f"Insufficient consequences: {len(response.unintended_consequences)} < {cls.MIN_CONSEQUENCES}"
            )

        # 3. Check recommendation quality
        if len(response.binah_recommendation) < cls.MIN_RECOMMENDATION_LENGTH:
            errors.append(
                f"Recommendation too short: {len(response.binah_recommendation)} chars < {cls.MIN_RECOMMENDATION_LENGTH}"
            )

        # 4. Check explanation quality
        if len(response.explanation_summary) < cls.MIN_EXPLANATION_LENGTH:
            errors.append(
                f"Explanation too short: {len(response.explanation_summary)} chars < {cls.MIN_EXPLANATION_LENGTH}"
            )

        # 5. Check for empty/placeholder content in arrays
        all_items = response.key_tensions + response.unintended_consequences
        for item in all_items:
            item_lower = item.lower().strip()
            if item_lower in cls.PLACEHOLDER_VALUES or item_lower == "":
                errors.append(f"Placeholder/empty content detected: '{item}'")

        # 6. Check for duplicate items (indicates lazy generation)
        if len(response.key_tensions) != len(set(response.key_tensions)):
            errors.append("Duplicate tensions detected")

        if len(response.unintended_consequences) != len(set(response.unintended_consequences)):
            errors.append("Duplicate consequences detected")

        # 7. Check that items are substantive (not too short)
        MIN_ITEM_LENGTH = 10
        for tension in response.key_tensions:
            if len(tension) < MIN_ITEM_LENGTH:
                errors.append(f"Tension too short: '{tension}'")

        for consequence in response.unintended_consequences:
            if len(consequence) < MIN_ITEM_LENGTH:
                errors.append(f"Consequence too short: '{consequence}'")

        # 8. Validate index and confidence are in valid ranges
        if not 0.0 <= response.binah_sigma_index <= 1.0:
            errors.append(f"Invalid index value: {response.binah_sigma_index}")

        if not 0.0 <= response.binah_sigma_confidence <= 1.0:
            errors.append(f"Invalid confidence value: {response.binah_sigma_confidence}")

        # If any errors, raise with detailed message
        if errors:
            raise ValueError(
                f"Quality validation failed ({len(errors)} issues): " + "; ".join(errors)
            )

    @classmethod
    def get_quality_score(cls, response: BinahSigmaResponse) -> float:
        """
        Calculate a quality score (0-100) for the response.

        Returns:
            float: Quality score, where 100 is perfect
        """
        score = 100.0

        # Deduct points for issues
        rec_lower = response.binah_recommendation.lower()
        for phrase in cls.FORBIDDEN_GENERIC_PHRASES:
            if phrase in rec_lower:
                score -= 10

        if len(response.key_tensions) < cls.MIN_TENSIONS:
            score -= 15

        if len(response.unintended_consequences) < cls.MIN_CONSEQUENCES:
            score -= 15

        if len(response.binah_recommendation) < cls.MIN_RECOMMENDATION_LENGTH:
            score -= 10

        if len(response.explanation_summary) < cls.MIN_EXPLANATION_LENGTH:
            score -= 10

        # Bonus for exceeding minimums
        if len(response.key_tensions) >= 5:
            score += 5

        if len(response.unintended_consequences) >= 7:
            score += 5

        return max(0.0, min(100.0, score))
