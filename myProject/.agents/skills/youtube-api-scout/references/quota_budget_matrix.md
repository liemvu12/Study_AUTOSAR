# Bảng Định Mức Hạn Ngạch & Tối Ưu Chi Phí API (Quota Budget Matrix)

Tài liệu này cung cấp hướng dẫn kiến trúc và ma trận chi phí của **YouTube Data API v3** nhằm giúp `youtube-api-scout` vận hành với chi phí điểm hạn ngạch (Quota Units) tối ưu nhất, ngăn chặn triệt để tình trạng cạn kiệt quota 10,000 units/ngày của tài khoản Google Cloud miễn phí.

---

## 1. So Sánh Kiến Trúc: Truy Vấn Ngây Thơ (Naive) vs. Uploads Playlist (Scout)

Hầu hết các công cụ scraping ngây thơ sử dụng endpoint `search.list` để tìm video của một kênh. Đây là nguyên nhân hàng đầu khiến hạn ngạch bốc hơi chỉ sau vài truy vấn.

| Thao Tác Nghiên Cứu | Cách Tiếp Cận Ngây Thơ (`search.list`) | Giải Pháp Tối Ưu Của Scout (`playlistItems.list`) | Mức Tiết Kiệm Quota |
| :--- | :--- | :--- | :--- |
| **Lấy 50 video của 1 kênh** | Gọi `search.list` với `channelId` $\rightarrow$ **100 units** | Lấy playlist `UU...` + gọi `playlistItems.list` (1 unit) + batch `videos.list` (1 unit) $\rightarrow$ **2 units** | **Tiết kiệm 98% (gấp 50 lần)** |
| **Lấy 200 video của 1 kênh** | 4 lần gọi `search.list` $\rightarrow$ **400 units** | 4 lần `playlistItems.list` (4 units) + 4 lần `videos.list` (4 units) $\rightarrow$ **8 units** | **Tiết kiệm 98%** |
| **Quét 100 kênh đối thủ (mỗi kênh 50 video)** | $100 \times 100 = \mathbf{10,000\ units}$ (Sập quota ngay trong ngày đầu tiên!) | $100 \times 2 = \mathbf{200\ units}$ | **Quét được tới 5,000 kênh/ngày!** |

---

## 2. Chi Phí Chi Tiết Từng Endpoint (Endpoint Quota Cost Breakdown)

Theo tài liệu chính thức từ Google Developers (YouTube Data API v3 Quota Calculator):

| Endpoint | Quota Cost (Units) | Mục Đích Sử Dụng Hợp Lý | Khuyến Nghị Trong Pipeline |
| :--- | :---: | :--- | :--- |
| `channels.list` | **1** | Lấy thông tin kênh, số subs, uploads playlist ID (`contentDetails`). | Dùng 1 lần duy nhất cho kênh mới hoặc tự động hoán đổi `UC` $\rightarrow$ `UU`. |
| `playlistItems.list` | **1** | Duyệt danh sách video trong uploads playlist (tối đa 50 item/trang). | **Phương thức cốt lõi** để lấy `video_id` của toàn bộ kênh. |
| `videos.list` | **1** | Làm giàu metadata theo lô tối đa 50 ID (`snippet,contentDetails,statistics`). | **Phương thức cốt lõi** để lấy views, likes, duration, publishedAt. |
| `commentThreads.list` | **1** | Lấy bình luận video. | **Hạn chế dùng** (ủy thác cho `youtube-market-researcher` cào không tốn quota API). |
| `search.list` | **100** | Tìm kiếm từ khóa mở rộng khi chưa biết Channel ID. | **Tuyệt đối không dùng** để lấy video của một kênh đã biết ID. |

---

## 3. Thuật Toán Hoán Đổi Zero-Cost ID: `UC` $\rightarrow$ `UU`

YouTube quản lý toàn bộ video tải lên của một kênh dưới dạng một playlist hệ thống (Uploads Playlist).
Mã playlist tải lên luôn luôn tuân theo quy tắc toán học:

$$\text{Uploads Playlist ID} = \text{"UU"} + \text{channel\_id}[2:]$$

*Ví dụ:*
- `channel_id` = `UC_x5XG1OV2P6uZZ5FSM9Ttw`
- Thay tiền tố `UC` bằng `UU` $\rightarrow$ `uploads_playlist_id` = `UU_x5XG1OV2P6uZZ5FSM9Ttw`

> [!TIP]
> Việc tự hoán đổi chuỗi ký tự này trong mã nguồn Python giúp giảm chi phí gọi `channels.list` từ 1 unit xuống **0 unit**, biến bước phân giải Uploads Playlist thành hoàn toàn miễn phí!

---

## 4. Chu Kỳ Đặt Lại Hạn Ngạch & Quota Tracker Nội Bộ

1. **Thời Điểm Đặt Lại Server-Side (Reset Time):**
   - Hạn ngạch 10,000 units/ngày của Google Cloud Console được đặt lại chính xác vào **Nửa Đêm Giờ Thái Bình Dương (Midnight Pacific Time - PT)**.
   - Pacific Time thay đổi giữa **PST (UTC-8)** vào mùa đông và **PDT (UTC-7)** vào mùa hè (Daylight Saving Time).
   - Bộ theo dõi nội bộ `quota_tracker.py` tính toán chính xác mốc UTC tương ứng với Midnight PT của ngày kế tiếp.
2. **Bản Chất Của Local Quota Tracker:**
   - Bộ theo dõi local là **ước tính client-side (local estimate)** nhằm bảo vệ tài khoản, ghi log mỗi khi script gửi request API.
   - Không được coi bộ đếm local là số liệu 100% đồng bộ với Google Cloud Console nếu có các ứng dụng khác cùng dùng chung một API Key.
3. **Phân Vùng Ngưỡng An Toàn (Safety Zones):**
   - **Xanh (0 - 7,000 units):** Hoạt động bình thường.
   - **Vàng (7,001 - 9,000 units):** Cảnh báo quota sắp cạn; chỉ cho phép các batch quan trọng.
   - **Đỏ (> 9,000 units):** Kích hoạt cơ chế dừng mềm (Soft Throttling); từ chối quét kênh mới để bảo lưu hạn ngạch dự phòng.

---

## 5. Đính Chính Thuật Ngữ "Zero-Quota"

- Khi làm việc với `youtube-market-researcher` (sử dụng thư viện cào web như `scrapetube`, `youtube-transcript-api`), thuật ngữ chính xác phải là:
  > **"Không dùng hạn ngạch YouTube Data API chính thức (Does not consume YouTube Data API quota)"**
- Tuyệt đối không gọi là *"Zero-Quota vô hạn"* vì việc cào web từ các endpoint công khai vẫn bị giới hạn bởi:
  - Cơ chế chặn IP / Rate limit HTTP 429 từ máy chủ Google.
  - Thử thách Captcha / Bot detection.
  - Thay đổi cấu trúc DOM / JSON nội bộ của YouTube.
- Mô hình phối hợp hai skill theo pipeline giúp kết hợp ưu điểm của cả hai:
  - `youtube-api-scout` dùng API chính thức cực kỳ ổn định, chuẩn xác, không bao giờ bị captcha, chi phí chỉ 2 units/50 video.
  - `youtube-market-researcher` đào sâu transcript và bình luận mà không đốt hàng ngàn units API đắt đỏ.
