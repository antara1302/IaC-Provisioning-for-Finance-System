"""
Pytest configuration for CI/CD pipeline testing.
Provides mocking for external dependencies (Groq API) so tests don't require real API keys.
"""

import os
import json
from unittest.mock import Mock, patch, MagicMock


def pytest_configure(config):
    """
    Configure pytest before test collection.
    Mocks the Groq API client so tests can run without a real GROQ_API_KEY.
    """
    # Set a dummy API key to prevent client initialization errors
    os.environ["GROQ_API_KEY"] = "test-api-key-for-ci-cd-pipeline"
    
    # Create a realistic mock response
    mock_response = MagicMock()
    mock_response.choices = [
        MagicMock(
            message=MagicMock(
                content=json.dumps({
                    "urgency": "CRITICAL",
                    "intent": "FRAUD_ALERT",
                    "confidence": 0.95,
                    "reasoning": "Compromised account with unauthorized transfers",
                    "key_concern": "Account security breach",
                    "sentiment": "NEGATIVE",
                    "requires_escalation": True,
                    "entities": ["ACC-992841", "$45,000"],
                    "response": "Account security issue detected and being investigated"
                })
            )
        )
    ]
    
    # Mock the Groq client globally
    mock_groq = MagicMock()
    mock_groq.chat.completions.create = MagicMock(return_value=mock_response)
    
    # Patch the Groq class before modules are imported
    patcher = patch("groq.Groq", return_value=mock_groq)
    patcher.start()
