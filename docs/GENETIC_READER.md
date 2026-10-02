# Genetic-file reader — first functional slice

This supersedes the document-only product scope. Home is now a browser-local reader; the earlier evidence library remains at `evidence.html` with all captured sources and verification.

## Supported scope

23andMe tab-separated text exports declaring GRCh37 and positive strand, maximum 25 MiB / 1.2 million records. Only three CYP2C19 marker substitutions are interpreted: rs4244285 G>A (selected *2 marker), rs4986893 G>A (selected *3 marker), rs12248560 C>T (selected *17 marker). Build 37 chromosome 10 positions are 96541616, 96540410, 96521657 respectively. These are 1-based coordinates.

Identifiers, positions and chromosome must agree. Other alleles at these multiallelic loci are not silently converted or interpreted. Calls may be detected, not-detected, missing, no-call or unsupported. Identical target duplicates collapse; conflicting target calls fail the import. Other loci are discarded. No phasing, complete star alleles, diplotype, phenotype, dosage or treatment selection is inferred. This is selected-marker education, not a comprehensive pharmacogenomic test.

## Evidence

Checked 2026-09-30:
- NCBI RefSNP API `https://api.ncbi.nlm.nih.gov/variation/v0/refsnp/4244285` (and /4986893, /12248560), `NC_000010.10` placements. API SPDI positions are zero-based, so add one. Multiple alternative bases exist; our rule supports only the stated substitution. Raw RefSNP responses and the CPIC PDF are now captured in research/marker-evidence/raw, with retrieval timestamps, lengths and SHA-256 hashes in manifest.json. Offline replay checks the captured bytes, identities and GRCh37 substitutions and regenerates dist/marker-rules.mjs. Functional/star-allele associations remain an explicit source-based mapping, not an independent clinical review.
- NCBI Medical Genetics Summaries, selected CYP2C19 allele nomenclature: https://www.ncbi.nlm.nih.gov/books/NBK379740/table/diazepam.Te/
- CPIC 2022 clopidogrel update, DOI 10.1002/cpt.2526: https://files.cpicpgx.org/data/guideline/publication/clopidogrel/2022/35034351.pdf . Page 1 defines allele functional groups; page 3 describes activation and metabolizer associations. No medication recommendation is derived from the imported markers.
- 23andMe raw-data boundaries: https://customercare.23andme.com/hc/en-us/articles/212196868-Accessing-Your-Raw-Genetic-Data

## Data handling

No ingestion endpoint, remote interpreter, logging, storage API or analytics in the reader. A restrictive meta CSP disallows connections (`connect-src 'none'`) and permits same-origin worker code (`worker-src 'self'`). Bundled JS and fonts load normally; evidence-library navigation is a separate page. Filenames are not displayed or exported. File reading and parsing happen in a module Web Worker, terminated after completion, error, cancellation or page exit; results retain only the selected calls and counts. Clear and pagehide remove rendered results. Save findings is an explicit sensitive local JSON download. Browser/OS memory erasure is not claimed. Third-party extensions and the hosting platform are outside the parser's controls.

The bundled sample is invented. No personal genomic file was used during development.

## Verification and remaining work

`node --test tests/genetics.test.mjs` covers malformed formats/builds/strand, no calls, conflicts, alternate allele handling, missing coverage, coordinate mismatches and no unwarranted phenotype. `python3 verify.py` includes these tests and the prior source-replay suite. Browser verification should exercise synthetic input through the actual file chooser, export, reset, invalid replacement, mobile layout and absence of data-dependent network/storage writes.

Next: independent interpretation review, more supported gene/drug pairs and file formats only with their own validation. This first slice does not complete the broader personal pharmacogenomics product.


## Evidence and report replay

`python3 scripts/replay-marker-evidence.py --check` verifies the source capture and generated browser rules. Omit --check only when intentionally regenerating after a reviewed source/rule update. Five Python tests cover byte tampering, mismatched coordinates, wrong source identity and path escape. `verify.py` includes them.

`node scripts/replay-findings.mjs REPORT.json` recomputes the selected-marker findings from the calls retained in an exported report and requires matching evidence/rule versions. Five tests cover valid replay, altered findings, mismatched evidence, fabricated phenotype and absent calls. It cannot authenticate the original assay, total source-row count, duplicates or synthetic flag. A matching checksum establishes consistency with the captured copy, not publisher authenticity or clinical truth.

## Large-file browser verification

Synthetic 700,003-row / 16,689,169-byte disk fixture, Chrome headless with a 390px viewport and 4× CPU throttling: 841 ms from file selection to results in one local run, with maximum 39 ms gap in a 25 ms UI heartbeat. These are local engineering measurements, not physical-phone or production performance claims. An initial buffer-injection harness included a 3,256 ms browser automation transfer gap; the disk-file selection run avoids that transfer method. Cancellation was tested deterministically by delaying worker module loading, then confirming that a new sample could succeed without stale results.

Browser module loads are ordinary static GET requests with no genetic data. The raw file is never sent to a server. Updated browser checks permit these fixed worker-module requests and reject other activity during import. No raw-data network/storage behavior was added.

Evidence: portfolio-program/qa/context-large-file-checks.json and context-reader-checks.json. Harnesses use external local Playwright and are not represented as portable package tests.

## Medication-context expansion

The findings page now includes an educational selector for clopidogrel and six PPIs: omeprazole, lansoprazole, pantoprazole, dexlansoprazole, esomeprazole and rabeprazole. Genetic coverage is still the same three CYP2C19 markers. Selecting a medication never changes the marker result, assigns a phenotype or records a medication history. No dose or treatment recommendation is produced.

The captured 2020 CPIC PPI guideline (DOI 10.1002/cpt.2015) supports distinct summaries: first-generation PPI clearance context; limited-data optional recommendations for dexlansoprazole; and no recommendation in that guideline for esomeprazole/rabeprazole. See page 3, Table 2 and page 5. Clopidogrel activation context remains tied to its 2022 guideline. These are dated captured publications, not a claim of comprehensive current guidance. The CPIC guideline landing page redirects to a JavaScript-rendered ClinPGx page; latest revision state was not established from that landing page.

Raw PDFs and curated summaries are in research/medication-evidence. `python3 scripts/replay-medication-evidence.py --check` verifies captured bytes, valid source references and the generated catalog. It does not mechanically prove the scientific correctness of authored summaries. Source hashes are consistency checks, not independent clinical validation. `verify.py` includes three catalog-source tests and five medication-context tests.

Exports include the selected medication, source, dated locator and catalog fingerprint. `replay-findings.mjs` validates this section when present; prior reports without a medication section remain supported if their marker evidence/rule version matches. A change to a summary, selected drug or source invalidates replay unless it matches the catalog exactly.

Browser QA exercised every selection, unchanged marker findings, report replay, no selection-triggered network/URL writes, clear/reset and 390/320 layouts. Phone screenshot inspected. Evidence: portfolio-program/qa/context-medication-checks.json. No physical-device or independent clinician evaluation claimed.

## Personalized report priority — October 1 UTC / September 30 local

Jordan clarified again that genetic file → personalized pharmacogenomic outputs is the product; medication browsing alone is insufficient. The main report now automatically derives a bounded set of marker-level medication implications. The reference explorer and raw-call detail are secondary disclosures.

`dist/insights.mjs` rule set cyp2c19-marker-implications-1 branches on confirmed-as-reported calls, not a user-selected medication: selected *2/*3-associated variants produce conditional reduced clopidogrel activation and increased first-generation PPI exposure implications; *17-only produces conditional PPI clearance context and explicitly no standalone clopidogrel response prediction; co-detected markers do not cancel; reference-only and unresolved-only patterns do not generate directional medication cards. Every output carries the reported rsID/call basis, missing-marker context, rule version and marker/medication evidence fingerprints.

These are hypotheses conditional on clinical confirmation, not lab-confirmed phenotypes. No complete diplotype, phase, dose, individual risk probability or drug suitability is inferred. CPIC clopidogrel 2022 page 3 and Tables 2–3 and PPI 2020 page 3/Table 2 support the directional links; the reports do not apply their prescribing recommendations to incomplete consumer data. Interpretation engine is source-backed and tested but not independently clinically validated. A full consumer pharmacogenomics product remains unfinished.

The report export includes these derived implications. Offline replay recomputes them from retained calls and rejects altered output text. Eight added tests cover loss/gain/mixed/reference/unresolved/second loss marker/version mismatch and report tampering. Browser synthetic scenarios check automatic outputs, input basis, exports and 320/390 layout. A full-page phone screenshot repeated viewport regions; the replacement viewport capture of the implication cards was inspected. This is not physical-device validation.

Next priority: broaden the actual file-to-insight pipeline with another well-characterized gene/drug relationship and a defined interpretation acceptance matrix. Do not add generic catalog entries as a substitute for personalized outputs.


## Current scope — two-gene report

This section supersedes historical three-marker counts above. Four selected markers are assessed: three CYP2C19 markers and SLCO1B1 rs4149056 (GRCh37 chromosome 12, position 21331549, positive-strand T>C). The NCBI RefSNP capture supplies the coordinate/substitution check. The captured CPIC 2022 statin guideline (DOI 10.1002/cpt.2557, background and Table 2) supports the bounded simvastatin implication. Both captures are hashed and replayed offline.

A detected C call produces a conditional explanation of reduced hepatic uptake, greater simvastatin-acid exposure and muscle toxicity risk. No SLCO1B1 star allele, full phenotype, dose or individual risk probability is assigned. One locus cannot exclude other relevant variants. Other statins are not extrapolated from this rule. Missing or reference calls never establish drug safety.

### Interpretation acceptance matrix

| Input | Expected report |
| --- | --- |
| SLCO1B1 TC or CC | Simvastatin implication, exact reported call and source; no phenotype |
| SLCO1B1 TT | No directional simvastatin card; incomplete coverage remains explicit |
| Missing, no-call or unsupported SLCO1B1 call | No directional card; unresolved coverage shown |
| SLCO1B1 detected, CYP2C19 missing | Simvastatin only; separate gene coverage |
| Detected CYP2C19 loss marker and SLCO1B1 C | Existing clopidogrel/PPI cards plus simvastatin, with separate call bases |
| Wrong chromosome/position, conflicting duplicate or locus alias collision | Import rejected; stale report cleared |
| Altered exported implication or incompatible rule version | Offline replay rejected |

Current marker rules: pgx-selected-markers-3; implications: pgx-marker-implications-2; medication catalog: pgx-medication-context-2. Exports from older rule/evidence versions are intentionally rejected by the current replay engine; the corresponding historical source commit is required to reproduce them. The new example contains synthetic findings in both genes. It is not personal data.

Verification: 88 tests (33 research, 8 Python source replay, 47 Node) passed with byte-identical prior research artifacts. Existing personalized CYP2C19 browser scenarios and new two-gene import, export/replay, missing-marker and wrong-chromosome scenarios passed. Desktop and phone captures inspected; 390/320 widths checked. Evidence: portfolio-program/qa/context-two-gene-checks.json and context-personalized-checks.json. External local Playwright is used by these browser harnesses; no physical-phone or independent clinical validation is claimed.

Next: reassess report usefulness and visual hierarchy, refresh the now-outdated case study and release artifacts, and identify the next justified interpretation/format extension. Do not present four markers as complete pharmacogenomics.


## Import recovery

Failed imports now show a focused recovery panel with a reason, next step, direct file-picker retry and synthetic-example fallback. Known ZIP/PDF/VCF signatures are rejected explicitly; these formats have not been added as supported inputs. Empty files, file-size limits, original-header requirements, genome build, strand, coordinate mismatches and conflicting records have distinct recovery guidance. The reader never repairs calls or relabels builds. No input lines, file names or genotypes are inserted into recovery copy.

Starting a replacement removes prior results; successful retry clears the error and input-invalid state. Worker cancellation/generation guards remain in place. No upload or persistent storage introduced. Existing genetic rules and report versions remain unchanged.

97 tests pass (33 research, 8 source Python, 56 Node) including nine recovery cases, with byte-identical research artifact replay. Browser synthetic checks cover ZIP/PDF/VCF/build rejection, error focus, cleared stale findings, sample fallback, actual chooser retry and 320/390 overflow. Phone/desktop captures inspected. Evidence: portfolio-program/qa/context-import-checks.json and context-import-recovery.mjs. External browser harness; no physical-device, clinical or user validation claimed.

## Card-specific evidence paths

Each implication now retains its own triggering calls, gene, deterministic condition, other assessed calls in that gene, source locator/hash and stable rule identifier. The UI exposes reported call → interpretation condition → evidence under “Why this appears”; reproduction metadata is a separate disclosure. A statin card cannot attribute itself to CYP2C19 simply because both genes appear in the report. Missing/uncalled data remain explicit context, never trigger evidence. Existing medication conclusions and selected genetic coverage are unchanged.

Insight version is pgx-marker-implications-3. Downloads include the complete evidence path and replay rejects altered calls, swapped marker attribution, changed source hashes or missing traces. Older implication-version exports require their historical engine; marker version alone is insufficient to replay old insights.

101 tests pass (33 research, 8 source Python, 60 Node). One matrix test exercises 625 combinations across reference, heterozygous, homozygous, no-call and unsupported calls at four loci. It checks gene isolation, detected-only bases, complete accounting of selected calls, reduced-function precedence and matching source hashes. These are software invariants, not 625 clinically validated patient results. Browser checks exercise all three sample cards, disclosure contents, download/replay and 320/390 layout; desktop and phone inspected. QA evidence: portfolio-program/qa/context-trace-checks.json and context-evidence-path.mjs.

Portfolio value: this feature makes deterministic reasoning inspectable and falsifiable through exported evidence, while using progressive disclosure to keep ordinary reading manageable. Independent clinical review and real-user usability remain open.

## DPYD direct-marker expansion

Current scope supersedes earlier counts: eight markers across CYP2C19, SLCO1B1 and DPYD. Four direct DPYD sites are checked in GRCh37 positive-strand data: rs3918290 chr1:97915614 C>T, rs55886062 chr1:97981343 A>C, rs67376798 chr1:97547947 T>A, rs75017182 chr1:98045449 G>C. Coding-DNA labels use the opposite strand and are displayed separately from reported calls. RefSNP captures and explicit complementary mappings are replay-checked. The rs56038477 proxy is not used, and presence on any consumer-array version is not presumed.

A detected selected DPYD variant produces conditional fluorouracil/capecitabine metabolism/toxicity context tied to the captured 2017 guideline. No activity score, phenotype, dose or personal risk probability is produced. Missing, no-call and reference-only DPYD states do not establish normal DPD function or safety. The dedicated synthetic example contains one detected site and one no-call. The primary example continues to demonstrate CYP2C19/SLCO1B1.

Evidence status is explicit: CPIC's July 9, 2026 notice announces an rs75017182-specific update while older database values remain visible until publication. Searches did not verify publication of a full replacement guideline. The notice is a manually curated linked summary, read online; direct archival retrieval failed with HTTP 403. Its summary and URL are bound to the medication manifest and exported trace; no raw notice capture is claimed. This product uses neither old nor announced activity values/dosing rules. It makes a dated directional association, not a current prescribing-guideline implementation.

Source module/rule versions advanced. Old reports require their historical source engine. The report stores a detached copy of update metadata so editing a report cannot mutate the catalog used to recompute it.

Verification: 109 tests (33 research, 10 source Python, 66 Node), original research artifacts byte-identical. New cases cover all four direct variants, heterozygous/homozygous calls, missing/reference/no-call behavior, coding/genomic confusion, proxy exclusion, conflicting records, off-by-one location and altered update metadata. Previous 625-combination matrix remains scoped to the original four loci with DPYD reference calls; it is not an eight-locus exhaustive matrix. Browser tests cover synthetic DPYD sample and file input, three-gene coverage, exact CT versus coding G>A presentation, update notice, export replay and 320/390 widths. Desktop/phone captures inspected. No physical-device or independent clinical/user validation claimed.

QA: portfolio-program/qa/context-dpyd-checks.json and context-dpyd.mjs. Historical browser harnesses with hard-coded marker counts must be updated before rerun. This remains a selected-marker educational prototype, not a comprehensive chemotherapy risk screen.
