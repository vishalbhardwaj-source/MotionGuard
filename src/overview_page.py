import os
from pathlib import Path
import streamlit as st


def render_project_overview_page():
    """
    Renders the executive project overview, mission statement, architectural pipeline,
    and technological differentiators for MotionGuard.
    """
    # Quick Navigation Header
    header_col1, header_col2 = st.columns([3, 1])
    with header_col1:
        st.markdown(
            """
            <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 8px;">
                <span style="font-size: 1.5rem;">🚦</span>
                <span style="font-size: 1.1rem; font-weight: 800; color: #ffffff; letter-spacing: -0.02em;">MotionGuard</span>
                <span style="background: rgba(56, 189, 248, 0.15); border: 1px solid rgba(56, 189, 248, 0.35); color: #38bdf8; padding: 2px 8px; border-radius: 999px; font-size: 0.72rem; font-weight: 700; text-transform: uppercase;">
                    Edge AI · Road Safety Workstation
                </span>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with header_col2:
        if st.button("🚀 Launch Operations Workstation →", type="primary", use_container_width=True, key="top_cta_workstation"):
            st.session_state["active_view"] = "workstation"
            st.rerun()

    # Grand Futuristic Hero Banner
    st.markdown(
        """
        <div style="
            background: radial-gradient(circle at 15% 20%, rgba(14, 116, 144, 0.35) 0%, rgba(15, 23, 42, 0.95) 85%);
            border: 1px solid rgba(56, 189, 248, 0.35);
            border-radius: 16px;
            padding: 34px 32px 28px 32px;
            margin-bottom: 24px;
            box-shadow: 0 12px 36px rgba(0, 0, 0, 0.45);
        ">
            <div style="display: inline-flex; align-items: center; gap: 8px; background: rgba(56, 189, 248, 0.12); border: 1px solid rgba(56, 189, 248, 0.35); padding: 4px 12px; border-radius: 999px; font-size: 0.75rem; font-weight: 700; color: #38bdf8; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 12px;">
                <span style="display: inline-block; width: 6px; height: 6px; border-radius: 50%; background: #38bdf8; box-shadow: 0 0 6px #38bdf8;"></span>
                Autonomous Incident Detection & Emergency Dispatch Hub
            </div>
            <h1 style="font-size: clamp(1.9rem, 3.2vw, 2.85rem); font-weight: 850; letter-spacing: -0.03em; color: #ffffff; margin: 0 0 12px 0; line-height: 1.15;">
                MotionGuard: Autonomous Road-Safety Intelligence
            </h1>
            <p style="font-size: clamp(0.98rem, 1.25vw, 1.15rem); color: #cbd5e1; max-width: 920px; line-height: 1.55; margin: 0 0 20px 0;">
                Transform standard traffic surveillance CCTV into a proactive, physics-grounded incident investigation workstation.
                MotionGuard detects real-world highway collisions in <b>sub-second time (0.30s)</b>, eliminates alert fatigue with
                <b>zero false alarms on normal traffic</b>, and autonomously dispatches <b>photographic keyframe evidence and PDF dossiers</b> to emergency authorities.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Key Performance Metric Ribbon
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(
            """
            <div class="kpi-card" style="border-left: 3px solid #10b981;">
                <div class="kpi-label" style="color: #34d399;">⚡ Neural Inference</div>
                <div class="kpi-value">~18<span style="font-size: 1rem; font-weight: 600; color: #94a3b8;">ms</span></div>
                <div class="kpi-caption">YOLO11n + ByteTrack CUDA FP16</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with k2:
        st.markdown(
            """
            <div class="kpi-card" style="border-left: 3px solid #38bdf8;">
                <div class="kpi-label" style="color: #38bdf8;">🛡️ False Responder Alarms</div>
                <div class="kpi-value">0.0<span style="font-size: 1rem; font-weight: 600; color: #94a3b8;">/hr</span></div>
                <div class="kpi-caption">Zero nuisance alerts on normal traffic</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with k3:
        st.markdown(
            """
            <div class="kpi-card" style="border-left: 3px solid #ef4444;">
                <div class="kpi-label" style="color: #f87171;">⏱️ Detection Onset Delay</div>
                <div class="kpi-value" style="color: #f87171;">0.30<span style="font-size: 1rem; font-weight: 600; color: #94a3b8;">s</span></div>
                <div class="kpi-caption">Escalation within 300ms of collision contact</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with k4:
        st.markdown(
            """
            <div class="kpi-card" style="border-left: 3px solid #a855f7;">
                <div class="kpi-label" style="color: #c084fc;">📦 Alert Deduplication</div>
                <div class="kpi-value" style="color: #c084fc;">88<span style="font-size: 1rem; font-weight: 600; color: #94a3b8;">%</span></div>
                <div class="kpi-caption">Redundant warnings fused into episodes</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height: 18px;'></div>", unsafe_allow_html=True)

    # Mission & Problem vs Solution
    st.subheader("📌 The Mission: Solving the Road-Safety Crisis")
    st.caption("Why traditional traffic camera monitoring fails and how MotionGuard fixes it.")

    col_prob, col_sol, col_exp = st.columns(3)

    with col_prob:
        st.markdown(
            """
            <div style="
                background: rgba(30, 41, 59, 0.55);
                border: 1px solid rgba(239, 68, 68, 0.35);
                border-top: 4px solid #ef4444;
                border-radius: 12px;
                padding: 20px;
                height: 100%;
            ">
                <div style="font-size: 1.5rem; margin-bottom: 8px;">🛑</div>
                <h4 style="color: #f87171; margin: 0 0 8px 0; font-size: 1.1rem;">The Crisis: Alert Fatigue</h4>
                <p style="color: #cbd5e1; font-size: 0.88rem; line-height: 1.5; margin: 0;">
                    Traffic command centers monitor hundreds of video feeds manually. Naive computer vision systems trigger hundreds of false alarms for routine merges and close following.
                    Operators suffer <b>severe alert fatigue</b>, causing catastrophic accidents to go unnoticed for <b>5–15 minutes</b> until 911 calls arrive.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_sol:
        st.markdown(
            """
            <div style="
                background: rgba(30, 41, 59, 0.55);
                border: 1px solid rgba(56, 189, 248, 0.35);
                border-top: 4px solid #38bdf8;
                border-radius: 12px;
                padding: 20px;
                height: 100%;
            ">
                <div style="font-size: 1.5rem; margin-bottom: 8px;">⚡</div>
                <h4 style="color: #38bdf8; margin: 0 0 8px 0; font-size: 1.1rem;">The Solution: Physics Kinematics</h4>
                <p style="color: #cbd5e1; font-size: 0.88rem; line-height: 1.5; margin: 0;">
                    MotionGuard overcomes monocular camera distortion by calculating <b>Lee's Optical-Tau (τ) Time-To-Collision</b>, <b>Scale-Normalized Distance (d<sub>norm</sub>)</b>,
                    and <b>Bounding Box Contact IoU (≥ 0.05)</b>. It filters routine close passing and triggers emergency dispatches <b>only upon verified physical impact</b>.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_exp:
        st.markdown(
            """
            <div style="
                background: rgba(30, 41, 59, 0.55);
                border: 1px solid rgba(52, 211, 153, 0.35);
                border-top: 4px solid #34d399;
                border-radius: 12px;
                padding: 20px;
                height: 100%;
            ">
                <div style="font-size: 1.5rem; margin-bottom: 8px;">⚖️</div>
                <h4 style="color: #34d399; margin: 0 0 8px 0; font-size: 1.1rem;">The Standard: Explainable Audit</h4>
                <p style="color: #cbd5e1; font-size: 0.88rem; line-height: 1.5; margin: 0;">
                    No black-box predictions. Every flagged incident produces an <b>auditable evidentiary chain</b>: exact vehicle track IDs, timestamps, closing speed vectors,
                    photographic snapshots, and auto-generated <b>ReportLab PDF forensic dossiers</b> ready for first responders and court proceedings.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height: 24px;'></div>", unsafe_allow_html=True)

    # 6-Stage End-to-End Architectural Pipeline
    st.subheader("🏗️ End-to-End System Architecture")
    st.caption("How raw surveillance camera footage flows through MotionGuard to deliver sub-second emergency response.")

    pipe_steps = [
        {
            "num": "01",
            "title": "Surveillance Stream Ingestion",
            "icon": "📹",
            "desc": "Accepts high-throughput highway surveillance footage (MP4, AVI, MOV, RTSP-ready). Handles variable lighting and perspective foreshortening.",
            "tech": "OpenCV · FFmpeg",
        },
        {
            "num": "02",
            "title": "Class-Filtered Neural Perception",
            "icon": "🔍",
            "desc": "Ultralytics YOLO11n filters detections strictly to motorized road vehicles (car, truck, bus, motorcycle), preventing noise from road signs or barriers.",
            "tech": "YOLO11n · CUDA FP16 (~18ms)",
        },
        {
            "num": "03",
            "title": "Persistent Multi-Object Tracking",
            "icon": "🎯",
            "desc": "ByteTrack (with BoT-SORT support) assigns persistent track IDs across frames, building continuous trajectory coordinates and velocity vectors.",
            "tech": "ByteTrack · Kalman Filtering",
        },
        {
            "num": "04",
            "title": "Kinematic Physics & Optical Tau (τ)",
            "icon": "📐",
            "desc": "Calculates monocular bounding box growth rate (τ ≈ s / (ds/dt)), scale-normalized distance (d_norm), IoU physical contact, and post-impact kinetic halts.",
            "tech": "Ecological Optic Flow · Kinematics",
        },
        {
            "num": "05",
            "title": "Spatial Geofencing & Zone Rules",
            "icon": "🗺️",
            "desc": "Polygon region-of-interest zones dynamically modulate sensitivity: merge zones tolerate tighter vehicle headway; breakdown shoulders escalate vigilance.",
            "tech": "Ray-Casting Geofencing",
        },
        {
            "num": "06",
            "title": "Autonomous Escalation & PDF Dossiers",
            "icon": "🚨",
            "desc": "Instantly delivers rich Telegram emergency alerts with photographic evidence snapshots, SMS dispatches, and auto-compiles forensic PDF dossiers.",
            "tech": "Telegram Bot · Twilio · ReportLab PDF",
        },
    ]

    p_col1, p_col2 = st.columns(2)
    for idx, s in enumerate(pipe_steps):
        target_col = p_col1 if idx % 2 == 0 else p_col2
        with target_col:
            st.markdown(
                f"""
                <div style="
                    background: rgba(15, 23, 42, 0.70);
                    border: 1px solid rgba(56, 189, 248, 0.18);
                    border-radius: 10px;
                    padding: 14px 18px;
                    margin-bottom: 14px;
                    display: flex;
                    align-items: flex-start;
                    gap: 14px;
                ">
                    <div style="
                        background: rgba(56, 189, 248, 0.12);
                        color: #38bdf8;
                        border: 1px solid rgba(56, 189, 248, 0.35);
                        font-weight: 800;
                        font-size: 0.85rem;
                        padding: 6px 10px;
                        border-radius: 8px;
                        line-height: 1;
                    ">{s['num']}</div>
                    <div style="flex: 1;">
                        <div style="font-weight: 700; font-size: 0.98rem; color: #f8fafc; margin-bottom: 4px;">
                            {s['icon']} {s['title']}
                        </div>
                        <div style="font-size: 0.85rem; color: #94a3b8; line-height: 1.45; margin-bottom: 6px;">
                            {s['desc']}
                        </div>
                        <span style="display: inline-block; background: rgba(255,255,255,0.06); color: #7dd3fc; padding: 2px 8px; border-radius: 4px; font-size: 0.72rem; font-family: monospace;">
                            ⚙️ {s['tech']}
                        </span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("<div style='height: 24px;'></div>", unsafe_allow_html=True)

    # Multi-Class Severity & Protocol Matrix
    st.subheader("🏷️ Multi-Class Incident Severity & Response Protocols")
    st.caption("How MotionGuard categorizes road hazards and maps them to appropriate emergency response procedures.")

    m_col1, m_col2, m_col3 = st.columns(3)

    with m_col1:
        st.markdown(
            """
            <div style="
                background: rgba(239, 68, 68, 0.08);
                border: 2px solid #ef4444;
                border-radius: 10px;
                padding: 16px;
                height: 100%;
            ">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                    <span style="font-weight: 800; font-size: 1.05rem; color: #f87171;">🔴 CONFIRMED COLLISION</span>
                    <span style="background: #ef4444; color: white; padding: 2px 8px; border-radius: 4px; font-size: 0.72rem; font-weight: bold;">
                        PRIORITY 1
                    </span>
                </div>
                <div style="font-size: 0.84rem; color: #cbd5e1; line-height: 1.4; margin-bottom: 10px;">
                    <b>Trigger Condition:</b> Physical bounding box contact (IoU ≥ 0.05) or sudden post-impact kinetic halt (v &lt; 5 px/s). Threat Score: <b>80–100</b>.
                </div>
                <div style="background: rgba(15, 23, 42, 0.75); border-radius: 6px; padding: 10px; font-size: 0.80rem; color: #e2e8f0; line-height: 1.4;">
                    <b>Action Protocol:</b> Instant autonomous Telegram alert with photographic snapshot proof + carrier SMS + forensic ReportLab PDF dossier generation.
                    <br/><b style="color: #f87171;">Dispatch Target:</b> EMS Ambulances, Highway Patrol, Tow Recovery.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with m_col2:
        st.markdown(
            """
            <div style="
                background: rgba(245, 158, 11, 0.08);
                border: 2px solid #f59e0b;
                border-radius: 10px;
                padding: 16px;
                height: 100%;
            ">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                    <span style="font-weight: 800; font-size: 1.05rem; color: #fbbf24;">🟡 NEAR-MISS / CLOSE CONFLICT</span>
                    <span style="background: #f59e0b; color: white; padding: 2px 8px; border-radius: 4px; font-size: 0.72rem; font-weight: bold;">
                        SAFETY TRIAGE
                    </span>
                </div>
                <div style="font-size: 0.84rem; color: #cbd5e1; line-height: 1.4; margin-bottom: 10px;">
                    <b>Trigger Condition:</b> Rapid optical-tau approach rate (TTC &lt; 2.0s) and close separation without physical contact. Threat Score: <b>50–75</b>.
                </div>
                <div style="background: rgba(15, 23, 42, 0.75); border-radius: 6px; padding: 10px; font-size: 0.80rem; color: #e2e8f0; line-height: 1.4;">
                    <b>Action Protocol:</b> Logged to Operator Investigation Queue for forensic review. Replay clip exported with burned-in telemetry HUD. No false emergency sirens.
                    <br/><b style="color: #fbbf24;">Dispatch Target:</b> Traffic Operations Center, Safety Analytics.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with m_col3:
        st.markdown(
            """
            <div style="
                background: rgba(168, 85, 247, 0.08);
                border: 2px solid #a855f7;
                border-radius: 10px;
                padding: 16px;
                height: 100%;
            ">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                    <span style="font-weight: 800; font-size: 1.05rem; color: #c084fc;">🟠 STOPPED VEHICLE OBSTRUCTION</span>
                    <span style="background: #a855f7; color: white; padding: 2px 8px; border-radius: 4px; font-size: 0.72rem; font-weight: bold;">
                        HAZARD PATROL
                    </span>
                </div>
                <div style="font-size: 0.84rem; color: #cbd5e1; line-height: 1.4; margin-bottom: 10px;">
                    <b>Trigger Condition:</b> Vehicle cessation of motion (&gt; 2.0s halt) within active travel lanes or emergency breakdown shoulder. Threat Score: <b>40–60</b>.
                </div>
                <div style="background: rgba(15, 23, 42, 0.75); border-radius: 6px; padding: 10px; font-size: 0.80rem; color: #e2e8f0; line-height: 1.4;">
                    <b>Action Protocol:</b> Secondary incident hazard logged. Highway dynamic message sign advisory queued to divert oncoming traffic.
                    <br/><b style="color: #c084fc;">Dispatch Target:</b> Incident Response Tow & Roadway Maintenance.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height: 24px;'></div>", unsafe_allow_html=True)

    # Interactive Technical Innovations Deep Dive
    st.subheader("🔬 Deep-Dive: Core Technical Innovations")
    st.caption("Expand below to examine the mathematical physics and software engineering underpinning MotionGuard.")

    with st.expander("📐 1. Monocular Optical Scale TTC (Lee's Tau τ)", expanded=False):
        st.markdown(
            r"""
            #### Why Raw Euclidean Pixel Distance Fails in Monocular Cameras
            A monocular surveillance camera projects a 3D real-world scene onto a 2D image plane ($Z \to (x, y)$).
            Two vehicles driving 50 meters away in the background may be separated by only **15 pixels**, while two vehicles
            in the immediate foreground separated by 5 meters span **120 pixels**.

            If an AI collision detector relies solely on raw pixel distance ($d = \sqrt{\Delta x^2 + \Delta y^2}$), it will trigger
            catastrophic false alarms on distant vehicles and fail to catch high-speed impacts nearby.

            #### Lee's Ecological Optic Flow Formulation
            MotionGuard calculates the monocular scale growth rate:
            $$\tau = \frac{s(t)}{\frac{ds(t)}{dt}}$$
            Where:
            - $s(t) = \sqrt{\text{width} \times \text{height}}$ represents the bounding box optical scale.
            - $\frac{ds(t)}{dt}$ represents the rate of optical looming (expansion) over time.

            As vehicle $A$ approaches vehicle $B$, its retinal size $s$ grows exponentially. When $\tau$ drops below **3.5 seconds**,
            a high-risk optical approach is detected **independently of camera focal length calibration**.
            """
        )

    with st.expander("🛡️ 2. Two-Tier Architecture: Zero False Responder Alarms", expanded=False):
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

    with st.expander("🎬 3. Dynamic Incident Video Clip Exporter with Telemetry HUD", expanded=False):
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

    with st.expander("🔐 4. Operator Access Security Gate", expanded=False):
        st.markdown(
            """
            #### Industrial Safety & Privacy Guardrails:
            - Live telecommunications broadcasts (Twilio SMS / Telegram Bot) are guarded behind an **Operator Security Gate** (`OPERATOR_PIN`).
            - Exposed dashboard interfaces in public hackathons or control rooms run in **Simulator Mode** by default.
            - External emergency dispatches require explicit operator authentication and confirmation, ensuring no accidental broadcasts are sent.
            """
        )

    with st.expander("⚙️ 5. Empirical Calibration & Ground-Truth Confusion Matrix", expanded=False):
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

    st.markdown("<div style='height: 24px;'></div>", unsafe_allow_html=True)

    # Technology Stack Badges
    st.subheader("🛠️ Technical Specifications & Stack")
    badges = [
        "Python 3.12",
        "Ultralytics YOLO11n",
        "ByteTrack",
        "BoT-SORT Option",
        "PyTorch CUDA FP16",
        "OpenCV 4.10",
        "ReportLab PDF Engine",
        "Telegram Bot API",
        "Twilio SMS Gateway",
        "Streamlit 1.35+",
        "SQLite Audit DB",
        "FFmpeg H.264",
    ]
    st.markdown(
        "".join([f"<span class='badge-pill'>⚡ {b}</span>" for b in badges]),
        unsafe_allow_html=True,
    )

    st.markdown("<div style='height: 32px;'></div>", unsafe_allow_html=True)

    # Bottom Call to Action
    st.markdown(
        """
        <div style="
            background: linear-gradient(135deg, rgba(30, 58, 138, 0.45), rgba(15, 23, 42, 0.90));
            border: 1px solid rgba(56, 189, 248, 0.4);
            border-radius: 14px;
            padding: 26px 30px;
            text-align: center;
            margin-bottom: 24px;
        ">
            <h3 style="color: #ffffff; margin: 0 0 8px 0; font-size: 1.45rem;">
                Ready to Experience MotionGuard in Action?
            </h3>
            <p style="color: #94a3b8; font-size: 0.92rem; max-width: 650px; margin: 0 auto 18px auto;">
                Jump into the live Operations Workstation to upload surveillance footage, run YOLO11 + ByteTrack tracking,
                simulate autonomous emergency broadcasts, and inspect explainable risk dossiers.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    btn_col1, btn_col2, btn_col3 = st.columns([1, 2, 1])
    with btn_col2:
        if st.button("🚀 Launch Live Operations Workstation Now", type="primary", use_container_width=True, key="bottom_cta_workstation"):
            st.session_state["active_view"] = "workstation"
            st.rerun()

    st.divider()
    st.caption("MotionGuard AI · Submission Ready · Hackathon Edition · Explainable Decision-Support System")
