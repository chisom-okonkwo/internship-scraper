from scraper.microsoft import scrape_microsoft_jobs
from scraper.nvidia import scrape_nvidia_jobs

from scraper.google import scrape_google_jobs
import pandas as pd


SCRAPER_SETTINGS = {
    "max_pages": 1,
    "internship_only": False,
    "locations": [],
}

# List of Greenhouse board tokens for popular tech companies


def main():
    all_jobs = []
    seen_urls = set()

    # 1. Custom/Complex Scrapers (Eightfold)
    print("--- Starting Eightfold Scrapers ---")
    eightfold_scrapers = [
        scrape_microsoft_jobs,
        scrape_nvidia_jobs,
    ]
    
    for scrape_func in eightfold_scrapers:
        try:
            print(f"Running {scrape_func.__name__}...")
            jobs = scrape_func(**SCRAPER_SETTINGS)
            for job in jobs:
                if job["url"] not in seen_urls:
                    seen_urls.add(job["url"])
                    all_jobs.append(job)
        except Exception as e:
            print(f"Error running {scrape_func.__name__}: {e}")



    # 3. Google Scraper
    print("\n--- Starting Google Scraper ---")
    try:
        google_jobs = scrape_google_jobs(**SCRAPER_SETTINGS)
        count = 0
        for job in google_jobs:
            if job["url"] not in seen_urls:
                seen_urls.add(job["url"])
                all_jobs.append(job)
                count += 1
        print(f"  -> Found {count} new Google jobs")
    except Exception as e:
        print(f"  -> Error scraping Google: {e}")

    print(f"\nTotal jobs scraped after filters: {len(all_jobs)}")

    if all_jobs:
        df = pd.DataFrame(all_jobs)
        df.to_csv("data/jobs.csv", index=False)
        print("Saved jobs to data/jobs.csv")
    else:
        print("No jobs found.")


if __name__ == "__main__":
    main()