> Canonical research source now lives under `pgx-site/research/`. Run `python3 verify.py` from the repository root for full offline verification. Commands below are relative to this research directory.

# Pharmacogenomics evidence workbench

Technical foundation for the Context educational evidence-comparison project. A private interface is implemented in the parent directory of this consolidated repository at https://pgx-evidence.piloe1.chatgpt.site. Jordan will review visual direction later from a laptop; technical work continues meanwhile.

## The question

How does the source context change what a clopidogrel–CYP2C19 evidence record means, and can a reviewer trace each statement to the exact source version?

## First workflow

Intended reader: a clinician-educator or health-tech reviewer comparing source scope, rather than a patient seeking medication changes. This is a product hypothesis, not validated user research.

1. Open the fixed drug–gene pair and see source names, snapshot date and scope.
2. Choose a source context and phenotype category as document filters, not patient inputs.
3. Inspect the original record, classification, source pointer and limitations.
4. Compare another context without treating a different population as contradictory evidence.
5. Distinguish explicit “No Recommendation,” missing source data, and a context the source does not cover.
6. Compare two pinned snapshots and export the specific records and changes for review.

Initial synthetic task: a reviewer sees a record for one source context and asks whether it can be transferred to another. Success means identifying the context boundary, finding the appropriate source record, explaining any missing coverage and exporting its provenance. No patient profile, genotype upload, medication list, dose calculation or prescribing output.

## Distinct portfolio contribution

Fieldnotes demonstrated quantitative cohort analysis. This project adds heterogeneous evidence modeling and source-version reconciliation. It must distinguish differences in scope from genuine disagreements, and detect source text changes even when a classification label stays the same. It should help a reader inspect original guidance, not claim authority over that guidance.

Alternatives are the original CPIC/ClinPGx pages, the guideline publication and the FDA tables/labeling. The project must preserve direct links to those sources. Convenience and reproducibility are proposed benefits; no time-saving or safety claim is established.

## Implemented

- Four bounded CPIC API snapshots: drug, guideline, recommendations and publications.
- Exact request URLs, retrieval timestamps, byte counts and SHA-256 checksums.
- A validated index of 24 records, three source context codes and eight phenotype categories.
- Joins on drug/guideline identity; unique record and context/phenotype checks.
- Source versions, raw population strings, classification states, exact JSON pointers and row hashes.
- Context-required lookup; missing context never silently inherits another record.
- Added/removed/changed record comparison, including text changes represented by row hashes.
- Thirty tests covering source structure, exact joins, missing context, phenotype mapping, conservative comparison, export tampering and refresh failure recovery. No third-party Python packages required.
- A separately pinned FDA association-table snapshot and parser with changed-structure/subgroup rejection.
- Context labels mapped to the 2022 guideline tables; current page history reviewed and all 24 API records checked against its downloadable recommendation workbook.
- A reproducible two-source scope-comparison artifact with explicit no-inference boundaries.

## Run locally

Python 3.9+; snapshot activation uses Unix file locking (macOS/Linux):

```sh
python3 scripts/evidence.py
python3 scripts/fda.py
python3 scripts/build.py
python3 scripts/reconcile.py
python3 -m unittest discover -s tests -v
```

These commands use saved snapshots and require no network. `scripts/acquire.py` is for a fresh empty raw directory; it deliberately refuses to overwrite a recorded snapshot. Use the snapshot commands below for subsequent refreshes. A source index is derived from validated raw bytes; the hashes establish consistency with the manifest, not independent authenticity of the publisher.

## Sources and terms

CPIC API: https://api.cpicpgx.org/ . Exact endpoint requests are in `data/source-manifest.json`. Source row versions are preserved; retrieval time is not publication date. A multi-request acquisition is not an atomic upstream database snapshot.

CPIC content terms: https://github.com/cpicpgx/cpic-data/blob/main/LICENSE.md . Curated content is CC0; retain attribution, guideline references and source dates. No CPIC logo is used. Provider notes warn that API and guideline-page updates can differ. This is why the original guideline still needs review alongside structured records.

The March 2026 schema migration is documented at https://blog.clinpgx.org/updates-to-the-cpic-database-and-api/ . Current fields use `clinpgxid`. The general PharmGKB API hostname was retired in favor of ClinPGx; the installed PharmGKB helper has an old hostname and missing local requests dependency, so this foundation uses the independently documented CPIC API directly. No PharmGKB annotation payload was imported.

FDA comparison source ingested separately with its own manifest: https://www.fda.gov/medical-devices/precision-medicine/table-pharmacogenetic-associations . Its table is not a substitute for product labeling and does not provide comprehensive prescribing information. The FDA association table, a drug label, a CPIC guideline and curated clinical annotations must remain distinct source types.

## Next gates before interface implementation

1. Context labels have been checked against Tables 2 and 3 of the 2022 publication (DOI 10.1002/cpt.2526). Raw codes remain preserved.
2. Page-history review and pinned workbook/API correspondence are complete for this capture. Retain their scope and retrieval dates; refresh does not automatically renew this review.
3. FDA association-table adapter and conservative source-scope policy are implemented. Preserve the distinction from a drug label; add no automatic clinical conflict/equivalence verdict.
4. Snapshot refresh, source-change review, failure recovery and reproducible exports are implemented and verified; integrate them into the browser journey.
5. Build one complete browser journey from the above real records. Design direction: a document comparison workspace with readable original evidence, context visible beside every claim, and explicit provenance. Avoid repeating the Fieldnotes scatterplot layout or creating a generic patient dashboard.

The private UI is implemented; no clinical reconciliation verdict, diplotype interpretation or validated clinical workflow is claimed. The implemented comparison concerns source scope only. C15 peptide design remains deferred until current projects and the personal portfolio are complete.

## Source-context review

`data/context-map.json` records manually reviewed labels and exact table/footnote locations from https://pmc.ncbi.nlm.nih.gov/articles/PMC9287492/ . The bibliography join verifies that its DOI occurs in the pinned guideline publications, but does not prove that the current API and guideline page are synchronized. The generic CPIC population endpoint describes study populations/ethnicity and is not the meaning table for these recommendation-context codes; it was not imported.

`data/derived/comparison.json` contains 24 contextual comparisons. Explicit FDA subgroup membership is retained only for its named categories; likely phenotypes are not silently merged. A missing/changed FDA row fails parsing. CPIC absence, explicit No Recommendation and an unlisted FDA subgroup remain separate states. The raw FDA HTML is saved for reproducible parsing; original government source URL and retrieval timestamp accompany every derived comparison.

## Snapshot refresh and portable export

Each `data/snapshots/<sha256>.json` file is a portable bundle containing all five exact source texts, their manifests, the reviewed context map and the derived comparison. Copy that file to export it. Replay recomputes the comparison offline and rejects mismatched source bytes or altered derived results.

```sh
python3 scripts/snapshots.py pack
python3 scripts/snapshots.py replay data/snapshots/SNAPSHOT_ID.json
python3 scripts/snapshots.py refresh SNAPSHOT_ID
python3 scripts/snapshots.py compare OLD_ID CANDIDATE_ID
python3 scripts/snapshots.py activate CANDIDATE_ID --expected-current OLD_ID
```

Replace the capitalized IDs with emitted snapshot IDs. First activation uses `--expected-current none`. Refresh stages a candidate only after all five bounded requests and validation succeed. Compare shows changed source files, CPIC records, FDA content and manually reviewed context mappings. Explicit activation checks the expected prior ID under a file lock, then atomically replaces the current pointer. Older bundles remain available; a failed request cannot partially replace current evidence.

Live verification on September 29, 2026: all five source contents were unchanged; the newly retrieved bundle replayed all 24 comparisons. The active baseline remained `32bcccb9563bb8786ecb3565aca14754f46c4fb6f2145e708112a52d53c413a8`; staged candidate `b9e899c09ecf593a50ae8e7a7d145d4392e48961f74eb5f76812b9c84104ae42` differs by retrieval metadata. No candidate was automatically promoted.

Checksums establish internal consistency, not publisher authentication. The context map remains a reviewed interpretation, not a signed authority. Separate upstream requests are not a simultaneous database snapshot. The local pointer is not a regulated audit trail; filesystem crash durability is not claimed. No clinical equivalence is inferred from a successful replay.

## Guideline correspondence checkpoint

The former CPIC guideline URL redirects to the ClinPGx guideline page. Its rendered page lists the 2022 publication and two history entries: a March 2026 summary gene-name correction and a June 2025 literature addition. The manual observation, method and limits are recorded in `data/review/guideline-page-review.json`.

The page-linked recommendation workbook is pinned separately, with URL, retrieval time, byte count and SHA-256 in `data/review/recommendation-manifest.json`. `scripts/reconcile.py` checks all 24 context/phenotype records against the captured API: implications, recommendation text, classification and comments match exactly. Each check preserves sheet name, cell range and API record ID in `data/derived/guideline-reconciliation.json`. Missing or duplicate records fail validation; differences are reported rather than interpreted as clinical conflicts.

This is a separate review artifact. Existing portable bundles retain their original limitations and bytes; they do not retroactively acquire a review. A new source snapshot must be compared again before the interface displays a correspondence claim. The workbook and API may share upstream data, so agreement is not independent scientific validation. No allele/diplotype interpretation or prescribing validation was performed.
