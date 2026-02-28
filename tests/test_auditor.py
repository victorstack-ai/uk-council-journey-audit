import pytest
from unittest.mock import MagicMock, patch, PropertyMock
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError, Error as PlaywrightError
from uk_council_journey_audit.auditor import (
    CouncilAuditor,
    AuditError,
    ElementNotFoundError,
    NavigationError,
)
from uk_council_journey_audit.journeys import DEFAULT_JOURNEYS
from uk_council_journey_audit.models import Journey, JourneyStep, AuditResult


# ---------------------------------------------------------------------------
# Model tests
# ---------------------------------------------------------------------------

class TestModels:
    def test_journey_model_missed_bin(self):
        journey = DEFAULT_JOURNEYS["missed-bin"]
        assert journey.name == "Report a Missed Bin"
        assert len(journey.steps) == 3

    def test_journey_model_council_tax(self):
        journey = DEFAULT_JOURNEYS["council-tax"]
        assert journey.name == "Council Tax Payment"
        assert len(journey.steps) == 3

    def test_journey_model_pay_council_tax(self):
        journey = DEFAULT_JOURNEYS["pay-council-tax"]
        assert journey.name == "Pay Council Tax"
        assert len(journey.steps) == 4

    def test_journey_model_report_pothole(self):
        journey = DEFAULT_JOURNEYS["report-pothole"]
        assert journey.name == "Report a Pothole"
        assert len(journey.steps) == 3

    def test_journey_model_parking_permit(self):
        journey = DEFAULT_JOURNEYS["parking-permit"]
        assert journey.name == "Apply for Parking Permit"
        assert len(journey.steps) == 4

    def test_journey_model_planning_applications(self):
        journey = DEFAULT_JOURNEYS["planning-applications"]
        assert journey.name == "Find Planning Applications"
        assert len(journey.steps) == 4

    def test_journey_model_register_to_vote(self):
        journey = DEFAULT_JOURNEYS["register-to-vote"]
        assert journey.name == "Register to Vote"
        assert len(journey.steps) == 3

    def test_all_journeys_have_required_fields(self):
        for key, journey in DEFAULT_JOURNEYS.items():
            assert journey.name, f"Journey '{key}' is missing a name"
            assert journey.description, f"Journey '{key}' is missing a description"
            assert len(journey.steps) >= 2, f"Journey '{key}' should have at least 2 steps"
            # Every journey should start with a navigate step
            assert journey.steps[0].action == "navigate", (
                f"Journey '{key}' should start with a navigate action"
            )

    def test_journey_step_model(self):
        step = JourneyStep(name="Test Step", action="search", target="test query")
        assert step.name == "Test Step"
        assert step.action == "search"
        assert step.target == "test query"

    def test_journey_step_optional_target(self):
        step = JourneyStep(name="Navigate", action="navigate")
        assert step.target is None

    def test_audit_result_model(self):
        result = AuditResult(
            journey_name="Test",
            url="https://example.gov.uk",
            success=True,
            steps_taken=3,
            duration=2.5,
            log=["Step 1", "Step 2", "Step 3"],
        )
        assert result.success is True
        assert result.error_message is None

    def test_audit_result_with_error(self):
        result = AuditResult(
            journey_name="Test",
            url="https://example.gov.uk",
            success=False,
            steps_taken=1,
            duration=0.5,
            error_message="Something went wrong",
            log=["Step 1", "Error: Something went wrong"],
        )
        assert result.success is False
        assert result.error_message == "Something went wrong"


# ---------------------------------------------------------------------------
# Helper to build a mock Playwright stack
# ---------------------------------------------------------------------------

def _build_playwright_mocks(mock_playwright):
    """Build and return a mock Playwright context with page."""
    mock_p = mock_playwright.return_value.__enter__.return_value
    mock_browser = mock_p.chromium.launch.return_value
    mock_context = mock_browser.new_context.return_value
    mock_page = mock_context.new_page.return_value

    # Defaults: all methods succeed silently
    mock_response = MagicMock()
    mock_response.status = 200
    mock_page.goto.return_value = mock_response
    mock_page.is_visible.return_value = True
    mock_page.fill.return_value = None
    mock_page.press.return_value = None
    mock_page.click.return_value = None
    mock_page.wait_for_load_state.return_value = None

    mock_locator = MagicMock()
    mock_locator.wait_for.return_value = None
    mock_locator.click.return_value = None
    mock_page.get_by_role.return_value.first = mock_locator

    return mock_browser, mock_context, mock_page


# ---------------------------------------------------------------------------
# Auditor success tests
# ---------------------------------------------------------------------------

class TestAuditorSuccess:
    @patch("uk_council_journey_audit.auditor.sync_playwright")
    def test_run_journey_success(self, mock_playwright):
        _, _, mock_page = _build_playwright_mocks(mock_playwright)

        auditor = CouncilAuditor("https://example.gov.uk")
        journey = DEFAULT_JOURNEYS["missed-bin"]
        result = auditor.run_journey(journey)

        assert result.success is True
        assert result.journey_name == "Report a Missed Bin"
        assert result.steps_taken == 3
        assert len(result.log) >= 3

    @patch("uk_council_journey_audit.auditor.sync_playwright")
    def test_run_journey_records_url(self, mock_playwright):
        _build_playwright_mocks(mock_playwright)

        auditor = CouncilAuditor("https://example.gov.uk")
        result = auditor.run_journey(DEFAULT_JOURNEYS["missed-bin"])
        assert result.url == "https://example.gov.uk"

    @patch("uk_council_journey_audit.auditor.sync_playwright")
    def test_run_journey_duration_is_positive(self, mock_playwright):
        _build_playwright_mocks(mock_playwright)

        auditor = CouncilAuditor("https://example.gov.uk")
        result = auditor.run_journey(DEFAULT_JOURNEYS["missed-bin"])
        assert result.duration > 0

    @patch("uk_council_journey_audit.auditor.sync_playwright")
    def test_run_all_journeys(self, mock_playwright):
        """Every default journey should complete successfully with a mocked browser."""
        _build_playwright_mocks(mock_playwright)

        for key, journey in DEFAULT_JOURNEYS.items():
            auditor = CouncilAuditor("https://example.gov.uk")
            result = auditor.run_journey(journey)
            assert result.success is True, f"Journey '{key}' failed unexpectedly"


# ---------------------------------------------------------------------------
# Auditor failure / error-handling tests
# ---------------------------------------------------------------------------

class TestAuditorErrors:
    @patch("uk_council_journey_audit.auditor.sync_playwright")
    def test_network_error(self, mock_playwright):
        _, _, mock_page = _build_playwright_mocks(mock_playwright)
        mock_page.goto.side_effect = PlaywrightError("net::ERR_CONNECTION_REFUSED")

        auditor = CouncilAuditor("https://example.gov.uk")
        result = auditor.run_journey(DEFAULT_JOURNEYS["missed-bin"])

        assert result.success is False
        assert "Navigation failed" in result.error_message

    @patch("uk_council_journey_audit.auditor.sync_playwright")
    def test_timeout_error(self, mock_playwright):
        _, _, mock_page = _build_playwright_mocks(mock_playwright)
        mock_page.goto.side_effect = PlaywrightTimeoutError("Timeout 30000ms exceeded")

        auditor = CouncilAuditor("https://example.gov.uk")
        result = auditor.run_journey(DEFAULT_JOURNEYS["missed-bin"])

        assert result.success is False
        assert "Navigation failed" in result.error_message

    @patch("uk_council_journey_audit.auditor.sync_playwright")
    def test_http_404_error(self, mock_playwright):
        _, _, mock_page = _build_playwright_mocks(mock_playwright)
        mock_response = MagicMock()
        mock_response.status = 404
        mock_page.goto.return_value = mock_response

        auditor = CouncilAuditor("https://example.gov.uk")
        result = auditor.run_journey(DEFAULT_JOURNEYS["missed-bin"])

        assert result.success is False
        assert "HTTP 404" in result.error_message

    @patch("uk_council_journey_audit.auditor.sync_playwright")
    def test_http_500_error(self, mock_playwright):
        _, _, mock_page = _build_playwright_mocks(mock_playwright)
        mock_response = MagicMock()
        mock_response.status = 500
        mock_page.goto.return_value = mock_response

        auditor = CouncilAuditor("https://example.gov.uk")
        result = auditor.run_journey(DEFAULT_JOURNEYS["missed-bin"])

        assert result.success is False
        assert "HTTP 500" in result.error_message

    @patch("uk_council_journey_audit.auditor.sync_playwright")
    def test_search_input_not_found(self, mock_playwright):
        _, _, mock_page = _build_playwright_mocks(mock_playwright)
        # Navigate succeeds but search input is never visible
        mock_page.is_visible.return_value = False

        journey = Journey(
            name="Test Search Fail",
            description="A journey that fails at the search step.",
            steps=[
                JourneyStep(name="Home", action="navigate"),
                JourneyStep(name="Search", action="search", target="test"),
            ]
        )
        auditor = CouncilAuditor("https://example.gov.uk")
        result = auditor.run_journey(journey)

        assert result.success is False
        assert "Element not found" in result.error_message
        assert "search input" in result.error_message.lower()

    @patch("uk_council_journey_audit.auditor.sync_playwright")
    def test_link_not_found(self, mock_playwright):
        _, _, mock_page = _build_playwright_mocks(mock_playwright)
        # Role locator fails, text selector fails, XPath fails
        mock_page.get_by_role.return_value.first.wait_for.side_effect = PlaywrightTimeoutError("timeout")
        mock_page.click.side_effect = PlaywrightTimeoutError("timeout")

        journey = Journey(
            name="Test Link Fail",
            description="A journey that fails at the click step.",
            steps=[
                JourneyStep(name="Home", action="navigate"),
                JourneyStep(name="Click", action="click_link", target="Nonexistent Link"),
            ]
        )
        auditor = CouncilAuditor("https://example.gov.uk")
        result = auditor.run_journey(journey)

        assert result.success is False
        assert "Element not found" in result.error_message

    @patch("uk_council_journey_audit.auditor.sync_playwright")
    def test_unknown_action_type(self, mock_playwright):
        _build_playwright_mocks(mock_playwright)

        journey = Journey(
            name="Test Unknown Action",
            description="A journey with an invalid action.",
            steps=[
                JourneyStep(name="Home", action="navigate"),
                JourneyStep(name="Bad Step", action="fly_to_moon", target="moon"),
            ]
        )
        auditor = CouncilAuditor("https://example.gov.uk")
        result = auditor.run_journey(journey)

        assert result.success is False
        assert "Unknown action type" in result.error_message

    @patch("uk_council_journey_audit.auditor.sync_playwright")
    def test_generic_exception(self, mock_playwright):
        _, _, mock_page = _build_playwright_mocks(mock_playwright)
        mock_page.goto.side_effect = Exception("Something completely unexpected")

        auditor = CouncilAuditor("https://example.gov.uk")
        result = auditor.run_journey(DEFAULT_JOURNEYS["missed-bin"])

        assert result.success is False
        assert "Unexpected error" in result.error_message

    @patch("uk_council_journey_audit.auditor.sync_playwright")
    def test_networkidle_timeout_fallback(self, mock_playwright):
        _, _, mock_page = _build_playwright_mocks(mock_playwright)
        # networkidle times out but domcontentloaded succeeds
        call_count = 0
        def wait_for_load_state_side_effect(state, timeout=None):
            nonlocal call_count
            call_count += 1
            if state == "networkidle":
                raise PlaywrightTimeoutError("networkidle timeout")
        mock_page.wait_for_load_state.side_effect = wait_for_load_state_side_effect

        journey = Journey(
            name="Single Navigate",
            description="Just navigate.",
            steps=[
                JourneyStep(name="Home", action="navigate"),
            ]
        )
        auditor = CouncilAuditor("https://example.gov.uk")
        result = auditor.run_journey(journey)

        assert result.success is True
        assert any("networkidle timed out" in entry for entry in result.log)


# ---------------------------------------------------------------------------
# Auditor log / reset tests
# ---------------------------------------------------------------------------

class TestAuditorLog:
    @patch("uk_council_journey_audit.auditor.sync_playwright")
    def test_log_resets_between_runs(self, mock_playwright):
        _build_playwright_mocks(mock_playwright)

        auditor = CouncilAuditor("https://example.gov.uk")

        result1 = auditor.run_journey(DEFAULT_JOURNEYS["missed-bin"])
        result2 = auditor.run_journey(DEFAULT_JOURNEYS["missed-bin"])

        # Each run should have its own independent log
        assert len(result1.log) == len(result2.log)
        assert result1.log == result2.log

    @patch("uk_council_journey_audit.auditor.sync_playwright")
    def test_custom_timeout(self, mock_playwright):
        _, mock_context, _ = _build_playwright_mocks(mock_playwright)

        auditor = CouncilAuditor("https://example.gov.uk", timeout_ms=5000)
        auditor.run_journey(DEFAULT_JOURNEYS["missed-bin"])

        mock_context.set_default_timeout.assert_called_with(5000)


# ---------------------------------------------------------------------------
# Journey definitions tests
# ---------------------------------------------------------------------------

class TestJourneyDefinitions:
    def test_expected_journey_keys_exist(self):
        expected_keys = [
            "missed-bin",
            "council-tax",
            "pay-council-tax",
            "report-pothole",
            "parking-permit",
            "planning-applications",
            "register-to-vote",
        ]
        for key in expected_keys:
            assert key in DEFAULT_JOURNEYS, f"Missing journey: {key}"

    def test_journey_count(self):
        assert len(DEFAULT_JOURNEYS) >= 7
