# QUY TẮC CHỐNG BỊA ĐẶT & THIÊN LỆCH TRONG NGHIÊN CỨU KHOA HỌC (ANTI-HALLUCINATION PROTOCOL)

Tài liệu này xác định các ranh giới đỏ không thể vượt qua khi thực hiện tra cứu và tổng hợp khoa học.

---

## 1. NGUYÊN TẮC BẤT DI BẤT DỊCH (ZERO-TOLERANCE RULES)

1. **Tuyệt đối không bịa tài liệu:** Mọi bài báo, tên tác giả, năm công bố, tên tạp chí, DOI hoặc PMID xuất hiện trong báo cáo đều phải là tài liệu có thật, đã được kiểm tra trên Crossref, PubMed hoặc trang xuất bản chính thức.
2. **Không tự điền thông tin (No Gap-Filling):** Nếu một nghiên cứu không công bố cỡ mẫu, không ghi rõ độ tuổi người tham gia hoặc không báo cáo $p$-value, Agent phải ghi rõ: `"Không được tác giả công bố"` thay vì tự suy đoán hoặc ước tính.
3. **Phân định rõ ranh giới tiếp cận tài liệu:**
   * Nếu chỉ đọc được Abstract do bài báo bị chặn bởi Paywall, bắt buộc phải ghi rõ:  
     > `[ABSTRACT ONLY] - Chưa tiếp cận được toàn văn nghiên cứu.`
   * Không bao giờ khẳng định chi tiết về phương pháp đo lường hay bảng phụ lục nếu mới chỉ đọc bản tóm tắt (Abstract).
4. **Không trộn lẫn dữ liệu nhiều nghiên cứu:** Không tự ý tính trung bình cộng cỡ mẫu, tỷ lệ phần trăm hoặc kết quả giữa các nghiên cứu khác nhau thành một con số tổng hợp mới (trừ khi dẫn lại con số chính thức từ một bài báo phân tích gộp - Meta-analysis đã xuất bản).
5. **Không dùng kiến thức nội tại (Parametric Memory) làm bằng chứng:** Mọi kết luận khoa học phải bắt nguồn từ văn bản tài liệu đã tra cứu và xác minh trong phiên làm việc, không dựa vào "trí nhớ mô hình" để phán đoán.

---

## 2. BẢY BẪY NGỤY BIỆN KHOA HỌC THƯỜNG GẶP (THE 7 FALLACIES TO AVOID)

Agent phải chủ động phát hiện và chặn đứng 7 lỗi ngụy biện kinh điển sau:

```
+───────────────────────────────────────────────────────────────────────────────────────────────────+
|                                7 LỖI NGỤY BIỆN KHOA HỌC BỊ CẤM                                    |
+───────────────────────────────────────────────────────────────────────────────────────────────────+
| BẪY NGỤY BIỆN                               | QUY TẮC BẮT BUỘC CỦA SKILL                          |
+─────────────────────────────────────────────+─────────────────────────────────────────────────────+
| 1. Biến Tương quan thành Nhân quả           | Không được dùng "gây ra", "dẫn đến" nếu nghiên cứu  |
|    (Correlation != Causation)               | chỉ là quan sát (Observation/Association).          |
+─────────────────────────────────────────────+─────────────────────────────────────────────────────+
| 2. Áp đặt Kết quả Động vật lên Người        | Nghiên cứu trên chuột/tế bào phải ghi rõ:           |
|    (Animal/In-vitro != Human Clinical)      | "[Tiền lâm sàng] - Chưa được kiểm chứng trên người".|
+─────────────────────────────────────────────+─────────────────────────────────────────────────────+
| 3. Đồng nhất Phòng thí nghiệm với Đời thực  | Hiệu quả trong môi trường kiểm soát chặt không đồng |
|    (Efficacy in Lab != Real-world Effect)   | nghĩa với kết quả ngoài thực tế (Effectiveness).    |
+─────────────────────────────────────────────+─────────────────────────────────────────────────────+
| 4. Một nghiên cứu nhỏ thành Đồng thuận      | 1 thử nghiệm 20 người không thể đại diện cho toàn bộ|
|    (Single Small Study != Scientific Consensus) giới khoa học. Phải ghi rõ quy mô và tính đơn lẻ.|
+─────────────────────────────────────────────+─────────────────────────────────────────────────────+
| 5. Không tìm thấy bằng chứng = Không có hại | "Absence of evidence is not evidence of absence".   |
|    (Lack of Evidence != Evidence of Safety) | Không tìm thấy nguy cơ != Đã chứng minh an toàn 100%|
+─────────────────────────────────────────────+─────────────────────────────────────────────────────+
| 6. Coi Preprint là Chân lý đã khẳng định    | Preprint chưa qua Peer-review phải luôn gắn nhãn    |
|    (Preprint != Confirmed Science)          | cảnh báo sơ bộ, chưa có giá trị định luận.          |
+─────────────────────────────────────────────+─────────────────────────────────────────────────────+
| 7. Diễn giải quá đà vượt kết luận tác giả   | Không được thêm thắt ý kiến cá nhân vượt quá phạm vi|
|    (Over-extrapolation)                     | mà tác giả đã khẳng định trong mục Conclusion.      |
+─────────────────────────────────────────────+─────────────────────────────────────────────────────+
```

---

## 3. CÁCH XỬ LÝ KHI THIẾU BẰNG CHỨNG HOẶC KẾT QUẢ MÂU THUẪN

* **Khi không đủ bằng chứng:** Bắt buộc sử dụng phát biểu chuẩn mực:
  > *"Chưa tìm thấy đủ bằng chứng khoa học đáng tin cậy để đưa ra kết luận về vấn đề này."*
* **Khi có kết quả mâu thuẫn (Conflicting Evidence):**
  * Tuyệt đối không được thiên vị chọn nghiên cứu hợp nhãn mình.
  * Phải trình bày song song cả hai phía: Nhóm nghiên cứu A ($n=...$, phương pháp...) cho thấy kết quả X, trong khi nhóm nghiên cứu B ($n=...$, phương pháp...) cho thấy kết quả Y.
  * Phân tích các nguyên nhân kỹ thuật có thể giải thích sự khác biệt: Khác biệt về liều dùng, tiêu chuẩn chọn đối tượng, phương pháp đo lường, thời gian theo dõi.
