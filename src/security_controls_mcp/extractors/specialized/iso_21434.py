"""Specialized extractor for ISO 21434 (Automotive Cybersecurity)."""

import io
import logging
import re
import time
from typing import List, Tuple, Dict, Any, Optional

from ..base import BaseExtractor, Control, ExtractionResult, VersionDetection
from ..registry import register_extractor

logger = logging.getLogger(__name__)

# Configuration constants
VERSION_DETECTION_MAX_PAGES = 10
MIN_TITLE_LENGTH = 5
MIN_CONTENT_LENGTH = 10

# ISO 21434 clause categories (main clauses 5-14)
CLAUSE_CATEGORIES: Dict[str, str] = {
    "5": "Organizational Cybersecurity Management",
    "6": "Project Dependent Cybersecurity Management",
    "7": "Distributed Cybersecurity Activities",
    "8": "Continual Cybersecurity Activities",
    "9": "Concept Phase",
    "10": "Product Development",
    "11": "Cybersecurity Validation",
    "12": "Production",
    "13": "Operations and Maintenance",
    "14": "End of Cybersecurity Support and Decommissioning",
}

# Lifecycle phases
LIFECYCLE_PHASES = [
    "Management",
    "Concept",
    "Product Development",
    "Production",
    "Operations and Maintenance",
    "Decommissioning",
]


@register_extractor("iso_21434")
class ISO21434Extractor(BaseExtractor):
    """Specialized extractor for ISO 21434 (Automotive Cybersecurity)."""

    def _detect_version(self, pdf_bytes: bytes) -> Tuple[str, VersionDetection, List[str]]:
        """Detect ISO 21434 version from PDF content.

        Returns:
            Tuple of (version_string, detection_level, evidence_list)
        """
        evidence: List[str] = []
        text = ""

        try:
            import pdfplumber

            with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
                # Check first pages for version indicators
                max_pages = min(VERSION_DETECTION_MAX_PAGES, len(pdf.pages))

                for page in pdf.pages[:max_pages]:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text

        except ImportError:
            logger.debug("pdfplumber not available, using basic detection")
        except Exception as e:
            logger.debug(f"Error during PDF parsing: {e}")

        # Fallback: try to extract text directly
        if not text:
            try:
                text = pdf_bytes.decode('utf-8', errors='ignore')
            except Exception as e:
                logger.debug(f"Error during text extraction: {e}")
                return ("unknown", VersionDetection.UNKNOWN, evidence)

        # Look for explicit year indicators
        if re.search(r"21434:2021", text):
            evidence.append("Found '21434:2021' text")
            return ("2021", VersionDetection.DETECTED, evidence)

        if re.search(r"ISO(?:/SAE)?\s+21434", text, re.IGNORECASE):
            evidence.append("Found ISO 21434 identifier")
            # Check for publication date
            if re.search(r"2021", text):
                evidence.append("Found '2021' year")
                return ("2021", VersionDetection.DETECTED, evidence)
            # Default to 2021 (the main published version)
            return ("2021", VersionDetection.AMBIGUOUS, evidence)

        # Check for automotive cybersecurity keywords
        if re.search(r"(?:Road vehicles|Automotive).*?[Cc]ybersecurity", text):
            evidence.append("Found automotive cybersecurity keywords")
            return ("2021", VersionDetection.AMBIGUOUS, evidence)

        return ("unknown", VersionDetection.UNKNOWN, evidence)

    def _extract_clauses_2021(self, pdf_bytes: bytes) -> List[Control]:
        """Extract clauses from ISO 21434:2021 PDF.

        Returns:
            List of extracted Control objects (representing clauses)
        """
        controls: List[Control] = []

        try:
            import pdfplumber

            with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    page_text = page.extract_text()
                    if page_text:
                        page_controls = self._parse_clauses_from_text(
                            page_text, page_num + 1
                        )
                        controls.extend(page_controls)

        except ImportError:
            logger.debug("pdfplumber not available for 2021 extraction")
            # Fallback to basic extraction
            text = pdf_bytes.decode('utf-8', errors='ignore')
            controls = self._parse_clauses_from_text(text, 1)

        except Exception as e:
            logger.debug(f"Error during 2021 extraction: {e}")

        return controls

    def _parse_clauses_from_text(
        self, text: str, page_num: int
    ) -> List[Control]:
        """Parse ISO 21434 clauses from text.

        Args:
            text: Text content to parse
            page_num: Page number for extracted clauses

        Returns:
            List of Control objects found in text
        """
        controls: List[Control] = []

        # Pattern for ISO clauses: X or X.Y or X.Y.Z or X.Y.Z.W
        # Format: NUMBER[.NUMBER[.NUMBER[.NUMBER]]] TITLE
        # Examples: "5 Organizational cybersecurity" or "5.4.2 Risk assessment methodology"
        pattern = r'(\d+(?:\.\d+){0,3})\s+([A-Z][A-Za-z\s,\-\(\)]+?)(?:\n|$|\.(?=\s*\d+\.))'

        for match in re.finditer(pattern, text):
            clause_id = match.group(1)
            title = match.group(2).strip()

            # Validate
            if len(title) < MIN_TITLE_LENGTH:
                continue

            # Only extract clauses from main sections (5-14)
            main_clause = clause_id.split(".")[0]
            if main_clause not in CLAUSE_CATEGORIES:
                continue

            # Determine category
            category = CLAUSE_CATEGORIES.get(main_clause, "General")

            # Determine parent (if it's a sub-clause)
            parent = None
            parts = clause_id.split(".")
            if len(parts) > 2:
                # Has a parent (e.g., 5.4.2 has parent 5.4)
                parent = ".".join(parts[:-1])

            # Extract content (simplified)
            content = f"{title}"

            if len(content) >= MIN_CONTENT_LENGTH:
                controls.append(Control(
                    id=clause_id,
                    title=title,
                    content=content,
                    page=page_num,
                    category=category,
                    parent=parent
                ))

        return controls

    def extract(self, pdf_bytes: bytes) -> ExtractionResult:
        """Extract clauses from ISO 21434 PDF.

        Args:
            pdf_bytes: Raw PDF file bytes

        Returns:
            ExtractionResult with extracted clauses and metadata
        """
        start_time = time.time()
        warnings: List[str] = []

        # Detect version
        version, detection, evidence = self._detect_version(pdf_bytes)

        if version == "unknown":
            warnings.append("Could not detect ISO 21434 version")

        # Extract clauses based on version
        controls: List[Control] = []

        if version == "2021":
            controls = self._extract_clauses_2021(pdf_bytes)
        else:
            warnings.append(f"Unsupported version: {version}")

        # Calculate confidence
        extracted_count = len(controls)

        confidence_score = 0.0

        if detection == VersionDetection.DETECTED:
            confidence_score += 0.3
        elif detection == VersionDetection.AMBIGUOUS:
            confidence_score += 0.15

        # ISO 21434 has many clauses across 10 main sections
        # A reasonable extraction would have at least 20-30 clauses
        expected_min_clauses = 20
        if extracted_count >= expected_min_clauses:
            # Scale up to 0.7 for good extractions
            ratio = min(extracted_count / 50, 1.0)
            confidence_score += 0.7 * ratio
        else:
            # Partial credit for some extraction
            ratio = extracted_count / expected_min_clauses
            confidence_score += 0.7 * ratio

        # Check for missing major clauses
        extracted_main_clauses = set()
        for control in controls:
            main_clause = control.id.split(".")[0]
            extracted_main_clauses.add(main_clause)

        expected_main_clauses = set(CLAUSE_CATEGORIES.keys())
        missing_main_clauses = expected_main_clauses - extracted_main_clauses

        if missing_main_clauses:
            warnings.append(
                f"Missing main clauses: {', '.join(sorted(missing_main_clauses))} "
                f"(extracted {len(extracted_main_clauses)} of {len(expected_main_clauses)})"
            )

        if extracted_count < expected_min_clauses:
            warnings.append(
                f"Sparse extraction: only {extracted_count} clauses extracted "
                f"(expected at least {expected_min_clauses})"
            )

        duration = time.time() - start_time

        return ExtractionResult(
            standard_id="iso_21434",
            version=version,
            version_detection=detection,
            version_evidence=evidence,
            controls=controls,
            expected_control_ids=None,  # ISO 21434 doesn't have fixed control IDs like ISO 27001
            missing_control_ids=None,
            confidence_score=confidence_score,
            extraction_method="specialized",
            extraction_duration_seconds=duration,
            warnings=warnings,
        )
