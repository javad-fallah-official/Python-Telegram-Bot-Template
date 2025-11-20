#!/usr/bin/env python3
"""
flush_temp.py - Utility script to purge temporary artefacts from the repository.

Features:
- Deletes Python byte-code: *.pyc, *.pyo and __pycache__/ directories.
- Deletes files with common temporary extensions: *.log, *.tmp, *.cache
- Optional --extensions to customise list.
- Optional --dry-run to preview deletions.
- Optional --quiet to suppress output.
- Detects project root automatically (directory containing this script).
- Cross-platform.

Usage:
    python scripts/flush_temp.py            # delete default set
    python scripts/flush_temp.py --dry-run  # preview only
    python scripts/flush_temp.py -e .log .tmp
"""

import argparse
import os
import shutil
from pathlib import Path

DEFAULT_EXTS = {".pyc", ".pyo", ".log", ".tmp", ".cache"}
DEFAULT_DIRS = {"__pycache__", ".pytest_cache", ".mypy_cache"}

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Flush temporary files and directories from the project.")
    parser.add_argument(
        "-e", "--extensions",
        nargs="+",
        help="Additional file extensions to delete (e.g. .log .tmp).",
    )
    parser.add_argument(
        "-d",
        "--dry-run",
        action="store_true",
        help="Only show what would be deleted without actually deleting.",
    )
    parser.add_argument(
        "-q", "--quiet", action="store_true", help="Suppress output messages."
    )
    return parser.parse_args()

def log(message: str, quiet: bool):
    if not quiet:
        print(message)

def remove_file(path: Path, dry_run: bool, quiet: bool):
    if dry_run:
        log(f"[DRY-RUN] Remove file: {path}", quiet)
    else:
        try:
            path.unlink(missing_ok=True)
            log(f"Removed file: {path}", quiet)
        except Exception as exc:
            log(f"Failed to remove file {path}: {exc}", quiet)

def remove_dir(path: Path, dry_run: bool, quiet: bool):
    if dry_run:
        log(f"[DRY-RUN] Remove directory: {path}", quiet)
    else:
        try:
            shutil.rmtree(path, ignore_errors=True)
            log(f"Removed directory: {path}", quiet)
        except Exception as exc:
            log(f"Failed to remove directory {path}: {exc}", quiet)

def main():
    args = parse_args()
    exts = DEFAULT_EXTS.union(set(args.extensions or []))
    project_root = Path(__file__).resolve().parents[1]  # scripts/..
    log(f"Scanning {project_root} ...", args.quiet)

    for root, dirnames, filenames in os.walk(project_root):
        # Remove temporary directories first
        for dirname in list(dirnames):
            if dirname in DEFAULT_DIRS:
                dir_path = Path(root) / dirname
                remove_dir(dir_path, args.dry_run, args.quiet)
                # Prevent descending into this directory
                dirnames.remove(dirname)

        # Remove temporary files
        for filename in filenames:
            file_path = Path(root) / filename
            if file_path.suffix in exts:
                remove_file(file_path, args.dry_run, args.quiet)

    log("Flush completed.", args.quiet)

if __name__ == "__main__":
    main()