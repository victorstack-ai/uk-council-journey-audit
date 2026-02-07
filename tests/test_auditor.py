import pytest
from unittest.mock import MagicMock, patch
from uk_council_journey_audit.auditor import CouncilAuditor
from uk_council_journey_audit.journeys import DEFAULT_JOURNEYS
from uk_council_journey_audit.models import Journey, JourneyStep

def test_journey_model():
    journey = DEFAULT_JOURNEYS["missed-bin"]
    assert journey.name == "Report a Missed Bin"
    assert len(journey.steps) == 3

@patch("uk_council_journey_audit.auditor.sync_playwright")
def test_auditor_run_journey_success(mock_playwright):
    # Setup mocks
    mock_p = mock_playwright.return_value.__enter__.return_value
    mock_browser = mock_p.chromium.launch.return_value
    mock_context = mock_browser.new_context.return_value
    mock_page = mock_context.new_page.return_value
    
    # Mock page methods
    mock_page.goto.return_value = None
    mock_page.is_visible.return_value = True
    
    auditor = CouncilAuditor("https://example.gov.uk")
    journey = DEFAULT_JOURNEYS["missed-bin"]
    
    result = auditor.run_journey(journey)
    
    assert result.success is True
    assert result.journey_name == "Report a Missed Bin"
    assert result.steps_taken == 3
    assert len(result.log) >= 3

@patch("uk_council_journey_audit.auditor.sync_playwright")
def test_auditor_run_journey_failure(mock_playwright):
    # Setup mocks to fail
    mock_p = mock_playwright.return_value.__enter__.return_value
    mock_browser = mock_p.chromium.launch.return_value
    mock_context = mock_browser.new_context.return_value
    mock_page = mock_context.new_page.return_value
    
    mock_page.goto.side_effect = Exception("Network Error")
    
    auditor = CouncilAuditor("https://example.gov.uk")
    journey = DEFAULT_JOURNEYS["missed-bin"]
    
    result = auditor.run_journey(journey)
    
    assert result.success is False
    assert "Network Error" in result.error_message
