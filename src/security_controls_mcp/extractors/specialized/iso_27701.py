"""Specialized extractor for ISO 27701 (Privacy Information Management)."""

import io
import logging
import re
import time
from typing import List, Tuple

from ..base import BaseExtractor, Control, ExtractionResult, VersionDetection
from ..registry import register_extractor

logger = logging.getLogger(__name__)

VERSION_DETECTION_MAX_PAGES = 10
MIN_TITLE_LENGTH = 5


@register_extractor("iso_27701")
class ISO27701Extractor(BaseExtractor):
    """Specialized extractor for ISO/IEC 27701 (Privacy)."""

    def _detect_version(self, pdf_bytes: bytes) -> Tuple[str, VersionDetection, List[str]]:
        """Detect ISO 27701 version."""
        evidence: List[str] = []
        text = ""

        try:
            import pdfplumber
            with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
                for page in pdf.pages[:VERSION_DETECTION_MAX_PAGES]:
                    if page_text := page.extract_text():
                        text += page_text
        except Exception as e:
            logger.debug(f"Error: {e}")

        if not text:
            text = pdf_bytes.decode('utf-8', errors='ignore')

        # ISO 27701:2019
        if re.search(r"27701:2019", text):
            evidence.append("Found '27701:2019'")
            return ("2019", VersionDetection.DETECTED, evidence)

        if re.search(r"ISO(?:/IEC)?\s*27701", text, re.IGNORECASE):
            evidence.append("Found ISO 27701 identifier")
            return ("2019", VersionDetection.AMBIGUOUS, evidence)

        if re.search(r"Privacy.*?Information.*?Management", text, re.IGNORECASE):
            evidence.append("Found PIMS keywords")
            return ("2019", VersionDetection.AMBIGUOUS, evidence)

        return ("unknown", VersionDetection.UNKNOWN, evidence)

    def _extract_controls(self, pdf_bytes: bytes) -> List[Control]:
        """Extract ISO 27701 controls."""
        controls: List[Control] = []

        try:
            import pdfplumber
            with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    if page_text := page.extract_text():
                        controls.extend(self._parse_controls(page_text, page_num + 1))
        except Exception as e:
            logger.debug(f"Error: {e}")

        return controls

    def _parse_controls(self, text: str, page_num: int) -> List[Control]:
        """Parse ISO 27701 controls (extends ISO 27002)."""
        controls: List[Control] = []

        # ISO 27701 extends ISO 27002 with additional controls
        # Format: X.Y.Z (e.g., 6.2.1) or Annex format
        pattern = r'(\d+\.\d+\.\d+)\s+([A-Z][A-Za-z\s,\-\(\):]+?)(?:\n|$)'

        for match in re.finditer(pattern, text):
            control_id = match.group(1)
            title = match.group(2).strip()

            if len(title) < MIN_TITLE_LENGTH:
                continue

            # Categorize by main clause
            main_clause = control_id.split(".")[0]
            categories = {
                "5": "PIMS-specific policies",
                "6": "Organization of information security",
                "7": "Human resource security",
                "8": "Asset management",
                "9": "Access control",
                "10": "Cryptography",
                "11": "Physical and environmental security",
                "12": "Operations security",
                "13": "Communications security",
                "14": "System acquisition, development and maintenance",
                "15": "Supplier relationships",
                "16": "Information security incident management",
                "17": "Information security aspects of business continuity",
                "18": "Compliance",
            }
            category = categories.get(main_clause, "Privacy Management")

            controls.append(Control(
                id=control_id,
                title=title,
                content=title,
                page=page_num,
                category=category,
                parent=None
            ))

        return controls

    def extract(self, pdf_bytes: bytes) -> ExtractionResult:
        """Extract from ISO 27701 PDF."""
        start_time = time.time()
        warnings: List[str] = []

        version, detection, evidence = self._detect_version(pdf_bytes)
        controls = self._extract_controls(pdf_bytes)

        confidence_score = 0.3 if detection == VersionDetection.DETECTED else 0.15
        extracted_count = len(controls)

        # ISO 27701 has additional controls on top of ISO 27002
        if extracted_count >= 30:
            confidence_score += 0.7 * min(extracted_count / 60, 1.0)
        else:
            confidence_score += 0.7 * (extracted_count / 30)

        if extracted_count < 15:
            warnings.append(f"Sparse extraction: {extracted_count} controls")

        return ExtractionResult(
            standard_id="iso_27701",
            version=version,
            version_detection=detection,
            version_evidence=evidence,
            controls=controls,
            expected_control_ids=None,
            missing_control_ids=None,
            confidence_score=confidence_score,
            extraction_method="specialized",
            extraction_duration_seconds=time.time() - start_time,
            warnings=warnings,
        )
