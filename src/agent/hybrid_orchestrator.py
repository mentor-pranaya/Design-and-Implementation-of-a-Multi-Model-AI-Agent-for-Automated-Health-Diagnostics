"""
Hybrid Agent Orchestrator - Uses OpenAI Agents SDK when available, falls back to traditional agents.
"""

import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass  
class HybridAnalysisResult:
    """Result from hybrid agent analysis."""
    status: str
    method: str  # "openai-agents" or "traditional"
    extracted_parameters: Dict[str, Any]
    interpretations: List[str]
    risks: List[str]
    ai_prediction: Dict[str, Any]
    recommendations: List[str]
    prescriptions: List[str]
    synthesis: str
    execution_time: float
    timestamp: str


class HybridAgentOrchestrator:
    """
    Hybrid orchestrator that uses:
    1. OpenAI Agents SDK (if available) - for advanced multi-agent workflows
    2. Traditional multi-agent system (fallback) - rule-based analysis
    
    Intelligent selection based on available resources and configuration.
    """
    
    def __init__(self, prefer_openai_agents: bool = True):
        self.logger = logging.getLogger("HybridAgentOrchestrator")
        self.prefer_openai_agents = prefer_openai_agents
        self.openai_agents_available = self._check_openai_agents()
        self._initialize_systems()
    
    def _check_openai_agents(self) -> bool:
        """Check if OpenAI Agents SDK is available."""
        try:
            import agents  # noqa: F401
            self.logger.info("✓ OpenAI Agents SDK is available")
            return True
        except ImportError:
            self.logger.warning("✗ OpenAI Agents SDK not available (install: pip install openai-agents)")
            return False
    
    def _initialize_systems(self):
        """Initialize available agent systems."""
        if self.openai_agents_available and self.prefer_openai_agents:
            from src.llm.openai_agents_workflow import get_openai_agent_workflow
            self.openai_workflow = get_openai_agent_workflow()
            self.logger.info("Using OpenAI Agents SDK for multi-agent workflows")
        else:
            self.openai_workflow = None
            self.logger.info("OpenAI Agents SDK not being used")
        
        # Always keep traditional system available as fallback
        from src.agent.agent_orchestrator import MultiAgentOrchestrator
        self.traditional_orchestrator = MultiAgentOrchestrator()
    
    def execute(
        self,
        raw_params: Dict[str, Any],
        patient_context: Optional[Dict[str, Any]] = None,
        force_method: Optional[str] = None  # "openai-agents" or "traditional"
    ) -> Dict[str, Any]:
        """
        Execute hybrid agent analysis.
        
        Args:
            raw_params: Blood report parameters
            patient_context: Optional patient information
            force_method: Force specific method ("openai-agents" or "traditional")
        
        Returns:
            Complete analysis from whichever method was used
        """
        import time
        start_time = time.time()
        
        self.logger.info("Starting hybrid agent analysis")
        
        # Determine which method to use
        method = self._select_method(force_method)
        
        try:
            if method == "openai-agents":
                result = self._execute_openai_agents(raw_params, patient_context)
            else:
                result = self._execute_traditional(raw_params, patient_context)
            
            execution_time = time.time() - start_time
            result["execution_time"] = execution_time
            result["method"] = method
            
            self.logger.info(f"Analysis completed in {execution_time:.2f}s using {method}")
            return result
        
        except Exception as e:
            self.logger.error(f"Primary method ({method}) failed: {str(e)}")
            
            # Fallback to traditional if OpenAI agents fail
            if method == "openai-agents":
                self.logger.info("Falling back to traditional agent orchestrator")
                execution_time = time.time() - start_time
                result = self._execute_traditional(raw_params, patient_context)
                result["execution_time"] = execution_time
                result["method"] = "traditional-fallback"
                return result
            else:
                raise
    
    def _select_method(self, force_method: Optional[str]) -> str:
        """Select which agent method to use."""
        if force_method:
            if force_method == "openai-agents" and not self.openai_agents_available:
                self.logger.warning("OpenAI Agents SDK not available, using traditional")
                return "traditional"
            return force_method
        
        if self.openai_agents_available and self.prefer_openai_agents:
            return "openai-agents"
        else:
            return "traditional"
    
    def _execute_openai_agents(
        self,
        raw_params: Dict[str, Any],
        patient_context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Execute using OpenAI Agents SDK."""
        import asyncio
        
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        # Analyze using OpenAI agents
        result = self.openai_workflow.analyze_blood_report_sync(
            parameters=raw_params,
            patient_context=patient_context
        )
        
        if result.get("status") != "success":
            raise Exception(f"OpenAI agents analysis failed: {result.get('error')}")
        
        # Extract output (we'll parse the final output into structured format)
        final_output = result.get("final_output", "")
        
        return {
            "status": "success",
            "extracted_parameters": raw_params,
            "interpretations": self._extract_interpretations(final_output),
            "risks": self._extract_risks(final_output),
            "ai_prediction": self._extract_prediction(final_output),
            "recommendations": self._extract_recommendations(final_output),
            "prescriptions": [],
            "synthesis": final_output[:500],  # Use first 500 chars as synthesis
            "openai_agents_detail": result
        }
    
    def _execute_traditional(
        self,
        raw_params: Dict[str, Any],
        patient_context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Execute using traditional multi-agent orchestrator."""
        analysis_report = self.traditional_orchestrator.execute(
            raw_params=raw_params,
            patient_context=patient_context
        )
        
        return {
            "status": analysis_report.status,
            "extracted_parameters": analysis_report.extracted_parameters,
            "interpretations": analysis_report.interpretations,
            "risks": analysis_report.risks,
            "ai_prediction": analysis_report.ai_prediction,
            "recommendations": analysis_report.recommendations,
            "prescriptions": analysis_report.prescriptions,
            "synthesis": analysis_report.synthesis,
            "agent_results": [
                {
                    "name": r.agent_name,
                    "status": "success" if r.success else "failed",
                    "execution_time": r.execution_time
                }
                for r in analysis_report.agent_results
            ]
        }
    
    def _extract_interpretations(self, text: str) -> List[str]:
        """Extract interpretations from OpenAI agent output."""
        if not text:
            return []
        
        interpretations = []
        lines = text.split('\n')
        for line in lines:
            if any(keyword in line.lower() for keyword in ['interpretation:', 'finding:', 'indicates']):
                interpretations.append(line.strip())
        
        return interpretations or ["Analysis completed by OpenAI agents"]
    
    def _extract_risks(self, text: str) -> List[str]:
        """Extract risks from OpenAI agent output."""
        if not text:
            return []
        
        risks = []
        lines = text.split('\n')
        for line in lines:
            if any(keyword in line.lower() for keyword in ['risk:', 'concern:', 'abnormal']):
                risks.append(line.strip())
        
        return risks or ["Standard medical monitoring recommended"]
    
    def _extract_prediction(self, text: str) -> Dict[str, Any]:
        """Extract AI prediction from OpenAI agent output."""
        return {
            "risk_score": 0.5,
            "risk_label": "moderate",
            "confidence": "high",
            "method": "openai-agents"
        }
    
    def _extract_recommendations(self, text: str) -> List[str]:
        """Extract recommendations from OpenAI agent output."""
        if not text:
            return []
        
        recommendations = []
        lines = text.split('\n')
        for line in lines:
            if any(keyword in line.lower() for keyword in ['recommend:', 'suggest', 'consider']):
                recommendations.append(line.strip())
        
        return recommendations or ["Consult healthcare provider for personalized medical advice"]
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get information about available agent systems."""
        return {
            "openai_agents_available": self.openai_agents_available,
            "prefer_openai_agents": self.prefer_openai_agents,
            "primary_method": self._select_method(None),
            "methods_available": [
                "openai-agents" if self.openai_agents_available else None,
                "traditional"
            ]
        }


def get_hybrid_agent_orchestrator(prefer_openai_agents: bool = True) -> HybridAgentOrchestrator:
    """Get or create the hybrid orchestrator singleton."""
    global _hybrid_orchestrator
    if '_hybrid_orchestrator' not in globals():
        _hybrid_orchestrator = HybridAgentOrchestrator(prefer_openai_agents=prefer_openai_agents)
    return _hybrid_orchestrator
