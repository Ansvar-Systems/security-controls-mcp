"""Premium version tracking tools for Security Controls MCP.

These tools provide control version history, diff comparison, and framework
change monitoring. They load version data from data/version-history.json
and are gated behind the PREMIUM_ENABLED environment variable.

On free tier, tools return an upgrade message pointing to Ansvar Intelligence Portal.
"""

import json
import os
from pathlib import Path
from typing import Any

# ── Premium gate ─────────────────────────────────────────────────────────────


def is_premium_enabled() -> bool:
    return os.environ.get("PREMIUM_ENABLED") == "true"


def upgrade_response() -> dict[str, Any]:
    return {
        "premium": False,
        "message": (
            "Version tracking requires Ansvar Intelligence Portal (premium tier). "
            "Contact hello@ansvar.ai for access."
        ),
        "upgrade_url": "https://ansvar.eu/intelligence-portal",
    }


# ── Version history data loader ──────────────────────────────────────────────


class VersionHistory:
    """Loads and queries SCF version history data."""

    def __init__(self, data_dir: Path | None = None):
        self.data_dir = data_dir or Path(__file__).parent.parent / "data"
        self.history: list[dict[str, Any]] = []
        self.control_history: dict[str, list[dict[str, Any]]] = {}
        self._loaded = False

    def _ensure_loaded(self) -> None:
        if self._loaded:
            return
        history_file = self.data_dir / "version-history.json"
        if history_file.exists():
            with open(history_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.history = data.get("changes", [])
                # Build per-control index
                for change in self.history:
                    cid = change.get("control_id", "")
                    if cid not in self.control_history:
                        self.control_history[cid] = []
                    self.control_history[cid].append(change)
        self._loaded = True

    def get_control_history(self, control_id: str) -> list[dict[str, Any]]:
        self._ensure_loaded()
        return sorted(
            self.control_history.get(control_id, []),
            key=lambda c: c.get("effective_date", ""),
        )

    def get_recent_changes(
        self,
        since: str,
        framework: str | None = None,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        self._ensure_loaded()
        results = []
        for change in self.history:
            if change.get("effective_date", "") < since:
                continue
            if framework and framework not in change.get("frameworks_affected", []):
                continue
            results.append(change)

        results.sort(key=lambda c: c.get("effective_date", ""), reverse=True)
        return results[:limit]

    def get_framework_changes(
        self,
        framework: str,
        since: str | None = None,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        self._ensure_loaded()
        results = []
        for change in self.history:
            if framework not in change.get("frameworks_affected", []):
                continue
            if since and change.get("effective_date", "") < since:
                continue
            results.append(change)

        results.sort(key=lambda c: c.get("effective_date", ""), reverse=True)
        return results[:limit]


# ── Singleton ─────────────────────────────────────────────────────────────

_version_history: VersionHistory | None = None


def get_version_history() -> VersionHistory:
    global _version_history
    if _version_history is None:
        _version_history = VersionHistory()
    return _version_history


# ── Tool definitions (for list_tools) ────────────────────────────────────────

PREMIUM_TOOLS = [
    {
        "name": "get_control_history",
        "description": (
            "Returns the full version timeline for a specific SCF control. "
            "Shows when the control was added, modified, or removed across SCF releases. "
            "Premium feature — requires Ansvar Intelligence Portal."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "control_id": {
                    "type": "string",
                    "description": 'SCF control ID (e.g., "GOV-01", "IAC-05")',
                    "pattern": "^[A-Z]{2,5}-\\d{2}(\\.\\d{1,2})?$",
                },
            },
            "required": ["control_id"],
            "additionalProperties": False,
        },
    },
    {
        "name": "diff_control",
        "description": (
            "Shows what changed in an SCF control between two SCF releases. "
            "Returns a change summary and affected framework mappings. "
            "Premium feature — requires Ansvar Intelligence Portal."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "control_id": {
                    "type": "string",
                    "description": 'SCF control ID (e.g., "GOV-01")',
                    "pattern": "^[A-Z]{2,5}-\\d{2}(\\.\\d{1,2})?$",
                },
                "from_version": {
                    "type": "string",
                    "description": 'SCF release version (e.g., "2024.4")',
                },
                "to_version": {
                    "type": "string",
                    "description": 'SCF release version (defaults to current)',
                },
            },
            "required": ["control_id", "from_version"],
            "additionalProperties": False,
        },
    },
    {
        "name": "get_framework_changes",
        "description": (
            "Lists all SCF control changes that affected a specific framework's mappings. "
            "Useful for monitoring how framework coverage evolves across releases. "
            "Premium feature — requires Ansvar Intelligence Portal."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "framework": {
                    "type": "string",
                    "description": 'Framework key (e.g., "iso_27001_2022", "nist_csf_2.0")',
                },
                "since": {
                    "type": "string",
                    "description": 'ISO date to look back from (e.g., "2024-01-01")',
                },
                "limit": {
                    "type": "integer",
                    "description": "Max results (default: 50, max: 200)",
                    "default": 50,
                    "minimum": 1,
                    "maximum": 200,
                },
            },
            "required": ["framework"],
            "additionalProperties": False,
        },
    },
]


# ── Tool handlers ────────────────────────────────────────────────────────────


def handle_get_control_history(arguments: dict) -> str:
    """Handle get_control_history tool call."""
    if not is_premium_enabled():
        return json.dumps(upgrade_response(), indent=2)

    control_id = str(arguments.get("control_id") or "").strip()
    if not control_id:
        return "Error: control_id is required."

    vh = get_version_history()
    history = vh.get_control_history(control_id)

    if not history:
        return json.dumps(
            {
                "control_id": control_id,
                "versions": [],
                "message": f"No version history found for {control_id}. "
                "History is populated from the monthly ingestion pipeline.",
            },
            indent=2,
        )

    return json.dumps(
        {
            "control_id": control_id,
            "versions": history,
            "total_versions": len(history),
        },
        indent=2,
    )


def handle_diff_control(arguments: dict) -> str:
    """Handle diff_control tool call."""
    if not is_premium_enabled():
        return json.dumps(upgrade_response(), indent=2)

    control_id = str(arguments.get("control_id") or "").strip()
    from_version = str(arguments.get("from_version") or "").strip()
    to_version = str(arguments.get("to_version") or "current").strip()

    if not control_id or not from_version:
        return "Error: control_id and from_version are required."

    vh = get_version_history()
    history = vh.get_control_history(control_id)

    from_entry = next(
        (h for h in history if h.get("scf_version") == from_version), None
    )
    to_entry = next(
        (h for h in history if h.get("scf_version") == to_version), None
    )

    if not from_entry and not to_entry:
        return json.dumps(
            {
                "control_id": control_id,
                "from_version": from_version,
                "to_version": to_version,
                "diff": None,
                "change_summary": f"No version data found for {control_id} "
                f"in releases {from_version} or {to_version}.",
            },
            indent=2,
        )

    changes_between = [
        h
        for h in history
        if h.get("scf_version", "") >= from_version
        and (to_version == "current" or h.get("scf_version", "") <= to_version)
    ]

    return json.dumps(
        {
            "control_id": control_id,
            "from_version": from_version,
            "to_version": to_version,
            "changes_between": changes_between,
            "total_changes": len(changes_between),
        },
        indent=2,
    )


def handle_get_framework_changes(arguments: dict) -> str:
    """Handle get_framework_changes tool call."""
    if not is_premium_enabled():
        return json.dumps(upgrade_response(), indent=2)

    framework = str(arguments.get("framework") or "").strip()
    since = arguments.get("since")
    limit = min(max(int(arguments.get("limit", 50) or 50), 1), 200)

    if not framework:
        return "Error: framework is required."

    vh = get_version_history()
    changes = vh.get_framework_changes(framework, since, limit)

    return json.dumps(
        {
            "framework": framework,
            "since": since,
            "changes": changes,
            "total": len(changes),
        },
        indent=2,
    )


# ── Dispatch ──────────────────────────────────────────────────────────────

PREMIUM_HANDLERS = {
    "get_control_history": handle_get_control_history,
    "diff_control": handle_diff_control,
    "get_framework_changes": handle_get_framework_changes,
}
