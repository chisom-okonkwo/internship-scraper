from __future__ import annotations

import time
from typing import List, Optional, Any

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    NoSuchElementException,
    ElementClickInterceptedException,
    TimeoutException,
)

from .base import BaseScraper


class EightfoldScraper(BaseScraper):
    """
    Generic scraper for career sites powered by Eightfold.ai.
    """

    # Default selectors (can be overridden in __init__)
    # Note: These class-based selectors are brittle and might need updating
    DEFAULT_SELECTORS = {
        "job_card": "a.r-link",  # Removed specific hash class to be slightly more generic if possible, or we stick to exact
        # "job_card": "a.css-12345" # fallback
        "title": "div[class*='title']", # heuristic
        "location": "div[class*='fieldValue']",
        "posted": "div[class*='subData']",
        "next_button": 'button[aria-label="Next jobs"]',
    }
    
    # Using the specific ones found in the user's code as primary defaults for now to ensure continuity, 
    # but allowing overrides.
    SPECIFIC_SELECTORS = {
        "job_card": "a.r-link.card-F1ebU",
        "title": "div.title-1aNJK",
        "location": "div.fieldValue-3kEar",
        "posted": "div.subData-13Lm1",
        "next_button": 'button[aria-label="Next jobs"]',
    }

    def __init__(
        self,
        base_url: str,
        company_name: str,
        selectors: Optional[dict[str, str]] = None,
        max_pages: int = 1,
        internship_only: bool = False,
        locations: Optional[List[str]] = None,
    ):
        super().__init__(
            max_pages=max_pages,
            internship_only=internship_only,
            locations=locations,
        )
        self.base_url = base_url
        self.company_name = company_name
        self.selectors = self.SPECIFIC_SELECTORS.copy()
        if selectors:
            self.selectors.update(selectors)

    def _get_driver_options(self) -> Options:
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        # Add basic user-agent to avoid being blocked immediately
        options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        )
        return options

    def is_internship(self, title: str) -> bool:
        keywords = ["intern", "internship", "student", "university", "graduate"]
        title_lower = title.lower()
        return any(keyword in title_lower for keyword in keywords)

    def matches_location(self, job_location: str) -> bool:
        if not self.locations:
            return True
        job_location_lower = job_location.lower()
        return any(loc.lower() in job_location_lower for loc in self.locations)

    def scrape(self) -> List[dict]:
        driver = webdriver.Chrome(service=Service(), options=self._get_driver_options())
        all_jobs = []
        
        try:
            print(f"[{self.company_name}] Connecting to {self.base_url}...")
            driver.get(self.base_url)
            
            # Initial wait for the app to load
            try:
                # Wait until at least one job card is present
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, self.selectors["job_card"]))
                )
            except TimeoutException:
                print(f"[{self.company_name}] Timed out waiting for job cards to load.")
                # We don't return immediately, explicitly checking for '0 jobs found' could be skipped for now

            current_page = 1
            while current_page <= self.max_pages:
                print(f"[{self.company_name}] Scraping page {current_page} of {self.max_pages}...")
                
                jobs_on_page = self._scrape_page(driver)
                
                # Filter and add jobs
                for job in jobs_on_page:
                    # Deduplicate by URL within this run
                    if job["url"] in [j["url"] for j in all_jobs]:
                        continue
                    
                    if self.internship_only and not self.is_internship(job["title"]):
                        continue
                        
                    if not self.matches_location(job["location"]):
                        continue

                    job["company"] = self.company_name
                    all_jobs.append(job)

                # Pagination
                if current_page < self.max_pages:
                    if not self._go_to_next_page(driver):
                        print(f"[{self.company_name}] No next page or failed to click next.")
                        break
                
                current_page += 1
                
        except Exception as e:
            print(f"[{self.company_name}] An fatal error occurred: {e}")
        finally:
            driver.quit()
            
        return all_jobs

    def _scrape_page(self, driver: WebDriver) -> List[dict]:
        jobs = []
        try:
            # We wait for cards to be visible
            job_cards = driver.find_elements(By.CSS_SELECTOR, self.selectors["job_card"])
        except NoSuchElementException:
            return []

        for card in job_cards:
            try:
                url = card.get_attribute("href")
                
                # Scoping finds to the card element
                try:
                    title = card.find_element(By.CSS_SELECTOR, self.selectors["title"]).text
                except NoSuchElementException:
                    title = "Unknown Title"

                try:
                    location = card.find_element(By.CSS_SELECTOR, self.selectors["location"]).text
                except NoSuchElementException:
                    location = "Unknown Location"
                    
                try:
                    posted = card.find_element(By.CSS_SELECTOR, self.selectors["posted"]).text
                except NoSuchElementException:
                    posted = ""

                jobs.append({
                    "title": title,
                    "location": location,
                    "posted": posted,
                    "url": url
                })
            except Exception as e:
                # If a card fails, skip it but log
                continue
                
        return jobs

    def _go_to_next_page(self, driver: WebDriver) -> bool:
        try:
            next_button = driver.find_element(By.CSS_SELECTOR, self.selectors["next_button"])
            
            # Check if disabled
            if next_button.get_attribute("aria-disabled") == "true":
                return False

            # Scroll into view
            driver.execute_script("arguments[0].scrollIntoView(true);", next_button)
            time.sleep(0.5) # Short sleep for scroll animation settlement
            
            # Click
            next_button.click()
            
            # Wait for stale element (page refresh) or new content
            # This is tricky in SPAs. Simplified approach: wait a bit or wait for loading indicators.
            # Eightfold usually updates the list. 
            time.sleep(2) # Keeping a small implicit wait for the SPA generic transition
            return True

        except (NoSuchElementException, ElementClickInterceptedException):
            return False
