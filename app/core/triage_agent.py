import time
from datetime import datetime
from core.classifier import classify_message, URGENCY_LEVELS
from core.ner_extractor import extract_all_entities
from core.response_generator import generate_draft_response


def run_triage(message_text: str, agent_name: str = "Finance Operations") -> dict:
    start_time = time.time()

    result = {
        "id": f"TRG-{int(time.time())}",
        "timestamp": datetime.now().isoformat(),
        "original_message": message_text,
        "status": "processing",
        "pipeline": {}
    }

    # STEP 1: Classification
    try:
        classification = classify_message(message_text)
        result["pipeline"]["classification"] = {"status": "success", "data": classification}
    except Exception as e:
        result["pipeline"]["classification"] = {"status": "error", "error": str(e)}
        classification = {"urgency": "MEDIUM", "intent": "GENERAL_INQUIRY", "confidence": 0.5}

    # STEP 2: NER Extraction
    try:
        entities = extract_all_entities(message_text)
        result["pipeline"]["ner"] = {"status": "success", "data": entities}
    except Exception as e:
        result["pipeline"]["ner"] = {"status": "error", "error": str(e)}
        entities = {"spacy": {}, "patterns": {}, "llm": {}, "summary": {}}

    # STEP 3: Draft Response
    try:
        draft = generate_draft_response(message_text, classification, entities, agent_name)
        result["pipeline"]["response"] = {"status": "success", "data": draft}
    except Exception as e:
        result["pipeline"]["response"] = {"status": "error", "error": str(e)}
        draft = {"subject": "Re: Your inquiry", "body": "Thank you for contacting us.", "metadata": {}}

    elapsed = round(time.time() - start_time, 2)

    result.update({
        "status": "complete",
        "urgency": classification.get("urgency", "MEDIUM"),
        "intent": classification.get("intent", "GENERAL_INQUIRY"),
        "confidence": classification.get("confidence", 0.5),
        "urgency_meta": URGENCY_LEVELS.get(classification.get("urgency", "MEDIUM"), {}),
        "entities_summary": entities.get("summary", {}),
        "draft_response": draft,
        "processing_time_seconds": elapsed,
        "requires_escalation": classification.get("requires_escalation", False),
    })

    return result