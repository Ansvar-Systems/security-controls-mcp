"""Specialized extractor for NIST AI RMF (AI Risk Management Framework)."""

import io
import logging
import re
import time
from typing import List, Tuple

from ..base import BaseExtractor, Control, ExtractionResult, VersionDetection
from ..registry import register_extractor

logger = logging.getLogger(__name__)

VERSION_DETECTION_MAX_PAGES = 10


@register_extractor("nist_ai_rmf")
class NISTAIRMFExtractor(BaseExtractor):
    """Specialized extractor for NIST AI Risk Management Framework."""

    def _detect_version(self, pdf_bytes: bytes) -> Tuple[str, VersionDetection, List[str]]:
        """Detect NIST AI RMF version."""
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

        # NIST AI 100-1
        if re.search(r"(?:NIST\s+)?AI\s+100-1", text, re.IGNORECASE):
            evidence.append("Found 'AI 100-1'")
            return ("1.0", VersionDetection.DETECTED, evidence)

        if re.search(r"AI\s+Risk\s+Management\s+Framework", text, re.IGNORECASE):
            evidence.append("Found AI RMF identifier")
            return ("1.0", VersionDetection.AMBIGUOUS, evidence)

        if re.search(r"NIST.*?Trustworthy.*?AI", text, re.IGNORECASE):
            evidence.append("Found NIST trustworthy AI keywords")
            return ("1.0", VersionDetection.AMBIGUOUS, evidence)

        return ("unknown", VersionDetection.UNKNOWN, evidence)

    def _extract_controls(self, pdf_bytes: bytes) -> List[Control]:
        """Extract NIST AI RMF suggested actions."""
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
        """Parse NIST AI RMF functions and suggested actions."""
        controls: List[Control] = []

        # NIST AI RMF uses functions: GOVERN, MAP, MEASURE, MANAGE
        # Format: GOVERN-1.1, MAP-2.3, etc.
        pattern = r'((?:GOVERN|MAP|MEASURE|MANAGE)-\d+\.\d+)\s*[:.]?\s*([A-Z][A-Za-z\s,\-\(\):]+?)(?:\n|$)'

        for match in re.finditer(pattern, text):
            control_id = match.group(1)
            title = match.group(2).strip()

            if len(title) < 5:
                continue

            # Categorize by function
            function = control_id.split("-")[0]
            categories = {
                "GOVERN": "Governance",
                "MAP": "Map Context",
                "MEASURE": "Measure Risks",
                "MANAGE": "Manage Risks",
            }
            category = categories.get(function, "AI Risk Management")

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
        """Extract from NIST AI RMF PDF."""
        start_time = time.time()
        warnings: List[str] = []

        version, detection, evidence = self._detect_version(pdf_bytes)
        controls = self._extract_controls(pdf_bytes)

        confidence_score = 0.3 if detection == VersionDetection.DETECTED else 0.15
        extracted_count = len(controls)

        # NIST AI RMF has suggested actions across 4 functions
        if extracted_count >= 20:
            confidence_score += 0.7 * min(extracted_count / 40, 1.0)
        else:
            confidence_score += 0.7 * (extracted_count / 20)

        if extracted_count < 10:
            warnings.append(f"Sparse extraction: {extracted_count} actions")

        return ExtractionResult(
            standard_id="nist_ai_rmf",
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
