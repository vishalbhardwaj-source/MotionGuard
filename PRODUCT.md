# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

1. **Traffic Management Center (TMC) Operators & Dispatchers**: Monitor real-time CCTV feeds, verify anomalous vehicle kinematics, and triage potential traffic collisions without drowning in false alarms.
2. **First Responder Coordinators (Police / EMS / Fire)**: Receive instant emergency alerts with timestamped photographic proof and kinematic severity metrics to prioritize dispatches.
3. **Forensic Crash Reconstruction Investigators & DOT Analysts**: Review temporal collision episodes, examine optical Time-to-Collision ($\tau$), track separation distances, and generate court-ready PDF dossiers.

## Product Purpose

MotionGuard is an AI-powered road-safety risk assessment and real-time emergency incident response workstation. It transforms raw traffic surveillance CCTV footage into structured, explainable safety intelligence, automated emergency dispatches with photographic snapshot proof, and exportable forensic investigation dossiers.

## Positioning

Unlike black-box AI collision alarms that flood operators with false warnings on normal traffic, MotionGuard provides physics-grounded, explainable decision-support. Every flagged event is linked to multi-object track IDs, monocular scale-expansion Time-to-Collision ($\tau$), scale-normalized distance, closest approach keyframes, and an operator verification loop achieving 0.0 false emergency responder alerts per hour on normal highway traffic.

## Operating Context

- High-stress 24/7 Command & Control / SOC environments with ambient low lighting.
- Multi-screen operations with simultaneous live video streams, kinematic telemetry plots, and real-time dispatch logs.
- Need for immediate visual hierarchy: green for nominal traffic, amber for near-miss/stationary hazards, and vivid pulsing red for confirmed physical collisions requiring emergency escalation.
- Zero-tolerance for UI latency, illegible metrics, or ambiguous alerts.

## Capabilities and Constraints

- **Web Stack**: Streamlit (Python 3.10-3.12), HTML5, CSS3, SVG, ReportLab, OpenCV, Ultralytics YOLO11n + ByteTrack.
- **Three Primary Views**:
  1. *Welcome Landing*: High-impact cybernetic launch portal and system status hub.
  2. *Architecture Overview*: Interactive pipeline walkthrough, benchmark results, and technical specifications.
  3. *Operations Workstation*: 6 dedicated investigation tabs (Video Analysis, Incident Investigation, Scenario Stress Testing, Incident Records & Emergency Broadcasts, Investigation Dossier, Sensitivity Calibration).
- **Hard Constraints**: Streamlit DOM constraints require clean inline `<style>` injection, robust scoping, accessible contrast ratios (WCAG AAA for critical telemetry, AAA/AA 7:1+ for text), and responsive fluid layout for desktop and tablet screens.

## Brand Commitments

- **Name**: MotionGuard (v2.5 Autonomous Edge AI).
- **Voice**: Authoritative, mission-critical, scientifically honest, and precise.
- **Visual Aesthetic**: Tactical Mission Control / Cybernetic SOC. Obsidian canvas (`#070a13` / `#0b0f19`), cybernetic glass borders (`rgba(56, 189, 248, 0.25)`), telemetry cyan accents (`#06b6d4`, `#38bdf8`), emergency alert red (`#ef4444`), warning amber (`#f59e0b`), operational green (`#10b981`), and high-legibility monospace numerals (`JetBrains Mono` / `Fira Code`).

## Evidence on Hand

- Real-world highway traffic video (`data/videos/normal.mp4`) and collision benchmark clip (`data/videos/crash_demo.mp4`).
- Ground truth collision annotations (`data/benchmarks/ground_truth.json`).
- Automated incident pipeline logs and dispatch records in `outputs/`.
- Pre-trained neural weights (`yolo11n.pt`).

## Product Principles

1. **Clarity Over Clutter**: Mission-critical metrics must be instantly scannable within 200ms of visual fixation.
2. **Actionable Telemetry**: Pair every number with its physical unit ($px/s$, $\tau$, $m$, $s$) and qualitative status indicator.
3. **Fail-Safe Integrity**: Distinguish automated heuristic detection from human operator review decisions and verified dispatches.
4. **Cinematic Precision**: Deliver an engaging, military/aerospace-grade aesthetic without compromising performance or readability.

## Accessibility & Inclusion

- Dark theme optimized for prolonged monitoring in low-light control rooms with reduced glare.
- Contrast ratio exceeding 7:1 for all primary data readouts against dark cards.
- Multi-modal status indication: color is never used alone; always accompanied by explicit text badges and iconography.
- Reduced motion support: critical telemetry updates without disorienting layout shifts or rapid flickering.
