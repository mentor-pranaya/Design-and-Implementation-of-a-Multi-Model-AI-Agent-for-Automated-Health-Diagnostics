# OpenAI Agents SDK Integration

## Overview

INBLOODO AGENT now supports **OpenAI's Agents SDK** - a powerful framework for building multi-agent workflows with handoffs between specialized agents. This provides enterprise-grade agent orchestration for blood report analysis.

## Key Features

### 1. **Multi-Agent Handoff System**
Agents can hand off work to other specialized agents:
```
Triage Agent 
  → Parameter Analysis Agent
  → Medical Interpretation Agent  
  → Risk Assessment Agent
  → Recommendation Agent
```

### 2. **Automatic Conversation History**
Built-in session management maintains context across agent interactions.

### 3. **Advanced Tracing & Debugging**
Complete tracing of agent execution with detailed logging.

### 4. **Hybrid Orchestration**
- **Primary**: OpenAI Agents SDK (when available)
- **Fallback**: Traditional multi-agent system
- Automatic selection based on availability

## Architecture

```
┌─────────────────────────────────────┐
│   Blood Report (PDF/CSV/Image/JSON)  │
└──────────────┬──────────────────────┘
               │
       ┌───────▼────────┐
       │ Hybrid           │
       │ Orchestrator     │
       └────────┬────────┘
               │
    ┌──────────┴──────────┐
    │                     │
    ▼                     ▼
┌─OpenAI Agents──  ┌─Traditional──
│ Triage Agent ──  │ Multi-Agent  │
│ ├─Parameters     │ System       │
│ ├─Interpret      │ (Fallback)   │
│ ├─Risk           │              │
│ └─Recommend  ──  └──────────────┘
└──────────────────┐
                   │
                   ▼
          ┌────────────────┐
          │ LLM Providers  │
          │ (Gemini, GPT)  │
          └────────────────┘
                   │
                   ▼
          ┌────────────────┐
          │ Blood Report   │
          │ Analysis       │
          └────────────────┘
```

## Installation

### 1. Install Required Packages
```bash
pip install -r requirements.txt
```

Or individually:
```bash
# Core OpenAI Agents SDK
pip install openai-agents

# LLM Providers
pip install openai anthropic google-generativeai
```

### 2. Configure Environment
```env
# Select orchestrator method (default: hybrid with OpenAI agents if available)
ORCHESTRATOR_METHOD=hybrid  # Options: hybrid, openai-agents, traditional

# LLM Configuration
LLM_PROVIDER=gemini
GEMINI_API_KEY=your-key
OPENAI_API_KEY=your-key
ANTHROPIC_API_KEY=your-key
```

## Usage Example

### Basic Analysis (Hybrid Mode)
```python
from src.agent.hybrid_orchestrator import get_hybrid_agent_orchestrator

# Get orchestrator (automatically selects best method)
orchestrator = get_hybrid_agent_orchestrator(prefer_openai_agents=True)

# Analyze blood report
result = orchestrator.execute(
    raw_params={
        "hemoglobin": 9.5,
        "glucose": 155,
        "cholesterol": 220
    },
    patient_context={
        "age": 45,
        "gender": "male"
    }
)

print(f"Method: {result['method']}")
print(f"Recommendations: {result['recommendations']}")
```

### Force Specific Method
```python
# Force OpenAI Agents
result = orchestrator.execute(
    raw_params=params,
    patient_context=context,
    force_method="openai-agents"  # or "traditional"
)
```

### API Endpoints

#### 1. Analyze with Automatic Method Selection
```bash
curl -X POST "http://localhost:10000/analyze-report/" \
  -H "X-API-Key: your-key" \
  -F "file=@blood_report.pdf"
```

#### 2. Force OpenAI Agents
```bash
curl -X POST "http://localhost:10000/analyze-report/" \
  -H "X-API-Key: your-key" \
  -H "X-Agent-Method: openai-agents" \
  -F "file=@blood_report.pdf"
```

#### 3. Force Traditional Method
```bash
curl -X POST "http://localhost:10000/analyze-report/" \
  -H "X-API-Key: your-key" \
  -H "X-Agent-Method: traditional" \
  -F "file=@blood_report.pdf"
```

#### 4. Get System Info
```bash
curl -X GET "http://localhost:10000/api/agent-systems/" \
  -H "X-API-Key: your-key"
```

Response:
```json
{
  "openai_agents_available": true,
  "traditional_available": true,
  "primary_method": "openai-agents",
  "methods_available": ["openai-agents", "traditional"],
  "hybrid_mode": true
}
```

## Response Format

### Hybrid Orchestrator Response
```json
{
  "status": "success",
  "method": "openai-agents",
  "extracted_parameters": {...},
  "interpretations": [...],
  "risks": [...],
  "ai_prediction": {...},
  "recommendations": [...],
  "prescriptions": [...],
  "synthesis": "...",
  "execution_time": 2.34,
  "llm_provider_info": {
    "primary": "Google Gemini",
    "available_providers": [...],
    "total_available": 1,
    "fallback_enabled": true
  },
  "agent_execution": {...}
}
```

## OpenAI Agents SDK Features

### Agents
Specialized agents with specific roles:
```python
from agents import Agent

interpretation_agent = Agent(
    name="Medical Interpretation Agent",
    instructions="You are a medical expert specializing in blood report interpretation...",
    model="gpt-4-turbo"
)
```

### Handoffs
Transfer work between agents:
```python
triage_agent = Agent(
    name="Triage Agent",
    handoffs=[parameter_agent, interpretation_agent, risk_agent]
)
```

### Function Tools
Use Python functions as LLM tools:
```python
from agents import function_tool

@function_tool
def validate_parameter(param_name: str, value: float) -> str:
    """Validate blood parameter against clinical ranges."""
    # Implementation
    pass

agent = Agent(
    name="Parameter Agent",
    tools=[validate_parameter]
)
```

### Sessions
Built-in conversation memory:
```python
from agents import SQLiteSession, Runner

session = SQLiteSession("user_123", "conversations.db")

result = await Runner.run(
    agent,
    "What's my hemoglobin level?",
    session=session
)

# Second turn automatically remembers context
result = await Runner.run(
    agent,
    "Is it normal?",
    session=session
)
```

## Comparison: Traditional vs. OpenAI Agents

| Feature | Traditional | OpenAI Agents |
|---------|-----------|---------------|
| Architecture | Rule-based agents | LLM-coordinated agents |
| Handoffs | Limited | Full support |
| Session Memory | Manual | Built-in |
| Tracing | Basic logging | Advanced UI |
| Flexibility | Moderate | Very high |
| Speed | Fast | Moderate (API calls) |
| Cost | Free | OpenAI API costs |
| Complexity | Moderate | Can be complex |

## Monitoring & Logging

### Check Available Methods
```bash
python -c "from src.agent import get_hybrid_agent_orchestrator; 
orchestrator = get_hybrid_agent_orchestrator(); 
print(orchestrator.get_system_info())"
```

### Enable Debug Logging
```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Now run analysis with detailed output
orchestrator.execute(raw_params, patient_context)
```

### View Tracing
OpenAI Agents SDK provides:
- Agent execution timeline
- Tool call history
- Message exchanges
- Token usage
- Error tracking

## Performance Characteristics

### Traditional Method
- **Speed**: ~500ms-1s per analysis
- **Cost**: Free (local execution)
- **Accuracy**: Rule-based (consistent)
- **Flexibility**: Limited

### OpenAI Agents Method
- **Speed**: ~2-4s per analysis (includes API calls)
- **Cost**: Based on OpenAI API pricing
- **Accuracy**: LLM-based (contextual)
- **Flexibility**: High

### Fallback Behavior
If primary method fails:
1. OpenAI Agents → Traditional (fallback)
2. Both methods available simultaneously
3. Response indicates which method was used

## Troubleshooting

### OpenAI Agents Not Available
```
WARNING: OpenAI Agents SDK not available (install: pip install openai-agents)
```
**Solution**: Install optional dependency
```bash
pip install openai-agents
```

### OpenAI Agents API Errors
```
openai.APIConnectionError: Failed to connect to OpenAI API
```
**Solution**: 
- Check OPENAI_API_KEY is set
- Verify API key is valid
- Check internet connectivity
- System will automatically fallback to traditional method

### Slow Response Times
- OpenAI Agents makes API calls (slower)
- Use traditional method for speed
- Or configure force_method="traditional" 

### Memory/Session Issues
- Check SQLite database permissions
- Verify database file exists
- Clear old sessions if needed

## Advanced Configuration

### Custom Agent Instructions
Modify agent instructions in `openai_agents_workflow.py`:
```python
def create_interpretation_agent(self) -> "Agent":
    return self.Agent(
        name="Medical Interpretation Agent",
        instructions="Your custom medical instructions here...",
        model="gpt-4-turbo"  # Can change model
    )
```

### Custom Session Storage
Implement custom session:
```python
from agents.memory import Session

class MyCustomSession:
    async def get_items(self, limit: int | None = None):
        # Your implementation
        pass
    
    # ... other required methods
```

## Examples

See the `examples/` directory for complete examples:
- Basic blood report analysis
- Multi-turn analysis with session memory
- Custom agent creation
- Advanced handoff workflows

## Support  & Documentation

- [OpenAI Agents SDK Docs](https://openai.github.io/openai-agents-python/)
- [GitHub Repository](https://github.com/openai/openai-agents-python)
- INBLOODO AGENT Issues: Check GitHub issues for specific problems

## Next Steps

1. **Install**: `pip install openai-agents`
2. **Configure**: Set `.env` variables
3. **Test**: Run hybrid orchestrator with your data
4. **Deploy**: Use production-ready hybrid configuration
5. **Monitor**: Check logs and agent execution stats

---

**Multi-Agent Blood Report Analysis - Now with OpenAI Agents SDK!** 🚀
