# Quy Chuẩn Toán Học & Thuật Toán Phát Hiện Outlier (Outlier Math Specification)

Tài liệu này xác lập nền tảng toán học, công thức tính toán và các nguyên tắc phân tầng dữ liệu cho module `outlier_engine.py` thuộc skill `youtube-api-scout`.

---

## 1. Thuật Toán Trung Vị Loại Trừ Bản Thân (Leave-One-Out / Jackknife Median)

### 1.1 Khiếm Khuyết Của Trung Vị Thông Thường (Standard Median)
Trong thống kê thông thường, trung vị toàn bộ tập hợp $M = \text{Median}(X)$ chứa chính phần tử đang được đánh giá $x_i$.
- Khi kích thước mẫu nhỏ ($N = 10 \sim 30$) và phần tử $x_i$ có giá trị cực lớn, $x_i$ kéo phân vị của tập hợp lên cao, làm giảm độ nhạy của phép đo bội số.
- Ngược lại, nếu tập hợp có nhiều giá trị 0 hoặc cực thấp, việc tính $x_i$ trong mẫu làm lệch chuẩn cục bộ.

### 1.2 Công Thức Leave-One-Out (LOO)
Để loại bỏ hoàn toàn ảnh hưởng tự thân (self-skewing bias) của video ứng viên, thuật toán Leave-One-Out tách riêng video $x_i$ ra khỏi tập hợp trước khi tính trung vị:

$$\text{Tập hợp đối chiếu}_{\setminus i} = X \setminus \{x_i\} = \{x_1, x_2, \dots, x_{i-1}, x_{i+1}, \dots, x_N\}$$

$$\text{Median}_{\setminus i} = \text{Median}\left(\text{Tập hợp đối chiếu}_{\setminus i}\right)$$

Bội số tăng trưởng đột biến (Leave-One-Out Multiplier) của video $i$ được xác định là:

$$\text{Multiplier}_i = \frac{x_i}{\max(\text{Median}_{\setminus i}, 1.0)}$$

*(Lưu ý: Mẫu số luôn lấy tối thiểu là $1.0$ để triệt tiêu lỗi chia cho 0 khi trung vị bằng 0).*

---

## 2. Phân Tầng Theo Nhóm Tuổi Phát Hành (Age Cohort Stratification)

### 2.1 Bản Chất Của Lực Tích Lũy Thời Gian (Cumulative Bias)
Một video phát hành 2 năm trước có 100,000 lượt xem không thể so sánh cơ học với một video mới phát hành 3 ngày trước đạt 15,000 lượt xem:
- Video 2 năm tuổi có thời gian tích lũy 730 ngày (trung bình ~136 view/ngày).
- Video 3 ngày tuổi đạt 15,000 view tức tốc độ tích lũy lên tới 5,000 view/ngày!
Nếu tính chung một trung vị toàn kênh (Global Median), video mới sẽ bị đánh giá thấp sai lệch (False Negative), trong khi video cũ bị gán mác đột biến sai lệch (False Positive).

### 2.2 Bốn Nhóm Tuổi Tiêu Chuẩn (Standard Age Cohorts)
Thuật toán phân chia video của kênh thành 4 nhóm độc lập:

| Mã Nhóm Cohort | Khoảng Thời Gian Phát Hành | Ý Nghĩa Phân Tích |
| :--- | :--- | :--- |
| `recent_lte_14d` | $\text{Age} \le 14\ \text{ngày}$ | Video đang trong chu kỳ phân phối đề xuất ban đầu. |
| `growth_15_60d` | $14\ \text{ngày} < \text{Age} \le 60\ \text{ngày}$ | Video trong pha tăng trưởng ổn định hoặc suy giảm tự nhiên. |
| `established_61_180d` | $60\ \text{ngày} < \text{Age} \le 180\ \text{ngày}$ | Video đã hoàn thành vòng đời chính, phản ánh lượng fan cứng. |
| `evergreen_gt_180d` | $\text{Age} > 180\ \text{ngày}$ | Video trường tồn (Evergreen/Search), tích lũy qua tìm kiếm. |

**Quy Tắc Tính Bội Số:**
Mỗi video nhận 2 chỉ số:
1. `outlier_multiplier_cohort`: Bội số so với trung vị LOO của các video **cùng nhóm tuổi**.
2. `outlier_multiplier_global`: Bội số so với trung vị LOO của **toàn bộ video** trên kênh.

---

## 3. Ngưỡng Sàn Tuyệt Đối (Absolute Floor Threshold)

### 3.1 Vấn Đề Nhiễu Mẫu Nhỏ (The Low-View Artifact)
Xét ví dụ thực tế:
- Một kênh có 10 video với lượt xem lần lượt là: `[1, 2, 2, 3, 2, 2, 3, 2, 12, 2]`.
- Trung vị LOO của các video thông thường là 2.
- Video đạt 12 view có Multiplier = $12 / 2 = \mathbf{6.0\times}$ (Đạt ngưỡng "Mega Outlier"!).
- **Hệ quả sai lệch:** Đội ngũ sản xuất bỏ 2 ngày phân tích kịch bản hook của một video 12 lượt xem!

### 3.2 Quy Chuẩn Sàn (`MIN_FLOOR`)
Một video chỉ được chính thức gắn cờ là Video Đột Biến Hợp Lệ (`floor_cleared = true`) khi và chỉ khi thỏa mãn đồng thời hai điều kiện:

$$\mathbf{Is\_Outlier} \iff (\text{Multiplier} \ge 2.5\times) \land (\text{ViewCount} \ge \text{MIN\_FLOOR})$$

- Giá trị mặc định của hệ thống: $\text{MIN\_FLOOR} = 500\ \text{views}$ (có thể cấu hình qua cờ `--min-floor`).
- Những video có $\text{Multiplier} \ge 2.5\times$ nhưng $\text{ViewCount} < \text{MIN\_FLOOR}$ sẽ được dán nhãn: `SUB_FLOOR_OUTLIER_REJECTED` và **không được chuyển tiếp** vào pipeline bóc tách kịch bản.

---

## 4. Phân Biệt Tốc Độ Xem: Lifetime VPH vs. Snapshot VPH

Để đánh giá chính xác sức hút của video, hệ thống tách bạch hai chỉ số tốc độ:

### 4.1 Lifetime VPH (Tốc Độ Trung Bình Toàn Vòng Đời)
Đo lường trung bình số lượt xem thu được trên mỗi giờ kể từ khi video được công khai:

$$\text{Lifetime VPH} = \frac{\text{ViewCount}}{\max(\text{Age in Hours}, 1.0)}$$

*Hạn chế:* Chỉ số này giảm dần theo thời gian khi video nguội đi, không phản ánh được một video cũ bất ngờ ăn đề xuất trở lại.

### 4.2 Snapshot VPH (Tốc Độ Bứt Tốc Giữa Hai Thời Điểm Ghi Nhận)
Khi hệ thống có ít nhất hai bản ghi ảnh chụp lịch sử (Snapshot) tại thời điểm $t_1$ và $t_2$ ($t_2 > t_1$):

$$\Delta V = \text{ViewCount}(t_2) - \text{ViewCount}(t_1)$$

$$\Delta t = t_2 - t_1\quad (\text{đơn vị: giờ})$$

$$\text{Snapshot VPH} = \frac{\Delta V}{\Delta t}$$

*Giá trị:* Đây là chỉ số chân thực nhất đo lường mức độ "đang nóng" (Real-time Viral Velocity) của video tại thời điểm hiện tại.

---

## 5. Quy Chuẩn Xử Lý Định Dạng Shorts (Shorts Duration Nuance)

### 5.1 Thay Đổi Chính Sách Kỹ Thuật Của YouTube (15/10/2024)
- Kể từ ngày 15/10/2024, YouTube chính thức nâng giới hạn độ dài của YouTube Shorts từ tối đa 60 giây lên **tối đa 3 phút (180 giây)** đối với video có tỷ lệ khung hình vuông (1:1) hoặc dọc (9:16).
- Mọi video phát hành trước ngày 15/10/2024 có độ dài từ 61s đến 180s vẫn là Long-form video truyền thống.

### 5.2 Quy Tắc Gán Nhãn & Ràng Buộc Kiểm Toán
- **Tuyệt đối cấm** khẳng định *"Thời lượng > 180s lọc chính xác 100% Shorts"* vì:
  1. Video $\le 180$s với tỷ lệ ngang 16:9 vẫn là Long-form video tiêu chuẩn.
  2. Video $\le 180$s tải lên trước 15/10/2024 vẫn được hệ thống YouTube lưu trữ như video dài.
- **Phương Pháp Phân Loại Của Scout:**
  - Nếu `duration_seconds > 180`: Dán nhãn `is_shorts_candidate = false`, phương pháp `DURATION_GT_180S`.
  - Nếu `duration_seconds <= 180`: Dán nhãn `is_shorts_candidate = true`, phương pháp `DURATION_LTE_180S_PENDING_ENDPOINT_OR_ASPECT_RATIO_CHECK`.
  - Giữ thái độ thận trọng, không đưa ra tuyên bố tuyệt đối nếu chưa có thông tin tỷ lệ khung hình hoặc kiểm tra HTTP chuyển hướng tại endpoint `/shorts/<video_id>`.
