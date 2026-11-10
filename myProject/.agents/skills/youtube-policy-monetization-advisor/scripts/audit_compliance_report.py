#!/usr/bin/env python3
"""
Audit script for YouTube Policy & Monetization Advisory reports.
Validates report structure, mandatory official sources, citation links,
risk classifications, and anti-hallucination labeling.
"""

import sys
import re
import argparse
from pathlib import Path

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

MANDATORY_SECTIONS = [
    "Executive Summary",
    "Official Sources Consulted",
    "Applicable YouTube Policies",
    "Evidence-Based Policy Analysis",
    "Risk Assessment",
    "Monetization Impact",
    "Actionable Compliance Blueprint",
    "Confidence Level"
]

MANDATORY_DOMAINS = [
    "support.google.com",
    "youtube.com",
]

FORBIDDEN_HEDGES = [
    r"\bchắc chắn kiếm được nhiều tiền\b",
    r"\blàm giàu nhanh\b",
    r"\blách luật\b",
    r"\bbypass youtube\b",
    r"\bauto 100% không cần làm gì\b"
]

def audit_report(file_path: Path):
    if not file_path.exists():
        print(f"[FAIL] Report file not found: {file_path}")
        return 1

    content = file_path.read_text(encoding="utf-8")
    errors = []
    warnings = []

    print(f"\n========================================================")
    print(f" AUDITING POLICY ADVISORY REPORT: {file_path.name}")
    print(f"========================================================\n")

    # 1. Section presence check
    for section in MANDATORY_SECTIONS:
        pattern = rf"(?i)#{{1,3}}\s+.*{re.escape(section)}"
        if not re.search(pattern, content):
            errors.append(f"Missing mandatory section: '{section}'")

    # 2. Official URL presence check
    found_domains = 0
    for domain in MANDATORY_DOMAINS:
        if domain in content:
            found_domains += 1
    if found_domains == 0:
        errors.append(f"No official Tier 1 Google/YouTube support URLs detected (e.g., support.google.com).")

    # 3. Claim classification check
    tags = ["[OFFICIAL POLICY]", "[OFFICIAL RECOMMENDATION]", "[INDUSTRY PRACTICE]", "[CREATOR OPINION]"]
    found_tags = {tag: len(re.findall(re.escape(tag), content)) for tag in tags}
    total_tags = sum(found_tags.values())

    print("[INFO] Claim Classification Breakdown:")
    for tag, count in found_tags.items():
        print(f"  - {tag}: {count}")

    if found_tags["[OFFICIAL POLICY]"] == 0:
        warnings.append("No claims tagged with '[OFFICIAL POLICY]' found.")

    # 4. Forbidden speculative language check
    for forbidden in FORBIDDEN_HEDGES:
        matches = re.findall(forbidden, content, re.IGNORECASE)
        if matches:
            errors.append(f"Forbidden speculative or black-hat phrase detected: '{matches[0]}'")

    # 5. Risk classification check
    risk_levels = ["LOW RISK", "MEDIUM RISK", "HIGH RISK", "CRITICAL RISK"]
    found_risks = [r for r in risk_levels if r in content]
    if not found_risks:
        warnings.append("No standardized risk ratings (LOW/MEDIUM/HIGH/CRITICAL) detected in report.")

    # Summary
    print("\n--------------------------------------------------------")
    if errors:
        print(f"❌ AUDIT FAILED: {len(errors)} critical error(s) found:")
        for err in errors:
            print(f"  [ERROR] {err}")
    else:
        print("✅ STRUCTURE & POLICY CITATION CHECKS PASSED.")

    if warnings:
        print(f"\n⚠️  WARNINGS ({len(warnings)}):")
        for w in warnings:
            print(f"  [WARN] {w}")

    print("--------------------------------------------------------\n")
    return 1 if errors else 0

def main():
    parser = argparse.ArgumentParser(description="Audit a YouTube Policy Advisory Report.")
    parser.add_argument("report_file", type=Path, help="Path to markdown report file")
    args = parser.parse_args()

    sys.exit(audit_report(args.report_file))

if __name__ == "__main__":
    main()
