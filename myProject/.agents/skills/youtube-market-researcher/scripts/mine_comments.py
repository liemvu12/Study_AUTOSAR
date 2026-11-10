#!/usr/bin/env python3
"""
mine_comments.py - Audience Pain-Point & Feature Request Miner
Downloads high-engagement YouTube comments and identifies recurring questions, criticisms, and content requests.
"""

import argparse
from itertools import islice
import json
import re
import sys
from youtube_comment_downloader import YoutubeCommentDownloader, SORT_BY_POPULAR


PAIN_POINT_PATTERNS = [
    r"\?",
    r"\b(how|why|can you|could you|please make|wish|request|waiting for)\b",
    r"\b(tại sao|làm sao|thế nào|bao giờ|khi nào|ước gì|mong|làm tiếp|phần 2)\b"
]

CRITICISM_PATTERNS = [
    r"\b(too fast|too loud|boring|scary|annoying|hate|bad|cringe|fix)\b",
    r"\b(quá nhanh|quá to|ồn|sợ|nhảm|chán|khó chịu|ghét|dở)\b"
]


def classify_comment_intent(text):
    lower = text.lower()
    is_pain_or_request = any(re.search(p, lower) for p in PAIN_POINT_PATTERNS)
    is_criticism = any(re.search(p, lower) for p in CRITICISM_PATTERNS)

    if is_pain_or_request and is_criticism:
        return "CRITIQUE_AND_REQUEST"
    elif is_pain_or_request:
        return "AUDIENCE_REQUEST_OR_QUESTION"
    elif is_criticism:
        return "OBJECTION_OR_FRICTION"
    else:
        return "GENERAL_FEEDBACK"


def mine_comments(video_url_or_id, limit=100):
    if not (video_url_or_id.startswith("http://") or video_url_or_id.startswith("https://")):
        url = f"https://www.youtube.com/watch?v={video_url_or_id}"
    else:
        url = video_url_or_id

    print(f"[*] Mining top comments from: {url} (Limit: {limit}, Sorted by: Popular)...", file=sys.stderr)

    downloader = YoutubeCommentDownloader()
    comments = []

    try:
        raw_comments = downloader.get_comments_from_url(url, sort_by=SORT_BY_POPULAR)
        for c in islice(raw_comments, limit):
            votes_raw = c.get("votes", 0)
            votes = int(votes_raw) if str(votes_raw).isdigit() else 0
            text = c.get("text", "")
            author = c.get("author", "Anonymous")
            time_str = c.get("time", "")

            intent = classify_comment_intent(text)

            comments.append({
                "author": author,
                "votes": votes,
                "time": time_str,
                "intent": intent,
                "text": text
            })
    except Exception as e:
        print(f"[!] Error mining comments: {e}", file=sys.stderr)
        return {"error": str(e), "comments": []}

    print(f"[+] Successfully extracted {len(comments)} comments.", file=sys.stderr)

    # Filter out requests & pain points
    requests_and_questions = [c for c in comments if c["intent"] in ["AUDIENCE_REQUEST_OR_QUESTION", "CRITIQUE_AND_REQUEST"]]
    frictions = [c for c in comments if c["intent"] in ["OBJECTION_OR_FRICTION", "CRITIQUE_AND_REQUEST"]]

    return {
        "source_url": url,
        "total_mined": len(comments),
        "requests_found_count": len(requests_and_questions),
        "objections_found_count": len(frictions),
        "high_priority_requests": sorted(requests_and_questions, key=lambda x: x["votes"], reverse=True)[:15],
        "top_friction_points": sorted(frictions, key=lambda x: x["votes"], reverse=True)[:15],
        "all_comments_ranked": sorted(comments, key=lambda x: x["votes"], reverse=True)
    }


def main():
    parser = argparse.ArgumentParser(description="Mine YouTube comments for audience pain-points and feature requests.")
    parser.add_argument("--video", "-v", required=True, help="YouTube Video URL or Video ID")
    parser.add_argument("--limit", "-l", type=int, default=100, help="Max comments to fetch (default: 100)")
    parser.add_argument("--output", "-o", default=None, help="Output file path (.json). Default: stdout JSON")

    args = parser.parse_args()
    data = mine_comments(args.video, limit=args.limit)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"[+] Exported comments analysis to {args.output}", file=sys.stderr)
    else:
        print(json.dumps(data, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
