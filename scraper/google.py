from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException
import time

from .base import BaseScraper


def is_internship(title: str) -> bool:
    keywords = ["intern", "internship", "student"]
    title_lower = title.lower()
    return any(keyword in title_lower for keyword in keywords)


def matches_location(job_location: str, allowed_locations: list) -> bool:
    job_location_lower = job_location.lower()
    return any(loc.lower() in job_location_lower for loc in allowed_locations)


class GoogleScraper(BaseScraper):
    def scrape(self):
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")

        driver = webdriver.Chrome(service=Service(), options=options)

        url = "https://www.google.com/about/careers/applications/jobs/results/"
        driver.get(url)
        time.sleep(5)  # allow JS to load

        all_jobs = []
        current_page = 1

        while current_page <= self.max_pages:
            print(f"Scraping page {current_page} of {self.max_pages}...")
            time.sleep(2)

            job_links = driver.find_elements(
                By.CSS_SELECTOR,
                'a[href*="/about/careers/applications/jobs/results/"]',
            )

            for link in job_links:
                try:
                    job_url = link.get_attribute("href")
                except:
                    continue

                if not job_url:
                    continue

                # Deduplicate by URL
                if job_url in [job["url"] for job in all_jobs]:
                    continue

                title = ""
                location = ""

                try:
                    link_text = link.text.strip()
                    if link_text.lower().startswith("learn more about "):
                        title = link_text[len("Learn more about "):].strip()
                    else:
                        title = link_text
                except:
                    title = ""

                container = None
                try:
                    container = link.find_element(By.XPATH, "./ancestor::li[1]")
                except:
                    try:
                        container = link.find_element(By.XPATH, "./ancestor::div[1]")
                    except:
                        container = None

                if container:
                    lines = [line.strip() for line in container.text.splitlines() if line.strip()]

                    if not title and lines:
                        title = lines[0]

                    location_line = next((line for line in lines if "|" in line), "")
                    if location_line:
                        parts = [part.strip() for part in location_line.split("|")]
                        if len(parts) >= 2:
                            location = parts[1]

                posted = ""

                # --- Internship filter ---
                if self.internship_only and not is_internship(title):
                    continue

                # --- Location filter ---
                if self.locations and not matches_location(location, self.locations):
                    continue

                all_jobs.append({
                    "company": "Google",
                    "title": title,
                    "location": location,
                    "posted": posted,
                    "url": job_url
                })

            # Stop early if no next page exists
            try:
                next_button = None
                selectors = [
                    'a[aria-label="Go to next page"]',
                    'button[aria-label="Go to next page"]',
                    'a[aria-label="Next"]',
                    'button[aria-label="Next"]',
                ]

                for selector in selectors:
                    matches = driver.find_elements(By.CSS_SELECTOR, selector)
                    if matches:
                        next_button = matches[0]
                        break

                if not next_button:
                    print("Next button not found — stopping.")
                    break

                aria_disabled = next_button.get_attribute("aria-disabled")
                class_name = next_button.get_attribute("class") or ""
                if aria_disabled == "true" or "disabled" in class_name:
                    print("Next button disabled — reached last page.")
                    break

                driver.execute_script("arguments[0].scrollIntoView(true);", next_button)
                time.sleep(0.5)
                next_button.click()

                current_page += 1
                time.sleep(3)

            except NoSuchElementException:
                print("Next button not found — stopping.")
                break
            except ElementClickInterceptedException:
                print("Next button not clickable — stopping.")
                break

        driver.quit()
        return all_jobs
