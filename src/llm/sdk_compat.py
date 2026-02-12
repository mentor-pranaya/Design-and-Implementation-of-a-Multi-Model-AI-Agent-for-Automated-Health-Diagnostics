"""Compatibility layer to call LLM SDKs safely across different library versions."""
from typing import List, Dict, Any, Optional

def openai_chat_completion(api_key: str, model: str, messages: List[Dict[str, str]], max_tokens: int = 2048, temperature: float = 0.7) -> Optional[str]:
    try:
        import openai
        openai.api_key = api_key
        # Try legacy ChatCompletion
        try:
            resp = openai.ChatCompletion.create(model=model, messages=messages, temperature=temperature, max_tokens=max_tokens)
            return _extract_openai_text(resp)
        except Exception:
            # Try new OpenAI client wrapper
            try:
                from openai import OpenAI
                client = OpenAI(api_key=api_key)
                resp = client.chat.completions.create(model=model, messages=messages, temperature=temperature, max_tokens=max_tokens)
                return _extract_openai_text(resp)
            except Exception:
                return None
    except ImportError:
        return None

def _extract_openai_text(resp: Any) -> Optional[str]:
    try:
        # support different response shapes
        if hasattr(resp, 'choices'):
            choice = resp.choices[0]
            if hasattr(choice, 'message') and hasattr(choice.message, 'content'):
                return choice.message.content
            if isinstance(choice, dict) and 'message' in choice and 'content' in choice['message']:
                return choice['message']['content']
        if isinstance(resp, dict):
            return resp.get('choices', [])[0].get('message', {}).get('content')
    except Exception:
        return None
    return None


def anthropic_completion(api_key: str, model: str, prompt: str, max_tokens: int = 2048) -> Optional[str]:
    try:
        import anthropic
        # Try new client pattern
        try:
            client = anthropic.Client(api_key=api_key)
            resp = client.completions.create(model=model, prompt=prompt, max_tokens_to_sample=max_tokens)
            # resp may be dict-like
            if hasattr(resp, 'completion'):
                return resp.completion
            if isinstance(resp, dict):
                return resp.get('completion') or resp.get('text')
        except Exception:
            # Try older name
            try:
                client = anthropic.Anthropic(api_key=api_key)
                resp = client.completions.create(model=model, prompt=prompt, max_tokens_to_sample=max_tokens)
                if isinstance(resp, dict):
                    return resp.get('completion') or resp.get('text')
            except Exception:
                return None
    except ImportError:
        return None
    return None


def genai_generate(api_key: str, model: str, prompt: str, max_tokens: int = 2048) -> Optional[str]:
    try:
        import google.generativeai as genai
        
        # Ensure API key is set
        if not api_key:
            return None
            
        genai.configure(api_key=api_key)
        
        # Clean model name (remove models/ prefix if present)
        clean_model = model.split('/')[-1] if '/' in model else model
        
        # Use GenerativeModel API (current standard approach)
        try:
            model_obj = genai.GenerativeModel(clean_model)
            resp = model_obj.generate_content(prompt)
            if resp and hasattr(resp, 'text'):
                return resp.text
            
            # Fallback if text attribute is missing but result exists
            if hasattr(resp, 'candidates') and resp.candidates:
                return resp.candidates[0].content.parts[0].text
        except Exception as e:
            # Log the error for debugging
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Gemini API generation error ({clean_model}): {str(e)}")
            
            # Try fallback with deprecated generate_text (for older SDK versions)
            try:
                resp = genai.generate_text(model=clean_model, prompt=prompt, max_output_tokens=max_tokens)
                if isinstance(resp, dict):
                    return resp.get('candidates', [])[0].get('output', None) if resp.get('candidates') else None
                if hasattr(resp, 'text'):
                    return resp.text
            except Exception:
                return None
    except ImportError:
        return None
    return None
