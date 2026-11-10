#!/usr/bin/env python3
"""
check_trends.py - YouTube Search Demand & Breakout Trend Validator
Uses pytrends with gprop='youtube' to analyze search momentum and identify rising breakout queries.
"""

import argparse
import json
import sys
import pandas as pd
from pytrends.request import TrendReq


def analyze_youtube_trend(keyword, timeframe="today 12-m", geo=""):
    print(f"[*] Querying YouTube Trend for '{keyword}' (Geo: '{geo or 'GLOBAL'}', Timeframe: '{timeframe}')...", file=sys.stderr)
    try:
        pytrends = TrendReq(hl="en-US", tz=360, timeout=(10, 25))
        pytrends.build_payload([keyword], cat=0, timeframe=timeframe, geo=geo, gprop="youtube")
        
        # 1. Interest over time
        df_interest = pytrends.interest_over_time()
        interest_history = []
        trend_direction = "UNKNOWN"
        
        if not df_interest.empty and keyword in df_interest.columns:
            series = df_interest[keyword]
            # Calculate simple trend direction (comparing last 20% vs first 20%)
            chunk_size = max(len(series) // 5, 1)
            start_avg = series.iloc[:chunk_size].mean()
            end_avg = series.iloc[-chunk_size:].mean()
            
            if end_avg >= start_avg * 1.25:
                trend_direction = "RISING / BULLISH (+25% growth)"
            elif end_avg <= start_avg * 0.75:
                trend_direction = "DECLINING / BEARISH (-25% drop)"
            else:
                trend_direction = "STABLE / EVERGREEN (within +/- 25%)"

            for date_idx, val in series.items():
                interest_history.append({
                    "date": date_idx.strftime("%Y-%m-%d"),
                    "interest_score": int(val)
                })

        # 2. Related queries
        related = pytrends.related_queries()
        rising_queries = []
        top_queries = []

        if keyword in related:
            rising_df = related[keyword].get("rising")
            if rising_df is not None and not rising_df.empty:
                for _, row in rising_df.iterrows():
                    val = row.get("value")
                    val_str = "Breakout (+5000%)" if val == 0 or val is None or str(val) == "Breakout" else f"+{val}%"
                    rising_queries.append({
                        "query": str(row.get("query")),
                        "growth": val_str
                    })

            top_df = related[keyword].get("top")
            if top_df is not None and not top_df.empty:
                for _, row in top_df.iterrows():
                    top_queries.append({
                        "query": str(row.get("query")),
                        "volume_score": int(row.get("value", 0))
                    })

        return {
            "keyword": keyword,
            "platform": "YouTube (gprop=youtube)",
            "timeframe": timeframe,
            "geo": geo or "GLOBAL",
            "trend_direction": trend_direction,
            "data_points_count": len(interest_history),
            "rising_breakout_queries": rising_queries[:15],
            "top_queries": top_queries[:15],
            "recent_interest_trend": interest_history[-10:] if interest_history else []
        }

    except Exception as e:
        print(f"[!] PyTrends Error (likely rate-limited by Google): {e}", file=sys.stderr)
        return {
            "keyword": keyword,
            "error": str(e),
            "advice": "Google Trends may rate-limit frequent requests. Try switching IP, waiting 5 minutes, or broadening search scope."
        }


def main():
    parser = argparse.ArgumentParser(description="Validate YouTube Search Trends and identify breakout topics.")
    parser.add_argument("--keyword", "-k", required=True, help="Keyword or topic to check")
    parser.add_argument("--timeframe", "-t", default="today 12-m", help="Timeframe (e.g. 'now 7-d', 'today 1-m', 'today 3-m', 'today 12-m')")
    parser.add_argument("--geo", "-g", default="", help="Country code (e.g. 'VN', 'US', or empty for global)")
    parser.add_argument("--output", "-o", default=None, help="Output file path (.json). Default: stdout JSON")

    args = parser.parse_args()
    data = analyze_youtube_trend(args.keyword, timeframe=args.timeframe, geo=args.geo)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"[+] Exported YouTube Trend data to {args.output}", file=sys.stderr)
    else:
        print(json.dumps(data, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
