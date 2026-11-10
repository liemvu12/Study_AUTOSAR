# Claim Ledger & Extraction Guide

This guide defines the standardized methodology for decomposing a research report into discrete, auditable claim units, classifying their epistemology, and evaluating their evidentiary support.

---

## 1. Claim Atomicity Rule

When extracting claims from a report:
* **One assertion per claim:** If a sentence contains two distinct ideas, break it into two separate claims.
  * *Example:* "Channel A published 35 videos [NUMERICAL] and achieved virality because of its fast hook [CAUSAL]."
  * $\rightarrow$ `CLM-001` (Numerical): Channel A published 35 videos.
  * $\rightarrow$ `CLM-002` (Causal): Channel A achieved virality because of its fast hook.

---

## 2. Epistemological Classification Taxonomy

Each claim must be assigned to exactly one of the 11 classes:

```text
                                  ┌─── FACTUAL (Objective verifiable fact)
                                  ├─── NUMERICAL (Exact stated count or metric)
         ┌── Empirical / Data ────┼─── CALCULATED (Derived via math/algorithm)
         │                        └─── OBSERVATIONAL (Direct sensory perception)
         │
         │                        ┌─── METHODOLOGICAL (Procedural rules & filters)
Claims ──┼── Logic & Method ──────┼─── CORRELATIONAL (Two variables moving together)
         │                        └─── CAUSAL (A causes B - high burden of proof)
         │
         │                        ┌─── INTERPRETIVE (Subjective analysis of meaning)
         └── Interpretive/Action ─┼─── PREDICTIVE (Forecasting future outcome)
                                  ├─── POLICY (Legal, platform rule, or TOS)
                                  └─── RECOMMENDATION (Prescriptive action advice)
```

---

## 3. Evidence Evaluation Protocol

For each extracted claim:
1. **Identify Evidence Required:** What empirical measurement would satisfy an impartial scientist or auditor?
2. **Identify Evidence Provided:** What exact proof does the report's author offer?
3. **Identify Evidence Actually Accessed:** In this audit turn, what files, URLs, or API responses did the auditor directly inspect?
4. **Determine Recalculation Status:**
   - For `NUMERICAL` or `CALCULATED`: Perform the mathematical operation independently.
   - Record: `Reported Value` vs. `Calculated Value`.
5. **Assign Verification Status:**
   - `EXTERNALLY VERIFIED`: Raw data opened and matched.
   - `INTERNALLY CONSISTENT`: Math is correct and matches text, but raw dataset is unavailable.
   - `EXTERNALLY UNVERIFIED`: Relies on external source that was not provided.
   - `MISSING EVIDENCE`: No evidence provided in text.
   - `INSUFFICIENT EVIDENCE`: Evidence provided is too small or unrepresentative.
   - `CONTRADICTED`: Internal or external evidence refutes the claim.
