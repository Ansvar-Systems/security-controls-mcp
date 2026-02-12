"""ISO 27001 specialized extractor."""

import io
import re
import time
from typing import Any, Dict, List, Tuple

from ..base import BaseExtractor, Control, ExtractionResult, VersionDetection
from ..registry import register_extractor


@register_extractor("iso_27001")
class ISO27001Extractor(BaseExtractor):
    """Specialized extractor for ISO 27001 standards.

    Handles both ISO 27001:2022 (93 controls) and ISO 27001:2013 (114 controls).
    Uses heuristics to detect version and extract controls with high precision.
    """

    # Expected control counts and IDs by version
    VERSIONS: Dict[int, Dict[str, Any]] = {
        2022: {
            "count": 93,
            "expected_ids": [
                # Organizational Controls (A.5) - 37 controls
                "A.5.1",
                "A.5.2",
                "A.5.3",
                "A.5.4",
                "A.5.5",
                "A.5.6",
                "A.5.7",
                "A.5.8",
                "A.5.9",
                "A.5.10",
                "A.5.11",
                "A.5.12",
                "A.5.13",
                "A.5.14",
                "A.5.15",
                "A.5.16",
                "A.5.17",
                "A.5.18",
                "A.5.19",
                "A.5.20",
                "A.5.21",
                "A.5.22",
                "A.5.23",
                "A.5.24",
                "A.5.25",
                "A.5.26",
                "A.5.27",
                "A.5.28",
                "A.5.29",
                "A.5.30",
                "A.5.31",
                "A.5.32",
                "A.5.33",
                "A.5.34",
                "A.5.35",
                "A.5.36",
                "A.5.37",
                # People Controls (A.6) - 8 controls
                "A.6.1",
                "A.6.2",
                "A.6.3",
                "A.6.4",
                "A.6.5",
                "A.6.6",
                "A.6.7",
                "A.6.8",
                # Physical Controls (A.7) - 14 controls
                "A.7.1",
                "A.7.2",
                "A.7.3",
                "A.7.4",
                "A.7.5",
                "A.7.6",
                "A.7.7",
                "A.7.8",
                "A.7.9",
                "A.7.10",
                "A.7.11",
                "A.7.12",
                "A.7.13",
                "A.7.14",
                # Technological Controls (A.8) - 34 controls
                "A.8.1",
                "A.8.2",
                "A.8.3",
                "A.8.4",
                "A.8.5",
                "A.8.6",
                "A.8.7",
                "A.8.8",
                "A.8.9",
                "A.8.10",
                "A.8.11",
                "A.8.12",
                "A.8.13",
                "A.8.14",
                "A.8.15",
                "A.8.16",
                "A.8.17",
                "A.8.18",
                "A.8.19",
                "A.8.20",
                "A.8.21",
                "A.8.22",
                "A.8.23",
                "A.8.24",
                "A.8.25",
                "A.8.26",
                "A.8.27",
                "A.8.28",
                "A.8.29",
                "A.8.30",
                "A.8.31",
                "A.8.32",
                "A.8.33",
                "A.8.34",
            ],
        },
        2013: {
            "count": 114,
            "expected_ids": [],  # To be added in future tasks
        },
    }

    def _detect_version(
        self, pdf_bytes: bytes
    ) -> Tuple[str, VersionDetection, List[str]]:
        """Detect ISO 27001 version from PDF content.

        Args:
            pdf_bytes: Raw bytes of the ISO 27001 PDF document.

        Returns:
            Tuple of (version_string, detection_level, evidence_list)
            - version_string: "2022", "2013", or "unknown"
            - detection_level: DETECTED, AMBIGUOUS, or UNKNOWN
            - evidence_list: List of text snippets supporting the detection

        Note:
            Analyzes first 5 pages only for performance.
            Uses case-insensitive matching.
        """
        evidence: List[str] = []

        # Try to import pdfplumber
        try:
            import pdfplumber
        except ImportError:
            # If pdfplumber not available, try simple text extraction
            try:
                text = pdf_bytes.decode("utf-8", errors="ignore").lower()
            except Exception:
                return ("unknown", VersionDetection.UNKNOWN, [])
        else:
            # Use pdfplumber to extract text from first 5 pages
            try:
                import io
                with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
                    text_parts = []
                    # Extract from first 5 pages only for performance
                    for page in pdf.pages[:5]:
                        page_text = page.extract_text()
                        if page_text:
                            text_parts.append(page_text)
                    text = "\n".join(text_parts).lower()
            except Exception:
                # Fall back to simple decoding if pdfplumber fails
                try:
                    text = pdf_bytes.decode("utf-8", errors="ignore").lower()
                except Exception:
                    return ("unknown", VersionDetection.UNKNOWN, [])

        if not text or len(text.strip()) == 0:
            return ("unknown", VersionDetection.UNKNOWN, [])

        # Version detection patterns

        # 1. Check for explicit year references (highest confidence)
        year_2022_patterns = [
            r"iso/iec\s+27001:2022",
            r"iso\s+27001:2022",
            r"27001:2022",
        ]

        year_2013_patterns = [
            r"iso/iec\s+27001:2013",
            r"iso\s+27001:2013",
            r"27001:2013",
        ]

        has_2022_year = False
        has_2013_year = False

        for pattern in year_2022_patterns:
            if re.search(pattern, text):
                has_2022_year = True
                # Extract the matching text for evidence
                match = re.search(pattern, text)
                if match:
                    evidence.append(f"Found year reference: {match.group(0)}")
                break

        for pattern in year_2013_patterns:
            if re.search(pattern, text):
                has_2013_year = True
                # Extract the matching text for evidence
                match = re.search(pattern, text)
                if match:
                    evidence.append(f"Found year reference: {match.group(0)}")
                break

        # 2. Check for control count patterns (medium confidence)
        control_93_pattern = r"93\s+control"
        control_114_pattern = r"114\s+control"

        has_93_controls = re.search(control_93_pattern, text) is not None
        has_114_controls = re.search(control_114_pattern, text) is not None

        if has_93_controls:
            evidence.append("Found control count: 93 controls")
        if has_114_controls:
            evidence.append("Found control count: 114 controls")

        # 3. Check for version-specific control patterns (lower confidence)

        # 2022 version has A.5 (Organizational), A.6 (People), A.7 (Physical), A.8 (Technological)
        has_2022_categories = (
            re.search(r"a\.5\s+(organizational|organisation)", text) is not None
            or re.search(r"a\.6\s+people", text) is not None
            or re.search(r"a\.7\s+physical", text) is not None
            or re.search(r"a\.8\s+technological", text) is not None
        )

        # 2013 version has A.5 through A.18 (14 categories)
        # Key indicators: A.9 (Access control), A.12 (Operations), A.18 (Compliance)
        has_2013_categories = (
            re.search(r"a\.9\s+access\s+control", text) is not None
            or re.search(r"a\.12\s+operations", text) is not None
            or re.search(r"a\.18\s+compliance", text) is not None
        )

        if has_2022_categories:
            evidence.append("Found 2022 control categories (A.5-A.8)")
        if has_2013_categories:
            evidence.append("Found 2013 control categories (A.5-A.18)")

        # Determine version based on patterns

        # If explicit year found, return DETECTED (after gathering all evidence)
        if has_2022_year:
            return ("2022", VersionDetection.DETECTED, evidence)
        if has_2013_year:
            return ("2013", VersionDetection.DETECTED, evidence)

        # No explicit year - use pattern scoring (AMBIGUOUS if found)

        # 2022 indicators
        score_2022 = 0
        if has_93_controls:
            score_2022 += 2
        if has_2022_categories:
            score_2022 += 1

        # 2013 indicators
        score_2013 = 0
        if has_114_controls:
            score_2013 += 2
        if has_2013_categories:
            score_2013 += 1

        if score_2022 > score_2013 and score_2022 > 0:
            return ("2022", VersionDetection.AMBIGUOUS, evidence)
        elif score_2013 > score_2022 and score_2013 > 0:
            return ("2013", VersionDetection.AMBIGUOUS, evidence)
        else:
            # No clear indicators found
            return ("unknown", VersionDetection.UNKNOWN, [])

    def _extract_controls_2022(self, pdf_bytes: bytes) -> List[Control]:
        """Extract controls from ISO 27001:2022 PDF.

        Args:
            pdf_bytes: Raw bytes of the ISO 27001:2022 PDF document.

        Returns:
            List of Control objects extracted from the PDF.

        Note:
            Handles control ID pattern matching with spacing variations.
            Sets categories based on A.X prefix (5=Org, 6=People, 7=Physical, 8=Tech).
            Extracts control titles and content until next control or section.
        """
        controls: List[Control] = []

        # Try to use pdfplumber for better text extraction
        try:
            import pdfplumber

            with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    page_text = page.extract_text()
                    if page_text:
                        # Extract controls from this page
                        page_controls = self._parse_controls_from_text(
                            page_text, page_num + 1
                        )
                        controls.extend(page_controls)
        except ImportError:
            # Fall back to simple text extraction if pdfplumber not available
            try:
                text = pdf_bytes.decode("utf-8", errors="ignore")
                page_controls = self._parse_controls_from_text(text, 1)
                controls.extend(page_controls)
            except Exception:
                # If all extraction methods fail, return empty list
                return []
        except Exception:
            # If pdfplumber fails, try simple text extraction
            try:
                text = pdf_bytes.decode("utf-8", errors="ignore")
                page_controls = self._parse_controls_from_text(text, 1)
                controls.extend(page_controls)
            except Exception:
                return []

        return controls

    def _parse_controls_from_text(self, text: str, page_num: int) -> List[Control]:
        """Parse controls from text content.

        Args:
            text: Text content to parse.
            page_num: Page number for tracking.

        Returns:
            List of Control objects found in the text.
        """
        controls: List[Control] = []

        # Control ID pattern: A.X.Y (with possible spacing variations)
        # Matches: A.5.1, A.5.1 , A 5 1, etc.
        control_pattern = r"A[\.\s]?(\d+)[\.\s]?(\d+)"

        # Find all control IDs in the text
        matches = list(re.finditer(control_pattern, text))

        for i, match in enumerate(matches):
            # Extract control ID parts
            category_num = match.group(1)
            control_num = match.group(2)
            control_id = f"A.{category_num}.{control_num}"

            # Only process if this is an expected control ID
            if control_id not in self.VERSIONS[2022]["expected_ids"]:
                continue

            # Determine category based on A.X prefix
            category_map = {
                "5": "Organizational",
                "6": "People",
                "7": "Physical",
                "8": "Technological",
            }
            category = category_map.get(category_num, "Unknown")

            # Set parent (e.g., A.5.1 -> A.5)
            parent = f"A.{category_num}"

            # Extract title (text after control ID on same line or next line)
            start_pos = match.end()
            # Find the end of the line with the control ID
            line_end = text.find("\n", start_pos)
            if line_end == -1:
                line_end = len(text)

            # Title is the rest of the line after control ID
            title_line = text[start_pos:line_end].strip()

            # If title is empty or very short, check next line
            if len(title_line) < 3:
                next_line_start = line_end + 1
                next_line_end = text.find("\n", next_line_start)
                if next_line_end == -1:
                    next_line_end = len(text)
                title_line = text[next_line_start:next_line_end].strip()

            title = title_line

            # Extract content (from after title to next control or end)
            content_start = line_end + 1

            # Find the next control ID or end of content
            if i + 1 < len(matches):
                content_end = matches[i + 1].start()
            else:
                content_end = len(text)

            content = text[content_start:content_end].strip()

            # Clean up content (remove excessive whitespace)
            content = " ".join(content.split())

            # Create control object
            control = Control(
                id=control_id,
                title=title,
                content=content,
                page=page_num,
                category=category,
                parent=parent,
            )
            controls.append(control)

        return controls

    def extract(self, pdf_bytes: bytes) -> ExtractionResult:
        """Extract controls from ISO 27001 PDF.

        Args:
            pdf_bytes: Raw bytes of the ISO 27001 PDF document.

        Returns:
            ExtractionResult with extracted controls and metadata.
        """
        start_time = time.time()

        # Detect version
        version, version_detection, version_evidence = self._detect_version(pdf_bytes)

        # Initialize variables
        controls: List[Control] = []
        extraction_method = "version_detection_only"
        warnings: List[str] = []
        expected_control_ids: List[str] = []
        missing_control_ids: List[str] = []
        confidence_score = 0.0

        # Extract controls based on version
        if version == "2022":
            extraction_method = "specialized_iso_27001_2022"
            controls = self._extract_controls_2022(pdf_bytes)

            # Get expected control IDs for validation
            expected_control_ids = self.VERSIONS[2022]["expected_ids"]

            # Calculate missing controls
            extracted_ids = [c.id for c in controls]
            missing_control_ids = [
                cid for cid in expected_control_ids if cid not in extracted_ids
            ]

            # Calculate confidence score based on completeness
            if len(expected_control_ids) > 0:
                confidence_score = len(extracted_ids) / len(expected_control_ids)
            else:
                confidence_score = 0.0

            # Add warnings for missing controls
            if len(missing_control_ids) > 0:
                warnings.append(
                    f"Missing {len(missing_control_ids)} of {len(expected_control_ids)} "
                    f"expected controls ({confidence_score:.1%} complete)"
                )

        elif version == "2013":
            # 2013 extraction not yet implemented
            warnings.append("ISO 27001:2013 extraction not yet implemented")
            extraction_method = "not_implemented_2013"

        else:
            # Unknown version
            warnings.append("Could not detect ISO 27001 version")
            extraction_method = "version_detection_failed"

        # Calculate duration
        duration = time.time() - start_time

        return ExtractionResult(
            standard_id="iso_27001",
            version=version,
            version_detection=version_detection,
            version_evidence=version_evidence,
            controls=controls,
            expected_control_ids=expected_control_ids if expected_control_ids else None,
            missing_control_ids=(
                missing_control_ids
                if expected_control_ids  # Only set if we have expected IDs
                else None
            ),
            confidence_score=confidence_score,
            extraction_method=extraction_method,
            extraction_duration_seconds=duration,
            warnings=warnings,
        )
