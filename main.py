from scraper.microsoft import scrape_microsoft_jobs
import pandas as pd


def main():
    MAX_PAGES = 5  # 👈 change this to whatever you want

    jobs = scrape_microsoft_jobs(max_pages=MAX_PAGES)
    print(f"Total jobs scraped: {len(jobs)}")

    df = pd.DataFrame(jobs)
    df.to_csv("data/microsoft_jobs.csv", index=False)
    print("Saved jobs to data/microsoft_jobs.csv")


if __name__ == "__main__":
    main()
