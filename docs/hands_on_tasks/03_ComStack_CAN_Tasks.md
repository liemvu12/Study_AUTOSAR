# CHUYÊN ĐỀ 03: Communication Stack & CAN Protocol Hands-on Tasks
## KẾ HOẠCH BÀI TẬP THỰC HÀNH CHUYÊN SÂU — 11 Tasks (~28 giờ)

> 📚 **Tài liệu lý thuyết đối chiếu:** [`docs/theory/03_Communication_Stack_And_CAN_Protocol.md`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/docs/theory/03_Communication_Stack_And_CAN_Protocol.md)  
> 📑 **Ma trận gói tin & DBC:** [`docs/theory/10_CAN_DBC_Format_And_Tools.md`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/docs/theory/10_CAN_DBC_Format_And_Tools.md)  
> 💡 **Bộ Lời Giải Mẫu Chi Tiết (Solutions):** [`docs/hands_on_tasks/solutions/03_ComStack_CAN_Solutions.md`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/docs/hands_on_tasks/solutions/03_ComStack_CAN_Solutions.md)  
> 🔧 **Source code base:** [`as/com/as.infrastructure/communication/`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/com/as.infrastructure/communication/)  
> ⏱️ **Tổng thời lượng ước tính:** ~28 giờ

---

### 📊 Ma Trận Nhiệm Vụ Chuyên Đề 03 (ComStack Task Summary):

| Mã Task | Tên Nhiệm Vụ Thực Hành | Mức Độ | Thời Gian | Trọng Tâm Kỹ Nghệ & Mục Tiêu |
| :--- :--- | :--- | :---: | :---: | :--- |
| **Task 3.1** | **Trace Dòng Chảy CAN Message 6 Tầng Toàn Diện (End-to-End Trace)** | 🔴 Advanced | ~3h | Trace 6 tầng BSW: COM $\rightarrow$ PduR $\rightarrow$ CanIf $\rightarrow$ MCAL Can $\rightarrow$ UART1 SLCAN |
| **Task 3.2** | **CAN Bit Timing Calculation & Sample Point Verification** | 🟢 Beginner | ~1.5h | Tính thanh ghi BRP, TS1, TS2 đạt Sample Point 87.5% cho 500 kbps |
| **Task 3.3** | **Khảo Sát CAN Driver MCAL — Cấu Hình Mailbox HTH / HRH & Ring Buffer** | 🟡 Intermediate | ~3h | Phân tích `Can_Write()`, struct `Can_PduType`, HTH, HRH, bảo vệ vùng nhớ găng |
| **Task 3.4** | **CanIf Software Acceptance Filter — Lọc CAN ID Bằng Mặt Nạ Bitmask** | 🟡 Intermediate | ~2h | Hàm `CanIf_RxIndication()`, giải mã công thức bitmask lọc ID và chống tràn Mailbox |
| **Task 3.5** | **CanTp Multi-Frame Transmission — Phân Mảnh UDS (ISO 15765-2 DoCAN)** | 🔴 Advanced | ~3.5h | Giao thức ISOTP: First Frame (FF), Flow Control (FC), Consecutive Frame (CF), BS & STmin |
| **Task 3.6** | **COM — Signal Packing Into I-PDU & Endianness (Intel vs Motorola)** | 🔴 Advanced | ~3h | Đóng gói nhiều Signal vào 1 I-PDU 8 bytes, xử lý Byte Order và Start Bit |
| **Task 3.7** | **Bus Load Calculation & Overload Monitoring** | 🟡 Intermediate | ~2h | Công thức tính % Bus Load, đếm frames trong CAN ISR và phát cảnh báo quá tải (>70%) |
| **Task 3.8** ✨ | **Tầng Vật Lý, Trở Kháng Đầu Cuối 120Ω & Bắt Bệnh Sóng Oscilloscope** | 🟡 Intermediate | ~2.5h | Tính trở $60\Omega$, phân tích sóng $V_{\text{diff}}$, bắt 4 bệnh: Ringing hụt trở, sụt áp, Ground Shift |
| **Task 3.9** ✨ | **Trở Thành BSW Engineer — Cấu Hình ARXML & Sinh Mã C Bằng Python Toolchain** | 🔴 Advanced | ~3h | Thêm PDU mới vào `autosar.arxml`, chạy `argen` (`GenCanIf.py`, `GenPduR.py`), verify code C sinh ra |
| **Task 3.10** ✨| **Khảo Sát Fault Confinement & Bus-Off Recovery CanSM State Machine** | 🔴 Advanced | ~2.5h | Đếm lỗi TEC/REC, máy trạng thái CanSM phục hồi Bus-Off (L1 Fast Recovery / L2 Slow Recovery) |
| **Task 3.11** 🚀| **Kiến Trúc Sư Hệ Thống — Phân Bổ SWC Trong System ARXML & Điều Hướng RTE** | 🔴 Advanced | ~3h | Thực hành mapping SWC vào ECU trong ARXML; so sánh mã C sinh ra của RTE: Intra-ECU RAM vs Inter-ECU CAN `Com_SendSignal` |

---

## TASK 3.1: Trace Dòng Chảy CAN Message 6 Tầng Toàn Diện (End-to-End ComStack Trace)
**Thời gian ước tính:** ~3h | **Mức độ:** Advanced

> 🎯 **Mục tiêu:** Trace 1 thông điệp CAN xuyên suốt 6 tầng kiến trúc AUTOSAR theo cả 2 chiều hoàn toàn dựa trên **mã nguồn gốc có sẵn của dự án `as` (100% Native Code Base)**:
> 1. **Chiều Gửi (Tx Path):** Trace dòng chảy gói tin thời gian gốc **`TxMsgTime` (CAN ID: `0x101`)** qua toàn bộ ngăn xếp BSW COM và gói tin quản trị mạng gốc **`OSEK_NM_TX` (CAN ID: `0x401`)** từ Lõi BSW $\longrightarrow$ PduR $\longrightarrow$ CanIf $\longrightarrow$ MCAL Driver $\longrightarrow$ Dây Bus CAN vật lý.
> 2. **Chiều Nhận (Rx Path):** Trace dòng chảy gói tin tốc độ xe gốc **`RxMsgAbsInfo` (CAN ID: `0x102`)** từ Khung mạng vật lý MCAL $\longrightarrow$ CanIf $\longrightarrow$ PduR $\longrightarrow$ COM $\longrightarrow$ RTE $\longrightarrow$ Application SWC (`widget_refresh.c`).

### 📂 Tệp Cần Đọc & Đối Chiếu:
1. [`as/com/as.application/common/autosar.arxml`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/com/as.application/common/autosar.arxml#L352) (Dòng 352: Cấu hình I-PDU `TxMsgTime`).
2. [`as/com/as.infrastructure/system/SchM/SchM.c`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/com/as.infrastructure/system/SchM/SchM.c) (Dòng 441: `Com_IpduGroupStart`, Dòng 522: `SCHM_MAINFUNCTION_COMTX`).
3. [`as/com/as.infrastructure/communication/Com/Com_Sched.c`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/com/as.infrastructure/communication/Com/Com_Sched.c) (Dòng 98: `Com_MainFunctionTx`).
4. [`as/com/as.infrastructure/communication/Com/Com_Com.c`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/com/as.infrastructure/communication/Com/Com_Com.c) (Dòng 198: `Com_Internal_TriggerIPduSend`, Dòng 236: `PduR_ComTransmit`).
5. [`as/com/as.infrastructure/communication/PduR/PduR_Routing.c`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/com/as.infrastructure/communication/PduR/PduR_Routing.c) (Dòng 59: `CanIf_Transmit`).
6. [`as/build/nt/lm3s6965evb/ascore/config/CanIf_Cfg.c`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/build/nt/lm3s6965evb/ascore/config/CanIf_Cfg.c) (Dòng 168: Ánh xạ CAN ID `0x101`).
7. [`as/com/as.infrastructure/communication/CanIf/CanIf.c`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/com/as.infrastructure/communication/CanIf/CanIf.c) (Dòng 774: `CanIf_Transmit`).
8. [`as/com/as.infrastructure/arch/common/mcal/SCan.c`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/com/as.infrastructure/arch/common/mcal/SCan.c) (Dòng 83: `Can_Write` format SLCAN ra UART1).

### 🛠️ Tiêu Chí Thành Công (Success Criteria):
* Vẽ được sơ đồ Call Graph chi tiết 6 tầng cho cả 2 chiều Tx và Rx với tên hàm và số dòng chính xác.
* Chạy QEMU bắt được chuỗi frame thực tế trên UART1: `t101807DD0C0F1331005A` (`TxMsgTime`) và `t40180101000000000000` (`OSEK NM`).

---

## TASK 3.2: CAN Bit Timing Calculation & Sample Point Verification
**Thời gian ước tính:** ~1.5h | **Mức độ:** Beginner

**Mục tiêu (Objective):** Tính toán các thanh ghi BTR0/BTR1 (BRP, TS1, TS2) cho baudrate 500 kbps tại xung nhịp Clock 36MHz (STM32F107) hoặc 50MHz (LM3S).

**Lý thuyết & Công thức:**
* $\text{Bit Time} = \frac{1}{\text{Baudrate}} = \text{Sync\_Seg} + \text{Prop\_Seg} + \text{Phase\_Seg1} + \text{Phase\_Seg2}$
* $\text{Sample Point} = \frac{\text{Sync\_Seg} + \text{Prop\_Seg} + \text{Phase\_Seg1}}{\text{Total Time Quanta (TQ)}} \times 100\%$ (Mục tiêu chuẩn CiA: 87.5%, SJW = 1 TQ).

**Yêu cầu công việc:**
1. Viết Python script tính toán và verify các giá trị cấu hình bit timing.
2. Verify kết quả đầu ra (Ví dụ cho 36MHz/500kbps: BRP=3, TS1=11, TS2=2 $\rightarrow$ Tổng 16 TQ, Sample Point = $(1+11+2)/16 = 87.5\%$).
3. Đối chiếu với cấu hình trong [`as/build/nt/lm3s6965evb/ascore/config/Can_PBCfg.c`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/build/nt/lm3s6965evb/ascore/config/Can_PBCfg.c) (`CanControllerSeg1 = 12`, `CanControllerSeg2 = 1`).

---

## TASK 3.3: Khảo Sát CAN Driver MCAL — Cấu Hình Mailbox HTH / HRH & Ring Buffer
**Thời gian ước tính:** ~3h | **Mức độ:** Intermediate

**Mục tiêu (Objective):** Đọc và phân tích mã nguồn MCAL CAN Driver: [`as/com/as.infrastructure/arch/lm3s/mcal/Can.c`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/com/as.infrastructure/arch/lm3s/mcal/Can.c) và [`as/com/as.infrastructure/arch/common/mcal/SCan.c`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/com/as.infrastructure/arch/common/mcal/SCan.c).

**Yêu cầu công việc:**
1. Tìm hiểu struct `Can_PduType`, đối tượng Mailbox phần cứng: **HTH (Hardware Transmit Handle)** và **HRH (Hardware Receive Handle)**.
2. Trace hàm `Can_Write()`: Phân tích đường đi từ API call của CanIf xuống việc nạp dữ liệu vào thanh ghi phần cứng Mailbox.
3. Giải thích cơ chế bảo vệ vùng nhớ găng (`Irq_Save` / `Irq_Restore`) khi đẩy frame vào bộ đệm vòng (Ring Buffer) chống xung đột dữ liệu đa tác vụ.

---

## TASK 3.4: CanIf Software Acceptance Filter — Lọc CAN ID Bằng Mặt Nạ Bitmask
**Thời gian ước tính:** ~2h | **Mức độ:** Intermediate

**Mục tiêu (Objective):** Đọc [`as/com/as.infrastructure/communication/CanIf/CanIf.c`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/com/as.infrastructure/communication/CanIf/CanIf.c), hiểu cơ chế lọc CAN ID bằng phần mềm (Software Filtering Mask).

**Yêu cầu công việc:**
1. Tìm hàm `CanIf_RxIndication()` và hàm nội bộ `scheduleRxIndication()`.
2. Phân tích công thức kiểm tra bitmask lọc ID:
   ```c
   if ((CanId & entry->CanIfCanRxPduCanIdMask) == entry->CanIfCanRxPduCanId)
   ```
3. Giải thích tại sao `CanIf` phải lọc bằng phần mềm khi Hardware Mailbox của vi điều khiển bị giới hạn số lượng bộ lọc phần cứng (Hardware Acceptance Filters).

---

## TASK 3.5: CanTp Multi-Frame Transmission — Phân Mảnh UDS (ISO 15765-2 DoCAN)
**Thời gian ước tính:** ~3.5h | **Mức độ:** Advanced

**Mục tiêu (Objective):** Trace và phân tích quy trình truyền gói tin chẩn đoán UDS lớn (>8 bytes) qua giao thức phân mảnh CanTp (DoCAN).

**Yêu cầu công việc:**
1. Phân tích 4 loại khung PCI (Protocol Control Information): Single Frame (SF), First Frame (FF), Consecutive Frame (CF), Flow Control (FC).
2. Vẽ sequence diagram minh họa tiến trình phân mảnh với các tham số: Block Size (`BS = 8`) và Separation Time (`STmin = 1ms`).
3. Đọc mã nguồn [`as/com/as.infrastructure/communication/CanTp/CanTp.c`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/com/as.infrastructure/communication/CanTp/CanTp.c) và tìm hàm `CanTp_Transmit()`, giải thích cơ chế quản lý các Network Timers: $N\_Ar$, $N\_Br$, $N\_Cr$.

---

## TASK 3.6: COM — Signal Packing into I-PDU & Endianness (Intel vs Motorola)
**Thời gian ước tính:** ~3h | **Mức độ:** Advanced

**Mục tiêu (Objective):** Hiểu cách module COM đóng gói nhiều tín hiệu rời rạc vào một khung I-PDU 8 bytes tuân thủ quy tắc Byte Order.

**Cấu hình Signals Mẫu:**
* `VehicleSpeed`: 16-bit, Byte 0-1, Big-endian (Motorola), Factor = 0.1 km/h.
* `GearPosition`: 4-bit, Byte 2 bits [7:4].
* `DoorStatus`: 1-bit, Byte 2 bit [3].

**Yêu cầu công việc:**
1. Đọc [`as/com/as.infrastructure/communication/Com/Com_Com.c`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/com/as.infrastructure/communication/Com/Com_Com.c) (`Com_SendSignal` và `Com_ReceiveSignal`).
2. Viết đoạn code C minh họa cách tính toán bitmask để chèn/trích xuất tín hiệu không làm biến dạng các bit lân cận trong cùng một byte.
3. Phân biệt sự khác nhau giữa **Intel (Little Endian)** và **Motorola (Big Endian)** khi định nghĩa start bit trong file DBC và ARXML.

---

## TASK 3.7: Bus Load Calculation & Overload Monitoring
**Thời gian ước tính:** ~2h | **Mức độ:** Intermediate

**Mục tiêu (Objective):** Đo và tính toán tải bus (Bus Load) với $N$ frames định kỳ trên đường truyền CAN.

**Công thức:**
$$\text{Bus Load (\%)} = \frac{N_{\text{frames}} \times \text{BitLength}_{\text{worst-case}}}{\text{Baudrate} \times \text{Cycle (s)}} \times 100\%$$

**Yêu cầu công việc:**
1. Viết Python script tính toán: với 10 frames $\times$ 130 bits (có bit stuffing) tại 500 kbps chu kỳ 10ms $\rightarrow$ Bus Load = 26%.
2. Thiết kế logic giám sát trong CAN ISR phát cảnh báo nếu Bus Load vượt ngưỡng an toàn quy định cho ô tô (> 70%).

---

## TASK 3.8: Tầng Vật Lý, Trở Kháng Đầu Cuối 120Ω & Bắt Bệnh Dạng Sóng Oscilloscope
**Thời gian ước tính:** ~2.5h | **Mức độ:** Intermediate

> 🎯 **Mục tiêu:** Áp dụng toàn bộ kiến thức vật lý ISO 11898-2 từ [Mục 1.1 trong `03_Communication_Stack_And_CAN_Protocol.md`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/docs/theory/03_Communication_Stack_And_CAN_Protocol.md#L28-L245) để giải quyết các sự cố đo kiểm thực tế trên bàn thử nghiệm (Bench Test) và trên xe thật.

### Phần A: Đo Kiểm Trở Kháng Đầu Cuối Bằng Đồng Hồ VOM
1. Trong mô hình xe điện 4 ECU (ECU 1: BMS, ECU 2: VCU, ECU 3: Inverter, ECU 4: BCM), giải thích tại sao chỉ có BMS và BCM được gắn điện trở $120\Omega$, còn VCU và Inverter tuyệt đối không được gắn trở.
2. Tính điện trở tương đương $R_{\text{bus}}$ đo được giữa CAN_H và CAN_L khi tắt nguồn xe:
   $$R_{\text{bus}} = R_1 \parallel R_2 = \frac{120\Omega \times 120\Omega}{120\Omega + 120\Omega} = 60\Omega$$
3. Giả sử một kỹ sư cắm nhầm 1 ECU thứ 3 có chứa sẵn điện trở $120\Omega$ vào bus. Hãy tính:
   - Điện trở tương đương mới $R_{\text{bus\_mới}}$.
   - Dòng điện vi sai $I_{\text{diff}}$ mà chip CAN Transceiver phải gánh ở mức Dominant ($V_{\text{diff}} = 2.0\text{V}$). So sánh với dòng điện chuẩn $33.3\text{mA}$ và nêu nguy cơ quá nhiệt gây sập nguồn chip.

### Phần B: Giải Mã Dạng Sóng Thực Tế Trên Màn Hình Máy Hiện Sóng (Oscilloscope)
Cho dạng sóng đo được trên máy hiện sóng với cấu hình: CH1 = CAN_H, CH2 = CAN_L, MATH = CH1 - CH2:
```text
 Điện áp (V)
   ▲
3.5┼               ┌───────────────────────┐                       ┌───────────────────────┐  <-- CAN_H (CH1)
   │               │                       │                       │                       │
2.5┼═══════════════╡                       ╞═══════════════════════╡                       ╞══  <-- CAN_H & CAN_L
   │               │                       │                       │                       │
1.5┼               └───────────┬───────────┘                       └───────────┬───────────┘  <-- CAN_L (CH2)
   │                           │ Sample Point (80%)                            │
0.0┴───────────────────────────────────────────────────────────────────────────────────────► Thời gian (t)
   │◄── 2.0 µs ───►│◄────── 2.0 µs ───────►│◄────── 2.0 µs ───────►│◄────── 2.0 µs ───────►│
```
1. Xác định mức điện áp tĩnh (Recessive) và mức điện áp vi sai (Dominant) trên bus.
2. Từ độ rộng mỗi ô bit $T_{\text{bit}} = 2.0\,\mu\text{s}$, hãy tính tốc độ baudrate thực tế của mạng.
3. Giải thích tại sao sườn lên chuyển sang Dominant lại dốc hơn ($t_{\text{rise}} < 50\text{ns}$) so với sườn xuống trở về Recessive ($t_{\text{fall}} \approx 50\text{ns} - 100\text{ns}$).

### Phần C: Bắt Bệnh 4 Dị Tật Tín Hiệu (Signal Anomalies)
Lập bảng chẩn đoán nguyên nhân và cách khắc phục khi gặp 4 hình ảnh sóng bất thường trên màn hình máy hiện sóng:
1. Sóng có xung gai dội ngược hình sin (**Ringing / Overshoot $> 4.0\text{V}$**).
2. Biên độ vi sai bị sụt giảm thấp (**$V_{\text{diff}} < 1.2\text{V}$**).
3. Điện áp tĩnh bị dời từ $2.5\text{V}$ lên $3.8\text{V}$ (**Ground Offset / Shift**).
4. Đường tín hiệu CAN_H hoặc CAN_L bị ghim cứng ở $0\text{V}$ hoặc $12\text{V}$.

---

## TASK 3.9: Trở Thành BSW Engineer — Cấu Hình ARXML & Sinh Mã C Bằng Python Toolchain (`argen`)
**Thời gian ước tính:** ~3h | **Mức độ:** Advanced

> 🎯 **Mục tiêu:** Thực hành toàn bộ quy trình làm việc chuẩn mực của một Kỹ sư AUTOSAR BSW trong dự án `Study_AUTOSAR`: Thêm một gói tin PDU mới vào tập tin cấu hình ARXML, chạy bộ sinh mã tự động bằng Python, và đối chiếu mã nguồn C được tạo ra.

### 📂 Tệp Cần Thao Tác & Chỉnh Sửa:
1. Tập tin cấu hình gốc: [`as/com/as.application/common/autosar.arxml`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/com/as.application/common/autosar.arxml).
2. Bộ sinh mã Python:
   - [`as/com/as.tool/config.infrastructure.system/argen/GenCanIf.py`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/com/as.tool/config.infrastructure.system/argen/GenCanIf.py)
   - [`as/com/as.tool/config.infrastructure.system/argen/GenPduR.py`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/com/as.tool/config.infrastructure.system/argen/GenPduR.py)
3. Tập tin C được tạo ra để kiểm chứng:
   - `as/build/nt/lm3s6965evb/ascore/config/CanIf_Cfg.c`
   - `as/build/nt/lm3s6965evb/ascore/config/PduR_Cfg.c`

### Yêu Cầu Thực Hiện:
1. **Bước 1: Thêm gói tin mới vào `autosar.arxml`:**
   Giả sử xe điện bổ sung một cảm biến dòng điện pin cao áp mới cần truyền định kỳ:
   - Tên PDU EcuC: `TxBmsPackStatus`
   - CAN ID: `0x250` (Standard 11-bit)
   - DLC: 8 bytes
   - HTH Reference: `LS_Hth`
   - TransmitNotifier: `PduR`
   - UserNotification: `CanIf_User`
   Thêm thẻ `<Pdu>` này vào `<TxPduList>` của `<CanIf>` và tạo tuyến định tuyến tương ứng trong `<PduR>`.

2. **Bước 2: Chạy bộ sinh mã Python:**
   Sử dụng Python chạy script sinh mã cho module CanIf và PduR từ thư mục công cụ của dự án.
3. **Bước 3: Kiểm chứng kết quả sinh mã C:**
   - Mở file `CanIf_Cfg.c` vừa sinh và kiểm tra mảng `CanIfTxPduConfigData[]`:
     - Xác nhận đã có phần tử mới với `CanIfCanTxPduIdCanId = 0x250`.
     - Xác nhận con trỏ callback `CanIfUserTxConfirmation` trỏ đúng vào `PduR_CanIfTxConfirmation`.
   - Mở file `PduR_Cfg.c` và xác nhận bảng định tuyến đã cập nhật tuyến chuyển tiếp gói tin từ COM xuống CanIf.

---

## TASK 3.10: Khảo Sát Fault Confinement & Bus-Off Recovery CanSM State Machine
**Thời gian ước tính:** ~2.5h | **Mức độ:** Advanced

> 🎯 **Mục tiêu:** Nắm vững cơ chế bảo vệ phần cứng tự động của CAN Bus (Fault Confinement) và máy trạng thái phục hồi lỗi nghiêm trọng (Bus-Off Recovery) theo chuẩn AUTOSAR CanSM.

### 📂 Tệp Cần Đọc & Đối Chiếu:
1. Lý thuyết tham chiếu: [Mục 1.5 & Mục 3.6 trong `03_Communication_Stack_And_CAN_Protocol.md`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/docs/theory/03_Communication_Stack_And_CAN_Protocol.md#L450-L550).
2. Mã nguồn CanSM: [`as/com/as.infrastructure/communication/CanSM/CanSM.c`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/com/as.infrastructure/communication/CanSM/CanSM.c).
3. Cấu hình CanSM: [`as/com/as.application/common/config/CanSM_LCfg.c`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/com/as.application/common/config/CanSM_LCfg.c).
4. Callback từ CanIf: [`as/com/as.infrastructure/communication/CanIf/CanIf.c`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/com/as.infrastructure/communication/CanIf/CanIf.c).

### Yêu Cầu Thực Hiện:
1. **Phân tích cơ chế bộ đếm lỗi phần cứng (Hardware Error Counters):**
   - Giải thích quy tắc tăng/giảm của **TEC (Transmit Error Counter)** và **REC (Receive Error Counter)** khi phát hiện lỗi Bit Error, Stuff Error, CRC Error, ACK Error.
   - Vẽ sơ đồ chuyển đổi 3 trạng thái:
     $$\text{Error Active (TEC, REC } \le 96) \longleftrightarrow \text{Error Passive (96 } < \text{ TEC, REC } \le 255) \longrightarrow \text{Bus-Off (TEC } > 255)$$
2. **Trace chuỗi gọi hàm khi xảy ra Bus-Off:**
   - Khi phần cứng MCU phát hiện `TEC > 255`:
     $$\text{Hardware Interrupt} \longrightarrow \text{Can\_MainFunction\_BusOff()} \longrightarrow \text{CanIf\_ControllerBusOff()} \longrightarrow \text{CanSM\_ControllerBusOff()}$$
3. **Phân tích máy trạng thái phục hồi (Bus-Off Recovery State Machine) trong CanSM:**
   - Đọc hàm `CanSM_MainFunction()` và phân tích 2 bộ định thời phục hồi:
     - **L1 (BorTimeL1 - Fast Recovery Timer, ví dụ 50ms):** Cho phép thử phục hồi nhanh khi lỗi chập chờn nhất thời.
     - **L2 (BorTimeL2 - Slow Recovery Timer, ví dụ 3000ms):** Chuyển sang chu kỳ phục hồi chậm khi lỗi phần cứng kéo dài để tránh làm nghẽn mạng toàn xe.
   - Trình bày lệnh gọi API của CanSM để tái khởi động bộ điều khiển CAN: `Can_SetControllerMode(Controller, CAN_T_START)`.

---

## TASK 3.11: Kiến Trúc Sư Hệ Thống (System Architect) — Phân Bổ SWC Vào ECU Trong System ARXML & Thay Đổi Bản Chất Điều Hướng Của RTE (Intra-ECU RAM vs Inter-ECU CAN)
**Thời gian ước tính:** ~3h | **Mức độ:** Advanced

> 🎯 **Mục tiêu:** Nhập vai một **System Architect** trong giai đoạn thiết kế toàn xe (System Design / VFB Phase) để làm sáng tỏ bản chất:  
> **Làm sao RTE Generator biết khi nào sinh mã ghi RAM nội bộ (Intra-ECU) và khi nào sinh mã gọi ComStack `Com_SendSignal()` để bắn khung CAN (Inter-ECU)?**  
> Bạn sẽ trực tiếp phân tích và chỉnh sửa cấu trúc `System ARXML`, thực nghiệm hai kịch bản phân bổ ECU, và đối chiếu sự thay đổi của mã nguồn C được sinh ra trong tầng RTE mà không cần thay đổi dù chỉ một dòng code của tầng Application (Location Transparency).

### 📂 Tệp Cần Đọc & Đối Chiếu:
1. Lý thuyết tham chiếu:
   - [Mục 5.3 trong `01_AUTOSAR_Layered_Architecture_And_VFB_Masterclass.md`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/docs/theory/01_AUTOSAR_Layered_Architecture_And_VFB_Masterclass.md#53-bản-chất-kỹ-thuật-rte-thực-chất-làm-những-thao-tác-gì) (Lưu ý về quy ước điều hướng tĩnh của RTE).
   - [Mục 3 & Mục 4 trong `06_Virtual_Functional_Bus_VFB_Deep_Dive.md`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/docs/supplementary_knowledge/06_Virtual_Functional_Bus_VFB_Deep_Dive.md) (Quy trình 4 bước chuyển hóa từ VFB sang RTE).
2. Tệp mô tả hệ thống gốc:
   - [`as/com/as.application/common/autosar.arxml`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/com/as.application/common/autosar.arxml).
3. Bộ sinh mã RTE:
   - [`as/com/as.tool/config.infrastructure.system/argen/GenRte.py`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/com/as.tool/config.infrastructure.system/argen/GenRte.py).
4. Mã nguồn SWC tham chiếu:
   - [`as/com/as.application/swc/telltale/Swc_Telltale.c`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/com/as.application/swc/telltale/Swc_Telltale.c).

---

### 🔬 Bối Cảnh Thực Nghiệm:
Xét tính năng điều khiển vị trí bàn đạp ga trên xe điện:
* Thành phần gửi: `SWC_Pedal` cung cấp cổng `PPort_PedalPosition` (Signal: `PedalVal`, kiểu `uint16`).
* Thành phần nhận: `SWC_Motor` yêu cầu cổng `RPort_PedalPosition` (Signal: `PedalVal`).
* Trên Bus Chức Năng Ảo (VFB), 2 cổng này được nối với nhau qua một `ASSEMBLY-SW-CONNECTOR`.

---

### 🛠️ Yêu Cầu Thực Hiện:

#### Phần A: Phân Tích Cấu Trúc Ánh Xạ Trong System ARXML (Design-Time)
1. **Thiết lập Kịch bản 1 (Intra-ECU Mapping):**
   - Viết đoạn mã ARXML mẫu trong thẻ `<SWC-TO-ECU-MAPPING>` định nghĩa việc gán cả `SWC_Pedal` và `SWC_Motor` vào cùng hộp điều khiển `ECU_VCU`.
   - Giải thích: Tại sao trong kịch bản này, thẻ `<DATA-MAPPING>` (ánh xạ tín hiệu vào mạng CAN) hoàn toàn không cần khai báo cho luồng dữ liệu `PedalVal`?
2. **Thiết lập Kịch bản 2 (Inter-ECU Mapping):**
   - Giả định kiến trúc sư tách `SWC_Motor` sang hộp điều khiển cầu sau `ECU_Inverter`, còn `SWC_Pedal` vẫn ở `ECU_VCU`.
   - Viết đoạn mã ARXML mẫu thể hiện:
     - `SWC-TO-ECU-MAPPING`: Gán `SWC_Pedal` $\rightarrow$ `ECU_VCU`; `SWC_Motor` $\rightarrow$ `ECU_Inverter`.
     - `SENDER-RECEIVER-TO-SIGNAL-MAPPING`: Ánh xạ cổng dữ liệu VFB `PedalVal` vào tín hiệu mạng `I-SIGNAL` mang tên `ISig_PedalPosition`.
     - `I-SIGNAL-TO-I-PDU-MAPPING`: Đóng gói `ISig_PedalPosition` vào khung CAN PDU `TxPedalPdu` (CAN ID: `0x180`).

---

#### Phần B: Đối Chiếu Mã Nguồn C Do RTE Generator Sinh Ra
1. **Mã sinh ra của RTE trên `ECU_VCU` trong Kịch bản 1 (Intra-ECU):**
   - Phân tích và viết đoạn code C mà `GenRte.py` sẽ sinh ra cho API `Rte_Write_PPort_PedalPosition_PedalVal()`.
   - Chỉ ra việc truy cập biến toàn cục trong RAM nội bộ (`static uint16 Rte_Buffer_PedalVal`) và chi phí thời gian thực (Zero network latency, < 10 CPU cycles).
2. **Mã sinh ra của RTE trên `ECU_VCU` trong Kịch bản 2 (Inter-ECU):**
   - Phân tích và viết đoạn code C mà `GenRte.py` sẽ sinh ra cho API `Rte_Write_PPort_PedalPosition_PedalVal()`.
   - Chỉ ra việc RTE tự động chuyển sang gọi API của tầng BSW ComStack:
     ```c
     Com_SendSignal(COM_SID_ISig_PedalPosition, &data);
     ```
   - Phân tích mã sinh ra của `Rte_Read_RPort_PedalPosition_PedalVal()` trên `ECU_Inverter`: Lấy dữ liệu từ bộ đệm nhận của `Com_ReceiveSignal()` hoặc thông qua callback `Rte_COMCbk()`.

---

#### Phần C: Thẩm Định Kiến Trúc & Câu Hỏi Phỏng Vấn Chuyên Sâu
1. **Chứng minh tính "Location Transparency":**
   - Hãy xem xét file mã nguồn C của `SWC_Pedal.c`:
     ```c
     void Pedal_Runnable(void) {
         uint16 raw_pedal = Read_Pedal_Sensors();
         Rte_Write_PPort_PedalPosition_PedalVal(raw_pedal);
     }
     ```
   - Chứng minh rằng khi chuyển từ Kịch bản 1 sang Kịch bản 2, mã nguồn trên của `SWC_Pedal` **không cần phải thay đổi dù chỉ một ký tự**.
   - Điều gì sẽ xảy ra nếu một kỹ sư không dùng AUTOSAR mà code C truyền thống gọi thẳng `CAN_Write(0x180, ...)` khi chuyển kiến trúc?
2. **Bắt bệnh "Content-Addressed" của mạng CAN:**
   - Khi `Rte_Write` gọi `Com_SendSignal()` trên VCU, tại sao RTE không thể biết được liệu Inverter có đang sống để nhận khung CAN `0x180` hay không?
   - Cơ chế nào của AUTOSAR COM giúp SWC phát hiện ra hộp Inverter bị mất nguồn hoặc đứt cáp CAN? (Gợi ý: Thuộc tính `ComTimeout` và mã lỗi trả về `RTE_E_TIMEOUT`).

---

### 🛠️ Tiêu Chí Thành Công (Success Criteria):
* Hoàn thành đầy đủ các đoạn trích ARXML mẫu chuẩn AUTOSAR Release 4.x cho cả 2 kịch bản phân bổ.
* Chỉ ra được sự khác biệt $100\%$ trong mã nguồn C của `Rte.c` giữa Intra-ECU và Inter-ECU.
* Giải thích thấu đáo vai trò của System Architect trong việc quyết định hành vi điều hướng của RTE mà không làm ảnh hưởng đến mã nguồn ứng dụng.

---

> 🎉 **Tổng kết:** Hoàn thành trọn vẹn 11 nhiệm vụ trên, bạn sẽ nắm vững toàn bộ kiến thức kỹ nghệ thực chiến của ngăn xếp CAN AUTOSAR — từ tính toán vật lý, đo đạc oscilloscope, phân tích driver MCAL, cấu hình ma trận ARXML, phân mảnh chẩn đoán UDS, xử lý sự cố Bus-Off, cho đến vai trò System Architect phân bổ SWC và điều hướng thông điệp trên toàn xe!
