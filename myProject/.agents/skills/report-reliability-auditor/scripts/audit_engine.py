#!/usr/bin/env python3
"""
Report Reliability Auditor Engine.
Forensic evaluation engine for research reports, datasets, and claim verification.
"""

import sys
import re
import json
import argparse
from pathlib import Path
from typing import List, Dict, Any, Optional

class Claim:
    def __init__(self, claim_id: str, text: str, claim_type: str, location: str = ""):
        self.claim_id = claim_id
        self.text = text
        self.claim_type = claim_type
        self.location = location
        self.evidence_required = ""
        self.evidence_provided = ""
        self.evidence_accessed = ""
        self.calculation_result = ""
        self.assumptions = ""
        self.contradictions = ""
        self.status = "UNVERIFIED"
        self.verdict = "UNVERIFIED"
        self.confidence = "LOW"

    def to_dict(self):
        return {
            "id": self.claim_id,
            "text": self.text,
            "type": self.claim_type,
            "location": self.location,
            "evidence_required": self.evidence_required,
            "evidence_provided": self.evidence_provided,
            "evidence_accessed": self.evidence_accessed,
            "calculation_result": self.calculation_result,
            "assumptions": self.assumptions,
            "contradictions": self.contradictions,
            "status": self.status,
            "verdict": self.verdict,
            "confidence": self.confidence
        }

class Finding:
    def __init__(self, finding_id: str, severity: str, title: str, affected_claim: str,
                 report_evidence: str, independent_check: str, why_it_matters: str,
                 impact_on_conclusion: str, required_correction: str, status: str):
        self.finding_id = finding_id
        self.severity = severity  # CRITICAL, HIGH, MEDIUM, LOW, INFORMATIONAL
        self.title = title
        self.affected_claim = affected_claim
        self.report_evidence = report_evidence
        self.independent_check = independent_check
        self.why_it_matters = why_it_matters
        self.impact_on_conclusion = impact_on_conclusion
        self.required_correction = required_correction
        self.status = status

    def to_dict(self):
        return {
            "id": self.finding_id,
            "severity": self.severity,
            "title": self.title,
            "affected_claim": self.affected_claim,
            "report_evidence": self.report_evidence,
            "independent_check": self.independent_check,
            "why_it_matters": self.why_it_matters,
            "impact_on_conclusion": self.impact_on_conclusion,
            "required_correction": self.required_correction,
            "status": self.status
        }

class AuditorEngine:
    def __init__(self, mode: str = "REPORT-ONLY"):
        self.mode = mode
        self.claims: List[Claim] = []
        self.findings: List[Finding] = []
        self.dimension_ratings: Dict[str, str] = {
            "internal_consistency": "PASS",
            "arithmetic_correctness": "PASS",
            "statistical_soundness": "ACCEPTABLE",
            "source_traceability": "PARTIAL",
            "methodological_soundness": "SOUND",
            "reproducibility": "PARTIALLY REPRODUCIBLE",
            "conclusion_support": "QUALIFIED SUPPORT",
            "decision_readiness": "READY WITH CONDITIONS"
        }
        self.overall_verdict = "RELIABLE WITH LIMITATIONS"

    def check_arithmetic_fraction(self, numerator: float, denominator: float, reported_pct: float, tolerance: float = 0.05) -> Dict[str, Any]:
        """Recalculates a percentage and checks if input data is verified."""
        if denominator == 0:
            return {"status": "ERROR", "message": "Division by zero"}
        
        calculated_pct = (numerator / denominator) * 100.0
        diff = abs(calculated_pct - reported_pct)
        arithmetic_pass = diff <= tolerance
        
        # In REPORT-ONLY mode without underlying verified dataset:
        input_status = "EXTERNALLY VERIFIED" if self.mode == "FULL-EVIDENCE" else "EXTERNALLY UNVERIFIED"
        
        return {
            "numerator": numerator,
            "denominator": denominator,
            "reported_pct": reported_pct,
            "calculated_pct": round(calculated_pct, 4),
            "diff": round(diff, 4),
            "arithmetic_pass": arithmetic_pass,
            "input_status": input_status
        }

    def check_duration_filter_contradiction(self, filter_threshold_sec: float, reported_median_sec: float) -> Optional[Finding]:
        """Detects contradiction between duration filter and reported median."""
        if reported_median_sec < filter_threshold_sec:
            fnd = Finding(
                finding_id=f"FND-{len(self.findings)+1:03d}",
                severity="HIGH",
                title="Duration Filter Contradiction with Reported Sample Median",
                affected_claim="Methodological duration filter vs. Median video duration",
                report_evidence=f"Bộ lọc: thời lượng lọc >{filter_threshold_sec}s; Kết quả: Thời lượng video trung vị: {reported_median_sec}s",
                independent_check=f"Nếu tập mẫu đã lọc bỏ toàn bộ video <={filter_threshold_sec}s, thì giá trị trung vị của tập mẫu bắt buộc phải >{filter_threshold_sec}s. Giá trị {reported_median_sec}s chứng minh bộ lọc bị vi phạm hoặc mẫu chứa dữ liệu Shorts ngoài dự kiến.",
                why_it_matters="Sai lệch dữ liệu đầu vào hoặc bộ lọc không được áp dụng đúng như mô tả phương pháp.",
                impact_on_conclusion="Làm giảm độ tin cậy của phương pháp lọc mẫu; có thể làm sai lệch phân tích thời lượng và tỷ lệ giữ chân.",
                required_correction="Kiểm tra lại pipeline lọc dữ liệu, loại bỏ các video <180s hoặc đính chính lại giá trị trung vị thực tế.",
                status="CONTRADICTED"
            )
            self.findings.append(fnd)
            self.dimension_ratings["internal_consistency"] = "FAIL"
            return fnd
        return None

    def audit_causal_claim(self, observation_text: str, causal_claim_text: str, has_controlled_study: bool = False) -> Dict[str, Any]:
        """Separates observation from causal assertion and evaluates evidentiary support."""
        if not has_controlled_study:
            fnd = Finding(
                finding_id=f"FND-{len(self.findings)+1:03d}",
                severity="HIGH",
                title="Unverified Causal Inference from Observational Co-occurrence",
                affected_claim=causal_claim_text,
                report_evidence=f"Quan sát: '{observation_text}' -> Quy kết nhân quả: '{causal_claim_text}'",
                independent_check="Tương quan hoặc đồng xuất hiện (correlation/co-occurrence) giữa một hook tâm lý và lượt xem triệu view không đủ để chứng minh quan hệ nhân quả. Thuật toán YouTube phân phối dựa trên nhiều biến số ẩn (thời điểm, lịch sử kênh, tệp khán giả ban đầu, thumbnail CTR).",
                why_it_matters="Nhầm lẫn giữa quan sát hiện tượng và quy luật nhân quả dẫn đến ảo tưởng rằng sao chép hook sẽ lặp lại thành công.",
                impact_on_conclusion="Hạ mức độ kết luận từ nguyên nhân chắc chắn xuống thành giả thuyết chưa được kiểm chứng (Hypothesis Not Verified).",
                required_correction="Tách riêng quan sát thực nghiệm khỏi giả thuyết nhân quả; gắn nhãn [HYPOTHESIS NOT VERIFIED] cho lý do thành công.",
                status="UNVERIFIED CAUSATION"
            )
            self.findings.append(fnd)
            self.dimension_ratings["conclusion_support"] = "UNSUPPORTED OVERCLAIM"
            return {
                "observation": observation_text,
                "causal_claim": causal_claim_text,
                "causation_verified": False,
                "status": "HYPOTHESIS NOT VERIFIED",
                "finding": fnd.to_dict()
            }
        return {
            "observation": observation_text,
            "causal_claim": causal_claim_text,
            "causation_verified": True,
            "status": "EXTERNALLY VERIFIED"
        }

if __name__ == "__main__":
    print("Report Reliability Auditor Engine initialized.")
