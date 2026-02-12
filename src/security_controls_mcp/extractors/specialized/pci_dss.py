"""Specialized extractor for PCI DSS (Payment Card Industry Data Security Standard)."""

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
MIN_CONTENT_LENGTH = 10


@register_extractor("pci_dss")
class PCIDSSExtractor(BaseExtractor):
    """Specialized extractor for PCI DSS."""

    def _detect_version(self, pdf_bytes: bytes) -> Tuple[str, VersionDetection, List[str]]:
        """Detect PCI DSS version."""
        evidence: List[str] = []
        text = ""

        try:
            import pdfplumber
            with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
                for page in pdf.pages[:VERSION_DETECTION_MAX_PAGES]:
                    if page_text := page.extract_text():
                        text += page_text
        except Exception as e:
            logger.debug(f"PDF parsing error: {e}")

        if not text:
            text = pdf_bytes.decode('utf-8', errors='ignore')

        # Version 4.0
        if re.search(r"PCI\s+DSS.*?v?4\.0", text, re.IGNORECASE):
            evidence.append("Found 'PCI DSS v4.0'")
            return ("4.0", VersionDetection.DETECTED, evidence)

        # Version 3.2.1
        if re.search(r"PCI\s+DSS.*?v?3\.2\.1", text, re.IGNORECASE):
            evidence.append("Found 'PCI DSS v3.2.1'")
            return ("3.2.1", VersionDetection.DETECTED, evidence)

        if re.search(r"Payment Card Industry", text, re.IGNORECASE):
            evidence.append("Found 'Payment Card Industry'")
            return ("4.0", VersionDetection.AMBIGUOUS, evidence)

        return ("unknown", VersionDetection.UNKNOWN, evidence)

    def _extract_controls(self, pdf_bytes: bytes) -> List[Control]:
        """Extract PCI DSS requirements."""
        controls: List[Control] = []

        try:
            import pdfplumber
            with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    if page_text := page.extract_text():
                        controls.extend(self._parse_controls(page_text, page_num + 1))
        except Exception as e:
            logger.debug(f"Extraction error: {e}")

        return controls

    def _parse_controls(self, text: str, page_num: int) -> List[Control]:
        """Parse PCI DSS requirements from text."""
        controls: List[Control] = []

        # PCI DSS format: Requirement X.Y.Z
        pattern = r'(?:Requirement\s+)?(\d+\.\d+(?:\.\d+)?)\s+([A-Z][A-Za-z\s,\-\(\):]+?)(?:\n|$)'

        for match in re.finditer(pattern, text):
            req_id = match.group(1)
            title = match.group(2).strip()

            if len(title) < MIN_TITLE_LENGTH:
                continue

            # Determine category from main requirement
            main_req = req_id.split(".")[0]
            categories = {
                "1": "Network Security",
                "2": "Configuration Management",
                "3": "Data Protection",
                "4": "Encryption",
                "5": "Malware Protection",
                "6": "Secure Development",
                "7": "Access Control",
                "8": "Identity Management",
                "9": "Physical Security",
                "10": "Logging and Monitoring",
                "11": "Security Testing",
                "12": "Security Policy",
            }
            category = categories.get(main_req, "General")

            # Determine parent
            parent = None
            parts = req_id.split(".")
            if len(parts) > 2:
                parent = ".".join(parts[:-1])

            controls.append(Control(
                id=req_id,
                title=title,
                content=title,
                page=page_num,
                category=category,
                parent=parent
            ))

        return controls

    def extract(self, pdf_bytes: bytes) -> ExtractionResult:
        """Extract requirements from PCI DSS PDF."""
        start_time = time.time()
        warnings: List[str] = []

        version, detection, evidence = self._detect_version(pdf_bytes)
        if version == "unknown":
            warnings.append("Could not detect PCI DSS version")

        controls = self._extract_controls(pdf_bytes)

        confidence_score = 0.0
        if detection == VersionDetection.DETECTED:
            confidence_score += 0.3
        elif detection == VersionDetection.AMBIGUOUS:
            confidence_score += 0.15

        # PCI DSS has ~300 requirements
        extracted_count = len(controls)
        if extracted_count >= 100:
            confidence_score += 0.7 * min(extracted_count / 300, 1.0)
        else:
            confidence_score += 0.7 * (extracted_count / 100)

        if extracted_count < 50:
            warnings.append(f"Sparse extraction: {extracted_count} requirements")

        return ExtractionResult(
            standard_id="pci_dss",
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
