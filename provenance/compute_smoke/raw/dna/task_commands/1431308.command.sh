#!/bin/bash -ue
if [ -n "/scratch/project_2008084/pihla-publish_v5/conf/tool_weights_wgs.json" ] && [ -f "/scratch/project_2008084/pihla-publish_v5/conf/tool_weights_wgs.json" ]; then
      cp "/scratch/project_2008084/pihla-publish_v5/conf/tool_weights_wgs.json" runtime_weights.json
    else
      python3 - << 'PYEOF'
import csv
import json
from collections import defaultdict

modality = "wgs"
weights = {"tool_weights": defaultdict(dict), "gene_weights": defaultdict(lambda: defaultdict(dict))}

with open("aggregated_calls.tsv", "r", encoding="utf-8") as handle:
    r = csv.DictReader(handle, delimiter="	")
    seen = defaultdict(set)
    for row in r:
        tool = row.get("tool", "").strip()
        gene = row.get("gene", "").strip()
        if not tool or not gene:
            continue
        seen[tool].add(gene)

for tool, genes in seen.items():
    weights["tool_weights"][tool][modality] = {"final_weight": 1.0}
    for gene in genes:
        weights["gene_weights"][tool][modality][gene] = {"final_weight": 1.0}

# convert defaultdicts
weights["tool_weights"] = dict(weights["tool_weights"])
weights["gene_weights"] = {k: dict(v) for k, v in weights["gene_weights"].items()}

with open("runtime_weights.json", "w", encoding="utf-8") as out:
    json.dump(weights, out, indent=2, sort_keys=True)
PYEOF
    fi

    python3 /scratch/project_2008084/pihla-publish_v5/bin/majority_voting.py       --calls aggregated_calls.tsv       --weights runtime_weights.json       --output consensus_calls.tsv       --weighting calibrated       --min-weight 0.0
