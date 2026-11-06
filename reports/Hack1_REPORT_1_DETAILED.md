# Detailed Repository Assessment Report
**Run ID:** `run_20261024_102233_cbb754`  
**Generated:** 2026-10-24T10:22:38.119360+00:00  
**Target Repository:** `Hack1` (`C:\Users\visha\Downloads\Hack1`)  
**Commit Revision:** `46e9a049ac42a89325e4e735920e3f73096acf22` (Working Tree Clean: False)  
**Active Branch:** `main` | **Comparison Base:** `main`  
**Operating System / Platform:** `Windows-11-10.0.26200-SP0` | **Python:** `3.12.10`  
**Network Isolation:** `Python-level egress guard (Defense in Depth); Kernel Isolation: Not Present (Bare Metal)` | **Script Execution Approved:** `False`  

---

## 1. Executive Summary
> [!NOTE]
> **Assessment Status: REVIEW RECOMMENDED**
> No Critical or High issues identified. 15 minor or informational observations recorded.

### Key Observations & Operational Risk
- **Total Discovered Files:** 202 (65 analyzed, 13 excluded, 0 generated, 102 binary)
- **Identified Ecosystem:** Languages: `Python, YAML, Dockerfile, Markdown, Requirements, Batch, Shell, JSON` | Frameworks: `None`
- **Offline SBOM Dependencies:** 12 components across `pypi`
- **Test Execution Security:** Project-supplied test scripts were BLOCKED from automated execution per safety policy.

---

## 2. Repository Inventory
### File Classification Breakdown
| Classification | Count | Description |
| :--- | :---: | :--- |
| **Analyzed** | 65 | Source code and configuration files processed offline |
| **Excluded** | 13 | Files matching default exclusion patterns (.git, caches, build dirs) |
| **Generated** | 0 | Bundles, minified files, lockfiles, or code generation output |
| **Binary** | 102 | Non-text assets (images, binaries, fonts, archives) |
| **Unsupported** | 22 | Formats not mapped to an active offline language parser |
| **Failed to Inspect** | 0 | Files unreadable due to I/O or permissions |
| **Total Discovered** | **202** | **100% cataloged** |

### Excluded Files by Reason
| Excluded File Path | Reason / Matched Pattern |
| :--- | :--- |
| `.pytest_cache/.gitignore` | Matched default exclusion pattern '^\.pytest_cache([\\/].*)?$' |
| `.pytest_cache/CACHEDIR.TAG` | Matched default exclusion pattern '^\.pytest_cache([\\/].*)?$' |
| `.pytest_cache/README.md` | Matched default exclusion pattern '^\.pytest_cache([\\/].*)?$' |
| `.pytest_cache/v/cache/lastfailed` | Matched default exclusion pattern '^\.pytest_cache([\\/].*)?$' |
| `.pytest_cache/v/cache/nodeids` | Matched default exclusion pattern '^\.pytest_cache([\\/].*)?$' |
| `__pycache__/app.cpython-312.pyc` | Matched default exclusion pattern '^__pycache__([\\/].*)?$' |
| `__pycache__/test_alert_dispatcher.cpython-312-pytest-9.1.1.pyc` | Matched default exclusion pattern '^__pycache__([\\/].*)?$' |
| `__pycache__/test_event_aggregation.cpython-312-pytest-9.1.1.pyc` | Matched default exclusion pattern '^__pycache__([\\/].*)?$' |
| `__pycache__/test_incident_pipeline.cpython-312-pytest-9.1.1.pyc` | Matched default exclusion pattern '^__pycache__([\\/].*)?$' |
| `__pycache__/test_interaction_analysis.cpython-312-pytest-9.1.1.pyc` | Matched default exclusion pattern '^__pycache__([\\/].*)?$' |
| `__pycache__/test_reporting.cpython-312-pytest-9.1.1.pyc` | Matched default exclusion pattern '^__pycache__([\\/].*)?$' |
| `__pycache__/test_risk.cpython-312-pytest-9.1.1.pyc` | Matched default exclusion pattern '^__pycache__([\\/].*)?$' |
| `__pycache__/test_trajectory_analysis.cpython-312-pytest-9.1.1.pyc` | Matched default exclusion pattern '^__pycache__([\\/].*)?$' |

### Inspected Source Files & Assigned Analyzers
| File Path | Language | Category | Assigned Offline Analyzer | Lines |
| :--- | :--- | :--- | :--- | :---: |
| `app.py` | Python | entry_point | Python AST Validator & Security AST Visitor | 3069 |
| `config.yaml` | YAML | config | Offline SBOM & Dependency Configuration Inspector | 47 |
| `Dockerfile` | Dockerfile | source | Offline Dockerfile Inspector | 31 |
| `download_weights.py` | Python | source | Python AST Validator & Security AST Visitor | 26 |
| `requirements.txt` | Requirements | config | Offline SBOM & Dependency Configuration Inspector | 30 |
| `run_dashboard.sh` | Shell | source | Offline Shell Inspector | 26 |
| `run_tests.sh` | Shell | source | Offline Shell Inspector | 17 |
| `.github/workflows/ci.yml` | YAML | config | Offline SBOM & Dependency Configuration Inspector | 41 |
| `.vscode/settings.json` | JSON | config | Offline SBOM & Dependency Configuration Inspector | 3 |
| `data/benchmarks/ground_truth.json` | JSON | config | Offline SBOM & Dependency Configuration Inspector | 35 |
| `scripts/check_duplicate_tracks.py` | Python | source | Python AST Validator & Security AST Visitor | 22 |
| `scripts/check_event_evidence_counts.py` | Python | source | Python AST Validator & Security AST Visitor | 22 |
| `scripts/clean_stale_evidence.py` | Python | source | Python AST Validator & Security AST Visitor | 32 |
| `scripts/demo_event_risk.py` | Python | source | Python AST Validator & Security AST Visitor | 78 |
| `scripts/detect_test.py` | Python | test | Python AST Validator & Security AST Visitor | 44 |
| `scripts/detect_video.py` | Python | source | Python AST Validator & Security AST Visitor | 84 |
| `scripts/inspect_duplicate_overlap.py` | Python | source | Python AST Validator & Security AST Visitor | 33 |
| `scripts/list_stale_evidence.py` | Python | source | Python AST Validator & Security AST Visitor | 22 |
| `scripts/track_video.py` | Python | source | Python AST Validator & Security AST Visitor | 81 |
| `scripts/verify_prune.py` | Python | source | Python AST Validator & Security AST Visitor | 91 |
| `src/alert_dispatcher.py` | Python | source | Python AST Validator & Security AST Visitor | 427 |
| `src/benchmark.py` | Python | source | Python AST Validator & Security AST Visitor | 445 |
| `src/config.py` | Python | source | Python AST Validator & Security AST Visitor | 125 |
| `src/db.py` | Python | source | Python AST Validator & Security AST Visitor | 215 |
| `src/event_aggregation.py` | Python | source | Python AST Validator & Security AST Visitor | 123 |
| `src/gemini_service.py` | Python | source | Python AST Validator & Security AST Visitor | 298 |
| `src/incident_pipeline.py` | Python | source | Python AST Validator & Security AST Visitor | 287 |
| `src/interaction_analysis.py` | Python | source | Python AST Validator & Security AST Visitor | 489 |
| `src/overview_page.py` | Python | source | Python AST Validator & Security AST Visitor | 643 |
| `src/pdf_report.py` | Python | source | Python AST Validator & Security AST Visitor | 292 |
| `src/prune_gateway.py` | Python | source | Python AST Validator & Security AST Visitor | 212 |
| `src/reporting.py` | Python | source | Python AST Validator & Security AST Visitor | 156 |
| `src/risk_engine.py` | Python | source | Python AST Validator & Security AST Visitor | 730 |
| `src/trajectory_analysis.py` | Python | source | Python AST Validator & Security AST Visitor | 164 |
| `src/video_processor.py` | Python | source | Python AST Validator & Security AST Visitor | 669 |
| `src/welcome_page.py` | Python | source | Python AST Validator & Security AST Visitor | 182 |
| `src/worker.py` | Python | source | Python AST Validator & Security AST Visitor | 89 |
| `src/zones.py` | Python | source | Python AST Validator & Security AST Visitor | 150 |
| `src/__init__.py` | Python | source | Python AST Validator & Security AST Visitor | 0 |
| `tests/test_aggregate_video_findings.py` | Python | test | Python AST Validator & Security AST Visitor | 64 |
| `tests/test_alert_dispatcher.py` | Python | test | Python AST Validator & Security AST Visitor | 217 |
| `tests/test_benchmark.py` | Python | test | Python AST Validator & Security AST Visitor | 88 |
| `tests/test_candidate_event_risk.py` | Python | test | Python AST Validator & Security AST Visitor | 291 |
| `tests/test_config.py` | Python | test | Python AST Validator & Security AST Visitor | 22 |
| `tests/test_confusion_matrix.py` | Python | test | Python AST Validator & Security AST Visitor | 81 |
| `tests/test_db.py` | Python | test | Python AST Validator & Security AST Visitor | 56 |
| `tests/test_event_aggregation.py` | Python | test | Python AST Validator & Security AST Visitor | 71 |
| `tests/test_event_clip.py` | Python | test | Python AST Validator & Security AST Visitor | 40 |
| `tests/test_event_evidence.py` | Python | test | Python AST Validator & Security AST Visitor | 207 |
| `tests/test_gemini_service.py` | Python | test | Python AST Validator & Security AST Visitor | 77 |
| `tests/test_incident_pipeline.py` | Python | test | Python AST Validator & Security AST Visitor | 123 |
| `tests/test_interaction_analysis.py` | Python | test | Python AST Validator & Security AST Visitor | 347 |
| `tests/test_interaction_from_video.py` | Python | test | Python AST Validator & Security AST Visitor | 71 |
| `tests/test_new_videos.py` | Python | test | Python AST Validator & Security AST Visitor | 50 |
| `tests/test_pair_422_429.py` | Python | test | Python AST Validator & Security AST Visitor | 31 |
| `tests/test_prune_gateway.py` | Python | test | Python AST Validator & Security AST Visitor | 84 |
| `tests/test_reporting.py` | Python | test | Python AST Validator & Security AST Visitor | 60 |
| `tests/test_risk.py` | Python | test | Python AST Validator & Security AST Visitor | 77 |
| `tests/test_severity_classification.py` | Python | test | Python AST Validator & Security AST Visitor | 84 |
| `tests/test_tracking.py` | Python | test | Python AST Validator & Security AST Visitor | 59 |
| `tests/test_tracking_trails.py` | Python | test | Python AST Validator & Security AST Visitor | 59 |
| `tests/test_trajectory_analysis.py` | Python | test | Python AST Validator & Security AST Visitor | 47 |
| `tests/test_worker.py` | Python | test | Python AST Validator & Security AST Visitor | 21 |
| `tests/test_zones.py` | Python | test | Python AST Validator & Security AST Visitor | 101 |
| `tests/__init__.py` | Python | test | Python AST Validator & Security AST Visitor | 1 |

- **Total Inspected Source Lines:** 11959 lines (Reconciliation: 42 lines across all project branches — 36 lines on main branch plus 6 lines on feature/checkout branch; previously misreported as 52 lines due to counting unpruned cache or test run artifacts).

### Offline Software Bill of Materials (SBOM) Summary
- **Total Tracked Dependencies:** 12
- **Direct Dependencies:** 12
- **Ecosystems:** pypi

| Package | Version | Ecosystem | Direct | Source File |
| :--- | :--- | :---: | :---: | :--- |
| **`streamlit`** | `1.35.0` | pypi | Yes | `requirements.txt` |
| **`ultralytics`** | `8.2.0` | pypi | Yes | `requirements.txt` |
| **`opencv-python`** | `4.8.0` | pypi | Yes | `requirements.txt` |
| **`pillow`** | `10.0.0` | pypi | Yes | `requirements.txt` |
| **`numpy`** | `1.24.0` | pypi | Yes | `requirements.txt` |
| **`torch`** | `2.1.0` | pypi | Yes | `requirements.txt` |
| **`torchvision`** | `0.16.0` | pypi | Yes | `requirements.txt` |
| **`pandas`** | `2.0.0` | pypi | Yes | `requirements.txt` |
| **`pyyaml`** | `6.0` | pypi | Yes | `requirements.txt` |
| **`reportlab`** | `4.0.0` | pypi | Yes | `requirements.txt` |
| **`requests`** | `2.28.0` | pypi | Yes | `requirements.txt` |
| **`pytest`** | `7.4.0` | pypi | Yes | `requirements.txt` |

> [!NOTE]
> **Transitive Dependency Resolution Boundary:** The offline SBOM catalogs direct manifest dependencies declared in repository configuration (e.g. `requirements.txt`). In an offline, isolated environment without package index access (PyPI) or pre-resolved lockfiles (e.g., `poetry.lock`), indirect/transitive dependencies cannot be expanded.

---

## 3. Application Map & Structure
Discovered endpoints, feature flags, integrations, and application workflows:

### Web & API Routes
_No explicit HTTP routes or API endpoints discovered in source files._

### Role-Based Access Control (RBAC) Matrix
- **Identified Roles:** _None explicitly identified_
- **Endpoints Covered in RBAC Map:** 0

### Inferred OpenAPI 3.1 Spec
- **OpenAPI Version:** `3.1.0` | **Endpoints Synthesized:** 0

### Application Workflows & Features
#### Discovered Application Workflows
| Workflow Name | Type / Status | Description | Steps Count | Flow Sequence | Linked Test Suites |
| :--- | :---: | :--- | :---: | :--- | :--- |
| **`CI/CD Pipeline: ci.yml`** | Inferred | Automated continuous integration workflow | 1 | `Build / Lint / Test pipeline defined in CI configuration` | _None detected_ |

---

## 4. Branch and Change Analysis
- **Working Tree Status:** `Dirty (Uncommitted modifications present)`

| Branch | Status | HEAD Commit | Message |
| :--- | :---: | :--- | :--- |
| **`main`** (active) (base) | assessed | `46e9a04` | refactor: remove references to judges and judging rounds |

---

## 5. Checks & Test Execution Results
| Check Name | Tool (Version) | Type | Execution | Gate Policy | Duration | Output / Diagnostics |
| :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| **Static AST, Security & Secret Analysis** | offtest-static-scanner (`0.1.0`) | security | Completed | **PASS** | 0.15s | Exit code 0 |
| **Python Pytest Suite** | pytest (`9.1.1`) | unit_test | Blocked | **BLOCKED** | 0.0s | Untrusted repository script execution blocked by default. Pass '--allow-scripts' to approve running project test suite. |

### Synthesized Branch Tests (Constrained Generation)
- **Total Generated Tests:** 10
- **Syntax Verified:** 10 | **Repaired:** 0
- **Test Suite Output File:** `Hack1_reports\run_20261024_102233_cbb754\generated_tests\test_offline_generated_suite.py`

| Test ID | Target File:Line | Predicate Type | Validation Status | Description |
| :--- | :--- | :---: | :---: | :--- |
| `test_gen_1_read_sms_log` | `app.py:62` | function_call | `synthesized, unverified` | Branch reachability test for 'SMS_LOG.exists()' in read_sms_log |
| `test_gen_2_read_reports` | `app.py:80` | function_call | `synthesized, unverified` | Branch reachability test for 'INCIDENT_LOG.exists()' in read_reports |
| `test_gen_3_read_notification_log` | `app.py:95` | function_call | `synthesized, unverified` | Branch reachability test for 'NOTIFICATION_LOG.exists()' in read_notification_log |
| `test_gen_4_read_review_log` | `app.py:112` | function_call | `synthesized, unverified` | Branch reachability test for 'REVIEW_LOG.exists()' in read_review_log |
| `test_gen_5_record_review` | `app.py:138` | function_call | `synthesized, unverified` | Branch reachability test for 'hasattr(st, 'cache_data')' in record_review |
| `test_gen_6_record_notification` | `app.py:173` | function_call | `synthesized, unverified` | Branch reachability test for 'hasattr(st, 'cache_data')' in record_notification |
| `test_gen_7_get_event_evidence_image` | `app.py:194` | null_check | `synthesized, unverified` | Branch reachability test for 'not event' in get_event_evidence_image |
| `test_gen_8_get_event_evidence_image` | `app.py:198` | comparison | `synthesized, unverified` | Branch reachability test for 'ts Is None' in get_event_evidence_image |

---

## 6. Discovered Findings & Vulnerabilities

### [FIND-0001] Minimum Version Constraint (Unpinned Python Dependency)
- **Severity:** **Low** | **Confidence:** **Confirmed** | **Status:** **Observed** | Branch: `main`
- **Taxonomy:** `CWE-1357` (Reliance on Insufficiently Trustworthy Component)
- **Estimated CVSS Base:** `3.7` (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:L/A:N) _[Heuristic Estimate]_
- **Location:** `requirements.txt:5`
- **Source Anchor Content Hash:** `7baa727e2a306906...` (verified)
- **Oracle Origin:** `static_rule`
- **Tool:** `dependency-pin-checker`
- **User / System Impact:** Dependency specifies a minimum or range constraint ('streamlit>=1.35.0') rather than an exact pinned version ('=='). While standard during local development, unpinned builds can pull unexpected upstream changes and cause non-deterministic offline environments.
- **Evidence / Reproduction:**
```
Line 5: streamlit>=1.35.0
```
- **Recommended Next Action:** Pin exact version in requirements.txt (e.g. streamlit==x.y.z) for deterministic offline builds.

### [FIND-0002] Minimum Version Constraint (Unpinned Python Dependency)
- **Severity:** **Low** | **Confidence:** **Confirmed** | **Status:** **Observed** | Branch: `main`
- **Taxonomy:** `CWE-1357` (Reliance on Insufficiently Trustworthy Component)
- **Estimated CVSS Base:** `3.7` (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:L/A:N) _[Heuristic Estimate]_
- **Location:** `requirements.txt:8`
- **Source Anchor Content Hash:** `7baa727e2a306906...` (verified)
- **Oracle Origin:** `static_rule`
- **Tool:** `dependency-pin-checker`
- **User / System Impact:** Dependency specifies a minimum or range constraint ('ultralytics>=8.2.0') rather than an exact pinned version ('=='). While standard during local development, unpinned builds can pull unexpected upstream changes and cause non-deterministic offline environments.
- **Evidence / Reproduction:**
```
Line 8: ultralytics>=8.2.0
```
- **Recommended Next Action:** Pin exact version in requirements.txt (e.g. ultralytics==x.y.z) for deterministic offline builds.

### [FIND-0003] Minimum Version Constraint (Unpinned Python Dependency)
- **Severity:** **Low** | **Confidence:** **Confirmed** | **Status:** **Observed** | Branch: `main`
- **Taxonomy:** `CWE-1357` (Reliance on Insufficiently Trustworthy Component)
- **Estimated CVSS Base:** `3.7` (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:L/A:N) _[Heuristic Estimate]_
- **Location:** `requirements.txt:9`
- **Source Anchor Content Hash:** `7baa727e2a306906...` (verified)
- **Oracle Origin:** `static_rule`
- **Tool:** `dependency-pin-checker`
- **User / System Impact:** Dependency specifies a minimum or range constraint ('opencv-python>=4.8.0') rather than an exact pinned version ('=='). While standard during local development, unpinned builds can pull unexpected upstream changes and cause non-deterministic offline environments.
- **Evidence / Reproduction:**
```
Line 9: opencv-python>=4.8.0
```
- **Recommended Next Action:** Pin exact version in requirements.txt (e.g. opencv-python==x.y.z) for deterministic offline builds.

### [FIND-0004] Minimum Version Constraint (Unpinned Python Dependency)
- **Severity:** **Low** | **Confidence:** **Confirmed** | **Status:** **Observed** | Branch: `main`
- **Taxonomy:** `CWE-1357` (Reliance on Insufficiently Trustworthy Component)
- **Estimated CVSS Base:** `3.7` (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:L/A:N) _[Heuristic Estimate]_
- **Location:** `requirements.txt:10`
- **Source Anchor Content Hash:** `7baa727e2a306906...` (verified)
- **Oracle Origin:** `static_rule`
- **Tool:** `dependency-pin-checker`
- **User / System Impact:** Dependency specifies a minimum or range constraint ('pillow>=10.0.0') rather than an exact pinned version ('=='). While standard during local development, unpinned builds can pull unexpected upstream changes and cause non-deterministic offline environments.
- **Evidence / Reproduction:**
```
Line 10: pillow>=10.0.0
```
- **Recommended Next Action:** Pin exact version in requirements.txt (e.g. pillow==x.y.z) for deterministic offline builds.

### [FIND-0005] Minimum Version Constraint (Unpinned Python Dependency)
- **Severity:** **Low** | **Confidence:** **Confirmed** | **Status:** **Observed** | Branch: `main`
- **Taxonomy:** `CWE-1357` (Reliance on Insufficiently Trustworthy Component)
- **Estimated CVSS Base:** `3.7` (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:L/A:N) _[Heuristic Estimate]_
- **Location:** `requirements.txt:11`
- **Source Anchor Content Hash:** `7baa727e2a306906...` (verified)
- **Oracle Origin:** `static_rule`
- **Tool:** `dependency-pin-checker`
- **User / System Impact:** Dependency specifies a minimum or range constraint ('numpy>=1.24.0') rather than an exact pinned version ('=='). While standard during local development, unpinned builds can pull unexpected upstream changes and cause non-deterministic offline environments.
- **Evidence / Reproduction:**
```
Line 11: numpy>=1.24.0
```
- **Recommended Next Action:** Pin exact version in requirements.txt (e.g. numpy==x.y.z) for deterministic offline builds.

### [FIND-0006] Minimum Version Constraint (Unpinned Python Dependency)
- **Severity:** **Low** | **Confidence:** **Confirmed** | **Status:** **Observed** | Branch: `main`
- **Taxonomy:** `CWE-1357` (Reliance on Insufficiently Trustworthy Component)
- **Estimated CVSS Base:** `3.7` (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:L/A:N) _[Heuristic Estimate]_
- **Location:** `requirements.txt:14`
- **Source Anchor Content Hash:** `7baa727e2a306906...` (verified)
- **Oracle Origin:** `static_rule`
- **Tool:** `dependency-pin-checker`
- **User / System Impact:** Dependency specifies a minimum or range constraint ('torch>=2.1.0') rather than an exact pinned version ('=='). While standard during local development, unpinned builds can pull unexpected upstream changes and cause non-deterministic offline environments.
- **Evidence / Reproduction:**
```
Line 14: torch>=2.1.0
```
- **Recommended Next Action:** Pin exact version in requirements.txt (e.g. torch==x.y.z) for deterministic offline builds.

### [FIND-0007] Minimum Version Constraint (Unpinned Python Dependency)
- **Severity:** **Low** | **Confidence:** **Confirmed** | **Status:** **Observed** | Branch: `main`
- **Taxonomy:** `CWE-1357` (Reliance on Insufficiently Trustworthy Component)
- **Estimated CVSS Base:** `3.7` (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:L/A:N) _[Heuristic Estimate]_
- **Location:** `requirements.txt:15`
- **Source Anchor Content Hash:** `7baa727e2a306906...` (verified)
- **Oracle Origin:** `static_rule`
- **Tool:** `dependency-pin-checker`
- **User / System Impact:** Dependency specifies a minimum or range constraint ('torchvision>=0.16.0') rather than an exact pinned version ('=='). While standard during local development, unpinned builds can pull unexpected upstream changes and cause non-deterministic offline environments.
- **Evidence / Reproduction:**
```
Line 15: torchvision>=0.16.0
```
- **Recommended Next Action:** Pin exact version in requirements.txt (e.g. torchvision==x.y.z) for deterministic offline builds.

### [FIND-0008] Minimum Version Constraint (Unpinned Python Dependency)
- **Severity:** **Low** | **Confidence:** **Confirmed** | **Status:** **Observed** | Branch: `main`
- **Taxonomy:** `CWE-1357` (Reliance on Insufficiently Trustworthy Component)
- **Estimated CVSS Base:** `3.7` (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:L/A:N) _[Heuristic Estimate]_
- **Location:** `requirements.txt:18`
- **Source Anchor Content Hash:** `7baa727e2a306906...` (verified)
- **Oracle Origin:** `static_rule`
- **Tool:** `dependency-pin-checker`
- **User / System Impact:** Dependency specifies a minimum or range constraint ('pandas>=2.0.0') rather than an exact pinned version ('=='). While standard during local development, unpinned builds can pull unexpected upstream changes and cause non-deterministic offline environments.
- **Evidence / Reproduction:**
```
Line 18: pandas>=2.0.0
```
- **Recommended Next Action:** Pin exact version in requirements.txt (e.g. pandas==x.y.z) for deterministic offline builds.

### [FIND-0009] Minimum Version Constraint (Unpinned Python Dependency)
- **Severity:** **Low** | **Confidence:** **Confirmed** | **Status:** **Observed** | Branch: `main`
- **Taxonomy:** `CWE-1357` (Reliance on Insufficiently Trustworthy Component)
- **Estimated CVSS Base:** `3.7` (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:L/A:N) _[Heuristic Estimate]_
- **Location:** `requirements.txt:21`
- **Source Anchor Content Hash:** `7baa727e2a306906...` (verified)
- **Oracle Origin:** `static_rule`
- **Tool:** `dependency-pin-checker`
- **User / System Impact:** Dependency specifies a minimum or range constraint ('pyyaml>=6.0') rather than an exact pinned version ('=='). While standard during local development, unpinned builds can pull unexpected upstream changes and cause non-deterministic offline environments.
- **Evidence / Reproduction:**
```
Line 21: pyyaml>=6.0
```
- **Recommended Next Action:** Pin exact version in requirements.txt (e.g. pyyaml==x.y.z) for deterministic offline builds.

### [FIND-0010] Minimum Version Constraint (Unpinned Python Dependency)
- **Severity:** **Low** | **Confidence:** **Confirmed** | **Status:** **Observed** | Branch: `main`
- **Taxonomy:** `CWE-1357` (Reliance on Insufficiently Trustworthy Component)
- **Estimated CVSS Base:** `3.7` (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:L/A:N) _[Heuristic Estimate]_
- **Location:** `requirements.txt:24`
- **Source Anchor Content Hash:** `7baa727e2a306906...` (verified)
- **Oracle Origin:** `static_rule`
- **Tool:** `dependency-pin-checker`
- **User / System Impact:** Dependency specifies a minimum or range constraint ('reportlab>=4.0.0') rather than an exact pinned version ('=='). While standard during local development, unpinned builds can pull unexpected upstream changes and cause non-deterministic offline environments.
- **Evidence / Reproduction:**
```
Line 24: reportlab>=4.0.0
```
- **Recommended Next Action:** Pin exact version in requirements.txt (e.g. reportlab==x.y.z) for deterministic offline builds.

### [FIND-0011] Minimum Version Constraint (Unpinned Python Dependency)
- **Severity:** **Low** | **Confidence:** **Confirmed** | **Status:** **Observed** | Branch: `main`
- **Taxonomy:** `CWE-1357` (Reliance on Insufficiently Trustworthy Component)
- **Estimated CVSS Base:** `3.7` (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:L/A:N) _[Heuristic Estimate]_
- **Location:** `requirements.txt:27`
- **Source Anchor Content Hash:** `7baa727e2a306906...` (verified)
- **Oracle Origin:** `static_rule`
- **Tool:** `dependency-pin-checker`
- **User / System Impact:** Dependency specifies a minimum or range constraint ('requests>=2.28.0') rather than an exact pinned version ('=='). While standard during local development, unpinned builds can pull unexpected upstream changes and cause non-deterministic offline environments.
- **Evidence / Reproduction:**
```
Line 27: requests>=2.28.0
```
- **Recommended Next Action:** Pin exact version in requirements.txt (e.g. requests==x.y.z) for deterministic offline builds.

### [FIND-0012] Minimum Version Constraint (Unpinned Python Dependency)
- **Severity:** **Low** | **Confidence:** **Confirmed** | **Status:** **Observed** | Branch: `main`
- **Taxonomy:** `CWE-1357` (Reliance on Insufficiently Trustworthy Component)
- **Estimated CVSS Base:** `3.7` (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:L/A:N) _[Heuristic Estimate]_
- **Location:** `requirements.txt:30`
- **Source Anchor Content Hash:** `7baa727e2a306906...` (verified)
- **Oracle Origin:** `static_rule`
- **Tool:** `dependency-pin-checker`
- **User / System Impact:** Dependency specifies a minimum or range constraint ('pytest>=7.4.0') rather than an exact pinned version ('=='). While standard during local development, unpinned builds can pull unexpected upstream changes and cause non-deterministic offline environments.
- **Evidence / Reproduction:**
```
Line 30: pytest>=7.4.0
```
- **Recommended Next Action:** Pin exact version in requirements.txt (e.g. pytest==x.y.z) for deterministic offline builds.

### [FIND-0013] Non-Standard UTF-8 BOM (Byte Order Mark) Detected
- **Severity:** **Low** | **Confidence:** **Confirmed** | **Status:** **Observed** | Branch: `main`
- **Location:** `scripts/clean_stale_evidence.py:1`
- **Source Anchor Content Hash:** `6f36fa869436dd29...` (verified)
- **Oracle Origin:** `static_rule`
- **Tool:** `file-encoding-checker`
- **User / System Impact:** File begins with a UTF-8 Byte Order Mark (0xEF 0xBB 0xBF / U+FEFF). While standard Python runtimes strip the BOM automatically when running files from disk, strict CI linters, non-Windows compilers, or string-based AST parsers may flag or mishandle BOM characters.
- **Evidence / Reproduction:**
```
Line 1: File starts with 3-byte UTF-8 BOM sequence (0xEF 0xBB 0xBF)
```
- **Recommended Next Action:** Re-save file as standard UTF-8 without BOM to ensure universal cross-platform and linter compatibility.

### [FIND-0014] Non-Standard UTF-8 BOM (Byte Order Mark) Detected
- **Severity:** **Low** | **Confidence:** **Confirmed** | **Status:** **Observed** | Branch: `main`
- **Location:** `src/trajectory_analysis.py:1`
- **Source Anchor Content Hash:** `0d3bd949e789d339...` (verified)
- **Oracle Origin:** `static_rule`
- **Tool:** `file-encoding-checker`
- **User / System Impact:** File begins with a UTF-8 Byte Order Mark (0xEF 0xBB 0xBF / U+FEFF). While standard Python runtimes strip the BOM automatically when running files from disk, strict CI linters, non-Windows compilers, or string-based AST parsers may flag or mishandle BOM characters.
- **Evidence / Reproduction:**
```
Line 1: File starts with 3-byte UTF-8 BOM sequence (0xEF 0xBB 0xBF)
```
- **Recommended Next Action:** Re-save file as standard UTF-8 without BOM to ensure universal cross-platform and linter compatibility.

### [FIND-0015] Non-Standard UTF-8 BOM (Byte Order Mark) Detected
- **Severity:** **Low** | **Confidence:** **Confirmed** | **Status:** **Observed** | Branch: `main`
- **Location:** `tests/test_event_evidence.py:1`
- **Source Anchor Content Hash:** `c7e32b334a599562...` (verified)
- **Oracle Origin:** `static_rule`
- **Tool:** `file-encoding-checker`
- **User / System Impact:** File begins with a UTF-8 Byte Order Mark (0xEF 0xBB 0xBF / U+FEFF). While standard Python runtimes strip the BOM automatically when running files from disk, strict CI linters, non-Windows compilers, or string-based AST parsers may flag or mishandle BOM characters.
- **Evidence / Reproduction:**
```
Line 1: File starts with 3-byte UTF-8 BOM sequence (0xEF 0xBB 0xBF)
```
- **Recommended Next Action:** Re-save file as standard UTF-8 without BOM to ensure universal cross-platform and linter compatibility.

---

## 7. Coverage Assessment & Gaps
| Dimension | Value | Formula / Denominator | Status | Details |
| :--- | :---: | :---: | :---: | :--- |
| **Repository Inventory Disposition** | _N/A (Breakdown)_ | 65/202 total cataloged files | Available | Cataloged 202 total repository files: 65 analyzed, 13 excluded, 0 generated, 102 binary, 22 unsupported, 0 unreadable. (Percentages reserved for actionable test dimensions). |
| **Static Analysis Coverage** | **100.0%** | 65/65 eligible source files | Available | 65 of 65 eligible source files inspected across offline analyzers: 57 Python (AST security & syntax parsing), 5 Manifest/Config (SBOM & pin inspector). 0 parse failures. |
| **Test Suite Execution Coverage** | **0.0%** | 0/1 test suites | Available | 0 of 1 discovered test suites executed in isolated offline runner. |
| **Code Coverage (Statement/Branch)** | _Unavailable_ | N/A | **UNAVAILABLE** | Unavailable: No offline coverage instrumentation report (e.g., coverage.xml or lcov.info) was supplied or generated. |
| **Workflow Coverage** | **0.0%** | 0/1 workflows | Available | 0 of 1 application workflows confirmed covered (test suite execution was blocked or not run; synthesized tests are excluded from confirmed coverage). |
| **Feature Coverage** | _Unavailable_ | N/A | **UNAVAILABLE** | Unavailable: No distinct feature toggles or named features were identified in source code. |
| **Git Branch Assessment** | **100.0%** | 1/1 git branches | Available | 1 of 1 requested local branches assessed (main scanned as active branch). |

> [!IMPORTANT]
> **Coverage Principles:** Missing metrics are labeled `Unavailable`, not zero or 100%. A passing test suite does not guarantee that every code path or workflow is defect-free.

---

## 8. Reproducibility Details & Tool Manifest
| Tool Name | Version | Path | Category | Available Offline |
| :--- | :--- | :--- | :--- | :---: |
| **Python Runtime** | `3.12.10` | `C:\Program Files\Python312\python.exe` | runtime | Yes |
| **Git CLI** | `git version 2.55.0.windows.5` | `C:\Program Files\Git\cmd\git.EXE` | vcs | Yes |
| **Node.js Runtime** | `v24.20.0` | `C:\Program Files\nodejs\node.EXE` | runtime | Yes |
| **Pytest Test Runner** | `9.1.1` | `C:\Program Files\Python312\python.exe` | test_runner | Yes |
| **offtest AST & Security Scanner** | `0.1.0` | `built-in` | static_analysis | Yes |

### Execution Assumptions
- Execution running on platform 'Windows-11-10.0.26200-SP0' with Python '3.12.10'.
- IsolatedRunner enforced environment scrubbing (host secrets stripped) and proxy nullification.
- No remote network calls or remote git fetches performed during assessment.

---

## 9. Explicit Limitations & Boundaries
- Assessment runs in an offline isolated environment without external dependency retrieval.
- Static analysis provides full AST depth for Python; regex heuristics apply for other languages.
- Undocumented APIs and implicit workflows without local guards are explicitly tagged as Unverified.
- On Windows 11 / bare-metal host platforms, process isolation enforces environment scrubbing and proxy sinkholing; physical/kernel air-gap requires containerization (Docker --network none) or OS-level packet filtering.
- Repository-provided test suites and build scripts were blocked from execution per the script safety approval policy.