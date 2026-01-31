"""Smoke tests for production readiness."""

import json
from pathlib import Path


class TestDataFiles:
    """Smoke tests for data file integrity."""

    def test_scf_controls_file_exists(self):
        """Verify scf-controls.json exists."""
        data_dir = Path(__file__).parent.parent / "src" / "security_controls_mcp" / "data"
        controls_file = data_dir / "scf-controls.json"
        assert controls_file.exists(), "scf-controls.json not found"

    def test_framework_to_scf_file_exists(self):
        """Verify framework-to-scf.json exists."""
        data_dir = Path(__file__).parent.parent / "src" / "security_controls_mcp" / "data"
        framework_file = data_dir / "framework-to-scf.json"
        assert framework_file.exists(), "framework-to-scf.json not found"

    def test_scf_controls_valid_json(self):
        """Verify scf-controls.json is valid JSON."""
        data_dir = Path(__file__).parent.parent / "src" / "security_controls_mcp" / "data"
        controls_file = data_dir / "scf-controls.json"
        with open(controls_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert "controls" in data
        assert isinstance(data["controls"], list)

    def test_framework_to_scf_valid_json(self):
        """Verify framework-to-scf.json is valid JSON."""
        data_dir = Path(__file__).parent.parent / "src" / "security_controls_mcp" / "data"
        framework_file = data_dir / "framework-to-scf.json"
        with open(framework_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert isinstance(data, dict)

    def test_controls_data_populated(self):
        """Verify controls data is populated."""
        data_dir = Path(__file__).parent.parent / "src" / "security_controls_mcp" / "data"
        controls_file = data_dir / "scf-controls.json"
        with open(controls_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert len(data["controls"]) == 1451, "Expected 1451 controls"

    def test_all_frameworks_present(self):
        """Verify all expected frameworks are present in data."""
        from security_controls_mcp.data_loader import SCFData

        data = SCFData()

        expected_frameworks = [
            # Original 16 frameworks
            "nist_csf_2.0",
            "nist_800_53_r5",
            "iso_27001_2022",
            "iso_27002_2022",
            "cis_csc_8.1",
            "pci_dss_4.0.1",
            "cmmc_2.0_level_1",
            "cmmc_2.0_level_2",
            "soc_2_tsc",
            "dora",
            "nis2",
            "gdpr",
            "ncsc_caf_4.0",
            "uk_cyber_essentials",
            "fedramp_r5_moderate",
            "hipaa_security_rule",
            # New 12 frameworks
            "australia_essential_8",
            "australia_ism_2024",
            "singapore_mas_trm_2021",
            "swift_cscf_2023",
            "nist_privacy_framework_1_0",
            "netherlands",
            "norway",
            "sweden",
            "germany",
            "germany_bait",
            "germany_c5_2020",
            "csa_ccm_4",
        ]

        for framework in expected_frameworks:
            assert framework in data.frameworks, f"Framework {framework} not found"


class TestModuleImports:
    """Smoke tests for module imports."""

    def test_import_main_package(self):
        """Can import main package."""
        import security_controls_mcp

        assert security_controls_mcp.__version__ == "0.3.1"

    def test_import_server(self):
        """Can import server module."""
        from security_controls_mcp import server

        assert hasattr(server, "app")

    def test_import_data_loader(self):
        """Can import data loader."""
        from security_controls_mcp.data_loader import SCFData

        assert SCFData is not None


class TestPackageMetadata:
    """Smoke tests for package metadata."""

    def test_version_defined(self):
        """Package version is defined."""
        from security_controls_mcp import __version__

        assert __version__ is not None
        assert isinstance(__version__, str)

    def test_pyproject_toml_exists(self):
        """pyproject.toml exists."""
        project_root = Path(__file__).parent.parent
        pyproject = project_root / "pyproject.toml"
        assert pyproject.exists()


class TestDocumentation:
    """Smoke tests for documentation."""

    def test_readme_exists(self):
        """README.md exists."""
        project_root = Path(__file__).parent.parent
        readme = project_root / "README.md"
        assert readme.exists()
        assert readme.stat().st_size > 1000, "README too small"

    def test_license_exists(self):
        """LICENSE file exists."""
        project_root = Path(__file__).parent.parent
        license_file = project_root / "LICENSE"
        assert license_file.exists()

    def test_install_docs_exist(self):
        """Installation documentation exists."""
        project_root = Path(__file__).parent.parent
        install_md = project_root / "INSTALL.md"
        assert install_md.exists()
