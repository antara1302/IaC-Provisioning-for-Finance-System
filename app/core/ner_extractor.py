import re
import json
import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Try to load spaCy, fall back gracefully if not available
try:
    import spacy
    nlp = spacy.load("en_core_web_sm")
    SPACY_AVAILABLE = True
except Exception:
    SPACY_AVAILABLE = False


def extract_with_spacy(text: str) -> dict:
    if not SPACY_AVAILABLE:
        return {"persons": [], "organizations": [], "dates": [], "money": [], "locations": []}
    doc = nlp(text)
    entities = {"persons": [], "organizations": [], "dates": [], "money": [], "locations": []}
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            entities["persons"].append(ent.text)
        elif ent.label_ == "ORG":
            entities["organizations"].append(ent.text)
        elif ent.label_ in ("DATE", "TIME"):
            entities["dates"].append(ent.text)
        elif ent.label_ == "MONEY":
            entities["money"].append(ent.text)
        elif ent.label_ in ("GPE", "LOC"):
            entities["locations"].append(ent.text)
    return entities


def extract_finance_patterns(text: str) -> dict:
    return {
        "invoice_ids": re.findall(r'\b(?:INV|INVOICE|inv)[-#]?\s*\d{4,10}\b', text, re.IGNORECASE),
        "account_numbers": re.findall(r'\b(?:ACC|ACCT|Account)[-#]?\s*\d{6,12}\b', text, re.IGNORECASE),
        "transaction_ids": re.findall(r'\b(?:TXN|TRX|REF|TRANS)[-#]?\s*[A-Z0-9]{6,15}\b', text, re.IGNORECASE),
        "amounts": re.findall(
            r'(?:USD|EUR|GBP|INR|₹|\$|€|£)\s*[\d,]+(?:\.\d{2})?|\b\d{1,3}(?:,\d{3})*(?:\.\d{2})?\s*(?:USD|EUR|GBP|INR)',
            text, re.IGNORECASE
        ),
        "email_addresses": re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text),
        "phone_numbers": re.findall(r'\b(?:\+\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b', text),
    }


def extract_with_llm(text: str) -> dict:
    prompt = f"""Extract all financial entities from this message. Return ONLY valid JSON, no markdown:

MESSAGE: \"\"\"{text}\"\"\"

{{
  "client_name": null,
  "company_name": null,
  "due_dates": [],
  "payment_amounts": [],
  "invoice_references": [],
  "account_references": [],
  "mentioned_banks": [],
  "contract_references": [],
  "urgency_indicators": [],
  "action_required": "what specific action is being requested"
}}"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        max_tokens=400,
        messages=[{"role": "user", "content": prompt}]
    )
    raw = response.choices[0].message.content.strip()
    raw = re.sub(r'^```json|^```|```$', '', raw, flags=re.MULTILINE).strip()
    return json.loads(raw)


def extract_all_entities(text: str) -> dict:
    spacy_entities = extract_with_spacy(text)
    pattern_entities = extract_finance_patterns(text)
    llm_entities = extract_with_llm(text)

    return {
        "spacy": spacy_entities,
        "patterns": pattern_entities,
        "llm": llm_entities,
        "summary": {
            "total_entities_found": (
                len(spacy_entities.get("persons", [])) +
                len(pattern_entities.get("invoice_ids", [])) +
                len(pattern_entities.get("amounts", [])) +
                len(llm_entities.get("mentioned_banks", []))
            ),
            "has_monetary_values": bool(
                pattern_entities.get("amounts") or llm_entities.get("payment_amounts")
            ),
            "has_deadlines": bool(
                spacy_entities.get("dates") or llm_entities.get("due_dates")
            ),
            "action_required": llm_entities.get("action_required", "Unknown"),
        }
    }