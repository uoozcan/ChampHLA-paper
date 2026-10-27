#!/bin/bash -ue
mkdir -p HG00096.mate_aware_hla_polysolver_raw

    echo "[POLYSOLVER] Running on HG00096.mate_aware_hla (build: hg38)..."

    # Fix 1: novoalign stack overflow on modern kernels (default 8MB stack too small)
    ulimit -s unlimited

    # Fix 2: SAMTOOLS_DIR env var is unset in container for hg38 branch
    export SAMTOOLS_DIR=/home/polysolver/binaries

    # Fix 3: Picard SamToFastq "Illegal mate state" — pre-sort by name + fixmate + re-sort
    # Required when BAM has inconsistent mate flags (common in some pipelines)
    echo "[POLYSOLVER] Applying fixmate pre-processing for HG00096.mate_aware_hla..."
    /home/polysolver/binaries/samtools sort -n HG00096.mate_aware_hla.bam HG00096.mate_aware_hla_namesort
    /home/polysolver/binaries/samtools fixmate HG00096.mate_aware_hla_namesort.bam HG00096.mate_aware_hla_fixmate.bam
    /home/polysolver/binaries/samtools sort HG00096.mate_aware_hla_fixmate.bam HG00096.mate_aware_hla_fixed
    /home/polysolver/binaries/samtools index HG00096.mate_aware_hla_fixed.bam
    POLYSOLVER_INPUT="HG00096.mate_aware_hla_fixed.bam"

    # Fix 4: SortSam.jar has TMP_DIR=/home/polysolver hardcoded — patch script at runtime
    # /home/polysolver is read-only in Singularity; replace with writable CWD tmp
    mkdir -p picard_tmp
    PICARD_TMP=$(pwd)/picard_tmp
    export _JAVA_OPTIONS="-Djava.io.tmpdir=${PICARD_TMP}"
    # Fix 5: POLYSOLVER hardcodes its hg38 HLA regions without a chr prefix --
    # `samtools view HG00096.mate_aware_hla.bam 6:29941260-29945884` -- but GRCh38_full_analysis_set BAMs
    # name the contig chr6. Every region query then matches nothing, POLYSOLVER
    # writes no winners file, and the run looks like a tool that found no alleles:
    #   [main_samview] region "6:29941260-29945884" specifies an unknown reference name
    # Detect the naming from the BAM header, the same way modules/spechla.nf does,
    # and rewrite the queries to match.
    CHR6=$(/home/polysolver/binaries/samtools view -H HG00096.mate_aware_hla.bam               | awk '/^@SQ.*SN:chr6	/{print "chr6"; exit} /^@SQ.*SN:6	/{print "6"; exit}')
    if [ -z "${CHR6}" ]; then CHR6=6; fi
    echo "[POLYSOLVER] BAM names chromosome 6 as '${CHR6}'"

    if [ "${CHR6}" = "chr6" ]; then
        SED_CHR='s|\$bam 6:|\$bam chr6:|g'
    else
        SED_CHR='s|__panelhla_noop__|__panelhla_noop__|'
    fi

    sed -e "s|TMP_DIR=/home/polysolver|TMP_DIR=${PICARD_TMP}|g"         -e "${SED_CHR}"         /home/polysolver/scripts/shell_call_hla_type > patched_shell_call_hla_type
    chmod +x patched_shell_call_hla_type

    # POLYSOLVER args: BAM race includeFreq build format insertCalc outdir
    # race=Unknown (population-agnostic), includeFreq=0, insertCalc=0 (germline)
    # Record the status instead of discarding it with `|| true`. The process sets
    # errorStrategy 'ignore', so one bad sample still does not kill a run -- but a
    # crash is now distinguishable from a clean run that found nothing.
    set +e
    bash patched_shell_call_hla_type         $POLYSOLVER_INPUT Unknown 0 hg38 STDFQ 0 HG00096.mate_aware_hla_polysolver_raw
    POLYSOLVER_RC=$?
    set -e
    echo "[POLYSOLVER] shell_call_hla_type exit=${POLYSOLVER_RC}"

    # Cleanup intermediate BAMs
    rm -f HG00096.mate_aware_hla_namesort.bam HG00096.mate_aware_hla_fixmate.bam HG00096.mate_aware_hla_fixed.bam HG00096.mate_aware_hla_fixed.bam.bai

    # Parse winners.hla.nofreq.txt → standard pipeline TSV
    if [ -f "HG00096.mate_aware_hla_polysolver_raw/winners.hla.nofreq.txt" ]; then
        python3 /scratch/project_2008084/pihla-publish_v5/bin/parse_polysolver_results.py             --input  HG00096.mate_aware_hla_polysolver_raw/winners.hla.nofreq.txt             --sample HG00096.mate_aware_hla             --output HG00096.mate_aware_hla_polysolver.txt
    else
        # Never manufacture an empty result. A placeholder file exits 0 and is
        # indistinguishable downstream from a caller that genuinely typed nothing.
        echo "POLYSOLVER produced no winners.hla.nofreq.txt for HG00096.mate_aware_hla" >&2
        echo "shell_call_hla_type exited ${POLYSOLVER_RC}; chromosome 6 named '${CHR6}'." >&2
        echo "Contents of HG00096.mate_aware_hla_polysolver_raw:" >&2
        ls -la HG00096.mate_aware_hla_polysolver_raw >&2 || true
        exit 1
    fi

    cat <<END_VERSIONS > versions.yml
"POLYSOLVER":
    polysolver: "v4"
END_VERSIONS
