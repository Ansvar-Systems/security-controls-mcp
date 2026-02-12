"""Specialized extractor for IEC 62443 (Industrial Cybersecurity)."""

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


@register_extractor("iec_62443")
class IEC62443Extractor(BaseExtractor):
    """Specialized extractor for IEC 62443 (OT/ICS Security)."""

    def _detect_version(self, pdf_bytes: bytes) -> Tuple[str, VersionDetection, List[str]]:
        """Detect IEC 62443 part/version."""
        evidence: List[str] = []
        text = ""

        try:
            import pdfplumber
            with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
                for page in pdf.pages[:VERSION_DETECTION_MAX_PAGES]:
                    if page_text := page.extract_text():
                        text += page_text
        except Exception as e:
            logger.debug(f"PDF error: {e}")

        if not text:
            text = pdf_bytes.decode('utf-8', errors='ignore')

        # IEC 62443 has multiple parts (62443-2-1, 62443-3-3, etc.)
        if match := re.search(r"62443-(\d)-(\d)", text):
            part = f"{match.group(1)}-{match.group(2)}"
            evidence.append(f"Found IEC 62443-{part}")
            return (part, VersionDetection.DETECTED, evidence)

        if re.search(r"IEC\s*62443", text, re.IGNORECASE):
            evidence.append("Found IEC 62443 identifier")
            return ("3-3", VersionDetection.AMBIGUOUS, evidence)

        if re.search(r"Industrial.*?cybersecurity", text, re.IGNORECASE):
            evidence.append("Found industrial cybersecurity keywords")
            return ("3-3", VersionDetection.AMBIGUOUS, evidence)

        return ("unknown", VersionDetection.UNKNOWN, evidence)

    def _extract_controls(self, pdf_bytes: bytes) -> List[Control]:
        """Extract IEC 62443 requirements."""
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
        """Parse IEC 62443 requirements (SR, FR, CR format)."""
        controls: List[str] = []

        # IEC 62443-3-3 uses SR (Security Requirement), FR (Foundational Requirement)
        # Format: SR X.Y, FR X, CR X.Y
        pattern = r'((?:SR|FR|CR)\s*\d+(?:\.\d+)?)\s+(?:-\s*)?([A-Z][A-Za-z\s,\-\(\):]+?)(?:\n|$)'

        for match in re.finditer(pattern, text):
            req_id = match.group(1).replace(" ", "")
            title = match.group(2).strip()

            if len(title) < MIN_TITLE_LENGTH:
                continue

            # Categorize by prefix
            category = "Security Requirement"
            if req_id.startswith("FR"):
                category = "Foundational Requirement"
            elif req_id.startswith("CR"):
                category = "Component Requirement"

            controls.append(Control(
                id=req_id,
                title=title,
                content=title,
                page=page_num,
                category=category,
                parent=None
            ))

        return controls

    def extract(self, pdf_bytes: bytes) -> ExtractionResult:
        """Extract from IEC 62443 PDF."""
        start_time = time.time()
        warnings: List[str] = []

        version, detection, evidence = self._detect_version(pdf_bytes)
        controls = self._extract_controls(pdf_bytes)

        confidence_score = 0.3 if detection == VersionDetection.DETECTED else 0.15
        extracted_count = len(controls)

        if extracted_count >= 20:
            confidence_score += 0.7 * min(extracted_count / 50, 1.0)
        else:
            confidence_score += 0.7 * (extracted_count / 20)

        if extracted_count < 10:
            warnings.append(f"Sparse extraction: {extracted_count} requirements")

        return ExtractionResult(
            standard_id="iec_62443",
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
