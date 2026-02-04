"""
Phase 3 Recommendations Package
Provides diet, exercise, and lifestyle recommendation modules.
"""

from .recommender import RecommendationEngine, SafetyValidator, format_recommendations_for_display
from .diet import DietRecommendationModule
from .exercise import ExerciseRecommendationModule
from .lifestyle import LifestyleRecommendationModule

__all__ = [
    'RecommendationEngine',
    'SafetyValidator',
    'format_recommendations_for_display',
    'DietRecommendationModule',
    'ExerciseRecommendationModule',
    'LifestyleRecommendationModule'
]
