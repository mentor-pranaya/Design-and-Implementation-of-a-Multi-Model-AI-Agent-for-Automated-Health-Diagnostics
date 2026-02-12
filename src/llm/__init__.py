"""LLM Service - Multi-provider LLM system for health diagnostics."""

from src.llm.multi_llm_service import (
    MultiLLMService,
    get_multi_llm_service
)
from src.llm.llm_provider import LLMProvider
from src.llm.gemini_provider import GeminiLLMProvider
from src.llm.openai_provider import OpenAILLMProvider
from src.llm.claude_provider import ClaudeLLMProvider

try:
    from src.llm.openai_agents_workflow import (
        BloodReportAgentWorkflow,
        get_openai_agent_workflow
    )
    OPENAI_AGENTS_AVAILABLE = True
except ImportError:
    OPENAI_AGENTS_AVAILABLE = False

__all__ = [
    "MultiLLMService",
    "get_multi_llm_service",
    "LLMProvider",
    "GeminiLLMProvider",
    "OpenAILLMProvider",
    "ClaudeLLMProvider",
]

if OPENAI_AGENTS_AVAILABLE:
    __all__.extend([
        "BloodReportAgentWorkflow",
        "get_openai_agent_workflow"
    ])
