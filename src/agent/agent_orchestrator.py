"""
Multi-Agent Orchestrator for Health Diagnostics.

Coordinates multiple AI agents to analyze blood reports:
- Parameter Extraction Agent
- Data Validation Agent
- Interpretation Agent (Model 1)
- Risk Analysis Agent (Model 2)
- Prediction Agent
- LLM Recommendation Agent
- Report Generation Agent
"""

import logging
import asyncio
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime

from src.data_cleaning.data_cleaner import clean_and_structure_data
from src.models.model_1_parameter_interpretation import interpret_parameters
from src.models.model_2_pattern_analysis import analyze_risks
from src.analysis.predictor import predict_risk
from src.llm.multi_llm_service import get_multi_llm_service
from src.recommendation.recommendation_generator import generate_recommendations, generate_prescriptions
from src.synthesis.findings_synthesizer import synthesize_findings
from src.agent.intent_inference_agent import IntentInferenceAgent, ConversationContext, IntentResult

logger = logging.getLogger(__name__)


@dataclass
class AgentResult:
    """Result from an individual agent."""
    agent_name: str
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    execution_time: float = 0.0


@dataclass
class AnalysisReport:
    """Final analysis report from the multi-agent system."""
    status: str
    extracted_parameters: Dict[str, Any]
    interpretations: List[str]
    risks: List[str]
    ai_prediction: Dict[str, Any]
    recommendations: List[str]
    prescriptions: List[str]
    synthesis: str
    agent_results: List[AgentResult]
    timestamp: str
    intent_result: Optional[IntentResult] = None
    conversation_context: Optional[ConversationContext] = None


class ParameterExtractionAgent:
    """Agent responsible for extracting and cleaning medical parameters."""
    
    def __init__(self):
        self.name = "Parameter Extraction Agent"
        self.logger = logging.getLogger(self.name)
    
    def execute(self, raw_params: Dict[str, Any]) -> AgentResult:
        """Extract and clean medical parameters."""
        import time
        start_time = time.time()
        
        try:
            self.logger.info(f"Processing {len(raw_params)} raw parameters")
            cleaned_params = clean_and_structure_data(raw_params)
            
            if not cleaned_params:
                raise ValueError("No valid medical parameters found after cleaning")
            
            execution_time = time.time() - start_time
            self.logger.info(f"Successfully processed {len(cleaned_params)} parameters in {execution_time:.2f}s")
            
            return AgentResult(
                agent_name=self.name,
                success=True,
                data=cleaned_params,
                execution_time=execution_time
            )
        except Exception as e:
            self.logger.error(f"Parameter extraction failed: {str(e)}")
            return AgentResult(
                agent_name=self.name,
                success=False,
                error=str(e)
            )


class InterpretationAgent:
    """Agent responsible for interpreting blood parameters (Model 1)."""
    
    def __init__(self):
        self.name = "Parameter Interpretation Agent"
        self.logger = logging.getLogger(self.name)
    
    def execute(self, cleaned_params: Dict[str, Any]) -> AgentResult:
        """Interpret medical parameters using Model 1."""
        import time
        start_time = time.time()
        
        try:
            self.logger.info("Starting parameter interpretation")
            interpretations = interpret_parameters(cleaned_params)
            
            execution_time = time.time() - start_time
            self.logger.info(f"Generated {len(interpretations)} interpretations in {execution_time:.2f}s")
            
            return AgentResult(
                agent_name=self.name,
                success=True,
                data=interpretations,
                execution_time=execution_time
            )
        except Exception as e:
            self.logger.error(f"Parameter interpretation failed: {str(e)}")
            return AgentResult(
                agent_name=self.name,
                success=False,
                data=[],
                error=str(e)
            )


class RiskAnalysisAgent:
    """Agent responsible for analyzing health risks (Model 2)."""
    
    def __init__(self):
        self.name = "Risk Analysis Agent"
        self.logger = logging.getLogger(self.name)
    
    def execute(self, cleaned_params: Dict[str, Any], interpretations: List[str]) -> AgentResult:
        """Analyze risks using Model 2."""
        import time
        start_time = time.time()
        
        try:
            self.logger.info("Starting risk analysis")
            risks = analyze_risks(cleaned_params, interpretations)
            
            execution_time = time.time() - start_time
            self.logger.info(f"Identified {len(risks)} risks in {execution_time:.2f}s")
            
            return AgentResult(
                agent_name=self.name,
                success=True,
                data=risks,
                execution_time=execution_time
            )
        except Exception as e:
            self.logger.error(f"Risk analysis failed: {str(e)}")
            return AgentResult(
                agent_name=self.name,
                success=False,
                data=[],
                error=str(e)
            )


class PredictionAgent:
    """Agent responsible for AI-based risk prediction."""
    
    def __init__(self):
        self.name = "AI Prediction Agent"
        self.logger = logging.getLogger(self.name)
    
    def execute(self, cleaned_params: Dict[str, Any]) -> AgentResult:
        """Generate AI prediction for health risk."""
        import time
        start_time = time.time()
        
        try:
            self.logger.info("Starting AI risk prediction")
            prediction = predict_risk(cleaned_params)
            
            execution_time = time.time() - start_time
            self.logger.info(f"Generated risk prediction in {execution_time:.2f}s")
            
            return AgentResult(
                agent_name=self.name,
                success=True,
                data=prediction,
                execution_time=execution_time
            )
        except Exception as e:
            self.logger.error(f"AI prediction failed: {str(e)}")
            return AgentResult(
                agent_name=self.name,
                success=False,
                data={"risk_score": 0.5, "risk_label": "moderate", "confidence": "low"},
                error=str(e)
            )


class LLMRecommendationAgent:
    """Agent responsible for generating LLM-based recommendations using multiple LLM providers."""
    
    def __init__(self):
        self.name = "LLM Recommendation Agent"
        self.logger = logging.getLogger(self.name)
        self.multi_llm_service = get_multi_llm_service()
    
    async def execute(
        self,
        interpretations: List[str],
        risks: List[str],
        cleaned_params: Dict[str, Any],
        patient_context: Optional[Dict[str, Any]] = None
    ) -> AgentResult:
        """Generate recommendations using multiple LLM providers with fallback (Async)."""
        import time
        start_time = time.time()
        
        try:
            # Check availability first (fast, no I/O usually)
            if not self.multi_llm_service.is_any_available():
                self.logger.warning("No LLM providers available, using fallback recommendations")
                return self._fallback_recommendations(interpretations, risks)
            
            available_providers = self.multi_llm_service.get_available_providers()
            self.logger.info(f"Requesting recommendations from available LLMs: {', '.join(available_providers)}")
            
            # Run blocking LLM call in a thread
            recommendations = await asyncio.to_thread(
                self.multi_llm_service.generate_medical_recommendations,
                interpretations=interpretations,
                risks=risks,
                parameters=cleaned_params,
                patient_context=patient_context
            )
            
            execution_time = time.time() - start_time
            
            if recommendations:
                provider_info = self.multi_llm_service.get_provider_info()
                self.logger.info(f"Generated {len(recommendations)} LLM recommendations in {execution_time:.2f}s using {provider_info['primary']}")
                return AgentResult(
                    agent_name=self.name,
                    success=True,
                    data=recommendations,
                    execution_time=execution_time
                )
            else:
                self.logger.warning("Empty response from all LLMs, using fallback")
                return self._fallback_recommendations(interpretations, risks)
        
        except Exception as e:
            self.logger.error(f"LLM recommendation generation failed: {str(e)}")
            return self._fallback_recommendations(interpretations, risks)
    
    def _fallback_recommendations(self, interpretations: List[str], risks: List[str]) -> AgentResult:
        """Fallback to rule-based recommendations."""
        try:
            recommendations = generate_recommendations(interpretations, risks)
            return AgentResult(
                agent_name=self.name,
                success=True,
                data=recommendations,
                error="LLM unavailable, using fallback recommendations"
            )
        except Exception as e:
            self.logger.error(f"Fallback recommendations failed: {str(e)}")
            return AgentResult(
                agent_name=self.name,
                success=False,
                data=["Consult healthcare provider for personalized advice"],
                error=str(e)
            )


class PrescriptionAgent:
    """Agent responsible for generating prescriptions."""
    
    def __init__(self):
        self.name = "Prescription Generation Agent"
        self.logger = logging.getLogger(self.name)
    
    def execute(
        self,
        interpretations: List[str],
        risks: List[str],
        cleaned_params: Dict[str, Any]
    ) -> AgentResult:
        """Generate prescriptions based on analysis."""
        import time
        start_time = time.time()
        
        try:
            self.logger.info("Starting prescription generation")
            prescriptions = generate_prescriptions(interpretations, risks, cleaned_params)
            
            execution_time = time.time() - start_time
            self.logger.info(f"Generated {len(prescriptions)} prescriptions in {execution_time:.2f}s")
            
            return AgentResult(
                agent_name=self.name,
                success=True,
                data=prescriptions,
                execution_time=execution_time
            )
        except Exception as e:
            self.logger.error(f"Prescription generation failed: {str(e)}")
            return AgentResult(
                agent_name=self.name,
                success=False,
                data=[],
                error=str(e)
            )


class SynthesisAgent:
    """Agent responsible for synthesizing all findings into a coherent summary."""
    
    def __init__(self):
        self.name = "Findings Synthesis Agent"
        self.logger = logging.getLogger(self.name)
    
    def execute(
        self,
        interpretations: List[str],
        risks: List[str]
    ) -> AgentResult:
        """Synthesize all findings into a summary."""
        import time
        start_time = time.time()
        
        try:
            self.logger.info("Starting findings synthesis")
            synthesis = synthesize_findings(interpretations, risks)
            
            execution_time = time.time() - start_time
            self.logger.info(f"Generated synthesis in {execution_time:.2f}s")
            
            return AgentResult(
                agent_name=self.name,
                success=True,
                data=synthesis,
                execution_time=execution_time
            )
        except Exception as e:
            self.logger.error(f"Findings synthesis failed: {str(e)}")
            return AgentResult(
                agent_name=self.name,
                success=False,
                data="",
                error=str(e)
            )


class MultiAgentOrchestrator:
    """
    Orchestrates multiple agents to perform comprehensive health analysis.
    
    Workflow:
    1. Parameter Extraction Agent -> clean and normalize data
    2. Interpretation Agent -> interpret parameters (Model 1)
    3. Risk Analysis Agent -> analyze risks (Model 2)
    4. Prediction Agent -> AI risk prediction
    5. LLM Recommendation Agent -> generate recommendations via Gemini API
    6. Prescription Agent -> generate prescriptions
    7. Synthesis Agent -> synthesize all findings
    """
    
    def __init__(self):
        self.logger = logging.getLogger("MultiAgentOrchestrator")
        self.intent_inference_agent = IntentInferenceAgent()
        self.extraction_agent = ParameterExtractionAgent()
        self.interpretation_agent = InterpretationAgent()
        self.risk_analysis_agent = RiskAnalysisAgent()
        self.prediction_agent = PredictionAgent()
        self.llm_recommendation_agent = LLMRecommendationAgent()
        self.prescription_agent = PrescriptionAgent()
        self.synthesis_agent = SynthesisAgent()
        self.agent_results: List[AgentResult] = []
    
    async def execute(
        self,
        raw_params: Dict[str, Any],
        patient_context: Optional[Dict[str, Any]] = None
    ) -> AnalysisReport:
        """
        Execute the multi-agent workflow to analyze health data (legacy method).

        Args:
            raw_params: Raw medical parameters to analyze
            patient_context: Optional patient information

        Returns:
            AnalysisReport with analysis results
        """
        # Create dummy conversation context for backward compatibility
        dummy_context = ConversationContext()
        return await self.execute_with_intent(
            user_input="Analyze blood report",  # Default intent
            raw_params=raw_params,
            conversation_context=dummy_context,
            patient_context=patient_context
        )

    async def execute_with_intent(
        self,
        user_input: str,
        raw_params: Optional[Dict[str, Any]] = None,
        conversation_context: Optional[ConversationContext] = None,
        patient_context: Optional[Dict[str, Any]] = None
    ) -> AnalysisReport:
        """
        Execute the multi-agent workflow with intent inference for natural user interaction.

        Args:
            user_input: Natural language user input
            raw_params: Optional raw medical parameters from input
            conversation_context: Optional conversation history and user state
            patient_context: Optional patient context (age, gender, etc.)

        Returns:
            AnalysisReport with results from all agents including intent analysis
        """
        import time
        overall_start = time.time()
        self.agent_results = []

        self.logger.info("Starting intent-aware multi-agent health analysis workflow")
        self.logger.info(f"User input: '{user_input[:100]}...'")

        # Stage 0: Infer user intent (async, I/O bound)
        intent_result = await self.intent_inference_agent.analyze_intent(user_input, conversation_context)
        self.logger.info(f"Inferred intent: {intent_result.inferred_intent} (confidence: {intent_result.confidence_score:.2f})")

        # Update conversation context
        if conversation_context:
            conversation_context = self.intent_inference_agent.update_conversation_context(
                conversation_context, user_input, intent_result
            )

        # Determine if we need parameters for this intent
        intent_requires_params = intent_result.inferred_intent in [
            'analyze_blood_report', 'follow_up_previous_analysis'
        ]

        params_to_use = raw_params if intent_requires_params else None

        # Stage 1: Extract and clean parameters (CPU bound, fast)
        if params_to_use:
            extraction_result = self.extraction_agent.execute(params_to_use)
            self.agent_results.append(extraction_result)

            if not extraction_result.success:
                self.logger.error("Parameter extraction failed, cannot continue")
                return self._create_failed_report(extraction_result, intent_result, conversation_context)

            cleaned_params = extraction_result.data or {}
        else:
            # No parameters to extract, proceed with intent-based analysis
            cleaned_params = {}
            self.logger.info("Skipping parameter extraction - intent doesn't require parameters")
        
        # Stage 2: Interpret parameters
        interpretation_result = self.interpretation_agent.execute(cleaned_params)
        self.agent_results.append(interpretation_result)
        interpretations = interpretation_result.data or []
        
        # Stage 3: Analyze risks
        risk_result = self.risk_analysis_agent.execute(cleaned_params, interpretations)
        self.agent_results.append(risk_result)
        risks = risk_result.data or []
        
        # Stage 4: Generate AI prediction
        prediction_result = self.prediction_agent.execute(cleaned_params)
        self.agent_results.append(prediction_result)
        ai_prediction = prediction_result.data or {}
        
        # Stage 5: Generate recommendations via LLM (I/O bound -> await)
        llm_result = await self.llm_recommendation_agent.execute(
            interpretations,
            risks,
            cleaned_params,
            patient_context
        )
        self.agent_results.append(llm_result)
        recommendations = llm_result.data or []
        
        # Stage 6: Generate prescriptions
        prescription_result = self.prescription_agent.execute(
            interpretations,
            risks,
            cleaned_params
        )
        self.agent_results.append(prescription_result)
        prescriptions = prescription_result.data or []
        
        # Stage 7: Synthesize findings
        synthesis_result = self.synthesis_agent.execute(interpretations, risks)
        self.agent_results.append(synthesis_result)
        synthesis = synthesis_result.data or ""
        
        overall_time = time.time() - overall_start
        
        # Build final report
        report = AnalysisReport(
            status="success",
            extracted_parameters=cleaned_params,
            interpretations=interpretations,
            risks=risks,
            ai_prediction=ai_prediction,
            recommendations=recommendations,
            prescriptions=prescriptions,
            synthesis=synthesis,
            agent_results=self.agent_results,
            intent_result=intent_result,
            conversation_context=conversation_context,
            timestamp=datetime.now().isoformat()
        )
        
        self.logger.info(f"Multi-agent analysis completed in {overall_time:.2f}s")
        self._log_agent_summary(report)
        
        return report
    
    def _create_failed_report(
        self,
        initial_error: AgentResult,
        intent_result: Optional[IntentResult] = None,
        conversation_context: Optional[ConversationContext] = None
    ) -> AnalysisReport:
        """Create a failed analysis report."""
        return AnalysisReport(
            status="failed",
            extracted_parameters={},
            interpretations=[],
            risks=[],
            ai_prediction={},
            recommendations=["Consult healthcare provider for personalized advice"],
            prescriptions=[],
            synthesis="",
            agent_results=self.agent_results,
            intent_result=intent_result,
            conversation_context=conversation_context,
            timestamp=datetime.now().isoformat()
        )
    
    def _log_agent_summary(self, report: AnalysisReport) -> None:
        """Log summary of agent results."""
        self.logger.info("=" * 60)
        self.logger.info("MULTI-AGENT ANALYSIS SUMMARY")
        self.logger.info("=" * 60)
        
        for result in report.agent_results:
            status = "✓ SUCCESS" if result.success else "✗ FAILED"
            self.logger.info(f"{status} | {result.agent_name} ({result.execution_time:.2f}s)")
            if result.error:
                self.logger.warning(f"  Error: {result.error}")
        
        self.logger.info("=" * 60)
        self.logger.info(f"Total Parameters: {len(report.extracted_parameters)}")
        self.logger.info(f"Interpretations: {len(report.interpretations)}")
        self.logger.info(f"Identified Risks: {len(report.risks)}")
        self.logger.info(f"Recommendations: {len(report.recommendations)}")
        self.logger.info(f"Prescriptions: {len(report.prescriptions)}")
        self.logger.info("=" * 60)
