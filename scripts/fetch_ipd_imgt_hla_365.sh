#!/usr/bin/env bash
set -euo pipefail

project_root=$(cd "$(dirname "$0")/.." && pwd)
target="${project_root}/resources/ipd_imgt_hla/3.65.0"
base="https://raw.githubusercontent.com/ANHIG/IMGTHLA/v3.65.0-alpha"

mkdir -p "${target}/wmda"
curl --fail --location --retry 3 "${base}/release_version.txt" -o "${target}/release_version.txt"
curl --fail --location --retry 3 "${base}/Allelelist.txt" -o "${target}/Allelelist.txt"
curl --fail --location --retry 3 "${base}/Deleted_alleles.txt" -o "${target}/Deleted_alleles.txt"
curl --fail --location --retry 3 "${base}/wmda/hla_nom_p.txt" -o "${target}/wmda/hla_nom_p.txt"
curl --fail --location --retry 3 "${base}/wmda/hla_nom_g.txt" -o "${target}/wmda/hla_nom_g.txt"
curl --fail --location --retry 3 "${base}/LICENCE.md" -o "${target}/LICENCE.md"

grep -Fq "IPD-IMGT/HLA 3.65.0" "${target}/release_version.txt"
(
  cd "${target}"
  sha256sum release_version.txt Allelelist.txt Deleted_alleles.txt \
    wmda/hla_nom_p.txt wmda/hla_nom_g.txt LICENCE.md > SHA256SUMS
)
(cd "${target}" && sha256sum --check SHA256SUMS)
