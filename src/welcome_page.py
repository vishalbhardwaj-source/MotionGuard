import streamlit as st
from src.ui_icons import get_svg_icon


def render_welcome_page():
    """
    Renders the Welcome to MotionGuard landing experience with Tactical Mission Control
    aesthetics, cybernetic HUD elements, uniform stroke SVG iconography, and responsive portals.
    Adheres to Impeccable and UI/UX Pro Max guidelines.
    """
    # Top Status Bar
    status_col1, status_col2 = st.columns([2, 1])
    with status_col1:
        st.html(
            f"""
            <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 6px;">
                <span style="display: inline-flex; align-items: center; justify-content: center; width: 32px; height: 32px; background: rgba(56, 189, 248, 0.12); border: 1px solid rgba(56, 189, 248, 0.3); border-radius: 8px;">
                    {get_svg_icon("shield", size=20, color="#38bdf8")}
                </span>
                <span style="font-size: 1.35rem; font-weight: 800; color: #ffffff; letter-spacing: -0.02em;">MotionGuard</span>
                <span style="background: rgba(56, 189, 248, 0.12); border: 1px solid rgba(56, 189, 248, 0.35); color: #38bdf8; padding: 2px 10px; border-radius: 999px; font-size: 0.72rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; font-family: 'JetBrains Mono', monospace;">
                    v2.5 · Autonomous Edge AI
                </span>
            </div>
            """
        )
    with status_col2:
        top_btn1, top_btn2 = st.columns(2)
        with top_btn1:
            if st.button("Architecture", use_container_width=True, key="w_top_arch_btn"):
                st.session_state["active_view"] = "overview"
                st.rerun()
        with top_btn2:
            if st.button("Workstation", type="primary", use_container_width=True, key="w_top_workstation_btn"):
                st.session_state["active_view"] = "workstation"
                st.rerun()

    # Tactical Mission Control Welcome Hero with Radar Animation & Cybernetic HUD
    st.html(
        f"""
        <style>
        @keyframes radar-pulse {{
            0% {{ transform: scale(0.96); opacity: 0.9; }}
            50% {{ transform: scale(1.04); opacity: 0.45; }}
            100% {{ transform: scale(0.96); opacity: 0.9; }}
        }}
        @keyframes scan-sweep {{
            0% {{ transform: rotate(0deg); }}
            100% {{ transform: rotate(360deg); }}
        }}
        .welcome-hero-card {{
            background: radial-gradient(circle at 10% 15%, rgba(14, 116, 144, 0.32) 0%, rgba(11, 15, 25, 0.96) 75%),
                        linear-gradient(135deg, rgba(15, 23, 42, 0.9), rgba(8, 12, 22, 0.98));
            border: 1px solid rgba(56, 189, 248, 0.35);
            border-radius: 16px;
            padding: 36px 36px 32px 36px;
            margin-bottom: 24px;
            box-shadow: 0 16px 40px rgba(0, 0, 0, 0.6);
            position: relative;
            overflow: hidden;
        }}
        .welcome-hero-card::after {{
            content: '';
            position: absolute;
            top: 0; left: 0; right: 0; height: 2px;
            background: linear-gradient(90deg, #38bdf8 0%, #818cf8 35%, #10b981 70%, #ef4444 100%);
        }}
        .portal-card {{
            background: linear-gradient(145deg, rgba(17, 24, 39, 0.75), rgba(11, 15, 25, 0.92));
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 14px;
            padding: 24px;
            height: 100%;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            transition: transform 0.22s ease, border-color 0.22s ease, box-shadow 0.22s ease;
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.35);
            position: relative;
            overflow: hidden;
        }}
        .portal-card:hover {{
            border-color: rgba(56, 189, 248, 0.45);
            transform: translateY(-3px);
            box-shadow: 0 12px 32px rgba(0, 0, 0, 0.5), 0 0 20px rgba(56, 189, 248, 0.12);
        }}
        .portal-card::before {{
            content: '';
            position: absolute;
            top: 0; left: 0; right: 0; height: 1px;
            background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
        }}
        .radar-beacon {{
            display: inline-block;
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #10b981;
            box-shadow: 0 0 10px #10b981;
            margin-right: 8px;
            animation: radar-pulse 2s infinite ease-in-out;
        }}
        .radar-scope {{
            position: relative;
            width: 90px;
            height: 90px;
            border-radius: 50%;
            border: 1px solid rgba(56, 189, 248, 0.35);
            background: radial-gradient(circle, rgba(56, 189, 248, 0.08) 0%, rgba(15, 23, 42, 0.6) 80%);
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: inset 0 0 16px rgba(56, 189, 248, 0.12);
        }}
        .radar-sweep {{
            position: absolute;
            top: 0; left: 0; right: 0; bottom: 0;
            border-radius: 50%;
            background: conic-gradient(from 0deg, rgba(56, 189, 248, 0.4) 0deg, transparent 65deg, transparent 360deg);
            animation: scan-sweep 3.5s linear infinite;
        }}
        .radar-crosshair {{
            position: absolute;
            width: 100%; height: 1px;
            background: rgba(56, 189, 248, 0.2);
        }}
        .radar-crosshair.vert {{
            width: 1px; height: 100%;
        }}
        </style>
        <div class="welcome-hero-card">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 24px;">
                <div style="flex: 1; min-width: 320px;">
                    <div style="display: inline-flex; align-items: center; background: rgba(56, 189, 248, 0.1); border: 1px solid rgba(56, 189, 248, 0.35); padding: 4px 14px; border-radius: 999px; font-size: 0.74rem; font-weight: 700; color: #38bdf8; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 14px; font-family: 'JetBrains Mono', monospace;">
                        <span class="radar-beacon"></span> LIVE AUTONOMOUS SURVEILLANCE ARMED
                    </div>
                    <h1 style="font-size: clamp(2.1rem, 3.6vw, 3.2rem); font-weight: 800; letter-spacing: -0.03em; color: #ffffff; margin: 0 0 14px 0; line-height: 1.15;">
                        Welcome to MotionGuard
                    </h1>
                    <p style="font-size: clamp(0.98rem, 1.3vw, 1.18rem); color: #cbd5e1; max-width: 840px; line-height: 1.6; margin: 0 0 22px 0;">
                        The Autonomous Edge AI system transforming traffic CCTV video into instant, explainable road-safety intelligence.
                        Pinpoints high-speed highway collisions in <strong style="color: #f8fafc;">sub-second time (0.30s)</strong>, eliminates alert fatigue with
                        <strong style="color: #f8fafc;">0.0 false emergency alarms on normal traffic</strong>, and autonomously broadcasts <strong style="color: #f8fafc;">verified photographic proof</strong> to first responders.
                    </p>
                    <div style="display: flex; gap: 10px; flex-wrap: wrap; margin-bottom: 4px;">
                        <span style="display: inline-flex; align-items: center; gap: 6px; background: rgba(15, 23, 42, 0.8); border: 1px solid rgba(56, 189, 248, 0.28); color: #7dd3fc; padding: 5px 12px; border-radius: 6px; font-size: 0.78rem; font-weight: 600; font-family: 'JetBrains Mono', monospace;">
                            {get_svg_icon("cpu", size=14, color="#38bdf8")} YOLO11n + ByteTrack CUDA FP16
                        </span>
                        <span style="display: inline-flex; align-items: center; gap: 6px; background: rgba(15, 23, 42, 0.8); border: 1px solid rgba(16, 185, 129, 0.28); color: #6ee7b7; padding: 5px 12px; border-radius: 6px; font-size: 0.78rem; font-weight: 600; font-family: 'JetBrains Mono', monospace;">
                            {get_svg_icon("activity", size=14, color="#10b981")} Optical Tau (τ) Physics Kinematics
                        </span>
                        <span style="display: inline-flex; align-items: center; gap: 6px; background: rgba(15, 23, 42, 0.8); border: 1px solid rgba(239, 68, 68, 0.28); color: #fca5a5; padding: 5px 12px; border-radius: 6px; font-size: 0.78rem; font-weight: 600; font-family: 'JetBrains Mono', monospace;">
                            {get_svg_icon("send", size=14, color="#ef4444")} Telegram Photo-Proof Dispatch
                        </span>
                        <span style="display: inline-flex; align-items: center; gap: 6px; background: rgba(15, 23, 42, 0.8); border: 1px solid rgba(129, 140, 248, 0.28); color: #c7d2fe; padding: 5px 12px; border-radius: 6px; font-size: 0.78rem; font-weight: 600; font-family: 'JetBrains Mono', monospace;">
                            {get_svg_icon("file-text", size=14, color="#818cf8")} ReportLab Forensic PDF Dossiers
                        </span>
                    </div>
                </div>
                <div style="display: flex; flex-direction: column; align-items: center; gap: 10px;">
                    <div class="radar-scope">
                        <div class="radar-crosshair"></div>
                        <div class="radar-crosshair vert"></div>
                        <div class="radar-sweep"></div>
                        <div style="width: 8px; height: 8px; border-radius: 50%; background: #38bdf8; box-shadow: 0 0 10px #38bdf8;"></div>
                    </div>
                    <div style="text-align: center;">
                        <span style="display: block; font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; color: #38bdf8; font-weight: 700; letter-spacing: 0.08em;">
                            OPTICAL HUD
                        </span>
                        <span style="font-family: 'JetBrains Mono', monospace; font-size: 0.68rem; color: #64748b;">
                            60 FPS · 1080P
                        </span>
                    </div>
                </div>
            </div>
        </div>
        """
    )

    # Tactical Metric Ribbon
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.html(
            f"""
            <div class="kpi-card">
                <div class="kpi-label">
                    {get_svg_icon("cpu", size=14, color="#38bdf8")} Neural Inference
                </div>
                <div class="kpi-value">~18<span style="font-size: 0.95rem; font-weight: 600; color: #94a3b8; font-family: 'JetBrains Mono', monospace;">ms</span></div>
                <div class="kpi-caption">YOLO11n + ByteTrack CUDA FP16</div>
            </div>
            """
        )
    with m2:
        st.html(
            f"""
            <div class="kpi-card">
                <div class="kpi-label" style="color: #34d399;">
                    {get_svg_icon("shield", size=14, color="#34d399")} False Responder Alarms
                </div>
                <div class="kpi-value" style="color: #34d399;">0.0<span style="font-size: 0.95rem; font-weight: 600; color: #94a3b8; font-family: 'JetBrains Mono', monospace;">/hr</span></div>
                <div class="kpi-caption">Zero nuisance sirens on normal traffic</div>
            </div>
            """
        )
    with m3:
        st.html(
            f"""
            <div class="kpi-card">
                <div class="kpi-label" style="color: #f87171;">
                    {get_svg_icon("zap", size=14, color="#f87171")} Impact Detection Onset
                </div>
                <div class="kpi-value" style="color: #f87171;">0.30<span style="font-size: 0.95rem; font-weight: 600; color: #94a3b8; font-family: 'JetBrains Mono', monospace;">s</span></div>
                <div class="kpi-caption">Autonomous triage within 300ms of collision</div>
            </div>
            """
        )
    with m4:
        st.html(
            f"""
            <div class="kpi-card">
                <div class="kpi-label" style="color: #c084fc;">
                    {get_svg_icon("video", size=14, color="#c084fc")} Telemetry Video HUD
                </div>
                <div class="kpi-value" style="color: #c084fc;">±2.5<span style="font-size: 0.95rem; font-weight: 600; color: #94a3b8; font-family: 'JetBrains Mono', monospace;">s</span></div>
                <div class="kpi-caption">Dynamic H.264 incident clip export</div>
            </div>
            """
        )

    st.html("<div style='height: 20px;'></div>")

    # Two Main Gateways / Launch Portal Cards
    st.markdown("### Launch Operations")
    st.caption("Select your mission profile to proceed:")

    launch_col1, launch_col2 = st.columns(2)

    with launch_col1:
        st.html(
            f"""
            <div class="portal-card">
                <div>
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px;">
                        <span style="display: inline-flex; align-items: center; justify-content: center; width: 36px; height: 36px; background: rgba(239, 68, 68, 0.12); border: 1px solid rgba(239, 68, 68, 0.35); border-radius: 8px;">
                            {get_svg_icon("shield-alert", size=20, color="#ef4444")}
                        </span>
                        <span style="background: rgba(239, 68, 68, 0.14); border: 1px solid rgba(239, 68, 68, 0.35); color: #f87171; padding: 3px 10px; border-radius: 999px; font-size: 0.72rem; font-weight: 700; text-transform: uppercase; font-family: 'JetBrains Mono', monospace;">
                            TACTICAL CONSOLE
                        </span>
                    </div>
                    <h3 style="color: #ffffff; margin: 0 0 10px 0; font-size: 1.30rem; font-weight: 800;">
                        Live Operations Workstation
                    </h3>
                    <p style="color: #cbd5e1; font-size: 0.88rem; line-height: 1.6; margin: 0 0 20px 0;">
                        Experience the complete 6-tab interactive command center: quick-load verified highway collision footage, run the autonomous incident pipeline, review optical tau (τ) kinematics, dispatch live Telegram alerts with photographic evidence, and generate PDF dossiers.
                    </p>
                </div>
            </div>
            """
        )
        if st.button("Enter Live Operations Workstation →", type="primary", use_container_width=True, key="w_launch_workstation"):
            st.session_state["active_view"] = "workstation"
            st.rerun()

    with launch_col2:
        st.html(
            f"""
            <div class="portal-card">
                <div>
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px;">
                        <span style="display: inline-flex; align-items: center; justify-content: center; width: 36px; height: 36px; background: rgba(56, 189, 248, 0.12); border: 1px solid rgba(56, 189, 248, 0.35); border-radius: 8px;">
                            {get_svg_icon("layers", size=20, color="#38bdf8")}
                        </span>
                        <span style="background: rgba(56, 189, 248, 0.14); border: 1px solid rgba(56, 189, 248, 0.35); color: #38bdf8; padding: 3px 10px; border-radius: 999px; font-size: 0.72rem; font-weight: 700; text-transform: uppercase; font-family: 'JetBrains Mono', monospace;">
                            SPECIFICATION
                        </span>
                    </div>
                    <h3 style="color: #ffffff; margin: 0 0 10px 0; font-size: 1.30rem; font-weight: 800;">
                        System Architecture & Physics
                    </h3>
                    <p style="color: #cbd5e1; font-size: 0.88rem; line-height: 1.6; margin: 0 0 20px 0;">
                        Examine the mathematical derivation of Lee's Optical-Tau (τ) Time-To-Collision, scale-normalized distance (d<sub>norm</sub>), polygon geofencing rules, empirical confusion matrix evaluation, and zero-dependency Prune AI Gateway integration.
                    </p>
                </div>
            </div>
            """
        )
        if st.button("Explore System Architecture & Math →", use_container_width=True, key="w_launch_overview"):
            st.session_state["active_view"] = "overview"
            st.rerun()

    st.html("<div style='height: 20px;'></div>")
    st.divider()
    st.caption("MotionGuard AI · Autonomous Edge AI Road-Safety Workstation · Mission Control Edition")
