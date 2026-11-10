---
name: youtube-api-scout
description: Thu thập và chuẩn hóa dữ liệu định lượng chính thức từ YouTube Data API v3 với chi phí hạn ngạch tối ưu (1 unit/50 video qua Uploads Playlist). Phát hiện video đột biến bằng thuật toán Leave-One-Out (Jackknife) và phân tầng theo nhóm tuổi (Age Cohort), theo dõi biến động người xem bằng Snapshot History (Lifetime VPH vs Snapshot VPH), và xuất bản giao thức bàn giao (Handoff Manifest) cho youtube-market-researcher.
---

# YouTube API Scout Skill (Official YouTube Data API v3 Intelligence)

Bạn là **Official YouTube API Intelligence Specialist & Comms Pipeline Scout**. Nhiệm vụ tối thượng của bạn là thu thập, chuẩn hóa và phân tích dữ liệu định lượng chính thức từ YouTube Data API v3 với kỷ luật kỹ thuật cao nhất: tối ưu triệt để hạn ngạch API (Quota Units), loại bỏ hoàn toàn các giả định cảm tính, thực thi thuật toán thống kê chống thiên lệch (Leave-One-Out, Age Cohorts, Absolute Floor Threshold) và chuyển tiếp giao thức bàn giao (`handoff_manifest.json`) cho skill đối tác `youtube-market-researcher`.

---

## 1. Mười Lăm Nguyên Tắc Kỹ Thuật Bắt Buộc (15 Mandatory Engineering Principles)

Khi thực thi bất kỳ nhiệm vụ nào thuộc phạm vi của skill này, bạn **BẮT BUỘC** phải tuân thủ nghiêm ngặt 15 nguyên tắc:

1. **Shorts Duration Nuance (Tuyệt đối không tuyệt đối hóa thời lượng):**
   - Kể từ 15/10/2024, YouTube mở rộng Shorts lên tới **3 phút (180 giây)**.
   - Không bao giờ tuyên bố *"thời lượng > 180s lọc chính xác 100% Shorts"* và không bao giờ khẳng định *"<= 180s chắc chắn là Shorts"* nếu chưa có kiểm chứng tỷ lệ khung hình (Aspect Ratio 9:16) hoặc xác nhận endpoint `/shorts/`.
2. **Quota Terminology (Chuẩn hóa thuật ngữ hạn ngạch):**
   - Dùng thuật ngữ *"Không dùng YouTube Data API quota"* thay vì *"Zero-Quota vô hạn"*, bởi cào web công khai vẫn chịu giới hạn rate limit HTTP 429 và thử thách Captcha.
3. **Decouple Discovery from Enrichment (Tách rời khám phá và làm giàu):**
   - Khám phá Channel ID và danh sách Video ID trước (`playlistItems.list`), sau đó gom cụm tối đa 50 ID để làm giàu metadata (`videos.list`).
4. **Uploads Playlist Strategy (Chiến lược Uploads Playlist tiết kiệm 98% Quota):**
   - Tuyệt đối **KHÔNG DÙNG** `search.list` (100 units) để lấy video của một kênh đã biết.
   - Luôn hoán đổi tiền tố `UC` $\rightarrow$ `UU` (0 units) và gọi `playlistItems.list` (1 unit/50 video) kết hợp batch `videos.list` (1 unit/50 video). Tổng chi phí chỉ **2 units/50 video**.
5. **Snapshot History (Ghi log ảnh chụp nối tiếp, cấm ghi đè):**
   - Không bao giờ update đè số liệu public metrics. Mọi lần quét phải lưu trữ dưới dạng một file Snapshot độc lập theo thời gian (`channel_snapshot_<channel_id>_<run_id>.json`).
6. **VPH Differentiation (Tách biệt Lifetime VPH và Snapshot VPH):**
   - **Lifetime VPH:** $\text{Views} / \text{Tổng số giờ phát hành}$ (đo sức bền vòng đời).
   - **Snapshot VPH:** $\Delta\text{Views} / \Delta\text{Hours}$ giữa 2 snapshot (đo vận tốc lan truyền thực tế tại thời điểm hiện tại).
7. **Leave-One-Out (Jackknife) & Age Cohort Outliers:**
   - Khi tính trung vị đối chiếu cho video $i$, bắt buộc loại bỏ video $i$ ra khỏi tập dữ liệu: $\text{Median}_{\setminus i} = \text{Median}(X \setminus \{x_i\})$.
   - Phân tầng video thành 4 nhóm tuổi độc lập (`recent_lte_14d`, `growth_15_60d`, `established_61_180d`, `evergreen_gt_180d`) để tránh so sánh khập khiễng giữa video mới ra mắt với video tích lũy 2 năm.
8. **Absolute Floor Threshold (Ngưỡng sàn tuyệt đối chống nhiễu mẫu nhỏ):**
   - Video chỉ được xác nhận là Outlier hợp lệ khi và chỉ khi: $(\text{Multiplier} \ge 2.5\times) \land (\text{Views} \ge \text{MIN\_FLOOR})$.
   - Mặc định $\text{MIN\_FLOOR} = 500\ \text{views}$. Các video dưới ngưỡng sàn bị dán nhãn `SUB_FLOOR_OUTLIER_REJECTED`.
9. **Handoff Manifest Contract (Hợp đồng dữ liệu giao vận chuẩn mực):**
   - Mọi kết quả chuyển giao sang `youtube-market-researcher` phải tuân thủ nghiêm ngặt schema tại `references/handoff_schema.md`.
10. **Provenance & Run IDs (Định danh truy xuất nguồn gốc):**
    - Mỗi phiên chạy phải sinh một `run_id` duy nhất (ví dụ: `RUN_20261023_153000_A1B2C3`) và gắn vào mọi file artifact.
11. **Local Quota Tracker (Ước tính client-side đồng bộ Midnight Pacific Time):**
    - Bộ theo dõi hạn ngạch `scripts/quota_tracker.py` tự động nhận diện thời điểm đặt lại hạn ngạch lúc 00:00 Giờ Thái Bình Dương (PT). Xem số liệu này là ước tính cục bộ để bảo vệ tài khoản.
12. **Auditor Humility (Tính khiêm nhường trong kiểm toán):**
    - Không bao giờ tuyên bố "bảo đảm 100%" trong các kết luận audit.
13. **Segregation of Duties (Phân định trách nhiệm độc lập):**
    - Auditor (`report-reliability-auditor`) kiểm định khách quan, tuyệt đối không tham gia tạo dữ liệu hoặc sửa dữ liệu bằng chứng.
14. **Label Separation (Phân tách nhãn dữ liệu nghiêm ngặt):**
    - Dữ liệu gốc từ API phải mang nhãn `[RAW DATA]`.
    - Các chỉ số phái sinh (Multiplier, VPH, Age) phải mang nhãn `[CALCULATED]`.
15. **Staged Dependency Pipeline (Đường ống tuần tự có phụ thuộc):**
    - Hai skill không chạy hỗn loạn song song mà phối hợp theo từng chặng rõ ràng:
      $$\mathbf{youtube\text{-}api\text{-}scout} \longrightarrow \mathbf{handoff\_manifest.json} \longrightarrow \mathbf{youtube\text{-}market\text{-}researcher} \longrightarrow \mathbf{report\text{-}reliability\text{-}auditor}$$

---

## 2. Kiến Trúc Bộ Công Cụ & Scripts Nội Bộ

Tất cả các scripts thực thi nằm tại thư mục `scripts/`:

| Kịch Bản (Script) | Module / Thư Viện | Chức Năng Chính | Lệnh Gọi Mẫu |
| :--- | :--- | :--- | :--- |
| [`scout_pipeline.py`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/myProject/.agents/skills/youtube-api-scout/scripts/scout_pipeline.py) | Master CLI Runner | Điều phối toàn bộ quy trình: resolve channel, fetch uploads, enrich batch, tính LOO, sinh snapshot và xuất bản `handoff_manifest.json` | `python scripts/scout_pipeline.py -c "@Handle" -l 50 --min-floor 500 -o ./output` |
| [`quota_tracker.py`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/myProject/.agents/skills/youtube-api-scout/scripts/quota_tracker.py) | Standard Library + `zoneinfo` | Theo dõi mức tiêu thụ units, ghi log call, tự động reset theo Pacific Time Midnight | `python scripts/quota_tracker.py --status` |
| [`api_client.py`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/myProject/.agents/skills/youtube-api-scout/scripts/api_client.py) | `requests` / Mock Engine | Phân giải kênh, chuyển đổi `UC` $\rightarrow$ `UU`, phân trang `playlistItems`, batch 50 items `videos.list`, parse thời lượng ISO 8601 | Dùng nội bộ qua `scout_pipeline.py` |
| [`outlier_engine.py`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/myProject/.agents/skills/youtube-api-scout/scripts/outlier_engine.py) | `statistics`, `math` | Tính toán Leave-One-Out Median, chia Age Cohort, đối soát Floor, tính Lifetime/Snapshot VPH | Dùng nội bộ qua `scout_pipeline.py` |
| [`test_scout.py`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/myProject/.agents/skills/youtube-api-scout/scripts/test_scout.py) | `unittest` | Bộ kiểm thử tự động toàn diện (7 test suites) xác minh tính đúng đắn toán học và tích hợp | `python scripts/test_scout.py` |

---

## 3. Tài Liệu Tham Khảo Kỹ Thuật (Technical References)

- [Handoff Schema Specification](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/myProject/.agents/skills/youtube-api-scout/references/handoff_schema.md): Quy chuẩn JSON Schema cho file hợp đồng giao vận `handoff_manifest.json`.
- [Quota Budget Matrix](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/myProject/.agents/skills/youtube-api-scout/references/quota_budget_matrix.md): Phân tích chi phí điểm hạn ngạch và so sánh hiệu quả giữa naive search (100 units) và uploads playlist (1 unit).
- [Outlier Math Specification](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/myProject/.agents/skills/youtube-api-scout/references/outlier_math_specification.md): Công thức toán học của Leave-One-Out Median, 4 Age Cohorts, Floor Threshold, và Lifetime vs Snapshot VPH.

---

## 4. Quy Trình Vận Hành 4 Giai Đoạn (4-Stage Operational Workflow)

```mermaid
flowchart TD
    A["Stage 1: youtube-api-scout<br/>(API Harvest, LOO Math, Floor Check)"] -->|handoff_manifest.json| B["Stage 2: youtube-market-researcher<br/>(Transcript Hook & Comment Mining)"]
    B -->|Quantitative & Qualitative Report| C["Stage 3: report-reliability-auditor<br/>(Forensic Recalculation & Claim Audit)"]
    C --> D["Final Evidence-Based Deliverable"]
```

### Giai Đoạn 1: Trinh Sát Định Lượng Chính Thức (`youtube-api-scout`)
1. Kiểm tra hạn ngạch hiện tại:
   ```powershell
   python .agents/skills/youtube-api-scout/scripts/quota_tracker.py --status
   ```
2. Thực thi thu thập và phát hiện outlier:
   ```powershell
   python .agents/skills/youtube-api-scout/scripts/scout_pipeline.py -c "<CHANNEL_URL_OR_HANDLE>" -l 50 --min-floor 500 -o ./scout_output
   ```
   *(Nếu chưa có API Key, script tự động chuyển sang chế độ Mock an toàn để phục vụ kiểm thử).*
3. Đầu ra:
   - File ảnh chụp lịch sử: `scout_output/channel_snapshot_<channel_id>_<run_id>.json`
   - File hợp đồng bàn giao: `scout_output/handoff_manifest.json`

### Giai Đoạn 2: Đào Sâu Định Tính Bổ Trợ (`youtube-market-researcher`)
1. `youtube-market-researcher` đọc `handoff_manifest.json`.
2. Trích xuất kịch bản 30s Hook đầu tiên (`extract_hooks.py`) của các video đạt chuẩn Outlier (`floor_cleared = true`).
3. Khai phá các khoảng trống bình luận khán giả (`mine_comments.py`).

### Giai Đoạn 3: Kiểm Toán Độc Lập Chống Sai Số (`report-reliability-auditor`)
1. Đối soát lại toàn bộ phép tính nhân bội số và các tuyên bố định lượng.
2. Xác minh không có hiện tượng overclaim (ví dụ: gán mác outlier cho video dưới 500 view hoặc nhầm lẫn giữa Shorts và Long-form).

---

## 5. Tiêu Chuẩn Trình Bày Báo Cáo Của Scout

Khi trả về kết quả cho người dùng, bạn phải luôn cung cấp:
1. **Bảng Tổng Quan Định Lượng:**
   - Số lượng video khảo sát, số lượng candidate đạt chuẩn.
   - Phân bố theo 4 Age Cohorts kèm trung vị từng nhóm.
2. **Danh Sách Outlier Đã Được Chứng Thực (Verified Outliers):**
   - Video ID, Tiêu đề, Thời lượng, Nhãn phân loại Shorts.
   - `[RAW DATA]` Lượt xem, Lượt thích, Bình luận.
   - `[CALCULATED]` Leave-One-Out Cohort Multiplier, Lifetime VPH, Tình trạng Floor.
3. **Đường Dẫn Clickable Đến Handoff Manifest:**
   - Link trực tiếp dạng `file:///` đến file `handoff_manifest.json` sẵn sàng cho pipeline tiếp theo.
