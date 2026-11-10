# QUY TRÌNH TÌM KIẾM & CHIẾN LƯỢC TRUY VẤN ĐA NGUỒN (SEARCH STRATEGY)

Tài liệu này định nghĩa phương pháp luận tìm kiếm học thuật chuẩn hóa cho **Scientific Research Lookup Skill**.

---

## 1. KHUNG ĐỊNH HÌNH CÂU HỎI NGHIÊN CỨU (PICO & PECO)

Trước khi gửi bất kỳ truy vấn tìm kiếm nào, Agent bắt buộc phải chuyển đổi yêu cầu của người dùng thành khung câu hỏi nghiên cứu chuẩn y sinh hoặc kỹ thuật:

### Khung PICO (Nghiên cứu Can thiệp / Lâm sàng):
* **P (Population / Patient / Problem):** Quần thể đối tượng hoặc vấn đề cụ thể (Ví dụ: Trẻ em từ 2–5 tuổi; bệnh nhân tiểu đường type 2).
* **I (Intervention / Exposure):** Can thiệp hoặc yếu tố tiếp xúc (Ví dụ: Bổ sung Creatine; tiếp xúc ánh sáng xanh trước khi ngủ).
* **C (Comparison / Control):** Đối chứng (Ví dụ: Giả dược (Placebo); nhóm không tiếp xúc ánh sáng xanh).
* **O (Outcome):** Kết cục đo lường (Ví dụ: Rụng tóc; chất lượng giấc ngủ / nồng độ melatonin; HbA1c).

### Khung PECO (Nghiên cứu Dịch tễ / Môi trường):
* **P:** Quần thể.
* **E (Exposure):** Yếu tố phơi nhiễm (ô nhiễm không khí, thói quen sinh hoạt).
* **C:** Nhóm không phơi nhiễm.
* **O:** Tỷ lệ mắc bệnh hoặc biến cố sức khỏe.

---

## 2. XÂY DỰNG CHÙM TỪ KHÓA & LOGIC BOOLEAN

Không bao giờ tìm kiếm bằng một câu tự nhiên duy nhất. Bắt buộc tạo ra chùm từ khóa gồm 3 tầng:

1. **Thuật ngữ chính (Primary Keywords):** Khái niệm cốt lõi.
2. **Từ đồng nghĩa & Thuật ngữ y sinh (Synonyms & MeSH Terms):**  
   * *Ví dụ:* "Sleep" $\rightarrow$ `sleep OR circadian rhythm OR sleep latency OR melatonin secretion`.
   * *Ví dụ:* "Blue light" $\rightarrow$ `blue light OR screen time OR short-wavelength light OR digital devices`.
3. **Toán tử Boolean:** Kết hợp `AND`, `OR`, `NOT` và dấu ngoặc kép `""` cho cụm từ chính xác:
   * `("blue light" OR "screen time") AND ("sleep quality" OR "melatonin") AND ("children" OR "pediatric" OR "adolescent")`

---

## 3. CƠ SỞ DỮ LIỆU ĐƯỢC CHỈ ĐỊNH THEO CHUYÊN NGÀNH

Mỗi lĩnh vực phải được tra cứu trên cơ sở dữ liệu chuyên trách:

| Chuyên ngành | Cơ sở dữ liệu ưu tiên | Cú pháp truy vấn mẫu |
| :--- | :--- | :--- |
| **Y sinh & Sức khỏe** | PubMed (NCBI), Cochrane Library, medRxiv, bioRxiv | `site:pubmed.ncbi.nlm.nih.gov "meta-analysis" ...` |
| **Khoa học đa ngành** | Google Scholar, ScienceDirect, Nature, Science, SpringerLink | `site:sciencedirect.com "systematic review" ...` |
| **Kỹ thuật & Công nghệ** | IEEE Xplore, ACM Digital Library, arXiv (cs, stat, math) | `site:ieeexplore.ieee.org OR site:arxiv.org ...` |
| **Khoa học Xã hội & Tâm lý** | JSTOR, PsycINFO, ERIC, DOAJ | `site:jstor.org ...` |
| **Dữ liệu đăng ký thử nghiệm** | ClinicalTrials.gov, WHO ICTRP | Tra cứu mã thử nghiệm (NCT ID) |

---

## 4. QUY TẮC ĐỐI CHIẾU ĐA NGUỒN ĐỘC LẬP (TRIANGULATION)

1. **Quy tắc Tối thiểu 2 Nguồn:** Mọi kết luận khoa học phải được kiểm chứng qua tối thiểu 2 cơ sở dữ liệu hoặc 2 nhóm nghiên cứu độc lập.
2. **Không tin vào Snippet tìm kiếm:** Không bao giờ trích dẫn một bài báo chỉ dựa vào 2 dòng mô tả tóm tắt trên Google Search. Bắt buộc phải mở trang chính thức của bài báo (PubMed, DOI landing page) để đọc trực tiếp.
3. **Truy ngược Citation gốc (Primary Source First):** Nếu bài báo A trích dẫn số liệu của bài báo B, phải tìm và đọc trực tiếp bài báo B để xác nhận số liệu gốc, tránh hiện tượng trích dẫn sai truyền tiêu (citation chain distortion).
