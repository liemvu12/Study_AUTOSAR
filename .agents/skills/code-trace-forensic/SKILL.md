---
name: code-trace-forensic
description: >-
  Enforces a strict, evidence-based code tracing methodology (Strict Forensic Mode).
  Activates when analyzing codebase flows, tracing call chains, debugging, verifying function execution paths,
  or investigating software architecture. Eliminates assumptions and hallucinations by mandating that source code
  is the only authority, requiring wide-first search, negative evidence verification, runtime path validation,
  evidence tagging ([FACT], [HYPOTHESIS]), and a standardized forensic output format.
---

# CODE TRACE SKILL - STRICT FORENSIC MODE

## MISSION
Mục tiêu tối thượng là **tìm sự thật trong source code**, không phải tạo ra một lời giải thích có vẻ hợp lý.

> ### 🚨 Forensic Prime Directive
> 1. **"Source code thực thi là chân lý duy nhất."**
> 2. **"Nếu mã nguồn không chứng minh được, bắt buộc phải trả lời: 'Không tìm thấy bằng chứng trong source code'."**
> 3. **"Tuyệt đối không bù đắp khoảng trống thông tin bằng kinh nghiệm cá nhân hay phỏng đoán."**

---

## MANDATORY RULES (10 NGUYÊN TẮC BẮT BUỘC)

### 1. SEARCH WIDE FIRST (Mở Rộng Phạm Vi Tìm Kiếm Trước Tiên)
* **Không được kết luận** chỉ từ một thư mục hoặc một file đơn lẻ.
* Phải mở rộng tìm kiếm trên toàn bộ codebase trước khi đưa ra nhận định.
* Luôn truy vết ngược và xuôi đa chiều:
  * `caller` (ai gọi hàm này?)
  * `callee` (hàm này gọi những ai?)
  * `interface` (giao tiếp trừu tượng nào?)
  * `callback` (hàm callback nào được đăng ký?)
  * `event` (sự kiện nào phát sinh?)
  * `message` / `IPC` (thông điệp / hàng đợi nào truyền nhận?)
  * `state machine` (trạng thái nào cho phép chạy?)
  * `config` (file cấu hình nào quy định?)
  * `build flag` / `macro` (cờ biên dịch nào bật/tắt đoạn mã này?)
  * `generated code` (mã tự động sinh trong thư mục build/out).
* Tiếp tục truy vết cho đến khi chạm tới điểm thực thi thực sự ngoài phần cứng/entry point hoặc khi hết bằng chứng.

### 2. SOURCE CODE IS THE ONLY AUTHORITY (Chỉ Source Code Có Quyền Lực)
* **Cấm suy đoán chức năng qua tên hàm:** Tên hàm `ProcessData()` không đồng nghĩa với việc nó xử lý dữ liệu thực tế nếu mã bên trong rỗng hoặc bị return sớm.
* **Cấm dùng comment làm bằng chứng chính:** Comment có thể lỗi thời, viết sai hoặc không phản ánh đúng logic thực thi. Comment chỉ mang giá trị tham khảo.
* **Cấm dùng tên file/thư mục làm bằng chứng chính:** File nằm trong thư mục `driver/` không chứng minh nó là driver đang chạy thật nếu không được liên kết trong build script.
* Chỉ coi **mã nguồn C/C++/Assembly thực thi** là bằng chứng có giá trị chứng minh.

### 3. NO HALLUCINATION (Tuyệt Đối Không Ảo Tưởng)
* Nếu code không chứng minh được, bắt buộc phải tuyên bố:
  > *"Không tìm thấy bằng chứng trong source code."*
* Cấm suy đoán ý nghĩa, hành vi hoặc luồng chạy chưa được xác nhận trực tiếp bằng mã nguồn.
* Không được điền vào khoảng trống thông tin bằng kiến thức chung, tiêu chuẩn lý thuyết hoặc kinh nghiệm cá nhân nếu không tìm thấy bằng chứng tương ứng trong repo.

### 4. FACT VS HYPOTHESIS (Phân Định Rạch Ròi Sự Thật vs Giả Thuyết)
Mọi kết luận kỹ thuật bắt buộc phải được gắn nhãn phân loại:
* **`[FACT]` (Sự Thật):**
  * Có bằng chứng trực tiếp, không thể chối cãi trong source code.
  * Chỉ rõ file, dòng, hàm và mã nguồn cụ thể.
* **`[HYPOTHESIS]` (Giả Thuyết):**
  * Suy luận logic khi chưa đủ 100% bằng chứng trực tiếp.
  * Bắt buộc phải nêu rõ: **Cần trace thêm điều gì hoặc cần thêm file/log nào để xác nhận.**
* Tuyệt đối không được trình bày giả thuyết như một sự thật hiển nhiên.

### 5. EVIDENCE REQUIRED (Bắt Buộc Dẫn Chứng Kỹ Thuật Đầy Đủ)
Mọi kết luận kỹ thuật đều vô giá trị nếu thiếu bằng chứng. Bắt buộc phải đi kèm:
* **File path:** Đường dẫn tuyệt đối hoặc tương đối chính xác (`file:///...`).
* **Function:** Tên hàm chính xác.
* **Line:** Số dòng chính xác (`#L123-L145`).
* **Code snippet:** Trích đoạn mã nguồn thực tế chứng minh luận điểm.
* **Call chain:** Chuỗi gọi hàm tuần tự dẫn tới vị trí đó.
> *Không có evidence = Không có kết luận.*

### 6. TRACE REAL EXECUTION PATH (Truy Vết Đường Thực Thi Thực Tế)
Không bao giờ kết luận một chức năng đang chạy chỉ vì hàm đó tồn tại trong codebase. Luôn kiểm tra 8 yếu tố thực thi:
1. **Ai gọi hàm?** (Caller chain).
2. **Khi nào được gọi?** (Khởi động, ngắt, hay vòng lặp chu kỳ?).
3. **Điều kiện gọi là gì?** (Câu lệnh `if`, `switch-case`, `guard condition`).
4. **State nào gọi?** (State machine hiện tại có cho phép không?).
5. **Thread / Task nào gọi?** (Ngữ cảnh thực thi: Main loop, ISR, RTOS Task nào?).
6. **Timer nào kích hoạt?** (Hardware Timer, Software Timer chu kỳ bao nhiêu ms?).
7. **Event nào kích hoạt?** (Interrupt flag, Semaphore, Queue message?).
8. **Build flag nào ảnh hưởng?** (`#ifdef`, `#if defined`, CMakeLists, Makefile, SCons).

### 7. CHECK NEGATIVE EVIDENCE (Tìm Kiếm Bằng Chứng Phủ Định)
Trước khi chốt bất kỳ kết luận nào, phải chủ động cố gắng **chứng minh kết luận đó là SAI** bằng cách rà soát:
* Có implementation khác của cùng interface không?
* Có hàm override hoặc re-define ở platform khác không?
* Hàm có thuộc tính `__weak` (weak symbol) bị hàm khác ghi đè không?
* Hàm có bị `#define` thay thế bằng macro rỗng không?
* Điều kiện compile (`#ifdef`, `#ifndef`) có vô hiệu hóa khối mã này trong target hiện tại không?
* Có mã nguồn chuyên biệt theo từng biến thể phần cứng (variant/board-specific) thay thế không?
> *Chỉ khi không tìm thấy bằng chứng phủ định, kết luận mới được phép giữ nguyên.*

### 8. HANDLE UNKNOWN PROPERLY (Xử Lý Minh Bạch Khi Chưa Rõ)
Hệ thống chấp nhận hoàn toàn các câu trả lời:
* *"Không đủ dữ liệu trong codebase hiện tại."*
* *"Chưa xác định được do thiếu cấu hình build / generated code."*
* *"Cần thêm mã nguồn hoặc sơ đồ kết nối phần cứng để kết luận."*
> *Thừa nhận chưa rõ là một kết quả phân tích hợp lệ và có giá trị cao. Tuyệt đối không được đoán mò.*

### 9. RUNTIME OVER STATIC ASSUMPTION (Thực Thi Runtime Quan Trọng Hơn Tồn Tại Tĩnh)
Không bao giờ giả định mã nguồn sẽ chạy trong thực tế chỉ vì:
* Hàm có tồn tại trong source code.
* Callback đã được gán vào con trỏ hàm.
* Event đã được định nghĩa trong header.
* Trạng thái (State) có mặt trong enum.

Bắt buộc phải tìm bằng chứng cho toàn bộ chuỗi runtime:
$$\text{Source Event / Interrupt} \longrightarrow \text{Dispatcher} \longrightarrow \text{Handler} \longrightarrow \text{State Machine} \longrightarrow \text{Target Function}$$
> *Nếu chuỗi truy vết chưa chạm tới Target Function, cấm khẳng định luồng xử lý đó thực sự xảy ra!*

---

## 10. SUBAGENT DELEGATION POLICY (Chính Sách Ủy Quyền Cho Research Subagent)

Nhằm bảo toàn cửa sổ ngữ cảnh (Context Window Preservation) và ngăn ngừa suy giảm chất lượng suy luận do tràn token khi khảo sát codebase lớn:

1. **Khảo sát cục bộ (≤ 3 files hoặc vị trí đã biết rõ):**
   - Agent trực tiếp sử dụng công cụ `read_file` trong phiên làm việc hiện tại để phản hồi nhanh.

2. **Khảo sát diện rộng (> 3 files, quét toàn bộ repository, hoặc truy vết phụ thuộc chéo module):**
   - Agent BẮT BUỘC ủy quyền việc đọc và grep dữ liệu thô cho built-in subagent `research` thông qua công cụ `invoke_subagent`:
     ```json
     invoke_subagent({
       "TypeName": "research",
       "Role": "Forensic Codebase Investigator",
       "Prompt": "Áp dụng nghiêm ngặt các nguyên tắc của code-trace-forensic: Điều tra [Mục tiêu]. Chỉ trả về bản chưng cất [FACT], số dòng file, prototype và kết luận ngắn gọn.",
       "Model": "inherit",
       "Workspace": "inherit"
     })
     ```
   - Subagent `research` hoạt động trong **Read-Only Sandbox an toàn tuyệt đối**, thực hiện toàn bộ quá trình đọc dữ liệu thô trong context riêng và chỉ gửi về bản tóm tắt có cấu trúc, giúp bảo vệ 100% Context Window của Agent chính.

---

## 11. OUTPUT FORMAT (KHUNG BÁO CÁO BẮT BUỘC)

Mọi phản hồi điều tra mã nguồn dưới chế độ này bắt buộc phải tuân thủ nghiêm ngặt cấu trúc sau:

```markdown
### QUESTION
[Câu hỏi hoặc mục tiêu truy vết của người dùng]

### SEARCHED SCOPE
[Danh sách các thư mục, file, module và build target đã được rà soát trên toàn codebase]

### EVIDENCE
[Các trích đoạn mã nguồn thực tế kèm đường dẫn clickable link file:///, tên hàm và số dòng chính xác]

### CALL CHAIN
[Sơ đồ chuỗi gọi hàm thực tế từ điểm phát sinh sự kiện đến điểm đích thực thi]
Trigger -> Function_A() -> Function_B() -> Target_Function()

### FACTS
- [FACT] Luận điểm 1 được chứng minh bởi mã nguồn...
- [FACT] Luận điểm 2 được chứng minh bởi mã nguồn...

### HYPOTHESES
- [HYPOTHESIS] Giả thuyết kỹ thuật (nếu có)...
  * Cần trace thêm: [Cụ thể tên file, biến hoặc log cần kiểm tra để chuyển thành Fact]

### MISSING EVIDENCE
- [Liệt kê các bằng chứng còn thiếu, các cờ build chưa xác định, hoặc các file generated code chưa có]

### FINAL CONCLUSION
[Kết luận súc tích, bám sát sự thật kỹ thuật, không suy đoán]

### CONFIDENCE
[HIGH / MEDIUM / LOW]
- HIGH: Có bằng chứng trực tiếp đầy đủ 100% trong mã nguồn thực thi.
- MEDIUM: Có bằng chứng gián tiếp nhưng chưa trace được toàn bộ runtime path đến tận cùng.
- LOW: Chưa đủ bằng chứng, chủ yếu là giả thuyết cần kiểm chứng thêm.
```
