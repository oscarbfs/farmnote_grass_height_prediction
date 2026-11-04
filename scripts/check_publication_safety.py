"""Fail when the public tree contains likely secrets or raw operational IDs."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPOSITORY_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from farmnote_grass_height.data.loader import load_analytical_dataset  # noqa: E402


IGNORED_DIRECTORIES = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    ".pytest_cache",
    "reproduced",
    "smoke",
}
FORBIDDEN_FILENAMES = {
    ".env",
    "google-services.json",
    "GoogleService-Info.plist",
}
FORBIDDEN_SUFFIXES = {".pem", ".p12", ".pfx", ".key"}
TEXT_PATTERNS = {
    "MongoDB URI": re.compile(r"mongodb(?:\+srv)?://", re.IGNORECASE),
    "private key": re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    "Bearer credential": re.compile(r"\bbearer\s+[A-Za-z0-9._~+/=-]{16,}", re.IGNORECASE),
    "assigned credential": re.compile(
        r"\b(?:password|client_secret|api[_-]?key|access[_-]?key|token|secret)"
        r"\s*[:=]\s*['\"][^'\"\r\n]{8,}['\"]",
        re.IGNORECASE,
    ),
    "raw UUID": re.compile(
        r"\b[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}\b",
        re.IGNORECASE,
    ),
}


def _iter_files(root: Path):
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if any(part in IGNORED_DIRECTORIES for part in path.relative_to(root).parts):
            continue
        yield path


def scan_tree(root: Path) -> list[str]:
    findings: list[str] = []
    for path in _iter_files(root):
        relative = path.relative_to(root)
        if path.name in FORBIDDEN_FILENAMES or path.suffix.lower() in FORBIDDEN_SUFFIXES:
            findings.append(f"forbidden file: {relative}")
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        for label, pattern in TEXT_PATTERNS.items():
            for match in pattern.finditer(text):
                line = text.count("\n", 0, match.start()) + 1
                findings.append(f"{label}: {relative}:{line}")
    return findings


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dataset",
        type=Path,
        default=REPOSITORY_ROOT / "data" / "pasturages_anonymized.csv",
    )
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    findings = scan_tree(REPOSITORY_ROOT)
    if args.dataset.exists():
        try:
            load_analytical_dataset(args.dataset, require_public_identifiers=True)
        except Exception as exc:
            findings.append(f"dataset validation: {exc}")
    else:
        findings.append(f"dataset missing: {args.dataset}")

    if findings:
        print("Publication-safety check failed:")
        for finding in findings:
            print(f"- {finding}")
        return 1
    print("Publication-safety check passed: no likely secret or raw identifier found.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
