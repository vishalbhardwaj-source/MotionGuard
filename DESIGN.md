# MotionGuard Design System & Visual Authority

<!-- impeccable:design-schema 1 -->

## Direction Contract

- **Thesis**: An authentic Tactical Mission Control & Incident Investigation Workstation (Cybernetic SOC). Deep obsidian ground (`#080c16`), crisp 1px borders with subtle cyan/slate rim light, and high-contrast telemetry indicators. Color communicates state: emergency red (`#ef4444`) only for confirmed collisions/dispatches, amber (`#f59e0b`) for proximity warnings, emerald (`#10b981`) for nominal tracking, and cyan (`#06b6d4` / `#38bdf8`) for spatial geometry and optical kinematics.
- **Own-World**: Low-ambient lighting SOC terminal. Micro-beveled telemetry tiles, precision tabular layout, inline SVG iconography with 1.75px uniform strokes, high-legibility monospace numbers (`Fira Code` / `JetBrains Mono`) strictly for measurements and codes, paired with clean technical grotesk typography (`Plus Jakarta Sans` / `Inter`) for copy.
- **Story**: An operator sits in a 24/7 Command Center. Within seconds of an incident, the screen pinpoints the exact collision onset, displays the optical TTC $\tau$, calculates closing speed, verifies keyframe evidence, and enables single-click Telegram/SMS dispatch and court-ready PDF dossier generation with zero nuisance alarms.
- **First Viewport**: Clean header bar with operational health pulse, active video feed status, and seamless view routing (Welcome, Architecture, Operations Workstation). Below: tactical KPI ribbon with physical units and status pips, followed by the video feed + live kinematic telemetry HUD.
- **Signature Interactions**:
  1. Interactive video scrubber with synchronized kinematic metrics and closest approach timestamps.
  2. One-click instant emergency dispatch trigger with visual confirmation pill and photographic preview.
  3. Interactive confusion matrix sliders dynamically recalibrating precision, recall, and false alarm rate.
- **Finish**: Unreviewed and undocumented is unfinished; this build ends with the finish review, the verdict, DESIGN.md, and every shipping raster carrying its provenance.

---

## Design Tokens

### Color Palette

| Token | Hex / Value | Purpose |
|---|---|---|
| `--mg-canvas` | `#080c16` | Deep obsidian application background |
| `--mg-surface-1` | `#0d1322` | Primary panel and tab background |
| `--mg-surface-2` | `#131b2e` | Elevated cards, metric tiles, table headers |
| `--mg-surface-3` | `#1a243d` | Hover states, active selections |
| `--mg-border-subtle` | `rgba(255, 255, 255, 0.08)` | Standard container border |
| `--mg-border-focus` | `rgba(56, 189, 248, 0.45)` | Active/focused element border |
| `--mg-text-primary` | `#f8fafc` | Primary headlines, metric values, high contrast |
| `--mg-text-secondary`| `#94a3b8` | Supporting descriptions, metadata |
| `--mg-text-muted` | `#64748b` | Timestamps, inactive labels |
| `--mg-accent-cyan` | `#38bdf8` | Primary telemetry accent, tracking trails |
| `--mg-status-nominal`| `#10b981` | Safe highway baseline, active radar health |
| `--mg-status-warning`| `#f59e0b` | Near-miss, close passing, elevated caution |
| `--mg-status-alert` | `#ef4444` | Confirmed physical collision, urgent 911 dispatch |
| `--mg-status-info` | `#818cf8` | Pipeline stages, architectural specs |

### Typography

- **UI & Headings**: `'Fira Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif`
  - Weight scale: `400` (regular), `500` (medium), `600` (semibold), `700` (bold), `800` (extrabold)
  - Letter spacing: `-0.02em` on titles, `0` on body, `+0.05em` on uppercase badges
- **Telemetry & Numerals**: `'Fira Code', 'JetBrains Mono', monospace`
  - Used strictly for timestamps (`05.20s`), speed (`px/s`), distance (`px`), optical TTC ($\tau$), vehicle track IDs (`#422`), coordinates, and confusion matrix rates.

### Spatial Spacing & Radius Scale

- **Radius**: `6px` (badges), `10px` (buttons, inputs), `14px` (cards, video wrapper, hero banner)
- **Shadows**:
  - `sm`: `0 2px 8px rgba(0, 0, 0, 0.3)`
  - `md`: `0 8px 24px rgba(0, 0, 0, 0.45)`
  - `glow-cyan`: `0 0 16px rgba(56, 189, 248, 0.2)`
  - `glow-red`: `0 0 20px rgba(239, 68, 68, 0.35)`

---

## Craft Floor Adherence

1. **No unicode emoji as UI icons**: Clean vector SVG paths for status, camera, radar, alert, file, and download icons.
2. **No gradient text**: High contrast solid text with balanced typographic scale.
3. **No thick left borders**: Elegant 1px precision borders with contextual background tinting.
4. **Accessible contrast**: Text contrast ratios exceeding 7:1 against dark cards.
5. **Full browser styling**: Bespoke scrollbars, custom text selection, active focus rings, and streamlined Streamlit widget wrappers.
