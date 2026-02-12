"""
OpenAI Agents SDK - Multi-Agent Workflow for Blood Report Analysis.

Uses OpenAI's agents framework with handoffs between specialized medical agents.
Features:
- Parameter Analysis Agent
- Medical Interpretation Agent  
- Risk Assessment Agent
- Recommendation Agent
- Built-in conversation history and tracing
"""

import os
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class AgentAnalysisResult:
    """Result from OpenAI agent analysis."""
    final_output: str
    agent_name: str
    success: bool
    execution_time: float
    error: Optional[str] = None


class BloodReportAgentWorkflow:
    """
    Orchestrates OpenAI agents for blood report analysis.
    
    Workflow:
    1. Triage Agent receives report and routes to appropriate specialists
    2. Parameter Analysis Agent extracts and validates parameters
    3. Medical Interpretation Agent interprets findings
    4. Risk Assessment Agent identifies health risks
    5. Recommendation Agent generates personalized recommendations
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._initialize_agents()
    
    def _initialize_agents(self):
        """Initialize OpenAI agents - lazy loaded on first use."""
        try:
            from agents import Agent, SQLiteSession
            self.Agent = Agent
            self.SQLiteSession = SQLiteSession
            self.agents_available = True
            self.logger.info("OpenAI Agents SDK available")
        except ImportError:
            self.logger.warning(
                "OpenAI Agents SDK not installed. "
                "Install with: pip install openai-agents"
            )
            self.agents_available = False
    
    def create_parameter_analysis_agent(self) -> "Agent":
        """Create agent for parameter extraction and validation."""
        if not self.agents_available:
            raise RuntimeError("OpenAI Agents SDK not available")
        
        return self.Agent(
            name="Parameter Analysis Agent",
            instructions="""You are a medical parameter analysis specialist.
Your role is to:
1. Analyze extracted blood report parameters
2. Validate parameter ranges (hemoglobin, glucose, cholesterol, etc.)
3. Identify abnormal values
4. Format parameters for downstream agents
5. Handoff to Medical Interpretation Agent when complete

Be precise and clinical in your analysis.""",
            model="gpt-4-turbo"
        )
    
    def create_interpretation_agent(self) -> "Agent":
        """Create agent for medical interpretation."""
        if not self.agents_available:
            raise RuntimeError("OpenAI Agents SDK not available")
        
        return self.Agent(
            name="Medical Interpretation Agent",
            instructions="""You are a medical expert specializing in blood report interpretation.
Your role is to:
1. Interpret abnormal parameter values
2. Identify potential health conditions
3. Correlate findings with medical knowledge
4. Provide clinical insights
5. Handoff to Risk Assessment Agent with findings

Focus on accuracy and evidence-based interpretation.""",
            model="gpt-4-turbo"
        )
    
    def create_risk_assessment_agent(self) -> "Agent":
        """Create agent for health risk assessment."""
        if not self.agents_available:
            raise RuntimeError("OpenAI Agents SDK not available")
        
        return self.Agent(
            name="Risk Assessment Agent",
            instructions="""You are a clinical risk assessment specialist.
Your role is to:
1. Assess overall health risk levels
2. Identify critical vs. moderate vs. minor concerns
3. Determine urgency of medical consultation
4. Categorize risks by organ system
5. Handoff to Recommendation Agent with risk profile

Prioritize patient safety and accurate risk stratification.""",
            model="gpt-4-turbo"
        )
    
    def create_recommendation_agent(self) -> "Agent":
        """Create agent for personalized health recommendations."""
        if not self.agents_available:
            raise RuntimeError("OpenAI Agents SDK not available")
        
        return self.Agent(
            name="Recommendation Agent",
            instructions="""You are a health and wellness recommendation specialist.
Your role is to:
1. Generate personalized health recommendations
2. Prioritize recommendations by risk level
3. Include lifestyle, dietary, and medical advice
4. Provide actionable steps
5. Emphasize need for professional medical consultation

Make recommendations specific, practical, and evidence-based.""",
            model="gpt-4-turbo"
        )
    
    def create_triage_agent(
        self,
        analysis_agent: "Agent",
        interpretation_agent: "Agent",
        risk_agent: "Agent",
        recommendation_agent: "Agent"
    ) -> "Agent":
        """Create triage agent with handoffs to specialists."""
        if not self.agents_available:
            raise RuntimeError("OpenAI Agents SDK not available")
        
        return self.Agent(
            name="Blood Report Triage Agent",
            instructions="""You are the primary triage agent for blood report analysis.
Your role is to:
1. Receive blood report parameters
2. Route to Parameter Analysis Agent
3. Coordinate handoffs between specialized agents
4. Ensure comprehensive analysis
5. Synthesize final recommendations

Ensure all aspects of the report are analyzed.""",
            model="gpt-4-turbo",
            handoffs=[
                analysis_agent,
                interpretation_agent,
                risk_agent,
                recommendation_agent
            ]
        )
    
    async def analyze_blood_report(
        self,
        parameters: Dict[str, Any],
        patient_context: Optional[Dict[str, Any]] = None,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze blood report using multi-agent workflow.
        
        Args:
            parameters: Blood test parameters
            patient_context: Optional patient info (age, gender, etc.)
            session_id: Optional session ID for conversation history
        
        Returns:
            Complete analysis with all agent outputs
        """
        if not self.agents_available:
            raise RuntimeError("OpenAI Agents SDK not available")
        
        import time
        from agents import Runner
        
        start_time = time.time()
        
        try:
            # Create agents
            analysis_agent = self.create_parameter_analysis_agent()
            interpretation_agent = self.create_interpretation_agent()
            risk_agent = self.create_risk_assessment_agent()
            recommendation_agent = self.create_recommendation_agent()
            triage_agent = self.create_triage_agent(
                analysis_agent,
                interpretation_agent,
                risk_agent,
                recommendation_agent
            )
            
            # Format input prompt
            param_str = "\n".join([f"- {k}: {v}" for k, v in parameters.items()])
            prompt = f"""Analyze the following blood report parameters:

PARAMETERS:
{param_str}
"""
            
            if patient_context:
                context_str = "\n".join([f"- {k}: {v}" for k, v in patient_context.items()])
                prompt += f"\nPATIENT CONTEXT:\n{context_str}"
            
            # Create session if provided
            session = None
            if session_id:
                session = self.SQLiteSession(session_id)
            
            # Run analysis through triage agent
            result = await Runner.run(
                triage_agent,
                prompt,
                session=session
            )
            
            execution_time = time.time() - start_time
            
            return {
                "status": "success",
                "final_output": result.final_output,
                "agent_messages": getattr(result, "messages", []),
                "execution_time": execution_time,
                "tracing_enabled": True
            }
        
        except Exception as e:
            self.logger.error(f"Blood report analysis failed: {str(e)}")
            return {
                "status": "failed",
                "error": str(e),
                "execution_time": time.time() - start_time
            }
    
    def analyze_blood_report_sync(
        self,
        parameters: Dict[str, Any],
        patient_context: Optional[Dict[str, Any]] = None,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Synchronous wrapper for blood report analysis."""
        import asyncio
        
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        return loop.run_until_complete(
            self.analyze_blood_report(parameters, patient_context, session_id)
        )


def get_openai_agent_workflow() -> BloodReportAgentWorkflow:
    """Get or create the OpenAI agent workflow singleton."""
    global _openai_workflow
    if '_openai_workflow' not in globals():
        _openai_workflow = BloodReportAgentWorkflow()
    return _openai_workflow
