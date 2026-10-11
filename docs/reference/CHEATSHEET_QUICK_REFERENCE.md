# AUTOSAR Quick Reference Cheatsheet

Tài liệu tra cứu nhanh (Cheatsheet) dành cho Senior BSW Integration Engineer trong quá trình code, debug, và cấu hình các module AUTOSAR.

---

## Section 1: ECU Startup Sequence (ASCII flowchart)

Trình tự khởi động chuẩn của một ECU theo kiến trúc AUTOSAR:

```text
[Power On / Hardware Reset]
         ↓
  [StartupCode]        (Assembly/C boot): Thiết lập Stack Pointer, xóa RAM, vô hiệu hóa ngắt toàn cục.
         ↓
  [Mcu_Init]           (Microcontroller Unit): Cấu hình PLL, Clock tree, Memory Controller. (Gọi Mcu_InitClock, Mcu_DistributePllClock).
         ↓
  [Port_Init]          (Port Driver): Cấu hình trạng thái các chân I/O cơ bản (GPIO, Alternate functions).
         ↓
  [EcuM_Init]          (ECU State Manager): Khởi tạo EcuM, gọi EcuM_AL_DriverInitZero (Watchdog, v.v.), EcuM_AL_DriverInitOne (MCU, Port, Dio...).
         ↓
  [BswM_Init]          (Basic Software Mode Manager): Khởi tạo Rule Engine để quản lý trạng thái BSW.
         ↓
  [StartOS]            (AUTOSAR OS): Bắt đầu hệ điều hành. Chuyển từ luồng thực thi tuyến tính sang đa nhiệm. OS tự gọi StartupHook().
         ↓
  [SchM_Init]          (Bsw Scheduler): OS bắt đầu lập lịch cho các hàm MainFunction của BSW (qua các SchM_Task).
         ↓
  [BswM_Action]        (Action List của BswM): BswM thực thi các action list để khởi tạo Communication Stack (Can_Init, CanIf_Init, PduR_Init, Com_Init).
         ↓
  [Rte_Start]          (Run-Time Environment): Mở khóa giao tiếp giữa BSW và các Software Components (SWC).
         ↓
  [Runnable]           Các Application SWC bắt đầu hoạt động (được map vào các OS Tasks định kỳ hoặc sự kiện).
```

**Notes:**
- **Ai gọi ai:** Trình tự trước `StartOS` thường được gọi bởi hàm `main()` hoặc mã khởi động của EcuM. Sau `StartOS`, mọi thứ được quản lý bởi OS Task thông qua BswM Action Lists.
- **Phase:** Pre-OS (Driver Init 0 & 1), OS Init, Post-OS (Driver Init 2 & 3).
- **Điều kiện:** Phải hoàn thành `Mcu_Init` mới được dùng Clock. Phải `StartOS` mới dùng được Event, Task, Alarm. Phải `Rte_Start` mới gửi/nhận tín hiệu Application được.

---

## Section 2: AUTOSAR OS API Quick Reference

| API | Tham số | Return | Khi nào dùng | Lỗi thường gặp |
|-----|---------|--------|--------------|----------------|
| `ActivateTask(TaskID)` | `TaskType TaskID` | `StatusType` (E_OK, E_OS_LIMIT...) | Muốn kích hoạt một Task từ Task khác hoặc ISR. (Dùng cho Basic/Extended Task). | Kích hoạt vượt quá `ACTIVATION` limit, gọi từ ISR Category 1. |
| `TerminateTask()` | *none* | `StatusType` | Kết thúc Task hiện tại. **Bắt buộc** gọi ở cuối hàm của một Task. | Quên gọi dẫn đến crash; Gọi khi vẫn đang giữ Resource (`E_OS_RESOURCE`). |
| `ChainTask(TaskID)` | `TaskType TaskID` | `StatusType` | Kết thúc Task hiện tại và kích hoạt TaskID ngay lập tức. | Giống TerminateTask, chưa nhả Resource. |
| `WaitEvent(Mask)` | `EventMaskType Mask` | `StatusType` | Extended Task tạm dừng (WAITING state) chờ Event(s). | Gọi từ Basic Task (`E_OS_ACCESS`); Gọi khi đang giữ Spinlock/Resource. |
| `SetEvent(Task, Mask)` | `TaskType TaskID, EventMaskType Mask` | `StatusType` | Đánh thức Extended Task đang đợi Event tương ứng. | Đặt Event cho Basic Task; Task bị SUSPENDED. |
| `ClearEvent(Mask)` | `EventMaskType Mask` | `StatusType` | Xóa cờ Event sau khi nhận và xử lý xong. | Không clear sẽ bị gọi lại liên tục; Clear nhầm Event của module khác. |
| `GetResource(ResID)` | `ResourceType ResID` | `StatusType` | Lock tài nguyên (vào Critical Section), chặn preempt từ Task có độ ưu tiên thấp hơn (Priority Ceiling). | Deadlock nếu dùng sai thứ tự hoặc lồng nhau sai cách. |
| `ReleaseResource(ResID)` | `ResourceType ResID` | `StatusType` | Unlock tài nguyên. | Unlock sai Resource, hoặc chưa lấy đã unlock. |
| `SetRelAlarm(AlarmID, inc, cycle)` | `AlarmType AlarmID, TickType increment, TickType cycle` | `StatusType` | Đặt báo thức tương đối. `inc`: tick ban đầu, `cycle`: tick lặp lại. | Báo thức đã được set (`E_OS_STATE`); `cycle` vượt quá max allowed. |
| `CancelAlarm(AlarmID)` | `AlarmType AlarmID` | `StatusType` | Hủy báo thức. | Hủy báo thức không hoạt động (`E_OS_NOFUNC`). |

---

## Section 3: OIL Config Quick Reference

Cú pháp chuẩn của tệp `.oil` để cấu hình hệ điều hành OSEK/AUTOSAR OS.

**1. TASK**
```oil
TASK OsTask_10ms {
    PRIORITY = 10;                     /* Độ ưu tiên (Càng cao càng ưu tiên) */
    SCHEDULE = FULL;                   /* FULL (Preemptive) / NON (Non-preemptive) */
    ACTIVATION = 1;                    /* Số lần xếp hàng kích hoạt tối đa */
    AUTOSTART = TRUE { APPMODE = AppMode1; };
    EVENT = Rte_Ev_Cyclic_10ms;        /* Liên kết với Event */
    RESOURCE = Res_SPI_Lock;           /* Resource mà Task có thể dùng */
};
```

**2. ISR (Interrupt Service Routine)**
```oil
ISR Isr_CanRx {
    CATEGORY = 2;                      /* Cat 2 dùng được OS API (SetEvent, ActivateTask) */
    PRIORITY = 20;                     /* Hardware Priority */
    SOURCE = CAN0_RX_IRQ;              /* Vector ngắt phần cứng */
};
```

**3. COUNTER & ALARM**
```oil
COUNTER SystemTimer {
    MINCYCLE = 1;
    MAXALLOWEDVALUE = 65535;
    TICKSPERBASE = 1;
};

ALARM Alarm_10ms {
    COUNTER = SystemTimer;
    ACTION = SETEVENT {
        TASK = OsTask_10ms;
        EVENT = Rte_Ev_Cyclic_10ms;
    };
    AUTOSTART = TRUE {
        ALARMTIME = 10;
        CYCLETIME = 10;
        APPMODE = AppMode1;
    };
};
```

**4. EVENT & RESOURCE**
```oil
EVENT Rte_Ev_Cyclic_10ms { MASK = AUTO; };
RESOURCE Res_SPI_Lock { RESOURCEPROPERTY = STANDARD; };
```

---

## Section 4: COM / PduR / CanIf API Quick Reference

Luồng dữ liệu: `SWC -> RTE -> COM -> PduR -> CanIf -> Can -> Hardware`

| Module | API | Purpose | Typical caller |
|--------|-----|---------|---------------|
| **COM** | `Com_SendSignal(SignalId, SignalDataPtr)` | Ghi dữ liệu vào Signal buffer trong COM. Có thể kích hoạt gửi I-PDU ngay lập tức hoặc chờ chu kỳ. | RTE (do SWC ghi tín hiệu) |
| **COM** | `Com_ReceiveSignal(SignalId, SignalDataPtr)` | Đọc dữ liệu Signal từ buffer của COM lên RTE. | RTE (do SWC đọc tín hiệu) |
| **COM** | `Com_MainFunctionRx()` | Xử lý các frame nhận (Timeout, Deadlines, Unpack). | OS Task (Bsw Scheduler) |
| **COM** | `Com_MainFunctionTx()` | Đóng gói (Pack) signals vào I-PDU và gửi xuống PduR theo chu kỳ. | OS Task (Bsw Scheduler) |
| **PduR** | `PduR_ComTransmit(TxPduId, PduInfoPtr)` | Chuyển PDU từ COM xuống module tầng dưới (vd: CanIf). PduR đóng vai trò Router. | COM |
| **CanIf** | `CanIf_Transmit(TxPduId, PduInfoPtr)` | Ánh xạ PDU ID, kiểm tra trạng thái Controller/Trcv, truyền xuống CAN Driver. | PduR |
| **CanIf** | `CanIf_SetControllerMode(ControllerId, ControllerMode)` | Chuyển đổi trạng thái kênh CAN (SLEEP, STARTED, STOPPED). Dùng để bật/tắt mạng CAN. | BswM / CanSM |
| **CAN** | `Can_Write(Hth, PduInfoPtr)` | Ghi trực tiếp vào thanh ghi Hardware Transmit (Mailbox) của CAN Controller. | CanIf |
| **CAN** | `Can_SetControllerMode(Controller, Transition)` | Thao tác ghi register vật lý để đổi trạng thái CAN Controller. | CanIf |

---

## Section 5: DCM / DEM / NvM API Quick Reference

| API | Purpose | Parameter | Return |
|-----|---------|-----------|--------|
| `Dcm_ReadDataByIdentifier` | Xử lý UDS Service 0x22 (Đọc thông số). Do Dsp xử lý hoặc pass cho SWC qua C/S Interface. | `OpStatus`, `Data` (out) | `Std_ReturnType` / `ErrorCode` |
| `Dem_SetEventStatus` | Báo cáo trạng thái Lỗi (Pass / Fail / Pre-Pass / Pre-Fail). | `EventId`, `EventStatus` | `Std_ReturnType` |
| `Dem_GetDTCByOccurrenceTime` | Lấy mã DTC theo thời điểm xảy ra (DTC mới nhất / cũ nhất). | `DTCRequest`, `DTC` (out) | `Std_ReturnType` |
| `NvM_ReadBlock` | Đọc dữ liệu từ bộ nhớ phiếm định (Flash/EEPROM) lên RAM. | `BlockId`, `NvM_DstPtr` (buf) | `Std_ReturnType` (Bất đồng bộ) |
| `NvM_WriteBlock` | Ghi dữ liệu từ RAM xuống Flash/EEPROM. | `BlockId`, `NvM_SrcPtr` (buf) | `Std_ReturnType` (Bất đồng bộ) |
| `NvM_WriteAll` | Ghi tất cả RAM Blocks xuống NV Memory trong phase tắt máy (Shutdown). | *none* | *none* (chờ BswM kiểm tra trạng thái) |
| `NvM_ReadAll` | Đọc tất cả NV Blocks lên RAM trong phase khởi động (Startup). | *none* | *none* |
| `MemIf_GetStatus` | Kiểm tra trạng thái của module NV (đang bận hay đã rảnh). | `DeviceIndex` | `MemIf_StatusType` |

---

## Section 6: UDS Service Quick Table

| Service ID | Tên | Request Format | Positive Response | Common NRC |
|-----------|-----|----------------|------------------|------------|
| **0x10** | DiagnosticSessionControl | `10 01` (Default) | `50 01` [P2, P2*] | `0x12` (SubFuncNotSupported), `0x22` (ConditionsNotCorrect) |
| **0x11** | ECUReset | `11 01` (Hard Reset) | `51 01` | `0x22` (ConditionsNotCorrect), `0x33` (SecurityAccessDenied) |
| **0x22** | ReadDataByIdentifier | `22 F1 90` (VIN) | `62 F1 90` [Data] | `0x14` (Too long), `0x22`, `0x31` (RequestOutOfRange) |
| **0x27** | SecurityAccess | `27 01` (Req Seed)<br>`27 02` [Key] (Send Key) | `67 01` [Seed]<br>`67 02` | `0x24` (RequestSequenceError), `0x35` (InvalidKey), `0x36` (ExceedAttempts) |
| **0x2E** | WriteDataByIdentifier | `2E F1 90` [Data] | `6E F1 90` | `0x22`, `0x31` (Out of Range), `0x33` (SecurityDenied) |
| **0x31** | RoutineControl | `31 01 02 03` (Start) | `71 01 02 03` | `0x22`, `0x24`, `0x33` |
| **0x14** | ClearDiagnosticInformation | `14 FF FF FF` (All) | `54` | `0x22`, `0x31` |
| **0x19** | ReadDTCInformation | `19 02` [Status Mask] | `59 02` [Mask] [DTCs] | `0x12`, `0x22`, `0x31` |
| **0x3E** | TesterPresent | `3E 00` (w/ Response) | `7E 00` | - |
| **0x28** | CommunicationControl | `28 03 01` (Disable Tx/Rx) | `68 03` | `0x22`, `0x31` |
| **0x85** | ControlDTCSetting | `85 02` (Off) | `C5 02` | `0x22`, `0x31` |

**NRC (Negative Response Code) Full Table:**

| NRC | Hex | Meaning | When triggered |
|-----|-----|---------|----------------|
| `generalReject` | `0x10` | Lỗi chung | Khi không có NRC cụ thể nào khớp. Dcm nội bộ bị lỗi. |
| `serviceNotSupported` | `0x11` | Dịch vụ không hỗ trợ | Gửi SID không tồn tại hoặc không cấu hình (VD: Gửi 0x99). |
| `subFunctionNotSupported` | `0x12` | Sub-function không hỗ trợ | Gửi Sub-function sai (VD: 10 04 nhưng không hỗ trợ session 4). |
| `incorrectMessageLengthOrInvalidFormat` | `0x13` | Độ dài thông điệp sai | Thiếu byte hoặc thừa byte (VD: Gửi 22 chỉ có 1 byte DID thay vì 2 byte). |
| `responseTooLong` | `0x14` | Phản hồi quá dài | Kích thước Data > độ dài buffer Tx (PduR buffer overflow). |
| `busyRepeatRequest` | `0x21` | Hệ thống đang bận | Module xử lý ở dưới (VD: NvM) đang bận, tester cần thử lại. |
| `conditionsNotCorrect` | `0x22` | Điều kiện không đúng | Xe đang chạy tốc độ cao nhưng đòi ECU Reset, hoặc điện áp quá thấp. |
| `requestSequenceError` | `0x24` | Sai trình tự | Gửi Key (27 02) trước khi xin Seed (27 01). |
| `requestOutOfRange` | `0x31` | Nằm ngoài phạm vi | Ghi data DID vượt ngưỡng (Ví dụ data = 200 nhưng max = 100). |
| `securityAccessDenied` | `0x33` | Từ chối bảo mật | Truy cập DID cần level Unlocked nhưng ECU đang ở Locked. |
| `invalidKey` | `0x35` | Sai khóa bảo mật | Tester gửi Key (27 02) không khớp với thuật toán. |
| `exceedNumberOfAttempts` | `0x36` | Quá số lần thử Key | Sai Key liên tục 3 lần. ECU sẽ block timer vài giây. |

---

## Section 7: ARXML Key Tags Quick Lookup

| ARXML Tag (XML) | Ý nghĩa | Ví dụ ngữ cảnh sử dụng |
|-----------------|---------|------------------------|
| `<SWC-B-SW-RUNNABLE-ENTITY>` | Định nghĩa một hàm Runnable bên trong SWC. | Chứa tag `<MINIMUM-START-INTERVAL>`, `<EVENTS>`. |
| `<SENDER-RECEIVER-INTERFACE>`| Giao diện gửi/nhận dữ liệu Data Elements. | Khai báo biến `VehicleSpeed` cho COM. |
| `<CLIENT-SERVER-INTERFACE>` | Giao diện gọi hàm RPC (Client gọi Server). | Khai báo API `SetVoltage(int vol)` cho các khối BSW. |
| `<SYSTEM-SIGNAL>` | Định nghĩa một Signal mạng logic (CAN, LIN). | Map `<SYSTEM-SIGNAL>` vào `<I-SIGNAL>`. |
| `<I-SIGNAL-TO-I-PDU-MAPPING>`| Map tín hiệu vào PDU cụ thể (bit position). | Đặt tín hiệu Speed ở byte 2, bit 0, độ dài 16 bit. |
| `<DATA-TYPE-MAPPING-SET>` | Ánh xạ kiểu dữ liệu Application (logic) sang Implementation (C data type). | Map `Speed_T` sang `uint16_t`. |
| `<ECUC-MODULE-CONFIGURATION-VALUES>`| Chứa các thông số cấu hình cụ thể cho 1 module BSW (Com, Can, Os...). | BSW Configuration (tạo ra mã C như Can_PBcfg.c). |
| `<RTE-EVENT>` | Event kích hoạt Runnable. | `<TIMING-EVENT>` (định kỳ) hoặc `<DATA-RECEIVED-EVENT>` (khi có Data). |

---

## Section 8: Common Error Codes & Meanings

**1. Standard Return Types (`Std_ReturnType`)**
- `E_OK (0x00)`: Chạy thành công.
- `E_NOT_OK (0x01)`: Chạy thất bại chung.
- `DCM_E_PENDING (0x0A)`: API chưa xong, cần gọi lại hàm này ở chu kỳ tiếp theo (Asynchronous processing). VD: Xóa Flash memory tốn nhiều thời gian.
- `RTE_E_UNCONNECTED (0x05)`: Port của SWC chưa được nối vào đâu cả (Lỗi config).

**2. DET Errors (Default Error Tracer) - Development Errors**
DET thường làm crash hệ thống nếu kích hoạt trong chế độ Debug (`Det_ReportError`).
- `CAN_E_UNINIT (0x05)`: Cố gắng gửi CAN khi chưa gọi `Can_Init()`.
- `COM_E_PARAM (0x01)`: Truyền sai tham số ID vào Com.
- `MCU_E_PARAM_CLOCK (0x0A)`: Cấu hình Clock PLL không hợp lệ.
- `OS_E_CORE (0x03)`: Thao tác OS API trên core không hợp lệ (Multicore OS).

**3. DEM Errors (Diagnostic Event Manager) - Production Errors**
- Báo cáo lỗi thật (DTC) ra ngoài cho chẩn đoán viên.
- Mẫu: `DEM_EVENT_STATUS_FAILED`, `DEM_EVENT_STATUS_PASSED`, `DEM_EVENT_STATUS_PREFAILED`.

---

## Section 9: Bit Timing Formula (CAN/CAN-FD)

Công thức chuẩn để kỹ sư cấu hình Bit Timing trong CAN Controller (Module `Can_Config`).

**Cơ bản:**
- `Time Quanta (Tq)` = Prescaler / Clock
- `Bit Time` = 1 + TS1 + TS2  (đơn vị là Tq). (1 là Sync Segment).
- **Baudrate** = 1 / (Bit Time * Tq)
  => **Baudrate** = `Clock / (Prescaler × (1 + TS1 + TS2))`

**Sample Point (Điểm lấy mẫu):**
- **Sample Point (%)** = `(1 + TS1) / (1 + TS1 + TS2) × 100%`
- Khuyến cáo: CAN thường đặt ở 80% - 87.5% tùy yêu cầu OEM. CAN-FD Data phase thường đặt ở 75% - 80%.

**Ví dụ:** Clock CAN = 80 MHz, Baudrate cần 500 kbps (Bit Time = 2us).
- Chọn Prescaler = 8 => Tq = 8 / 80M = 0.1us.
- Bit Time = 2us / 0.1us = 20 Tq.
- (1 + TS1 + TS2) = 20 => TS1 + TS2 = 19.
- Đặt TS1 = 15, TS2 = 4 (Sync=1).
- Sample Point = (1 + 15) / 20 = 80%.

---

## Section 10: Memory Layout Reference (Flash Mapping)

Cấu trúc phân bổ bộ nhớ (Flash/RAM) điển hình trong MCU AUTOSAR sử dụng Linker Script (`.ld`, `.lsl`, `.icf`).

```text
======================= FLASH (ROM) =======================
0x0000 0000 | BOOTLOADER_RESET_VECTOR  (Điểm bắt đầu)
0x0000 0100 | BOOTLOADER_CODE          (Firmware Bootloader)
-----------------------------------------------------------
0x0002 0000 | APPLICATION_RESET_VECTOR (Entry của SW)
0x0002 0400 | OS_INTERRUPT_VECTORS     (Vector Table cho OS)
0x0002 1000 | CODE_TEXT                (Mã thực thi C/C++, .text)
0x0010 0000 | CONST_DATA               (Dữ liệu hằng số, .rodata)
0x0018 0000 | CALIBRATION_DATA         (Vùng Data hiệu chỉnh A2L/XCP, PTE)
0x001F F000 | CHECKSUM / SIGNATURE     (Dữ liệu mã hóa cho Secure Boot)
===========================================================

======================== RAM (SRAM) =======================
0x2000 0000 | OS_STACK_CORE0           (Stack riêng cho từng Core/OS Task)
0x2000 1000 | OS_STACK_CORE1           (Multicore)
0x2000 2000 | DATA_BSS                 (Biến toàn cục khởi tạo = 0)
0x2001 0000 | DATA_INIT                (Biến toàn cục có khởi tạo giá trị)
0x2002 0000 | GLOBAL_NOCACHE           (Vùng DMA trực tiếp: Ethernet/CAN buffers)
0x2002 5000 | NVM_RAM_MIRROR           (Shadow buffer cho bộ nhớ NvM)
===========================================================
```

**Notes:**
- **#pragma section:** Trong mã AUTOSAR (`MemMap.h`), kỹ sư sẽ dùng các thẻ như `#define COM_START_SEC_VAR_CLEARED_8` sau đó include `Com_MemMap.h` để báo cho compiler đặt biến này vào `DATA_BSS`.
- Kỹ sư Integration phải đảm bảo `CODE_TEXT` không đè lên `CALIBRATION_DATA` và RAM không bị tràn Stack (`OS_STACK`).
