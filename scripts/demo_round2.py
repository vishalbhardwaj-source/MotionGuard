"""
MotionGuard Round 2 Demo Script
Runs outputs/trajectories_trails_test.jsonl through:
  1. analyze_interactions
  2. aggregate_interaction_events
  3. assess_event_risk
And displays each event's id, distance in px, closing speed in px/s, threat level, and score.
"""

import json
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.interaction_analysis import analyze_interactions
from src.event_aggregation import aggregate_interaction_events
from src.risk_engine import assess_event_risk


def run_round2_demo():
    traj_path = Path("outputs/trajectories_trails_test.jsonl")
    if not traj_path.is_file():
        print(f"Error: Trajectory file {traj_path} not found.")
        return

    print("=" * 80)
    print("MOTIONGUARD ROUND 2: IMAGE-SPACE RISK SCORER & DEMO VERIFICATION")
    print("=" * 80)
    print(f"Loading trajectory records from: {traj_path}")

    records = [json.loads(line) for line in traj_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    print(f"Loaded {len(records)} trajectory records.")

    # Step 1: Interaction Analysis
    findings = analyze_interactions(records)
    print(f"Candidate pairwise interaction findings detected: {len(findings)}")

    # Step 2: Event Aggregation
    events = aggregate_interaction_events(findings)
    print(f"Aggregated interaction events: {len(events)}\n")

    print(f"{'Event ID':<12} | {'Min Dist (px)':<14} | {'Closing (px/s)':<15} | {'Level':<12} | {'Score':<8} | {'Status'}")
    print("-" * 80)

    for ev in events:
        risk = assess_event_risk(ev)
        ev_id = ev.get("event_id", "N/A")
        min_dist = ev.get("minimum_distance_px", 0.0)
        closing = ev.get("peak_closing_speed_px_per_second", 0.0)
        level = risk["threat_level"]
        score = risk["threat_score"]
        status = risk["event_status"]

        print(f"{ev_id:<12} | {min_dist:<14.2f} | {closing:<15.2f} | {level:<12} | {score:<8} | {status}")

    print("-" * 80)
    if events:
        sample_ev = events[0]
        sample_risk = assess_event_risk(sample_ev)
        print("\n[SAMPLE EVENT EXPLAINABLE RISK BREAKDOWN (Pixel-based Factor Cards)]")
        print(f"Event ID: {sample_ev.get('event_id')}")
        print(f"Threat Score: {sample_risk['threat_score']}/100 ({sample_risk['threat_level']})")
        print(f"Explainability Summary: {sample_risk['explainability_summary']}\n")
        print("Factor Breakdown Cards:")
        for card in sample_risk["factor_breakdown"]:
            print(f"  • {card['factor']}: [{card['display_status']}] -> {card['detail']}")

    print("\n" + "=" * 80)
    print("Demo step 1 complete!")
    print("=" * 80)


if __name__ == "__main__":
    run_round2_demo()
