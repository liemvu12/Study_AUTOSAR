# CHUYÊN ĐỀ 08: Automotive Ethernet, SOME/IP & DoIP Hands-on Tasks
## KẾ HOẠCH BÀI TẬP THỰC HÀNH CHUYÊN SÂU — 4 Tasks (~8 giờ)

> 📚 **Tài liệu lý thuyết đối chiếu:** [`docs/theory/12_Automotive_Ethernet_SOMEIP_DoIP_Deep_Dive.md`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/docs/theory/12_Automotive_Ethernet_SOMEIP_DoIP_Deep_Dive.md)  
> 🔧 **Mã nguồn gốc đối chiếu:** [`as/com/as.infrastructure/communication/Eth/`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/com/as.infrastructure/communication/Eth/), [`SoAd/`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/com/as.infrastructure/communication/SoAd/), [`DoIP/`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/com/as.infrastructure/communication/DoIP/), [`as/com/as.application/common/autosar.arxml`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/com/as.application/common/autosar.arxml#L294-L305)  
> ⏱️ **Tổng thời lượng ước tính:** ~8 giờ

---

### 🗺️ Tổng Quan Các Bài Tập Trong Chuyên Đề:

| Mã Task | Tên Bài Tập Thực Hành | Độ Khó | Trọng Tâm Kiến Thức |
| :---: | :--- | :---: | :--- |
| **Task 8.1** | **Trace Dòng Chảy Gói Tin Socket Gốc `SOAD_TX` / `SOAD_RX`** | 🟢 Beginner | UDS DCM $\rightarrow$ PduR $\rightarrow$ SoAd $\rightarrow$ TcpIp Socket $\rightarrow$ Eth Driver |
| **Task 8.2** | **Cấu Hình Ánh Xạ Socket Adaptor (SoAd Routing Table)** | 🟡 Intermediate | Chuyển đổi PDU ID sang IP Address:Port (TCP Port 13400 / UDP Port 30490) |
| **Task 8.3** | **Trace Sequence Chẩn Đoán DoIP (ISO 13400) & Routing Activation** | 🔴 Advanced | Thiết lập kết nối TCP, Routing Activation Request `0x0005`, truyền UDS qua IP |
| **Task 8.4** | **Triển Khai SOME/IP Service & Service Discovery (SD)** | 🔴 Advanced | Xây dựng SOME/IP Header, cơ chế OfferService / FindService / Subscribe Event |

---

## TASK 8.1: Trace Dòng Chảy Gói Tin Socket Gốc `SOAD_TX` / `SOAD_RX` (~2h)

### 🎯 Mục Tiêu:
Trace dòng chảy gói tin chẩn đoán UDS qua mạng Ethernet gốc **`SOAD_TX`** (Dòng 77 & 300 trong `autosar.arxml`) từ module DCM xuống Socket Adaptor và Driver mạng Ethernet.

### 📂 Tệp Cần Đọc:
1. `as/com/as.application/common/autosar.arxml` (Dòng 294-305: PduR Routing giữa `Dcm` và `SoAdTp`).
2. `as/com/as.infrastructure/diagnostic/Dcm/Dcm.c` (Hàm gửi phản hồi chẩn đoán `Dcm_ProcessingDone`).
3. `as/com/as.infrastructure/communication/PduR/PduR_Routing.c` (Hàm `PduR_DcmTransmit` chuyển tiếp sang `SoAd_Transmit`).
4. `as/com/as.infrastructure/communication/SoAd/SoAd.c` (Hàm `SoAd_Transmit` & `SoAd_IfTransmit`).
5. `as/com/as.infrastructure/communication/Eth/Eth.c` (MCAL Driver `Eth_Transmit`).

---

## TASK 8.2: Cấu Hình Ánh Xạ Socket Adaptor (SoAd Routing Table) (~2h)

### 🎯 Mục Tiêu:
Hiểu và xây dựng bảng cấu hình `SoAd_PduRoute` ánh xạ một PDU ID cố định sang Socket kết nối IP (IP:Port, TCP/UDP).

---

## TASK 8.3: Trace Sequence Chẩn Đoán DoIP (ISO 13400) (~2h)

### 🎯 Mục Tiêu:
Trace toàn bộ vòng đời phiên chẩn đoán DoIP: Cắm cáp mạng LAN $\rightarrow$ Nhận IP qua DHCP $\rightarrow$ Handshake Routing Activation $\rightarrow$ Đọc số VIN qua UDS 0x22 F190.

---

## TASK 8.4: Triển Khai SOME/IP Service & Service Discovery (SD) (~2h)

### 🎯 Mục Tiêu:
Xây dựng bản tin SOME/IP chuẩn 16 bytes và mô phỏng chu trình Service Discovery tìm dịch vụ camera ADAS.
