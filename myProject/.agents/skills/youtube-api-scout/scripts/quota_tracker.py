#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Local Quota Tracker for YouTube Data API v3
Tracks daily client-side quota unit consumption with Pacific Time (PT) midnight reset detection.
"""

import os
import json
import logging
from datetime import datetime, time, timedelta
from typing import Dict, Any, Tuple, Optional

try:
    import zoneinfo
    PT_TZ = zoneinfo.ZoneInfo("America/Los_Angeles")
except Exception:
    # Fallback to UTC-7 if tzdata is missing
    from datetime import timezone
    PT_TZ = timezone(timedelta(hours=-7))

logger = logging.getLogger("QuotaTracker")

DEFAULT_STATE_FILE = os.path.join(os.path.dirname(__file__), "quota_state.json")
DEFAULT_DAILY_LIMIT = 10000
DEFAULT_WARNING_THRESHOLD = 8000

# Quota unit cost matrix per Google Developer Docs
ENDPOINT_COSTS = {
    "channels.list": 1,
    "playlistItems.list": 1,
    "videos.list": 1,
    "commentThreads.list": 1,
    "search.list": 100,
    "subscriptions.list": 1,
}

class QuotaTracker:
    def __init__(
        self,
        state_file: str = DEFAULT_STATE_FILE,
        daily_limit: int = DEFAULT_DAILY_LIMIT,
        warning_threshold: int = DEFAULT_WARNING_THRESHOLD,
    ):
        self.state_file = state_file
        self.daily_limit = daily_limit
        self.warning_threshold = warning_threshold
        self.state = self._load_state()
        self._check_and_reset_if_needed()

    def _get_pt_now(self) -> datetime:
        return datetime.now(PT_TZ)

    def _get_next_pt_midnight(self, pt_now: datetime) -> datetime:
        tomorrow = pt_now.date() + timedelta(days=1)
        return datetime.combine(tomorrow, time.min, tzinfo=PT_TZ)

    def _load_state(self) -> Dict[str, Any]:
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Could not load quota state file, initializing fresh: {e}")
        
        pt_now = self._get_pt_now()
        return {
            "current_pt_date": pt_now.strftime("%Y-%m-%d"),
            "daily_used_estimate": 0,
            "daily_limit_budget": self.daily_limit,
            "calls_count": 0,
            "last_call_timestamp": None,
            "history": [],
            "call_log": [],
        }

    def _save_state(self) -> None:
        try:
            os.makedirs(os.path.dirname(os.path.abspath(self.state_file)), exist_ok=True)
            with open(self.state_file, "w", encoding="utf-8") as f:
                json.dump(self.state, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Failed to save quota state: {e}")

    def _check_and_reset_if_needed(self) -> bool:
        pt_now = self._get_pt_now()
        today_pt = pt_now.strftime("%Y-%m-%d")
        stored_date = self.state.get("current_pt_date")

        if stored_date != today_pt:
            # Archive previous day's record
            if stored_date is not None:
                self.state.setdefault("history", []).append({
                    "pt_date": stored_date,
                    "units_used": self.state.get("daily_used_estimate", 0),
                    "calls_count": self.state.get("calls_count", 0),
                })
                # Keep last 30 days history
                self.state["history"] = self.state["history"][-30:]

            logger.info(f"Pacific Time midnight passed. Resetting quota tracker: {stored_date} -> {today_pt}")
            self.state["current_pt_date"] = today_pt
            self.state["daily_used_estimate"] = 0
            self.state["calls_count"] = 0
            self.state["call_log"] = []
            self._save_state()
            return True
        return False

    def can_consume(self, units: int = 1) -> Tuple[bool, str]:
        self._check_and_reset_if_needed()
        current_used = self.state.get("daily_used_estimate", 0)
        projected = current_used + units

        if projected > self.daily_limit:
            return False, f"EXCEEDED: Projected {projected} > Daily Limit {self.daily_limit}"
        elif projected >= self.warning_threshold:
            return True, f"WARNING: Projected {projected} >= Warning Threshold {self.warning_threshold}"
        else:
            return True, f"OK: Projected {projected} / {self.daily_limit}"

    def consume(
        self,
        endpoint: str,
        units: Optional[int] = None,
        description: str = "",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        self._check_and_reset_if_needed()

        if units is None:
            units = ENDPOINT_COSTS.get(endpoint, 1)

        pt_now = self._get_pt_now()
        can_proceed, status_msg = self.can_consume(units)

        self.state["daily_used_estimate"] = self.state.get("daily_used_estimate", 0) + units
        self.state["calls_count"] = self.state.get("calls_count", 0) + 1
        self.state["last_call_timestamp"] = pt_now.isoformat()

        log_entry = {
            "timestamp": pt_now.isoformat(),
            "endpoint": endpoint,
            "units": units,
            "description": description,
            "metadata": metadata or {},
        }
        self.state.setdefault("call_log", []).append(log_entry)
        if len(self.state["call_log"]) > 1000:
            self.state["call_log"] = self.state["call_log"][-500:]

        self._save_state()

        return {
            "allowed": can_proceed,
            "status": status_msg,
            "units_consumed": units,
            "total_daily_used": self.state["daily_used_estimate"],
            "remaining_budget": max(0, self.daily_limit - self.state["daily_used_estimate"]),
            "current_pt_date": self.state["current_pt_date"],
        }

    def get_summary(self) -> Dict[str, Any]:
        self._check_and_reset_if_needed()
        pt_now = self._get_pt_now()
        next_midnight = self._get_next_pt_midnight(pt_now)
        used = self.state.get("daily_used_estimate", 0)
        remaining = max(0, self.daily_limit - used)

        if used >= self.daily_limit:
            tier = "EXCEEDED"
        elif used >= self.warning_threshold:
            tier = "WARNING"
        else:
            tier = "SAFE"

        return {
            "client_side_estimate": True,
            "note": "Local estimate. Official usage is tracked server-side in Google Cloud Console.",
            "current_pt_time": pt_now.isoformat(),
            "current_pt_date": self.state.get("current_pt_date"),
            "next_pt_reset_utc": next_midnight.astimezone(zoneinfo.ZoneInfo("UTC")).isoformat() if hasattr(zoneinfo, "ZoneInfo") else next_midnight.isoformat(),
            "daily_limit_budget": self.daily_limit,
            "daily_used_estimate": used,
            "remaining_units": remaining,
            "percentage_used": round((used / self.daily_limit) * 100, 2),
            "tier_status": tier,
            "calls_count": self.state.get("calls_count", 0),
        }

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="YouTube API Local Quota Tracker")
    parser.add_argument("--status", action="store_true", help="Display current quota status")
    parser.add_argument("--consume", type=str, help="Simulate or record endpoint call (e.g. playlistItems.list)")
    parser.add_argument("--units", type=int, default=None, help="Explicit units to consume")
    args = parser.parse_args()

    tracker = QuotaTracker()
    if args.consume:
        res = tracker.consume(args.consume, units=args.units, description="CLI invocation")
        print(json.dumps(res, indent=2))
    else:
        print(json.dumps(tracker.get_summary(), indent=2))
