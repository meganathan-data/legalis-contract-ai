import json
import google.generativeai as genai

SYSTEM_PROMPT = """
You are Legalis, a lawyer for Indian SMEs. Analyze contracts for:
1. Jurisdiction (prefer local).
2. Termination (avoid unilateral).
3. Indemnity (avoid unlimited).
4. Non-Compete (check validity).
Output strictly Valid JSON.
JSON Structure:
{
    "contract_type": "string",
    "overall_risk_score": 0-100,
    "summary": "string",
    "clauses": [{"risk": "High/Medium/Low", "topic": "string", "excerpt": "string", "explanation": "string", "recommendation": "string"}]
}
"""

def get_best_model(api_key):
    """
    Finds the exact model name for Flash to avoid 404s.
    """
    genai.configure(api_key=api_key)
    try:
        # Get all models available to your key
        all_models = list(genai.list_models())
        
        # Priority 1: Find a "Flash" model (Best Free Tier)
        for m in all_models:
            if 'flash' in m.name.lower() and 'generateContent' in m.supported_generation_methods:
                return m.name # Returns exact name like 'models/gemini-1.5-flash-001'
        
        # Priority 2: Find standard "Gemini Pro"
        for m in all_models:
            if 'gemini-pro' in m.name.lower() and 'generateContent' in m.supported_generation_methods:
                return m.name
                
        # Priority 3: Anything that generates text
        for m in all_models:
            if 'generateContent' in m.supported_generation_methods:
                return m.name
                
    except Exception as e:
        print(f"Error listing models: {e}")
    
    # Absolute fallback if listing fails
    return 'models/gemini-1.5-flash'

def analyze_agreement(text, api_key):
    try:
        # Dynamic Model Selection
        model_name = get_best_model(api_key)
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(model_name)
        
        response = model.generate_content(
            f"{SYSTEM_PROMPT}\n\nHere is the contract text:\n{text}",
            generation_config={"response_mime_type": "application/json"}
        )
        
        return json.loads(response.text)
        
    except Exception as e:
        return {"error": f"AI Error: {str(e)}"}

def create_template_draft(ctype, details, api_key):
    try:
        model_name = get_best_model(api_key)
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(model_name)
        
        response = model.generate_content(
            f"Draft a valid Indian legal contract: {ctype}. Include these details: {details}."
        )
        return response.text
    except Exception as e:
        return f"Error drafting: {str(e)}"