"""Specialized extractor for CCPA/CPRA (California Privacy Rights Act)."""

import io
import logging
import re
import time
from typing import List, Tuple

from ..base import BaseExtractor, Control, ExtractionResult, VersionDetection
from ..registry import register_extractor

logger = logging.getLogger(__name__)

VERSION_DETECTION_MAX_PAGES = 10


@register_extractor("ccpa")
class CCPAExtractor(BaseExtractor):
    """Specialized extractor for CCPA/CPRA."""

    def _detect_version(self, pdf_bytes: bytes) -> Tuple[str, VersionDetection, List[str]]:
        """Detect CCPA/CPRA version."""
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

        # CPRA (2020 amendment)
        if re.search(r"(?:CPRA|California\s+Privacy\s+Rights\s+Act)", text, re.IGNORECASE):
            evidence.append("Found CPRA")
            if re.search(r"2020|Proposition\s+24", text):
                evidence.append("Found 2020/Prop 24")
                return ("2020_cpra", VersionDetection.DETECTED, evidence)
            return ("2020_cpra", VersionDetection.AMBIGUOUS, evidence)

        # CCPA (original 2018)
        if re.search(r"(?:CCPA|California\s+Consumer\s+Privacy\s+Act)", text, re.IGNORECASE):
            evidence.append("Found CCPA")
            if re.search(r"2018|AB\s*375", text):
                evidence.append("Found 2018/AB 375")
                return ("2018_ccpa", VersionDetection.DETECTED, evidence)
            return ("2018_ccpa", VersionDetection.AMBIGUOUS, evidence)

        return ("unknown", VersionDetection.UNKNOWN, evidence)

    def _extract_controls(self, pdf_bytes: bytes) -> List[Control]:
        """Extract CCPA sections."""
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
        """Parse CCPA sections."""
        controls: List[Control] = []

        # CCPA format: Section 1798.XXX or §1798.XXX
        pattern = r'(?:Section|§)\s*(1798\.\d+)\s+([A-Z][A-Za-z\s,\-\(\):]+?)(?:\n|$)'

        for match in re.finditer(pattern, text):
            section_id = f"Section {match.group(1)}"
            title = match.group(2).strip()

            if len(title) < 5:
                continue

            # Categorize by section number
            section_num = int(match.group(1).split(".")[1])
            if section_num < 110:
                category = "Definitions"
            elif section_num < 120:
                category = "Consumer Rights"
            elif section_num < 140:
                category = "Business Obligations"
            elif section_num < 150:
                category = "Enforcement"
            elif section_num < 160:
                category = "Service Providers"
            else:
                category = "General Provisions"

            controls.append(Control(
                id=section_id,
                title=title,
                content=title,
                page=page_num,
                category=category,
                parent=None
            ))

        return controls

    def extract(self, pdf_bytes: bytes) -> ExtractionResult:
        """Extract from CCPA/CPRA PDF."""
        start_time = time.time()
        warnings: List[str] = []

        version, detection, evidence = self._detect_version(pdf_bytes)
        controls = self._extract_controls(pdf_bytes)

        confidence_score = 0.3 if detection == VersionDetection.DETECTED else 0.15
        extracted_count = len(controls)

        # CCPA has ~50 main sections
        if extracted_count >= 25:
            confidence_score += 0.7 * min(extracted_count / 50, 1.0)
        else:
            confidence_score += 0.7 * (extracted_count / 25)

        if extracted_count < 10:
            warnings.append(f"Sparse extraction: {extracted_count} sections")

        return ExtractionResult(
            standard_id="ccpa",
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
