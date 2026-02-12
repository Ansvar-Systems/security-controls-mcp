"""Registry for auto-discovering specialized extractors."""

from typing import Dict, Optional, Type

# Global registry of specialized extractors
SPECIALIZED_EXTRACTORS: Dict[str, Type] = {}


def register_extractor(standard_pattern: str):
    """
    Decorator to register a specialized extractor.

    Args:
        standard_pattern: Standard identifier pattern (e.g., "iso_27001")

    Returns:
        Decorator function

    Example:
        @register_extractor("iso_27001")
        class ISO27001Extractor(BaseExtractor):
            ...
    """

    def decorator(cls):
        SPECIALIZED_EXTRACTORS[standard_pattern] = cls
        return cls

    return decorator


def get_extractor(standard_pattern: str) -> Optional[Type]:
    """
    Get extractor class for a standard pattern.

    Args:
        standard_pattern: Standard identifier pattern

    Returns:
        Extractor class or None if not found
    """
    return SPECIALIZED_EXTRACTORS.get(standard_pattern)
