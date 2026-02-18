"""Drift detection tests for data files.

Validates that SCF data files haven't changed unexpectedly by comparing
SHA-256 hashes against known-good values in fixtures/golden-hashes.json.
When data files are intentionally updated, re-compute hashes and update
the golden file.
"""

import hashlib
import json
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
GOLDEN_HASHES_FILE = REPO_ROOT / "fixtures" / "golden-hashes.json"


@pytest.fixture(scope="module")
def golden_hashes():
    """Load golden hashes from fixtures."""
    with open(GOLDEN_HASHES_FILE) as f:
        return json.load(f)


def _sha256(path: Path) -> str:
    """Compute SHA-256 hex digest of a file."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


class TestDataDrift:
    """Verify data files haven't drifted from known-good hashes."""

    def test_golden_hashes_file_exists(self):
        """Golden hashes fixture must exist."""
        assert GOLDEN_HASHES_FILE.exists(), f"Missing {GOLDEN_HASHES_FILE}"

    def test_all_data_files_present(self, golden_hashes):
        """All files listed in golden hashes must exist on disk."""
        for rel_path in golden_hashes["files"]:
            full_path = REPO_ROOT / rel_path
            assert full_path.exists(), f"Data file missing: {rel_path}"

    @pytest.mark.parametrize(
        "rel_path",
        [
            "src/security_controls_mcp/data/scf-controls.json",
            "src/security_controls_mcp/data/framework-to-scf.json",
        ],
    )
    def test_data_file_hash(self, golden_hashes, rel_path):
        """SHA-256 of data file must match golden hash."""
        expected = golden_hashes["files"][rel_path]["sha256"]
        actual = _sha256(REPO_ROOT / rel_path)
        assert actual == expected, (
            f"Data drift detected in {rel_path}!\n"
            f"  Expected: {expected}\n"
            f"  Actual:   {actual}\n"
            f"If this change is intentional, update fixtures/golden-hashes.json"
        )

    def test_scf_controls_count(self, golden_hashes):
        """SCF controls file must contain the expected number of controls."""
        meta = golden_hashes["files"]["src/security_controls_mcp/data/scf-controls.json"]
        expected_count = meta.get("expected_controls")
        if expected_count is None:
            pytest.skip("No expected_controls in golden hashes")

        with open(REPO_ROOT / "src/security_controls_mcp/data/scf-controls.json") as f:
            data = json.load(f)

        actual_count = len(data) if isinstance(data, list) else len(data.get("controls", []))
        assert actual_count == expected_count, (
            f"Control count mismatch: expected {expected_count}, got {actual_count}"
        )
