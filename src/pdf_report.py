from io import BytesIO
from pathlib import Path

try:
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import mm
    from reportlab.platypus import (
        SimpleDocTemplate,
        Paragraph,
        Spacer,
        Image,
        Table,
        TableStyle,
        HRFlowable,
    )
except ImportError:
    colors = None

from src.risk_engine import assess_event_risk


def create_interaction_pdf(event, evidence_path=None):
    """Create a comprehensive, forensic investigation-support PDF dossier for a MotionGuard interaction event."""
    buffer = BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=16 * mm,
        bottomMargin=16 * mm,
        title=f"MotionGuard Investigation - {event.get('event_id', 'Unknown')}",
    )

    styles = getSampleStyleSheet()

    report_title_style = ParagraphStyle(
        name="ReportTitle",
        parent=styles["Title"],
        alignment=TA_LEFT,
        textColor=colors.HexColor("#0F172A"),
        fontSize=20,
        leading=24,
        spaceAfter=2,
    )

    subtitle_style = ParagraphStyle(
        name="SubTitle",
        parent=styles["Normal"],
        textColor=colors.HexColor("#475569"),
        fontSize=10,
        leading=14,
        spaceAfter=6,
    )

    heading_style = ParagraphStyle(
        name="SectionHeading",
        parent=styles["Heading2"],
        textColor=colors.HexColor("#1E3A8A"),
        fontSize=12,
        leading=16,
        spaceBefore=8,
        spaceAfter=4,
    )

    callout_style = ParagraphStyle(
        name="CalloutText",
        parent=styles["Normal"],
        textColor=colors.HexColor("#B45309"),
        fontSize=9,
        leading=13,
    )

    event_id = str(event.get("event_id", "Unknown event"))
    timestamp = event.get("evidence_timestamp_seconds", "N/A")
    if isinstance(timestamp, (int, float)):
        timestamp_str = f"{timestamp:.3f} seconds"
    else:
        timestamp_str = str(timestamp)

    start_time = event.get("start_seconds")
    end_time = event.get("end_seconds")
    duration = event.get("duration_seconds")

    if start_time is not None and end_time is not None:
        timeline = f"{float(start_time):.2f}s to {float(end_time):.2f}s"
    else:
        timeline = "Not available"

    duration_text = (
        f"{float(duration):.2f} seconds" if duration is not None else "Not available"
    )

    finding = str(event.get("finding", "Not specified"))
    review_status = event.get("review_status", "PENDING REVIEW")
    notification_status = event.get("notification_status", "NOT SUBMITTED")

    if finding == "POTENTIAL_APPROACHING_INTERACTION":
        summary = (
            "The automated trajectory analysis identified an approaching interaction between "
            "tracked road entities. This event record serves as decision support for human investigators, "
            "not as an autonomous collision certainty or legal determination."
        )
    else:
        summary = (
            f"The video analysis recorded the event finding '{finding}'. "
            "Secondary operator review is required before drawing conclusions."
        )

    story = [
        Paragraph("<b>MOTIONGUARD</b> | Safety Intelligence Dossier", subtitle_style),
        Paragraph(f"Incident Investigation Report: {event_id}", report_title_style),
        Paragraph(
            "AI-Assisted Video Risk Assessment & Evidence Extraction Prototype",
            subtitle_style,
        ),
        HRFlowable(width="100%", thickness=1, color=colors.HexColor("#CBD5E1"), spaceAfter=10),
        
        # Prototype Disclaimer Box
        Table(
            [
                [
                    Paragraph(
                        "<b>PROTOTYPE REPORT NOTICE:</b> Measurements reflect uncalibrated 2D image coordinates. "
                        "Proximity and closing vectors indicate candidate interactions for review, not certified physical collisions.",
                        callout_style,
                    )
                ]
            ],
            colWidths=[174 * mm],
            style=[
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#FEF3C7")),
                ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#F59E0B")),
                ("LEFTPADDING", (0, 0), (-1, -1), 10),
                ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ],
        ),
        Spacer(1, 5 * mm),
        Paragraph("1. Incident Summary & Timeline", heading_style),
        Paragraph(summary, styles["BodyText"]),
        Spacer(1, 2 * mm),
        Paragraph(
            f"<b>Active Episode Interval:</b> {timeline} &nbsp;&nbsp;|&nbsp;&nbsp; "
            f"<b>Duration:</b> {duration_text} &nbsp;&nbsp;|&nbsp;&nbsp; "
            f"<b>Closest-Approach Timestamp:</b> {timestamp_str}",
            styles["BodyText"],
        ),
        Spacer(1, 5 * mm),
        Paragraph("2. Kinematic & Observational Metrics", heading_style),
    ]

    details = [
        ["Investigation Attribute", "Recorded Algorithmic Metric"],
        ["Incident Dossier ID", event_id],
        ["Target Timestamp", timestamp_str],
        ["Classification Finding", finding],
        ["Algorithmic Confidence", str(event.get("confidence", "UNVALIDATED_HEURISTIC"))],
        ["Tracked Entity IDs", ", ".join(map(str, event.get("track_ids", []))) or "N/A"],
        ["Consecutive Detections", str(event.get("detection_count", "N/A"))],
        ["Peak Consecutive Confirmations", str(event.get("peak_confirmation_count", "N/A"))],
        ["Minimum Image-Space Distance", f"{event.get('minimum_distance_px', 'N/A')} px"],
        ["Peak Image-Space Closing Speed", f"{event.get('peak_closing_speed_px_per_second', 'N/A')} px/s"],
        ["Operator Triage Decision", str(review_status)],
        ["Authority Dispatch Status", str(notification_status)],
    ]

    table = Table(details, colWidths=[64 * mm, 110 * mm], repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1E3A8A")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 9),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#CBD5E1")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )

    story.extend([table, Spacer(1, 4 * mm)])

    # Explainable Risk Breakdown Section (Round 2 Stretch: Active Thresholds & Measured Values)
    story.append(Paragraph("3. Explainable Risk Factor Breakdown", heading_style))
    story.append(
        Paragraph(
            "Algorithmic decision-support factors explaining how the image-space scorer characterized event risk:",
            styles["BodyText"],
        )
    )
    story.append(Spacer(1, 1 * mm))

    risk_eval = assess_event_risk(event)
    active_thresh = risk_eval.get("thresholds_used") or {}
    thresh_line = (
        f"<b>Active Scorer Thresholds:</b> "
        f"Distance [Crit &le; {active_thresh.get('distance_critical_px', 15.0):.1f} px, Mod &le; {active_thresh.get('distance_moderate_px', 45.0):.1f} px] | "
        f"Closing [Crit &ge; {active_thresh.get('closing_speed_critical_px_s', 30.0):.1f} px/s, Mod &ge; {active_thresh.get('closing_speed_moderate_px_s', 15.0):.1f} px/s] | "
        f"Confirmation [Crit &ge; {active_thresh.get('confirmation_count_critical', 4)} frames]"
    )
    story.append(Paragraph(thresh_line, subtitle_style))
    story.append(Spacer(1, 2 * mm))

    factor_rows = [["Evaluation Factor", "Measured Value", "Active Threshold", "Status", "Investigation Context"]]
    for f in risk_eval.get("factor_breakdown", []):
        factor_rows.append([
            Paragraph(f"<b>{f.get('factor', '')}</b>", styles["BodyText"]),
            Paragraph(str(f.get("measured_value", "N/A")), styles["BodyText"]),
            Paragraph(str(f.get("threshold", "N/A")), styles["BodyText"]),
            Paragraph(f"<b>{f.get('display_status', '')}</b>", styles["BodyText"]),
            Paragraph(f.get("detail", ""), styles["BodyText"]),
        ])

    factor_table = Table(factor_rows, colWidths=[34 * mm, 24 * mm, 28 * mm, 22 * mm, 66 * mm], repeatRows=1)
    factor_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#334155")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 8.5),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#CBD5E1")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    story.extend([factor_table, Spacer(1, 4 * mm)])

    # Evidence Image Section
    story.append(Paragraph("4. Supporting Visual Evidence", heading_style))
    if evidence_path and Path(evidence_path).is_file():
        story.extend(
            [
                Paragraph(
                    f"Frame captured at closest approach ({timestamp_str}) with tracked entity bounding boxes and IDs.",
                    styles["BodyText"],
                ),
                Spacer(1, 2 * mm),
                Image(str(evidence_path), width=160 * mm, height=88 * mm, kind="proportional"),
                Spacer(1, 4 * mm),
            ]
        )
    else:
        story.extend(
            [
                Paragraph("Visual evidence snapshot currently unavailable for this record.", styles["BodyText"]),
                Spacer(1, 4 * mm),
            ]
        )

    # Limitations & Next Steps
    story.append(Paragraph("5. Technical Limitations & Required Next Steps", heading_style))
    limitations = event.get("limitations", [])
    if not limitations:
        limitations = [
            "Image coordinates (pixels) do not correspond linearly to ground-plane meters without extrinsic calibration.",
            "Visual occlusion or camera perspective may cause temporary track ID switches.",
            "Proximity alone does not confirm physical contact or impact damage.",
        ]

    for limitation in limitations:
        story.append(Paragraph(f"&bull; <b>Limitation:</b> {limitation}", styles["BodyText"]))
        story.append(Spacer(1, 1.5 * mm))

    next_steps = [
        "Cross-reference timestamp with secondary camera viewpoints or roadside telemetry.",
        "Perform optical camera calibration if real-world velocity measurements are required for litigation.",
        "Submit incident dossier to designated authority dispatcher for manual verification.",
    ]
    for step in next_steps:
        story.append(Paragraph(f"&bull; <b>Action:</b> {step}", styles["BodyText"]))
        story.append(Spacer(1, 1.5 * mm))

    document.build(story)
    buffer.seek(0)
    return buffer.getvalue()
