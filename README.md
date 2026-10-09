# Context — pharmacogenomics evidence

A public educational genetic-file reader for three CYP2C19 markers, one SLCO1B1 marker and four direct DPYD variants, with medication context for clopidogrel, six proton pump inhibitors simvastatin, fluorouracil and capecitabine, plus a separate clopidogrel evidence library. Import a supported 23andMe text export or try synthetic data. The report derives conditional medication implications from detected markers, shows the reported basis and coverage gaps, and does not infer a complete genotype, metabolizer status or prescribing decision.

Results can be saved as a readable, offline HTML report or technical JSON. Browser Print/PDF styles are included; actual PDF output remains unverified.

See [genetic-reader scope and verification](docs/GENETIC_READER.md). The earlier document comparison remains at `evidence.html`. The architecture and historical checks below describe that library unless specified otherwise.

## Run

Requirements: Python 3.9+, Node.js 22+, macOS or Linux (snapshot activation uses Unix file locking). No package installation is required.

```sh
python3 verify.py
python3 -m http.server 4182 --bind 127.0.0.1 --directory dist
```

Open http://127.0.0.1:4182/. Verification uses the bundled captures offline, runs 33 research tests and seven loading tests, reconstructs the correspondence review, replays the evidence bundle and requires byte-identical packaged artifacts. `python3 prepare.py` rebuilds artifacts after an intentional reviewed evidence update; it refuses mismatched review/source hashes.

The build has no framework or runtime package dependencies. Genetic-file parsing runs in a local Web Worker with cancellation. Marker evidence replay and exported-findings replay are documented in docs/GENETIC_READER.md. `dist/` is tracked and published through Sites. `research/` contains the canonical research code and captures. Licensed fonts and notices are tracked in `dist/`. No sibling project folders are needed.

## Architecture

- Five original source captures and the complete derived comparison travel together in an immutable evidence bundle.
- Browser verifies the exact bundle hash and each source's hash/byte count before displaying records.
- The separate correspondence review must match the displayed API source hashes. Its failure removes the correspondence claim while retaining valid source evidence.
- All 24 selections use original API records. Context and phenotype are explicit URL state. FDA subgroup membership is literal; likely categories are not inferred.
- Export uses the verified original bundle bytes. Full Python replay independently reconstructs the saved comparison.
- Optional WebMCP `read_evidence_selection` reads the same visible state and rejects arguments. It makes no clinical agreement claim.
- Native select, buttons and details work without custom interaction libraries. Rendering uses textContent for source text.

## Design

A document workspace: dark green selection rail, generous light evidence surface, Newsreader and IBM Plex Sans, fine rules, one restrained accent. Mobile stacks controls and documents. No stock imagery, gradients, animated decoration or fabricated metrics. Font licenses are included in dist.

## Verification checkpoint

- Research suite: 30 passing tests.
- Browser: all 24 context/phenotype selections matched source record IDs and classifications.
- 1440/390 layouts visually inspected; 320-width overflow check passed.
- Missing evidence and altered evidence hide the result with an explicit error.
- Missing review retains the source evidence and removes the correspondence claim.
- Unknown URL categories fail explicitly. A valid selection survives reload; anchor navigation preserves the current selection.
- WebMCP read-back matched visible state; invalid arguments were rejected.
- Published evidence file passed Python offline replay (24 comparisons).
- Browser download was clicked, but the embedded browser did not expose a download event; completed file-save verification remains open. No browser errors were reported.

Full accessibility audit, physical-device testing, independent user feedback, final Jordan design acceptance and browser snapshot-change review remain open. Technical content is real; the workflow is not clinically validated.

## Keyboard and navigation follow-up

Source and skip links now move keyboard focus to their named destination without replacing the evidence-selection URL. A selected neurovascular/Poor Metabolizer record survived source navigation and reload in the browser. Enter activation worked for context controls, cross-context comparison rows and the source-details disclosure; rebuilding comparison rows retained keyboard focus.

The original focus outline had 2.21:1 contrast against the green panel. Panel controls now use a light outline; the original outline remains on light surfaces (4.61:1). This is a targeted keyboard/focus review, not a full accessibility or screen-reader conformance claim.

## Source history

The source-history view compares the active bundle with one explicitly pinned later capture. Both are replay-validated during packaging; the browser verifies the packaged report hash and its binding to the displayed source files. It does not fetch live guidance or activate another snapshot. The current real pair contains five identical source files and different retrieval metadata.

Changed CPIC rows retain complete before/after records, including changes that do not alter classification. Missing or altered comparison reports hide that comparison while retaining the active evidence. Three new research tests cover timestamp-only changes, text changes with unchanged classification, and corrupt derived comparisons (33 total passing).

Browser checks: five unchanged source rows, zero changed CPIC records, keyboard disclosure, phone-width overflow, and unavailable comparison isolation. Synthetic changed-record fixtures are tested in the pipeline; this release does not present them as real guideline changes.

## Independent loading and bounded requests

The core evidence becomes usable immediately after verification. Correspondence review and source history load independently. Each fetch is bounded to ten seconds and two million bytes, including bodies without a Content-Length header. Supplemental failure removes only the relevant claim/view. Seven Node tests cover exact bytes, tampering, HTTP failure, declared and streamed size limits, stalled connection and stalled body; browser tests with delayed supplemental responses confirm the main comparison remains interactive before and after timeout. Run `node --test tests/resource.test.mjs`.

The technical case study and two-minute walkthrough are in `research/research/CASE_STUDY.md`. They are drafts for review, not approved public portfolio copy.

## Repository map and limits

- `dist/`: static interface, licensed fonts and verified public-source artifacts.
- `research/scripts/`: acquisition, adapters, comparison, replay and snapshot lifecycle.
- `research/data/`: original captures, manifests, immutable snapshots and review evidence.
- `research/tests/`: research regressions. `tests/`: browser fault fixtures and loading tests.
- `research/research/CASE_STUDY.md`: technical story and demonstration walkthrough.

The old sibling `pharmacogenomics-workbench` is a historical copy. Make future research changes here. Original captures have their own source terms and attribution; see `research/data/CPIC_TERMS.md` and each manifest. Font license files accompany the font binaries. Public repository publication and an original-code license decision remain pending; no open-source license is implied for original code.

The Site's `.openai/hosting.json` identifies its existing public deployment. Do not create a replacement Site or include that identity in an unrelated deployment. Local reproduction does not need Sites credentials.
