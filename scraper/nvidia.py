from .eightfold import EightfoldScraper


def scrape_nvidia_jobs(
    max_pages: int = 1,
    internship_only: bool = False,
    locations: list[str] | None = None
) -> list[dict]:
    
    # Nvidia's specific Eightfold URL
    base_url = "https://nvidia.eightfold.ai/careers?start=0&pid=893392964053&sort_by=timestamp"
    
    scraper = EightfoldScraper(
        base_url=base_url,
        company_name="Nvidia",
        max_pages=max_pages,
        internship_only=internship_only,
        locations=locations,
    )
    return scraper.scrape()
