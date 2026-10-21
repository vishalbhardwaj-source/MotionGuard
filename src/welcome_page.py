import streamlit as st


def render_welcome_page():
    """
    Renders the Welcome to MotionGuard landing experience with high-tech visuals,
    cybernetic glassmorphism, animated radar HUD elements, and clear launch portals.
    """
    # Top Status Bar
    status_col1, status_col2 = st.columns([2, 1])
    with status_col1:
        st.markdown(
            """
            <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 4px;">
                <span style="font-size: 1.6rem; filter: drop-shadow(0 0 8px rgba(56, 189, 248, 0.6));">🚦</span>
                <span style="font-size: 1.25rem; font-weight: 850; color: #ffffff; letter-spacing: -0.02em;">MotionGuard</span>
                <span style="background: rgba(56, 189, 248, 0.15); border: 1px solid rgba(56, 189, 248, 0.4); color: #38bdf8; padding: 2px 10px; border-radius: 999px; font-size: 0.74rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em;">
                    v2.5 · Autonomous Edge AI
                </span>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with status_col2:
        top_btn1, top_btn2 = st.columns(2)
        with top_btn1:
            if st.button("📖 Architecture", use_container_width=True, key="w_top_arch_btn"):
                st.session_state["active_view"] = "overview"
                st.rerun()
        with top_btn2:
            if st.button("🚀 Workstation", type="primary", use_container_width=True, key="w_top_workstation_btn"):
                st.session_state["active_view"] = "workstation"
                st.rerun()

    # Grand Futuristic Welcome Hero with Radar Animation & Cybernetic Aesthetics
    st.markdown(
        """
        <style>
        @keyframes radar-pulse {
            0% { transform: scale(0.95); opacity: 0.85; }
            50% { transform: scale(1.05); opacity: 0.4; }
            100% { transform: scale(0.95); opacity: 0.85; }
        }
        @keyframes scan-sweep {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        .welcome-hero-card {
            background: radial-gradient(circle at 10% 15%, rgba(14, 116, 144, 0.45) 0%, rgba(15, 23, 42, 0.95) 75%),
                        linear-gradient(135deg, rgba(30, 41, 59, 0.8), rgba(2, 6, 23, 0.95));
            border: 1px solid rgba(56, 189, 248, 0.45);
            border-radius: 20px;
            padding: 40px 36px 36px 36px;
            margin-bottom: 26px;
            box-shadow: 0 16px 48px rgba(0, 0, 0, 0.55), 0 0 30px rgba(56, 189, 248, 0.15);
            position: relative;
            overflow: hidden;
        }
        .welcome-hero-card::before {
            content: '';
            position: absolute;
            top: 0; left: 0; right: 0; height: 3px;
            background: linear-gradient(90deg, #38bdf8, #818cf8, #34d399, #ef4444);
        }
        .portal-card {
            background: linear-gradient(145deg, rgba(30, 41, 59, 0.65), rgba(15, 23, 42, 0.85));
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 14px;
            padding: 22px 24px;
            height: 100%;
            transition: all 0.25s ease;
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
        }
        .portal-card:hover {
            border-color: rgba(56, 189, 248, 0.5);
            transform: translateY(-4px);
            box-shadow: 0 12px 32px rgba(56, 189, 248, 0.2);
        }
        .radar-beacon {
            display: inline-block;
            width: 10px;
            height: 10px;
            border-radius: 50%;
            background: #34d399;
            box-shadow: 0 0 12px #34d399;
            margin-right: 6px;
            animation: radar-pulse 2s infinite ease-in-out;
        }
        </style>

        <div class="welcome-hero-card">
            <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 16px;">
                <div style="flex: 1; min-width: 300px;">
                    <div style="display: inline-flex; align-items: center; background: rgba(56, 189, 248, 0.12); border: 1px solid rgba(56, 189, 248, 0.4); padding: 4px 14px; border-radius: 999px; font-size: 0.76rem; font-weight: 700; color: #38bdf8; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 14px;">
                        <span class="radar-beacon"></span> LIVE AUTONOMOUS SURVEILLANCE ARMED
                    </div>
                    <h1 style="font-size: clamp(2.2rem, 3.8vw, 3.4rem); font-weight: 900; letter-spacing: -0.03em; color: #ffffff; margin: 0 0 14px 0; line-height: 1.12;">
                        Welcome to <span style="background: linear-gradient(135deg, #38bdf8, #818cf8, #f87171); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">MotionGuard</span>
                    </h1>
                    <p style="font-size: clamp(1.02rem, 1.35vw, 1.22rem); color: #cbd5e1; max-width: 820px; line-height: 1.55; margin: 0 0 20px 0;">
                        The Autonomous Edge AI system that transforms CCTV camera streams into instant road-safety intelligence.
                        Pinpointing high-speed highway collisions in <b>sub-second time (0.30s)</b>, eliminating alert fatigue with
                        <b>zero false alarms on normal traffic</b>, and autonomously broadcasting <b>verified photographic proof</b> to first responders.
                    </p>
                    <div style="display: flex; gap: 12px; flex-wrap: wrap; margin-bottom: 8px;">
                        <span style="background: rgba(15, 23, 42, 0.7); border: 1px solid rgba(56, 189, 248, 0.25); color: #7dd3fc; padding: 4px 12px; border-radius: 6px; font-size: 0.80rem; font-weight: 600;">
                            ⚡ YOLO11n + ByteTrack CUDA FP16
                        </span>
                        <span style="background: rgba(15, 23, 42, 0.7); border: 1px solid rgba(52, 211, 153, 0.25); color: #6ee7b7; padding: 4px 12px; border-radius: 6px; font-size: 0.80rem; font-weight: 600;">
                            📐 Monocular Optical Tau (τ) Physics
                        </span>
                        <span style="background: rgba(15, 23, 42, 0.7); border: 1px solid rgba(239, 68, 68, 0.25); color: #fca5a5; padding: 4px 12px; border-radius: 6px; font-size: 0.80rem; font-weight: 600;">
                            📱 Telegram Photo-Proof Dispatch
                        </span>
                        <span style="background: rgba(15, 23, 42, 0.7); border: 1px solid rgba(168, 85, 247, 0.25); color: #d8b4fe; padding: 4px 12px; border-radius: 6px; font-size: 0.80rem; font-weight: 600;">
                            📄 ReportLab Forensic PDF Dossiers
                        </span>
                    </div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Two Main Gateways / Launch Portal Cards
    st.markdown("### 🚀 Choose Your Experience")
    st.caption("Select how you would like to explore MotionGuard:")

    launch_col1, launch_col2 = st.columns(2)

    with launch_col1:
        st.markdown(
            """
            <div class="portal-card" style="border-left: 4px solid #ef4444;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                    <span style="font-size: 1.8rem;">🚦</span>
                    <span style="background: rgba(239, 68, 68, 0.15); border: 1px solid rgba(239, 68, 68, 0.4); color: #f87171; padding: 3px 10px; border-radius: 999px; font-size: 0.72rem; font-weight: bold; text-transform: uppercase;">
                        RECOMMENDED FOR JUDGES
                    </span>
                </div>
                <h3 style="color: #ffffff; margin: 0 0 8px 0; font-size: 1.35rem;">
                    Live Operations Workstation
                </h3>
                <p style="color: #cbd5e1; font-size: 0.88rem; line-height: 1.5; margin: 0 0 16px 0;">
                    Experience the complete 6-tab interactive command center. Quick-load the verified 5.5s highway crash clip, run the 1-click autonomous pipeline, view instant Telegram alerts on your phone, and download the forensic PDF dossier.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("🚀 Enter Live Operations Workstation →", type="primary", use_container_width=True, key="w_launch_workstation"):
            st.session_state["active_view"] = "workstation"
            st.rerun()

    with launch_col2:
        st.markdown(
            """
            <div class="portal-card" style="border-left: 4px solid #38bdf8;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                    <span style="font-size: 1.8rem;">📖</span>
                    <span style="background: rgba(56, 189, 248, 0.15); border: 1px solid rgba(56, 189, 248, 0.4); color: #38bdf8; padding: 3px 10px; border-radius: 999px; font-size: 0.72rem; font-weight: bold; text-transform: uppercase;">
                        TECHNICAL ARCHITECTURE
                    </span>
                </div>
                <h3 style="color: #ffffff; margin: 0 0 8px 0; font-size: 1.35rem;">
                    System Architecture & Mission
                </h3>
                <p style="color: #cbd5e1; font-size: 0.88rem; line-height: 1.5; margin: 0 0 16px 0;">
                    Examine the engineering deep-dive: the mathematical derivation of Lee's Optical-Tau (τ), scale-normalized distance (d<sub>norm</sub>), two-tier false alarm mitigation, and empirical ground-truth benchmark metrics.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("📖 Explore System Architecture & Math →", use_container_width=True, key="w_launch_overview"):
            st.session_state["active_view"] = "overview"
            st.rerun()

    st.markdown("<div style='height: 18px;'></div>", unsafe_allow_html=True)
    st.divider()
    st.caption("MotionGuard AI · Autonomous Edge AI Road-Safety Workstation · Submission Ready")
