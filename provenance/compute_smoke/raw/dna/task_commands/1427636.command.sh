#!/bin/bash -ue
# Create working directory
    mkdir -p HG00096.mate_aware_hla
    trap 'rm -f hla_region.bam unmapped.bam merged.bam sorted.bam R1.fastq R2.fastq core.*' EXIT

    # Check for BAM index, create if missing
    if [ ! -f "HG00096.mate_aware_hla.bam.bai" ] && [ ! -f "HG00096.mate_aware_hla.bai" ]; then
        echo "Creating BAM index..."
        samtools index -@ 16 HG00096.mate_aware_hla.bam
    fi

    # Extract HLA reads from BAM
    echo "[Step 1] Extracting HLA reads..."
    samtools view -b -h HG00096.mate_aware_hla.bam chr6:28000000-34000000 > hla_region.bam 2>/dev/null ||     samtools view -b -h HG00096.mate_aware_hla.bam 6:28000000-34000000 > hla_region.bam

    # Add unmapped reads
    samtools view -b -f 4 HG00096.mate_aware_hla.bam > unmapped.bam
    samtools merge -f merged.bam hla_region.bam unmapped.bam
    samtools sort -n -@ 16 merged.bam -o sorted.bam

    # Convert to FASTQ
    samtools fastq -@ 16 -1 R1.fastq -2 R2.fastq -0 /dev/null -s /dev/null sorted.bam

    # Run HLA-HD
    echo "[Step 2] Running HLA-HD..."
    HLAHD_BIN=$(command -v hlahd.sh 2>/dev/null || true)
    [ -n "$HLAHD_BIN" ] || HLAHD_BIN=/app/hlahd.1.4.0/bin/hlahd.sh
    [ -x "$HLAHD_BIN" ] || { echo "HLA-HD executable not found" >&2; exit 127; }
    # Detect read length and set -m accordingly (stfr -L TSIZE filters reads shorter than TSIZE)
    READ_LEN=$(awk 'NR==2{print length($0); exit}' R1.fastq 2>/dev/null || echo 100)
    MIN_TAG=$(( READ_LEN < 100 ? READ_LEN / 2 : 50 ))
    echo "[Read length detected: ${READ_LEN}bp, using -m ${MIN_TAG}]"
    "$HLAHD_BIN" -t 16 -m ${MIN_TAG} -c 0.95 -f /app/hlahd.1.4.0/freq_data         R1.fastq R2.fastq /app/hlahd.1.4.0/HLA_gene.split.txt /app/hlahd.1.4.0/dictionary         HG00096.mate_aware_hla HG00096.mate_aware_hla

    # Parse results with per-gene read counts
    # Use cut to extract exactly 3 fields (avoids trailing fields for HLA-E etc.)
    echo "[Step 3] Parsing results with read counts...]"

    RESULT_DIR="HG00096.mate_aware_hla/HG00096.mate_aware_hla/result"
    if [ -f "${RESULT_DIR}/HG00096.mate_aware_hla_final.result.txt" ]; then
        while IFS='' read -r LINE; do
            GENE=$(printf '%s
' "$LINE" | cut -f1)
            ALLELE1=$(printf '%s
' "$LINE" | cut -f2)
            ALLELE2=$(printf '%s
' "$LINE" | cut -f3)
            GENE_SHORT="${GENE#HLA-}"
            READ_FILE="${RESULT_DIR}/HG00096.mate_aware_hla_${GENE_SHORT}.read.txt"
            READS=0
            if [ -f "${READ_FILE}" ]; then
                RAW=$(awk 'NR==1{print $2}' "${READ_FILE}" 2>/dev/null)
                [[ "${RAW}" =~ ^[0-9]+$ ]] && READS=${RAW}
            fi
            printf '%s	%s	%s	%s	%s
' "${GENE}" "${ALLELE1}" "${ALLELE2}" "${READS}" "${READS}"
        done < "${RESULT_DIR}/HG00096.mate_aware_hla_final.result.txt" > HG00096.mate_aware_hla_hlahd.txt
    else
        # Never manufacture an empty result. A placeholder file exits 0 and is
        # indistinguishable downstream from a caller that genuinely typed
        # nothing -- which is how SpecHLA produced header-only files for months
        # without anyone being told. Fail, and say where to look.
        echo "HLA-HD produced no parsable output for HG00096.mate_aware_hla" >&2
        echo "Expected a *_final.result.txt. Working directory contains:" >&2
        ls -la . >&2 || true
        exit 1
    fi

    # Version info
    HLAHD_VER=$([ -n "$HLAHD_BIN" ] && "$HLAHD_BIN" 2>&1 | grep -i version | head -1 || echo "1.4.0")
    SAM_VER=$(samtools --version | head -1 | cut -d' ' -f2)
    printf '"HLAHD_BAM":
    hlahd: %s
    samtools: %s
' "$HLAHD_VER" "$SAM_VER" > versions.yml
