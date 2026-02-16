"""
Intent Inference Agent for Natural User Interaction.

Uses LLMs to analyze user input, conversation history, and contextual cues
to determine the underlying user intent, even when requests are vague or implicit.
"""

import logging
import asyncio
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

from src.llm.multi_llm_service import get_multi_llm_service

logger = logging.getLogger(__name__)


@dataclass
class IntentResult:
    """Result from intent inference analysis."""
    inferred_intent: str
    confidence_score: float  # 0.0 to 1.0
    requires_clarification: bool
    clarifying_questions: List[str]
    assumptions_made: List[str]
    context_summary: str
    execution_time: float = 0.0


@dataclass
class ConversationContext:
    """Context for conversation history and user state."""
    user_id: Optional[str] = None
    conversation_history: List[Dict[str, Any]] = None
    user_profile: Optional[Dict[str, Any]] = None
    last_interaction: Optional[datetime] = None

    def __post_init__(self):
        if self.conversation_history is None:
            self.conversation_history = []


class IntentInferenceAgent:
    """
    Agent responsible for inferring user intent from natural language input.

    Capabilities:
    - Analyze user input with conversation history and context
    - Detect ambiguity and generate clarifying questions
    - Make reasonable assumptions when appropriate
    - Route to appropriate workflows based on inferred intent
    """

    def __init__(self):
        self.name = "Intent Inference Agent"
        self.logger = logging.getLogger(self.name)
        self.multi_llm_service = get_multi_llm_service()

        # Intent categories for health diagnostics
        self.intent_categories = [
            "analyze_blood_report",
            "ask_health_question",
            "request_recommendations",
            "follow_up_previous_analysis",
            "clarify_previous_response",
            "general_health_inquiry",
            "emergency_concern",
            "lifestyle_advice"
        ]

    async def analyze_intent(
        self,
        user_input: str,
        conversation_context: Optional[ConversationContext] = None
    ) -> IntentResult:
        """
        Analyze user input to infer intent using LLM.

        Args:
            user_input: The user's natural language input
            conversation_context: Optional context including history and user profile

        Returns:
            IntentResult with inferred intent and analysis details
        """
        import time
        start_time = time.time()

        try:
            self.logger.info(f"Analyzing intent for input: '{user_input[:100]}...'")

            # Prepare context for LLM analysis
            context_summary = self._prepare_context_summary(conversation_context)

            # Generate intent analysis prompt
            prompt = self._build_intent_analysis_prompt(user_input, context_summary)

            # Use LLM for intent inference
            if not self.multi_llm_service.is_any_available():
                self.logger.warning("No LLM available for intent inference, using fallback")
                return self._fallback_intent_analysis(user_input, context_summary)

            # Run LLM analysis in thread to avoid blocking
            analysis_response = await asyncio.to_thread(
                self.multi_llm_service.generate_text,
                prompt,
                max_tokens=1024
            )

            if not analysis_response:
                self.logger.warning("LLM returned empty response, using fallback")
                return self._fallback_intent_analysis(user_input, context_summary)

            # Parse LLM response
            intent_result = self._parse_intent_response(analysis_response, context_summary)

            intent_result.execution_time = time.time() - start_time

            self.logger.info(f"Intent inferred: {intent_result.inferred_intent} "
                           f"(confidence: {intent_result.confidence_score:.2f})")

            return intent_result

        except Exception as e:
            self.logger.error(f"Intent analysis failed: {str(e)}")
            return self._fallback_intent_analysis(user_input, conversation_context or ConversationContext())

    def _prepare_context_summary(self, context: Optional[ConversationContext]) -> str:
        """Prepare a summary of conversation context for LLM analysis."""
        if not context:
            return "No previous conversation context available."

        summary_parts = []

        # User profile info
        if context.user_profile:
            profile_info = []
            if 'age' in context.user_profile:
                profile_info.append(f"Age: {context.user_profile['age']}")
            if 'gender' in context.user_profile:
                profile_info.append(f"Gender: {context.user_profile['gender']}")
            if profile_info:
                summary_parts.append(f"User Profile: {', '.join(profile_info)}")

        # Recent conversation history (last 5 interactions)
        if context.conversation_history:
            recent_history = context.conversation_history[-5:]
            history_summary = []
            for msg in recent_history:
                role = msg.get('role', 'unknown')
                content = msg.get('content', '')[:100]  # Truncate long messages
                history_summary.append(f"{role}: {content}")
            if history_summary:
                summary_parts.append(f"Recent Conversation:\n" + "\n".join(history_summary))

        # Last interaction time
        if context.last_interaction:
            time_diff = datetime.now() - context.last_interaction
            hours_ago = time_diff.total_seconds() / 3600
            summary_parts.append(f"Last interaction: {hours_ago:.1f} hours ago")

        return "\n".join(summary_parts) if summary_parts else "No previous conversation context available."

    def _build_intent_analysis_prompt(self, user_input: str, context_summary: str) -> str:
        """Build the prompt for LLM intent analysis."""
        return f"""
You are an expert intent inference agent for a health diagnostics AI system. Your task is to analyze the user's input and determine their true intent, even if the request is vague, implicit, or incomplete.

CONTEXT INFORMATION:
{context_summary}

USER INPUT: "{user_input}"

INTENT CATEGORIES (choose the most appropriate):
- analyze_blood_report: User wants to analyze/upload blood test results
- ask_health_question: General health-related question
- request_recommendations: Seeking health advice or recommendations
- follow_up_previous_analysis: Referring to previous blood report analysis
- clarify_previous_response: Needs clarification on previous AI response
- general_health_inquiry: Broad health information request
- emergency_concern: Urgent health concern that needs immediate attention
- lifestyle_advice: Questions about diet, exercise, lifestyle changes

ANALYSIS REQUIREMENTS:
1. Infer the most likely intent from the categories above
2. Provide a confidence score (0.0-1.0) for your inference
3. Determine if clarification is needed (yes/no)
4. If clarification needed, list 1-3 specific questions to ask
5. List any reasonable assumptions you're making
6. Provide a brief summary of the context you considered

RESPONSE FORMAT (JSON):
{{
    "inferred_intent": "category_name",
    "confidence_score": 0.85,
    "requires_clarification": false,
    "clarifying_questions": [],
    "assumptions_made": ["Assumption 1", "Assumption 2"],
    "context_summary": "Brief summary of context analysis"
}}

Be thorough but concise. If the intent is unclear, prefer to ask for clarification rather than guessing.
"""

    def _parse_intent_response(self, response: str, context_summary: str) -> IntentResult:
        """Parse the LLM response into an IntentResult."""
        import json

        try:
            # Extract JSON from response (LLM might add extra text)
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                json_str = response[json_start:json_end]
                data = json.loads(json_str)

                return IntentResult(
                    inferred_intent=data.get('inferred_intent', 'general_health_inquiry'),
                    confidence_score=float(data.get('confidence_score', 0.5)),
                    requires_clarification=data.get('requires_clarification', False),
                    clarifying_questions=data.get('clarifying_questions', []),
                    assumptions_made=data.get('assumptions_made', []),
                    context_summary=data.get('context_summary', context_summary)
                )
            else:
                raise ValueError("No JSON found in response")

        except (json.JSONDecodeError, ValueError, KeyError) as e:
            self.logger.warning(f"Failed to parse LLM response: {e}, using fallback")
            return self._fallback_intent_analysis("", ConversationContext())

    def _fallback_intent_analysis(self, user_input: str, context: ConversationContext) -> IntentResult:
        """Fallback intent analysis when LLM is unavailable."""
        # Simple keyword-based fallback
        input_lower = user_input.lower()

        if any(keyword in input_lower for keyword in ['blood', 'test', 'report', 'analysis', 'results']):
            intent = 'analyze_blood_report'
            confidence = 0.8
        elif any(keyword in input_lower for keyword in ['recommend', 'advice', 'suggest', 'what should']):
            intent = 'request_recommendations'
            confidence = 0.7
        elif any(keyword in input_lower for keyword in ['follow', 'previous', 'last', 'before']):
            intent = 'follow_up_previous_analysis'
            confidence = 0.6
        elif any(keyword in input_lower for keyword in ['emergency', 'urgent', 'serious', 'worried']):
            intent = 'emergency_concern'
            confidence = 0.9
        else:
            intent = 'general_health_inquiry'
            confidence = 0.5

        # Check if clarification might be needed
        requires_clarification = confidence < 0.7
        clarifying_questions = []
        if requires_clarification:
            clarifying_questions = [
                "Could you provide more details about your health concern?",
                "Are you referring to a specific blood test or general health question?"
            ]

        return IntentResult(
            inferred_intent=intent,
            confidence_score=confidence,
            requires_clarification=requires_clarification,
            clarifying_questions=clarifying_questions,
            assumptions_made=["Using keyword-based analysis due to LLM unavailability"],
            context_summary="Fallback analysis without LLM"
        )

    def update_conversation_context(
        self,
        context: ConversationContext,
        user_input: str,
        intent_result: IntentResult
    ) -> ConversationContext:
        """Update conversation context with new interaction."""
        # Add to history
        context.conversation_history.append({
            'role': 'user',
            'content': user_input,
            'timestamp': datetime.now().isoformat(),
            'inferred_intent': intent_result.inferred_intent,
            'confidence': intent_result.confidence_score
        })

        # Update last interaction
        context.last_interaction = datetime.now()

        # Keep history manageable (last 20 messages)
        if len(context.conversation_history) > 20:
            context.conversation_history = context.conversation_history[-20:]

        return context
