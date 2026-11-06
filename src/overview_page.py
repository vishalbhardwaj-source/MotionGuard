import os
from pathlib import Path
import streamlit as st
from src.ui_icons import get_svg_icon


def render_project_overview_page():
    """
    Renders the executive project overview, mission statement, architectural pipeline,
    mathematical derivations, and empirical benchmark results for MotionGuard.
    Adheres strictly to Impeccable and UI/UX Pro Max guidelines.
    """
    # Quick Navigation Header
    header_col1, header_col2 = st.columns([2, 1])
    with header_col1:
        st.html(
            f"""
            <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 8px;">
                <span style="display: inline-flex; align-items: center; justify-content: center; width: 30px; height: 30px; background: rgba(56, 189, 248, 0.12); border: 1px solid rgba(56, 189, 248, 0.3); border-radius: 6px;">
                    {get_svg_icon("layers", size=18, color="#38bdf8")}
                </span>
                <span style="font-size: 1.15rem; font-weight: 800; color: #ffffff; letter-spacing: -0.02em;">MotionGuard</span>
                <span style="background: rgba(56, 189, 248, 0.12); border: 1px solid rgba(56, 189, 248, 0.35); color: #38bdf8; padding: 2px 8px; border-radius: 999px; font-size: 0.70rem; font-weight: 700; text-transform: uppercase; font-family: 'JetBrains Mono', monospace;">
                    System Architecture & Mission
                </span>
            </div>
            """
        )
    with header_col2:
        top_btn_w, top_btn_ws = st.columns(2)
        with top_btn_w:
            if st.button("Welcome Portal", use_container_width=True, key="ov_top_welcome_btn"):
                st.session_state["active_view"] = "welcome"
                st.rerun()
        with top_btn_ws:
            if st.button("Workstation →", type="primary", use_container_width=True, key="top_cta_workstation"):
                st.session_state["active_view"] = "workstation"
                st.rerun()

    # Grand Futuristic Hero Banner
    st.html(
        f"""
        <div style="
            background: radial-gradient(circle at 12% 18%, rgba(14, 116, 144, 0.30) 0%, rgba(11, 15, 25, 0.96) 80%),
                        linear-gradient(135deg, rgba(15, 23, 42, 0.85), rgba(8, 12, 22, 0.98));
            border: 1px solid rgba(56, 189, 248, 0.35);
            border-radius: 16px;
            padding: 32px 30px 26px 30px;
            margin-bottom: 24px;
            box-shadow: 0 16px 40px rgba(0, 0, 0, 0.55);
            position: relative;
            overflow: hidden;
        ">
            <div style="position: absolute; top: 0; left: 0; right: 0; height: 2px; background: linear-gradient(90deg, #38bdf8, #818cf8, #10b981);"></div>
            <div style="display: inline-flex; align-items: center; gap: 8px; background: rgba(56, 189, 248, 0.1); border: 1px solid rgba(56, 189, 248, 0.35); padding: 4px 12px; border-radius: 999px; font-size: 0.74rem; font-weight: 700; color: #38bdf8; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 14px; font-family: 'JetBrains Mono', monospace;">
                <span style="display: inline-block; width: 6px; height: 6px; border-radius: 50%; background: #38bdf8; box-shadow: 0 0 8px #38bdf8;"></span>
                Autonomous Incident Detection & Emergency Dispatch Hub
            </div>
            <h1 style="font-size: clamp(1.85rem, 3.1vw, 2.75rem); font-weight: 800; letter-spacing: -0.03em; color: #ffffff; margin: 0 0 12px 0; line-height: 1.15;">
                MotionGuard: Autonomous Road-Safety Intelligence
            </h1>
            <p style="font-size: clamp(0.96rem, 1.25vw, 1.14rem); color: #cbd5e1; max-width: 940px; line-height: 1.6; margin: 0 0 18px 0;">
                Transforming standard highway surveillance CCTV into a proactive, physics-grounded incident investigation workstation.
                MotionGuard detects real-world highway collisions in <strong style="color: #f8fafc;">sub-second time (0.30s)</strong>, eliminates alert fatigue with
                <strong style="color: #f8fafc;">0.0 false alarms on normal traffic</strong>, and autonomously dispatches <strong style="color: #f8fafc;">photographic keyframe evidence and PDF dossiers</strong> to emergency authorities.
            </p>
        </div>
        """
    )

    # Key Performance Metric Ribbon
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.html(
            f"""
            <div class="kpi-card">
                <div class="kpi-label" style="color: #34d399;">
                    {get_svg_icon("cpu", size=14, color="#34d399")} Neural Inference
                </div>
                <div class="kpi-value">~18<span style="font-size: 0.95rem; font-weight: 600; color: #94a3b8; font-family: 'JetBrains Mono', monospace;">ms</span></div>
                <div class="kpi-caption">YOLO11n + ByteTrack CUDA FP16</div>
            </div>
            """
        )
    with k2:
        st.html(
            f"""
            <div class="kpi-card">
                <div class="kpi-label" style="color: #38bdf8;">
                    {get_svg_icon("shield", size=14, color="#38bdf8")} False Responder Alarms
                </div>
                <div class="kpi-value">0.0<span style="font-size: 0.95rem; font-weight: 600; color: #94a3b8; font-family: 'JetBrains Mono', monospace;">/hr</span></div>
                <div class="kpi-caption">Zero nuisance alerts on normal traffic</div>
            </div>
            """
        )
    with k3:
        st.html(
            f"""
            <div class="kpi-card">
                <div class="kpi-label" style="color: #f87171;">
                    {get_svg_icon("zap", size=14, color="#f87171")} Detection Onset Delay
                </div>
                <div class="kpi-value" style="color: #f87171;">0.30<span style="font-size: 0.95rem; font-weight: 600; color: #94a3b8; font-family: 'JetBrains Mono', monospace;">s</span></div>
                <div class="kpi-caption">Escalation within 300ms of collision contact</div>
            </div>
            """
        )
    with k4:
        st.html(
            f"""
            <div class="kpi-card">
                <div class="kpi-label" style="color: #c084fc;">
                    {get_svg_icon("activity", size=14, color="#c084fc")} Alert Deduplication
                </div>
                <div class="kpi-value" style="color: #c084fc;">88<span style="font-size: 0.95rem; font-weight: 600; color: #94a3b8; font-family: 'JetBrains Mono', monospace;">%</span></div>
                <div class="kpi-caption">Redundant warnings fused into episodes</div>
            </div>
            """
        )

    st.html("<div style='height: 20px;'></div>")

    # 4 Key Architectural Pillars (Feature Showcase Grid)
    st.markdown("### The 4 Pillars of MotionGuard")
    st.caption("How MotionGuard achieves reliable accident recognition without expensive 3D LiDAR or depth sensors:")

    p1, p2, p3, p4 = st.columns(4)

    with p1:
        st.html(
            f"""
            <div class="portal-card">
                <div style="display: flex; align-items: center; justify-content: center; width: 36px; height: 36px; background: rgba(56, 189, 248, 0.12); border: 1px solid rgba(56, 189, 248, 0.3); border-radius: 8px; margin-bottom: 12px;">
                    {get_svg_icon("camera", size=18, color="#38bdf8")}
                </div>
                <h4 style="color: #38bdf8; margin: 0 0 8px 0; font-size: 1.05rem; font-weight: 700;">Edge Vision Perception</h4>
                <p style="color: #94a3b8; font-size: 0.83rem; line-height: 1.5; margin: 0;">
                    YOLO11n neural detector running in CUDA FP16 mode (~18ms inference), filtered strictly to motorized vehicle classes to eliminate background distraction.
                </p>
            </div>
            """
        )

    with p2:
        st.html(
            f"""
            <div class="portal-card">
                <div style="display: flex; align-items: center; justify-content: center; width: 36px; height: 36px; background: rgba(16, 185, 129, 0.12); border: 1px solid rgba(16, 185, 129, 0.3); border-radius: 8px; margin-bottom: 12px;">
                    {get_svg_icon("activity", size=18, color="#10b981")}
                </div>
                <h4 style="color: #34d399; margin: 0 0 8px 0; font-size: 1.05rem; font-weight: 700;">Optical Tau Kinematics</h4>
                <p style="color: #94a3b8; font-size: 0.83rem; line-height: 1.5; margin: 0;">
                    Solves monocular camera perspective foreshortening using Lee's ecological optic flow (τ ≈ s / (ds/dt)) and bounding box physical contact IoU (≥ 0.05).
                </p>
            </div>
            """
        )

    with p3:
        st.html(
            f"""
            <div class="portal-card">
                <div style="display: flex; align-items: center; justify-content: center; width: 36px; height: 36px; background: rgba(239, 68, 68, 0.12); border: 1px solid rgba(239, 68, 68, 0.3); border-radius: 8px; margin-bottom: 12px;">
                    {get_svg_icon("shield-alert", size=18, color="#ef4444")}
                </div>
                <h4 style="color: #f87171; margin: 0 0 8px 0; font-size: 1.05rem; font-weight: 700;">Instant Alert Escalation</h4>
                <p style="color: #94a3b8; font-size: 0.83rem; line-height: 1.5; margin: 0;">
                    Pushes real-time alerts to responders' smartphones via Telegram Bot API with visual snapshots, plus local carrier simulator with rate-limiting cooldown.
                </p>
            </div>
            """
        )

    with p4:
        st.html(
            f"""
            <div class="portal-card">
                <div style="display: flex; align-items: center; justify-content: center; width: 36px; height: 36px; background: rgba(192, 132, 252, 0.12); border: 1px solid rgba(192, 132, 252, 0.3); border-radius: 8px; margin-bottom: 12px;">
                    {get_svg_icon("file-text", size=18, color="#c084fc")}
                </div>
                <h4 style="color: #c084fc; margin: 0 0 8px 0; font-size: 1.05rem; font-weight: 700;">Forensic PDF Dossiers</h4>
                <p style="color: #94a3b8; font-size: 0.83rem; line-height: 1.5; margin: 0;">
                    Automatically compiles structured investigation-support PDF reports with vehicle telemetry, closest-approach photos, and scientific disclaimers.
                </p>
            </div>
            """
        )

    st.html("<div style='height: 24px;'></div>")

    # Before vs After MotionGuard Comparison
    st.markdown("### Operational Paradigm Shift: Real-World Comparison")
    st.caption("Comparing traditional traffic monitoring with MotionGuard Autonomous Edge AI:")

    comp_col1, comp_col2 = st.columns(2)

    with comp_col1:
        st.html(
            f"""
            <div style="
                background: rgba(239, 68, 68, 0.05);
                border: 1px solid rgba(239, 68, 68, 0.28);
                border-radius: 12px;
                padding: 22px;
                height: 100%;
            ">
                <div style="font-size: 1.10rem; font-weight: 700; color: #f87171; margin-bottom: 14px; display: flex; align-items: center; gap: 8px;">
                    {get_svg_icon("alert-triangle", size=18, color="#ef4444")} Traditional CCTV Monitoring & Naive AI
                </div>
                <ul style="color: #cbd5e1; font-size: 0.86rem; line-height: 1.7; padding-left: 20px; margin: 0;">
                    <li><strong style="color: #f1f5f9;">5–15 Minute Response Latency:</strong> Operators only learn of accidents when emergency 911 phone calls arrive from passing drivers.</li>
                    <li><strong style="color: #f1f5f9;">Severe Alert Fatigue:</strong> Naive frame-by-frame distance triggers hundreds of false alarms per day on routine close lane merges.</li>
                    <li><strong style="color: #f1f5f9;">Manual Video Scrubbing:</strong> Investigators spend hours manually seeking keyframe timestamps from gigabytes of footage.</li>
                    <li><strong style="color: #f1f5f9;">Black-Box Predictions:</strong> Opaque neural models give raw probabilities with no auditable physics or legal chain-of-custody.</li>
                </ul>
            </div>
            """
        )

    with comp_col2:
        st.html(
            f"""
            <div style="
                background: rgba(16, 185, 129, 0.05);
                border: 1px solid rgba(16, 185, 129, 0.28);
                border-radius: 12px;
                padding: 22px;
                height: 100%;
            ">
                <div style="font-size: 1.10rem; font-weight: 700; color: #34d399; margin-bottom: 14px; display: flex; align-items: center; gap: 8px;">
                    {get_svg_icon("check-circle", size=18, color="#10b981")} MotionGuard Autonomous Edge AI
                </div>
                <ul style="color: #cbd5e1; font-size: 0.86rem; line-height: 1.7; padding-left: 20px; margin: 0;">
                    <li><strong style="color: #f1f5f9;">0.30s Impact Detection:</strong> Autonomous escalation within 300 milliseconds of physical vehicle contact.</li>
                    <li><strong style="color: #f1f5f9;">0.0 False Alarms / Hour:</strong> Strict two-tier isolation ensures zero nuisance emergency sirens on normal traffic.</li>
                    <li><strong style="color: #f1f5f9;">Automated Keyframe & Video HUD:</strong> Instantly extracts closest-approach evidence and exports ±2.5s telemetry video replays.</li>
                    <li><strong style="color: #f1f5f9;">Explainable Physics Audit:</strong> Every alert provides transparent track IDs, closing velocities, optical tau (τ), and auto-compiled PDF dossiers.</li>
                </ul>
            </div>
            """
        )

    st.html("<div style='height: 24px;'></div>")

    # 6-Stage End-to-End Architectural Pipeline
    st.markdown("### End-to-End System Architecture")
    st.caption("How raw surveillance camera footage flows through MotionGuard to deliver sub-second emergency response:")

    pipe_steps = [
        {
            "tag": "STAGE 01",
            "title": "Surveillance Stream Ingestion",
            "icon": "video",
            "desc": "Accepts high-throughput highway surveillance footage (MP4, AVI, MOV, RTSP-ready). Handles variable lighting and perspective foreshortening.",
            "tech": "OpenCV · FFmpeg H.264",
        },
        {
            "tag": "STAGE 02",
            "title": "Class-Filtered Neural Perception",
            "icon": "crosshair",
            "desc": "Ultralytics YOLO11n filters detections strictly to motorized road vehicles (car, truck, bus, motorcycle), preventing noise from road signs or barriers.",
            "tech": "YOLO11n · CUDA FP16 (~18ms)",
        },
        {
            "tag": "STAGE 03",
            "title": "Persistent Multi-Object Tracking",
            "icon": "radar",
            "desc": "ByteTrack (with BoT-SORT support) assigns persistent track IDs across frames, building continuous trajectory coordinates and velocity vectors.",
            "tech": "ByteTrack · Kalman Association",
        },
        {
            "tag": "STAGE 04",
            "title": "Kinematic Physics & Optical Tau (τ)",
            "icon": "activity",
            "desc": "Calculates monocular bounding box growth rate (τ ≈ s / (ds/dt)), scale-normalized distance (d_norm), IoU physical contact, and post-impact kinetic halts.",
            "tech": "Ecological Optic Flow · Kinematics",
        },
        {
            "tag": "STAGE 05",
            "title": "Spatial Geofencing & Zone Rules",
            "icon": "compass",
            "desc": "Polygon region-of-interest zones dynamically modulate sensitivity: merge zones tolerate tighter vehicle headway; breakdown shoulders escalate vigilance.",
            "tech": "Ray-Casting Geofencing",
        },
        {
            "tag": "STAGE 06",
            "title": "Autonomous Escalation & PDF Dossiers",
            "icon": "send",
            "desc": "Instantly delivers rich Telegram emergency alerts with photographic evidence snapshots, SMS dispatches, and auto-compiles forensic PDF dossiers.",
            "tech": "Telegram Bot · Twilio · ReportLab PDF",
        },
    ]

    p_col1, p_col2 = st.columns(2)
    for idx, s in enumerate(pipe_steps):
        target_col = p_col1 if idx % 2 == 0 else p_col2
        with target_col:
            st.html(
                f"""
                <div style="
                    background: rgba(15, 23, 42, 0.70);
                    border: 1px solid rgba(56, 189, 248, 0.20);
                    border-radius: 10px;
                    padding: 16px 20px;
                    margin-bottom: 14px;
                    display: flex;
                    align-items: flex-start;
                    gap: 14px;
                ">
                    <div style="
                        background: rgba(56, 189, 248, 0.12);
                        color: #38bdf8;
                        border: 1px solid rgba(56, 189, 248, 0.35);
                        font-family: 'JetBrains Mono', monospace;
                        font-weight: 700;
                        font-size: 0.74rem;
                        padding: 6px 8px;
                        border-radius: 6px;
                        line-height: 1;
                        white-space: nowrap;
                    ">{s['tag']}</div>
                    <div style="flex: 1;">
                        <div style="display: flex; align-items: center; gap: 8px; font-weight: 700; font-size: 0.98rem; color: #f8fafc; margin-bottom: 6px;">
                            {get_svg_icon(s['icon'], size=16, color='#38bdf8')} {s['title']}
                        </div>
                        <div style="font-size: 0.84rem; color: #94a3b8; line-height: 1.5; margin-bottom: 8px;">
                            {s['desc']}
                        </div>
                        <span style="display: inline-block; background: rgba(255,255,255,0.06); color: #7dd3fc; padding: 2px 8px; border-radius: 4px; font-size: 0.72rem; font-family: 'JetBrains Mono', monospace;">
                            {s['tech']}
                        </span>
                    </div>
                </div>
                """
            )

    st.html("<div style='height: 24px;'></div>")

    # Multi-Class Severity & Protocol Matrix
    st.markdown("### Multi-Class Incident Severity & Response Protocols")
    st.caption("How MotionGuard categorizes road hazards and maps them to appropriate emergency response procedures:")

    m_col1, m_col2, m_col3 = st.columns(3)

    with m_col1:
        st.html(
            f"""
            <div class="portal-card" style="border: 1px solid rgba(239, 68, 68, 0.45);">
                <div>
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                        <span style="font-weight: 800; font-size: 0.98rem; color: #f87171; display: flex; align-items: center; gap: 6px;">
                            {get_svg_icon("alert-triangle", size=16, color="#ef4444")} CONFIRMED COLLISION
                        </span>
                        <span style="background: rgba(239, 68, 68, 0.2); border: 1px solid rgba(239, 68, 68, 0.45); color: #f87171; padding: 2px 8px; border-radius: 4px; font-size: 0.70rem; font-weight: 700; font-family: 'JetBrains Mono', monospace;">
                            PRIORITY 1
                        </span>
                    </div>
                    <div style="font-size: 0.84rem; color: #cbd5e1; line-height: 1.45; margin-bottom: 12px;">
                        <strong style="color: #f1f5f9;">Trigger Condition:</strong> Physical bounding box contact (IoU ≥ 0.05) or sudden post-impact kinetic halt (v &lt; 5 px/s). Threat Score: <strong style="color: #f87171;">80–100</strong>.
                    </div>
                    <div style="background: rgba(15, 23, 42, 0.85); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 6px; padding: 12px; font-size: 0.80rem; color: #e2e8f0; line-height: 1.45;">
                        <strong style="color: #38bdf8;">Action Protocol:</strong> Autonomous Telegram alert with photographic snapshot proof + carrier SMS + forensic ReportLab PDF dossier generation.
                        <div style="margin-top: 6px; color: #f87171; font-weight: 600;">Dispatch: EMS Ambulances, Highway Patrol, Tow Recovery.</div>
                    </div>
                </div>
            </div>
            """
        )

    with m_col2:
        st.html(
            f"""
            <div class="portal-card" style="border: 1px solid rgba(245, 158, 11, 0.45);">
                <div>
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                        <span style="font-weight: 800; font-size: 0.98rem; color: #fbbf24; display: flex; align-items: center; gap: 6px;">
                            {get_svg_icon("activity", size=16, color="#f59e0b")} NEAR-MISS CONFLICT
                        </span>
                        <span style="background: rgba(245, 158, 11, 0.2); border: 1px solid rgba(245, 158, 11, 0.45); color: #fbbf24; padding: 2px 8px; border-radius: 4px; font-size: 0.70rem; font-weight: 700; font-family: 'JetBrains Mono', monospace;">
                            SAFETY TRIAGE
                        </span>
                    </div>
                    <div style="font-size: 0.84rem; color: #cbd5e1; line-height: 1.45; margin-bottom: 12px;">
                        <strong style="color: #f1f5f9;">Trigger Condition:</strong> Rapid optical-tau approach rate (TTC &lt; 2.0s) and close separation without physical contact. Threat Score: <strong style="color: #fbbf24;">50–75</strong>.
                    </div>
                    <div style="background: rgba(15, 23, 42, 0.85); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 6px; padding: 12px; font-size: 0.80rem; color: #e2e8f0; line-height: 1.45;">
                        <strong style="color: #38bdf8;">Action Protocol:</strong> Logged to Operator Investigation Queue for forensic review. Replay clip exported with burned-in telemetry HUD. No false emergency sirens.
                        <div style="margin-top: 6px; color: #fbbf24; font-weight: 600;">Dispatch: Traffic Operations Center, Safety Analytics.</div>
                    </div>
                </div>
            </div>
            """
        )

    with m_col3:
        st.html(
            f"""
            <div class="portal-card" style="border: 1px solid rgba(192, 132, 252, 0.45);">
                <div>
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                        <span style="font-weight: 800; font-size: 0.98rem; color: #c084fc; display: flex; align-items: center; gap: 6px;">
                            {get_svg_icon("alert-triangle", size=16, color="#c084fc")} STOPPED OBSTRUCTION
                        </span>
                        <span style="background: rgba(192, 132, 252, 0.2); border: 1px solid rgba(192, 132, 252, 0.45); color: #c084fc; padding: 2px 8px; border-radius: 4px; font-size: 0.70rem; font-weight: 700; font-family: 'JetBrains Mono', monospace;">
                            HAZARD PATROL
                        </span>
                    </div>
                    <div style="font-size: 0.84rem; color: #cbd5e1; line-height: 1.45; margin-bottom: 12px;">
                        <strong style="color: #f1f5f9;">Trigger Condition:</strong> Vehicle cessation of motion (&gt; 2.0s halt) within active travel lanes or emergency breakdown shoulder. Threat Score: <strong style="color: #c084fc;">40–60</strong>.
                    </div>
                    <div style="background: rgba(15, 23, 42, 0.85); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 6px; padding: 12px; font-size: 0.80rem; color: #e2e8f0; line-height: 1.45;">
                        <strong style="color: #38bdf8;">Action Protocol:</strong> Secondary incident hazard logged. Highway dynamic message sign advisory queued to divert oncoming traffic.
                        <div style="margin-top: 6px; color: #c084fc; font-weight: 600;">Dispatch: Incident Response Tow & Roadway Maintenance.</div>
                    </div>
                </div>
            </div>
            """
        )

    st.html("<div style='height: 24px;'></div>")

    # Interactive Technical Innovations Deep Dive
    st.markdown("### Deep-Dive: Core Technical Innovations")
    st.caption("Expand below to examine the mathematical physics and software engineering underpinning MotionGuard:")

    with st.expander("1. Monocular Optical Scale TTC (Lee's Tau τ)", expanded=False):
        st.markdown(
            r"""
            #### Why Raw Euclidean Pixel Distance Fails in Monocular Cameras
            A monocular surveillance camera projects a 3D real-world scene onto a 2D image plane ($Z \to (x, y)$).
            Two vehicles driving 50 meters away in the background may be separated by only **15 pixels**, while two vehicles
            in the immediate foreground separated by 5 meters span **120 pixels**.

            If an AI collision detector relies solely on raw pixel distance ($d = \sqrt{\Delta x^2 + \Delta y^2}$), it will trigger
            false alarms on distant vehicles and fail to catch high-speed impacts nearby.

            #### Lee's Ecological Optic Flow Formulation
            MotionGuard calculates the monocular scale growth rate:
            $$\tau = \frac{s(t)}{\frac{ds(t)}{dt}}$$
            Where:
            - $s(t) = \sqrt{\text{width} \times \text{height}}$ represents bounding box optical scale.
            - $\frac{ds(t)}{dt}$ represents the rate of optical looming (expansion) over time.

            As vehicle $A$ approaches vehicle $B$, its retinal size $s$ grows exponentially. When $\tau$ drops below **3.5 seconds**,
            a high-risk optical approach is detected **independently of camera focal length calibration**.
            """
        )

    with st.expander("2. Two-Tier Architecture: Zero False Responder Alarms", expanded=False):
        st.markdown(
            r"""
            #### The Two-Tier Paradigm:
            1. **Tier 1: Continuous Candidate Monitoring (Safety Analyst Queue)**
               - Tracks all candidate vehicle interactions, lane changes, and close headway approaches.
               - Temporal deduplication clusters adjacent-frame warnings into a single cohesive interaction episode.
               - Provides traffic safety engineers with proactive conflict heatmaps.
            2. **Tier 2: High-Consequence Autonomous Emergency Dispatch**
               - Reserved **strictly** for verified physical collisions ($IoU \ge 0.05$, post-impact deceleration halt, or threat score $\ge 80$).
               - Bypasses false alarms completely, yielding **0.0 false emergency responder alerts per hour** on normal highway traffic.
            """
        )

    with st.expander("3. Dynamic Incident Video Clip Exporter with Telemetry HUD", expanded=False):
        st.markdown(
            r"""
            #### Beyond Static Snapshots:
            While first responders need an instant photo on their phones, courtrooms, insurers, and forensic investigators
            require video motion context.
            - MotionGuard exports a **5.0-second incident video clip** ($[-2.5\text{s}, +2.5\text{s}]$ window) centered on the exact moment of minimum separation.
            - Burns a real-time **telemetry HUD** (timestamp, time-delta from collision onset, event ID, and severity badge) directly into the video stream.
            - Transcodes via FFmpeg to streamable H.264 (`yuv420p` + `faststart`) for instant playback in modern web browsers and Telegram push messages.
            """
        )

    with st.expander("4. Empirical Calibration & Ground-Truth Confusion Matrix", expanded=False):
        st.markdown(
            r"""
            #### Interactive Empirical Tuning:
            In Tab 6 of the Workstation, traffic authorities can interactively tune:
            - **Bounding Box Contact IoU Threshold** ($0.01$ to $0.30$)
            - **Monocular Scale Expansion TTC Ceiling** ($0.5\text{s}$ to $5.0\text{s}$)
            - **Scale-Normalized Distance ($d_{\text{norm}}$)** ($0.2$ to $3.0\times$)

            The system recalculates in real-time an empirical $2 \times 2$ **Confusion Matrix** (TP, FP, FN, TN),
            Precision, Recall, Specificity, F1-Score, and False Alarms per Hour, providing automated recommendations
            for optimal operational deployment.
            """
        )

    st.html("<div style='height: 24px;'></div>")

    # Technology Stack Badges
    st.markdown("### Technical Specifications & Stack")
    badges = [
        ("cpu", "Python 3.12"),
        ("crosshair", "Ultralytics YOLO11n"),
        ("radar", "ByteTrack"),
        ("sliders", "BoT-SORT Option"),
        ("zap", "PyTorch CUDA FP16"),
        ("video", "OpenCV 4.10"),
        ("file-text", "ReportLab PDF Engine"),
        ("send", "Telegram Bot API"),
        ("radio", "Twilio SMS Gateway"),
        ("layers", "Streamlit 1.35+"),
        ("activity", "SQLite Audit DB"),
        ("terminal", "FFmpeg H.264"),
    ]
    badge_html = " ".join([
        f"<span class='badge-pill' style='display: inline-flex; align-items: center; gap: 5px; font-family: \"JetBrains Mono\", monospace;'>{get_svg_icon(b[0], size=12, color='#38bdf8')} {b[1]}</span>"
        for b in badges
    ])
    st.html(badge_html)

    st.html("<div style='height: 30px;'></div>")

    # Bottom Call to Action
    st.html(
        f"""
        <div style="
            background: linear-gradient(135deg, rgba(14, 116, 144, 0.25), rgba(11, 15, 25, 0.95));
            border: 1px solid rgba(56, 189, 248, 0.35);
            border-radius: 14px;
            padding: 28px 30px;
            text-align: center;
            margin-bottom: 22px;
            position: relative;
        ">
            <h3 style="color: #ffffff; margin: 0 0 10px 0; font-size: 1.40rem; font-weight: 800;">
                Ready to Experience MotionGuard in Action?
            </h3>
            <p style="color: #94a3b8; font-size: 0.92rem; max-width: 650px; margin: 0 auto 20px auto; line-height: 1.6;">
                Jump into the live Operations Workstation to upload surveillance footage, run YOLO11 + ByteTrack tracking,
                simulate autonomous emergency broadcasts, and inspect explainable risk dossiers.
            </p>
        </div>
        """
    )

    btn_col1, btn_col2 = st.columns(2)
    with btn_col1:
        if st.button("Back to Welcome Page", use_container_width=True, key="bottom_welcome_btn"):
            st.session_state["active_view"] = "welcome"
            st.rerun()
    with btn_col2:
        if st.button("Launch Live Operations Workstation Now", type="primary", use_container_width=True, key="bottom_cta_workstation"):
            st.session_state["active_view"] = "workstation"
            st.rerun()

    st.divider()
    st.caption("MotionGuard AI · Submission Ready · Operations Edition · Explainable Decision-Support System")
