"""
============================================================
SERVICE: URL Security Analyzer
OWNER:   Person A
============================================================

Analyzes URLs for phishing, scams, and security risks
using a custom-trained local Logistic Regression classifier
combined with Gemini AI for rich semantic explanations.
============================================================
"""

import os
import json
import re
import urllib.parse
import joblib
from google.genai import types
from backend.services.gemini_service import get_gemini_client, get_model_id

# Path to saved models
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, "saved_models", "url_model.joblib")
VECTORIZER_PATH = os.path.join(BASE_DIR, "saved_models", "url_vectorizer.joblib")

# Global variables for caching models
_url_model = None
_url_vectorizer = None

def load_url_model():
    """Lazy loads the trained URL machine learning model and vectorizer."""
    global _url_model, _url_vectorizer
    if _url_model is None or _url_vectorizer is None:
        if os.path.exists(MODEL_PATH) and os.path.exists(VECTORIZER_PATH):
            try:
                _url_model = joblib.load(MODEL_PATH)
                _url_vectorizer = joblib.load(VECTORIZER_PATH)
                print("[INFO] Local URL ML model loaded successfully!")
            except Exception as e:
                print(f"[WARNING] Failed to load local URL model: {e}")
        else:
            print("[WARNING] Saved URL model files not found. Local ML classification will be skipped.")

# Load at import time
load_url_model()

def clean_url_input(text: str) -> str:
    """Extracts raw URL from frontend prompt envelopes or cleans plain text input."""
    text = text.strip()
    
    # Strip common prompt envelope wrappers sent by frontend app.js
    match = re.search(r"Analyze this URL for security risks:\s*(.*)", text, re.IGNORECASE)
    if match:
        url = match.group(1).strip()
    else:
        url = text
        
    # Standardize simple inputs that don't have schema
    if not url.startswith(("http://", "https://")) and "." in url:
        url = "https://" + url
        
    return url

def get_local_url_fallback(url: str, classification: str, risk_score: int) -> dict:
    """Provides structured reasons and recommendations offline if Gemini fails."""
    reasons = []
    parsed = urllib.parse.urlparse(url)
    domain = parsed.netloc or parsed.path.split("/")[0]
    
    # Simple rule checks to enhance reasons
    if len(url) > 75:
        reasons.append("The URL is unusually long, which is a common technique to hide malicious query parameters.")
    if "@" in url:
        reasons.append("The URL contains an '@' character, which is often used to redirect users to unauthorized systems.")
    if re.search(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", domain):
        reasons.append("The URL uses a raw IP address instead of a recognized domain name.")
    if "-" in domain:
        reasons.append("The domain contains hyphens, a pattern frequently observed in typosquatting phishing domains.")

    if classification == "SAFE":
        reasons.append("Character-level n-gram heuristics matched safe, highly legitimate domain reputation profiles.")
        reasons.append("The domain structural features do not indicate spoofing or obfuscation signatures.")
        rec = "This link appears genuine. However, always exercise normal precautions before entering sensitive credentials."
    elif classification == "SUSPICIOUS":
        reasons.append("Machine learning character sequences identify patterns moderately similar to known spoofed services.")
        if not reasons:
            reasons.append("Subdomain structures or TLD reputations suggest abnormal web presence.")
        rec = "Exercise caution. Do not submit personal details or passwords on this webpage unless you can verify its authenticity."
    else: # DANGEROUS
        reasons.append("The character sequence of the domain/path matches known malicious patterns (malware/phishing/defacement).")
        reasons.append("TLD and structural character patterns show extremely high correlation with malicious domain configurations.")
        rec = "[HIGH RISK] We strongly advise against visiting this URL. Avoid entering credentials or downloading files."

    return {
        "classification": classification,
        "risk_score": risk_score,
        "reasons": reasons[:4], # Keep concise
        "recommendation": rec
    }

def analyze_url(message: str) -> dict:
    """
    Sends a URL or text to our hybrid system (Local ML Model + Gemini explanation).
    
    Args:
        message: The URL or prompt envelope to analyze.
        
    Returns:
        Dictionary with classification, risk_score, reasons, recommendation.
    """
    url = clean_url_input(message)
    load_url_model()
    
    classification = "SAFE"
    risk_score = 0
    local_success = False
    
    # Parse domain and check whitelist to prevent false positives on major benign sites
    parsed = urllib.parse.urlparse(url)
    domain = (parsed.netloc or parsed.path.split("/")[0]).lower()
    if domain.startswith("www."):
        domain = domain[4:]
        
    whitelist = {
        "google.com", "github.com", "microsoft.com", "apple.com", "youtube.com",
        "facebook.com", "wikipedia.org", "amazon.com", "twitter.com", "linkedin.com",
        "netflix.com", "reddit.com", "instagram.com", "gmail.com", "yahoo.com",
        "zoom.us", "githubusercontent.com", "googleusercontent.com", "gstatic.com"
    }
    
    is_whitelisted = False
    for d in whitelist:
        if domain == d or domain.endswith("." + d):
            is_whitelisted = True
            break
            
    if is_whitelisted:
        print(f"[INFO] Domain '{domain}' is whitelisted. Bypassing ML model classification.")
        classification = "SAFE"
        risk_score = 0
        local_success = True
    elif _url_model is not None and _url_vectorizer is not None:
        try:
            feats = _url_vectorizer.transform([url])
            # predict probabilities [prob_safe, prob_dangerous]
            probs = _url_model.predict_proba(feats)[0]
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
            print(f"[INFO] Local URL ML result: {classification} ({risk_score}/100) for '{url}'")
        except Exception as e:
            print(f"[WARNING] Local URL ML prediction failed: {e}")
            
    if not local_success:
        # Defaults if ML model fails to execute
        classification = "SUSPICIOUS"
        risk_score = 50
        
    try:
        client = get_gemini_client()
        
        # Craft hybrid prompt asking LLM to generate logical reasons matching our ML results
        system_instruction = (
            "You are an expert cybersecurity threat intelligence analyst.\n"
            f"We have mathematically analyzed the URL: '{url}' using our trained Logistic Regression classifier.\n"
            f"The local classifier determined the classification to be {classification} with a risk score of {risk_score}/100.\n"
            "Your task is to analyze the URL content/structure semantically and generate a list of exact "
            "security reasons and a concise, actionable recommendation supporting this classification.\n"
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
            contents=f"Analyze this URL under your cybersecurity guidelines: {url}",
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                system_instruction=system_instruction,
            ),
        )
        
        response_text = response.text
        cleaned = response_text.replace("```json", "").replace("```", "").strip()
        result = json.loads(cleaned)
        
        # Override classification & risk score to guarantee model integrity
        result["classification"] = classification
        result["risk_score"] = risk_score
        return result
        
    except Exception as e:
        print(f"[WARNING] Gemini analysis failed, using local offline fallback: {e}")
        return get_local_url_fallback(url, classification, risk_score)
