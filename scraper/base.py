from __future__ import annotations

from typing import Iterable, List, Optional


class BaseScraper:
    def __init__(
        self,
        max_pages: int = 1,
        internship_only: bool = False,
        locations: Optional[Iterable[str]] = None,
    ) -> None:
        self.max_pages = max_pages
        self.internship_only = internship_only
        self.locations = list(locations) if locations is not None else []

    def scrape(self) -> List[dict]:
        """Return a list of job records."""
        raise NotImplementedError("Subclasses must implement scrape().")
