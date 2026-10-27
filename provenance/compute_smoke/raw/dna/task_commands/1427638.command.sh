#!/bin/bash -ue
echo "[Kourami] Running on HG00096.mate_aware_hla..."

    # Ensure BAM index exists (required for region-based extraction)
    [ -f "HG00096.mate_aware_hla.bam.bai" ] || samtools index HG00096.mate_aware_hla.bam

    # Step 1: Extract HLA-region reads.
    # If kourami_hs38_ref is set, use Kourami's alignAndExtract script for precise extraction.
    # Otherwise, use samtools to extract reads directly from the HLA region (chr6 28M-34M).
    # Auto-detect chromosome naming: check if BAM uses "chr6" or "6".
    if [ "null" != "null" ] && [ -n "null" ]; then
        bash /usr/local/bin/kourami-0.9.6/scripts/alignAndExtract_hs38DH.sh             -d /usr/local/bin/kourami-0.9.6/db             -r null             HG00096.mate_aware_hla. HG00096.mate_aware_hla.bam || true
        R1="HG00096.mate_aware_hla._extract_1.fq.gz"
        R2="HG00096.mate_aware_hla._extract_2.fq.gz"
    else
        # Direct extraction: detect chr naming (chr6 vs 6)
        CHR=$(samtools view -H HG00096.mate_aware_hla.bam | awk '/^@SQ.*SN:chr6	/{print "chr6"; exit} /^@SQ.*SN:6	/{print "6"; exit}')
        if [ -z "$CHR" ]; then
            echo "[Kourami] WARNING: could not detect chr6 in BAM header for HG00096.mate_aware_hla"
            CHR="6"
        fi
        echo "[Kourami] Extracting HLA region from ${CHR}:28000000-34000000..."
        samtools view -b HG00096.mate_aware_hla.bam "${CHR}:28000000-34000000" |             samtools sort -n -@ 16 |             samtools fastq -1 HG00096.mate_aware_hla._hla_1.fq.gz -2 HG00096.mate_aware_hla._hla_2.fq.gz -s /dev/null -
        R1="HG00096.mate_aware_hla._hla_1.fq.gz"
        R2="HG00096.mate_aware_hla._hla_2.fq.gz"
    fi

    if [ ! -f "$R1" ] || [ ! -s "$R1" ]; then
        echo "[Kourami] WARNING: HLA read extraction produced no output for HG00096.mate_aware_hla"
        # Never manufacture an empty result. A placeholder file is
        # indistinguishable downstream from a caller that genuinely typed
        # nothing -- see modules/spechla.nf for what that cost.
        # This branch also used to `exit 0`, reporting success outright.
        echo "Kourami produced no parsable output for HG00096.mate_aware_hla" >&2
        echo "Working directory contains:" >&2
        ls -la . >&2 || true
        exit 1
    fi

    # Step 2: Align extracted HLA reads to the augmented Kourami panel
    bwa mem -t 16         /usr/local/bin/kourami-0.9.6/db/All_FINAL_with_Decoy.fa.gz         $R1 $R2         -o HG00096.mate_aware_hla.panel.sam

    samtools sort -@ 16 -o HG00096.mate_aware_hla.panel.bam HG00096.mate_aware_hla.panel.sam
    samtools index HG00096.mate_aware_hla.panel.bam

    # Step 3: Kourami assembly-graph typing
    # Jar location differs: container uses target/Kourami.jar; local build uses build/Kourami.jar;
    # /usr/local/bin/Kourami.jar is a direct symlink available in the zlskidmore/kourami container.
    KOURAMI_JAR="/usr/local/bin/kourami-0.9.6/build/Kourami.jar"
    [ -f "$KOURAMI_JAR" ] || KOURAMI_JAR="/usr/local/bin/kourami-0.9.6/target/Kourami.jar"
    [ -f "$KOURAMI_JAR" ] || KOURAMI_JAR="/usr/local/bin/Kourami.jar"
    java -Xmx10g -jar $KOURAMI_JAR         -d /usr/local/bin/kourami-0.9.6/db         HG00096.mate_aware_hla.panel.bam         -o HG00096.mate_aware_hla.kourami || true

    # Parse .result file → standard pipeline TSV
    if [ -f "HG00096.mate_aware_hla.kourami.result" ]; then
        python3 /scratch/project_2008084/pihla-publish_v5/bin/parse_kourami_results.py             --input  HG00096.mate_aware_hla.kourami.result             --sample HG00096.mate_aware_hla             --output HG00096.mate_aware_hla_kourami.txt
    else
        # Never manufacture an empty result. A placeholder file is
        # indistinguishable downstream from a caller that genuinely typed
        # nothing -- see modules/spechla.nf for what that cost.
        echo "Kourami produced no parsable output for HG00096.mate_aware_hla" >&2
        echo "Working directory contains:" >&2
        ls -la . >&2 || true
        exit 1
    fi

    # Cleanup large intermediate files
    rm -f HG00096.mate_aware_hla.panel.sam HG00096.mate_aware_hla.panel.bam HG00096.mate_aware_hla.panel.bam.bai
    rm -f HG00096.mate_aware_hla._hla_1.fq.gz HG00096.mate_aware_hla._hla_2.fq.gz
    rm -f HG00096.mate_aware_hla._extract_1.fq.gz HG00096.mate_aware_hla._extract_2.fq.gz

    cat <<END_VERSIONS > versions.yml
"KOURAMI":
kourami: "0.9.6"
END_VERSIONS
