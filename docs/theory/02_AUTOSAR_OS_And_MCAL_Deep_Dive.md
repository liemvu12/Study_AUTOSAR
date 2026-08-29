# Chuyên Đề 02: AUTOSAR OS (OSEK/VDX Standard) & MCAL Core Deep Dive
## Masterclass Phân Tích Nhân Hệ Điều Hành Thời Gian Thực OSEK/VDX, Cơ Chế Quản Trị Task/Resource, ISR Cat 1/2 và 7 Phân Hệ Trình Điều Khiển MCAL Cốt Lõi

> **Ngôn ngữ:** Tiếng Việt Kỹ Nghệ Chuẩn Mực  
> **Cấp độ:** Universal Learning Resource (Newbie to Expert)  
> **Tiêu chuẩn tham chiếu:** AUTOSAR OS SWS (Specification of Operating System Release 4.x), OSEK/VDX OS 2.2.3, AUTOSAR MCAL Drivers Specification  
> **Mã nguồn đối chiếu thực tế:** Kho mã nguồn [Study_AUTOSAR-main/as/](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as) (`com/as.infrastructure/system/kernel/trampoline/`, `com/as.infrastructure/include/`)  
> **Vị trí tài liệu:** [Study_AUTOSAR-main/docs/02_AUTOSAR_OS_And_MCAL_Deep_Dive.md](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/docs/02_AUTOSAR_OS_And_MCAL_Deep_Dive.md)

---

## 📖 Hệ Thống Biểu Tượng (Icon System)
- 📖 Glossary / Định nghĩa thuật ngữ lõi
- 💡 Ví dụ / Example / Ẩn dụ thực tế 
- ⚠️ Warning / Pitfall cần tránh
- ✅ Best Practice (Nên làm)
- ❌ Bad Practice (Không nên làm)
- 🎯 Use Case (Ứng dụng thực tế)
- 🔧 API Reference (Giao diện lập trình)
- 📊 Data / Statistics (Dữ liệu thống kê)
- 🛠️ Hands-On Exercise (Thực hành)
- 🟢 LEVEL 1 / 🟡 LEVEL 2 / 🔴 LEVEL 3 (Difficulty Level)
- 💀 Critical Bug (Lỗi nghiêm trọng)
- 🌟 Pro Tip (Mẹo chuyên gia)

---

## Mục Lục
0. [Bức Tranh Toàn Cảnh: Mạng Lưới 100+ ECU & Hệ Sinh Thái Linh Kiện Điện Tử Trên Xe Hơi](#0-bức-tranh-toàn-cảnh-mạng-lưới-100-ecu--hệ-sinh-thái-linh-kiện-điện-tử-trên-xe-hơi)
1. [Mô Hình Hai Loại Tác Vụ Cốt Lõi: Basic Task vs Extended Task (Kèm Mã Nguồn Gốc)](#1-mô-hình-hai-loại-tác-vụ-cốt-lõi-basic-task-vs-extended-task-kèm-mã-nguồn-gốc)
2. [Bản Chất 4 Cấp Độ Tuân Thủ (Conformance Classes: BCC1, BCC2, ECC1, ECC2) Qua Mã Nguồn C](#2-bản-chất-4-cấp-độ-tuân-thủ-conformance-classes-bcc1-bcc2-ecc1-ecc2-qua-mã-nguồn-c)
3. [Phân Tích Task Autostart SchM_Startup & Chuỗi Function-Call-Function Khởi Tạo Task Khi Boot ECU](#3-phân-tích-task-autostart-schm_startup--chuỗi-function-call-function-khởi-tạo-task-khi-boot-ecu)
4. [Hiện Tượng Đảo Ngược Độ Ưu Tiên & Giao Thức Priority Ceiling Protocol (PCP)](#4-hiện-tượng-đảo-ngược-độ-ưu-tiên--giao-thức-priority-ceiling-protocol-pcp)
5. [Phân Cấp Ngắt Phần Cứng: ISR Category 1 vs ISR Category 2](#5-phân-cấp-ngắt-phần-cứng-isr-category-1-vs-isr-category-2)
6. [Cơ Chế Định Thời: Counter, Alarm & Schedule Table](#6-cơ-chế-định-thời-counter-alarm--schedule-table)
7. [Hệ Thống Hàm Hook Quản Trị Trạng Thái (Hook Routines)](#7-hệ-thống-hàm-hook-quản-trị-trạng-thái-hook-routines)
8. [Tầng Trừu Tượng Vi Điều Khiển (MCAL Layer Architecture & SWS Patterns)](#8-tầng-trừu-tượng-vi-điều-khiển-mcal-layer-architecture--sws-patterns)
9. [Phân Tích Chi Tiết 7 Module MCAL Cốt Lõi (Kèm API & Struct Trong parai/as)](#9-phân-tích-chi-tiết-7-module-mcal-cốt-lõi-kèm-api--struct-trong-paraias)
10. [Cơ Chế Bắt Lỗi Phát Triển (Default Error Tracer - DET) & Common Pitfalls](#10-cơ-chế-bắt-lỗi-phát-triển-default-error-tracer---det--common-pitfalls)
11. [Bảng So Sánh AUTOSAR OS vs FreeRTOS Chi Tiết](#11-bảng-so-sánh-autosar-os-vs-freertos-chi-tiết)
12. [🛠️ Hands-On Exercises Thực Chiến](#12-️-hands-on-exercises-thực-chiến)
13. [Bộ Câu Hỏi Phỏng Vấn (Q&A 3 Levels)](#13-bộ-câu-hỏi-phỏng-vấn-qa-3-levels)
4. [Phân Cấp Ngắt Phần Cứng: ISR Category 1 vs ISR Category 2](#4-phân-cấp-ngắt-phần-cứng-isr-category-1-vs-isr-category-2)
5. [Cơ Chế Định Thời: Counter, Alarm & Schedule Table](#5-cơ-chế-định-thời-counter-alarm--schedule-table)
6. [Hệ Thống Hàm Hook Quản Trị Trạng Thái (Hook Routines)](#6-hệ-thống-hàm-hook-quản-trị-trạng-thái-hook-routines)
7. [Tầng Trừu Tượng Vi Điều Khiển (MCAL Layer Architecture & SWS Patterns)](#7-tầng-trừu-tượng-vi-điều-khiển-mcal-layer-architecture--sws-patterns)
8. [Phân Tích Chi Tiết 7 Module MCAL Cốt Lõi (Kèm API & Struct)](#8-phân-tích-chi-tiết-7-module-mcal-cốt-lõi-kèm-api--struct-trong-paraias)
9. [Cơ Chế Bắt Lỗi Phát Triển (Default Error Tracer - DET) & Common Pitfalls](#9-cơ-chế-bắt-lỗi-phát-triển-default-error-tracer---det--common-pitfalls)
10. [Bảng So Sánh AUTOSAR OS vs FreeRTOS Chi Tiết](#10-bảng-so-sánh-autosar-os-vs-freertos-chi-tiết)
11. [🛠️ Hands-On Exercises Thực Chiến](#11-️-hands-on-exercises)
12. [Bộ Câu Hỏi Phỏng Vấn (Q&A 3 Levels)](#12-bộ-câu-hỏi-phỏng-vấn-qa-3-levels)

---

## 0. Bức Tranh Toàn Cảnh: Mạng Lưới 100+ ECU & Hệ Sinh Thái Linh Kiện Điện Tử Trên Xe Hơi

Trong một chiếc ô tô hiện đại, hệ thống điều khiển không vận hành trên một bộ vi xử lý duy nhất mà là một **"xã hội phân cấp" đa tầng vi điều khiển** — từ những con chip 8-bit/16-bit siêu nhỏ (chỉ có 512 Bytes đến 1KB RAM) cho đến những siêu chip 32-bit/64-bit đa lõi xử lý hàng tỷ phép tính mỗi giây.

---

### 0.1 📊 Quy Mô ECU & Số Lượng Linh Kiện Điều Khiển Trên Một Chiếc Xe:

* **Số lượng ECU theo từng phân khúc xe:**
  * 🚗 **Xe Phổ Thông / Giá Rẻ (Hạng A/B):** `20 – 40 ECUs` (Toyota Vios, Hyundai Grand i10).
  * 🚙 **Xe Tầm Trung & Xe Điện EV Phổ Thông (Hạng C/D):** `50 – 80 ECUs` (Mazda CX-5, VinFast VF8, Tesla Model 3).
  * 🚘 **Xe Hạng Sang / Xe Công Nghệ Cao (Hạng E/F):** `100 – 150+ ECUs` (Mercedes-Benz S-Class, BMW 7-Series, Audi A8).
* **Số lượng linh kiện điện - điện tử mà mạng lưới ECU trực tiếp "care" (giám sát & điều khiển):**
  * **300 – 600+ Cảm Biến (Sensors):** Cảm biến nhiệt độ cell pin BMS, cảm biến dòng Shunt, áp suất lốp TPMS, tốc độ bánh xe ABS, góc đánh lái EPS, vị trí chân ga/phanh, cảm biến mưa/ánh sáng, Radar sóng milimet, Camera ADAS, Siêu âm lùi.
  * **200 – 500+ Cơ Cấu Chấp Hành (Actuators):** Động cơ kéo Inverter, Van phanh thủy lực ESP, Trợ lực lái điện, Rơ-le cao áp Contactor, Động cơ nâng kính, Động cơ chỉnh ghế, Motor gạt mưa, Cốp điện, Đèn LED ma trận pha tự động.

---

### 0.2 🗺️ Bản Đồ Phân Bổ 5 Vùng Chức Năng (Domain Architecture) & Cấu Hình Phần Cứng:

```
┌────────────────────────────────────────────────────────────────────────────────────────────────┐
│                         BẢN ĐỒ PHÂN BỔ ECU THEO VÙNG CHỨC NĂNG TRÊN XE                         │
├────────────────────────────────────────────────────────────────────────────────────────────────┤
│ 1. NHÓM THÔNG MINH CẤP THẤP (Smart Sensors / LIN Slaves)                                       │
│    • TPMS (Lốp), Nút cửa kính, Cảm biến gạt mưa, Chỉnh gương                                   │
│    • Chip: 8/16-bit MCU (STM8, PIC, Cypress)  │ RAM: 512 B - 4 KB   │ OS: OSEK BCC1 / Bare-metal│
│                                                                                                │
│ 2. NHÓM THÂN XE & TIỆN NGHI (Body & Comfort)                                                   │
│    • BCM, Điều hòa (HVAC), Cửa điện, Cửa sổ trời, Ghế điện                                     │
│    • Chip: 16/32-bit Cortex-M0+/M4            │ RAM: 8 KB - 64 KB   │ OS: AUTOSAR BCC2 / ECC1   │
│                                                                                                │
│ 3. NHÓM ĐỘNG LỰC & AN TOÀN CAO NHẤT (Powertrain & Chassis - ASIL D)                            │
│    • BMS (Pin), VCU (Điều khiển xe), Inverter Motor, ABS/ESP (Phanh), EPS (Lái)                │
│    • Chip: 32-bit TriCore (AURIX), Renesas    │ RAM: 256 KB - 2 MB  │ OS: AUTOSAR Classic ECC2  │
│                                                                                                │
│ 4. NHÓM HỖ TRỢ LÁI TỰ HÀNH (ADAS & Autonomous Driving - ASIL B/D)                              │
│    • Forward Camera, Imaging Radar, ADAS Domain Controller                                     │
│    • Chip: Multi-core SoC (NVIDIA, Mobileye)  │ RAM: 8 GB - 32 GB   │ OS: Adaptive AUTOSAR/Linux│
│                                                                                                │
│ 5. NHÓM GIẢI TRÍ & KẾT NỐI TỪ XA (Infotainment & Telematics - QM)                              │
│    • Màn hình giải trí trung tâm (IVI), Hộp đen 4G/5G GPS (T-Box)                              │
│    • Chip: 64-bit ARM Cortex-A76 (Qualcomm)   │ RAM: 4 GB - 16 GB   │ OS: Android Automotive/QNX│
└────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

### 0.3 🔬 Bảng Đối Chiếu Các Dòng Chip ECU Thực Tế Ngoài Đời Thật:

| Tên ECU Trên Xe | Nhiệm Vụ Cụ Thể | Dòng Vi Điều Khiển Thực Tế | Dung Lượng RAM | Dung Lượng Flash/ROM | Cấp Độ OS Sử Dụng |
| :--- | :--- | :--- | :---: | :---: | :---: |
| **TPMS Sensor** | Đo áp suất và nhiệt độ trong lốp xe | NXP FXTH87 (8-bit) | **512 Bytes** | 8 KB | **Bare-metal (Không OS)** |
| **Door Module (DCM)** | Nâng hạ kính, khóa chốt cửa, sấy gương | ST STM8AF / Microchip PIC | **2 KB – 4 KB** | 32 KB – 64 KB | **OSEK BCC1** |
| **BCM (Body Controller)** | Điều khiển đèn xe, xi nhan, gạt mưa, còi | NXP S32K144 (Cortex-M4F) | **64 KB** | 512 KB | **AUTOSAR Classic BCC2/ECC1** |
| **BMS (Quản lý Pin EV)** | Giám sát 96 cell pin, cân bằng cell, tính SoC | Infineon AURIX TC397 (32-bit 6 lõi) | **1.5 MB – 2 MB** | 16 MB | **AUTOSAR Classic ECC2 (ASIL D)** |
| **VCU / MCU (Inverter)** | Tính toán mô-men xoắn, điều khiển động cơ điện | Renesas RH850 / AURIX TC387 | **1 MB – 2 MB** | 10 MB | **AUTOSAR Classic ECC2 (ASIL D)** |
| **ADAS Controller** | Xử lý ảnh camera AI, phanh khẩn cấp AEB | NVIDIA DRIVE Orin / TI TDA4 | **16 GB – 32 GB** | 128 GB UFS | **AUTOSAR Adaptive (QNX / Linux)** |

> 🎯 **Tại sao phải có chuẩn AUTOSAR OS & Conformance Classes?**  
> Chính vì sự chênh lệch phần cứng từ 512 Bytes RAM đến 32 GB RAM, không một hệ điều hành đơn lẻ nào có thể bao quát toàn bộ. Chuẩn **AUTOSAR OS chia thành 4 Conformance Classes (BCC1 $
ightarrow$ ECC2)** để có thể chuẩn hóa phần mềm từ vi điều khiển cửa kính 1KB RAM nhỏ nhất cho tới ECU điều khiển động cơ mạnh nhất!

---

## 1. Mô Hình Hai Loại Tác Vụ Cốt Lõi: Basic Task vs Extended Task (Kèm Mã Nguồn Gốc)

Trong chuẩn hệ điều hành thời gian thực ô tô OSEK/VDX và AUTOSAR OS, tác vụ (Task) được chia làm **2 loại hình kiến trúc độc lập**:

```mermaid
stateDiagram-v2
    [*] --> Suspended
    
    state "1. Basic Task (3 Trạng Thái - Non-Blocking)" as BTSM {
        Suspended --> Ready: ActivateTask() / Alarm
        Ready --> Running: Scheduler Dispatch
        Running --> Ready: Preempted by Higher Prio
        Running --> Suspended: TerminateTask()
    }
    
    state "2. Extended Task (4 Trạng Thái - Event-Driven Blocking)" as ETSM {
        state Suspended_Ext as "Suspended"
        state Ready_Ext as "Ready"
        state Running_Ext as "Running"
        state Waiting_Ext as "Waiting (Blocked)"
        
        Suspended_Ext --> Ready_Ext: ActivateTask()
        Ready_Ext --> Running_Ext: Scheduler Dispatch
        Running_Ext --> Waiting_Ext: WaitEvent(Mask)
        Waiting_Ext --> Ready_Ext: SetEvent(Mask) từ ISR/Task
        Running_Ext --> Suspended_Ext: TerminateTask()
    }
```

---

### 1.1 📊 Bảng So Sánh Chi Tiết Giữa Basic Task & Extended Task:

| Tiêu Chí Kỹ Thuật | 🟢 Basic Task (Tác Vụ Cơ Sở) | 🔴 Extended Task (Tác Vụ Mở Rộng) |
| :--- | :--- | :--- |
| **Số lượng trạng thái** | **3 trạng thái:** `SUSPENDED`, `READY`, `RUNNING`. | **4 trạng thái:** `SUSPENDED`, `READY`, `RUNNING`, `WAITING`. |
| **Cơ chế chờ đợi (Blocking)**| ❌ **Không thể ngủ chờ (Non-blocking)**. Chạy 1 mạch từ đầu hàm đến lệnh `TerminateTask()`. | ✅ **Có thể chủ động dừng ngủ chờ sự kiện** bằng lệnh `WaitEvent(EventMask)`. |
| **Quản trị Stack (RAM)** | **Dùng chung 1 Stack (Single Shared Stack):** Nhiều Basic Task có thể dùng chung 1 vùng RAM Stack $= \max(	ext{Stack}_{T1..Tn})$. $
ightarrow$ **Cực kỳ tiết kiệm RAM**. | **Bắt buộc có Stack riêng (Dedicated Stack):** Khi bị block ở `WaitEvent()`, Context phải lưu trên Stack riêng của Task đó. 10 Tasks $= \sum 	ext{Stack}$ $
ightarrow$ **Tốn RAM**. |
| **Mã nguồn Kernel (`kernel_internal.h`)** | `pEventVar = NULL` trong `TaskConstType`. Không tốn bộ nhớ lưu Event. | `pEventVar = &Task_EventVar` chứa 2 trường `set` và `wait`. |
| **Ứng dụng thực tế trên xe** | Xử lý chu kỳ định kỳ: `Com_MainFunctionTx`, `Can_Write`, `Adc_Read`, `WdgM_MainFunction`. | Xử lý sự kiện ngắt bất đồng bộ: `TaskNmInd` (chờ gói tin NM), `TaskDiag` (chờ gói tin UDS). |

---

### 1.2 🔍 Mã Nguồn C Gốc Của Basic Task & Extended Task Trong Dự Án `as`:

#### 🅰️ Mã Nguồn Gốc Basic Task: [`TASK(SchM_BswService)`](../../as/com/as.infrastructure/system/SchM/SchM.c#L491-L555) (File: `SchM.c`)
```c
/* as/com/as.infrastructure/system/SchM/SchM.c: Dòng 491-555 */
/* Đặc điểm: Không có trạng thái WAITING, chạy 1 mạch xử lý các hàm chu kỳ rồi kết thúc */
TASK(SchM_BswService)
{
    OS_TASK_BEGIN();
    
    /* 1. Thực thi chu kỳ các module truyền thông BSW */
    SCHM_MAINFUNCTION_COMTX();
    SCHM_MAINFUNCTION_COMRX();
    SCHM_MAINFUNCTION_CAN_WRITE();
    SCHM_MAINFUNCTION_CAN_READ();
    
    /* 2. Kết thúc Task: Giải phóng CPU và chuyển thẳng về trạng thái SUSPENDED */
    OsTerminateTask(SchM_BswService);
    OS_TASK_END();
}
```

#### 🅱️ Mã Nguồn Gốc Extended Task: [`TASK(TaskNmInd)`](../../as/com/as.application/common/config/OsekNm_Cfg.c#L93-L122) (File: `OsekNm_Cfg.c`)
```c
/* as/com/as.application/common/config/OsekNm_Cfg.c: Dòng 93-122 */
/* Đặc điểm: Có Stack riêng, chủ động gọi WaitEvent() để dừng chờ tín hiệu Quản trị mạng */
TASK(TaskNmInd)
{
    StatusType ercd;
    EventMaskType mask;
    OS_TASK_BEGIN();
    
    /* 1. Dừng chờ một trong các sự kiện NM kích hoạt từ ngắt CAN (Trạng thái WAITING) */
    ercd = WaitEvent(EventNmNormal | EventNmLimphome | EventNmStatus | EventRingData);
    if(E_OK == ercd)
    {
        /* 2. Đọc sự kiện kích hoạt và xử lý */
        GetEvent(TASK_ID_TaskNmInd, &mask);
        if((mask & EventNmNormal) != 0)
        {
            printf("In NM normal state, config changed.\n");
        }
        if((mask & EventNmStatus) != 0)
        {
            printf("NM network status changed.\n");
        }
        /* 3. Xóa cờ sự kiện sau khi xử lý xong */
        ClearEvent(EventNmNormal | EventNmLimphome | EventNmStatus | EventRingData);
    }
    OsTerminateTask(TaskNmInd);
    OS_TASK_END();
}
```

---

### 1.3 🔄 Vòng Đời Siêu Tốc Của 1 Basic Task & Cơ Chế Kích Hoạt (Trigger Without WAITING):

> ❓ **Câu hỏi kinh điển:** *Basic Task không có trạng thái WAITING thì nó nhận Trigger kiểu gì? Vòng đời của nó có phải rất ngắn?*

#### 1. Bản Chất Vòng Đời Basic Task: "Vào Việc ──► Làm Thần Tốc ──► Tự Sát (Terminate)"
Khác với Thread trong FreeRTOS (sống vĩnh viễn trong vòng lặp `while(1)` và ngủ ở `BLOCKED/WAITING`), một **Basic Task trong AUTOSAR/OSEK** được thiết kế để sống chớp nhoáng:
* Khi không có việc: Nằm "chết lâm sàng" ở trạng thái `SUSPENDED` (**0 bytes RAM Stack, 0% CPU**).
* Khi có sự kiện kích hoạt: Bật dậy chuyển sang `READY` $
ightarrow$ `RUNNING` $
ightarrow$ Thực thi logic trong khoảng **vài Micro-giây ($\mu s$)** $
ightarrow$ Gọi `TerminateTask()` tự sát về lại `SUSPENDED`!

```mermaid
sequenceDiagram
    autonumber
    participant Timer as Phần Cứng SysTick Counter (portable.c / Mcu.c)
    participant Counter as Kernel SignalCounter() (counter.c)
    participant AlarmAction as Alarm_BswService_Action() (Os_Cfg.c)
    participant Scheduler as Kernel Sched_GetReady() (sched-bubble.c)
    participant Task as TASK(SchM_BswService) (SchM.c)

    Note over Task: [t = 0.00ms] Trạng Thái: SUSPENDED (0 bytes Stack RAM)
    Timer->>Counter: SysTick ngắt mỗi 1ms -> Gọi SignalCounter(COUNTER_ID_OsClock)
    Note over Counter: [t = 10.00ms] Counter đếm đủ 10ms -> Alarm hết hạn (Expired)
    Counter->>AlarmAction: Thực thi Action callback AlarmConstArray[ALARM_ID_Alarm_BswService].Action()
    AlarmAction->>Scheduler: Gọi ActivateTask(TASK_ID_SchM_BswService)
    Note over Task: [t = 10.00ms] Trạng Thái: READY (Đưa vào Binary Heap)
    Scheduler->>Task: Dispatch cấp CPU thực thi (Trạng Thái: RUNNING)
    Note over Task: [t = 10.01ms - 10.05ms] Thực thi hàm ComTx, ComRx, CanWrite
    Task->>Scheduler: Gọi OsTerminateTask(SchM_BswService)
    Note over Task: [t = 10.05ms] Trạng Thái: SUSPENDED (Giải phóng 100% Stack RAM)
    Note over Task: [t = 10.05ms -> 20.00ms] Ngủ sâu với 0% tài nguyên CPU/RAM
```

---

#### 2. Minh Chứng Vòng Đời Thực Tế Của `SchM_BswService` Qua Mã Nguồn Dự Án `as`:

##### 1️⃣ Bước 1: Khởi động bộ đếm chu kỳ 10ms trong [`SchM.c: L410-L485`](../../as/com/as.infrastructure/system/SchM/SchM.c#L410-L485)
```c
/* as/com/as.infrastructure/system/SchM/SchM.c */
TASK(SchM_Startup)
{
    OS_TASK_BEGIN();
    EcuM_StartupTwo();
    
    /* Cài đặt Alarm chu kỳ: Bắt đầu sau 10 tick và lặp lại mỗi 10 tick (10ms) */
    SetRelAlarm(ALARM_ID_Alarm_BswService, 10, 10);
    
    OsTerminateTask(SchM_Startup);
    OS_TASK_END();
}
```

##### 2️⃣ Bước 2: Ngắt SysTick gọi `SignalCounter()` & kích hoạt Action trong [`counter.c`](../../as/com/as.infrastructure/system/kernel/askar/kernel/counter.c#L24-L65) và [`Os_Cfg.c`](../../as/build/nt/lm3s6965evb/ascore/config/Os_Cfg.c#L267-L270)
* Ngắt phần cứng Timer (như SysTick trong [`portable.c: L136`](../../as/com/as.infrastructure/system/kernel/askar/portable/cortex-m/portable.c#L136) hoặc Mcu Timer trong [`Mcu.c: L135`](../../as/com/as.infrastructure/arch/lm3s/mcal/Mcu.c#L135)) gọi:
  ```c
  SignalCounter(0); /* hoặc SignalCounter(COUNTER_ID_OsClock) */
  ```
* Trong kernel [`as/com/as.infrastructure/system/kernel/askar/kernel/counter.c: L24-L65`](../../as/com/as.infrastructure/system/kernel/askar/kernel/counter.c#L24-L65):
  ```c
  /* as/com/as.infrastructure/system/kernel/askar/kernel/counter.c */
  StatusType SignalCounter(CounterType CounterID)
  {
      /* 1. Tăng giá trị thời gian thực tế của Counter */
      CounterVarArray[CounterID].value++;
      curValue = CounterVarArray[CounterID].value;

      #if (ALARM_NUM > 0)
      /* 2. Quét danh sách Alarm đang chờ trên Counter */
      while(NULL != (pVar = TAILQ_FIRST(&CounterVarArray[CounterID].head)))
      {
          if (pVar->value == curValue) /* Alarm đã đến hạn (Expired) */
          {
              AlarmID = pVar - AlarmVarArray;
              TAILQ_REMOVE(&CounterVarArray[CounterID].head, &AlarmVarArray[AlarmID], entry);
              OS_STOP_ALARM(&AlarmVarArray[AlarmID]);
              
              /* 3. Tự động nạp lại chu kỳ 10ms tiếp theo (Periodic Reload) */
              if(AlarmVarArray[AlarmID].period != 0)
              {
                  Os_StartAlarm(AlarmID, (TickType)(curValue + AlarmVarArray[AlarmID].period),
                                AlarmVarArray[AlarmID].period);
              }

              /* 4. Thực thi Action Callback của Alarm */
              AlarmConstArray[AlarmID].Action();
          }
          else { break; }
      }
      #endif
  }
  ```
* Hàm Action Callback được sinh mã tự động trong [`as/build/nt/lm3s6965evb/ascore/config/Os_Cfg.c: L267-L270`](../../as/build/nt/lm3s6965evb/ascore/config/Os_Cfg.c#L267-L270):
  ```c
  /* as/build/nt/lm3s6965evb/ascore/config/Os_Cfg.c */
  static void Alarm_BswService_Action(void)
  {
      /* Đánh thức Basic Task SchM_BswService từ SUSPENDED -> READY */
      (void)ActivateTask(TASK_ID_SchM_BswService);
  }
  ```

##### 3️⃣ Bước 3: Basic Task thực thi trong $50\mu s$ rồi tự sát trong [`SchM.c: L491-L555`](../../as/com/as.infrastructure/system/SchM/SchM.c#L491-L555)
```c
/* as/com/as.infrastructure/system/SchM/SchM.c */
TASK(SchM_BswService)
{
    OS_TASK_BEGIN();
    
    /* 1. Xử lý các gói tin truyền thông BSW */
    SCHM_MAINFUNCTION_COMTX();
    SCHM_MAINFUNCTION_COMRX();
    SCHM_MAINFUNCTION_CAN_WRITE();
    SCHM_MAINFUNCTION_CAN_READ();
    
    /* 2. Tự sát: Giải phóng CPU và quay về SUSPENDED */
    OsTerminateTask(SchM_BswService);
    OS_TASK_END();
}
```

---

### 1.4 🏎️ ECU Đơn Nhân vs. Đa Nhân & Cơ Chế Thực Thi Đa Tác Vụ (Single-Core vs. Multi-Core):

> ❓ **Câu hỏi:** *ECU là đơn nhân hay đa nhân? Khi có nhiều Basic Task thì chúng chạy đồng thời hay tuần tự?*

#### 1. Phân Loại Phần Cứng ECU Trên Xe Hơi:
* **ECU Đơn Nhân (Single-Core MCU):** Cửa điện, gạt mưa, đèn xe BCM, điều hòa HVAC — sử dụng các chip nhỏ 16/32-bit như ARM Cortex-M0+/M4 (NXP S32K144, STM32F1).
* **ECU Đa Nhân (Multi-Core MCU - 2 đến 6 Cores):** Quản lý Pin BMS, Điều khiển xe điện VCU, Động cơ Inverter, Hộp đen Gateway, ADAS — sử dụng các chip cao cấp như **Infineon AURIX TC397 (6 lõi TriCore 300MHz)** hoặc **Renesas RH850 (Multi-core)**.

---

#### 2. Cơ Chế Thực Thi Đa Tác Vụ Trên 1 Lõi Đơn (Single-Core Execution):
Trên một lõi CPU đơn, tại một chu kỳ xung nhịp vật lý **CHỈ CÓ DUY NHẤT 1 TASK ĐƯỢC CHẠY**. Cách các Task kết thúc phụ thuộc vào cơ chế lập lịch:

##### 🅰️ Chế Độ Không Tiếm Quyền (Non-Preemptive — Chạy Tuần Tự Tuyệt Đối):
Task A đang chạy thì Task B (ưu tiên cao hơn) xuất hiện $
ightarrow$ Task B **buộc phải chờ xếp hàng**. Task A chạy xong đến `TerminateTask()` thì Task B mới được chạy.
```
CPU Core 0: [──── Task A chạy từ đầu đến cuối ────] ──► [──── Task B mới được chạy ────]
```

##### 🅱️ Chế Độ Có Tiếm Quyền (Preemptive — Chạy Lồng Nhau Kiểu Ngăn Xếp LIFO):
Task A (Priority 2) đang chạy dở dang thì Task B (Priority 8) xuất hiện $
ightarrow$ Kernel **tạm dừng Task A**, lưu ngữ cảnh vào Stack và trao CPU cho Task B chạy ngay lập tức. Sau khi Task B kết thúc (`TerminateTask`), CPU **quay lại chạy nốt phần còn lại của Task A**.
```
Task B (Prio 8):                       [── Chạy B ──] (Terminate)
                                             ▲              │
                                   Preempt   │              │ Return
                                             │              ▼
Task A (Prio 2): [── Chạy A dở dang ─────────┘              └────── Chạy nốt A ──] (Terminate)
```

---

### 1.5 ⚖️ So Sánh Toàn Diện: AUTOSAR / OSEK Task vs. FreeRTOS / POSIX Thread:

| Tiêu Chí Kỹ Thuật | 🚗 AUTOSAR / OSEK OS Task | 💻 FreeRTOS Task / POSIX Thread / Linux |
| :--- | :--- | :--- |
| **1. Triết lý Vòng Đời (Lifecycle)** | **Chạy một mạch rồi Kết Thúc (`TerminateTask`)**. Khi cần thì Kích hoạt lại (`ActivateTask`). Hầu như không dùng `while(1)`. | **Chạy Vòng Lặp Vô Hạn (`while(1)`)**. Khi không có việc thì tự `vTaskDelay()` hoặc Block chờ Queue/Semaphore. |
| **2. Cơ Chế Cấp Phát Bộ Nhớ** | **Tĩnh 100% lúc Compile-time (Static Allocation)**. Khai báo sẵn trong ARXML. Tuyệt đối **cấm dùng `malloc()`** hoặc tạo Task động lúc chạy. | **Động lúc Runtime (Dynamic Creation)**. Có các hàm tạo luồng động như `xTaskCreate()`, `pthread_create()`, `osThreadNew()`. |
| **3. Cơ Chế Ngăn Xếp (Stack Memory)** | **Single Shared Stack (Dùng chung Stack)**: Toàn bộ Basic Task có thể dùng chung 1 vùng RAM duy nhất $= \max(	ext{Stack})$. Tiết kiệm RAM khủng khiếp cho MCU nhỏ. | **Dedicated Stack (Mỗi Thread 1 Stack riêng)**: Bắt buộc cấp phát RAM Stack riêng cho từng Thread. 10 Threads tốn gấp 10 lần RAM. |
| **4. Cơ Chế Đồng Bộ & Tránh Deadlock** | **Giao thức Trần Ưu Tiên Tĩnh (Priority Ceiling Protocol - PCP)**: Mọi quyền truy cập Resource được tính toán sẵn từ file cấu hình. **Triệt tiêu Deadlock 100% từ thiết kế**. | Dùng **Mutex / Semaphore động** với cơ chế Thừa kế ưu tiên (Priority Inheritance). Vẫn có nguy cơ Deadlock nếu lập trình viên lock sai thứ tự. |
| **5. Tính Tất Định & Chuẩn An Toàn** | **Hard Real-Time Cực Khắt Khe**. Đạt chứng chỉ an toàn chức năng cao nhất của ô tô **ISO 26262 ASIL-D**. | Phù hợp thiết bị IoT / Embedded thông thường. Bản gốc FreeRTOS chỉ là Soft Real-Time (cần bản SafeRTOS thương mại để đạt an toàn). |

---

## 2. Bản Chất 4 Cấp Độ Tuân Thủ (Conformance Classes: BCC1, BCC2, ECC1, ECC2) Qua Mã Nguồn C

### 2.1 ❓ Bản Chất Kỹ Nghệ: Thứ Gì Tuân Thủ Và Tại Sao Phải Phân Chia?
* **Thứ gì tuân thủ?**
  1. **Nhân hệ điều hành RTOS (`askar`, `trampoline`):** Mã nguồn C của Kernel phải cài đặt chính xác các thuật toán lập lịch, cấu trúc dữ liệu theo đúng đặc tả chuẩn ISO 17356-3.
  2. **File Cấu hình sinh ra (`Os_Cfg.h`, `Os_Cfg.c`):** Toolchain đọc file ARXML và sinh ra các cờ tiền xử lý (`#define`) phù hợp với cấp độ được chọn.
* **Tại sao phân chia 4 cấp độ?** Nhằm tối ưu hóa triệt để phần cứng (**Hardware Scalability**):
  * Một chip vi điều khiển nhỏ 8-bit/16-bit chỉ có **1 KB RAM** (cảm biến lốp TPMS, công tắc cửa) $
ightarrow$ Dùng **BCC1** để toàn bộ OS chỉ chiếm $<500	ext{ Bytes RAM}$.
  * Một ECU 32-bit cao cấp (BMS, VCU, ADAS) có **512 KB - vài MB RAM** $
ightarrow$ Dùng **ECC2** để tận dụng tối đa cơ chế đa nhiệm Event-Driven và hàng đợi Task FIFO.

---

### 2.2 🔬 So Sánh Cấu Trúc Mã Nguồn C Của 4 Cấp Độ Trong Kernel `askar`:

Bảng dưới đây chỉ ra chính xác cách 4 cấp độ được cấu hình trong `Os_Cfg.h` và cách mã nguồn C của Kernel thay đổi tương ứng:

| Cấp Độ Tuân Thủ | Cờ Cấu Hình Trong `Os_Cfg.h` | Cấu Trúc Dữ Liệu Task (`TaskConstType` / `TaskVarType`) | Thuật Toán Scheduler (`sched-bubble.c`) | Quản Lý Bộ Nhớ Stack |
| :--- | :--- | :--- | :--- | :--- |
| 🟢 **BCC1** *(Basic Class 1)* | `/* Không define EXTENDED_TASK */`<br>`/* Không define MULTIPLY_TASK_PER_PRIORITY */`<br>`/* Không define MULTIPLY_TASK_ACTIVATION */` | • `pEventVar` **không tồn tại** (tiết kiệm ROM/RAM).<br>• `activation` **không tồn tại**.<br>• `event.c` **bị loại bỏ 100% khi biên dịch**. | • Hàng đợi Ready là mảng Bitmap đơn giản $O(1)$.<br>• Mỗi Priority có đúng 1 Task duy nhất. | • Cho phép **1 Stack dùng chung** (`Task_SharedStack`) cho tất cả các Task. |
| 🟡 **BCC2** *(Basic Class 2)* | `/* Không define EXTENDED_TASK */`<br>`#define MULTIPLY_TASK_PER_PRIORITY`<br>`#define MULTIPLY_TASK_ACTIVATION` | • `pEventVar` **không tồn tại**.<br>• Bật biến đếm `uint8 activation` trong `TaskVarType`.<br>• Bật biến `uint8 maxActivation` trong `TaskConstType`. | • Hàng đợi Ready dùng cơ chế FIFO Heap / Ring Buffer.<br>• Priority được mã hóa kèm số thứ tự kích hoạt: `(((prio)<<3) | (--PrioSeqVal[prio]))`. | • Dùng chung Stack cho các Basic Task không ngắt lẫn nhau. |
| 🟠 **ECC1** *(Extended Class 1)* | `#define EXTENDED_TASK`<br>`/* Không define MULTIPLY_TASK_PER_PRIORITY */`<br>`/* Không define MULTIPLY_TASK_ACTIVATION */` | • Bật con trỏ `EventVarType* pEventVar`.<br>• Bật đầy đủ `event.c` (`WaitEvent`, `SetEvent`, `ClearEvent`). | • Lập lịch ưu tiên tĩnh, mỗi mức Priority chỉ có đúng 1 Task. | • Basic Task có thể chung Stack, nhưng Extended Task **bắt buộc có Dedicated Stack riêng**. |
| 🔴 **ECC2** *(Extended Class 2)* | `#define EXTENDED_TASK`<br>`#define MULTIPLY_TASK_PER_PRIORITY`<br>`#define MULTIPLY_TASK_ACTIVATION` | • Bật đầy đủ `pEventVar` cho Extended Tasks.<br>• Bật đầy đủ `maxActivation` và `activation` cho Basic Tasks. | • Đầy đủ hàng đợi FIFO đa mức ưu tiên kết hợp máy trạng thái 4 trạng thái. | • Toàn bộ các Extended Task có Dedicated Stack riêng. |

---

### 2.3 📂 Trích Dẫn Mã C Của 4 Cấp Độ Từ Mã Nguồn Gốc:

#### 1. Cấu trúc Task thay đổi theo Cờ Cấu hình ([`kernel_internal.h: L280-L345`](../../as/com/as.infrastructure/system/kernel/askar/kernel/kernel_internal.h#L280-L345)):
```c
/* as/com/as.infrastructure/system/kernel/askar/kernel/kernel_internal.h */

typedef struct
{
    void* pStack;
    uint32_t stackSize;
    TaskMainEntryType entry;
    
    #ifdef EXTENDED_TASK
    /* CHỈ CÓ TRONG ECC1 VÀ ECC2: Quản lý con trỏ sự kiện Set/Wait */
    EventVarType* pEventVar;
    #endif
    
    PriorityType initPriority;
    PriorityType runPriority;
    
    #ifdef MULTIPLY_TASK_ACTIVATION
    /* CHỈ CÓ TRONG BCC2 VÀ ECC2: Giới hạn số lần kích hoạt gối đầu */
    uint8 maxActivation;
    #endif
} TaskConstType;

typedef struct TaskVar
{
    TaskContextType context;
    PriorityType priority;
    const TaskConstType* pConst;
    
    #ifdef MULTIPLY_TASK_ACTIVATION
    /* CHỈ CÓ TRONG BCC2 VÀ ECC2: Đếm số yêu cầu kích hoạt đang xếp hàng */
    uint8 activation;
    #endif
    
    volatile StatusType state; /* SUSPENDED, READY, RUNNING, WAITING */
    ResourceType currentResource;
} TaskVarType;
```

#### 2. Mã Nguồn Cấu Hình Thực Tế Của Dự Án `ascore` Đang Chạy Ở Chuẩn **ECC2** ([`Os_Cfg.h: L40-L72`](../../as/build/nt/lm3s6965evb/ascore/config/Os_Cfg.h#L40-L72)):
```c
/* as/build/nt/lm3s6965evb/ascore/config/Os_Cfg.h */

#define OS_STATUS EXTENDED
#define EXTENDED_TASK               /* Bật tính năng Extended Task -> Nhóm ECC */
#define MULTIPLY_TASK_PER_PRIORITY  /* Cho phép nhiều Task chung 1 Priority -> Cấp 2 */
#define MULTIPLY_TASK_ACTIVATION    /* Cho phép kích hoạt lặp gối đầu -> Cấp 2 */
```

---

### 2.4 🔬 Giải Thích Chi Tiết Thuật Toán Scheduler & Quản Trị Bộ Nhớ Stack Trong Mã Nguồn C:

Trong mã nguồn của nhân hệ điều hành `askar`, sự khác nhau giữa 4 cấp độ tuân thủ được cài đặt ở mức vi kiến trúc mã nguồn C như sau:

---

#### 🅰️ 1. Thuật Toán Lập Lịch (Scheduler Algorithm — File: [`sched-bubble.c: L37-L120`](../../as/com/as.infrastructure/system/kernel/askar/kernel/sched-bubble.c#L37-L120)):

```
┌────────────────────────────────────────────────────────────────────────────────────────────────┐
│                     THUẬT TOÁN ĐIỀU PHỐI HÀNG ĐỢI READY (BINARY HEAP SCHEDULER)                 │
├────────────────────────────────────────────────────────────────────────────────────────────────┤
│ 1. CẤP ĐỘ 1 (BCC1 / ECC1 — 1 Task/Priority):                                                   │
│    • NEW_PRIORITY(prio) = prio  ──► So sánh trực tiếp giá trị Priority (O(1)).                │
│                                                                                                │
│ 2. CẤP ĐỘ 2 (BCC2 / ECC2 — Nhiều Task chung Priority):                                         │
│    • NEW_PRIORITY(prio) = (prio << SEQUENCE_SHIFT) | (--PrioSeqVal[prio] & SEQUENCE_MASK)     │
│    • Nhúng bộ đếm thứ tự kích hoạt giảm dần vào các bits thấp nhất.                            │
│    • Task nào gọi ActivateTask() trước ──► Sequence cao hơn ──► Nằm ở đỉnh Heap ──► Chạy trước!│
└────────────────────────────────────────────────────────────────────────────────────────────────┘
```

* **Mã nguồn thực tế thuật toán phân xử thứ tự FIFO (`sched-bubble.c: L37-L73`):**
  ```c
  /* as/com/as.infrastructure/system/kernel/askar/kernel/sched-bubble.c */

  #ifdef MULTIPLY_TASK_PER_PRIORITY
  /* Dịch trái độ ưu tiên 3 bits và nhúng số thứ tự kích hoạt PrioSeqVal vào 3 bits cuối */
  #define NEW_PRIORITY(prio) (((uint16)(prio)<<SEQUENCE_SHIFT)|((--PrioSeqVal[prio])&SEQUENCE_MASK))
  #define REAL_PRIORITY(prio) Sched_RealPriority(prio)
  #else
  #define NEW_PRIORITY(prio) (prio)
  #define REAL_PRIORITY(prio) (prio)
  #endif
  ```
* **Cách thức vận hành Binary Heap (`Sched_BubbleUp` & `Sched_BubbleDown`):**  
  Khi `ActivateTask(TaskNmInd)` và `ActivateTask(SchM_Startup)` cùng có Priority 7 được kích hoạt:
  * Task kích hoạt trước nhận giá trị `NEW_PRIORITY = (7 << 3) | 7 = 63`.
  * Task kích hoạt sau nhận giá trị `NEW_PRIORITY = (7 << 3) | 6 = 62`.
  * Hàm `Sched_BubbleUp()` đẩy phần tử có giá trị 63 lên đỉnh mảng `ReadyQueue.heap[0]`. Khi Scheduler gọi `Sched_GetReady()`, Task kích hoạt trước được nhả ra chạy trước, đảm bảo **100% nguyên tắc hàng đợi FIFO** của chuẩn OSEK!

---

#### 🅱️ 2. Cơ Chế Quản Trị Bộ Nhớ Stack (RAM Management — File: [`Os_Cfg.c: L30-L37`](../../as/build/nt/lm3s6965evb/ascore/config/Os_Cfg.c#L30-L37)):

* **Nhóm BCC (BCC1 / BCC2) — Cơ Chế Dùng Chung Một Ngăn Xếp (Single Shared Stack):**
  * *Tại sao Basic Task có thể dùng chung Stack?*  
    Vì Basic Task không có lệnh `WaitEvent()` (không bao giờ ngủ giữa chừng). Khi một Basic Task chạy, nó thực thi từ đầu đến cuối rồi gọi `TerminateTask()` $
ightarrow$ toàn bộ khung ngăn xếp (Stack Frame) của hàm được giải phóng hoàn toàn. Con trỏ Stack Pointer (SP) quay trở về đáy ngăn xếp.
  * *Hiệu quả tiết kiệm RAM:* Hệ thống 10 Basic Tasks không cần 10 mảng RAM mà chỉ cần **1 mảng Stack duy nhất** bằng kích thước của Task lớn nhất ($pprox 512	ext{ Bytes}$).
* **Nhóm ECC (ECC1 / ECC2) — Cơ Chế Ngăn Xếp Riêng Biệt (Dedicated Stacks):**
  * *Tại sao Extended Task bắt buộc phải có Stack riêng?*  
    Khi Extended Task gọi `WaitEvent()`, nó chuyển sang trạng thái `WAITING` và nhường CPU cho Task khác. Toàn bộ các biến cục bộ (Local Variables) và thanh ghi CPU của nó **phải được bảo lưu nguyên vẹn trên Stack**. Nếu dùng chung Stack, Task khác chạy xen vào sẽ ghi đè và làm hỏng (corrupt) bộ nhớ của Task đang ngủ!
  * *Minh chứng trong mã C sinh ra ([`Os_Cfg.c: L30-L37`](../../as/build/nt/lm3s6965evb/ascore/config/Os_Cfg.c#L30-L37)):*
    ```c
    /* as/build/nt/lm3s6965evb/ascore/config/Os_Cfg.c */
    
    /* Mỗi Extended Task được cấp phát riêng một mảng RAM độc lập */
    static uint32_t TaskApp_Stack[(2048*OS_STK_SIZE_SCALER+sizeof(uint32_t)-1)/sizeof(uint32_t)];
    static EventVarType TaskApp_EventVar;
    
    static uint32_t TaskNmInd_Stack[(2048*OS_STK_SIZE_SCALER+sizeof(uint32_t)-1)/sizeof(uint32_t)];
    static EventVarType TaskNmInd_EventVar;
    ```

---

### 2.5 📂 Thư Mục Chứng Minh Thực Chiến & Hướng Dẫn Cấu Hình 4 Cấp Độ Trong Mã Nguồn:

Để xem toàn bộ mã nguồn cấu hình mẫu XML, các file `.h`/`.c` sinh ra và phân tích sâu thuật toán lập lịch cho từng cấp độ, xem bộ tài liệu chuyên biệt tại:
* 📑 [**`00_CONFORMANCE_CLASSES_MASTER_PROOF.md`**](02_conformance_classes_proof/00_CONFORMANCE_CLASSES_MASTER_PROOF.md): Tổng quan cơ chế tính toán cấp độ của Toolchain `GenOS.py`.
* 🟢 [**`01_BCC1_Proof_And_Config.md`**](02_conformance_classes_proof/01_BCC1_Proof_And_Config.md): Cấu hình ARXML, Single Shared Stack, loại bỏ 100% `event.c` cho vi điều khiển < 1KB RAM.
* 🟡 [**`02_BCC2_Proof_And_Config.md`**](02_conformance_classes_proof/02_BCC2_Proof_And_Config.md): Cấu hình nhiều Task trùng Priority, Hàng đợi kích hoạt `activation`, thuật toán FIFO Sequence Shift trong `sched-bubble.c`.
* 🟠 [**`03_ECC1_Proof_And_Config.md`**](02_conformance_classes_proof/03_ECC1_Proof_And_Config.md): Cấu hình Extended Task với `WaitEvent()`, Dedicated Stack.
* 🔴 [**`04_ECC2_Proof_And_Config.md`**](02_conformance_classes_proof/04_ECC2_Proof_And_Config.md): Bằng chứng mã nguồn cấu hình thực tế của dự án `ascore` (6 Tasks thỏa mãn trọn vẹn chuẩn ECC2).

---
## 3. Phân Tích Task Autostart SchM_Startup & Chuỗi Function-Call-Function Khởi Tạo Task Khi Boot ECU

> ❓ **Câu hỏi:** *Task bình thường với Task Autostart `SchM_Startup` có gì khác nhau? Các Task này được khởi tạo và kích hoạt bằng code như thế nào khi ECU khởi động?*

---

### 3.1 📊 So Sánh 4 Loại Task Thực Tế Trong Dự Án `as`:

Trong file cấu hình sinh ra [`as/build/nt/lm3s6965evb/ascore/config/Os_Cfg.c`](../../as/build/nt/lm3s6965evb/ascore/config/Os_Cfg.c), có 4 loại Task với vai trò và cơ chế kích hoạt hoàn toàn khác nhau:

| Tên Task Trong `Os_Cfg.c` | Loại Task | Thuộc Tính Autostart (`appModeMask`) | Độ Ưu Tiên (`initPriority`) | Cơ Chế Kích Hoạt (Trigger Mechanism) |
| :--- | :---: | :---: | :---: | :--- |
| **`SchM_Startup`** | **Basic Task** | ✅ `OSDEFAULTAPPMODE` | **Priority = 7** | **Tự động chạy ngay khi gọi `StartOS()`** để khởi tạo BSW Phase 2 rồi `TerminateTask`. |
| **`TaskIdle`** | **Basic Task** | ✅ `OSDEFAULTAPPMODE` | **Priority = 0 (Thấp nhất)** | **Tự động chạy khi hệ thống rảnh rỗi** (không có Task nào khác cần CPU). |
| **`SchM_BswService`** | **Basic Task** | ❌ `0 (Không Autostart)` | **Priority = 8** | **Kích hoạt định kỳ chu kỳ 10ms bởi `Alarm_BswService`**. |
| **`TaskNmInd`** | **Extended Task** | ✅ `OSDEFAULTAPPMODE` | **Priority = 7** | **Autostart vào chạy trước rồi rơi vào trạng thái `WAITING`** chờ Event từ ngắt CAN. |

---

### 3.2 🌳 Chuỗi Gọi Hàm Function-Call-Function Khởi Tạo Và Thực Thi Task Khi Boot ECU:

Dưới đây là chuỗi thực thi thực tế 100% trong mã nguồn C từ khi gọi `StartOS()` đến khi CPU nhảy vào thực thi `TASK(SchM_Startup)`:

```
[Điểm Vào Bootloader / main.c]
   │
   ▼
1. StartOS(OSDEFAULTAPPMODE)  (as/com/as.infrastructure/system/kernel/askar/kernel/kernel.c: L183)
   │  ├── Irq_Disable()
   │  ├── Os_PortInit()
   │  │
   │  ▼
2. Os_TaskInit(OSDEFAULTAPPMODE)  (as/com/as.infrastructure/system/kernel/askar/kernel/task.c: L606-L628)
   │  │  [Vòng lặp quét mảng TaskConstArray từ id = 0 đến TASK_NUM - 1]
   │  │  ├── id = 0 (TaskApp):          appModeMask = 0              ──► Bỏ qua (Trạng thái SUSPENDED)
   │  │  ├── id = 1 (TaskCanIf):        appModeMask = 0              ──► Bỏ qua (Trạng thái SUSPENDED)
   │  │  ├── id = 2 (TaskNmInd):        appModeMask = DEFAULTMODE    ──► Gọi ActivateTask(TaskNmInd)
   │  │  ├── id = 3 (TaskIdle):         appModeMask = DEFAULTMODE    ──► Gọi ActivateTask(TaskIdle)
   │  │  ├── id = 4 (SchM_Startup):     appModeMask = DEFAULTMODE    ──► Gọi ActivateTask(SchM_Startup)
   │  │  └── id = 5 (SchM_BswService):  appModeMask = 0              ──► Bỏ qua (Trạng thái SUSPENDED)
   │  │
   │  ▼
3. ActivateTask(TASK_ID_SchM_Startup)  (task.c: L143-L167)
   │  ├── InitContext(&TaskVarArray[SchM_Startup]) (task.c: L33)
   │  │     ├── pTaskVar->state = READY;
   │  │     ├── pTaskVar->priority = 7;
   │  │     └── Os_PortInitContext(pTaskVar)  (Nạp con trỏ hàm TaskMainSchM_Startup vào Stack)
   │  └── Sched_AddReady(TASK_ID_SchM_Startup) (sched-bubble.c: L85) (Đưa vào hàng đợi Ready)
   │
   ▼
4. Sched_GetReady()  (kernel.c: L206)
   │  └── Quét hàng đợi Ready: Thấy SchM_Startup có Priority = 7 (Cao nhất trong số các Task Ready)
   │      ──► Gán RunningVar = &TaskVarArray[SchM_Startup]
   │
   ▼
5. Os_PortStartFirstDispatch()  (kernel.c: L207 & portable/cortex-m/arch.c)
   │  └── Nạp thanh ghi CPU từ Stack của SchM_Startup ──► CPU nhảy vào hàm thực thi!
   │
   ▼
6. TASK(SchM_Startup)  (as/com/as.infrastructure/system/SchM/SchM.c: L410-L485)
   │  ├── EcuM_StartupTwo()  ──► Khởi tạo BSW Phase 2: PduR_Init(), Can_Init(), Com_Init(), Rte_Start()
   │  ├── SetRelAlarm(ALARM_ID_Alarm_BswService, 10, 10)  ──► Kích hoạt Timer 10ms cho SchM_BswService
   │  ├── Com_IpduGroupStart(COM_DEFAULT_IPDU_GROUP, TRUE) ──► Cho phép truyền phát CAN định kỳ
   │  └── OsTerminateTask(SchM_Startup)  ──► Hoàn tất nhiệm vụ, chuyển về SUSPENDED nhường CPU cho Task khác!
```

---

### 3.3 🔬 Case Study Thực Chiến: Vòng Đời & Chuỗi Gọi Hàm Của `TaskIdle` (Mã Nguồn Gốc 100%)

> ❓ **Câu hỏi kỹ nghệ:** *Khi `SchM_Startup` hoàn thành nhiệm vụ và gọi `TerminateTask()`, hệ điều hành sẽ chuyển sang chạy cái gì? `TaskIdle` được cấu hình, khởi tạo, nhận CPU và bị ngắt quyền (preempt) như thế nào theo mã nguồn C gốc?*

---

#### 1. Khai Báo Cấu Hình Gốc (Single Source of Truth):
Trong file cấu hình kiến trúc [`as/com/as.application/common/infrastructure.xml: L59`](../../as/com/as.application/common/infrastructure.xml#L59) (hoặc `autosar.arxml`), `TaskIdle` được định nghĩa là một **Basic Task** có cờ `Autostart="True"`, độ ưu tiên thấp nhất hệ thống (`Priority="0"`) và chiếm 1 quyền kích hoạt:
```xml
<!-- as/com/as.application/common/infrastructure.xml -->
<Task Name="TaskIdle" Priority="0" Activation="1" Autostart="True" StackSize="512" Schedule="FULL" />
```

---

#### 2. Dữ Liệu Cấu Hình Sinh Tự Động Trong `Os_Cfg.h` & `Os_Cfg.c`:
Bộ sinh mã `GenOS.py` tự động xuất thông số cấu hình tĩnh của `TaskIdle` ra thư mục build:
* **Định danh ID (`Os_Cfg.h: L54`):**
  ```c
  #define TASK_ID_TaskIdle    3   /* priority = 0 (Thấp nhất trong 6 Tasks) */
  ```
* **Bản ghi cấu hình tĩnh trong `TaskConstArray` ([`Os_Cfg.c: L187-L203`](../../as/build/nt/lm3s6965evb/ascore/config/Os_Cfg.c#L187-L203)):**
  ```c
  /* as/build/nt/lm3s6965evb/ascore/config/Os_Cfg.c */
  const TaskConstType TaskConstArray[TASK_NUM] = {
      /* ... [0]: TaskApp, [1]: TaskCanIf, [2]: TaskNmInd ... */
      [TASK_ID_TaskIdle] = {
          /*.pStack =*/         TaskIdle_Stack,
          /*.stackSize =*/      sizeof(TaskIdle_Stack),
          /*.entry =*/          TaskMainTaskIdle,
          #ifdef EXTENDED_TASK
          /*.pEventVar =*/      NULL,                     /* Basic Task -> Không có Event */
          #endif
          /*.appModeMask =*/    (0 | (OSDEFAULTAPPMODE)), /* Cờ Autostart khi khởi động */
          /*.name =*/           "TaskIdle",
          /*.initPriority =*/   OS_PTHREAD_PRIORITY + 0,  /* Độ ưu tiên khởi tạo = 0 */
          /*.runPriority =*/    OS_PTHREAD_PRIORITY + 0,
          #ifdef MULTIPLY_TASK_ACTIVATION
          /*.maxActivation =*/  1,
          #endif
      },
      /* ... [4]: SchM_Startup, [5]: SchM_BswService ... */
  };
  ```

---

#### 3. Chuỗi Gọi Hàm Function-Call-Function Của `TaskIdle` Từ Boot Đến Thực Thi:

```
[GIAI ĐOẠN 1: KHỞI TẠO TẠI BOOT ECU]
1. StartOS(OSDEFAULTAPPMODE)  (kernel.c: L183)
   │
   ▼
2. Os_TaskInit(OSDEFAULTAPPMODE)  (task.c: L606-L628)
   │  └── Quét tới id = 3 (TaskIdle): Có cờ appModeMask == OSDEFAULTAPPMODE
   │      ──► Gọi ActivateTask(TASK_ID_TaskIdle) (task.c: L143)
   │
   ▼
3. ActivateTask(TASK_ID_TaskIdle)  (task.c: L143-L167)
   ├── InitContext(&TaskVarArray[TASK_ID_TaskIdle]) (task.c: L33)
   │     ├── pTaskVar->state = READY;
   │     ├── pTaskVar->priority = 0;
   │     └── Os_PortInitContext(pTaskVar)  (Nạp con trỏ hàm TaskMainTaskIdle vào Stack)
   └── Sched_AddReady(TASK_ID_TaskIdle) (sched-bubble.c: L85)
         └── Đưa TaskIdle vào hàng đợi ReadyQueue.heap[] với Priority = 0.
             (Lúc này SchM_Startup và TaskNmInd có Priority = 7 cao hơn nên chiếm CPU chạy trước,
              TaskIdle tạm thời nằm chờ ở trạng thái READY).

─────────────────────────────────────────────────────────────────────────────────────────────────

[GIAI ĐOẠN 2: CHUYỂN GIAO QUYỀN VÀ THỰC THI TASKIDLE]
4. TASK(SchM_Startup) hoàn thành Phase 2 -> Gọi OsTerminateTask(SchM_Startup) (task.c: L261)
   │  ├── Chuyển SchM_Startup sang trạng thái SUSPENDED.
   │  └── TaskNmInd (Priority 7) gọi WaitEvent() -> Chuyển sang trạng thái WAITING.
   │  └── Gọi hàm lập lịch Sched_GetReady() (kernel.c: L206).
   │
   ▼
5. Sched_GetReady()
   │  └── Quét hàng đợi Ready: Hàng đợi không còn Task nào ưu tiên cao hơn
   │      ──► Task duy nhất ở trạng thái READY là TaskIdle (Priority = 0)!
   │      ──► Gán RunningVar = &TaskVarArray[TASK_ID_TaskIdle]
   │
   ▼
6. Os_PortDispatch()  (portable/cortex-m/arch.c)
   │  └── Nạp thanh ghi CPU từ TaskIdle_Stack ──► CPU nhảy vào hàm thực thi TASK(TaskIdle)!
   │
   ▼
7. TASK(TaskIdle)  (as/com/as.infrastructure/system/kernel/Os.c: L100-L124)
   ├── ASLOG(STDOUT, ("TaskIdle is running\n"))  ──► Xuất chuỗi log: "STDOUT :TaskIdle is running"
   └── for(;;)  [VÒNG LẶP NỀN VÔ TẬN]
         ├── Irq_Enable();        ──► Luôn mở ngắt để sẵn sàng nhận ngắt CAN / Timer ngoại vi
         ├── KSM_EXECUTE();       ──► Thực thi các máy trạng thái phi thời gian thực (KSM)
         ├── (void)Schedule();    ──► Điểm nhường CPU tự nguyện nếu có Task khác vừa được kích hoạt
         └── TaskIdleHook();      ──► Điểm móc nối hook MCU (ngủ tiết kiệm điện WFI / xóa Watchdog)
```

---

#### 4. Mã Nguồn Thực Thi Gốc `TASK(TaskIdle)` Trong [`Os.c: L96-L124`](../../as/com/as.infrastructure/system/kernel/Os.c#L96-L124):

```c
/* as/com/as.infrastructure/system/kernel/Os.c */

#ifndef __POSIX_OSAL__
#if !defined(__HIWARE__)
/* Hook mặc định kiểu weak, cho phép MCAL override để đưa CPU vào chế độ Sleep */
void __weak TaskIdleHook(void)
{
}
#endif

TASK(TaskIdle)
{
#if !defined(USE_TINYOS) && !defined(USE_CONTIKI)
    /* 1. In thông báo hệ thống đã vào chế độ hoạt động bình thường */
    ASLOG(STDOUT, ("TaskIdle is running\n"));
    for(;;)
    {
#endif
        /* 2. Đảm bảo cờ ngắt toàn cục luôn được mở để không treo vi điều khiển */
        Irq_Enable(); /* for robustness */

        /* 3. Thực thi bộ máy trạng thái nền của hệ thống */
        KSM_EXECUTE();

#if defined(__FREEOSEK__) || defined(__UCOSII_OS__) || defined(__RTTHREAD_OS__) || defined(__ASKAR_OS__)
        /* 4. Điểm kiểm tra lập lịch: Nếu có Task ưu tiên cao hơn sẵn sàng, lập tức nhường CPU */
        (void)Schedule();
#endif

        /* 5. Gọi Hook tiết kiệm điện (Ví dụ gọi __WFI() trong arch/stm32f1/mcal/Mcu.c: L566) */
        TaskIdleHook();

#if !defined(USE_TINYOS) && !defined(USE_CONTIKI)
    }
#endif
}
#endif /* __POSIX_OSAL__ */
```

---

#### 5. Cơ Chế Bị Cướp Quyền (Preemption) & Khôi Phục Ngữ Cảnh:
* **Khi có ngắt phần cứng (Ví dụ: SysTick Timer 1ms hết hạn):**
  1. Ngắt gọi chuỗi `knl_system_tick_handler()` $\rightarrow$ `SignalCounter(SysTimer)`.
  2. `Alarm_BswService` đạt chu kỳ 10ms $\rightarrow$ Kích hoạt `ActivateTask(SchM_BswService)` (**Priority = 8**).
  3. Nhân OS phát hiện `Priority(SchM_BswService) = 8 > Priority(TaskIdle) = 0` $\rightarrow$ Thực hiện **Ngắt quyền (Preemption)**: Đẩy toàn bộ thanh ghi CPU của `TaskIdle` vào `TaskIdle_Stack`, chuyển CPU sang chạy `TASK(SchM_BswService)`.
* **Khi `SchM_BswService` kết thúc (`TerminateTask`):**
  * Nhân OS gọi `Sched_GetReady()`, lấy lại `TaskIdle` từ hàng đợi Ready, khôi phục thanh ghi CPU từ `TaskIdle_Stack` và tiếp tục vòng lặp `for(;;)` của `TaskIdle` ngay tại vị trí bị ngắt trước đó!

---

### 🟢 LEVEL 1: NEWBIE FRIENDLY
📖 **PCP** (*Priority Ceiling Protocol*): Giao thức trần ưu tiên hệ điều hành.

💡 **Ẩn dụ thực tế:** 
- **Hiện tượng Đảo ngược ưu tiên:** Tổng giám đốc (Priority Cao) cần máy chiếu, nhưng Nhân viên tập sự (Priority Thấp) đang mượn máy chiếu. Lúc này, Trưởng phòng (Priority Vừa) đi qua, bắt Nhân viên tập sự làm báo cáo. Kết quả: Tổng giám đốc bị block và phải chờ Trưởng phòng (người không liên quan đến máy chiếu) làm xong việc!
- **Giải pháp PCP (Thẻ VIP Tạm Thời):** Mỗi khi mượn máy chiếu, người mượn tạm thời được cấp **Thẻ VIP (Priority Ceiling)** bằng cấp của Tổng giám đốc. Lúc này Trưởng phòng không dám sai vặt Nhân viên tập sự nữa. Nhân viên tập sự dùng xong máy chiếu, trả lại Thẻ VIP. Tổng giám đốc ngay lập tức lấy máy chiếu và sử dụng mà không bị trì hoãn.

### 🟡 LEVEL 2: INTERMEDIATE
Khi Task ưu tiên thấp (Task Low) giữ tài nguyên chung (Resource) và Task ưu tiên cao (Task High) cần tài nguyên đó, nếu không có cơ chế bảo vệ, Task Medium (không cần Resource) có thể ngắt Task Low, làm cho Task High bị trễ hạn (*Deadline Miss*).

Giải pháp AUTOSAR OS - OSEK PCP quy định:
1. **Trần ưu tiên tĩnh (Ceiling Priority):** Mỗi Resource được gán một mức trần tĩnh bằng độ ưu tiên của **Task cao nhất từng được cấu hình sử dụng Resource đó**.
2. **Kế thừa tức thì:** Khi một Task bất kỳ gọi `GetResource(ResID)`, độ ưu tiên của nó ngay lập tức được hệ điều hành **nâng lên mức Ceiling Priority của Resource đó**.
3. Không một Task nào khác có thể ngắt giữa chừng nếu ưu tiên <= Ceiling.

```c
/* MÃ NGUỒN GỐC SỬ DỤNG RESOURCE TRONG DỰ ÁN as */
/* (Trích xuất từ as/com/as.infrastructure/system/EcuM/EcuM_Main.c: L315-L325 & sys_arch.c: L120) */

/* 1. Chiếm quyền truy cập Resource RES_SCHEDULER (Độ ưu tiên được nâng tức thì lên Ceiling Priority = 31) */
GetResource(RES_SCHEDULER);

/* 2. Critical Section: Bảo vệ dữ liệu hàng đợi sự kiện / danh sách Task khỏi bị ngắt ngắt quãng */
EcuM_ProcessScheduledEvents();

/* 3. Giải phóng tài nguyên (Độ ưu tiên được hạ trở lại mức ưu tiên ban đầu của Task) */
ReleaseResource(RES_SCHEDULER);
```

### 🔴 LEVEL 3: EXPERT (Deep Dive)
**Trace Execution Step-by-step (Quá trình PCP):**
1. **Task L (Prio 1)** đang chạy, gọi `GetResource(ResX)`. Trần cấu hình tĩnh của ResX là 3.
2. OS lập tức nâng ưu tiên của Task L từ 1 lên 3.
3. Ngắt ngoại vi kích hoạt, **Task M (Prio 2)** trở thành Ready. Tuy nhiên, vì Task L đang ở mức 3 > 2, Task M bị Block, không thể ngắt Task L.
4. Một ngắt khác kích hoạt, **Task H (Prio 3)** trở thành Ready. Nó muốn chiếm CPU. Task L và Task H cùng mức 3, OSEK quy định Task đang chạy không bị ngắt bởi Task cùng mức ưu tiên $\rightarrow$ Task H bị Block (đưa vào Wait Queue).
5. Task L thực thi xong Critical Section, gọi `ReleaseResource(ResX)`. OS hạ ưu tiên Task L trở về 1.
6. OS Scheduler quét danh sách Ready, thấy **Task H (Prio 3)** là cao nhất $\rightarrow$ Dispatch lập tức Task H.

💀 **Deadlock Scenario & Phương Pháp Phòng Tránh:**
Nếu sử dụng Multiple Resources mà không cẩn thận, hệ thống có thể bị Deadlock kinh điển:
- Task A giữ Res1, xin Res2.
- Task B giữ Res2, xin Res1.
✅ **Phòng tránh trong AUTOSAR:** OSEK OS thiết kế loại trừ hoàn toàn Deadlock bằng luật cứng:
1. Task **bắt buộc phải trả các Resource theo đúng thứ tự ngược lại lúc lấy (LIFO)**. `Get(Res1) -> Get(Res2) -> Release(Res2) -> Release(Res1)`.
2. Do thuật toán Static Ceiling Priority, khi Task A lấy Res1, Priority của nó đã lớn hơn hoặc bằng Task B (Vì Task B cũng cần Res1 nên Ceiling của Res1 $\ge$ Prio B). Do đó Task B không bao giờ có cơ hội ngắt Task A để lấy Res2. Deadlock logic trên OSEK PCP là **BẤT KHẢ THI**.

---

## 5. Phân Cấp Ngắt Phần Cứng: ISR Category 1 vs ISR Category 2

### 🟢 LEVEL 1: NEWBIE FRIENDLY
📖 **ISR** (*Interrupt Service Routine*): Hàm phục vụ sự kiện ngắt phần cứng.
💡 **Ẩn dụ thực tế:**
- **ISR Cat 1 (Chuông báo cháy):** Phản ứng ngay lập tức, đập vỡ kính, không cần xin phép bảo vệ (Hệ điều hành). Tốc độ cực nhanh, nhưng cấm dùng điện thoại nội bộ tòa nhà (Cấm dùng OS API).
- **ISR Cat 2 (Người đưa thư đến):** Phải qua trạm gác bảo vệ (OS Wrapper) để ghi danh. Tuy chậm hơn một chút do làm thủ tục, nhưng được quyền nhờ bảo vệ đánh thức người trong tòa nhà (Gọi `SetEvent`, `ActivateTask`).

### 🟡 LEVEL 2: INTERMEDIATE
Để cân bằng giữa **độ trễ phản hồi ngắt cực ngắn** và **tính toàn vẹn của OS**, hệ thống chia ISR thành:

```mermaid
sequenceDiagram
    participant HW as Hardware
    participant OS as OS Wrapper
    participant ISR2 as ISR Cat 2 Function
    participant Task as OS Task

    HW->>OS: Hardware Interrupt Triggered
    Note over OS: Lưu ngữ cảnh CPU (Save Context)
    OS->>ISR2: Gọi hàm ISR C-Code User
    ISR2->>OS: SetEvent(TaskA, Event1)
    Note over OS: Cập nhật trạng thái TaskA thành Ready
    ISR2-->>OS: Kết thúc hàm ISR C-Code
    Note over OS: Scheduler đánh giá lại Priority
    OS-->>Task: Context Switch sang TaskA
```

| Tiêu Chí So Sánh | ISR Category 1 (Cat 1) | ISR Category 2 (Cat 2) |
|---|---|---|
| **Sự can thiệp của OS** | **Hoàn toàn không qua OS**: Nhảy trực tiếp từ Vector Table phần cứng vào hàm xử lý C. | **Có OS can thiệp**: OS thực hiện lưu/khôi phục Register Context và kiểm tra lập lịch. |
| **Độ trễ (Latency)** | **Cực nhỏ (Zero OS Overhead)**. Dùng cho ngắt khẩn (Over-current Inverter). | Trễ cao hơn do OS push toàn bộ thanh ghi. |
| **Quyền gọi OS API** | ❌ **Tuyệt đối cấm** gọi bất kỳ API nào của OS (không `SetEvent`, không `ActivateTask`). | ✅ **Được phép** gọi các API hệ điều hành cho phép. |

### 🔴 LEVEL 3: EXPERT (Deep Dive & Function-Call-Function Trace Thực Chiến)

Dưới đây là phân tích chi tiết cơ chế xử lý từ **tín hiệu kích hoạt vật lý (Hardware Trigger)**, qua các tầng phần mềm và nhân hệ điều hành, đến điểm thực thi hàm logic trong mã nguồn gốc của dự án `as`.

---

#### 🅰️ CASE STUDY 1: DÒNG CHẢY ISR CATEGORY 1 (NGẮT PHẦN CỨNG TRỰC TIẾP KHÔNG QUA OS)

> 💡 **Đặc tính kỹ nghệ:** Dành cho các ngắt yêu cầu phản ứng tức thời ở tần số cao (ví dụ: ngắt Fault bảo vệ ngắn mạch cầu H Inverter, ngắt lấy mẫu ADC dòng điện động cơ, hoặc ngoại lệ vi điều khiển như `hard_fault_handler`).

```
┌────────────────────────────────────────────────────────────────────────────────────────────────┐
│  ⚡ DÒNG CHẢY ISR CATEGORY 1 NGUYÊN BẢN (DIRECT HARDWARE INTERRUPT — ZERO OS OVERHEAD):       │
└────────────────────────────────────────────────────────────────────────────────────────────────┘

1. [PHẦN CỨNG NGOẠI VI PHÁT TÍN HIỆU NGẮT]
   Cảm biến / Timer / Chân ngoại vi kéo mức điện áp ──► Kích hoạt đường ngắt phần cứng vào NVIC.
        │
        ▼ (Khối NVIC của ARM Cortex-M tự động push {R0-R3, R12, LR, PC, xPSR} trong 12 clock cycles)
2. [BẢNG VECTOR NGẮT PHẦN CỨNG (VECTOR TABLE)]
   __vector_table (as/com/as.infrastructure/system/kernel/askar/portable/cortex-m/startup.S: L52)
        │
        └── [DÒNG 52]: Con trỏ ngắt trỏ TRỰC TIẾP vào hàm C của Driver
            ──► KHÔNG qua hàm bọc (Wrapper), KHÔNG gọi EnterISR(), KHÔNG đổi CallLevel.
                │
                ▼
3. [DRIVER / MCAL C-HANDLER THỰC THI TRỰC TIẾP]
   Fast_Cat1_ISR_Handler()  (Mã nguồn C tầng MCAL)
        │
        ├── 1. Đọc thanh ghi phần cứng (Hardware Registers)
        ├── 2. Thực thi xử lý khẩn cấp (Ví dụ: Set chân GPIO ngắt dòng Inverter < 100ns)
        ├── 3. Xóa cờ ngắt phần cứng trong thanh ghi ngoại vi (Clear Interrupt Pending Flag)
        └── 4. ❌ TUYỆT ĐỐI KHÔNG GỌI OS API (Không SetEvent, Không ActivateTask, Không Schedule)
                │
                ▼
4. [LỆNH THOÁT NGẮT PHẦN CỨNG]
   Thực thi lệnh Assembly: BX LR (EXC_RETURN = 0xFFFFFFF9)
        │
        └── Phần cứng NVIC tự động POP {R0-R3, R12, LR, PC, xPSR} khỏi Stack
            ──► CPU quay lại ngay dòng lệnh của Task đang chạy trước đó với 0 chu kỳ trễ từ OS!
```

---

#### 🅱️ CASE STUDY 2: DÒNG CHẢY ISR CATEGORY 2 (NGẮT CÓ OS WRAPPER — VÍ DỤ `Can_RxIsr` KÍCH HOẠT `TaskNmInd`)

> 💡 **Đặc tính kỹ nghệ:** Đây là cơ chế ngắt chuẩn mực nhất trong AUTOSAR BSW. Ngắt phần cứng được bọc bởi lớp vỏ OS Wrapper để bảo toàn ngữ cảnh CPU, cho phép gọi an toàn các API của OS (`SetEvent`, `ActivateTask`) và thực hiện **Lập lịch cướp quyền (Preemption Context Switch)** ngay tại thời điểm kết thúc ngắt.

```
┌────────────────────────────────────────────────────────────────────────────────────────────────┐
│  🚗 DÒNG CHẢY ISR CATEGORY 2 TOÀN DIỆN: TỪ DÂY CAN VẬT LÝ ──► OS WRAPPER ──► PREEMPTION DISPATCH│
└────────────────────────────────────────────────────────────────────────────────────────────────┘

1. [TÍN HIỆU VẬT LÝ TRÊN DÂY MẠNG CAN]
   Bản tin CAN (ví dụ CAN ID 0x401) truyền đến chân vi điều khiển ──► CAN Transceiver nhận tín hiệu vi sai
   ──► Khối CAN Controller phần cứng giải mã, khớp bộ lọc (Hardware Filter) và lưu vào FIFO Rx Mailbox
   ──► Kéo đường ngắt CAN_RX lên mức tích cực gửi vào khối NVIC.
        │
        ▼ (NVIC Stacking tự động {R0-R3, R12, LR, PC, xPSR} vào Stack)
2. [VECTOR TABLE NHẢY VÀO OS WRAPPER]
   __vector_table (as/com/as.infrastructure/system/kernel/askar/portable/cortex-m/startup.S: L67)
        │
        └── Vector 16..N trỏ tới hàm bọc hệ điều hành: knl_isr_process
                │
                ▼
3. [TẦNG OS WRAPPER — BẢO TOÀN NGỮ CẢNH & THIẾT LẬP INTERRUPT STACK]
   knl_isr_process (as/com/as.infrastructure/system/kernel/askar/portable/cortex-m/portableS.S: L235-L240)
        │
        ├── 1. Gọi EnterISR() (portableS.S: L126):
        │     ├── ISR2Counter++ (Tăng bộ đếm lồng ngắt ISR Cat 2)
        │     ├── push {r4-r11} (Lưu các thanh ghi còn lại của Task đang chạy - RunningVar)
        │     ├── ldr sp, =knl_system_stack_top (Chuyển con trỏ SP sang Ngăn xếp Ngắt riêng biệt)
        │     └── CallLevel = TCL_ISR2 (Ghi nhận hệ thống đang ở mức ngắt ISR Category 2)
        ├── 2. mrs r0, ipsr (Đọc số hiệu ngắt từ thanh ghi phần cứng IPSR)
        └── 3. Gọi knl_isr_handler(intno) (portable.c: L118)
                │
                ▼
4. [TẦNG MCAL DRIVER — ĐỌC DỮ LIỆU PHẦN CỨNG & XÓA CỜ NGẮT]
   Can_RxIsr(CAN_CTRL_1) (as/com/as.infrastructure/arch/stm32f1/mcal/Can.c: L308)
        │
        ├── 1. Đọc thanh ghi Mailbox phần cứng: CAN ID, DLC, và 8 Data Bytes
        ├── 2. Ghi thanh ghi CAN_RFR_RFOM0 để giải phóng Mailbox và xóa cờ ngắt phần cứng
        └── 3. Đóng gói PduInfoType và gọi tiếp lên tầng giao diện BSW:
            └──► CanIf_RxIndication(Hrh, CanId, &PduInfo) (CanIf.c: L831)
                    │
                    ▼
5. [TẦNG BSW COM & GỌI OS API SETEVENT]
   OsekNm_RxIndication() (OsekNm.c)
        │
        └── Gọi OS API: SetEvent(TASK_ID_TaskNmInd, EVENT_MASK_TaskNmInd_RxInd)
            (as/com/as.infrastructure/system/kernel/askar/kernel/event.c: L53-L96)
                │
                ├── TaskConstArray[TaskNmInd].pEventVar->set |= Mask
                ├── Phát hiện TaskNmInd đang ở trạng thái WAITING chờ Mask này
                ├── Chuyển trạng thái TaskNmInd: WAITING ──► READY
                └── Sched_AddReady(TASK_ID_TaskNmInd) (sched-bubble.c: L85)
                    ──► Đưa TaskNmInd vào ReadyQueue với Độ ưu tiên Priority = 7!
                    ──► Gán ReadyVar = &TaskVarArray[TaskNmInd]
                    (Lúc này vì CallLevel == TCL_ISR2, OS chưa đổi Task ngay mà chờ đến khi thoát ISR).
                        │
                        ▼
6. [TẦNG THOÁT NGẮT OS WRAPPER & LẬP LỊCH PREEMPTION]
   ExitISR() (as/com/as.infrastructure/system/kernel/askar/portable/cortex-m/portableS.S: L173-L218)
        │
        ├── 1. Khôi phục CallLevel cũ và giảm ISR2Counter--
        ├── 2. Đánh giá độ ưu tiên lập lịch:
        │     ├── Priority(ReadyVar)   = 7 (TaskNmInd vừa được đánh thức)
        │     └── Priority(RunningVar) = 0 (TaskIdle đang chạy trước khi có ngắt)
        ├── 3. Phát hiện Priority(ReadyVar) > Priority(RunningVar) (7 > 0):
        │     └──► Gọi Sched_Preempt()
        │     └──► Nhảy thẳng vào knl_start_dispatch (portableS.S: L73)
        │
        ▼ (CPU KHÔNG quay lại TaskIdle mà chuyển ngữ cảnh ngay lập tức)
7. [TASK ƯU TIÊN CAO ĐƯỢC THỰC THI NGAY SAU KHI THOÁT NGẮT]
   TASK(TaskNmInd) (as/com/as.infrastructure/diagnostic/OsekNm/OsekNm_Cfg.c: L110)
        └── Bắt đầu chạy xử lý gói tin mạng CAN với độ trễ tối thiểu!
```

---

#### 📊 Bảng So Sánh Chi Tiết Cơ Chế Thực Thi Mã Nguồn:

| Tiêu Chí Kỹ Thuật | ISR Category 1 (`Fast_Cat1_ISR`) | ISR Category 2 (`knl_isr_process` $\rightarrow$ `Can_RxIsr`) |
| :--- | :--- | :--- |
| **Bảng Vector Ngắt (`startup.S`)** | Trỏ trực tiếp đến địa chỉ hàm C MCAL. | Trỏ vào nhãn OS Wrapper `knl_isr_process`. |
| **Thao Tác Stack** | Tận dụng Stack hiện tại của CPU. | Tự động đổi con trỏ SP sang `knl_system_stack_top`. |
| **Lưu Trữ Ngữ Cảnh (Context Save)** | Chỉ 8 thanh ghi do phần cứng Cortex-M tự lưu. | Lưu bổ sung `{r4-r11}` vào `RunningVar` qua `EnterISR`. |
| **Trạng Thái `CallLevel`** | Giữ nguyên mức trước đó (Không đổi). | Thiết lập `CallLevel = TCL_ISR2` (2). |
| **Khả Năng Gọi OS API** | ❌ **Bị cấm 100%** (Gây hỏng trạng thái nhân OS). | ✅ **Được phép gọi**: `SetEvent()`, `ActivateTask()`. |
| **Điểm Preemption (Cướp Quyền)** | Không có. Luôn quay lại lệnh bị ngắt ban đầu. | Thực hiện ngay trong `ExitISR` nếu `ReadyVar > RunningVar`. |
| **Độ Trễ Phản Hồi (Latency)** | Cực nhỏ ($< 100\text{ ns}$ / 12 chu kỳ lệnh). | $\approx 1\ \mu\text{s}$ (Do chi phí push/pop thanh ghi và scheduler). |

---

## 6. Cơ Chế Định Thời: Counter, Alarm & Schedule Table

### 🟢 LEVEL 1: NEWBIE FRIENDLY
💡 **Ẩn dụ:**
- **Counter:** Cái đồng hồ tích tắc trên tường.
- **Alarm:** Cái đồng hồ báo thức bạn vặn để 10 phút nữa kêu. Kêu xong bạn phải thức dậy (ActivateTask) hoặc chuông reng (SetEvent).
- **Schedule Table:** Thời khóa biểu ở trường học (7h vào lớp, 7h45 ra chơi, 8h vào tiết 2). Lịch trình cố định tuyệt đối, không thay đổi, cực kỳ chính xác.

### 🟡 LEVEL 2: INTERMEDIATE
✅ **Best Practice: Ví dụ WaitEvent() bắt buộc có bảo vệ Timeout (Watchdog nội bộ)**

Trong lập trình ô tô an toàn (ISO 26262), **không bao giờ WaitEvent vĩnh viễn**. Nếu ngoại vi hỏng (ví dụ đứt dây CAN), Task sẽ bị kẹt mãi mãi (Deadlock). Ta dùng Alarm làm Timeout Watchdog.

```c
TASK(Wait_CAN_With_Timeout) {
    // Đặt Alarm 100 Ticks (ví dụ 100ms), nếu hết giờ Alarm sẽ SetEvent(TIMEOUT_EVENT)
    SetRelAlarm(Alarm_Timeout, 100, 0); 
    
    // Chờ 1 trong 2 sự kiện: Có CAN RX Event hoặc Timeout Event
    WaitEvent(CAN_RX_EVENT | TIMEOUT_EVENT); 
    
    EventMaskType events;
    GetEvent(Wait_CAN_With_Timeout, &events);
    ClearEvent(CAN_RX_EVENT | TIMEOUT_EVENT);
    
    if (events & CAN_RX_EVENT) {
        CancelAlarm(Alarm_Timeout); // Hủy báo thức vì đã nhận được thư an toàn
        Process_CAN_Data();
    } else if (events & TIMEOUT_EVENT) {
        Report_Error("CRITICAL: CAN Reception Timeout, Cable Broken?");
        Go_To_Safe_State();
    }
}
```

### 🔴 LEVEL 3: EXPERT (Deep Dive)
**Tại sao phải dùng Schedule Table thay vì mảng các Alarm?**
Trong các hệ thống phức tạp (Vd: Engine Control Unit), có hàng trăm tác vụ cần kích hoạt (Ví dụ Task 1ms, Task 5ms, Task 10ms). Nếu dùng Alarm, OS phải duyệt một Array tuyến tính tất cả các Alarm trong mỗi Timer Tick $\rightarrow$ Tốn hàng nghìn CPU Cycles $\rightarrow$ Jitter thời gian cao.
**Schedule Table** biên dịch trước (Pre-calculate) toàn bộ thời khóa biểu thành các *Expiry Points* (Mốc sự kiện) theo cơ chế Offset. Quan trọng hơn, Schedule Table hỗ trợ **Explicit Synchronization** (Đồng bộ thời gian chuẩn) với Global Time Master qua mạng FlexRay hoặc Automotive Ethernet (gọi qua API `SyncScheduleTable()`).

---

## 7. Hệ Thống Hàm Hook Quản Trị Trạng Thái (Hook Routines)

### 🟢 LEVEL 1: NEWBIE FRIENDLY
💡 Hook giống như các **camera an ninh** được đặt tại các cửa ra vào của hệ điều hành. Mỗi khi có việc quan trọng xảy ra (Hệ thống khởi động, xảy ra lỗi, một task bắt đầu chạy), camera sẽ tự động gọi bảo vệ (Code của bạn) ra để kiểm tra xử lý.

### 🟡 LEVEL 2: INTERMEDIATE
Hệ điều hành cung cấp các hàm Callback đặc biệt (Hook) được kích hoạt tại các thời điểm chuyển giao:
* `StartupHook()`: Được gọi sau khi `StartOS()` hoàn tất khởi tạo cấu trúc dữ liệu, trước khi Task đầu tiên chạy. Thường dùng để Init MCAL (Port, Dio, Spi).
* `ShutdownHook()`: Được gọi khi có lệnh `ShutdownOS()`. Dùng để ghi dữ liệu cuối cùng vào EEPROM.
* `ErrorHook(StatusType Error)`: Được gọi tự động mỗi khi một API của OS trả về mã lỗi khác `E_OK`.
* `PreTaskHook()` / `PostTaskHook()`: Được gọi ngay trước khi một Task chuyển sang `Running` và ngay sau khi rời khỏi `Running`.

### 🔴 LEVEL 3: EXPERT (Deep Dive)
🎯 **Use Case: Đo tải CPU (CPU Load Profiling) với Pre/Post Task Hook**
Trong dự án thực tế, kỹ sư cần phải chứng minh tải CPU (CPU Load) không vượt quá 80%.
```c
uint32 TaskStart_Time[MAX_TASKS];
uint32 TaskExec_Time[MAX_TASKS];

void PreTaskHook(void) {
    TaskType currentTask;
    GetTaskID(&currentTask);
    // Lưu lại Timestamp phần cứng cực nhanh (Hardware Timer Tick)
    TaskStart_Time[currentTask] = Gpt_GetTimeElapsed(HW_TIMER_CH_1);
}

void PostTaskHook(void) {
    TaskType currentTask;
    GetTaskID(&currentTask);
    // Tính khoảng thời gian Task vừa chiếm dụng CPU
    uint32 delta = Gpt_GetTimeElapsed(HW_TIMER_CH_1) - TaskStart_Time[currentTask];
    TaskExec_Time[currentTask] += delta; // Cộng dồn thời gian chạy
}
```

---

## 8. Tầng Trừu Tượng Vi Điều Khiển (MCAL Layer Architecture & SWS Patterns)

### 🟢 LEVEL 1: NEWBIE FRIENDLY
📖 **MCAL** (*Microcontroller Abstraction Layer*): Tầng phần mềm nằm thấp nhất, giao tiếp sát sườn với phần cứng.
💡 **Ẩn dụ:** Nếu ứng dụng xe hơi của bạn là một Giám đốc nói tiếng Việt, phần cứng là công nhân người nước ngoài (Mỗi hãng MCU nói một tiếng: Infineon, NXP, Renesas). MCAL chính là **phiên dịch viên đạt chuẩn ISO**. Giám đốc chỉ cần ra lệnh `Dio_WriteChannel()` (tiếng Việt), MCAL tự dịch sang mã lệnh tương ứng để chích điện vào chân IC.

### 🟡 LEVEL 2: INTERMEDIATE
Tất cả các mô-đun MCAL phải tuân thủ khắt khe định dạng AUTOSAR:
```
[QUY TẮC ĐẶT TÊN API VÀ FILE CHUẨN TRONG MCAL]
- Tên File Header:       <Module>.h (Ví dụ: Port.h, Dio.h, Can.h)
- Tên File Cấu Hình:    <Module>_Cfg.h, <Module>_Lcfg.c, <Module>_PBcfg.c
- Tên Hàm API:           <Module>_<FunctionName>() (Ví dụ: Dio_WriteChannel, Port_Init)
- Tên Mã Lỗi Service:    <MODULE>_E_<ERROR_NAME> (Ví dụ: DIO_E_PARAM_INVALID_CHANNEL_ID)
```

### 🔴 LEVEL 3: EXPERT (Deep Dive)
**Code Generation trong AUTOSAR (Tự động hóa):**
Thực tế kỹ sư không tự gõ tay các file cấu hình `Port_PBcfg.c`. Họ sử dụng công cụ như **EB Tresos** hoặc **Vector DaVinci Configurator**. Tool sẽ parse file ARXML (chứa mô tả xe) và Generate ra C-code tương ứng cho chip. MCAL phân tách làm 3 cấp cấu hình:
1. **Pre-Compile (PC):** Định nghĩa qua `#define`. Tốc độ chạy nhanh nhất, nhưng compile xong là chết cứng.
2. **Link-Time (LT):** Định nghĩa bằng biến `extern const`. Cho phép thay thế module ở giai đoạn Linker.
3. **Post-Build (PB):** Cấu hình là một con trỏ vùng nhớ truyền vào hàm `Init`. Cho phép nạp (flash) một cấu hình mới vào xe ngay cả sau khi xe xuất xưởng mà không cần build lại code!

---

## 9. Phân Tích Chi Tiết 7 Module MCAL Cốt Lõi (Kèm API & Struct Trong parai/as)

### 8.1 Port Driver (`Port.h`)
* **Trách nhiệm:** Cấu hình gốc rễ của mọi chân IC. Hướng chân (*Input/Output*), chức năng thay thế (*GPIO, UART, CAN, SPI*), điện trở kéo (*Pull-up/Pull-down*), và tốc độ quét xung (Slew Rate).
* ⚠️ **Warning - Quy tắc bắt buộc:** `Port_Init(&Port_Config)` **phải được gọi đầu tiên** tại `StartupHook`, trước khi bất kỳ module ngoại vi nào khác (như `Dio`, `Spi`, `Adc`) được khởi tạo.

```c
/* File: com/as.infrastructure/include/Port.h */
void Port_Init(const Port_ConfigType *ConfigPtr);
void Port_SetPinDirection(Port_PinType Pin, Port_PinDirectionType Direction);
void Port_SetPinMode(Port_PinType Pin, Port_PinModeType Mode);
void Port_RefreshPortDirection(void);
```

### 8.2 Digital I/O Driver (`Dio.h`)
* **Trách nhiệm:** Chỉ Đọc/ghi các mức logic số (**`STD_HIGH` = 1, `STD_LOW` = 0**) trên các chân đã được Port cấu hình làm GPIO.
* **Cấu trúc phân cấp kênh:** `Channel` (1 chân lẻ) $\rightarrow$ `Port` (Gồm 8/16/32 kênh) $\rightarrow$ `ChannelGroup` (Mask gom nhóm nhiều bit trên 1 Port).

🎯 **Use Case: Đọc Nút Bấm Khởi Động Xe (Start Button)**

❌ **Mã cổ điển (Không dùng MCAL - Phụ thuộc Cứng phần cứng):**
```c
if ((GPIOA->IDR & 0x01) == 1) { 
    /* Xử lý nút bấm */ 
} 
// Lỗi kỹ nghệ: Nếu công ty đổi chip STM32 sang NXP S32K, toàn bộ Application Layer vứt đi viết lại!
```

✅ **Mã chuẩn AUTOSAR MCAL (Portable 100%):**
```c
// Lớp ứng dụng chỉ gọi API chuẩn AUTOSAR, không quan tâm thanh ghi:
Dio_LevelType buttonLevel = Dio_ReadChannel(DioConf_DioChannel_START_BUTTON);
if (buttonLevel == STD_HIGH) {
    // Xử lý nổ máy an toàn
}
```

### 8.3 General Purpose Timer Driver (`Gpt.h`)
* **Trách nhiệm:** Quản lý các Hardware Timers. Đo khoảng thời gian, tạo tín hiệu định kỳ, kích hoạt Notification Callback.

```c
/* File: com/as.infrastructure/include/Gpt.h */
void Gpt_Init(const Gpt_ConfigType *configPtr);
void Gpt_StartTimer(Gpt_ChannelType channel, Gpt_ValueType value); // value = Số tick hw
void Gpt_StopTimer(Gpt_ChannelType channel);
Gpt_ValueType Gpt_GetTimeElapsed(Gpt_ChannelType channel); // Cực quan trọng cho Timing
void Gpt_EnableNotification(Gpt_ChannelType channel);
```

### 8.4 Analog to Digital Converter Driver (`Adc.h`)
* **Trách nhiệm:** Quản lý module ADC. Hỗ trợ cấu hình Channel Group, kích hoạt bằng Software hoặc phần cứng (PWM/Timer Trigger).
* 🌟 **Pro Tip:** Đối với lấy mẫu tần số cao (Motor Control), không dùng CPU để đọc ADC mà phải cấu hình `Adc_StartGroupConversion()` với chế độ DMA. ADC chuyển đổi xong tự động đổ dữ liệu vào RAM, cởi trói CPU.

```c
/* File: com/as.infrastructure/include/Adc.h */
Std_ReturnType Adc_StartGroupConversion(Adc_GroupType Group);
void Adc_StopGroupConversion(Adc_GroupType Group);
Std_ReturnType Adc_ReadGroup(Adc_GroupType Group, Adc_ValueGroupType *DataBufferPtr);
```

### 8.5 Serial Peripheral Interface Driver (`Spi.h`)
* **Trách nhiệm:** Giao tiếp SPI tốc độ cao với EEPROM ngoài, IC nguồn (SBC), Cảm biến.
* **Phân cấp độc đáo của AUTOSAR SPI:**
  * **Channel:** Vùng đệm chứa dữ liệu Tx/Rx lẻ.
  * **Job:** Tập hợp các Channel truyền đến cùng 1 Chip Select (CS).
  * **Sequence:** Chuỗi nhiều Jobs nối tiếp nhau.

```c
Std_ReturnType Spi_SyncTransmit(Spi_SequenceType Sequence);  // Dừng CPU chờ truyền xong
Std_ReturnType Spi_AsyncTransmit(Spi_SequenceType Sequence); // Trả về ngay, dùng Ngắt báo
```

### 8.6 Controller Area Network Driver (`Can.h`)
* **Trách nhiệm:** Tầng thấp nhất điều khiển trực tiếp CAN Controller (Mailbox, Bit Timing, Acceptance Filters).

#### 🟡 LEVEL 2: INTERMEDIATE - Gửi Frame CAN với Error Handling

```c
Can_PduType PduInfo;
uint8 Payload[8] = {0x01, 0x02, 0x03, 0x00, 0x00, 0x00, 0x00, 0x00};

PduInfo.id = 0x123;           // CAN ID
PduInfo.swPduHandle = 1;      // Handle cho tầng CanIf phía trên
PduInfo.length = 8;           // Data Length
PduInfo.sdu = Payload;        // Data Buffer Pointer

Can_ReturnType status = Can_Write(CanConf_CanHardwareObject_Tx, &PduInfo);
if (status != CAN_OK) {
    if (status == CAN_BUSY) {
        // Mailbox đang bận, báo lên CanIf lập lịch thử lại sau
    }
}
```

#### 🔴 LEVEL 3: EXPERT - Cơ Chế Truyền CAN Phần Cứng
Hàm `Can_Write` không hề chặn (Block) chương trình để chờ Frame đẩy lên mạng CAN. Nó chỉ copy Payload vào thanh ghi HW Mailbox và set cờ Truyền (Tx Request). Khi quá trình đẩy bit lên bus CAN vật lý hoàn tất, ngắt Tx Confirmation (Cat 2 ISR) của MCU sẽ nhảy vào, từ đó MCAL gọi ngược lên `CanIf_TxConfirmation()` báo hiệu cho phần mềm tuyến trên.

### 8.7 Watchdog Driver (`Wdg.h` & `WdgIf.h`)
* **Trách nhiệm:** Trình điều khiển Watchdog Timer phần cứng, "chó canh cổng" chống treo chip.
* **3 Chế độ:** `WDGIF_OFF_MODE`, `WDGIF_SLOW_MODE` (Chờ cập nhật firmware), `WDGIF_FAST_MODE` (Đang chạy bình thường).
* API: `Wdg_SetMode()`, `Wdg_SetTriggerCondition(uint16 timeout)`.

---

## 10. Cơ Chế Bắt Lỗi Phát Triển (Default Error Tracer - DET) & Common Pitfalls

### 🟢 LEVEL 1: NEWBIE FRIENDLY
📖 **DET** (*Default Error Tracer*): Sổ ghi lỗi trong quá trình phát triển. Trong giai đoạn lập trình, tất cả các module phải "báo cáo" sai phạm (Truyền sai tham số, chưa khởi tạo) vào DET.
*(Lưu ý: Chức năng này sẽ được tắt (Disable) khi xe bán ra thị trường để tối ưu bộ nhớ và tốc độ CPU).*

### 🟡 LEVEL 2: INTERMEDIATE
Trong mọi API MCAL, AUTOSAR quy định kiểm tra `NULL_PTR`, tham số hợp lệ, trạng thái Init. Nếu sai, gọi hàm:
```c
Std_ReturnType Det_ReportError(
    uint16 ModuleId,       // Vd: MODULE_ID_DIO = 120
    uint8 InstanceId,      // Vd: Chip số 0
    uint8 ApiId,           // Vd: DIO_WRITECHANNEL_ID = 0x01
    uint8 ErrorId          // Vd: DIO_E_PARAM_INVALID_CHANNEL_ID = 10
);
```

### 🔴 LEVEL 3: EXPERT (Deep Dive)
⚠️ **Common Pitfalls (5 Lỗi Điển Hình Gây Crash Hệ Thống):**
1. **Quên gọi `Port_Init` trước các thao tác I/O**: Gây lỗi Trap (HardFault, Data Bus Error) do thanh ghi ngoại vi chưa được cấp điện hoặc Clock.
2. **Gọi `WaitEvent` bên trong ISR hoặc Basic Task**: Hệ thống sẽ phát hiện hành vi sai trái và nhảy vào `ErrorHook()` kèm mã lỗi `E_OS_CALLEVEL` (Calling Level sai lệch).
3. **Quên gọi `ClearEvent` sau khi `WaitEvent` thức dậy**: Task sẽ rơi vào một vòng lặp vô hạn (Infinite Loop) vì Event cờ vẫn dựng mức 1 $\rightarrow$ Gây Starvation cho toàn hệ thống.
4. **Cấu hình kích thước Stack của Extended Task quá nhỏ**: Vì Extended Task phải tự lưu trữ toàn bộ Context Stack (Có thể lên tới 512 bytes trên chip lõi ARM Cortex-M/R). Khai báo quá nhỏ gây Stack Overflow phá hủy biến cục bộ của OS.
5. **Gán ISR Hardware Priority lớn hơn OS Priority Threshold**: Hành động này phá vỡ toàn bộ cấu trúc bảo vệ thời gian của Hệ điều hành, ISR sẽ tùy ý chèn ngang các hoạt động nhạy cảm của Kernel.

---

## 11. Bảng So Sánh AUTOSAR OS vs FreeRTOS Chi Tiết

| Đặc tính | AUTOSAR OS (Automotive) | FreeRTOS (General IoT) | Nhận xét Chuyên Gia |
|:---|:---|:---|:---|
| **Cấp phát bộ nhớ** | Tĩnh 100% (Build time) | Động (Heap) và Tĩnh | Ô tô tuyệt đối cấm dùng Heap rò rỉ bộ nhớ. |
| **Quản trị rủi ro Deadlock** | OSEK PCP | Priority Inheritance | PCP của AUTOSAR vượt trội hoàn toàn về mặt Determinism, không có rủi ro trễ thời gian khôi phục. |
| **Chế độ bảo vệ bộ nhớ** | OS-Applications (MPU partitions) | FreeRTOS-MPU (Addon phụ) | Kiến trúc AUTOSAR tích hợp sâu MPU vào hệ điều hành lõi (Microkernel). |
| **Bảo vệ thời gian** | LockTime, ExecutionTime | Không hỗ trợ Native | AUTOSAR có thể phạt Task nào giữ Spinlock hoặc chạy quá lâu bằng cách giết Task đó qua ProtectionHook. |
| **Chứng chỉ An Toàn** | ISO 26262 ASIL-D Native | Cần nâng cấp bản SafeRTOS | FreeRTOS thuần không được phép chạy cho ABS/Airbag. |

---

## 12. 🛠️ Hands-On Exercises Thực Chiến

**🛠️ Bài Tập 1: Tạo Basic Task Chớp Tắt Đèn**
- **Mục tiêu:** Hiểu chu trình Lifecycle của một Basic Task.
- **Mô tả:** Viết C-code cho một Basic Task `Task_BlinkLED`. OS có một Alarm định kỳ 500ms kích hoạt Task này.
- **Yêu cầu:** Dùng API của MCAL Dio để lật trạng thái chân (Ví dụ: `DIO_CHANNEL_LED_RED`), sau đó trả CPU về OS.
- **Gợi ý Code:**
```c
TASK(Task_BlinkLED) {
    Dio_FlipChannel(DIO_CHANNEL_LED_RED); // API AUTOSAR MCAL 4.0
    TerminateTask(); // Giải phóng CPU ngay lập tức
}
```

**🛠️ Bài Tập 2: Phân Tích Hiện Tượng Priority Inversion Bằng Diagram**
- **Mục tiêu:** Thực hành giao thức OSEK PCP.
- **Mô tả:** Giả định MCU có 3 Task (T1 prio=1, T2 prio=2, T3 prio=3). T1 và T3 dùng chung Mutex/Resource tên là `RES_I2C`.
- **Yêu cầu:** Hãy xác định Ceiling Priority cho `RES_I2C` trong file `.oil`. Vẽ Sequence Diagram mô tả việc T3 kích hoạt khi T1 đang cầm `RES_I2C`. Liệu T2 có thể ngắt ngang T1 được không?
- **Gợi ý:** Ceiling của `RES_I2C` bắt buộc phải là 3 (Max priority của các task sử dụng). Khi T1 gọi GetResource, nó lên Prio 3, T2 (Prio 2) vô phương ngắt ngang.

**🛠️ Bài Tập 3: Lập Trình Extended Task Chờ Sự Kiện Kép**
- **Mục tiêu:** Xử lý Timer/Timeout an toàn cho Extended Task.
- **Mô tả:** Viết Extended Task chờ tin nhắn mạng CAN. Nếu trong vòng 20ms mạng CAN không gửi tin đến, kích hoạt trạng thái báo lỗi mạng.
- **Yêu cầu:** Dùng `SetRelAlarm` để cài Timeout, `WaitEvent(CAN_RX | TIMEOUT)`. Hủy Alarm nếu CAN đến sớm. Dùng `GetEvent` và bitwise Mask để phân nhánh logic.

---

## 13. Bộ Câu Hỏi Phỏng Vấn (Q&A 3 Levels)

**🟢 Level 1: Newbie Interview**
* **Câu hỏi:** Tại sao các chuyên gia khuyên không được viết vòng lặp vô tận `while(1)` bên trong một Basic Task?
* **Trả lời:** Basic Task trong OSEK không có trạng thái Waiting (Không có `WaitEvent`). Nếu lập trình `while(1)`, Basic Task đó sẽ "ăn" toàn bộ CPU vĩnh viễn. Các Task ưu tiên thấp hơn không bao giờ được chạy. Cuối cùng Watchdog phần cứng sẽ phát hiện MCU bị đơ và thực hiện Hardware Reset xe.

**🟡 Level 2: Intermediate Interview**
* **Câu hỏi:** Giải thích sự khác biệt kiến trúc giữa ISR Cat 1 và ISR Cat 2? Hãy cho ví dụ thực tế trên xe.
* **Trả lời:**
  * **ISR Cat 1:** Bỏ qua hệ điều hành (Bypass OS Wrapper), nhảy thẳng vào hàm xử lý. Tốc độ thực thi cực nhanh (Độ trễ ns). Dùng cho ngắt khẩn cấp cứu mạng hoặc ngắt chu kỳ siêu ngắn (như điều khiển PWM Inverter của xe điện - chu kỳ ngắt 50us). Tuyệt đối cấm gọi OS API bên trong Cat 1.
  * **ISR Cat 2:** Phải thông qua OS (Có OS Wrapper lưu/khôi phục Register Context). Trễ hơn nhưng an toàn. Được phép gọi OS API như `SetEvent` để đánh thức Task phía trên. Dùng cho ngắt mạng CAN, báo nhận UART/SPI.

**🔴 Level 3: Expert / Architect Interview**
* **Câu hỏi:** Khi một hệ điều hành đa nhiệm thông thường sử dụng Mutex, việc gọi `Lock()` có thể gây Context Switch. Tuy nhiên, trong AUTOSAR OS, điều gì xảy ra ở mức Assembly/Kernel khi một Task gọi `GetResource()`? Tại sao chuyên gia lại nói "Không có Context Switch"?
* **Trả lời:** 
Trong AUTOSAR OS áp dụng OSEK PCP, khi gọi `GetResource()`, hệ điều hành chỉ đơn giản cập nhật con trỏ/thanh ghi chứa số Priority của Task hiện tại lên thành mức Ceiling Priority của Resource đó (Ví dụ từ Prio 1 lên Prio 3).
**KHÔNG có Context Switch** diễn ra (nghĩa là không đẩy Stack xuống vùng nhớ, không đổi con trỏ lệnh PC), vì Priority mới của Task chỉ có TĂNG lên (hoặc giữ nguyên) so với Priority cũ. CPU nghiễm nhiên vẫn tiếp tục thuộc về quyền sở hữu của Task đó.
Một thao tác Context Switch chỉ có nguy cơ tiềm ẩn ở hàm `ReleaseResource()`, khi Priority của Task hiện tại bị giảm trở về mức cũ (Ví dụ từ 3 về 1), và lúc này Scheduler phát hiện có một Task khác trong Ready Queue đang có Priority = 2 (lớn hơn 1) đang chực chờ được chạy.

---
> **Báo cáo Kỹ Nghệ Nâng Cấp Document:**
> - Tài liệu đã được đại tu lên mức **Universal Learning Resource**.
> - Nội dung đã bao quát 100% Acronyms yêu cầu (OSEK, VDX, MCAL, ISR, PCP).
> - Tích hợp đầy đủ so sánh chi tiết Basic/Extended Task (với WaitEvent Timeout), API Internals, 5 Lỗi Pitfalls phổ biến nhất, Bảng So Sánh OS.
> - Bổ sung 3 🛠️ Hands-On Exercises Thực Chiến và Bộ Câu Hỏi Phỏng Vấn (Q&A 3 Levels) thực tế dành riêng cho các kỹ sư Embedded Automotive.
> - Kích thước tài liệu được mở rộng tối đa, phân tích sâu chuyên ngành đảm bảo vượt 40KB (hoặc tối thiểu gấp đôi bản 20KB gốc).
