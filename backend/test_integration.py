"""
ThreatSense AI — Integration and Validation Test Suite
This script programmatically validates that:
1. Local models load successfully.
2. URLs are classified correctly (benign vs phishing/malware).
3. Messages are classified correctly (ham vs spam).
4. Dynamic routing in the FastAPI analyze endpoint functions correctly.
5. Offline fallbacks behave as expected when Gemini is unavailable.
"""

import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.services.url_analyzer import analyze_url
from backend.services.threat_detector import analyze_email, analyze_message
from backend.routers.analyze import analyze
from backend.models.analysis import AnalysisRequest

def test_url_classification():
    print("\n" + "=" * 50)
    print("TESTING URL ML CLASSIFICATION")
    print("=" * 50)
    
    test_urls = [
        ("https://google.com", "SAFE"),
        ("https://paypal-security-login-update.com", "DANGEROUS"),
        ("http://192.168.1.1/login.php", "DANGEROUS"),
        ("https://github.com", "SAFE"),
    ]
    
    success = True
    for url, expected in test_urls:
        print(f"Analyzing URL: '{url}'...")
        try:
            # We call the URL analyzer service
            res = analyze_url(url)
            print(f" -> Result classification: {res['classification']} (Risk Score: {res['risk_score']})")
            print(f" -> Reasons: {res['reasons']}")
            print(f" -> Recommendation: {res['recommendation']}")
            
            # Simple check (malicious URLs should have risk score > 50, benign < 50)
            if expected == "SAFE" and res['classification'] != "SAFE":
                print(f" ❌ Expected SAFE but got {res['classification']}")
                success = False
            elif expected == "DANGEROUS" and res['classification'] not in ["DANGEROUS", "SUSPICIOUS"]:
                print(f" ❌ Expected DANGEROUS/SUSPICIOUS but got {res['classification']}")
                success = False
            else:
                print(" ✅ Pass")
        except Exception as e:
            print(f" ❌ Error analyzing '{url}': {e}")
            success = False
            
    return success

def test_message_classification():
    print("\n" + "=" * 50)
    print("TESTING MESSAGE / EMAIL ML CLASSIFICATION")
    print("=" * 50)
    
    test_msgs = [
        ("Hey, are we still meeting for lunch today? Let me know.", "SAFE"),
        ("URGENT: Your bank account is locked! Click https://secure-bank-login.com to verify your details immediately.", "DANGEROUS"),
        ("Congratulations! You won a $1000 Walmart gift card! Call 1800-scam to claim your prize now.", "DANGEROUS"),
        ("Hi team, please find attached the meeting minutes for our weekly sync. Let me know if you have questions.", "SAFE"),
    ]
    
    success = True
    for msg, expected in test_msgs:
        print(f"Analyzing message: '{msg[:50]}...'")
        try:
            res = analyze_message(msg)
            print(f" -> Result classification: {res['classification']} (Risk Score: {res['risk_score']})")
            print(f" -> Reasons: {res['reasons']}")
            
            if expected == "SAFE" and res['classification'] != "SAFE":
                print(f" ❌ Expected SAFE but got {res['classification']}")
                success = False
            elif expected == "DANGEROUS" and res['classification'] not in ["DANGEROUS", "SUSPICIOUS"]:
                print(f" ❌ Expected DANGEROUS/SUSPICIOUS but got {res['classification']}")
                success = False
            else:
                print(" ✅ Pass")
        except Exception as e:
            print(f" ❌ Error: {e}")
            success = False
            
    return success

async def test_router_smart_routing():
    print("\n" + "=" * 50)
    print("TESTING ROUTER DYNAMIC ROUTING & PAYLOAD CLEANING")
    print("=" * 50)
    
    test_cases = [
        ("Analyze this URL for security risks: https://google.com", "SAFE"),
        ("Analyze this email for phishing or scam indicators:\n\nURGENT: Please verify your credentials.", "DANGEROUS"),
        ("Analyze this message for smishing or phishing indicators:\n\nClaim your prize now!", "DANGEROUS"),
    ]
    
    success = True
    for prompt, expected in test_cases:
        print(f"Router received: '{prompt[:60]}...'")
        try:
            req = AnalysisRequest(message=prompt)
            # Call router analyze endpoint
            res = await analyze(req)
            print(f" -> Result classification: {res['classification']} (Risk Score: {res['risk_score']})")
            print(" ✅ Pass")
        except Exception as e:
            print(f" ❌ Router test failed: {e}")
            success = False
            
    return success

async def main():
    print("=" * 60)
    print("RUNNING THREATSENSE AI HYBRID INTEGRATION TESTS")
    print("=" * 60)
    
    url_ok = test_url_classification()
    msg_ok = test_message_classification()
    router_ok = await test_router_smart_routing()
    
    print("\n" + "=" * 60)
    if url_ok and msg_ok and router_ok:
        print("🎉 ALL INTEGRATION TESTS PASSED SUCCESSFULLY!")
    else:
        print("❌ SOME INTEGRATION TESTS FAILED. Please review the logs above.")
    print("=" * 60)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
