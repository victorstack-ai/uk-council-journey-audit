import time
from typing import List
from playwright.sync_api import (
    sync_playwright,
    Page,
    TimeoutError as PlaywrightTimeoutError,
    Error as PlaywrightError,
)
from .models import Journey, AuditResult

# Default timeout for page actions in milliseconds
DEFAULT_TIMEOUT_MS = 15000
# Default timeout for navigation in milliseconds
NAVIGATION_TIMEOUT_MS = 30000


class AuditError(Exception):
    """Base exception for audit-specific errors."""
    pass


class ElementNotFoundError(AuditError):
    """Raised when a required page element cannot be found."""
    pass


class NavigationError(AuditError):
    """Raised when page navigation fails."""
    pass


class CouncilAuditor:
    def __init__(self, base_url: str, timeout_ms: int = DEFAULT_TIMEOUT_MS):
        self.base_url = base_url
        self.timeout_ms = timeout_ms
        self.log: List[str] = []

    def run_journey(self, journey: Journey) -> AuditResult:
        start_time = time.time()
        success = False
        error_message = None
        steps_taken = 0
        self.log = []

        with sync_playwright() as p:
            browser = None
            try:
                browser = p.chromium.launch(headless=True)
                context = browser.new_context()
                context.set_default_timeout(self.timeout_ms)
                context.set_default_navigation_timeout(NAVIGATION_TIMEOUT_MS)
                page = context.new_page()

                for step in journey.steps:
                    steps_taken += 1
                    self.log.append(f"Step {steps_taken}: {step.name} ({step.action})")

                    if step.action == "navigate":
                        self._handle_navigate(page)
                    elif step.action == "search":
                        self._handle_search(page, step.target or "")
                    elif step.action == "click_link":
                        self._handle_click_link(page, step.target or "")
                    else:
                        raise AuditError(f"Unknown action type: {step.action}")

                    self._wait_for_page_ready(page)

                success = True

            except PlaywrightTimeoutError as e:
                error_message = f"Timeout: page or element took too long to respond. {e}"
                self.log.append(f"Error (timeout): {error_message}")
            except ElementNotFoundError as e:
                error_message = f"Element not found: {e}"
                self.log.append(f"Error (element not found): {error_message}")
            except NavigationError as e:
                error_message = f"Navigation failed: {e}"
                self.log.append(f"Error (navigation): {error_message}")
            except PlaywrightError as e:
                error_message = f"Browser error: {e}"
                self.log.append(f"Error (browser): {error_message}")
            except ConnectionError as e:
                error_message = f"Network connection error: {e}"
                self.log.append(f"Error (network): {error_message}")
            except Exception as e:
                error_message = f"Unexpected error: {e}"
                self.log.append(f"Error: {error_message}")
            finally:
                if browser is not None:
                    try:
                        browser.close()
                    except Exception:
                        pass

        duration = time.time() - start_time
        return AuditResult(
            journey_name=journey.name,
            url=self.base_url,
            success=success,
            steps_taken=steps_taken,
            duration=duration,
            error_message=error_message,
            log=self.log,
        )

    def _handle_navigate(self, page: Page) -> None:
        """Navigate to the base URL with error handling."""
        try:
            response = page.goto(self.base_url, wait_until="domcontentloaded")
            if response and response.status >= 400:
                raise NavigationError(
                    f"HTTP {response.status} when loading {self.base_url}"
                )
        except PlaywrightTimeoutError:
            raise NavigationError(
                f"Timed out loading {self.base_url} "
                f"(waited {NAVIGATION_TIMEOUT_MS}ms)"
            )
        except PlaywrightError as e:
            if "net::ERR_" in str(e) or "NS_ERROR_" in str(e):
                raise NavigationError(
                    f"Network error loading {self.base_url}: {e}"
                )
            raise

    def _handle_search(self, page: Page, query: str) -> None:
        """Find a search input and submit a query with fallback selectors."""
        search_selectors = [
            'input[type="search"]',
            'input[name="s"]',
            'input[name="q"]',
            'input[name="query"]',
            'input[name="search"]',
            'input[placeholder*="search" i]',
            'input[aria-label*="search" i]',
            '#search-input',
            '#site-search',
            '.search-input input',
        ]

        for selector in search_selectors:
            try:
                if page.is_visible(selector, timeout=1000):
                    page.fill(selector, query)
                    page.press(selector, "Enter")
                    self.log.append(
                        f"  -> Found search input via: {selector}"
                    )
                    return
            except (PlaywrightTimeoutError, PlaywrightError):
                continue

        raise ElementNotFoundError(
            f"Could not find search input on page. "
            f"Tried {len(search_selectors)} selectors for query: {query}"
        )

    def _handle_click_link(self, page: Page, text: str) -> None:
        """Click a link matching the given text with multiple fallback strategies."""
        # Strategy 1: Playwright role-based locator (best practice)
        try:
            locator = page.get_by_role("link", name=text, exact=False).first
            locator.wait_for(state="visible", timeout=self.timeout_ms)
            locator.click()
            self.log.append(f"  -> Clicked link via role locator: '{text}'")
            return
        except (PlaywrightTimeoutError, PlaywrightError):
            pass

        # Strategy 2: CSS text selector
        try:
            page.click(f"text='{text}'", timeout=self.timeout_ms)
            self.log.append(f"  -> Clicked link via text selector: '{text}'")
            return
        except (PlaywrightTimeoutError, PlaywrightError):
            pass

        # Strategy 3: Partial text match with XPath
        try:
            xpath = f"//a[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{text.lower()}')]"
            page.click(xpath, timeout=self.timeout_ms)
            self.log.append(f"  -> Clicked link via XPath: '{text}'")
            return
        except (PlaywrightTimeoutError, PlaywrightError):
            pass

        raise ElementNotFoundError(
            f"Could not find clickable link with text: '{text}'. "
            f"Tried role locator, text selector, and XPath."
        )

    def _wait_for_page_ready(self, page: Page) -> None:
        """Wait for the page to reach a stable state after an action."""
        try:
            page.wait_for_load_state("networkidle", timeout=self.timeout_ms)
        except PlaywrightTimeoutError:
            # Fall back to domcontentloaded if networkidle times out
            # (some pages have persistent connections that prevent networkidle)
            try:
                page.wait_for_load_state(
                    "domcontentloaded", timeout=5000
                )
                self.log.append(
                    "  -> Warning: networkidle timed out, "
                    "fell back to domcontentloaded"
                )
            except PlaywrightTimeoutError:
                self.log.append(
                    "  -> Warning: page load state check timed out"
                )
