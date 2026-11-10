#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Main Scout Pipeline CLI Tool
Coordinates:
- YouTube API harvesting (uploads playlist + batch videos)
- Outlier Engine (Leave-One-Out median + Cohorts + Floor threshold)
- Quota Tracker logging
- Handoff Manifest generation for youtube-market-researcher
"""

import os
import sys
import json
import uuid
import argparse
import logging
from datetime import datetime, timezone
from typing import Optional

from quota_tracker import QuotaTracker
from api_client import YouTubeAPIClient
from outlier_engine import OutlierEngine

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("ScoutPipeline")

def generate_run_id() -> str:
    now_str = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    rand_suffix = uuid.uuid4().hex[:6].upper()
    return f"RUN_{now_str}_{rand_suffix}"

def run_scout_pipeline(
    channel_identifier: str,
    limit: int = 50,
    min_floor: int = 500,
    threshold: float = 2.5,
    api_key: Optional[str] = None,
    mock_mode: bool = False,
    prev_snapshot_path: Optional[str] = None,
    out_dir: str = "./scout_output",
) -> dict:
    run_id = generate_run_id()
    now_utc = datetime.now(timezone.utc)
    os.makedirs(out_dir, exist_ok=True)

    logger.info(f"=== Starting Scout Pipeline Execution [{run_id}] ===")
    logger.info(f"Target Channel: {channel_identifier}")
    logger.info(f"Parameters: Limit={limit}, Floor={min_floor}, Threshold={threshold}x, Mock={mock_mode}")

    # 1. Initialize Quota Tracker & API Client
    tracker = QuotaTracker()
    client = YouTubeAPIClient(api_key=api_key, quota_tracker=tracker, mock_mode=mock_mode)
    engine = OutlierEngine(min_floor_views=min_floor, outlier_multiplier_threshold=threshold)

    # 2. Resolve Channel & Uploads Playlist
    channel_info = client.resolve_channel(channel_identifier)
    channel_id = channel_info["channel_id"]
    uploads_id = channel_info["uploads_playlist_id"]

    logger.info(f"Resolved Channel: '{channel_info['title']}' ({channel_id})")
    logger.info(f"Uploads Playlist ID: {uploads_id} (Zero-cost UC->UU translation)")

    # 3. Fetch Video IDs from Uploads Playlist
    video_ids = client.fetch_playlist_video_ids(uploads_id, limit=limit)
    logger.info(f"Retrieved {len(video_ids)} video IDs from uploads playlist.")

    if not video_ids:
        logger.warning("No videos retrieved. Aborting pipeline.")
        return {"run_id": run_id, "status": "NO_VIDEOS"}

    # 4. Batch Enrich Videos
    enriched_records = client.batch_enrich_videos(video_ids)
    logger.info(f"Enriched metadata for {len(enriched_records)} videos.")

    # 5. Load Previous Snapshot if provided
    prev_snapshot = None
    if prev_snapshot_path and os.path.exists(prev_snapshot_path):
        try:
            with open(prev_snapshot_path, "r", encoding="utf-8") as f:
                prev_snapshot = json.load(f)
            logger.info(f"Loaded previous snapshot from: {prev_snapshot_path}")
        except Exception as e:
            logger.warning(f"Failed to load previous snapshot: {e}")

    # 6. Execute Outlier Engine
    analysis_result = engine.process_records(
        enriched_records=enriched_records,
        previous_snapshot=prev_snapshot,
        now_utc=now_utc,
    )

    processed_records = analysis_result["processed_records"]
    candidates = analysis_result["candidates"]
    cohort_summaries = analysis_result["cohort_summaries"]

    # 7. Build Full Snapshot Document (Append-only storage)
    snapshot_doc = {
        "run_id": run_id,
        "timestamp": now_utc.isoformat(),
        "channel": channel_info,
        "pipeline_parameters": {
            "limit": limit,
            "min_floor_views": min_floor,
            "outlier_multiplier_threshold": threshold,
            "mock_mode": mock_mode,
        },
        "summary": {
            "total_videos_analyzed": len(processed_records),
            "candidates_count": len(candidates),
            "global_median_raw": analysis_result["global_median_raw"],
            "cohort_summaries": cohort_summaries,
        },
        "records": processed_records,
    }
    snapshot_filename = f"channel_snapshot_{channel_id}_{run_id}.json"
    snapshot_path = os.path.join(out_dir, snapshot_filename)
    with open(snapshot_path, "w", encoding="utf-8") as f:
        json.dump(snapshot_doc, f, indent=2, ensure_ascii=False)
    logger.info(f"Saved full immutable snapshot: {snapshot_path}")

    # 8. Build Handoff Manifest Document (Contract for youtube-market-researcher)
    quota_summary = tracker.get_summary()
    handoff_doc = {
        "schema_version": "1.0.0",
        "run_id": run_id,
        "generated_at": now_utc.isoformat(),
        "source_skill": "youtube-api-scout",
        "target_skill": "youtube-market-researcher",
        "audit_status": "READY_FOR_PIPELINE",
        "channel": channel_info,
        "pipeline_parameters": {
            "min_floor_views": min_floor,
            "outlier_multiplier_threshold": threshold,
            "sample_size_analyzed": len(processed_records),
            "age_cohort_enabled": True,
        },
        "provenance": {
            "api_version": "YouTube Data API v3 (Official)",
            "mock_mode": mock_mode,
            "quota_units_consumed": 2 if not mock_mode else 0,
            "endpoint_flow": [
                "channels.list (1 unit - contentDetails)",
                "playlistItems.list (1 unit - uploads batch)",
                "videos.list (1 unit - batch statistics/duration)",
            ],
            "local_quota_tracker_snapshot": quota_summary,
        },
        "cohort_summaries": cohort_summaries,
        "candidates": candidates,
    }
    handoff_path = os.path.join(out_dir, "handoff_manifest.json")
    with open(handoff_path, "w", encoding="utf-8") as f:
        json.dump(handoff_doc, f, indent=2, ensure_ascii=False)
    logger.info(f"Saved handoff manifest contract: {handoff_path}")

    # 9. Print Concise Summary Table
    print("\n" + "=" * 80)
    print(f"SCOUT PIPELINE SUMMARY: {channel_info['title']} ({channel_info['handle']})")
    print(f"Run ID: {run_id} | Sample Size: {len(processed_records)} | Outlier Candidates: {len(candidates)}")
    print("=" * 80)
    print(f"{'VIDEO ID':<13} | {'VIEWS [RAW]':<12} | {'COHORT LOO':<11} | {'MULT [CALC]':<11} | {'FLOOR':<6} | {'CLASSIFICATION':<20}")
    print("-" * 80)
    for rec in processed_records:
        vid = rec["video_id"]
        v_raw = rec["raw_data"]["view_count"]
        calc = rec["calculated_metrics"]
        c_loo = calc["cohort_median_loo"]
        mult = calc["effective_multiplier"]
        fl = "PASS" if calc["floor_cleared"] else "FAIL"
        cls_name = calc["classification"]

        marker = ">>>" if calc["floor_cleared"] and mult >= threshold else "   "
        print(f"{marker} {vid:<10} | {v_raw:<12,d} | {c_loo:<11,.1f} | {mult:<10.2f}x | {fl:<6} | {cls_name:<20}")

    print("=" * 80)
    print(f"Candidates qualified for Handoff: {len(candidates)}")
    print(f"Handoff Manifest: {os.path.abspath(handoff_path)}")
    print(f"Snapshot File:    {os.path.abspath(snapshot_path)}")
    print(f"Quota Tracker:    Used {quota_summary['daily_used_estimate']}/{quota_summary['daily_limit_budget']} units (Tier: {quota_summary['tier_status']})")
    print("=" * 80 + "\n")

    return {
        "run_id": run_id,
        "snapshot_path": snapshot_path,
        "handoff_path": handoff_path,
        "candidates_count": len(candidates),
        "channel_title": channel_info["title"],
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="YouTube API Scout Pipeline Runner")
    parser.add_argument("-c", "--channel", required=True, help="Channel URL, @handle, or ID (UC...)")
    parser.add_argument("-l", "--limit", type=int, default=50, help="Number of videos to analyze (default: 50)")
    parser.add_argument("--min-floor", type=int, default=500, help="Minimum views floor for outlier qualification (default: 500)")
    parser.add_argument("-t", "--threshold", type=float, default=2.5, help="Outlier multiplier threshold (default: 2.5)")
    parser.add_argument("--api-key", type=str, default=None, help="Explicit YouTube Data API v3 key")
    parser.add_argument("--mock", action="store_true", help="Force offline mock mode")
    parser.add_argument("--prev-snapshot", type=str, default=None, help="Path to previous snapshot for Snapshot VPH")
    parser.add_argument("-o", "--out-dir", type=str, default="./scout_output", help="Directory for output artifacts")

    args = parser.parse_args()
    run_scout_pipeline(
        channel_identifier=args.channel,
        limit=args.limit,
        min_floor=args.min_floor,
        threshold=args.threshold,
        api_key=args.api_key,
        mock_mode=args.mock,
        prev_snapshot_path=args.prev_snapshot,
        out_dir=args.out_dir,
    )
