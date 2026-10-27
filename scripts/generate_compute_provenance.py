"""Build the checksummed single-sample Roihu compute-provenance registry."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from champhla_recovery.compute_provenance import build_compute_smoke_registry  # noqa: E402


def main() -> int:
    rows = build_compute_smoke_registry(
        ROOT / "provenance" / "compute_smoke" / "raw",
        ROOT / "artifacts" / "compute_smoke_benchmark.tsv",
        ROOT / "artifacts" / "compute_smoke_benchmark_manifest.json",
    )
    print(f"generated {len(rows)} compute-smoke task records")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
