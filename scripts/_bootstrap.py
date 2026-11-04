"""Allow the documented scripts to run from a fresh clone before installation."""

from __future__ import annotations

import sys
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPOSITORY_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

DEFAULT_DATASET = REPOSITORY_ROOT / "data" / "pasturages_anonymized.csv"
DEFAULT_RESULTS_ROOT = REPOSITORY_ROOT / "results"
