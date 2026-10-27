#!/bin/bash -ue
# Set up SpecHLA environment
    SPECHLA_PATH="/projappl/project_2008084/SpecHLAx"

    if [ "true" = "true" ]; then
        # Local installation mode - may need custom library paths
        export PATH="${SPECHLA_PATH}/spechla_env/bin:${SPECHLA_PATH}/bin:${PATH}"
        # Add local library path if set (for htslib compatibility)
        if [ -n "" ]; then
            export LD_LIBRARY_PATH=":${SPECHLA_PATH}/spechla_env/lib:${LD_LIBRARY_PATH:-}"
        else
            export LD_LIBRARY_PATH="${SPECHLA_PATH}/spechla_env/lib:${LD_LIBRARY_PATH:-}"
        fi
    else
        # Container mode - libraries are properly installed in /usr/local
        export PATH="${SPECHLA_PATH}/spechla_env/bin:${SPECHLA_PATH}/bin:/usr/local/bin:${PATH}"
        export LD_LIBRARY_PATH="/usr/local/lib:${SPECHLA_PATH}/spechla_env/lib:${LD_LIBRARY_PATH:-}"
    fi

    # Fail before doing 20 minutes of BAM work if SpecHLA is not where we were told.
    # The default spechla_path points inside the container image; the roihu and
    # puhti profiles run these processes natively, so it must be overridden there.
    if [ ! -f "${SPECHLA_PATH}/script/whole/SpecHLA.sh" ]; then
        echo "SpecHLA not found at ${SPECHLA_PATH}/script/whole/SpecHLA.sh" >&2
        echo "Set params.spechla_path to the SpecHLA install (a params file entry" >&2
        echo "such as conf/roihu_params.yaml), or run this process in a container." >&2
        exit 1
    fi

    # Create output directory
    mkdir -p HG00096.mate_aware_hla
    trap 'rm -f HG00096.mate_aware_hla/hla_region.bam HG00096.mate_aware_hla/namesort.bam HG00096.mate_aware_hla/R1.fastq HG00096.mate_aware_hla/R2.fastq HG00096.mate_aware_hla/R1.fastq.gz HG00096.mate_aware_hla/R2.fastq.gz core.*' EXIT

    # Check for BAM index, create if missing
    if [ ! -f "HG00096.mate_aware_hla.bam.bai" ] && [ ! -f "HG00096.mate_aware_hla.bai" ]; then
        echo "Creating HLA BAM index..."
        samtools index HG00096.mate_aware_hla.bam
    fi

    # Step 1: Extract HLA region then convert to FASTQ
    # SpecHLA docs recommend using HLA reads only; name-sorting the full WGS BAM is very slow
    echo "[Step 1] Extracting HLA region from input BAM..."
    CHR=$(samtools view -H HG00096.mate_aware_hla.bam | awk '/^@SQ.*SN:chr6	/{print "chr6"; exit} /^@SQ.*SN:6	/{print "6"; exit}')
    if [ -z "$CHR" ]; then CHR=6; fi
    samtools view -b HG00096.mate_aware_hla.bam "${CHR}:28000000-34000000" > HG00096.mate_aware_hla/hla_region.bam
    echo "[Step 1b] Preparing FASTQs from HLA region BAM..."
    samtools sort -n HG00096.mate_aware_hla/hla_region.bam -o HG00096.mate_aware_hla/namesort.bam
    rm -f HG00096.mate_aware_hla/hla_region.bam
    # samtools 1.3.1 doesn't auto-compress, output to uncompressed then gzip
    samtools fastq         -1 HG00096.mate_aware_hla/R1.fastq         -2 HG00096.mate_aware_hla/R2.fastq         -0 /dev/null -s /dev/null         HG00096.mate_aware_hla/namesort.bam
    gzip HG00096.mate_aware_hla/R1.fastq
    gzip HG00096.mate_aware_hla/R2.fastq

    # Step 2: Run SpecHLA
    echo "[Step 2] Running SpecHLA from pipeline-generated HLA BAM..."
    cd HG00096.mate_aware_hla
    bash ${SPECHLA_PATH}/script/whole/SpecHLA.sh         -n HG00096.mate_aware_hla         -1 R1.fastq.gz         -2 R2.fastq.gz         -o .         -j 16         -u 0
    cd ..

    # Step 3: Parse results
    echo "[Step 3] Parsing results..."
    # SpecHLA writes one row per sample with a column pair per gene. Every other
    # caller here emits one row per gene, and modules/aggregation.nf reads only
    # that -- so copying SpecHLA's native layout through meant it contributed
    # nothing to the consensus despite calling correctly. Keep the raw file and
    # emit the long form under the name aggregation matches.
    if [ -f "HG00096.mate_aware_hla/hla.result.txt" ]; then
        cp HG00096.mate_aware_hla/hla.result.txt HG00096.mate_aware_hla_spechla_raw.txt
    elif [ -f "HG00096.mate_aware_hla/HG00096.mate_aware_hla/hla.result.txt" ]; then
        cp HG00096.mate_aware_hla/HG00096.mate_aware_hla/hla.result.txt HG00096.mate_aware_hla_spechla_raw.txt
    else
        # Never manufacture an empty result. A placeholder file exits 0 and is
        # indistinguishable downstream from a caller that genuinely typed
        # nothing -- which is how SpecHLA produced header-only files for months
        # without anyone being told. Fail, and say where to look.
        echo "SpecHLA produced no hla.result.txt for HG00096.mate_aware_hla." >&2
        echo "Looked in HG00096.mate_aware_hla/ and HG00096.mate_aware_hla/HG00096.mate_aware_hla/. Contents:" >&2
        ls -la HG00096.mate_aware_hla/ >&2 || true
        exit 1
    fi

    python3 /scratch/project_2008084/pihla-publish_v5/bin/parse_spechla_results.py         --input  HG00096.mate_aware_hla_spechla_raw.txt         --sample HG00096.mate_aware_hla         --output HG00096.mate_aware_hla_spechla.txt

    # Cleanup intermediate files
    rm -f HG00096.mate_aware_hla/namesort.bam

    # Version info
    cat <<END_VERSIONS > versions.yml
"SPECHLA_BAM":
    spechla: "1.0.7"
    samtools: $(samtools --version | head -1 | cut -d' ' -f2)
END_VERSIONS
