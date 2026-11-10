# EVIDENCE MATRIX (MA TRẬN TRUY VẾT BẰNG CHỨNG)

Evidence Matrix là công cụ cốt lõi giúp người dùng có thể kiểm tra ngược từ mọi khẳng định trong báo cáo về bài báo gốc, vị trí đoạn văn, phương pháp và cỡ mẫu.

---

## 1. CẤU TRÚC BẢNG TIÊU CHUẨN

Mọi báo cáo trong chế độ `DEEP RESEARCH`, `CLAIM VERIFICATION` hoặc `LITERATURE COMPARISON` bắt buộc phải có bảng này:

| Claim ID | Khẳng định cụ thể (Claim) | Nguồn hỗ trợ (Citation) | Vị trí bằng chứng (Location) | Thiết kế nghiên cứu & Cỡ mẫu (Design & Sample) | Tính chất bằng chứng (Direct / Indirect) | Hạn chế chính (Limitations) | Phán quyết / Độ tin cậy (Status & Confidence) |
| :---: | :--- | :--- | :--- | :--- | :---: | :--- | :---: |
| **C-01** | [Mô tả khẳng định] | [Tác giả, Năm, DOI/PMID] | [Abstract / Results, Table 1] | [RCT / Meta-analysis / Cohort, n=...] | `Direct` / `Indirect` | [Hạn chế do tác giả nêu hoặc phương pháp] | `SUPPORTED` (High) |
| **C-02** | [Mô tả khẳng định] | [Tác giả, Năm, DOI/PMID] | [Discussion, Para 3] | [Animal Study / In-vitro, n=...] | `Indirect` | [Chưa kiểm chứng lâm sàng trên người] | `PARTIALLY SUPPORTED` (Low) |
| **C-03** | [Mô tả khẳng định] | [Chưa có nguồn] | N/A | N/A | N/A | [Thiếu dữ liệu thực nghiệm] | `UNSUPPORTED` (Insufficient) |

---

## 2. ĐỊNH NGHĨA CÁC TRƯỜNG DỮ LIỆU

1. **Claim ID:** Mã số nhận diện duy nhất cho khẳng định (C-01, C-02, C-03...).
2. **Claim:** Phát biểu cụ thể, chính xác, không mập mờ (Ví dụ: *"Uống Creatine monohydrate 5g/ngày trong 12 tuần không làm tăng nồng độ DHT huyết thanh ở vận động viên nam trẻ"*).
3. **Supporting Source:** Tác giả chính, năm xuất bản, tên tạp chí và liên kết DOI hoặc PMID.
4. **Evidence Location:** Vị trí chính xác trong tài liệu gốc (Ví dụ: *Results section, Table 2, p. 145* hoặc *Abstract paragraph 3*).
5. **Study Design & Sample:** Thiết kế nghiên cứu chuẩn và số lượng mẫu cụ thể (Ví dụ: *Double-blind RCT, n = 34 rugby players*).
6. **Direct / Indirect Evidence:**
   * `Direct`: Đo lường trực tiếp kết cục nghiên cứu.
   * `Indirect`: Đo lường chỉ số trung gian hoặc suy luận cơ chế sinh học.
7. **Limitations:** Các hạn chế quan trọng nhất ảnh hưởng đến khả năng khái quát hóa kết quả.
8. **Status & Confidence:**
   * Nhãn phân loại: `SUPPORTED`, `PARTIALLY SUPPORTED`, `CONFLICTING`, `UNSUPPORTED`, `NOT ENOUGH EVIDENCE`.
   * Mức độ tin cậy: `High`, `Moderate`, `Low`, `Insufficient`.
