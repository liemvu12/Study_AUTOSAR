# TÀI LIỆU DEEP DIVE: NVM MEMORY STACK

Tài liệu này trình bày chuyên sâu về kiến trúc ngăn xếp bộ nhớ (Memory Stack) trong AUTOSAR, cách các khối dữ liệu (Data Blocks) được lưu trữ vào bộ nhớ không bay hơi (Non-volatile Memory) như Flash hoặc EEPROM.

## 1. Stack Overview — Kiến trúc Tổng quan

```
Application (SWC) (Gọi qua RTE)
  | NvM_ReadBlock() / NvM_WriteBlock()
  ▼
NvM (Non-volatile Memory Manager)
  - Quản lý các logical block, map application data vào NvM block.
  - Tính toán và xác minh CRC.
  - Retry mechanisms, quản lý lỗi cơ bản (Error handling).
  | Gọi MemIf_Read() / MemIf_Write()
  ▼
MemIf (Memory Interface Abstraction)
  - Là bộ ghép kênh (Multiplexer).
  - Tra cứu Device ID để định tuyến lệnh gọi xuống module quản lý bộ nhớ thích hợp: Fee (cho Flash) hoặc Ea (cho EEPROM).
  | Gọi Fee_Read() / Fee_Write() hoặc Ea_Read() / Ea_Write()
  ▼
Fee (Flash EEPROM Emulation) | Ea (EEPROM Abstraction)
  - Fee: Mô phỏng hành vi của EEPROM trên phần cứng Flash (cho phép ghi byte/block thay vì phải xóa cả sector lớn).
  - Quản lý Virtual Sector, thực hiện Wear Leveling để cân bằng độ mòn Flash.
  | Gọi Fls_Read() / Fls_Write() / Fls_Erase()
  ▼
Fls (Flash Driver MCAL) | Eeprom Driver
  - Trình điều khiển mức thấp tương tác với vi điều khiển.
  - Đọc, ghi và xóa các physical sector / page trên phần cứng bộ nhớ.
  ▼
[Flash / EEPROM Hardware]
```

## 2. NvM Block Types (Phân loại khối dữ liệu)

NvM phân chia dữ liệu thành các loại Block tùy thuộc vào mức độ quan trọng và cách sử dụng:

| Type | Description (Mô tả) | Use Case (Trường hợp sử dụng điển hình) |
|------|--------------------|----------------------------------------|
| **NATIVE** | Block cơ bản nhất. Chỉ có 1 bản sao (single copy) của dữ liệu trên NV RAM. Header + Data (+ CRC). | Thông số cấu hình (Calibration data), cấu hình người dùng, dữ liệu thông thường. |
| **REDUNDANT** | Có 2 bản sao (2 copies) trên NV RAM. Khi đọc, nếu bản 1 hỏng (CRC sai), nó sẽ thử đọc bản 2. Nâng cao độ tin cậy. | Dữ liệu an toàn hệ thống (Safety-critical), odometer (Odo xe), khóa bảo mật (Immo). |
| **DATASET** | Gồm nhiều Data arrays (datasets). Application có thể chọn index (NvM_SetDataIndex) để đọc/ghi một dataset cụ thể. | DTC freeze frames (Mã lỗi và dữ liệu đóng băng đi kèm), lưu các bản ghi sự cố. |

## 3. Async Operation Pattern (Cơ chế hoạt động bất đồng bộ)

Các thao tác ghi bộ nhớ (nhất là Flash) rất chậm và tốn thời gian (có thể mất vài chục ms). Vì vậy, NvM stack hoạt động hoàn toàn bất đồng bộ.

- **Request:** Khi SWC gọi `NvM_WriteBlock(BlockId, &Data)`, hàm này chỉ đẩy yêu cầu vào hàng đợi (Queue) và trả về `E_OK` ngay lập tức. Dữ liệu chưa thực sự được ghi vào Flash.
- **Background Processing:** Một task hệ điều hành gọi định kỳ (ví dụ mỗi 10ms) hàm `NvM_MainFunction()`. Hàm này sẽ xử lý các yêu cầu trong queue, điều khiển máy trạng thái (State machine) gọi xuống MemIf → Fee → Fls.
- **Completion Notification:**
  - **Polling:** SWC có thể gọi `NvM_GetErrorStatus(BlockId, &Status)` để kiểm tra. Trạng thái `NVM_REQ_PENDING` nghĩa là đang ghi. `NVM_REQ_OK` là xong, `NVM_REQ_FAILED` là có lỗi.
  - **Callback:** Cấu hình một hàm callback (ví dụ `NvM_JobFinishedNotification_BlockX`) để NvM tự động gọi (thông qua RTE) báo cho SWC biết khi hoàn thành.

## 4. NvM_ReadAll() và NvM_WriteAll()

- **NvM_ReadAll():** Gọi trong quá trình khởi động hệ thống (Startup / EcuM_Init). Đọc toàn bộ các block được đánh dấu cấu hình để nạp vào RAM. Nếu Flash trống hoặc dữ liệu lỗi (VD: CRC mismatch), NvM sẽ tự động sao chép giá trị mặc định từ ROM block sang RAM block.
- **NvM_WriteAll():** Gọi trong quá trình tắt máy (Shutdown / EcuM_GoDown). Ghi toàn bộ các block trong RAM đã bị thay đổi (được đánh dấu bằng hàm `NvM_SetRamBlockStatus()`) xuống Flash. Điều này giúp hệ thống hoạt động nhanh trong runtime (chỉ ghi lên RAM) và lưu xuống NV khi tắt máy.

## 5. Fee Wear Leveling (Thuật toán cân bằng độ mòn)

Bộ nhớ Flash có số lần Xóa/Ghi (Erase cycles) giới hạn (thường khoảng 100,000 lần). Khác với EEPROM, Flash chỉ có thể xóa theo Sector/Page lớn (VD: 2KB, 16KB). Fee (Flash EEPROM Emulation) giải quyết vấn đề này.
- **Virtual Sectors:** Cấu hình ít nhất 2 virtual sectors (Ví dụ: Sector A và Sector B). Tại một thời điểm, chỉ một sector đang active (Active Sector).
- **Ghi thêm (Append-only):** Khi cần ghi đè một block, Fee không xóa dữ liệu cũ mà ghi bản sao mới vào khoảng trống tiếp theo của Active Sector, kèm theo một header chứa Block ID và Generation Counter.
- **Garbage Collection / Swap:** Khi Sector A đầy (hết khoảng trống), Fee thực hiện swap. Nó duyệt qua Sector A, copy tất cả dữ liệu hợp lệ (những block phiên bản mới nhất) sang Sector B. Sau đó, nó thực hiện lệnh Erase trên toàn bộ Sector A để dọn trống và đánh dấu Sector B làm Active Sector.

## 6. CRC Protection (Bảo vệ tính toàn vẹn dữ liệu)

Để đảm bảo dữ liệu không bị hỏng (Bit flip) do nhiễu vật lý hoặc quá trình ghi bị ngắt, NvM sử dụng thuật toán kiểm tra lỗi CRC (Cyclic Redundancy Check).
- **Cấu hình:** Có thể chọn CRC8, CRC16, CRC32 cho từng block.
- **Quá trình Ghi:** NvM tính toán CRC của dữ liệu RAM và nối nó vào cuối trước khi chuyển xuống Fee.
- **Quá trình Đọc:** NvM lấy dữ liệu lên, tính lại CRC, và so sánh với giá trị CRC được lưu. Nếu không khớp (mismatch), NvM trả về `NVM_REQ_INTEGRITY_FAILED` và có thể tự khôi phục bằng giá trị mặc định.

## 7. Power-loss Recovery (Phục hồi sau mất điện)

Mất điện đột ngột trong khi ghi (`NvM_WriteAll` đang chạy chưa xong) là rủi ro lớn nhất làm hỏng dữ liệu. Kiến trúc Memory Stack AUTOSAR chống lại điều này bằng cách:
- **Fee Header First:** Fee thường ghi Header (đánh dấu block đang invalid) trước, sau đó ghi Data, rồi mới xác nhận Header là valid. Nếu mất điện giữa chừng, Header chưa valid, hệ thống bỏ qua bản ghi dở dang này ở lần khởi động sau và đọc bản cũ (vẫn còn trên sector vì Fee ghi theo kiểu append).
- **Redundant Blocks:** Với NvM REDUNDANT, quá trình ghi sẽ ghi lần lượt copy 1 rồi copy 2. Nếu hỏng 1 bản, NvM vẫn đọc được bản còn lại.
- **Admin Blocks:** Fee có các block quản trị hệ thống ghi trạng thái swap sector, giúp khôi phục quá trình swap đang dở dang khi có điện trở lại.

## 8. Các Kịch Bản Gỡ Lỗi Điển Hình (Debug Scenarios)

1. **Dữ liệu bị mất sau Power Cycle (Reset lại mất hết biến):**
   - Lỗi do `NvM_SetRamBlockStatus(BlockId, TRUE)` chưa được gọi sau khi thay đổi dữ liệu trên RAM.
   - Hàm `NvM_WriteAll()` ở quá trình Shutdown không có đủ thời gian chạy xong (Tụ điện không đủ xả, ngắt điện quá nhanh).
2. **Lỗi CRC liên tục:**
   - Dữ liệu ở RAM bị task khác ghi đè lên ngay trong lúc `NvM_WriteBlock` (background) đang tính toán CRC (Data Inconsistency).
3. **Fee Sector Full (Không thể ghi tiếp):**
   - Do kích thước cấu hình quá nhỏ, không đủ lưu trữ tất cả PDU cộng thêm các bản update (Append). Cần cấu hình kích thước Virtual Sector lớn hơn tổng dung lượng dữ liệu nhiều lần để chứa các bản sao trong runtime.
4. **Startup quá chậm:**
   - `NvM_ReadAll()` phải đọc quá nhiều khối dữ liệu lớn đồng bộ tại bước EcuM_Init. Nên để tải nền (lazy load) nếu không cần gấp.

## 9. Vị trí Code (Source Code Mapping & Code Example)

Tham chiếu file tiêu chuẩn:
- `as/com/as.infrastructure/memory/NvM/NvM.c` (State machine, CRC calculation)
- `as/com/as.infrastructure/memory/Fee/Fee.c` (Sector swap, wear leveling)
- `as/com/as.infrastructure/memory/MemIf/MemIf.c` (Device router)

**Code C Pattern:**
```c
// Lấy giá trị biến từ RAM (đã được tải lên bởi NvM_ReadAll)
uint8 engineState;
NvM_ReadBlock(NvMConf_NvMBlockDescriptor_EngineState, &engineState);

// Thay đổi dữ liệu và yêu cầu ghi lưu
engineState = ENGINE_RUNNING;
// Báo cho NvM biết RAM block đã bị modify để phục vụ NvM_WriteAll lúc shutdown
NvM_SetRamBlockStatus(NvMConf_NvMBlockDescriptor_EngineState, TRUE);

// Hoặc ép buộc ghi lập tức xuống Flash
NvM_WriteBlock(NvMConf_NvMBlockDescriptor_EngineState, &engineState);

// Trong background task:
void OS_Task_10ms() {
    NvM_MainFunction(); // Xử lý queue
    Fee_MainFunction(); // Tương tác Flash hardware
    Fls_MainFunction();
}
```

## 10. 20 Câu Hỏi Phỏng Vấn (Interview Q&A)

1. **Q:** Sự khác biệt cơ bản giữa EEPROM và Flash là gì? Tại sao cần lớp Fee?
   **A:** EEPROM có thể xóa ghi theo từng byte/word. Flash phải xóa cả khối lớn (Sector) trước khi ghi. Fee mô phỏng khả năng xóa/ghi byte của EEPROM trên nền Flash bằng cách ghi nối vào chỗ trống và chuyển đổi block (Swap sector) ẩn dưới nền.
2. **Q:** Khi nào NvM sử dụng ROM Block?
   **A:** Khi Flash hoàn toàn trắng (lần khởi động đầu tiên) hoặc dữ liệu từ Flash bị lỗi CRC, NvM tự động load Default data từ ROM (Flash program memory) đè lên RAM.
3. **Q:** NvM REDUNDANT hoạt động thế nào khi bị lỗi 1 block?
   **A:** Khi đọc copy 1 sai CRC, NvM đọc sang copy 2. Nếu đúng, nó tải lên RAM, và sau đó (thường là ngầm định) nó sẽ tự động ghi đè bản đúng đó lên bản copy 1 đang hỏng (Recovery mechanism).
4. **Q:** MemIf dùng để làm gì trong khi chỉ có hệ thống Flash (Fee)?
   **A:** Kiến trúc AUTOSAR bắt buộc phải qua MemIf để đồng nhất giao diện (API) cho NvM. MemIf giúp trừu tượng hóa phần cứng. Ta có thể thêm Ea mà không đổi NvM.
5. **Q:** Vì sao không nên gọi trực tiếp `NvM_WriteBlock` trong ngắt cấp cao?
   **A:** Ngắt yêu cầu thời gian thực thi cực ngắn. NvM có thể tốn time để copy buffer (nếu có explicit sync). Yêu cầu chỉ nên chạy ở task context.
6. **Q:** Wear Leveling của Fee là thuật toán Tĩnh (Static) hay Động (Dynamic)?
   **A:** Thường là Dynamic. Các block bị thay đổi nhiều (như Odo) sẽ di chuyển khắp Sector. Các block tĩnh (ít đổi) chỉ dời đi khi Sector Swap.
7. **Q:** Lỗi "Sector Swap not finished" có thể gây hậu quả gì?
   **A:** Hệ thống có thể bị block các thao tác write khác hoặc thậm chí mất dữ liệu nếu sector B chưa kịp copy xong mà Sector A bị hỏng.
8. **Q:** DataIndex trong cấu hình DATASET được lưu ở đâu?
   **A:** Lớp Application (SWC) tự giữ và set nó thông qua `NvM_SetDataIndex(BlockId, index)` trước khi gọi Read/Write block đó.
9. **Q:** Sự khác biệt giữa `NvM_ReadBlock()` và việc trực tiếp truy cập vào RAM Mirror?
   **A:** NvM_ReadBlock ra lệnh cho máy trạng thái lấy dữ liệu từ Flash (chờ NvM_MainFunction chạy) đẩy lên RAM. Nếu lấy thẳng RAM Mirror thì chỉ đọc giá trị trong RAM hiện tại (tải từ lúc bootup).
10. **Q:** Làm thế nào để đảm bảo RAM Data Consistency khi WriteBlock?
    **A:** Cấu hình "Explicit Synchronization". Khi đó NvM dùng callback `NvM_ReadRamBlockFromNvM` hoặc `NvM_WriteRamBlockToNvM` ép ứng dụng cung cấp bản copy dữ liệu an toàn để tránh bị thay đổi trong tiến trình nền.
11. **Q:** Lệnh Erase của Flash tốn rất nhiều thời gian, làm sao để CPU không bị treo?
    **A:** Fls (MCAL) thực hiện Erase dưới chế độ ngắt (Hardware Async) hoặc chia nhỏ công việc trong `Fls_MainFunction()` để không lock task OS.
12. **Q:** `NvM_SetRamBlockStatus(BlockId, TRUE)` khác `NvM_WriteBlock(BlockId)` ra sao?
    **A:** `SetRamBlockStatus` đánh dấu `Dirty`, không thao tác phần cứng ngay, chờ đến lúc Shutdown chạy `NvM_WriteAll` mới ghi. `WriteBlock` đưa vào queue để ghi xuống Flash ngay lập tức ở runtime.
13. **Q:** Fee Header lưu những thông tin gì?
    **A:** ID của khối lập trình (Block Number ảo), Độ dài khối, State (Valid, Inconsistent, Erased), Checksum của Header.
14. **Q:** Khối "NvM_ConfigId" dùng làm gì?
    **A:** NvM lưu một chữ ký cấu hình (Config ID) lúc biên dịch vào Flash. Lúc bootup, nếu phần mềm mới có Config ID khác bản trên bộ nhớ Flash (tức là layout NVM thay đổi do update firmware), NvM sẽ từ chối đọc các block cũ và khởi tạo lại toàn bộ từ ROM.
15. **Q:** "NvM_GetErrorStatus" có thể trả về các trạng thái nào?
    **A:** NVM_REQ_OK, NVM_REQ_NOT_OK, NVM_REQ_PENDING, NVM_REQ_INTEGRITY_FAILED, NVM_REQ_BLOCK_SKIPPED, NVM_REQ_NV_INVALIDATED...
16. **Q:** Có thể cấm chức năng "WriteAll" ghi một số block cụ thể không?
    **A:** Có, trong Cấu hình của block có cờ `NVM_WRITE_BLOCK_ONCE` hoặc bỏ tick `NVM_SELECT_BLOCK_FOR_WRITEALL`.
17. **Q:** Dữ liệu có thể bị xóa vĩnh viễn bằng cách nào trên ứng dụng?
    **A:** Gọi hàm `NvM_InvalidateNvBlock()`, NvM sẽ ra lệnh báo cho Fee ghi một trạng thái "Invalid" lên vùng dữ liệu đó.
18. **Q:** "Job Prioritization" trong NvM làm nhiệm vụ gì?
    **A:** Có thể gán Priority cho các Block. `NvM_WriteBlock` của block ưu tiên cao (vd Immo keys) sẽ vượt mặt block ưu tiên thấp (vd setting radio) trong hàng đợi. Immediate data được đưa lên đầu queue.
19. **Q:** CRC lỗi thường do phần cứng hay phần mềm?
    **A:** Cả hai. Phần cứng Flash có thể rò rỉ điện tích (Bit flip theo thời gian). Phần mềm: Thường do Data Inconsistency khi task ghi/đọc RAM bị race condition.
20. **Q:** Fls_MainFunction chạy trên lớp nào?
    **A:** Chạy dưới lớp MCAL. Được trigger định kỳ từ OS task để quét trạng thái các thanh ghi SPI/Memory controller xem tác vụ xóa/ghi đã done chưa (vì Flash hardware xử lý rất chậm).

---
*Tài liệu được biên soạn dành cho Senior/Principal BSW Engineer.*
