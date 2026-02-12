"""Specialized extractor for ISO 42001 (AI Management System)."""

import io
import logging
import re
import time
from typing import List, Tuple

from ..base import BaseExtractor, Control, ExtractionResult, VersionDetection
from ..registry import register_extractor

logger = logging.getLogger(__name__)

VERSION_DETECTION_MAX_PAGES = 10


@register_extractor("iso_42001")
class ISO42001Extractor(BaseExtractor):
    """Specialized extractor for ISO/IEC 42001 (AI Management System)."""

    def _detect_version(self, pdf_bytes: bytes) -> Tuple[str, VersionDetection, List[str]]:
        """Detect ISO 42001 version."""
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

        # ISO 42001:2023
        if re.search(r"42001:2023", text):
            evidence.append("Found '42001:2023'")
            return ("2023", VersionDetection.DETECTED, evidence)

        if re.search(r"ISO(?:/IEC)?\s*42001", text, re.IGNORECASE):
            evidence.append("Found ISO 42001 identifier")
            return ("2023", VersionDetection.AMBIGUOUS, evidence)

        if re.search(r"(?:Artificial\s+Intelligence|AI).*?Management\s+System", text, re.IGNORECASE):
            evidence.append("Found AI Management System keywords")
            return ("2023", VersionDetection.AMBIGUOUS, evidence)

        return ("unknown", VersionDetection.UNKNOWN, evidence)

    def _extract_controls(self, pdf_bytes: bytes) -> List[Control]:
        """Extract ISO 42001 controls."""
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
        """Parse ISO 42001 controls."""
        controls: List[Control] = []

        # ISO 42001 follows similar structure to ISO 27001
        # Clause format: X.Y or X.Y.Z
        pattern = r'(\d+\.\d+(?:\.\d+)?)\s+([A-Z][A-Za-z\s,\-\(\):]+?)(?:\n|$)'

        for match in re.finditer(pattern, text):
            control_id = match.group(1)
            title = match.group(2).strip()

            if len(title) < 5:
                continue

            # Categorize by main clause
            main_clause = control_id.split(".")[0]
            categories = {
                "4": "Context of the Organization",
                "5": "Leadership",
                "6": "Planning",
                "7": "Support",
                "8": "Operation",
                "9": "Performance Evaluation",
                "10": "Improvement",
            }
            category = categories.get(main_clause, "AI Management")

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
        """Extract from ISO 42001 PDF."""
        start_time = time.time()
        warnings: List[str] = []

        version, detection, evidence = self._detect_version(pdf_bytes)
        controls = self._extract_controls(pdf_bytes)

        confidence_score = 0.3 if detection == VersionDetection.DETECTED else 0.15
        extracted_count = len(controls)

        if extracted_count >= 20:
            confidence_score += 0.7 * min(extracted_count / 40, 1.0)
        else:
            confidence_score += 0.7 * (extracted_count / 20)

        if extracted_count < 10:
            warnings.append(f"Sparse extraction: {extracted_count} clauses")

        return ExtractionResult(
            standard_id="iso_42001",
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
