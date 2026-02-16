import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional
from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
# from fastapi.middleware.gzip import GZIPMiddleware  # Commented out due to import error

from src.agent.intent_inference_agent import IntentInferenceAgent, ConversationContext
from src.agent.agent_orchestrator import MultiAgentOrchestrator

logger = logging.getLogger(__name__)
app = FastAPI(title="Blood Report AI", version="1.0.0")

# Initialize agents
intent_agent = IntentInferenceAgent()
orchestrator = MultiAgentOrchestrator()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# app.add_middleware(GZIPMiddleware, minimum_size=1000)  # Commented out due to import error

ALLOWED = {'.pdf', '.png', '.jpg', '.jpeg', '.tiff', '.tif', '.bmp', '.csv', '.json', '.txt'}
MAX_SIZE = 50 * 1024 * 1024

@app.get("/")
async def root():
    return {
        "service": "Blood Report AI",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "/health": "health check",
            "/api/upload": "file upload",
            "/docs": "api documentation"
        }
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "Blood Report AI",
        "time": str(datetime.now())
    }

@app.post("/api/upload")
async def upload(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(400, "No filename")
    
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED:
        raise HTTPException(400, f"Format not allowed")
    
    content = await file.read()
    if len(content) == 0:
        raise HTTPException(400, "Empty file")
    
    Path("data/uploads").mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    fname = f"{ts}_{file.filename}"
    fpath = Path("data/uploads") / fname
    
    fpath.write_bytes(content)
    logger.info(f"Uploaded: {fname}")
    
    return {
        "status": "success",
        "file": fname,
        "type": ext,
        "size_mb": round(len(content) / 1024 / 1024, 2)
    }

@app.get("/api/formats")
async def formats():
    return {
        "formats": sorted(list(ALLOWED)),
        "total": len(ALLOWED)
    }

@app.get("/api/stats")
async def stats():
    d = Path("data/uploads")
    files = list(d.glob("*")) if d.exists() else []
    size = sum(f.stat().st_size for f in files if f.is_file())
    return {
        "total_files": len(files),
        "total_mb": round(size / 1024 / 1024, 2)
    }


class ChatRequest(BaseModel):
    user_input: str
    conversation_context: Optional[Dict[str, Any]] = None


class ChatResponse(BaseModel):
    intent_result: Dict[str, Any]
    requires_clarification: bool
    clarifying_questions: List[str]
    response_message: str
    conversation_context: Dict[str, Any]


@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Conversational endpoint for natural language interaction.
    Analyzes user intent and provides appropriate responses.
    """
    try:
        # Convert conversation context to ConversationContext object
        conversation_context = None
        if request.conversation_context:
            conversation_context = ConversationContext(
                user_id=request.conversation_context.get("user_id"),
                conversation_history=request.conversation_context.get("conversation_history", []),
                user_profile=request.conversation_context.get("user_profile"),
                last_interaction=request.conversation_context.get("last_interaction")
            )

        # Analyze intent
        intent_result = await intent_agent.analyze_intent(
            request.user_input,
            conversation_context
        )

        # Update conversation context
        if conversation_context:
            conversation_context = intent_agent.update_conversation_context(
                conversation_context,
                request.user_input,
                intent_result
            )

        # Generate response message based on intent
        response_message = _generate_response_message(intent_result)

        return ChatResponse(
            intent_result={
                "inferred_intent": intent_result.inferred_intent,
                "confidence_score": intent_result.confidence_score,
                "assumptions_made": intent_result.assumptions_made,
                "context_summary": intent_result.context_summary
            },
            requires_clarification=intent_result.requires_clarification,
            clarifying_questions=intent_result.clarifying_questions,
            response_message=response_message,
            conversation_context={
                "user_id": conversation_context.user_id if conversation_context else None,
                "conversation_history": conversation_context.conversation_history if conversation_context else [],
                "user_profile": conversation_context.user_profile if conversation_context else None,
                "last_interaction": conversation_context.last_interaction.isoformat() if conversation_context and conversation_context.last_interaction else None
            }
        )

    except Exception as e:
        logger.error(f"Chat endpoint error: {str(e)}")
        raise HTTPException(500, f"Chat processing failed: {str(e)}")


@app.post("/api/chat_analyze")
async def chat_analyze_endpoint(
    user_input: str = Form(...),
    file: Optional[UploadFile] = File(None),
    conversation_context: Optional[str] = Form(None)
):
    """
    Combined chat and analysis endpoint.
    Handles both conversational input and file uploads for blood report analysis.
    """
    try:
        # Parse conversation context
        context_dict = None
        if conversation_context:
            try:
                context_dict = json.loads(conversation_context)
            except json.JSONDecodeError:
                context_dict = None

        conversation_ctx = None
        if context_dict:
            conversation_ctx = ConversationContext(
                user_id=context_dict.get("user_id"),
                conversation_history=context_dict.get("conversation_history", []),
                user_profile=context_dict.get("user_profile"),
                last_interaction=context_dict.get("last_interaction")
            )

        # Analyze intent first
        intent_result = await intent_agent.analyze_intent(user_input, conversation_ctx)

        # Prepare parameters for analysis if intent requires it
        params_to_analyze = None
        if intent_result.inferred_intent == "analyze_blood_report":
            if file:
                # Save uploaded file and extract parameters
                content = await file.read()
                if len(content) > MAX_SIZE:
                    raise HTTPException(400, f"File too large (max {MAX_SIZE//1024//1024}MB)")

                ext = Path(file.filename).suffix.lower()
                if ext not in ALLOWED:
                    raise HTTPException(400, f"Format not allowed: {ext}")

                # Save file
                Path("data/uploads").mkdir(parents=True, exist_ok=True)
                ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                fname = f"{ts}_{file.filename}"
                fpath = Path("data/uploads") / fname
                fpath.write_bytes(content)

                # Extract parameters from file (simplified - would need full extraction logic)
                # For now, return file info
                params_to_analyze = {"file_uploaded": fname, "file_type": ext}
            else:
                # No file provided, might need clarification
                if not intent_result.requires_clarification:
                    intent_result.requires_clarification = True
                    intent_result.clarifying_questions.append("Please upload your blood report file for analysis.")

        # Run analysis if we have parameters and intent requires it
        analysis_result = None
        if params_to_analyze and intent_result.inferred_intent == "analyze_blood_report":
            try:
                analysis_result = await orchestrator.execute_with_intent(
                    user_input=user_input,
                    raw_params=params_to_analyze,
                    conversation_context=conversation_ctx
                )
            except Exception as analysis_error:
                logger.error(f"Analysis failed: {str(analysis_error)}")
                analysis_result = {"error": f"Analysis failed: {str(analysis_error)}"}

        # Update conversation context
        if conversation_ctx:
            conversation_ctx = intent_agent.update_conversation_context(
                conversation_ctx,
                user_input,
                intent_result
            )

        # Generate comprehensive response
        response_data = {
            "intent_analysis": {
                "inferred_intent": intent_result.inferred_intent,
                "confidence_score": intent_result.confidence_score,
                "requires_clarification": intent_result.requires_clarification,
                "clarifying_questions": intent_result.clarifying_questions,
                "assumptions_made": intent_result.assumptions_made,
                "context_summary": intent_result.context_summary
            },
            "response_message": _generate_response_message(intent_result),
            "analysis_result": analysis_result,
            "conversation_context": {
                "user_id": conversation_ctx.user_id if conversation_ctx else None,
                "conversation_history": conversation_ctx.conversation_history if conversation_ctx else [],
                "user_profile": conversation_ctx.user_profile if conversation_ctx else None,
                "last_interaction": conversation_ctx.last_interaction.isoformat() if conversation_ctx and conversation_ctx.last_interaction else None
            }
        }

        if file:
            response_data["file_info"] = {
                "filename": file.filename,
                "size_mb": round(len(content) / 1024 / 1024, 2),
                "type": ext
            }

        return response_data

    except Exception as e:
        logger.error(f"Chat analyze endpoint error: {str(e)}")
        raise HTTPException(500, f"Chat analysis failed: {str(e)}")


def _generate_response_message(intent_result: IntentResult) -> str:
    """Generate a user-friendly response message based on intent analysis."""
    intent = intent_result.inferred_intent

    if intent_result.requires_clarification:
        base_message = "I'd like to help you better. "
        if intent_result.clarifying_questions:
            base_message += f"{intent_result.clarifying_questions[0]}"
        else:
            base_message += "Could you provide more details?"
        return base_message

    # Intent-specific response messages
    intent_messages = {
        "analyze_blood_report": "I understand you want to analyze a blood report. Please upload your file and I'll provide a comprehensive analysis.",
        "ask_health_question": "I'm here to help with your health question. Let me provide some information based on what you've asked.",
        "request_recommendations": "I'd be happy to provide health recommendations. Let me give you some personalized advice.",
        "follow_up_previous_analysis": "I see you're following up on a previous analysis. Let me help you with that.",
        "clarify_previous_response": "I want to make sure I understand correctly. Let me clarify my previous response.",
        "general_health_inquiry": "I'm here to help with general health information. What would you like to know?",
        "emergency_concern": "This sounds like it might be urgent. While I can provide information, please consult a healthcare professional for immediate concerns.",
        "lifestyle_advice": "I'd be glad to provide lifestyle and wellness advice. Here are some recommendations."
    }

    return intent_messages.get(intent, "I'm here to help with your health-related questions. How can I assist you today?")

@app.exception_handler(Exception)
async def error_handler(request, exc):
    logger.error(f"Error: {exc}")
    return JSONResponse({"error": str(exc)}, 500)
