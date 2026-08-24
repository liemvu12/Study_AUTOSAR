# AUTOSAR PORTFOLIO & INTERVIEW GUIDE - BÍ KÍP TỪ SENIOR TECHNICAL LEAD

Là một Kỹ sư phần mềm nhúng (Embedded Software Engineer) trong lĩnh vực Automotive, đặc biệt là AUTOSAR, bạn đang bước vào một trong những thị trường khắt khe nhất thế giới. Từ kinh nghiệm phỏng vấn và xây dựng đội ngũ tại Bosch, LG VS, VinFast, và Hyundai Kefico, tôi khẳng định: Một Portfolio chất lượng và kỹ năng phỏng vấn theo chuẩn cấu trúc sẽ giúp bạn vượt qua 80% ứng viên chỉ có lý thuyết suông.

Tài liệu này cung cấp hướng dẫn toàn diện từ việc xây dựng dự án cá nhân (Portfolio), cấu trúc kho lưu trữ (Repository), thiết kế CV, đến các kỹ năng trả lời phỏng vấn chuyên sâu cho từng công ty Tier-1 và OEM hàng đầu.

---

## 1. Tại Sao Portfolio Quan Trọng Trong AUTOSAR?

### 1.1. Đặc thù của ngành Automotive Software
- **Bảo mật và Độc quyền:** Khác với Web Development hay Mobile App, mã nguồn trong ngành ô tô thường mang tính bảo mật cao (NDA, IP protection). Do đó, bạn không thể mang code từ công ty cũ đi phỏng vấn.
- **Tính Phức Tạp Của Hệ Thống:** Các dự án AUTOSAR thường đòi hỏi kiến thức về hệ thống phân tán, thời gian thực (Real-time), an toàn chức năng (Functional Safety - ISO 26262), và vi điều khiển (MCU).
- **Yêu Cầu Về Quy Trình:** Phát triển phần mềm ô tô tuân theo các quy trình khắt khe như ASPICE (Automotive SPICE), MISRA C/C++.

### 1.2. Lợi ích của một Portfolio Thực Hành
- **Chứng minh năng lực thực tế:** Nhà tuyển dụng (Interviewer) muốn thấy bạn "CÓ THỂ" làm được việc, thay vì chỉ "NÓI" rằng bạn hiểu lý thuyết. Một dự án thực tế chạy trên bo mạch hoặc Simulator (như POSIX) có sức thuyết phục gấp mười lần một chứng chỉ lý thuyết.
- **Phân biệt bạn với sinh viên mới ra trường:** Mini-projects, như những ví dụ trong `Study_AUTOSAR-main`, chứng tỏ khả năng tự học, nghiên cứu tài liệu kỹ thuật, và tích hợp các module phần mềm phức tạp.
- **Tạo nền tảng cho vòng phỏng vấn kỹ thuật:** Portfolio của bạn sẽ trở thành trung tâm của buổi phỏng vấn. Bạn sẽ làm chủ cuộc trò chuyện bằng cách điều hướng người phỏng vấn vào những phần bạn làm tốt nhất.

---

## 2. Git Repository Structure — Chuẩn Tier-1

Một kho lưu trữ (Repository) chuyên nghiệp không chỉ chứa mã nguồn, mà còn phải phản ánh tư duy quy trình (Process-driven mindset) của một kỹ sư Automotive. Dưới đây là cấu trúc thư mục chuẩn Tier-1:

```text
Study_AUTOSAR-main/
├── README.md                    ← Executive summary: Tổng quan dự án, cách build và run.
├── docs/                        ← Tài liệu kỹ thuật, phản ánh tư duy Systems Engineering.
│   ├── architecture/            ← Kiến trúc phần mềm.
│   │   └── system_overview.md   ← Sơ đồ khối tổng thể ECU.
│   ├── design/                  ← Thiết kế chi tiết cho từng module/SWC.
│   │   └── swdd_bms.md          ← SW Detailed Design: Thiết kế thuật toán, flowchart.
│   └── test/                    ← Báo cáo kiểm thử.
│       └── test_report_bms.md   ← Kết quả Unit Test, Integration Test.
├── as/                          ← Source code chính, phân tách rõ ràng theo Layer.
│   ├── bsw/                     ← Basic Software (OS, COM, DEM, DCM, NvM, ...).
│   ├── rte/                     ← Runtime Environment (Generated code).
│   └── com/as.application/
│       └── board.posix/
│           └── bms_swc/         ← Mini BMS project (Software Component).
├── tools/                       ← Công cụ hỗ trợ phát triển và kiểm thử.
│   └── python_can_scripts/      ← Các script Python để giả lập tín hiệu CAN và UDS.
├── .gitignore                   ← Loại bỏ các file build object, file tạm.
└── CHANGELOG.md                 ← Lịch sử cập nhật dự án theo chuẩn Semantic Versioning.
```

---

## 3. README.md Template Hoàn Chỉnh

Trang README là điểm chạm đầu tiên của Hiring Manager. Nó cần phải rõ ràng, súc tích và kỹ thuật.

```markdown
# AUTOSAR Learning Portfolio — [Tên Của Bạn]

## 🎯 Overview
Kho lưu trữ này chứa các dự án thực hành về kiến trúc AUTOSAR Classic, được phát triển và tích hợp dựa trên mã nguồn mở (parai/as fork). Mục tiêu là chứng minh năng lực thiết kế phần mềm, cấu hình BSW, và phát triển ứng dụng (ASW) cho hệ thống nhúng ô tô.

Hai dự án chính:
1. **Mini BMS ECU:** Ứng dụng quản lý pin (Battery Management System).
2. **UDS Diagnostic Stack:** Tích hợp và cấu hình dịch vụ chẩn đoán theo chuẩn ISO 14229.

## 🛠️ Technical Stack
- **OS:** AUTOSAR OS (Trampoline OSEK) + POSIX Simulator (cho phép chạy trực tiếp trên PC).
- **Communication:** CAN Protocol via ComStack (COM, PduR, CanIf, Can).
- **Diagnostics:** UDS (DCM) hỗ trợ các Service: 0x10, 0x22, 0x27, 0x19, 0x31.
- **Memory:** NvM (Non-Volatile Memory) + Fee (Flash EEPROM Emulation).
- **Build System:** SCons, GCC ARM Toolchain.
- **Tools:** Python-CAN, cantools, GDB, Wireshark (CAN frame analysis).

## 📁 Projects

### Project 1: Mini BMS ECU Software Component
**Goal:** Thiết kế và phát triển tính năng tính toán State of Charge (SoC) tích hợp trên ngăn xếp AUTOSAR BSW.

**Architecture & Design:**
- **SWC Design:** `BMS_MainRunnable` (Chu kỳ 10ms), `BMS_FaultRunnable` (Chu kỳ 5ms).
- **Algorithm:** Sử dụng phương pháp Coulomb Counting (Tích phân I×dt) để ước lượng SoC.
- **Fault Detection:** Báo cáo lỗi qua DEM (Diagnostic Event Manager) khi phát hiện quá nhiệt (DTC: P0A7E - Battery Pack Over-temperature).
- **Data Persistence:** Sử dụng NvM để lưu trữ trạng thái sạc tích lũy trước khi tắt máy và khôi phục khi khởi động.
- **Output:** Phát bản tin CAN `BMS_Status` định kỳ (ID: 0x180, 100ms chu kỳ).

**Skills Demonstrated:**
✅ Cấu hình AUTOSAR OS Task, Alarm, và Resource (file `.oil`).
✅ Đóng gói tín hiệu bằng COM module (8-byte PDU mapping).
✅ Quản lý lỗi hệ thống qua DEM với cơ chế Debounce (Time-based).
✅ Đọc/ghi bất đồng bộ (Asynchronous) qua NvM module.
✅ Đọc mã lỗi (DTC) qua dịch vụ UDS 0x19.

**Code Reference:** [`as/com/as.application/board.posix/bms_swc/`](link-to-folder)

### Project 2: UDS Diagnostic Stack Integration
**Goal:** Cấu hình và kiểm thử tính năng chẩn đoán thông qua mạng CAN.

**Features Implemented:**
- **Diagnostic Session Control (0x10):** Chuyển đổi giữa Default và Extended session.
- **Read Data By Identifier (0x22):** Đọc thông số nhiệt độ và điện áp Cell pin.
- **Security Access (0x27):** Thuật toán Seed & Key mức độ cơ bản để mở khóa lập trình.
- **Clear Diagnostic Information (0x14):** Xóa bộ nhớ DTC.

## 🔧 How to Build and Run
Dự án có thể chạy trực tiếp trên Linux hoặc WSL (Windows Subsystem for Linux).

```bash
# 1. Prerequisites: Python 3.9+, SCons, GCC ARM
# Chi tiết cài đặt xem tại docs/00_BUILD_ENVIRONMENT_SETUP.md

# 2. Clone repository
git clone [your-repo-url]
cd Study_AUTOSAR-main/as

# 3. Build cho target POSIX
scons --board=posix

# 4. Run ECU Simulator
./build/posix/as
```

## 📊 Test Results & Validation
| Module | Test Type | Coverage Standard | Result |
|--------|-----------|-------------------|--------|
| BMS SoC | Unit Test | Statement (85%), Branch (75%) | Pass |
| UDS DCM | Integration | ISO 14229 Service Compliance | All services pass |
| CAN COM | HIL Sim | Bus Load < 30%, 0 Frame Loss | Pass |

## 📖 Learning Resources & Documentation
Tham khảo thư mục `docs/` để đọc các tài liệu thiết kế hệ thống chuyên sâu do tôi tự biên soạn.
```

---

## 4. Architecture Presentation Template

Trong buổi phỏng vấn Technical, khả năng trình bày kiến trúc (Architecture) là yếu tố quyết định để định giá Seniority của bạn.

### Cách vẽ Architecture Diagram
- **Công cụ:** Sử dụng Draw.io (định dạng xml/png) hoặc MermaidJS (tích hợp trực tiếp vào markdown).
- **Mô hình chuẩn:** Layered Architecture. Phải thể hiện rõ 3 tầng: Application (SWC) → RTE (V-FB) → BSW (Services/ECU Abstraction/MCAL) → Hardware.

### Template Trình Bày (Pitching Script)
- **Mở bài:** "Để phát triển tính năng BMS này, tôi thiết kế hệ thống theo chuẩn AUTOSAR Layered Architecture."
- **Đi vào chi tiết:** "Ở tầng Application, tôi định nghĩa `BMS_SWC` với các Runnable độc lập. Để đảm bảo Real-time, tôi map các Runnable này vào các OS Task khác nhau dựa trên chu kỳ thực thi."
- **Data Flow:** "Giải thích luồng dữ liệu Tx (Transmit): Dữ liệu SoC từ SWC → qua RTE → gọi hàm API của COM → COM đóng gói tín hiệu vào PDU → đẩy xuống PduR để định tuyến → CanIf → CAN Driver (MCAL) → truyền ra Bus vật lý."
- **Key Messages (Nhấn mạnh):**
  - "Tôi chọn phương án thiết kế này vì nó đảm bảo tính Modular và dễ dàng porting sang MCU khác."
  - "Vấn đề tôi gặp phải là xử lý đồng bộ dữ liệu giữa Task 10ms và Task 5ms. Tôi đã giải quyết bằng cách sử dụng cơ chế bảo vệ tài nguyên (OS Resource / PCP)."

---

## 5. Demo Video Script

Một video demo ngắn (5-7 phút) đính kèm trong CV/Portfolio sẽ tạo ấn tượng cực mạnh.

**Cấu trúc Video (5–7 phút):**

1. **(0:00–0:30) Introduction:**
   - Xin chào, tôi là [Tên], kỹ sư nhúng với định hướng AUTOSAR.
   - Đây là dự án Mini BMS ECU tôi tự thiết kế và implement bằng kiến trúc AUTOSAR Classic.

2. **(0:30–1:30) Build Project:**
   - Mở terminal: `scons --board=posix`.
   - Vừa chờ build vừa giải thích ngắn gọn: "Hệ thống đang biên dịch BSW, RTE và Application code. Tôi dùng môi trường POSIX để có thể chạy giả lập trực tiếp trên PC, tiết kiệm chi phí phần cứng nhưng vẫn giữ nguyên logic phần mềm."

3. **(1:30–3:00) Run Simulator & Console Output:**
   - Chạy lệnh: `./build/posix/as`.
   - Hiển thị log console: Chỉ ra các dòng log khởi tạo OS khởi động (StartOS), EcuM Init.
   - Chỉ ra log của thuật toán SoC đang tính toán định kỳ.

4. **(3:00–4:30) CAN & UDS Demonstration:**
   - Mở terminal thứ hai, chạy kịch bản Python-CAN: `python3 tools/python_can_scripts/uds_tester.py`.
   - Giải thích: "Script này đóng vai trò là Diagnostic Tester. Nó đang gửi request UDS 0x22 để đọc nhiệt độ pin, và nhận response từ hệ thống."
   - Cho xem các frame CAN raw trên màn hình và cách chúng được decode thành thông số vật lý.

5. **(4:30–5:30) Code Walkthrough (Giải thích mã nguồn):**
   - Mở IDE (VSCode), show file `BMS_SWC.c` hoặc cấu hình `.oil`.
   - Tập trung vào 1 đoạn quan trọng: "Đây là cấu hình của COM module. Tôi đã define PDU và Signal mapping ở đây để đảm bảo độ dài 8 bytes."

6. **(5:30–6:00) Challenges & Lessons Learned:**
   - "Thử thách lớn nhất là cấu hình NvM để lưu trữ dữ liệu bất đồng bộ. Tôi đã học được cách sử dụng Callback function từ NvM về RTE để thông báo hoàn thành ghi bộ nhớ."

---

## 6. CV / Resume Section Templates

Hãy làm nổi bật dự án của bạn trong CV theo cấu trúc Action-Result.

### [EN Version]
**AUTOSAR Learning Project | Self-study & Implementation | 2024**
- Implemented a Mini Battery Management System (BMS) ECU using the AUTOSAR Classic stack architecture (parai/as).
- Configured OSEK-compliant OS elements including Tasks with precise scheduling priorities, ISR Category 2 handling, and Resource management using Priority Ceiling Protocol (OIL configuration).
- Integrated Communication Stack (ComStack) for CAN signal transmission: Application → RTE → COM → PduR → CanIf → CAN Driver.
- Developed and integrated UDS diagnostic services adhering to ISO 14229 (0x22 Read DID, 0x27 SecurityAccess, 0x19 ReadDTC).
- Developed automated Python-CAN testing scripts to simulate CAN bus nodes and validate ECU communication behaviors.

### [VN Version]
**Dự Án Tích Hợp AUTOSAR Thực Hành | Tự Nghiên Cứu | 2024**
- Triển khai và phát triển phần mềm Mini BMS ECU dựa trên kiến trúc AUTOSAR Classic stack (Trampoline OSEK).
- Cấu hình hệ điều hành OSEK: Thiết kế Task theo mức ưu tiên, xử lý ngắt ISR Category 2, và quản lý tài nguyên đồng thời với Priority Ceiling Protocol (PCP).
- Tích hợp thành công ComStack phục vụ truyền dẫn tín hiệu CAN theo luồng chuẩn: RTE → COM → PduR → CanIf → CAN Driver.
- Triển khai module chẩn đoán UDS (DCM), hỗ trợ các dịch vụ 0x22 (Đọc thông số), 0x27 (Truy cập bảo mật) và 0x19 (Quản lý mã lỗi DTC).
- Viết các kịch bản kiểm thử (Scripts) bằng Python-CAN để giả lập môi trường mạng và tự động hóa kiểm thử giao tiếp ECU.

---

## 7. STAR Story Examples cho Phỏng Vấn

Khung STAR (Situation - Task - Action - Result) là vũ khí bí mật trong phỏng vấn hành vi và kỹ thuật chuyên sâu.

### Story 1: "Kể về lần bạn debug một vấn đề khó khăn nhất liên quan đến hệ điều hành"
- **Situation (Tình huống):** Khi đang phát triển module giao tiếp trong AUTOSAR, tôi cần implement một Extended Task để xử lý các frame nhận được từ CAN bus.
- **Task (Nhiệm vụ):** Yêu cầu là Task phải đợi Event (`WaitEvent`) từ CAN Receive ISR để thực thi, nhằm tối ưu hóa CPU usage thay vì dùng polling. Tuy nhiên, hệ thống bị treo hoặc mất frame (missed events).
- **Action (Hành động):** Tôi bắt đầu trace code từng bước từ lúc ngắt xảy ra. Tôi kiểm tra phần khai báo ngắt trong file `.oil` và phát hiện ngắt đang được cấu hình là ISR Category 1. Tôi tra cứu lại chuẩn OSEK/VDX OS và nhận ra rằng ISR Category 1 không được phép gọi các dịch vụ của OS như API `SetEvent()`. Tôi lập tức cấu hình lại ngắt thành ISR Category 2 và đảm bảo cấu hình đúng bảng vector ngắt.
- **Result (Kết quả):** Hệ thống hoạt động trơn tru, Task nhận Event chính xác không bị rớt frame. Qua đó, tôi hiểu sâu sắc về sự khác biệt kiến trúc giữa các loại ISR trong AUTOSAR OS.

### Story 2: "Kể về lần bạn học một công nghệ/module mới một cách nhanh chóng"
- **Situation (Tình huống):** Dự án yêu cầu tích hợp tính năng chẩn đoán UDS (DCM), đặc biệt là lưu trữ lỗi (DEM/NvM) nhưng tôi chưa từng làm về module NvM.
- **Task (Nhiệm vụ):** Phải hoàn thành cấu hình cơ chế lưu lỗi vào EEPROM giả lập trong vòng 1 tuần.
- **Action (Hành động):** Thay vì đọc mù quáng hàng nghìn trang spec của AUTOSAR, tôi tiếp cận từ trên xuống (Top-down). Đầu tiên, tôi đọc tài liệu "AUTOSAR Layered Architecture" để hiểu vị trí của NvM. Sau đó, tôi tập trung đọc spec của NvM phần "Sequence Diagram" để hiểu luồng Read/Write bất đồng bộ. Cuối cùng, tôi viết một ứng dụng nhỏ thử nghiệm ghi/đọc 1 block dữ liệu độc lập trước khi tích hợp vào dự án BMS.
- **Result (Kết quả):** Tôi hoàn thành task đúng hạn, hiểu rõ cơ chế RAM Block và ROM Block trong cấu hình NvM.

### Story 3: "Kể về dự án AUTOSAR mà bạn tự học và phát triển"
- **Situation (Tình huống):** Nhận thấy ngành Automotive cần kiến thức thực chiến, tôi quyết định tự xây dựng dự án Mini BMS.
- **Task (Nhiệm vụ):** Triển khai trọn vẹn luồng gửi tín hiệu qua CAN và xử lý lỗi UDS.
- **Action (Hành động):** Tôi đã fork bộ mã nguồn mở `parai/as`. Tôi tập trung cấu hình file `.oil` cho hệ điều hành, viết code Application tính SoC, cấu hình luồng truyền tín hiệu qua COM, PduR. Tôi còn tự viết script Python để đóng vai trò làm Tester.
- **Result (Kết quả):** Nó chứng minh tôi không chỉ biết lý thuyết mà có khả năng debug, đọc code C phức tạp, và hiểu toàn bộ chuỗi công cụ (toolchain).

---

## 8. Interview Preparation theo Từng Công Ty

Mỗi công ty Tier-1 hay OEM đều có văn hóa và bộ câu hỏi đặc thù. Bạn cần chuẩn bị chiến thuật riêng cho từng công ty.

### Bosch Vietnam (BGSV)
- **Focus:** Tuân thủ quy trình chặt chẽ, tiêu chuẩn chất lượng cao, hiểu biết về ASPICE Level 2/3.
- **Technical Domains:** Rất mạnh về BSW Integration, Cấu hình OSEK/VDX, Phát triển MCAL, và System Architecture.
- **Typical Questions:**
  - "Hãy vẽ sơ đồ khối và trình bày luồng khởi động (Startup sequence) của AUTOSAR (EcuM, BswM)."
  - "Giải thích chi tiết sự khác nhau giữa Polling và Interrupt trong giao tiếp SPI/CAN. Ưu nhược điểm?"
  - "Làm sao để đảm bảo tính toàn vẹn bộ nhớ (Memory Layout, Linker script)?"
- **Culture:** Môi trường hướng quy trình (Process-driven). Hãy nhấn mạnh khả năng viết tài liệu (Documentation), Unit test, MISRA-C, và làm việc với Jira/Doors.

### LG VS (Vehicle Component Solutions)
- **Focus:** Hệ thống truyền động điện (EV Powertrain), VCU, và Hệ thống quản lý pin (BMS).
- **Technical Domains:** Thuật toán điều khiển, xử lý tín hiệu CAN/LIN, An toàn chức năng ISO 26262 (ASIL-C/D).
- **Typical Questions:**
  - "Làm thế nào để tính toán State of Charge (SoC) một cách chính xác trong môi trường nhiễu?"
  - "Khái niệm Safety Mechanism là gì? Làm thế nào để đạt được ASIL-D cho tín hiệu truyền trên CAN (Ví dụ: E2E Protection)?"
  - "Xử lý đa nhiệm, chống Deadlock trong OS?"
- **Culture:** Văn hóa làm việc của Hàn Quốc: Yêu cầu sự tỉ mỉ, chi tiết, khả năng chịu áp lực cao, và tốc độ phản hồi nhanh.

### VinFast
- **Focus:** Phát triển toàn diện từ đầu (End-to-End) các ECU trên xe.
- **Technical Domains:** Kiến thức bao quát về toàn bộ hệ sinh thái AUTOSAR, kỹ năng thực hành nhanh (Hands-on), tích hợp OTA (Over-The-Air update), và Cybersecurity.
- **Typical Questions:**
  - "Thiết kế kiến trúc cho một tính năng cập nhật phần mềm qua mạng (FOTA/OTA) sẽ gồm những module nào?"
  - "Làm sao để tích hợp SecOC (Secure Onboard Communication)?"
  - "Kinh nghiệm làm việc với các Toolchain thương mại như Vector DaVinci, ETAS, hay Elektrobit?"
- **Culture:** Môi trường Startup kết hợp tiêu chuẩn Automotive. Ưu tiên những người chủ động (Proactive), khả năng giải quyết vấn đề nhanh gọn, không ngại việc khó.

### Hyundai Kefico
- **Focus:** Điều khiển động cơ (Engine/Powertrain Control Systems), và các hệ thống ADAS.
- **Technical Domains:** Vi điều khiển chuyên dụng, MCAL phức tạp, xử lý thời gian thực khắt khe, DSP (Digital Signal Processing).
- **Typical Questions:**
  - "Phân tích thời gian thực (Timing Analysis). Làm sao để chứng minh hệ thống không trễ Deadline?"
  - "Thiết kế hàm ngắt (ISR) tối ưu là như thế nào?"
  - "Luật MISRA-C nào bạn hay vi phạm nhất và cách khắc phục?"

---

## 9. 30 Câu Hỏi Phỏng Vấn Điển Hình + Gợi Ý Trả Lời

### Phần A: AUTOSAR Architecture & OS (Hệ điều hành)
1. **Câu hỏi:** Kiến trúc AUTOSAR gồm những tầng chính nào? Mục đích của tầng RTE là gì?
   - *Gợi ý:* 3 tầng chính (Application, RTE, BSW). RTE (Runtime Environment) cung cấp các API chuẩn để các SWC giao tiếp với nhau và giao tiếp với BSW, tách biệt phần cứng khỏi ứng dụng.
2. **Câu hỏi:** Phân biệt Basic Task và Extended Task trong OSEK OS?
   - *Gợi ý:* Extended Task có trạng thái `WAITING` (có thể chờ Event), trong khi Basic Task chỉ có `READY`, `RUNNING`, `SUSPENDED`.
3. **Câu hỏi:** Priority Inversion (Đảo ngược mức ưu tiên) là gì? AUTOSAR OS giải quyết nó như thế nào?
   - *Gợi ý:* Là tình trạng task ưu tiên cao bị block bởi task ưu tiên thấp do tranh chấp tài nguyên. AUTOSAR OS dùng OSEK Priority Ceiling Protocol (PCP) để nâng tạm thời mức ưu tiên của task đang giữ tài nguyên.
4. **Câu hỏi:** Sự khác biệt giữa ISR Category 1 và Category 2?
   - *Gợi ý:* ISR Cat 1 không dùng các API của OS, chạy rất nhanh. ISR Cat 2 được OS quản lý, có thể gọi một số API của OS (ví dụ `SetEvent`).

### Phần B: ComStack (Truyền thông mạng)
5. **Câu hỏi:** Trình bày luồng truyền (Tx path) của một frame CAN trong AUTOSAR?
   - *Gợi ý:* SWC → RTE → COM (Signal to PDU) → PduR (Routing) → CanIf (Interface abstraction) → Can (MCAL driver) → Hardware.
6. **Câu hỏi:** Module COM trong AUTOSAR làm nhiệm vụ gì?
   - *Gợi ý:* Đóng gói tín hiệu (Signal) thành PDU (Protocol Data Unit), quản lý chu kỳ truyền/nhận, quản lý timeout (Deadline monitoring).
7. **Câu hỏi:** PduR (PDU Router) dùng để làm gì?
   - *Gợi ý:* Định tuyến các PDU giữa COM/DCM tới các bus tương ứng (CAN, LIN, FlexRay) thông qua CanIf/LinIf. Hỗ trợ Gateway (route giữa 2 bus).

### Phần C: Diagnostics (UDS & DEM/DCM)
8. **Câu hỏi:** Trình bày luồng xử lý khi nhận một request UDS từ Tester?
   - *Gợi ý:* Can → CanIf → CanTp (phân mảnh dữ liệu) → PduR → Dcm. DCM sẽ xử lý request, gọi tới các module tương ứng (như RTE/SWC cho 0x22, hoặc DEM cho 0x19).
9. **Câu hỏi:** Module DEM khác gì với DCM?
   - *Gợi ý:* DEM (Diagnostic Event Manager) quản lý trạng thái các lỗi (Event/DTC), lưu trữ lỗi. DCM (Diagnostic Communication Manager) quản lý giao tiếp UDS với bên ngoài, nhận request và trả response.
10. **Câu hỏi:** UDS Service 0x19 và 0x22 dùng làm gì?
    - *Gợi ý:* 0x19: Read Diagnostic Trouble Code Information (đọc mã lỗi). 0x22: Read Data By Identifier (đọc thông số vật lý hiện tại).

### Phần D: C Programming & Microcontroller (Kỹ năng cốt lõi)
11. **Câu hỏi:** Khóa `volatile` trong ngôn ngữ C có tác dụng gì?
    - *Gợi ý:* Ngăn chặn compiler tối ưu hóa biến số đó, vì biến có thể bị thay đổi bởi phần cứng (như thanh ghi I/O) hoặc ISR. Rất quan trọng trong lập trình MCAL.
12. **Câu hỏi:** Trình bày quá trình khởi động (Boot process) của một Vi điều khiển?
    - *Gợi ý:* Power On Reset → Cấu hình Clock (PLL) → Cấu hình Stack pointer → Cấu hình Watchdog → Copy biến Data từ ROM sang RAM, khởi tạo bss bằng 0 → Chuyển tới hàm `main()`.

*(Các câu hỏi tình huống: Hãy sử dụng cấu trúc STAR ở Phần 7 để trả lời)*

---

## 10. Preparation Checklist (Danh Sách Kiểm Tra Trước Phỏng Vấn)

Hãy tick chọn (✅) các mục sau đây trước khi gửi CV và tham gia phỏng vấn:

### Hồ Sơ & Dự Án
- [ ] GitHub Repository được set Public với mã nguồn sạch sẽ.
- [ ] Trang `README.md` trình bày đầy đủ, chi tiết (Sử dụng template mục 3).
- [ ] Có thể Build và Demo thành công project trong vòng dưới 2 phút.
- [ ] File `.oil` (Cấu hình OS) được comment rõ ràng về các quyết định thiết kế.

### Kiến Thức Nền Tảng
- [ ] Thuộc lòng bản đồ AUTOSAR Layered Architecture.
- [ ] Đọc và hiểu sâu 3 tài liệu cơ bản nhất: OS Specification, COM Specification, và DEM/DCM Specification.
- [ ] Giải thích mạch lạc luồng Tx (Transmit) và Rx (Receive) của mạng CAN.
- [ ] Thuộc lòng cơ chế hoạt động của tối thiểu 2 UDS Services (ví dụ: 0x22 và 0x19).

### Kỹ Năng Trình Bày
- [ ] Soạn sẵn 3 câu chuyện hành vi theo mô hình S.T.A.R.
- [ ] Vẽ sẵn sơ đồ kiến trúc phần mềm và lưu dưới dạng PDF hoặc Ảnh chất lượng cao để share screen khi cần.
- [ ] Chuẩn bị sẵn kịch bản và thực tập Demo/Pitching hệ thống.
- [ ] Tìm hiểu kỹ văn hóa công ty mục tiêu (Bosch, LG, VinFast, Hyundai...) để điều chỉnh hướng trả lời.

---
*Prepared with expertise to elevate your career in the Automotive Software Industry.*

