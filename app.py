
import json
import os
import subprocess
from pathlib import Path

import streamlit as st
from ultralytics import YOLO

from src.risk_engine import assess_risk
from src.trajectory_analysis import analyze_trajectories
from src.reporting import create_incident_report
from src.pdf_report import create_interaction_pdf
from src.video_processor import (
    track_video,
    save_frame,
    inspect_video,
    create_event_clip,
)
from src.alert_dispatcher import (
    format_emergency_sms,
    dispatch_sms,
    log_sms_dispatch,
)

st.set_page_config(
    page_title="MotionGuard — Road Safety & Incident Investigation",
    page_icon="🚦",
    layout="wide",
)


OUTPUT_DIR = Path("outputs")
EVIDENCE_DIR = OUTPUT_DIR / "evidence"
INCIDENT_LOG = OUTPUT_DIR / "incidents.jsonl"
NOTIFICATION_LOG = OUTPUT_DIR / "authority_notifications.jsonl"
REVIEW_LOG = OUTPUT_DIR / "interaction_reviews.jsonl"
SMS_LOG = OUTPUT_DIR / "sms_dispatches.jsonl"
VIDEO_PATH = Path("data/videos/normal.mp4")
EVIDENCE_PATH = EVIDENCE_DIR / "test_frame.png"
MODEL_PATH = Path("yolo11n.pt")


def read_sms_log():
    dispatches = []
    if SMS_LOG.exists():
        with SMS_LOG.open("r", encoding="utf-8") as file:
            for line in file:
                try:
                    dispatches.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return dispatches


@st.cache_resource
def load_model():
    return YOLO(str(MODEL_PATH))


def read_reports():
    reports = []
    if INCIDENT_LOG.exists():
        with INCIDENT_LOG.open("r", encoding="utf-8") as file:
            for line in file:
                try:
                    reports.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return reports



def read_notification_log():
    notifications = []

    if NOTIFICATION_LOG.exists():
        with NOTIFICATION_LOG.open("r", encoding="utf-8") as file:
            for line in file:
                try:
                    notifications.append(json.loads(line))
                except json.JSONDecodeError:
                    continue

    return notifications




def read_review_log():
    reviews = []

    if REVIEW_LOG.exists():
        with REVIEW_LOG.open("r", encoding="utf-8") as file:
            for line in file:
                try:
                    reviews.append(json.loads(line))
                except json.JSONDecodeError:
                    continue

    return reviews




def record_review(event_id, decision, reviewed_by="Demo operator"):
    REVIEW_LOG.parent.mkdir(parents=True, exist_ok=True)

    review = {
        "event_id": event_id,
        "decision": decision,
        "reviewed_by": reviewed_by,
        "reviewed_at": __import__("datetime").datetime.now().astimezone().isoformat(),
    }

    with REVIEW_LOG.open("a", encoding="utf-8") as file:
        file.write(json.dumps(review) + "\n")

    return review





def record_notification(event, authority, submitted_by="Demo operator"):
    NOTIFICATION_LOG.parent.mkdir(parents=True, exist_ok=True)

    notification = {
        "notification_id": f"MG-NOTICE-{event.get('event_id', 'UNKNOWN')}",
        "event_id": event.get("event_id", "Unknown event"),
        "authority": authority,
        "submitted_by": submitted_by,
        "submitted_at": __import__("datetime").datetime.now().astimezone().isoformat(),
        "status": "SUBMITTED_SIMULATED",
        "report": {
            "track_ids": event.get("track_ids", []),
            "timestamp_seconds": event.get("evidence_timestamp_seconds"),
            "finding": event.get("finding", "Not specified"),
            "confidence": event.get("confidence", "Not specified"),
            "minimum_distance_px": event.get("minimum_distance_px"),
            "peak_closing_speed_px_per_second": event.get(
                "peak_closing_speed_px_per_second"
            ),
            "limitations": event.get("limitations", []),
        },
    }

    with NOTIFICATION_LOG.open("a", encoding="utf-8") as file:
        file.write(json.dumps(notification) + "\n")

    return notification



INTERACTION_EVENTS_PATH = OUTPUT_DIR / "interaction_events_test.jsonl"
INTERACTION_EVIDENCE_DIR = OUTPUT_DIR / "event_evidence_test"

def read_interaction_events():
    events = []

    if INTERACTION_EVENTS_PATH.exists():
        with INTERACTION_EVENTS_PATH.open("r", encoding="utf-8") as file:
            for line in file:
                try:
                    events.append(json.loads(line))
                except json.JSONDecodeError:
                    continue

    return events


# Inject custom CSS for sleek dashboard cards and badges
st.markdown(
    """
    <style>
    .metric-card {
        background: rgba(128, 128, 128, 0.08);
        border: 1px solid rgba(128, 128, 128, 0.2);
        border-radius: 8px;
        padding: 12px 18px;
        margin-bottom: 12px;
    }
    .badge {
        display: inline-block;
        padding: 3px 8px;
        border-radius: 4px;
        font-size: 0.8rem;
        font-weight: 600;
        letter-spacing: 0.5px;
    }
    .badge-critical { background: rgba(255, 75, 75, 0.2); color: #ff4b4b; border: 1px solid #ff4b4b; }
    .badge-high { background: rgba(255, 140, 66, 0.2); color: #ff8c42; border: 1px solid #ff8c42; }
    .badge-medium { background: rgba(245, 197, 66, 0.2); color: #f5c542; border: 1px solid #f5c542; }
    .badge-low { background: rgba(46, 204, 113, 0.2); color: #2ecc71; border: 1px solid #2ecc71; }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 8px 16px;
        border-radius: 6px;
        font-weight: 500;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("🚦 MotionGuard")
st.caption(
    "AI-Powered Road-Safety Risk Assessment & Incident Investigation | "
    "Decision-Support Prototype"
)

reports = read_reports()
critical_count = sum(1 for r in reports if r.get("threat_level") == "CRITICAL")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Logged Incidents", len(reports))
col2.metric("Critical Reviews", critical_count)
col3.metric("Video Input", "Verified (H.264)" if VIDEO_PATH.is_file() else "Missing")
col4.metric("Pipeline Mode", "Full Traceability")

st.divider()

video_tab, interaction_tab, scenario_tab, incidents_tab, authority_tab = st.tabs(
    [
        "📹 Video Analysis",
        "🔍 Interaction Investigation",
        "⚖️ Risk Scenario",
        "🚨 Incident Command",
        "📋 Authority Dossier & PDF",
    ]
)



with interaction_tab:
    st.subheader("Interaction Investigation")
    st.caption(
        "Potential road-safety interactions detected from video. "
        "These are unvalidated heuristics, not confirmed collisions."
    )

    interaction_events = read_interaction_events()

    if not interaction_events:
        st.info(
            "No interaction events found. Run the interaction-analysis "
            "pipeline to generate event records."
        )
    else:
        single_detection_events = [
            event for event in interaction_events
            if event.get("detection_count", 0) < 2
        ]
        primary_events = [
            event for event in interaction_events
            if event.get("detection_count", 0) >= 2
        ]

        metric1, metric2, metric3 = st.columns(3)
        metric1.metric("Total potential events", len(interaction_events))
        metric2.metric("Primary investigation queue", len(primary_events))
        metric3.metric("Needs review", len(single_detection_events))

        st.info(
            "Single-detection events are separated for review, not deleted. "
            "All event records remain available below."
        )

        queue_filter = st.selectbox(
            "Filter investigation queue",
            [
                "All events",
                "Primary queue (2+ detections)",
                "Needs review (fewer than 2 detections)",
            ],
        )

        if queue_filter == "Primary queue (2+ detections)":
            displayed_events = primary_events
        elif queue_filter == "Needs review (fewer than 2 detections)":
            displayed_events = single_detection_events
        else:
            displayed_events = interaction_events

        st.write(f"Showing {len(displayed_events)} events")

        sort_option = st.selectbox(
            "Sort events by",
            [
                "Earliest event",
                "Most detections",
                "Shortest image-space distance",
                "Highest closing speed",
            ],
        )

        if sort_option == "Most detections":
            displayed_events = sorted(
                displayed_events,
                key=lambda event: event.get("detection_count", 0),
                reverse=True,
            )
        elif sort_option == "Shortest image-space distance":
            displayed_events = sorted(
                displayed_events,
                key=lambda event: event.get(
                    "minimum_distance_px", float("inf")
                ),
            )
        elif sort_option == "Highest closing speed":
            displayed_events = sorted(
                displayed_events,
                key=lambda event: event.get(
                    "peak_closing_speed_px_per_second", 0
                ),
                reverse=True,
            )
        else:
            displayed_events = sorted(
                displayed_events,
                key=lambda event: event.get("start_seconds", 0),
            )

        for event in displayed_events:
            event_id = event.get("event_id", "Unknown event")
            detection_count = event.get("detection_count", 0)
            minimum_distance = event.get(
                "minimum_distance_px", float("inf")
            )
            closing_speed = event.get(
                "peak_closing_speed_px_per_second", 0
            )
            confirmation_count = event.get(
                "peak_confirmation_count", 0
            )


            review_label = (
                "NEEDS REVIEW"
                if detection_count < 2
                else "PRIMARY QUEUE"
            )


            if detection_count < 2:
                priority_label = "PRIORITY C — VERIFY EVIDENCE"
                priority_color = "gray"
                priority_reason = (
                    "Only one detection; evidence is insufficient "
                    "for a stronger assessment."
                )
            elif (
                confirmation_count >= 3
                and minimum_distance <= 15
                and closing_speed >= 25
            ):
                priority_label = "PRIORITY A — REVIEW FIRST"
                priority_color = "red"
                priority_reason = (
                    f"Very small image-space separation "
                    f"({minimum_distance:.2f} px) and high measured "
                    f"closing speed ({closing_speed:.2f} px/s)."
                )
            elif confirmation_count >= 3 and minimum_distance <= 15:
                priority_label = "PRIORITY A — REVIEW FIRST"
                priority_color = "red"
                priority_reason = (
                    f"Very small image-space separation: "
                    f"{minimum_distance:.2f} px."
                )
            elif confirmation_count >= 3 and closing_speed >= 25:
                priority_label = "PRIORITY A — REVIEW FIRST"
                priority_color = "red"
                priority_reason = (
                    f"High measured closing speed: "
                    f"{closing_speed:.2f} px/s."
                )
            else:
                priority_label = "PRIORITY B — INVESTIGATE"
                priority_color = "orange"
                priority_reason = (
                    "Repeated detections; further investigation "
                    "is recommended."
                )



            expander_title = (
                f"{event_id} · {priority_label.split(' — ')[0]} · "
                f"Time: {event.get('start_seconds', 0):.2f}s · "
                f"Tracks: {event.get('track_ids', [])} · "
                f"Min Sep: {minimum_distance:.1f}px · "
                f"{detection_count} detection(s)"
            )

            with st.expander(expander_title):
                if priority_color == "red":
                    st.error(f"{priority_label}: {priority_reason}")
                elif priority_color == "orange":
                    st.warning(f"{priority_label}: {priority_reason}")
                else:
                    st.info(f"{priority_label}: {priority_reason}")
                detail_col1, detail_col2 = st.columns(2)

                with detail_col1:
                    st.write("**Track IDs**:", event.get("track_ids", []))
                    st.write(
                        "**Duration:**",
                        f"{event.get('duration_seconds', 0):.3f} s",
                    )
                    st.write(
                        "**Minimum center distance:**",
                        f"{event.get('minimum_distance_px', 0):.2f} px",
                    )



                with detail_col2:
                    st.write(
                        "**Peak closing speed:**",
                        f"{event.get('peak_closing_speed_px_per_second', 0):.2f} px/s",
                    )
                    st.write(
                        "**Peak consecutive confirmations:**",
                        event.get("peak_confirmation_count", "N/A"),
                    )
                    st.write(
                        "**Finding:**",
                        event.get("finding", "Unknown"),
                    )
                    st.write(
                        "**Confidence:**",
                        event.get("confidence", "Unknown"),
                    )


                st.caption(
                    "Image-space measurements are not real-world distances. "
                    "A potential interaction does not establish a collision."
                )

                evidence_path = (
                    INTERACTION_EVIDENCE_DIR / f"{event_id}.jpg"
                )

                if evidence_path.exists():
                    st.image(
                        str(evidence_path),
                        caption=f"Evidence frame for {event_id}",
                        use_container_width=True,
                    )
                else:
                    st.info(
                        f"No saved evidence image is available for {event_id}."
                    )


with scenario_tab:
    st.subheader("Assess a test scenario")
    st.info(
        "Speed is supplied manually. Scores are rule-based review scores, "
        "not measured vehicle speeds or accident probabilities."
    )

    with st.form("risk_form"):
        scenario_id = st.text_input("Scenario ID", value="overspeed_demo")
        speed = st.number_input(
            "Vehicle speed (km/h)", min_value=0.0,
            max_value=400.0, value=80.0, step=5.0,
        )
        speed_limit = st.number_input(
            "Speed limit (km/h)", min_value=1.0,
            max_value=200.0, value=50.0, step=5.0,
        )
        collision_flag = st.checkbox(
            "Flag a suspected collision for urgent review"
        )
        submitted = st.form_submit_button("Assess risk", type="primary")

    if submitted:
        try:
            st.session_state["latest_risk"] = assess_risk(
                speed_kmh=speed,
                speed_limit_kmh=speed_limit,
                suspected_collision=collision_flag,
            )
            st.session_state["latest_scenario"] = (
                scenario_id.strip() or "demo"
            )
        except ValueError as error:
            st.error(str(error))

    risk = st.session_state.get("latest_risk")
    if risk:
        st.subheader("Assessment result")
        c1, c2, c3 = st.columns(3)
        c1.metric("Threat score", f'{risk["threat_score"]}/100')
        c2.metric("Threat level", risk["threat_level"])
        c3.metric(
            "Speed above limit",
            f'{risk["overspeed_ratio"] * 100:.0f}%',
        )
        for reason in risk["reasons"]:
            st.write(f"- {reason}")

        auto_sms = False
        alert_phone = "+91 98765 43210"
        if risk["event_status"] == "SUSPECTED_COLLISION" or risk["threat_level"] == "CRITICAL":
            st.error("🚨 CRITICAL COLLISION ALERT — IMMEDIATE ACTION REQUIRED")
            auto_sms = st.checkbox("📱 Automatically dispatch emergency SMS to authorities upon creating incident", value=True)
            alert_phone = st.text_input("Concerned Authority Phone Number", value="+91 98765 43210")

        if st.button("Generate incident report", type="primary"):
            if not EVIDENCE_PATH.is_file():
                st.error("Sample evidence missing: outputs/evidence/test_frame.png")
            else:
                report = create_incident_report(
                    risk_result=risk,
                    scenario_id=st.session_state["latest_scenario"],
                    timestamp_seconds=5.0,
                    evidence_image=EVIDENCE_PATH,
                    event_source=(
                        "MANUALLY_FLAGGED_SUSPECTED_COLLISION"
                        if risk["event_status"] == "SUSPECTED_COLLISION"
                        else "NO_COLLISION_EVENT"
                    ),
                )
                if auto_sms and alert_phone:
                    try:
                        sms_text = format_emergency_sms(
                            {
                                "event_id": report["incident_id"],
                                "evidence_timestamp_seconds": 5.0,
                                "track_ids": ["COLLISION-VEHICLE"],
                                "minimum_distance_px": 0.0,
                                "peak_closing_speed_px_per_second": round(risk["speed_kmh"] * 0.277, 1),
                            },
                            incident_type="CONFIRMED / FLAGGED ACCIDENT",
                        )
                        sms_res = dispatch_sms(alert_phone, sms_text)
                        log_sms_dispatch(sms_res)
                        st.success(f"📱 Emergency Text Alert Dispatched to {sms_res['recipient']} ({sms_res['channel']})!")
                    except Exception as e:
                        st.warning(f"SMS dispatch skipped or error: {e}")

                st.success(f'Report created: {report["incident_id"]}')
                st.json(report)
                st.rerun()



with incidents_tab:
    from src.reporting import update_review_status

    st.subheader("🚨 Incident Command")
    reports = read_reports()

    if not reports:
        st.info("No incident reports yet. Generate a report first.")
    else:
        total = len(reports)
        critical = sum(
            r.get("threat_level") == "CRITICAL" for r in reports
        )
        new_cases = sum(
            r.get("review_status", "NEW") == "NEW" for r in reports
        )
        under_review = sum(
            r.get("review_status", "NEW") == "UNDER REVIEW"
            for r in reports
        )

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total incidents", total)
        col2.metric("Critical reviews", critical)
        col3.metric("Awaiting review", new_cases)
        col4.metric("Under review", under_review)

        st.divider()

        filter_col, status_col = st.columns(2)

        with filter_col:
            severity_filter = st.selectbox(
                "Filter by severity",
                ["ALL", "CRITICAL", "VERY HIGH", "HIGH", "ELEVATED", "LOW"],
            )

        with status_col:
            status_filter = st.selectbox(
                "Filter by status",
                ["ALL", "NEW", "UNDER REVIEW", "RESOLVED"],
            )

      
        severity_order = {
            "CRITICAL": 0,
            "VERY HIGH": 1,
            "HIGH": 2,
            "ELEVATED": 3,
            "LOW": 4,
        }

        filtered_reports = [
            report for report in reports
            if (
                severity_filter == "ALL"
                or report.get("threat_level") == severity_filter
            )
            and (
                status_filter == "ALL"
                or report.get("review_status", "NEW") == status_filter
            )
        ]

        filtered_reports.sort(
            key=lambda report: (
                severity_order.get(
                    report.get("threat_level", "LOW"), 5
                ),
                report.get("review_status", "NEW") != "NEW",
                -float(report.get("threat_score", 0)),
                report.get("created_at_utc", ""),
            )
        )


        st.caption(
            f"Showing {len(filtered_reports)} of {total} incident reports"
        )

        for report in filtered_reports:
            incident_id = report.get("incident_id", "Unknown")
            level = report.get("threat_level", "UNKNOWN")
            score = report.get("threat_score", 0)
            current_status = report.get("review_status", "NEW")

       
            severity_colors = {
                "CRITICAL": "#ff4b4b",
                "VERY HIGH": "#ff8c42",
                "HIGH": "#f5c542",
                "ELEVATED": "#5dade2",
                "LOW": "#2ecc71",
            }
            severity_color = severity_colors.get(level, "#9e9e9e")

            st.markdown(
                f"""
                <div style="
                    border-left: 6px solid {severity_color};
                    padding: 10px 14px;
                    margin: 6px 0 10px 0;
                    background: rgba(128,128,128,0.10);
                    border-radius: 6px;
                ">
                    <div style="font-size: 1.05rem; font-weight: 700;">
                        {level} — {score}/100
                    </div>
                    <div style="font-size: 0.9rem; opacity: 0.8;">
                        Incident: {incident_id} · Status: {current_status}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            with st.expander(
                f"{incident_id} | {level} | {score}/100 | {current_status}"
            ):
                details_col, evidence_col = st.columns([1, 1])

                with details_col:
                    st.write("**Incident details**")
                    st.write(f"Scenario: {report.get('scenario_id', 'Unknown')}")
                    st.write(
                        f"Timestamp: "
                        f"{report.get('timestamp_seconds', 0)} seconds"
                    )
                    track_id = report.get("track_id")
                    vehicle_class = report.get("vehicle_class")

                    st.write(
                        f"**Tracked vehicle ID:** "
                        f"{track_id if track_id is not None else 'Unconfirmed'}"
                    )
                    st.write(
                        f"**Vehicle class:** "
                        f"{vehicle_class if vehicle_class else 'Unconfirmed'}"
                    )
                    st.write(
                        f"Speed input: {report.get('speed_kmh', 'N/A')} km/h"
                    )
                    st.write(
                        f"Speed limit: "
                        f"{report.get('speed_limit_kmh', 'N/A')} km/h"
                    )
                    st.write(
                        f"Event status: "
                        f"{report.get('event_status', 'Unknown')}"
                    )
                    st.write(
                        f"Event source: "
                        f"{report.get('event_source', 'Unknown')}"
                    )
                    st.write(
                        "Reasons: "
                        + "; ".join(report.get("reasons", []))
                    )

                with evidence_col:
                    image_path = Path(report.get("evidence_image", ""))
                    if image_path.is_file():
                        st.image(
                            str(image_path),
                            caption=f"Evidence for {incident_id}",
                        )
                    else:
                        st.warning("Evidence image not found.")

                st.divider()
                
                st.write("**Review History**")

                history = report.get("review_history", [])

                if history:
                    for event in history:
                        st.caption(
                            f'{event.get("status", "UNKNOWN")} — '
                            f'{event.get("changed_at", "Timestamp unavailable")}'
                        )
                else:
                    st.caption(
                        "No status-change history recorded for this incident yet."
                    )

                st.write("**Review workflow**")

                options = ["NEW", "UNDER REVIEW", "RESOLVED"]
                safe_status = (
                    current_status
                    if current_status in options
                    else "NEW"
                )

                selected_status = st.selectbox(
                    "Review status",
                    options,
                    index=options.index(safe_status),
                    key=f"review_{incident_id}",
                )

                if st.button(
                    "Save review status",
                    key=f"save_{incident_id}",
                    type="primary",
                ):
                    try:
                        update_review_status(incident_id, selected_status)
                        st.success(
                            f"{incident_id} saved as {selected_status}."
                        )
                        st.rerun()
                    except (ValueError, OSError, FileNotFoundError) as error:
                        st.error(f"Could not save status: {error}")



with video_tab:
    st.subheader("Process a road video")
    st.write(
        "Upload an MP4, run YOLO detection and ByteTrack, "
        "then inspect the annotated result."
    )

    uploaded_video = st.file_uploader(
        "Choose a video file",
        type=["mp4", "avi", "mov", "mkv"],
    )

    if uploaded_video is not None:
        if st.button("Process Video", type="primary"):
            input_path = Path("data") / "uploaded_demo.mp4"
            output_path = OUTPUT_DIR / "uploaded_tracked.mp4"
            trajectory_path = OUTPUT_DIR / "uploaded_trajectories.jsonl"
            input_path.parent.mkdir(parents=True, exist_ok=True)
            OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
            input_path.write_bytes(uploaded_video.getvalue())

            try:
                info = inspect_video(input_path)
                st.write(
                    f'Video: {info["width"]} × {info["height"]}, '
                    f'{info["fps"]:.2f} FPS, '
                    f'{info["duration_seconds"]:.1f} seconds'
                )

                progress_bar = st.progress(0.0)
                status = st.empty()

                def update_progress(value):
                    progress_bar.progress(value)
                    status.write(f"Processing: {value:.0%}")

                model = load_model()
                
                result = track_video(
                    video_path=input_path,
                    output_path=output_path,
                    progress_callback=update_progress,
                    model=model,
                    trajectory_output_path=trajectory_path,
                )

                
                trajectory_records = []
                with trajectory_path.open("r", encoding="utf-8") as file:
                    for line in file:
                        if line.strip():
                            trajectory_records.append(json.loads(line))

                trajectory_results = analyze_trajectories(trajectory_records)

                valid_speeds = [
                    item["image_speed_px_per_second"]
                    for item in trajectory_results
                    if item["image_speed_px_per_second"] is not None
                ]

                trajectory_summary = {
                    "records_exported": len(trajectory_records),
                    "motion_measurements": len(valid_speeds),
                    "average_image_speed_px_per_second": (
                        round(sum(valid_speeds) / len(valid_speeds), 2)
                        if valid_speeds else None
                    ),
                }
                st.session_state["trajectory_summary"] = trajectory_summary
                st.session_state["trajectory_records"] = trajectory_records

                web_output_path = OUTPUT_DIR / "uploaded_tracked_web.mp4"

                conversion = subprocess.run(
                    [
                        "ffmpeg",
                        "-y",
                        "-i", str(output_path),
                        "-c:v", "libx264",
                        "-preset", "fast",
                        "-crf", "23",
                        "-pix_fmt", "yuv420p",
                        "-movflags", "+faststart",
                        "-an",
                        str(web_output_path),
                    ],
                    capture_output=True,
                    text=True,
                )

                if (
                    conversion.returncode != 0
                    or not web_output_path.is_file()
                    or web_output_path.stat().st_size == 0
                ):
                    raise RuntimeError(
                        "Browser video conversion failed: "
                        + conversion.stderr[-1500:]
                    )

                st.session_state["processed_video"] = str(web_output_path)
                st.session_state["tracking_result"] = result
                st.success("Video processing completed!")

            except Exception as error:
                st.error(f"Video processing failed: {error}")

    # Auto-load verified demonstration footage if session state is empty
    if "processed_video" not in st.session_state:
        default_video = OUTPUT_DIR / "uploaded_tracked_web.mp4"
        default_trajectories = OUTPUT_DIR / "uploaded_trajectories.jsonl"
        if default_video.is_file() and default_trajectories.is_file():
            st.session_state["processed_video"] = str(default_video)
            records = []
            with default_trajectories.open("r", encoding="utf-8") as file:
                for line in file:
                    if line.strip():
                        records.append(json.loads(line))
            st.session_state["trajectory_records"] = records
            traj_results = analyze_trajectories(records)
            speeds = [
                item["image_speed_px_per_second"]
                for item in traj_results
                if item.get("image_speed_px_per_second") is not None
            ]
            st.session_state["trajectory_summary"] = {
                "records_exported": len(records),
                "motion_measurements": len(speeds),
                "average_image_speed_px_per_second": (
                    round(sum(speeds) / len(speeds), 2) if speeds else None
                ),
            }
            st.session_state["tracking_result"] = {
                "frames_processed": 300,
                "frames_with_tracks": 298,
                "distinct_track_ids_observed": len({r["track_id"] for r in records}),
                "duration_seconds": 10.0,
            }

    processed_video = st.session_state.get("processed_video")
    tracking_result = st.session_state.get("tracking_result")

    if processed_video and Path(processed_video).is_file():
        st.subheader("Annotated video & trajectory trails")
        st.video(processed_video)

        if tracking_result:
            a, b, c = st.columns(3)
            a.metric("Frames processed", tracking_result["frames_processed"])
            b.metric(
                "Frames with tracked objects",
                tracking_result["frames_with_tracks"],
            )
            c.metric(
                "Distinct track IDs observed",
                tracking_result["distinct_track_ids_observed"],
            )
            
        trajectory_summary = st.session_state.get("trajectory_summary")

        if trajectory_summary:
            st.subheader("Trajectory analysis")
            st.caption(
                "Motion is measured in image-space pixels. "
                "These values are not vehicle speeds in km/h."
            )

            t1, t2, t3 = st.columns(3)

            t1.metric(
                "Trajectory records",
                trajectory_summary["records_exported"],
            )
            t2.metric(
                "Motion measurements",
                trajectory_summary["motion_measurements"],
            )

            average_speed = trajectory_summary[
                "average_image_speed_px_per_second"
            ]
            t3.metric(
                "Average image-space speed",
                (
                    f"{average_speed:.2f} px/s"
                    if average_speed is not None
                    else "N/A"
                ),
            )

       
            
        duration = (
            tracking_result.get("duration_seconds", 0)
            if tracking_result else 0
        )

        if duration > 0:
            evidence_time = st.slider(
                "Select evidence timestamp (seconds)",
                min_value=0.0,
                max_value=float(duration),
                value=min(5.0, float(duration)),
                step=0.1,
            )

            if st.button("Save selected evidence frame"):
                evidence_output = EVIDENCE_DIR / "uploaded_evidence.png"
                try:
                    save_frame(
                        processed_video,
                        evidence_time,
                        evidence_output,
                    )
                    st.session_state["uploaded_evidence"] = str(
                        evidence_output
                    )
                    st.session_state["uploaded_evidence_time"] = evidence_time
                    st.success(
                        f"Evidence saved at {evidence_time:.1f} seconds."
                    )
                except (ValueError, OSError) as error:
                    st.error(str(error))
        else:
            st.info("Process a video first to select an evidence timestamp.")

        saved_frame = st.session_state.get("uploaded_evidence")
        if saved_frame and Path(saved_frame).is_file():
            st.image(saved_frame, caption="Saved evidence frame")

        # Find tracked vehicles near the saved evidence timestamp.
        trajectory_records = st.session_state.get(
            "trajectory_records", []
        )
        selected_time = float(
            st.session_state.get("uploaded_evidence_time", 5.0)
        )

        nearby_vehicles = {}
        if trajectory_records:
            nearest_time = min(
                (
                    float(record["timestamp_seconds"])
                    for record in trajectory_records
                ),
                key=lambda timestamp: abs(timestamp - selected_time),
            )

            # Only offer vehicles observed close to the evidence time.
            if abs(nearest_time - selected_time) <= 0.2:
                for record in trajectory_records:
                    if abs(
                        float(record["timestamp_seconds"]) - nearest_time
                    ) <= 0.001:
                        track_id = record["track_id"]
                        nearby_vehicles[str(track_id)] = {
                            "track_id": track_id,
                            "class_name": record["class_name"],
                        }

        vehicle_options = ["Unconfirmed"]
        for key, vehicle in sorted(nearby_vehicles.items()):
            vehicle_options.append(
                f'ID {vehicle["track_id"]} | {vehicle["class_name"]}'
            )


        if saved_frame and Path(saved_frame).is_file():
            st.subheader("Generate incident report")

            with st.form("video_incident_form"):
                incident_scenario = st.text_input(
                    "Scenario ID",
                    value="video_review_demo",
                )

                selected_vehicle = st.selectbox(
                    "Vehicle linked to this incident",
                    options=vehicle_options,
                    help=(
                        "Select the vehicle shown in the evidence. "
                        "Choose Unconfirmed if you cannot identify it."
                    ),
                )

                incident_speed = st.number_input(
                    "Scenario speed (km/h)",
                    min_value=0.0,
                    max_value=400.0,
                    value=80.0,
                    step=5.0,
                )
                incident_limit = st.number_input(
                    "Speed limit (km/h)",
                    min_value=1.0,
                    max_value=200.0,
                    value=50.0,
                    step=5.0,
                )
                suspected_collision = st.checkbox(
                    "Flag suspected collision for urgent review"
                )

                create_report = st.form_submit_button(
                    "Generate incident report",
                    type="primary",
                )

            if create_report:
                try:
                    risk = assess_risk(
                        speed_kmh=incident_speed,
                        speed_limit_kmh=incident_limit,
                        suspected_collision=suspected_collision,
                    )

                    event_timestamp = st.session_state.get(
                        "uploaded_evidence_time", 5.0
                    )
                    event_clip_path = (
                        OUTPUT_DIR
                        / "event_replays"
                        / f"{Path(saved_frame).stem}_replay.mp4"
                    )

                    clip_result = create_event_clip(
                        video_path=processed_video,
                        timestamp_seconds=event_timestamp,
                        output_path=event_clip_path,
                        window_seconds=3.0,
                    )


                    report = create_incident_report(
                        risk_result=risk,
                        scenario_id=incident_scenario.strip()
                        or "video_review_demo",
                        timestamp_seconds=event_timestamp,
                        evidence_image=saved_frame,
                        event_source=(
                            "MANUALLY_FLAGGED_SUSPECTED_COLLISION"
                            if suspected_collision
                            else "MANUAL_VIDEO_REVIEW"
                        ),

                        event_clip=clip_result["output_path"],
                        track_id=(
                            nearby_vehicles[
                                selected_vehicle.split("|")[0]
                                .replace("ID ", "")
                                .strip()
                            ]["track_id"]
                            if selected_vehicle != "Unconfirmed"
                            else None
                        ),
                        vehicle_class=(
                            nearby_vehicles[
                                selected_vehicle.split("|")[0]
                                .replace("ID ", "")
                                .strip()
                            ]["class_name"]
                            if selected_vehicle != "Unconfirmed"
                            else None
                        ),
                    )
                    st.success(
                        f'Report created: {report["incident_id"]}'
                    )

                except (ValueError, OSError, RuntimeError) as error:
                    st.error(
                        f"Could not create incident report or replay: {error}"
                    )

with authority_tab:
    st.subheader("Authority Notification Centre")
    st.caption(
        "Review investigation evidence and prepare a simulated notification. "
        "No real authority is contacted."
    )

    events = read_interaction_events()
    notifications = read_notification_log()

    if not events:
        st.info("No interaction events found. Generate investigation events first.")
    else:
        event_options = {
            f"{event.get('event_id', 'Unknown')} | "
            f"{event.get('finding', 'Unknown finding')} | "
            f"{event.get('evidence_timestamp_seconds', 0):.2f}s": event
            for event in events
        }

        selected_label = st.selectbox(
            "Select an investigation event",
            list(event_options.keys()),
        )

        selected_event = event_options[selected_label]

        event_id = selected_event.get("event_id", "Unknown event")


        matching_notifications = [
            notification
            for notification in notifications
            if notification.get("event_id") == event_id
        ]

        if matching_notifications:
            latest_notification = matching_notifications[-1]
            notification_status = (
                f"{latest_notification.get('status', 'UNKNOWN')} "
                "(local demo only; not delivered)"
            )
        else:
            notification_status = "NOT SUBMITTED"

        matching_reviews = [
            review
            for review in read_review_log()
            if review.get("event_id") == event_id
        ]

        if matching_reviews:
            latest_review = matching_reviews[-1]
            review_status = latest_review.get(
                "decision",
                "PENDING REVIEW",
            )
        else:
            review_status = "PENDING REVIEW"

        selected_event = {
            **selected_event,
            "notification_status": notification_status,
            "review_status": review_status,
        }


        pdf_evidence_path = (
            INTERACTION_EVIDENCE_DIR / f"{event_id}.jpg"
        )

        try:
            pdf_bytes = create_interaction_pdf(
                selected_event,
                evidence_path=pdf_evidence_path,
            )

            st.download_button(
                label="Download investigation report (PDF)",
                data=pdf_bytes,
                file_name=f"MotionGuard_{event_id}_report.pdf",
                mime="application/pdf",
                key=f"download_pdf_{event_id}",
            )
        except (OSError, ValueError, RuntimeError) as error:
            st.error(f"Could not generate PDF report: {error}")

        event_id = selected_event.get("event_id", "Unknown event")

        st.markdown("### Investigation report preview")

        col_a, col_b, col_c = st.columns(3)
        col_a.metric("Event ID", event_id)
        col_b.metric(
            "Evidence timestamp",
            f"{selected_event.get('evidence_timestamp_seconds', 0):.2f}s",
        )
        col_c.metric(
            "Detection count",
            selected_event.get("detection_count", 0),
        )

        evidence_path = (
            INTERACTION_EVIDENCE_DIR / f"{event_id}.jpg"
        )
        if evidence_path.exists():
            st.image(
                str(evidence_path),
                caption=f"Evidence for {event_id}",
                use_container_width=True,
            )
        else:
            st.warning("Evidence image is unavailable for this event.")

        st.write("**Finding:**", selected_event.get("finding", "Not specified"))
        st.write("**Confidence:**", selected_event.get("confidence", "Not specified"))
        st.write("**Track IDs:**", selected_event.get("track_ids", []))
        st.write(
            "**Minimum image-space distance:**",
            f"{selected_event.get('minimum_distance_px', 'N/A')} px",
        )
        st.write(
            "**Peak image-space closing speed:**",
            f"{selected_event.get('peak_closing_speed_px_per_second', 'N/A')} px/s",
        )

        limitations = selected_event.get("limitations", [])
        st.write("**Limitations:**")

        for limitation in limitations:
            st.write(f"- {limitation}")

        st.divider()

        st.markdown("### Investigation review")

        existing_reviews = [
            review
            for review in read_review_log()
            if review.get("event_id") == event_id
        ]

        latest_review = (
            existing_reviews[-1].get("decision", "PENDING REVIEW")
            if existing_reviews
            else "PENDING REVIEW"
        )

        review_options = [
            "PENDING REVIEW",
            "REVIEWED — NO ACTION REQUIRED",
            "REVIEWED — ESCALATION RECOMMENDED",
        ]

        review_decision = st.selectbox(
            "Review decision",
            review_options,
            index=(
                review_options.index(latest_review)
                if latest_review in review_options
                else 0
            ),
            key=f"review_decision_{event_id}",
        )

        st.caption(
            "This is an operator's local review decision, not an official finding."
        )

        if st.button(
            "Save review decision",
            key=f"save_review_{event_id}",
        ):
            record_review(event_id, review_decision)
            st.success("Review decision saved to local history.")
            st.rerun()


        st.divider()
        st.markdown("### Prepare notification")


        authority = st.selectbox(
            "Intended recipient",
            [
                "Traffic Police (demo)",
                "Road Safety Department (demo)",
                "Campus Security (demo)",
                "Other Authority (demo)",
            ],
        )

        st.warning(
            "Demo mode: submitting creates a local record only. "
            "It does not send an email, call an API, or contact authorities."
        )

        already_submitted = any(
            item.get("event_id") == event_id
            and item.get("status") == "SUBMITTED_SIMULATED"
            for item in notifications
        )

        if already_submitted:
            st.info(
                "A simulated notification for this event already exists. "
                "Check the submission history below."
            )

        confirm_submission = st.checkbox(
            f"I reviewed the evidence for {event_id} and want to record "
            "a simulated notification.",
            key=f"confirm_notification_{event_id}",
        )

        if st.button(
            "Submit simulated notification",
            key=f"submit_notification_{event_id}",
            disabled=already_submitted or not confirm_submission,
        ):
            record_notification(selected_event, authority)
            st.success(
                f"Simulated submission recorded for {event_id}. "
                "No real authority was contacted."
            )
            st.rerun()

        st.divider()
        st.markdown("### 📱 Emergency Text / SMS Dispatcher")
        st.caption(
            "Immediately dispatch high-priority accident / interaction text alerts directly to concerned authorities."
        )

        sms_c1, sms_c2 = st.columns([1, 1])
        with sms_c1:
            dest_phone = st.text_input(
                "Concerned Authority Mobile Number",
                value="+91 98765 43210",
                help="Enter phone number with country code (e.g. +91... or +1...)",
                key=f"phone_{event_id}",
            )
            camera_loc = st.text_input(
                "CCTV Location Identifier",
                value="Highway Junction Cam #04",
                key=f"cam_{event_id}",
            )
            sms_gateway = st.radio(
                "SMS Gateway Provider",
                [
                    "Local Emergency Carrier Simulator (Instant zero-setup demo)",
                    "Twilio SMS Gateway (Real Text Message to your phone)",
                    "Telegram Instant Alert (Free push to your phone)",
                ],
                key=f"gateway_{event_id}",
            )

            twilio_sid = None
            twilio_token = None
            twilio_from = None
            tg_token = None
            tg_chat = None

            if "Twilio" in sms_gateway:
                st.info("Enter Twilio credentials (or define TWILIO_ACCOUNT_SID in environment):")
                twilio_sid = st.text_input("Twilio Account SID", type="password", key=f"tw_sid_{event_id}")
                twilio_token = st.text_input("Twilio Auth Token", type="password", key=f"tw_tok_{event_id}")
                twilio_from = st.text_input("Twilio Sender Number", placeholder="+1...", key=f"tw_from_{event_id}")
            elif "Telegram" in sms_gateway:
                _env_tg_token = os.getenv("TELEGRAM_BOT_TOKEN", "")
                _env_tg_chat = os.getenv("TELEGRAM_CHAT_ID", "")
                if _env_tg_token and _env_tg_chat:
                    st.success("✅ Telegram credentials loaded from environment variables — ready to dispatch!")
                else:
                    st.info("Enter Telegram Bot credentials (or set TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID env vars):")
                tg_token = st.text_input(
                    "Telegram Bot Token",
                    value=_env_tg_token,
                    type="password",
                    key=f"tg_tok_{event_id}",
                )
                tg_chat = st.text_input(
                    "Telegram Chat ID",
                    value=_env_tg_chat,
                    placeholder="e.g. 123456789",
                    key=f"tg_chat_{event_id}",
                )

        sms_body = format_emergency_sms(selected_event, camera_name=camera_loc)

        with sms_c2:
            st.markdown("**Smartphone Alert Payload Preview:**")
            st.markdown(
                f"""
                <div style="
                    background: #0f172a;
                    border: 1px solid #334155;
                    border-left: 5px solid #ef4444;
                    border-radius: 8px;
                    padding: 12px 16px;
                    font-family: monospace;
                    font-size: 0.85rem;
                    color: #f1f5f9;
                    white-space: pre-wrap;
                    line-height: 1.4;
                ">{sms_body}</div>
                """,
                unsafe_allow_html=True,
            )

        if st.button("🚨 Dispatch Emergency Text Alert Now", type="primary", key=f"btn_send_sms_{event_id}"):
            try:
                selected_mode = "TWILIO" if "Twilio" in sms_gateway else ("TELEGRAM" if "Telegram" in sms_gateway else "SIMULATOR")
                dispatch_res = dispatch_sms(
                    phone_number=dest_phone,
                    message_text=sms_body,
                    twilio_sid=twilio_sid,
                    twilio_token=twilio_token,
                    twilio_from=twilio_from,
                    telegram_token=tg_token,
                    telegram_chat_id=tg_chat,
                    gateway_mode=selected_mode,
                )
                log_sms_dispatch(dispatch_res)
                if dispatch_res.get("success"):
                    st.success(
                        f"✅ Text Alert Dispatched to {dispatch_res['recipient']} via {dispatch_res['channel']}! "
                        f"Message ID: {dispatch_res['message_id']}"
                    )
                    st.balloons()
                else:
                    st.error(f"Dispatch error: {dispatch_res.get('error')}")
            except Exception as e:
                st.error(f"Invalid phone number or dispatch failure: {e}")

    st.divider()
    st.markdown("### Dispatch & Notification History")

    history_tab1, history_tab2 = st.tabs(["📋 Formal Authority Notifications", "📱 Text / SMS Dispatches Log"])

    with history_tab1:
        notifications = read_notification_log()
        if not notifications:
            st.info("No notification submissions recorded yet.")
        else:
            for item in reversed(notifications):
                with st.expander(
                    f"{item.get('event_id', 'Unknown event')} — "
                    f"{item.get('authority', 'Unknown recipient')} — "
                    f"{item.get('status', 'Unknown status')}"
                ):
                    st.write("**Notification ID:**", item.get("notification_id"))
                    st.write("**Submitted at:**", item.get("submitted_at"))
                    st.write("**Submitted by:**", item.get("submitted_by"))
                    st.json(item.get("report", {}))

    with history_tab2:
        sms_records = read_sms_log()
        if not sms_records:
            st.info("No text alerts dispatched yet. Use the dispatcher above to send an emergency alert.")
        else:
            for record in reversed(sms_records):
                with st.expander(
                    f"{record.get('channel', 'SMS')} → {record.get('recipient')} — {record.get('status')} ({record.get('dispatched_at', '')[:19]})"
                ):
                    st.write("**Dispatched At:**", record.get("dispatched_at"))
                    st.write("**Message ID:**", record.get("message_id"))
                    st.write("**Channel:**", record.get("channel"))
                    st.code(record.get("body", record.get("message", "")))





st.divider()
st.caption(
    "Prototype only. Speed is manually supplied, collision flags require "
    "review, and notifications are simulated. Tracking IDs are not "
    "guaranteed to represent unique real-world vehicles."
)
