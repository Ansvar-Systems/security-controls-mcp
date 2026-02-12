"""Base dataclasses for security standard extraction."""

import abc
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional


@dataclass
class Control:
    """Represents a single security control extracted from a standard."""

    id: str
    title: str
    content: str
    page: int
    category: str
    parent: Optional[str] = None


class VersionDetection(Enum):
    """Confidence levels for version detection."""

    DETECTED = "detected"
    AMBIGUOUS = "ambiguous"
    UNKNOWN = "unknown"


@dataclass
class ExtractionResult:
    """Results from extracting a security standard."""

    standard_id: str
    version: str
    version_detection: VersionDetection
    version_evidence: List[str]
    controls: List[Control]
    expected_control_ids: Optional[List[str]]
    missing_control_ids: Optional[List[str]]
    confidence_score: float
    extraction_method: str
    extraction_duration_seconds: float
    warnings: List[str]


@dataclass
class ExtractionComparison:
    """Comparison when both specialized and generic extractors run."""

    specialized: ExtractionResult
    generic: ExtractionResult
    controls_in_both: List[str]
    unique_to_specialized: List[str]
    unique_to_generic: List[str]
    recommendation: str


class BaseExtractor(abc.ABC):
    """Abstract base class for all security standard extractors.

    All specialized extractors (ISO 27001, NIST 800-53, etc.) and the generic
    extractor must inherit from this class and implement the extract() method.

    This ensures a consistent interface for all extractors.
    """

    @abc.abstractmethod
    def extract(self, pdf_bytes: bytes) -> ExtractionResult:
        """Extract controls from a PDF document.

        Args:
            pdf_bytes: Raw bytes of the PDF document to extract from.

        Returns:
            ExtractionResult containing extracted controls, version info,
            and metadata about the extraction process.

        Raises:
            Exception: May raise various exceptions during PDF processing.
        """
        pass
