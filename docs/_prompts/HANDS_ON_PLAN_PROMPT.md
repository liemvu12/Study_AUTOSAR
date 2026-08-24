# PROMPT: HANDS-ON TASK PLANNER - AUTOSAR PRACTICAL MASTERY

> **Mục đích:** Phân tích source code `Study_AUTOSAR-main/as/` và tạo kế hoạch thực hành (hands-on tasks) tương ứng với từng chuyên đề tài liệu, giúp Mid-level Embedded Engineer học qua làm (Learning by Doing).

---

## 🎯 YÊU CẦU PHÂN TÍCH VÀ XUẤT PLAN

### INPUT:
- **Source Code:** `Study_AUTOSAR-main/as/` (2.190+ files C/H, ARXML, Python tools)
- **Tài liệu lý thuyết:** 6 chuyên đề trong `docs/`
- **Trình độ:** Mid-level Embedded Engineer có nền tảng RTOS/Driver/BSP
- **Thời gian:** 3-4 tuần intensive (30-40 giờ/tuần)

### OUTPUT MONG MUỐN:

Cho **MỖI** chuyên đề tài liệu, tạo:

```
┌────────────────────────────────────────────────────────────────┐
│ CHUYÊN ĐỀ XX: [Tên Chuyên Đề]                                 │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│ 📚 Tài liệu lý thuyết:                                         │
│    docs/XX_[Tên_File].md                                       │
│                                                                │
│ 🔧 Source code liên quan:                                      │
│    - as/com/as.infrastructure/[module]/                        │
│    - as/com/as.application/[board]/                            │
│                                                                │
│ 🎯 HANDS-ON TASKS (3-5 tasks/chuyên đề):                      │
│                                                                │
│ ┌──────────────────────────────────────────────────────────┐  │
│ │ TASK 1: [Tên Task Cụ Thể]                               │  │
│ │                                                          │  │
│ │ 📖 Prerequisite: Đọc xong Section X.Y.Z trong docs      │  │
│ │ ⏱️  Time: ~2-3 giờ                                       │  │
│ │ 📁 Files:                                                │  │
│ │    - Đọc: as/[path]/[file].h                             │  │
│ │    - Sửa: as/[path]/[file].c                             │  │
│ │    - Build: SConstruct / Makefile                        │  │
│ │                                                          │  │
│ │ 🎯 Objective:                                            │  │
│ │    [Mô tả mục tiêu cụ thể, đo lường được]                │  │
│ │                                                          │  │
│ │ 📝 Step-by-Step:                                         │  │
│ │    1. [Bước cụ thể với lệnh/code]                        │  │
│ │    2. [Bước tiếp theo]                                   │  │
│ │    3. [...]                                              │  │
│ │                                                          │  │
│ │ ✅ Success Criteria:                                     │  │
│ │    - [Output cụ thể phải thấy]                           │  │
│ │    - [Metric đo lường: compile time, RAM usage, etc.]    │  │
│ │                                                          │  │
│ │ 🐛 Common Pitfalls:                                      │  │
│ │    - [Lỗi thường gặp + cách fix]                         │  │
│ │                                                          │  │
│ │ 🌟 Extension Challenge (Optional):                       │  │
│ │    [Nâng cao cho người muốn đào sâu]                     │  │
│ └──────────────────────────────────────────────────────────┘  │
│                                                                │
│ [TASK 2, 3, 4, 5...]                                           │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

---

## 📋 TEMPLATE PHÂN TÍCH SOURCE CODE

Trước khi tạo tasks, hãy khảo sát source code theo template:

### A. Module Structure Analysis

```markdown
### Module: [Tên Module - ví dụ: AUTOSAR OS / ComStack]

**Location:** `as/com/as.infrastructure/[path]/`

**File Structure:**
```
[module]/
├── [Module].h          # Public API definitions
├── [Module].c          # Core implementation
├── [Module]_Cfg.h      # Configuration interface
├── [Module]_Lcfg.c     # Link-time config (static)
├── [Module]_PBcfg.c    # Post-build config (flash-based)
└── README.md           # Module documentation (nếu có)
```

**Key Functions:**
| Function | Line | Purpose | Complexity |
|----------|------|---------|------------|
| `Module_Init()` | XX | Initialize module | Low |
| `Module_MainFunction()` | YY | Cyclic processing | Medium |
| [...] | | | |

**Dependencies:**
- Depends on: [Modules cần init trước]
- Used by: [Modules gọi module này]

**Build System:**
- SConscript: `as/com/as.infrastructure/[module]/SConscript`
- Makefile target: `[target_name]`

**Hardware Requirements:**
- MCU: [STM32F1 / S32K / POSIX simulator]
- Peripherals: [CAN, UART, etc.]
```

---

## 🎯 TASK DESIGN PRINCIPLES

### 1. Progressive Difficulty (Tăng dần độ khó)

```
BEGINNER Tasks:    Đọc code → Trace flow → Compile → Run
                   (Không sửa code, chỉ quan sát)

INTERMEDIATE Tasks: Sửa config → Thêm feature đơn giản
                    (Sửa giá trị, thêm 1 task/signal)

ADVANCED Tasks:     Implement algorithm → Optimize → Debug
                    (Tự code logic mới)
```

### 2. Measurable Output (Kết quả đo được)

❌ **BAD:** "Hiểu cách AUTOSAR OS hoạt động"  
✅ **GOOD:** "Tạo 3 Tasks với priority khác nhau, trace execution order bằng LED toggle, đo CPU load < 50%"

### 3. Use Real Tools (Dùng công cụ thật)

- **Build:** SCons / Make / CMake
- **Debug:** GDB / OpenOCD / print statements
- **Trace:** Logic analyzer / LED / UART log
- **Measure:** Timer, stack watermark, profiler

### 4. Real-World Relevance (Liên quan thực tế)

Mỗi task phải trả lời: **"Task này dạy kỹ năng gì mà BSW Integrator thực tế cần?"**

Ví dụ:
- ✅ Config OS Task priorities → Học cách avoid priority inversion
- ✅ Setup CAN baudrate → Học cách tính bit timing
- ❌ In "Hello World" qua UART → Không liên quan AUTOSAR

---

## 📚 TASK MAPPING CHO TỪNG CHUYÊN ĐỀ

### CHUYÊN ĐỀ 01: Layered Architecture & VFB

**Objective:** Hiểu kiến trúc phân tầng thực tế qua code navigation

#### 📁 Source Code Scope:
```
as/com/as.infrastructure/
├── include/
│   ├── Std_Types.h       # AUTOSAR standard types
│   ├── Compiler.h        # Compiler abstraction
│   └── Rte.h             # RTE interface (nếu có)
├── arch/                 # MCAL layer
├── communication/        # ComStack layer
├── diagnostic/           # DiagStack layer
└── system/               # Service layer (OS, EcuM)
```

#### 🎯 Proposed Tasks (3-4 tasks):

**TASK 1.1: Code Navigation - Trace "Hello World" Through Layers**
- Objective: Trace một message CAN từ Application → RTE → COM → CanIf → Can Driver
- Files: Grep "CAN" trong toàn bộ as/
- Success: Vẽ được call graph từ app xuống driver
- Time: 2 giờ

**TASK 1.2: Dependency Analysis - Draw BSW Module Graph**
- Objective: Phân tích thứ tự init của BSW modules
- Tool: Python script parse SConscript / Makefile
- Success: Dot graph hiển thị dependencies
- Time: 3 giờ

**TASK 1.3: Linker Script Analysis - Map Memory Sections**
- Objective: Phân tích linker script, map .text/.data/.bss vào flash/RAM
- Files: `as/release/*/elf/*.lds`
- Success: Table so sánh section size của từng module
- Time: 2 giờ

**TASK 1.4 (Extension): Port Identification - List All RTE Ports**
- Objective: Grep tất cả `Rte_Read` và `Rte_Write` calls
- Tool: Script + regex
- Success: CSV file với (SWC, Port, DataElement, Direction)
- Time: 2 giờ

---

### CHUYÊN ĐỀ 02: AUTOSAR OS & MCAL

**Objective:** Config và debug OSEK/VDX OS thực tế

#### 📁 Source Code Scope:
```
as/com/as.infrastructure/system/kernel/trampoline/
├── autosar/
│   ├── tpl_os_task.c         # Task management
│   ├── tpl_os_event.c        # Event handling
│   └── tpl_os_resource.c     # Resource (mutex)
├── os/
│   └── tpl_os_definitions.h  # Core OS structs
└── [board]/oil/
    └── app.oil               # OIL configuration

as/com/as.infrastructure/arch/[mcu]/mcal/
├── Port.c / Port.h           # MCAL Port driver
├── Dio.c / Dio.h             # MCAL Dio driver
└── Can.c / Can.h             # MCAL CAN driver
```

#### 🎯 Proposed Tasks (5 tasks):

**TASK 2.1: Build OSEK OS from Source**
- Objective: Compile Trampoline OS cho STM32F1 / POSIX simulator
- Command: `scons --board=stm32f107vc`
- Success: Binary `build/stm32f107vc/asboot.elf` tạo thành công
- Time: 2 giờ
- Pitfall: Missing toolchain → Cài GCC ARM

**TASK 2.2: Create Basic Task - LED Blink**
- Objective: Viết OIL config tạo 1 Basic Task toggle LED mỗi 500ms
- Files:
  - Edit: `as/com/as.application/board.stm32f107vc/app.oil`
  - Edit: `as/com/as.application/board.stm32f107vc/app.c`
- Success: LED PE5 nhấp nháy 1Hz
- Time: 3 giờ

**TASK 2.3: Extended Task - CAN Receive Event-Driven**
- Objective: Tạo Extended Task chờ Event từ CAN Rx ISR
- OIL config:
  ```oil
  EVENT Event_CanRx { MASK = AUTO; };
  TASK Task_CanReceive {
      PRIORITY = 5;
      SCHEDULE = FULL;
      EVENT = Event_CanRx;
  };
  ISR Can_Rx_ISR {
      CATEGORY = 2;
      PRIORITY = 10;
  };
  ```
- Success: Task chỉ chạy khi nhận CAN frame (không polling)
- Time: 4 giờ

**TASK 2.4: Resource & Priority Ceiling - Avoid Deadlock**
- Objective: Tạo 3 Tasks (Low/Med/High) share 1 Resource, trace PCP
- Config:
  ```oil
  RESOURCE Res_SharedData {
      RESOURCEPROPERTY = STANDARD;
  };
  ```
- Success: High priority task không bị block bởi Medium task
- Measure: Trace với LED GPIO hoặc logic analyzer
- Time: 3 giờ

**TASK 2.5: MCAL Port/Dio - Control RGB LED**
- Objective: Config 3 pins cho RGB LED, điều khiển màu
- Files:
  - `as/com/as.infrastructure/arch/stm32f1/mcal/Port_Cfg.h`
  - `as/com/as.infrastructure/arch/stm32f1/mcal/Dio_Cfg.h`
- Success: Gọi `Dio_WriteChannel()` đổi màu LED
- Time: 2 giờ

**TASK 2.6 (Extension): Stack Overflow Detection**
- Objective: Tạo task với stack quá nhỏ, detect overflow bằng pattern
- Method: Fill stack với 0xDEADBEEF, check watermark
- Success: Detect overflow trước khi crash
- Time: 3 giờ

---

### CHUYÊN ĐỀ 03: Communication Stack & CAN

**Objective:** Config và test ComStack end-to-end

#### 📁 Source Code Scope:
```
as/com/as.infrastructure/communication/
├── Can/              # MCAL CAN driver
├── CanIf/            # CAN Interface
├── CanTp/            # CAN Transport Protocol (ISO 15765-2)
├── PduR/             # PDU Router
└── Com/              # COM module
```

#### 🎯 Proposed Tasks (5 tasks):

**TASK 3.1: CAN Bit Timing Calculation**
- Objective: Tính toán BTR0/BTR1 cho 500 kbps @ 8MHz
- Tool: Python script hoặc spreadsheet
- Formula: Tài liệu Section 1.4
- Success: Sample Point = 87.5%, SJW = 1
- Time: 1 giờ

**TASK 3.2: CAN Driver - Send Raw Frame**
- Objective: Config CAN1 mailbox, gửi 1 frame ID=0x123
- Files: `Can_Cfg.h`, `Can_PBcfg.c`
- API: `Can_Write(HTH, &PduInfo)`
- Success: Logic analyzer bắt được frame
- Time: 3 giờ

**TASK 3.3: CanIf - Software Filter**
- Objective: Config CanIf chỉ nhận ID 0x100-0x1FF
- Files: `CanIf_Cfg.h`
- Success: Frame ngoài range bị reject (check counter)
- Time: 2 giờ

**TASK 3.4: CanTp - Multi-Frame Transmission**
- Objective: Gửi data 20 bytes qua CanTp (SF/FF/CF flow)
- Config: Block Size = 3, STmin = 10ms
- Success: Wireshark trace thấy đúng sequence SF→FF→CF→CF...
- Time: 4 giờ

**TASK 3.5: COM - Signal Packing**
- Objective: Pack 3 signals vào 1 I-PDU 8 bytes
  - Speed (16-bit, byte 0-1)
  - Gear (4-bit, byte 2 upper nibble)
  - DoorStatus (1-bit, byte 2 bit 3)
- Files: `Com_Cfg.c`
- Success: Verify byte layout bằng debugger
- Time: 3 giờ

**TASK 3.6 (Extension): Bus Load Monitoring**
- Objective: Đo bus load với 10 frames @ 10ms cycle
- Formula: Section 1.3
- Success: Bus load < 30% (safe margin)
- Time: 2 giờ

---

### CHUYÊN ĐỀ 04: Diagnostic UDS & Memory Stack

**Objective:** Implement UDS services và NvM persistence

#### 📁 Source Code Scope:
```
as/com/as.infrastructure/diagnostic/
├── Dcm/              # Diagnostic Communication Manager
├── Dem/              # Diagnostic Event Manager
└── Det/              # Development Error Tracer

as/com/as.infrastructure/memory/
├── NvM/              # Non-Volatile Memory Manager
├── MemIf/            # Memory Interface
├── Fee/              # Flash EEPROM Emulation
└── Fls/              # Flash Driver (MCAL)
```

#### 🎯 Proposed Tasks (5 tasks):

**TASK 4.1: DCM - Implement Service 0x22 (Read DID)**
- Objective: Đọc VIN (DID 0xF190) qua UDS
- Request: `22 F1 90`
- Response: `62 F1 90 [17 bytes VIN ASCII]`
- Files: `Dcm_Cfg.c` - thêm DID definition
- Success: Test bằng Python-UDS hoặc CanOE
- Time: 3 giờ

**TASK 4.2: DCM - Service 0x27 Seed/Key**
- Objective: Implement security unlock algorithm
- Algorithm: `Key = (Seed XOR 0x12345678) + 0xABCD`
- Success: Unlock level 1, sau đó gọi được service 0x2E
- Time: 4 giờ

**TASK 4.3: DEM - Report DTC**
- Objective: Khi nhiệt độ > 60°C, set DTC 0x123456
- API: `Dem_SetEventStatus(DemConf_Event_OverTemp, DEM_EVENT_STATUS_FAILED)`
- Success: Service 0x19 đọc được DTC status byte
- Time: 3 giờ

**TASK 4.4: NvM - Save Calibration Data**
- Objective: Lưu 1 struct 32 bytes vào flash
- Config: NvM block type = Native
- API: `NvM_WriteBlock(NvMConf_Block_CalData, &data)`
- Success: Sau power cycle, data còn đúng
- Time: 4 giờ

**TASK 4.5: Fee - Wear Leveling Analysis**
- Objective: Ghi 1 block 100 lần, kiểm tra fee không tràn flash
- Tool: Monitor flash erase counter
- Success: Virtual sector swap xảy ra, không brick flash
- Time: 3 giờ

**TASK 4.6 (Extension): Freeze Frame**
- Objective: Khi DTC xảy ra, snapshot 5 signals vào freeze frame
- Data: Voltage, Temperature, Speed, Gear, ErrorCounter
- Success: Service 0x19 04 đọc được snapshot
- Time: 4 giờ

---

### CHUYÊN ĐỀ 05: Toolchain & ARXML

**Objective:** Generate code từ ARXML và integrate vào build

#### 📁 Source Code Scope:
```
as/com/as.tool/
├── config.infrastructure.gui/      # GUI configurator
├── config.infrastructure.system/   # System gen tools
└── lua/                            # Code generators

as/release/ascore/
└── SgDesign/                       # Sample ARXML files (nếu có)
```

#### 🎯 Proposed Tasks (4 tasks):

**TASK 5.1: Parse ARXML - Extract Signal List**
- Objective: Viết Python script parse System.arxml, list all signals
- Lib: `lxml` hoặc `xml.etree`
- Output: CSV với (Signal, BitLength, Byte Order, Init Value)
- Success: >= 20 signals extracted
- Time: 3 giờ

**TASK 5.2: Generate OIL from Template**
- Objective: Tạo app.oil từ Jinja2 template + JSON config
- Template vars: `{{task_name}}`, `{{priority}}`, `{{stack_size}}`
- Success: Generated OIL compile thành công
- Time: 2 giờ

**TASK 5.3: EcuM Startup Flow Trace**
- Objective: Trace boot flow với breakpoints
- Breakpoints:
  1. `EcuM_Init()` entry
  2. `StartOS()` call
  3. `EcuM_StartupTwo()` entry
  4. `Rte_Start()` call
- Success: Measure time từng phase < 100ms
- Time: 2 giờ

**TASK 5.4: BswM Mode Switch**
- Objective: Config BswM switch từ STARTUP → RUN mode
- Trigger: NvM_ReadAll() complete
- Effect: Enable COM transmission
- Success: Log message "BswM: Switched to RUN mode"
- Time: 3 giờ

**TASK 5.5 (Extension): Full DaVinci Workflow**
- Objective: Import mock System.arxml → Generate RTE → Integrate
- Tools: DaVinci Developer (nếu có license) hoặc mock gen
- Success: SWC app code compile với generated Rte.h
- Time: 6 giờ

---

### CHUYÊN ĐỀ 06: Real-World Applications

**Objective:** Implement mini BMS hoặc VCU với đầy đủ stack

#### 📁 Source Code Scope:
```
as/com/as.application/
├── board.*/               # Board-specific apps
│   ├── app.c              # Application entry
│   ├── app.oil            # OS config
│   └── swc/               # Software components
└── common/                # Shared utilities
```

#### 🎯 Proposed Tasks (3 major projects):

**TASK 6.1: Mini BMS - SoC Calculation**
- Objective: Implement Coulomb Counting algorithm
- Inputs:
  - ADC: Pack current (mA)
  - Timer: Sampling every 10ms
- Output:
  - SoC % (0-100%)
  - CAN signal broadcast @ 100ms
- Success: SoC accurate ±5% vs reference
- Time: 8 giờ

**TASK 6.2: VCU - Torque Request**
- Objective: Calc torque request từ accelerator pedal
- Inputs:
  - ADC1: Pedal position sensor 1
  - ADC2: Pedal position sensor 2 (redundancy)
- Logic:
  - Plausibility check: |Sensor1 - Sensor2| < 5%
  - Torque map: 0-100% pedal → 0-300 Nm
- Success: Torque command gửi qua CAN
- Time: 10 giờ

**TASK 6.3: Body Controller - Door Lock Central**
- Objective: Central door lock với CAN wakeup
- Features:
  - CAN wakeup từ sleep mode
  - Lock/unlock 4 doors via relay
  - LED indicator
- Success: Current < 1mA trong sleep mode
- Time: 8 giờ

**TASK 6.4 (Extension): Full Integration Test**
- Objective: Chạy cả 3 ECUs (BMS+VCU+Body) trên 1 CAN bus
- Test scenarios:
  1. BMS báo SoC low → VCU limit torque
  2. Door unlock → BMS wakeup
- Success: Full system stable 1 giờ liên tục
- Time: 12 giờ

---

## 🔍 CHECKLIST OUTPUT QUALITY

Plan phải đạt các tiêu chí:

### A. Completeness (Đầy đủ)
- [ ] Tất cả 6 chuyên đề đều có tasks
- [ ] Mỗi chuyên đề có 3-5 tasks + 1 extension
- [ ] Tổng 25-30 tasks trong 3-4 tuần

### B. Specificity (Cụ thể)
- [ ] Mỗi task có file path chính xác
- [ ] Command/code example rõ ràng
- [ ] Success criteria đo được (không mơ hồ)

### C. Difficulty Progression (Tăng dần)
- [ ] Task 1 mỗi chuyên đề: Beginner (read-only)
- [ ] Task 2-3: Intermediate (config/modify)
- [ ] Task 4+: Advanced (implement logic)

### D. Real-World Alignment (Thực tế)
- [ ] Task training skills BSW Integrator cần
- [ ] Không có "Hello World" vô nghĩa
- [ ] Có scenarios giống dự án production

### E. Tool Coverage (Công cụ đầy đủ)
- [ ] Build system: SCons/Make
- [ ] Debug: GDB/OpenOCD
- [ ] Analysis: Python scripts
- [ ] Measurement: Timer/profiler

---

## 📊 EXAMPLE OUTPUT FORMAT

```markdown
# HANDS-ON TASK MASTER PLAN - AUTOSAR PRACTICAL MASTERY

**Total Tasks:** 28 tasks (6 chuyên đề × ~4-5 tasks)  
**Total Time:** 80-100 giờ (3-4 tuần @ 25-30 giờ/tuần)  
**Difficulty:** Beginner → Advanced (progressive)

---

## CHUYÊN ĐỀ 01: Layered Architecture & VFB (8 giờ)

### 📚 Theory Prerequisite
- Đọc `docs/01_AUTOSAR_Layered_Architecture_And_VFB_Masterclass.md`
- Focus: Section 2 (Layered Architecture), Section 4 (RTE)

### 🔧 Source Code Base
```
as/com/as.infrastructure/
├── include/Std_Types.h
├── include/Compiler.h
├── arch/              (MCAL layer)
├── communication/     (ComStack layer)
└── system/            (Service layer)
```

---

### 🎯 TASK 1.1: Code Navigation - Trace Message Through Layers

**⏱️ Time:** 2 giờ  
**📖 Prerequisite:** Section 2.1-2.4 đọc xong  
**🎚️ Difficulty:** ⭐ Beginner

**Objective:**  
Trace 1 CAN message từ Application SWC xuống CAN Controller Driver, vẽ call graph.

**📁 Files to Read:**
```
as/com/as.application/board.stm32f107vc/swc/
as/com/as.infrastructure/communication/Com/Com.c
as/com/as.infrastructure/communication/PduR/PduR.c
as/com/as.infrastructure/communication/CanIf/CanIf.c
as/com/as.infrastructure/communication/Can/Can.c
```

**📝 Steps:**

1. **Tìm entry point:**
   ```bash
   cd Study_AUTOSAR-main/as
   grep -r "Rte_Write" --include="*.c" | head -10
   ```
   → Note function name và location

2. **Trace xuống COM layer:**
   ```bash
   grep -r "Com_SendSignal" communication/Com/
   ```
   → Đọc implementation `Com_SendSignal()` trong `Com.c`

3. **Trace xuống PduR:**
   - Trong `Com.c`, tìm call `PduR_ComTransmit()`
   - Mở `PduR.c`, đọc routing logic

4. **Trace xuống CanIf:**
   - Tìm `CanIf_Transmit()` trong `CanIf.c`
   - Note: HTH (Hardware Transmit Handle) mapping

5. **Trace xuống Can Driver:**
   - Tìm `Can_Write()` trong `Can.c`
   - Note: Mailbox configuration

6. **Vẽ call graph:**
   ```
   [SWC App]
      │
      │ Rte_Write_PpSpeed_Speed(uint16 speed)
      ▼
   [RTE Generated Code]
      │
      │ Com_SendSignal(ComConf_Signal_Speed, &speed)
      ▼
   [COM Module]
      │
      │ PduR_ComTransmit(PduId, &PduInfo)
      ▼
   [PduR]
      │
      │ CanIf_Transmit(CanTxPduId, &PduInfo)
      ▼
   [CanIf]
      │
      │ Can_Write(HTH_0, &PduInfo)
      ▼
   [Can Driver]
      │
      │ Write to CAN Controller Mailbox Register
      ▼
   [CAN Hardware]
   ```

**✅ Success Criteria:**
- [ ] Call graph vẽ đủ 6 layers
- [ ] Note được tên hàm chính xác (không "...")
- [ ] Giải thích được vai trò mỗi layer trong 1-2 câu

**🐛 Common Pitfalls:**
- ⚠️ Nhầm lẫn giữa `Com_SendSignal()` và `Com_TriggerTransmit()`
  → Fix: Đọc kỹ comment trong code
- ⚠️ Không tìm thấy PduR routing config
  → Fix: Check `PduR_Cfg.c` / `PduR_PBcfg.c`

**🌟 Extension Challenge:**
- Trace ngược lại: CAN Rx ISR → SWC (Reception path)
- Count total lines of code cho message path (~300-500 LOC)

---

### 🎯 TASK 1.2: Dependency Analysis - Draw BSW Init Graph

[... tương tự format trên cho 27 tasks còn lại ...]

```

---

## 🚀 CÁCH SỬ DỤNG PROMPT NÀY

### Bước 1: Gửi cho AI

Copy toàn bộ file này và gửi:

```
Hãy phân tích source code trong `Study_AUTOSAR-main/as/` 
và tạo HANDS-ON TASK MASTER PLAN theo template trên với yêu cầu:

1. Phân tích 6 chuyên đề tài liệu
2. Map với source code cụ thể trong as/
3. Tạo 4-5 tasks/chuyên đề (tổng ~25-30 tasks)
4. Mỗi task phải có:
   - File paths chính xác
   - Commands cụ thể
   - Success criteria đo được
   - Time estimate realistic

Focus vào:
- Tasks training skills BSW Integration Engineer cần
- Tận dụng nền tảng RTOS/Driver của Mid-level Engineer
- Progressive difficulty: Read → Config → Implement

Output format: Markdown file, follow template TASK 1.1 ở trên.
```

### Bước 2: Review Output

Checklist sau khi nhận plan:

- [ ] Đếm tasks: Phải có 25-30 tasks
- [ ] Check file paths: Verify tồn tại trong repo
- [ ] Time estimate: Tổng 80-100 giờ (3-4 tuần)
- [ ] Difficulty progression: Easy → Hard
- [ ] Success criteria: Cụ thể, đo được

### Bước 3: Execute Plan

```bash
# Tạo tracking sheet
touch PROGRESS.md

# Format:
## Week 1
- [x] Task 1.1 ✅ (2.5h actual, 2h estimated)
- [ ] Task 1.2 🚧 (in progress)
- [ ] Task 1.3

## Week 2
...
```

---

## 📈 EXPECTED LEARNING OUTCOMES

Sau khi hoàn thành 28 tasks:

### Technical Skills
✅ Build AUTOSAR project từ source  
✅ Config OS tasks và priorities  
✅ Setup ComStack end-to-end  
✅ Implement UDS diagnostic services  
✅ Use toolchain (SCons/GDB/Python)  

### Soft Skills
✅ Code navigation trong large codebase (2190+ files)  
✅ Debugging systematic approach  
✅ Documentation reading (SWS specs)  

### Interview Readiness
✅ Demo được mini-project (BMS/VCU)  
✅ Explain được AUTOSAR architecture với confidence  
✅ Answer technical questions với code examples  

---

**🎯 MỤC TIÊU:**

> "Sau 3-4 tuần intensive hands-on, bạn có thể tự tin apply vị trí BSW Integration Engineer / ECU Software Engineer với portfolio GitHub chứa code AUTOSAR thật đã build và chạy được."

---

**END OF HANDS-ON PLAN PROMPT**

Sử dụng prompt này để generate detailed task plan cho learning path của bạn.
