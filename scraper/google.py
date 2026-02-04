from typing import List, Optional
import requests
from bs4 import BeautifulSoup
from .base import BaseScraper
import urllib.parse

class GoogleScraper(BaseScraper):
    def __init__(
        self,
        max_pages: int = 1,
        internship_only: bool = False,
        locations: Optional[List[str]] = None,
    ):
        super().__init__(max_pages=max_pages, internship_only=internship_only, locations=locations)
        self.base_url = "https://www.google.com/about/careers/applications/jobs/results/"

    def scrape(self) -> List[dict]:
        all_jobs = []
        page = 1
        
        while page <= self.max_pages:
            print(f"[Google] Scraping page {page}...")
            # Query construction
            query = "intern" if self.internship_only else "software engineer"
            params = {
                "page": page,
                "q": query,
                "sort_by": "relevance"
            }
            if self.locations:
                # Google supports location in 'q' or separate filters, but 'q' is easiest for now
                # q=software engineer in New York
                params["q"] += f" in {' '.join(self.locations)}"

            try:
                resp = requests.get(self.base_url, params=params, headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
                })
                resp.raise_for_status()
                soup = BeautifulSoup(resp.text, 'html.parser')
                
                job_links = []
                # Finding all "Learn more about..." links
                for a in soup.find_all('a', href=True, attrs={"aria-label": True}):
                    label = a['aria-label']
                    if label.startswith("Learn more about "):
                        title = label.replace("Learn more about ", "").strip()
                        href = a['href']
                        if href.startswith("./"):
                            href = href[2:]
                        full_url = urllib.parse.urljoin(self.base_url, href)
                        
                        # Location extraction (Heuristic)
                        # The parent text usually contains: "Title\nCompany\nLocation\n..."
                        # We can try to get the parent text.
                        location = "See URL for details"
                        try:
                            # Try to find the text of the card
                            # Navigation: a -> div (actions) -> div (card content) -> div (card frame)
                            # This is brittle, so we'll just search parent text for now.
                            parent_text = a.parent.get_text(" | ", strip=True)
                            # Basic cleanup or just store it. 
                            # If we identify known cities in self.locations, we can refine.
                            location = parent_text[:200] # Truncate to avoid huge dump
                        except:
                            pass

                        job_links.append({
                            "title": title,
                            "company": "Google",
                            "location": location, # Placeholder or extracted text
                            "posted": "Unknown", # Google doesn't easily expose date in snippet
                            "url": full_url,
                            "description": "Visit URL for full description."
                        })

                if not job_links:
                    print(f"[Google] No jobs found on page {page}.")
                    break

                for job in job_links:
                    # Filter
                    if self.internship_only:
                        if "intern" not in job["title"].lower():
                            continue
                            
                    # Manual location check if query param didn't filter perfectly
                    if self.locations:
                        # loose check
                        if not any(l.lower() in job["location"].lower() for l in self.locations):
                             # Only strict filter if we are sure about location data quality. 
                             # Since location is messy text, let's NOT filter strictly here to avoid false negatives.
                             pass

                    all_jobs.append(job)

                page += 1
                
            except Exception as e:
                print(f"[Google] Error scraping page {page}: {e}")
                break
                
        print(f"[Google] Found {len(all_jobs)} jobs total.")
        return all_jobs

def scrape_google_jobs(
    max_pages: int = 1,
    internship_only: bool = False,
    locations: Optional[List[str]] = None,
) -> List[dict]:
    scraper = GoogleScraper(
        max_pages=max_pages,
        internship_only=internship_only,
        locations=locations
    )
    return scraper.scrape()
