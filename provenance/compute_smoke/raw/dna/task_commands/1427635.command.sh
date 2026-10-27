#!/bin/bash -ue
samtools sort -n -@ 8 HG00096.mate_aware_hla.bam -o HG00096.mate_aware_hla.namesort.bam
samtools fastq -@ 8       -1 HG00096.mate_aware_hla_R1.fastq.gz       -2 HG00096.mate_aware_hla_R2.fastq.gz       -0 /dev/null -s /dev/null       HG00096.mate_aware_hla.namesort.bam
rm -f HG00096.mate_aware_hla.namesort.bam
