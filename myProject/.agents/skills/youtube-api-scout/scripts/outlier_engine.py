#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Outlier Engine for YouTube API Scout
Implements:
- Leave-One-Out (Jackknife) Median calculation
- Age Cohort Stratification (<=14d, 15-60d, 61-180d, >180d)
- Absolute Floor Threshold filtering (MIN_FLOOR)
- Lifetime VPH & Snapshot VPH calculation
- Strict data provenance and [RAW DATA] vs [CALCULATED] segregation
"""

import math
import statistics
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional, Tuple

COHORTS = {
    "recent_lte_14d": {"label": "Recent (<= 14 days)", "max_days": 14.0},
    "growth_15_60d": {"label": "Growth (15 - 60 days)", "max_days": 60.0},
    "established_61_180d": {"label": "Established (61 - 180 days)", "max_days": 180.0},
    "evergreen_gt_180d": {"label": "Evergreen (> 180 days)", "max_days": float("inf")},
}

def parse_iso_datetime(dt_str: str) -> datetime:
    """Parses ISO 8601 string to timezone-aware UTC datetime."""
    clean = dt_str.replace("Z", "+00:00")
    dt = datetime.fromisoformat(clean)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)

def calculate_leave_one_out_median(values: List[float], exclude_idx: int) -> float:
    """
    Computes the sample median excluding the element at exclude_idx.
    Eliminates self-skewing bias of the candidate video.
    """
    if len(values) <= 1:
        return 1.0

    subset = [val for i, val in enumerate(values) if i != exclude_idx]
    if not subset:
        return 1.0

    return float(statistics.median(subset))

def assign_age_cohort(published_at_str: str, now_utc: Optional[datetime] = None) -> Tuple[str, float, float]:
    """
    Computes age in days/hours and returns cohort ID.
    """
    if now_utc is None:
        now_utc = datetime.now(timezone.utc)

    pub_dt = parse_iso_datetime(published_at_str)
    diff = now_utc - pub_dt
    age_hours = max(diff.total_seconds() / 3600.0, 0.1)
    age_days = age_hours / 24.0

    if age_days <= 14.0:
        cohort_id = "recent_lte_14d"
    elif age_days <= 60.0:
        cohort_id = "growth_15_60d"
    elif age_days <= 180.0:
        cohort_id = "established_61_180d"
    else:
        cohort_id = "evergreen_gt_180d"

    return cohort_id, round(age_days, 2), round(age_hours, 2)

def calculate_lifetime_vph(view_count: int, age_hours: float) -> float:
    """Lifetime Views Per Hour = Total Views / Total Hours Published."""
    return round(float(view_count) / max(age_hours, 1.0), 2)

def calculate_snapshot_vph(
    current_views: int,
    previous_views: int,
    current_time: datetime,
    previous_time: datetime,
) -> Optional[float]:
    """
    Snapshot VPH = Delta Views / Delta Hours between two snapshots.
    """
    delta_seconds = (current_time - previous_time).total_seconds()
    if delta_seconds <= 0:
        return None
    delta_hours = delta_seconds / 3600.0
    delta_views = current_views - previous_views
    return round(float(delta_views) / delta_hours, 2)

class OutlierEngine:
    def __init__(
        self,
        min_floor_views: int = 500,
        outlier_multiplier_threshold: float = 2.5,
    ):
        self.min_floor_views = min_floor_views
        self.multiplier_threshold = outlier_multiplier_threshold

    def process_records(
        self,
        enriched_records: List[Dict[str, Any]],
        previous_snapshot: Optional[Dict[str, Any]] = None,
        now_utc: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """
        Processes enriched video records, computes Leave-One-Out metrics,
        cohort medians, and tags records for pipeline handoff.
        """
        if now_utc is None:
            now_utc = datetime.now(timezone.utc)

        # Build index for previous snapshot lookup (for Snapshot VPH)
        prev_views_map: Dict[str, Tuple[int, datetime]] = {}
        if previous_snapshot and "records" in previous_snapshot:
            prev_ts = parse_iso_datetime(previous_snapshot.get("timestamp", now_utc.isoformat()))
            for r in previous_snapshot["records"]:
                vid = r.get("video_id")
                vc = r.get("raw_data", {}).get("view_count", 0)
                if vid:
                    prev_views_map[vid] = (vc, prev_ts)

        # 1. Assign age cohorts and basic metrics
        all_views = [r["raw_data"]["view_count"] for r in enriched_records]
        cohort_groups: Dict[str, List[Tuple[int, float]]] = {c: [] for c in COHORTS}

        for idx, rec in enumerate(enriched_records):
            cohort_id, age_days, age_hours = assign_age_cohort(rec["published_at"], now_utc)
            rec["_temp_cohort"] = cohort_id
            rec["_temp_age_days"] = age_days
            rec["_temp_age_hours"] = age_hours
            cohort_groups[cohort_id].append((idx, float(rec["raw_data"]["view_count"])))

        # 2. Compute cohort summary medians
        cohort_summaries = {}
        for c_id, members in cohort_groups.items():
            if members:
                vals = [m[1] for m in members]
                cohort_summaries[c_id] = {
                    "count": len(members),
                    "median_views": float(statistics.median(vals)),
                }
            else:
                cohort_summaries[c_id] = {"count": 0, "median_views": 0.0}

        # 3. Compute Leave-One-Out medians and multipliers
        processed_records = []
        candidates_for_handoff = []

        for idx, rec in enumerate(enriched_records):
            raw = rec["raw_data"]
            views = raw["view_count"]
            cohort_id = rec["_temp_cohort"]
            age_days = rec["_temp_age_days"]
            age_hours = rec["_temp_age_hours"]

            # Global Leave-One-Out Median
            global_loo_med = calculate_leave_one_out_median(all_views, idx)
            global_multiplier = round(views / max(global_loo_med, 1.0), 2)

            # Cohort Leave-One-Out Median
            c_members = cohort_groups[cohort_id]
            c_views = [m[1] for m in c_members]
            c_idx_within_cohort = [m[0] for m in c_members].index(idx)
            cohort_loo_med = calculate_leave_one_out_median(c_views, c_idx_within_cohort)
            cohort_multiplier = round(views / max(cohort_loo_med, 1.0), 2)

            # Lifetime VPH
            lt_vph = calculate_lifetime_vph(views, age_hours)

            # Snapshot VPH (if previous snapshot available)
            snap_vph = None
            if rec["video_id"] in prev_views_map:
                prev_v, prev_t = prev_views_map[rec["video_id"]]
                snap_vph = calculate_snapshot_vph(views, prev_v, now_utc, prev_t)

            # Floor validation
            floor_cleared = (views >= self.min_floor_views)

            # Classification
            effective_multiplier = max(cohort_multiplier, global_multiplier)
            if effective_multiplier >= 5.0 and floor_cleared:
                classification = "MEGA_OUTLIER"
                handoff_action = "EXTRACT_HOOK_AND_MINE_COMMENTS"
                priority = "HIGH"
            elif effective_multiplier >= self.multiplier_threshold and floor_cleared:
                classification = "STRONG_OUTLIER"
                handoff_action = "EXTRACT_HOOK_AND_MINE_COMMENTS"
                priority = "MEDIUM"
            elif effective_multiplier >= self.multiplier_threshold and not floor_cleared:
                classification = "SUB_FLOOR_OUTLIER_REJECTED"
                handoff_action = "SKIP_INSUFFICIENT_VIEWS"
                priority = "NONE"
            else:
                classification = "NORMAL_PERFORMER"
                handoff_action = "ARCHIVE_ONLY"
                priority = "LOW"

            record_entry = {
                "video_id": rec["video_id"],
                "title": rec["title"],
                "published_at": rec["published_at"],
                "url": rec["url"],
                "raw_data": raw,
                "shorts_inspection": rec.get("shorts_inspection", {}),
                "calculated_metrics": {
                    "age_days": age_days,
                    "age_hours": age_hours,
                    "cohort_id": cohort_id,
                    "cohort_median_loo": round(cohort_loo_med, 2),
                    "global_median_loo": round(global_loo_med, 2),
                    "outlier_multiplier_cohort": cohort_multiplier,
                    "outlier_multiplier_global": global_multiplier,
                    "effective_multiplier": effective_multiplier,
                    "lifetime_vph": lt_vph,
                    "snapshot_vph": snap_vph,
                    "floor_cleared": floor_cleared,
                    "classification": classification,
                },
                "handoff_directives": {
                    "action": handoff_action,
                    "priority": priority,
                    "reason": f"Classified as {classification} (Multiplier: {effective_multiplier}x, Views: {views}, Floor Cleared: {floor_cleared})",
                }
            }
            processed_records.append(record_entry)

            if handoff_action == "EXTRACT_HOOK_AND_MINE_COMMENTS":
                candidates_for_handoff.append(record_entry)

        return {
            "processed_records": processed_records,
            "candidates": candidates_for_handoff,
            "cohort_summaries": cohort_summaries,
            "global_median_raw": float(statistics.median(all_views)) if all_views else 0.0,
        }
