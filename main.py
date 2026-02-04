from scraper.microsoft import scrape_microsoft_jobs
from scraper.nvidia import scrape_nvidia_jobs
import pandas as pd


SCRAPER_SETTINGS = {
    "max_pages": 1,
    "internship_only": False,
    "locations": [],
}


def main():
    # List of scraper functions to run
    scraper_functions = [
        scrape_microsoft_jobs,
        scrape_nvidia_jobs,
    ]

    all_jobs = []
    seen_urls = set()
    
    for scrape_func in scraper_functions:
        try:
            print(f"Running {scrape_func.__name__}...")
            jobs = scrape_func(**SCRAPER_SETTINGS)
            
            for job in jobs:
                url = job.get("url")
                if url and url in seen_urls:
                    continue
                if url:
                    seen_urls.add(url)
                all_jobs.append(job)
        except Exception as e:
            print(f"Error running {scrape_func.__name__}: {e}")

    print(f"Total jobs scraped after filters: {len(all_jobs)}")

    if all_jobs:
        df = pd.DataFrame(all_jobs)
        df.to_csv("data/jobs.csv", index=False)
        print("Saved jobs to data/jobs.csv")
    else:
        print("No jobs found.")


if __name__ == "__main__":
    main()