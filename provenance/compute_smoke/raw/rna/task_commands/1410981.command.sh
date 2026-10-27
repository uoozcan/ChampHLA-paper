#!/bin/bash -ue
echo "[seq2HLA] Running on HG00096..."

# seq2HLA writes output files prefixed by the -r value.
# With -r HG00096. the tool produces:
#   HG00096.-ClassI-class.HLAgenotype4digits    (A, B, C)
#   HG00096.-ClassI-nonclass.HLAgenotype4digits (E, F, G, ... — not used)
#   HG00096.-ClassII.HLAgenotype4digits          (DRB1, DQA1, DQB1, DPA1, DPB1)
seq2HLA         -r HG00096.         -p 8         -1 HG00096_R1.fastq.gz         -2 HG00096_R2.fastq.gz
SEQ2HLA_EXIT=$?
if [ $SEQ2HLA_EXIT -ne 0 ]; then
    echo "[seq2HLA] WARNING: seq2HLA exited with code ${SEQ2HLA_EXIT} for HG00096" >&2
fi

# Parse classical Class I + Class II result files → standard pipeline TSV
# Uses the Python 2/3 compatible parse_seq2hla_results.py script
# (seq2HLA container has Python 2.7 only — script uses 'python' shebang)
python /scratch/project_2008084/pihla-publish_verify/bin/parse_seq2hla_results.py         --sample HG00096         --prefix "HG00096."         --output HG00096_seq2hla.txt

cat <<-END_VERSIONS > versions.yml
"SEQ2HLA":
    seq2hla: "2.3"
END_VERSIONS
