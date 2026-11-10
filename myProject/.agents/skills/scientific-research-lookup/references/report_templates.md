# BỘ KHUNG MẪU BÁO CÁO KHOA HỌC THEO TỪNG CHẾ ĐỘ HOẠT ĐỘNG (REPORT TEMPLATES)

Tài liệu này cung cấp mẫu chuẩn cho 5 chế độ hoạt động của **Scientific Research Lookup Skill**.

---

## 1. MẪU BÁO CÁO CHẾ ĐỘ `DEEP RESEARCH` (MẶC ĐỊNH)

```markdown
# Scientific Research Report: [Tên chủ đề nghiên cứu]

## 1. Research Question
* **PICO Question:** [Câu hỏi theo khung PICO]
* **Mục tiêu:** [Mục tiêu cụ thể của cuộc tra cứu]

## 2. Scope and Search Strategy
* **Databases searched:** [PubMed, Crossref, ScienceDirect, arXiv...]
* **Search keywords:** [Các chuỗi truy vấn Boolean]
* **Time range:** [Ví dụ: 2015 – 2026]
* **Inclusion criteria:** [Systematic reviews, RCTs, peer-reviewed articles...]
* **Exclusion criteria:** [Non-peer reviewed blogs, in-vitro studies only...]
* **Search limitations:** [Chỉ tiếp cận được abstract ở một số bài báo paywall...]

## 3. Executive Summary
[Tóm tắt ngắn gọn 3-5 ý cốt lõi nhất: Những gì khoa học đã chứng minh rõ ràng, những gì còn tranh cãi và mức độ tin cậy chung.]

## 4. Key Findings

### Finding 1: [Tiêu đề phát hiện 1]
* **Claim:** [Khẳng định cụ thể]
* **Supporting evidence:** [Dữ liệu thực nghiệm trích từ bài báo]
* **Study type & Sample:** [Loại nghiên cứu, cỡ mẫu n = ...]
* **Main result:** [Chỉ số thống kê: p-value, OR, RR, 95% CI]
* **Limitations:** [Hạn chế của nghiên cứu]
* **Confidence level:** [High / Moderate / Low / Insufficient]
* **Source:** [Citation đầy đủ kèm DOI/PMID]

### Finding 2: [Tiêu đề phát hiện 2]
...

## 5. Conflicting Evidence
[Phân tích các nghiên cứu có kết quả trái ngược nhau, so sánh cỡ mẫu và phương pháp để lý giải sự khác biệt.]

## 6. Evidence Matrix
| Claim ID | Claim | Supporting Source | Evidence Location | Study Type & Sample | Direct / Indirect | Limitations | Status & Confidence |
| :---: | :--- | :--- | :--- | :--- | :---: | :--- | :---: |
| C-01 | ... | ... | ... | ... | Direct | ... | SUPPORTED (High) |

## 7. Research Gaps
[Liệt kê những câu hỏi mà y văn/tài liệu hiện tại chưa có dữ liệu giải đáp thỏa đáng.]

## 8. Final Assessment
* **Có thể kết luận chắc chắn (Established Facts):** [Nội dung]
* **Có khả năng nhưng cần thêm dữ liệu (Probable but Inconclusive):** [Nội dung]
* **Chưa đủ bằng chứng để khẳng định (Insufficient Evidence):** [Nội dung]
* **Không thể xác minh / Khẳng định sai lệch (Refuted / Unverifiable):** [Nội dung]

## 9. References
1. [Authors]. ([Year]). "[Title]". *[Journal Name]*, [Vol]([Issue]), [Pages]. DOI: [Link DOI] | PMID: [PMID]. Trạng thái: [Peer-reviewed / Systematic Review] | Truy cập: [Full text reviewed / Abstract only].
```

---

## 2. MẪU BÁO CÁO CHẾ ĐỘ `CLAIM VERIFICATION`

```markdown
# Scientific Claim Verification Report: "[Tuyên bố cần kiểm chứng]"

## 1. Verified Claim
* **Claim Statement:** [Phát biểu cần xác minh]
* **Domain / Category:** [Y sinh / Dinh dưỡng / Kỹ thuật / Vật lý...]

## 2. Verdict (Phán quyết bằng chứng)
👉 **PHÁN QUYẾT:** `[SUPPORTED | PARTIALLY SUPPORTED | CONFLICTING | UNSUPPORTED | NOT ENOUGH EVIDENCE]`  
👉 **ĐỘ TIN CẬY (CONFIDENCE):** `[High | Moderate | Low | Insufficient]`

## 3. Summary of Scientific Consensus
[Giải thích ngắn gọn đồng thuận khoa học hiện nay về claim này.]

## 4. Evidence Breakdown
* **Bằng chứng ủng hộ (Supporting Evidence):** [Trích dẫn nghiên cứu, cỡ mẫu, kết quả]
* **Bằng chứng phản bác (Counter Evidence):** [Trích dẫn nghiên cứu phản đối]
* **Bẫy ngụy biện đã loại trừ:** [Ví dụ: Claim xuất phát từ hiểu nhầm nghiên cứu động vật hoặc đánh tráo tương quan thành nhân quả]

## 5. Traceability Matrix
| Claim Aspect | Scientific Finding | Key Citation | Evidence Location | Verdict |
| :--- | :--- | :--- | :--- | :---: |
| ... | ... | ... | ... | SUPPORTED |

## 6. Primary References
[Danh mục tài liệu tham khảo đã xác minh DOI/PMID]
```

---

## 3. MẪU BÁO CÁO CHẾ ĐỘ `PAPER AUDIT`

```markdown
# Independent Paper Audit: [Tên bài báo cần kiểm định]

## 1. Publication Metadata Verification
* **Title:** [Tiêu đề chính xác]
* **Authors:** [Danh sách tác giả và cơ quan công tác]
* **Journal / Venue:** [Tạp chí, Năm xuất bản, Số phát hành]
* **DOI / PMID:** [Mã định danh đã kiểm tra qua API]
* **Peer-Review Status:** [Peer-reviewed / Preprint]
* **Retraction Watch Check:** [An toàn / Có đính chính / Bị rút bài]

## 2. Methodological Rigor & Critical Appraisal
* **Research Question:** [Câu hỏi nghiên cứu]
* **Study Design:** [Thiết kế nghiên cứu và mức độ kiểm soát]
* **Sample Size & Power Analysis:** [Cỡ mẫu n = ..., có tính toán cỡ mẫu trước không?]
* **Blinding & Randomization:** [Có làm mù đôi và ngẫu nhiên hóa chuẩn không?]
* **Statistical Validity:** [Kiểm định thống kê có phù hợp không? $p$-hacking risk?]

## 3. Findings vs. Author Conclusions (Kiểm tra Over-extrapolation)
* **Kết quả thực nghiệm thật:** [Dữ liệu đo được trong bảng kết quả]
* **Kết luận của tác giả:** [Tác giả viết gì trong phần Conclusion]
* **Đánh giá diễn giải quá đà:** [Tác giả có nói quá kết quả nghiên cứu không?]

## 4. Risk of Bias & Conflict of Interest
* **Nguồn tài trợ:** [Đơn vị cấp kinh phí]
* **Xung đột lợi ích:** [Có tác giả nào làm việc cho công ty liên quan không?]

## 5. Final Audit Verdict
👉 **Chất lượng phương pháp:** `[High / Moderate / Low / Flawed]`  
👉 **Độ tin cậy của kết luận:** `[Vững chắc / Cần dè dặt / Không đáng tin cậy]`
```

---

## 4. MẪU BÁO CÁO CHẾ ĐỘ `LITERATURE COMPARISON`

```markdown
# Literature Comparison Report: [Chủ đề có kết quả trái chiều]

## 1. Debate Overview
[Mô tả cốt lõi của sự bất đồng khoa học: Trường phái A ủng hộ X, trường phái B ủng hộ Y.]

## 2. Comparison Matrix
| Tiêu chí so sánh | Nhóm nghiên cứu Ủng hộ (Camp A) | Nhóm nghiên cứu Trái ngược (Camp B) |
| :--- | :--- | :--- |
| **Nghiên cứu tiêu biểu** | [Smith et al., 2021 (DOI: ...)] | [Johnson et al., 2023 (DOI: ...)] |
| **Thiết kế & Cỡ mẫu** | [RCT, n = 45] | [Prospective Cohort, n = 12.000] |
| **Can thiệp / Liều lượng** | [Can thiệp ngắn hạn 4 tuần] | [Theo dõi dài hạn 5 năm] |
| **Kết quả đo lường** | [Chỉ số X giảm 15% (p < 0.05)] | [Không có sự khác biệt có ý nghĩa] |
| **Hạn chế chính** | [Cỡ mẫu nhỏ, mất dấu] | [Tự báo cáo, yếu tố nhiễu lối sống] |

## 3. Root Cause of Discrepancy (Nguyên nhân gây mâu thuẫn)
[Bóc tách nguyên nhân: Khác biệt về tiêu chuẩn chọn mẫu, liều can thiệp, phương pháp đo hay thời gian theo dõi.]

## 4. Current State of Scientific Consensus
[Khoa học hiện nay nghiêng về bên nào hơn và các thử nghiệm cần thiết trong tương lai.]
```
