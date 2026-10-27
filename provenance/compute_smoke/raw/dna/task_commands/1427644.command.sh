#!/bin/bash -ue
mkdir -p t1k_out

    HLA_FA=""
    if [ -n "/scratch/project_2008084/hla_references/t1k_hlaidx" ] && [ -f "/scratch/project_2008084/hla_references/t1k_hlaidx/hla_dna.fa" ]; then
        HLA_FA="/scratch/project_2008084/hla_references/t1k_hlaidx/hla_dna.fa"
    elif [ -n "/scratch/project_2008084/hla_references/t1k_hlaidx" ] && [ -f "/scratch/project_2008084/hla_references/t1k_hlaidx/_dna_seq.fa" ]; then
        HLA_FA="/scratch/project_2008084/hla_references/t1k_hlaidx/_dna_seq.fa"
    else
        HLA_FA=$(find /usr/local/share -maxdepth 2 -type f -name 'hla_dna.fa' 2>/dev/null | head -1 || true)
    fi
    echo "[T1K] HLA reference: ${HLA_FA:-missing}"

    F1="HG00096.mate_aware_hla_R1.fastq.gz"
    F2="HG00096.mate_aware_hla_R2.fastq.gz"
    T1K_PRESET=$([ "dna" = "rna" ] && echo "hla" || echo "hla-wgs")

    if [ -f "${HLA_FA}" ]; then
        run-t1k             -1 "${F1}"             -2 "${F2}"             -f "${HLA_FA}"             --preset "${T1K_PRESET}"             -t 8             -o t1k_out/HG00096.mate_aware_hla             2>t1k_out/t1k_stderr.log
    else
        echo "Missing T1K reference FASTA" > t1k_out/t1k_stderr.log
        exit 1
    fi

    GENOTYPE_FILE=$(ls t1k_out/HG00096.mate_aware_hla_genotype.tsv t1k_out/HG00096.mate_aware_hla.genotype.tsv 2>/dev/null | head -1 || true)
    if [ -n "${GENOTYPE_FILE}" ] && [ -f "${GENOTYPE_FILE}" ]; then
        python3 /scratch/project_2008084/pihla-publish_v5/bin/parse_t1k_results.py             "${GENOTYPE_FILE}"             "HG00096.mate_aware_hla_t1k.txt"
    else
        # Never manufacture an empty result. A placeholder file exits 0 and is
        # indistinguishable downstream from a caller that genuinely typed
        # nothing -- which is how SpecHLA produced header-only files for months
        # without anyone being told. Fail, and say where to look.
        echo "T1K produced no parsable output for HG00096.mate_aware_hla" >&2
        echo "Expected a genotype TSV. Working directory contains:" >&2
        ls -la . >&2 || true
        cat t1k_out/t1k_stderr.log >&2 || true
        exit 1
    fi

    cat <<END_VERSIONS > versions.yml
"T1K_FASTQ":
    t1k: $(run-t1k --version 2>&1 | grep -oP '[0-9]+\.[0-9]+\.[0-9]+' | head -1 || echo "1.0.9")
END_VERSIONS
