"""Build the reviewer-response copy of the combined document.

Encodes one specific round: Ziaurrehman Tanoli's seventeen comments of
2026-10-05 on the Google Drive copy. It writes a NEW file rather than editing
the reviewed one, because that copy is a native Google Doc whose comment
threads cannot be preserved through a replacement upload.

The body text comes from the corrected markdown via the normal Drive build,
NOT from the reviewed DOCX: the reviewed copy was generated from an older
build and lacks the NCI-60 section and other later work. Each reviewer comment
is lifted verbatim out of the reviewed file, re-anchored to the paragraph
carrying the revised wording, and given a reply beneath it.

Usage:
    python scripts/build_review_response_docx.py [REVIEWED_DOCX] [OUTPUT_DOCX]
"""
import re
import shutil
import sys
import zipfile
from pathlib import Path
from xml.sax.saxutils import escape

from docx import Document

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
WQ = '{%s}' % W

ROOT = Path(__file__).resolve().parents[1]
BENCHMARK = ROOT / 'manuscripts' / 'benchmark'
BUILT = BENCHMARK / 'PanelHLA_manuscript_COMBINED_DRIVE.docx'

REVIEWED = Path(sys.argv[1]) if len(sys.argv) > 1 else (
    Path.home().parent / 'uonur' / 'Downloads' / 'PanelHLA_Manuscript_v1.docx')
OUT = Path(sys.argv[2]) if len(sys.argv) > 2 else (
    BENCHMARK / 'PanelHLA_Manuscript_v2.docx')

RESPONDER = 'Umut Onur Özcan'
RESPONDED = '2026-10-06T00:00:00Z'

# anchor text in the REVISED document -> reply for that comment id
SPEC = {
    '0':  ("A fitted policy that selects the single best caller",
           "Rewritten in plain language: it now says directly that picking the "
           "single best caller did not improve on the plurality vote, and says "
           "what phi measures. All values unchanged."),
    '1':  ("PanelHLA is a transparent",
           "Moved out of the Abstract as you asked. It now opens this closing "
           "passage in Conclusions."),
    '2':  ("disease-association research",
           "Expanded in place: HLA alleles tested for statistical association "
           "with susceptibility to autoimmune and infectious disease."),
    '3':  ("OptiType uses integer programming",
           "Done. Each caller now carries its own citation: OptiType (Szolek "
           "2014), HLA-HD (Kawaguchi 2017), arcasHLA (Orenbuch 2019), POLYSOLVER "
           "(Shukla 2015), T1K (Song 2023), SpecHLA (Wang 2023)."),
    '4':  ("another important caller class",
           "Described: they align reads to a graph in which known alleles are "
           "alternative paths, rather than to one linear reference, so reads "
           "from strongly divergent alleles can still be placed correctly."),
    '5':  ("result tables produced by that earlier analysis",
           "Disambiguated, and the defect is now stated: a single allele was "
           "selected from an ambiguous typing string instead of the ambiguity "
           "being treated as unresolved."),
    '6':  ("means that the caller outputs were produced",
           "Rewritten: the outputs were produced by an earlier run and kept as "
           "files; that workflow is not part of this repository, so the "
           "benchmark starts from the stored outputs, not from raw reads."),
    '7':  ("separately pre-registered protocol",
           "Defined on first use. PLEASE CONFIRM this matches your intent: a "
           "second pre-registered protocol locking a subject-disjoint "
           "public-data extension before any truth labels are joined."),
    '8':  ("International Genome Sample Resource",
           "Expanded. A full first-use audit was also run over both documents "
           "and five more abbreviations were expanded: nested-CV, CR1, TSV, "
           "AML, MDS and HED."),
    '9':  ("cryptographic digest of the file contents",
           "Glossed in place. The checksum value itself is kept deliberately - "
           "removing it would weaken the auditability the paper argues for."),
    '10': ("is one individual in the public 1000 Genomes",
           "A definition was added before first substantive use: a subject is "
           "one individual in these public collections, and a locus is one "
           "subject-gene pair within one assay."),
    '11': ("consented population-genomics donors, not patients",
           "No - and the text now says so explicitly. These are consented "
           "population-genomics donors; no clinical samples are involved."),
    '12': ("Because no outputs from these callers survive",
           "Explained: no outputs from those callers survive in the recovered "
           "data, so they could not be scored, and no claim is made about them "
           "in either direction."),
    '13': ("exact unordered diploid concordance at two-field resolution",
           "Defined: a locus counts as concordant only when both predicted "
           "alleles match both reference alleles to the first two fields, in "
           "either order, with no credit for matching one allele of the pair."),
    '14': ("national computing centre used for this work",
           "Rewritten for an external reader. PLEASE CONFIRM that CSC may be "
           "named here and in Acknowledgements."),
    '15': ("refuses to run if any input table carries",
           "Explained as an enforced code behaviour - this is the truth "
           "firewall: prediction cannot run if any input carries a "
           "reference-genotype column."),
    '16': ("Study design, truth firewall and cohort flow",
           "Done for the main text: Figures 1-4 now sit immediately after the "
           "paragraph that first cites them, and the separate Figure legends "
           "section is gone. Tables already appeared in place. The supplement "
           "is left collected on purpose - only S5-S7 are cited inside it, so "
           "inlining there put the supplementary figures out of numeric order. "
           "Say the word and I will inline those too."),
}


def reviewed_comments():
    with zipfile.ZipFile(REVIEWED) as z:
        import xml.etree.ElementTree as ET
        root = ET.fromstring(z.read('word/comments.xml'))
        out = {}
        for c in root.findall(WQ + 'comment'):
            text = ''.join(t.text or '' for t in c.iter(WQ + 't'))
            out[c.get(WQ + 'id')] = {
                'author': c.get(WQ + 'author'),
                'date': c.get(WQ + 'date'),
                'initials': c.get(WQ + 'initials') or '',
                'text': re.sub(r'\s+', ' ', text).strip(),
            }
    return out


def norm(s):
    return re.sub(r'\s+', ' ', s.replace('\u00a0', ' ')).strip().lower()


def main():
    originals = reviewed_comments()
    missing = set(SPEC) - set(originals)
    assert not missing, f'no such comment id in the reviewed file: {missing}'

    shutil.copyfile(BUILT, OUT)
    document = Document(str(OUT))
    paragraphs = document.paragraphs

    entries = []          # (comment_id, author, date, initials, text)
    next_id = 0
    unmatched = []

    for cid in sorted(SPEC, key=int):
        anchor, reply = SPEC[cid]
        target = next((p for p in paragraphs
                       if norm(anchor) in norm(p.text)), None)
        if target is None:
            unmatched.append((cid, anchor))
            continue

        original = originals[cid]
        ids = []
        for author, date, initials, body in (
            (original['author'], original['date'], original['initials'],
             original['text']),
            (RESPONDER, RESPONDED, 'UOÖ', 'RESPONSE: ' + reply),
        ):
            entries.append((next_id, author, date, initials, body))
            ids.append(next_id)
            next_id += 1

        element = target._p
        # w:pPr, when present, must stay the first child of w:p, so the range
        # markers go after it rather than at index 0.
        first = 1 if (len(element) and element[0].tag == WQ + 'pPr') else 0
        for offset, i in enumerate(ids):
            start = element.makeelement(WQ + 'commentRangeStart', {WQ + 'id': str(i)})
            element.insert(first + offset, start)
        for i in ids:
            end = element.makeelement(WQ + 'commentRangeEnd', {WQ + 'id': str(i)})
            element.append(end)
            run = element.makeelement(WQ + 'r', {})
            ref = element.makeelement(WQ + 'commentReference', {WQ + 'id': str(i)})
            run.append(ref)
            element.append(run)

    document.save(str(OUT))

    comments_xml = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
                    '<w:comments xmlns:w="%s">' % W]
    for cid, author, date, initials, body in entries:
        comments_xml.append(
            '<w:comment w:id="%d" w:author="%s" w:date="%s" w:initials="%s">'
            '<w:p><w:r><w:t xml:space="preserve">%s</w:t></w:r></w:p></w:comment>'
            % (cid, escape(author, {'"': '&quot;'}), escape(date),
               escape(initials, {'"': '&quot;'}), escape(body)))
    comments_xml.append('</w:comments>')
    comments_blob = ''.join(comments_xml).encode('utf-8')

    with zipfile.ZipFile(OUT) as z:
        parts = {n: z.read(n) for n in z.namelist()}

    parts['word/comments.xml'] = comments_blob

    rels = parts['word/_rels/document.xml.rels'].decode('utf-8')
    if 'comments.xml' not in rels:
        rid = 'rIdComments'
        rels = rels.replace('</Relationships>',
                            '<Relationship Id="%s" Type="http://schemas.openxml'
                            'formats.org/officeDocument/2006/relationships/'
                            'comments" Target="comments.xml"/></Relationships>'
                            % rid)
        parts['word/_rels/document.xml.rels'] = rels.encode('utf-8')

    types = parts['[Content_Types].xml'].decode('utf-8')
    if 'wordprocessingml.comments+xml' not in types:
        types = types.replace('</Types>',
                              '<Override PartName="/word/comments.xml" '
                              'ContentType="application/vnd.openxmlformats-'
                              'officedocument.wordprocessingml.comments+xml"/>'
                              '</Types>')
        parts['[Content_Types].xml'] = types.encode('utf-8')

    with zipfile.ZipFile(OUT, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for name in sorted(parts):
            info = zipfile.ZipInfo(name, (2000, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            z.writestr(info, parts[name])

    print('wrote %s' % OUT.name)
    print('  comments written : %d (%d reviewer + %d responses)'
          % (len(entries), len(entries) // 2, len(entries) // 2))
    if unmatched:
        print('  UNMATCHED ANCHORS:')
        for cid, anchor in unmatched:
            print('    #%s  %s' % (cid, anchor))
    else:
        print('  every one of the 17 comments was re-anchored')


main()
