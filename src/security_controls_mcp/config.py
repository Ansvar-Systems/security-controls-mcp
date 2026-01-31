"""Configuration management for security controls MCP server."""

import json
from pathlib import Path
from typing import Any, Dict, Optional


class Config:
    """Manages configuration for the security controls MCP server."""

    def __init__(self, config_dir: Optional[Path] = None):
        """Initialize configuration.

        Args:
            config_dir: Optional path to config directory. Defaults to ~/.security-controls-mcp/
        """
        if config_dir is None:
            self.config_dir = Path.home() / ".security-controls-mcp"
        else:
            self.config_dir = Path(config_dir)

        self.config_file = self.config_dir / "config.json"
        self.standards_dir = self.config_dir / "standards"

        # Ensure directories exist
        self._ensure_directories()

        # Load or create config
        self.data = self._load_config()

    def _ensure_directories(self) -> None:
        """Ensure config and standards directories exist."""
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.standards_dir.mkdir(parents=True, exist_ok=True)

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file or create default."""
        if self.config_file.exists():
            with open(self.config_file, "r") as f:
                return json.load(f)
        else:
            # Create default config
            default_config = {
                "standards": {},
                "query_settings": {
                    "always_show_attribution": True,
                    "include_page_numbers": True,
                    "max_results_per_query": 20,
                },
                "legal": {
                    "acknowledged_scf_restrictions": False,
                    "acknowledged_paid_licenses": False,
                    "last_acknowledgment_date": None,
                },
            }
            self._save_config(default_config)
            return default_config

    def _save_config(self, data: Dict[str, Any]) -> None:
        """Save configuration to file."""
        with open(self.config_file, "w") as f:
            json.dump(data, f, indent=2)

    def get_enabled_standards(self) -> Dict[str, Dict[str, Any]]:
        """Get all enabled paid standards.

        Returns:
            Dictionary of enabled standards with their configuration
        """
        return {
            standard_id: config
            for standard_id, config in self.data.get("standards", {}).items()
            if config.get("enabled", True)
        }

    def add_standard(
        self,
        standard_id: str,
        path: str,
        enabled: bool = True,
        show_license_warnings: bool = True,
    ) -> None:
        """Add a new standard to configuration.

        Args:
            standard_id: Unique identifier for the standard
            path: Relative path to standard data (from standards_dir)
            enabled: Whether the standard is enabled
            show_license_warnings: Whether to show license warnings for this standard
        """
        if "standards" not in self.data:
            self.data["standards"] = {}

        self.data["standards"][standard_id] = {
            "enabled": enabled,
            "path": path,
            "show_license_warnings": show_license_warnings,
        }
        self._save_config(self.data)

    def remove_standard(self, standard_id: str) -> None:
        """Remove a standard from configuration.

        Args:
            standard_id: Unique identifier for the standard to remove
        """
        if standard_id in self.data.get("standards", {}):
            del self.data["standards"][standard_id]
            self._save_config(self.data)

    def get_standard_path(self, standard_id: str) -> Optional[Path]:
        """Get the full path to a standard's data directory.

        Args:
            standard_id: Unique identifier for the standard

        Returns:
            Full path to standard data directory, or None if not found
        """
        standard_config = self.data.get("standards", {}).get(standard_id)
        if not standard_config:
            return None

        return self.standards_dir / standard_config["path"]

    def acknowledge_legal_notices(self) -> None:
        """Mark legal notices as acknowledged."""
        from datetime import datetime

        self.data["legal"]["acknowledged_scf_restrictions"] = True
        self.data["legal"]["acknowledged_paid_licenses"] = True
        self.data["legal"]["last_acknowledgment_date"] = datetime.now().isoformat()
        self._save_config(self.data)

    def needs_legal_acknowledgment(self) -> bool:
        """Check if legal notices need to be acknowledged.

        Returns:
            True if user needs to acknowledge legal notices
        """
        legal = self.data.get("legal", {})
        return not (
            legal.get("acknowledged_scf_restrictions", False)
            and legal.get("acknowledged_paid_licenses", False)
        )
