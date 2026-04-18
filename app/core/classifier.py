import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

URGENCY_LEVELS = {
    "CRITICAL": {"color": "#FF3B3B", "icon": "🔴", "sla": "1 hour"},
    "HIGH":     {"color": "#FF8C00", "icon": "🟠", "sla": "4 hours"},
    "MEDIUM":   {"color": "#FFD700", "icon": "🟡", "sla": "24 hours"},
    "LOW":      {"color": "#00C851", "icon": "🟢", "sla": "72 hours"},
}

INTENT_TYPES = [
    "PAYMENT_DISPUTE",
    "FRAUD_ALERT",
    "INVOICE_QUERY",
    "ACCOUNT_CLOSURE",
    "COMPLIANCE_REQUEST",
    "REFUND_REQUEST",
    "CREDIT_APPLICATION",
    "GENERAL_INQUIRY",
]

def classify_message(text: str) -> dict:
    prompt = f"""You are a senior finance operations analyst. Analyze this incoming finance communication and classify it.

MESSAGE:
\"\"\"{text}\"\"\"

Respond ONLY with valid JSON (no markdown, no extra text):
{{
  "urgency": "CRITICAL",
  "intent": "FRAUD_ALERT",
  "confidence": 0.95,
  "reasoning": "brief 1-sentence explanation",
  "key_concern": "the single most important issue in this message",
  "sentiment": "NEGATIVE",
  "requires_escalation": true
}}"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        max_tokens=300,
        messages=[{"role": "user", "content": prompt}]
    )
    raw = response.choices[0].message.content.strip()
    # Strip markdown fences if present
    import re
    raw = re.sub(r'^```json|^```|```$', '', raw, flags=re.MULTILINE).strip()
    return json.loads(raw)