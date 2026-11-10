#!/usr/bin/env python3
"""
extract_hooks.py - YouTube Transcript & Script Hook Deconstructor
Extracts the first 15s, 30s, and 60s of spoken audio, calculates Words Per Minute (WPM) pacing,
and benchmarks against target audience archetypes.
"""

import argparse
import json
import re
import sys
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound


def extract_video_id(url_or_id):
    if len(url_or_id) == 11 and not ("/" in url_or_id or "?" in url_or_id):
        return url_or_id
    patterns = [
        r"(?:v=|\/)([0-9A-Za-z_-]{11}).*",
        r"youtu\.be\/([0-9A-Za-z_-]{11})"
    ]
    for p in patterns:
        m = re.search(p, url_or_id)
        if m:
            return m.group(1)
    return url_or_id


def evaluate_pacing(wpm, niche="general"):
    if wpm <= 0:
        return "NO_SPEECH_OR_MUSIC_ONLY"
    elif wpm < 100:
        return f"{wpm} WPM (Slow / Kid-friendly 1-4yo / Meditative)"
    elif 100 <= wpm <= 135:
        return f"{wpm} WPM (Standard Broadcast / Calm Explainer)"
    elif 135 < wpm <= 165:
        return f"{wpm} WPM (High Engagement / Modern Documentary)"
    else:
        return f"{wpm} WPM (Hyper-fast / Gen Z / TikTok-style)"


def deconstruct_script(video_id, preferred_langs=["vi", "en"]):
    clean_id = extract_video_id(video_id)
    print(f"[*] Extracting transcript for Video ID: {clean_id}...", file=sys.stderr)

    try:
        # Support both youtube-transcript-api >= 1.0 (instance .list) and < 1.0 (static .list_transcripts)
        if hasattr(YouTubeTranscriptApi, "list_transcripts"):
            transcript_list = YouTubeTranscriptApi.list_transcripts(clean_id)
        else:
            ytt_api = YouTubeTranscriptApi()
            transcript_list = ytt_api.list(clean_id)
        
        # Try to find transcript in preferred languages (manual or generated)
        transcript = None
        chosen_lang = "unknown"
        is_generated = False
        
        try:
            transcript = transcript_list.find_transcript(preferred_langs)
            chosen_lang = transcript.language_code
            is_generated = transcript.is_generated
        except NoTranscriptFound:
            # Fallback to the first available transcript
            for t in transcript_list:
                transcript = t
                chosen_lang = t.language_code
                is_generated = t.is_generated
                break

        if not transcript:
            return {"error": "No transcript available in any language", "video_id": clean_id}

        raw_entries = transcript.fetch()
        entries = []
        for e in raw_entries:
            if isinstance(e, dict):
                entries.append(e)
            else:
                entries.append({
                    "text": getattr(e, "text", ""),
                    "start": float(getattr(e, "start", 0.0)),
                    "duration": float(getattr(e, "duration", 0.0)),
                })
        
    except (TranscriptsDisabled, NoTranscriptFound) as e:
        return {"error": f"Transcripts unavailable: {str(e)}", "video_id": clean_id}
    except Exception as e:
        return {"error": f"Failed to retrieve transcript: {str(e)}", "video_id": clean_id}

    # Aggregate text segments
    hook_15s_items = [e["text"] for e in entries if e["start"] <= 15.0]
    hook_30s_items = [e["text"] for e in entries if e["start"] <= 30.0]
    hook_60s_items = [e["text"] for e in entries if e["start"] <= 60.0]
    full_text_items = [e["text"] for e in entries]

    hook_15s = " ".join(hook_15s_items).replace("\n", " ").strip()
    hook_30s = " ".join(hook_30s_items).replace("\n", " ").strip()
    hook_60s = " ".join(hook_60s_items).replace("\n", " ").strip()
    full_text = " ".join(full_text_items).replace("\n", " ").strip()

    total_duration = entries[-1]["start"] + entries[-1]["duration"] if entries else 0
    total_words = len(full_text.split())
    wpm = round((total_words / total_duration) * 60, 1) if total_duration > 0 else 0

    return {
        "video_id": clean_id,
        "video_url": f"https://www.youtube.com/watch?v={clean_id}",
        "language_detected": chosen_lang,
        "is_auto_generated": is_generated,
        "total_spoken_duration_seconds": round(total_duration, 1),
        "total_words": total_words,
        "words_per_minute_wpm": wpm,
        "pacing_classification": evaluate_pacing(wpm),
        "hook_first_15_seconds": hook_15s or "[No speech in first 15 seconds]",
        "hook_first_30_seconds": hook_30s or "[No speech in first 30 seconds]",
        "hook_first_60_seconds": hook_60s or "[No speech in first 60 seconds]",
        "full_transcript_sample": full_text[:500] + ("..." if len(full_text) > 500 else "")
    }


def main():
    parser = argparse.ArgumentParser(description="Deconstruct YouTube video hook and script pacing.")
    parser.add_argument("--video", "-v", required=True, help="YouTube Video URL or Video ID")
    parser.add_argument("--langs", "-l", nargs="+", default=["vi", "en"], help="Preferred language codes (default: vi en)")
    parser.add_argument("--output", "-o", default=None, help="Output file path (.json). Default: stdout JSON")

    args = parser.parse_args()
    data = deconstruct_script(args.video, preferred_langs=args.langs)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"[+] Exported script hook data to {args.output}", file=sys.stderr)
    else:
        print(json.dumps(data, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
