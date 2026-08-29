# 🗺️ HANDS-ON TASK MASTER PLAN — AUTOSAR PRACTICAL MASTERY
## Kế Hoạch Thực Hành 4 Tuần Dành Cho Mid-level Embedded Engineer

> **Đối tượng:** Mid-level Embedded Engineer có nền tảng RTOS/Driver/BSP
> **Mục tiêu:** Thực hành Learning-by-Doing trên source code thực tế `Study_AUTOSAR-main/as/`
> **Thời gian:** ~4 tuần (25–30 giờ/tuần, tổng ~99 giờ)
> **Build target mặc định:** `scons --board=posix` (POSIX simulator, không cần phần cứng)

---

## 📁 Cấu Trúc Thư Mục Tasks

```
docs/hands_on_tasks/
├── 00_MASTER_PLAN_INDEX.md          ← File này (Roadmap tổng thể)
├── 01_Architecture_VFB_Tasks.md     ← Chuyên đề 01: Layered Arch & VFB (5 tasks)
├── 02_OS_MCAL_Tasks.md              ← Chuyên đề 02: AUTOSAR OS & MCAL (5+1 tasks)
├── 03_ComStack_CAN_Tasks.md         ← Chuyên đề 03: ComStack & CAN Protocol (7 tasks)
├── 04_Diagnostic_Memory_Tasks.md    ← Chuyên đề 04: UDS Diagnostic & Memory (5+1 tasks)
├── 05_Toolchain_ARXML_Tasks.md      ← Chuyên đề 05: Toolchain & ARXML (4+1 tasks)
├── 06_RealWorld_BMS_VCU_Tasks.md    ← Chuyên đề 06: BMS / VCU / Body ECU (3+1 tasks)
├── 07_LIN_Stack_Tasks.md            ← Chuyên đề 07: LIN Protocol & LinStack (4 tasks)
├── 08_Ethernet_SOMEIP_DoIP_Tasks.md ← Chuyên đề 08: Automotive Ethernet & SOME/IP/DoIP (4 tasks)
└── solutions/
    ├── 01_Architecture_VFB_Solutions.md     ← Đáp án Chuyên Đề 01 (Boot, Hooks, Linker, BSW Order, Ports)
    ├── 02_ComStack_CAN_Solutions.md         ← Đáp án Chuyên Đề 03 (End-to-End CAN 6 Tầng, Timing, CanTp, COM)
    └── 03_LIN_Ethernet_Solutions.md         ← Đáp án Chuyên Đề 07 & 08 (LIN Stack & Automotive Ethernet/DoIP)
```

---

## 📊 Tổng Quan Nhiệm Vụ (Task Summary Matrix)

| # | File Task | Chuyên Đề | Số Tasks | Giờ Ước Tính | Tuần |
|:---:|---|---|:---:|:---:|:---:|
| 01 | [Architecture & VFB](./01_Architecture_VFB_Tasks.md) | Layered Architecture, RTE, Memory, OS Hooks | 5 tasks | ~12 giờ | Tuần 1 |
| 02 | [OS & MCAL](./02_OS_MCAL_Tasks.md) | OSEK OS, Task, ISR, MCAL Drivers | 5+1 tasks | ~15 giờ | Tuần 1–2 |
| 03 | [ComStack & CAN](./03_ComStack_CAN_Tasks.md) | CAN Protocol, 6-Layer ComStack E2E, CanTp, COM | 7 tasks | ~17 giờ | Tuần 2 |
| 04 | [Diagnostic & Memory](./04_Diagnostic_Memory_Tasks.md) | UDS, DCM, DEM, NvM, Fee | 5+1 tasks | ~18 giờ | Tuần 3 |
| 05 | [Toolchain & ARXML](./05_Toolchain_ARXML_Tasks.md) | ARXML, EcuM, BswM, Code Gen | 4+1 tasks | ~12 giờ | Tuần 3–4 |
| 06 | [Real-World BMS/VCU/Body](./06_RealWorld_BMS_VCU_Tasks.md) | Mini BMS, VCU Torque, BCM Sleep | 3+1 tasks | ~30 giờ | Tuần 4 |
| 07 | [LIN Stack](./07_LIN_Stack_Tasks.md) | LIN Protocol, LinIf Schedule, Wiper Control | 4 tasks | ~8 giờ | Tuần 4 |
| 08 | [Automotive Ethernet](./08_Ethernet_SOMEIP_DoIP_Tasks.md) | 100BASE-T1, SOME/IP, DoIP, SoAd | 4 tasks | ~8 giờ | Tuần 4 |
| | **TỔNG** | | **35 tasks** | **~115 giờ** | **4–5 Tuần** |

---

## 🚀 Cách Build Source Code

```bash
# Di chuyển vào thư mục as/
cd Study_AUTOSAR-main/as

# Build trên POSIX simulator (không cần phần cứng, chạy trên Windows/Linux)
scons --board=posix

# Build cho QEMU ARM Target lm3s6965evb (Khuyên dùng - Cortex-M3 thật)
$env:BOARD="lm3s6965evb"; $env:RELEASE="ascore"; scons

# Build cho POSIX Simulator
scons --board=posix

# Build cho STM32F107VC Chip Thật (Tùy chọn)
scons --board=stm32f107vc

# Chạy POSIX simulator
./build/posix/as

# Debug với GDB (POSIX)
gdb ./build/posix/as
```

---

## 🗓️ Lịch Học 4 Tuần

```
TUẦN 1 (Nền tảng Architecture + OS):
├── Task 1.1: Code Navigation — Trace CAN Message (2h)
├── Task 1.2: Dependency Analysis — BSW Init Order (3h)
├── Task 1.3: Linker Script — Memory Section Map (2h)
├── Task 1.4: RTE Port Mapping (3h)
├── Task 2.1: Build OSEK OS from Source (2h)
└── Task 2.2: Create Basic Task Periodic (3h)

TUẦN 2 (OS sâu + ComStack):
├── Task 2.3: Extended Task Event-Driven CAN (4h)
├── Task 2.4: Resource & Priority Ceiling (3h)
├── Task 2.5: MCAL Port/Dio Analysis (2h)
├── Task 3.1: CAN Bit Timing Calculation (1h)
├── Task 3.2: CAN Driver Source & Mailbox Config (3h)
└── Task 3.3: CanIf Acceptance Filter (2h)

TUẦN 3 (ComStack hoàn thiện + Diagnostic):
├── Task 3.4: CanTp Multi-Frame Transmission (4h)
├── Task 3.5: COM Signal Packing (3h)
├── Task 4.1: DCM Service 0x22 Read DID (3h)
├── Task 4.2: SecurityAccess 0x27 Seed/Key (4h)
├── Task 4.3: DEM Report DTC + Debounce (3h)
└── Task 4.4: NvM Save Calibration Data (4h)

TUẦN 4 (Memory + Toolchain + Real Projects):
├── Task 4.5: Fee Wear Leveling Analysis (3h)
├── Task 5.1: Parse ARXML Extract Signals (3h)
├── Task 5.2: Generate OIL from Template (2h)
├── Task 5.3: EcuM Startup Flow Trace (2h)
├── Task 5.4: BswM Mode Switch (3h)
└── Task 6.1: Mini BMS SoC + CAN Broadcast (8h)
    [Optional] Task 6.2: VCU Torque Request (8h)
    [Optional] Task 6.3: BCM Sleep/Wakeup (8h)
    [Optional] Task 6.4: Full Integration Test (12h)
```

---

## 📈 Progress Tracker

Copy bảng này vào file `PROGRESS.md` để theo dõi tiến độ cá nhân:

```markdown
# AUTOSAR Learning Progress

## Tuần 1
- [ ] Task 1.1 Code Navigation         (est: 2h | actual: ___h) ___
- [ ] Task 1.2 Dependency Analysis      (est: 3h | actual: ___h) ___
- [ ] Task 1.3 Linker Script            (est: 2h | actual: ___h) ___
- [ ] Task 1.4 RTE Port Mapping         (est: 3h | actual: ___h) ___
- [ ] Task 2.1 Build OS                 (est: 2h | actual: ___h) ___
- [ ] Task 2.2 Basic Task               (est: 3h | actual: ___h) ___

## Tuần 2
- [ ] Task 2.3 Extended Task CAN        (est: 4h | actual: ___h) ___
- [ ] Task 2.4 Resource PCP             (est: 3h | actual: ___h) ___
- [ ] Task 2.5 MCAL Dio                 (est: 2h | actual: ___h) ___
- [ ] Task 3.1 CAN Bit Timing           (est: 1h | actual: ___h) ___
- [ ] Task 3.2 CAN Raw Frame            (est: 3h | actual: ___h) ___
- [ ] Task 3.3 CanIf Filter             (est: 2h | actual: ___h) ___

## Tuần 3
- [ ] Task 3.4 CanTp MultiFrame         (est: 4h | actual: ___h) ___
- [ ] Task 3.5 COM Signal Pack          (est: 3h | actual: ___h) ___
- [ ] Task 4.1 DCM Read DID             (est: 3h | actual: ___h) ___
- [ ] Task 4.2 SecurityAccess           (est: 4h | actual: ___h) ___
- [ ] Task 4.3 DEM DTC                  (est: 3h | actual: ___h) ___
- [ ] Task 4.4 NvM Save Data            (est: 4h | actual: ___h) ___

## Tuần 4
- [ ] Task 4.5 Fee Wear Level           (est: 3h | actual: ___h) ___
- [ ] Task 5.1 Parse ARXML              (est: 3h | actual: ___h) ___
- [ ] Task 5.2 OIL Generator            (est: 2h | actual: ___h) ___
- [ ] Task 5.3 EcuM Startup Trace       (est: 2h | actual: ___h) ___
- [ ] Task 5.4 BswM Mode Switch         (est: 3h | actual: ___h) ___
- [ ] Task 6.1 Mini BMS SoC             (est: 8h | actual: ___h) ___
- [ ] Task 6.2 VCU Torque (Optional)    (est: 8h | actual: ___h) ___
- [ ] Task 6.3 BCM Sleep (Optional)     (est: 8h | actual: ___h) ___
- [ ] Task 6.4 Integration (Optional)   (est: 12h| actual: ___h) ___
```

---

## 🎯 Kết Quả Mong Đợi Sau 4 Tuần

| Kỹ Năng | Trước | Sau |
|---|:---:|:---:|
| Đọc hiểu codebase AUTOSAR (2190+ files) | ❌ | ✅ |
| Build project với SCons từ source | ❌ | ✅ |
| Config OSEK OS tasks, ISR, Resource | ❌ | ✅ |
| Setup ComStack CAN end-to-end | ❌ | ✅ |
| Implement UDS Service 0x22/0x27 | ❌ | ✅ |
| Config NvM + Fee data persistence | ❌ | ✅ |
| Trace EcuM startup boot flow | ❌ | ✅ |
| Thiết kế mini BMS/VCU SWC | ❌ | ✅ |
| Trả lời phỏng vấn với code demo thật | ❌ | ✅ |

---

## 💡 Gợi Ý Thực Hành

- **Commit mỗi task hoàn thành** lên GitHub để tạo portfolio
- **Ghi lại thời gian thực tế** vs ước tính để tự đánh giá
- **Ưu tiên POSIX simulator** — không cần phần cứng thật
- **Đọc lý thuyết tương ứng** trước khi bắt đầu mỗi task

---

*📌 Được tạo bởi HANDS_ON_PLAN_PROMPT.md | Study_AUTOSAR-main*
