#!/usr/bin/env python3
"""
Test Suite for Report Reliability Auditor.
Executes the three mandatory validation tests required by the specification.
"""

import sys
import io
from pathlib import Path

# Ensure UTF-8 output on Windows console
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))
from audit_engine import AuditorEngine

def test_1_contradiction():
    print("\n--- RUNNING TEST 1: Contradiction (Filter >180s vs Median 82s) ---")
    engine = AuditorEngine(mode="REPORT-ONLY")
    
    filter_val = 180.0
    median_val = 82.0
    
    finding = engine.check_duration_filter_contradiction(filter_val, median_val)
    
    assert finding is not None, "FAILED: No finding generated for duration contradiction!"
    assert finding.severity in ["HIGH", "CRITICAL"], f"FAILED: Severity {finding.severity} is less than HIGH!"
    assert "CONTRADICTED" in finding.status, f"FAILED: Finding status is {finding.status}, expected CONTRADICTED!"
    
    print(f"[PASS] TEST 1 PASSED:")
    print(f"   - Finding ID: {finding.finding_id}")
    print(f"   - Severity: {finding.severity}")
    print(f"   - Title: {finding.title}")
    print(f"   - Status: {finding.status}")
    print(f"   - Independent Check: {finding.independent_check}")
    return True

def test_2_arithmetic_vs_unverified_input():
    print("\n--- RUNNING TEST 2: Correct Arithmetic vs Unverified Input (215/424 = 50.71%) ---")
    engine = AuditorEngine(mode="REPORT-ONLY")
    
    numerator = 215.0
    denominator = 424.0
    reported_pct = 50.71
    
    result = engine.check_arithmetic_fraction(numerator, denominator, reported_pct)
    
    assert result["arithmetic_pass"] is True, f"FAILED: Arithmetic check failed! Diff: {result['diff']}"
    assert result["input_status"] == "EXTERNALLY UNVERIFIED", f"FAILED: Expected EXTERNALLY UNVERIFIED, got {result['input_status']}"
    
    print(f"[PASS] TEST 2 PASSED:")
    print(f"   - Numerator: {result['numerator']}, Denominator: {result['denominator']}")
    print(f"   - Calculated: {result['calculated_pct']}%, Reported: {result['reported_pct']}%")
    print(f"   - Arithmetic Status: PASS (Diff: {result['diff']}%)")
    print(f"   - Input Data Status: {result['input_status']} (No raw dataset provided in REPORT-ONLY mode)")
    return True

def test_3_unsupported_causation():
    print("\n--- RUNNING TEST 3: Unsupported Causation (1M Views on IQ Video vs Ego-Validation Hook) ---")
    engine = AuditorEngine(mode="REPORT-ONLY")
    
    observation = "Video '_0pHoxnR8bw' về 5 thói quen người IQ cao đạt 1.064.988 views (Multiplier 3.669.7x)."
    causal_claim = "Video thành công bứt phá triệu view VÌ sử dụng kỹ thuật tâm lý Ego-Validation Hook."
    
    result = engine.audit_causal_claim(observation, causal_claim, has_controlled_study=False)
    
    assert result["causation_verified"] is False, "FAILED: Causation was marked as verified without proof!"
    assert result["status"] == "HYPOTHESIS NOT VERIFIED", f"FAILED: Expected HYPOTHESIS NOT VERIFIED, got {result['status']}"
    assert result["finding"]["severity"] in ["HIGH", "CRITICAL"], "FAILED: Severity less than HIGH!"
    
    print(f"[PASS] TEST 3 PASSED:")
    print(f"   - Empirical Observation: '{result['observation']}'")
    print(f"   - Unverified Causal Claim: '{result['causal_claim']}'")
    print(f"   - Causation Status: {result['status']}")
    print(f"   - Generated Finding: [{result['finding']['id']}] {result['finding']['title']} ({result['finding']['severity']})")
    print(f"   - Required Action: Tách quan sát thực nghiệm khỏi quy kết nhân quả; không nhầm lẫn tương quan với nguyên nhân cốt lõi.")
    return True

def run_all_tests():
    print("======================================================================")
    print(" EXECUTING VALIDATION SUITE: REPORT RELIABILITY AUDITOR")
    print("======================================================================")
    
    t1 = test_1_contradiction()
    t2 = test_2_arithmetic_vs_unverified_input()
    t3 = test_3_unsupported_causation()
    
    if t1 and t2 and t3:
        print("\n======================================================================")
        print(" [SUCCESS] ALL 3 MANDATORY VALIDATION TESTS PASSED PERFECTLY!")
        print("======================================================================\n")
        return 0
    else:
        print("\n[FAIL] SOME TESTS FAILED.")
        return 1

if __name__ == "__main__":
    sys.exit(run_all_tests())
