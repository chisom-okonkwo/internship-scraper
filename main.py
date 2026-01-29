from scraper.microsoft import MicrosoftScraper
from scraper.nvidia import NvidiaScraper
import pandas as pd


SCRAPER_SETTINGS = {
    "max_pages": 1,
    "internship_only": False,
    "locations": [],
}


def main():
    scrapers = [
        MicrosoftScraper(**SCRAPER_SETTINGS),
        NvidiaScraper(**SCRAPER_SETTINGS),
    ]

    all_jobs = []
    seen_urls = set()
    for scraper in scrapers:
        for job in scraper.scrape():
            url = job.get("url")
            if url and url in seen_urls:
                continue
            if url:
                seen_urls.add(url)
            all_jobs.append(job)

    print(f"Total jobs scraped after filters: {len(all_jobs)}")

    df = pd.DataFrame(all_jobs)
    df.to_csv("data/jobs.csv", index=False)
    print("Saved jobs to data/jobs.csv")


if __name__ == "__main__":
    main()