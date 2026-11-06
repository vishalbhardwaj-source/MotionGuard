# Actionable Issue-Focused Assessment Report
**Target:** `Hack1` | **Run ID:** `run_20261024_102233_cbb754` | **Commit:** `46e9a049ac42a89325e4e735920e3f73096acf22` | **Working Tree Clean:** `False`

**Isolation Mode:** `Python-level egress guard (Defense in Depth); Kernel Isolation: Not Present (Bare Metal)`

## Issue Summary by Severity
| Severity | Count | Immediate Priority |
| :--- | :---: | :--- |
| **CRITICAL** | **0** | Must resolve before any release or distribution |
| **HIGH** | **0** | Fix required prior to staging deployment |
| **MEDIUM** | 0 | Address in upcoming iteration |
| **LOW** | 15 | Clean up during regular maintenance |
| **INFORMATIONAL** | 0 | Best-practice observations |
| **TOTAL FINDINGS** | **15** | |

> [!CAUTION]
> **NO CLEAN BILL OF HEALTH**: 0 high-severity defects identified and 1 checks were blocked. Comprehensive security and stability are NOT guaranteed.

## Low Severity Issues (15)

### [FIND-0001] Minimum Version Constraint (Unpinned Python Dependency)
- **Severity:** `Low` | **Confidence:** `Confirmed` | **Status:** `Observed` | Branch: `main`
- **Taxonomy:** `CWE-1357` (Reliance on Insufficiently Trustworthy Component)
- **Estimated CVSS Base:** `3.7` _[Heuristic Estimate]_
- **Location:** `requirements.txt:5`
- **Impact:** Dependency specifies a minimum or range constraint ('streamlit>=1.35.0') rather than an exact pinned version ('=='). While standard during local development, unpinned builds can pull unexpected upstream changes and cause non-deterministic offline environments.
- **Evidence / Reproduction:**
```
Line 5: streamlit>=1.35.0
```
- **Suggested Action:** Pin exact version in requirements.txt (e.g. streamlit==x.y.z) for deterministic offline builds.

### [FIND-0002] Minimum Version Constraint (Unpinned Python Dependency)
- **Severity:** `Low` | **Confidence:** `Confirmed` | **Status:** `Observed` | Branch: `main`
- **Taxonomy:** `CWE-1357` (Reliance on Insufficiently Trustworthy Component)
- **Estimated CVSS Base:** `3.7` _[Heuristic Estimate]_
- **Location:** `requirements.txt:8`
- **Impact:** Dependency specifies a minimum or range constraint ('ultralytics>=8.2.0') rather than an exact pinned version ('=='). While standard during local development, unpinned builds can pull unexpected upstream changes and cause non-deterministic offline environments.
- **Evidence / Reproduction:**
```
Line 8: ultralytics>=8.2.0
```
- **Suggested Action:** Pin exact version in requirements.txt (e.g. ultralytics==x.y.z) for deterministic offline builds.

### [FIND-0003] Minimum Version Constraint (Unpinned Python Dependency)
- **Severity:** `Low` | **Confidence:** `Confirmed` | **Status:** `Observed` | Branch: `main`
- **Taxonomy:** `CWE-1357` (Reliance on Insufficiently Trustworthy Component)
- **Estimated CVSS Base:** `3.7` _[Heuristic Estimate]_
- **Location:** `requirements.txt:9`
- **Impact:** Dependency specifies a minimum or range constraint ('opencv-python>=4.8.0') rather than an exact pinned version ('=='). While standard during local development, unpinned builds can pull unexpected upstream changes and cause non-deterministic offline environments.
- **Evidence / Reproduction:**
```
Line 9: opencv-python>=4.8.0
```
- **Suggested Action:** Pin exact version in requirements.txt (e.g. opencv-python==x.y.z) for deterministic offline builds.

### [FIND-0004] Minimum Version Constraint (Unpinned Python Dependency)
- **Severity:** `Low` | **Confidence:** `Confirmed` | **Status:** `Observed` | Branch: `main`
- **Taxonomy:** `CWE-1357` (Reliance on Insufficiently Trustworthy Component)
- **Estimated CVSS Base:** `3.7` _[Heuristic Estimate]_
- **Location:** `requirements.txt:10`
- **Impact:** Dependency specifies a minimum or range constraint ('pillow>=10.0.0') rather than an exact pinned version ('=='). While standard during local development, unpinned builds can pull unexpected upstream changes and cause non-deterministic offline environments.
- **Evidence / Reproduction:**
```
Line 10: pillow>=10.0.0
```
- **Suggested Action:** Pin exact version in requirements.txt (e.g. pillow==x.y.z) for deterministic offline builds.

### [FIND-0005] Minimum Version Constraint (Unpinned Python Dependency)
- **Severity:** `Low` | **Confidence:** `Confirmed` | **Status:** `Observed` | Branch: `main`
- **Taxonomy:** `CWE-1357` (Reliance on Insufficiently Trustworthy Component)
- **Estimated CVSS Base:** `3.7` _[Heuristic Estimate]_
- **Location:** `requirements.txt:11`
- **Impact:** Dependency specifies a minimum or range constraint ('numpy>=1.24.0') rather than an exact pinned version ('=='). While standard during local development, unpinned builds can pull unexpected upstream changes and cause non-deterministic offline environments.
- **Evidence / Reproduction:**
```
Line 11: numpy>=1.24.0
```
- **Suggested Action:** Pin exact version in requirements.txt (e.g. numpy==x.y.z) for deterministic offline builds.

### [FIND-0006] Minimum Version Constraint (Unpinned Python Dependency)
- **Severity:** `Low` | **Confidence:** `Confirmed` | **Status:** `Observed` | Branch: `main`
- **Taxonomy:** `CWE-1357` (Reliance on Insufficiently Trustworthy Component)
- **Estimated CVSS Base:** `3.7` _[Heuristic Estimate]_
- **Location:** `requirements.txt:14`
- **Impact:** Dependency specifies a minimum or range constraint ('torch>=2.1.0') rather than an exact pinned version ('=='). While standard during local development, unpinned builds can pull unexpected upstream changes and cause non-deterministic offline environments.
- **Evidence / Reproduction:**
```
Line 14: torch>=2.1.0
```
- **Suggested Action:** Pin exact version in requirements.txt (e.g. torch==x.y.z) for deterministic offline builds.

### [FIND-0007] Minimum Version Constraint (Unpinned Python Dependency)
- **Severity:** `Low` | **Confidence:** `Confirmed` | **Status:** `Observed` | Branch: `main`
- **Taxonomy:** `CWE-1357` (Reliance on Insufficiently Trustworthy Component)
- **Estimated CVSS Base:** `3.7` _[Heuristic Estimate]_
- **Location:** `requirements.txt:15`
- **Impact:** Dependency specifies a minimum or range constraint ('torchvision>=0.16.0') rather than an exact pinned version ('=='). While standard during local development, unpinned builds can pull unexpected upstream changes and cause non-deterministic offline environments.
- **Evidence / Reproduction:**
```
Line 15: torchvision>=0.16.0
```
- **Suggested Action:** Pin exact version in requirements.txt (e.g. torchvision==x.y.z) for deterministic offline builds.

### [FIND-0008] Minimum Version Constraint (Unpinned Python Dependency)
- **Severity:** `Low` | **Confidence:** `Confirmed` | **Status:** `Observed` | Branch: `main`
- **Taxonomy:** `CWE-1357` (Reliance on Insufficiently Trustworthy Component)
- **Estimated CVSS Base:** `3.7` _[Heuristic Estimate]_
- **Location:** `requirements.txt:18`
- **Impact:** Dependency specifies a minimum or range constraint ('pandas>=2.0.0') rather than an exact pinned version ('=='). While standard during local development, unpinned builds can pull unexpected upstream changes and cause non-deterministic offline environments.
- **Evidence / Reproduction:**
```
Line 18: pandas>=2.0.0
```
- **Suggested Action:** Pin exact version in requirements.txt (e.g. pandas==x.y.z) for deterministic offline builds.

### [FIND-0009] Minimum Version Constraint (Unpinned Python Dependency)
- **Severity:** `Low` | **Confidence:** `Confirmed` | **Status:** `Observed` | Branch: `main`
- **Taxonomy:** `CWE-1357` (Reliance on Insufficiently Trustworthy Component)
- **Estimated CVSS Base:** `3.7` _[Heuristic Estimate]_
- **Location:** `requirements.txt:21`
- **Impact:** Dependency specifies a minimum or range constraint ('pyyaml>=6.0') rather than an exact pinned version ('=='). While standard during local development, unpinned builds can pull unexpected upstream changes and cause non-deterministic offline environments.
- **Evidence / Reproduction:**
```
Line 21: pyyaml>=6.0
```
- **Suggested Action:** Pin exact version in requirements.txt (e.g. pyyaml==x.y.z) for deterministic offline builds.

### [FIND-0010] Minimum Version Constraint (Unpinned Python Dependency)
- **Severity:** `Low` | **Confidence:** `Confirmed` | **Status:** `Observed` | Branch: `main`
- **Taxonomy:** `CWE-1357` (Reliance on Insufficiently Trustworthy Component)
- **Estimated CVSS Base:** `3.7` _[Heuristic Estimate]_
- **Location:** `requirements.txt:24`
- **Impact:** Dependency specifies a minimum or range constraint ('reportlab>=4.0.0') rather than an exact pinned version ('=='). While standard during local development, unpinned builds can pull unexpected upstream changes and cause non-deterministic offline environments.
- **Evidence / Reproduction:**
```
Line 24: reportlab>=4.0.0
```
- **Suggested Action:** Pin exact version in requirements.txt (e.g. reportlab==x.y.z) for deterministic offline builds.

### [FIND-0011] Minimum Version Constraint (Unpinned Python Dependency)
- **Severity:** `Low` | **Confidence:** `Confirmed` | **Status:** `Observed` | Branch: `main`
- **Taxonomy:** `CWE-1357` (Reliance on Insufficiently Trustworthy Component)
- **Estimated CVSS Base:** `3.7` _[Heuristic Estimate]_
- **Location:** `requirements.txt:27`
- **Impact:** Dependency specifies a minimum or range constraint ('requests>=2.28.0') rather than an exact pinned version ('=='). While standard during local development, unpinned builds can pull unexpected upstream changes and cause non-deterministic offline environments.
- **Evidence / Reproduction:**
```
Line 27: requests>=2.28.0
```
- **Suggested Action:** Pin exact version in requirements.txt (e.g. requests==x.y.z) for deterministic offline builds.

### [FIND-0012] Minimum Version Constraint (Unpinned Python Dependency)
- **Severity:** `Low` | **Confidence:** `Confirmed` | **Status:** `Observed` | Branch: `main`
- **Taxonomy:** `CWE-1357` (Reliance on Insufficiently Trustworthy Component)
- **Estimated CVSS Base:** `3.7` _[Heuristic Estimate]_
- **Location:** `requirements.txt:30`
- **Impact:** Dependency specifies a minimum or range constraint ('pytest>=7.4.0') rather than an exact pinned version ('=='). While standard during local development, unpinned builds can pull unexpected upstream changes and cause non-deterministic offline environments.
- **Evidence / Reproduction:**
```
Line 30: pytest>=7.4.0
```
- **Suggested Action:** Pin exact version in requirements.txt (e.g. pytest==x.y.z) for deterministic offline builds.

### [FIND-0013] Non-Standard UTF-8 BOM (Byte Order Mark) Detected
- **Severity:** `Low` | **Confidence:** `Confirmed` | **Status:** `Observed` | Branch: `main`
- **Location:** `scripts/clean_stale_evidence.py:1`
- **Impact:** File begins with a UTF-8 Byte Order Mark (0xEF 0xBB 0xBF / U+FEFF). While standard Python runtimes strip the BOM automatically when running files from disk, strict CI linters, non-Windows compilers, or string-based AST parsers may flag or mishandle BOM characters.
- **Evidence / Reproduction:**
```
Line 1: File starts with 3-byte UTF-8 BOM sequence (0xEF 0xBB 0xBF)
```
- **Suggested Action:** Re-save file as standard UTF-8 without BOM to ensure universal cross-platform and linter compatibility.

### [FIND-0014] Non-Standard UTF-8 BOM (Byte Order Mark) Detected
- **Severity:** `Low` | **Confidence:** `Confirmed` | **Status:** `Observed` | Branch: `main`
- **Location:** `src/trajectory_analysis.py:1`
- **Impact:** File begins with a UTF-8 Byte Order Mark (0xEF 0xBB 0xBF / U+FEFF). While standard Python runtimes strip the BOM automatically when running files from disk, strict CI linters, non-Windows compilers, or string-based AST parsers may flag or mishandle BOM characters.
- **Evidence / Reproduction:**
```
Line 1: File starts with 3-byte UTF-8 BOM sequence (0xEF 0xBB 0xBF)
```
- **Suggested Action:** Re-save file as standard UTF-8 without BOM to ensure universal cross-platform and linter compatibility.

### [FIND-0015] Non-Standard UTF-8 BOM (Byte Order Mark) Detected
- **Severity:** `Low` | **Confidence:** `Confirmed` | **Status:** `Observed` | Branch: `main`
- **Location:** `tests/test_event_evidence.py:1`
- **Impact:** File begins with a UTF-8 Byte Order Mark (0xEF 0xBB 0xBF / U+FEFF). While standard Python runtimes strip the BOM automatically when running files from disk, strict CI linters, non-Windows compilers, or string-based AST parsers may flag or mishandle BOM characters.
- **Evidence / Reproduction:**
```
Line 1: File starts with 3-byte UTF-8 BOM sequence (0xEF 0xBB 0xBF)
```
- **Suggested Action:** Re-save file as standard UTF-8 without BOM to ensure universal cross-platform and linter compatibility.

## Blocked & Unverified Checks
| Check Name | Status | Tool | Reason / Blocker |
| :--- | :---: | :--- | :--- |
| **Python Pytest Suite** | **BLOCKED** | `pytest` | Untrusted repository script execution blocked by default. Pass '--allow-scripts' to approve running project test suite. |

## Key Coverage Gaps
- **Test Suite Execution Coverage (0.0%):** 0 of 1 discovered test suites executed in isolated offline runner.
- **Code Coverage (Statement/Branch) (UNAVAILABLE):** Unavailable: No offline coverage instrumentation report (e.g., coverage.xml or lcov.info) was supplied or generated.
- **Workflow Coverage (0.0%):** 0 of 1 application workflows confirmed covered (test suite execution was blocked or not run; synthesized tests are excluded from confirmed coverage).
- **Feature Coverage (UNAVAILABLE):** Unavailable: No distinct feature toggles or named features were identified in source code.