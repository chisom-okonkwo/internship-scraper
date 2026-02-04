from .eightfold import EightfoldScraper


def scrape_microsoft_jobs(
    max_pages: int = 1,
    internship_only: bool = False,
    locations: list[str] | None = None
) -> list[dict]:
    
    # Microsoft's specific Eightfold URL
    base_url = "https://apply.careers.microsoft.com/careers?start=0&pid=1970393556642939&sort_by=timestamp"
    
    scraper = EightfoldScraper(
        base_url=base_url,
        company_name="Microsoft",
        max_pages=max_pages,
        internship_only=internship_only,
        locations=locations,
    )
    return scraper.scrape()
