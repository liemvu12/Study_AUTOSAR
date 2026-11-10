# Standard Audit Report Template

Use this template to generate standardized forensic audit reports.

```markdown
# REPORT RELIABILITY AUDIT: [Report Title]

## 1. Audit Scope & Metadata
- **Target Report Title:** [Exact title from target document]
- **Audit Mode:** [REPORT-ONLY AUDIT | FULL-EVIDENCE AUDIT]
- **Auditor Framework:** Report Reliability Auditor (Forensic Evidence-Based)
- **Data Files Physically Accessed:** [List full paths, or "None (Report-Only Mode)"]
- **Audit Date:** YYYY-MM-DD
- **Total Audited Claims:** [N]
- **Total Cataloged Findings:** [N] (Critical: [X], High: [Y], Medium: [Z], Low: [W])

---

## 2. Executive Verdict
- **Overall Reliability Verdict:** [RELIABLE | RELIABLE WITH LIMITATIONS | PARTIALLY RELIABLE | UNVERIFIED | MATERIALLY UNRELIABLE | NOT AUDITABLE]
- **Decision Readiness:** [READY FOR DECISION | READY WITH CONDITIONS | READY ONLY FOR EXPLORATION | REQUIRES CORRECTION | REQUIRES SOURCE DATA | REQUIRES RE-RUN | REJECT AS DECISION EVIDENCE]
- **Executive Synthesis:**
  [Dense, evidence-grounded summary of the target document's technical soundness, main strengths, fatal contradictions, and strategic risks.]

---

## 3. Reliability Dimensions
| Audit Dimension | Dimension Rating | Summary of Audited Reality |
| :--- | :---: | :--- |
| **Internal Consistency** | [PASS / MARGINAL / FAIL] | [Evaluation of internal alignment and contradictions] |
| **Arithmetic Correctness** | [PASS / DISCREPANCY / UNVERIFIABLE] | [Recalculation accuracy of visible math] |
| **Statistical Soundness** | [ROBUST / ACCEPTABLE / SKEWED_RISK / FLAWED] | [Use of median, sample representation, outlier logic] |
| **Source Traceability** | [COMPLETE / PARTIAL / UNTRACED] | [Ability to trace claims to specific IDs or files] |
| **Methodological Soundness**| [SOUND / GAPS / FLAWED] | [Rigor of sampling, filtering, and bias control] |
| **Reproducibility** | [FULLY / PARTIALLY / NOT REPRODUCIBLE] | [Can commands/results be independently reproduced] |
| **Conclusion Support** | [FULLY SUPPORTED / QUALIFIED / OVERCLAIM] | [Extent to which data justifies final recommendations] |
| **Decision Readiness** | [Select from Decision Readiness tiers] | [Practical fitness for executive decision-making] |

---

## 4. Critical and High Findings

### [FND-001] [Brief Descriptive Title of Defect]
- **Severity:** [CRITICAL | HIGH]
- **Affected Claim(s):** [CLM-xxx]
- **Exact Report Evidence:** "[Direct verbatim quote from report]"
- **Independent Check:** [Audit recalculation, logical proof, or data check]
- **Why It Matters:** [Technical impact on truth]
- **Impact on Conclusion:** [How this alters the report's takeaway]
- **Required Correction:** [Exact numerical or narrative repair required]
- **Verification Status:** [CONTRADICTED | MISSING EVIDENCE | UNVERIFIED]

---

## 5. Internal Consistency Audit
[Detailed audit of contradictions between text sections, filters vs. results, tables vs. commentary.]

---

## 6. Numerical and Statistical Audit
| Metric / Calculation Stated | Reported Value | Recalculated Value | Discrepancy | Arithmetic Status | Input Status |
| :--- | :---: | :---: | :---: | :---: | :---: |
| [e.g., Kênh nhỏ Hướng 1 %] | 50.71% | 215 / 424 = 50.7075% | None | PASS | EXTERNALLY UNVERIFIED |

---

## 7. Source and Evidence Audit
| Stated Source / Citation | Physical Existence on Disk | Direct Citation Relevance | Audit Finding |
| :--- | :---: | :---: | :--- |
| [e.g., channels.csv] | [EXISTS / NOT FOUND / UNCHECKED] | [Supports claim / Irrelevant / Not provided] | [Finding] |

---

## 8. Methodology & Bias Audit
- **Sampling Flow & Exclusion Checks:** [Did filters drop data inappropriately?]
- **Survivorship Bias Assessment:** [Were dead/inactive entities omitted?]
- **Cohort & Timeline Alignment:** [Were comparisons normalized for time/age?]

---

## 9. Claim Ledger
| ID | Location | Claim Verbatim | Type | Evidence Provided | Accessed | Recalc Status | Verification Status | Verdict |
| :--- | :--- | :--- | :---: | :--- | :---: | :---: | :---: | :---: |
| CLM-001 | Sec 1.1 | ... | NUMERICAL | Stated count | Yes / No | 100% Match | INTERNALLY CONSISTENT | VERIFIED |

---

## 10. Conclusion Support Matrix
| Final Report Conclusion | Underlying Claims | Degree of Evidentiary Support | Auditor Assessment |
| :--- | :--- | :---: | :--- |
| [e.g., Hướng 1 bền vững hơn] | [CLM-003, CLM-005, ...] | [Fully Supported / Partially Supported / Overclaim] | [Audit verdict] |

---

## 11. Required Actions & Remediations
1. [Remediation 1]
2. [Remediation 2]

---

## 12. Final Decision & Advisory Guardrails
- **Actionable Boundaries:** [What the user can safely rely upon]
- **Quarantined Claims:** [What claims must NOT be used for capital/time decisions]
```
