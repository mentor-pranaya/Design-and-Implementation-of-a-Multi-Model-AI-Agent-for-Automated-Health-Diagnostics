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
from src.analysis.predictor import predict_risk
from src.llm.multi_llm_service import get_multi_llm_service
from src.agent.intent_inference_agent import IntentInferenceAgent, ConversationContext, IntentResult

# Integrated Models
from src.analysis.model_2 import Model2
from src.analysis.model_3 import Model3
from src.synthesis.findings_synthesizer import synthesize_findings
from src.recommendation.recommendation_generator import RecommendationGenerator, generate_prescriptions

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
    derived_metrics: Dict[str, Any]
    interpretations: List[str]
    risks: List[str]
    ai_prediction: Dict[str, Any]
    recommendations: List[str]  # Plain text for backward compatibility
    linked_recommendations: List[Dict[str, str]]
    prescriptions: List[str]
    synthesis: str
    summary: str # Short description
    agent_results: List[AgentResult]
    timestamp: str
    intent_result: Optional[IntentResult] = None
    conversation_context: Optional[ConversationContext] = None
    context_adjustments: List[str] = None


class ParameterExtractionAgent:
    """Agent responsible for extracting and cleaning medical parameters."""
    
    def __init__(self):
        self.name = "Parameter Extraction Agent"
        self.logger = logging.getLogger(self.name)
    
    def execute(self, raw_params: Dict[str, Any], raw_text: Optional[str] = None) -> AgentResult:
        """Extract and clean medical parameters, with LLM fallback."""
        import time
        start_time = time.time()
        
        try:
            self.logger.info(f"Processing {len(raw_params)} raw parameters")
            cleaned_params = clean_and_structure_data(raw_params)
            
            # Fallback to LLM if cleaning failed or yielded nothing
            if not cleaned_params and raw_text:
                self.logger.info("Regex extraction yielded no results. Attempting LLM extraction...")
                llm_service = get_multi_llm_service()
                llm_params = llm_service.extract_parameters_from_llm(raw_text)
                
                if llm_params:
                    self.logger.info(f"LLM extraction found {len(llm_params)} parameters")
                    # Clean the LLM output as well
                    cleaned_params = clean_and_structure_data(llm_params)
            
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
        self.name = "Risk Analysis Agent (Model 2)"
        self.logger = logging.getLogger(self.name)
        self.model_2 = Model2()
    
    def execute(self, cleaned_params: Dict[str, Any], patient_context: Dict[str, Any]) -> AgentResult:
        """Analyze risks and compute derived metrics using Model 2."""
        import time
        start_time = time.time()
        
        try:
            self.logger.info("Starting risk analysis with Model 2")
            # Model 2 returns { "derived_metrics": {}, "risk_indicators": [] }
            results = self.model_2.analyze(cleaned_params, patient_context)
            
            execution_time = time.time() - start_time
            self.logger.info(f"Identified {len(results.get('risk_indicators', []))} risks in {execution_time:.2f}s")
            
            return AgentResult(
                agent_name=self.name,
                success=True,
                data=results,
                execution_time=execution_time
            )
        except Exception as e:
            self.logger.error(f"Risk analysis failed: {str(e)}")
            return AgentResult(
                agent_name=self.name,
                success=False,
                data={"derived_metrics": {}, "risk_indicators": []},
                error=str(e)
            )


class ContextAnalysisAgent:
    """Agent responsible for contextual analysis (Model 3)."""
    
    def __init__(self):
        self.name = "Context Analysis Agent (Model 3)"
        self.logger = logging.getLogger(self.name)
        self.model_3 = Model3()
    
    def execute(self, cleaned_params: Dict[str, Any], patient_context: Dict[str, Any]) -> AgentResult:
        """Analyze context using Model 3."""
        import time
        start_time = time.time()
        
        try:
            self.logger.info("Starting contextual analysis with Model 3")
            # Model 3 returns { "context_adjustments": [] }
            results = self.model_3.analyze(cleaned_params, patient_context)
            
            execution_time = time.time() - start_time
            self.logger.info(f"Generated {len(results.get('context_adjustments', []))} context adjustments in {execution_time:.2f}s")
            
            return AgentResult(
                agent_name=self.name,
                success=True,
                data=results,
                execution_time=execution_time
            )
        except Exception as e:
            self.logger.error(f"Context analysis failed: {str(e)}")
            return AgentResult(
                agent_name=self.name,
                success=False,
                data={"context_adjustments": []},
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


class RecommendationAgent:
    """Agent responsible for generating Linked Recommendations."""
    
    def __init__(self):
        self.name = "Recommendation Agent"
        self.logger = logging.getLogger(self.name)
        self.generator = RecommendationGenerator()
    
    def execute(
        self,
        interpretations: List[str],
        risks: List[str],
        cleaned_params: Dict[str, Any],
        derived_metrics: Dict[str, Any]
    ) -> AgentResult:
        """Generate linked recommendations."""
        import time
        start_time = time.time()
        
        try:
            self.logger.info("Starting recommendation generation")
            recommendations = self.generator.generate(interpretations, risks, cleaned_params, derived_metrics)
            
            execution_time = time.time() - start_time
            self.logger.info(f"Generated {len(recommendations)} recommendations in {execution_time:.2f}s")
            
            return AgentResult(
                agent_name=self.name,
                success=True,
                data=recommendations, # List[Dict]
                execution_time=execution_time
            )
        except Exception as e:
            self.logger.error(f"Recommendation generation failed: {str(e)}")
            return AgentResult(
                agent_name=self.name,
                success=False,
                data=[],
                error=str(e)
            )


class LLMEnrichmentAgent:
    """
    Optional Agent: Uses LLM to enrich recommendations or provide a second opinion.
    Integrated into the main workflow but can be toggled.
    """
    def __init__(self):
        self.name = "LLM Enrichment Agent"
        self.logger = logging.getLogger(self.name)
        self.multi_llm_service = get_multi_llm_service()

    async def execute(
        self,
        interpretations: List[str],
        risks: List[str],
        cleaned_params: Dict[str, Any],
        patient_context: Optional[Dict[str, Any]] = None
    ) -> AgentResult:
         # Placeholder for advanced LLM features if needed, 
         # currently RecommendationAgent covers the core "linked" requirement.
         # We can keep this if we want to add an "Ask AI" feature later.
         return AgentResult(self.name, True, [], 0.0)


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
        cleaned_params: Dict[str, Any],
        interpretations: List[str],
        risks: List[str],
        recommendations: List[str], # Plain text recommendations
        derived_metrics: Dict[str, Any],
        context_adjustments: List[str]
    ) -> AgentResult:
        """Synthesize all findings into a summary."""
        import time
        start_time = time.time()
        
        try:
            self.logger.info("Starting findings synthesis")
            synthesis = synthesize_findings(
                cleaned_params, interpretations, risks, recommendations, derived_metrics, context_adjustments
            )
            
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
    3. Risk Analysis Agent -> analyze risks & ratios (Model 2)
    4. Context Analysis Agent -> adjust for context (Model 3)
    5. Prediction Agent -> AI risk prediction
    6. Recommendation Agent -> generate linked recommendations
    7. Prescription Agent -> generate prescriptions
    8. Synthesis Agent -> synthesize all findings
    """
    
    def __init__(self):
        self.logger = logging.getLogger("MultiAgentOrchestrator")
        self.intent_inference_agent = IntentInferenceAgent()
        self.extraction_agent = ParameterExtractionAgent()
        self.interpretation_agent = InterpretationAgent()
        self.risk_analysis_agent = RiskAnalysisAgent()
        self.context_analysis_agent = ContextAnalysisAgent()
        self.prediction_agent = PredictionAgent()
        self.recommendation_agent = RecommendationAgent()
        self.prescription_agent = PrescriptionAgent()
        self.synthesis_agent = SynthesisAgent()
        self.agent_results: List[AgentResult] = []
    
    async def execute(
        self,
        raw_params: Dict[str, Any],
        raw_text: Optional[str] = None,
        patient_context: Optional[Dict[str, Any]] = None
    ) -> AnalysisReport:
        """
        Execute the multi-agent workflow to analyze health data.
        """
        # Create dummy conversation context for backward compatibility
        dummy_context = ConversationContext()
        return await self.execute_with_intent(
            user_input="Analyze blood report",  # Default intent
            raw_params=raw_params,
            raw_text=raw_text,
            conversation_context=dummy_context,
            patient_context=patient_context
        )

    async def execute_with_intent(
        self,
        user_input: str,
        raw_params: Optional[Dict[str, Any]] = None,
        raw_text: Optional[str] = None,
        conversation_context: Optional[ConversationContext] = None,
        patient_context: Optional[Dict[str, Any]] = None
    ) -> AnalysisReport:
        """
        Execute the multi-agent workflow with intent inference.
        """
        import time
        overall_start = time.time()
        self.agent_results = []
        
        if patient_context is None:
            patient_context = {"gender": "unknown", "age": 30}

        self.logger.info("Starting intent-aware multi-agent health analysis workflow")
        
        # Stage 0: Infer user intent (async, I/O bound)
        intent_result = await self.intent_inference_agent.analyze_intent(user_input, conversation_context)
        
        # Update conversation context
        if conversation_context:
            conversation_context = self.intent_inference_agent.update_conversation_context(
                conversation_context, user_input, intent_result
            )

        # Determine if we need parameters for this intent
        intent_requires_params = intent_result.inferred_intent in [
            'analyze_blood_report', 'follow_up_previous_analysis'
        ]

        # Stage 1: Extract and clean parameters
        cleaned_params = {}
        if intent_requires_params:
            # Pass both structured params and raw text for fallback
            extraction_result = self.extraction_agent.execute(raw_params or {}, raw_text)
            self.agent_results.append(extraction_result)

            if not extraction_result.success:
                return self._create_failed_report(extraction_result, intent_result, conversation_context)

            cleaned_params = extraction_result.data or {}
        
        # PARALLEL EXECUTION: Stages 2, 3, 4, 5 (Independent)
        # These agents depend on cleaned_params but not on each other
        
        async def run_agent(agent, *args):
            return await asyncio.to_thread(agent.execute, *args)

        self.logger.info("Executing analysis models in parallel...")
        results = await asyncio.gather(
            run_agent(self.interpretation_agent, cleaned_params),
            run_agent(self.risk_analysis_agent, cleaned_params, patient_context),
            run_agent(self.context_analysis_agent, cleaned_params, patient_context),
            run_agent(self.prediction_agent, cleaned_params)
        )
        
        interpretation_result, risk_result, context_result, prediction_result = results
        
        self.agent_results.extend([interpretation_result, risk_result, context_result, prediction_result])
        
        # Unpack results
        interpretations = interpretation_result.data or []
        
        m2_data = risk_result.data or {}
        derived_metrics = m2_data.get("derived_metrics", {})
        risks = m2_data.get("risk_indicators", [])
        
        m3_data = context_result.data or {}
        context_adjustments = m3_data.get("context_adjustments", [])
        
        if context_adjustments:
             interpretations.extend([f"[Context] {adj}" for adj in context_adjustments])

        ai_prediction = prediction_result.data or {}
        
        # Stage 6 & 7: Recommendations and Prescriptions (Can be parallel)
        rec_pres_results = await asyncio.gather(
            run_agent(self.recommendation_agent, interpretations, risks, cleaned_params, derived_metrics),
            run_agent(self.prescription_agent, interpretations, risks, cleaned_params)
        )
        
        rec_result, prescription_result = rec_pres_results
        self.agent_results.extend([rec_result, prescription_result])
        
        linked_recommendations = rec_result.data or []
        plain_recommendations = [r["recommendation"] for r in linked_recommendations]
        prescriptions = prescription_result.data or []
        
        # Stage 8: Synthesize findings (Depends on everything)
        synthesis_result = self.synthesis_agent.execute(
            cleaned_params, interpretations, risks, plain_recommendations, derived_metrics, context_adjustments
        )
        self.agent_results.append(synthesis_result)
        synthesis = synthesis_result.data or ""
        
        overall_time = time.time() - overall_start
        
        # Build description/summary
        summary = synthesis
        
        # Build final report
        report = AnalysisReport(
            status="success",
            extracted_parameters=cleaned_params,
            derived_metrics=derived_metrics,
            interpretations=interpretations,
            risks=risks,
            ai_prediction=ai_prediction,
            recommendations=plain_recommendations,
            linked_recommendations=linked_recommendations,
            prescriptions=prescriptions,
            synthesis=synthesis,
            summary=summary,
            agent_results=self.agent_results,
            intent_result=intent_result,
            conversation_context=conversation_context,
            context_adjustments=context_adjustments,
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
            derived_metrics={},
            interpretations=[],
            risks=[],
            ai_prediction={},
            recommendations=["Consult healthcare provider for personalized advice"],
            linked_recommendations=[],
            prescriptions=[],
            synthesis="",
            summary="Analysis failed.",
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
        self.logger.info("=" * 60)
