"""Specialized extractor for GDPR (EU General Data Protection Regulation)."""

import io
import logging
import re
import time
from typing import List, Tuple

from ..base import BaseExtractor, Control, ExtractionResult, VersionDetection
from ..registry import register_extractor

logger = logging.getLogger(__name__)

VERSION_DETECTION_MAX_PAGES = 10


@register_extractor("gdpr")
class GDPRExtractor(BaseExtractor):
    """Specialized extractor for GDPR."""

    def _detect_version(self, pdf_bytes: bytes) -> Tuple[str, VersionDetection, List[str]]:
        """Detect GDPR version."""
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

        # GDPR (Regulation 2016/679)
        if re.search(r"(?:Regulation|EU)\s*(?:\(EU\))?\s*2016/679", text):
            evidence.append("Found 'Regulation 2016/679'")
            return ("2016", VersionDetection.DETECTED, evidence)

        if re.search(r"General\s+Data\s+Protection\s+Regulation", text, re.IGNORECASE):
            evidence.append("Found GDPR identifier")
            return ("2016", VersionDetection.AMBIGUOUS, evidence)

        if re.search(r"GDPR", text):
            evidence.append("Found 'GDPR'")
            return ("2016", VersionDetection.AMBIGUOUS, evidence)

        return ("unknown", VersionDetection.UNKNOWN, evidence)

    def _extract_controls(self, pdf_bytes: bytes) -> List[Control]:
        """Extract GDPR articles."""
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
        """Parse GDPR articles."""
        controls: List[Control] = []

        # GDPR format: Article X or Article X(Y)
        pattern = r'Article\s+(\d+(?:\(\d+\))?)\s+(?:-\s+)?([A-Z][A-Za-z\s,\-\(\):]+?)(?:\n|$)'

        for match in re.finditer(pattern, text):
            article_id = f"Article {match.group(1)}"
            title = match.group(2).strip()

            if len(title) < 5:
                continue

            # Categorize by article range
            article_num = int(re.search(r'\d+', match.group(1)).group())
            if article_num <= 4:
                category = "General Provisions"
            elif article_num <= 11:
                category = "Principles"
            elif article_num <= 23:
                category = "Rights of Data Subject"
            elif article_num <= 43:
                category = "Controller and Processor"
            elif article_num <= 50:
                category = "Transfer of Personal Data"
            elif article_num <= 76:
                category = "Supervisory Authorities"
            elif article_num <= 84:
                category = "Remedies, Liability and Penalties"
            else:
                category = "Final Provisions"

            controls.append(Control(
                id=article_id,
                title=title,
                content=title,
                page=page_num,
                category=category,
                parent=None
            ))

        return controls

    def extract(self, pdf_bytes: bytes) -> ExtractionResult:
        """Extract from GDPR PDF."""
        start_time = time.time()
        warnings: List[str] = []

        version, detection, evidence = self._detect_version(pdf_bytes)
        controls = self._extract_controls(pdf_bytes)

        confidence_score = 0.3 if detection == VersionDetection.DETECTED else 0.15
        extracted_count = len(controls)

        # GDPR has 99 articles
        if extracted_count >= 50:
            confidence_score += 0.7 * min(extracted_count / 99, 1.0)
        else:
            confidence_score += 0.7 * (extracted_count / 50)

        if extracted_count < 20:
            warnings.append(f"Sparse extraction: {extracted_count} articles")

        return ExtractionResult(
            standard_id="gdpr",
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
