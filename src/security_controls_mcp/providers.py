"""Provider abstraction for security standards."""

import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional


class StandardMetadata:
    """Metadata about a security standard."""

    def __init__(self, data: Dict[str, Any]):
        """Initialize metadata from dictionary."""
        self.standard_id = data.get("standard_id", "")
        self.title = data.get("title", "")
        self.version = data.get("version", "")
        self.purchased_from = data.get("purchased_from", "")
        self.purchase_date = data.get("purchase_date", "")
        self.imported_date = data.get("imported_date", "")
        self.license = data.get("license", "")
        self.pages = data.get("pages", 0)
        self.restrictions = data.get("restrictions", [])


class SearchResult:
    """A search result from a standard."""

    def __init__(
        self,
        standard_id: str,
        clause_id: str,
        title: str,
        content: str,
        page: Optional[int] = None,
        section_type: Optional[str] = None,
    ):
        """Initialize search result."""
        self.standard_id = standard_id
        self.clause_id = clause_id
        self.title = title
        self.content = content
        self.page = page
        self.section_type = section_type


class StandardProvider(ABC):
    """Abstract base class for standard providers."""

    @abstractmethod
    def get_metadata(self) -> StandardMetadata:
        """Get metadata about this standard."""
        pass

    @abstractmethod
    def search(self, query: str, limit: int = 10) -> List[SearchResult]:
        """Search for content within the standard.

        Args:
            query: Search query string
            limit: Maximum number of results to return

        Returns:
            List of search results
        """
        pass

    @abstractmethod
    def get_clause(self, clause_id: str) -> Optional[SearchResult]:
        """Get a specific clause by ID.

        Args:
            clause_id: The clause/section identifier (e.g., "5.1.2", "A.5.15")

        Returns:
            The clause content, or None if not found
        """
        pass

    @abstractmethod
    def get_all_clauses(self) -> List[SearchResult]:
        """Get all clauses in the standard.

        Returns:
            List of all clauses
        """
        pass


class PaidStandardProvider(StandardProvider):
    """Provider for paid standards loaded from JSON files."""

    def __init__(self, standard_path: Path):
        """Initialize provider from standard data directory.

        Args:
            standard_path: Path to standard data directory containing
                          metadata.json and full_text.json
        """
        self.standard_path = standard_path
        self.metadata_file = standard_path / "metadata.json"
        self.full_text_file = standard_path / "full_text.json"

        # Load data
        self._load_data()

    def _load_data(self) -> None:
        """Load metadata and full text data."""
        if not self.metadata_file.exists():
            raise FileNotFoundError(f"Metadata file not found: {self.metadata_file}")

        if not self.full_text_file.exists():
            raise FileNotFoundError(f"Full text file not found: {self.full_text_file}")

        with open(self.metadata_file, "r") as f:
            self.metadata = StandardMetadata(json.load(f))

        with open(self.full_text_file, "r") as f:
            self.data = json.load(f)

    def get_metadata(self) -> StandardMetadata:
        """Get metadata about this standard."""
        return self.metadata

    def search(self, query: str, limit: int = 10) -> List[SearchResult]:
        """Search for content within the standard."""
        query_lower = query.lower()
        results = []

        # Search in sections
        for section in self._iterate_sections(self.data.get("structure", {}).get("sections", [])):
            if (
                query_lower in section.get("content", "").lower()
                or query_lower in section.get("title", "").lower()
            ):
                results.append(
                    SearchResult(
                        standard_id=self.metadata.standard_id,
                        clause_id=section["id"],
                        title=section["title"],
                        content=section.get("content", "")[:500],  # Truncate for preview
                        page=section.get("page"),
                        section_type="section",
                    )
                )
                if len(results) >= limit:
                    return results

        # Search in annexes
        for annex in self.data.get("structure", {}).get("annexes", []):
            for control in annex.get("controls", []):
                if (
                    query_lower in control.get("content", "").lower()
                    or query_lower in control.get("title", "").lower()
                ):
                    results.append(
                        SearchResult(
                            standard_id=self.metadata.standard_id,
                            clause_id=control["id"],
                            title=control["title"],
                            content=control.get("content", "")[:500],
                            page=control.get("page"),
                            section_type=f"Annex {annex['id']} - {control.get('category', 'control')}",
                        )
                    )
                    if len(results) >= limit:
                        return results

        return results

    def _iterate_sections(self, sections: List[Dict]) -> List[Dict]:
        """Recursively iterate through sections and subsections."""
        for section in sections:
            yield section
            # Recursively iterate subsections
            if "subsections" in section:
                yield from self._iterate_sections(section["subsections"])

    def get_clause(self, clause_id: str) -> Optional[SearchResult]:
        """Get a specific clause by ID."""
        # Search in sections
        for section in self._iterate_sections(self.data.get("structure", {}).get("sections", [])):
            if section["id"] == clause_id:
                return SearchResult(
                    standard_id=self.metadata.standard_id,
                    clause_id=section["id"],
                    title=section["title"],
                    content=section.get("content", ""),
                    page=section.get("page"),
                    section_type="section",
                )

        # Search in annexes
        for annex in self.data.get("structure", {}).get("annexes", []):
            for control in annex.get("controls", []):
                if control["id"] == clause_id:
                    return SearchResult(
                        standard_id=self.metadata.standard_id,
                        clause_id=control["id"],
                        title=control["title"],
                        content=control.get("content", ""),
                        page=control.get("page"),
                        section_type=f"Annex {annex['id']} - {control.get('category', 'control')}",
                    )

        return None

    def get_all_clauses(self) -> List[SearchResult]:
        """Get all clauses in the standard."""
        results = []

        # Get all sections
        for section in self._iterate_sections(self.data.get("structure", {}).get("sections", [])):
            results.append(
                SearchResult(
                    standard_id=self.metadata.standard_id,
                    clause_id=section["id"],
                    title=section["title"],
                    content=section.get("content", "")[:200],  # Brief preview
                    page=section.get("page"),
                    section_type="section",
                )
            )

        # Get all annex controls
        for annex in self.data.get("structure", {}).get("annexes", []):
            for control in annex.get("controls", []):
                results.append(
                    SearchResult(
                        standard_id=self.metadata.standard_id,
                        clause_id=control["id"],
                        title=control["title"],
                        content=control.get("content", "")[:200],
                        page=control.get("page"),
                        section_type=f"Annex {annex['id']}",
                    )
                )

        return results
