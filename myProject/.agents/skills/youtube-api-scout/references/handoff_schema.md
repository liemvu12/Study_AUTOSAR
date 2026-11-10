# Handoff Manifest Schema Specification (v1.0.0)

Tài liệu này định nghĩa cấu trúc chuẩn của file hợp đồng giao vận `handoff_manifest.json` được xuất xưởng bởi skill `youtube-api-scout` để chuyển tiếp quyền xử lý sang skill `youtube-market-researcher`.

---

## 1. Mục Đích & Nguyên Tắc Thiết Kế

1. **Phân Định Trách Nhiệm Rõ Ràng (Separation of Concerns):**
   - `youtube-api-scout` chịu trách nhiệm thu thập số liệu chính thức từ YouTube Data API v3, chuẩn hóa thời gian, tính toán Leave-One-Out Median, phân loại Age Cohort, đối soát Floor Threshold, và phân biệt Lifetime/Snapshot VPH.
   - `youtube-market-researcher` chỉ tiếp nhận danh sách các video đột biến đã được chứng thực (`floor_cleared = true`) để tiến hành mổ xẻ nội dung định tính (Hook transcript, comment mining, audio/visual structure) mà không cần tính lại outlier từ đầu.
2. **Minh Bạch Dữ Liệu & Nhãn Phân Biệt:**
   - Dữ liệu truy xuất trực tiếp từ API bắt buộc mang nhãn quy ước `[RAW DATA]`.
   - Các chỉ số phái sinh do thuật toán tính toán bắt buộc mang nhãn quy ước `[CALCULATED]`.
3. **Truy Xuất Nguồn Gốc (Data Provenance):**
   - Mọi manifest bắt buộc gắn liền với một `run_id` duy nhất và timestamp ISO 8601 để phục vụ kiểm toán độc lập bởi `report-reliability-auditor`.

---

## 2. Cấu Trúc JSON Chuẩn (Canonical JSON Format)

```json
{
  "schema_version": "1.0.0",
  "run_id": "RUN_20261023_153000_X7Y8",
  "generated_at": "2026-10-23T15:30:00Z",
  "source_skill": "youtube-api-scout",
  "target_skill": "youtube-market-researcher",
  "audit_status": "READY_FOR_PIPELINE",
  "channel": {
    "channel_id": "UCxxxxxxxxxxxxxxxxxxxx",
    "uploads_playlist_id": "UUxxxxxxxxxxxxxxxxxxxx",
    "title": "Channel Name",
    "handle": "@ChannelHandle",
    "custom_url": "https://www.youtube.com/@ChannelHandle",
    "raw_metrics": {
      "subscriber_count": 125000,
      "video_count": 340,
      "view_count": 18500000
    }
  },
  "pipeline_parameters": {
    "min_floor_views": 500,
    "outlier_multiplier_threshold": 2.5,
    "sample_size_analyzed": 50,
    "age_cohort_enabled": true
  },
  "provenance": {
    "api_version": "YouTube Data API v3",
    "quota_units_consumed": 2,
    "endpoint_flow": [
      "channels.list (1 unit - contentDetails)",
      "playlistItems.list (1 unit - uploads 50 items)",
      "videos.list (1 unit - batch statistics/contentDetails 50 items)"
    ],
    "local_quota_tracker_snapshot": {
      "daily_used_estimate": 142,
      "daily_limit_budget": 10000,
      "pt_reset_timestamp": "2026-10-24T07:00:00Z"
    }
  },
  "cohort_summaries": {
    "recent_lte_14d": { "count": 4, "median_views": 3200 },
    "growth_15_60d": { "count": 12, "median_views": 5800 },
    "established_61_180d": { "count": 18, "median_views": 7500 },
    "evergreen_gt_180d": { "count": 16, "median_views": 11200 }
  },
  "candidates": [
    {
      "video_id": "dQw4w9WgXcQ",
      "title": "Tên Video Đột Biến",
      "published_at": "2026-10-01T12:00:00Z",
      "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
      "raw_data": {
        "view_count": 85000,
        "like_count": 4200,
        "comment_count": 680,
        "iso_duration": "PT8M24S",
        "duration_seconds": 504
      },
      "calculated_metrics": {
        "age_days": 22.1,
        "age_hours": 530.4,
        "cohort_id": "growth_15_60d",
        "cohort_median_loo": 5600,
        "global_median_loo": 6900,
        "outlier_multiplier_cohort": 15.18,
        "outlier_multiplier_global": 12.32,
        "lifetime_vph": 160.26,
        "snapshot_vph": null,
        "floor_cleared": true,
        "is_shorts_candidate": false,
        "shorts_classification_method": "DURATION_GT_180S"
      },
      "handoff_directives": {
        "action": "EXTRACT_HOOK_AND_MINE_COMMENTS",
        "priority": "HIGH",
        "reason": "Multiplier >= 5.0x (Mega Outlier) vượt ngưỡng sàn 500 lượt xem"
      }
    }
  ]
}
```

---

## 3. Quy Tắc Xác Thực Trường (Field Validation Rules)

| Trường | Bắt Buộc | Kiểu Dữ Liệu | Ràng Buộc Kiểm Toán |
| :--- | :---: | :--- | :--- |
| `schema_version` | Có | String | Phải là `1.0.0`. |
| `run_id` | Có | String | Định dạng `RUN_YYYYMMDD_HHMMSS_<ID>`. |
| `source_skill` | Có | String | Bắt buộc là `youtube-api-scout`. |
| `target_skill` | Có | String | Bắt buộc là `youtube-market-researcher`. |
| `raw_data` | Có | Object | Chỉ chứa số liệu trực tiếp từ API. Tuyệt đối không chứa công thức phái sinh. |
| `calculated_metrics` | Có | Object | Bắt buộc phân tách rõ `cohort_median_loo` (Leave-One-Out) khỏi `global_median_loo`. |
| `floor_cleared` | Có | Boolean | Phải là `true` nếu `view_count >= min_floor_views`. Video có `floor_cleared = false` không được bàn giao sang phân tích hook sâu. |
| `duration_seconds` | Có | Integer | Giây nguyên bản được quy đổi từ `iso_duration`. |
| `is_shorts_candidate`| Có | Boolean | Ghi chú rõ phương pháp xác định (không được khẳng định tuyệt đối nếu chỉ dựa vào thời lượng). |

---

## 4. Giao Thức Đọc & Thực Thi Phía `youtube-market-researcher`

Khi nhận manifest:
1. `youtube-market-researcher` đọc file bằng script `scripts/consume_manifest.py` hoặc đọc trực tiếp từ JSON.
2. Lọc danh sách `candidates` có `floor_cleared == true` và `handoff_directives.action == "EXTRACT_HOOK_AND_MINE_COMMENTS"`.
3. Dùng `youtube-transcript-api` và `youtube-comment-downloader` để bóc tách hook và bình luận cho các video này.
4. Trả kết quả kèm `run_id` để `report-reliability-auditor` có thể đối chiếu chéo toàn diện.
