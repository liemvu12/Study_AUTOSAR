# ASPICE và V-Model Process trong Automotive

## 1. Automotive Software Development Lifecycle

### Tại sao cần Process (ISO 9001 không đủ cho safety-critical)?
Trong ngành công nghiệp ô tô, phần mềm không chỉ điều khiển các tính năng giải trí mà còn chịu trách nhiệm cho các hệ thống an toàn sinh tử (safety-critical systems) như phanh (ABS/ESC), túi khí, hệ thống lái, và quản lý pin (BMS).
ISO 9001 là tiêu chuẩn quản lý chất lượng chung, tập trung vào sự hài lòng của khách hàng và quy trình cải tiến liên tục, nhưng nó không cung cấp các hướng dẫn cụ thể về kỹ thuật phần mềm, quản lý yêu cầu (requirements management), traceability, hay các cấp độ kiểm thử chuyên sâu.
Vì vậy, ngành ô tô yêu cầu các tiêu chuẩn khắt khe hơn như **ASPICE** (Quy trình phát triển phần mềm) và **ISO 26262** (An toàn chức năng - Functional Safety) để đảm bảo chất lượng, độ tin cậy và khả năng truy xuất nguồn gốc từ lúc bắt đầu cho đến khi kết thúc dự án.

### V-Model: Mỗi cấp development có cấp test tương ứng
V-Model (Mô hình chữ V) là cốt lõi của quy trình phát triển phần mềm ô tô. Nó thể hiện mối quan hệ đối xứng giữa các giai đoạn phát triển (bên trái) và các giai đoạn kiểm thử tương ứng (bên phải). Nguyên tắc cơ bản:
- Hệ thống được phân rã từ trên xuống dưới (Top-Down) trong pha phát triển.
- Hệ thống được tích hợp và kiểm thử từ dưới lên trên (Bottom-Up) trong pha xác thực.
- Mỗi mức thiết kế/yêu cầu bên nhánh trái phải có một mức kiểm thử tương ứng bên nhánh phải để xác minh (verify).

### Timeline điển hình: Từ RfQ đến SOP (Start of Production)
Một dự án ô tô điển hình kéo dài từ 2 đến 3 năm, bao gồm các giai đoạn:
1. **Concept Phase & Quotation (RfQ) (6 months):** Khách hàng (OEM) gửi Request for Quotation (Yêu cầu báo giá). Tier-1 phân tích tính khả thi, đưa ra system concept sơ bộ và báo giá.
2. **System Design (6 months):** Thu thập yêu cầu hệ thống, phân tích và thiết kế System Architecture (phân bổ chức năng cho Hardware, Software, Mechanical).
3. **SW Development (12 months):** Thu thập yêu cầu phần mềm, thiết kế kiến trúc phần mềm, thiết kế chi tiết và lập trình (Coding). Tích hợp các module phần mềm.
4. **Validation & Verification (6 months):** Thực hiện System Integration Test, System Test trên phần cứng thực tế, thực hiện xe thực tế (Vehicle level test).
5. **Production Ramp-up (3 months):** Tối ưu hóa quy trình sản xuất, fix các lỗi nhỏ (bug fixes) và chuẩn bị SOP.

---

## 2. ASPICE Overview

### ASPICE (Automotive SPICE) là gì?
ASPICE (Automotive Software Process Improvement and Capability dEtermination) là một tiêu chuẩn quốc tế cung cấp một framework để đánh giá và cải tiến năng lực quy trình phát triển phần mềm và hệ thống trong ngành ô tô. Nó dựa trên ISO/IEC 15504 và hiện tại là ISO/IEC 33020.

### Level 0 → Level 5: Ý nghĩa từng level
Năng lực quy trình được đánh giá qua 6 cấp độ (Capability Levels - CL):
- **Level 0 (Incomplete):** Quy trình không được thực hiện hoặc không đạt được mục tiêu của nó. (Hỗn loạn).
- **Level 1 (Performed):** Quy trình được thực hiện và đạt được mục đích, nhưng không có kế hoạch, quản lý rủi ro hay theo dõi bài bản. Làm ra được sản phẩm nhưng khó lặp lại.
- **Level 2 (Managed):** Quy trình được thực hiện, có kế hoạch, được giám sát và điều chỉnh. Sản phẩm của quy trình (Work products) được quản lý, kiểm soát version và review đầy đủ. **Đây là mức tối thiểu hầu hết OEM yêu cầu Tier-1 đạt được.**
- **Level 3 (Established):** Quy trình được tiêu chuẩn hóa áp dụng cho toàn bộ tổ chức (Organization-wide standard process) và được tinh chỉnh cho từng dự án (Tailoring).
- **Level 4 (Predictable):** Quy trình được đo lường thống kê và kiểm soát định lượng. (Biết chính xác mất bao nhiêu giờ cho 1 function).
- **Level 5 (Innovating):** Quy trình được cải tiến liên tục dựa trên phân tích nguyên nhân gốc rễ và tối ưu hóa sáng tạo.

### Các Process Areas phổ biến (HIS Scope/VDA Scope)
- **SYS.1 - SYS.5 (System Engineering):** Từ thu thập yêu cầu hệ thống (System Requirements) đến kiểm thử hệ thống (System Testing).
- **SWE.1 (Software Requirements Analysis):** Phân tích, phân loại, đánh giá rủi ro yêu cầu phần mềm.
- **SWE.2 (Software Architectural Design):** Thiết kế kiến trúc phần mềm (các components, interfaces, dynamic behaviors).
- **SWE.3 (Software Detailed Design & Unit Construction):** Thiết kế chi tiết cho từng component (Flowchart, State machine) và viết code.
- **SWE.4 (Software Unit Verification):** Kiểm thử mức đơn vị (Unit Test), Static analysis (MISRA).
- **SWE.5 (Software Integration and Integration Test):** Tích hợp các unit lại và test sự giao tiếp giữa chúng.
- **SWE.6 (Software Qualification Test):** Test phần mềm hoàn chỉnh theo SWE.1 (Software Requirements).
- **MAN.3 (Project Management):** Quản lý dự án, lập kế hoạch, theo dõi tiến độ, quản lý rủi ro.
- **SUP.8 (Configuration Management):** Quản lý phiên bản, source code, tài liệu (Git, SVN).
- **SUP.9 (Problem Resolution Management):** Quản lý lỗi (Issue/Bug tracking), quy trình xử lý lỗi (Jira).

---

## 3. Traceability — Yêu Cầu Quan Trọng Nhất

Traceability (Khả năng truy xuất nguồn gốc) là xương sống của ASPICE. Nó chứng minh rằng: "Mọi yêu cầu đều được thực hiện, mọi yêu cầu đều được test, và không có code nào thừa (không có yêu cầu)".
Traceability phải là **Bidirectional** (Hai chiều: Forward và Backward).

### Traceability matrix: Requirement → Design → Code → Test Case
- **Forward:** Yêu cầu khách hàng -> Yêu cầu hệ thống -> Yêu cầu phần mềm -> Kiến trúc -> Code -> Test. Để đảm bảo tính đầy đủ (Completeness).
- **Backward:** Test -> Code -> Kiến trúc -> Yêu cầu phần mềm -> Yêu cầu khách hàng. Để đảm bảo không có chức năng ngoài lề (No unintended functions) và đánh giá tác động khi thay đổi (Impact Analysis).

### Ví dụ thực tế:
1. **System Requirement (SYS-REQ-001):** "BMS shall report SoC (State of Charge) every 100ms via CAN."
2. **Software Requirement (SWE-REQ-005):** "BMS_Runnable shall execute every 100ms and call SoC calculation module." (Link tới SYS-REQ-001)
3. **Software Architecture (SWAD-010):** Interface `CalcSoC()` được định nghĩa giữa module RTE và `SoC_App`. (Link tới SWE-REQ-005)
4. **Code:** Hàm `BMS_MainRunnable()` tại `app.c:line 45` gọi `CalcSoC()`.
5. **Unit Test (SWE.4):** `TC_SoC_001` test hàm `CalcSoC()` đúng công thức. (Link tới SWAD/SWDD).
6. **Software Qualification Test (SWE.6):** `TC_BMS_001` giả lập chạy trên target, verify timer 100ms gọi function. (Link tới SWE-REQ-005).

### Tools sử dụng:
- **Polarion ALM, IBM DOORS, codeBeamer:** Phổ biến nhất trong Automotive, tự động link và tạo Traceability Matrix, cảnh báo khi có Broken Link.
- **Excel:** Chỉ dành cho project cực nhỏ hoặc Proof of Concept, do làm thủ công rất dễ sai sót.

---

## 4. Typical Workflow: Customer Req → Release

Quy trình phát triển tuân thủ V-Model và ASPICE diễn ra tuần tự và lặp lại (Iterative):

```text
1. Customer RfQ / Customer Requirements
   ↓ (Analyze, Negotiate)
2. System Requirement Specification (SRS) - [SYS.2]
   ↓ (System Design)
3. System Architecture Design - [SYS.3] (Phân bổ cho HW/SW)
   ↓ (Extract SW parts)
4. Software Requirement Specification (SwRS) - [SWE.1]
   ↓ (SW Design)
5. Software Architecture Design (SwAD) - [SWE.2]
   ↓ (Detailing)
6. Software Detailed Design (SwDD) - [SWE.3]
   ↓ (Coding)
7. Source Code Implementation
   ↓ (Unit Testing)
8. Unit Test (UT) - [SWE.4] (Test từng file C/function)
   ↓ (Integrate)
9. Software Integration Test (SIT) - [SWE.5] (Test BSW, RTE, SWC)
   ↓ (Test against SwRS)
10. Software Qualification Test (SQT) - [SWE.6]
   ↓ (Flash to Hardware)
11. System Test - [SYS.4/5] (Test full ECU)
   ↓
12. Review & Release (Quality Assurance, Baseline creation)
```

---

## 5. Testing Levels trong AUTOSAR Project

### Unit Test (SWE.4)
- **Mục tiêu:** Đảm bảo từng hàm (function) trong module C chạy đúng.
- **Phương pháp:** Module được test hoàn toàn cách ly (isolation). Mọi hàm gọi ra ngoài (dependencies), biến toàn cục, register đều phải được Mock hoặc Stub.
- **Tools:** Google Test (GTest) + CppUMock cho C/C++, Unity, LDRA, VectorCAST, TESSY.
- **Coverage requirement:** Dựa vào ISO 26262 ASIL (Automotive Safety Integrity Level).
  - ASIL A/B: Statement Coverage (100%), Branch Coverage (100%).
  - ASIL C/D: Bắt buộc MC/DC Coverage (Modified Condition/Decision Coverage).
- **Ví dụ test case cho BMS SoC calculation:** Test hàm `CalcSoC(voltage, current, temp)`. Input voltage=3.7V, current=10A, temp=25C. Kiểm tra output trả về SoC = 85%.

### Integration Test (SWE.5)
- **Mục tiêu:** Kiểm tra sự tương tác giữa các module (interfaces).
- **Ví dụ AUTOSAR BSW integration test:** Tích hợp bộ nhớ: NvM (Non-volatile Memory Manager) + Fee (Flash EEPROM Emulation) + Fls (Flash Driver). Viết test case yêu cầu NvM ghi data, kiểm tra xem Fls có thực sự ghi xuống Flash mô phỏng hoặc phần cứng thật không.
- **Môi trường:** Có thể test trên PC (SIL - Software In the Loop) hoặc trên Test Bench (Target). Hardware-in-the-Loop (HiL) setup thường được dùng ở mức này hoặc mức System.

### System Test (SWE.6 và SYS.5)
- **Mục tiêu:** Test toàn bộ ECU với phần cứng thật và các tín hiệu giả lập (stimuli) giống xe thật. Test dựa trên System Requirements.
- **Test environment:** Dùng Vector CANoe (kết hợp VN1630/1640) để giả lập mạng CAN/LIN/FlexRay, phát các bản tin từ các ECU khác. Dùng Lauterbach Trace32 để debug trực tiếp trên chip (On-target debug), đo tải CPU, thời gian thực thi (Execution time profiling).

---

## 6. Tools Ecosystem

| Tool | Purpose | Phase (Giai đoạn) |
|------|---------|--------------------|
| **Polarion ALM** | Quản lý Requirements, Traceability, Test cases | All phases |
| **IBM DOORS** | Quản lý Requirements (Legacy, vẫn rất phổ biến) | All phases |
| **JIRA** | Bug tracking, Task tracking, Agile/Scrum board | Development, Testing |
| **Jenkins / GitLab CI**| CI/CD pipeline, Tự động build, chạy test, sinh report | Build & Test |
| **Git / Bitbucket** | Version control, Branching, Code review (Pull Request) | Development |
| **DaVinci Developer/Configurator**| Cấu hình kiến trúc và các module AUTOSAR | SW Architecture & Design |
| **Lauterbach Trace32**| Debug trực tiếp trên Vi điều khiển (JTAG), đo hiệu năng | Testing, Debugging |
| **Vector CANoe** | Gửi/Nhận bản tin CAN/LIN, giả lập các ECU khác (Restbus) | Integration/System Test |
| **LDRA / VectorCAST** | Chạy Unit Test và đo đạt Code Coverage (MC/DC) | Unit Testing (SWE.4) |
| **QAC / Polyspace** | Static Code Analysis, quét lỗi MISRA C | Unit Testing (SWE.4) |

---

## 7. BSW Engineer trong ASPICE Context

Một Kỹ sư Basic Software (BSW Engineer) trong quy trình ASPICE không chỉ "cắm đầu viết code".
### Responsibilities tại từng phase:
1. **SWE.1/SWE.2:** Đọc và hiểu Software Requirements và Architecture. Tham gia Review với System/Architect.
2. **SWE.3:** Cấu hình các module BSW trong AUTOSAR Tool (DaVinci). Viết tài liệu **Software Unit Detailed Design (SWDD)** mô tả behavior của module mình phụ trách (ví dụ cấu hình CAN, OS).
3. **Coding:** Generate code từ Tool, viết code cho phần Complex Device Driver (CDD) hoặc tích hợp. Chạy MISRA Check.
4. **SWE.4:** Tự viết và chạy Unit Test cho các hàm mình viết (CDD) hoặc chạy test tự động sinh ra cho BSW. Tạo **Unit Test Report**.
5. **Review:** Đóng vai trò là Reviewer cho code/design của đồng nghiệp.

### Deliverables (Sản phẩm giao nộp) phải produce:
- C code và Header files (rõ ràng).
- Cấu hình ARXML files (AUTOSAR).
- Static Analysis Report (MISRA) - giải trình nếu có warning (Deviation record).
- Software Unit Detailed Design (SWDD).
- Unit Test Specification & Unit Test Report.
- Review records (Biên bản review).

---

## 8. Interview Q&A — 20 câu hỏi về ASPICE & Quy trình

1. **Câu 1: ASPICE là gì và tại sao OEM lại yêu cầu nó?**
   *Đáp:* ASPICE là tiêu chuẩn đánh giá năng lực quy trình phát triển phần mềm ô tô. OEM yêu cầu vì nó đảm bảo chất lượng, giảm rủi ro lỗi safety-critical, và đảm bảo mọi yêu cầu đều được traceability rõ ràng.
2. **Câu 2: V-Model có ưu điểm gì so với Agile trong ngành ô tô?**
   *Đáp:* V-Model nhấn mạnh vào thiết kế chi tiết, tài liệu rõ ràng và các mức kiểm thử đối xứng, phù hợp với các hệ thống yêu cầu an toàn cao (ISO 26262). Agile thường thiếu tài liệu và traceability ở giai đoạn đầu. Hiện nay người ta kết hợp Agile trong ASPICE (Agile SPICE).
3. **Câu 3: Giải thích Traceability là gì?**
   *Đáp:* Là khả năng truy xuất nguồn gốc của một hạng mục từ trên xuống dưới (Requirement -> Design -> Code -> Test) và ngược lại, đảm bảo tính đầy đủ và không thừa.
4. **Câu 4: ASPICE Level 2 khác Level 1 ở điểm nào?**
   *Đáp:* Level 1 chỉ là làm được việc (Performed). Level 2 là có quy trình được quản lý (Managed): có kế hoạch, được review, quản lý version, cấu hình (Configuration Management) và tài liệu đầy đủ.
5. **Câu 5: SWE.4 (Unit Test) và SWE.5 (Integration Test) khác nhau thế nào?**
   *Đáp:* UT kiểm tra riêng lẻ từng function/file C, dùng mock/stub. IT kiểm tra giao tiếp (interfaces) giữa các file/module C với nhau.
6. **Câu 6: Bạn xử lý thế nào nếu mã nguồn (code) vi phạm quy tắc MISRA C?**
   *Đáp:* Nếu sửa được để tuân thủ thì sửa. Nếu bắt buộc phải vi phạm (ví dụ do tối ưu phần cứng), phải viết Deviation Record ghi rõ lý do và chứng minh nó an toàn.
7. **Câu 7: MC/DC coverage là gì? Khi nào cần dùng?**
   *Đáp:* Modified Condition/Decision Coverage. Đảm bảo mỗi điều kiện trong một câu lệnh if đều độc lập ảnh hưởng đến kết quả cuối cùng. Bắt buộc cho chuẩn ASIL C và ASIL D.
8. **Câu 8: Sự khác biệt giữa System Requirement và Software Requirement?**
   *Đáp:* System Req mô tả chức năng của cả hệ thống (gồm cả HW, SW, Cơ khí), ví dụ "Hệ thống phanh phải dừng xe trong 3s". Software Req lấy từ System Req phân bổ cho phần mềm: "Phần mềm phải kích hoạt van PWM 50% trong 50ms khi nhận tín hiệu phanh".
9. **Câu 9: Công cụ nào bạn từng dùng để quản lý Requirements?**
   *Đáp:* Polarion, DOORS, hoặc JIRA tùy dự án. (Cần mô tả cách bạn tạo link giữa yêu cầu và code).
10. **Câu 10: Nếu khách hàng thay đổi yêu cầu ở giữa dự án, quy trình ASPICE xử lý thế nào?**
    *Đáp:* Thực hiện Change Management. Phân tích tác động (Impact Analysis) dựa vào Traceability để biết những design, code, và test case nào bị ảnh hưởng. Sau đó cập nhật từ trên xuống dưới.
11. **Câu 11: Base Practice và Generic Practice trong ASPICE là gì?**
    *Đáp:* Base Practice là các hoạt động đặc thù của 1 process (ví dụ SWE.3 phải tạo design). Generic Practice là các hoạt động quản lý áp dụng cho mọi process (ví dụ lập kế hoạch, review tài liệu).
12. **Câu 12: Review Checklist là gì và tại sao quan trọng?**
    *Đáp:* Là danh sách các tiêu chí dùng khi review code/design. Nó đảm bảo mọi người review theo cùng một chuẩn mực và không bỏ sót các lỗi thường gặp.
13. **Câu 13: Khi chạy Unit Test, Stub và Mock khác nhau thế nào?**
    *Đáp:* Stub là hàm giả lập trả về giá trị cứng (hardcoded). Mock thông minh hơn, kiểm tra xem hàm đó có được gọi đúng số lần, đúng tham số truyền vào hay không.
14. **Câu 14: Biểu hiện của một dự án trượt ASPICE Level 2?**
    *Đáp:* Thiếu Traceability, code được viết mà không có design, thay đổi code không được quản lý qua hệ thống version control, không có biên bản review (Review records).
15. **Câu 15: Configuration Management (SUP.8) áp dụng cho Code hay cả Tài liệu?**
    *Đáp:* Cả hai. Mọi work product (Requirements, Design, Code, Test Scripts) đều phải được đưa vào hệ thống quản lý cấu hình (Git/SVN/Polarion) để kiểm soát phiên bản.
16. **Câu 16: Hardware-in-the-Loop (HiL) nằm ở bước nào trong V-Model?**
    *Đáp:* Nằm bên nhánh phải, thường dùng ở bước System Test (SYS.4/SYS.5) hoặc Software Qualification Test (SWE.6).
17. **Câu 17: Ai là người chịu trách nhiệm cho SWE.3?**
    *Đáp:* Kỹ sư phần mềm (Software Developer/BSW Engineer). Họ nhận SWAD và tạo ra Software Detailed Design (SwDD) cùng với Source code.
18. **Câu 18: Sự khác nhau giữa Verification và Validation?**
    *Đáp:* Verification (Xác minh): Đảm bảo làm sản phẩm đúng quy trình, đúng tài liệu (Did we build the product right?). Validation (Xác thực): Đảm bảo sản phẩm đáp ứng đúng nhu cầu thực tế của khách hàng (Did we build the right product?).
19. **Câu 19: Làm sao bạn chứng minh với Assessor (Người đánh giá) là bạn đã làm Unit Test đúng cách?**
    *Đáp:* Show tài liệu Unit Test Specification có link tới SwDD. Show file test scripts, Test Report với kết quả PASSED. Show Code Coverage Report (đạt 100% Statement/Branch). Show Review Record của Unit test.
20. **Câu 20: CI/CD (Continuous Integration / Continuous Deployment) hỗ trợ ASPICE như thế nào?**
    *Đáp:* CI/CD tự động hóa việc build, chạy MISRA, chạy Unit Test và tạo report mỗi khi có người push code. Giúp phát hiện lỗi sớm và đảm bảo SUP.8 (Configuration Management) luôn có build artifact chuẩn.
