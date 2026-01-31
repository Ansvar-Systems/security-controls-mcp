"""PDF extraction for security standards."""

import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

import pdfplumber


def extract_standard(
    pdf_path: Path,
    standard_id: str,
    title: str,
    version: str,
    purchased_from: str,
    purchase_date: str,
) -> Dict[str, Any]:
    """Extract a standard from PDF.

    Args:
        pdf_path: Path to PDF file
        standard_id: Unique identifier for the standard
        title: Full title of the standard
        version: Version string
        purchased_from: Where it was purchased
        purchase_date: When it was purchased

    Returns:
        Dictionary with metadata and structure
    """
    # Open PDF and extract text
    with pdfplumber.open(pdf_path) as pdf:
        total_pages = len(pdf.pages)

        # Extract text from all pages
        pages_text = []
        for page_num, page in enumerate(pdf.pages, start=1):
            text = page.extract_text() or ""
            pages_text.append({"page": page_num, "text": text})

    # Detect structure
    sections = _detect_sections(pages_text)
    annexes = _detect_annexes(pages_text)

    # Build metadata
    metadata = {
        "standard_id": standard_id,
        "title": title,
        "version": version,
        "purchased_from": purchased_from,
        "purchase_date": purchase_date,
        "imported_date": datetime.now().isoformat(),
        "license": "Proprietary - Licensed to individual user",
        "pages": total_pages,
        "restrictions": [
            "Personal use only",
            "No redistribution",
            "No derivative works without permission",
        ],
    }

    # Build structure
    structure = {
        "metadata": metadata,
        "sections": sections,
        "annexes": annexes,
    }

    # Calculate stats
    total_clauses = len(sections)
    for annex in annexes:
        total_clauses += len(annex.get("controls", []))

    stats = {
        "pages": total_pages,
        "sections": len(sections),
        "annexes": len(annexes),
        "total_clauses": total_clauses,
    }

    return {"metadata": metadata, "structure": structure, "stats": stats}


def _detect_sections(pages_text: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Detect main sections in the document.

    This uses heuristics to identify section headings like:
    - "1 Scope"
    - "5.1.2 Cryptographic controls"
    - "Chapter 3: Requirements"
    """
    sections = []

    # Common section patterns
    # Matches: "1 Title", "1.2 Title", "1.2.3 Title"
    section_pattern = re.compile(r"^(\d+(?:\.\d+)*)\s+([A-Z][^\n]{5,80})$", re.MULTILINE)

    for page_info in pages_text:
        page_num = page_info["page"]
        text = page_info["text"]

        # Find all section headers on this page
        matches = section_pattern.finditer(text)

        for match in matches:
            section_id = match.group(1)
            section_title = match.group(2).strip()

            # Extract content until next section or end of page
            start_pos = match.end()
            next_match = section_pattern.search(text, start_pos)

            if next_match:
                content = text[start_pos : next_match.start()].strip()
            else:
                content = text[start_pos:].strip()

            # Only include if we have meaningful content
            if content and len(content) > 20:
                sections.append(
                    {
                        "id": section_id,
                        "title": section_title,
                        "page": page_num,
                        "content": content[:2000],  # Limit length
                        "subsections": [],
                    }
                )

    # Build hierarchy (nest subsections)
    sections = _build_hierarchy(sections)

    return sections


def _detect_annexes(pages_text: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Detect annexes (like Annex A in ISO 27001).

    Annexes often contain control listings with IDs like:
    - "A.5.15 Access control"
    - "Annex B.2.1 Requirements"
    """
    annexes = []

    # Pattern for annex headers
    annex_pattern = re.compile(r"^Annex\s+([A-Z])[:\s]+([^\n]+)$", re.MULTILINE | re.IGNORECASE)

    # Pattern for controls within annexes
    control_pattern = re.compile(r"^([A-Z]\.\d+(?:\.\d+)*)\s+([A-Z][^\n]{5,80})$", re.MULTILINE)

    current_annex = None

    for page_info in pages_text:
        page_num = page_info["page"]
        text = page_info["text"]

        # Check for new annex
        annex_match = annex_pattern.search(text)
        if annex_match:
            # Save previous annex if exists
            if current_annex:
                annexes.append(current_annex)

            # Start new annex
            annex_id = annex_match.group(1)
            annex_title = annex_match.group(2).strip()
            current_annex = {
                "id": annex_id,
                "title": annex_title,
                "page": page_num,
                "controls": [],
            }

        # If we're in an annex, look for controls
        if current_annex:
            control_matches = control_pattern.finditer(text)

            for match in control_matches:
                control_id = match.group(1)
                control_title = match.group(2).strip()

                # Extract content
                start_pos = match.end()
                next_match = control_pattern.search(text, start_pos)

                if next_match:
                    content = text[start_pos : next_match.start()].strip()
                else:
                    content = text[start_pos:].strip()

                if content and len(content) > 10:
                    current_annex["controls"].append(
                        {
                            "id": control_id,
                            "title": control_title,
                            "content": content[:1000],
                            "page": page_num,
                            "category": f"Annex {current_annex['id']}",
                            "type": "normative",
                        }
                    )

    # Add final annex
    if current_annex and current_annex["controls"]:
        annexes.append(current_annex)

    return annexes


def _build_hierarchy(sections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Build hierarchical structure from flat section list.

    Converts:
        [{"id": "1"}, {"id": "1.1"}, {"id": "1.2"}, {"id": "2"}]
    Into:
        [{"id": "1", "subsections": [{"id": "1.1"}, {"id": "1.2"}]}, {"id": "2"}]
    """
    if not sections:
        return []

    # Build a tree structure
    root = []
    stack = []  # Stack of (section, level)

    for section in sections:
        section_id = section["id"]
        level = section_id.count(".")

        # Remove subsections key to avoid duplication
        section = {k: v for k, v in section.items() if k != "subsections"}
        section["subsections"] = []

        # Pop stack until we find the parent level
        while stack and stack[-1][1] >= level:
            stack.pop()

        if not stack:
            # Top level section
            root.append(section)
            stack.append((section, level))
        else:
            # Add as subsection of parent
            parent = stack[-1][0]
            parent["subsections"].append(section)
            stack.append((section, level))

    return root
