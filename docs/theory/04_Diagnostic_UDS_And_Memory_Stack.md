# Chuyên Đề 04: Diagnostic Stack (UDS ISO 14229, DCM, DEM) & Memory Stack (NvM, MemIf, Fee) Masterclass
## Masterclass Phân Tích Chuyên Sâu Giao Thức Chẩn Đoán UDS, Hệ Thống Quản Lý Mã Lỗi DEM/DCM và Ngăn Xếp Lưu Trữ Bộ Nhớ Phi Bốc Hơi NvM/MemIf/Fee

> **Ngôn ngữ:** Tiếng Việt Kỹ Nghệ Chuẩn Mực  
> **Cấp độ:** Universal Learning Resource (Từ Newbie đến Expert)
> **Tiêu chuẩn tham chiếu:** ISO 14229-1 (UDS), ISO 15031 (OBD), AUTOSAR DCM SWS, AUTOSAR DEM SWS, AUTOSAR NvM SWS, AUTOSAR Fee SWS  
> **Mã nguồn đối chiếu thực tế:** Kho mã nguồn [Study_AUTOSAR-main/as/](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as) (`com/as.infrastructure/diagnostic/`, `com/as.infrastructure/memory/`)  

---

## 📖 Bảng Thuật Ngữ (Glossary) Bắt Buộc Cần Nắm

*   **UDS** (*Unified Diagnostic Services - ISO 14229*): Giao thức chẩn đoán hợp nhất tiêu chuẩn toàn cầu được sử dụng hầu hết trên các phương tiện hiện nay.
*   **DTC** (*Diagnostic Trouble Code*): Mã lỗi chẩn đoán hư hỏng phần cứng/cảm biến/mạng. Giúp kỹ thuật viên nhận diện nhanh nguyên nhân.
*   **DID** (*Data Identifier*): Mã định danh dữ liệu 2-byte dùng để đọc/ghi thông số từ ECU, ví dụ DID 0xF190 để lấy số VIN.
*   **NRC** (*Negative Response Code*): Mã phản hồi âm khi yêu cầu UDS không hợp lệ hoặc không thể thực thi (VD: 0x13, 0x33, 0x78).
*   **Freeze Frame**: Khung dữ liệu đóng băng, lưu lại trạng thái các cảm biến tại khoảnh khắc xảy ra lỗi, cực kỳ hữu ích để tái hiện sự kiện.
*   **DCM** (*Diagnostic Communication Manager*): Module quản lý giao tiếp chẩn đoán, đóng vai trò định tuyến các tin nhắn UDS tới ứng dụng tương ứng.
*   **DEM** (*Diagnostic Event Manager*): Module quản lý sự kiện chẩn đoán, lưu trữ DTC, Freeze Frame và Extended Data vào bộ nhớ.
*   **NvM** (*Non-Volatile Memory Manager*): Module quản lý bộ nhớ phi bốc hơi, trừu tượng hóa các thao tác với EEPROM hoặc Flash.
*   **Fee** (*Flash EEPROM Emulation*): Module giả lập hành vi EEPROM trên chip Flash vật lý, cung cấp thuật toán Wear Leveling để nâng cao tuổi thọ Flash.
*   **Fls** (*Flash Driver*): Driver phần cứng điều khiển chip Flash vật lý (MCAL).
*   **MemIf** (*Memory Abstraction Interface*): Tầng trung gian cho phép NvM giao tiếp với cả Fee (Flash) và Eep (EEPROM vật lý) một cách trong suốt.

---

## Mục Lục

1. [Tổng Quan Ngăn Xếp Chẩn Đoán (Diagnostic Stack & UDS ISO 14229)](#1-tổng-quan-ngăn-xếp-chẩn-đoán-diagnostic-stack--uds-iso-14229)
2. [Bảng Ma Trận Các Dịch Vụ UDS Cốt Lõi (Core UDS Services)](#2-bảng-ma-trận-các-dịch-vụ-uds-cốt-lõi-core-uds-services)
   - [2.1 Dịch Vụ 0x10: DiagnosticSessionControl](#21-dịch-vụ-0x10-diagnosticsessioncontrol)
   - [2.2 Dịch Vụ 0x27: SecurityAccess (Thuật Toán Seed & Key)](#22-dịch-vụ-0x27-securityaccess-thuật-toán-seed--key)
   - [2.3 Dịch Vụ 0x22 & 0x2E: Read / Write Data By Identifier (DID)](#23-dịch-vụ-0x22--0x2e-read--write-data-by-identifier-did)
   - [2.4 Dịch Vụ 0x19 & 0x14: Read & Clear DTC Information](#24-dịch-vụ-0x19--0x14-read--clear-dtc-information)
   - [2.5 Cấu Trúc Khung Phản Hồi Âm (Negative Response - NRC)](#25-cấu-trúc-khung-phản-hồi-âm-negative-response---nrc)
3. [Module DCM (Diagnostic Communication Manager: DSL, DSD, DSP)](#3-module-dcm-diagnostic-communication-manager-dsl-dsd-dsp)
4. [Module DEM (Diagnostic Event Manager) & Cấu Trúc Mã Lỗi DTC](#4-module-dem-diagnostic-event-manager--cấu-trúc-mã-lỗi-dtc)
   - [4.1 Cấu Trúc Mã Lỗi DTC 3-Byte & Mã Kiểu Lỗi (Fault Type Byte - FTB)](#41-cấu-trúc-mã-lỗi-dtc-3-byte--mã-kiểu-lỗi-fault-type-byte---ftb)
   - [4.2 Giải Mã Chi Tiết 8-Bit Của DTC Status Byte](#42-giải-mã-chi-tiết-8-bit-của-dtc-status-byte)
   - [4.3 Thuật Toán Lọc Rung Lỗi (Debounce Algorithms: Counter-Based vs Time-Based)](#43-thuật-toán-lọc-rung-lỗi-debounce-algorithms-counter-based-vs-time-based)
   - [4.4 Khung Dữ Liệu Đóng Băng (Freeze Frame) & Extended Data Records](#44-khung-dữ-liệu-đóng-băng-freeze-frame--extended-data-records)
5. [Ngăn Xếp Bộ Nhớ Phi Bốc Hơi (Memory Stack: NvM, MemIf, Fee, Fls)](#5-ngăn-xếp-bộ-nhớ-phi-bốc-hơi-memory-stack-nvm-memif-fee-fls)
   - [5.1 Kiến Trúc 4 Tầng Của Memory Stack](#51-kiến-trúc-4-tầng-của-memory-stack)
   - [5.2 3 Loại Khối Bộ Nhớ NVRAM Block Types (Native, Redundant, Dataset)](#52-3-loại-khối-bộ-nhớ-nvram-block-types-native-redundant-dataset)
   - [5.3 Chu Trình Đọc/Ghi Bất Đồng Bộ (NvM_WriteBlock)](#53-chu-trình-đọcghi-bất-đồng-bộ-nvm_readall-nvm_writeall-nvm_writeblock)
   - [5.4 Cơ Chế Giả Lập Flash EEPROM (Fee: Virtual Sectors, Wear Leveling, Garbage Collection)](#54-cơ-chế-giả-lập-flash-eeprom-fee-virtual-sectors-wear-leveling-garbage-collection)
6. [Thực Chiến & Hands-On Exercise](#6-thực-chiến--hands-on-exercise)
7. [Các Cạm Bẫy Phổ Biến (Common Pitfalls)](#7-các-cạm-bẫy-phổ-biến-common-pitfalls)
8. [Bằng Chứng Mã Nguồn & Định Nghĩa Giao Tiếp](#8-bằng-chứng-mã-nguồn--định-nghĩa-giao-tiếp-trong-paraias)
9. [Đúc Kết Kỹ Nghệ & Bảng Tra Cứu APIs](#9-đúc-kết-kỹ-nghệ--bảng-tra-cứu-apis)
10. [Bộ Câu Hỏi Phỏng Vấn (Interview Questions)](#10-bộ-câu-hỏi-phỏng-vấn)

---

## 1. Tổng Quan Ngăn Xếp Chẩn Đoán (Diagnostic Stack & UDS ISO 14229)

🟢 **LEVEL 1: NEWBIE FRIENDLY**
📖 **Diagnostic Stack** giống như một "bác sĩ khám bệnh" cho xe ô tô. Khi bạn cắm máy chẩn đoán vào cổng OBD-II dưới vô lăng, máy đó sẽ "hỏi" ECU (hộp điều khiển) xem có bệnh gì không, xe chạy tốt không.
💡 *Ví dụ:* Máy chẩn đoán hỏi: "Nhiệt độ nước làm mát bao nhiêu?". ECU trả lời: "Đang là 90 độ C". Quá trình trao đổi này được chuẩn hóa toàn cầu bằng giao thức gọi là UDS.

🟡 **LEVEL 2: INTERMEDIATE**
Ngăn xếp chẩn đoán (*Diagnostic Stack*) phục vụ việc giao tiếp giữa **Thiết bị kiểm chuẩn bên ngoài (Diagnostic Tester / Scanner cắm qua cổng OBD-II)** và các hộp **ECU** trên xe hơi để:
1. Đọc và xóa mã lỗi hư hỏng phần cứng/cảm biến (**Diagnostic Trouble Codes - DTCs**).
2. Đọc thông số thời gian thực của xe (Live Sensor Data: Điện áp bình, Nhiệt độ dầu, Tốc độ động cơ).
3. Hiệu chỉnh cấu hình (Calibration), nạp số khung xe (VIN), và cập nhật Firmware (Flashing / FOTA).
4. Khởi chạy các Routine đặc biệt như xả gió phanh, tự học vị trí bướm ga.

```mermaid
graph TD
    Tester["🖥️ Diagnostic Tester (Thiết bị cắm cổng OBD-II)"] <-->|Cáp Mạng CAN / Ethernet| HW["CAN / Eth Controller (ECU)"]
    
    subgraph "BSW: DIAGNOSTIC STACK"
        HW <--> CANTP["CanTp (ISO 15765-2) / DoIP"]
        CANTP <--> PDUR["PDU Router (PduR)"]
        PDUR <--> DCM["Module DCM (Diagnostic Communication Manager)<br>• DSL: Quản trị Session & Bảo Mật<br>• DSD: Phân giải Service ID<br>• DSP: Xử lý nội dung dịch vụ UDS"]
        DCM <--> DEM["Module DEM (Diagnostic Event Manager)<br>• Quản trị mã lỗi DTC<br>• Debouncing Filter<br>• Freeze Frame Data"]
    end
    
    subgraph "APPLICATION & RTE"
        DCM <--> RTE["Tầng RTE"]
        DEM <--> RTE
        RTE <--> SWC["Application SWC<br>(Báo cáo lỗi qua Rte_Call_SetEventStatus)"]
    end

    style Tester fill:#f5f5f5,stroke:#666666,stroke-width:2px
    style DCM fill:#d5e8d4,stroke:#82b366,stroke-width:2px
    style DEM fill:#ffe6cc,stroke:#d79b00,stroke-width:2px
    style RTE fill:#dae8fc,stroke:#6c8ebf,stroke-width:2px
    style SWC fill:#d5e8d4,stroke:#82b366,stroke-width:2px
```

🔴 **LEVEL 3: EXPERT (Deep Dive)**
Ở cấp độ kiến trúc hệ thống, Diagnostic Stack phải xử lý các luồng dữ liệu song song và quản lý bộ nhớ đệm (buffer management). Khi nhận một gói lệnh UDS dài qua CanTp (ISO 15765-2 Segmentation), PDUR gọi DCM cung cấp buffer (`Dcm_ProvideRxBuffer`). DCM phải tính toán timeout (P2/P2*). Nếu việc thao tác bộ nhớ kéo dài, DCM phải tự động phát NRC 0x78 (Response Pending) định kỳ để Tester không bị timeout ở Transport Layer. Sự đồng bộ giữa DCM (nhận request), DEM (đọc trạng thái fault hiện tại) và NvM (lấy snapshot data) là cực kỳ quan trọng, thường được đồng bộ thông qua các hàm callback bất đồng bộ được gọi từ BSW Scheduler (SchM).

---

## 2. Bảng Ma Trận Các Dịch Vụ UDS Cốt Lõi (Core UDS Services)

🟢 **LEVEL 1: NEWBIE FRIENDLY**
Giao thức UDS định nghĩa các "mã lệnh" chuẩn. Ví dụ `0x22` là đọc dữ liệu, giống như bạn gửi tin nhắn `GET_INFO` cho bạn bè. ECU trả lời `0x62` (cộng thêm 0x40 vào 0x22) kèm theo dữ liệu bạn cần. Nếu ECU bận hoặc bạn yêu cầu sai, nó sẽ trả lời bằng mã lỗi (NRC).

🟡 **LEVEL 2: INTERMEDIATE**
Chuẩn **ISO 14229-1 (Unified Diagnostic Services - UDS)** quy định các mã dịch vụ (*Service Identifier - SID*) chuẩn. Dưới đây là bảng phân loại các Service quan trọng nhất:

| SID Request | SID Positive Response | Tên Dịch Vụ UDS | Mô Tả Kỹ Thuật & Ứng Dụng Thực Tế |
|:---:|:---:|---|---|
| **`0x10`** | `0x50` | **DiagnosticSessionControl** | Chuyển đổi phiên làm việc (Default, Programming, Extended Diagnostic). |
| **`0x11`** | `0x51` | **ECUReset** | Yêu cầu ECU khởi động lại phần cứng (Hard Reset, Soft Reset, Key-Off-On). |
| **`0x14`** | `0x54` | **ClearDiagnosticInformation** | Xóa sạch bộ nhớ lưu trữ mã lỗi DTC và Freeze Frame trong Flash/EEPROM. |
| **`0x19`** | `0x59` | **ReadDTCInformation** | Đọc danh sách mã lỗi, số lượng lỗi, Snapshot dữ liệu lúc xảy ra lỗi. |
| **`0x22`** | `0x62` | **ReadDataByIdentifier (RDBI)** | Đọc dữ liệu biến/thông số từ ECU dựa theo mã định danh 2-byte DID. |
| **`0x2E`** | `0x6E` | **WriteDataByIdentifier (WDBI)** | Ghi dữ liệu cấu hình (VIN, Calibration data) vào bộ nhớ ECU theo DID. |
| **`0x27`** | `0x67` | **SecurityAccess** | Mở khóa bảo mật mức cao (yêu cầu Seed $
ightarrow$ tính toán Key) trước khi nạp Flash. |
| **`0x28`** | `0x68` | **CommunicationControl** | Bật / tắt tạm thời việc phát gói tin thông thường trên mạng CAN. |
| **`0x31`** | `0x71` | **RoutineControl** | Kích hoạt thực thi một hàm chức năng đặc biệt (Xả gió phanh ABS, Kiểm tra kim phun). |
| **`0x34`** | `0x74` | **RequestDownload** | Bắt đầu quy trình nạp phần mềm FOTA: Khai báo địa chỉ và dung lượng binary. |
| **`0x36`** | `0x76` | **TransferData** | Truyền các khối dữ liệu binary nhị phân vào RAM/Flash của ECU. |
| **`0x37`** | `0x77` | **RequestTransferExit** | Kết thúc quá trình truyền dữ liệu và kiểm tra toàn vẹn mã CRC. |

🔴 **LEVEL 3: EXPERT (Deep Dive)**
Các dịch vụ như 0x22, 0x2E, 0x31 đòi hỏi quyền truy cập dựa trên (1) Session, (2) Security Level, (3) Application State. Ma trận quyền truy cập này được định nghĩa tĩnh trong cấu hình DcmDsp (DcmDspDidInfo, DcmDspRoutineInfo). Ví dụ, DID 0xF190 (VIN) có thể cấu hình Read Allowed trong mọi Session, nhưng Write chỉ Allowed trong Extended Session và Security Level 1. Nếu không thỏa mãn, DCM tự động reject request bằng DSD mà không cần DSP xử lý, trả về 0x7F 0x2E 0x33.

### 2.1 Dịch Vụ 0x10: DiagnosticSessionControl
Mỗi ECU luôn khởi động ở chế độ mặc định (**Default Session**). Để thực hiện các tác vụ nguy hiểm, Tester phải yêu cầu chuyển Session. Mỗi session được duy trì bằng bộ đếm timeout (S3_Server, mặc định 5s). Nếu Tester ngắt kết nối không gửi thông điệp TesterPresent (0x3E), session sẽ reset về Default.
* `0x01` — **Default Session:** Phiên cơ bản, chỉ cho phép đọc thông số và đọc lỗi.
* `0x02` — **Programming Session:** Phiên nạp Flash Bootloader (vô hiệu hóa các ứng dụng thông thường).
* `0x03` — **Extended Diagnostic Session:** Cho phép điều khiển cơ cấu chấp hành và cấu hình thông số.

### 2.2 Dịch Vụ 0x27: SecurityAccess (Thuật Toán Seed & Key)

Quy trình bắt tay bảo mật 2 bước để ngăn chặn truy cập trái phép vào ECU (ví dụ ngăn chặn Odometer tampering - tua công tơ mét).

```mermaid
sequenceDiagram
    autonumber
    actor Tester as Diagnostic Tester
    participant ECU as Hộp Điều Khiển ECU (DCM)

    Note over Tester,ECU: Bước 1: Yêu cầu mã ngẫu nhiên (Seed)
    Tester->>ECU: Request: 0x27 0x01 (SecurityAccess - Request Seed Level 1)
    Note over ECU: ECU sinh số ngẫu nhiên (VD: 0xA1B2C3D4)
    ECU-->>Tester: Positive Response: 0x67 0x01 0xA1 0xB2 0xC3 0xD4 (Seed)
    
    Note over Tester: Tester dùng thuật toán bí mật f(Seed, SecretKey) -> Key
    Note over ECU: ECU cũng tự tính toán kết quả f(Seed, SecretKey) nội bộ
    
    Note over Tester,ECU: Bước 2: Gửi khóa giải mã (Send Key)
    Tester->>ECU: Request: 0x27 0x02 0x5E 0x89 0xF1 0x02 (Calculated Key)
    
    alt Khóa trùng khớp
        Note over ECU: Mở khóa Security Level 1 thành công!
        ECU-->>Tester: Positive Response: 0x67 0x02 (Access Granted)
    else Khóa sai hoặc quá thời gian
        Note over ECU: Báo lỗi bảo mật và khóa trong 10 giây
        ECU-->>Tester: Negative Response: 0x7F 0x27 0x35 (Invalid Key)
    end
```

🔧 **Code C: Thuật toán f(Seed, Key) và Pitfall Attempt Counter**
```c
// Ví dụ thuật toán XOR/CRC đơn giản (Chỉ mang tính chất minh họa học thuật)
uint32 Calculate_Key(uint32 Seed, uint32 SecretKey) {
    // ⚠️ Warning: Thuật toán thực tế dùng AES-128/RSA, đây chỉ là dummy example
    return (Seed ^ SecretKey) + 0x12345678; 
}

// State Machine trong DCM
static uint8 SecurityAttemptCounter = 0;
static boolean IsLockedOut = FALSE;

Std_ReturnType Dcm_ProcessSecurityAccess(uint32 ReceivedKey) {
    if (IsLockedOut) {
        return E_NOT_OK; // ❌ Phải chờ Delay Timer (ví dụ 10 giây) kết thúc
    }
    
    uint32 ExpectedKey = Calculate_Key(CurrentSeed, APP_SECRET_KEY);
    
    if (ReceivedKey == ExpectedKey) {
        SecurityAttemptCounter = 0; // ✅ Best Practice: Luôn reset counter khi đúng để tránh khóa do tích lũy
        Unlock_Security_Level();
        return E_OK;
    } else {
        SecurityAttemptCounter++;
        if (SecurityAttemptCounter >= 3) {
            IsLockedOut = TRUE;
            Start_Penalty_Timer(10000); // 💀 Critical: Khóa 10 giây (Anti-bruteforce bảo vệ Brute Force Attack)
        }
        return E_NOT_OK;
    }
}
```

### 2.3 Dịch Vụ 0x22 & 0x2E: Read / Write Data By Identifier (DID)
Mỗi thông số được định danh bằng một số nguyên 2-byte (**DID - Data Identifier**):
* `0xF190`: Mã nhận diện xe VIN (17 ký tự ASCII).
* `0xF189`: Phiên bản phần mềm ECU Software Version.
* `0x0100`: Điện áp ắc-quy (Battery Voltage).

💡 **Code Example: Gửi UDS Request 0x22 & 0x2E (Đọc/Ghi VIN)**
```text
[ĐỌC VIN - Service 0x22, DID 0xF190]
Request  (Tester -> ECU): 0x22 0xF1 0x90
Response (ECU -> Tester): 0x62 0xF1 0x90 0x57 0x41 0x55 0x5A 0x5A 0x5A ... (Chuỗi ASCII của WAUZZZ...)

[GHI VIN - Service 0x2E, DID 0xF190]
Request  (Tester -> ECU): 0x2E 0xF1 0x90 0x57 0x41 0x55 0x5A 0x5A 0x5A ...
Response (ECU -> Tester): 0x6E 0xF1 0x90 (Báo hiệu ECU đã nhận và ghi thành công)
```
*(Nếu việc ghi mất thời gian, ECU sẽ trả về NRC 0x78 cho Tester đợi, sau đó trả về 0x6E).*

### 2.4 Dịch Vụ 0x19 & 0x14: Read & Clear DTC Information
* `0x19 0x01`: Yêu cầu báo cáo số lượng mã lỗi theo mặt nạ trạng thái (*reportNumberOfDTCByStatusMask*).
* `0x19 0x02`: Yêu cầu báo cáo danh sách mã lỗi theo mặt nạ trạng thái (*reportDTCByStatusMask*).
* `0x19 0x04`: Đọc dữ liệu đóng băng Snapshot của một mã lỗi cụ thể (*reportDTCSnapshotRecordByDTCNumber*).
* `0x14 0xFF 0xFF 0xFF`: Xóa toàn bộ mã lỗi của tất cả các nhóm lỗi.

### 2.5 Cấu Trúc Khung Phản Hồi Âm (Negative Response - NRC)

Khi một yêu cầu không hợp lệ hoặc bị từ chối, ECU trả về khung lỗi có định dạng 3 byte:
```
+------------+------------------------+---------------------------------+
| Byte 0: 7F | Byte 1: Requested SID  | Byte 2: NRC (Negative Resp Code)|
+------------+------------------------+---------------------------------+
```

| Mã NRC | Tên Mã Lỗi Chuẩn | Ý Nghĩa Kỹ Thuật |
|:---:|---|---|
| **`0x11`** | `serviceNotSupported` | ECU không hỗ trợ Service ID này (ví dụ gửi 0xAA không tồn tại). |
| **`0x12`** | `subFunctionNotSupported` | Sub-function không được hỗ trợ trong phiên hiện tại. |
| **`0x13`** | `incorrectMessageLengthOrInvalidFormat` | Chiều dài byte của gói tin Request bị sai so với cấu hình chuẩn. |
| **`0x22`** | `conditionsNotCorrect` | Điều kiện xe chưa thỏa mãn (ví dụ: đòi xả phanh ABS nhưng xe đang chạy 100km/h). |
| **`0x31`** | `requestOutOfRange` | Tham số DID hoặc Routine ID vượt quá dải cho phép. |
| **`0x33`** | `securityAccessDenied` | Chưa mở khóa dịch vụ `0x27` thành công. |
| **`0x78`** | `responsePending` | ECU đã nhận lệnh hợp lệ nhưng đang bận xử lý tác vụ dài (ví dụ: Ghi Flash/EEPROM), Tester chờ tiếp. |

---

## 3. Module DCM (Diagnostic Communication Manager: DSL, DSD, DSP)

🟢 **LEVEL 1: NEWBIE FRIENDLY**
DCM là "Cảnh sát giao thông" và "Lễ tân" của ECU. Nó kiểm tra xem Tester có được phép gửi lệnh đó không (có đúng Session không, đã có thẻ VIP Security chưa), sau đó dẫn đường đến đúng phân hệ để lấy dữ liệu. Quản lý timeout cũng là việc của DCM.

🟡 **LEVEL 2: INTERMEDIATE**
Module DCM được chia thành 3 tầng chức năng nội bộ rõ rệt:

```mermaid
graph TD
    subgraph "DCM INTERNALS (ISO 14229 IMPLEMENTATION)"
        DSL["1. DSL (Diagnostic Session Layer)<br>• Quản trị Session (Default/Programming/Extended)<br>• Giám sát Security Level<br>• Điều phối bộ định thời P2_Server & P2*_Server"]
        DSD["2. DSD (Diagnostic Service Dispatcher)<br>• Kiểm tra tính hợp lệ của gói tin Request<br>• Kiểm tra quyền thực thi theo Session/Security<br>• Điều hướng (Dispatch) tới hàm xử lý tương ứng"]
        DSP["3. DSP (Diagnostic Service Processing)<br>• Hiện thực hóa logic của từng dịch vụ UDS<br>• Gọi sang DEM để đọc lỗi hoặc gọi sang NvM để đọc/ghi DID"]
    end

    DSL --> DSD
    DSD --> DSP
    DSP -->|Tương tác lỗi| DEM_Mod["Module DEM"]
    DSP -->|Đọc/Ghi dữ liệu| NVM_Mod["Module NvM"]

    style DSL fill:#dae8fc,stroke:#6c8ebf,stroke-width:2px
    style DSD fill:#d5e8d4,stroke:#82b366,stroke-width:2px
    style DSP fill:#ffe6cc,stroke:#d79b00,stroke-width:2px
```

🔴 **LEVEL 3: EXPERT (Deep Dive)**
Quản trị tài nguyên đệm trong DCM rất khắt khe. Khi Tester gọi `0x19 0x02` (Read DTCs by Status Mask), buffer TX (Transmission Buffer) có thể không đủ chứa hàng trăm DTC. Việc phân trang (Pagination) thông qua cơ chế của ISO 15765-2 (gửi các Consecutive Frames liên tục) phải được xử lý ở tầng DSP kết hợp với DSD. Mỗi khi một block dữ liệu được gửi thành công, `Dcm_TpTxConfirmation` được kích hoạt, cho phép DCM điền block tiếp theo vào buffer, bảo đảm an toàn bộ nhớ RAM hẹp hòi của MCU.

---

## 4. Module DEM (Diagnostic Event Manager) & Cấu Trúc Mã Lỗi DTC

🟢 **LEVEL 1: NEWBIE FRIENDLY**
DEM giống như một "Cuốn sổ Nam Tào". Khi cảm biến (ví dụ: nhiệt độ) báo lỗi, DEM sẽ ghi vào sổ mã lỗi (DTC). Để chắc chắn đó không phải do chập chờn (xe đi vào ổ gà), DEM đếm: "Lỗi 1 lần, 2 lần... 10 lần! Chắc chắn lỗi rồi, bật đèn Check Engine lên!".

🟡 **LEVEL 2: INTERMEDIATE**
### 4.1 Cấu Trúc Mã Lỗi DTC 3-Byte & Mã Kiểu Lỗi (Fault Type Byte - FTB)

Một mã lỗi **DTC (Diagnostic Trouble Code)** trong AUTOSAR gồm đúng **3 bytes (24 bits)**, định dạng phổ biến nhất theo ISO 15031-6:

```
+-----------------------------------+-----------------------------------+-----------------------------------+
|     Byte 1 (High Byte): Category  |     Byte 2 (Middle Byte): Subsys  |     Byte 3 (Low Byte): Fault Type |
+-----------------------------------+-----------------------------------+-----------------------------------+
```

* **Byte 1 & 2:** Xác định phân hệ bị lỗi:
  * **`Pxxxx` (Powertrain):** Động cơ, Hộp số, Pin BMS.
  * **`Cxxxx` (Chassis):** Khung gầm, Phanh ABS, Trợ lực lái EPS.
  * **`Bxxxx` (Body):** Thân xe, Cửa, Đèn, Túi khí.
  * **`Uxxxx` (Network):** Lỗi giao tiếp mạng bus CAN/LIN/Ethernet/FlexRay.
* **Byte 3 (FTB - Fault Type Byte):** Loại lỗi cụ thể:
  * `0x11`: Ngắn mạch lên nguồn dương (*Short to Battery*).
  * `0x12`: Ngắn mạch xuống mass (*Short to Ground*).
  * `0x13`: Hở mạch (*Open Circuit*).
  * `0x29`: Tín hiệu không hợp lệ (*Signal Invalid*).

### 4.2 Giải Mã Chi Tiết 8-Bit Của DTC Status Byte

Mỗi mã lỗi trong ECU luôn đi kèm một **Byte Trạng Thái (Status Byte 8-bit)** phản ánh vòng đời của lỗi:

| Bit | Tên Cờ Trạng Thái | Giá Trị `1` | Giá Trị `0` |
|:---:|---|---|---|
| **Bit 0** | `testFailed` | Lỗi đang xuất hiện ở chu kỳ kiểm tra gần nhất. | Lần kiểm tra gần nhất không có lỗi. |
| **Bit 1** | `testFailedThisOperationCycle` | Đã từng xuất hiện lỗi ít nhất 1 lần trong chu kỳ nổ máy hiện tại. | Chưa từng bị lỗi trong chu kỳ nổ máy này. |
| **Bit 2** | `pendingDTC` | Lỗi xuất hiện tạm thời nhưng chưa đủ lâu để xác nhận (chờ Debounce). | Không có lỗi chờ xác nhận. |
| **Bit 3** | `confirmedDTC` | **Lỗi đã được xác nhận chính thức** (ghi đè vào bộ nhớ Flash/EEPROM). | Lỗi chưa được xác nhận hoặc đã bị xóa. |
| **Bit 4** | `testNotCompletedSinceLastClear` | Kể từ lần xóa lỗi gần nhất, thuật toán kiểm tra lỗi chưa hoàn tất chạy. | Thuật toán kiểm tra đã chạy xong ít nhất 1 lần. |
| **Bit 5** | `testFailedSinceLastClear` | Kể từ lần xóa lỗi gần nhất, đã có ít nhất 1 lần phát hiện lỗi. | Chưa từng phát hiện lỗi từ khi xóa. |
| **Bit 6** | `testNotCompletedThisOperationCycle` | Trong chu kỳ nổ máy này, thuật toán kiểm tra lỗi chưa hoàn tất chạy. | Thuật toán đã hoàn tất kiểm tra trong chu kỳ này. |
| **Bit 7** | `warningIndicatorRequested` | Yêu cầu bật đèn cảnh báo lỗi trên đồng hồ taplo (**đèn Check Engine / MIL ON**). | Không yêu cầu bật đèn cảnh báo. |

🔴 **LEVEL 3: EXPERT (Deep Dive)**
### 4.3 Thuật Toán Lọc Rung Lỗi (Debounce Algorithms: Counter-Based vs Time-Based)

Để tránh báo lỗi giả do nhiễu điện từ đột biến, DEM cung cấp 2 thuật toán lọc, thường được kỹ sư Calibration cấu hình.

1. **Counter-Based Debouncing (Bộ đếm bước):**
   * Duy trì một biến đếm *Fault Counter*.
   * Khi phát hiện lỗi $
ightarrow$ Tăng biến đếm thêm `+StepUp` (ví dụ: +2).
   * Khi không có lỗi $
ightarrow$ Giảm biến đếm `-StepDown` (ví dụ: -1).
   * Chỉ khi biến đếm vượt ngưỡng **`Failed Threshold` (+127)** $
ightarrow$ Mới chính thức xác nhận lỗi (`confirmedDTC = 1`).
2. **Time-Based Debouncing (Bộ đếm thời gian):**
   * Lỗi phải tồn tại liên tục trong một khoảng thời gian cố định (ví dụ: liên tục 500 ms) mới xác nhận lỗi.

🔧 **Code C: Counter-based debounce với State Machine**
```c
#define DEBOUNCE_FAILED_THRESHOLD  127
#define DEBOUNCE_PASSED_THRESHOLD -128
#define STEP_UP 2
#define STEP_DOWN 1

static int8 FaultCounter = 0;

// Hàm này được gọi chu kỳ 10ms từ DEM MainFunction để đánh giá trạng thái lỗi
void Dem_DebounceCounter(boolean IsErrorActive) {
    if (IsErrorActive) {
        if (FaultCounter < DEBOUNCE_FAILED_THRESHOLD) {
            FaultCounter += STEP_UP; // Tăng nhanh khi có lỗi
        }
        if (FaultCounter >= DEBOUNCE_FAILED_THRESHOLD) {
            Dem_ReportConfirmedDTC(); // ✅ Xác nhận lỗi, chuyển cờ bit 3 lên 1, kích hoạt Freeze Frame
        }
    } else {
        if (FaultCounter > DEBOUNCE_PASSED_THRESHOLD) {
            FaultCounter -= STEP_DOWN; // Giảm chậm khi không có lỗi
        }
        if (FaultCounter <= DEBOUNCE_PASSED_THRESHOLD) {
            Dem_ReportPassedDTC(); // Xóa trạng thái lỗi tạm thời, clear bit 0
        }
    }
}
```

### 4.4 Khung Dữ Liệu Đóng Băng (Freeze Frame) & Extended Data Records

* **Freeze Frame (Snapshot Data):** Ngay tại thời điểm mã lỗi được xác nhận (`confirmedDTC`), DEM lập tức chụp lại toàn bộ trạng thái cảm biến của xe lúc đó (Tốc độ xe, Điện áp bình, Nhiệt độ nước làm mát, Vị trí bàn đạp ga) và lưu vĩnh viễn vào Flash để thợ sửa xe điều tra nguyên nhân.
* **Extended Data Records:** Lưu trữ số lần lỗi lặp lại (*Fault Occurrence Counter*), chu kỳ lão hóa lỗi (*Aging Counter*). Nó giúp biết xe bị lỗi bao nhiêu lần kể từ lần nổ máy cuối.

📊 **Data: Ví dụ dữ liệu Freeze Frame thực tế của lỗi P0A7E (BMS Over-temperature)**
```text
DTC: P0A7E (0x0A7E) - Battery Pack Over Temperature
Status: 0x2F (Bit 0,1,2,3,5 là 1: Confirmed, TestFailedThisCycle, Pending...)
--- Freeze Frame Data Record ---
DID 0x0100 (Battery Voltage): 385.5 V
DID 0x0101 (Battery Current): +150.0 A (Discharge)
DID 0x0102 (Max Cell Temp):   65 °C 💀 Critical!
DID 0x0103 (Vehicle Speed):   120 km/h
```
*(Chẩn đoán từ chuyên gia: Xe chạy tốc độ cao, dòng xả pin cực lớn trong thời gian dài khiến nhiệt độ cell pin vượt ngưỡng an toàn).*

---

## 5. Ngăn Xếp Bộ Nhớ Phi Bốc Hơi (Memory Stack: NvM, MemIf, Fee, Fls)

🟢 **LEVEL 1: NEWBIE FRIENDLY**
Ngăn xếp nhớ (NvM) là "Ổ cứng SSD" của xe. Tắt máy dữ liệu vẫn còn (VD: Số Kilomet, mã lỗi, cài đặt đài Radio). Trong đó, Module Fee đóng vai trò "Kẻ đánh lừa", làm cho chip Flash vật lý tưởng mình là bộ nhớ EEPROM cao cấp, giúp phân bổ dữ liệu nhỏ lẻ để ghi và tăng tuổi thọ chip, tránh việc ghi đi ghi lại 1 chỗ gây cháy chip.

🟡 **LEVEL 2: INTERMEDIATE**
### 5.1 Kiến Trúc 4 Tầng Của Memory Stack

```mermaid
graph TD
    SWC["Application SWC / DEM Diagnostic"] -->|Rte_Call_NvM_WriteBlock| NVM["1. Module NvM (Non-Volatile Memory Manager)<br>• Quản trị hàng đợi bất đồng bộ (Async Queue)<br>• Kiểm tra toàn vẹn mã CRC (CRC16/CRC32)<br>• Quản lý phục hồi giá trị mặc định ROM"]
    
    NVM -->|MemIf_Write| MEMIF["2. Module MemIf (Memory Interface)<br>• Trừu tượng hóa việc chọn thiết bị lưu trữ<br>• Định tuyến tới Driver Flash hoặc Driver EEPROM"]
    
    MEMIF -->|Fee_Write| FEE["3. Module Fee (Flash EEPROM Emulation)<br>• Giả lập EEPROM trên bộ nhớ Flash<br>• Quản lý Virtual Sectors & Wear Leveling<br>• Garbage Collection & Data Swapping"]
    
    MEMIF -.->|Eep_Write| EEP["Module Eep (EEPROM Driver)"]
    
    FEE -->|Fls_Write| FLS["4. Module MCAL Fls (Flash Driver)<br>• Ghi / Xóa theo từng Sector vật lý của chip"]

    style NVM fill:#d5e8d4,stroke:#82b366,stroke-width:2px
    style MEMIF fill:#dae8fc,stroke:#6c8ebf,stroke-width:2px
    style FEE fill:#ffe6cc,stroke:#d79b00,stroke-width:2px
    style FLS fill:#f8cecc,stroke:#b85e5e,stroke-width:2px
```

### 5.2 3 Loại Khối Bộ Nhớ NVRAM Block Types (Native, Redundant, Dataset)

| Loại Khối NVRAM | Cấu Trúc Vật Lý Lưu Trữ | Độ An Toàn & Khả Năng Khôi Phục | Ứng Dụng Thực Tế |
|---|---|---|---|
| **Native Block** | 1 bản sao duy nhất trong Flash + 1 mã kiểm tra CRC. | Trung bình: Nếu CRC lỗi $
ightarrow$ Dữ liệu bị hỏng vĩnh viễn, phải nạp lại ROM Default. | Lưu thông số cấu hình thông thường (Cài đặt âm lượng, Độ sáng màn hình, Vị trí ghế lái). |
| **Redundant Block** | **2 bản sao lưu độc lập (Copy 1 & Copy 2)** + 2 mã CRC riêng biệt. | **Cực cao**: Nếu Copy 1 bị hỏng hoặc mất nguồn giữa lúc đang ghi, NvM tự động khôi phục dữ liệu từ Copy 2. | **Dữ liệu an toàn sống còn**: Odometer (Số km xe đã chạy), Mã lỗi chẩn đoán DTC, Dữ liệu túi khí, Khóa bảo mật. |
| **Dataset Block** | Mảng gồm **N phần tử dữ liệu con** được đánh chỉ số từ `0` đến `N-1`. | Linh hoạt: Cho phép ứng dụng chọn lựa phần tử cần đọc/ghi qua hàm `NvM_SetDataIndex()`. | Bảng dữ liệu hiệu chỉnh động cơ theo nhiều chế độ lái (Eco, Sport, Comfort). |

🔴 **LEVEL 3: EXPERT (Deep Dive)**
### 5.3 Chu Trình Đọc/Ghi Bất Đồng Bộ (`NvM_ReadAll`, `NvM_WriteAll`, `NvM_WriteBlock`)

Quá trình ghi Flash mất rất nhiều thời gian (vài mili-giây đến vài giây tùy kích thước block). Do đó, NvM hoạt động theo cơ chế **Bất Đồng Bộ (Asynchronous Non-Blocking)**:

1. **Giai đoạn Khởi động xe (`NvM_ReadAll`):**
   * Hàm `EcuM` gọi `NvM_ReadAll()` lúc hệ thống boot.
   * NvM tự động nạp toàn bộ các block dữ liệu từ Flash vào các vùng nhớ RAM tương ứng (*RAM Mirror Buffers*) và kiểm tra mã CRC. Nếu sai, nạp Default ROM.
2. **Giai đoạn Hoạt động bình thường Lúc Xe Chạy:**
   * Ứng dụng chỉ việc đọc/ghi trực tiếp trên RAM Mirror Buffer $
ightarrow$ Tốc độ tức thì (0 ns).
   * Khi muốn lưu vĩnh viễn xuống Flash, ứng dụng gọi `NvM_WriteBlock(BlockId, NULL)` $
ightarrow$ Lệnh được đẩy vào hàng đợi *NvM Queue*. Hàm nền `NvM_MainFunction()` chạy định kỳ để âm thầm thực thi tác vụ từ hàng đợi, nhường CPU cho các task khác chạy song song.
3. **Giai đoạn Tắt máy (`NvM_WriteAll`):**
   * Khi tài xế tắt chìa khóa xe (Key-Off), `EcuM` gọi `NvM_WriteAll()`.
   * NvM quét toàn bộ các RAM Mirror có cờ đánh dấu đã thay đổi (*Block Changed*) và ghi đồng loạt xuống Flash trước khi ngắt nguồn ECU hoàn toàn (đòi hỏi Mạch duy trì nguồn - Power Hold Circuit).

```mermaid
sequenceDiagram
    autonumber
    actor SWC as Application SWC
    participant NVM as Module NvM
    participant QUEUE as NvM Job Queue
    participant MAIN as NvM_MainFunction
    participant FEE as Module Fee
    participant FLS as Module Fls

    SWC->>NVM: NvM_WriteBlock(BlockId)
    NVM->>QUEUE: Đẩy Job vào Queue
    NVM-->>SWC: Trả về E_OK (Đã nhận yêu cầu)
    Note over SWC,NVM: Trả về ngay lập tức (Non-blocking)
    
    loop Chu kỳ (VD: 10ms)
        MAIN->>QUEUE: Lấy Job ra xử lý
        MAIN->>FEE: Fee_Write()
        FEE->>FLS: Fls_Write() (Giao tiếp phần cứng)
    end
    
    Note over MAIN,FLS: Quá trình vật lý tốn phần cứng có thể mất hàng chục ms
    FLS-->>FEE: Callback(Job End)
    FEE-->>MAIN: Fee Job Done
    MAIN-->>SWC: Gọi Callback NvM_JobFinished()
```

### 5.4 Cơ Chế Giả Lập Flash EEPROM (Fee: Virtual Sectors, Wear Leveling, Garbage Collection)

Bộ nhớ Flash có 2 nhược điểm vật lý cố hữu:
1. **Phải xóa toàn bộ Sector** lớn (ví dụ: 4KB - 64KB) trước khi ghi.
2. **Tuổi thọ xóa/ghi có giới hạn** (khoảng 10.000 đến 100.000 lần Erase Cycles), nếu ghi mãi vào 1 chỗ sẽ gây "cháy" sector đó.

Module **`Fee`** giải quyết triệt để vấn đề này, biến Flash thô sơ thành một thiết bị lưu trữ thông minh:
* **Virtual Sectors:** Chia Flash thành ít nhất 2 Sector ảo (*Sector 1* và *Sector 2*).
* **Chunk Allocation:** Khi ứng dụng cập nhật một biến Odometer (12 byte), Fee không xóa Flash. Nó ghi thêm block 12 byte này vào vùng trống (*Appended Chunks*) ngay dưới block cũ. Lúc này block cũ bị đánh dấu là "Rác" (Invalidated).
* **Garbage Collection (Thu gom rác):** Khi Sector 1 gần đầy, Fee tự động kích hoạt tiến trình sao chép các bản dữ liệu *mới nhất và hợp lệ* từ Sector 1 sang Sector 2. Sau khi sao chép xong an toàn, nó mới xóa trắng hoàn toàn Sector 1 để tái sử dụng.
* Cơ chế này luân phiên sử dụng toàn bộ dung lượng Flash, dàn đều số lần Erase lên khắp bề mặt vật lý, thuật ngữ này gọi là **Wear Leveling**. Tuổi thọ bộ nhớ có thể tăng từ 10.000 lên hàng trăm ngàn vòng đời.

```mermaid
graph LR
    subgraph "Sector 1 (Đã đầy 100%)"
        A[Chunk 1: ODO 10km] --> B[Chunk 2: ODO 12km] --> C[Chunk 3: ODO 15km]
        D[Rác: Bản ODO cũ] --> C
    end
    
    subgraph "Sector 2 (Đang trống)"
        E[Trống]
    end
    
    Sector1 -- "Copy bản mới nhất (ODO 15km)" --> Sector2
    Sector1 -. "Erase (Xóa trắng Sector 1)" .-> Trống1[Sector 1 Trống]
```

---

## 6. Thực Chiến & Hands-On Exercise

🛠️ **Hands-On Exercise: Dùng CANoe/PCAN gửi UDS frame đọc DTC và parse response**
**Yêu cầu:** Kết nối máy tính (cài đặt phần mềm CANoe hoặc PCAN-Explorer) với mạng CAN của xe qua cổng OBD-II.
**Bước 1:** Gửi UDS Request đọc mã lỗi:
`Tx: 03 19 02 08 00 00 00 00`
*(Giải thích: `03` là PCI độ dài gói Single Frame, `19 02` là Service ReadDTCByStatusMask, `08` là Mask lọc theo bit 3 - Confirmed DTC).*
**Bước 2:** ECU xử lý và trả về UDS Response. Nhận khung phản hồi:
`Rx: 07 59 02 09 0A 7E 2F 00`
**Bước 3:** Parse Response:
*   `07`: Độ dài nội dung 7 byte.
*   `59 02`: Positive Response của dịch vụ 19 02 (19 + 40 = 59).
*   `09`: DTC Status Availability Mask của ECU (báo cho Tester biết ECU có thể cung cấp các trạng thái nào).
*   `0A 7E`: Chính là mã lỗi `P0A7E` được lưu dưới dạng Hex.
*   `2F`: Status Byte của lỗi này (0x2F tức là 0010 1111 dạng nhị phân, bit 0,1,2,3 và 5 đều bật $
ightarrow$ TestFailed + Confirmed + Pending + TestFailedSinceLastClear).

🎯 **Real-world Scenario:**
Xe điện (EV) đang đi trên cao tốc, tài xế thấy báo lỗi hệ thống pin (BMS) nhấp nháy trên đồng hồ trung tâm. Thợ sửa xe đưa xe vào gara, dùng máy chẩn đoán cắm vào cổng OBD-II, gửi lệnh `19 04` (Read DTC Snapshot) để đọc Freeze Frame của mã lỗi P0A7E. Khi phân tích Freeze Frame trên màn hình máy scan, thợ thấy `Max Cell Temp` là 65 độ C tại thời điểm lỗi phát sinh, trong khi `Vehicle Speed` đang là 120km/h. Thợ sửa chữa tiếp tục kích hoạt Routine Control `0x31` bật bơm nước bằng tay, kết quả thấy bơm quay lờ đờ, dòng điện tiêu thụ thấp. Kết luận: Hệ thống làm mát pin bị nghẽn (do mô tơ bơm nước làm mát yếu đi sau thời gian sử dụng), dẫn đến nhiệt độ cell pin không kịp thoát khi xả dòng lớn chạy cao tốc. Thợ quyết định thay cụm bơm nước.

---

## 7. Các Cạm Bẫy Phổ Biến (Common Pitfalls)

1. ⚠️ **NRC 0x78 Loop:** ECU trả về NRC 0x78 (Response Pending) liên tục mà không có điểm dừng khi thao tác NvM bị kẹt hoặc phần cứng Fls bị lỗi không thể hoàn thành lệnh, làm Tester bị treo vô hạn, ảnh hưởng đến quy trình sản xuất End-Of-Line. ✅ *Khắc phục: Phải cấu hình thông số DcmDspMaxNumOf0x78 trong DCM để giới hạn số vòng lặp tối đa, quá giới hạn thì abort và trả về NRC `0x22` hoặc `0x10`.*
2. 💀 **Seed=0 Vulnerability:** Thuật toán sinh random trong chip (TRNG - True Random Number Generator) bị lỗi khởi tạo, lúc nào cũng sinh ra `Seed = 0x00000000`. Hacker bắt được gói, dễ dàng tìm được khóa bí mật (SecretKey) nếu thuật toán là hàm toán học đơn giản. ✅ *Khắc phục: Luôn kiểm tra Seed sinh ra, nếu bằng 0 phải sinh lại. Hơn nữa, tích hợp các chuẩn mã hóa HSM (Hardware Security Module) hoặc AES-128 để mã hóa Seed-Key.*
3. ❌ **NvM Blocking:** Gọi trực tiếp hàm ghi Flash (`Fls_Write`) bên trong một hàm ngắt (Interrupt ISR) hoặc MainFunction đồng bộ của ứng dụng. Điều này chiếm trọn CPU, gây treo Task, OS Watchdog reset ECU. ✅ *Khắc phục: Bắt buộc gọi `NvM_WriteBlock` (Async) để ghi ngầm nền, và cung cấp callback `Rte_Call_NvM_JobFinished()`.*
4. ⚠️ **Redundant block bị corruption cả 2 bản:** Mất nguồn điện đúng lúc hệ thống đang ghi song song hoặc ghi đè cả hai block dự phòng cùng một lúc. ✅ *Khắc phục: Kiến trúc module MemIf và Fee phải xử lý ghi tuần tự (Sequential). Ghi xong Copy 1 hoàn chỉnh, cập nhật Management byte (trạng thái hợp lệ), xác nhận thành công, rồi mới bắt đầu ghi Copy 2. Vậy nếu mất điện lúc ghi Copy 1, ta còn Copy 2 nguyên vẹn, và ngược lại.*
5. ❌ **Bỏ qua Negative Response khi Routine Control:** Tester gửi lệnh kích hoạt hàm xả gió phanh ABS (`0x31 0x01 0x02 0x03`), Tester (máy chẩn đoán của thợ) nhận về khung NRC `0x7F 0x31 0x22` (Conditions Not Correct, do ECU từ chối vì xe đang chạy ở tốc độ cao). Tester lại hiển thị cho thợ là "Bắt đầu xả gió thành công" vì lập trình viên quên bắt lỗi. Gây hiểu nhầm vô cùng nguy hiểm.

---

## 8. Bằng Chứng Mã Nguồn & Định Nghĩa Giao Tiếp

### 8.1 Cấu Trúc Khối Dữ Liệu NvM: `NvM.h`
**File:** `com/as.infrastructure/include/NvM.h`

```c
/* Khởi tạo toàn bộ ngăn xếp NvM */
void NvM_Init(void);

/* Đọc đồng loạt toàn bộ dữ liệu từ Flash lên RAM lúc khởi động (Gọi từ EcuM) */
void NvM_ReadAll(void);

/* Ghi đồng loạt toàn bộ dữ liệu từ RAM xuống Flash lúc tắt nguồn (Gọi từ EcuM) */
void NvM_WriteAll(void);

/* Yêu cầu ghi 1 block bất đồng bộ (Gọi từ App SWC) */
Std_ReturnType NvM_WriteBlock(NvM_BlockIdType BlockId, const uint8 *NvM_SrcPtr);

/* Yêu cầu đọc 1 block bất đồng bộ */
Std_ReturnType NvM_ReadBlock(NvM_BlockIdType BlockId, uint8 *NvM_DstPtr);

/* Lấy trạng thái kết quả của yêu cầu bất đồng bộ (Đang PENDING, OK, hay FAILED) */
Std_ReturnType NvM_GetErrorStatus(NvM_BlockIdType BlockId, NvM_RequestResultType *RequestResultPtr);
```

🔧 **Code Example: NvM_WriteBlock với callback khi ghi xong**
```c
// File: Bms_NvM_Callback.c
// Hàm này được cấu hình gọi khi NvM xử lý xong Job trong hàng đợi cho một Block cụ thể (Ví dụ block cấu hình dòng xả)
Std_ReturnType NvM_JobFinished_BMS_Config(uint8 ServiceId, NvM_RequestResultType JobResult) {
    if (JobResult == NVM_REQ_OK) {
        // Ghi thành công vào bộ nhớ phi bốc hơi, gửi notification cho State Machine của BMS
        Bms_UpdateStatus_NvmWrite(BMS_NVM_SUCCESS);
    } else {
        // Lỗi ghi bộ nhớ (ví dụ do Flash bị mòn, vượt quá tuổi thọ, hoặc lỗi phần cứng)
        Bms_UpdateStatus_NvmWrite(BMS_NVM_FAILED);
        // Báo lỗi hệ thống bộ nhớ lên DEM, để kỹ thuật viên biết ECU đã hư phần cứng lưu trữ
        (void) Dem_SetEventStatus(DEM_EVENT_EEPROM_ERROR, DEM_EVENT_STATUS_FAILED);
    }
    return E_OK; // Return OK cho BSW caller
}
```

### 8.2 Báo Cáo Lỗi Từ Ứng Dụng Lên DEM: `Dem.h`
**File:** `com/as.infrastructure/include/Dem.h`

```c
/* Hàm API cốt lõi để SWC hoặc BSW báo cáo trạng thái lỗi cho DEM */
Std_ReturnType Dem_SetEventStatus(
    Dem_EventIdType     EventId,       /* Mã định danh sự kiện lỗi (Được gen từ cấu hình) */
    Dem_EventStatusType EventStatus    /* Trạng thái: DEM_EVENT_STATUS_PASSED hoặc DEM_EVENT_STATUS_FAILED */
);

/* Hàm xóa mã lỗi chẩn đoán (Được gọi từ DCM khi nhận UDS 0x14) */
Std_ReturnType Dem_ClearDTC(
    uint32              DTC,           /* Mã DTC 3-byte hoặc 0xFFFFFF (Clear All) */
    Dem_DTCKindType     DTCKind,       /* Nhóm lỗi: DEM_DTC_KIND_ALL_DTCS */
    Dem_DTCOriginType   DTCOrigin      /* Vùng nhớ lưu: DEM_DTC_ORIGIN_PRIMARY_MEMORY */
);
```

🔧 **Code Example: Implement Dem_SetEventStatus trong BMS SWC cho lỗi quá nhiệt**
```c
// File: Bms_App.c
// Task giám sát nhiệt độ định kỳ mỗi 50ms
void BMS_MonitorTemperature(void) {
    // Lấy nhiệt độ cao nhất từ tất cả các cell pin (qua BSW ADC hoặc Sensor)
    float CurrentMaxTemp = Adc_GetMaxCellTemperature();
    
    // Nếu nhiệt độ lớn hơn 60 độ, báo lỗi FAILED
    if (CurrentMaxTemp >= 60.0f) {
        (void) Dem_SetEventStatus(DEM_DTC_BMS_OVERTEMP_P0A7E, DEM_EVENT_STATUS_FAILED);
        
        // Có thể bổ sung cơ chế Derating (giảm công suất xe để bảo vệ) tại đây
        Bms_ActivatePowerDerating(DERATING_LEVEL_SEVERE);
    } 
    // Nếu nhiệt độ giảm xuống mức an toàn, báo PASSED
    else if (CurrentMaxTemp <= 50.0f) {
        // Hiện tượng Hysteresis (trễ) giữa 50 - 60 giúp lọc rung chập chờn
        (void) Dem_SetEventStatus(DEM_DTC_BMS_OVERTEMP_P0A7E, DEM_EVENT_STATUS_PASSED);
        Bms_DeactivatePowerDerating();
    }
}
```

---

## 9. Đúc Kết Kỹ Nghệ & Bảng Tra Cứu APIs

```
[BẢNG TỔNG KẾT VAI TRÒ DIAGNOSTIC & MEMORY STACK TRONG AUTOSAR CLASSIC]

1. DCM (Diagnostic Communication Manager):
   - Xử lý phiên làm việc (Session Control 0x10) và xác thực bảo mật Seed/Key (Security Access 0x27).
   - Tiếp nhận và định tuyến các dịch vụ UDS 0x11, 0x14, 0x19, 0x22, 0x2E, 0x31.
   - Quản lý P2, P2* timeout, phát sinh NRC 0x78 khi hệ thống bận rộn.

2. DEM (Diagnostic Event Manager):
   - Quản lý tập trung toàn bộ mã lỗi DTC 3-byte và Status Byte 8-bit từ tất cả SWC.
   - Cung cấp thuật toán lọc rung lỗi (Debounce Counter/Timer) giảm thiểu false-positive.
   - Chụp dữ liệu đóng băng Freeze Frame Data Record và Extended Data Record tại tích tắc lỗi xảy ra.
   - Quyết định việc bật đèn cảnh báo MIL (Check Engine).

3. NVM (Non-Volatile Memory Manager):
   - Đọc/Ghi dữ liệu bất đồng bộ xuống phần cứng lưu trữ vật lý.
   - Hỗ trợ Native, Redundant (2 bản sao an toàn chống mất nguồn), Dataset blocks.
   - Tự động hóa tiến trình NvM_ReadAll lúc Startup và NvM_WriteAll lúc Shutdown xe.
   - Đảm bảo tính toàn vẹn qua cấu hình CRC16/CRC32.

4. FEE (Flash EEPROM Emulation):
   - Giả lập hành vi EEPROM (ghi nhỏ lẻ byte) trên nền tảng bộ nhớ Flash (buộc xóa sector).
   - Phân tán mức độ hao mòn số lần ghi (Wear Leveling) bảo vệ chip.
   - Tự động thu gom vùng nhớ rác (Garbage Collection) trong nền.
```

---

## 10. Bộ Câu Hỏi Phỏng Vấn (Interview Questions)

**Q1:** Sự khác biệt cốt lõi giữa hàm `NvM_WriteBlock` và `NvM_WriteAll` là gì? Khi nào dùng cái nào?
> *Trả lời:* `NvM_WriteBlock` là hàm lưu 1 block dữ liệu cụ thể một cách bất đồng bộ, thường được gọi bởi SWC khi đang chạy bình thường để lưu ngay một dữ liệu quan trọng. Trái lại, `NvM_WriteAll` là hàm lưu đồng loạt toàn bộ các block RAM bị thay đổi (có cờ Block Changed) xuống Flash. Nó chỉ được gọi một lần duy nhất bởi BSW Manager (`EcuM`) trong pha Shutdown Phase lúc tắt máy. Dùng WriteBlock liên tục quá nhiều sẽ làm mòn Flash, còn dùng WriteAll thì phải đảm bảo ECU không bị ngắt điện đột ngột trước khi quá trình ghi hàng loạt hoàn tất (cần Power Hold Relay).

**Q2:** Hãy giải thích ý nghĩa và sự liên kết của bit 3 (ConfirmedDTC) và bit 0 (TestFailed) trong DTC Status Byte?
> *Trả lời:* Bit 0 biểu thị lỗi đang thực sự xảy ra ngay tại khoảnh khắc hệ thống lấy mẫu hiện tại. Bit 3 biểu thị lỗi đã từng tồn tại đủ lâu để vượt qua bộ lọc đếm thời gian/số lần (Debounce Filter) và đã được ghi nhận chính thức vào bộ nhớ phi bốc hơi. 
> - Nếu bit 0 = 1 và bit 3 = 0: Lỗi mới chớm xuất hiện, đang chờ đếm Debounce, chưa lưu.
> - Nếu bit 0 = 1 và bit 3 = 1: Lỗi đang xảy ra và đã được ghi nhận.
> - Nếu bit 0 = 0 nhưng bit 3 = 1: Lỗi đã từng xảy ra và được xác nhận trước đây, nhưng hiện tại hệ thống cảm biến đã ổn định và không còn lỗi (Ví dụ: tuột giắc cắm nhưng thợ đã cắm lại). Lỗi này gọi là lỗi lịch sử.

**Q3:** Cơ chế Wear Leveling của module Fee hoạt động như thế nào để bảo vệ Flash khỏi hiện tượng hao mòn do ghi lặp lại?
> *Trả lời:* Module Fee tạo ra khái niệm các "Virtual Sectors". Thay vì xóa toàn bộ Sector khi có một byte thay đổi (gây tốn kém và mòn bộ nhớ), Fee sử dụng cơ chế "Chunk Allocation" để ghi nối tiếp các block mới cập nhật vào vùng trống tiếp theo của Sector hiện tại, đồng thời đánh dấu block cũ là invalid (rác). Khi Sector hiện tại đã đầy, cơ chế "Garbage Collection" sẽ kích hoạt: copy các block dữ liệu mới nhất (còn hợp lệ) sang một Sector mới, và tiến hành "Erase" toàn bộ Sector cũ để tạo vùng trống luân phiên. Điều này dàn trải chu kỳ xóa/ghi (Erase/Write cycles) luân phiên ra toàn bộ bề mặt vật lý của bộ nhớ Flash, tránh tình trạng "cháy" một vùng nhớ cụ thể.

**Q4:** NRC 0x78 (Response Pending) được gửi trong hoàn cảnh nào? Làm sao để Tester không bị treo vô hạn?
> *Trả lời:* NRC 0x78 được gửi bởi module DCM khi nó đã nhận một Request hợp lệ, nhưng quá trình thực thi cần nhiều thời gian hơn P2 timeout (ví dụ: đang gọi NvM_WriteBlock để ghi DID xuống Flash, thao tác I/O này mất hàng trăm ms). DCM sẽ phát NRC 0x78 để "xin" Tester cấp thêm thời gian P2*. Để ngăn chặn vòng lặp 0x78 vô tận khi phần cứng Flash bị treo, ta phải cấu hình thuộc tính `DcmDspMaxNumOf0x78` (số lần phát NRC 0x78 tối đa). Nếu vượt quá số lần này mà Job chưa xong, DCM tự động abort tác vụ và trả về NRC 0x10 hoặc 0x22 (General Reject), giải phóng kết nối cho Tester.
