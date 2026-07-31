"""
Emotion Signal Implementation.

Detects emotional content using pattern matching and emotion classification.
Supports multiple emotion types with intensity scoring.
"""

import re
from typing import List, Dict
from enum import Enum

from attention.core.interfaces import AttentionContext, AttentionResult
from attention.core.types import SignalName
from attention.signals.base import BaseSignal


class EmotionType(str, Enum):
    """Emotion categories."""
    JOY = "joy"
    ANGER = "anger"
    FEAR = "fear"
    SADNESS = "sadness"
    SURPRISE = "surprise"
    DISGUST = "disgust"
    NEUTRAL = "neutral"


class EmotionSignal(BaseSignal):
    """
    Emotion attention signal.
    
    Detects emotional content through:
    1. Pattern matching for emotion keywords
    2. Emotion classification
    3. Intensity scoring
    
    High emotion indicates emotionally charged information worth remembering.
    """
    
    # Emotion patterns
    EMOTION_PATTERNS = {
        EmotionType.JOY: [
            r"\b(happy|excited|joy|delighted|thrilled|elated)\b",
            r"\b(love|enjoy|amazing|wonderful|fantastic)\b",
            r"\b(laugh|smile|cheer|celebrate)\b",
        ],
        EmotionType.ANGER: [
            r"\b(angry|furious|mad|irritated|annoyed)\b",
            r"\b(hate|dislike|frustrated|outraged)\b",
            r"\b(rage|fume|seething)\b",
        ],
        EmotionType.FEAR: [
            r"\b(scared|afraid|frightened|terrified)\b",
            r"\b(worried|anxious|nervous|panicked)\b",
            r"\b(dread|horror|terror)\b",
        ],
        EmotionType.SADNESS: [
            r"\b(sad|unhappy|depressed|miserable)\b",
            r"\b(cry|tears|grief|sorrow)\b",
            r"\b(disappointed|heartbroken|devastated)\b",
        ],
        EmotionType.SURPRISE: [
            r"\b(surprised|shocked|amazed|astonished)\b",
            r"\b(unexpected|sudden|wow)\b",
            r"\b(startled|stunned)\b",
        ],
        EmotionType.DISGUST: [
            r"\b(disgusted|repulsed|revolted)\b",
            r"\b(gross|nasty|awful)\b",
            r"\b(sick|nauseous)\b",
        ],
    }
    
    INTENSITY_PATTERNS = {
        "high": [r"\b(very|extremely|incredibly|absolutely|totally)\b"],
        "medium": [r"\b(quite|rather|somewhat|pretty)\b"],
        "low": [r"\b(slightly|a little|kind of)\b"],
    }
    
    def __init__(
        self,
        weight: float = 0.07,
        enabled: bool = True,
        enable_intensity_detection: bool = True,
    ):
        """
        Initialize the emotion signal.
        
        Args:
            weight: Signal weight in aggregation (default: 0.07)
            enabled: Whether signal is enabled
            enable_intensity_detection: Whether to detect emotion intensity
        """
        super().__init__(weight, enabled)
        self.enable_intensity_detection = enable_intensity_detection
    
    @property
    def signal_name(self) -> str:
        """Return the signal name."""
        return SignalName.EMOTION.value
    
    async def _compute_score(self, context: AttentionContext) -> float:
        """
        Compute emotion score.
        
        Emotion is computed by:
        1. Pattern matching for emotion keywords
        2. Emotion classification
        3. Intensity scoring
        
        Args:
            context: The attention context
            
        Returns:
            Emotion score between 0.0 and 1.0
        """
        text = context.input_text.lower()
        
        # Detect emotions
        emotion_scores = self._detect_emotions(text)
        
        # Get the highest emotion score
        max_emotion_score = max(emotion_scores.values()) if emotion_scores else 0.0
        
        # Intensity detection if enabled
        intensity_multiplier = 1.0
        if self.enable_intensity_detection:
            intensity_multiplier = self._detect_intensity(text)
        
        # Combine emotion and intensity
        final_score = max_emotion_score * intensity_multiplier
        
        return self._clamp_score(final_score)
    
    def _detect_emotions(self, text: str) -> Dict[EmotionType, float]:
        """
        Detect emotions in text.
        
        Args:
            text: Input text
            
        Returns:
            Dictionary mapping emotion types to scores
        """
        emotion_scores = {}
        
        for emotion_type, patterns in self.EMOTION_PATTERNS.items():
            matches = 0
            for pattern in patterns:
                matches += super()._count_pattern_matches(text, pattern)
            # Normalize score based on number of patterns
            score = self._normalize_score(matches, 0, len(patterns))
            emotion_scores[emotion_type] = score
        
        return emotion_scores
    
    def _detect_intensity(self, text: str) -> float:
        """
        Detect emotion intensity.
        
        Args:
            text: Input text
            
        Returns:
            Intensity multiplier (1.0 - 1.5)
        """
        high_intensity = self._count_pattern_matches(text, self.INTENSITY_PATTERNS["high"])
        medium_intensity = self._count_pattern_matches(text, self.INTENSITY_PATTERNS["medium"])
        low_intensity = self._count_pattern_matches(text, self.INTENSITY_PATTERNS["low"])
        
        if high_intensity > 0:
            return 1.5
        elif medium_intensity > 0:
            return 1.25
        elif low_intensity > 0:
            return 1.1
        else:
            return 1.0
    
    def _generate_explanation(self, score: float, context: AttentionContext) -> str:
        """Generate explanation for the emotion score."""
        text = context.input_text.lower()
        
        emotion_scores = self._detect_emotions(text)
        dominant_emotion = max(emotion_scores.items(), key=lambda x: x[1])[0] if emotion_scores else EmotionType.NEUTRAL
        
        if score >= 0.8:
            return f"Input has high emotional content (score: {score:.2f}), strong {dominant_emotion.value} detected."
        elif score >= 0.5:
            return f"Input has moderate emotional content (score: {score:.2f}), {dominant_emotion.value} detected."
        elif score >= 0.3:
            return f"Input has low emotional content (score: {score:.2f}), mild emotion detected."
        else:
            return f"Input has no emotional content (score: {score:.2f}), neutral tone."
    
    def _build_metadata(self, score: float, context: AttentionContext) -> dict:
        """Build metadata with emotion-specific information."""
        metadata = super()._build_metadata(score, context)
        text = context.input_text.lower()
        
        emotion_scores = self._detect_emotions(text)
        dominant_emotion = max(emotion_scores.items(), key=lambda x: x[1])[0] if emotion_scores else EmotionType.NEUTRAL
        
        metadata.update({
            "dominant_emotion": dominant_emotion.value,
            "emotion_scores": {k.value: v for k, v in emotion_scores.items()},
            "enable_intensity_detection": self.enable_intensity_detection,
        })
        return metadata
