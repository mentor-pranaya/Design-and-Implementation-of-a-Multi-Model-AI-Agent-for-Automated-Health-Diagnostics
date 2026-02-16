# Multi-LLM System Documentation

## Overview

The INBLOODO AGENT now supports **multiple Large Language Model (LLM) providers** with intelligent fallback mechanisms. This allows the system to use different AI models and automatically switch to alternatives if the primary provider fails.

## Supported LLM Providers

### 1. Google Gemini ⭐ (Default)
- **Model**: gemini-1.5-flash
- **Cost**: Free tier available + pay-as-you-go
- **Speed**: Fast
- **API Key**: Get from [Google AI Studio](https://aistudio.google.com/app/apikey)
- **Environment Variable**: `GEMINI_API_KEY`

### 2. OpenAI GPT
- **Model**: gpt-4
- **Cost**: Pay-as-you-go (requires credits)
- **Speed**: Very Fast
- **API Key**: Get from [OpenAI Platform](https://platform.openai.com/api-keys)
- **Environment Variable**: `OPENAI_API_KEY`
- **Installation**: `pip install openai`

### 3. Anthropic Claude
- **Model**: claude-3-opus-20240229
- **Cost**: Pay-as-you-go
- **Speed**: Fast
- **API Key**: Get from [Anthropic Console](https://console.anthropic.com)
- **Environment Variable**: `ANTHROPIC_API_KEY`
- **Installation**: `pip install anthropic`

## Configuration

### Setting Primary LLM Provider

Edit your `.env` file:

```env
# Set primary LLM provider (default: gemini)
LLM_PROVIDER=gemini
# Options: gemini, openai, claude

# Add API keys for providers you want to use
GEMINI_API_KEY=your-gemini-key
OPENAI_API_KEY=your-openai-key
ANTHROPIC_API_KEY=your-anthropic-key
```

### Examples

**Using Gemini (default):**
```env
LLM_PROVIDER=gemini
GEMINI_API_KEY=AIzaSyBkFhAESsvfbQxDYl9BSs_i_TZT4TmEcFs
```

**Using OpenAI as primary with Gemini fallback:**
```env
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-your-openai-key
GEMINI_API_KEY=your-gemini-key  # Fallback
```

**Using Claude with multiple fallbacks:**
```env
LLM_PROVIDER=claude
ANTHROPIC_API_KEY=sk-ant-your-claude-key
OPENAI_API_KEY=sk-your-openai-key  # Fallback 1
GEMINI_API_KEY=your-gemini-key     # Fallback 2
```

## Intelligent Fallback Mechanism

The system uses the following priority order:

1. **Primary Provider** (from `LLM_PROVIDER` environment variable)
2. **Secondary Providers** (first available alternative)
3. **Hardcoded Fallback** (rule-based recommendations if all LLMs fail)

### Workflow

```
User uploads blood report
        ↓
Multi-Agent Orchestrator processes data
        ↓
LLM Recommendation Agent tries:
   1. Primary LLM Provider
   2. If fails → Try OpenAI
   3. If fails → Try Claude
   4. If fails → Try Gemini
   5. If all fail → Use hardcoded fallback
        ↓
Return recommendations to user
```

## API Response with Multi-LLM Info

When recommendations are generated, the response includes provider information:

```json
{
  "status": "success",
  "recommendations": [...],
  "agent_execution": {
    "agents": [
      {
        "name": "LLM Recommendation Agent",
        "status": "success",
        "execution_time": 2.34
      }
    ]
  },
  "llm_provider_info": {
    "primary": "OpenAI GPT",
    "available": ["OpenAI GPT", "Google Gemini", "Anthropic Claude"],
    "total_available": 3,
    "fallback_enabled": true
  }
}
```

## Installation & Requirements

### Base Requirements (Already Included)
```bash
pip install fastapi uvicorn google-generativeai
```

### Optional LLM Provider Libraries

**For OpenAI GPT:**
```bash
pip install openai
```

**For Anthropic Claude:**
```bash
pip install anthropic
```

**Install all (recommended):**
```bash
pip install openai anthropic
```

## Usage Examples

### Load Blood Report (Any Format)

```bash
# Automatically uses configured LLM providers
curl -X POST "http://localhost:10000/analyze-report/" \
  -H "X-API-Key: your-api-key" \
  -F "file=@blood_report.pdf"
```

### Specify Preferred LLM Provider

The system automatically selects based on your `.env` configuration. To override temporarily, you can modify the agent's behavior, or simply change `LLM_PROVIDER` in your `.env` file before restarting.

## Monitoring & Logging

Check logs to see which LLM provider is being used:

```
INFO | MultiLLMService: Found 3 available LLM providers
INFO | MultiLLMService: Primary LLM Provider: OpenAI GPT
INFO | LLMRecommendationAgent: Requesting recommendations from OpenAI GPT
INFO | LLMRecommendationAgent: Generated 10 LLM recommendations in 2.34s using OpenAI GPT
```

If primary fails:
```
WARNING | LLMRecommendationAgent: OpenAI request failed
INFO | LLMRecommendationAgent: Trying fallback LLM provider: Google Gemini
INFO | LLMRecommendationAgent: Generated 10 recommendations from Google Gemini in 1.50s
```

## Cost Comparison

| Provider | Model | Cost | Speed |
|----------|-------|------|-------|
| Gemini | gemini-1.5-flash | ~$0.075/M tokens | ⚡⚡⚡ |
| OpenAI | gpt-4 | ~$0.03/K tokens | ⚡⚡ |
| Claude | claude-3-opus | ~$0.015/K tokens | ⚡⚡⚡ |

*Prices as of Feb 2026 - check provider websites for current rates*

## Troubleshooting

### No LLM Providers Available
```
WARNING | MultiLLMService: No LLM providers available! Using fallback recommendations only.
```
**Solution**: Add at least one API key to your `.env` file

### Specific Provider Not Available
```
WARNING | GeminiLLMProvider: GEMINI_API_KEY not found in environment variables
```
**Solution**: Add the missing API key to `.env`

### Slow Responses
- Check which LLM is being used in logs
- Consider switching to faster provider (Gemini or Claude)
- Verify API rate limits haven't been exceeded

### Empty Recommendations
- All LLMs failed - check API keys and connectivity
- System will use hardcoded fallback
- Check logs for specific error messages

## Best Practices

1. **Always configure at least 2 providers** for redundancy
2. **Use Gemini as primary** for cost efficiency
3. **Add OpenAI or Claude as fallback** for reliability
4. **Monitor logs** to see which provider is being used
5. **Test configuration** before deploying to production
6. **Set appropriate rate limits** based on expected load

## Architecture

```
┌─────────────────────────────────────┐
│   API Request (PDF/CSV/JSON/Image)  │
└──────────────┬──────────────────────┘
               │
       ┌───────▼────────┐
       │ Format Detector │
       └───────┬────────┘
               │
    ┌──────────▼──────────┐
    │ Multi-Agent System  │
    └──────────┬──────────┘
               │
    ┌──────────▼─────────────────┐
    │ LLM Recommendation Agent   │
    └──────────┬─────────────────┘
               │
    ┌──────────▼──────────────────────┐
    │  Multi-LLM Service              │
    │  ┌────────────────────────────┐ │
    │  │ ✓ Primary (Gemini)         │ │
    │  │ ✓ Fallback 1 (OpenAI)      │ │
    │  │ ✓ Fallback 2 (Claude)      │ │
    │  └────────────────────────────┘ │
    └──────────┬──────────────────────┘
               │
    ┌──────────▼──────────────────┐
    │  Return Recommendations    │
    │  + Provider Info           │
    └─────────────────────────────┘
```

## Support

For issues or questions:
1. Check logs for error messages
2. Verify API keys are correct
3. Test provider connectivity independently
4. Check provider documentation
5. Open an issue on GitHub

---

**Multi-LLM System Ready!** Choose your favorite AI provider or use multiple for maximum reliability. 🚀
