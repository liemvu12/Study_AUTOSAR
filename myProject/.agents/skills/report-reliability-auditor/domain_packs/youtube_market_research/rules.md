# Domain Pack: YouTube Market Research & Video Analytics Audit

This domain pack defines specialized auditing rules, error patterns, and prohibited inferences when evaluating YouTube market intelligence reports, competitor studies, and video performance analyses.

---

## 1. Domain-Specific Audit Dimensions

When evaluating a YouTube market research report, the auditor must rigorously test each of the following 14 dimensions:

### 1. Channel Age vs. Niche-Entry Age
- **Audit Rule:** The platform registration date (`publishedAt` of the channel) does **not** reflect how long the creator has been publishing in the specific niche.
- **Flaw Pattern:** Calling an old channel (e.g., created in 2018) a "veteran in AI tools" when it only pivoted to AI content 3 months ago.
- **Verification:** Auditor must check the upload date of the first video in that specific niche.

### 2. View / Subscriber Snapshot Dynamics
- **Audit Rule:** YouTube metrics are dynamic and volatile. Any stated subscriber or view count is valid **only at the exact timestamp of collection**.
- **Flaw Pattern:** Treating view counts as static historical constants without stating the collection date.

### 3. Shorts vs. Long-form Duration Parsing
- **Audit Rule:** Shorts and Long-form have fundamentally distinct algorithmic distribution systems, view scales, and monetization rates.
- **Flaw Pattern:**
  - Filtering for Long-form by declaring a minimum duration (e.g., $>180$ seconds), but then reporting a median duration below that threshold (e.g., 82 seconds).
  - Mixing Shorts metrics into Long-form median calculations, which artificially inflates view counts and crushes watch time.

### 4. Query & Search Term Bias
- **Audit Rule:** The choice of search keywords in the YouTube Data API determines which channels are discovered.
- **Flaw Pattern:** Searching only broad terms (e.g., "AI") and claiming the sample represents specialized sub-niches (e.g., "Excel VBA AI integration").

### 5. Duplicate Data & Channel Multi-Counting
- **Audit Rule:** Large API pulls frequently return identical videos across multiple search queries or capture the same channel under different video IDs.
- **Flaw Pattern:** Reporting total sample sizes without deduplication against unique `channel_id` and `video_id`.

### 6. Video Age Cohort & Normalization
- **Audit Rule:** A video uploaded 3 years ago has had 1,000 days to accumulate views; a video uploaded 3 days ago has had 72 hours.
- **Flaw Pattern:** Directly comparing absolute view counts between old and new videos without normalizing for age or using Velocity (Views Per Hour - VPH) on mature videos ($\ge 30$ days).

### 7. Survivorship Bias (Thiên Kiến Kẻ Sống Sót)
- **Audit Rule:** API searches only surface videos and channels that currently exist and have achieved sufficient algorithmic traction to rank.
- **Flaw Pattern:** Concluding that "new channels have a 40% success rate" by only counting surviving active channels, ignoring the thousands of channels that uploaded 3 videos, received 0 views, and were abandoned.

### 8. Public Metrics vs. Private YouTube Studio Analytics
- **Audit Rule:** Public YouTube endpoints expose: views, likes, comment counts, video duration, and publish date. Public endpoints **DO NOT EXPOSE**: Click-Through Rate (CTR), Audience Retention Graph, Average Percentage Viewed (APV), Traffic Source Breakdown, or Real-time Impressions.
- **Flaw Pattern:** Claiming a specific hook "retained 70% of viewers" without access to the creator's private YouTube Studio dashboard.

### 9. RPM, CPM & Revenue Estimation Fallacies
- **Audit Rule:** Monetization rates vary dramatically by viewer geographic location, advertiser seasonality (Q4 vs Q1), video length (mid-rolls), and viewer demographics.
- **Flaw Pattern:** Multiplying public views by an arbitrary "industry average RPM" and presenting the resulting figure as verified channel income.

### 10. Search vs. Browse Feature Attribution
- **Audit Rule:** Traffic sources (YouTube Search, Suggested Videos, Browse Features/Home, External) cannot be determined purely from public view counts.
- **Flaw Pattern:** Asserting that a video "is 100% driven by Evergreen Search" solely because it has a tutorial title, without verifying search volume index or traffic source data.

### 11. Outlier Calculation & Baseline Definition
- **Audit Rule:** An Outlier Multiplier must be calculated against a statistically valid baseline of the **same channel's typical performance** (ideally Median of the last 10–30 videos).
- **Flaw Pattern:**
  - Calculating multipliers against the Mean (which is distorted by the outlier itself).
  - Calculating multipliers on channels with fewer than 5 historical videos (insufficient baseline).

### 12. Median vs. Mean Distribution Reality
- **Audit Rule:** YouTube view counts follow extreme right-skewed power-law distributions.
- **Flaw Pattern:** Using Mean view counts to forecast what a typical new creator can expect to achieve.

### 13. YouTube Partner Program (YPP) & Content Authenticity Claims
- **Audit Rule:** YouTube policies on Reused Content and Repetitious Content (Section 1311392) require human editorial transformation.
- **Flaw Pattern:**
  - Claiming that any AI-voiced or stock-footage video will "automatically fail YPP" (ignoring successful educational channels with unique scripts).
  - Claiming that fully automated faceless channels are "100% safe for monetization" (ignoring mass-demonetization waves).

### 14. Google Trends Interpretation Limitations
- **Audit Rule:** Google Trends displays **relative search interest (0–100 index)**, not absolute search volume. An index of 100 in a tiny sub-niche may represent only 500 searches, while an index of 20 in a broad topic represents 500,000 searches.
- **Flaw Pattern:** Equating high Google Trends index directly with high market size or high traffic volume.

---

## 2. Six Strictly Prohibited Inferences (Zero Tolerance)

The auditor must flag a `HIGH` or `CRITICAL` finding whenever a report commits any of the following 6 unwarranted logical leaps:

1. **`[Views ➔ Revenue]`**: Inferring actual dollar revenue or creator earnings directly from public view counts.
2. **`[Revenue ➔ Profit]`**: Assuming that high ad revenue equates to business profitability, ignoring asset licensing, voice API, editor, and compute costs.
3. **`[Google Trends ➔ Actual Traffic Source]`**: Inferring that viewers found a video through YouTube search solely based on a rising Google Trends line.
4. **`[Stock Footage / AI Voice ➔ Automatic Policy Violation]`**: Declaring a channel in violation of YouTube's Reused Content policy without evaluating narrative transformation and original script value.
5. **`[Single Outlier Video ➔ Repeatable Channel Success]`**: Treating an isolated viral spike ($\text{Multiplier} > 10\times$) as evidence that the format can be reliably replicated by a newcomer.
6. **`[Top 10 Comments ➔ Entire Audience Sentiment]`**: Treating a handful of upvoted comments as a statistically representative survey of the entire viewer demographic.
