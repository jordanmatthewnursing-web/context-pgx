# Context: reading pharmacogenomic evidence in its clinical context

Technical case-study draft. Jordan has not approved this as public portfolio copy.

## The question

How does clinical context change the meaning of a clopidogrel–CYP2C19 recommendation, and can a reader follow each statement back to its source?

## What I built

An educational evidence workbench for one drug–gene pair. A reader selects a phenotype category and clinical context, reads the original CPIC recommendation and qualifications, and compares the FDA association row without treating the two sources as interchangeable. The interface also shows source provenance and changes between saved captures.

The intended user is a clinician-educator or health-tech reviewer. That is a product hypothesis; no independent workflow study has established usefulness or time savings.

## How it works

Four captured CPIC API responses join drug identity, guideline identity, recommendation records and publications. A separate parser extracts the clopidogrel–CYP2C19 row from the FDA association table. The data model preserves 24 CPIC records across three clinical contexts and eight phenotype categories.

Clinical context is mandatory. Missing coverage, an explicit “No Recommendation,” and an unlisted FDA subgroup remain separate states. “Likely” phenotypes are not silently merged into the FDA's named categories. The app does not infer clinical agreement from overlapping words or assign its own evidence score.

Each snapshot contains original source text, retrieval metadata, checksums and the derived comparison. Offline replay reconstructs the comparison. Refresh stages a candidate; activation checks the expected prior snapshot under a file lock. The browser verifies captured bytes before displaying evidence. Review and history load independently, with request and file-size limits.

The guideline page's linked workbook was captured separately. All 24 recommendation records match its implications, recommendation text, classification and comments. That is text correspondence; the workbook and API may share an upstream database.

## Result

A working private prototype with traceable source records, reproducible comparison and explicit failure states. The two real captures currently displayed contain identical source content and different retrieval metadata. Synthetic tests demonstrate that changed wording is detected even when classification stays unchanged; those fixtures are never presented as real guideline updates.

Verification includes 33 research tests, seven resource-loading tests, browser checks of all 24 selections, keyboard navigation, narrow-screen layout and fault isolation. These checks do not establish clinical correctness, screen-reader conformance or real-world adoption. Final downloaded-file confirmation in the embedded browser remains unresolved.

## Design decisions

A restrained document workspace keeps the active context beside the recommendation. The FDA record occupies a visibly separate section. Source details use progressive disclosure, and the same phenotype can be compared across all three contexts. The layout uses locally bundled Newsreader and IBM Plex Sans, a green control panel and fine rules. Final design review with Jordan remains open.

## Reproduce and inspect

One self-contained repository: `research/` contains the research pipeline and `dist/` the interface. No public GitHub repository is claimed yet.

```sh
python3 verify.py
python3 research/scripts/snapshots.py replay PATH_TO_EXPORTED_BUNDLE
```

## What I'd do next

Validate whether a reviewer can explain the context boundary and trace the source without assistance. Complete independent accessibility and device checks before making usability claims or expanding to another drug–gene pair.

## Two-minute walkthrough

1. Choose **Intermediate Metabolizer**. Compare all three contexts; the recorded classifications differ.
2. Open the recommendation's qualifications. Explain which source context applies to that text.
3. Inspect the FDA association row. Explain why its scope does not establish an equivalent context-specific recommendation.
4. Open **What changed?** The current pair has no source-content changes; retrieval time is not a new guideline publication.
5. Inspect provenance and export the bundle. Explain the difference between hash consistency, offline replay and independent scientific validation.

A useful reviewer task: find the original qualification, state a limitation, and reproduce the selected record. Observe errors and unanswered questions; do not invent success rates.
