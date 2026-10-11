# CHUYÊN ĐỀ 08: Automotive Ethernet, SOME/IP, DoIP & vECU Hands-on Tasks
## KẾ HOẠCH BÀI TẬP THỰC HÀNH CHUYÊN SÂU TẦNG SÂU — 5 Tasks (~12 giờ)

> 📚 **Tài liệu lý thuyết đối chiếu:** [`docs/theory/12_Automotive_Ethernet_SOMEIP_DoIP_Deep_Dive.md`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/docs/theory/12_Automotive_Ethernet_SOMEIP_DoIP_Deep_Dive.md)  
> 🔧 **Mã nguồn gốc đối chiếu thực tế:**  
> • [`as/com/as.infrastructure/communication/Eth/Eth.c`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/com/as.infrastructure/communication/Eth/Eth.c) (MCAL Driver)  
> • [`as/com/as.infrastructure/communication/EthIf/EthIf.c`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/com/as.infrastructure/communication/EthIf/EthIf.c) (Ethernet Interface)  
> • [`as/com/as.infrastructure/communication/SoAd/SoAd.c`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/com/as.infrastructure/communication/SoAd/SoAd.c) (Socket Adaptor)  
> • [`as/com/as.infrastructure/communication/DoIP/DoIP.c`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/com/as.infrastructure/communication/DoIP/DoIP.c) (DoIP ISO 13400 Core)  
> • [`as/com/as.infrastructure/communication/SD/SD.c`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/com/as.infrastructure/communication/SD/SD.c) (SOME/IP Service Discovery)  
> • [`as/com/as.virtual/source/vEcu.cpp`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/com/as.virtual/source/vEcu.cpp) & [`xlLoadlib.cpp`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/com/as.virtual/source/xlLoadlib.cpp) (vECU & Vector XL API)  
> • [`as/com/as.application/common/autosar.arxml`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/com/as.application/common/autosar.arxml#L294-L305)  
> ⏱️ **Tổng thời lượng ước tính:** ~12 giờ  

---

### 🗺️ Bảng Ma Trận Các Bài Tập Thực Hành:

| Mã Task | Tên Bài Tập Thực Hành | Độ Khó | Trọng Tâm Kiến Thức & Source Code |
| :---: | :--- | :---: | :--- |
| **Task 8.1** | **Trace Dòng Chảy Gói Tin Socket Gốc `SOAD_TX` / `SOAD_RX`** | 🟢 Intermediate | `autosar.arxml` $\to$ `Dcm.c` $\to$ `PduR` $\to$ `SoAd.c` $\to$ `TcpIp` $\to$ `Eth.c` |
| **Task 8.2** | **Cấu Hình & Hiện Thực Bảng Ánh Xạ Socket Adaptor (`SoAd_PduRoute`)** | 🟡 Intermediate | Ánh xạ PDU ID tĩnh sang TCP/UDP Socket IP:Port (`SoAd.c`, `SoAd_Internal.h`) |
| **Task 8.3** | **Trace Sequence Chẩn Đoán DoIP (ISO 13400) & Routing Activation** | 🔴 Advanced | Bắt tay TCP Port 13400, Routing Activation `0x0005`/`0x0006`, UDS `0x8001` (`DoIP.c`) |
| **Task 8.4** | **Triển Khai SOME/IP Service Discovery (SD Entries & Options)** | 🔴 Advanced | Phân giải Entries Array (Find/Offer) & IPv4 Endpoint Option (`SD.c`, `SD_Entries.c`) |
| **Task 8.5** | **Thiết Lập Môi Trường Mô Phỏng Virtual ECU (vECU) & Vector XL API** | 🔴 Senior/Lead | Tích hợp vECU Type 3, nạp thư viện `vxlapi.dll` mô phỏng CANoe (`vEcu.cpp`, `xlLoadlib.cpp`) |

---

## TASK 8.1: Trace Dòng Chảy Gói Tin Socket Gốc `SOAD_TX` / `SOAD_RX` (~2h)

### 🎯 Mục Tiêu:
Lần theo mã nguồn C thực tế để vẽ sơ đồ Call Graph chi tiết của dòng chảy gói tin UDS qua mạng Ethernet từ tầng ứng dụng chẩn đoán xuống tầng Driver phần cứng.

### 📂 Tệp Cần Đọc:
1. [`as/com/as.application/common/autosar.arxml`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/com/as.application/common/autosar.arxml#L294-L305):
   * Khai báo PduR Routing Path: Source `Dcm` $\longrightarrow$ Destination `SoAdTp` (PDU: `SOAD_TX_MSG`).
2. [`as/com/as.infrastructure/diagnostic/Dcm/Dcm.c`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/com/as.infrastructure/diagnostic/Dcm/Dcm.c):
   * Tìm hàm `Dcm_ProcessingDone()` kích hoạt việc truyền gói phản hồi UDS qua `PduR_DcmTransmit()`.
3. [`as/com/as.infrastructure/communication/PduR/PduR_Routing.c`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/com/as.infrastructure/communication/PduR/PduR_Routing.c):
   * Phân tích hàm `PduR_DcmTransmit()` chuyển hướng sang `SoAd_Transmit()`.
4. [`as/com/as.infrastructure/communication/SoAd/SoAd.c`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/com/as.infrastructure/communication/SoAd/SoAd.c):
   * Tìm hàm `SoAd_Transmit()` bọc PDU vào Socket Buffer và gọi `TcpIp_Transmit()`.
5. [`as/com/as.infrastructure/communication/Eth/Eth.c`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/com/as.infrastructure/communication/Eth/Eth.c):
   * Phân tích hàm `Eth_Transmit()` đưa frame vào DMA TX Ring Buffer của card mạng.

### 🛠️ Tiêu Chí Đánh Giá Thành Công:
* Vẽ được sơ đồ tuần tự (Sequence Diagram) chính xác tên hàm, đối số truyền vào và số dòng code trong `as`.
* Giải thích được cơ chế Buffer Locking chống Race Condition khi tầng Socket Adaptor truyền bất đồng bộ.

---

## TASK 8.2: Cấu Hình & Hiện Thực Bảng Ánh Xạ Socket Adaptor (`SoAd_PduRoute`) (~2.5h)

### 🎯 Mục Tiêu:
Hiểu rõ kiến trúc bên trong của `SoAd.c`, tự viết bảng cấu hình liên kết PDU ID với địa chỉ IP và Port.

### 📂 Tệp Cần Đọc:
* [`as/com/as.infrastructure/communication/SoAd/SoAd.c`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/com/as.infrastructure/communication/SoAd/SoAd.c)
* [`as/com/as.infrastructure/include/SoAd.h`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/com/as.infrastructure/include/SoAd.h)
* [`as/com/as.infrastructure/include/SoAd_Types.h`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/com/as.infrastructure/include/SoAd_Types.h)

### 💻 Bài Tập Thực Hành:
Viết đoạn mã cấu hình C khởi tạo 2 kết nối mạng trong `SoAd`:
1. **Kết nối DoIP (TCP):** IP `192.168.1.10`, Port `13400`, ánh xạ PDU ID `SOAD_PDU_DOIP_TX = 0`.
2. **Kết nối SOME/IP (UDP):** IP `192.168.1.50`, Port `30490`, ánh xạ PDU ID `SOAD_PDU_SOMEIP_TX = 1`.

```c
/* Code thực hành mẫu: SoAd_Lcfg.c */
#include "SoAd.h"
#include "SoAd_Types.h"

static const SoAd_SocketConnectionType SoAd_Connections[] = {
    {
        .SoAdSocketId = 0,
        .Protocol = SOAD_SOCKET_TCP,
        .RemotePort = 13400,
        .RemoteIpAddress = {192, 168, 1, 10}
    },
    {
        .SoAdSocketId = 1,
        .Protocol = SOAD_SOCKET_UDP,
        .RemotePort = 30490,
        .RemoteIpAddress = {192, 168, 1, 50}
    }
};

/* Cấu hình Route phát tin PDU */
const SoAd_PduRouteType SoAd_PduRoutes[] = {
    {
        .TxPduId = 0, /* SOAD_PDU_DOIP_TX */
        .SocketConnection = &SoAd_Connections[0]
    },
    {
        .TxPduId = 1, /* SOAD_PDU_SOMEIP_TX */
        .SocketConnection = &SoAd_Connections[1]
    }
};
```

### 🛠️ Tiêu Chí Đánh Giá:
* Biên dịch thử nghiệm với target posix: `scons --board=posix`.
* Giải thích được cách hàm `SoAd_IfTransmit()` tra cứu trong `SoAd_PduRoutes` để chọn đúng Socket Connection.

---

## TASK 8.3: Trace Sequence Chẩn Đoán DoIP (ISO 13400) Trong `DoIP.c` (~2.5h)

### 🎯 Mục Tiêu:
Thấu hiểu cơ chế máy trạng thái (State Machine) của DoIP trong [`as/com/as.infrastructure/communication/DoIP/DoIP.c`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/com/as.infrastructure/communication/DoIP/DoIP.c), từ lúc kết nối TCP đến khi thực thi chẩn đoán UDS.

### 📂 Tệp Cần Đọc:
* [`as/com/as.infrastructure/communication/DoIP/DoIP.c`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/com/as.infrastructure/communication/DoIP/DoIP.c) (Xem dòng 40–120 và các hàm xử lý bản tin)

### 🔬 Các Bước Thực Hiện:
1. **Phân tích Header DoIP:**
   * Mở `DoIP.c`, kiểm tra các hằng số:
     * `DOIP_PROTOCOL_VERSION = 2`
     * `DOIP_PLT_ROUTING_ACTIV_REQ = 0x0005`
     * `DOIP_PLT_ROUTING_ACTIV_RES = 0x0006`
     * `DOIP_PLT_DIAGNOSTIC_MSG = 0x8001`
2. **Kịch bản kiểm thử với Python Tester:**
   Viết file script Python [`test_doip_client.py`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/test_doip_client.py) để gửi bản tin DoIP giả lập một Tester cắm cổng Ethernet:

```python
import socket
import struct

# Kết nối TCP đến DoIP Server cổng 13400
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(("127.0.0.1", 13400))

# 1. Gửi Routing Activation Request (Payload Type 0x0005)
# Header: Vers(0x02), InvVers(0xFD), Type(0x0005), Len(0x00000007)
# Payload: SA(0x0E00), ActivationType(0x00), Reserved(0x00000000)
req_activation = struct.pack("!BBHI", 0x02, 0xFD, 0x0005, 7) + struct.pack("!HB4s", 0x0E00, 0x00, b'\x00\x00\x00\x00')
s.sendall(req_activation)
res = s.recv(1024)
print("Routing Activation Response:", res.hex())

# 2. Gửi UDS Diagnostic Message 0x22 F1 90 (Read VIN) qua DoIP (Payload Type 0x8001)
# Header: Vers(0x02), InvVers(0xFD), Type(0x8001), Len(0x00000007)
# Payload: SA(0x0E00), TA(0x1000), UDS(0x22, 0xF1, 0x90)
diag_msg = struct.pack("!BBHI", 0x02, 0xFD, 0x8001, 7) + struct.pack("!HH3s", 0x0E00, 0x1000, b'\x22\xF1\x90')
s.sendall(diag_msg)
res_diag = s.recv(1024)
print("DoIP Diagnostic Response:", res_diag.hex())
```

### 🛠️ Tiêu Chí Đánh Giá:
* Phân tích được các mã lỗi phản hồi NACK trong `DoIP.c` khi gửi sai Header:
  * Thử gửi `InvVers = 0x00` $\implies$ Kiểm tra server trả về `DOIP_E_INCORRECT_PATTERN_FORMAT (0x00)`.
  * Thử gửi `SA = 0xFFFF` $\implies$ Kiểm tra server trả về `DOIP_E_DIAG_INVALID_SA (0x02)`.

---

## TASK 8.4: Triển Khai SOME/IP Service & Service Discovery (SD) (~2.5h)

### 🎯 Mục Tiêu:
Hiểu cách cấu trúc thông điệp SOME/IP-SD (Service Discovery) được định nghĩa và đóng gói trong mã nguồn C của `as`.

### 📂 Tệp Cần Đọc:
* [`as/com/as.infrastructure/communication/SD/SD.c`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/com/as.infrastructure/communication/SD/SD.c)
* [`as/com/as.infrastructure/communication/SD/SD_Entries.c`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/com/as.infrastructure/communication/SD/SD_Entries.c)
* [`as/com/as.infrastructure/communication/SD/SD_Messages.c`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/com/as.infrastructure/communication/SD/SD_Messages.c)

### 🔬 Các Bước Thực Hiện:
1. Đọc tệp `SD_Entries.c`, phân tích cấu trúc phần tử `Entry`:
   * `Type`: `0x00` (FindService), `0x01` (OfferService).
   * `Service ID`: 16-bit nhận dạng dịch vụ (ví dụ: `0x1001` - BCM Door Control).
   * `Instance ID`: 16-bit (ví dụ: `0x0001` - Cửa trước bên lái).
   * `Major Version`, `Minor Version`, `TTL (Time to Live)`.
2. Đọc tệp `SD_Messages.c`, phân tích cách ghép `IPv4 Endpoint Option`:
   * Chứa địa chỉ IP và Port mà dịch vụ đang lắng nghe kết nối.
3. Viết hàm mô phỏng phát bản tin `Sd_ServerService_OfferService`:
   ```c
   Std_ReturnType Mock_Sd_OfferService(uint16 ServiceId, uint16 InstanceId, uint32 IpAddr, uint16 Port) {
       /* 1. Tạo SD Entry Type 0x01 (OfferService) */
       /* 2. Gắn Option Type 0x04 (IPv4 Endpoint) */
       /* 3. Gọi SoAd_Transmit phát UDP Multicast ra 224.0.0.1:30490 */
       return E_OK;
   }
   ```

### 🛠️ Tiêu Chí Đánh Giá:
* Giải thích được 3 giai đoạn của SD State Machine: **Initial Wait Phase $\to$ Repetition Phase $\to$ Main Phase**.
* Trình bày được tại sao thời gian sống `TTL = 0` được sử dụng để thông báo hủy dịch vụ (`StopOfferService`).

---

## TASK 8.5: Thiết Lập Môi Trường Mô Phỏng Virtual ECU & Tích Hợp Vector XL API (~2.5h)

### 🎯 Mục Tiêu:
Thực hành với kiến trúc vECU Type 3 trong [`as/virtual`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/com/as.virtual) để chuẩn bị cho các vị trí tuyển dụng yêu cầu mô phỏng ECU và Vector Toolchain (HCLTech, VinFast, Bosch).

### 📂 Tệp Cần Đọc:
* [`as/com/as.virtual/source/vEcu.cpp`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/com/as.virtual/source/vEcu.cpp)
* [`as/com/as.virtual/source/xlLoadlib.cpp`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/com/as.virtual/source/xlLoadlib.cpp)
* [`as/com/as.virtual/include/vxlapi.h`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/com/as.virtual/include/vxlapi.h)

### 🔬 Các Bước Thực Hiện:
1. Mở `xlLoadlib.cpp`, tìm hiểu các con trỏ hàm API của Vector:
   * `xlGetApplConfig`: Đọc cấu hình Virtual Bus của Vector Hardware Configuration.
   * `xlOpenPort`: Mở kết nối giao tiếp với kênh ảo CANoe Virtual Channel.
   * `xlCanTransmit`: Gửi Frame CAN từ vECU sang phần mềm Vector CANoe.
   * `xlReceive`: Bắt gói tin CAN do CANoe truyền tới vECU.
2. Mở `vEcu.cpp`, tìm hiểu luồng `vEcu_Init()`:
   * Cách vECU tạo luồng chạy song song để duy trì chu kỳ tick hệ thống mà không cần phần cứng timer thật.
3. Viết bản tóm tắt kiến trúc giải thích sự khác biệt giữa:
   * **vECU Type 1:** Mô phỏng thuần logic code (MIL/SIL trên PC).
   * **vECU Type 3:** Mô phỏng toàn bộ ngăn xếp BSW chuẩn AUTOSAR kết hợp Driver ảo hóa kết nối với mạng bus ảo (Vector XL Driver / CANoe).

### 🛠️ Tiêu Chí Đánh Giá:
* Nắm chắc cách vECU kết nối với Vector CANoe để trả lời trôi chảy các câu hỏi kỹ thuật trong các vòng phỏng vấn chuyên sâu.
