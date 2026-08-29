# CHUYÊN ĐỀ 03: Communication Stack & CAN Protocol Hands-on Tasks
## KẾ HOẠCH BÀI TẬP THỰC HÀNH CHUYÊN SÂU — 7 Tasks (~17 giờ)

> 📚 **Tài liệu lý thuyết đối chiếu:** [`docs/theory/03_Communication_Stack_And_CAN_Protocol.md`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/docs/theory/03_Communication_Stack_And_CAN_Protocol.md)  
> 📑 **Ma trận gói tin & DBC:** [`docs/theory/10_CAN_DBC_Format_And_Tools.md`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/docs/theory/10_CAN_DBC_Format_And_Tools.md)  
> 💡 **Bộ Lời Giải Mẫu Chi Tiết (Solutions):** [`docs/hands_on_tasks/solutions/02_ComStack_CAN_Solutions.md`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/docs/hands_on_tasks/solutions/02_ComStack_CAN_Solutions.md)  
> 🔧 **Source code base:** `as/com/as.infrastructure/communication/`  
> ⏱️ **Tổng thời lượng ước tính:** ~17 giờ

---

### 📊 Ma Trận Nhiệm Vụ Chuyên Đề 03 (ComStack Task Summary):

| Mã Task | Tên Nhiệm Vụ Thực Hành | Mức Độ | Thời Gian | Trọng Tâm Kỹ Nghệ |
| :---: | :--- | :---: | :---: | :--- |
| **Task 3.1** | **Trace Dòng Chảy CAN Message 6 Tầng Toàn Diện (End-to-End Trace)** | 🔴 Advanced | ~3h | Trace 6 tầng BSW: COM $\rightarrow$ PduR $\rightarrow$ CanIf $\rightarrow$ MCAL Can $\rightarrow$ UART1 |
| **Task 3.2** | **CAN Bit Timing Calculation & Sample Point Verification** | 🟢 Beginner | ~1h | Tính thanh ghi BRP, TS1, TS2 đạt Sample Point 87.5% cho 500 kbps |
| **Task 3.3** | **Khảo Sát CAN Driver MCAL — Cấu Hình Mailbox HTH / HRH** | 🟡 Intermediate | ~3h | Phân tích `Can_Write()`, cơ chế Mailbox và thanh ghi phần cứng |
| **Task 3.4** | **CanIf Software Acceptance Filter — Lọc CAN ID Bằng Phần Mềm** | 🟡 Intermediate | ~2h | Hàm `CanIf_RxIndication()`, lọc dải ID hợp lệ và loại bỏ frame rác |
| **Task 3.5** | **CanTp Multi-Frame Transmission — Phân Mảnh UDS (ISO 15765-2)** | 🔴 Advanced | ~4h | Giao thức ISOTP: First Frame (FF), Flow Control (FC), Consecutive Frame (CF) |
| **Task 3.6** | **COM — Signal Packing Into I-PDU & Endianness (Intel vs Motorola)** | 🔴 Advanced | ~3h | Đóng gói nhiều Signal vào 1 I-PDU 8 bytes, xử lý Byte Order |
| **Task 3.7** | **Bus Load Calculation & Overload Monitoring** | 🟡 Intermediate | ~2h | Công thức tính % Bus Load, đếm frames trong CAN ISR và phát cảnh báo |

---

## TASK 3.1: Trace Dòng Chảy CAN Message 6 Tầng Toàn Diện (End-to-End ComStack Trace)
**Thời gian ước tính:** ~3h | **Mức độ:** Advanced

> 🎯 **Mục tiêu:** Trace 1 thông điệp CAN xuyên suốt 6 tầng kiến trúc AUTOSAR theo cả 2 chiều hoàn toàn dựa trên **mã nguồn gốc có sẵn của dự án `as` (100% Native Code Base)**:
> 1. **Chiều Gửi (Tx Path):** Trace dòng chảy gói tin thời gian gốc **`TxMsgTime` (CAN ID: `0x101`)** qua toàn bộ ngăn xếp BSW COM và gói tin quản trị mạng gốc **`OSEK_NM_TX` (CAN ID: `0x401`)** từ Lõi BSW $\longrightarrow$ PduR $\longrightarrow$ CanIf $\longrightarrow$ MCAL Driver $\longrightarrow$ Dây Bus CAN vật lý.
> 2. **Chiều Nhận (Rx Path):** Trace dòng chảy gói tin tốc độ xe gốc **`RxMsgAbsInfo` (CAN ID: `0x102`)** từ Khung mạng vật lý MCAL $\longrightarrow$ CanIf $\longrightarrow$ PduR $\longrightarrow$ COM $\longrightarrow$ RTE $\longrightarrow$ Application SWC (`widget_refresh.c`).

### 📂 Tệp Cần Đọc & Đối Chiếu:
1. `as/com/as.application/common/autosar.arxml` (Dòng 352: Cấu hình I-PDU `TxMsgTime`).
2. `as/com/as.infrastructure/system/SchM/SchM.c` (Dòng 441: `Com_IpduGroupStart`, Dòng 522: `SCHM_MAINFUNCTION_COMTX`).
3. `as/com/as.infrastructure/communication/Com/Com_Sched.c` (Dòng 98: `Com_MainFunctionTx`).
4. `as/com/as.infrastructure/communication/Com/Com_Com.c` (Dòng 198: `Com_Internal_TriggerIPduSend`, Dòng 236: `PduR_ComTransmit`).
5. `as/com/as.infrastructure/communication/PduR/PduR_Routing.c` (Dòng 59: `CanIf_Transmit`).
6. `as/build/nt/lm3s6965evb/ascore/config/CanIf_Cfg.c` (Dòng 168: Ánh xạ CAN ID `0x101`).
7. `as/com/as.infrastructure/communication/CanIf/CanIf.c` (Dòng 774: `CanIf_Transmit`).
8. `as/com/as.infrastructure/arch/common/mcal/SCan.c` (Dòng 83: `Can_Write` format SLCAN ra UART1).

### 🛠️ Tiêu Chí Thành Công (Success Criteria):
* Vẽ được sơ đồ Call Graph chi tiết 6 tầng cho cả 2 chiều Tx và Rx với tên hàm và số dòng chính xác.
* Chạy QEMU bắt được chuỗi frame thực tế trên UART1: `t101807DD0C0F1331005A` (`TxMsgTime`) và `t40180101000000000000` (`OSEK NM`).

---

## TASK 3.2: CAN Bit Timing Calculation & Sample Point Verification
**Thời gian ước tính:** ~1h | **Mức độ:** Beginner

**Mục tiêu (Objective):** Tính toán các thanh ghi BTR0/BTR1 (BRP, TS1, TS2) cho baudrate 500 kbps tại xung nhịp Clock 36MHz (STM32F107) hoặc 50MHz (LM3S).

**Lý thuyết & Công thức:**
* $	ext{Bit Time} = rac{1}{	ext{Baudrate}} = 	ext{Sync\_Seg} + 	ext{Prop\_Seg} + 	ext{Phase\_Seg1} + 	ext{Phase\_Seg2}$
* $	ext{Sample Point} = rac{	ext{Sync\_Seg} + 	ext{Prop\_Seg} + 	ext{Phase\_Seg1}}{	ext{Total Time Quanta (TQ)}} 	imes 100\%$ (Mục tiêu: 87.5%, SJW = 1 TQ).

**Yêu cầu công việc:**
1. Viết Python script tính toán và verify các giá trị cấu hình bit timing.
2. Verify kết quả đầu ra (Ví dụ cho 36MHz/500kbps: BRP=3, TS1=11, TS2=2 $
ightarrow$ Tổng 16 TQ, Sample Point = $(1+11+2)/16 = 87.5\%$).

---

## TASK 3.3: Read CAN Driver Source Code — Config Mailbox
**Thời gian ước tính:** ~3h | **Mức độ:** Intermediate

**Mục tiêu (Objective):** Đọc và phân tích mã nguồn MCAL CAN Driver: `as/com/as.infrastructure/arch/lm3s/mcal/Can.c` và `arch/common/mcal/SCan.c`.

**Yêu cầu công việc:**
1. Tìm hiểu struct `Can_PduType`, HTH (Hardware Transmit Handle), HRH (Hardware Receive Handle).
2. Trace hàm `Can_Write()`: Phân tích đường đi từ API call xuống việc ghi vào thanh ghi phần cứng Mailbox.
3. Giải thích cơ chế bảo vệ vùng nhớ găng (`Irq_Save` / `Irq_Restore`) khi đẩy frame vào Ring Buffer.

---

## TASK 3.4: CanIf Software Acceptance Filter
**Thời gian ước tính:** ~2h | **Mức độ:** Intermediate

**Mục tiêu (Objective):** Đọc `as/com/as.infrastructure/communication/CanIf/CanIf.c`, hiểu cơ chế lọc CAN ID bằng phần mềm (Software Filtering Mask).

**Yêu cầu công việc:**
1. Tìm hàm `CanIf_RxIndication()` và `scheduleRxIndication()`.
2. Phân tích công thức kiểm tra bitmask lọc ID:
   ```c
   if ((CanId & entry->CanIfCanRxPduCanIdMask) == entry->CanIfCanRxPduCanId)
   ```
3. Giải thích tại sao `CanIf` phải lọc bằng phần mềm khi Hardware Mailbox của MCU bị giới hạn số lượng bộ lọc.

---

## TASK 3.5: CanTp Multi-Frame Transmission (ISO 15765-2)
**Thời gian ước tính:** ~4h | **Mức độ:** Advanced

**Mục tiêu (Objective):** Trace và phân tích quy trình truyền gói tin chẩn đoán UDS lớn (>8 bytes) qua giao thức phân mảnh CanTp (ISOTP).

**Yêu cầu công việc:**
1. Trace 4 loại khung PCI (Protocol Control Information): Single Frame (SF), First Frame (FF), Consecutive Frame (CF), Flow Control (FC).
2. Vẽ sequence diagram minh họa tiến trình phân mảnh với các tham số: Block Size (BS = 3) và Separation Time (STmin = 10ms).
3. Đọc mã nguồn `as/com/as.infrastructure/communication/CanTp/CanTp.c` và tìm hàm `CanTp_Transmit()`.

---

## TASK 3.6: COM — Signal Packing into I-PDU & Endianness
**Thời gian ước tính:** ~3h | **Mức độ:** Advanced

**Mục tiêu (Objective):** Hiểu cách module COM đóng gói nhiều tín hiệu rời rạc vào một khung I-PDU 8 bytes.

**Cấu hình Signals Mẫu:**
* `VehicleSpeed`: 16-bit, Byte 0-1, Big-endian (Motorola), Factor = 0.1 km/h.
* `GearPosition`: 4-bit, Byte 2 bits [7:4].
* `DoorStatus`: 1-bit, Byte 2 bit [3].

**Yêu cầu công việc:**
1. Đọc `as/com/as.infrastructure/communication/Com/Com_Com.c` (`Com_SendSignal` và `Com_ReceiveSignal`).
2. Viết đoạn code minh họa cách tính toán bitmask để trích xuất tín hiệu không bị tràn byte.
3. Phân biệt sự khác nhau giữa **Intel (Little Endian)** và **Motorola (Big Endian)** khi định nghĩa start bit.

---

## TASK 3.7: Bus Load Calculation & Monitoring
**Thời gian ước tính:** ~2h | **Mức độ:** Intermediate

**Mục tiêu (Objective):** Đo và tính toán bus load với $N$ frames định kỳ trên đường truyền CAN.

**Công thức:**
$$	ext{Bus Load (\%)} = rac{N_{	ext{frames}} 	imes 	ext{BitLength}_{	ext{worst-case}}}{	ext{Baudrate} 	imes 	ext{Cycle (s)}} 	imes 100\%$$

**Yêu cầu công việc:**
1. Viết Python script tính toán: với 10 frames $	imes$ 130 bits tại 500 kbps chu kỳ 10ms $
ightarrow$ Bus Load = 26%.
2. Thiết kế logic giám sát trong CAN ISR phát cảnh báo nếu Bus Load vượt ngưỡng an toàn (> 70%).
