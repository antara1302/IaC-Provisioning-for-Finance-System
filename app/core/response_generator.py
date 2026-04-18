import os
import re
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

RESPONSE_TEMPLATES = {
    "PAYMENT_DISPUTE": "payment dispute investigation and resolution",
    "FRAUD_ALERT": "urgent fraud investigation and account security",
    "INVOICE_QUERY": "invoice clarification and documentation",
    "ACCOUNT_CLOSURE": "account closure process and requirements",
    "COMPLIANCE_REQUEST": "compliance documentation and regulatory response",
    "REFUND_REQUEST": "refund processing and timeline",
    "CREDIT_APPLICATION": "credit application review and next steps",
    "GENERAL_INQUIRY": "general finance inquiry",
}

def generate_draft_response(original_message: str, classification: dict, entities: dict, agent_name: str = "Finance Operations Team") -> dict:
    urgency = classification.get("urgency", "MEDIUM")
    intent = classification.get("intent", "GENERAL_INQUIRY")
    key_concern = classification.get("key_concern", "")

    llm_entities = entities.get("llm", {})
    pattern_entities = entities.get("patterns", {})

    entity_context = []
    if llm_entities.get("client_name"):
        entity_context.append(f"Client: {llm_entities['client_name']}")
    refs = llm_entities.get("invoice_references", []) + pattern_entities.get("invoice_ids", [])
    if refs:
        refs_str = [str(r) for r in refs[:3]]
        entity_context.append(f"Invoice refs: {', '.join(refs_str)}")
    amounts = llm_entities.get("payment_amounts", []) + pattern_entities.get("amounts", [])
    if amounts:
        amounts_str = [str(a) for a in amounts[:3]]
        entity_context.append(f"Amounts: {', '.join(amounts_str)}")
    if llm_entities.get("due_dates"):
        dates_str = [str(d) for d in llm_entities["due_dates"][:2]]
        entity_context.append(f"Due dates: {', '.join(dates_str)}")

    entity_str = "\n".join(entity_context) if entity_context else "No specific entities extracted"

    tone_map = {
        "CRITICAL": "urgent, empathetic, and action-oriented. Acknowledge the severity immediately.",
        "HIGH": "prompt and professional, showing urgency and clear next steps.",
        "MEDIUM": "professional and helpful with clear timelines.",
        "LOW": "friendly and informative with no urgency.",
    }
    tone = tone_map.get(urgency, "professional")

    prompt = f"""You are a senior finance operations specialist drafting a response to an incoming client communication.

ORIGINAL MESSAGE:
\"\"\"{original_message}\"\"\"

CLASSIFICATION:
- Urgency: {urgency}
- Intent Type: {intent} ({RESPONSE_TEMPLATES.get(intent, 'general finance matter')})
- Key Concern: {key_concern}

EXTRACTED ENTITIES:
{entity_str}

INSTRUCTIONS:
1. Write a professional email response
2. Tone: Be {tone}
3. Address the specific concern identified
4. Reference any invoice IDs, amounts, or dates extracted
5. Provide clear next steps and a realistic timeline
6. Include a proper salutation and sign-off from "{agent_name}"
7. Keep it concise: 150-250 words maximum
8. DO NOT make up specific policy details

Write ONLY the email body:"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        max_tokens=600,
        messages=[{"role": "user", "content": prompt}]
    )
    draft_text = response.choices[0].message.content.strip()

    subject_prompt = f"""Write a professional email subject line for a finance {intent.lower().replace('_', ' ')} response.
Urgency: {urgency}. Key concern: {key_concern}.
Reply with ONLY the subject line, no quotes, no labels."""

    subject_response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        max_tokens=60,
        messages=[{"role": "user", "content": subject_prompt}]
    )
    subject_line = subject_response.choices[0].message.content.strip()

    return {
        "subject": subject_line,
        "body": draft_text,
        "metadata": {
            "model_used": "llama-3.3-70b-versatile",
            "urgency": urgency,
            "intent": intent,
            "word_count": len(draft_text.split()),
        }
    }