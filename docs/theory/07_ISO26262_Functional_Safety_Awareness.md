# 07. ISO 26262 Functional Safety Awareness

**Tác giả**: Principal Functional Safety Reviewer / AUTOSAR Safety Expert
**Kinh nghiệm**: 15 năm trong ngành Automotive Software
**Lưu ý**: Tài liệu này được biên soạn dựa trên kinh nghiệm thực tiễn và tiêu chuẩn ISO 26262. Một số clause numbers cụ thể hoặc reference sâu có thể được đánh dấu `[NEEDS VERIFICATION]` nếu cần đối chiếu chính xác với tài liệu tiêu chuẩn ISO bản quyền.

---

## 1. Tại Sao Cần Functional Safety? (với ví dụ thực tế)

Trong ngành công nghiệp ô tô (Automotive), software không chỉ điều khiển màn hình giải trí mà còn điều khiển hệ thống phanh (Brake), hệ thống lái (Steering) và hệ thống quản lý pin (Battery Management System - BMS). Một lỗi software ở các hệ thống consumer electronics (như điện thoại, laptop) thường chỉ gây khó chịu cho người dùng (có thể reboot lại), nhưng trong automotive, nó có thể trực tiếp đe dọa đến tính mạng con người.

**Các vụ tai nạn do lỗi software thực tế:**
- **Toyota Unintended Acceleration (2000s):** Đây là một case study kinh điển trong ngành công nghiệp ô tô. Lỗi tăng tốc ngoài ý muốn đã dẫn đến nhiều vụ tai nạn chết người. Quá trình điều tra (đặc biệt bởi NASA và nhóm chuyên gia phần mềm) chỉ ra rằng source code có hàng nghìn vi phạm MISRA-C, sử dụng global variables không kiểm soát, stack overflow và kiến trúc phần mềm không có cơ chế fail-safe đủ mạnh.
- **Lỗi hệ thống phanh ABS / Airbag không nổ:** Do các lỗi logic (race condition, timeout), hệ thống có thể bị treo (deadlock) ngay tại thời điểm tai nạn xảy ra.

**Chi phí recall vs chi phí phòng ngừa:**
- Khi một ECU bị lỗi safety trên xe đã bán ra thị trường, chi phí để recall (triệu hồi) hàng triệu xe có thể lên tới hàng tỷ USD, chưa kể đến thiệt hại khổng lồ về uy tín thương hiệu và các vụ kiện tụng (liability).
- Chi phí đầu tư vào Functional Safety (nhân sự, toolchain, third-party assessment) trong giai đoạn R&D chỉ là một phần rất nhỏ so với chi phí recall.

**Tại sao automotive software khác consumer electronics:**
- **Môi trường khắc nghiệt:** Nhiệt độ, rung lắc, nhiễu điện từ (EMI) cao có thể gây ra lỗi phần cứng ngẫu nhiên (random hardware failures như bit-flip trong RAM).
- **Real-time requirement:** Các hệ thống phanh/lái yêu cầu phản hồi trong thời gian mili-giây (hard real-time). Bỏ lỡ deadline (deadline violation) cũng bị coi là một lỗi hệ thống.

---

## 2. ISO 26262 Overview

ISO 26262 là tiêu chuẩn quốc tế về an toàn chức năng (Functional Safety) dành riêng cho hệ thống điện/điện tử (E/E) trên các phương tiện giao thông đường bộ (Road Vehicles).

**Standard này cover gì:**
Tiêu chuẩn này bao gồm toàn bộ vòng đời phát triển sản phẩm (safety lifecycle), từ lúc lên ý tưởng (concept), thiết kế (design), lập trình (implementation), kiểm thử (testing), sản xuất (production) cho đến khi xe ngừng hoạt động (decommissioning).

**Parts overview (ISO 26262 Edition 2 - 2018):**
- **Part 1:** Vocabulary (Định nghĩa thuật ngữ).
- **Part 2:** Management of functional safety (Quản lý an toàn chức năng, safety culture, quy trình tổ chức).
- **Part 3:** Concept phase (Giai đoạn lên ý tưởng, thực hiện HARA, định nghĩa Safety Goals).
- **Part 4:** Product development at the system level (Thiết kế kiến trúc hệ thống, phân bổ yêu cầu H/W và S/W).
- **Part 5:** Product development at the hardware level (Phát triển phần cứng, tính toán FMEDA).
- **Part 6:** Product development at the software level (Phát triển phần mềm, kiến trúc S/W, coding guidelines, testing).
- **Part 7:** Production, operation, service and decommissioning (Sản xuất và vận hành).
- **Part 8:** Supporting processes (Các quy trình hỗ trợ như Configuration Management, Tool Qualification).
- **Part 9:** Automotive Safety Integrity Level (ASIL)-oriented and safety-oriented analyses (Phân tích ASIL decomposition, dependent failures).
- **Part 10:** Guidelines on ISO 26262 (Hướng dẫn áp dụng).
- **Part 11:** Guidelines on application of ISO 26262 to semiconductors (Hướng dẫn cho semiconductor - chip/SoC).
- **Part 12:** Adaptation of ISO 26262 for motorcycles (Dành cho xe máy).

**Roadmap: từ concept phase đến production:**
1. Item Definition -> 2. HARA -> 3. Safety Goals -> 4. Functional Safety Concept (FSC) -> 5. Technical Safety Concept (TSC) -> 6. H/W & S/W Design & Implementation -> 7. Integration & Testing -> 8. Safety Validation -> 9. Production.

**Không cover:**
- **Cybersecurity:** ISO 26262 tập trung vào việc hệ thống không tự gây hại. Việc bảo vệ hệ thống khỏi các cuộc tấn công có chủ đích từ bên ngoài được cover bởi **ISO/SAE 21434**.
- **Machine Safety (Công nghiệp):** Được cover bởi **IEC 61508** (ISO 26262 chính là bản adaptation của IEC 61508 cho ô tô).
- **SOTIF (Safety of the Intended Functionality):** Các rủi ro do giới hạn hiệu năng của sensor (ví dụ camera bị lóa nắng) được cover bởi **ISO 21448**.

---

## 3. HARA — Hazard Analysis and Risk Assessment

HARA là bước phân tích cốt lõi trong Part 3 để xác định mức độ rủi ro (ASIL) và định nghĩa Safety Goals.

**Hazard là gì:**
Một nguồn gốc tiềm tàng gây ra tổn hại vật lý.
*Ví dụ:* "Unintended brake application" (Tự động phanh đột ngột ngoài ý muốn khi đang chạy trên cao tốc).

**Severity (Mức độ nghiêm trọng của tổn thương - S):**
- **S0:** Không có thương tích.
- **S1:** Thương tích nhẹ, trầy xước.
- **S2:** Thương tích nặng, có thể sống sót (gãy xương).
- **S3:** Thương tích đe dọa tính mạng (tử vong).

**Exposure (Tần suất xuất hiện tình huống lái xe - E):**
- **E0:** Rất hiếm khi (almost impossible) `[NEEDS VERIFICATION: E0 is sometimes considered outside scope/not assigned]`.
- **E1:** Ít xảy ra (ví dụ: chạy trên đường băng tuyết ở một số quốc gia).
- **E2:** Thi thoảng xảy ra.
- **E3:** Khá thường xuyên (ví dụ: kẹt xe).
- **E4:** Gần như mọi lúc (ví dụ: lái xe trên đường nhựa thông thường).

**Controllability (Khả năng kiểm soát tình huống của tài xế hoặc người khác - C):**
- **C0:** Dễ dàng kiểm soát.
- **C1:** Khá dễ kiểm soát (ví dụ: xe mất trợ lực lái khi đang chạy chậm, tài xế vẫn bẻ lái được dù nặng).
- **C2:** Khó kiểm soát, phần lớn người lái bình thường có thể xoay xở nhưng một số thì không.
- **C3:** Không thể kiểm soát (ví dụ: xe đang chạy 120km/h mà phanh khóa cứng đột ngột).

**ASIL Formula:**
ASIL được nội suy từ ma trận của 3 yếu tố: `ASIL = f(S, E, C)`.
(Chỉ khi S>0, E>0, C>0 mới tính ASIL).

**Bảng ví dụ HARA cho BMS (Battery Management System):**
- **Hazard:** Chập mạch / Overcharge pin dẫn đến cháy nổ xe (Thermal Runaway).
- **Tình huống (Operational Situation):** Đang sạc nhanh (Fast Charging) ở trạm sạc có đông người.
- **Phân tích:**
  - Severity: **S3** (Cháy nổ pin đe dọa tính mạng nhiều người).
  - Exposure: **E4** (Sạc pin diễn ra rất thường xuyên).
  - Controllability: **C3** (Khi pin bốc cháy bùng phát, tài xế không thể kiểm soát để tránh tai nạn).
- **Kết quả:** `S3 + E4 + C3` -> **ASIL D** (Mức khắt khe nhất).

---

## 4. ASIL Levels với Real ECU Examples

ASIL (Automotive Safety Integrity Level) phân loại rủi ro từ QM (thấp nhất) đến ASIL D (cao nhất).

| ASIL | Mô tả | Ví dụ ECU/Function | Hardware requirement điển hình |
|------|-------|-------------------|---------------------|
| **QM** | Quality Management (Chỉ cần quy trình quản lý chất lượng thông thường, không yêu cầu safety ISO 26262 khắt khe). | Radio, Infotainment, AC control (Điều hòa). | Vi điều khiển thông thường, không cần Lockstep, không cần ECC RAM nghiêm ngặt. |
| **ASIL A** | Mức độ an toàn thấp nhất. | BCM (Body Control Module) - Door lock, Cửa sổ chỉnh điện. | Watchdog cơ bản, RAM parity. |
| **ASIL B** | Mức độ an toàn trung bình. | Camera lùi, Instrument Cluster (Hiển thị tốc độ), một phần của ABS/ESP. | HW Watchdog, Memory Protection Unit (MPU) cơ bản. |
| **ASIL C** | Mức độ an toàn cao. | EPS (Electric Power Steering) - Hệ thống trợ lực lái điện. | Có cơ chế dự phòng H/W, CPU có test chẩn đoán (BIST). |
| **ASIL D** | Mức độ an toàn khắt khe nhất (rủi ro tử vong cao nhất). | BMS Contactors (cắt điện cao áp), Brake-by-wire, Airbag. | Lockstep CPU (2 cores chạy đồng bộ), ECC RAM (Error-Correcting Code), Dual/Redundant Sensors, rèn luyện quy trình ngặt nghèo (MC/DC coverage). |

---

## 5. Safety Goals & Functional Safety Requirements (FSR)

**Top-level Safety Goal (SG):**
Từ phân tích HARA, chúng ta định nghĩa các Safety Goals. Đây là mục tiêu cao nhất.
- *Ví dụ SG:* "Unintended battery discharge/overcharge không được xảy ra" (ASIL D).

**Phân tách theo cấp độ (Requirement Decomposition):**
1. **FSR (Functional Safety Requirements):** Ở mức hệ thống, giải thích CÁCH (What) để đạt SG.
   - *Ví dụ:* "Hệ thống phải ngắt Contactor ngay lập tức nếu điện áp pin vượt quá mức V_max trong thời gian t_max".
2. **TSR (Technical Safety Requirements):** Hiện thực FSR ở mức kỹ thuật (How) cho System/Hardware/Software.
   - *Ví dụ:* "Microcontroller phải đo điện áp pin qua kênh ADC định kỳ mỗi 10ms. Nếu V_batt > 4.2V, GPIO nối với Contactor Driver phải được kéo xuống LOW trong vòng 50ms".
3. **HWSR (Hardware Safety Requirements):** Yêu cầu cho phần cứng.
   - *Ví dụ:* Mạch ADC phải có sai số < 1%. Hardware Watchdog phải reset chip nếu MCU treo.
4. **SSR (Software Safety Requirements):** Yêu cầu chi tiết cho source code.
   - *Ví dụ:* "Task `Tsk_BmsVoltMon` phải có priority cao nhất, thực hiện đọc ADC. Nếu ADC register trả về giá trị > 0x0F00 (4.2V), gọi hàm `IoHwAb_SetContactor(LOW)`. Đồng thời `Tsk_BmsVoltMon` phải được giám sát bởi WdgM (Alive monitoring)".

---

## 6. Safety Mechanisms trong AUTOSAR

Để đáp ứng các SSR, AUTOSAR cung cấp sẵn các Standardized Safety Mechanisms.

### 6.1 Watchdog (WdgM - Watchdog Manager)
Giám sát luồng thực thi của Software.
- **Alive supervision:** Task có đang chạy đúng chu kỳ không? (Quá chậm hay quá nhanh đều lỗi).
- **Deadline monitoring:** Task có kết thúc công việc trong khoảng thời gian (deadline) cho phép không?
- **Logical supervision:** Thứ tự thực thi code có đúng không? (Task A phải chạy xong điểm X mới đến điểm Y).
- **Code example:**
  ```c
  void Tsk_SafetyCritical(void) {
      WdgM_CheckpointReached(WdgMConf_WdgMSupervisedEntity_SE1, WdgMConf_WdgMCheckpoint_CP_START);
      // ... do critical processing ...
      WdgM_CheckpointReached(WdgMConf_WdgMSupervisedEntity_SE1, WdgMConf_WdgMCheckpoint_CP_END);
  }
  ```

### 6.2 ECC (Error Correction Code) RAM
Lỗi tia vũ trụ hoặc EMI có thể làm lật 1 bit trong RAM (bit-flip).
- **Single-bit error correction:** Hardware ECC sẽ tự động sửa lỗi nếu chỉ có 1 bit bị sai (Software không sập, nhưng có thể báo lỗi).
- **Double-bit error detection:** Nếu 2 bit bị lật, ECC không sửa được nhưng phát hiện được. MCU sẽ throw Exception.
- **OS Hook:** Trong AUTOSAR OS, khi có trap/exception do double-bit ECC, OS sẽ gọi `ProtectionHook()` hoặc NMI handler để thực hiện Safe State (ví dụ reset chip, ngắt điện).

### 6.3 Lockstep CPU
Đối với ASIL D (ví dụ TI TMS570, NXP S32K3), MCU có 2 CPU cores vật lý (Core chính và Core checker).
- Checker core chạy chậm hơn vài clock cycles.
- Cả 2 core chạy chung một tập lệnh (instruction) cùng lúc.
- Hardware comparator ở đầu ra sẽ so sánh kết quả của 2 cores. Nếu sai lệch -> Phát hiện lỗi phần cứng -> Reset/Safe State ngay lập tức.
- Với Lockstep, Software developer thường viết code như cho 1 core (transparent to software).

### 6.4 Memory Protection Unit (MPU)
Bảo vệ bộ nhớ không bị ghi đè trái phép.
- **Ngăn task A ghi đè stack task B:** Nếu một QM Task bị buffer overflow, nó có thể ghi đè sang biến của một ASIL D Task. MPU phần cứng sẽ chặn thao tác này và văng `Memory Protection Exception`.
- **AUTOSAR MemMap:** Code và variables được đặt trong các section riêng biệt (`#pragma SECTION`) và AUTOSAR OS cấu hình MPU rules khi context switch.

### 6.5 Dual-sensor Redundancy
Sử dụng dư thừa phần cứng (Redundancy) để detect sensor bị hỏng.
- **Ví dụ accelerator pedal (chân ga):** Luôn có 2 cảm biến (thường là 2 biến trở ngược chiều nhau, tổng V1 + V2 = 5V).
- **Plausibility check (Code ví dụ):**
  ```c
  uint16 v1_mv = Adc_Read(CH_PEDAL_MAIN);
  uint16 v2_mv = Adc_Read(CH_PEDAL_SUB);
  if (abs((v1_mv + v2_mv) - 5000) > TOLERANCE_MV) {
      // Plausibility error -> Chân ga lỗi -> Báo đèn, giảm tốc.
      Enter_Safe_State();
  }
  ```

### 6.6 CRC Check cho NvM Data
Khi lưu data xuống EEPROM/Flash, dữ liệu có thể bị corrupt.
- **Tại sao cần CRC:** Để đảm bảo data đọc lên là nguyên vẹn (Integrity). Ví dụ: Odometer (số km), Calibration data.
- **AUTOSAR NvM CRC types:** NvM module hỗ trợ tự động tính CRC8, CRC16, CRC32 cho từng block dữ liệu (cấu hình qua tool). Nếu sai CRC khi boot, NvM sẽ load giá trị Default (ROM).

---

## 7. Software Development theo ISO 26262 Part 6

**Design constraints:**
ISO 26262 cấm/hạn chế các kỹ thuật lập trình dễ gây lỗi khó đoán định:
- **No dynamic memory (malloc/free):** Gây memory leak và heap fragmentation. Mọi biến phải cấp phát tĩnh (static/global) hoặc trên stack với size hữu hạn.
- **No recursion:** Đệ quy dễ gây stack overflow.
- **Bounded loops:** Các vòng lặp `while/for` phải có giới hạn điều kiện thoát chắc chắn (timeout/max iteration) để tránh dead loop (infinite loop).

**MISRA-C 2012 compliance:**
- **Tại sao MISRA-C:** C language có rất nhiều "Undefined Behaviors" (UB). MISRA-C là tập hợp các quy tắc bắt buộc phải tuân theo để viết code an toàn (Ví dụ: không cast pointer bừa bãi, gán giá trị rõ ràng, không dùng Goto). Các dự án ASIL bắt buộc phải pass Static Code Analysis (vd: QAC, Polyspace) cho MISRA-C.

**Testing & MC/DC (Modified Condition/Decision Coverage):**
- **Statement & Branch Coverage:** Cho ASIL A/B.
- **MC/DC Coverage:** Bắt buộc mạnh mẽ (Highly Recommended) cho ASIL C/D. Đảm bảo mọi điều kiện (condition) trong lệnh `if (A && B)` đều đã được test khả năng làm thay đổi kết quả (decision) một cách độc lập.

**Code Review Requirements:**
Review không chỉ là nhìn bằng mắt, mà phải có checklist rõ ràng, reviewer phải có đủ năng lực (competence), và phải lưu lại bằng chứng (review report/record) để phục vụ cho các đợt Safety Audit.

---

## 8. FMEA — Failure Mode and Effects Analysis

FMEA là phương pháp phân tích rủi ro quy nạp (Bottom-up).
- **Concept đơn giản:** Nếu linh kiện/module X bị hỏng theo cách Y (Failure Mode), thì tác động đến toàn hệ thống là gì (Effect)?
- **Hardware FMEA (FMEDA):** Phân tích từng điện trở, tụ điện, IC (VD: Điện trở bị chập, bị hở mạch).
- **Software FMEA:** Phân tích từng function, biến số (VD: Hàm tính toán trả về giá trị sai, biến bị tràn (overflow), timeout).

**Ví dụ FMEA table cho BMS Current Sensor (Đơn giản hóa):**
| Item | Failure Mode | Local Effect | System Effect (Hazard) | Severity | Safety Mechanism |
|------|-------------|--------------|------------------------|----------|------------------|
| Current Sensor | Trả về 0A trong khi đang có dòng xả lớn (Stuck at 0). | Software không nhận diện được dòng xả thực tế. | Pin bị Overcurrent -> Overheating -> Cháy. | S3 | Redundant current estimation via Voltage drop; Plausibility check. |

---

## 9. FTA — Fault Tree Analysis (Top-down)

FTA là phương pháp phân tích diễn dịch (Top-down).
- **Concept:** Bắt đầu từ một sự cố cấp hệ thống (Top Event / Hazard), sau đó vẽ sơ đồ cây để tìm ra các nguyên nhân gốc rễ (Root causes) dẫn đến sự cố đó.
- **Logic Gates:** Sử dụng cổng AND (tất cả lỗi cùng xảy ra) và OR (chỉ cần 1 lỗi xảy ra).

**Ví dụ FTA cho "Unintended vehicle acceleration" (Top Event):**
- Top Event: Unintended acceleration
  - `OR GATE`:
    - Event 1: Kẹt cơ khí ở chân ga (Mechanical stuck).
    - Event 2: Lỗi MCU tính toán sai torque (Software bug).
      - `AND GATE` (ASIL Decomposition):
        - Nguyên nhân 2a: Main function tính sai torque.
        - Nguyên nhân 2b: Safety Monitor function không phát hiện được lỗi.
    - Event 3: Lỗi CAN bus bị inject message giả (Cybersecurity).

---

## 10. AUTOSAR Safety Architecture Pattern

**QM partition vs ASIL partition trong AUTOSAR OS:**
- Ứng dụng thường được chia thành các OS Applications (Partition).
- **QM Partition:** Chứa code không an toàn (Infotainment, logging). Nếu crash, hệ thống vẫn an toàn.
- **ASIL Partition:** Chứa code safety-critical. Được bảo vệ bởi MPU. Nếu partition này crash, xe phải vào Safe State.
- *Nguyên tắc:* QM không được phép gọi trực tiếp code ASIL (để tránh lây nhiễm rủi ro - Freedom from Interference - FFI).

**ASIL decomposition:**
Một kỹ thuật rất phổ biến để giảm chi phí phần cứng/phần mềm.
- `ASIL D -> ASIL B(D) + ASIL B(D)`.
- Thay vì phải làm 1 khối thuật toán siêu phức tạp ở chuẩn ASIL D, ta làm 2 khối song song và độc lập ở chuẩn ASIL B. Nếu cả 2 đều hỏng cùng lúc (rất khó) thì mới gây ra ASIL D.

**Trusted Functions vs Untrusted SWCs:**
- Khi SWC ở QM Partition (Untrusted) muốn tương tác với OS hoặc ASIL Partition (Trusted), nó không thể gọi API trực tiếp. Nó phải gọi qua một cơ chế ngắt phần mềm gọi là `Trusted Function Call` (TFC). OS sẽ check quyền trước khi thực thi.

---

## 11. Typical Safety Review Checklist cho BSW Engineer

Khi BSW Engineer submit code, Safety Reviewer (như tôi) sẽ soi các điểm sau:
1. **MISRA-C Warnings:** Có bất kỳ warning nào bị "justify" (bỏ qua) một cách vô lý không?
2. **Global Variables:** Biến global có được bảo vệ chống lại Data Consistency/Race condition (VD: dùng Spinlock, Disable Interrupt) khi nhiều task cùng truy cập không?
3. **Pointers:** Pointer có được check `NULL` trước khi dereference không?
4. **Timeouts:** Các vòng lặp `while (HW_REG != READY)` có timeout counter không? (Chống infinite loop nếu HW chết).
5. **Memory Mapping:** Các biến của ASIL module đã được map đúng vào phân vùng RAM ASIL chưa?
6. **Init phase:** Các thanh ghi safety (Watchdog, MPU) đã được khởi tạo trước khi bật ngắt chưa?

**Common findings và cách fix:**
- *Finding:* Dùng `while(1)` hoặc chờ cờ phần cứng không có giới hạn. -> *Fix:* Thêm biến đếm (timeout counter), nếu hết đếm mà cờ chưa set thì báo DET/DEM error.
- *Finding:* Ép kiểu (cast) con trỏ không an toàn. -> *Fix:* Sử dụng union hoặc memcpy nếu cần thiết, tuân thủ MISRA.

---

## 12. Interview Q&A — 30 câu hỏi 3 levels

### Level 1: Basic (Dành cho Junior/Fresher)
1. **Q:** ISO 26262 là gì? -> **A:** Tiêu chuẩn Functional Safety cho ô tô.
2. **Q:** ASIL là viết tắt của gì? -> **A:** Automotive Safety Integrity Level.
3. **Q:** Nêu 4 mức ASIL? -> **A:** ASIL A, B, C, D (D cao nhất).
4. **Q:** QM là gì? -> **A:** Quality Management, mức độ không yêu cầu tiêu chuẩn safety đặc biệt.
5. **Q:** HARA gồm 3 yếu tố nào? -> **A:** Severity, Exposure, Controllability.
6. **Q:** WdgM trong AUTOSAR có nhiệm vụ gì? -> **A:** Giám sát thời gian và logic thực thi của phần mềm.
7. **Q:** Lockstep CPU là gì? -> **A:** Hai nhân CPU chạy cùng 1 tập lệnh và so sánh kết quả liên tục.
8. **Q:** MISRA-C sinh ra để làm gì? -> **A:** Ngăn chặn các hành vi không xác định (Undefined Behavior) trong code C.
9. **Q:** FMEA là phân tích Top-down hay Bottom-up? -> **A:** Bottom-up.
10. **Q:** HARA thực hiện ở phase nào của project? -> **A:** Concept Phase (Part 3).

### Level 2: Intermediate (Dành cho Mid-level / BSW / App Engineer)
11. **Q:** Phân biệt FSR, TSR, SSR? -> **A:** FSR (Hệ thống), TSR (Kỹ thuật/Kiến trúc), SSR (Chi tiết cho Software).
12. **Q:** Làm sao để ngăn 1 Task QM phá hỏng RAM của Task ASIL D? -> **A:** Dùng Memory Protection Unit (MPU).
13. **Q:** Alive Supervision khác Deadline Monitoring thế nào? -> **A:** Alive đếm số lần task chạy, Deadline đo thời gian chạy từ lúc bắt đầu đến kết thúc.
14. **Q:** Freedom from Interference (FFI) là gì? -> **A:** Đảm bảo các thành phần non-safety không gây ảnh hưởng đến thành phần safety.
15. **Q:** MC/DC Coverage là gì? Khác Branch Coverage thế nào? -> **A:** Phân tích ảnh hưởng độc lập của từng condition trong một if-statement phức tạp. Bắt buộc cho ASIL D.
16. **Q:** ECC RAM hoạt động ra sao? -> **A:** Sửa lỗi 1 bit (SECDED), phát hiện lỗi 2 bit.
17. **Q:** E2E (End-to-End) protection trong AUTOSAR là gì? -> **A:** Dùng CRC, Counter, Data ID để bảo vệ gói tin (CAN/Ethernet) không bị corrupt, lost, delay.
18. **Q:** ASIL Decomposition có làm giảm mức độ nghiêm trọng (Severity) của Hazard không? -> **A:** Không, nó chỉ phân bổ rủi ro phát triển phần mềm/phần cứng cho các component độc lập (VD: D -> B+B).
19. **Q:** Sự khác biệt giữa ISO 26262 và ISO 21434? -> **A:** 26262 là Safety (hệ thống không tự hỏng), 21434 là Cybersecurity (bảo vệ khỏi hacker).
20. **Q:** Plausibility check là gì? -> **A:** Kiểm tra tính hợp lý của dữ liệu đầu vào (VD: 2 sensor ga phải có tổng điện áp = 5V).

### Level 3: Advanced (Dành cho Senior / Architect / Safety Manager)
21. **Q:** Nếu dự án dùng 1 con chip không có Lockstep (chỉ có 1 core), làm sao để đạt ASIL D? -> **A:** Rất khó, phải dùng external HW watchdog, Software Diverse Redundancy, hoặc ASIL Decomposition với 2 vi điều khiển song song.
22. **Q:** Giải thích "Dependent Failures" (Common Cause Failure & Cascading Failure). -> **A:** Cascading là A hỏng làm B hỏng theo. Common Cause là C hỏng làm cả A và B cùng hỏng (VD: Nguồn cấp bị lỗi làm 2 sensor cùng hỏng). Phân tích bằng DFA (Dependent Failure Analysis).
23. **Q:** Tool Qualification (Part 8) là gì? Tại sao phải qualify compiler? -> **A:** Chứng minh rằng compiler (ví dụ GCC, Tasking, GreenHills) không tự ý sinh ra code sai lệch (bug compiler). `[NEEDS VERIFICATION: exact sub-clause Part 8]`.
24. **Q:** Làm thế nào để chứng minh FFI giữa bộ nhớ, thời gian thực thi (timing) và truyền thông (communication)? -> **A:** Bộ nhớ (MPU), Timing (WdgM/OS deadline), Communication (E2E/CRC).
25. **Q:** SOTIF (ISO 21448) bổ sung gì cho ISO 26262? -> **A:** SOTIF xử lý các tình huống hệ thống hoạt động bình thường (không có lỗi H/W, S/W) nhưng vẫn gây nguy hiểm do giới hạn công nghệ (VD: Camera không thấy xe màu trắng trong tuyết).
26. **Q:** FIT rate là gì và công thức tính PMHF? -> **A:** FIT = Failures In Time (1 lỗi / 1 tỷ giờ). PMHF (Probabilistic Metric for Random Hardware Failures) là xác suất lỗi H/W dùng để đánh giá phần cứng có đạt ASIL target hay không. `[NEEDS VERIFICATION: exact mathematical formula is complex and varies by part]`.
27. **Q:** Hardware metrics (SPFM, LFM) cho ASIL D yêu cầu bao nhiêu %? -> **A:** SPFM (Single Point Fault Metric) >= 99%, LFM (Latent Fault Metric) >= 90%.
28. **Q:** Khi tích hợp một thư viện 3rd party (ví dụ OpenCV) vào hệ thống ASIL B, bạn làm gì? -> **A:** Sử dụng quy trình SEooC (Safety Element out of Context) hoặc bọc nó vào QM partition, hoặc thực hiện Software Qualification nếu bắt buộc dùng trong ASIL path.
29. **Q:** Làm sao để test khả năng bắt lỗi của Error Handler (ví dụ MPU exception)? -> **A:** Dùng Fault Injection Testing (Software hoặc Hardware-based). Chủ động ép con trỏ ghi đè bộ nhớ để xem OS Hook có chạy không.
30. **Q:** Safety Case là gì? -> **A:** Bộ tài liệu tổng hợp toàn bộ các bằng chứng (evidence) từ requirement, design, review report, test result, HARA... để chứng minh với Assessor (TÜV) rằng hệ thống đã an toàn.

---

## 13. Hands-on Exercise

**Tình huống:** Bạn đang thiết kế hệ thống **BMS (Battery Management System)** cho xe điện.
**Chức năng:** Giám sát nhiệt độ Cell pin. Nếu nhiệt độ > 60°C, phải ngắt Relay (Contactor) trong vòng 100ms.

**Bước 1: Phân tích HARA (Giả định)**
- **Hazard:** Pin quá nhiệt dẫn đến bốc cháy toàn bộ xe.
- **S (Severity):** S3 (Gây tử vong).
- **E (Exposure):** E4 (Xe hoạt động hàng ngày, sạc/xả liên tục).
- **C (Controllability):** C3 (Không thể kiểm soát khi xe đã cháy).
- -> **ASIL Level:** ASIL D.

**Bước 2: Định nghĩa Safety Goal & FSR**
- **Safety Goal (SG):** BMS phải ngăn chặn Cell pin vượt quá 60°C do xả/sạc quá mức (ASIL D).
- **FSR_01:** BMS phải liên tục đo nhiệt độ của các Cell pin (ASIL D).
- **FSR_02:** Khi phát hiện T_cell > 60°C, BMS phải ngắt Contactor trong < 100ms (ASIL D).

**Bước 3: Xác định Safety Mechanisms cần implement (TSR/SSR)**
- **Hardware:**
  - Sử dụng ít nhất 2 cảm biến nhiệt độ (NTC) cho mỗi module pin (Redundancy).
  - Vi điều khiển (MCU) đạt chuẩn ASIL D (có Lockstep, ECC).
- **Software:**
  - **Plausibility Check:** So sánh giá trị của Sensor 1 và Sensor 2. Nếu sai lệch > 5°C, đánh cờ lỗi (Sensor Failure).
  - **WdgM:** Giám sát task đọc nhiệt độ (`Tsk_ReadTemp`). Nếu task này bị treo (không update được nhiệt độ mới), WdgM phải reset MCU.
  - **E2E Protection:** Nếu nhiệt độ được truyền qua CAN đến một ECU khác để xử lý, bản tin CAN phải có CRC và Rolling Counter (E2E Profile 1/2) để chống nhiễu trên đường truyền.
  - **Timeout Monitoring:** Vòng lặp đọc ADC phải có giới hạn (Timeout) tránh tình trạng `while(ADC_NOT_READY)` vĩnh viễn.

---
*(Tài liệu này là tài sản tham khảo nội bộ và dành cho việc đào tạo chuyên sâu)*

