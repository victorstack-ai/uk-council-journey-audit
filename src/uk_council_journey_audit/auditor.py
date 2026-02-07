import time
from typing import List
from playwright.sync_api import sync_playwright, Page
from .models import Journey, AuditResult

class CouncilAuditor:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.log = []

    def run_journey(self, journey: Journey) -> AuditResult:
        start_time = time.time()
        success = False
        error_message = None
        steps_taken = 0

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()
            page = context.new_page()

            try:
                for step in journey.steps:
                    steps_taken += 1
                    self.log.append(f"Step {steps_taken}: {step.name} ({step.action})")
                    
                    if step.action == "navigate":
                        page.goto(self.base_url)
                    elif step.action == "search":
                        self._handle_search(page, step.target)
                    elif step.action == "click_link":
                        self._handle_click_link(page, step.target)
                    
                    page.wait_for_load_state("networkidle")
                
                success = True
            except Exception as e:
                error_message = str(e)
                self.log.append(f"Error: {error_message}")
            finally:
                browser.close()

        duration = time.time() - start_time
        return AuditResult(
            journey_name=journey.name,
            url=self.base_url,
            success=success,
            steps_taken=steps_taken,
            duration=duration,
            error_message=error_message,
            log=self.log
        )

    def _handle_search(self, page: Page, query: str):
        # Try to find a search input
        search_selectors = [
            'input[type="search"]',
            'input[name="s"]',
            'input[name="q"]',
            'input[placeholder*="search" i]',
            'input[aria-label*="search" i]'
        ]
        
        found = False
        for selector in search_selectors:
            if page.is_visible(selector):
                page.fill(selector, query)
                page.press(selector, "Enter")
                found = True
                break
        
        if not found:
            raise Exception(f"Could not find search input for query: {query}")

    def _handle_click_link(self, page: Page, text: str):
        # Try to find a link with the text
        try:
            page.get_by_role("link", name=text, exact=False).first.click()
        except:
            # Fallback to search-like behavior or just finding any text
            try:
                page.click(f"text='{text}'")
            except:
                 raise Exception(f"Could not find link with text: {text}")
