"""
Risk Signal Implementation.

Detects potential threats, negative outcomes, and risk factors
using pattern matching and sentiment analysis.
"""

import re
from typing import List

from attention.core.interfaces import AttentionContext, AttentionResult
from attention.core.types import SignalName
from attention.signals.base import BaseSignal


class RiskSignal(BaseSignal):
    """
    Risk attention signal.
    
    Detects potential threats and negative outcomes through:
    1. Pattern matching for risk indicators
    2. Sentiment analysis for negative sentiment
    3. Threat detection
    
    High risk indicates information that requires careful attention.
    """
    
    # Risk patterns
    RISK_PATTERNS = [
        r"\b(danger|dangerous|risk|threat|warning|caution)\b",
        r"\b(fail|failure|failed|crash|broke|broken|error|bug)\b",
        r"\b(problem|issue|trouble|difficulty|challenge)\b",
        r"\b(lose|loss|lost|damage|harm|hurt)\b",
        r"\b(security|vulnerability|exploit|attack)\b",
        r"\b(critical|urgent|emergency|crisis)\b",
        r"\b(severe|serious|grave|major)\b",
    ]
    
    NEGATIVE_SENTIMENT_PATTERNS = [
        r"\b(angry|frustrated|worried|scared|afraid|anxious)\b",
        r"\b(sad|disappointed|upset|unhappy|depressed)\b",
        r"\b(hate|dislike|annoyed|irritated)\b",
        r"\b(concerned|troubled|disturbed)\b",
    ]
    
    def __init__(
        self,
        weight: float = 0.10,
        enabled: bool = True,
        enable_sentiment_analysis: bool = True,
    ):
        """
        Initialize the risk signal.
        
        Args:
            weight: Signal weight in aggregation (default: 0.10)
            enabled: Whether signal is enabled
            enable_sentiment_analysis: Whether to perform sentiment analysis
        """
        super().__init__(weight, enabled)
        self.enable_sentiment_analysis = enable_sentiment_analysis
    
    @property
    def signal_name(self) -> str:
        """Return the signal name."""
        return SignalName.RISK.value
    
    async def _compute_score(self, context: AttentionContext) -> float:
        """
        Compute risk score.
        
        Risk is computed by:
        1. Pattern matching for risk indicators
        2. Sentiment analysis for negative sentiment
        3. Threat detection
        
        Args:
            context: The attention context
            
        Returns:
            Risk score between 0.0 and 1.0
        """
        text = context.input_text.lower()
        
        # Pattern matching for risk indicators
        risk_matches = 0
        for pattern in self.RISK_PATTERNS:
            risk_matches += super()._count_pattern_matches(text, pattern)
        pattern_score = self._normalize_score(risk_matches, 0, 3)
        
        # Sentiment analysis if enabled
        sentiment_score = 0.0
        if self.enable_sentiment_analysis:
            sentiment_score = self._compute_sentiment_score(text)
        
        # Threat detection from metadata
        threat_score = self._compute_threat_score(context)
        
        # Combine scores
        final_score = (
            (pattern_score * 0.5) +
            (sentiment_score * 0.3) +
            (threat_score * 0.2)
        )
        
        return self._clamp_score(final_score)
    
    def _compute_sentiment_score(self, text: str) -> float:
        """
        Compute sentiment score using pattern matching.
        
        Args:
            text: Input text
            
        Returns:
            Sentiment score between 0.0 and 1.0
        """
        negative_matches = self._count_pattern_matches(text, self.NEGATIVE_SENTIMENT_PATTERNS)
        return self._normalize_score(negative_matches, 0, 2)
    
    def _compute_threat_score(self, context: AttentionContext) -> float:
        """
        Compute threat score from context metadata.
        
        Args:
            context: Attention context
            
        Returns:
            Threat score between 0.0 and 1.0
        """
        # Check for threat markers in metadata
        is_threat = context.metadata.get("is_threat", False)
        threat_level = context.metadata.get("threat_level")
        
        if is_threat:
            if threat_level == "critical":
                return 1.0
            elif threat_level == "high":
                return 0.8
            elif threat_level == "medium":
                return 0.6
            elif threat_level == "low":
                return 0.4
            else:
                return 0.5
        
        return 0.0
    
    def _generate_explanation(self, score: float, context: AttentionContext) -> str:
        """Generate explanation for the risk score."""
        text = context.input_text.lower()
        
        if score >= 0.8:
            return f"Input indicates high risk (score: {score:.2f}), contains threat or danger indicators."
        elif score >= 0.5:
            return f"Input indicates moderate risk (score: {score:.2f}), some risk factors detected."
        elif score >= 0.3:
            return f"Input indicates low risk (score: {score:.2f}), minimal risk indicators."
        else:
            return f"Input indicates no risk (score: {score:.2f}), no threat or danger indicators."
    
    def _build_metadata(self, score: float, context: AttentionContext) -> dict:
        """Build metadata with risk-specific information."""
        metadata = super()._build_metadata(score, context)
        text = context.input_text.lower()
        
        metadata.update({
            "risk_matches": self._count_pattern_matches(text, self.RISK_PATTERNS),
            "negative_sentiment_matches": self._count_pattern_matches(text, self.NEGATIVE_SENTIMENT_PATTERNS),
            "is_threat": context.metadata.get("is_threat", False),
            "threat_level": context.metadata.get("threat_level"),
            "enable_sentiment_analysis": self.enable_sentiment_analysis,
        })
        return metadata
