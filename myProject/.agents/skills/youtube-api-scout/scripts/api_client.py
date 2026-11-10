#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Robust YouTube Data API v3 Client
Optimized for minimum quota expenditure:
- Derives Uploads Playlist ID (UC -> UU) for 0 quota units.
- Fetches videos via playlistItems.list (1 unit per 50 items).
- Enriches metadata via batch videos.list (1 unit per 50 items).
- Includes ISO 8601 duration parser and offline mock generator.
"""

import os
import re
import json
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional, Tuple

try:
    import requests
except ImportError:
    requests = None

from quota_tracker import QuotaTracker

logger = logging.getLogger("YouTubeAPIClient")

YOUTUBE_API_BASE = "https://www.googleapis.com/youtube/v3"

def parse_iso8601_duration(duration_str: str) -> int:
    """
    Parses an ISO 8601 duration string (e.g. 'PT1H2M30S', 'PT45S', 'PT12M') into seconds.
    """
    if not duration_str or not duration_str.startswith("P"):
        return 0

    pattern = re.compile(
        r"P(?:(?P<days>\d+)D)?"
        r"(?:T(?:(?P<hours>\d+)H)?(?:(?P<minutes>\d+)M)?(?:(?P<seconds>\d+)S)?)?"
    )
    match = pattern.match(duration_str)
    if not match:
        return 0

    parts = match.groupdict()
    days = int(parts.get("days") or 0)
    hours = int(parts.get("hours") or 0)
    minutes = int(parts.get("minutes") or 0)
    seconds = int(parts.get("seconds") or 0)

    return days * 86400 + hours * 3600 + minutes * 60 + seconds

def load_env_file_if_present() -> None:
    """
    Lightweight .env loader without third-party dependencies.
    Searches current working directory and skill folders.
    """
    candidates = [
        os.path.join(os.getcwd(), ".env"),
        os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".env")),
        os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".env")),
    ]
    for env_path in candidates:
        if os.path.isfile(env_path):
            try:
                with open(env_path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#") and "=" in line:
                            k, v = line.split("=", 1)
                            k = k.strip()
                            v = v.strip().strip('"').strip("'")
                            if k and k not in os.environ:
                                os.environ[k] = v
                break
            except Exception:
                pass

class YouTubeAPIClient:
    def __init__(
        self,
        api_key: Optional[str] = None,
        quota_tracker: Optional[QuotaTracker] = None,
        mock_mode: bool = False,
    ):
        load_env_file_if_present()
        self.api_key = api_key or os.environ.get("YOUTUBE_API_KEY", "").strip()
        self.mock_mode = mock_mode or (not self.api_key)
        self.quota_tracker = quota_tracker or QuotaTracker()

        if self.mock_mode and not api_key:
            logger.info("No API Key detected. Initializing client in MOCK/OFFLINE mode.")

    def derive_uploads_playlist_id(self, channel_id: str) -> Optional[str]:
        """
        Derives uploads playlist ID by swapping prefix 'UC' -> 'UU'.
        Cost: 0 Quota Units!
        """
        if channel_id and channel_id.startswith("UC") and len(channel_id) == 24:
            return "UU" + channel_id[2:]
        return None

    def resolve_channel(self, identifier: str) -> Dict[str, Any]:
        """
        Resolves channel identifier (URL, @handle, or ID) to Channel Details.
        """
        clean_id = identifier.strip()
        if "youtube.com/channel/" in clean_id:
            clean_id = clean_id.split("youtube.com/channel/")[1].split("/")[0].split("?")[0]
        elif "youtube.com/@" in clean_id:
            clean_id = "@" + clean_id.split("youtube.com/@")[1].split("/")[0].split("?")[0]

        if self.mock_mode:
            channel_id = clean_id if clean_id.startswith("UC") else f"UC_mock_{abs(hash(clean_id)) % 1000000000:09d}"
            uploads_id = self.derive_uploads_playlist_id(channel_id) or f"UU_mock_{abs(hash(clean_id)) % 1000000000:09d}"
            return {
                "channel_id": channel_id,
                "uploads_playlist_id": uploads_id,
                "title": f"Mock Channel for {identifier}",
                "handle": clean_id if clean_id.startswith("@") else f"@{clean_id}",
                "custom_url": f"https://www.youtube.com/{clean_id}",
                "raw_metrics": {
                    "subscriber_count": 50000,
                    "video_count": 120,
                    "view_count": 10000000,
                },
                "is_mock": True,
            }

        # Check if clean_id is already a 24-char UC channel ID
        if clean_id.startswith("UC") and len(clean_id) == 24:
            uploads_id = self.derive_uploads_playlist_id(clean_id)
            # Fetch channel snippet & statistics (1 unit)
            return self._fetch_channel_by_id(clean_id, uploads_id)

        # Handle lookup
        if clean_id.startswith("@"):
            return self._fetch_channel_by_handle(clean_id[1:])

        # Fallback to general channel id lookup
        return self._fetch_channel_by_id(clean_id)

    def _fetch_channel_by_id(self, channel_id: str, known_uploads_id: Optional[str] = None) -> Dict[str, Any]:
        can_run, msg = self.quota_tracker.can_consume(1)
        if not can_run:
            raise RuntimeError(f"Quota budget exhausted: {msg}")

        url = f"{YOUTUBE_API_BASE}/channels"
        params = {
            "part": "snippet,contentDetails,statistics",
            "id": channel_id,
            "key": self.api_key,
        }
        resp = requests.get(url, params=params, timeout=15)
        self.quota_tracker.consume("channels.list", units=1, description=f"Fetch channel {channel_id}")

        if resp.status_code != 200:
            raise RuntimeError(f"API Error ({resp.status_code}): {resp.text}")

        data = resp.json()
        items = data.get("items", [])
        if not items:
            raise ValueError(f"Channel not found: {channel_id}")

        item = items[0]
        snippet = item.get("snippet", {})
        stats = item.get("statistics", {})
        content = item.get("contentDetails", {})
        uploads_id = known_uploads_id or content.get("relatedPlaylists", {}).get("uploads")

        return {
            "channel_id": item.get("id"),
            "uploads_playlist_id": uploads_id,
            "title": snippet.get("title", ""),
            "handle": snippet.get("customUrl", ""),
            "custom_url": f"https://www.youtube.com/{snippet.get('customUrl', '')}",
            "raw_metrics": {
                "subscriber_count": int(stats.get("subscriberCount", 0)),
                "video_count": int(stats.get("videoCount", 0)),
                "view_count": int(stats.get("viewCount", 0)),
            },
            "is_mock": False,
        }

    def _fetch_channel_by_handle(self, handle: str) -> Dict[str, Any]:
        can_run, msg = self.quota_tracker.can_consume(1)
        if not can_run:
            raise RuntimeError(f"Quota budget exhausted: {msg}")

        url = f"{YOUTUBE_API_BASE}/channels"
        params = {
            "part": "snippet,contentDetails,statistics",
            "forHandle": handle,
            "key": self.api_key,
        }
        resp = requests.get(url, params=params, timeout=15)
        self.quota_tracker.consume("channels.list", units=1, description=f"Fetch channel handle @{handle}")

        if resp.status_code != 200:
            raise RuntimeError(f"API Error ({resp.status_code}): {resp.text}")

        data = resp.json()
        items = data.get("items", [])
        if not items:
            raise ValueError(f"Channel not found for handle: @{handle}")

        item = items[0]
        snippet = item.get("snippet", {})
        stats = item.get("statistics", {})
        content = item.get("contentDetails", {})
        uploads_id = content.get("relatedPlaylists", {}).get("uploads") or self.derive_uploads_playlist_id(item.get("id"))

        return {
            "channel_id": item.get("id"),
            "uploads_playlist_id": uploads_id,
            "title": snippet.get("title", ""),
            "handle": snippet.get("customUrl", f"@{handle}"),
            "custom_url": f"https://www.youtube.com/{snippet.get('customUrl', '@' + handle)}",
            "raw_metrics": {
                "subscriber_count": int(stats.get("subscriberCount", 0)),
                "video_count": int(stats.get("videoCount", 0)),
                "view_count": int(stats.get("viewCount", 0)),
            },
            "is_mock": False,
        }

    def fetch_playlist_video_ids(self, uploads_playlist_id: str, limit: int = 50) -> List[str]:
        """
        Fetches up to `limit` video IDs from the uploads playlist using playlistItems.list.
        Costs 1 unit per 50 items.
        """
        if self.mock_mode:
            return [f"mock_vid_{i:03d}" for i in range(1, limit + 1)]

        video_ids = []
        next_page_token = None

        while len(video_ids) < limit:
            can_run, msg = self.quota_tracker.can_consume(1)
            if not can_run:
                logger.warning(f"Quota limit reached during playlist fetch: {msg}")
                break

            max_batch = min(50, limit - len(video_ids))
            url = f"{YOUTUBE_API_BASE}/playlistItems"
            params = {
                "part": "contentDetails",
                "playlistId": uploads_playlist_id,
                "maxResults": max_batch,
                "key": self.api_key,
            }
            if next_page_token:
                params["pageToken"] = next_page_token

            resp = requests.get(url, params=params, timeout=15)
            self.quota_tracker.consume("playlistItems.list", units=1, description=f"Fetch {max_batch} playlist items")

            if resp.status_code != 200:
                logger.error(f"Error fetching playlistItems ({resp.status_code}): {resp.text}")
                break

            data = resp.json()
            for item in data.get("items", []):
                vid = item.get("contentDetails", {}).get("videoId")
                if vid:
                    video_ids.append(vid)

            next_page_token = data.get("nextPageToken")
            if not next_page_token:
                break

        return video_ids

    def batch_enrich_videos(self, video_ids: List[str]) -> List[Dict[str, Any]]:
        """
        Enriches a list of video IDs in batches of up to 50 via videos.list.
        Costs 1 unit per 50 items.
        """
        if not video_ids:
            return []

        if self.mock_mode:
            return self._generate_mock_enriched_videos(video_ids)

        enriched_records = []
        batch_size = 50

        for i in range(0, len(video_ids), batch_size):
            chunk = video_ids[i:i + batch_size]
            can_run, msg = self.quota_tracker.can_consume(1)
            if not can_run:
                logger.warning(f"Quota limit reached during video enrichment: {msg}")
                break

            url = f"{YOUTUBE_API_BASE}/videos"
            params = {
                "part": "snippet,contentDetails,statistics",
                "id": ",".join(chunk),
                "key": self.api_key,
            }
            resp = requests.get(url, params=params, timeout=15)
            self.quota_tracker.consume("videos.list", units=1, description=f"Enrich batch of {len(chunk)} videos")

            if resp.status_code != 200:
                logger.error(f"Error enriching videos ({resp.status_code}): {resp.text}")
                continue

            data = resp.json()
            for item in data.get("items", []):
                snippet = item.get("snippet", {})
                content = item.get("contentDetails", {})
                stats = item.get("statistics", {})

                iso_duration = content.get("duration", "PT0S")
                duration_sec = parse_iso8601_duration(iso_duration)

                is_shorts_cand = (duration_sec <= 180 and duration_sec > 0)
                shorts_method = (
                    "DURATION_LTE_180S_PENDING_ENDPOINT_OR_ASPECT_RATIO_CHECK"
                    if is_shorts_cand else "DURATION_GT_180S"
                )

                enriched_records.append({
                    "video_id": item.get("id"),
                    "title": snippet.get("title", ""),
                    "published_at": snippet.get("publishedAt", ""),
                    "url": f"https://www.youtube.com/watch?v={item.get('id')}",
                    "raw_data": {
                        "view_count": int(stats.get("viewCount", 0)),
                        "like_count": int(stats.get("likeCount", 0)),
                        "comment_count": int(stats.get("commentCount", 0)),
                        "iso_duration": iso_duration,
                        "duration_seconds": duration_sec,
                    },
                    "shorts_inspection": {
                        "is_shorts_candidate": is_shorts_cand,
                        "method": shorts_method,
                        "certainty": "PROBABILISTIC_DURATION_ONLY",
                    }
                })

        return enriched_records

    def _generate_mock_enriched_videos(self, video_ids: List[str]) -> List[Dict[str, Any]]:
        """
        Generates deterministic, realistic mock video data for offline testing.
        Includes a variety of age cohorts, typical views (median ~5,000),
        and 2-3 genuine outliers (including one >= 5.0x Mega Outlier).
        """
        now = datetime.now(timezone.utc)
        records = []

        # Synthetic profile for deterministic testing:
        # Most videos around 3,000 - 6,000 views.
        # Video 5: Outlier with 45,000 views (Cohort growth 15-60d)
        # Video 12: Outlier with 78,000 views (Cohort recent <= 14d)
        # Video 20: Sub-floor outlier (12 views on 2 median) to test floor rejection
        for idx, vid in enumerate(video_ids):
            # Spread publication dates
            days_ago = (idx * 5) + 1
            pub_date = now - timedelta(days=days_ago)

            if idx == 4:
                # Strong Outlier
                views = 48500
                likes = 2300
                comments = 320
                duration_sec = 620
                iso_dur = "PT10M20S"
            elif idx == 11:
                # Mega Outlier
                views = 92000
                likes = 5100
                comments = 740
                duration_sec = 485
                iso_dur = "PT8M5S"
            elif idx == 19:
                # Sub-floor candidate (testing floor rejection)
                views = 150
                likes = 8
                comments = 1
                duration_sec = 310
                iso_dur = "PT5M10S"
            elif idx == 25:
                # Shorts candidate (<= 180s)
                views = 8500
                likes = 450
                comments = 30
                duration_sec = 58
                iso_dur = "PT58S"
            else:
                base_views = 3500 + ((idx * 137) % 2500)
                views = base_views
                likes = int(views * 0.04)
                comments = int(views * 0.005)
                duration_sec = 420 + (idx * 15)
                iso_dur = f"PT{duration_sec // 60}M{duration_sec % 60}S"

            is_shorts = (duration_sec <= 180 and duration_sec > 0)
            records.append({
                "video_id": vid,
                "title": f"Video Title {idx + 1} - Production Topic",
                "published_at": pub_date.isoformat(),
                "url": f"https://www.youtube.com/watch?v={vid}",
                "raw_data": {
                    "view_count": views,
                    "like_count": likes,
                    "comment_count": comments,
                    "iso_duration": iso_dur,
                    "duration_seconds": duration_sec,
                },
                "shorts_inspection": {
                    "is_shorts_candidate": is_shorts,
                    "method": "DURATION_LTE_180S_PENDING_ENDPOINT_OR_ASPECT_RATIO_CHECK" if is_shorts else "DURATION_GT_180S",
                    "certainty": "PROBABILISTIC_DURATION_ONLY",
                }
            })

        return records
