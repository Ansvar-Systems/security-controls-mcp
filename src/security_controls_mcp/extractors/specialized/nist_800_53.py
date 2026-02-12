"""Specialized extractor for NIST 800-53."""

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
MIN_TITLE_LENGTH = 3
MIN_CONTENT_LENGTH = 10

# NIST 800-53 control families
CONTROL_FAMILIES = {
    "AC": "Access Control",
    "AU": "Audit and Accountability",
    "AT": "Awareness and Training",
    "CM": "Configuration Management",
    "CP": "Contingency Planning",
    "IA": "Identification and Authentication",
    "IR": "Incident Response",
    "MA": "Maintenance",
    "MP": "Media Protection",
    "PS": "Personnel Security",
    "PE": "Physical and Environmental Protection",
    "PL": "Planning",
    "PM": "Program Management",
    "RA": "Risk Assessment",
    "CA": "Assessment, Authorization, and Monitoring",
    "SC": "System and Communications Protection",
    "SI": "System and Information Integrity",
    "SA": "System and Services Acquisition",
    "SR": "Supply Chain Risk Management",
    "PT": "PII Processing and Transparency",
}

# Expected control counts per version
VERSIONS: Dict[str, Dict[str, Any]] = {
    "r5": {
        "count": 320,
        "expected_ids": []  # Populated below
    },
    "r4": {
        "count": 946,  # Including enhancements
        "expected_ids": []
    }
}

# Generate expected control IDs for R5 (320 base controls)
# Actual counts per family in R5:
# AC=25, AT=5, AU=16, CA=9, CM=14, CP=13, IA=12, IR=10, MA=6, MP=8,
# PE=23, PL=11, PM=33, PS=9, PT=8, RA=10, SA=22, SC=51, SI=23, SR=12
_r5_control_counts = {
    "AC": 25, "AT": 5, "AU": 16, "CA": 9, "CM": 14, "CP": 13, "IA": 12,
    "IR": 10, "MA": 6, "MP": 8, "PE": 23, "PL": 11, "PM": 33, "PS": 9,
    "PT": 8, "RA": 10, "SA": 22, "SC": 51, "SI": 23, "SR": 12
}

for family, count in _r5_control_counts.items():
    for i in range(1, count + 1):
        VERSIONS["r5"]["expected_ids"].append(f"{family}-{i}")


@register_extractor("nist_800_53")
class NIST80053Extractor(BaseExtractor):
    """Specialized extractor for NIST 800-53."""

    def _detect_version(self, pdf_bytes: bytes) -> Tuple[str, VersionDetection, List[str]]:
        """Detect NIST 800-53 version from PDF content.

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

        # Look for explicit revision indicators
        if re.search(r"Revision\s+5", text, re.IGNORECASE):
            evidence.append("Found 'Revision 5' text")
            return ("r5", VersionDetection.DETECTED, evidence)

        if re.search(r"Rev(?:ision)?\.?\s+5", text, re.IGNORECASE):
            evidence.append("Found 'Rev. 5' text")
            return ("r5", VersionDetection.DETECTED, evidence)

        if re.search(r"September\s+2020", text):
            evidence.append("Found 'September 2020' publication date (R5)")
            return ("r5", VersionDetection.DETECTED, evidence)

        if re.search(r"Revision\s+4", text, re.IGNORECASE):
            evidence.append("Found 'Revision 4' text")
            return ("r4", VersionDetection.DETECTED, evidence)

        # Check for NIST 800-53 identifier
        if re.search(r"NIST\s+(?:SP\s+)?800-53", text, re.IGNORECASE):
            evidence.append("Found NIST 800-53 identifier")
            # Default to R5 if no explicit version
            return ("r5", VersionDetection.AMBIGUOUS, evidence)

        return ("unknown", VersionDetection.UNKNOWN, evidence)

    def _extract_controls_r5(self, pdf_bytes: bytes) -> List[Control]:
        """Extract controls from NIST 800-53 Revision 5 PDF.

        Returns:
            List of extracted Control objects
        """
        controls: List[Control] = []

        try:
            import pdfplumber

            with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    page_text = page.extract_text()
                    if page_text:
                        page_controls = self._parse_controls_r5_from_text(
                            page_text, page_num + 1
                        )
                        controls.extend(page_controls)

        except ImportError:
            logger.debug("pdfplumber not available for R5 extraction")
            # Fallback to basic extraction
            text = pdf_bytes.decode('utf-8', errors='ignore')
            controls = self._parse_controls_r5_from_text(text, 1)

        except Exception as e:
            logger.debug(f"Error during R5 extraction: {e}")

        return controls

    def _parse_controls_r5_from_text(
        self, text: str, page_num: int
    ) -> List[Control]:
        """Parse NIST 800-53 R5 controls from text.

        Args:
            text: Text content to parse
            page_num: Page number for extracted controls

        Returns:
            List of Control objects found in text
        """
        controls: List[Control] = []

        # Pattern for base controls: AC-1, AU-2, etc.
        # Format: FAMILY-NUMBER TITLE
        pattern = r'([A-Z]{2}-\d{1,2})\s+([A-Z][A-Za-z\s,\-]+?)(?:\n|$)'

        for match in re.finditer(pattern, text):
            control_id = match.group(1)
            title = match.group(2).strip()

            # Validate
            if len(title) < MIN_TITLE_LENGTH:
                continue

            # Determine family/category
            family = control_id.split("-")[0]
            category = CONTROL_FAMILIES.get(family, "Unknown")

            # Extract content (simplified - would need more sophisticated logic in production)
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

        # Pattern for control enhancements: AC-1(1), AU-2(3), etc.
        enhancement_pattern = r'([A-Z]{2}-\d{1,2})\((\d{1,2})\)\s+([A-Z][A-Za-z\s,\-]+?)(?:\n|$)'

        for match in re.finditer(enhancement_pattern, text):
            base_id = match.group(1)
            enhancement_num = match.group(2)
            title = match.group(3).strip()

            # Validate
            if len(title) < MIN_TITLE_LENGTH:
                continue

            control_id = f"{base_id}({enhancement_num})"

            # Determine family/category
            family = base_id.split("-")[0]
            category = CONTROL_FAMILIES.get(family, "Unknown")

            content = f"{title}"

            if len(content) >= MIN_CONTENT_LENGTH:
                controls.append(Control(
                    id=control_id,
                    title=title,
                    content=content,
                    page=page_num,
                    category=category,
                    parent=base_id
                ))

        return controls

    def extract(self, pdf_bytes: bytes) -> ExtractionResult:
        """Extract controls from NIST 800-53 PDF.

        Args:
            pdf_bytes: Raw PDF file bytes

        Returns:
            ExtractionResult with extracted controls and metadata
        """
        start_time = time.time()
        warnings: List[str] = []

        # Detect version
        version, detection, evidence = self._detect_version(pdf_bytes)

        if version == "unknown":
            warnings.append("Could not detect NIST 800-53 version")

        # Extract controls based on version
        controls: List[Control] = []

        if version == "r5":
            controls = self._extract_controls_r5(pdf_bytes)
        elif version == "r4":
            warnings.append("NIST 800-53 R4 extraction not yet implemented")
        else:
            warnings.append(f"Unsupported version: {version}")

        # Calculate confidence
        expected_count = VERSIONS.get(version, {}).get("count", 0)
        extracted_count = len(controls)

        confidence_score = 0.0

        if detection == VersionDetection.DETECTED:
            confidence_score += 0.3
        elif detection == VersionDetection.AMBIGUOUS:
            confidence_score += 0.1

        if expected_count > 0:
            extraction_ratio = min(extracted_count / expected_count, 1.0)
            confidence_score += 0.7 * extraction_ratio

        # Check for missing controls
        expected_ids = VERSIONS.get(version, {}).get("expected_ids", [])
        extracted_ids = [c.id for c in controls if "(" not in c.id]  # Base controls only
        missing_ids = [cid for cid in expected_ids if cid not in extracted_ids]

        if missing_ids:
            warnings.append(
                f"Missing {len(missing_ids)} expected controls "
                f"(extracted {extracted_count} of {expected_count})"
            )

        duration = time.time() - start_time

        return ExtractionResult(
            standard_id="nist_800_53",
            version=version,
            version_detection=detection,
            version_evidence=evidence,
            controls=controls,
            expected_control_ids=expected_ids if expected_ids else None,
            missing_control_ids=missing_ids if missing_ids else None,
            confidence_score=confidence_score,
            extraction_method="specialized",
            extraction_duration_seconds=duration,
            warnings=warnings,
        )
