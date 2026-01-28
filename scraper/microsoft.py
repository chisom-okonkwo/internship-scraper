from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException
import time


def scrape_microsoft_jobs(max_pages=1):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")

    driver = webdriver.Chrome(service=Service(), options=options)

    url = "https://apply.careers.microsoft.com/careers?start=0&pid=1970393556642939&sort_by=timestamp"
    driver.get(url)
    time.sleep(5)  # allow JS to load

    all_jobs = []
    current_page = 1

    while current_page <= max_pages:
        print(f"Scraping page {current_page} of {max_pages}...")
        time.sleep(2)

        job_cards = driver.find_elements(By.CSS_SELECTOR, "a.r-link.card-F1ebU")

        for card in job_cards:
            try:
                job_url = card.get_attribute("href")
            except:
                continue

            # Deduplicate by URL
            if job_url in [job["url"] for job in all_jobs]:
                continue

            try:
                title = card.find_element(By.CSS_SELECTOR, "div.title-1aNJK").text
            except:
                title = ""

            try:
                location = card.find_element(By.CSS_SELECTOR, "div.fieldValue-3kEar").text
            except:
                location = ""

            try:
                posted = card.find_element(By.CSS_SELECTOR, "div.subData-13Lm1").text
            except:
                posted = ""

            all_jobs.append({
                "title": title,
                "location": location,
                "posted": posted,
                "url": job_url
            })

        # Stop early if no next page exists
        try:
            next_button = driver.find_element(
                By.CSS_SELECTOR, 'button[aria-label="Next jobs"]'
            )

            if next_button.get_attribute("aria-disabled") == "true":
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
