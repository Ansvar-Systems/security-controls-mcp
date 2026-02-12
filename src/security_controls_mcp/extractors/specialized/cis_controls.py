"""Specialized extractor for CIS Controls."""

import io
import logging
import re
import time
from typing import List, Tuple

from ..base import BaseExtractor, Control, ExtractionResult, VersionDetection
from ..registry import register_extractor

logger = logging.getLogger(__name__)

VERSION_DETECTION_MAX_PAGES = 10


@register_extractor("cis_controls")
class CISControlsExtractor(BaseExtractor):
    """Specialized extractor for CIS Critical Security Controls."""

    def _detect_version(self, pdf_bytes: bytes) -> Tuple[str, VersionDetection, List[str]]:
        """Detect CIS Controls version."""
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

        # Version 8
        if re.search(r"CIS.*?Controls.*?v?8", text, re.IGNORECASE):
            evidence.append("Found CIS Controls v8")
            return ("v8", VersionDetection.DETECTED, evidence)

        # Version 7.1
        if re.search(r"CIS.*?Controls.*?v?7\.1", text, re.IGNORECASE):
            evidence.append("Found CIS Controls v7.1")
            return ("v7.1", VersionDetection.DETECTED, evidence)

        if re.search(r"CIS.*?(?:Critical\s+Security\s+)?Controls", text, re.IGNORECASE):
            evidence.append("Found CIS Controls")
            return ("v8", VersionDetection.AMBIGUOUS, evidence)

        return ("unknown", VersionDetection.UNKNOWN, evidence)

    def _extract_controls(self, pdf_bytes: bytes) -> List[Control]:
        """Extract CIS Controls."""
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
        """Parse CIS Controls from text."""
        controls: List[Control] = []

        # CIS Controls format: X.Y (e.g., 1.1, 4.3) or Control X
        pattern = r'(?:Control\s+)?(\d+(?:\.\d+)?)\s+([A-Z][A-Za-z\s,\-\(\):]+?)(?:\n|$)'

        for match in re.finditer(pattern, text):
            control_id = match.group(1)
            title = match.group(2).strip()

            if len(title) < 5:
                continue

            # CIS v8 has 18 controls
            main_control = control_id.split(".")[0]
            categories = {
                "1": "Inventory and Control of Enterprise Assets",
                "2": "Inventory and Control of Software Assets",
                "3": "Data Protection",
                "4": "Secure Configuration",
                "5": "Account Management",
                "6": "Access Control Management",
                "7": "Continuous Vulnerability Management",
                "8": "Audit Log Management",
                "9": "Email and Web Browser Protections",
                "10": "Malware Defenses",
                "11": "Data Recovery",
                "12": "Network Infrastructure Management",
                "13": "Network Monitoring and Defense",
                "14": "Security Awareness and Training",
                "15": "Service Provider Management",
                "16": "Application Software Security",
                "17": "Incident Response Management",
                "18": "Penetration Testing",
            }
            category = categories.get(main_control, "General")

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
        """Extract from CIS Controls PDF."""
        start_time = time.time()
        warnings: List[str] = []

        version, detection, evidence = self._detect_version(pdf_bytes)
        controls = self._extract_controls(pdf_bytes)

        confidence_score = 0.3 if detection == VersionDetection.DETECTED else 0.15
        extracted_count = len(controls)

        # CIS v8 has 153 safeguards across 18 controls
        if extracted_count >= 75:
            confidence_score += 0.7 * min(extracted_count / 150, 1.0)
        else:
            confidence_score += 0.7 * (extracted_count / 75)

        if extracted_count < 20:
            warnings.append(f"Sparse extraction: {extracted_count} controls")

        return ExtractionResult(
            standard_id="cis_controls",
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
