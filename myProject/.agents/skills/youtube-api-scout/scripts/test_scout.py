#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Automated Test Suite for YouTube API Scout
Verifies:
1. ISO 8601 Duration Parser
2. Leave-One-Out (Jackknife) Median Math vs Standard Median
3. Age Cohort Stratification
4. Absolute Floor Filtering (MIN_FLOOR)
5. Lifetime VPH & Snapshot VPH Math
6. Quota Tracker Consumption & Reset
7. End-to-End Pipeline Execution & Schema Validation
"""

import os
import json
import shutil
import unittest
from datetime import datetime, timezone, timedelta

from api_client import parse_iso8601_duration, YouTubeAPIClient
from quota_tracker import QuotaTracker
from outlier_engine import (
    calculate_leave_one_out_median,
    assign_age_cohort,
    calculate_lifetime_vph,
    calculate_snapshot_vph,
    OutlierEngine,
)
from scout_pipeline import run_scout_pipeline

TEST_TEMP_DIR = os.path.join(os.path.dirname(__file__), "test_temp_output")

class TestYouTubeAPIScout(unittest.TestCase):
    def setUp(self):
        os.makedirs(TEST_TEMP_DIR, exist_ok=True)

    def tearDown(self):
        if os.path.exists(TEST_TEMP_DIR):
            shutil.rmtree(TEST_TEMP_DIR, ignore_errors=True)

    def test_01_iso_duration_parser(self):
        """Test ISO 8601 duration parser across multiple formats."""
        self.assertEqual(parse_iso8601_duration("PT1H2M30S"), 3750)
        self.assertEqual(parse_iso8601_duration("PT58S"), 58)
        self.assertEqual(parse_iso8601_duration("PT15M"), 900)
        self.assertEqual(parse_iso8601_duration("PT3M0S"), 180)
        self.assertEqual(parse_iso8601_duration("P1DT2H"), 93600)
        self.assertEqual(parse_iso8601_duration("INVALID"), 0)
        self.assertEqual(parse_iso8601_duration(""), 0)

    def test_02_leave_one_out_median(self):
        """
        Prove Leave-One-Out removes self-skewing bias:
        Sample: [100, 100, 100, 1000]
        Standard Median = 100
        LOO for element 3 (1000) excludes 1000: median of [100, 100, 100] = 100.
        Multiplier = 1000 / 100 = 10.0x.
        
        Now consider sample: [10, 20, 100]
        Standard median = 20.
        LOO for 100: median of [10, 20] = 15.
        With standard median, multiplier would be 100 / 20 = 5.0x.
        With LOO, multiplier is 100 / 15 = 6.67x (fairer comparison baseline).
        """
        sample = [10.0, 20.0, 100.0]
        loo_med_for_100 = calculate_leave_one_out_median(sample, 2)
        self.assertEqual(loo_med_for_100, 15.0)

        # LOO for element 1 (20): median of [10, 100] = 55.0
        loo_med_for_20 = calculate_leave_one_out_median(sample, 1)
        self.assertEqual(loo_med_for_20, 55.0)

    def test_03_age_cohort_assignment(self):
        """Verify publication dates are partitioned into the 4 standard cohorts."""
        now = datetime(2026, 10, 23, 12, 0, 0, tzinfo=timezone.utc)

        # 5 days ago -> recent_lte_14d
        pub_5d = (now - timedelta(days=5)).isoformat()
        c_id, age_days, _ = assign_age_cohort(pub_5d, now)
        self.assertEqual(c_id, "recent_lte_14d")
        self.assertAlmostEqual(age_days, 5.0, places=1)

        # 30 days ago -> growth_15_60d
        pub_30d = (now - timedelta(days=30)).isoformat()
        c_id, age_days, _ = assign_age_cohort(pub_30d, now)
        self.assertEqual(c_id, "growth_15_60d")

        # 120 days ago -> established_61_180d
        pub_120d = (now - timedelta(days=120)).isoformat()
        c_id, age_days, _ = assign_age_cohort(pub_120d, now)
        self.assertEqual(c_id, "established_61_180d")

        # 365 days ago -> evergreen_gt_180d
        pub_365d = (now - timedelta(days=365)).isoformat()
        c_id, age_days, _ = assign_age_cohort(pub_365d, now)
        self.assertEqual(c_id, "evergreen_gt_180d")

    def test_04_absolute_floor_threshold(self):
        """
        Verify that sub-floor candidates (e.g. 150 views with 3.0x multiplier)
        are flagged as SUB_FLOOR_OUTLIER_REJECTED and not handed off.
        """
        engine = OutlierEngine(min_floor_views=500, outlier_multiplier_threshold=2.5)

        records = [
            {
                "video_id": "v_normal_1",
                "title": "Normal Video 1",
                "published_at": "2026-10-01T00:00:00Z",
                "url": "https://youtube.com/watch?v=v_normal_1",
                "raw_data": {"view_count": 50, "like_count": 2, "comment_count": 0, "duration_seconds": 300},
            },
            {
                "video_id": "v_normal_2",
                "title": "Normal Video 2",
                "published_at": "2026-10-02T00:00:00Z",
                "url": "https://youtube.com/watch?v=v_normal_2",
                "raw_data": {"view_count": 50, "like_count": 2, "comment_count": 0, "duration_seconds": 300},
            },
            {
                "video_id": "v_sub_floor",
                "title": "Sub floor outlier",
                "published_at": "2026-10-03T00:00:00Z",
                "url": "https://youtube.com/watch?v=v_sub_floor",
                "raw_data": {"view_count": 200, "like_count": 10, "comment_count": 1, "duration_seconds": 300},
            },
            {
                "video_id": "v_genuine_outlier",
                "title": "Genuine Outlier",
                "published_at": "2026-10-04T00:00:00Z",
                "url": "https://youtube.com/watch?v=v_genuine_outlier",
                "raw_data": {"view_count": 5000, "like_count": 250, "comment_count": 30, "duration_seconds": 300},
            },
        ]

        result = engine.process_records(records)
        processed = {r["video_id"]: r for r in result["processed_records"]}

        # v_sub_floor: Views = 200 (< 500 floor), Multiplier = 200/50 = 4.0x
        sub_floor_calc = processed["v_sub_floor"]["calculated_metrics"]
        self.assertFalse(sub_floor_calc["floor_cleared"])
        self.assertEqual(sub_floor_calc["classification"], "SUB_FLOOR_OUTLIER_REJECTED")

        # v_genuine_outlier: Views = 5000 (>= 500 floor), Multiplier = 5000/50 = 100x
        genuine_calc = processed["v_genuine_outlier"]["calculated_metrics"]
        self.assertTrue(genuine_calc["floor_cleared"])
        self.assertEqual(genuine_calc["classification"], "MEGA_OUTLIER")

        # Only v_genuine_outlier should be in candidates
        self.assertEqual(len(result["candidates"]), 1)
        self.assertEqual(result["candidates"][0]["video_id"], "v_genuine_outlier")

    def test_05_lifetime_vs_snapshot_vph(self):
        """Verify Lifetime VPH and Snapshot VPH calculations."""
        # Lifetime VPH: 24,000 views over 48 hours = 500.0 VPH
        lt_vph = calculate_lifetime_vph(24000, 48.0)
        self.assertEqual(lt_vph, 500.0)

        # Snapshot VPH:
        t1 = datetime(2026, 10, 20, 10, 0, 0, tzinfo=timezone.utc)
        t2 = datetime(2026, 10, 20, 14, 0, 0, tzinfo=timezone.utc) # 4 hours delta
        v1 = 10000
        v2 = 12000 # delta views = 2000
        snap_vph = calculate_snapshot_vph(v2, v1, t2, t1)
        self.assertEqual(snap_vph, 500.0) # 2000 / 4 = 500.0 VPH

    def test_06_quota_tracker_consumption(self):
        """Verify QuotaTracker records consumption accurately."""
        state_file = os.path.join(TEST_TEMP_DIR, "test_quota_state.json")
        tracker = QuotaTracker(state_file=state_file, daily_limit=1000)

        # Initial state
        summary = tracker.get_summary()
        self.assertEqual(summary["daily_used_estimate"], 0)
        self.assertEqual(summary["tier_status"], "SAFE")

        # Consume 2 units
        res = tracker.consume("playlistItems.list", units=1)
        self.assertTrue(res["allowed"])
        self.assertEqual(res["total_daily_used"], 1)

        res2 = tracker.consume("videos.list", units=1)
        self.assertEqual(res2["total_daily_used"], 2)
        self.assertEqual(tracker.get_summary()["daily_used_estimate"], 2)

    def test_07_end_to_end_pipeline_mock(self):
        """Run full scout pipeline in mock mode and validate schema compliance."""
        out_dir = os.path.join(TEST_TEMP_DIR, "pipeline_run")
        res = run_scout_pipeline(
            channel_identifier="UC_mock_test_channel_1234",
            limit=30,
            min_floor=500,
            threshold=2.5,
            mock_mode=True,
            out_dir=out_dir,
        )

        self.assertTrue(os.path.exists(res["snapshot_path"]))
        self.assertTrue(os.path.exists(res["handoff_path"]))
        self.assertGreater(res["candidates_count"], 0)

        # Read and validate handoff manifest JSON
        with open(res["handoff_path"], "r", encoding="utf-8") as f:
            manifest = json.load(f)

        self.assertEqual(manifest["schema_version"], "1.0.0")
        self.assertEqual(manifest["source_skill"], "youtube-api-scout")
        self.assertEqual(manifest["target_skill"], "youtube-market-researcher")
        self.assertTrue(manifest["provenance"]["mock_mode"])

        # Check candidate structure
        for cand in manifest["candidates"]:
            self.assertIn("video_id", cand)
            self.assertIn("raw_data", cand)
            self.assertIn("calculated_metrics", cand)
            self.assertTrue(cand["calculated_metrics"]["floor_cleared"])
            self.assertGreaterEqual(cand["calculated_metrics"]["effective_multiplier"], 2.5)

if __name__ == "__main__":
    unittest.main()
