"""Command-line interface for security-controls-mcp."""

import sys
from pathlib import Path

try:
    import click
    import pdfplumber  # noqa: F401
except ImportError:
    print(
        "Error: Import tools not installed. Install with:\n" "  pip install -e '.[import-tools]'",
        file=sys.stderr,
    )
    sys.exit(1)

from .config import Config
from .extractors import extract_standard


@click.group()
def main():
    """Security Controls MCP - Command-line tools."""
    pass


@main.command("import-standard")
@click.option(
    "--file",
    "-f",
    "pdf_file",
    required=True,
    type=click.Path(exists=True, path_type=Path),
    help="Path to the PDF file to import",
)
@click.option(
    "--type",
    "-t",
    "standard_type",
    required=True,
    help="Standard type (e.g., iso_27001_2022, nist_800_53_r5, pci_dss_4.0.1)",
)
@click.option(
    "--title",
    required=True,
    help="Full title of the standard (e.g., 'ISO/IEC 27001:2022')",
)
@click.option(
    "--purchased-from",
    help="Where the standard was purchased from (e.g., 'ISO.org', 'NIST')",
)
@click.option(
    "--purchase-date",
    help="Date the standard was purchased (YYYY-MM-DD format)",
)
@click.option(
    "--version",
    help="Version of the standard (e.g., '2022', '4.0.1')",
)
@click.option(
    "--force",
    is_flag=True,
    help="Overwrite existing standard if it exists",
)
def import_standard(
    pdf_file: Path,
    standard_type: str,
    title: str,
    purchased_from: str,
    purchase_date: str,
    version: str,
    force: bool,
):
    """Import a purchased standard from PDF file.

    This command extracts text, structure, and metadata from a PDF standard
    and saves it in the user-local standards directory for querying via MCP.

    Example:
        scf-mcp import-standard \\
            --file ~/Downloads/ISO-27001-2022.pdf \\
            --type iso_27001_2022 \\
            --title "ISO/IEC 27001:2022" \\
            --purchased-from "ISO.org" \\
            --purchase-date "2026-01-29"
    """
    from datetime import datetime

    click.echo("=" * 80)
    click.echo("Security Controls MCP - Standard Import Tool")
    click.echo("=" * 80)
    click.echo()

    # Safety check: Verify we're not in a git repo or standards dir is gitignored
    _check_git_safety()

    # Initialize config
    config = Config()

    # Check if standard already exists
    if not force and standard_type in config.data.get("standards", {}):
        click.echo(
            f"❌ Error: Standard '{standard_type}' already exists. " "Use --force to overwrite.",
            err=True,
        )
        sys.exit(1)

    click.echo(f"📄 PDF File: {pdf_file}")
    click.echo(f"🏷️  Standard Type: {standard_type}")
    click.echo(f"📋 Title: {title}")
    click.echo()

    # Extract standard
    click.echo("🔍 Extracting PDF content...")
    click.echo()

    try:
        result = extract_standard(
            pdf_path=pdf_file,
            standard_id=standard_type,
            title=title,
            version=version or "unknown",
            purchased_from=purchased_from or "unknown",
            purchase_date=purchase_date or datetime.now().strftime("%Y-%m-%d"),
        )

        # Save to config directory
        output_dir = config.standards_dir / standard_type
        output_dir.mkdir(parents=True, exist_ok=True)

        # Save files
        import json

        metadata_file = output_dir / "metadata.json"
        full_text_file = output_dir / "full_text.json"

        with open(metadata_file, "w") as f:
            json.dump(result["metadata"], f, indent=2)

        with open(full_text_file, "w") as f:
            json.dump(result["structure"], f, indent=2)

        click.echo("✅ Extraction complete!")
        click.echo()
        click.echo("📊 Extraction Summary:")
        click.echo(f"   • Pages extracted: {result['stats']['pages']}")
        click.echo(f"   • Sections found: {result['stats']['sections']}")
        click.echo(f"   • Total clauses: {result['stats']['total_clauses']}")
        click.echo()

        # Add to config
        config.add_standard(
            standard_id=standard_type,
            path=standard_type,
            enabled=True,
            show_license_warnings=True,
        )

        click.echo(f"💾 Saved to: {output_dir}")
        click.echo()
        click.echo("✓ Standard successfully imported!")
        click.echo()
        click.echo("Next steps:")
        click.echo("  1. Restart your MCP server")
        click.echo(f"  2. Use list_available_standards to verify '{standard_type}' is loaded")
        click.echo("  3. Query the standard with query_standard or get_clause")
        click.echo()

    except Exception as e:
        click.echo(f"❌ Error during extraction: {e}", err=True)
        import traceback

        traceback.print_exc()
        sys.exit(1)


def _check_git_safety():
    """Check that we're not accidentally going to commit paid content."""
    import subprocess

    try:
        # Check if we're in a git repo
        result = subprocess.run(
            ["git", "rev-parse", "--is-inside-work-tree"],
            capture_output=True,
            text=True,
            check=False,
        )

        if result.returncode == 0:
            # We're in a git repo - check if standards dir is ignored
            config = Config()

            # Check if standards dir is inside the current repo
            try:
                standards_dir_rel = str(config.standards_dir.relative_to(Path.cwd()))
            except ValueError:
                # Standards dir is outside the repo (e.g., in home directory)
                # This is safe - can't be accidentally committed
                return

            result = subprocess.run(
                ["git", "check-ignore", "-q", standards_dir_rel],
                check=False,
            )

            if result.returncode != 0:
                click.echo(
                    "⚠️  WARNING: You are in a git repository and the standards "
                    "directory is NOT gitignored!",
                    err=True,
                )
                click.echo(
                    "   This could lead to accidental redistribution of licensed content.",
                    err=True,
                )
                click.echo()
                click.echo("   Add this to your .gitignore:", err=True)
                click.echo(f"   {standards_dir_rel}/", err=True)
                click.echo()
                if not click.confirm("Continue anyway?", default=False):
                    sys.exit(1)

    except FileNotFoundError:
        # Git not installed, skip check
        pass


@main.command("list-standards")
def list_standards():
    """List all imported standards."""
    from .registry import StandardRegistry

    config = Config()
    registry = StandardRegistry(config)

    standards = registry.list_standards()

    click.echo("Available Standards:")
    click.echo()

    for std in standards:
        if std["type"] == "built-in":
            click.echo(f"✓ {std['title']} (Built-in)")
            click.echo(f"  License: {std['license']}")
            click.echo(f"  Coverage: {std['controls']}")
        else:
            click.echo(f"✓ {std['title']} (Purchased)")
            click.echo(f"  ID: {std['standard_id']}")
            click.echo(f"  Version: {std['version']}")
            click.echo(f"  Purchased: {std['purchase_date']}")
        click.echo()


if __name__ == "__main__":
    main()
