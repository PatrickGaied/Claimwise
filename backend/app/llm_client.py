# Simplified LLM client for Claimwise
import os
from dotenv import load_dotenv
import requests
import json
from typing import Dict, Any

# Load environment variables
load_dotenv()

GROQ_URL = os.getenv("GROQ_API_URL")
GROQ_KEY = os.getenv("GROQ_API_KEY")
CEREBRAS_URL = os.getenv("CEREBRAS_API_URL")
CEREBRAS_KEY = os.getenv("CEREBRAS_API_KEY")
USE_MOCK = os.getenv("USE_MOCK_LLM", "false").lower() == "true"

def call_llm(prompt: str, system_prompt: str = None, max_tokens: int = 512, temperature: float = 0.0) -> Dict[str, Any]:
    """Main LLM call function - supports Groq and Cerebras"""
    print(f"DEBUG: call_llm called with USE_MOCK={USE_MOCK}")
    
    # Mock mode for testing
    if USE_MOCK:
        return {"text": "Mock response for testing"}
    
    # Try Cerebras first if available
    if CEREBRAS_URL and CEREBRAS_KEY:
        try:
            return call_cerebras(prompt, system_prompt, max_tokens, temperature)
        except Exception as e:
            print(f"DEBUG: Cerebras failed, trying Groq fallback: {e}")
    
    # Fallback to Groq
    if GROQ_URL and GROQ_KEY:
        return call_groq(prompt, system_prompt, max_tokens, temperature)
    
    raise RuntimeError("No working API key found. Set CEREBRAS_API_KEY or GROQ_API_KEY in .env file.")

def call_cerebras(prompt: str, system_prompt: str = None, max_tokens: int = 512, temperature: float = 0.0) -> Dict[str, Any]:
    """Cerebras API call"""
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})
    
    payload = {
        "model": "llama3.1-8b",
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
    }
    
    api_key = CEREBRAS_KEY.strip('"')
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    print(f"DEBUG: Cerebras API call with model: llama3.1-8b")
    print(f"DEBUG: Payload: {json.dumps(payload, indent=2)}")
    
    try:
        resp = requests.post(CEREBRAS_URL, headers=headers, json=payload, timeout=30)
        
        print(f"DEBUG: Cerebras API response status: {resp.status_code}")
        print(f"DEBUG: Cerebras API response: {resp.text}")
        
        if resp.status_code != 200:
            raise RuntimeError(f"Cerebras API failed with status {resp.status_code}: {resp.text}")
        
        j = resp.json()
        return {"text": j["choices"][0]["message"]["content"]}
        
    except requests.exceptions.RequestException as e:
        print(f"DEBUG: Cerebras API request failed: {e}")
        raise RuntimeError(f"Cerebras API call failed: {e}")

def call_groq(prompt: str, system_prompt: str = None, max_tokens: int = 512, temperature: float = 0.0) -> Dict[str, Any]:
    """Groq API call"""
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})
    
    payload = {
        "model": "llama-3.1-8b-instant",
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
    }
    
    api_key = GROQ_KEY.strip('"')
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    print(f"DEBUG: Groq API call with model: llama-3.1-8b-instant")
    print(f"DEBUG: Payload: {json.dumps(payload, indent=2)}")
    
    try:
        resp = requests.post(GROQ_URL, headers=headers, json=payload, timeout=30)
        
        print(f"DEBUG: Groq API response status: {resp.status_code}")
        print(f"DEBUG: Groq API response: {resp.text}")
        
        if resp.status_code != 200:
            raise RuntimeError(f"Groq API failed with status {resp.status_code}: {resp.text}")
        
        j = resp.json()
        return {"text": j["choices"][0]["message"]["content"]}
        
    except requests.exceptions.RequestException as e:
        print(f"DEBUG: Groq API request failed: {e}")
        raise RuntimeError(f"Groq API call failed: {e}")
