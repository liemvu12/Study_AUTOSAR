# YouTube Market Research Playbook & Quantitative Benchmarks

Tài liệu hướng dẫn phương pháp luận và chuẩn mực định lượng phục vụ điều tra thị trường YouTube chuyên sâu.

---

## 1. Hệ Thống Chỉ Số Định Lượng (Quantitative Metrics)

### 1.1 Sức Khỏe Kênh: Tỷ Lệ $V/S$ (Views-to-Subscribers Ratio)
$$V/S = \frac{\text{Lượt xem trung vị 10-30 video gần nhất}}{\text{Tổng số người đăng ký (Subscribers)}} \times 100\%$$

* **$V/S > 100\%$ (Cực kỳ thịnh vượng):** Kênh đang bùng nổ dữ dội. Thuật toán đẩy nội dung ra đại chúng (Non-subscribers chiếm >80% view).
* **$V/S \in [30\% - 100\%]$ (Khỏe mạnh & Tăng trưởng):** Tệp khán giả trung thành cao, tỷ lệ giữ chân (AVD) và click (CTR) tốt.
* **$V/S \in [10\% - 30\%]$ (Ổn định / Bão hòa):** Kênh vận hành đều đặn nhưng ít có đột phá thuật toán mới.
* **$V/S < 5\%$ (Kênh đang chết dần):** Tệp subs không còn tương tác (Ghost subscribers). Không nên lấy các kênh này làm hình mẫu tăng trưởng.

---

### 1.2 Radar Đột Biến: Hệ Số Outlier Multiplier
Tại sao dùng **Median (Trung vị)** thay vì **Mean (Trung bình cộng)**?
* Vì một video đạt 50 triệu view sẽ kéo chỉ số trung bình của 20 video khác lên cao một cách giả tạo. Trung vị phản ánh chính xác hiệu suất thực tế của một video bình thường.

$$\text{Multiplier} = \frac{\text{Lượt xem của Video}}{\text{Trung vị lượt xem của kênh}}$$

* **$\text{Multiplier} \ge 5.0\times$ (Mega Outlier):** Đề xuất diện rộng cấp hệ thống. Thuật toán đã phá vỡ rào cản tệp khán giả ban đầu. Bắt buộc mổ xẻ tiêu đề, thumbnail và kịch bản để tái tạo lại.
* **$\text{Multiplier} \in [2.5\times - 5.0\times]$ (Strong Outlier):** Chủ đề có nhu cầu vượt trội hoặc đóng gói (Packaging) xuất sắc.
* **$\text{Multiplier} \in [0.8\times - 1.2\times]$ (Baseline):** Video thông thường của kênh.
* **$\text{Multiplier} < 0.5\times$ (Underperforming):** Chủ đề thị trường từ chối hoặc bao bì đóng gói thất bại.

---

## 2. Chuẩn Mực Nhịp Điệu Lời Thoại (Pacing & WPM Benchmarks)

Chỉ số **Words Per Minute (WPM)** đo lường mật độ thông tin và tốc độ truyền đạt:

| Thể Loại & Nhóm Khán Giả | WPM Chuẩn | Phân Tích Tâm Lý Học |
| :--- | :--- | :--- |
| **Trẻ em mầm non (1–4 tuổi)** | **70 – 100 WPM** | Não bộ chưa hoàn thiện khả năng xử lý ngôn ngữ nhanh; cần khoảng lặng âm nhạc, hiệu ứng âm thanh và câu ngắn. |
| **Thiếu nhi & Hoạt hình (5–10 tuổi)** | **100 – 125 WPM** | Tốc độ vừa phải, ngữ điệu biểu cảm cao (High voice pitch variance). |
| **Phim tài liệu / Phân tích chuyên sâu** | **125 – 145 WPM** | Tốc độ chuẩn mực phát thanh, tạo cảm giác uy tín, đĩnh đạc, dễ ngấm thông tin. |
| **Tech Review / Kể chuyện nhanh** | **145 – 170 WPM** | Kích thích dopamine liên tục, cắt gọt sạch hơi thở và khoảng lặng (Jump-cuts). |
| **YouTube Shorts / TikTok** | **170 – 210+ WPM** | Dồn nén năng lượng tối đa để ngăn chặn hành vi quẹt bỏ (Swiping away). |

---

## 3. Giải Phẫu 30 Giây Đầu (The First 30s Hook Anatomy)

70% tỷ lệ giữ chân (Retention) được quyết định trong 30 giây đầu tiên:

1. **The Cold Open (0–5s):**
   * *Sai lầm:* Hiện logo kênh, giới thiệu "Chào mừng các bạn đã quay trở lại kênh của tôi...".
   * *Đúng chuẩn:* Đi thẳng vào tâm điểm mâu thuẫn hoặc câu hỏi lớn nhất của video ("Điều gì sẽ xảy ra nếu...").
2. **The Stakes & Promise (5–15s):**
   * Cho người xem thấy họ sẽ nhận được gì nếu xem đến cuối, hoặc điều tồi tệ gì sẽ xảy ra nếu họ bỏ lỡ.
3. **The Open Loop (15–30s):**
   * Mở ra một vòng lặp tò mò (Curiosity Loop) chưa được giải đáp ngay lập tức để giữ chân người xem sang phút thứ 2.

---

## 4. Khai Thác Bình Luận (Audience Comment Mining Taxonomy)

Khi quét dữ liệu bình luận từ `mine_comments.py`, tập trung vào 3 nhóm vàng:

1. **Unmet Desires (Nhu cầu chưa được đáp ứng):**
   * *"Mong kênh làm về chủ đề X..."*
   * *"Sao không thấy ai nói về góc độ Y..."*
   $\rightarrow$ Đây là ý tưởng video tiếp theo của bạn với nhu cầu thị trường có sẵn 100%.
2. **Confusion / Friction Points (Điểm nghẽn gây khó chịu):**
   * *"Nhạc nền to quá át cả lời..."*
   * *"Đoạn phút 3:20 giải thích nhanh quá không hiểu..."*
   $\rightarrow$ Điểm yếu của đối thủ chính là điểm mạnh cạnh tranh của bạn.
3. **Emotional Resonance Triggers (Đoạn gây ấn tượng mạnh):**
   * *"Đoạn 04:15 làm mình nổi da gà..."*
   $\rightarrow$ Học cách sao chép kỹ thuật dàn dựng tại đúng thời điểm đó.
