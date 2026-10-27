#!/usr/bin/env bash
# One supported verification entry point for the development paper.
set -euo pipefail

ROOT=$(cd "$(dirname "$0")/.." && pwd)
cd "${ROOT}"

PYTHON=${PYTHON:-python3}
PUBLIC_TRUTH=${PUBLIC_TRUTH:-runtime_data/public_truth/20140702_hla_diversity.txt}
BOOTSTRAP=${BOOTSTRAP:-100000}
POWER_ITERATIONS=${POWER_ITERATIONS:-2000}

ARGS=(
  --public-truth "${PUBLIC_TRUTH}"
  --bootstrap "${BOOTSTRAP}"
  --power-iterations "${POWER_ITERATIONS}"
)
if [[ "${RELEASE:-0}" == "1" ]]; then
  ARGS+=(--release)
fi
if [[ "${SUBMISSION:-0}" == "1" ]]; then
  ARGS+=(--submission)
fi
if [[ "${SKIP_TESTS:-0}" == "1" ]]; then
  ARGS+=(--skip-tests)
fi
if [[ -n "${RESTORED_CALLER_SOURCE:-}" ]]; then
  ARGS+=(--restored-caller-source "${RESTORED_CALLER_SOURCE}")
fi

exec "${PYTHON}" scripts/reproduce_development_benchmark.py "${ARGS[@]}"
