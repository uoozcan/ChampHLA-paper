"""Validate and checksum the aggregate-only FIMM and VenEx release."""
from pathlib import Path

from champhla_recovery.exploratory import freeze_exploratory_aggregates


ROOT = Path(__file__).resolve().parent.parent


if __name__ == "__main__":
    freeze_exploratory_aggregates(ROOT)
    print("validated and checksum-froze FIMM and VenEx aggregate artifacts")
