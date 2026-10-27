# IPD-IMGT/HLA normalization resources

Run `scripts/fetch_ipd_imgt_hla_365.sh` to acquire the unchanged official
IPD-IMGT/HLA 3.65.0 allele, deletion, P-group and G-group files from tag
`v3.65.0-alpha` of `ANHIG/IMGTHLA`. The script records SHA-256 checksums and
retains the upstream licence. Extension analysis must fail closed if these files
or their checksums are absent; legacy development calls remain explicitly marked
as syntax-only normalization.
