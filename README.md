# 🚗 AUTOSAR Classic & Adaptive — Self-Study Engineering Platform

> **Ngôn ngữ:** Tiếng Việt Kỹ Nghệ (Automotive Systems Engineering Standard)  
> **Mục tiêu nghề nghiệp:** BSW Integration Engineer · ECU Software Engineer (BMS / VCU / Body / Inverter)  
> **Công ty mục tiêu:** VinFast · Bosch BGSV · LG Vehicle Solutions · Hyundai Kefico · FPT Automotive · Vector · Elektrobit  
> **Mã nguồn thực tế:** `as/` — 2.190+ tệp tin C/H, ARXML, Tools (Dựa trên kiến trúc mã nguồn mở chuẩn AUTOSAR 4.x)

---

## 📁 Cấu Trúc Kho Lưu Trữ (Repository Architecture)

```text
Study_AUTOSAR-main/
├── as/                              ← Source code AUTOSAR BSW, RTE, OS, MCAL thực tế (2.190+ files)
│   ├── com/as.infrastructure/       ← Các tầng BSW chuẩn (ComStack, Diag, Memory, System, MCAL)
│   ├── com/as.application/          ← Các ứng dụng SWC mẫu (BMS, VCU, BCM) và Board target
│   └── release/ascore/              ← Cấu hình tích hợp và ứng dụng ECU mẫu (main, EcuM stubs)
│
└── docs/                            ← Hệ thống tài liệu kỹ thuật toàn diện
    ├── theory/                      ← 📖 14 Chuyên đề lý thuyết từ nền tảng đến chuyên sâu (00 → 12)
    ├── deep_dive/                   ← 🔬 Lần vết luồng thực thi từng dòng code (End-to-End Trace)
    ├── hands_on_tasks/              ← 🛠️ 35 Nhiệm vụ thực hành 4–5 tuần (Chuyên đề 01 → 08)
    │   ├── solutions/               ← 💡 Bộ lời giải mẫu chi tiết kèm số dòng code (Code Trace)
    │   └── task_fix/                ← 🧩 Phân tích nguyên nhân gốc (RCA) & so sánh trước/sau khi fix
    ├── reference/                   ← 📌 Cheatsheet, hướng dẫn debug (GDB/Trace32/QEMU) & Python scripts
    ├── samples/                     ← 📂 ARXML chuẩn AUTOSAR 4.3, DBC network & Python ARXML parser
    └── career/                      ← 🎯 Cẩm nang xây dựng Portfolio & bộ câu hỏi phỏng vấn Tier-1/OEM
```

---

## 🗺️ LỘ TRÌNH HỌC TẬP VÀ THỰC HÀNH (5 BƯỚC CHUẨN KỸ NGHỆ)

```
[BƯỚC 0: SETUP MÔI TRƯỜNG]  -->  [BƯỚC 1: LÝ THUYẾT NỀN TẢNG]  -->  [BƯỚC 2: 35 HANDS-ON TASKS]
 (SCons, GCC, QEMU, Python)       (14 Chuyên đề Theory 00->12)        (Thực hành trên repo as/)
                                                                               │
                                                                               ▼
[BƯỚC 4: PHỎNG VẤN & CAREER] <--  [BƯỚC 3: DEEP DIVE & RCA]   <─────────────────┘
 (Portfolio, Q&A Tier-1/OEM)      (Call Graphs, Memory, Fixes)
```

---

### 🚀 BƯỚC 0 — Chuẩn Bị Môi Trường Thực Hành (1–2 ngày)

> 📖 **Đọc trước:** [`docs/theory/00_BUILD_ENVIRONMENT_SETUP.md`](docs/theory/00_BUILD_ENVIRONMENT_SETUP.md)

* **Cài đặt:** Python 3.9+, SCons, GCC ARM Embedded Toolchain (`arm-none-eabi-gcc`), QEMU ARM (`qemu-system-arm`), SavvyCAN.
* **Xác thực môi trường:**
  ```powershell
  # 1. Build & chạy trên POSIX Simulator (Không cần phần cứng):
  cd as
  scons --board=posix
  ./build/posix/as

  # 2. Build cho QEMU ARM Cortex-M3 (Board lm3s6965evb):
  $env:BOARD="lm3s6965evb"; $env:RELEASE="ascore"; scons
  ```

---

### 📖 BƯỚC 1 — Nắm Vững Lý Thuyết Chuyên Sâu (14 Chuyên Đề)

| # | Tài Liệu Lý Thuyết | Nội Dung Cốt Lõi | Trọng Số |
|:---:|---|---|:---:|
| 00 | [`00_AUTOSAR_READING_ROADMAP.md`](docs/theory/00_AUTOSAR_READING_ROADMAP.md) | Lộ trình đọc tài liệu và phân cấp kỹ năng theo tuần | Khởi động |
| 01 | [`01_AUTOSAR_Layered_Architecture_And_VFB_Masterclass.md`](docs/theory/01_AUTOSAR_Layered_Architecture_And_VFB_Masterclass.md) | Kiến trúc 4 tầng, VFB, RTE Ports/Interfaces, SWC Types | ⭐⭐⭐⭐⭐ |
| 02 | [`02_AUTOSAR_OS_And_MCAL_Deep_Dive.md`](docs/theory/02_AUTOSAR_OS_And_MCAL_Deep_Dive.md) | OSEK OS (BCC1/ECC2), Task Scheduler, ISR 1/2, Resource Ceiling | ⭐⭐⭐⭐⭐ |
| 03 | [`03_Communication_Stack_And_CAN_Protocol.md`](docs/theory/03_Communication_Stack_And_CAN_Protocol.md) | CAN/CAN-FD Protocol, Bit Timing, COM, PduR, CanIf, CanTp | ⭐⭐⭐⭐⭐ |
| 04 | [`04_Diagnostic_UDS_And_Memory_Stack.md`](docs/theory/04_Diagnostic_UDS_And_Memory_Stack.md) | UDS ISO 14229 (DCM, DEM, FIM), NvM, MemIf, Fee/Ea Wear Leveling | ⭐⭐⭐⭐⭐ |
| 05 | [`05_Toolchain_ARXML_And_ECU_Integration.md`](docs/theory/05_Toolchain_ARXML_And_ECU_Integration.md) | Toolchain Vector DaVinci/EB Tresos/ArGen, ARXML, EcuM, BswM | ⭐⭐⭐⭐ |
| 06 | [`06_Real_World_ECU_Applications_BMS_VCU_Body.md`](docs/theory/06_Real_World_ECU_Applications_BMS_VCU_Body.md) | Kiến trúc ECU thực tế trên EV: BMS SoC/SoH, VCU Torque, BCM | ⭐⭐⭐⭐⭐ |
| 07 | [`07_ISO26262_Functional_Safety_Awareness.md`](docs/theory/07_ISO26262_Functional_Safety_Awareness.md) | An toàn chức năng FuSa, ASIL A/B/C/D, HARA, E2E Protection | ⭐⭐⭐⭐ |
| 08 | [`08_AUTOSAR_Adaptive_Platform_Overview.md`](docs/theory/08_AUTOSAR_Adaptive_Platform_Overview.md) | AUTOSAR Adaptive (ARA), POSIX, SOME/IP, C++14/17, Manifest | ⭐⭐⭐ |
| 09 | [`09_ASPICE_VModel_Process.md`](docs/theory/09_ASPICE_VModel_Process.md) | Quy trình Automotive SPICE, SWE.1 → SWE.6, Traceability | ⭐⭐⭐ |
| 10 | [`10_CAN_DBC_Format_And_Tools.md`](docs/theory/10_CAN_DBC_Format_And_Tools.md) | Cú pháp DBC, Signal Packing, Multiplexing, DBC $\leftrightarrow$ ARXML | ⭐⭐⭐ |
| 11 | [`11_LIN_Protocol_And_LinStack_Deep_Dive.md`](docs/theory/11_LIN_Protocol_And_LinStack_Deep_Dive.md) | LIN 2.1/2.2, Master-Slave Schedule Table, LinIf, LinTp, LinNm | ⭐⭐⭐⭐ |
| 12 | [`12_Automotive_Ethernet_SOMEIP_DoIP_Deep_Dive.md`](docs/theory/12_Automotive_Ethernet_SOMEIP_DoIP_Deep_Dive.md) | 100BASE-T1, TCP/IP, SoAd (Socket Adaptor), SOME/IP, DoIP (ISO 13400) | ⭐⭐⭐⭐ |

---

### 🛠️ BƯỚC 2 — Thực Hành 35 Hands-On Tasks Chuẩn Kỹ Nghệ

> 📋 **Master Index:** [`docs/hands_on_tasks/00_MASTER_PLAN_INDEX.md`](docs/hands_on_tasks/00_MASTER_PLAN_INDEX.md)  
> 🛑 **Quy tắc làm việc:** [`docs/hands_on_tasks/task_fix/rule.md`](docs/hands_on_tasks/task_fix/rule.md) *(3 Golden Rules: Tuyệt đối không sửa mã sinh tự động, ARXML là Single Source of Truth, phân vùng mã nguồn)*

| Chuyên Đề | File Nhiệm Vụ | Số Tasks | Thời Gian Ước Tính |
|---|---|:---:|:---:|
| **01. Architecture & VFB** | [`01_Architecture_VFB_Tasks.md`](docs/hands_on_tasks/01_Architecture_VFB_Tasks.md) | 4 tasks | ~10 giờ |
| **02. OS & MCAL** | [`02_OS_MCAL_Tasks.md`](docs/hands_on_tasks/02_OS_MCAL_Tasks.md) | 5+1 tasks | ~15 giờ |
| **03. ComStack & CAN** | [`03_ComStack_CAN_Tasks.md`](docs/hands_on_tasks/03_ComStack_CAN_Tasks.md) | 5+1 tasks | ~14 giờ |
| **04. Diagnostic & Memory** | [`04_Diagnostic_Memory_Tasks.md`](docs/hands_on_tasks/04_Diagnostic_Memory_Tasks.md) | 5+1 tasks | ~18 giờ |
| **05. Toolchain & ARXML** | [`05_Toolchain_ARXML_Tasks.md`](docs/hands_on_tasks/05_Toolchain_ARXML_Tasks.md) | 4+1 tasks | ~12 giờ |
| **06. Real-World BMS / VCU** | [`06_RealWorld_BMS_VCU_Tasks.md`](docs/hands_on_tasks/06_RealWorld_BMS_VCU_Tasks.md) | 3+1 tasks | ~30 giờ |
| **07. LIN Protocol Stack** | [`07_LIN_Stack_Tasks.md`](docs/hands_on_tasks/07_LIN_Stack_Tasks.md) | 4 tasks | ~8 giờ |
| **08. Automotive Ethernet & DoIP** | [`08_Ethernet_SOMEIP_DoIP_Tasks.md`](docs/hands_on_tasks/08_Ethernet_SOMEIP_DoIP_Tasks.md) | 4 tasks | ~8 giờ |
| **TỔNG CỘNG** | **8 Chuyên Đề Toàn Diện** | **35 Tasks** | **~115 Giờ (~4–5 Tuần)** |

---

### 🔬 BƯỚC 3 — Tham Khảo Deep Dive Traces & Lời Giải Mẫu

* **Lần vết luồng thực thi (Deep Dive):**
  * [`COM_STACK_END_TO_END_TRACE.md`](docs/deep_dive/COM_STACK_END_TO_END_TRACE.md): Lần vết từ `Rte_Write` $\rightarrow$ `Com` $\rightarrow$ `PduR` $\rightarrow$ `CanIf` $\rightarrow$ `Can_Write` $\rightarrow$ CAN Bus $\rightarrow$ `CanIf_RxIndication` $\rightarrow$ `Rte_Read`.
  * [`ECU_STARTUP_AND_SHUTDOWN_DEEP_DIVE.md`](docs/deep_dive/ECU_STARTUP_AND_SHUTDOWN_DEEP_DIVE.md): Lần vết từ `reset_handler` $\rightarrow$ `main` $\rightarrow$ `EcuM_Init` $\rightarrow$ `StartOS` $\rightarrow$ `EcuM_StartupTwo` $\rightarrow$ chế độ `RUN`.
  * [`NVM_MEMORY_STACK_DEEP_DIVE.md`](docs/deep_dive/NVM_MEMORY_STACK_DEEP_DIVE.md): Lần vết `NvM_WriteBlock` $\rightarrow$ `MemIf` $\rightarrow$ `Fee` (Wear Leveling) $\rightarrow$ Flash EEPROM.
* **Bộ lời giải mẫu chi tiết:**
  * [`01_Architecture_VFB_Solutions.md`](docs/hands_on_tasks/solutions/01_Architecture_VFB_Solutions.md): Lời giải trích dẫn chính xác số dòng code trong repo `as/`.
  * [`03_LIN_Ethernet_Solutions.md`](docs/hands_on_tasks/solutions/03_LIN_Ethernet_Solutions.md): Lời giải mẫu cho chuyên đề LIN và Ethernet / SOME/IP.
* **Nghiên cứu ca sửa lỗi thực tế (Root Cause Analysis - RCA):**
  * [`task_fix/01_fix_qemu_board_lm3s6965evb_target/`](docs/hands_on_tasks/task_fix/01_fix_qemu_board_lm3s6965evb_target/README.md): Khắc phục lỗi tương thích target QEMU Cortex-M3.
  * [`task_fix/02_fix_savvycan_slcan_streaming_integration/`](docs/hands_on_tasks/task_fix/02_fix_savvycan_slcan_streaming_integration/README.md): Tích hợp giao thức SLCAN stream dữ liệu sang SavvyCAN.
  * [`task_fix/03_enable_full_bsw_and_hook_logging/`](docs/hands_on_tasks/task_fix/03_enable_full_bsw_and_hook_logging/README.md): Kích hoạt log chi tiết cho toàn bộ BSW và OS Hooks.

---

### 📌 BƯỚC 4 — Công Cụ & Script Kiểm Thử Chẩn Đoán (Reference Tools)

* [`CHEATSHEET_QUICK_REFERENCE.md`](docs/reference/CHEATSHEET_QUICK_REFERENCE.md): Tra cứu nhanh BSW APIs, mã lỗi UDS NRC, cú pháp OIL, kiểu dữ liệu chuẩn AUTOSAR.
* [`DEBUGGING_AND_PROFILING_GUIDE.md`](docs/reference/DEBUGGING_AND_PROFILING_GUIDE.md): Hướng dẫn gỡ lỗi nâng cao với GDB, QEMU, Lauterbach Trace32, phân tích HardFault.
* **Bộ Test Scripts Python UDS qua CAN/DoIP:** [`docs/reference/python_can_scripts/`](docs/reference/python_can_scripts/)
  * `01_session_control.py`: UDS Service `0x10` (Default, Extended, Programming Session).
  * `02_read_did.py`: UDS Service `0x22` (Đọc Battery Voltage, SoC, Firmware Version).
  * `03_security_access.py`: UDS Service `0x27` (Thuật toán Seed/Key cấp độ Level 1 & Level 2).
  * `04_read_dtc.py`: UDS Service `0x19` (Đọc mã lỗi DTC từ DEM).
  * `05_clear_dtc.py`: UDS Service `0x14` (Xóa mã lỗi chẩn đoán).
  * `06_can_sniffer.py` & `send_virtual_can.py`: Lắng nghe và giả lập khung truyền CAN ảo.
* **Dữ liệu mạng & ARXML mẫu:** [`docs/samples/`](docs/samples/)
  * `SWCD_BMS_Sample.arxml` & `System_Sample.arxml`: File mô tả phần mềm chuẩn AUTOSAR 4.3.
  * `Vehicle_Network.dbc`: Cơ sở dữ liệu mạng CAN xe điện.
  * `parse_arxml.py`: Công cụ Python tự động bóc tách Signal, Port, Runnable từ file ARXML.

---

### 🎯 BƯỚC 5 — Chuẩn Bị Phỏng Vấn & Xây Dựng Portfolio

> 💼 **Đọc ngay:** [`docs/career/PORTFOLIO_GUIDE.md`](docs/career/PORTFOLIO_GUIDE.md)

* **Thiết lập GitHub Portfolio chuẩn Tier-1/OEM:** Hướng dẫn cấu trúc kho mã nguồn cá nhân, tài liệu kỹ thuật, demo video, và kết quả kiểm thử.
* **Bộ câu hỏi phỏng vấn kỹ thuật:** Tổng hợp 200+ câu hỏi phỏng vấn chuyên sâu theo 3 cấp độ (Fresher/Junior $\rightarrow$ Mid-level $\rightarrow$ Senior/Lead) dành riêng cho các nhà tuyển dụng hàng đầu:
  * **VinFast:** Chẩn đoán UDS, BSW Integration, Pin BMS & Động cơ VCU/Inverter, Ethernet DoIP.
  * **Bosch BGSV:** OSEK OS Scheduling, Resource Ceiling, ComStack PDU Router, Memory Stack Wear Leveling.
  * **LG Vehicle Solutions:** Telematics, SOME/IP, Adaptive AUTOSAR, Android Automotive OS bridge.
  * **Hyundai Kefico:** Powertrain MCAL drivers, SPI/CAN controller, MISRA-C & ISO 26262.

---

## 💻 HƯỚNG DẪN BIÊN DỊCH & CHẠY NHANH (QUICKSTART)

```powershell
# Di chuyển vào thư mục source code
cd as

# 1. Biên dịch và chạy Simulator POSIX (Khuyên dùng khi bắt đầu):
scons --board=posix
./build/posix/as

# 2. Biên dịch target QEMU Cortex-M3:
$env:BOARD="lm3s6965evb"; $env:RELEASE="ascore"; scons

# 3. Chạy kiểm thử UDS Diagnostic bằng Python (trong thư mục reference):
cd ../docs/reference/python_can_scripts
python 01_session_control.py
python 02_read_did.py
python 04_read_dtc.py
```

---

## 📊 THỐNG KÊ TOÀN BỘ TÀI NGUYÊN (LIBRARY METRICS)

| Phân Loại Tài Nguyên | Số Lượng / Quy Mô | Mục Đích |
|---|:---:|---|
| **Chuyên đề lý thuyết chuyên sâu** | 14 modules | Trang bị nền tảng kiến trúc, OS, ComStack, FuSa, Adaptive |
| **Nhiệm vụ thực hành (Hands-on)** | 35 tasks (4–5 tuần) | Rèn luyện kỹ năng code, config và debug trực tiếp |
| **Deep-dive End-to-End Traces** | 3 phân tích lớn | Lần vết từng dòng code cho Boot, CAN, NvM |
| **Bản phân tích lỗi & so sánh (RCA)** | 3 case studies | Học cách fix bug và so sánh code trước/sau |
| **Python UDS Test Scripts** | 7 scripts hoàn chỉnh | Giả lập CANoe/Tester gửi lệnh UDS thực tế |
| **File dữ liệu mẫu (ARXML / DBC)** | 5 files + Python parser | Thực hành bóc tách và tích hợp hệ thống |
| **Mã nguồn phần mềm thực tế (`as/`)** | 2.190+ tệp C/H | Codebase chuẩn mở AUTOSAR đầy đủ tính năng |

---

*📌 Kho tài liệu được thiết kế tương đương chương trình **AUTOSAR Internal Onboarding & Engineering Training** tại các hãng xe và Tier-1 Automotive toàn cầu.*
