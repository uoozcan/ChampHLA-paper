#!/bin/bash -ue
mkdir -p HG00096

    # Link FASTQs named as HG00096.1/2.fq.gz so arcasHLA output JSON
    # is named HG00096.genotype.json (parseable without glob)
    if [[ "HG00096_R1.fastq.gz" == *.gz ]]; then
        ln -sf "$(realpath HG00096_R1.fastq.gz)" HG00096/HG00096.1.fq.gz
        ln -sf "$(realpath HG00096_R2.fastq.gz)" HG00096/HG00096.2.fq.gz
    else
        gzip -c HG00096_R1.fastq.gz > HG00096/HG00096.1.fq.gz
        gzip -c HG00096_R2.fastq.gz > HG00096/HG00096.2.fq.gz
    fi

    echo "[Running arcasHLA genotype from FASTQ...]"
    # Patch arcasHLA align.py for KeyError: '0' bug (counts.get instead of counts[key])
    mkdir -p arcas_patch
    cp /home/arcasHLA-master/scripts/*.py ./arcas_patch/
    sed -i "s/count = counts\[eq\]/count = counts.get(eq, 0)/" ./arcas_patch/align.py
    export PYTHONPATH="$(pwd)/arcas_patch:${PYTHONPATH:-}"
    arcasHLA genotype         HG00096/HG00096.1.fq.gz         HG00096/HG00096.2.fq.gz         -o HG00096         -t 8         --min_count 75         -v

    # Copy genotype JSON with consistent name for downstream parsing
    echo "[Parsing results...]"
    GENOTYPE_JSON="HG00096/HG00096.genotype.json"
    if [ ! -f "$GENOTYPE_JSON" ]; then
        # Fall back to glob in case arcasHLA used a different stem
        GENOTYPE_JSON=$(find HG00096 -name "*.genotype.json" | head -1)
    fi

    if [ -n "$GENOTYPE_JSON" ] && [ -f "$GENOTYPE_JSON" ]; then
        cp "$GENOTYPE_JSON" HG00096_arcashla.json
        python3 - "$GENOTYPE_JSON" "HG00096_arcashla.txt" "HG00096" << 'PYEOF'
import json, sys
# Classical HLA genes only — non-classical (DMA, DMB, DOA, DOB, E, F, G, H, J, K, L)
# are not in the calibration ground truth and not needed for consensus voting
CLASSICAL = {'A', 'B', 'C', 'DRB1', 'DRB3', 'DRB4', 'DRB5',
             'DQA1', 'DQB1', 'DPA1', 'DPB1'}
json_path, out_path, sample = sys.argv[1], sys.argv[2], sys.argv[3]
with open(json_path) as f:
    data = json.load(f)
with open(out_path, 'w') as out:
    out.write("# arcasHLA results for {}\n".format(sample))
    out.write("Gene\tAllele1\tAllele2\n")
    for gene, alleles in sorted(data.items()):
        if gene not in CLASSICAL:
            continue
        if isinstance(alleles, list):
            a1 = alleles[0] if len(alleles) > 0 else '-'
            a2 = alleles[1] if len(alleles) > 1 else '-'
            out.write("HLA-{}\t{}\t{}\n".format(gene, a1, a2))
PYEOF
    else
        # Never manufacture an empty result. A placeholder file exits 0 and is
        # indistinguishable downstream from a caller that genuinely typed
        # nothing -- which is how SpecHLA produced header-only files for months
        # without anyone being told. Fail, and say where to look.
        echo "arcasHLA produced no parsable output for HG00096" >&2
        echo "Expected a genotype JSON. Working directory contains:" >&2
        ls -la . >&2 || true
        exit 1
    fi

    # Version info
    cat <<-END_VERSIONS > versions.yml
    "ARCASHLA_FASTQ":
        arcashla: $(arcasHLA 2>&1 | grep -oP '(?<=arcasHLA )[0-9.]+' | head -1 || echo "unknown")
    END_VERSIONS
