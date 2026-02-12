"""Specialized extractor for SOC 2 (Trust Services Criteria)."""

import io
import logging
import re
import time
from typing import List, Tuple, Dict, Any

from ..base import BaseExtractor, Control, ExtractionResult, VersionDetection
from ..registry import register_extractor

logger = logging.getLogger(__name__)

# Configuration constants
VERSION_DETECTION_MAX_PAGES = 10
MIN_TITLE_LENGTH = 5
MIN_CONTENT_LENGTH = 10

# SOC 2 Trust Services Categories
TSC_CATEGORIES: Dict[str, str] = {
    "CC": "Common Criteria",
    "A": "Availability",
    "PI": "Processing Integrity",
    "C": "Confidentiality",
    "P": "Privacy",
}


@register_extractor("soc2")
class SOC2Extractor(BaseExtractor):
    """Specialized extractor for SOC 2 Trust Services Criteria."""

    def _detect_version(self, pdf_bytes: bytes) -> Tuple[str, VersionDetection, List[str]]:
        """Detect SOC 2 version from PDF content."""
        evidence: List[str] = []
        text = ""

        try:
            import pdfplumber
            with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
                max_pages = min(VERSION_DETECTION_MAX_PAGES, len(pdf.pages))
                for page in pdf.pages[:max_pages]:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text
        except ImportError:
            logger.debug("pdfplumber not available")
        except Exception as e:
            logger.debug(f"Error during PDF parsing: {e}")

        if not text:
            try:
                text = pdf_bytes.decode('utf-8', errors='ignore')
            except Exception as e:
                logger.debug(f"Error during text extraction: {e}")
                return ("unknown", VersionDetection.UNKNOWN, evidence)

        # Look for version indicators
        if re.search(r"SOC\s*2.*?2017", text, re.IGNORECASE):
            evidence.append("Found 'SOC 2 2017' text")
            return ("2017_tsc", VersionDetection.DETECTED, evidence)

        if re.search(r"Trust\s+Services\s+Criteria", text, re.IGNORECASE):
            evidence.append("Found 'Trust Services Criteria' text")
            if re.search(r"2017", text):
                evidence.append("Found '2017' year")
                return ("2017_tsc", VersionDetection.DETECTED, evidence)
            return ("2017_tsc", VersionDetection.AMBIGUOUS, evidence)

        if re.search(r"SOC\s*2", text, re.IGNORECASE):
            evidence.append("Found 'SOC 2' identifier")
            return ("2017_tsc", VersionDetection.AMBIGUOUS, evidence)

        return ("unknown", VersionDetection.UNKNOWN, evidence)

    def _extract_controls(self, pdf_bytes: bytes) -> List[Control]:
        """Extract SOC 2 controls from PDF."""
        controls: List[Control] = []

        try:
            import pdfplumber
            with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    page_text = page.extract_text()
                    if page_text:
                        page_controls = self._parse_controls_from_text(page_text, page_num + 1)
                        controls.extend(page_controls)
        except ImportError:
            logger.debug("pdfplumber not available")
            text = pdf_bytes.decode('utf-8', errors='ignore')
            controls = self._parse_controls_from_text(text, 1)
        except Exception as e:
            logger.debug(f"Error during extraction: {e}")

        return controls

    def _parse_controls_from_text(self, text: str, page_num: int) -> List[Control]:
        """Parse SOC 2 controls from text."""
        controls: List[Control] = []

        # Pattern for SOC 2 controls: PREFIX + NUMBER.NUMBER
        # Examples: CC1.1, CC2.1, A1.2, PI1.1, C1.1, P1.1
        pattern = r'((?:CC|A|PI|C|P)\d+\.\d+)\s+([A-Z][A-Za-z\s,\-\(\):]+?)(?:\n|$|\.(?=\s*(?:CC|A|PI|C|P)\d))'

        for match in re.finditer(pattern, text):
            control_id = match.group(1)
            title = match.group(2).strip()

            if len(title) < MIN_TITLE_LENGTH:
                continue

            # Determine category from prefix
            prefix = "".join([c for c in control_id if c.isalpha()])
            category = TSC_CATEGORIES.get(prefix, "Security")

            content = f"{title}"

            if len(content) >= MIN_CONTENT_LENGTH:
                controls.append(Control(
                    id=control_id,
                    title=title,
                    content=content,
                    page=page_num,
                    category=category,
                    parent=None
                ))

        return controls

    def extract(self, pdf_bytes: bytes) -> ExtractionResult:
        """Extract controls from SOC 2 PDF."""
        start_time = time.time()
        warnings: List[str] = []

        version, detection, evidence = self._detect_version(pdf_bytes)

        if version == "unknown":
            warnings.append("Could not detect SOC 2 version")

        controls = self._extract_controls(pdf_bytes)

        # Calculate confidence
        confidence_score = 0.0

        if detection == VersionDetection.DETECTED:
            confidence_score += 0.3
        elif detection == VersionDetection.AMBIGUOUS:
            confidence_score += 0.15

        # SOC 2 typically has ~100 criteria across all categories
        extracted_count = len(controls)
        if extracted_count >= 50:
            ratio = min(extracted_count / 100, 1.0)
            confidence_score += 0.7 * ratio
        else:
            ratio = extracted_count / 50
            confidence_score += 0.7 * ratio

        if extracted_count < 20:
            warnings.append(f"Sparse extraction: only {extracted_count} controls")

        duration = time.time() - start_time

        return ExtractionResult(
            standard_id="soc2",
            version=version,
            version_detection=detection,
            version_evidence=evidence,
            controls=controls,
            expected_control_ids=None,
            missing_control_ids=None,
            confidence_score=confidence_score,
            extraction_method="specialized",
            extraction_duration_seconds=duration,
            warnings=warnings,
        )
