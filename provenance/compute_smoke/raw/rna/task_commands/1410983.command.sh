#!/bin/bash -ue
# Create working directory
    mkdir -p HG00096
    trap 'rm -f R1.fastq R2.fastq R1_pre.fastq R2_pre.fastq hla_pre.sam core.*' EXIT

    # Prepare FASTQ files (decompress if needed)
    if [[ "HG00096_R1.fastq.gz" == *.gz ]]; then
        zcat HG00096_R1.fastq.gz > R1_pre.fastq
        zcat HG00096_R2.fastq.gz > R2_pre.fastq
    else
        cp HG00096_R1.fastq.gz R1_pre.fastq
        cp HG00096_R2.fastq.gz R2_pre.fastq
    fi

    # Pre-filter: align against HLA-HD's own Bowtie2 index to extract HLA-enriched reads.
    # Without this, HLA-HD's internal FASTQ splitting fails silently on large RNA-seq inputs
    # (mapfile/*.fastq end up 0 bytes → "Unable to read file magic number" for all genes).
    echo "[Pre-filtering HLA reads using HLA-HD dictionary Bowtie2 index...]"
    HLA_BT2_IDX="/app/hlahd.1.4.0/dictionary/all_exon_intron_N150.fasta"
    bowtie2 -p 16 --no-unal -x "${HLA_BT2_IDX}"         -1 R1_pre.fastq -2 R2_pre.fastq -S hla_pre.sam 2>/dev/null || true

    MAPPED_READS=$(grep -c -v "^@" hla_pre.sam 2>/dev/null || echo 0)
    if [ -s hla_pre.sam ] && [ "${MAPPED_READS}" -gt 100 ]; then
        echo "[Pre-filter: ${MAPPED_READS} HLA-mapped reads → using enriched subset]"
        samtools sort -n hla_pre.sam | samtools fastq -1 R1.fastq -2 R2.fastq -0 /dev/null -s /dev/null -
    else
        echo "[Pre-filter: too few mapped reads (${MAPPED_READS}), using full input]"
        mv R1_pre.fastq R1.fastq
        mv R2_pre.fastq R2.fastq
    fi
    rm -f hla_pre.sam R1_pre.fastq R2_pre.fastq

    # Run HLA-HD
    echo "[Running HLA-HD from FASTQ...]"
    HLAHD_BIN=$(command -v hlahd.sh 2>/dev/null || true)
    [ -n "$HLAHD_BIN" ] || HLAHD_BIN=/app/hlahd.1.4.0/bin/hlahd.sh
    [ -x "$HLAHD_BIN" ] || { echo "HLA-HD executable not found" >&2; exit 127; }
    # Detect read length and set -m accordingly (stfr -L TSIZE filters reads shorter than TSIZE)
    READ_LEN=$(awk 'NR==2{print length($0); exit}' R1.fastq 2>/dev/null || echo 100)
    MIN_TAG=$(( READ_LEN < 100 ? READ_LEN / 2 : 50 ))
    echo "[Read length detected: ${READ_LEN}bp, using -m ${MIN_TAG}]"
    "$HLAHD_BIN" -t 16 -m ${MIN_TAG} -c 0.95 -f /app/hlahd.1.4.0/freq_data         R1.fastq R2.fastq /app/hlahd.1.4.0/HLA_gene.split.txt /app/hlahd.1.4.0/dictionary         HG00096 HG00096

    # Parse results with per-gene read counts
    echo "[Parsing results with read counts...]"
    RESULT_DIR="HG00096/HG00096/result"
    if [ -f "${RESULT_DIR}/HG00096_final.result.txt" ]; then
        while IFS='' read -r LINE; do
            GENE=$(printf '%s
' "$LINE" | cut -f1)
            ALLELE1=$(printf '%s
' "$LINE" | cut -f2)
            ALLELE2=$(printf '%s
' "$LINE" | cut -f3)
            GENE_SHORT="${GENE#HLA-}"
            READ_FILE="${RESULT_DIR}/HG00096_${GENE_SHORT}.read.txt"
            READS=0
            if [ -f "${READ_FILE}" ]; then
                RAW=$(awk 'NR==1{print $2}' "${READ_FILE}" 2>/dev/null)
                [[ "${RAW}" =~ ^[0-9]+$ ]] && READS=${RAW}
            fi
            printf '%s	%s	%s	%s	%s
' "${GENE}" "${ALLELE1}" "${ALLELE2}" "${READS}" "${READS}"
        done < "${RESULT_DIR}/HG00096_final.result.txt" > HG00096_hlahd.txt
    else
        # Never manufacture an empty result. A placeholder file exits 0 and is
        # indistinguishable downstream from a caller that genuinely typed
        # nothing -- which is how SpecHLA produced header-only files for months
        # without anyone being told. Fail, and say where to look.
        echo "HLA-HD produced no parsable output for HG00096" >&2
        echo "Expected a *_final.result.txt. Working directory contains:" >&2
        ls -la . >&2 || true
        exit 1
    fi

    # Cleanup
    rm -f R1.fastq R2.fastq

    # Version info
    HLAHD_VER=$([ -n "$HLAHD_BIN" ] && "$HLAHD_BIN" 2>&1 | grep -i version | head -1 || echo "1.4.0")
    printf '"HLAHD_FASTQ":
    hlahd: %s
' "$HLAHD_VER" > versions.yml
