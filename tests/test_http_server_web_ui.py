"""Tests for HTTP server web UI for standards import."""

import json
from pathlib import Path
from typing import Dict, Any

import pytest
from starlette.testclient import TestClient

from security_controls_mcp.http_server import app


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def sample_pdf_bytes():
    """Sample PDF bytes for testing."""
    # Minimal PDF header
    return b"%PDF-1.4\n%\xE2\xE3\xCF\xD3\nendobj\nstartxref\n%%EOF"


class TestStandardsUploadPage:
    """Tests for GET /standards/upload endpoint."""

    def test_upload_page_returns_html(self, client):
        """Test that upload page returns HTML."""
        response = client.get("/standards/upload")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]

    def test_upload_page_has_form(self, client):
        """Test that upload page contains file upload form."""
        response = client.get("/standards/upload")
        html = response.text

        # Check for form element
        assert "<form" in html
        assert 'enctype="multipart/form-data"' in html
        assert 'method="post"' in html.lower()

        # Check for file input
        assert 'type="file"' in html
        # Check for accept attribute (either .pdf or application/pdf)
        assert ('accept=' in html.lower() and '.pdf' in html.lower())

    def test_upload_page_has_submit_button(self, client):
        """Test that upload page has submit button."""
        response = client.get("/standards/upload")
        html = response.text

        assert 'type="submit"' in html

    def test_upload_page_has_results_container(self, client):
        """Test that upload page has container for displaying results."""
        response = client.get("/standards/upload")
        html = response.text

        # Should have a div/section for results
        assert "results" in html.lower()

    def test_upload_page_has_progress_indicator(self, client):
        """Test that upload page has progress/loading indicator."""
        response = client.get("/standards/upload")
        html = response.text

        # Should have something for progress indication
        assert "processing" in html.lower() or "loading" in html.lower()


class TestStandardsExtractAPI:
    """Tests for POST /api/standards/extract endpoint."""

    def test_extract_endpoint_exists(self, client):
        """Test that extract endpoint is accessible."""
        # Send empty request to verify endpoint exists
        response = client.post("/api/standards/extract")
        # Should fail validation but not 404
        assert response.status_code != 404

    def test_extract_requires_file(self, client):
        """Test that extract endpoint requires a file."""
        response = client.post("/api/standards/extract")
        assert response.status_code == 400
        data = response.json()
        assert "error" in data or "message" in data

    def test_extract_accepts_multipart_form(self, client, sample_pdf_bytes):
        """Test that extract endpoint accepts multipart/form-data."""
        # This test will initially fail until we implement the endpoint
        files = {"file": ("test.pdf", sample_pdf_bytes, "application/pdf")}
        response = client.post("/api/standards/extract", files=files)

        # Should not error on multipart processing
        assert response.status_code in [200, 400, 422, 500]

    def test_extract_returns_json(self, client, sample_pdf_bytes):
        """Test that extract endpoint returns JSON."""
        files = {"file": ("test.pdf", sample_pdf_bytes, "application/pdf")}
        response = client.post("/api/standards/extract", files=files)

        assert response.headers["content-type"] == "application/json"

    def test_extract_returns_extraction_result_structure(self, client, sample_pdf_bytes):
        """Test that extract returns proper ExtractionResult JSON structure."""
        files = {"file": ("test.pdf", sample_pdf_bytes, "application/pdf")}
        response = client.post("/api/standards/extract", files=files)

        # Even if extraction fails, should return proper JSON structure
        data = response.json()

        # Check for key fields from ExtractionResult
        if response.status_code == 200:
            assert "standard_id" in data
            assert "version" in data
            assert "version_detection" in data
            assert "controls" in data
            assert isinstance(data["controls"], list)
            assert "confidence_score" in data
            assert "warnings" in data

    def test_extract_includes_coverage_info(self, client, sample_pdf_bytes):
        """Test that successful extraction includes coverage metadata."""
        files = {"file": ("test.pdf", sample_pdf_bytes, "application/pdf")}
        response = client.post("/api/standards/extract", files=files)

        if response.status_code == 200:
            data = response.json()
            # Should have expected vs extracted control info
            assert "expected_control_ids" in data or "missing_control_ids" in data

    def test_extract_handles_invalid_pdf(self, client):
        """Test that extract handles invalid PDF gracefully."""
        files = {"file": ("invalid.pdf", b"not a pdf", "application/pdf")}
        response = client.post("/api/standards/extract", files=files)

        # Should not crash - either returns error or extraction result with warnings
        assert response.status_code in [200, 400, 422, 500]
        data = response.json()
        # Either has error or is a valid extraction result (possibly with warnings)
        assert "error" in data or "standard_id" in data

    def test_extract_with_real_iso27001_structure(self, client):
        """Test extraction with a more realistic PDF structure."""
        # Create a minimal but realistic PDF-like structure
        pdf_content = b"""%PDF-1.4
1 0 obj
<< /Type /Catalog /Pages 2 0 R >>
endobj
2 0 obj
<< /Type /Pages /Kids [3 0 R] /Count 1 >>
endobj
3 0 obj
<< /Type /Page /Parent 2 0 R /Contents 4 0 R >>
endobj
4 0 obj
<< /Length 44 >>
stream
BT
/F1 12 Tf
100 700 Td
(A.5.1 Test Control) Tj
ET
endstream
endobj
xref
0 5
trailer
<< /Size 5 /Root 1 0 R >>
startxref
%%EOF"""

        files = {"file": ("iso27001.pdf", pdf_content, "application/pdf")}
        response = client.post("/api/standards/extract", files=files)

        # Should process without crashing
        assert response.status_code in [200, 400, 422, 500]


class TestWebUIIntegration:
    """Integration tests for the complete web UI flow."""

    def test_upload_page_loads_independently(self, client):
        """Test that upload page can be accessed directly."""
        response = client.get("/standards/upload")
        assert response.status_code == 200
        assert len(response.text) > 1000  # Should have substantial HTML

    def test_api_endpoint_accessible_from_browser(self, client):
        """Test that API endpoint is accessible for AJAX calls."""
        # OPTIONS request to check CORS (if needed)
        response = client.options("/api/standards/extract")
        # Should not be 404
        assert response.status_code in [200, 204, 405]  # 405 if OPTIONS not implemented

    def test_html_includes_javascript(self, client):
        """Test that HTML page includes JavaScript for AJAX submission."""
        response = client.get("/standards/upload")
        html = response.text

        # Should have script tags
        assert "<script" in html

    def test_html_has_proper_structure(self, client):
        """Test that HTML has proper document structure."""
        response = client.get("/standards/upload")
        html = response.text

        assert "<!DOCTYPE html>" in html or "<!doctype html>" in html
        assert "<html" in html
        assert "<head>" in html
        assert "<body>" in html
        assert "</html>" in html

    def test_html_has_styling(self, client):
        """Test that HTML includes CSS styling."""
        response = client.get("/standards/upload")
        html = response.text

        # Should have either inline styles or style tag
        assert "<style>" in html or 'style="' in html

    def test_html_mobile_responsive(self, client):
        """Test that HTML includes viewport meta tag for mobile."""
        response = client.get("/standards/upload")
        html = response.text

        assert 'name="viewport"' in html


class TestExtractionResultDisplay:
    """Tests for how extraction results are displayed in the UI."""

    def test_html_has_version_display_area(self, client):
        """Test that HTML has area for displaying detected version."""
        response = client.get("/standards/upload")
        html = response.text

        # Should have element IDs or classes for version display
        assert 'version' in html.lower()

    def test_html_has_coverage_display_area(self, client):
        """Test that HTML has area for displaying coverage percentage."""
        response = client.get("/standards/upload")
        html = response.text

        assert 'coverage' in html.lower() or 'percentage' in html.lower()

    def test_html_has_controls_table_area(self, client):
        """Test that HTML has table/list for displaying controls."""
        response = client.get("/standards/upload")
        html = response.text

        assert '<table' in html.lower() or 'controls' in html.lower()

    def test_html_has_missing_controls_area(self, client):
        """Test that HTML has area for displaying missing controls."""
        response = client.get("/standards/upload")
        html = response.text

        assert 'missing' in html.lower()

    def test_html_has_confidence_badge_area(self, client):
        """Test that HTML has area for displaying confidence."""
        response = client.get("/standards/upload")
        html = response.text

        assert 'confidence' in html.lower() or 'badge' in html.lower()
