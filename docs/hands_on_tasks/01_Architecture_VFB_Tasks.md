# CHUYÊN ĐỀ 01: Layered Architecture & Virtual Functional Bus (VFB)
## HANDS-ON TASK PLAN — 4 Tasks (~10 giờ)

> 📚 **Tài liệu lý thuyết:** [docs/theory/01_AUTOSAR_Layered_Architecture_And_VFB_Masterclass.md](../theory/01_AUTOSAR_Layered_Architecture_And_VFB_Masterclass.md)  
> 🔧 **Source code base:** `as/com/as.infrastructure/`  
> ⏱️ **Tổng thời gian:** ~10 giờ  
> 🎯 **Quy tắc làm việc & lưu diff:** [docs/hands_on_tasks/task_fix/rule.md](task_fix/rule.md)

---

## 🌐 HƯỚNG DẪN THIẾT LẬP MÔI TRƯỜNG VIRTUAL CAN VỚI SAVVYCAN & VIRTUAL COM

Để thực hành kiểm tra luồng dữ liệu mạng CAN và chẩn đoán UDS mà **không cần mua phần cứng thật**, chúng ta sử dụng mô hình **Software-in-the-Loop (SIL)** kết hợp giữa **Virtual Serial Port Emulator (VSPE / com0com)** và phần mềm phân tích mạng **SavvyCAN**.

### 1. Sơ Đồ Kiến Trúc Mô Phỏng (Virtual SIL Test Bench)

```
┌──────────────────────────────────────────────┐                 ┌──────────────────────────────────────────────┐
│       ECU SIMULATOR / PYTHON TEST SCRIPT     │                 │              SAVVYCAN GUI APP                │
│    (Đóng gói Signal, gửi/nhận UDS Services)  │                 │    (Soi Frame CAN, Nạp DBC, Vẽ Đồ Thị)       │
└──────────────────────┬───────────────────────┘                 └──────────────────────▲───────────────────────┘
                       │ Gửi qua COM1 (SLCAN)                                           │ Đọc từ COM2 (SLCAN)
                       ▼                                                                │
              ┌─────────────────┐             CẶP CỔNG NỐI ẢO (PAIR)           ┌─────────────────┐
              │   Cổng COM 1    ├═════════════════════════════════════════════►│   Cổng COM 2    │
              └─────────────────┘             (Tạo bởi VSPE / com0com)         └─────────────────┘
```

---

### 2. Các Bước Cài Đặt & Cấu Hình Từng Bước (Step-by-Step)

#### 🔹 Bước 1: Tải & Khởi Chạy SavvyCAN
1. Tải bản Portable dành cho Windows từ trang chính thức: [SavvyCAN Releases (GitHub)](https://github.com/collin80/SavvyCAN/releases).
2. Giải nén file zip và chạy trực tiếp file `SavvyCAN.exe` (không cần cài đặt).

#### 🔹 Bước 2: Tạo Cặp Cổng Nối Tiếp Ảo (Virtual Serial Pair)
1. Tải và cài đặt công cụ **com0com** (Miễn phí, Open-Source) hoặc **Virtual Serial Ports Emulator (VSPE)**.
2. Tạo một **Device Type: Pair** kết nối hai cổng ảo với nhau:
   * **Cổng A:** `COM1` *(Dành cho Simulator / Python Script)*
   * **Cổng B:** `COM2` *(Dành cho SavvyCAN)*
3. Bấm **Apply / Emulate** để kích hoạt cặp cổng.

#### 🔹 Bước 3: Cấu Hình Kết Nối Trên SavvyCAN
1. Mở phần mềm **SavvyCAN**, trên thanh menu chọn: **`Connection` $\rightarrow$
ightarrow$\rightarrow$ `Open Connection Window`**.
2. Bấm nút **`Add New Device Connection`**.
3. Thiết lập các thông số kết nối:
   * **Connection Type:** Chọn **`SLCAN (Serial CAN / Lawicel)`** hoặc **`Serial (Generic)`**.
   * **Port:** Chọn cổng **`COM2`** (Cổng đích từ máy ảo).
   * **Baudrate:** Chọn **`115200`** hoặc **`500000`**.
   * **Bus Speed (CAN Bitrate):** Chọn **`500000 bps (500 kbps)`** (Tốc độ CAN tiêu chuẩn trên ô tô).
4. Tích chọn **`Enable Bus`** và bấm **`Create New Connection`**.
5. 👉 **Trạng thái thành công:** Đèn kết nối bên góc phải chuyển sang **màu xanh lá (Connected)**.

#### 🔹 Bước 4: Kiểm Tra Truyền Nhận Bằng Python Script (Verification)
Chạy đoạn mã Python sau trong terminal để bắn thử nghiệm 1 frame CAN ID `0x180` (BMS Status):

```python
import can
import time

# Mở kết nối SLCAN tới COM1
bus = can.interface.Bus(interface='slcan', channel='COM1', bitrate=500000)

print("Đang bắn frame CAN thử nghiệm vào COM1...")
msg = can.Message(
    arbitration_id=0x180,
    data=[0x50, 0x64, 0x0E, 0x10, 0x00, 0x00, 0x3C, 0x00],
    is_extended_id=False
)
bus.send(msg)
print("Đã gửi thành công! Hãy kiểm tra màn hình SavvyCAN.")
```

#### 🔹 Bước 5: Đón & Quan Sát CAN Packet Trên SavvyCAN (Tùy Chọn: Nạp File DBC Để Giải Mã)

> 💡 **Bản chất kỹ thuật bạn cần nắm rõ:**
> * **SavvyCAN chỉ là "bến đỗ đón gói tin" (Sniffer / Receiver):** Bạn chỉ cần bật SavvyCAN lên và cấu hình cổng `COM2`, nó sẽ tự động bắt 100% tất cả frame CAN thô (Raw CAN Packets) do ECU ảo phát sang mà **không bắt buộc phải nạp thêm bất kỳ file nào**.
> * **File DBC (CAN DataBase) là gì và khi nào cần dùng?**
>   - Nếu *không nạp DBC*, bạn vẫn nhận đủ mọi packet bình thường, màn hình hiển thị 8 byte Hex thô (`ID: 0x180 | Data: 50 64 0E 10 00 00 3C 00`).
>   - Nạp file `.dbc` là **tính năng tùy chọn (Optional)**: File DBC đóng vai trò như "cuốn từ điển" giúp SavvyCAN tự động dịch 8 byte Hex đó thành con số người đọc được (*SoC Pin = 80%, Điện áp = 360V, Nhiệt độ = 40°C*) và vẽ đồ thị dao động.
>   - 📚 *Xem chi tiết lý thuyết về chuẩn DBC tại:* [docs/theory/10_CAN_DBC_Format_And_Tools.md](../theory/10_CAN_DBC_Format_And_Tools.md)

1. **Xem trực tiếp packet thô:** Trên màn hình chính SavvyCAN, mở tab **`Frame Flow View`** hoặc **`Sniffer`** $\rightarrow$
ightarrow$\rightarrow$ Bạn sẽ thấy các dòng packet `0x180`, `0x200` nhảy liên tục theo thời gian thực.
2. **(Tùy chọn) Nạp file DBC để giải mã:** Chọn menu **`DBC File` $\rightarrow$
ightarrow$\rightarrow$ `Load DBC File`** $\rightarrow$
ightarrow$\rightarrow$ Trỏ tới file `.dbc` $\rightarrow$
ightarrow$\rightarrow$ SavvyCAN tự động bóc tách từng tín hiệu vật lý.
3. **(Tùy chọn) Vẽ đồ thị:** Mở tab **`Graphing Window`** để theo dõi đồ thị tín hiệu trực quan.

---

## 🛠️ CHI TIẾT CÁC TASKS CHUYÊN ĐỀ 01

### **TASK 1.1: Code Navigation — Trace CAN Message Through 6 Layers** (~2h, Beginner)
- **🎯 Objective:** Trace 1 CAN message từ Application SWC xuống CAN Controller Driver, vẽ call graph
- **📂 Files cần đọc:**
  - `as/com/as.application/swc/` (Application SWC)
  - `as/com/as.infrastructure/communication/Com/Com.c`
  - `as/com/as.infrastructure/communication/PduR/PduR.c`
  - `as/com/as.infrastructure/communication/CanIf/CanIf.c`
  - `as/com/as.infrastructure/arch/stm32f1/mcal/Can.c`
- **📝 Steps chi tiết:**
  1. Mở PowerShell tại thư mục gốc của project.
  2. Dùng lệnh PowerShell sau để tìm entry point:
     ```powershell
     Get-ChildItem -Path .s -Recurse | Select-String "Rte_Write"
     ```
  3. Chọn 1 hàm `Rte_Write_...` và trace xuống layer tiếp theo (Com). Tìm hàm như `Com_SendSignal`.
  4. Trace xuống PduR (ví dụ: `PduR_ComTransmit`).
  5. Trace xuống CanIf: `CanIf_Transmit`.
  6. Cuối cùng, trace tận cùng xuống MCAL Can Driver để tìm hàm `Can_Write`.
- **✅ Success Criteria:** Vẽ được call graph đầy đủ 6 layer với tên hàm chính xác.
- **⚠️ Common Pitfalls:** Dễ lạc lối giữa PduR và CanTp do PduR có chức năng định tuyến phức tạp. Cần bám sát luồng truyền dữ liệu CAN thông thường.
- **🌟 Extension Challenge:** Thử trace theo chiều ngược lại (Rx path) bắt đầu từ CAN Rx Interrupt (`Can_Isr`) ngược lên RTE.

---

### **TASK 1.2: Dependency Analysis — BSW Module Init Order** (~3h, Intermediate)
- **🎯 Objective:** Viết Python script phân tích thứ tự khởi tạo BSW modules
- **📂 Files cần đọc:**
  - `as/com/as.infrastructure/system/EcuM/EcuM.c`
  - `as/com/as.infrastructure/system/BswM/BswM.c`
  - `as/com/as.infrastructure/SConscript`
- **📝 Steps chi tiết:**
  1. Đọc nội dung hàm init trong `EcuM.c` và `BswM.c` để nắm luồng khởi động.
  2. Viết Python script parse `SConscript` để trích xuất cây phụ thuộc (dependency tree):
     ```python
     import re
     
     def parse_sconscript(filepath):
         with open(filepath, 'r') as f:
             content = f.read()
         # Implement logic to extract module dependencies
         print("Parsing dependencies from SConscript...")
         
     parse_sconscript('as/com/as.infrastructure/SConscript')
     ```
  3. Kết hợp kết quả từ kịch bản Python và file mã nguồn để sắp xếp lại trình tự.
- **📤 Output:** In ra màn hình thứ tự init chuẩn: `Mcu` → `Port` → `Wdg` → `Can` → `CanIf` → `Com` → `Dcm` → `DEM` → `NvM` → `Rte_Start`.
- **✅ Success Criteria:** Script Python chạy được mượt mà, parse thành công nội dung file và output ra đúng thứ tự init được yêu cầu.

---

### **TASK 1.3: Linker Script Analysis — Map Memory Sections** (~2h, Intermediate)
- **🎯 Objective:** Phân tích cấu trúc bộ nhớ Flash/RAM của AUTOSAR project
- **📂 Files cần đọc:**
  - `as/com/as.application/board.stm32f107vc/script/linker-app.lds`
  - `as/com/as.infrastructure/include/Std_Types.h`
  - `as/com/as.infrastructure/include/Compiler.h`
- **📝 Steps chi tiết:**
  1. Đọc và phân tích các macro trừu tượng hóa trình biên dịch trong `Compiler.h` như: `P2VAR`, `P2CONST`, `AUTOMATIC`, `STATIC`.
  2. Khảo sát cấu trúc Linker Script (`linker-app.lds`) để hiểu về các phân đoạn vật lý (`.text`, `.data`, `.bss`, `.isr_vector`).
  3. Ánh xạ các section macro của AUTOSAR vào các phân đoạn bộ nhớ C truyền thống. Lập bảng so sánh chi tiết.
- **📤 Output:** Bảng so sánh AUTOSAR Memory Sections vs Standard C sections.
- **✅ Success Criteria:** Giải thích được mạch lạc sự khác nhau giữa các `*_START_SEC_*` macros và lý do AUTOSAR thiết kế memory mapping theo cách này.

---

### **TASK 1.4 (Extension): RTE Port Mapping — Extract All Ports from Source** (~3h, Advanced)
- **🎯 Objective:** Viết Python/PowerShell script tìm tất cả `Rte_Read` và `Rte_Write` calls trong source
- **📝 Steps chi tiết với PowerShell commands:**
  1. Chạy lệnh sau để truy vấn thô trong mã nguồn:
     ```powershell
     Get-ChildItem -Path .s -Recurse -Include '*.c' | Select-String -Pattern 'Rte_Read|Rte_Write'
     ```
  2. Xây dựng một kịch bản PowerShell nâng cao (hoặc Python) để bóc tách bằng Regex và xuất ra định dạng dữ liệu có cấu trúc:
     ```powershell
     $\rightarrow$results = @()
     Get-ChildItem -Path .s -Recurse -Include '*.c' | ForEach-Object {
         $\rightarrow$file = $\rightarrow$_.FullName
         $\rightarrow$swc = $\rightarrow$_.BaseName
         Select-String -Path $\rightarrow$file -Pattern '(Rte_Read|Rte_Write)_([a-zA-Z0-9_]+)' | ForEach-Object {
             $\rightarrow$results += [PSCustomObject]@{
                 SWC = $\rightarrow$swc
                 Port = "Port_" + $\rightarrow$_.Matches.Groups[2].Value
                 Direction = $\rightarrow$_.Matches.Groups[1].Value
                 DataElement = $\rightarrow$_.Matches.Groups[2].Value
             }
         }
     }
     $\rightarrow$results | Export-Csv -Path 'docs/hands_on_tasks/task_fix/RtePortsMapping.csv' -NoTypeInformation
     ```
- **📤 Output:** CSV file với 4 cột (SWC, Port, Direction, DataElement) rõ ràng.
- **✅ Success Criteria:** Script quét tìm được ≥5 Rte calls trong project, trích xuất thành công và lập được bảng CSV chuẩn xác.
