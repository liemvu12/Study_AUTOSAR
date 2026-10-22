# CHUYÊN ĐỀ BỔ TRỢ 05: ĐỐI CHIẾU MÔ HÌNH MẠNG 7 TẦNG OSI, 4 TẦNG TCP/IP VÀ KIẾN TRÚC 4 TẦNG AUTOSAR COMSTACK
## (Masterclass: OSI 7-Layer vs TCP/IP 4-Layer vs AUTOSAR Layered Architecture — Signal, I-PDU, N-PDU, L-PDU & Automotive Protocol Mapping)

> 📌 **Vị trí tài liệu:** [`docs/supplementary_knowledge/05_OSI_7_Layers_vs_TCP_IP_And_AUTOSAR_ComStack.md`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/docs/supplementary_knowledge/05_OSI_7_Layers_vs_TCP_IP_And_AUTOSAR_ComStack.md)  
> 🎯 **Đối tượng mục tiêu:** Kỹ sư nhúng ô tô (Automotive Embedded Engineers), kỹ sư phần mềm BSW ComStack, và sinh viên/học viên chuyển từ mạng máy tính truyền thống sang kiến trúc tiêu chuẩn AUTOSAR Classic.  
> 🔧 **Mã nguồn thực nghiệm đối chiếu trong dự án Study_AUTOSAR:**
> - Driver MCAL CAN tầng 1 & 2: [`as/com/as.infrastructure/communication/Can/Can.c`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/com/as.infrastructure/communication/Can/Can.c) & [`as/com/as.infrastructure/communication/Can/Can.h`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/com/as.infrastructure/communication/Can/Can.h)
> - Tầng Data Link Interface (CanIf): [`as/com/as.infrastructure/communication/CanIf/CanIf.c`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/com/as.infrastructure/communication/CanIf/CanIf.c) & [`as/com/as.infrastructure/communication/CanIf/CanIf.h`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/com/as.infrastructure/communication/CanIf/CanIf.h)
> - Tầng Transport Protocol (CanTp): [`as/com/as.infrastructure/communication/CanTp/CanTp.c`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/com/as.infrastructure/communication/CanTp/CanTp.c) & [`as/com/as.infrastructure/communication/CanTp/CanTp.h`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/com/as.infrastructure/communication/CanTp/CanTp.h)
> - Tầng PDU Router (PduR): [`as/com/as.infrastructure/communication/PduR/PduR.c`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/com/as.infrastructure/communication/PduR/PduR.c) & [`as/com/as.infrastructure/communication/PduR/PduR.h`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/com/as.infrastructure/communication/PduR/PduR.h)
> - Tầng Interaction/COM (Com): [`as/com/as.infrastructure/communication/Com/Com.c`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/com/as.infrastructure/communication/Com/Com.c) & [`as/com/as.infrastructure/communication/Com/Com.h`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/com/as.infrastructure/communication/Com/Com.h)
> - File cấu hình hệ thống ARXML: [`as/com/as.application/common/autosar.arxml`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/com/as.application/common/autosar.arxml)

---

## 📑 MỤC LỤC CHI TIẾT

1. [Bản Chất Cốt Lõi: Tại Sao Phải Phân Tầng Trong Mạng Ô Tô?](#1-bản-chất-cốt-lõi-tại-sao-phải-phân-tầng-trong-mạng-ô-tô)
2. [Mổ Xẻ Mô Hình 7 Tầng OSI (ISO/IEC 7498-1) Trong Bối Cảnh Ô Tô](#2-mổ-xẻ-mô-hình-7-tầng-osi-isoiec-7498-1-trong-bối-cảnh-ô-tô)
   - [2.1. Tầng 7: Application Layer (Tầng Ứng Dụng)](#21-tầng-7-application-layer-tầng-ứng-dụng)
   - [2.2. Tầng 6: Presentation Layer (Tầng Trình Diễn)](#22-tầng-6-presentation-layer-tầng-trình-diễn)
   - [2.3. Tầng 5: Session Layer (Tầng Phiên)](#23-tầng-5-session-layer-tầng-phiên)
   - [2.4. Tầng 4: Transport Layer (Tầng Vận Chuyển)](#24-tầng-4-transport-layer-tầng-vận-chuyển)
   - [2.5. Tầng 3: Network Layer (Tầng Mạng)](#25-tầng-3-network-layer-tầng-mạng)
   - [2.6. Tầng 2: Data Link Layer (Tầng Liên Kết Dữ Liệu)](#26-tầng-2-data-link-layer-tầng-liên-kết-dữ-liệu)
   - [2.7. Tầng 1: Physical Layer (Tầng Vật Lý)](#27-tầng-1-physical-layer-tầng-vật-lý)
3. [Mô Hình 4 Tầng Thực Chiến (TCP/IP Model) & Automotive Ethernet](#3-mô-hình-4-tầng-thực-chiến-tcpip-model--automotive-ethernet)
4. [Kiến Trúc 4 Tầng Tiêu Chuẩn Của Toàn Bộ Hệ Thống AUTOSAR](#4-kiến-trúc-4-tầng-tiêu-chuẩn-của-toàn-bộ-hệ-thống-autosar)
5. [Giải Mã Các Khái Niệm Dữ Liệu: Signal, Signal Group, I-PDU, N-PDU, L-PDU](#5-giải-mã-các-khái-niệm-dữ-liệu-signal-signal-group-i-pdu-n-pdu-l-pdu)
   - [5.1. Cơ Chế Đóng Gói Phân Cấp: SDU + PCI = PDU](#51-cơ-chế-đóng-gói-phân-cấp-sdu--pci--pdu)
   - [5.2. Signal vs Signal Group: Bản Chất Vấn Đề Tính Nhất Quán Nguyên Tử (Atomic Consistency)](#52-signal-vs-signal-group-bản-chất-vấn-đề-tính-nhất-quán-nguyên-tử-atomic-consistency)
   - [5.3. I-PDU, N-PDU, L-PDU: Nguồn Gốc Tên Gọi & Nhiệm Vụ](#53-i-pdu-n-pdu-l-pdu-nguồn-gốc-tên-gọi--nhiệm-vụ)
6. [Bảng Ma Trận Đối Chiếu Toàn Diện 3 Chiều](#6-bảng-ma-trận-đối-chiếu-toàn-diện-3-chiều)
7. [Khảo Sát Thực Tế Mã Nguồn Trong Dự Án Study_AUTOSAR](#7-khảo-sát-thực-tế-mã-nguồn-trong-dự-án-study_autosar)
8. [Bộ Câu Hỏi Phỏng Vấn Chuyên Sâu Dành Cho Kỹ Sư Automotive Architect](#8-bộ-câu-hỏi-phỏng-vấn-chuyên-sâu-dành-cho-kỹ-sư-automotive-architect)

---

## 1. Bản Chất Cốt Lõi: Tại Sao Phải Phân Tầng Trong Mạng Ô Tô?

Trong các đồ án sinh viên hoặc mạch vi điều khiển đơn giản (Arduino, STM32 bare-metal), người lập trình thường gom tất cả vào một: đọc giá trị cảm biến $\to$ ép kiểu byte $\to$ nhét thẳng vào thanh ghi CAN Mailbox $\to$ phát ra dây.

Cách làm này sẽ **sụp đổ hoàn toàn** khi ứng dụng vào một chiếc xe hơi hiện đại có hơn 100 hộp ECU:
1. **Sự bùng nổ chủng loại bus:** Trên cùng một chiếc xe, có tới 4-5 loại mạng khác nhau cùng tồn tại: **CAN Classic** (500 kbps), **CAN-FD** (2-5 Mbps), **LIN** (20 kbps cho gạt nước, gương chiếu hậu), **FlexRay** (10 Mbps cho hệ thống lái/khung gầm), và **Automotive Ethernet** (100 Mbps - 1 Gbps cho ADAS, Camera, Radar, Infotainment).
2. **Yêu cầu độc lập phần cứng (Hardware Decoupling):** Kỹ sư viết thuật toán điều khiển bàn đạp ga (Software Component — SWC) không được phép phụ thuộc vào việc tín hiệu ga sẽ bay qua dây CAN hay dây Ethernet.
3. **Bài toán phân mảnh dữ liệu (Segmentation):** Khung CAN Classic chỉ chứa tối đa 8 byte dữ liệu. Nhưng gói tin chẩn đoán UDS (ISO 14229) hoặc bản tin nạp phần mềm firmware (OTA Flashing) có thể dài tới 4095 bytes hoặc hàng Megabyte. Cần có một tầng trung gian đứng ra băm nhỏ gói tin và ghép lại mà ứng dụng bên trên không hề hay biết.

👉 **Mô hình phân tầng (Layering Model)** chính là chìa khóa vàng: Mỗi tầng chỉ tập trung vào một nhiệm vụ duy nhất, cung cấp dịch vụ cho tầng trên và nhận dịch vụ từ tầng dưới thông qua các chuẩn giao tiếp trừu tượng.

---

## 2. Mổ Xẻ Mô Hình 7 Tầng OSI (ISO/IEC 7498-1) Trong Bối Cảnh Ô Tô

Mô hình **OSI (Open Systems Interconnection)** gồm 7 tầng lý thuyết được Tổ chức Tiêu chuẩn hóa Quốc tế (ISO) ban hành năm 1984. Dưới đây là phân tích chi tiết từng tầng và sự tương thích của nó trong hệ sinh thái xe hơi:

```text
 ◄────────────────────── MÔ HÌNH 7 TẦNG THAM CHIẾU OSI ──────────────────────►
┌───────────────┬─────────────────────────────────────────────────────────────┐
│ TẦNG OSI      │ VAI TRÒ & MODULE TƯƠNG ỨNG TRONG HỆ THỐNG NHÚNG Ô TÔ        │
├───────────────┼─────────────────────────────────────────────────────────────┤
│ 7. APPLICATION│ Ứng dụng SWC: Thuật toán phanh ABS, Tính toán mức tiêu thụ  │
│ 6. PRESENTATION│ COM: Chuẩn hóa Little/Big Endian (Intel/Motorola), Scaling │
│ 5. SESSION    │ COM / Dcm: Quản lý chu kỳ truyền (Periodic/Event), Session  │
│ 4. TRANSPORT  │ CanTp / DoIP: Phân mảnh gói tin > 8B, Kiểm soát luồng FC    │
│ 3. NETWORK    │ PduR: Định tuyến I-PDU giữa các bus CAN, LIN, Ethernet     │
│ 2. DATA LINK  │ CanIf + MCAL Can: Đóng khung CAN ID, DLC, CRC, Mailbox FIFO │
│ 1. PHYSICAL   │ CAN Transceiver + Cặp dây xoắn CAN_H/CAN_L: Mức điện áp vi sai│
└───────────────┴─────────────────────────────────────────────────────────────┘
```

### 2.1. Tầng 7: Application Layer (Tầng Ứng Dụng)
- **Đơn vị dữ liệu:** **Signal (Tín hiệu đơn lẻ)** hoặc **Signal Group (Cụm tín hiệu)**.
- **Nhiệm vụ:** Chứa logic nghiệp vụ thuần túy của xe. Tại đây không hề có khái niệm bit, byte hay khung truyền CAN ID.
- **Ví dụ trong ô tô:** Biến `VehicleSpeed` ($85\text{ km/h}$), `EngineSpeed` ($3200\text{ RPM}$), `DoorStatus` (`DOOR_OPEN / DOOR_CLOSED`).

### 2.2. Tầng 6: Presentation Layer (Tầng Trình Diễn)
- **Nhiệm vụ:** Chuyển đổi định dạng dữ liệu (Data Representation), mã hóa/giải mã, và xử lý trật tự byte (Endianness).
- **Trong AUTOSAR:** Do module **COM (Communication)** đảm trách:
  - Chuyển đổi định dạng số thực sang số nguyên thông qua công thức tỉ lệ: $\text{Physical Value} = \text{Raw Value} \times \text{Factor} + \text{Offset}$.
  - Xử lý xung đột kiến trúc bộ nhớ: Vi điều khiển ARM/Tricore lưu trữ dạng **Little-Endian (Intel)**, nhưng file ma trận mạng CAN có thể yêu cầu đóng gói theo chuẩn **Big-Endian (Motorola)**. COM thực hiện phép biến đổi bit-shifting và bit-masking này.

### 2.3. Tầng 5: Session Layer (Tầng Phiên)
- **Đơn vị dữ liệu:** **I-PDU (Interaction Layer PDU - Protocol Data Unit)**.
- **Nhiệm vụ:** Thiết lập, duy trì và đồng bộ hóa các phiên giao tiếp.
- **Trong AUTOSAR:** 
  - Module **COM** quản lý chế độ truyền: **Periodic** (chu kỳ $10\text{ms}, 20\text{ms}$ gửi 1 lần), **Direct / Event** (gửi ngay khi có sự kiện bàn đạp phanh đạp xuống), hoặc **Mixed**.
  - Kiểm soát thời hạn truyền nhận (Deadline Monitoring): Nếu sau $50\text{ms}$ không nhận được I-PDU vận tốc xe, COM báo timeout lên RTE/SWC.
  - Module **Dcm (Diagnostic Communication Manager)** quản lý các Diagnostic Session trong UDS: Default Session ($0x01$), Programming Session ($0x02$), Extended Session ($0x03$).

### 2.4. Tầng 4: Transport Layer (Tầng Vận Chuyển)
- **Đơn vị dữ liệu:** **N-PDU (Network/Transport PDU)**.
- **Nhiệm vụ:** Đảm bảo truyền dữ liệu tin cậy giữa hai đầu cuối (End-to-End), kiểm soát luồng (Flow Control), cắt nhỏ (Segmentation) và ráp nối (Reassembly) các khối dữ liệu vượt quá kích thước vật lý của 1 khung truyền.
- **Module AUTOSAR:**
  - **CanTp (CAN Transport Layer — ISO 15765-2):** Khi bản tin UDS dài 50 bytes, CanTp chia nhỏ thành: 1 khung First Frame (FF), các khung Consecutive Frame (CF) và nhận khung Flow Control (FC) để điều tiết tốc độ phát với các tham số Block Size (BS) và Separation Time ($ST_{\min}$).
  - Trong mạng Ethernet: Tương ứng với giao thức **TCP** (tin cậy, có ACK) hoặc **UDP** (thời gian thực, nhanh).

### 2.5. Tầng 3: Network Layer (Tầng Mạng)
- **Nhiệm vụ:** Định tuyến đường đi (Routing) cho gói tin xuyên qua các mạng khác nhau.
- **Module AUTOSAR:**
  - **PduR (PDU Router):** Đóng vai trò như một Router/Gateway trung tâm. PduR nhận một I-PDU từ CanIf của mạng CAN 1 (Powertrain) và chuyển tiếp nguyên khối sang CanIf của mạng CAN 2 (Body) hoặc sang LinIf mà **không cần giải nén từng Signal bên trong**.
  - Trong Automotive Ethernet: Tương ứng với giao thức **IPv4 / IPv6**.

### 2.6. Tầng 2: Data Link Layer (Tầng Liên Kết Dữ Liệu)
- **Đơn vị dữ liệu:** **L-PDU (Data Link Layer PDU)**.
- **Nhiệm vụ:** Đóng khung dữ liệu (Framing), phân xử tranh chấp bus (Arbitration), kiểm tra tính toàn vẹn (CRC-15), phản hồi ACK, phát hiện lỗi và quản lý lỗi (Fault Confinement TEC/REC).
- **Module AUTOSAR:**
  - **CanIf (CAN Interface):** Trừu tượng hóa phần cứng, quản lý quan hệ ánh xạ giữa `CanTxPduId` và phần cứng Mailbox.
  - **MCAL Can Driver:** Lập trình trực tiếp các thanh ghi CAN Controller (ví dụ `CAN_TIxR`, `CAN_TDTxR`), gắn CAN ID (11-bit hoặc 29-bit), DLC và kích hoạt truyền/nhận.

### 2.7. Tầng 1: Physical Layer (Tầng Vật Lý)
- **Đơn vị dữ liệu:** **Bits on Wire (Dòng bit điện áp)**.
- **Nhiệm vụ:** Chuyển đổi các bit nhị phân $0$ và $1$ thành tín hiệu điện thực tế lan truyền trên môi trường truyền dẫn vật lý.
- **Phần cứng:**
  - **CAN Transceiver:** Chip lái điện áp vi sai (CAN_H, CAN_L).
  - **Môi trường vật lý:** Cặp dây đồng xoắn (Twisted Pair) với hai trở kháng đầu cuối $120\Omega$, tốc độ truyền sóng khoảng $5\text{ ns/m}$.

---

## 3. Mô Hình 4 Tầng Thực Chiến (TCP/IP Model) & Automotive Ethernet

Trong thực tế triển khai công nghệ thông tin và mạng trên ô tô hiện đại, mô hình 7 tầng OSI thường được tinh gọn thành **Mô hình 4 tầng TCP/IP (Internet Reference Model)**:

```text
 7 TẦNG OSI               4 TẦNG TCP/IP              MÔ TẢ TRONG MẠNG AUTOMOTIVE ETHERNET
┌─────────────────┐      ┌─────────────────┐      ┌──────────────────────────────────────────────┐
│ 7. Application  │ ──┐  │                 │      │ Ứng dụng chẩn đoán, Camera ADAS, Infotainment │
├─────────────────┤   ├──┤ 1. APPLICATION  │ ───► ├──────────────────────────────────────────────┤
│ 6. Presentation │   │  │                 │      │ Giao thức SOME/IP (Scalable Service-Oriented) │
├─────────────────┤   │  │                 │      │ Giao thức DoIP (Diagnostics over IP)         │
│ 5. Session      │ ──┘  ├─────────────────┤      ├──────────────────────────────────────────────┤
├─────────────────┤      │ 2. TRANSPORT    │ ───► │ TCP (cho DoIP/Flashing)                      │
│ 4. Transport    │ ───► │                 │      │ UDP (cho SOME/IP Event, Camera Streaming)    │
├─────────────────┤      ├─────────────────┤      ├──────────────────────────────────────────────┤
│ 3. Network      │ ───► │ 3. INTERNET     │ ───► │ IPv4 / IPv6 Routing                          │
├─────────────────┤      ├─────────────────┤      ├──────────────────────────────────────────────┤
│ 2. Data Link    │ ──┐  │ 4. NETWORK      │ ───► │ IEEE 802.3 Ethernet MAC, VLAN (IEEE 802.1Q)  │
├─────────────────┤   ├──┤    ACCESS       │      ├──────────────────────────────────────────────┤
│ 1. Physical     │ ──┘  │    (LINK LAYER) │ ───► │ 100BASE-T1 / 1000BASE-T1 (BroadR-Reach Cáp 1 đôi)│
└─────────────────┘      └─────────────────┘      └──────────────────────────────────────────────┘
```

### Tại Sao Mô Hình 4 Tầng Lại Thống Trị Xe Tự Hành & Xe Điện Hiện Đại?
Khi xe hơi chuyển dịch sang kiến trúc điện-điện tử tập trung (Centralized E/E Architecture & Zonal Controller), các luồng dữ liệu khổng lồ từ Camera Lidar đòi hỏi băng thông Gigabits. Mạng **Automotive Ethernet** được tích hợp thẳng mô hình 4 tầng TCP/IP vào ComStack:
- **Tầng Application:** Module **DoIP** (Diagnostics over IP — ISO 13400) thay thế CanTp để nạp phần mềm với tốc độ nhanh gấp 100 lần CAN.
- **Tầng Transport:** Sử dụng trực tiếp **SoAd (Socket Adaptor)** kết nối với **TcpIp Stack** thay vì CanTp.

---

## 4. Kiến Trúc 4 Tầng Tiêu Chuẩn Của Toàn Bộ Hệ Thống AUTOSAR

Cần phân biệt rõ: **Mô hình mạng 4 tầng TCP/IP** là mô hình truyền thông, còn **Kiến trúc 4 tầng AUTOSAR (AUTOSAR Layered Software Architecture)** là kiến trúc phần mềm nhúng tổng thể của một hộp ECU:

```text
 ◄────────────────────── KIẾN TRÚC 4 TẦNG AUTOSAR CLASSIC ──────────────────────►
┌───────────────────────────────────────────────────────────────────────────────┐
│ 1. APPLICATION LAYER (SWC)                                                    │
│    - Các thành phần phần mềm ứng dụng độc lập: EngineControl, DoorControl...  │
│    - Giao tiếp thuần túy bằng [SIGNAL] thông qua các Port/Interface (R-Port, P-Port)│
└──────────────────────────────────────┬────────────────────────────────────────┘
                                       │ Rte_Write() / Rte_Read()
┌──────────────────────────────────────▼────────────────────────────────────────┐
│ 2. RUNTIME ENVIRONMENT (RTE)                                                  │
│    - "Hệ tuần hoàn" trung gian (Virtual Functional Bus - VFB)                 │
│    - Chuyển lời gọi hàm ứng dụng thành lời gọi dịch vụ BSW Com_SendSignal()   │
└──────────────────────────────────────┬────────────────────────────────────────┘
                                       │ Com_SendSignal()
┌──────────────────────────────────────▼────────────────────────────────────────┐
│ 3. BASIC SOFTWARE (BSW)                                                       │
│    ┌─────────────────────────────────────────────────────────────────────┐    │
│    │ 3.1. SERVICES LAYER: COM (Đóng gói I-PDU), PduR (Định tuyến I-PDU)   │    │
│    ├─────────────────────────────────────────────────────────────────────┤    │
│    │ 3.2. ECU ABSTRACTION LAYER: CanIf (Đóng L-PDU), CanTp (Tạo N-PDU)    │    │
│    ├─────────────────────────────────────────────────────────────────────┤    │
│    │ 3.3. MCAL LAYER: Can Driver (Ghi thanh ghi Mailbox phần cứng)       │    │
│    └─────────────────────────────────────────────────────────────────────┘    │
└──────────────────────────────────────┬────────────────────────────────────────┘
                                       │ Lái chân phần cứng vi điều khiển
┌──────────────────────────────────────▼────────────────────────────────────────┐
│ 4. MICROCONTROLLER & HARDWARE                                                 │
│    - Vi điều khiển (Silicon Core, CAN Controller Mailboxes, FIFOs)             │
│    - CAN Transceiver & Cáp vật lý: Bắn dòng bit [BITS ON WIRE]                │
└───────────────────────────────────────────────────────────────────────────────┘
```

---

## 5. Giải Mã Các Khái Niệm Dữ Liệu: Signal, Signal Group, I-PDU, N-PDU, L-PDU

### 5.1. Cơ Chế Đóng Gói Phân Cấp: SDU + PCI = PDU
Trong khoa học mạng truyền thông:
$$\mathbf{PDU = SDU + PCI}$$
- **SDU (Service Data Unit):** Khối dữ liệu nguyên bản từ tầng trên chuyển giao xuống.
- **PCI (Protocol Control Information):** Tiêu đề (Header) mang thông tin điều khiển do tầng hiện tại đóng gói thêm vào.
- **PDU (Protocol Data Unit):** Sản phẩm hoàn chỉnh sẵn sàng bàn giao cho tầng tiếp theo.

```text
[SWC]       Signal A, Signal B, Signal C (Dữ liệu nghiệp vụ thuần túy)
                  │
                  ▼
[COM]       I-SDU = {Signal A, B, C}
            COM gom các Signal vào mảng byte + Thông số chu kỳ
            ──► Tạo ra: I-PDU (Interaction Layer PDU)
                  │
                  ▼
[CanTp]     N-SDU = I-PDU (nếu kích thước > 8 bytes)
            CanTp thêm Header N-PCI (First Frame 0x10, Consecutive 0x21...)
            ──► Tạo ra: N-PDU (Network Layer PDU)
                  │
                  ▼
[CanIf]     L-SDU = N-PDU (hoặc I-PDU trực tiếp nếu <= 8 bytes)
            Can Driver thêm L-PCI (CAN ID: 11b/29b, trường DLC: 4b)
            ──► Tạo ra: L-PDU (Data Link Layer PDU)
                  │
                  ▼
[Transceiver] Thêm SOF, CRC-15, CRC Del, ACK, EOF
            ──► Biến thành Dòng Bit Điện Áp Vi Sai (Bits on Wire)
```

---

### 5.2. Signal vs Signal Group: Bản Chất Vấn Đề Tính Nhất Quán Nguyên Tử (Atomic Consistency)

#### A. Signal (Tín Hiệu Đơn)
- Đại diện cho một giá trị vô hướng (scalar).
- Cập nhật độc lập: Gọi hàm `Rte_Write_VehicleSpeed(85)` sẽ ghi thẳng giá trị vào bộ đệm của Signal trong COM.

#### B. Signal Group (Cụm Tín Hiệu Nhất Quán)
- **Hiểm họa kỹ thuật khi không dùng Signal Group:**  
  Xét hệ thống chống lật xe (ESC) cần đo gia tốc 3 chiều: $\text{Accel\_X}, \text{Accel\_Y}, \text{Accel\_Z}$.  
  Nếu đọc 3 Signal độc lập:
  1. Task điều khiển đọc $\text{Accel\_X}$ tại thời điểm $t_0$.
  2. Một ngắt ISR ưu tiên cao chen ngang, nhận khung CAN mới và cập nhật bộ đệm dữ liệu sang thời điểm $t_1$.
  3. Task điều khiển tiếp tục chạy, đọc $\text{Accel\_Y}$ và $\text{Accel\_Z}$ tại thời điểm $t_1$.  
  $\implies$ **Dữ liệu bị cọc cạch (Data Inconsistency)**: Trục $X$ đo ở $t_0$, nhưng trục $Y, Z$ đo ở $t_1$. Xe tính toán sai vector gia tốc và có thể kích hoạt phanh nhầm!
- **Giải pháp Shadow Buffer trong AUTOSAR:**
  - COM cung cấp bộ đệm phụ (Shadow Buffer).
  - Ứng dụng ghi từng trục vào bộ đệm bóng qua hàm `Com_UpdateShadowSignal()`.
  - Khi gọi hàm `Com_SendSignalGroup()`, toàn bộ dữ liệu từ Shadow Buffer được copy sang I-PDU **như một khối nguyên tử duy nhất (Atomic Operation)** dưới cơ chế khóa ngắt ngắn hạn. Đảm bảo toàn bộ nhóm tín hiệu luôn thuộc về cùng một khoảnh khắc thời gian đo.

---

### 5.3. I-PDU, N-PDU, L-PDU: Nguồn Gốc Tên Gọi & Nhiệm Vụ

| Ký Hiệu | Tên Đầy Đủ | Tầng Phụ Trách | Ý Nghĩa Chức Năng |
| :---: | :--- | :---: | :--- |
| **I-PDU** | **I**nteraction Layer PDU | **COM Module** | Khối dữ liệu trung gian tương tác giữa ứng dụng và mạng. Nó độc lập hoàn toàn với phần cứng bus (CAN, LIN hay FlexRay). |
| **N-PDU** | **N**etwork Layer PDU | **CanTp / FrTp / DoIP** | Gói tin của tầng vận chuyển mạng. Đã được băm nhỏ hoặc đính thêm byte điều khiển phân mảnh (ISO 15765-2). |
| **L-PDU** | Data **L**ink Layer PDU | **CanIf / MCAL Can** | Gói dữ liệu tầng liên kết phần cứng. Đã được gán định danh phần cứng (CAN ID), độ dài DLC và sẵn sàng nạp vào Mailbox truyền đi. |

---

## 6. Bảng Ma Trận Đối Chiếu Toàn Diện 3 Chiều

Dưới đây là bảng ma trận chuẩn hóa đối chiếu xuyên suốt giữa **Mô hình 7 Tầng OSI**, **Mô hình 4 Tầng Mạng**, và **Kiến Trúc 4 Tầng AUTOSAR**:

| Tầng Trong 7 Tầng OSI | Tầng Trong 4 Tầng Mạng | Tầng Trong 4 Tầng AUTOSAR | Đơn Vị Dữ Liệu | Module Xử Lý Trong ComStack | Chức Năng Cốt Lõi |
| :--- | :--- | :--- | :---: | :--- | :--- |
| **7. Application** | **1. Application** | **1. Application Layer (SWC)** | **Signal** / **Signal Group** | Application SWC | Chạy thuật toán điều khiển xe (ESP, ABS, BMS, ADAS). |
| **6. Presentation** | **1. Application** | **2. Runtime Environment (RTE)** | **Signal Group Buffer** | RTE | Phân phối tín hiệu, quản lý Shadow Buffer. |
| **5. Session** | **1. Application** | **3. BSW (Services Layer)** | **I-PDU** | **COM Module** | Đóng gói Signal vào mảng byte, chuyển đổi Endianness, chu kỳ truyền. |
| **4. Transport** | **2. Transport** | **3. BSW (Transport Layer)** | **N-PDU** | **CanTp** (ISO 15765-2) | Phân mảnh (Segmentation), ghép mảnh, kiểm soát luồng Flow Control. |
| **3. Network** | **3. Internet / Network** | **3. BSW (Services Layer)** | **I-PDU / N-PDU** | **PduR (PDU Router)** | Định tuyến gói tin liên bus (CAN $\leftrightarrow$ LIN $\leftrightarrow$ Ethernet Gateway). |
| **2. Data Link** | **4. Network Access** | **3. BSW (ECU Abstraction & MCAL)**| **L-PDU** | **CanIf** & **MCAL Can Driver** | Gán CAN ID, DLC, kiểm tra CRC-15, phân xử bitwise arbitration, Mailbox FIFO. |
| **1. Physical** | **4. Network Access** | **4. Microcontroller & Hardware** | **Bits on Wire** | **CAN Transceiver** & Cáp vi sai | Kéo mức điện áp $V_{\text{diff}}$ ($3.5\text{V} / 1.5\text{V}$), đồng bộ nhịp bit timing. |

---

## 7. Khảo Sát Thực Tế Mã Nguồn Trong Dự Án Study_AUTOSAR

Trong dự án [`Study_AUTOSAR-main`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main), toàn bộ dòng chảy dữ liệu này được thể hiện rõ ràng qua các cấu trúc dữ liệu chuẩn C:

### 1. Tại Tầng COM (`I-PDU` & `Signal Packing`):
Xem file [`as/com/as.infrastructure/communication/Com/Com.c`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/com/as.infrastructure/communication/Com/Com.c):
Hàm `Com_SendSignal()` trích xuất từng bit của biến nghiệp vụ và ghi đè vào mảng byte `Com_Arc_IPduBuffer`:
```c
/* Trích đoạn tư duy xử lý trong Com.c */
uint8* ipduPtr = Com_Arc_Config->ComIPdu[ipduId].ComIPduDataPtr;
/* Đóng gói giá trị signal vào đúng StartBit và BitSize của I-PDU */
Com_PackSignal(signalId, SignalDataPtr, ipduPtr);
```

### 2. Tại Tầng PduR (`I-PDU Routing`):
Xem file [`as/com/as.infrastructure/communication/PduR/PduR.c`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/com/as.infrastructure/communication/PduR/PduR.c):
PduR nhận `PduInfoType` từ COM và chuyển tiếp thẳng sang CanIf mà không hề giải nén dữ liệu:
```c
Std_ReturnType PduR_ComTransmit(PduIdType ComTxPduId, const PduInfoType *PduInfoPtr) {
    /* Tìm kiếm bảng định tuyến PduR_RoutingTable */
    PduIdType TargetPduId = PduR_Config->RoutingTable[ComTxPduId].TargetPduId;
    return CanIf_Transmit(TargetPduId, PduInfoPtr); /* Bàn giao nguyên khối I-PDU xuống tầng dưới */
}
```

### 3. Tại Tầng CanIf & Can Driver (`L-PDU` & `Mailbox`):
Xem file [`as/com/as.infrastructure/communication/CanIf/CanIf.c`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/com/as.infrastructure/communication/CanIf/CanIf.c) & [`Can.c`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/com/as.infrastructure/communication/Can/Can.c):
CanIf gán thông tin `Can_PduType` (chứa CAN ID, SduLength) và gọi xuống Driver MCAL để ghi vào thanh ghi phần cứng Mailbox:
```c
Can_PduType canPdu;
canPdu.id = CanIf_Config->TxPduConfig[CanTxPduId].CanId; /* CAN ID: 0x123 */
canPdu.length = PduInfoPtr->SduLength;                   /* DLC: 8 */
canPdu.sdu = PduInfoPtr->SduDataPtr;                     /* Trỏ tới mảng dữ liệu */
Can_Write(Hth, &canPdu);                                 /* Nạp vào thanh ghi phần cứng */
```

---

## 8. Bộ Câu Hỏi Phỏng Vấn Chuyên Sâu Dành Cho Kỹ Sư Automotive Architect

#### Câu 1: Tại sao AUTOSAR lại phân tách I-PDU và L-PDU mà không dùng chung một định nghĩa PDU?
*Gợi ý trả lời:*
I-PDU thuộc tầng Interaction (Services Layer), hoàn toàn độc lập với phần cứng mạng vi sai bên dưới. Một I-PDU có thể được định tuyến truyền qua CAN, LIN, hoặc FlexRay mà không bị thay đổi định dạng. L-PDU thuộc tầng Data Link (ECU Abstraction/MCAL), bị ràng buộc trực tiếp bởi đặc tính vật lý của mạng (ví dụ CAN L-PDU mang CAN ID 11-bit/29-bit và Mailbox handle HTH; trong khi LIN L-PDU mang LIN Frame ID và PID). Sự phân tách này giúp đạt được nguyên lý **Bus Independence (Độc lập bus truyền thông)**.

#### Câu 2: Signal Group giải quyết vấn đề gì mà Signal đơn lẻ không giải quyết được?
*Gợi ý trả lời:*
Signal Group giải quyết triệt để bài toán **Tính toàn vẹn nhất quán dữ liệu nguyên tử (Atomic Data Consistency)** giữa các tín hiệu có quan hệ ràng buộc logic mật thiết (ví dụ: Tọa độ 3 trục $X, Y, Z$ của cảm biến gia tốc, hoặc Vận tốc bánh xe kết hợp cờ phanh ABS). Nhờ cơ chế **Shadow Buffer**, việc cập nhật nhóm tín hiệu diễn ra như một giao dịch nguyên tử, loại trừ rủi ro bị ngắt (ISR/Preemption) làm xáo trộn các giá trị đo ở các thời điểm lấy mẫu khác nhau.

#### Câu 3: Khi nào dữ liệu từ COM đi qua CanTp, khi nào đi thẳng xuống CanIf?
*Gợi ý trả lời:*
- Dữ liệu đi thẳng từ COM $\to$ PduR $\to$ CanIf khi kích thước I-PDU nhỏ hơn hoặc bằng tải trọng tối đa của một khung truyền vật lý (ví dụ: $\le 8$ bytes đối với CAN Classic, hoặc $\le 64$ bytes đối với CAN-FD). Đây là luồng truyền thông tín hiệu điều khiển thời gian thực định kỳ thông thường.
- Dữ liệu phải đi qua CanTp khi kích thước vượt quá giới hạn khung vật lý (ví dụ bản tin chẩn đoán UDS từ module DCM dài từ hàng chục đến hàng ngàn bytes). Lúc này, CanTp bắt buộc phải can thiệp để thực hiện giao thức phân mảnh đa khung (Multi-frame segmentation) theo chuẩn ISO 15765-2.
