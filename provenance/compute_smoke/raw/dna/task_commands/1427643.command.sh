#!/bin/bash -ue
# Create output directory
    mkdir -p HG00096.mate_aware_hla
    trap 'rm -f R1.fastq R2.fastq core.*' EXIT

    # Prepare FASTQ files
    if [[ "HG00096.mate_aware_hla_R1.fastq.gz" == *.gz ]]; then
        zcat HG00096.mate_aware_hla_R1.fastq.gz > R1.fastq
        zcat HG00096.mate_aware_hla_R2.fastq.gz > R2.fastq
    else
        ln -s HG00096.mate_aware_hla_R1.fastq.gz R1.fastq
        ln -s HG00096.mate_aware_hla_R2.fastq.gz R2.fastq
    fi

    # Run OptiType
    echo "[Running OptiType from FASTQ...]"
    OptiTypePipeline.py         -i R1.fastq R2.fastq         --dna         -v         -o HG00096.mate_aware_hla         -p HG00096.mate_aware_hla

    # Parse results
    echo "[Parsing results...]"
    result_tsv=$(find HG00096.mate_aware_hla -name "*_result.tsv" | head -1)
    if [ -n "$result_tsv" ] && [ -f "$result_tsv" ]; then
        python3 <<EOF
import csv
import sys

with open('${result_tsv}', 'r') as f:
    reader = csv.DictReader(f, delimiter='\t')
    row = next(reader)

with open('HG00096.mate_aware_hla_optitype.txt', 'w') as out:
    out.write("# OptiType results for HG00096.mate_aware_hla\n")
    out.write("Gene\tAllele1\tAllele2\n")
    out.write("HLA-A\t{}\t{}\n".format(row.get('A1', '-'), row.get('A2', '-')))
    out.write("HLA-B\t{}\t{}\n".format(row.get('B1', '-'), row.get('B2', '-')))
    out.write("HLA-C\t{}\t{}\n".format(row.get('C1', '-'), row.get('C2', '-')))
EOF
    else
        # Never manufacture an empty result. A placeholder file exits 0 and is
        # indistinguishable downstream from a caller that genuinely typed
        # nothing -- which is how SpecHLA produced header-only files for months
        # without anyone being told. Fail, and say where to look.
        echo "OptiType produced no parsable output for HG00096.mate_aware_hla" >&2
        echo "Expected a *_result.tsv. Working directory contains:" >&2
        ls -la . >&2 || true
        exit 1
    fi

    # Cleanup
    rm -f R1.fastq R2.fastq

    # Version info
    cat <<END_VERSIONS > versions.yml
"OPTITYPE":
    optitype: $(OptiTypePipeline.py --version 2>&1 | head -1 || echo "1.3.5")
END_VERSIONS
