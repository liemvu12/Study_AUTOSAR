# QUY TRÌNH XÁC MINH CITATION & ĐỊNH DANH HỌC THUẬT (CITATION VERIFICATION PROTOCOL)

Tài liệu này hướng dẫn cách kiểm định tính xác thực của tài liệu khoa học và phát hiện các bài báo bị rút hoặc tạp chí giả mạo.

---

## 1. BẢNG TIÊU CHÍ XÁC MINH TÀI LIỆU (7 ĐIỂM KIỂM ĐỊNH)

Mỗi công trình khoa học được đưa vào báo cáo phải vượt qua đầy đủ 7 điểm kiểm định:

1. **Tiêu đề chính xác (Canonical Title):** Đúng từng từ, không tóm tắt hay tự ý sửa tiêu đề.
2. **Danh sách tác giả (Author List):** Tác giả chính (First author), tác giả liên hệ (Corresponding author), hoặc ghi rõ dạng `et al.` nếu trên 3 tác giả.
3. **Năm công bố (Year of Publication):** Phân biệt giữa năm đăng trực tuyến (online first/ahead of print) và năm xuất bản bản in chính thức.
4. **Cơ quan / Tạp chí phát hành (Venue / Journal):** Tên đầy đủ của tạp chí có bình duyệt hoặc kỷ yếu hội nghị.
5. **Mã định danh duy nhất (Permanent Identifier):** Bắt buộc phải có **DOI (Digital Object Identifier)** hoặc **PMID (PubMed ID)** hoặc mã lưu trữ **arXiv ID**.
6. **URL chính thức:** Đường dẫn đến trang xuất bản (ví dụ: `https://doi.org/10.xxxx/...` hoặc `https://pubmed.ncbi.nlm.nih.gov/...`).
7. **Trạng thái xuất bản (Publication Status):**
   * `Peer-Reviewed Journal Article` (Đã bình duyệt)
   * `Systematic Review / Meta-Analysis` (Tổng quan hệ thống)
   * `Conference Paper` (Hội nghị)
   * `Preprint` (Bản thảo chưa bình duyệt: arXiv, bioRxiv, medRxiv)
   * `Official Institutional Report` (Báo cáo cơ quan chính phủ/viện nghiên cứu)

---

## 2. QUY TRÌNH KIỂM TRA ĐÍNH CHÍNH & RÚT BÀI (RETRACTION & CORRECTION)

`[BẮT BUỘC]` Trước khi trích dẫn một bài báo, phải kiểm tra xem bài báo có bị rút bài (Retracted) hoặc đính chính lớn (Major Correction/Expression of Concern) hay không:

* **Sử dụng script:** Chạy `python verify_citation.py --doi <DOI>` để kiểm tra trường `update-to` của Crossref.
* **Tra cứu cơ sở dữ liệu Retraction Watch:** Kiểm tra xem bài báo có nằm trong danh mục rút bài vì lỗi dữ liệu, ngụy tạo số liệu hoặc vi phạm đạo đức nghiên cứu hay không.
* **Nếu bài báo bị Retracted:** Tuyệt đối không sử dụng làm bằng chứng ủng hộ cho kết luận. Nếu đề cập, phải ghi rõ:  
  > 🚨 **CẢNH BÁO:** Bài báo này đã bị tạp chí rút bỏ (Retracted) vào ngày [Ngày] do [Lý do].

---

## 3. QUY ĐỊNH VỀ PREPRINTS (bản thảo chưa phản biện)

Preprint là các bài báo đăng tải trên kho mở (arXiv, bioRxiv, medRxiv, SSRN) mà chưa trải qua quy trình bình duyệt kín (Peer review):

1. **Điều kiện sử dụng:** Chỉ được sử dụng preprint khi:
   * Vấn đề nghiên cứu quá mới (trong vòng vài tháng) và chưa có nghiên cứu peer-reviewed nào xuất bản về chủ đề đó.
   * Để nắm bắt phương pháp hoặc xu hướng tiên phong.
2. **Cảnh báo bắt buộc:** Khi trích dẫn preprint, bắt buộc phải gắn nhãn:
   > `[PREPRINT - NOT PEER REVIEWED]`  
   > *"Tài liệu này là bản thảo chưa qua phản biện độc lập, kết quả chỉ mang tính tham khảo ban đầu và chưa được xác nhận thành tri thức khoa học chính thức."*

---

## 4. DẤU HIỆU NHẬN DIỆN TẠP CHÍ RÁC / XUẤT BẢN THẢM HỌA (PREDATORY JOURNALS)

Agent phải cảnh giác và loại bỏ các bài báo xuất phát từ "tạp chí săn mồi" (Predatory publishers):
* Phí đăng bài cao bất thường đi kèm cam kết "phản biện thần tốc" (review trong 2-3 ngày).
* Trang web tạp chí mập mờ, tên nhái theo các tạp chí nổi tiếng (ví dụ nhái tên *The Lancet* hay *Nature*).
* Không có mã chỉ mục trên PubMed, Scopus, Web of Science, DOAJ.
* Ban biên tập là các tên tuổi giả mạo hoặc nhà khoa học không có thật trong lĩnh vực.
