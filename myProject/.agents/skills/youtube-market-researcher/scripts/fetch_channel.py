#!/usr/bin/env python3
"""
fetch_channel.py - Zero-Quota YouTube Channel Video Scraper
Uses scrapetube (no Google API key required) to pull video catalogs from channels, playlists, or search queries.
"""

import argparse
import json
import re
import sys
import scrapetube
import pandas as pd


def parse_view_count(text):
    if not text:
        return 0
    text = text.strip().replace(",", "").replace(".", "")
    # Check for formats like "1.2M views", "450K views", "123456 lượt xem"
    # Match standard digits
    match = re.search(r"(\d+)", text)
    if not match:
        return 0
    return int(match.group(1))


def scrape_channel_videos(channel_identifier, limit=50, sort_by="newest"):
    """
    Fetch videos from a channel using scrapetube.
    channel_identifier can be URL, handle (@username), or channel ID.
    sort_by: 'newest', 'popular', 'oldest'
    """
    kwargs = {"limit": limit, "sort_by": sort_by}
    
    if channel_identifier.startswith("http://") or channel_identifier.startswith("https://"):
        kwargs["channel_url"] = channel_identifier
    elif channel_identifier.startswith("@"):
        kwargs["channel_url"] = f"https://www.youtube.com/{channel_identifier}"
    elif channel_identifier.startswith("UC"):
        kwargs["channel_id"] = channel_identifier
    else:
        # Default try as username / custom name
        kwargs["channel_username"] = channel_identifier

    print(f"[*] Scraping channel: {channel_identifier} (Limit: {limit}, Sort: {sort_by})...", file=sys.stderr)
    
    videos = []
    try:
        raw_generator = scrapetube.get_channel(**kwargs)
        for vid in raw_generator:
            video_id = vid.get("videoId", "")
            
            # Extract title
            title = ""
            if "title" in vid and "runs" in vid["title"] and vid["title"]["runs"]:
                title = vid["title"]["runs"][0].get("text", "")
            elif "title" in vid and "simpleText" in vid["title"]:
                title = vid["title"]["simpleText"]
                
            # Extract view count
            views = 0
            view_text = vid.get("viewCountText", {}).get("simpleText", "")
            if not view_text and "shortViewCountText" in vid:
                view_text = vid.get("shortViewCountText", {}).get("simpleText", "")
            views = parse_view_count(view_text)

            # Published time
            published = vid.get("publishedTimeText", {}).get("simpleText", "N/A")
            
            # Duration
            duration = vid.get("lengthText", {}).get("simpleText", "N/A")
            
            # Thumbnail URL
            thumbnail = f"https://i.ytimg.com/vi/{video_id}/maxresdefault.jpg"

            videos.append({
                "video_id": video_id,
                "title": title,
                "views": views,
                "view_raw_text": view_text,
                "published": published,
                "duration": duration,
                "url": f"https://www.youtube.com/watch?v={video_id}",
                "thumbnail_url": thumbnail
            })
            
            if len(videos) >= limit:
                break
                
    except Exception as e:
        print(f"[!] Error fetching channel: {e}", file=sys.stderr)
        return []

    print(f"[+] Successfully fetched {len(videos)} videos.", file=sys.stderr)
    return videos


def main():
    parser = argparse.ArgumentParser(description="Fetch YouTube channel videos without API key.")
    parser.add_argument("--channel", "-c", required=True, help="Channel URL, handle (@handle), or ID")
    parser.add_argument("--limit", "-l", type=int, default=50, help="Max number of videos to fetch (default: 50)")
    parser.add_argument("--sort", "-s", choices=["newest", "popular", "oldest"], default="newest", help="Sort order")
    parser.add_argument("--output", "-o", default=None, help="Output file path (.json or .csv). Default: stdout JSON")

    args = parser.parse_args()
    results = scrape_channel_videos(args.channel, limit=args.limit, sort_by=args.sort)

    if not results:
        sys.exit(1)

    if args.output:
        if args.output.endswith(".csv"):
            df = pd.DataFrame(results)
            df.to_csv(args.output, index=False, encoding="utf-8-sig")
            print(f"[+] Exported CSV to {args.output}", file=sys.stderr)
        else:
            with open(args.output, "w", encoding="utf-8") as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            print(f"[+] Exported JSON to {args.output}", file=sys.stderr)
    else:
        print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
