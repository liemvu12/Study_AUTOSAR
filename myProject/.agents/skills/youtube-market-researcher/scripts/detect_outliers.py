#!/usr/bin/env python3
"""
detect_outliers.py - Algorithmic YouTube Outlier Video Detector
Calculates Channel Median Baseline and identifies breakout videos (Multiplier >= 2.5x).
"""

import argparse
import json
import sys
import numpy as np
import pandas as pd


def classify_multiplier(mult):
    if mult >= 5.0:
        return "MEGA_OUTLIER (>= 5.0x)"
    elif mult >= 2.5:
        return "STRONG_OUTLIER (>= 2.5x)"
    elif mult >= 1.3:
        return "ABOVE_AVERAGE (>= 1.3x)"
    elif mult >= 0.7:
        return "BASELINE (0.7x - 1.3x)"
    else:
        return "UNDERPERFORMING (< 0.7x)"


def analyze_outliers(videos_data, min_multiplier=2.5):
    if not videos_data:
        return {"error": "Empty video dataset"}

    df = pd.DataFrame(videos_data)
    if "views" not in df.columns or len(df) == 0:
        return {"error": "No 'views' column found in data"}

    # Filter out videos with 0 views if needed, or keep
    valid_views = df[df["views"] > 0]["views"]
    if len(valid_views) == 0:
        median_views = 1
        mean_views = 0
    else:
        median_views = float(valid_views.median())
        mean_views = float(valid_views.mean())

    baseline = max(median_views, 1.0)
    df["outlier_multiplier"] = (df["views"] / baseline).round(2)
    df["tier"] = df["outlier_multiplier"].apply(classify_multiplier)

    outliers = df[df["outlier_multiplier"] >= min_multiplier].sort_values(
        by="outlier_multiplier", ascending=False
    )

    stats = {
        "total_videos_analyzed": len(df),
        "channel_median_views": int(median_views),
        "channel_mean_views": int(mean_views),
        "outlier_threshold_used": min_multiplier,
        "outliers_count": len(outliers),
        "outliers_ratio_percent": round((len(outliers) / len(df)) * 100, 1) if len(df) > 0 else 0,
        "top_outliers": outliers.to_dict(orient="records"),
        "all_videos_ranked": df.sort_values(by="outlier_multiplier", ascending=False).to_dict(orient="records")
    }
    return stats


def format_markdown_report(stats):
    lines = []
    lines.append("# YouTube Outlier Detection Report")
    lines.append(f"- **Total Videos Analyzed:** {stats['total_videos_analyzed']}")
    lines.append(f"- **Channel Median Views (True Baseline):** {stats['channel_median_views']:,}")
    lines.append(f"- **Channel Mean Views:** {stats['channel_mean_views']:,}")
    lines.append(f"- **Outliers Detected (Multiplier >= {stats['outlier_threshold_used']}x):** {stats['outliers_count']} videos ({stats['outliers_ratio_percent']}%)")
    lines.append("")
    lines.append("## Top Breakout Outlier Videos")
    lines.append("| Multiplier | Tier | Views | Title | Published | Video URL |")
    lines.append("| :--- | :--- | :--- | :--- | :--- | :--- |")

    for v in stats["top_outliers"]:
        lines.append(f"| **{v['outlier_multiplier']}x** | {v['tier']} | {v['views']:,} | {v['title'][:60]} | {v.get('published', 'N/A')} | [Watch]({v['url']}) |")

    if not stats["top_outliers"]:
        lines.append("*No outlier videos found matching the multiplier threshold.*")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Detect breakout outlier videos from JSON dataset.")
    parser.add_argument("--input", "-i", required=True, help="Input JSON file path from fetch_channel.py")
    parser.add_argument("--threshold", "-t", type=float, default=2.5, help="Multiplier threshold (default: 2.5x)")
    parser.add_argument("--output", "-o", default=None, help="Output file path (.json or .md). Default: stdout Markdown")

    args = parser.parse_args()

    try:
        with open(args.input, "r", encoding="utf-8") as f:
            videos_data = json.load(f)
    except Exception as e:
        print(f"[!] Error reading input file: {e}", file=sys.stderr)
        sys.exit(1)

    stats = analyze_outliers(videos_data, min_multiplier=args.threshold)

    if args.output:
        if args.output.endswith(".md"):
            report = format_markdown_report(stats)
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(report)
            print(f"[+] Exported Markdown report to {args.output}", file=sys.stderr)
        else:
            with open(args.output, "w", encoding="utf-8") as f:
                json.dump(stats, f, ensure_ascii=False, indent=2)
            print(f"[+] Exported JSON report to {args.output}", file=sys.stderr)
    else:
        print(format_markdown_report(stats))


if __name__ == "__main__":
    main()
