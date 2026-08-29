# CHUYÊN ĐỀ 01: Layered Architecture & Virtual Functional Bus (VFB)
## HANDS-ON TASK PLAN — 6 Tasks (~14 giờ)

> 📚 **Tài liệu lý thuyết:** [docs/theory/01_AUTOSAR_Layered_Architecture_And_VFB_Masterclass.md](../theory/01_AUTOSAR_Layered_Architecture_And_VFB_Masterclass.md)  
> 💡 **Bộ Lời Giải Mẫu Chi Tiết (End-to-End Trace):** [docs/hands_on_tasks/solutions/01_Architecture_VFB_Solutions.md](solutions/01_Architecture_VFB_Solutions.md)  
> 🔧 **Source code base:** `as/com/as.infrastructure/`  
> ⏱️ **Tổng thời gian:** ~14 giờ  
> 🎯 **Quy tắc làm việc & lưu diff:** [docs/hands_on_tasks/task_fix/rule.md](task_fix/rule.md)

---

## 🎯 BẢNG ĐÁNH GIÁ TRỌNG SỐ & LỘ TRÌNH DÀNH CHO KỸ SƯ BASIC SOFTWARE (BSW ENGINEER)

> 💡 **Lời khuyên từ Principal AUTOSAR Architect:**  
> Một **Kỹ sư Phần mềm Cơ bản (Basic Software / BSW Engineer)** chịu trách nhiệm "nuôi sống bo mạch", tích hợp hệ điều hành RTOS, viết driver MCAL và vận hành ngăn xếp truyền thông ComStack. Do đó, mức độ ưu tiên của các bài tập trong Chuyên đề 01 được phân bổ theo ma trận trọng số dưới đây:

### 📊 Ma Trận Trọng Số & Mức Độ Ưu Tiên (BSW Priority Matrix)

| Task | Tên Nhiệm Vụ | Mức Độ Ưu Tiên | Trọng Số BSW | Lý Do Kỹ Nghệ & Kỹ Năng Cốt Lõi |
| :--- | :--- | :---: | :---: | :--- |
| **Task 1.1** | **Trace Full ECU Boot Sequence** *(Reset $\rightarrow$ EcuM $\rightarrow$ MCAL $\rightarrow$ StartOS)* | 🔴 **P1 (Must-Have)** | **30%** | **Sống còn khi Bring-up bo mạch mới:** BSW Engineer bắt buộc phải biết CPU chạy từ đâu, khởi tạo RAM/Flash, cấu hình Clock PLL và trao quyền cho OS như thế nào. |
| **Task 1.2** | **Trace 3 Cơ Chế: OS Hooks, BSW Callouts & MCAL Callbacks** | 🔴 **P1 (Must-Have)** | **25%** | **Bản lề tùy biến hệ thống:** Phân biệt rạch ròi giữa Event Handler của OS (`Hook`), Điểm neo phần cứng (`Callout`), và Báo hiệu I/O bất đồng bộ (`Callback`). Tránh sửa bậy vào mã nguồn chuẩn. |
| **Task 1.3** | **Linker Script Analysis — Map Memory Sections** | 🟡 **P2 (Important)** | **20%** | **Quản lý bộ nhớ & An toàn ISO 26262:** Cấu hình linker script (`.lds`), phân vùng RAM/Flash cho MPU, hiểu các macro trừu tượng hóa trình biên dịch (`P2VAR`, `P2CONST`, `AUTOMATIC`, `STATIC`). |
| **Task 1.4** | **Dependency Analysis — BSW Module Init Order** | 🟡 **P2 (Important)** | **15%** | **Tránh lỗi treo hệ thống (Deadlock / Hard Fault):** Hiểu thứ tự khởi tạo hợp lệ của các module BSW trong `EcuM` và `BswM` (Mcu $\rightarrow$ Port $\rightarrow$ Wdg $\rightarrow$ Can $\rightarrow$ Com...). |
| **Task 1.5** | **RTE Port Mapping — Extract All Ports from Source** | 🟢 **P3 (Tooling/Extension)** | **10%** | **Kỹ năng Tự động hóa & Tích hợp:** Viết kịch bản Python/PowerShell đối soát giữa file cấu hình ARXML và mã C thực tế của tầng Application SWC. |

> 💡 **Ghi chú về Ngăn Xếp Truyền Thông ComStack:**  
> Bài tập thực hành chuyên sâu về **Trace Dòng Chảy CAN 6 Tầng (End-to-End ComStack Trace)** được bố trí tại đúng vị trí chuyên đề chuyên biệt tương ứng: [**Chuyên Đề 03: Task 3.1**](03_ComStack_CAN_Tasks.md#task-31) và [**Lời Giải Chuyên Đề 03**](solutions/02_ComStack_CAN_Solutions.md).

---

### 🗺️ Lộ Trình Học Tập Đề Xuất Cho BSW Engineer:
1. **Giai đoạn 1 (Nền móng Sống còn):** Hoàn thành **Task 1.1 $\rightarrow$ Task 1.2 $\rightarrow$ Task 1.3** (Chiếm 70% trọng số kỹ năng tuyển dụng BSW).
2. **Giai đoạn 2 (Tích hợp & Quản lý Hệ thống):** Hoàn thành **Task 1.4 $\rightarrow$ Task 1.5** (Nắm chắc cấu trúc bộ nhớ và khởi tạo hệ thống).
3. **Giai đoạn 3 (Tự động hóa Nâng cao):** Hoàn thành **Task 1.6** (Tự động hóa kiểm tra mã nguồn).

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

### 💡 Bản Chất Kỹ Thuật: Tại Sao Giao Thức CAN Lại Truyền Nhận Qua Cổng Nối Tiếp (UART / Virtual COM)?

> ❓ **Câu hỏi kỹ nghệ kinh điển:**  
> *"CAN là giao thức mạng vi sai 2 dây ($CAN_H / CAN_L$), tại sao trong môi trường máy tính lại thấy nhận dữ liệu CAN qua cổng nối tiếp UART / COM?"*

#### 1. Trên Xe Ô Tô Thật (Physical Automotive CAN Bus):
Trên xe thật, vi điều khiển giao tiếp CAN qua **đường dây điện áp vi sai $CAN_H / CAN_L$**, hoàn toàn không đi qua UART:
* **Khối CAN Controller (On-chip MCU):** Xử lý logic khung truyền (Bit stuffing, CRC, Mailbox) ở mức điện áp số 3.3V/5V.
* **Chip CAN Transceiver (Off-chip PCB, ví dụ NXP TJA1043):** Chuyển đổi mức logic số thành điện áp vi sai $V_{CANH} - V_{CANL}$ trên cặp dây xoắn của xe.

```
┌──────────────────────── VI ĐIỀU KHIỂN (MCU) ───────────────────────┐
│  [Ứng Dụng AUTOSAR] ──► [MCAL Can.c] ──► [Khối CAN Controller]     │
└──────────────────────────────────┬─────────────────────────────────┘
                                   │ Tín hiệu logic số Tx/Rx (3.3V)
                                   ▼
                     ┌───────────────────────────┐
                     │ Chip CAN Transceiver      │
                     │ (Ví dụ: NXP TJA1043)      │
                     └─────────────┬─────────────┘
                                   │ Điện áp vi sai CAN_High / CAN_Low
                                   ▼
                     ═════════════════════════════
                     [ DÂY CÁP CAN BUS TRÊN XE ]
```

#### 2. Khi Kỹ Sư Cắm Máy Tính (Laptop/PC) Vào Xe Để Đọc CAN:
Máy tính cá nhân (Laptop/PC) **hoàn toàn KHÔNG CÓ cổng cắm vi sai $CAN_H / CAN_L$**. PC chỉ có cổng **USB** hoặc cổng **COM**!

Do đó, khi kỹ sư dùng các phần mềm phân tích mạng trên máy tính (**SavvyCAN, Vector CANoe, PCAN-View, BusMaster**), họ bắt buộc phải dùng một thiết bị phần cứng chuyển đổi gọi là **USB-to-CAN Adapter / Dongle** (Ví dụ: *CANable, Peak-System PCAN-USB, hoặc Vector VN1600*):
1. Chip vi điều khiển bên trong Dongle bắt khung CAN từ xe qua bộ thu phát vật lý.
2. Dongle bọc (encapsulate) khung CAN đó thành chuỗi ASCII theo giao thức **SLCAN (Serial CAN / Lawicel Protocol)**:
   $$	ext{Cấu trúc SLCAN Standard: } \mathbf{t}	ext{<ID: 3 hex>}	ext{<DLC: 1 hex>}	ext{<DATA: 2*DLC hex>}ackslash\mathbf{r}$$
   *(Ví dụ: Frame ID `0x180`, 8 byte dữ liệu `50 64 0E 10 00 00 3C 00` $\rightarrow$ `t180850640E1000003C00\r`)*.
3. Dongle đẩy chuỗi SLCAN qua cổng ảo **Virtual COM Port (UART-over-USB)** vào máy tính.
4. Phần mềm **SavvyCAN / CANoe** mở cổng Virtual COM, đọc chuỗi SLCAN và giải mã ngược lại thành Frame CAN nguyên bản!

```
[MẠNG DÂY CAN TRÊN XE] ──► [CỤC CHUYỂN ĐỔI USB-CAN ADAPTER (CANable / PCAN)] ──► [CỔNG VIRTUAL COM] ──► [SAVVYCAN / CANOE]
 (Dây xoắn CAN_H/CAN_L)     (Chuyển đổi CAN Frame thành chuỗi SLCAN ASCII)       (Giao tiếp Serial)       (Giải mã & Vẽ đồ thị)
```

#### 3. Trong Môi Trường Giả Lập SIL & QEMU (Virtual Test Bench):
Vì chúng ta đang học tập và kiểm thử phần mềm mà **không cần mua cục Adapter phần cứng đắt tiền**:
* Tầng MCAL ảo [`SCan.c`](../../as/com/as.infrastructure/arch/common/mcal/SCan.c) trong firmware AUTOSAR đóng vai trò như **chiếc CANable Dongle ảo**: nhận lệnh `Can_Write()`, đóng gói thành chuỗi SLCAN và đẩy ra cổng nối tiếp `UART1`.
* Cặp cổng nối ảo `COM1` $\leftrightarrow$ `COM2` (tạo bởi com0com / VSPE) đóng vai trò là **sợi cáp USB ảo**.
* **SavvyCAN** mở `COM2`, nhận chuỗi SLCAN và hiển thị đồ thị 100% như đang cắm máy đo vào xe thật!

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
1. Mở phần mềm **SavvyCAN**, trên thanh menu chọn: **`Connection` $
ightarrow$ `Open Connection Window`**.
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

1. **Xem trực tiếp packet thô:** Trên màn hình chính SavvyCAN, mở tab **`Frame Flow View`** hoặc **`Sniffer`** $
ightarrow$ Bạn sẽ thấy các dòng packet `0x180`, `0x200` nhảy liên tục theo thời gian thực.
2. **(Tùy chọn) Nạp file DBC để giải mã:** Chọn menu **`DBC File` $
ightarrow$ `Load DBC File`** $
ightarrow$ Trỏ tới file `.dbc` $
ightarrow$ SavvyCAN tự động bóc tách từng tín hiệu vật lý.
3. **(Tùy chọn) Vẽ đồ thị:** Mở tab **`Graphing Window`** để theo dõi đồ thị tín hiệu trực quan.

---

## ⚙️ CƠ CHẾ HOẠT ĐỘNG & KÍCH HOẠT (TRIGGERING) CỦA ECU SIMULATOR TRONG AUTOSAR

### 1. Bản Chất Của ECU Simulator Trong AUTOSAR
Trong kỹ nghệ ô tô, **ECU Simulator** không phải là một script Python tạo dữ liệu giả lập bên ngoài, mà chính là **toàn bộ ngăn xếp mã nguồn C thực tế của AUTOSAR** (bao gồm *Application SWC + RTE + BSW Service + ComStack + OS OSEK/VDX + Virtual MCAL*) được biên dịch (compile) thành một chương trình thực thi (`.exe` hoặc ELF binary) chạy trực tiếp trên máy tính.

Khi ECU Simulator khởi động, nó vận hành như một bộ điều khiển thực thụ bên trong chiếc xe: tự quản lý bộ nhớ, chạy hệ điều hành đa nhiệm thời gian thực và tự động phát/nhận các khung truyền CAN.

```
+─────────────────────────────────────────────────────────────────────────────────────────────+
│                       KIẾN TRÚC & CHU TRÌNH KÍCH HOẠT (TRIGGERING) ECU SIMULATOR             │
│                                                                                             │
│  ┌────────────────────── TẦNG 4: APPLICATION SWC (THUẬT TOÁN) ───────────────────────────┐  │
│  │ void Bms_MainFunction_100ms(void) {                                                    │  │
│  │     uint8_t current_soc = CalculateSoC();                                              │  │
│  │     Rte_Write_PpBmsStatus_SoC(current_soc); ──── (1. Gửi giá trị tính toán)            │  │
│  │ }                                                         │                            │  │
│  └───────────────────────────────────────────────────────────┼────────────────────────────┘  │
│                                                              ▼                            │
│  ┌────────────────────────────── TẦNG 3: RTE RUNTIME ENGINE ─────────────────────────────┐  │
│  │ Rte_Write_PpBmsStatus_SoC() ───────────────────────────► Com_SendSignal(Signal_SoC)    │  │
│  │                                                                 │ (2. Chuyển ComStack) │  │
│  └─────────────────────────────────────────────────────────────────┼──────────────────────┘  │
│                                                                    ▼                      │
│  ┌────────────────────────────── TẦNG 2: BASIC SOFTWARE (BSW) ───────────────────────────┐  │
│  │ • Module COM: Đóng gói Signal_SoC vào I-PDU (CAN ID 0x180) theo chu kỳ 100ms          │  │
│  │ • Module PduR: Định tuyến PduR_ComTransmit() ──► CanIf_Transmit()                     │  │
│  │ • Module CanIf: Quản lý trạng thái bộ điều khiển CAN                                   │  │
│  │ • Module AUTOSAR OS: Bộ đếm nhịp OsTick (1ms) kích hoạt Task định kỳ Com_MainFunction │  │
│  └─────────────────────────────────────────────────────────────────┬──────────────────────┘  │
│                                                                    ▼                      │
│  ┌────────────────────────────── TẦNG 1: VIRTUAL MCAL DRIVER ────────────────────────────┐  │
│  │ Hàm Can_Write() trong Virtual Can Driver đóng gói thành SLCAN ASCII:                   │  │
│  │ "t180850640E1000003C00\r" ──► Ghi trực tiếp ra Cổng Serial ảo COM1                    │  │
│  └─────────────────────────────────────────────────────────────────┬──────────────────────┘  │
│                                                                    ▼                      │
│                                                         [ CỔNG ẢO COM1 <===> COM2 ]       │
│                                                                    ▼                      │
│                                                        [ ỨNG DỤNG SAVVYCAN ĐÓN HỨNG ]     │
+─────────────────────────────────────────────────────────────────────────────────────────────+
```

---

### 2. Chu Trình Kích Hoạt Tự Động (Triggering Sequence)
Để một frame CAN được bắn ra bus, hệ thống trải qua chuỗi 5 bước kích hoạt liên hoàn:

1. **Nhịp xung hệ thống (System Timer Tick):** 
   Bộ định thời của máy tính (hoặc MCU Timer) phát ra ngắt `OsTick()` đều đặn mỗi **1 ms**.
2. **Kích hoạt Task theo lịch trình (OS Alarm & Task Dispatching):**
   * Khi `OsTick` đếm đủ chu kỳ (ví dụ: 100ms), **OS Alarm** tương ứng sẽ hết hạn.
   * Nhân hệ điều hành kích hoạt Task ứng dụng định kỳ: `ActivateTask(TaskApp_100ms)`.
3. **Kích hoạt Runnable trong SWC (RTE Event Triggering):**
   * Task OS chuyển quyền điều khiển cho RTE.
   * RTE kích hoạt hàm **Runnable** của SWC thông qua sự kiện `TimingEvent_100ms`.
   * Runnable thực thi thuật toán điều khiển (ví dụ: tính toán dung lượng pin còn lại) và gọi hàm:
     ```c
     Rte_Write_PpBmsStatus_SoC(80); // Cập nhật SoC = 80%
     ```
4. **Đóng gói Signal thành PDU (ComStack Signal Packing):**
   * `Rte_Write` gọi xuống `Com_SendSignal(ComConf_ComSignal_BMS_SoC, &val)`.
   * Module `COM` lưu giá trị vào bộ đệm Tx Buffer của I-PDU `0x180`.
   * Khi hàm `Com_MainFunction_Tx()` được kích hoạt theo chu kỳ, COM tiến hành đóng gói (Packing) các tín hiệu thành chuỗi 8 byte theo ma trận định nghĩa trong file ARXML/DBC, chèn mã kiểm tra toàn vẹn E2E (CRC + Alive Counter).
5. **Đẩy xuống phần cứng / Cổng ảo (Physical / Virtual CAN Transmission):**
   * `COM` gọi `PduR_ComTransmit()` $
ightarrow$ `CanIf_Transmit()` $
ightarrow$ MCAL `Can_Write()`.
   * **Trong môi trường ảo trên PC:** Hàm `Can_Write()` của driver ảo sẽ bọc khung CAN thành chuỗi chuẩn SLCAN và ghi ra cổng serial ảo `COM1`.
   * **SavvyCAN** kết nối ở đầu `COM2` lập tức bắt được frame và hiển thị lên màn hình.

---

### 3. Hướng Dẫn Khởi Chạy Mô Phỏng ECU & Kết Nối SavvyCAN

Để quan sát luồng dữ liệu thời gian thực từ ECU phát sang SavvyCAN, bạn có **3 chế độ thực thi chuyên nghiệp**:

---

#### 🚀 CHẾ ĐỘ 1: Software-in-the-Loop (SIL) Simulator (Script Python Test Bench)
Chế độ này mô phỏng nhanh luồng phát chu kỳ của 2 ECU: **BMS (ID `0x180`)** và **VCU (ID `0x200`)** bắn trực tiếp qua cặp cổng ảo `COM1` $\rightarrow$ `COM2` vào SavvyCAN:

1. **Bật phần mềm SavvyCAN:** Kết nối cổng `COM2` (SLCAN, 500 kbps), gán file `Vehicle_Network.dbc` vào Bus 0 và tích chọn `[x] Interpret Frames`.
2. **Khởi chạy luồng phát:**
   ```powershell
   python docs/reference/python_can_scripts/send_virtual_can.py COM1 50
   ```

---

#### 🎮 CHẾ ĐỘ 2: Chạy Toàn Bộ Firmware AUTOSAR Trên Máy Ảo QEMU ARM (Khuyên Dùng)
Chế độ này chạy **toàn bộ hệ điều hành AUTOSAR OS (`askar`) + Ngăn xếp ComStack + Tầng Ứng Dụng SWC** được biên dịch thành mã máy ARM Cortex-M3 thật, thực thi trong máy ảo QEMU và bắn trực tiếp khung tin CAN sang SavvyCAN qua giao thức SLCAN.

> 📚 **Tài liệu so sánh Source Code Diff & Báo cáo kỹ thuật (Xem bằng Beyond Compare / WinMerge):**
> * 📁 [Thư mục Fix QEMU Target: `task_fix/01_fix_qemu_board_lm3s6965evb_target/`](task_fix/01_fix_qemu_board_lm3s6965evb_target/README.md)
>   - 📄 [Báo cáo kỹ thuật chi tiết](task_fix/01_fix_qemu_board_lm3s6965evb_target/README.md)
>   - 📌 [File Patch Git Diff](task_fix/01_fix_qemu_board_lm3s6965evb_target/fix.diff)
>   - 📂 Thư mục mã nguồn trước & sau khi fix: `src_before/` $\leftrightarrow$ `src_after/`
> * 📁 [Thư mục Fix SavvyCAN Streaming: `task_fix/02_fix_savvycan_slcan_streaming_integration/`](task_fix/02_fix_savvycan_slcan_streaming_integration/README.md)
>   - 📄 [Báo cáo kỹ thuật chi tiết](task_fix/02_fix_savvycan_slcan_streaming_integration/README.md)
>   - 📌 [File Patch Git Diff](task_fix/02_fix_savvycan_slcan_streaming_integration/fix.diff)
>   - 📂 Thư mục mã nguồn trước & sau khi fix: `src_before/` $\leftrightarrow$ `src_after/`

##### 1. Biên dịch Firmware Target QEMU (`lm3s6965evb`):
Mở terminal PowerShell tại thư mục gốc của dự án:
```powershell
# Chuyển vào thư mục mã nguồn as/
cd "C:\Users\liem.vu\Liem.vuOD\Study_AUTOSAR-main\as"

# Thiết lập biến môi trường cho Target Board QEMU
$env:BOARD="lm3s6965evb"
$env:RELEASE="ascore"

# Tiến hành biên dịch (Sinh mã ArGen + Compile ARM GCC)
scons
```

##### 2. Khởi chạy máy ảo QEMU ARM với Kiến Trúc Dual UART (Khuyên Dùng):

* **Mục đích:** Kích hoạt đồng thời 2 cổng UART phần cứng của vi điều khiển ARM trong QEMU:
  * **Cổng `UART0` (`-serial mon:stdio`):** In 100% log khởi động OS `askar`, log Task và log sự kiện `>>> [CAN Tx Event]` ra **màn hình Terminal Console**.
  * **Cổng `UART1` (`-chardev serial,id=can0,path=COM1 -serial chardev:can0`):** Bắn luồng gói tin nhị phân SLCAN (`t1808...`, `t2008...`) vào cổng ảo **`COM1` $\rightarrow$ `COM2` $\rightarrow$ SavvyCAN** để vẽ đồ thị thời gian thực!

```powershell
cd "C:\Users\liem.vu\Liem.vuOD\Study_AUTOSAR-main"
& "C:\Program Files\qemu\qemu-system-arm.exe" -M lm3s6965evb -kernel "as/build/nt/lm3s6965evb/ascore/lm3s6965evb.exe" -nographic -monitor none -serial mon:stdio -chardev serial,id=can0,path=COM1 -serial chardev:can0
```
*(Khi xuất hiện hộp thoại "COM1 Properties": kiểm tra Baud rate 115200 $\rightarrow$ bấm **OK** (hoặc gõ Enter)).*

##### 3. Quan sát kết quả trên SavvyCAN:
1. Mở **SavvyCAN**, kết nối cổng `COM2` (SLCAN, 500 kbps), gán file `Vehicle_Network.dbc` vào Bus 0 và tích chọn `[x] Interpret Frames`.
2. Khung tin `0x180 BMS_Status` (SoC xả từ 80% về 20%) và `0x200 VCU_TorqueCmd` (Tốc độ tăng từ 40 lên 120 km/h) đổ về liên tục.
3. Mở tab **`Graphing`** để xem biểu đồ thời gian thực.

---

#### 🛠️ CHẾ ĐỘ 3: Biên Dịch Firmware Nạp Chip Vật Lý Thật (Target STM32F107VC)
Dành cho việc nạp trực tiếp vào bo mạch phần cứng STM32 thật qua mạch nạp ST-Link/J-Link:
1. **Biên dịch:**
   ```powershell
   cd as
   $env:BOARD="stm32f107vc"
   $env:RELEASE="ascore"
   scons
   ```
2. **Thành phẩm:** `as/build/nt/stm32f107vc/ascore/stm32f107vc.exe.s19` dùng phần mềm STM32CubeProgrammer nạp vào vi điều khiển thật.

---

## 🛠️ CHI TIẾT CÁC TASKS CHUYÊN ĐỀ 01

### **TASK 1.1: Code Navigation — Trace Full ECU Boot Sequence (Reset_Handler $\rightarrow$ EcuM $\rightarrow$ MCAL Init $\rightarrow$ StartOS)** (~2h, Beginner) 🔴 [TRỌNG SỐ BSW: 30%]
- **🎯 Objective:** Lần vết toàn bộ chu trình khởi động thực tế của ECU từ lúc bật nguồn: `reset_handler` $\rightarrow$ Khởi tạo RAM BSS/DATA $\rightarrow$ `main()` $\rightarrow$ `EcuM_Init()` $\rightarrow$ Khởi tạo ngoại vi MCAL (`Mcu`, `Port`, `Can`, `Adc`) $\rightarrow$ `StartOS()` $\rightarrow$ `EcuM_StartupTwo()` $\rightarrow$ `Rte_Start()`.
- **📂 Files cần đọc (Target QEMU ARM `lm3s6965evb`):**
  - `as/com/as.application/board.lm3s6965evb/script/linker.lds` (Xác định Entry Point `reset_handler` & Vùng nhớ Flash `0x00000000` / RAM `0x20000000`)
  - `as/com/as.application/board.lm3s6965evb/sys.c` & `main.c` (Điểm vào phần cứng `reset_handler` & `main()`)
  - `as/com/as.infrastructure/system/EcuM/EcuM.c` (Hàm `EcuM_Init` và `EcuM_StartupTwo`)
  - `as/com/as.infrastructure/arch/lm3s/mcal/Mcu.c` (`Mcu_Init`, `Mcu_InitClock`, `Usart_Init`)
  - `as/com/as.infrastructure/arch/lm3s/mcal/Can.c` & `as/com/as.infrastructure/arch/common/mcal/SCan.c` (`Can_Init`, `Can_Write`)
  - `as/build/nt/lm3s6965evb/ascore/config/Os_Cfg.c` (`StartOS`, Task khởi động `SchM_Startup`, `TaskIdle`)
- **📝 Steps chi tiết:**
  1. **Bước 1 (Reset & Entry Point):** Mở `linker.lds`, tìm dòng `ENTRY(reset_handler)`. Tìm hàm `reset_handler` để thấy cách CPU sao chép dữ liệu từ Flash sang RAM (`.data`) và xóa trắng biến rác (`.bss`).
  2. **Bước 2 (Chuyển tiếp vào main):** Lần vết từ cuối `reset_handler` nhảy vào hàm `main()`.
  3. **Bước 3 (EcuM Phase 1 - Pre-OS):** Mở `EcuM.c`, đọc hàm `EcuM_Init()`. Ghi lại thứ tự các hàm MCAL khởi tạo ngoại vi trước khi bật OS: `Mcu_Init()`, `Mcu_InitClock()`, `Mcu_DistributePllClock()`, `Port_Init()`, `Gpt_Init()`, `Wdg_Init()`.
  4. **Bước 4 (Khởi động Hệ điều hành):** Tìm lệnh `StartOS(OSDEFAULTAPPMODE)` và Task khởi động `SchM_Startup`.
  5. **Bước 5 (EcuM Phase 2 - Post-OS):** Trace vào Task khởi động, tìm hàm `EcuM_StartupTwo()`. Xem cách hệ thống khởi tạo các module tầng trên: `BswM_Init()`, `Com_Init()`, `Rte_Start()`.
- **📤 Output:** Vẽ sơ đồ tuần tự (Sequence Diagram hoặc Mermaid Diagram) mô tả chính xác 5 giai đoạn boot từ Reset Vector đến khi RTE chạy.
- **✅ Success Criteria:** Chỉ rõ được tên file, tên hàm và số dòng code của từng bước trong chuỗi khởi động.

---

### **TASK 1.2: Code Navigation & Architecture — Trace 3 Cơ Chế Giao Tiếp Đặc Biệt (OS Hooks, BSW Callouts & MCAL Callbacks)** (~2.5h, Intermediate) 🔴 [TRỌNG SỐ BSW: 25%]
- **🎯 Objective:** Phân tích, lần vết mã nguồn thực tế và phân biệt rạch ròi 3 cơ chế giao tiếp dọc/ngang cốt lõi trong kiến trúc AUTOSAR:
  1. **OS Hooks (Hàm Xử Lý Sự Kiện Vòng Đời OS):** Bắt các sự kiện hệ thống từ nhân OS (`StartupHook`, `ShutdownHook`, `ErrorHook`, `PreTaskHook`, `PostTaskHook`).
  2. **BSW Callouts (Điểm Neo Tùy Biến Của Kỹ Sư):** Các hàm khung rỗng do BSW gọi ra ngoài để kỹ sư khởi tạo phần cứng đặc thù (`EcuM_AL_DriverInitZero`, `EcuM_AL_DriverInitOne`, `EcuM_AL_DriverInitTwo`, `EcuM_AL_DriverInitThree`, `EcuM_CheckWakeup`).
  3. **MCAL / Driver Callbacks (Hàm Thông Báo Bất Đồng Bộ):** Báo hiệu từ driver cấp thấp lên tầng BSW khi phần cứng hoàn tất một tác vụ (`CanIf_RxIndication`, `CanIf_TxConfirmation`, `PduR_CanIfRxIndication`, `Com_RxIndication`).
- **📂 Files cần đọc & khảo sát:**
  - `as/com/as.infrastructure/system/kernel/askar/kernel/kernel.c` (Vị trí gọi `OSStartupHook()`, `OSShutdownHook()`)
  - `as/com/as.infrastructure/system/kernel/askar/kernel/kernel_internal.h` (Macro bọc ngắt và đổi CallLevel khi gọi Hook)
  - `as/build/nt/lm3s6965evb/ascore/config/Os_Cfg.h` (`#define OS_USE_STARTUP_HOOK`)
  - `as/release/ascore/app/app.c` (`StartupHook()`, `ShutdownHook()`, `ErrorHook()`)
  - `as/com/as.infrastructure/system/EcuM/EcuM.c` & `EcuM_Callout_Stubs.c`
  - `as/com/as.infrastructure/communication/CanIf/CanIf.c` & `CanIf_Cbk.h`
- **📤 Output:** Lập bảng ma trận so sánh chi tiết giữa 3 cơ chế (Caller, Implementer, Timing, Purpose, Rule).
- **✅ Success Criteria:** Chỉ ra được sự khác biệt cốt lõi giữa `Callout` (gọi xuôi xuống driver) và `Callback` (báo ngược lên trên).

---

### **TASK 1.3: Linker Script Analysis — Map Memory Sections (.text, .bss, P2VAR, P2CONST, AUTOMATIC)** (~2h, Intermediate) 🟡 [TRỌNG SỐ BSW: 20%]
- **🎯 Objective:** Phân tích cấu trúc phân vùng bộ nhớ Flash/RAM của dự án AUTOSAR và cách các macro trừu tượng hóa trình biên dịch của AUTOSAR map vào bộ nhớ vật lý của MCU.
- **📂 Files cần đọc:**
  - `as/com/as.application/board.lm3s6965evb/script/linker.lds` (Linker script chuẩn trên QEMU ARM Cortex-M3)
  - `as/com/as.infrastructure/include/Std_Types.h`
  - `as/com/as.infrastructure/include/Compiler.h`
- **📝 Steps chi tiết:**
  1. Đọc và phân tích các macro trừu tượng hóa trình biên dịch trong `Compiler.h` như: `P2VAR`, `P2CONST`, `CONSTP2VAR`, `AUTOMATIC`, `STATIC`.
  2. Khảo sát cấu trúc Linker Script (`linker.lds` tại `as/com/as.application/board.lm3s6965evb/script/linker.lds`) để hiểu về các phân đoạn vật lý (`.text`, `.data`, `.bss`, `.isr_vector`, `.stack`).
  3. Ánh xạ các section macro của AUTOSAR (`*_START_SEC_CODE`, `*_START_SEC_VAR_NOINIT_UNSPECIFIED`) vào các phân đoạn bộ nhớ C truyền thống.
- **📤 Output:** Bảng so sánh AUTOSAR Memory Sections vs Standard C sections.
- **✅ Success Criteria:** Giải thích được mạch lạc sự khác nhau giữa các `*_START_SEC_*` macros và lý do AUTOSAR thiết kế memory mapping theo cách này.

---

### **TASK 1.4: Dependency Analysis — BSW Module Init Order** (~3h, Intermediate) 🟡 [TRỌNG SỐ BSW: 15%]
- **🎯 Objective:** Phân tích thứ tự khởi tạo BSW modules và quan hệ phụ thuộc lẫn nhau.
- **📂 Files cần đọc:**
  - `as/com/as.infrastructure/system/EcuM/EcuM.c`
  - `as/com/as.infrastructure/system/BswM/BswM.c`
  - `as/com/as.infrastructure/SConscript`
- **📝 Steps chi tiết:**
  1. Đọc nội dung hàm init trong `EcuM.c` và `BswM.c` để nắm luồng khởi động.
  2. Viết Python script parse `SConscript` để trích xuất cây phụ thuộc (dependency tree).
  3. Sắp xếp lại trình tự khởi tạo chuẩn.
- **📤 Output:** In ra màn hình thứ tự init chuẩn: `Mcu` → `Port` → `Wdg` → `Can` → `CanIf` → `Com` → `Dcm` → `DEM` → `NvM` → `Rte_Start`.
- **✅ Success Criteria:** Giải thích được vì sao `Mcu_Init` và `Port_Init` phải chạy trước `Can_Init` và `Com_Init`.

---

### **TASK 1.5: RTE Port Mapping — Extract All Ports from Source** (~2.5h, Intermediate) 🟢 [TRỌNG SỐ BSW: 10%]
- **🎯 Objective:** Viết Python/PowerShell script quét tìm tất cả `Rte_Read` và `Rte_Write` calls trong source code để đối soát với file ARXML.
- **📝 Steps chi tiết với PowerShell commands:**
  ```powershell
  Get-ChildItem -Path .s -Recurse -Include '*.c' | Select-String -Pattern '(Rte_Read|Rte_Write)_([a-zA-Z0-9_]+)'
  ```
- **📤 Output:** File CSV với 4 cột (SWC, Port, Direction, DataElement) rõ ràng.
- **✅ Success Criteria:** Script quét tìm được các Rte calls trong project và lập bảng CSV chuẩn xác.
