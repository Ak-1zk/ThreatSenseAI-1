"""
============================================================
SERVICE: Email & Message Threat Detector
OWNER:   Person B
============================================================

Detects phishing emails and SMS scam messages ("smishing")
using a custom-trained local Multinomial Naive Bayes classifier
combined with Gemini AI for rich semantic explanations.
============================================================
"""

import os
import json
import re
import joblib
from google.genai import types
from backend.services.gemini_service import get_gemini_client, get_model_id

# Path to saved models
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, "saved_models", "message_model.joblib")
VECTORIZER_PATH = os.path.join(BASE_DIR, "saved_models", "message_vectorizer.joblib")

# Global variables for caching models
_msg_model = None
_msg_vectorizer = None

def load_message_model():
    """Lazy loads the trained Message machine learning model and vectorizer."""
    global _msg_model, _msg_vectorizer
    if _msg_model is None or _msg_vectorizer is None:
        if os.path.exists(MODEL_PATH) and os.path.exists(VECTORIZER_PATH):
            try:
                _msg_model = joblib.load(MODEL_PATH)
                _msg_vectorizer = joblib.load(VECTORIZER_PATH)
                print("[INFO] Local Message ML model loaded successfully!")
            except Exception as e:
                print(f"[WARNING] Failed to load local Message model: {e}")
        else:
            print("[WARNING] Saved Message model files not found. Local ML classification will be skipped.")

# Load at import time
load_message_model()

def clean_threat_input(text: str, threat_type: str) -> str:
    """Extracts raw threat payload from frontend prompt envelopes."""
    text = text.strip()
    if threat_type == "email":
        match = re.search(r"Analyze this email for phishing or scam indicators:\s*([\s\S]*)", text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    elif threat_type == "message":
        match = re.search(r"Analyze this message for smishing or phishing indicators:\s*([\s\S]*)", text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    return text

def get_local_threat_fallback(content: str, threat_type: str, classification: str, risk_score: int) -> dict:
    """Provides structured reasons and recommendations offline if Gemini fails."""
    reasons = []
    
    # Common phishing indicators inside the content text
    content_lower = content.lower()
    if any(word in content_lower for word in ["urgent", "immediately", "action required", "expir", "suspend", "lock"]):
        reasons.append("High-urgency language detected (creates artificial panic).")
    if any(word in content_lower for word in ["verify", "update details", "log in to", "reset", "credentials"]):
        reasons.append("Requests verification of sensitive credentials or account info.")
    if any(word in content_lower for word in ["winner", "prize", "cash", "awarded", "gift card", "claim"]):
        reasons.append("Scam alert: Offers an unsolicited reward, prize, or lottery payout.")
    if any(word in content_lower for word in ["http", "https", "link", "click"]):
        reasons.append("Contains hypermedia links urging immediate user interaction.")

    if classification == "SAFE":
        reasons.append(f"Naive Bayes text heuristics classify this {threat_type} as clean and non-phishing.")
        reasons.append("The vocabulary matches common conversational or business semantics without high-risk spam indicators.")
        rec = f"This {threat_type} appears to be legitimate. Continue with normal communication safety."
    elif classification == "SUSPICIOUS":
        reasons.append("The vocabulary shows unusual features or semantic constructs mimicking standard marketing spam.")
        if not reasons:
            reasons.append("Semantic analysis detects slight social engineering triggers.")
        rec = f"Exercise caution. Do not click links or respond to this {threat_type} unless you can independently verify the sender."
    else: # DANGEROUS
        reasons.append(f"Highly correlated with known phishing, smishing, or malicious spam dataset signatures.")
        if not reasons:
            reasons.append("The language strongly matches standard social engineering templates (urgency, credential harvesting, fake alerts).")
        rec = f"[HIGH RISK SCAM] Do not reply, click any embedded links, or disclose personal details. Mark as spam and delete."

    return {
        "classification": classification,
        "risk_score": risk_score,
        "reasons": reasons[:4],
        "recommendation": rec
    }

def analyze_email(content: str) -> dict:
    """Analyzes email content for phishing indicators."""
    return _analyze(content, "email")

def analyze_message(content: str) -> dict:
    """Analyzes SMS/chat messages for smishing indicators."""
    return _analyze(content, "message")

def _analyze(content: str, threat_type: str) -> dict:
    """Shared hybrid analysis logic for both email and message threats."""
    payload = clean_threat_input(content, threat_type)
    load_message_model()
    
    classification = "SAFE"
    risk_score = 0
    local_success = False
    
    if _msg_model is not None and _msg_vectorizer is not None:
        try:
            feats = _msg_vectorizer.transform([payload])
            # get prediction probability
            probs = _msg_model.predict_proba(feats)[0] # [prob_safe, prob_dangerous]
            danger_prob = probs[1]
            risk_score = int(danger_prob * 100)
            
            # Map risk score to classification tags
            if risk_score < 40:
                classification = "SAFE"
            elif risk_score < 75:
                classification = "SUSPICIOUS"
            else:
                classification = "DANGEROUS"
                
            local_success = True
            print(f"[INFO] Local Message ML result: {classification} ({risk_score}/100) for {threat_type}")
        except Exception as e:
            print(f"[WARNING] Local Message ML prediction failed: {e}")
            
    if not local_success:
        classification = "SUSPICIOUS"
        risk_score = 50
        
    try:
        client = get_gemini_client()
        
        # System instructions specializing in either smishing or email phishing
        if threat_type == "email":
            expert_role = "specializing in email phishing detection."
            threat_name = "email"
        else:
            expert_role = "specializing in smishing (SMS phishing) and mobile scam detection."
            threat_name = "SMS message"
            
        system_instruction = (
            f"You are a cybersecurity expert {expert_role}\n"
            f"We have mathematically analyzed the following {threat_name} using our trained Naive Bayes classifier:\n"
            f"--- START CONTENT ---\n{payload}\n--- END CONTENT ---\n"
            f"The local classifier determined the classification to be {classification} with a risk score of {risk_score}/100.\n"
            "Your task is to analyze the text semantically and generate a list of exact security reasons "
            "and a concise, actionable recommendation supporting this classification.\n"
            "Return ONLY a valid JSON object (no markdown, no notes) in this format:\n"
            "{\n"
            f'  "classification": "{classification}",\n'
            f'  "risk_score": {risk_score},\n'
            '  "reasons": ["reason 1", "reason 2", "reason 3"],\n'
            '  "recommendation": "string"\n'
            "}"
        )
        
        response = client.models.generate_content(
            model=get_model_id(),
            contents=f"Analyze this {threat_name} under your cybersecurity guidelines: {payload}",
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                system_instruction=system_instruction,
            ),
        )
        
        response_text = response.text or ""
        if not response_text and response.candidates:
            for part in response.candidates[0].content.parts:
                if hasattr(part, 'text') and part.text:
                    response_text = part.text
                    break
        cleaned = response_text.replace("```json", "").replace("```", "").strip()
        result = json.loads(cleaned)
        
        # Override classification & risk score to guarantee model integrity
        result["classification"] = classification
        result["risk_score"] = risk_score
        return result
        
    except Exception as e:
        print(f"[WARNING] Gemini analysis for {threat_type} failed, using local offline fallback: {e}")
        return get_local_threat_fallback(payload, threat_type, classification, risk_score)
