#!/usr/bin/env python3
"""
verify_audit.py - Evidence-Based Market Research Skill Audit Validator

Parses a markdown report generated under the Evidence-Based Market Research Skill,
counts claim classification tags, computes ratios, checks against audit thresholds,
and outputs the standardized Final Audit Block.
"""

import sys
import re
from pathlib import Path

# Fix Windows console UTF-8 output encoding
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

def audit_report(file_path: str):
    path = Path(file_path)
    if not path.exists():
        print(f"Error: File {file_path} does not exist.")
        sys.exit(1)

    content = path.read_text(encoding="utf-8")

    tags = {
        "FACT": len(re.findall(r"\[FACT\]", content)),
        "MEASURED DATA": len(re.findall(r"\[MEASURED DATA\]", content)),
        "DIRECT EVIDENCE": len(re.findall(r"\[DIRECT EVIDENCE\]", content)),
        "INFERENCE": len(re.findall(r"\[INFERENCE\]", content)),
        "SPECULATION": len(re.findall(r"\[SPECULATION\]", content)),
    }

    total_claims = sum(tags.values())

    print("\n" + "="*60)
    print("  EVIDENCE-BASED MARKET RESEARCH SKILL: AUDIT REPORT")
    print("="*60)
    print(f"File: {path.resolve()}")
    print(f"Total Tagged Claims: {total_claims}\n")

    if total_claims == 0:
        print("[WARNING] Không tìm thấy bất kỳ tag phân loại nào trong báo cáo!")
        print("Báo cáo cần bổ sung [FACT], [MEASURED DATA], [DIRECT EVIDENCE], [INFERENCE], hoặc [SPECULATION].")
        return

    inference_ratio = (tags["INFERENCE"] / total_claims) * 100
    speculation_ratio = (tags["SPECULATION"] / total_claims) * 100

    print(f"- [FACT] Count:            {tags['FACT']} ({tags['FACT']/total_claims*100:.1f}%)")
    print(f"- [MEASURED DATA] Count:   {tags['MEASURED DATA']} ({tags['MEASURED DATA']/total_claims*100:.1f}%)")
    print(f"- [DIRECT EVIDENCE] Count: {tags['DIRECT EVIDENCE']} ({tags['DIRECT EVIDENCE']/total_claims*100:.1f}%)")
    print(f"- [INFERENCE] Count:       {tags['INFERENCE']} ({inference_ratio:.1f}%)")
    print(f"- [SPECULATION] Count:     {tags['SPECULATION']} ({speculation_ratio:.1f}%)")
    print("-" * 60)

    # Threshold checks
    has_warning = False
    if inference_ratio > 30.0:
        print(f"\n[!] [AUDIT WARNING] Tỷ lệ suy luận [INFERENCE] vượt quá 30.0% ({inference_ratio:.1f}%)")
        print("    Khuyến nghị: Cần đối soát thêm tài liệu gốc Tiers 1-3 để chuyển hóa suy luận thành Fact.")
        has_warning = True

    if speculation_ratio > 10.0:
        print(f"\n[CRITICAL AUDIT ALERT] Tỷ lệ suy đoán [SPECULATION] vượt quá 10.0% ({speculation_ratio:.1f}%)")
        print("    CẢNH BÁO ĐỎ: Báo cáo KHÔNG ĐỦ CƠ SỞ để sử dụng cho quyết định kinh doanh hoặc đầu tư!")
        has_warning = True

    if not has_warning:
        print("\n[AUDIT PASSED] Báo cáo đạt chuẩn kiểm định bằng chứng khắt khe.")
    print("="*60 + "\n")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python verify_audit.py <path_to_report.md>")
        sys.exit(1)
    audit_report(sys.argv[1])
