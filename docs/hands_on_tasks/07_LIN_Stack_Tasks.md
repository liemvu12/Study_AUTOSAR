# CHUYÊN ĐỀ 07: LIN Protocol & AUTOSAR LinStack Hands-on Tasks
## KẾ HOẠCH BÀI TẬP THỰC HÀNH CHUYÊN SÂU — 4 Tasks (~8 giờ)

> 📚 **Tài liệu lý thuyết đối chiếu:** [`docs/theory/11_LIN_Protocol_And_LinStack_Deep_Dive.md`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/docs/theory/11_LIN_Protocol_And_LinStack_Deep_Dive.md)  
> 🔧 **Mã nguồn gốc đối chiếu:** [`as/com/as.infrastructure/communication/Lin/`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/com/as.infrastructure/communication/Lin/), [`as/com/as.application/common/autosar.arxml`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/com/as.application/common/autosar.arxml#L394-L405)  
> ⏱️ **Tổng thời lượng ước tính:** ~8 giờ

---

### 🗺️ Tổng Quan Các Bài Tập Trong Chuyên Đề:

| Mã Task | Tên Bài Tập Thực Hành | Độ Khó | Trọng Tâm Kiến Thức |
| :---: | :--- | :---: | :--- |
| **Task 7.1** | **Trace Dòng Chảy Frame Gốc `LIN_TX_MSG1` Xuyên Suốt 6 Tầng** | 🟢 Beginner | BSW COM $\rightarrow$ PduR $\rightarrow$ LinIf $\rightarrow$ Lin MCAL Driver $\rightarrow$ UART |
| **Task 7.2** | **Cấu Hình Bảng Lập Lịch LIN Schedule Table Trong LinIf** | 🟡 Intermediate | Quản lý Time Slots, Master Polling, Xử lý chuyển đổi bảng Schedule |
| **Task 7.3** | **Xử Lý Chiều Nhận Frame Gốc `LIN_RX_MSG1` & Timeout Monitoring** | 🟡 Intermediate | LinIf Rx Indication $\rightarrow$ PduR $\rightarrow$ COM Unpack $\rightarrow$ Deadline Monitoring |
| **Task 7.4** | **Phân Tích & Viết File LDF (LIN Description File) Cho Cụm Cửa Xe** | 🔴 Advanced | Thiết kế file LDF chuẩn công nghiệp, ánh xạ Node, Signal, Frame, Schedule |

---

## TASK 7.1: Trace Dòng Chảy Frame Gốc `LIN_TX_MSG1` Xuyên Suốt 6 Tầng (~2h)

### 🎯 Mục Tiêu:
Trace chi tiết đường đi của gói tin LIN Master Transmit gốc **`LIN_TX_MSG1`** được khai báo tại dòng 394 trong file `autosar.arxml` từ Tầng Ứng Dụng xuống Thanh ghi phần cứng UART.

### 📂 Tệp Cần Đọc:
1. `as/com/as.application/common/autosar.arxml` (Dòng 394: Khai báo I-PDU `LIN_TX_MSG1`).
2. `as/com/as.infrastructure/communication/Com/Com_Com.c` (Hàm `Com_SendSignal` & `Com_Internal_TriggerIPduSend`).
3. `as/com/as.infrastructure/communication/PduR/PduR_Routing.c` (Định tuyến sang `LinIf`).
4. `as/com/as.infrastructure/communication/Lin/LinIf.c` (Hàm `LinIf_Transmit` & `LinIf_MainFunction`).
5. `as/com/as.infrastructure/communication/Lin/Lin.c` (MCAL Driver `Lin_SendFrame`).

### 🛠️ Tiêu Chí Thành Công (Success Criteria):
* Vẽ được sơ đồ Call Graph chi tiết với tên hàm và số dòng chính xác.
* Giải thích được cơ chế đóng gói 8 bytes của Signal `LIN_TX_MSG1_DATA` (StartBit 7, Big Endian).

---

## TASK 7.2: Cấu Hình Bảng Lập Lịch LIN Schedule Table Trong LinIf (~2h)

### 🎯 Mục Tiêu:
Hiểu và xây dựng một bảng Schedule Table trong `LinIf` điều phối 3 khe thời gian (Time Slots):
* Slot 1 (10ms): Phát Header `LIN_TX_MSG1` (Lệnh gạt mưa).
* Slot 2 (10ms): Phát Header `LIN_RX_MSG1` (Slave phản hồi vị trí mô-tơ).
* Slot 3 (20ms): Khe trống hoặc Diagnostic Frame `0x3C`.

### 🛠️ Tiêu Chí Thành Công (Success Criteria):
* Giải thích được cách `LinIf_MainFunction()` kiểm tra biến đếm tick và chuyển sang Entry tiếp theo trong bảng lập lịch.

---

## TASK 7.3: Xử Lý Chiều Nhận Frame Gốc `LIN_RX_MSG1` & Deadline Monitoring (~2h)

### 🎯 Mục Tiêu:
Trace luồng nhận dữ liệu từ khi ngắt UART nhận đủ 8 bytes của `LIN_RX_MSG1` đến khi đẩy lên bộ đệm COM Signal, và cơ chế xử lý khi Slave bị đứt dây (Timeout Factor = 200).

### 🛠️ Tiêu Chí Thành Công (Success Criteria):
* Mapped chuỗi callback: `Lin_GetStatus()` / `LinIf_RxIndication()` $\rightarrow$ `PduR_LinIfRxIndication()` $\rightarrow$ `Com_RxIndication()` $\rightarrow$ `Com_RxProcessSignals()`.

---

## TASK 7.4: Thiết Kế File LDF Cho Cụm Cửa Xe (BCM Master & Door Slaves) (~2h)

### 🎯 Mục Tiêu:
Viết file LDF chuẩn công nghiệp mô tả mạng LIN 19.2 kbps kết nối 1 Master (BCM) và 2 Slaves (Door_Left, Door_Right).
