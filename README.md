# AUTOSAR Classic — Self-Study Engineering Platform

> **Ngôn ngữ:** Tiếng Việt Kỹ Nghệ  
> **Mục tiêu nghề nghiệp:** BSW Integration Engineer · ECU Software Engineer (BMS / VCU / Body)  
> **Công ty mục tiêu:** Bosch BGSV · LG Vehicle Solutions · VinFast · Hyundai Kefico · FPT Automotive  
> **Source code thực tế:** `as/` — 2.190+ files C/H, ARXML, tools (fork parai/as)

---

## 📁 Cấu Trúc Thư Mục

```
Study_AUTOSAR-main/
├── as/                      ← Source code AUTOSAR thực tế (2190+ files)
│   └── com/as.infrastructure/
│       ├── communication/   ← ComStack (CAN, CanIf, CanTp, PduR, COM)
│       ├── diagnostic/      ← DCM, DEM, DET
│       ├── memory/          ← NvM, Fee, MemIf
│       ├── system/kernel/   ← AUTOSAR OS (Trampoline OSEK)
│       └── arch/stm32f1/    ← MCAL drivers (Can.c, Dio.c, Port.c...)
│
└── docs/
    ├── theory/              ← 📖 Tài liệu lý thuyết chính (00 → 10)
    ├── deep_dive/           ← 🔬 Phân tích sâu từng stack
    ├── reference/           ← 📌 Cheatsheet, Debug guide, Python scripts
    ├── career/              ← 🎯 Chuẩn bị phỏng vấn & portfolio
    ├── hands_on_tasks/      ← 🛠️  27 bài tập thực hành (4 tuần)
    ├── samples/             ← 📂 ARXML mẫu thực tế
    └── _prompts/            ← ⚙️  Meta prompts (không phải học liệu)
```

---

## 🗺️ ROADMAP SỬ DỤNG TÀI LIỆU

### Bước 0 — Chuẩn Bị Môi Trường (1–2 ngày)

> **Đọc trước:** [`docs/theory/00_BUILD_ENVIRONMENT_SETUP.md`](docs/theory/00_BUILD_ENVIRONMENT_SETUP.md)

```bash
# Cài đặt: Python 3.9+, SCons, GCC ARM, WSL2 (Windows)
# Build thử để verify môi trường:
cd as
scons --board=posix
./build/posix/as
```

---

### Bước 1 — Nắm Lý Thuyết (3–4 tuần song song với hands-on)

Đọc theo thứ tự, mỗi tài liệu có 3 cấp độ (🟢 Newbie → 🟡 Intermediate → 🔴 Expert):

| # | Tài liệu | Thời gian | Trọng số |
|:---:|---|:---:|:---:|
| 00 | [`00_AUTOSAR_READING_ROADMAP.md`](docs/theory/00_AUTOSAR_READING_ROADMAP.md) | 30 phút | Đọc đầu tiên |
| 01 | [`01_AUTOSAR_Layered_Architecture_And_VFB_Masterclass.md`](docs/theory/01_AUTOSAR_Layered_Architecture_And_VFB_Masterclass.md) | 1 ngày | ⭐⭐⭐⭐⭐ |
| 02 | [`02_AUTOSAR_OS_And_MCAL_Deep_Dive.md`](docs/theory/02_AUTOSAR_OS_And_MCAL_Deep_Dive.md) | 1 ngày | ⭐⭐⭐⭐⭐ |
| 03 | [`03_Communication_Stack_And_CAN_Protocol.md`](docs/theory/03_Communication_Stack_And_CAN_Protocol.md) | 1 ngày | ⭐⭐⭐⭐⭐ |
| 04 | [`04_Diagnostic_UDS_And_Memory_Stack.md`](docs/theory/04_Diagnostic_UDS_And_Memory_Stack.md) | 1 ngày | ⭐⭐⭐⭐⭐ |
| 05 | [`05_Toolchain_ARXML_And_ECU_Integration.md`](docs/theory/05_Toolchain_ARXML_And_ECU_Integration.md) | 1 ngày | ⭐⭐⭐⭐ |
| 06 | [`06_Real_World_ECU_Applications_BMS_VCU_Body.md`](docs/theory/06_Real_World_ECU_Applications_BMS_VCU_Body.md) | 1 ngày | ⭐⭐⭐⭐⭐ |
| 07 | [`07_ISO26262_Functional_Safety_Awareness.md`](docs/theory/07_ISO26262_Functional_Safety_Awareness.md) | 0.5 ngày | ⭐⭐⭐⭐ |
| 08 | [`08_AUTOSAR_Adaptive_Platform_Overview.md`](docs/theory/08_AUTOSAR_Adaptive_Platform_Overview.md) | 0.5 ngày | ⭐⭐⭐ |
| 09 | [`09_ASPICE_VModel_Process.md`](docs/theory/09_ASPICE_VModel_Process.md) | 0.5 ngày | ⭐⭐⭐ |
| 10 | [`10_CAN_DBC_Format_And_Tools.md`](docs/theory/10_CAN_DBC_Format_And_Tools.md) | 0.5 ngày | ⭐⭐⭐ |

---

### Bước 2 — Thực Hành 27 Tasks (4 tuần song song)

> **Index:** [`docs/hands_on_tasks/00_MASTER_PLAN_INDEX.md`](docs/hands_on_tasks/00_MASTER_PLAN_INDEX.md)

| Tuần | Tasks | Chuyên đề | Tổng giờ |
|:---:|---|---|:---:|
| 1 | Task 1.1–1.4 + 2.1–2.2 | Architecture & OS cơ bản | ~25h |
| 2 | Task 2.3–2.5 + 3.1–3.3 | OS nâng cao + ComStack | ~25h |
| 3 | Task 3.4–3.5 + 4.1–4.4 | ComStack hoàn thiện + Diagnostic | ~28h |
| 4 | Task 4.5 + 5.1–5.4 + 6.1 | Memory + Toolchain + Mini BMS | ~25h |

---

### Bước 3 — Đào Sâu Khi Cần (tham khảo)

Dùng khi gặp vấn đề cụ thể trong lúc code:

| Vấn đề | Tài liệu |
|--------|---------|
| ECU không boot, startup chậm | [`docs/deep_dive/ECU_STARTUP_AND_SHUTDOWN_DEEP_DIVE.md`](docs/deep_dive/ECU_STARTUP_AND_SHUTDOWN_DEEP_DIVE.md) |
| CAN frame gửi sai / không nhận được | [`docs/deep_dive/COM_STACK_END_TO_END_TRACE.md`](docs/deep_dive/COM_STACK_END_TO_END_TRACE.md) |
| NvM data mất sau power cycle | [`docs/deep_dive/NVM_MEMORY_STACK_DEEP_DIVE.md`](docs/deep_dive/NVM_MEMORY_STACK_DEEP_DIVE.md) |

---

### Bước 4 — Công Cụ Tra Cứu Nhanh (dùng hàng ngày)

| Công cụ | Mục đích |
|---------|---------|
| [`docs/reference/CHEATSHEET_QUICK_REFERENCE.md`](docs/reference/CHEATSHEET_QUICK_REFERENCE.md) | Tra API nhanh, OIL syntax, UDS table |
| [`docs/reference/DEBUGGING_AND_PROFILING_GUIDE.md`](docs/reference/DEBUGGING_AND_PROFILING_GUIDE.md) | Debug GDB/Trace32, phân tích crash |
| [`docs/reference/python_can_scripts/`](docs/reference/python_can_scripts/) | Script test UDS qua CAN (Session, DID, DTC) |
| [`docs/samples/`](docs/samples/) | ARXML mẫu + Python parser |

---

### Bước 5 — Chuẩn Bị Phỏng Vấn (2 tuần cuối)

> **Đọc:** [`docs/career/PORTFOLIO_GUIDE.md`](docs/career/PORTFOLIO_GUIDE.md)

- Xây dựng GitHub portfolio từ mini BMS/VCU project
- Luyện 200+ câu hỏi Q&A phân bố trong các tài liệu theory
- Chuẩn bị STAR stories và demo video

---

## ⏱️ Lịch Học Tổng Thể

```
TUẦN 1–4: Lý thuyết + Hands-on song song
  Sáng: Đọc 1 chuyên đề theory (2–3 giờ)
  Chiều: Làm 1–2 tasks tương ứng (3–4 giờ)

TUẦN 5–6: Consolidate + Deep dive
  Đọc deep_dive/ khi gặp vấn đề
  Làm task 6.1 (Mini BMS) hoặc 6.2 (VCU Torque)

TUẦN 7–8: Interview prep
  Luyện Q&A mỗi buổi sáng (1 giờ)
  Hoàn thiện portfolio trên GitLab
  Mock interview với STAR stories
```

---

## 🔧 Build & Run Nhanh

```bash
# POSIX Simulator (không cần phần cứng)
cd as
scons --board=posix
./build/posix/as

# STM32F107VC (cần GCC ARM + board)
scons --board=stm32f107vc

# Test UDS qua Python-CAN (cần WSL2 + vcan0)
cd docs/reference/python_can_scripts
python 01_session_control.py
python 02_read_did.py
python 04_read_dtc.py
```

---

## 📊 Tổng Kết Library

| Danh mục | Số lượng |
|----------|:--------:|
| Tài liệu lý thuyết (01–10) | 10 docs · ~350KB |
| Deep-dive reference | 3 docs · ~55KB |
| Hands-on tasks | 27 tasks · 4 tuần |
| Python UDS test scripts | 7 scripts |
| ARXML mẫu thực tế | 2 files + parser |
| Interview Q&A | 200+ câu · 3 levels |
| Source code reference | 2190+ files C/H |

---

*Được xây dựng để tương đương **AUTOSAR Internal Onboarding Program** của Tier-1 automotive company.*
