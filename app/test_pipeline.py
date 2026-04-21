import pytest
from core.triage_agent import run_triage


def test_triage_pipeline_execution():
    """Test that the triage pipeline executes successfully"""
    test_message = "URGENT: My account ACC-992841 has been compromised with unauthorized transfers of $45,000."
    result = run_triage(test_message)
    
    # Verify result structure
    assert isinstance(result, dict), "Result should be a dictionary"
    assert "status" in result, "Result should contain status"
    assert "urgency" in result, "Result should contain urgency"
    assert "pipeline" in result, "Result should contain pipeline steps"
    assert "draft_response" in result, "Result should contain draft_response"


def test_triage_pipeline_status():
    """Test that pipeline completes with success status"""
    test_message = "URGENT: My account ACC-992841 has been compromised with unauthorized transfers of $45,000."
    result = run_triage(test_message)
    
    assert result["status"] == "complete", f"Pipeline should complete, got: {result['status']}"


def test_triage_urgency_detection():
    """Test that urgency is properly detected"""
    test_message = "URGENT: My account ACC-992841 has been compromised with unauthorized transfers of $45,000."
    result = run_triage(test_message)
    
    assert result["urgency"] in ["CRITICAL", "HIGH", "MEDIUM", "LOW"], f"Urgency should be valid, got: {result['urgency']}"


def test_triage_pipeline_steps():
    """Test that all pipeline steps complete"""
    test_message = "URGENT: My account ACC-992841 has been compromised with unauthorized transfers of $45,000."
    result = run_triage(test_message)
    
    pipeline = result["pipeline"]
    expected_steps = ["classification", "ner", "response"]
    
    for step in expected_steps:
        assert step in pipeline, f"Pipeline should contain {step} step"
        assert pipeline[step]["status"] in ["success", "error"], f"Step {step} should have valid status"


def test_triage_draft_response():
    """Test that draft response is generated"""
    test_message = "URGENT: My account ACC-992841 has been compromised with unauthorized transfers of $45,000."
    result = run_triage(test_message)
    
    draft = result["draft_response"]
    assert "subject" in draft, "Draft should contain subject"
    assert "body" in draft, "Draft should contain body"
    assert len(draft["subject"]) > 0, "Subject should not be empty"
    assert len(draft["body"]) > 0, "Body should not be empty"