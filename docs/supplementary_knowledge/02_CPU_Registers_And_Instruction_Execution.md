# 🖥️ CPU, REGISTER VÀ CÁCH CPU THỰC THI LỆNH — THỰC CHIẾN CHO EMBEDDED & AUTOSAR ENGINEER

> **Tác giả:** Senior Embedded Firmware & AUTOSAR Systems Engineer  
> **Cấp độ:** Junior+ → Mid/Senior Embedded  
> **Nền tảng:** ARM Cortex-M3 / Cortex-M4 / Cortex-M7 (Texas Instruments LM3S6965, STM32F107, STM32F4)  
> **Dự án thực tế:** Study AUTOSAR (`as` stack, OSEK/AUTOSAR OS `askar`, MCAL Drivers)  
> **Triết lý thực chiến:** Hiểu bản chất → Nhìn thấy trong C code → Nhìn thấy trong Assembly → Nhận diện khi Debug

---

## 📑 MỤC LỤC TOÀN DIỆN

### PHẦN 1: REGISTER MODEL & KIẾN TRÚC CỐT LÕI
1. [Chương 1: CPU và Hệ Thống Nhúng (Embedded System)](#chương-1-cpu-và-hệ-thống-nhúng-embedded-system)
2. [Chương 2: Register Model Của ARM Cortex-M](#chương-2-register-model-của-arm-cortex-m)
3. [Chương 3: R0–R3 — Function Arguments và Return Value](#chương-3-r0r3--function-arguments-và-return-value)
4. [Chương 4: R4–R12 — Preserved và Scratch Registers](#chương-4-r4r12--preserved-và-scratch-registers)
5. [Chương 5: SP / R13 — Stack Pointer và Vùng Nhớ Ngăn Xếp](#chương-5-sp--r13--stack-pointer-và-vùng-nhớ-ngăn-xếp)
6. [Chương 6: LR / R14 — Link Register và Lời Gọi Hàm (Function Call)](#chương-6-lr--r14--link-register-và-lời-gọi-hàm-function-call)
7. [Chương 7: PC / R15 — Program Counter và Điều Khiển Luồng Thực Thi](#chương-7-pc--r15--program-counter-và-điều-khiển-luồng-thực-thi)
8. [Chương 8: xPSR — Program Status Register và Các Cờ Điều Kiện (Flags)](#chương-8-xpsr--program-status-register-và-các-cờ-điều-kiện-flags)

### PHẦN 2: THỰC THI LỆNH, BỘ NHỚ VÀ NGẮT
9. [Chương 9: MSP và PSP — Kiến Trúc Hai Con Trỏ Ngăn Xếp](#chương-9-msp-và-psp--hai-stack-pointer)
10. [Chương 10: CPU Thực Thi Một Câu Lệnh Như Thế Nào?](#chương-10-cpu-thực-thi-một-instruction-như-thế-nào)
11. [Chương 11: LDR / STR — CPU Đọc và Ghi Bộ Nhớ](#chương-11-ldr--str--cpu-đọc-ghi-memory)
12. [Chương 12: Memory-Mapped Peripherals — Giao Tiếp Ngoại Vi](#chương-12-memory-mapped-peripheral)
13. [Chương 13: Từ C Code → Assembly → Machine Code → CPU](#chương-13-từ-c-code--assembly--machine-code--cpu)
14. [Chương 14: Interrupt và Exception — Cách CPU Xử Lý Ngắt](#chương-14-interrupt-và-exception--cách-cpu-xử-lý)
15. [Chương 15: Stack Frame Khi Có Ngắt (Hardware Context Stacking)](#chương-15-stack-frame-khi-interrupt)
16. [Chương 16: Kỹ Thuật Đọc & Phân Tích Register Dump Khi Debug](#chương-16-debug-register-dump)

### PHẦN 3: THỰC CHIẾN — DEBUG, RTOS, TẬP LỆNH VÀ CASE STUDIES
17. [Chương 17: HardFault — Quy Trình Chẩn Đoán Thực Dụng](#chương-17-hardfault--phân-tích-thực-dụng)
18. [Chương 18: RTOS Context Switch Dưới Góc Nhìn Thanh Ghi](#chương-18-rtos-context-switch)
19. [Chương 19: Các Lệnh Assembly Thiết Yếu Trong Lập Trình Nhúng](#chương-19-các-assembly-instruction-cần-biết)
20. [Chương 20: 15 Hiểu Lầm Tai Hại Phổ Biến Của Kỹ Sư Nhúng](#chương-20-15-common-misconceptions)
21. [Chương 21: 5 Case Study Bắt Bug Thực Chiến Trên Firmware](#chương-21-real-world-case-studies)
22. [Chương 22: 10 Bài Tập Rèn Luyện Tư Duy (Level 1 → Level 10)](#chương-22-exercises)
23. [Chương 23: Master Cheat Sheet (Tóm Tắt 1 Trang)](#chương-23-cheat-sheet)
24. [Chương 24: Senior Mental Model — Phản Xạ Tư Duy Khi Debug](#chương-24-senior-mental-model)

---

## 📌 QUY ƯỚC KÝ HIỆU THỰC CHIẾN

| Ký hiệu | Ý nghĩa | Ứng dụng trong công việc |
|:---|:---|:---|
| **[MUST]** | Kiến thức bắt buộc | Dùng hàng ngày khi code C, cấu hình MCAL, review code |
| **[SHOULD]** | Kiến thức nên biết | Cực kỳ hữu ích khi debug lỗi khó, tối ưu hiệu năng |
| **[AUTOSAR]** | Liên hệ thực tế | Ánh xạ trực tiếp tới AUTOSAR OS (`askar`), MCAL, BSW |
| **[SIMPLIFICATION]** | Đơn giản hóa có chủ đích | Lược bỏ chi tiết bán dẫn không cần thiết để tập trung bản chất |
| **[DEBUG]** | Kỹ năng gỡ lỗi | Cách quan sát trên GDB, Trace32, STM32CubeIDE |

---

# PHẦN 1: REGISTER MODEL & KIẾN TRÚC CỐT LÕI

---

## CHƯƠNG 1: CPU VÀ HỆ THỐNG NHÚNG (EMBEDDED SYSTEM)

### 1.1 Why — Tại Sao Kỹ Sư Nhúng Cần Hiểu Bản Chất CPU?
CPU không thực thi mã nguồn C/C++ trực tiếp. Mọi logic bạn viết trong hàm C (`if`, `for`, gọi hàm, gán biến) đều được trình biên dịch (compiler) dịch thành các chuỗi số nhị phân (Machine Instructions).

Khi xảy ra lỗi:
- Vi điều khiển bị treo trong vòng lặp vô tận `while(1)`.
- Hệ thống bị reset liên tục không rõ lý do (Watchdog hoặc HardFault).
- Dữ liệu mạng CAN bị rác hoặc mất gói tin.

Debugger sẽ dừng lại ở **Assembly và Register**. Nếu bạn không hiểu CPU lấy lệnh ở đâu, tính toán thế nào, tương tác với RAM và ngoại vi ra sao, bạn sẽ hoàn toàn bất lực và chỉ biết "đoán mò" hoặc chèn thêm lệnh `printf` vô vọng.

---

### 1.2 What — CPU Thực Sự Chứa Những Gì?

Bên trong lõi ARM Cortex-M (ví dụ Cortex-M3 trên board `lm3s6965evb` hoặc STM32F107 trong dự án `Study_AUTOSAR`), CPU bao gồm 4 khối chức năng cốt lõi:

```
+=============================================================================+
|                          ARM CORTEX-M CPU CORE                              |
|                                                                             |
|  +------------------------+             +--------------------------------+  |
|  |     REGISTER FILE      |             |     ARITHMETIC LOGIC UNIT      |  |
|  |  • R0 - R12: Data/Temp |<----------->|             (ALU)              |  |
|  |  • SP (R13): Stack Ptr |    Internal |  • Cộng, trừ, nhân (ADD, SUB)  |  |
|  |  • LR (R14): Link Reg  |    Bus      |  • Phép toán bit (AND, OR, XOR)|  |
|  |  • PC (R15): Prog Ctr  |             |  • Cập nhật cờ: N, Z, C, V     |  |
|  +------------------------+             +--------------------------------+  |
|               ▲                                      ▲                      |
|               │                                      │                      |
|  +------------┴-----------+             +------------┴-------------------+  |
|  |      CONTROL UNIT      |             |         BUS INTERFACE          |  |
|  |  • Instruction Fetch   |             |  • I-Code Bus (Fetch Code)     |  |
|  |  • Instruction Decode  |             |  • D-Code Bus (Data Literal)   |  |
|  |  • Flow Sequencing     |             |  • System Bus (SRAM & MMIO)    |  |
|  +------------------------+             +--------------------------------+  |
+======================================╤======================================+
                                       │ System Bus (AHB / APB)
        ┌──────────────────────────────┼──────────────────────────────┐
        ▼                              ▼                              ▼
+---------------+              +---------------+              +---------------+
|     FLASH     |              |     SRAM      |              |  PERIPHERALS  |
| (Code, Const) |              | (Data, Stack) |              | (CAN, UART...) |
| 0x00000000    |              | 0x20000000    |              | 0x40000000    |
+---------------+              +---------------+              +---------------+
```

1. **Register File (Tập thanh ghi):** Bộ nhớ siêu nhanh nằm ngay sát ALU. CPU chỉ có thể tính toán trực tiếp trên các thanh ghi này.
2. **ALU (Arithmetic Logic Unit):** Bộ não tính toán số học (+, -, *, /) và logic (AND, OR, NOT, Shift).
3. **Control Unit (Khối điều khiển):** Đọc lệnh máy từ bộ nhớ, giải mã (decode) xem lệnh yêu cầu làm gì, và ra lệnh cho ALU cùng Register File phối hợp thực hiện.
4. **Bus Interface (Giao diện Bus):** Cầu nối giúp CPU trao đổi dữ liệu với thế giới bên ngoài (Flash, SRAM và thanh ghi ngoại vi).

---

### 1.3 How — CPU Tương Tác Với Bộ Nhớ Và Ngoại Vi
ARM Cortex-M là kiến trúc **Load-Store Architecture**:
* **Không thể tính toán trực tiếp trên bộ nhớ:** CPU không thể lấy trực tiếp một ô nhớ trong Flash cộng với một ô nhớ trong SRAM rồi ghi thẳng vào SRAM.
* **Quy trình 3 bước bắt buộc:**
  1. **Load:** Đọc dữ liệu từ RAM/Ngoại vi vào Register (`LDR`).
  2. **Operate:** ALU thực hiện phép tính trên Register (`ADD`, `SUB`, `AND`...).
  3. **Store:** Ghi kết quả từ Register ngược lại RAM/Ngoại vi (`STR`).

---

### 1.4 Real-World — Liên Hệ Thực Tế Trong Dự Án `Study_AUTOSAR`
Khi khởi chạy mô phỏng board `lm3s6965evb` trên QEMU trong dự án `Study_AUTOSAR`:
- Vùng **Flash** bắt đầu tại `0x00000000`: Chứa Vector Table, mã máy của AUTOSAR OS (`askar`) và MCAL drivers.
- Vùng **SRAM** bắt đầu tại `0x20000000`: Chứa biến toàn cục, task stack của `TaskIdle`, và OS control structures.
- Vùng **Peripherals** tại `0x40000000`: Chứa thanh ghi của UART0 (`0x4000C000`) và CAN0 Controller (`0x40040000`).

> 💥 **Bài học từ Bug Target `stm32f107vc` trên QEMU:**  
> Khi chạy target `stm32f107vc`, hàm `Can_Init()` ghi vào thanh ghi `0x40006400` (`CAN1_BASE`). Vì QEMU model `stm32vldiscovery` không có mạch CAN phần cứng tại địa chỉ này, Bus Interface báo lỗi truy cập ô nhớ không tồn tại $
ightarrow$ CPU kích hoạt BusFault/HardFault ngay lập tức! Chuyển sang `lm3s6965evb` giải quyết được vấn đề vì QEMU có phần cứng CAN ảo tại `0x40040000`.

---

### 1.5 Code — Ví Dụ Cơ Sở Xuyên Suốt
```c
/* File: math_utils.c */
int add(int a, int b)
{
    return a + b;
}
```

---

### 1.6 Assembly — Mã Máy Tương Ứng Trên Cortex-M
```assembly
/* Biên dịch với arm-none-eabi-gcc -O2 -mcpu=cortex-m3 -mthumb */
add:
    ADD    r0, r0, r1    /* r0 = r0 + r1 */
    BX     lr            /* Quay về hàm gọi bằng địa chỉ trong Link Register */
```

---

### 1.7 Debug — Quan Sát CPU Hoạt Động Trong GDB
Khi dừng tại hàm `add`:
```text
(gdb) info registers
r0             0x5                 5        <-- Tham số a
r1             0xa                 10       <-- Tham số b
r2             0x20000100          536871168
r3             0x0                 0
pc             0x00000450          0x450 <add>
lr             0x00000483          0x483 <main+22>
(gdb) stepi
(gdb) info registers r0
r0             0xf                 15       <-- Kết quả a + b = 15 nằm tại r0
```

---

### 1.8 ❌ Common Mistakes Của Kỹ Sư Junior
1. **Hiểu nhầm:** Nghĩ rằng biến trong C luôn được CPU đọc/ghi trực tiếp vào RAM mỗi khi có lệnh gán.
   * *Thực tế:* Trình biên dịch luôn ưu tiên giữ biến trên Register để tăng tốc. Chỉ khi hết thanh ghi hoặc có từ khóa `volatile`, dữ liệu mới được đẩy ra SRAM.
2. **Hiểu nhầm:** Tưởng rằng thanh ghi ngoại vi (UART, CAN) là bộ nhớ thông thường.
   * *Thực tế:* Thanh ghi ngoại vi gắn liền với mạch logic phần cứng. Đọc hoặc ghi có thể làm thay đổi trạng thái phần cứng (ví dụ: đọc thanh ghi nhận dữ liệu sẽ tự động xóa cờ báo có dữ liệu).

---

### 1.9 📌 Remember (Điểm Cốt Lõi)
1. CPU chỉ tính toán được trên **Register File**, không tính trực tiếp trên RAM.
2. Mọi truy cập bộ nhớ đều qua Bus thông qua 2 thao tác cơ bản: **Load (`LDR`)** và **Store (`STR`)**.
3. Truy cập địa chỉ bộ nhớ không tồn tại sẽ bị Bus Interface chặn và gây lỗi **Hardware Fault**.

---

### 1.10 🔬 Advanced — Chưa Cần Học Sâu
* *Pipeline Stages:* Cortex-M3/M4 sử dụng pipeline 3 giai đoạn (Fetch, Decode, Execute). Cortex-M7 dùng superscalar 6 giai đoạn. Chưa cần học chi tiết cơ chế branch prediction và hazard mitigation ở giai đoạn này.

---

## CHƯƠNG 2: REGISTER MODEL CỦA ARM CORTEX-M

### 2.1 Why — Tại Sao Cần Nắm Vững Tập Thanh Ghi?
Khi xem disassembly, đọc call-stack bị crash, hoặc cấu hình RTOS task, bạn sẽ thấy hàng loạt ký hiệu `r0`, `r1`, `sp`, `lr`, `pc`. Nếu không biết thanh ghi nào giữ dữ liệu gì, thanh ghi nào bị hàm con ghi đè, bạn không thể đọc hiểu log crash của vi điều khiển.

---

### 2.2 What — Bảng 16 Thanh Ghi Chuẩn Của ARM Cortex-M

Lõi Cortex-M có **16 thanh ghi lõi (Core Registers) 32-bit**, đánh số từ R0 đến R15, kèm thanh ghi trạng thái xPSR:

```
+=============================================================================+
|                      ARM CORTEX-M CORE REGISTERS (32-BIT)                   |
+=============================================================================+
| Register | Tên Gọi / Vai Trò         | Quy Ước AAPCS (Calling Convention)   |
|----------|---------------------------|--------------------------------------|
| **R0**   | General / Argument / Ret  | Tham số 1 / Giá trị trả về (Scratch) |
| **R1**   | General / Argument        | Tham số 2 (Caller-saved / Scratch)   |
| **R2**   | General / Argument        | Tham số 3 (Caller-saved / Scratch)   |
| **R3**   | General / Argument        | Tham số 4 (Caller-saved / Scratch)   |
|----------|---------------------------|--------------------------------------|
| **R4**   | General Purpose           | Biến cục bộ (Callee-saved / Preserve)|
| **R5**   | General Purpose           | Biến cục bộ (Callee-saved / Preserve)|
| **R6**   | General Purpose           | Biến cục bộ (Callee-saved / Preserve)|
| **R7**   | General Purpose           | Frame Pointer (GCC) / Callee-saved   |
| **R8**   | General Purpose           | Biến cục bộ (Callee-saved / Preserve)|
| **R9**   | General Purpose           | Biến cục bộ (Callee-saved / Preserve)|
| **R10**  | General Purpose           | Biến cục bộ (Callee-saved / Preserve)|
| **R11**  | General Purpose           | Frame Pointer (ARM CC) / Callee-saved|
|----------|---------------------------|--------------------------------------|
| **R12**  | IP (Intra-Procedure Call) | Thanh ghi tạm nội bộ (Scratch)       |
| **R13**  | **SP** (Stack Pointer)    | Con trỏ đỉnh Stack (MSP hoặc PSP)    |
| **R14**  | **LR** (Link Register)    | Địa chỉ trở về / EXC_RETURN          |
| **R15**  | **PC** (Program Counter)  | Địa chỉ lệnh đang thực thi           |
|----------|---------------------------|--------------------------------------|
| **xPSR** | Program Status Register   | Chứa cờ ALU (N,Z,C,V) & Exception #  |
+=============================================================================+
```

---

### 2.3 How — Quy Ước Phân Chia Trách Nhiệm AAPCS
Theo chuẩn giao tiếp hàm ARM (**AAPCS — ARM Architecture Procedure Call Standard**):

```
                       QUY ƯỚC QUẢN LÝ THANH GHI
          ┌─────────────────────────────────────────────────┐
          │                                                 │
          ▼                                                 ▼
   CALLER-SAVED REGISTERS                        CALLEE-SAVED REGISTERS
     {R0, R1, R2, R3, R12}                           {R4 - R11}
          │                                                 │
  • Còn gọi là Scratch Registers.                • Còn gọi là Preserved Registers.
  • Hàm bị gọi (Callee) ĐƯỢC PHÉP                • Hàm bị gọi (Callee) NẾU DÙNG
    ghi đè tùy ý.                                  BẮT BUỘC PHẢI LƯU (PUSH) và
  • Hàm gọi (Caller) muốn giữ                      khôi phục (POP) nguyên vẹn
    phải tự cất vào Stack.                         trước khi return!
```

---

### 2.4 Real-World — Ứng Dụng Trong AUTOSAR OS Context Switching
Trong AUTOSAR OS (`askar`), khi hệ điều hành chuyển đổi ngữ cảnh từ `Task_A` sang `Task_B`:
- Khi xảy ra ngắt ngắt quãng (như SysTick), phần cứng ARM tự động PUSH nhóm **Caller-saved** `{R0-R3, R12, LR, PC, xPSR}` vào Stack.
- Hệ điều hành chỉ cần viết vài dòng Assembly ngắn để PUSH nốt nhóm **Callee-saved** `{R4-R11}`.
- Nhờ sự phân chia này, thời gian chuyển đổi Task trong AUTOSAR đạt tốc độ tối đa, tiết kiệm chu kỳ xung nhịp CPU.

---

### 2.5 Code & 2.6 Assembly — Minh Họa Caller vs Callee Saved
```c
int helper(int val);

int compute(int x)
{
    int saved_var = x * 3;     /* Cần giữ giá trị này */
    int res = helper(x);       /* Gọi hàm con */
    return res + saved_var;    /* Sử dụng lại saved_var */
}
```

Disassembly sinh ra từ trình biên dịch:
```assembly
compute:
    PUSH   {r4, lr}            /* [BẮT BUỘC] Lưu r4 (callee-saved) và lr */
    ADD    r4, r0, r0, LSL #1  /* r4 = r0 + r0*2 = x*3 (Lưu vào r4 an toàn) */
    BL     helper              /* Gọi helper(x). helper thoải mái dùng r0-r3, r12 */
    ADD    r0, r0, r4          /* r0 = res (từ helper) + saved_var (từ r4) */
    POP    {r4, pc}            /* [BẮT BUỘC] Khôi phục r4 cũ và nhảy về caller */
```

---

### 2.7 Debug — Quan Sát Preserved Registers Bị Lỗi
Nếu một hàm hợp ngữ (inline assembly) tự ý ghi đè vào `R4` mà không PUSH/POP:
```text
(gdb) break compute
(gdb) continue
(gdb) print $r4
$1 = 0x12345678    <-- Giá trị của hàm bên ngoài đang tin tưởng giữ trong r4
(gdb) finish
(gdb) print $r4
$2 = 0x0000002A    <-- BỊ GHI ĐÈ! Khi quay về hàm cha, biến cục bộ bị sai lệch hoàn toàn!
```

---

### 2.8 ❌ Common Mistakes
* **Viết Inline Assembly tự do:** Dùng các thanh ghi R4–R11 trong khối `__asm__` nhưng quên khai báo trong danh sách "Clobber List", khiến GCC tưởng thanh ghi chưa bị đổi và dùng tiếp dữ liệu rác.

---

### 2.9 📌 Remember
1. **R0–R3, R12:** Thanh ghi tạm (Scratch) — Gọi hàm xong là có thể bị mất giá trị.
2. **R4–R11:** Thanh ghi bảo toàn (Preserved) — Giá trị được giữ nguyên vẹn trước và sau khi gọi hàm.
3. **SP, LR, PC:** 3 thanh ghi điều khiển đặc biệt quan trọng nhất hệ thống.

---

### 2.10 🔬 Advanced
* Các thanh ghi mở rộng FPU (S0–S31, FPSCR) trên Cortex-M4F/M7 có quy ước riêng: S0–S15 là scratch, S16–S31 là preserved.

---

## CHƯƠNG 3: R0–R3 — FUNCTION ARGUMENTS VÀ RETURN VALUE

### 3.1 Why — Nhìn R0–R3 Biết Ngay Hàm Đang Làm Gì
Khi debug không có source code hoặc code bị tối ưu hóa `-O2` làm biến trong C biến mất (`<optimized out>`), cách duy nhất để biết hàm nhận giá trị gì và trả về cái gì là kiểm tra **R0, R1, R2, R3**.

---

### 3.2 What — Quy Tắc Phân Bổ R0–R3
1. **Truyền tham số (Arguments Passing):**
   * Tham số thứ 1 $
ightarrow$ `R0`
   * Tham số thứ 2 $
ightarrow$ `R1`
   * Tham số thứ 3 $
ightarrow$ `R2`
   * Tham số thứ 4 $
ightarrow$ `R3`
   * Tham số thứ 5 trở đi $
ightarrow$ Đẩy lên **Stack**!
2. **Giá trị trả về (Return Value):**
   * Giá trị 32-bit (hoặc con trỏ) $
ightarrow$ Đặt trong `R0`.
   * Giá trị 64-bit (`uint64_t`) $
ightarrow$ Đặt trong cặp `R0` (32-bit thấp) và `R1` (32-bit cao).

---

### 3.3 How — Sơ Đồ Truyền Tham Số Và Trả Về

```
Hàm Gọi: result = add(5, 10);

[CALLER CONTEXT]
  1. Gán R0 = 5
  2. Gán R1 = 10
  3. Gọi lệnh: BL add ──────────┐
                                │ Nhảy đến hàm
                                ▼
                        [CALLEE: add()]
                          4. Đọc R0 (5) và R1 (10)
                          5. Tính toán: R0 = 5 + 10 = 15
                          6. Lệnh: BX LR ──────┐
                                               │ Trở về hàm gọi
                                               ▼
[CALLER CONTEXT TIẾP TỤC]
  7. Đọc giá trị trả về ngay tại R0!
```

---

### 3.4 Real-World — Giao Tiếp Driver MCAL Trong AUTOSAR
Xét hàm gửi bản tin CAN chuẩn AUTOSAR MCAL:
```c
Std_ReturnType Can_Write(Can_HwHandleType Hth, const Can_PduType* PduInfo);
```
Khi gọi hàm này trong module `CanIf` hoặc `Can_App`:
- `R0`: Chứa giá trị `Hth` (ví dụ `0x00000000` đại diện cho kênh CAN Controller 0).
- `R1`: Chứa con trỏ địa chỉ của struct `PduInfo` trong SRAM (ví dụ `0x20000240`).
- Khi hàm `Can_Write` kết thúc, `R0` sẽ chứa mã trạng thái: `0x00` (`E_OK`) hoặc `0x01` (`E_NOT_OK`).

---

### 3.5 Code — Hàm Nhận 5 Tham Số
```c
/* Ví dụ hàm vượt quá 4 thanh ghi */
int process_sensor_data(int id, int temp, int press, int humi, int battery)
{
    return id + temp + press + humi + battery;
}
```

---

### 3.6 Assembly — Xử Lý Tham Số Thứ 5 Bằng Stack
```assembly
process_sensor_data:
    ADD    r0, r0, r1       /* r0 = id + temp */
    ADD    r0, r0, r2       /* r0 += press */
    ADD    r0, r0, r3       /* r0 += humi */
    LDR    r1, [sp, #0]     /* [QUAN TRỌNG] Đọc tham số thứ 5 (battery) từ Stack! */
    ADD    r0, r0, r1       /* r0 += battery */
    BX     lr               /* Kết quả cuối cùng trả về trong r0 */
```

---

### 3.7 Debug — Kiểm Tra Tham Số MCAL Bằng GDB
```text
(gdb) break Can_Write
(gdb) continue
Breakpoint 1, Can_Write (Hth=0, PduInfo=0x20000240)
(gdb) info registers r0 r1
r0             0x0                 0            <-- Hth = 0
r1             0x20000240          536871488    <-- Địa chỉ PduInfo
(gdb) x/4xw $r1                                 <-- Soi dữ liệu trong struct Can_PduType
0x20000240:    0x00000123    0x00000008    0x20000260    0x00000000
               (CanId 0x123) (Length 8)     (SduDataPtr)
```

---

### 3.8 ❌ Common Mistakes
* **Truyền quá nhiều tham số:** Viết hàm nhận 6-8 tham số khiến CPU liên tục phải đọc/ghi Stack, làm giảm hiệu năng hệ thống thời gian thực.
* **Quy tắc Senior:** Nếu hàm cần hơn 4 tham số, hãy gom vào một `struct` và truyền duy nhất **con trỏ struct** qua `R0`.

---

### 3.9 📌 Remember
1. 4 tham số đầu tiên luôn nằm trong **R0, R1, R2, R3**.
2. Giá trị trả về luôn nằm trong **R0**.
3. Tham số thứ 5 trở đi bị đẩy lên **Stack** $
ightarrow$ Tốn chi phí truy cập bộ nhớ.

---

### 3.10 🔬 Advanced
* Nếu giá trị trả về là một struct lớn hơn 64-bit, Caller sẽ cấp phát một vùng nhớ tạm trên stack và truyền địa chỉ vùng nhớ đó vào `R0` ẩn trước khi gọi hàm.

---

## CHƯƠNG 4: R4–R12 — PRESERVED VÀ SCRATCH REGISTERS

### 4.1 Why — Hiểu Cách Trình Biên Dịch Tối Ưu Biến Cục Bộ
Khi hàm C của bạn có nhiều biến cục bộ (`int x, y, z;`), Compiler sẽ quyết định biến nào được nằm trên thanh ghi siêu tốc `R4–R11` và khi nào cần dùng `R12`.

---

### 4.2 What — Vai Trò Từng Thanh Ghi Từ R4 Đến R12
* **R4 đến R11 (Callee-Saved / Preserved):**
  * Dùng để lưu trữ các biến cục bộ sống lâu qua nhiều câu lệnh.
  * Nếu một hàm dùng đến `R4-R11`, hàm đó bắt buộc phải `PUSH` chúng vào stack ở đầu hàm (Prologue) và `POP` khôi phục ở cuối hàm (Epilogue).
* **R12 (IP — Intra-Procedure Call Scratch Register):**
  * Là thanh ghi tạm tự do. Trình biên dịch có thể dùng R12 làm vùng đệm trung gian khi tính toán số học hoặc khi tạo mã nhảy xa (Veneer Branching) của Linker.
  * Giá trị R12 không được đảm bảo giữ nguyên qua bất kỳ lời gọi hàm nào.

---

### 4.3 How — Cơ Chế Prologue Và Epilogue Trong Function Call

```
┌─────────────────────────────────────────────────────────────┐
│                 CẤU TRÚC HÀM TIÊU CHUẨN                     │
├─────────────────────────────────────────────────────────────┤
│ 1. PROLOGUE (Đầu hàm):                                      │
│    PUSH {r4, r5, lr}      <-- Cất các thanh ghi sẽ dùng     │
│    SUB  sp, sp, #8        <-- Cấp phát bộ nhớ cho biến local│
├─────────────────────────────────────────────────────────────┤
│ 2. FUNCTION BODY (Thân hàm):                                │
│    Thực hiện logic tính toán. Thoải mái dùng R0-R3, R12.    │
│    Các biến quan trọng cần giữ nguyên được nạp vào R4, R5.  │
├─────────────────────────────────────────────────────────────┤
│ 3. EPILOGUE (Cuối hàm):                                     │
│    ADD  sp, sp, #8        <-- Thu hồi bộ nhớ biến local     │
│    POP  {r4, r5, pc}      <-- Khôi phục R4, R5 và return!   │
└─────────────────────────────────────────────────────────────┘
```

---

### 4.4 Real-World — Lưu Ngữ Cảnh Task Trong AUTOSAR OS
Khi AUTOSAR OS kích hoạt ngắt `PendSV_Handler` để chuyển Task:
```assembly
/* askar OS / FreeRTOS Context Save */
PendSV_Handler:
    MRS    r0, psp                 /* Lấy con trỏ stack của Task hiện tại */
    STMDB  r0!, {r4-r11}           /* Tự tay lưu R4-R11 vào Task Stack */
    LDR    r1, =Current_TCB        /* Lấy Task Control Block */
    LDR    r2, [r1]
    STR    r0, [r2]                /* Cập nhật đỉnh stack mới vào TCB */
    /* ... Chuyển sang Task mới ... */
    LDMIA  r0!, {r4-r11}           /* Khôi phục R4-R11 của Task mới */
    MSR    psp, r0                 /* Cập nhật lại PSP */
    BX     lr                      /* Thoát ngắt, phần cứng tự khôi phục R0-R3, R12, PC */
```

---

### 4.5 Code — Hàm Phức Tạp Sử Dụng Nhiều Biến
```c
int calculate_complex(int x)
{
    int factor1 = x * 2;
    int factor2 = x * 3;
    int temp = add(factor1, factor2);
    return temp + factor1;  /* factor1 cần sống sót qua lời gọi add() */
}
```

---

### 4.6 Assembly — Quan Sát R4 Lưu Trữ `factor1`
```assembly
calculate_complex:
    PUSH   {r4, lr}           /* Cất r4 vì sẽ dùng r4 lưu factor1 */
    LSL    r4, r0, #1         /* r4 = x * 2 (factor1) */
    ADD    r1, r4, r0         /* r1 = factor1 + x = x * 3 (factor2) */
    MOV    r0, r4             /* r0 = factor1 (chuẩn bị tham số 1 cho add) */
    BL     add                /* Gọi add(factor1, factor2). Kết quả trả về r0 */
    ADD    r0, r0, r4         /* r0 = temp + factor1 (r4 vẫn còn nguyên vẹn!) */
    POP    {r4, pc}           /* Khôi phục r4 và return */
```

---

### 4.7 Debug — Bắt Lỗi Mất Dữ Liệu Thanh Ghi R4
Khi debug hàm assembly tự viết, đặt Watchpoint để theo dõi xem R4 có bị hàm nào phá hoại:
```text
(gdb) watch $r4
Hardware watchpoint 2: $r4
(gdb) continue
Hardware watchpoint 2: $r4
Old value = 0x0000000a
New value = 0xdeadbeef    <-- Phát hiện một hàm con viết sai đã đè giá trị rác vào r4!
```

---

### 4.8 ❌ Common Mistakes
* **Tự ý dùng R4–R11 trong hàm ngắt (ISR) viết bằng Assembly:** Nếu viết ISR bằng Assembly mà không lưu `{r4-r11}`, bạn sẽ làm hỏng dữ liệu của bất kỳ Task nào đang chạy dở ở thời điểm ngắt kích hoạt!

---

### 4.9 📌 Remember
1. **R4–R11** là tài sản của hàm cha; hàm con muốn dùng thì phải mượn và trả lại nguyên vẹn (`PUSH/POP`).
2. **R12** là thanh ghi tạm tự do, không bao giờ được tin tưởng dữ liệu của nó sau khi gọi hàm khác.
3. Trong chuyển ngữ cảnh RTOS/AUTOSAR, lập trình viên phải chịu trách nhiệm lưu/khôi phục **R4–R11**.

---

### 4.10 🔬 Advanced
* Trong hệ điều hành Linux trên Cortex-A, `R7` hoặc `R11` thường cố định làm Frame Pointer để hỗ trợ stack unwinding khi debug core dump.

---

## CHƯƠNG 5: SP / R13 — STACK POINTER VÀ VÙNG NHỚ NGĂN XẾP

### 5.1 Why — 70% Lỗi Crash Xuất Phát Từ Stack
Stack Overflow (tràn ngăn xếp) và Stack Corruption (hỏng ngăn xếp) là hai nguyên nhân hàng đầu gây ra các lỗi HardFault bí ẩn trong các dự án nhúng ô tô AUTOSAR. Hiểu rõ thanh ghi SP là điều kiện tiên quyết để sống sót trong firmware debugging.

---

### 5.2 What — Ngăn Xếp (Stack) Là Gì?
* **Stack (Bộ nhớ ngăn xếp):** Vùng RAM được cấp phát để:
  1. Lưu trữ địa chỉ trả về của hàm (`LR`).
  2. Lưu trữ các thanh ghi cần bảo toàn (`R4–R11`).
  3. Cấp phát các biến cục bộ (Local Variables) và mảng trong hàm.
  4. Truyền các tham số thứ 5 trở đi.
* **SP (Stack Pointer — R13):** Thanh ghi 32-bit chứa địa chỉ của đỉnh ngăn xếp hiện tại.
* **Đặc tính ARM Cortex-M:** Là kiến trúc **Full-Descending Stack**:
  * Đỉnh stack ban đầu nằm ở địa chỉ cao nhất của RAM.
  * Khi lưu thêm dữ liệu (`PUSH`), địa chỉ trong SP **GIẢM DẦN**.
  * Khi rút dữ liệu ra (`POP`), địa chỉ trong SP **TĂNG DẦN**.

---

### 5.3 How — Cơ Chế Hoạt Động Của PUSH Và POP

```
BỘ NHỚ RAM:                     LỆNH: PUSH {R0}             LỆNH: POP {R0}
Địa chỉ cao                      (Lưu R0 xuống Stack)        (Rút từ Stack về R0)
┌──────────────┐                 ┌──────────────┐            ┌──────────────┐
│  Dữ liệu cũ  │                 │  Dữ liệu cũ  │            │  Dữ liệu cũ  │
├──────────────┤                 ├──────────────┤            ├──────────────┤
│              │ <-- SP ban đầu  │  Dữ liệu R0  │ <-- SP mới │              │ <-- SP phục hồi
├──────────────┤                 ├──────────────┤ (SP = SP-4)├──────────────┤
│              │                 │              │            │              │
Địa chỉ thấp
```

Thực chất trong phần cứng:
- `PUSH {r0}` tương đương với: `STR r0, [sp, #-4]!` (Giảm SP đi 4 bytes rồi ghi R0 vào).
- `POP {r0}` tương đương với: `LDR r0, [sp], #4` (Đọc giá trị tại SP vào R0 rồi tăng SP lên 4 bytes).

---

### 5.4 Real-World — Cấu Hình Task Stack Trong AUTOSAR OS
Trong file cấu hình hệ thống AUTOSAR (`os.oil` hoặc file cấu hình C):
```c
/* Định nghĩa Stack cho Task giám sát CAN trong AUTOSAR */
#define TASK_CAN_STACK_SIZE   256  /* 256 words = 1024 bytes */
uint32_t Task_Can_Stack[TASK_CAN_STACK_SIZE];

/* Đỉnh ban đầu của Stack (Full Descending): */
uint32_t* pTop = &Task_Can_Stack[TASK_CAN_STACK_SIZE - 1];
```
Nếu hàm xử lý gói tin CAN khai báo mảng tạm `uint8_t temp_buf[1200];`, dung lượng này vượt quá 1024 bytes $
ightarrow$ SP sẽ giảm xuống dưới đáy mảng `Task_Can_Stack` và ghi đè làm nát vùng nhớ của Task khác $
ightarrow$ Hệ thống crash ngẫu nhiên!

---

### 5.5 Code — Cấp Phát Biến Cục Bộ Trên Stack
```c
void demo_stack(void)
{
    int arr[4];
    arr[0] = 10;
    arr[1] = 20;
    /* arr nằm hoàn toàn trên stack */
}
```

---

### 5.6 Assembly — Compiler Cấp Phát Stack Frame
```assembly
demo_stack:
    SUB    sp, sp, #16        /* Cấp phát 16 bytes (4 phần tử int * 4 bytes) */
    MOVS   r0, #10
    STR    r0, [sp, #0]       /* arr[0] = 10 tại địa chỉ SP + 0 */
    MOVS   r0, #20
    STR    r0, [sp, #4]       /* arr[1] = 20 tại địa chỉ SP + 4 */
    ADD    sp, sp, #16        /* Thu hồi 16 bytes stack trước khi thoát */
    BX     lr
```

---

### 5.7 Debug — Kiểm Tra Stack Overflow Bằng Watermarking
Kỹ thuật cao cấp của Senior: Tô màu Stack bằng giá trị `0xA5A5A5A5` trước khi chạy:
```text
(gdb) x/16xw &Task_Can_Stack[0]
0x20000400:    0xa5a5a5a5    0xa5a5a5a5    0xa5a5a5a5    0xa5a5a5a5
0x20000410:    0xa5a5a5a5    0xa5a5a5a5    0x12345678    0x00000000
```
Nếu các ô nhớ đầu mảng (`0x20000400`) vẫn còn `0xa5a5a5a5`, nghĩa là Stack chưa chạm đáy (an toàn). Nếu các ô này bị ghi đè, hệ thống đã bị **Stack Overflow**!

---

### 5.8 ❌ Common Mistakes
* **Return con trỏ tới biến local:**
  ```c
  int* get_data(void) {
      int val = 100;
      return &val; /* CHẾT! Khi thoát hàm, SP tăng lên thu hồi bộ nhớ, con trỏ này thành rác */
  }
  ```
* **Khai báo buffer lớn trong hàm ngắt (ISR):** Làm tràn Main Stack Pointer (MSP).

---

### 5.9 📌 Remember
1. Stack phát triển **từ địa chỉ cao xuống địa chỉ thấp**.
2. Biến cục bộ trong hàm được cấp phát bằng lệnh `SUB sp, sp, #N`.
3. Dung lượng Stack có hạn, tuyệt đối không khai báo mảng lớn hoặc đệ quy sâu trong Embedded.

---

### 5.10 🔬 Advanced
* Quy tắc căn chỉnh AAPCS: Tại các biên gọi hàm công khai, giá trị của thanh ghi SP bắt buộc phải **chia hết cho 8** (8-byte aligned).

---

## CHƯƠNG 6: LR / R14 — LINK REGISTER VÀ FUNCTION CALL

### 6.1 Why — Bản Lề Của Kiểm Soát Luồng Thực Thi
Khi một hàm được gọi, làm sao CPU nhớ được vị trí ban đầu để quay lại sau khi thực hiện xong? Câu trả lời nằm ở thanh ghi **Link Register (LR — R14)**.

---

### 6.2 What — Vai Trò Kép Của LR
1. **Trong chế độ thường (Thread Mode):**
   * Giữ **địa chỉ trả về (Return Address)** của hàm gọi.
   * Lệnh `BL func` (Branch with Link) tự động nạp địa chỉ câu lệnh tiếp theo vào `LR`.
   * Lệnh `BX lr` nạp giá trị trong `LR` ngược lại vào `PC` để trở về.
2. **Trong chế độ ngắt (Handler Mode):**
   * Không chứa địa chỉ code thông thường! Thay vào đó, nó chứa mã ma thuật **`EXC_RETURN`** (ví dụ `0xFFFFFFF9`, `0xFFFFFFFD`) để điều khiển phần cứng phục hồi ngữ cảnh.

---

### 6.3 How — Luồng Hoạt Động Khi Gọi Hàm Lồng Nhau (Nested Calls)

```
main() { foo(); }
foo()  { bar(); }

[main]
  │
  ├─ 1. BL foo  ──────────> Nạp LR = địa chỉ lệnh sau BL trong main
  │                         Nhảy vào foo()
  │
  [foo]
    │
    ├─ 2. PUSH {lr}  ─────> [CỰC KỲ QUAN TRỌNG] Phải cất LR vào Stack!
    │                       Vì nếu gọi tiếp bar(), lệnh BL bar sẽ GHI ĐÈ mất LR!
    │
    ├─ 3. BL bar  ────────> Nạp LR = địa chỉ lệnh sau BL trong foo
    │                       Nhảy vào bar()
    │
    [bar]
      │
      └─ 4. BX lr  ───────> Nhảy về lại foo()
    │
    ├─ 5. POP {pc}  ──────> Rút địa chỉ cũ từ stack nạp thẳng vào PC!
  │                         Nhảy về lại main() thành công!
```

---

### 6.4 Real-World — Call-Stack Bị Phá Hỏng Trong Debug
Trong các dự án AUTOSAR, nếu một hàm copy chuỗi byte (như giải mã bản tin UDS chẩn đoán) bị tràn bộ đệm:
```c
void parse_uds(uint8_t* rx_data) {
    uint8_t buffer[8];
    memcpy(buffer, rx_data, 16); /* Tràn 8 bytes -> Ghi đè vào saved LR trên Stack! */
}
```
Khi hàm `parse_uds` thực hiện `POP {pc}`, CPU nạp giá trị rác từ `rx_data` vào `PC` $
ightarrow$ Nhảy thẳng vào vùng nhớ cấm gây **HardFault** ngay lập tức!

---

### 6.5 Code & 6.6 Assembly — Leaf Function vs Non-Leaf Function
1. **Leaf Function (Hàm lá — không gọi hàm nào khác):**
   ```c
   int square(int x) { return x * x; }
   ```
   ```assembly
   square:
       MUL    r0, r0, r0
       BX     lr          /* Không cần đụng vào Stack! Tiết kiệm tối đa thời gian */
   ```

2. **Non-Leaf Function (Hàm nhánh — có gọi hàm khác):**
   ```c
   int square_sum(int a, int b) { return square(a) + square(b); }
   ```
   ```assembly
   square_sum:
       PUSH   {r4, lr}    /* BẮT BUỘC lưu lr vào Stack */
       /* ... */
       POP    {r4, pc}    /* Khôi phục và thoát */
   ```

---

### 6.7 Debug — Đọc Call Stack (Backtrace) Bằng GDB
Debugger vẽ được cây gọi hàm (Call Stack) là nhờ dò theo các giá trị `LR` được lưu trữ trên Stack:
```text
(gdb) backtrace
#0  add (a=5, b=10) at math_utils.c:4
#1  0x00000486 in compute (x=5) at math_utils.c:12
#2  0x00000512 in Task_Can_Handler () at can_app.c:45
#3  0x00000820 in askar_task_entry () at portable.c:120
```

---

### 6.8 ❌ Common Mistakes
* **Viết hàm hợp ngữ không lưu LR:** Gọi `BL` trong một hàm con viết bằng assembly mà không PUSH `lr`, dẫn đến vòng lặp vô tận khi hàm con cố gắng thoát về chính nó.

---

### 6.9 📌 Remember
1. `BL` tự động lưu địa chỉ trả về vào **LR**.
2. Hàm có gọi hàm con (Non-leaf) bắt buộc phải **PUSH LR** ở đầu hàm.
3. Khi debug HardFault, nếu `LR = 0xFFFFFFFx`, bạn đang ở trong **Interrupt Handler**, không phải hàm thường!

---

### 6.10 🔬 Advanced
* Khái niệm ARM Security Extensions (TrustZone): LR còn hỗ trợ giá trị `FNC_RETURN` khi chuyển đổi giữa Secure và Non-Secure world trên ARMv8-M.

---

## CHƯƠNG 7: PC / R15 — PROGRAM COUNTER VÀ PROGRAM FLOW

### 7.1 Why — Kim Chỉ Nam Cho Mọi Lệnh Thực Thi
Nếu bạn muốn biết CPU đang đứng ở dòng code nào, instruction nào chuẩn bị chạy, hoặc tại sao CPU lại bị nhảy vào địa chỉ rác, **Program Counter (PC — R15)** là nơi duy nhất cho bạn câu trả lời.

---

### 7.2 What — Bản Chất Của Program Counter
* **PC (R15):** Thanh ghi 32-bit chứa địa chỉ bộ nhớ Flash/RAM của câu lệnh mà CPU đang nạp/thực thi.
* **Quy luật tự nhiên:** Sau mỗi câu lệnh, PC tự động tăng (+2 bytes với lệnh Thumb 16-bit, hoặc +4 bytes với lệnh Thumb-2 32-bit).
* **Đặc tính Thumb State (Bit 0):**
  * Trong kiến trúc ARM Cortex-M, mã máy luôn được căn chỉnh theo 2 bytes (địa chỉ chẵn). Do đó bit [0] của PC khi đang chạy luôn luôn là `0`.
  * Tuy nhiên, mọi con trỏ hàm (Function Pointer) trong bảng Vector Table hoặc biến con trỏ C bắt buộc phải có **Bit 0 = 1** để báo hiệu cho CPU biết đây là mã Thumb!

---

### 7.3 How — Các Lệnh Làm Thay Đổi Program Flow

```
LUỒNG TUẦN TỰ:
PC = 0x08000100 ──(Thực thi)──> PC = 0x08000104 ──(Thực thi)──> PC = 0x08000108

LUỒNG RẼ NHÁNH (BRANCH / JUMP):
1. Nhảy không điều kiện:
   B label             ---> PC = Địa chỉ label
2. Nhảy có điều kiện (If/Else):
   BEQ label           ---> Nếu cờ Zero=1: PC = Địa chỉ label. Ngược lại: PC tăng bình thường.
3. Lời gọi hàm:
   BL function         ---> LR = PC + 4, PC = Địa chỉ function
4. Thoát hàm / Nhảy qua con trỏ:
   BX Rm               ---> PC = Rm (Bit 0 của Rm nạp vào cờ Thumb state)
```

---

### 7.4 Real-World — Lỗi Mất Thumb Bit Trong Bootloader Nhảy Vào App
Trong các dự án AUTOSAR, khi Bootloader kiểm tra tính hợp lệ và nhảy vào Application:
```c
typedef void (*AppResetHandler_t)(void);

void jump_to_application(uint32_t app_vector_addr) {
    /* Đọc địa chỉ Reset_Handler của App tại ô nhớ thứ 2 (Vector Address + 4) */
    uint32_t app_entry = *(volatile uint32_t*)(app_vector_addr + 4);
    
    /* NẾU app_entry LÀ SỐ CHẴN (MẤT BIT 0) -> CPU SẼ CRASH NGAY LẬP TỨC! */
    AppResetHandler_t pApp = (AppResetHandler_t)app_entry;
    pApp(); /* Nạp giá trị này vào PC qua lệnh BX */
}
```
Nếu `app_entry` bị mất bit 0 (ví dụ `0x00010000` thay vì `0x00010001`), lệnh `BX` sẽ xóa cờ Thumb trong xPSR $
ightarrow$ CPU kích hoạt lỗi **UsageFault (INVSTATE)** ngay lập tức!

---

### 7.5 Code — Cấu Trúc Rẽ Nhánh
```c
int check_limit(int val)
{
    if (val > 100) {
        return 100;
    }
    return val;
}
```

---

### 7.6 Assembly — Dịch Sang Lệnh So Sánh Và Nhảy
```assembly
check_limit:
    CMP    r0, #100            /* So sánh val với 100 (Cập nhật cờ) */
    BLE    .L_return           /* Nếu val <= 100: Nhảy tới .L_return (PC = .L_return) */
    MOVS   r0, #100            /* Nếu val > 100: r0 = 100 */
.L_return:
    BX     lr                  /* Trở về */
```

---

### 7.7 Debug — Sự Khác Nhau Giữa PC Trong Debugger Và Phần Cứng
> ⚠️ **[SIMPLIFICATION CẦN BIẾT]:**  
> Khi bạn xem lệnh `print $pc` trong GDB, GDB hiển thị địa chỉ của lệnh đang dừng.  
> Tuy nhiên, ở cấp phần cứng bên trong lõi CPU, do kiến trúc **Pipeline 3 giai đoạn (Fetch - Decode - Execute)**, thanh ghi PC thực tế đang trỏ tới lệnh **ở phía trước 2 chu kỳ (PC + 4 bytes)**. Trình biên dịch và Debugger đã tự động trừ đi độ lệch này để hiển thị đúng cho lập trình viên.

---

### 7.8 ❌ Common Mistakes
* **Gán con trỏ hàm bằng địa chỉ chẵn:** Tự ép kiểu một địa chỉ số nguyên cứng thành con trỏ hàm mà quên đảm bảo số đó là số lẻ (có bit 0 = 1).
* **Tưởng PC tăng cố định 4 bytes:** Trong tập lệnh Thumb-2 của Cortex-M, có lệnh chiếm 2 bytes, có lệnh chiếm 4 bytes.

---

### 7.9 📌 Remember
1. **PC** trỏ tới lệnh đang được xử lý.
2. Mọi cấu trúc `if`, `while`, gọi hàm bản chất là các lệnh thay đổi giá trị của **PC**.
3. Con trỏ hàm trong Cortex-M bắt buộc phải có **Bit 0 = 1 (Thumb Bit)**.

---

### 7.10 🔬 Advanced
* Kỹ thuật ROP (Return-Oriented Programming): Kẻ tấn công ghi đè Stack để ép PC nhảy liên tục vào các đoạn code nhỏ (gadgets) để chiếm quyền điều khiển vi điều khiển.

---

## CHƯƠNG 8: xPSR — PROGRAM STATUS REGISTER VÀ FLAGS

### 8.1 Why — Trái Tim Của Mọi Quyết Định Logic
Làm sao CPU biết `a > b` hay `a == b`? Làm sao hệ điều hành biết CPU đang chạy ở ngắt số mấy? Mọi thông tin trạng thái này được nén chặt vào một thanh ghi 32-bit duy nhất: **xPSR (Program Status Register)**.

---

### 8.2 What — Cấu Trúc 3 Trong 1 Của xPSR
Thanh ghi xPSR thực chất là sự kết hợp của 3 thanh ghi trạng thái:
1. **APSR (Application PSR):** Chứa các cờ trạng thái số học (ALU condition flags).
2. **IPSR (Interrupt PSR):** Chứa số thứ tự ngoại lệ (Exception Number) đang hoạt động.
3. **EPSR (Execution PSR):** Chứa trạng thái thực thi (cờ Thumb state).

```
CẤU TRÚC 32-BIT CỦA THANH GHI xPSR:

 31  30  29  28  27          24           15               8 7           0
┌───┬───┬───┬───┬───┬──────────┬───┬───────────┬───────────────┬─────────────┐
│ N │ Z │ C │ V │ Q │ Reserved │ T │ Reserved  │ ICI / IT bits │  ISR_NUMBER │
└───┴───┴───┴───┴───┴──────────┴───┴───────────┴───────────────┴─────────────┘
  ◄──── APSR ─────►              ▲               ◄─── EPSR ───►  ◄── IPSR ──►
                                 │
                               EPSR.T (Thumb Bit: Luôn = 1 trên Cortex-M)
```

**Chi tiết các cờ APSR (Bits [31:28]):**
* **N (Negative - Bit 31):** Bằng `1` nếu kết quả phép toán là số âm (bit cao nhất = 1).
* **Z (Zero - Bit 30):** Bằng `1` nếu kết quả phép toán bằng đúng `0`.
* **C (Carry - Bit 29):** Bằng `1` nếu phép cộng bị tràn số không dấu (overflow carry) hoặc phép trừ không cần mượn.
* **V (Overflow - Bit 28):** Bằng `1` nếu phép toán số có dấu bị tràn vượt quá giới hạn 32-bit có dấu.

**Chi tiết IPSR (Bits [8:0] — Exception Number):**
* `0`: CPU đang chạy ở **Thread Mode** (chương trình chính, các task của AUTOSAR OS).
* `15`: CPU đang chạy trong ngắt **SysTick_Handler**.
* `16+`: CPU đang chạy trong ngắt ngoại vi phần cứng (ví dụ `16 + 28 = 44` là TIM2).

---

### 8.3 How — Quy Trình: Lệnh Trước Set Flag $
ightarrow$ Lệnh Sau So Sánh

```
LỆNH 1: CMP R0, R1
(CPU thực hiện phép trừ ngầm: R0 - R1, KHÔNG LƯU kết quả, CHỈ CẬP NHẬT FLAGS)
        │
        ├── Nếu R0 == R1 ──> Kết quả = 0 ──> Bật cờ Z = 1
        └── Nếu R0 != R1 ──> Kết quả != 0 ─> Xóa cờ Z = 0
        │
        ▼
LỆNH 2: BEQ target_address
(Lệnh rẽ nhánh kiểm tra cờ Z trong xPSR)
        │
        ├── Nếu Z == 1 ──> NHẢY: PC = target_address
        └── Nếu Z == 0 ──> KHÔNG NHẢY: Chạy tiếp lệnh kế tiếp
```

---

### 8.4 Real-World — Kiểm Tra Ngữ Cảnh Trong AUTOSAR OS
Trong AUTOSAR OS, một số API (như gửi tin nhắn qua Queue, giải phóng tài nguyên) chỉ được phép gọi từ **Task (Thread Mode)**, tuyệt đối không được gọi từ **ISR (Handler Mode)**.
Hệ điều hành kiểm tra việc này bằng cách đọc trường IPSR:
```c
/* Kiểm tra xem code có đang nằm trong Interrupt Handler không */
bool Is_In_Interrupt_Context(void)
{
    uint32_t ipsr_val;
    __asm__ volatile ("MRS %0, ipsr" : "=r" (ipsr_val));
    return (ipsr_val != 0); /* != 0 nghĩa là đang trong ISR! */
}
```

---

### 8.5 Code — Kiểm Tra Trạng Thái Cờ
```c
int is_zero(int val)
{
    if (val == 0) {
        return 1;
    }
    return 0;
}
```

---

### 8.6 Assembly — Minh Họa Cờ Z Hoạt Động
```assembly
is_zero:
    CMP    r0, #0              /* Lấy r0 - 0. Nếu r0 = 0 -> Set Z = 1 */
    BNE    .L_not_zero         /* Kiểm tra cờ Z. Nếu Z = 0 (val != 0) -> Nhảy */
    MOVS   r0, #1              /* Nếu Z = 1 (val == 0) -> r0 = 1 */
    BX     lr
.L_not_zero:
    MOVS   r0, #0              /* r0 = 0 */
    BX     lr
```

---

### 8.7 Debug — Đọc xPSR Để Chẩn Đoán Khi Treo Hệ Thống
Khi vi điều khiển bị crash hoặc dừng breakpoint, xem xPSR để biết CPU đang ở đâu:
```text
(gdb) print/x $xpsr
$1 = 0x6100000f
```
**Phân tích ngay lập tức:**
1. Byte cao `0x61` = nhị phân `0110 0001`:
   * Cờ `N = 0`, cờ `Z = 1` (kết quả phép tính trước đó bằng 0).
   * Cờ `C = 1`.
   * Cờ `T = 1` (bit 24: đang chạy Thumb code chuẩn xác).
2. 9 bits thấp `0x00f` = `15`:
   * CPU đang nằm trong **SysTick Exception (Exception #15)**!

---

### 8.8 ❌ Common Mistakes
* **Nghĩ rằng mọi lệnh toán học đều cập nhật cờ:**  
  Trong tập lệnh ARM Thumb-2, lệnh `ADD r0, r1` **KHÔNG** cập nhật cờ xPSR! Chỉ có lệnh có hậu tố `S` như `ADDS r0, r1` hoặc lệnh so sánh `CMP`, `TST` mới cập nhật cờ.

---

### 8.9 📌 Remember
1. **APSR [31:28]** chứa 4 cờ số học sống còn: **N, Z, C, V**.
2. **IPSR [8:0]** cho biết mã số ngắt đang thực thi (bằng 0 nghĩa là đang chạy code thường).
3. **EPSR.T (Bit 24)** bắt buộc luôn bằng `1` trên Cortex-M.

---

### 8.10 🔬 Advanced
* Khối lệnh IT (If-Then block): Cho phép thực thi có điều kiện tối đa 4 câu lệnh liên tiếp mà không cần lệnh nhảy branch, tối ưu hóa pipeline triệt để.

---

---

# PHẦN 2: THỰC THI LỆNH, BỘ NHỚ VÀ NGẮT

---
## CHƯƠNG 9: MSP VÀ PSP — HAI STACK POINTER

---

### 1. Why?

Cortex-M có **hai stack pointer** — điều này không phải ngẫu nhiên. Hãy nghĩ về câu hỏi sau:

> *"Nếu một RTOS task bị crash và làm hỏng stack, liệu kernel có còn hoạt động được không?"*

Nếu chỉ có **một** stack pointer dùng chung cho cả task lẫn kernel/ISR, thì câu trả lời là **không**. Stack của kernel và task lẫn vào nhau — một lỗi trong task có thể corrupt stack của kernel và làm cả hệ thống sụp đổ.

ARM giải quyết vấn đề này bằng cách thiết kế **hai stack pointer hoàn toàn độc lập**:

```
Không có MSP/PSP (giả sử):          Có MSP/PSP:
┌──────────────────────┐             ┌────────────┐  ┌────────────┐
│  Stack chung duy nhất│             │  MSP Stack │  │  PSP Stack │
│  ┌──────────────────┐│             │  (Kernel + │  │  (Task A,  │
│  │ Kernel data      ││             │   ISR)     │  │   Task B)  │
│  │ ISR data         ││             └────────────┘  └────────────┘
│  │ Task A data      ││                  ↑                ↑
│  │ Task B data      ││              Độc lập!         Độc lập!
│  └──────────────────┘│
│  ← Task lỗi → corrupt│
└──────────────────────┘
       Nguy hiểm!                        An toàn!
```

### 2. What?

**MSP – Main Stack Pointer** (`R13` khi ở Handler Mode hoặc khi CONTROL.SPSEL=0):
- Dùng bởi: Handler Mode (ISR, fault handler, SVC, PendSV)
- Reset vector luôn nạp địa chỉ khởi tạo vào MSP
- Giá trị mặc định sau reset: lấy từ địa chỉ `0x00000000` (đầu vector table)

**PSP – Process Stack Pointer** (`R13` khi ở Thread Mode với CONTROL.SPSEL=1):
- Dùng bởi: RTOS tasks, user-mode threads
- Mặc định không được kích hoạt — phải enable thủ công
- Mỗi RTOS task có **PSP riêng** → task switching = đổi PSP

```
Register file trong CPU (simplified):
┌─────────────────────────────────────────┐
│ R0, R1, R2, R3, R4, R5, R6, R7         │
│ R8, R9, R10, R11, R12                   │
│                                         │
│ R13 (SP) ──────────────┐                │
│                         ▼               │
│              ┌─────────────────────┐    │
│              │  CONTROL.SPSEL = 0  │    │
│              │  → MSP được dùng    │    │
│              ├─────────────────────┤    │
│              │  CONTROL.SPSEL = 1  │    │
│              │  → PSP được dùng    │    │
│              └─────────────────────┘    │
│                                         │
│ R14 (LR)                                │
│ R15 (PC)                                │
│ xPSR                                    │
└─────────────────────────────────────────┘
```

**Register CONTROL** (đặc biệt quan trọng):
```
Bit[1]: SPSEL
  0 = dùng MSP (Thread Mode dùng MSP)
  1 = dùng PSP (Thread Mode dùng PSP)

Bit[0]: nPRIV (Cortex-M3/M4)
  0 = Privileged Thread Mode
  1 = Unprivileged Thread Mode
```

### 3. How?

**CPU quyết định dùng MSP hay PSP như thế nào?**

```
CPU đang thực thi...
         │
    ┌────▼────┐
    │Handler  │ → Luôn dùng MSP (bất kể CONTROL.SPSEL)
    │  Mode   │
    └─────────┘
         │
    ┌────▼────┐
    │Thread   │ → CONTROL[1] == 0? → Dùng MSP
    │  Mode   │   CONTROL[1] == 1? → Dùng PSP
    └─────────┘
```

**Flow trong RTOS khi task switching:**

```
                     FreeRTOS Task Switch Flow
                     ─────────────────────────
RTOS Tick ISR           Kernel (Handler Mode)        Task Code (Thread Mode)
     │                        │                             │
     │  PendSV triggered       │                             │
     │────────────────────────>│                             │
     │                        │ 1. Lưu R4-R11 vào PSP       │
     │                        │    của task hiện tại        │
     │                        │                             │
     │                        │ 2. Lưu PSP → TCB            │
     │                        │    (Task Control Block)     │
     │                        │                             │
     │                        │ 3. Chọn task mới            │
     │                        │                             │
     │                        │ 4. Load PSP từ TCB mới      │
     │                        │                             │
     │                        │ 5. Restore R4-R11 từ PSP    │
     │                        │                             │
     │                        │ 6. BX LR (EXC_RETURN)       │
     │                        │    → CPU dùng PSP           │
     │                        │    → Thread Mode            │
     │                        │                             │
     │                        │─────────────────────────────>
     │                        │    Task mới tiếp tục chạy   │
```

### 4. Real-world

**Scenario thực tế: FreeRTOS**

Khi bạn chạy FreeRTOS trên STM32:
1. **Startup** (`main()`): CPU chạy Thread Mode, MSP đang được dùng (SPSEL=0)
2. **`vTaskStartScheduler()`**: Kernel setup PSP, gọi `portENABLE_FPU()`, sau đó switch sang PSP
3. **Mỗi task**: Chạy ở Thread Mode với PSP trỏ vào stack riêng của task đó
4. **PendSV / SysTick ISR**: Tự động switch sang MSP (Handler Mode)

```
Memory layout khi FreeRTOS chạy:
┌──────────────────────────────────────┐
│          RAM (0x20000000)            │
├──────────────────────────────────────┤
│  Task A Stack (4KB)   ← PSP Task A  │
├──────────────────────────────────────┤
│  Task B Stack (4KB)   ← PSP Task B  │
├──────────────────────────────────────┤
│  Task C Stack (4KB)   ← PSP Task C  │
├──────────────────────────────────────┤
│  Main/Kernel Stack    ← MSP         │
│  (ISR stack)                         │
├──────────────────────────────────────┤
│  .bss, .data, heap                   │
└──────────────────────────────────────┘
```

**Khi task A bị stack overflow**: PSP của Task A bị corrupt, nhưng MSP và PSP của các task khác **không bị ảnh hưởng**. Stack overflow detection của FreeRTOS (`configCHECK_FOR_STACK_OVERFLOW`) có thể phát hiện và xử lý.

### 5. Code

**Đọc/ghi MSP và PSP bằng CMSIS:**

```c
#include "cmsis_gcc.h"   // hoặc core_cm4.h

// Đọc MSP hiện tại
uint32_t msp_val = __get_MSP();

// Đọc PSP hiện tại
uint32_t psp_val = __get_PSP();

// Set PSP (thường dùng khi khởi tạo task đầu tiên)
__set_PSP(new_psp_value);

// Switch sang dùng PSP (trong Thread Mode)
// Cách 1: dùng CMSIS
__set_CONTROL(__get_CONTROL() | 0x02); // Set SPSEL=1
__ISB(); // Instruction Synchronization Barrier - quan trọng!

// Cách 2: dùng Assembly trực tiếp
__asm volatile (
    "MRS R0, CONTROL  \n"   // Đọc CONTROL vào R0
    "ORR R0, R0, #2   \n"   // Set bit 1 (SPSEL)
    "MSR CONTROL, R0  \n"   // Ghi lại vào CONTROL
    "ISB              \n"   // Flush pipeline
);
```

**Khởi tạo PSP cho task đầu tiên (FreeRTOS style):**

```c
// Giả lập setup stack frame cho task mới
void create_task_stack(uint32_t *stack_top, void (*task_func)(void))
{
    // Stack frame mà hardware sẽ pop khi EXC_RETURN
    // (xem Chương 15 để hiểu chi tiết)
    *(--stack_top) = 0x01000000;        // xPSR: Thumb state
    *(--stack_top) = (uint32_t)task_func; // PC
    *(--stack_top) = 0xFFFFFFFD;        // LR: EXC_RETURN (Thread, PSP)
    *(--stack_top) = 0x12121212;        // R12
    *(--stack_top) = 0x03030303;        // R3
    *(--stack_top) = 0x02020202;        // R2
    *(--stack_top) = 0x01010101;        // R1
    *(--stack_top) = 0x00000000;        // R0

    // stack_top bây giờ là PSP để load cho task này
    __set_PSP((uint32_t)stack_top);
}
```

**Kiểm tra đang dùng MSP hay PSP (debug utility):**

```c
typedef enum {
    STACK_USING_MSP = 0,
    STACK_USING_PSP = 1
} StackType_t;

StackType_t get_current_stack_type(void)
{
    return (StackType_t)((__get_CONTROL() >> 1) & 0x01);
}

void print_stack_info(void)
{
    printf("MSP = 0x%08X\n", __get_MSP());
    printf("PSP = 0x%08X\n", __get_PSP());
    printf("Using: %s\n",
           get_current_stack_type() == STACK_USING_PSP ? "PSP" : "MSP");
    printf("CONTROL = 0x%08X\n", __get_CONTROL());
}
```

### 6. Assembly

**Assembly khi kernel switch task (FreeRTOS PendSV handler — ARM Cortex-M4):**

```asm
; File: port.c / portasm.s (FreeRTOS)
; PendSV_Handler — đây là nơi context switch xảy ra

PendSV_Handler:
    ; 1. Disable interrupts tạm thời
    CPSID   I                   ; Disable interrupts

    ; 2. Lấy PSP của task hiện tại
    MRS     R0, PSP             ; R0 = PSP (stack pointer của task đang chạy)
    ISB                         ; Instruction sync barrier

    ; 3. Lưu R4-R11 vào stack của task (hardware đã lưu R0-R3,R12,LR,PC,xPSR)
    STMDB   R0!, {R4-R11}       ; Push R4-R11 xuống PSP stack
    ; R0 bây giờ trỏ vào đỉnh stack của task (bao gồm cả R4-R11)

    ; 4. Lưu PSP mới vào TCB của task hiện tại
    LDR     R3, =pxCurrentTCB   ; Load địa chỉ pointer đến TCB
    LDR     R2, [R3]            ; R2 = con trỏ đến TCB hiện tại
    STR     R0, [R2]            ; Lưu PSP vào đầu TCB

    ; 5. Chọn task tiếp theo (gọi C function)
    PUSH    {R3, R14}           ; Lưu LR (EXC_RETURN)
    BL      vTaskSwitchContext  ; Kernel chọn task mới, cập nhật pxCurrentTCB
    POP     {R3, R14}           ; Restore R3, LR

    ; 6. Load PSP của task mới
    LDR     R1, [R3]            ; R1 = TCB của task mới
    LDR     R0, [R1]            ; R0 = PSP của task mới (đầu TCB)

    ; 7. Restore R4-R11 từ stack của task mới
    LDMIA   R0!, {R4-R11}       ; Pop R4-R11, R0 tự tăng

    ; 8. Cập nhật PSP và return
    MSR     PSP, R0             ; Set PSP = đỉnh stack task mới
    ISB
    CPSIE   I                   ; Enable interrupts
    BX      R14                 ; Return (EXC_RETURN) → hardware pop R0-R3,R12,PC,xPSR
```

### 7. Debug

**Debug scenario: "Task stack bị corrupt"**

Trong debugger (Ozone / GDB), khi bạn gặp HardFault:

```
Debugger output:
  PC  = 0xDEADBEEF  ← PC trỏ vào địa chỉ không hợp lệ!
  SP  = 0x20001234  ← SP này là MSP hay PSP?
  LR  = 0xFFFFFFFD  ← EXC_RETURN: thread mode, PSP
```

**Cách xác định stack nào đang được dùng:**
```
LR = 0xFFFFFFFD → Trước khi exception: Thread Mode, dùng PSP
LR = 0xFFFFFFF9 → Trước khi exception: Thread Mode, dùng MSP
LR = 0xFFFFFFF1 → Trước khi exception: Handler Mode, dùng MSP
```

**GDB commands để kiểm tra:**
```bash
(gdb) p/x $msp      # Xem MSP
(gdb) p/x $psp      # Xem PSP
(gdb) p/x $control  # Xem CONTROL register
# Nếu CONTROL[1] = 1 → đang dùng PSP
# Nhìn vào PSP để tìm stack frame của task bị lỗi
(gdb) x/16xw $psp   # Xem 16 words tại PSP
```

### 8. ❌ Common Mistakes

**Lỗi 1: Quên ISB sau khi ghi CONTROL**
```c
// SAI - có thể không hoạt động đúng ngay lập tức
__set_CONTROL(__get_CONTROL() | 0x02);
// Tiếp tục dùng SP ngay → có thể còn là MSP!

// ĐÚNG
__set_CONTROL(__get_CONTROL() | 0x02);
__ISB();  // Flush pipeline, đảm bảo CONTROL có hiệu lực
```

**Lỗi 2: Handler Mode vẫn cứ set PSP nhưng không có tác dụng**
```c
// ISR code - đây là Handler Mode
void SysTick_Handler(void) {
    __set_CONTROL(0x02); // Set SPSEL=1
    // KHÔNG CÓ TÁC DỤNG! Handler Mode LUÔN dùng MSP
    // SPSEL chỉ có ý nghĩa khi return về Thread Mode
}
```

**Lỗi 3: Không set PSP trước khi switch sang dùng PSP**
```c
// SAI: switch sang PSP khi PSP chưa được setup
__set_CONTROL(0x02); // PSP đang trỏ vào 0x00000000 → crash ngay!

// ĐÚNG: Set PSP hợp lệ TRƯỚC
__set_PSP(valid_stack_address);
__ISB();
__set_CONTROL(0x02);
__ISB();
```

### 9. 📌 Remember

> **MSP = Kernel/ISR stack** | **PSP = Task stack**

- Reset → MSP được dùng mặc định
- Handler Mode → luôn dùng MSP (không thể thay đổi)
- Thread Mode → CONTROL[1] quyết định MSP hay PSP
- `LR = 0xFFFFFFFD` trong ISR nghĩa là trước khi vào ISR, task đang dùng **PSP**
- Luôn gọi `__ISB()` sau khi thay đổi CONTROL
- Mỗi RTOS task có **PSP riêng** → đây là cơ sở của multitasking an toàn

### 10. 🔬 Advanced

**Stack limit registers (Cortex-M33 với TrustZone):**

Cortex-M33 có thêm `MSPLIM` và `PSPLIM` — thanh ghi giới hạn stack:
```c
// Set giới hạn dưới của MSP stack (Cortex-M33)
__set_MSPLIM(MSP_STACK_BOTTOM);

// Nếu MSP < MSPLIM → UsageFault (STKOF)
// Phát hiện stack overflow bằng hardware!
```

**FPU Context (Cortex-M4F/M7):**

Khi FPU được enable và task dùng floating-point:
```
CONTROL[2]: FPCA (Floating-Point Context Active)
  0 = Thread không dùng FP gần đây → không cần save FP regs
  1 = Thread đã dùng FP → hardware auto-save thêm S0-S15, FPSCR
```
→ Stack frame có thể là 8 words (không FP) hoặc 26 words (có FP).

---

## CHƯƠNG 10: CPU THỰC THI MỘT INSTRUCTION NHƯ THẾ NÀO

---

### 1. Why?

Bạn viết:
```c
int c = a + b;
```

Compiler dịch thành:
```asm
ADD R2, R0, R1
```

CPU thực thi dòng assembly này như thế nào? Nó không "đọc và hiểu" — nó là một cỗ máy điện tử thực thi qua các bước cố định. Hiểu được flow này giúp bạn:

- Biết tại sao **pipeline hazard** xảy ra
- Biết tại sao một lệnh **không phải ngay lập tức** có kết quả
- Hiểu được **timing** trong firmware critical sections
- Đọc được **disassembly** một cách tự tin

### 2. What?

**Fetch–Decode–Execute cycle** (hay còn gọi là FDE cycle hoặc instruction cycle):

```
┌─────────────────────────────────────────────────────────────┐
│                    Instruction Cycle                         │
│                                                             │
│   ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐ │
│   │  FETCH  │───>│ DECODE  │───>│ EXECUTE │───>│WRITEBACK│ │
│   └─────────┘    └─────────┘    └─────────┘    └─────────┘ │
│        │              │              │               │       │
│     PC→Mem        Instruction    ALU/Memory      Kết quả   │
│     đọc opcode    → Control      thực thi        → Register│
└─────────────────────────────────────────────────────────────┘
```

**4 giai đoạn cụ thể:**

| Giai đoạn | Tên đầy đủ | Làm gì |
|-----------|------------|--------|
| **F** | Fetch | Đọc instruction từ memory tại địa chỉ PC |
| **D** | Decode | Giải mã opcode → biết phải làm gì |
| **E** | Execute | ALU tính toán, Memory đọc/ghi |
| **W** | Writeback | Ghi kết quả vào register đích |

### 3. How?

**Trace chi tiết: `ADD R2, R0, R1`**

Giả sử:
- `PC = 0x08000100`
- `R0 = 5`, `R1 = 3`
- Machine code của `ADD R2, R0, R1` là `0x18420000` (ví dụ 32-bit Thumb-2)

---

**Bước 1 — FETCH:**
```
CPU State: PC = 0x08000100

    CPU Core              Flash Memory
    ┌──────────┐          ┌──────────────────────┐
    │          │          │ Address  | Data       │
    │  PC ─────┼─────────>│ 0x080100 | 0x18420000│  ← đọc instruction
    │ 0x08000100          │ 0x080104 | ...        │
    │          │<─────────┤ 0x080108 | ...        │
    │ IR ← 0x18420000     └──────────────────────┘
    └──────────┘

Sau FETCH:
  - IR (Instruction Register) = 0x18420000  ← nội dung instruction
  - PC tự động tăng: PC = 0x08000102 (Thumb: +2 hoặc +4)
```

**Bước 2 — DECODE:**
```
IR = 0x18420000 (Thumb-2 encoding)

    ┌─────────────────────────────────────┐
    │           DECODE UNIT               │
    │                                     │
    │  Opcode bits → Lookup table         │
    │                                     │
    │  "Đây là lệnh ADD"                  │
    │  "Toán hạng 1: R0 (nguồn 1)"        │
    │  "Toán hạng 2: R1 (nguồn 2)"        │
    │  "Đích: R2"                          │
    │  "Loại: Register-Register ADD"       │
    │  "Update flags? No (ADD không S)"   │
    └─────────────────────────────────────┘

Sau DECODE:
  - Control signals được set để điều khiển ALU
  - Register file được yêu cầu cung cấp R0 và R1
  - R0 = 5, R1 = 3 được đưa vào ALU input
```

**Bước 3 — EXECUTE:**
```
    ALU (Arithmetic Logic Unit)
    ┌─────────────────────────────────────┐
    │                                     │
    │  Input A ← R0 = 5  (0x00000005)    │
    │  Input B ← R1 = 3  (0x00000003)    │
    │                                     │
    │  Operation: ADD                     │
    │                                     │
    │  5 + 3 = 8                          │
    │                                     │
    │  Output = 0x00000008                │
    │                                     │
    │  Flags: N=0, Z=0, C=0, V=0         │
    │  (không update vì không có S suffix)│
    └─────────────────────────────────────┘
```

**Bước 4 — WRITEBACK:**
```
    Register File
    ┌──────────────────────────────────┐
    │  R0 = 0x00000005  (không đổi)   │
    │  R1 = 0x00000003  (không đổi)   │
    │  R2 ← 0x00000008  ← KẾT QUẢ!   │
    │  R3 = ...                        │
    │  ...                             │
    └──────────────────────────────────┘

Kết thúc! R2 = 8.
```

**Pipeline trong Cortex-M3/M4:**

Cortex-M3/M4 dùng **3-stage pipeline** (F → D → E), không phải 4-stage như trên. Writeback được tích hợp vào Execute stage. Điều này có nghĩa là:

```
Cycle:  1    2    3    4    5
Inst1:  F    D    E
Inst2:       F    D    E
Inst3:            F    D    E
Inst4:                 F    D    E
```

→ CPU thực thi gần 1 instruction mỗi clock cycle (khi không có hazard).

> **[Simplification]**: Thực tế Cortex-M4 có 3-stage pipeline với nhiều tối ưu hơn. Phần trên mô tả conceptual model 4-stage để dễ hiểu.

### 4. Real-world

**Tại sao biết điều này quan trọng trong Embedded?**

**1. Memory access latency:**
```
Lệnh LDR R0, [R1] — không phải 1 cycle!
  - Flash với wait states: 2-5 cycles
  - RAM: 0-1 cycle
  - Peripheral: nhiều hơn
→ Pipeline stall xảy ra khi CPU chờ data từ memory
```

**2. Instruction ordering trong bare-metal:**
```c
// Vấn đề: compiler/CPU có thể reorder
volatile uint32_t *reg_A = (uint32_t*)0x40000000;
volatile uint32_t *reg_B = (uint32_t*)0x40000004;

*reg_A = 1;   // Compiler không reorder vì volatile
*reg_B = 2;   // Nhưng với DMA: cần memory barrier!
__DSB();      // Data Synchronization Barrier
```

**3. Branch penalty:**
```asm
; Nếu branch xảy ra → pipeline bị flush → ~1-3 cycles penalty
CMP   R0, #0
BNE   some_label     ; Nếu nhảy → flush pipeline
; Tiếp tục...
```

### 5. Code

**Đo thời gian thực thi bằng DWT cycle counter:**

```c
#include "core_cm4.h"

// Enable DWT Cycle Counter
void dwt_enable(void)
{
    CoreDebug->DEMCR |= CoreDebug_DEMCR_TRCENA_Msk;
    DWT->CYCCNT = 0;
    DWT->CTRL |= DWT_CTRL_CYCCNTENA_Msk;
}

// Đo số cycle của một đoạn code
uint32_t measure_cycles(void)
{
    uint32_t start, end;
    volatile int a = 5, b = 3, c;

    start = DWT->CYCCNT;

    c = a + b;  // Lệnh này tốn bao nhiêu cycle?

    end = DWT->CYCCNT;

    return (end - start);
}
// Kết quả: 1-3 cycles tùy vào optimizer và memory location của a, b
```

**Test pipeline effect với data dependency:**

```c
// Trường hợp 1: Có data dependency (pipeline stall)
void test_dependency(void)
{
    // R0 → R1 → R2 → R3: mỗi lệnh phụ thuộc kết quả trước
    __asm volatile (
        "MOV R0, #1         \n"
        "ADD R1, R0, #1     \n"   // Phụ thuộc R0 → stall
        "ADD R2, R1, #1     \n"   // Phụ thuộc R1 → stall
        "ADD R3, R2, #1     \n"   // Phụ thuộc R2 → stall
        ::: "r0","r1","r2","r3"
    );
}

// Trường hợp 2: Không có dependency (chạy nhanh hơn)
void test_no_dependency(void)
{
    __asm volatile (
        "MOV R0, #1         \n"
        "MOV R1, #2         \n"   // Độc lập với R0
        "MOV R2, #3         \n"   // Độc lập
        "ADD R3, R0, R1     \n"   // R0,R1 đã sẵn sàng
        ::: "r0","r1","r2","r3"
    );
}
```

### 6. Assembly

**Xem pipeline effect trong disassembly:**

```asm
; Đây là loop đơn giản, nhìn vào timing:
08000100:   MOV   R0, #10          ; R0 = 10 (counter)
08000104:   MOV   R1, #0           ; R1 = sum

; Loop start:
08000108:   ADD   R1, R1, R0       ; R1 += R0
0800010C:   SUBS  R0, R0, #1       ; R0 -= 1, update flags
08000110:   BNE   0x08000108       ; Nếu R0 != 0 → jump

; Phân tích pipeline trong loop body:
; Cycle 1: Fetch ADD,  ---,         ---
; Cycle 2: Fetch SUBS, Decode ADD,  ---
; Cycle 3: Fetch BNE,  Decode SUBS, Execute ADD
; Cycle 4: Fetch ???,  Decode BNE,  Execute SUBS (update flags)
; Cycle 5: [flush nếu branch taken], Execute BNE
; Nếu branch taken: fetch lại từ 0x08000108 → 1 cycle penalty
```

**Cortex-M4 có branch prediction đơn giản** để giảm penalty.

### 7. Debug

**Xem instruction execution trong GDB:**

```bash
# Single-step từng instruction
(gdb) stepi          # si — step 1 instruction
(gdb) nexti          # ni — step 1 instruction, không vào function

# Xem registers sau mỗi bước
(gdb) info registers # Xem tất cả registers
(gdb) p/x $r0        # Xem R0 dạng hex
(gdb) display/x $r0  # Tự động hiển thị R0 sau mỗi step

# Xem disassembly tại PC hiện tại
(gdb) x/10i $pc      # Xem 10 instructions từ PC
(gdb) disas $pc, $pc+20  # Disassembly một range
```

**Ozone (Segger)**: Có thể xem từng cycle với **Instruction Trace** (ETM) trên chip hỗ trợ.

### 8. ❌ Common Mistakes

**Lỗi 1: Nghĩ rằng C code thực thi "từng dòng một"**
```c
// 3 dòng C ≠ 3 instructions assembly
int a = 5;       // Có thể: MOV, hoặc không cần instruction gì (constant folding)
int b = a + 3;   // Có thể: ADD, hoặc = 8 luôn (compiler optimize)
int c = b * 2;   // Có thể: LSL (shift), không phải MUL
// Compiler tối ưu rất aggressively!
```

**Lỗi 2: Nghĩ rằng mỗi instruction tốn đúng 1 cycle**
```
- Flash instruction: thường 2-5 cycles (có wait state)
- SDRAM access: có thể 10+ cycles
- Pipeline stall khi data dependency
- Branch misprediction: 1-3 cycle penalty
```

**Lỗi 3: Không hiểu pipeline → viết critical timing code sai**
```c
// Muốn toggle GPIO đúng 10us, nhưng:
GPIOA->BSRR = GPIO_PIN_5;    // Set
delay_us(10);                  // 10us
GPIOA->BSRR = GPIO_PIN_5 << 16; // Reset

// Thực ra: instruction tới peripheral mất nhiều hơn 1 cycle
// Cần đo thực tế bằng oscilloscope!
```

### 9. 📌 Remember

> **Fetch → Decode → Execute → (Writeback)** — 4 bước cơ bản

- Cortex-M4 dùng 3-stage pipeline (F→D→E) → ~1 instruction/cycle (lý tưởng)
- PC tự tăng sau Fetch — đó là lý do PC luôn "trỏ trước" 4 bytes
- `ADD R2, R0, R1`: R0 và R1 phải sẵn sàng trước Execute stage
- Flash wait states → instruction fetch mất nhiều hơn 1 cycle
- Branch taken → pipeline flush → performance penalty

### 10. 🔬 Advanced

**Out-of-Order Execution:** Cortex-M không có OoOE (chỉ in-order), nhưng Cortex-A có. Đây là lý do memory barrier (`DMB`, `DSB`, `ISB`) quan trọng hơn nhiều trên Cortex-A.

**Thumb-2 Mixed encoding:**
```
16-bit Thumb:  ADD R0, R0, #1    → 2 bytes (tối ưu code size)
32-bit Thumb-2: ADD.W R0, R0, #1 → 4 bytes (cần cho immediate lớn hơn)
CPU fetch 16/32-bit tự động theo opcode đầu tiên
```

**Superscalar (Cortex-M7):**
Cortex-M7 có **6-stage pipeline** và **dual-issue** — có thể execute 2 instructions/cycle trong điều kiện tốt. Đây là bước tiến so với M4.

---

## CHƯƠNG 11: LDR / STR — CPU ĐỌC GHI MEMORY

---

### 1. Why?

Register trong CPU chỉ có ~16 cái, nhưng chương trình cần làm việc với hàng nghìn biến. Làm thế nào?

**CPU không thể ADD từ memory sang memory trực tiếp.** Nó phải:
1. **Load** (LDR) giá trị từ memory vào register
2. Xử lý trong register
3. **Store** (STR) kết quả từ register về memory

Đây là kiến trúc **Load-Store**, đặc trưng của RISC (ARM, MIPS, RISC-V). Hiểu LDR/STR là hiểu được **mọi hoạt động đọc/ghi** trong Embedded — biến, array, struct, peripheral registers.

### 2. What?

**Hai lệnh cơ bản nhất của ARM:**

```
LDR Rd, [Rn]    →  Rd = Memory[Rn]    (Load: đọc từ memory vào register)
STR Rs, [Rn]    →  Memory[Rn] = Rs    (Store: ghi từ register ra memory)
```

**Các biến thể quan trọng:**

| Instruction | Kích thước | C tương đương |
|-------------|-----------|---------------|
| `LDR R0, [R1]` | 32-bit word | `R0 = *(uint32_t*)R1` |
| `LDRH R0, [R1]` | 16-bit halfword | `R0 = *(uint16_t*)R1` |
| `LDRB R0, [R1]` | 8-bit byte | `R0 = *(uint8_t*)R1` |
| `LDRSB R0, [R1]` | 8-bit signed | `R0 = *(int8_t*)R1` |
| `STR R0, [R1]` | 32-bit word | `*(uint32_t*)R1 = R0` |
| `STRH R0, [R1]` | 16-bit halfword | `*(uint16_t*)R1 = R0` |
| `STRB R0, [R1]` | 8-bit byte | `*(uint8_t*)R1 = R0` |

**Addressing modes:**

```asm
LDR R0, [R1]          ; Base: đọc tại địa chỉ R1
LDR R0, [R1, #8]      ; Offset: đọc tại R1+8
LDR R0, [R1, R2]      ; Register offset: đọc tại R1+R2
LDR R0, [R1, R2, LSL #2] ; Scaled: đọc tại R1+(R2*4) ← dùng cho array!
LDR R0, [R1, #8]!     ; Pre-indexed: R1 = R1+8, rồi đọc tại R1
LDR R0, [R1], #8      ; Post-indexed: đọc tại R1, rồi R1 = R1+8
```

### 3. How?

**Liên hệ với con trỏ trong C:**

```c
int x = 10;
int *ptr = &x;
int y = *ptr;   // Đây là LDR!
*ptr = 20;      // Đây là STR!
```

```
Memory Layout:
┌──────────────────────────────────────────────┐
│  Address   │  Content  │  Tên biến           │
├──────────────────────────────────────────────┤
│ 0x20001000 │ 0x0000000A│  x = 10             │
│ 0x20001004 │ 0x20001000│  ptr = &x           │
│ 0x20001008 │ ???       │  y (chưa có giá trị)│
└──────────────────────────────────────────────┘

Thực thi `y = *ptr`:

Bước 1: Load ptr vào register
  LDR R0, [SP, #4]   ; R0 = 0x20001000 (giá trị của ptr)

Bước 2: Dereference (đây là "con trỏ")
  LDR R1, [R0]       ; R1 = Memory[0x20001000] = 10

Bước 3: Store vào y
  STR R1, [SP, #8]   ; Memory[addr_of_y] = 10
```

**Flow chi tiết của LDR R0, [R1]:**

```
Giả sử: R1 = 0x20001000

 CPU Core                    Bus Matrix              SRAM
┌─────────────────┐         ┌──────────┐         ┌──────────────┐
│                 │         │          │         │              │
│  1. Execute:    │─ADDRESS─>          │─ADDRESS─>│ 0x20001000  │
│  addr = R1      │ 0x20001000         │          │             │
│  = 0x20001000   │         │          │         │  [0x0000000A]│
│                 │         │          │<─DATA───┤             │
│  2. Memory Read │<─DATA──┤ 0x0000000A│         │             │
│  data=0x0A      │ 0x0000000A          │         └──────────────┘
│                 │         └──────────┘
│  3. Writeback:  │
│  R0 ← 0x0A     │
└─────────────────┘
```

### 4. Real-world

**Array indexing trong embedded:**

```c
uint32_t buffer[256];
uint32_t val = buffer[i]; // Làm thế nào compiler dịch cái này?
```

```asm
; R0 = base address của buffer
; R1 = i (index)
LDR R0, =buffer          ; R0 = &buffer[0]
LDR R1, [SP, #...]       ; R1 = i
LDR R2, [R0, R1, LSL #2] ; R2 = buffer[i]
;                 LSL #2 = nhân 4 (vì uint32_t = 4 bytes)
;                 R0 + (i * 4) = địa chỉ của buffer[i]
```

**Struct member access:**

```c
typedef struct {
    uint32_t x;    // offset 0
    uint32_t y;    // offset 4
    uint32_t z;    // offset 8
} Point_t;

Point_t p;
uint32_t val = p.z;  // Truy cập member z
```

```asm
; R0 = address của struct p
LDR R0, =p          ; R0 = &p
LDR R1, [R0, #8]    ; R1 = p.z (offset 8 bytes từ đầu struct)
```

**Multiple Load/Store (cho performance):**

```c
// Memcpy 4 words cùng lúc
void fast_copy(uint32_t *dst, uint32_t *src)
{
    __asm volatile (
        "LDMIA %0!, {R2-R5}   \n"  // Load 4 words từ src, auto-increment
        "STMIA %1!, {R2-R5}   \n"  // Store 4 words vào dst, auto-increment
        : "+r"(src), "+r"(dst)
        :: "r2","r3","r4","r5","memory"
    );
}
```

### 5. Code

**Hiểu pointer và LDR/STR:**

```c
#include <stdint.h>

// Demo: mọi thứ là LDR/STR
void ldr_str_demo(void)
{
    uint32_t x = 42;        // STR (lưu 42 vào stack)
    uint32_t y;
    uint32_t *ptr = &x;     // STR (lưu địa chỉ x vào stack)

    y = *ptr;               // LDR (load từ địa chỉ trong ptr)
    // Assembly: LDR R0, [ptr_reg] → LDR R1, [R0] → STR R1, [y_addr]

    *ptr = 100;             // STR (ghi 100 vào địa chỉ trong ptr)
    // Assembly: LDR R0, [ptr_reg] → MOV R1, #100 → STR R1, [R0]
}

// Unaligned access — NGUY HIỂM trên Cortex-M!
void alignment_demo(void)
{
    uint8_t buf[8] = {0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77, 0x88};

    // Aligned access (an toàn)
    uint32_t *aligned_ptr = (uint32_t*)buf;
    uint32_t val1 = *aligned_ptr;  // val1 = 0x44332211 (little-endian)

    // An toàn hơn: dùng memcpy hoặc packed struct
    uint32_t val2;
    __builtin_memcpy(&val2, buf + 1, sizeof(val2));
}
```

**LDR với offset — đọc struct members:**

```c
typedef struct {
    uint32_t status;    // +0
    uint32_t data;      // +4
    uint32_t control;   // +8
} Peripheral_t;

volatile Peripheral_t *periph = (Peripheral_t*)0x40000000;

uint32_t read_data(void)
{
    return periph->data;
    // Assembly tương đương:
    // LDR R0, =0x40000000   ; R0 = base address
    // LDR R1, [R0, #4]      ; R1 = *(R0 + 4) = periph->data
}
```

### 6. Assembly

**Compiler output thực tế (GCC -O1):**

```c
uint32_t global_var = 0;

void write_then_read(void)
{
    global_var = 0x12345678;
    uint32_t x = global_var;
}
```

```asm
; GCC ARM Cortex-M4 -O1 output:
write_then_read:
    LDR   R0, =global_var       ; R0 = address của global_var
    LDR   R1, =0x12345678       ; R1 = 0x12345678
    STR   R1, [R0]              ; global_var = 0x12345678
    LDR   R2, [R0]              ; x = global_var (đọc lại từ memory)
    BX    LR                    ; return

; Nếu KHÔNG có volatile:
write_then_read_no_volatile:
    ; Compiler có thể optimize thành:
    ; x = 0x12345678 (không cần LDR lại!)
    BX    LR
```

**Ví dụ LDMIA/STMIA (multiple register):**

```asm
; Điển hình trong function prologue/epilogue
function_entry:
    PUSH  {R4-R7, LR}      ; STM (Store Multiple) - lưu saved regs
    ; PUSH là shorthand của STMDB SP!, {R4-R7, LR}

function_exit:
    POP   {R4-R7, PC}       ; LDM (Load Multiple)
    ; POP là shorthand LDMIA SP!, {R4-R7, PC}
    ;   PC = Memory[SP+16]  ← PC = old LR → return!
```

### 7. Debug

**Xem LDR/STR trong debugger:**

```bash
# GDB: watch một địa chỉ memory
(gdb) watch *((uint32_t*)0x20001000)  # Dừng khi địa chỉ này bị ghi

# Xem memory tại địa chỉ
(gdb) x/4xw 0x20001000   # 4 words hex tại 0x20001000

# Trace LDR/STR manually
(gdb) stepi              # Chạy 1 instruction
(gdb) info registers     # Xem kết quả
(gdb) x/xw $r1          # Xem memory tại R1
```

**HardFault do alignment:**

```
Fault khi: LDR R0, [R1]  với R1 = 0x20000001 (unaligned!)

SCB->CFSR = 0x00000100   → UNALIGNED bit set (UsageFault)
SCB->HFSR = 0x40000000   → FORCED bit (HardFault do UsageFault)

Fix:
1. Tìm code gán R1 = unaligned address
2. Kiểm tra struct padding và __packed attributes
3. Hoặc enable unaligned access (SCB->CCR &= ~SCB_CCR_UNALIGN_TRP_Msk)
```

### 8. ❌ Common Mistakes

**Lỗi 1: Nhầm LDR (load immediate) với LDR (load from memory)**
```asm
LDR R0, =0x1234     ; KHÔNG phải đọc từ memory!
                    ; Load literal: R0 = 0x1234 (từ literal pool)

LDR R0, [R1]        ; Đọc từ memory tại địa chỉ R1
```

**Lỗi 2: Quên `volatile` với memory-mapped registers**
```c
// SAI: Compiler optimize bỏ vì nghĩ không cần đọc lại
uint32_t *reg = (uint32_t*)0x40000000;
*reg = 1;
uint32_t x = *reg;  // Compiler có thể bỏ LDR này! x = 1 luôn

// ĐÚNG: dùng volatile
volatile uint32_t *reg = (volatile uint32_t*)0x40000000;
```

**Lỗi 3: Unaligned 32-bit access**
```c
// Struct packed có thể gây unaligned access
typedef struct __attribute__((packed)) {
    uint8_t  a;
    uint32_t b;   // offset 1 → UNALIGNED!
} Bad_t;

Bad_t s;
uint32_t x = s.b;  // Có thể gây HardFault trên Cortex-M0!
```

### 9. 📌 Remember

> **LDR = *ptr (đọc)** | **STR = *ptr = val (ghi)**

- ARM là **Load-Store architecture**: không có ADD trực tiếp từ memory
- `LDR R0, [R1]` → `R0 = *(uint32_t*)R1`
- `STR R0, [R1]` → `*(uint32_t*)R1 = R0`
- Mọi thứ trong C (biến, array, struct, con trỏ) đều là LDR/STR ở cấp machine
- Alignment quan trọng: word (4B), halfword (2B), byte (1B)
- Dùng `volatile` cho memory-mapped registers, luôn luôn!

### 10. 🔬 Advanced

**Exclusive Load/Store (LDREX/STREX) cho atomic operations:**
```asm
; Atomic increment (không dùng disable interrupt)
retry:
    LDREX  R1, [R0]      ; Exclusive load, đặt "exclusive monitor"
    ADD    R1, R1, #1    ; Tăng
    STREX  R2, R1, [R0]  ; Exclusive store. R2 = 0 nếu thành công
    CMP    R2, #0
    BNE    retry         ; Nếu thất bại (bị interrupt chen vào) → thử lại
```

**Cache và LDR/STR (Cortex-M7):**

Cortex-M7 có L1 I-Cache (16KB) và D-Cache (16KB). `LDR` từ cached region = 1-2 cycles thay vì nhiều hơn. Nhưng: cache coherency với DMA có thể gây bug nghiêm trọng — cần `SCB_InvalidateDCache()` trước khi DMA đọc.

---

## CHƯƠNG 12: MEMORY-MAPPED PERIPHERAL

---

### 1. Why?

> **Đây là khái niệm cốt lõi nhất của Embedded Systems.**

Câu hỏi: Làm thế nào CPU nói chuyện với UART, GPIO, Timer, SPI? CPU không có "dây điện đặc biệt" nối với từng peripheral. Thay vào đó, ARM sử dụng một kỹ thuật cực kỳ thông minh:

**Peripheral registers được "ánh xạ" vào không gian địa chỉ bình thường của CPU.**

Điều này có nghĩa là:
- `UART->DR = 'A'` thực chất chỉ là **một lệnh STR** ghi vào địa chỉ `0x40011004`
- CPU không cần biết đó là UART hay RAM — nó chỉ làm STR
- Hardware (bus decoder) sẽ route tín hiệu đến đúng peripheral

Không có instruction đặc biệt nào để giao tiếp với peripheral — **chỉ là LDR và STR thông thường**.

### 2. What?

**Memory Map của STM32F4xx (ví dụ):**

```
Address Space (4GB với ARM 32-bit)
┌──────────────────────────────────────────────────────┐
│ 0xFFFFFFFF │                                         │
│     ...    │  Reserved                               │
│ 0xE0100000 │                                         │
├────────────┤─────────────────────────────────────────┤
│ 0xE000E000 │  CORTEX-M SYSTEM PERIPHERALS            │
│            │  (NVIC, SCB, SysTick, DWT, ITM)         │
│            │  Private Peripheral Bus (PPB)           │
├────────────┤─────────────────────────────────────────┤
│ 0x40026400 │  DMA2                                   │
│ 0x40026000 │  DMA1                                   │
│ 0x40023800 │  RCC  ← Clock Control                   │
├────────────┤                                         │
│ 0x40020000 │  AHB1 PERIPHERALS                       │
│            │  GPIOA(0x40020000), GPIOB, GPIOC, ...   │
├────────────┤─────────────────────────────────────────┤
│ 0x40013800 │  USART1                                 │
│ 0x40013000 │  SPI1                                   │
│ 0x40012000 │  ADC1                                   │
│ 0x40010000 │  APB2 PERIPHERALS                       │
├────────────┤─────────────────────────────────────────┤
│ 0x40007400 │  DAC                                    │
│ 0x40004400 │  USART2                                 │
│ 0x40002000 │  TIM2, TIM3, TIM4, TIM5                │
│ 0x40000000 │  APB1 PERIPHERALS                       │
├────────────┤─────────────────────────────────────────┤
│ 0x20000000 │  SRAM                                   │
├────────────┤─────────────────────────────────────────┤
│ 0x08000000 │  FLASH MEMORY                           │
│ 0x00000000 │  (aliased từ Flash hoặc SRAM)           │
└────────────┘─────────────────────────────────────────┘
```

**Cấu trúc register của USART1 (STM32F4):**

```
USART1 Base Address: 0x40011000

Offset  │ Register │ Description
────────┼──────────┼───────────────────────────────────
+0x00   │ SR       │ Status Register
+0x04   │ DR       │ Data Register  ← đọc/ghi data ở đây
+0x08   │ BRR      │ Baud Rate Register
+0x0C   │ CR1      │ Control Register 1
+0x10   │ CR2      │ Control Register 2
+0x14   │ CR3      │ Control Register 3
+0x18   │ GTPR     │ Guard time/Prescaler Register

Vậy:
USART1->DR  nằm tại địa chỉ: 0x40011000 + 0x04 = 0x40011004
USART1->SR  nằm tại địa chỉ: 0x40011000 + 0x00 = 0x40011000
```

### 3. How?

**Trace từng bước: `USART1->DR = 'A'`**

```c
// C Code:
USART1->DR = 'A';   // 'A' = 0x41
```

**Bước 1: Compiler tạo assembly:**
```asm
; USART1 = 0x40011000
; DR offset = 0x04
; 'A' = 0x41

LDR   R0, =0x40011004     ; R0 = địa chỉ của USART1->DR
MOV   R1, #0x41           ; R1 = 'A'
STR   R1, [R0]            ; *((uint32_t*)0x40011004) = 0x41
```

**Bước 2: CPU thực thi STR — bus routing:**
```
CPU thực thi STR R1, [R0]:

 CPU Core
┌────────────────┐
│ R0=0x40011004  │
│ R1=0x41        │    ADDRESS: 0x40011004
│                │    DATA:    0x41
│  STR           │    TYPE:    Write, 32-bit
│  instruction   │
└────────────────┘
         │
         ▼
┌─────────────────────┐
│   Bus Decoder       │
│                     │
│ 0x40011000-3FF      │
│   → Route to APB2   │
└──────────┬──────────┘
           │
┌──────────▼──────────┐
│   APB2 Bus          │
│                     │
│  USART1 Hardware    │
│  ┌───────────────┐  │
│  │  DR Register  │  │
│  │  [0x41] ←─────┼──┤ ← Giá trị ghi vào đây
│  └───────────────┘  │
│                     │
│  Hardware tự động:  │
│  - Shift vào TX     │
│  - Truyền bits      │
│    qua chân TX pin  │
└─────────────────────┘
```

**Kết quả vật lý:** Chân USART1_TX của STM32 sẽ phát ra tín hiệu UART với byte `0x41` = ký tự 'A'.

**Tương tự với GPIO:**

```c
GPIOA->BSRR = (1 << 5);  // Set pin PA5 (LED)
```

```asm
; GPIOA base = 0x40020000
; BSRR offset = 0x18

LDR   R0, =0x40020018     ; R0 = &GPIOA->BSRR
MOV   R1, #0x00000020     ; R1 = (1 << 5)
STR   R1, [R0]            ; Ghi vào BSRR
; → GPIO hardware set PA5 = HIGH
; → LED sáng!
```

### 4. Real-world

**Cách CMSIS định nghĩa peripheral registers:**

```c
// Từ stm32f4xx.h (CMSIS)
typedef struct {
    __IO uint32_t SR;    // USART Status register,     Address offset: 0x00
    __IO uint32_t DR;    // USART Data register,        Address offset: 0x04
    __IO uint32_t BRR;   // USART Baud rate register,   Address offset: 0x08
    __IO uint32_t CR1;   // USART Control register 1,   Address offset: 0x0C
    __IO uint32_t CR2;   // USART Control register 2,   Address offset: 0x10
    __IO uint32_t CR3;   // USART Control register 3,   Address offset: 0x14
    __IO uint32_t GTPR;  // USART Guard time/Prescaler, Address offset: 0x18
} USART_TypeDef;

// __IO = volatile

// Định nghĩa địa chỉ
#define USART1_BASE   0x40011000UL
#define USART1        ((USART_TypeDef *) USART1_BASE)

// Giờ thì:
// USART1->DR   = (USART_TypeDef*)0x40011000 → member DR ở offset 4
//             = *(uint32_t*)(0x40011004)
```

**Tại sao `__IO` (volatile) là BẮT BUỘC:**

```c
// KHÔNG CÓ volatile:
uint32_t *sr = (uint32_t*)0x40011000;
while (!(*sr & USART_SR_TXE));  // Đợi TX buffer empty

// Compiler "thông minh": thấy *sr không bao giờ thay đổi trong vòng lặp
// → Optimize thành: if (!initial_sr_value) { while(1); }
// → BUG! Program bị treo vĩnh viễn!

// CÓ volatile:
volatile uint32_t *sr = (volatile uint32_t*)0x40011000;
while (!(*sr & USART_SR_TXE));
// Compiler PHẢI đọc lại *sr mỗi lần lặp → đúng!
```

### 5. Code

**Custom register access — không dùng CMSIS:**

```c
#include <stdint.h>

// Định nghĩa thủ công
#define GPIOC_BASE      0x40020800UL
#define GPIOC_MODER     (*((volatile uint32_t*)(GPIOC_BASE + 0x00)))
#define GPIOC_BSRR      (*((volatile uint32_t*)(GPIOC_BASE + 0x18)))

#define RCC_BASE        0x40023800UL
#define RCC_AHB1ENR     (*((volatile uint32_t*)(RCC_BASE + 0x30)))

// Blink LED PC13 trên Blue Pill
void led_blink_raw(void)
{
    // Enable clock GPIOC
    RCC_AHB1ENR |= (1 << 2);    // Bit 2 = GPIOCEN

    // Set PC13 as output (MODER[27:26] = 01)
    GPIOC_MODER &= ~(0x3 << 26);
    GPIOC_MODER |=  (0x1 << 26);

    while (1) {
        GPIOC_BSRR = (1 << 13);        // Set PC13 (LED off - active low)
        for (int i = 0; i < 500000; i++);
        GPIOC_BSRR = (1 << (13 + 16)); // Reset PC13 (LED on)
        for (int i = 0; i < 500000; i++);
    }
}
```

**Bit-band region (Cortex-M3/M4):**

```c
// Bit-band: truy cập từng bit của peripheral register (atomic!)
#define PERIPH_BB_BASE   0x42000000UL

#define PERIPH_BIT(addr, bit) \
    (*((volatile uint32_t *)(PERIPH_BB_BASE + ((addr) - 0x40000000)*32 + (bit)*4)))

// Set bit TE của USART1->CR1 trực tiếp (không cần |=, atomic!)
#define USART1_CR1_TE_BB   PERIPH_BIT(0x4001100C, 3)

USART1_CR1_TE_BB = 1;  // Set TE bit → chỉ là STR vào bit-band region
USART1_CR1_TE_BB = 0;  // Clear TE bit
```

### 6. Assembly

**Disassembly thực tế của UART send:**

```asm
; C: USART1->DR = 'A';
uart_send_optimized:
    LDR    R1, =0x40011004   ; Address của DR
    MOV    R0, #0x41         ; 'A'
    STR    R0, [R1]          ; Ghi vào DR
    BX     LR
```

### 7. Debug

**Debug: Peripheral không hoạt động**

Quy trình debug systematic:

```
Bước 1: Kiểm tra clock
  (gdb) x/xw 0x40023830     # RCC->AHB1ENR
  # Bit tương ứng với peripheral phải = 1

Bước 2: Kiểm tra register config
  (gdb) x/xw 0x4001100C     # USART1->CR1
  # Phải có UE=1, TE=1, RE=1

Bước 3: Kiểm tra baud rate
  (gdb) x/xw 0x40011008     # USART1->BRR

Bước 4: Kiểm tra status
  (gdb) x/xw 0x40011000     # USART1->SR
  # TXE (bit 7) phải = 1 (buffer empty)

Bước 5: Thử ghi manual từ debugger
  (gdb) set *((int*)0x40011004) = 0x41   # Ghi 'A' trực tiếp
```

### 8. ❌ Common Mistakes

**Lỗi 1: Quên enable clock**
```c
// LỖI CỰC PHỔ BIẾN!
GPIOA->MODER = 0x555;  // Không có tác dụng! Chưa enable clock

// ĐÚNG:
RCC->AHB1ENR |= RCC_AHB1ENR_GPIOAEN;  // Enable clock TRƯỚC
GPIOA->MODER = 0x555;
```

**Lỗi 2: Thiếu `volatile` khi cast địa chỉ**
```c
// SAI: compiler optimize bỏ lần đọc thứ 2
uint32_t *reg = (uint32_t*)0x40020000;
uint32_t v1 = *reg;
uint32_t v2 = *reg;  // Compiler: "giống v1, tối ưu đi"

// ĐÚNG:
volatile uint32_t *reg = (volatile uint32_t*)0x40020000;
```

**Lỗi 3: Read-Modify-Write không atomic**
```c
// Vấn đề nếu ISR cũng ghi cùng register
GPIOA->ODR |= (1 << 5);    // NOT atomic! 3 instructions: LDR, ORR, STR

// ĐÚNG: Dùng BSRR (atomic set/reset)
GPIOA->BSRR = (1 << 5);    // Atomic set bit 5
GPIOA->BSRR = (1 << 21);   // Atomic reset bit 5
```

**Lỗi 4: Sai offset của register**
```c
// Tự tính offset sai
#define MY_USART_DR  (*((volatile uint32_t*)0x40011008))  // SAI! Offset 8 = BRR
#define MY_USART_DR  (*((volatile uint32_t*)0x40011004))  // ĐÚNG! Offset 4 = DR
```

### 9. 📌 Remember

> **Peripheral register = Memory address. LDR/STR = giao tiếp với hardware.**

- `UART->DR = 'A'` ≡ `STR 0x41, [0x40011004]` — không có gì thần bí
- Luôn enable **clock** trước khi dùng peripheral
- **`volatile`** là bắt buộc cho tất cả peripheral registers
- Kiểm tra **Reference Manual** cho offset, bit fields, access type (RO/WO/RW)
- Dùng **BSRR** thay **ODR** để set/clear GPIO bit một cách atomic

### 10. 🔬 Advanced

**APB vs AHB — tại sao có nhiều bus?**

```
AHB (Advanced High-performance Bus):
  - Tốc độ cao, không có wait state thêm
  - GPIOA, DMA, RCC dùng AHB
  - Clock = HCLK (thường = System Clock)

APB (Advanced Peripheral Bus):
  - Tốc độ thấp hơn, có prescaler
  - USART, SPI, I2C, TIM dùng APB
  - APB1: PCLK1 (thường HCLK/2 hoặc HCLK/4)
  - APB2: PCLK2 (thường HCLK/2)
```

→ Đây là lý do baud rate UART phụ thuộc vào APB clock!

**MPU (Memory Protection Unit):**

AUTOSAR và safety systems dùng MPU để:
- Ngăn một partition ghi vào peripheral của partition khác
- Nếu task A cố ghi vào `0x40011004` (USART1 của task B) → MPU fault → safe state

---

## CHƯƠNG 13: TỪ C CODE → ASSEMBLY → MACHINE CODE → CPU

---

### 1. Why?

Đây là "big picture" của quá trình biên dịch từ góc nhìn kỹ sư firmware. Khi bạn viết C code, chuỗi biến đổi sau xảy ra:

```
C Source → (Compiler) → Assembly → (Assembler) → Machine Code → (Linker) → ELF → (Flash) → CPU
```

Hiểu chuỗi này giúp bạn:
- Biết compiler đang làm gì với code của mình
- Debug assembly khi C code "trông đúng nhưng không chạy"
- Optimize code bằng cách đọc disassembly
- Hiểu calling convention để viết C/Assembly mixed code

### 2. What?

**Ví dụ xuyên suốt: hàm `add()`**

```c
// File: add.c
int add(int a, int b)
{
    return a + b;
}

int main(void)
{
    int result = add(5, 3);
    return result;
}
```

**ARM AAPCS (ARM Architecture Procedure Call Standard):**

```
Calling Convention cho ARM Cortex-M:

Truyền arguments:
  R0 = argument 1 (hoặc return value)
  R1 = argument 2
  R2 = argument 3
  R3 = argument 4
  [Stack] = argument 5, 6, ...

Return value:
  R0 = return value (32-bit)
  R0:R1 = return value (64-bit)

Callee-saved registers (function phải restore):
  R4, R5, R6, R7, R8, R9, R10, R11

Caller-saved registers (function có thể modify tự do):
  R0, R1, R2, R3, R12, LR
```

### 3. How?

**Bước 1: C Source Code**
```c
int add(int a, int b) { return a + b; }
```

**Bước 2: Compiler → Assembly (GCC ARM, -O0)**

```asm
; gcc -mcpu=cortex-m4 -mthumb -O0 -S add.c

add:
    PUSH    {R7, LR}          ; Lưu frame pointer và LR
    SUB     SP, SP, #8        ; Cấp phát 8 bytes cho local vars
    ADD     R7, SP, #0        ; R7 = frame pointer

    STR     R0, [R7, #4]      ; Lưu argument a (R0)
    STR     R1, [R7, #0]      ; Lưu argument b (R1)

    LDR     R2, [R7, #4]      ; Load a
    LDR     R3, [R7, #0]      ; Load b

    ADD     R3, R2, R3        ; R3 = a + b

    MOV     R0, R3            ; Return value = R3

    ADD     SP, R7, #8        ; Restore stack pointer
    POP     {R7, PC}          ; Restore R7, return
```

**Bước 2': Compiler → Assembly (GCC ARM, -O1) — tối ưu:**

```asm
; gcc -mcpu=cortex-m4 -mthumb -O1 -S add.c
add:
    ADD     R0, R0, R1        ; R0 = a + b (thẳng luôn!)
    BX      LR                ; Return

; Chỉ 2 instruction! -O1 hiểu a, b đã ở R0, R1
```

**Bước 3: Assembler → Machine Code**

```
Instruction: ADD R0, R0, R1 (Thumb 16-bit)
Binary encoding: 0001 1000 0100 0000
Hex: 0x1840

Instruction: BX LR (Thumb 16-bit)
Hex: 0x4770

Kết quả trong Flash (little-endian):
Address     Bytes        Assembly
0x08000200  40 18        ADD R0, R0, R1
0x08000202  70 47        BX LR
```

**Bước 4: CPU thực thi**

```
Trước khi gọi add(5, 3):
  main() thực thi:
    MOV   R0, #5      ; arg1
    MOV   R1, #3      ; arg2
    BL    add         ; LR = next PC, jump to add

  CPU state khi vào add():
    PC = 0x08000200
    LR = 0x08000210   (return address)
    R0 = 5
    R1 = 3

  ADD R0, R0, R1: R0 = 5 + 3 = 8
  BX LR:          PC = LR → quay về main

  Kết quả: R0 = 8
```

### 4. Real-world

**Trace đầy đủ với nhiều hơn 4 arguments:**

```c
int complex_add(int a, int b, int c, int d, int e)
{
    return a + b + c + d + e;
}
// Gọi: complex_add(1, 2, 3, 4, 5)
```

```asm
; Trong caller:
MOV   R0, #1      ; arg1
MOV   R1, #2      ; arg2
MOV   R2, #3      ; arg3
MOV   R3, #4      ; arg4
MOV   R4, #5
PUSH  {R4}        ; arg5 → lên stack (>4 args)
BL    complex_add
ADD   SP, SP, #4  ; Dọn dẹp stack argument

; Trong complex_add:
; R0=1, R1=2, R2=3, R3=4
; [SP+0] = 5  (arg5 trên stack)
LDR   R4, [SP, #0]  ; Load arg5 từ stack
ADD   R0, R0, R1
ADD   R0, R0, R2
ADD   R0, R0, R3
ADD   R0, R0, R4    ; R0 = 15
BX    LR
```

### 5. Code

**Tool để xem assembly thực tế:**

```bash
# Compile và giữ file assembly
arm-none-eabi-gcc -mcpu=cortex-m4 -mthumb -O1 -S add.c -o add.s

# Disassemble ELF file
arm-none-eabi-objdump -d firmware.elf | less

# Xem C code xen kẽ assembly (rất hữu ích!)
arm-none-eabi-objdump -dS firmware.elf | less
# -S cần compile với -g (debug symbols)
```

**Xem trực tiếp trong GDB:**

```bash
(gdb) disas add            # Disassembly hàm add
(gdb) disas /m add         # Xen kẽ C source và assembly
(gdb) x/10i 0x08000200     # 10 instructions từ địa chỉ này
```

### 6. Assembly

**Stack frame đầy đủ với -O0:**

```asm
multiply:
    PUSH {R7, LR}           ; SP -= 8
    SUB  SP, SP, #8         ; SP -= 8 (space for locals)
    ADD  R7, SP, #0         ; R7 = frame pointer

    STR  R0, [R7, #4]       ; [R7+4] = a
    STR  R1, [R7, #0]       ; [R7+0] = b

    LDR  R2, [R7, #4]       ; R2 = a
    LDR  R3, [R7, #0]       ; R3 = b

    MUL  R3, R2, R3         ; R3 = a * b

    MOV  R0, R3             ; Return value

    ADD  SP, R7, #8         ; Deallocate locals
    POP  {R7, PC}           ; Return

; Stack frame layout:
; High addr ┌──────────┐
;           │  old LR  │ ← pushed by PUSH {R7, LR}
;           ├──────────┤
;           │  old R7  │
;           ├──────────┤ ← R7 (frame pointer)
;           │  b       │ ← [R7+0]
;           ├──────────┤
;           │  a       │ ← [R7+4]
;           └──────────┘ ← SP
; Low addr
```

### 7. Debug

**Debug scenario: "Function return giá trị sai"**

```bash
# Đặt breakpoint vào đầu hàm
(gdb) break add
(gdb) run

# Tại breakpoint, kiểm tra arguments
(gdb) info registers r0 r1
# r0 = 5 (a), r1 = 3 (b)?

# Step qua từng instruction
(gdb) stepi
(gdb) p $r0    # Xem R0 sau mỗi bước

# Kiểm tra stack frame
(gdb) info frame
(gdb) backtrace
```

### 8. ❌ Common Mistakes

**Lỗi 1: Nhầm calling convention**
```c
// a → R0, b → R1 (không phải R1, R2!)
void my_func(int a, int b) { ... }
```

**Lỗi 2: Thay đổi R4-R11 mà không save/restore trong inline asm**
```c
// SAI: clobber R4 mà không khai báo
__asm volatile (
    "MOV R4, #10   \n"   // R4 là callee-saved!
    "ADD R0, R4, R0\n"
);

// ĐÚNG: khai báo clobber list
__asm volatile (
    "MOV R4, #10   \n"
    "ADD R0, R4, R0\n"
    ::: "r4"
);
```

**Lỗi 3: Nghĩ -O0 và -O2 có assembly giống nhau**

`-O2` có thể inline hàm nhỏ, reorder instructions, eliminate "useless" code — assembly rất khác C source.

### 9. 📌 Remember

> **R0=arg1, R1=arg2, R2=arg3, R3=arg4. Return = R0. BL = call. BX LR = return.**

- AAPCS: R0-R3 là scratch (caller-saved), R4-R11 callee-saved
- `BL func` = LR ← PC+4, PC ← func
- `BX LR` = PC ← LR → return
- `-O0`: assembly sát với C, dùng stack nhiều
- `-O2`: assembly rất khác C, inline, no stack frame
- `arm-none-eabi-objdump -dS` là công cụ debugging không thể thiếu

### 10. 🔬 Advanced

**Thumb vs ARM encoding:**
- Cortex-M chỉ dùng Thumb/Thumb-2
- Thumb: 16-bit instructions (compact)
- Thumb-2: mix 16-bit và 32-bit
- Bit 0 của địa chỉ hàm = 1 (Thumb mode): `add = 0x08000201` trong symbol table

**Link-Time Optimization (LTO):**
```
gcc -flto: Compiler tối ưu cross-file
→ add() có thể bị inline vào main() → biến mất trong binary
```

---

## CHƯƠNG 14: INTERRUPT VÀ EXCEPTION — CÁCH CPU XỬ LÝ

---

### 1. Why?

Hãy tưởng tượng CPU đang chạy vòng lặp main. UART nhận được byte mới. Làm sao CPU biết?

**Cách 1 — Polling (xấu):**
```c
while(1) {
    if (USART1->SR & USART_SR_RXNE) {
        char c = USART1->DR;
    }
    do_other_work();  // Mất time ở đây → miss UART byte!
}
```

**Cách 2 — Interrupt (tốt):**
```
CPU làm việc khác...
UART hardware: "Tôi có data!" → Gửi tín hiệu interrupt
CPU: Tạm dừng công việc hiện tại
CPU: Nhảy vào UART_ISR, xử lý byte
CPU: Return về công việc cũ, tiếp tục chính xác từ chỗ dừng
```

Interrupt là cơ chế **hardware-assisted preemption**.

### 2. What?

**Exception types trong Cortex-M:**

```
Exception Number │ Exception Type   │ Priority
─────────────────┼──────────────────┼──────────────────
1                │ Reset            │ -3 (highest)
2                │ NMI              │ -2 (non-maskable)
3                │ HardFault        │ -1
4                │ MemManage        │ Configurable
5                │ BusFault         │ Configurable
6                │ UsageFault       │ Configurable
11               │ SVCall           │ Configurable
14               │ PendSV           │ Configurable
15               │ SysTick          │ Configurable
16+N             │ IRQ0..N          │ Configurable
```

**Phân biệt:**
- **Exception**: Gây ra bởi CPU/software (Reset, Fault, SVCall, SysTick, PendSV)
- **Interrupt (IRQ)**: Gây ra bởi external peripheral (UART, GPIO, Timer, DMA...)
- Interrupt là một loại exception (Exception Number ≥ 16)
- Được quản lý bởi **NVIC (Nested Vectored Interrupt Controller)**

### 3. How?

**Toàn bộ flow từ Peripheral đến CPU:**

```
                INTERRUPT FLOW (Cortex-M4)
                ──────────────────────────

Peripheral        NVIC              CPU Core
(UART)            │                 │
│  RX data        │                 │
│  received →     │                 │
│  RXNE bit=1 →   │                 │
│  IRQ assert     │                 │
│─────────────────>                 │
│                 │  Priority check │
│                 │  Enabled?       │
│                 │─────────────────>
│                 │                 │ Hardware auto-push:
│                 │                 │ R0,R1,R2,R3,R12,LR,PC,xPSR
│                 │                 │
│                 │                 │ Fetch vector from table
│                 │                 │ PC ← ISR address
│                 │                 │ LR ← EXC_RETURN
│                 │                 │
│                 │                 │ Execute ISR:
│                 │                 │   Read USART1->DR
│                 │                 │   Process byte
│                 │                 │   BX LR
│                 │                 │
│                 │                 │ Hardware auto-pop:
│                 │                 │ xPSR,PC,LR,R12,R3,R2,R1,R0
│                 │                 │
│                 │                 │ Resume interrupted code
```

**Exception Entry (Hardware tự động làm):**

```
1. Hoàn thành instruction hiện tại
2. Push registers lên stack (hardware auto-push):
   Push: xPSR, PC, LR, R12, R3, R2, R1, R0
   SP -= 32 (8 * 4 bytes)

3. Fetch vector từ Vector Table:
   PC ← [VectorTable_base + Exception_number * 4]

4. Set LR = EXC_RETURN:
   0xFFFFFFF1: Return to Handler mode, MSP
   0xFFFFFFF9: Return to Thread mode, MSP
   0xFFFFFFFD: Return to Thread mode, PSP

5. Switch sang Handler Mode
6. Thực thi ISR
```

**Exception Return (khi ISR thực thi BX LR):**

```
CPU nhận ra EXC_RETURN (LR[31:5] = 0xFFFFFFF):
1. Kiểm tra bits [3:0] để biết mode
2. Pop registers từ stack: R0,R1,R2,R3,R12,LR,PC,xPSR
3. SP += 32
4. Tiếp tục từ stacked PC
5. Restore mode (Handler → Thread)
```

### 4. Real-world

**NVIC Configuration:**

```c
// 1. Cấu hình interrupt priority
NVIC_SetPriority(USART1_IRQn, 5);

// 2. Enable interrupt trong NVIC
NVIC_EnableIRQ(USART1_IRQn);

// 3. Enable interrupt source trong peripheral
USART1->CR1 |= USART_CR1_RXNEIE;

// ISR
void USART1_IRQHandler(void)
{
    if (USART1->SR & USART_SR_RXNE) {
        uint8_t byte = (uint8_t)(USART1->DR & 0xFF);
        // Xử lý byte...
    }
}
```

**Interrupt preemption:**

```
Priority (số nhỏ = ưu tiên cao hơn trên Cortex-M):
  USART1_IRQ priority = 5
  DMA_IRQ   priority = 3

Scenario:
  1. CPU đang chạy main
  2. USART1_IRQ (priority 5) → vào USART1_IRQHandler
  3. Trong khi đang xử lý, DMA_IRQ (priority 3) xảy ra
  4. Priority 3 < 5 → DMA preempt USART1!
  5. CPU vào DMA_IRQHandler
  6. DMA return → resume USART1_IRQHandler
  7. USART1 return → resume main
```

### 5. Code

**Complete UART interrupt example:**

```c
#define RING_BUFFER_SIZE  64
volatile uint8_t rx_buffer[RING_BUFFER_SIZE];
volatile uint32_t rx_head = 0, rx_tail = 0;

void USART1_IRQHandler(void)
{
    if (USART1->SR & USART_SR_RXNE) {
        uint8_t byte = (uint8_t)(USART1->DR & 0xFF);

        uint32_t next_head = (rx_head + 1) % RING_BUFFER_SIZE;
        if (next_head != rx_tail) {
            rx_buffer[rx_head] = byte;
            rx_head = next_head;
        }
    }

    if (USART1->SR & (USART_SR_ORE | USART_SR_FE | USART_SR_PE)) {
        (void)USART1->DR;  // Clear error flags
    }
}

uint8_t uart_read_byte(void)
{
    while (rx_head == rx_tail);  // Đợi có data
    uint8_t byte = rx_buffer[rx_tail];
    rx_tail = (rx_tail + 1) % RING_BUFFER_SIZE;
    return byte;
}
```

**Critical section:**

```c
void update_shared_data(void)
{
    uint32_t primask = __get_PRIMASK();
    __disable_irq();   // CPSID I

    shared_counter++;  // Thao tác an toàn

    __set_PRIMASK(primask);  // Restore (không enable nếu đã disabled)
}
```

### 6. Assembly

**EXC_RETURN magic values:**

```asm
; Khi vào ISR, LR được hardware set thành EXC_RETURN:
;
; 0xFFFFFFFD = ...1111 1101
;                    ├─── bit 3: 1 = Thread Mode trước khi fault
;                    └─── bit 2: 1 = PSP được dùng
;
; Bits [3:0]:
; 0001 = 0xFFFFFFF1: Handler mode, MSP, no FP
; 1001 = 0xFFFFFFF9: Thread mode,  MSP, no FP
; 1101 = 0xFFFFFFFD: Thread mode,  PSP, no FP ← RTOS task

BX LR   ; Khi LR = 0xFFFFFFFD → Exception Return to Thread/PSP
```

**ISR assembly:**

```asm
USART1_IRQHandler:
    ; Hardware đã push R0-R3,R12,LR,PC,xPSR
    ; ISR đơn giản không dùng R4-R11: không cần PUSH thêm
    LDR   R0, =0x40011000    ; USART1 base
    LDR   R1, [R0, #0]       ; Load SR
    TST   R1, #0x20          ; Check RXNE bit (bit 5)
    BEQ   .exit
    LDR   R1, [R0, #4]       ; Read DR (clears RXNE)
    AND   R1, R1, #0xFF
    ; ... process ...
.exit:
    BX    LR                 ; LR = EXC_RETURN → exception return
```

### 7. Debug

**Debug: "ISR không được gọi"**

```bash
# Bước 1: Kiểm tra NVIC
(gdb) p/x *(uint32_t*)0xE000E100   # NVIC->ISER[0]
# Bit IRQn phải = 1

# Bước 2: Kiểm tra peripheral
(gdb) p/x USART1->CR1              # RXNEIE phải = 1

# Bước 3: Kiểm tra global interrupt
(gdb) p/x $primask                 # 0 = enabled, 1 = disabled

# Bước 4: Kiểm tra pending
(gdb) p/x *(uint32_t*)0xE000E200   # NVIC->ISPR[0]

# Bước 5: Kiểm tra vector table
(gdb) x/xw 0x000000BC   # Vector USART1
# Phải trỏ vào USART1_IRQHandler + 1 (Thumb bit)
```

### 8. ❌ Common Mistakes

**Lỗi 1: Không clear interrupt flag trong ISR**
```c
void TIM2_IRQHandler(void)
{
    // SAI: Quên clear UIF flag → ISR gọi liên tục vô tận!
    do_something();

    // ĐÚNG:
    TIM2->SR &= ~TIM_SR_UIF;  // Clear flag trước
    do_something();
}
```

**Lỗi 2: ISR quá dài / blocking**
```c
void USART1_IRQHandler(void)
{
    // SAI: blocking trong ISR
    uint8_t data = USART1->DR;
    uart_send_response("OK\r\n"); // Blocking send → thảm họa!

    // ĐÚNG: ISR chỉ lấy data, set flag
    rx_buffer[rx_head++] = USART1->DR;
    data_ready_flag = 1;
}
```

**Lỗi 3: Quên `volatile` cho biến shared**
```c
// SAI:
uint8_t new_data = 0;
void ISR(void) { new_data = 1; }
void main(void) { while (!new_data); }  // Compiler: while(1)!

// ĐÚNG:
volatile uint8_t new_data = 0;
```

**Lỗi 4: Sai priority levels**
```c
// Cortex-M: số nhỏ = priority CAO HƠN!
NVIC_SetPriority(USART1_IRQn, 0);  // Priority 0 = highest!
// FreeRTOS: ISR gọi FreeRTOS API phải có priority >= configMAX_SYSCALL_INTERRUPT_PRIORITY
```

### 9. 📌 Remember

> **IRQ → NVIC → Hardware auto-push 8 regs → ISR → EXC_RETURN → Auto-pop 8 regs**

- Hardware tự động push/pop: `R0, R1, R2, R3, R12, LR, PC, xPSR`
- LR trong ISR = EXC_RETURN (không phải return address bình thường!)
- `BX LR` trong ISR = Exception Return
- Số priority nhỏ hơn = ưu tiên **cao hơn** trên Cortex-M
- `volatile` cho tất cả shared variables giữa ISR và main
- ISR phải **ngắn và nhanh**: lấy data → set flag → return

### 10. 🔬 Advanced

**Late Arrival Optimization:**
Nếu IRQ thứ 2 xảy ra trong khi CPU đang push stack cho IRQ thứ nhất, CPU có thể switch sang vector của IRQ thứ 2 mà không cần pop/push thêm.

**Tail-Chaining:**
Sau khi ISR return, nếu có IRQ khác pending cùng priority → CPU không pop-push lại mà "tail-chain" thẳng vào ISR tiếp theo. Tiết kiệm ~6 cycles.

**BASEPRI register:**
```c
// Disable tất cả interrupt có priority <= 5
__set_BASEPRI(5 << (8 - __NVIC_PRIO_BITS));
// Useful hơn PRIMASK: vẫn cho phép high-priority interrupt (NMI, HardFault)
```

---

## CHƯƠNG 15: STACK FRAME KHI INTERRUPT

---

### 1. Why?

Khi interrupt xảy ra, CPU phải "ghi nhớ" trạng thái hiện tại để sau này có thể tiếp tục chính xác. Cơ chế này gọi là **hardware auto-stacking**.

Việc hiểu stack frame này có ý nghĩa thực tiễn:
1. **Debug HardFault**: Stack frame chứa PC của instruction gây fault
2. **Debug RTOS**: Hiểu stack của task để đọc call stack
3. **Viết OS**: Cần biết format để tạo task stack giả
4. **Security**: Stack smashing → overwrite return address trong frame

### 2. What?

**Hardware Exception Stack Frame (Cortex-M3/M4, không FPU):**

```
                Stack Frame khi Exception Entry
                ─────────────────────────────────

  High address  ┌──────────────────────────────────┐
                │                                  │
                │   (Previous stack content)       │
                │                                  │
  SP trước      ├──────────────────────────────────┤ ← SP_before = SP + 32
  khi interrupt │         xPSR                     │  [SP+28] ← pushed CUỐI
                ├──────────────────────────────────┤
                │         PC (Return Address)      │  [SP+24] ← ★ KEY! ★
                ├──────────────────────────────────┤
                │         LR (R14)                 │  [SP+20]
                ├──────────────────────────────────┤
                │         R12                      │  [SP+16]
                ├──────────────────────────────────┤
                │         R3                       │  [SP+12]
                ├──────────────────────────────────┤
                │         R2                       │  [SP+8]
                ├──────────────────────────────────┤
                │         R1                       │  [SP+4]
                ├──────────────────────────────────┤
  SP sau        │         R0                       │  [SP+0] ← pushed ĐẦU TIÊN
  khi interrupt └──────────────────────────────────┘ ← SP_after = SP_before - 32

  Low address

  Thứ tự push (hardware): R0, R1, R2, R3, R12, LR, PC, xPSR
  Thứ tự pop  (hardware): xPSR, PC, LR, R12, R3, R2, R1, R0
```

```
★ Stacked PC = địa chỉ instruction BỊ INTERRUPT (chưa thực thi)
  → Sau exception return, CPU thực thi instruction này
  → Khi fault: đây CHÍNH XÁC là instruction gây lỗi
```

**xPSR Structure:**

```
xPSR [31:0]:
  Bit 31: N (Negative flag)
  Bit 30: Z (Zero flag)
  Bit 29: C (Carry flag)
  Bit 28: V (Overflow flag)
  Bit 27: Q (Saturation flag)
  Bit 24: T (Thumb state) ← PHẢI = 1 cho Cortex-M!
  Bit [8:0]: Exception number (đang active)
```

### 3. How?

**Stack frame khi Fault xảy ra:**

```c
void some_function(void)
{
    volatile int *bad_ptr = (volatile int*)0xDEADBEEF;
    int val = *bad_ptr;  // ← Instruction TẠI ĐÂY gây BusFault
}
```

```
Lúc LDR R0, [R1] (với R1=0xDEADBEEF) thực thi:

  PC = 0x08001234   (địa chỉ của instruction LDR)
  SP = 0x20008000
  R1 = 0xDEADBEEF

  BusFault xảy ra! Hardware push:

  0x20007FE0: R0    = 0x00000000
  0x20007FE4: R1    = 0xDEADBEEF  ← R1 chứa địa chỉ gây fault!
  0x20007FE8: R2    = ...
  0x20007FEC: R3    = ...
  0x20007FF0: R12   = ...
  0x20007FF4: LR    = 0x08001200  ← caller của some_function
  0x20007FF8: PC    = 0x08001234  ← ★ CHÍNH XÁC instruction gây fault! ★
  0x20007FFC: xPSR  = 0x21000000

  SP mới = 0x20007FE0
```

### 4. Real-world

**RTOS: Tạo initial stack frame cho task mới:**

```c
// FreeRTOS tạo stack frame giả để khi "return" từ PendSV,
// CPU sẽ "pop" frame này và "start" task như thể vừa bị interrupt

StackType_t *pxPortInitialiseStack(StackType_t *pxTopOfStack,
                                    TaskFunction_t pxCode,
                                    void *pvParameters)
{
    // Simulate hardware exception frame (từ trên xuống)
    pxTopOfStack--;
    *pxTopOfStack = portINITIAL_XPSR;              // xPSR: T=1 (Thumb)

    pxTopOfStack--;
    *pxTopOfStack = ((StackType_t)pxCode) & ~1UL;  // PC = task function

    pxTopOfStack--;
    *pxTopOfStack = (StackType_t)prvTaskExitError; // LR = error handler

    pxTopOfStack--;
    *pxTopOfStack = 0x00000000UL;  // R12

    pxTopOfStack--;
    *pxTopOfStack = 0x00000000UL;  // R3

    pxTopOfStack--;
    *pxTopOfStack = 0x00000000UL;  // R2

    pxTopOfStack--;
    *pxTopOfStack = 0x00000000UL;  // R1

    pxTopOfStack--;
    *pxTopOfStack = (StackType_t)pvParameters;  // R0 = task parameters

    // Simulate saved R4-R11 (software context, cần cho PendSV restore)
    pxTopOfStack -= 8;

    return pxTopOfStack;  // PSP sẽ point vào đây
}
```

**Phân tích HardFault từ register dump:**

```
Scenario: Embedded system crash

Khi vào HardFault handler:
  LR  = 0xFFFFFFFD  → Trước fault: Thread Mode, PSP

Stack tại PSP:
  [PSP+0 ]: R0  = 0x00000001
  [PSP+4 ]: R1  = 0x20001234   ← pointer (có hợp lệ không?)
  [PSP+8 ]: R2  = 0x00000004
  [PSP+12]: R3  = 0x00000000
  [PSP+16]: R12 = 0x00000000
  [PSP+20]: LR  = 0x08002A35   ← caller
  [PSP+24]: PC  = 0x08002B10   ← ★ INSTRUCTION GÂY FAULT!
  [PSP+28]: xPSR = 0x21000000

→ Disassembly tại 0x08002B10: LDR R0, [R1]
→ R1 = 0x20001234 → map file: đây là gì? Hợp lệ không?
```

### 5. Code

**HardFault handler đọc stack frame:**

```c
// Hard fault handler với stack frame analysis
void HardFault_Handler_C(uint32_t *fault_stack_address)
{
    volatile uint32_t stacked_r0  = fault_stack_address[0];
    volatile uint32_t stacked_r1  = fault_stack_address[1];
    volatile uint32_t stacked_r2  = fault_stack_address[2];
    volatile uint32_t stacked_r3  = fault_stack_address[3];
    volatile uint32_t stacked_r12 = fault_stack_address[4];
    volatile uint32_t stacked_lr  = fault_stack_address[5];
    volatile uint32_t stacked_pc  = fault_stack_address[6];  // ★ KEY!
    volatile uint32_t stacked_psr = fault_stack_address[7];

    volatile uint32_t cfsr  = SCB->CFSR;
    volatile uint32_t hfsr  = SCB->HFSR;
    volatile uint32_t bfar  = SCB->BFAR;
    volatile uint32_t mmfar = SCB->MMFAR;

    printf("=== HARD FAULT ===\n");
    printf("Stacked PC  = 0x%08X  <- Instruction that caused fault!\n", stacked_pc);
    printf("Stacked LR  = 0x%08X\n", stacked_lr);
    printf("Stacked R1  = 0x%08X\n", stacked_r1);
    printf("SCB->CFSR   = 0x%08X\n", cfsr);
    printf("SCB->BFAR   = 0x%08X\n", bfar);

    while(1) __NOP();
}

// Assembly trampoline để lấy đúng stack pointer
__attribute__((naked))
void HardFault_Handler(void)
{
    __asm volatile (
        "TST    LR, #4          \n"  // Test bit 2 của EXC_RETURN
        "ITE    EQ              \n"  // If EQ (bit2=0): MSP, Else: PSP
        "MRSEQ  R0, MSP         \n"
        "MRSNE  R0, PSP         \n"
        "B      HardFault_Handler_C \n"
    );
}
```

### 6. Assembly

**Khi exception entry xảy ra (pseudo-code của hardware):**

```asm
exception_entry:
    ; 1. Chọn stack pointer
    IF (CONTROL.SPSEL == 1) AND (mode == Thread)
        SP = PSP
    ELSE
        SP = MSP

    ; 2. Stack alignment nếu cần (CCR.STKALIGN)
    IF (SP NOT aligned to 8):
        SP -= 4
        xPSR |= (1 << 9)  ; ghi nhớ đã pad

    ; 3. Push frame
    SP -= 4;  MEM[SP] = xPSR
    SP -= 4;  MEM[SP] = PC
    SP -= 4;  MEM[SP] = LR
    SP -= 4;  MEM[SP] = R12
    SP -= 4;  MEM[SP] = R3
    SP -= 4;  MEM[SP] = R2
    SP -= 4;  MEM[SP] = R1
    SP -= 4;  MEM[SP] = R0

    ; 4. Set LR = EXC_RETURN
    ; 5. Switch → Handler Mode
    ; 6. Fetch vector, set PC
    PC = VectorTable[exception_number]
```

### 7. Debug

**GDB commands cho fault analysis:**

```bash
# Assume LR = 0xFFFFFFFD → PSP
(gdb) p/x $psp
# Kết quả: 0x20007FC0

(gdb) x/8xw 0x20007FC0
# Output:
# 0x20007FC0: 0x00000001  <- stacked R0
# 0x20007FC4: 0xDEADBEEF  <- stacked R1  ← LỖI! ptr = 0xDEADBEEF
# 0x20007FC8: 0x00000000  <- stacked R2
# 0x20007FCC: 0x00000000  <- stacked R3
# 0x20007FD0: 0x00000000  <- stacked R12
# 0x20007FD4: 0x080012AD  <- stacked LR (caller)
# 0x20007FD8: 0x08001234  <- stacked PC ← Fault tại đây!
# 0x20007FDC: 0x21000000  <- stacked xPSR

(gdb) x/5i 0x08001234    # Xem instruction tại fault
# 0x08001234: ldr r0, [r1]   ← Đọc từ 0xDEADBEEF → fault!
```

### 8. ❌ Common Mistakes

**Lỗi 1: Nhầm stacked PC với current PC trong HardFault handler**
```c
// SAI: đọc current PC (đang ở trong HardFault handler)
void HardFault_Handler(void) {
    uint32_t pc = __get_PC(); // Đây là PC của HardFault handler!
    // KHÔNG phải PC của code gây fault!
}

// ĐÚNG: đọc stacked PC từ stack frame (frame[6])
```

**Lỗi 2: Không xử lý stack alignment**
```
CCR.STKALIGN = 1 (default):
Stack được align đến 8 bytes trước khi push frame.
SP sau exception = SP_before - 32 HOẶC SP_before - 36
Bit 9 của stacked xPSR = 1 nếu có padding!
```

**Lỗi 3: Quên FPU thay đổi kích thước frame**
```
Không FPU context: 8 words = 32 bytes
Có FPU context (FPCA=1): 8 + 18 = 26 words = 104 bytes!
(thêm S0-S15, FPSCR, reserved)
```

### 9. 📌 Remember

> **8 registers hardware tự động save: R0, R1, R2, R3, R12, LR, PC, xPSR**

```
Stack frame layout (low to high):
[SP+0 ] R0
[SP+4 ] R1
[SP+8 ] R2
[SP+12] R3
[SP+16] R12
[SP+20] LR  (của code bị interrupt)
[SP+24] PC  ← KEY! Địa chỉ instruction bị fault
[SP+28] xPSR
```

- Stacked **PC** = instruction sẽ thực thi khi return = nơi fault
- Stacked **LR** = return address của function đang chạy khi bị interrupt
- **LR trong ISR** = EXC_RETURN
- FPU frame có thể gấp đôi kích thước (~26 words)

### 10. 🔬 Advanced

**Stack frame với FPU (Cortex-M4F):**

```
Khi FPCA=1 (task đã dùng FPU):

  [SP+0 ] R0      ─┐
  [SP+4 ] R1       │
  [SP+8 ] R2       │ Basic frame
  [SP+12] R3       │ (8 words = 32 bytes)
  [SP+16] R12      │
  [SP+20] LR       │
  [SP+24] PC       │
  [SP+28] xPSR    ─┘
  ─── Extended frame (FPU) ───
  [SP+32] S0
  [SP+36] S1
  ...
  [SP+88] S15
  [SP+92] FPSCR
  [SP+96] Reserved (align)

Tổng: 104 bytes!
```

**Lazy FPU stacking:**

Cortex-M4F có thể **trì hoãn** việc push FPU registers đến khi ISR thực sự cần FPU → giảm interrupt latency.

```c
// Enable lazy FPU stacking (thường mặc định):
FPU->FPCCR |= FPU_FPCCR_LSPEN_Msk | FPU_FPCCR_ASPEN_Msk;
```

---

## CHƯƠNG 16: DEBUG REGISTER DUMP

---

### 1. Why?

Hệ thống embedded crash. Không có display, không có logger, không có JTAG. Chỉ có **register dump** được ghi vào EEPROM/flash trước khi reset. Hoặc bạn đang debug live với GDB và cần đọc nhanh trạng thái CPU.

**Register dump** là "tấm ảnh chụp" trạng thái CPU tại thời điểm crash — và nếu bạn biết cách đọc, nó tiết lộ hầu hết mọi thứ bạn cần.

### 2. What?

**Một register dump đầy đủ bao gồm:**

```
=== ARM Cortex-M4 Register Dump ===
General Purpose Registers:
  R0  = 0x00000001
  R1  = 0xDEADBEEF
  R2  = 0x00000004
  R3  = 0x00000000
  R4  = 0x20000A00
  R5  = 0x00000000
  R6  = 0x00000000
  R7  = 0x200007D0
  R8  = 0x00000000
  R9  = 0x00000000
  R10 = 0x00000000
  R11 = 0x00000000
  R12 = 0x00000000

Special Registers:
  SP (MSP) = 0x200007A0
  SP (PSP) = 0x20007F80
  LR       = 0xFFFFFFFD
  PC       = 0x0800ABCD

Status Registers:
  xPSR     = 0x21000000
  PRIMASK  = 0x00000000
  BASEPRI  = 0x00000000
  CONTROL  = 0x00000002

Fault Registers:
  SCB->CFSR  = 0x00008200
  SCB->HFSR  = 0x40000000
  SCB->BFAR  = 0xDEADBEEF
  SCB->MMFAR = 0x00000000
```

### 3. How?

**Hướng dẫn đọc Register Dump từng bước:**

```
ORDER OF ANALYSIS:
  1. PC      → CPU đang ở đâu?
  2. LR      → Đang trong exception? Stack nào?
  3. SP      → Stack còn hợp lệ không?
  4. xPSR    → Mode, flags, exception number
  5. R0-R3   → Arguments/return values gần nhất
  6. Fault Registers → Chi tiết lỗi
  7. Stack contents  → Call stack và local data
```

### 4. Real-world

**Phân tích register dump thực tế (ví dụ đầy đủ):**

```
=== CRASH DUMP ===
PC  = 0x0800ABCD   (trong HardFault handler)
LR  = 0xFFFFFFFD   (EXC_RETURN)
SP  = 0x200007A0   (MSP — đang trong handler)
PSP = 0x20007F80

Stack tại PSP (0x20007F80):
  [+0 ] R0  = 0x00000001
  [+4 ] R1  = 0xDEADBEEF
  [+8 ] R2  = 0x00000004
  [+12] R3  = 0x00000000
  [+16] R12 = 0x00000000
  [+20] LR  = 0x0800AACD   ← Caller của function bị fault
  [+24] PC  = 0x0800AB10   ← ★ Instruction gây fault
  [+28] xPSR = 0x21000000

SCB->CFSR = 0x00008200
  Bit 15 (BFARVALID) = 1  → BFAR hợp lệ
  Bit 9  (PRECISERR) = 1  → BusFault chính xác
SCB->BFAR = 0xDEADBEEF
```

**Phân tích từng bước:**

```
Bước 1: PC = 0x0800ABCD
  → CPU đang trong HardFault_Handler
  → Không phải nơi bug xảy ra

Bước 2: LR = 0xFFFFFFFD
  ┌─────────────────────────────────────┐
  │ 0xFFFFFFFD: bits [3:0] = 1101      │
  │   bit 3 = 1 → Thread Mode          │
  │   bit 2 = 1 → PSP được dùng       │
  └─────────────────────────────────────┘
  → Đọc stack frame tại PSP!

Bước 3: PSP = 0x20007F80
  → Stack frame tại đây

Bước 4: Stacked PC = 0x0800AB10  ★
  → Mở disassembly: LDR R0, [R1]
  → R1 = stacked R1 = 0xDEADBEEF → địa chỉ không hợp lệ!

Bước 5: SCB->CFSR = 0x00008200
  → PRECISERR + BFARVALID → BusFault chính xác
  → BFAR = 0xDEADBEEF → xác nhận fault address

Bước 6: Stacked LR = 0x0800AACD
  → Map file: nằm trong hàm process_data()
  → Bug được gọi từ process_data()

Kết luận: Dereference null/garbage pointer (0xDEADBEEF)
tại 0x0800AB10, được gọi từ process_data()
```

### 5. Code

**Automatic Register Dump khi HardFault:**

```c
// Lưu dump vào section riêng (không bị clear khi reset)
typedef struct {
    uint32_t magic;        // 0xDEADDEAD = dump hợp lệ
    uint32_t r0, r1, r2, r3;
    uint32_t r12, lr, pc, psr;
    uint32_t sp_msp, sp_psp;
    uint32_t cfsr, hfsr, bfar, mmfar;
    uint32_t exc_return;
} CrashDump_t;

__attribute__((section(".noinit")))
CrashDump_t crash_dump;

__attribute__((naked))
void HardFault_Handler(void)
{
    __asm volatile (
        "TST     LR, #4         \n"
        "ITE     EQ             \n"
        "MRSEQ   R0, MSP        \n"
        "MRSNE   R0, PSP        \n"
        "MOV     R1, LR         \n"
        "B       HardFault_C_Handler \n"
    );
}

void HardFault_C_Handler(uint32_t *frame, uint32_t exc_return)
{
    crash_dump.magic = 0xDEADDEAD;
    crash_dump.r0    = frame[0];
    crash_dump.r1    = frame[1];
    crash_dump.r2    = frame[2];
    crash_dump.r3    = frame[3];
    crash_dump.r12   = frame[4];
    crash_dump.lr    = frame[5];
    crash_dump.pc    = frame[6];   // ★ Địa chỉ gây fault
    crash_dump.psr   = frame[7];

    crash_dump.sp_msp    = __get_MSP();
    crash_dump.sp_psp    = __get_PSP();
    crash_dump.cfsr      = SCB->CFSR;
    crash_dump.hfsr      = SCB->HFSR;
    crash_dump.bfar      = SCB->BFAR;
    crash_dump.mmfar     = SCB->MMFAR;
    crash_dump.exc_return = exc_return;

    SCB->CFSR = SCB->CFSR;   // Clear (W1C)
    SCB->HFSR = SCB->HFSR;

    NVIC_SystemReset();  // Reset và ghi nhớ dump
}

void check_crash_dump(void)
{
    if (crash_dump.magic == 0xDEADDEAD) {
        printf("=== PREVIOUS CRASH ===\n");
        printf("Fault PC = 0x%08X\n", crash_dump.pc);
        printf("Fault LR = 0x%08X\n", crash_dump.lr);
        printf("R1       = 0x%08X\n", crash_dump.r1);
        printf("CFSR     = 0x%08X\n", crash_dump.cfsr);
        printf("BFAR     = 0x%08X\n", crash_dump.bfar);
        crash_dump.magic = 0;
    }
}
```

**Decode CFSR register:**

```c
void decode_cfsr(uint32_t cfsr)
{
    printf("CFSR = 0x%08X\n", cfsr);

    // BusFault (bits [15:8])
    if (cfsr & SCB_CFSR_BFARVALID_Msk)
        printf("  [BF] BFAR address valid: 0x%08X\n", SCB->BFAR);
    if (cfsr & SCB_CFSR_PRECISERR_Msk)
        printf("  [BF] Precise BusFault at BFAR\n");
    if (cfsr & SCB_CFSR_IMPRECISERR_Msk)
        printf("  [BF] Imprecise BusFault (buffered write)\n");
    if (cfsr & SCB_CFSR_IBUSERR_Msk)
        printf("  [BF] BusFault on instruction prefetch\n");
    if (cfsr & SCB_CFSR_STKERR_Msk)
        printf("  [BF] BusFault on exception stacking\n");

    // UsageFault (bits [31:16])
    if (cfsr & SCB_CFSR_DIVBYZERO_Msk)
        printf("  [UF] Division by zero\n");
    if (cfsr & SCB_CFSR_UNALIGNED_Msk)
        printf("  [UF] Unaligned memory access\n");
    if (cfsr & SCB_CFSR_NOCP_Msk)
        printf("  [UF] No coprocessor (FPU not enabled?)\n");
    if (cfsr & SCB_CFSR_INVPC_Msk)
        printf("  [UF] Invalid PC on exception return\n");
    if (cfsr & SCB_CFSR_INVSTATE_Msk)
        printf("  [UF] Invalid state (EPSR.T=0)\n");
    if (cfsr & SCB_CFSR_UNDEFINSTR_Msk)
        printf("  [UF] Undefined instruction\n");

    // MemManage (bits [7:0])
    if (cfsr & SCB_CFSR_MMARVALID_Msk)
        printf("  [MM] MMFAR valid: 0x%08X\n", SCB->MMFAR);
    if (cfsr & SCB_CFSR_DACCVIOL_Msk)
        printf("  [MM] Data access MPU violation\n");
    if (cfsr & SCB_CFSR_IACCVIOL_Msk)
        printf("  [MM] Instruction fetch MPU violation\n");
}
```

### 6. Assembly

**Đọc tất cả special registers:**

```asm
; Lưu context registers vào buffer
; R0 = pointer tới buffer
save_special_regs:
    MRS     R1, MSP
    MRS     R2, PSP
    MRS     R3, XPSR
    MRS     R4, PRIMASK
    MRS     R5, FAULTMASK
    MRS     R6, BASEPRI
    MRS     R7, CONTROL
    STMIA   R0!, {R1-R7}   ; Lưu 7 special registers
    BX      LR
```

### 7. Debug

**Quy trình đọc register dump — Quick Reference:**

```
┌─────────────────────────────────────────────────────────┐
│              REGISTER DUMP ANALYSIS GUIDE               │
│                                                         │
│  Step 1: Xác định context                               │
│  ─────────────────────────────────────────────          │
│  LR = 0xFFFFFFF1 → Handler Mode, MSP                   │
│  LR = 0xFFFFFFF9 → Thread Mode,  MSP                   │
│  LR = 0xFFFFFFFD → Thread Mode,  PSP ← RTOS task       │
│  LR = 0xFFFFFFE1 → Handler Mode, MSP, FPU context      │
│  LR = 0xFFFFFFED → Thread Mode,  PSP, FPU context      │
│                                                         │
│  Step 2: Xác định stack frame                           │
│  ─────────────────────────────────────────────          │
│  LR[2]=0 → frame trên MSP                              │
│  LR[2]=1 → frame trên PSP                              │
│                                                         │
│  Step 3: Đọc stacked PC (offset +24 từ SP)              │
│  ─────────────────────────────────────────────          │
│  Stacked PC = instruction GÂY FAULT                     │
│  Map file + objdump để tìm hàm                         │
│                                                         │
│  Step 4: Đọc stacked R0-R3 (offset +0 đến +12)          │
│  ─────────────────────────────────────────────          │
│  Arguments/values tại thời điểm fault                   │
│                                                         │
│  Step 5: SCB fault registers                            │
│  ─────────────────────────────────────────────          │
│  CFSR → loại fault                                      │
│  BFAR → địa chỉ gây BusFault (nếu BFARVALID=1)         │
│  MMFAR → địa chỉ MPU violation                          │
│                                                         │
│  Step 6: Backtrace từ stacked LR                        │
│  ─────────────────────────────────────────────          │
│  Stacked LR → caller function (map file)                │
└─────────────────────────────────────────────────────────┘
```

**GDB script tự động hóa:**

```python
# fault_analysis.py — GDB Python script
import gdb

def analyze_fault():
    lr = int(gdb.parse_and_eval("$lr"))
    print(f"=== FAULT ANALYSIS ===")
    print(f"EXC_RETURN (LR) = 0x{lr:08X}")

    if lr & 0x4:
        sp = int(gdb.parse_and_eval("$psp"))
        print(f"Using PSP = 0x{sp:08X}")
    else:
        sp = int(gdb.parse_and_eval("$msp"))
        print(f"Using MSP = 0x{sp:08X}")

    regs = ['R0', 'R1', 'R2', 'R3', 'R12', 'LR', 'PC', 'xPSR']
    print(f"\nStacked registers at 0x{sp:08X}:")
    for i, name in enumerate(regs):
        addr = sp + i * 4
        val = int(gdb.parse_and_eval(f"*(unsigned int*)0x{addr:08X}"))
        marker = " ← FAULT INSTRUCTION" if name == 'PC' else ""
        print(f"  {name:5s} = 0x{val:08X}{marker}")

    cfsr = int(gdb.parse_and_eval("*(unsigned int*)0xE000ED28"))
    bfar = int(gdb.parse_and_eval("*(unsigned int*)0xE000ED38"))
    print(f"\nSCB->CFSR = 0x{cfsr:08X}")
    print(f"SCB->BFAR = 0x{bfar:08X}")

analyze_fault()
```

### 8. ❌ Common Mistakes

**Lỗi 1: Đọc nhầm stack (MSP thay vì PSP)**
```
Nếu LR = 0xFFFFFFFD nhưng đọc stack từ MSP:
→ Tất cả stacked registers đều SAI
→ PC, R0-R3 là garbage
→ Debug đi sai hướng hoàn toàn!

LUÔN kiểm tra LR[2] trước khi quyết định MSP hay PSP
```

**Lỗi 2: Quên clear fault status registers**
```c
// Sau khi đọc phải clear (W1C: Write 1 to Clear)
SCB->CFSR = SCB->CFSR;
SCB->HFSR = SCB->HFSR;
// Nếu không clear → fault tiếp theo vẫn thấy old value!
```

**Lỗi 3: Imprecise BusFault — PC không chỉ đúng instruction**
```
SCB->CFSR bit IMPRECISERR = 1:
→ BusFault do write buffer (buffered, phát hiện sau)
→ Stacked PC KHÔNG phải instruction gây lỗi!

Fix: Disable write buffer để chuyển thành precise fault
SCB->ACTLR |= SCB_ACTLR_DISDEFWBUF_Msk;  // Chậm hơn nhưng chính xác
```

**Lỗi 4: Không save dump vào noinit section**
```c
// SAI: dump bị zero sau reset!
uint32_t crash_pc;  // Trong .bss → bị clear khi startup

// ĐÚNG:
__attribute__((section(".noinit")))
uint32_t crash_pc;  // Giữ nguyên giá trị sau reset
```

### 9. 📌 Remember

> **Khi crash: LR → bit[2] → MSP hay PSP → đọc frame → stacked PC là chân lý**

**Quick reference:**

```
1. LR = 0xFFFFFFF?:
   LR[2]=0 → MSP   LR[2]=1 → PSP → đọc frame tại PSP

2. Stack frame offset:
   +0  = R0    +4  = R1    +8  = R2    +12 = R3
   +16 = R12   +20 = LR    +24 = PC★  +28 = xPSR

3. SCB->CFSR decode:
   Bit 9  PRECISERR: BusFault → BFAR hợp lệ
   Bit 15 BFARVALID: BFAR chứa địa chỉ gây lỗi
   Bit 16 UNDEFINSTR: Undefined instruction
   Bit 25 DIVBYZERO: Chia cho 0

4. Map file + stacked PC → tên hàm và dòng code
```

### 10. 🔬 Advanced

**CoreSight và ETM Trace:**

Một số MCU (STM32H7, STM32F7) hỗ trợ **ETM (Embedded Trace Macrocell)**:
- Ghi lại toàn bộ instruction trace
- Replay sequence dẫn đến crash
- Công cụ: Segger Ozone, Lauterbach Trace32, Keil ULINKpro

**ITM (Instrumentation Trace Macrocell) — printf không tốn UART:**

```c
// Setup
CoreDebug->DEMCR |= CoreDebug_DEMCR_TRCENA_Msk;
ITM->TCR |= ITM_TCR_ITMENA_Msk;
ITM->TER = 0x1;  // Enable port 0

// Send character qua SWO pin
void itm_putchar(char c) {
    while (ITM->PORT[0].u32 == 0);
    ITM->PORT[0].u8 = c;
}
```

**CrashCatcher — library tự động hóa crash dump:**

Open-source library tự động:
- Save toàn bộ registers, stack, peripheral state
- Format binary để decode offline
- Hỗ trợ RTOS task context
- GitHub: `adamgreen/CrashCatcher`

---

# PHẦN 3: THỰC CHIẾN — DEBUG, RTOS, ASSEMBLY VÀ MENTAL MODEL

> **Phần này dành cho kỹ sư đã hiểu lý thuyết và muốn áp dụng vào thực tế.**  
> Mỗi chương đều bắt đầu từ vấn đề thực tế, không phải từ lý thuyết.

---

# CHƯƠNG 17: HARDFAULT — PHÂN TÍCH THỰC DỤNG

## 17.1 Tại Sao HardFault Quan Trọng?

HardFault là "cái chết" của firmware. Mọi lỗi nghiêm trọng mà CPU không thể xử lý đều dẫn đến đây:
- Truy cập địa chỉ invalid (NULL pointer, out-of-bounds)
- Undefined instruction execution
- Stack overflow
- Divide by zero (Cortex-M3/M4)
- Unaligned access (nếu không được hỗ trợ)

```
CPU gặp lỗi
      │
      ▼
Có handler đặc thù? (MemManage, BusFault, UsageFault)
      │
   YES│                    NO (hoặc handler bị disable)
      │                         │
      ▼                         ▼
Handler đặc thù          HardFault Handler
được gọi                      │
                               ▼
                    while(1) { } ← firmware đứng ở đây
```

**Mục tiêu của chương này:** Khi HardFault xảy ra, bạn phải đọc được register dump và tìm ra root cause trong vòng < 5 phút.

---

## 17.2 Fault Registers — Checklist Đầy Đủ

### 17.2.1 Stack Frame khi HardFault xảy ra

Khi CPU nhảy vào HardFault handler, hardware tự động push 8 registers lên stack:

```
Stack (growing downward)          Offset từ SP gốc
┌─────────────────────┐
│       xPSR          │  +28 (0x1C)  ← Processor State lúc fault
├─────────────────────┤
│        PC           │  +24 (0x18)  ← ĐỊA CHỈ INSTRUCTION GÂY FAULT
├─────────────────────┤
│        LR           │  +20 (0x14)  ← Return address trước fault
├─────────────────────┤
│        R12          │  +16 (0x10)
├─────────────────────┤
│        R3           │  +12 (0x0C)
├─────────────────────┤
│        R2           │  +8  (0x08)
├─────────────────────┤
│        R1           │  +4  (0x04)
├─────────────────────┤
│        R0           │  +0  (0x00)  ← SP trỏ vào đây
└─────────────────────┘
         ↑
         SP sau khi hardware push
```

> **[SIMPLIFICATION]** Nếu có FPU và đang dùng floating-point, thêm 18 registers FPU (S0-S15, FPSCR) nữa. Cortex-M4F/M7.

### 17.2.2 Bảng Các Fault Registers Quan Trọng

| Register | Địa chỉ (STM32F4) | Tên đầy đủ | Cho biết điều gì |
|----------|-------------------|------------|-----------------|
| **PC** (từ stack) | - | Program Counter | **Instruction nào đang chạy khi fault** |
| **LR** (từ stack) | - | Link Register | Function nào đã gọi function gây fault |
| **SP** | - | Stack Pointer | Stack còn bao nhiêu |
| **xPSR** (từ stack) | - | Processor Status | Mode, Thumb bit, flags |
| **HFSR** | 0xE000ED2C | HardFault Status | Loại HardFault (forced/vector/debug) |
| **CFSR** | 0xE000ED28 | Configurable Fault Status | Tổng hợp MemManage+BusFault+Usage |
| **MMFSR** | 0xE000ED28 (byte 0) | MemManage Fault Status | Chi tiết lỗi memory protection |
| **BFSR** | 0xE000ED29 (byte 1) | BusFault Status | Chi tiết lỗi bus/access |
| **UFSR** | 0xE000ED2A (word) | UsageFault Status | Chi tiết lỗi instruction/alignment |
| **BFAR** | 0xE000ED38 | BusFault Address | **Địa chỉ gây BusFault** (nếu valid) |
| **MMFAR** | 0xE000ED34 | MemManage Fault Address | Địa chỉ gây MemManage fault |

### 17.2.3 Giải Thích Chi Tiết Từng Register

#### HFSR — HardFault Status Register (0xE000ED2C)

```
Bit 31: DEBUGEVT  → Debug event gây ra HardFault (hiếm)
Bit 30: FORCED    → HardFault do fault khác escalate lên (BusFault/MemManage/Usage bị disable)
Bit  1: VECTTBL   → Lỗi khi đọc bảng vector
Bit  0: (reserved)
```

**Quan trọng nhất:** Nếu `FORCED = 1`, nghĩa là BusFault hoặc MemManage hoặc UsageFault đã xảy ra nhưng handler bị disable → bị escalate thành HardFault. Phải đọc CFSR để biết lỗi thực sự.

#### CFSR — Configurable Fault Status Register (0xE000ED28)

```
Bit 31-16: UFSR (UsageFault Status)
Bit 15-8:  BFSR  (BusFault Status)
Bit  7-0:  MMFSR (MemManage Fault Status)

UFSR (bits 31-16):
  Bit 25: DIVBYZERO  → Chia cho 0 (UDIV instruction)
  Bit 24: UNALIGNED  → Unaligned memory access
  Bit 19: NOCP       → No Coprocessor (dùng FPU khi FPU bị disable)
  Bit 18: INVPC      → Invalid PC load (EXC_RETURN bị corrupt)
  Bit 17: INVSTATE   → Invalid state (EPSR.T bit = 0, cố execute ARM mode)
  Bit 16: UNDEFINSTR → Undefined instruction

BFSR (bits 15-8):
  Bit 15: BFARVALID  → BFAR chứa địa chỉ hợp lệ gây fault
  Bit 13: LSPERR     → Fault khi lazy floating-point save
  Bit 12: STKERR     → Fault khi hardware stacking cho exception
  Bit 11: UNSTKERR   → Fault khi hardware unstacking
  Bit 10: IMPRECISERR→ Imprecise fault (buffered write → khó debug!)
  Bit  9: PRECISERR  → Precise fault, BFAR valid
  Bit  8: IBUSERR    → Instruction fetch fault

MMFSR (bits 7-0):
  Bit  7: MMARVALID  → MMFAR chứa địa chỉ hợp lệ
  Bit  5: MLSPERR    → Fault khi lazy FP save
  Bit  4: MSTKERR    → Fault khi stacking cho exception
  Bit  3: MUNSTKERR  → Fault khi unstacking
  Bit  1: DACCVIOL   → Data access violation
  Bit  0: IACCVIOL   → Instruction access violation
```

---

## 17.3 HardFault Handler — Code Debug Chuẩn

```c
// hardfault_handler.c
// Đây là handler dùng để debug - KHÔNG dùng cho production

// Stack frame structure
typedef struct {
    uint32_t r0;
    uint32_t r1;
    uint32_t r2;
    uint32_t r3;
    uint32_t r12;
    uint32_t lr;   // Link Register
    uint32_t pc;   // Program Counter tại thời điểm fault
    uint32_t xpsr; // xPSR
} HardFault_StackFrame_t;

// Fault Status Registers
#define HFSR    (*(volatile uint32_t*)0xE000ED2C)
#define CFSR    (*(volatile uint32_t*)0xE000ED28)
#define MMFAR   (*(volatile uint32_t*)0xE000ED34)
#define BFAR    (*(volatile uint32_t*)0xE000ED38)

void HardFault_Handler_C(uint32_t *stack_ptr, uint32_t lr_value)
{
    HardFault_StackFrame_t *frame = (HardFault_StackFrame_t*)stack_ptr;
    
    // ==========================================================
    // ĐỌC STACK FRAME
    // ==========================================================
    volatile uint32_t stacked_r0   = frame->r0;
    volatile uint32_t stacked_r1   = frame->r1;
    volatile uint32_t stacked_r2   = frame->r2;
    volatile uint32_t stacked_r3   = frame->r3;
    volatile uint32_t stacked_r12  = frame->r12;
    volatile uint32_t stacked_lr   = frame->lr;
    volatile uint32_t stacked_pc   = frame->pc;  // <-- INSTRUCTION GÂY FAULT
    volatile uint32_t stacked_xpsr = frame->xpsr;
    
    // ==========================================================
    // ĐỌC FAULT STATUS REGISTERS
    // ==========================================================
    volatile uint32_t hfsr_val  = HFSR;
    volatile uint32_t cfsr_val  = CFSR;
    volatile uint32_t mmfar_val = MMFAR;
    volatile uint32_t bfar_val  = BFAR;
    
    // ==========================================================
    // PHÂN TÍCH
    // ==========================================================
    // Đặt breakpoint ở đây trong debugger
    // Xem các biến volatile ở trên để phân tích
    
    (void)stacked_r0; (void)stacked_r1; (void)stacked_r2; (void)stacked_r3;
    (void)stacked_r12; (void)stacked_lr; (void)stacked_pc; (void)stacked_xpsr;
    (void)hfsr_val; (void)cfsr_val; (void)mmfar_val; (void)bfar_val;
    
    while (1) { }  // Đứng ở đây để debug
}

// Assembly trampoline để lấy stack pointer đúng
__attribute__((naked))
void HardFault_Handler(void)
{
    __asm volatile(
        // Kiểm tra LR để biết đang dùng MSP hay PSP
        "TST    LR, #4          \n"  // Test bit 2 của EXC_RETURN
        "ITE    EQ              \n"
        "MRSEQ  R0, MSP         \n"  // Nếu bit 2 = 0 → dùng MSP
        "MRSNE  R0, PSP         \n"  // Nếu bit 2 = 1 → dùng PSP
        "MOV    R1, LR          \n"  // Truyền LR vào R1
        "B      HardFault_Handler_C \n"
        : : : "r0", "r1"
    );
}
```

> **[LƯU Ý]** Lý do cần assembly trampoline: HardFault_Handler bị gọi bởi CPU với SP đã bị thay đổi (hardware đã push stack frame). Cần phân biệt MSP/PSP để tìm stack frame đúng. Xem Chương 18 về MSP/PSP.

---

## 17.4 Ba Ví Dụ Thực Tế

### VÍ DỤ 1: NULL Pointer Dereference

#### Symptom
- Firmware chạy được một lúc, sau đó đứng trong `while(1)` của HardFault handler
- Watchdog reset sau vài giây
- Không có log nào trước khi chết

#### Code gây lỗi
```c
typedef struct {
    uint32_t id;
    uint32_t value;
    char     name[16];
} Sensor_t;

Sensor_t *g_sensor = NULL;  // Chưa khởi tạo!

void init_system(void)
{
    // Developer quên gọi: g_sensor = &sensor_instance;
    g_sensor->value = 42;    // CRASH! Ghi vào địa chỉ 0x00000004
}
```

#### Register Dump (trong debugger)

```
=== HARDFAULT REGISTER DUMP ===
--- Stack Frame (stacked by hardware) ---
R0   = 0x0000002A    (42 decimal - giá trị đang ghi)
R1   = 0x00000000    
R2   = 0x00000000
R3   = 0x00000000
R12  = 0x00000000
LR   = 0x080012F5    (return address: init_system() caller)
PC   = 0x080012C4    (← ĐÂY là instruction gây fault)
xPSR = 0x01000000    (Thumb mode, no active exception)

--- Fault Status Registers ---
HFSR = 0x40000000    (FORCED = 1 → escalated từ fault khác)
CFSR = 0x00008200    
  BFSR = 0x82:
    Bit 15 (BFARVALID) = 1  → BFAR chứa địa chỉ hợp lệ
    Bit  9 (PRECISERR) = 1  → Lỗi precise, địa chỉ chính xác
BFAR = 0x00000004    (← ĐÂY là địa chỉ bị truy cập sai)
MMFAR = 0xXXXXXXXX  (không valid)
```

#### Suy Luận Từng Bước

```
Bước 1: Đọc HFSR
  FORCED = 1 → HardFault do BusFault escalate
  → Phải đọc CFSR

Bước 2: Đọc CFSR
  BFSR.PRECISERR = 1, BFSR.BFARVALID = 1
  → Lỗi BusFault precise, địa chỉ trong BFAR

Bước 3: Đọc BFAR
  BFAR = 0x00000004
  → Địa chỉ 0x4 bị truy cập!
  → 0x0 là NULL, 0x4 là NULL + offset 4 bytes
  → Struct có field ở offset 4 = field "value" (sau uint32_t id)
  → Code đang ghi vào NULL->value!

Bước 4: Đọc PC
  PC = 0x080012C4
  → Trong debugger: xem disassembly tại 0x080012C4
  → Thấy: STR R0, [R1, #4]  ← ghi vào R1+4
  → R1 = NULL (0x00000000), R1+4 = 0x4 = BFAR

Bước 5: Tìm nguồn trong C
  Trong debugger đặt breakpoint tại 0x080012C4
  Hoặc dùng: addr2line -e firmware.elf 0x080012C4
  → init_system.c:line 14: g_sensor->value = 42;
```

#### Root Cause
`g_sensor` chưa được khởi tạo (vẫn là NULL). Code ghi vào `NULL->value` = địa chỉ `0x00000004`.

#### Fix
```c
static Sensor_t sensor_instance = {0};

void init_system(void)
{
    g_sensor = &sensor_instance;  // Khởi tạo trước khi dùng
    g_sensor->value = 42;         // Bây giờ OK
}

// Hoặc defensive programming:
void update_sensor(Sensor_t *sensor, uint32_t val)
{
    if (sensor == NULL) {
        // Log error
        return;
    }
    sensor->value = val;
}
```

---

### VÍ DỤ 2: Stack Overflow

#### Symptom
- Firmware crash sau khi gọi hàm đệ quy sâu, hoặc khi có mảng lớn trên stack
- Đôi khi crash xảy ra ở instruction hoàn toàn vô hại (ADD, MOV...)
- Dữ liệu global bị corrupt không rõ lý do

#### Code gây lỗi
```c
// Stack size mặc định STM32: 0x400 = 1024 bytes
// Mảng này chiếm 4096 bytes → TRÀN STACK!
void process_data(void)
{
    uint8_t buffer[4096];  // 4KB trên stack
    
    for (int i = 0; i < 4096; i++) {
        buffer[i] = compute_value(i);
    }
    // ... sử dụng buffer
}
```

#### Register Dump

```
=== HARDFAULT REGISTER DUMP ===
--- Stack Frame ---
R0   = 0x20000000    
R1   = 0x00000001
R2   = 0x00000042
R3   = 0x20000000
R12  = 0xDEADBEEF   ← GIÁ TRỊ RÁC (stack bị corrupt!)
LR   = 0x20001234   ← LR trỏ vào RAM (!!) → stack corrupt đã ghi đè LR
PC   = 0x0800ABCD   (một hàm hoàn toàn vô hại)
xPSR = 0x01000000

--- Fault Status Registers ---
HFSR = 0x40000000   (FORCED = 1)
CFSR = 0x00001000
  BFSR = 0x10:
    Bit 12 (STKERR) = 1  → Fault khi HARDWARE STACKING exception!
    ← Hardware cố push stack frame nhưng stack đã tràn vào vùng invalid
BFAR = 0x1FFFFC00   ← Dưới stack bottom (0x20000000)!
```

#### Suy Luận Từng Bước

```
Bước 1: CFSR.BFSR.STKERR = 1
  → Lỗi khi hardware đang push exception stack frame
  → Nghĩa là: một interrupt/exception xảy ra, CPU cố push 8 registers
    nhưng SP đã xuống quá thấp → không còn chỗ trên stack

Bước 2: BFAR = 0x1FFFFC00
  → Địa chỉ dưới 0x20000000 (stack bottom của RAM)
  → CPU cố ghi vào vùng không tồn tại

Bước 3: LR = 0x20001234
  → LR trỏ vào RAM thay vì Flash (0x08000000...)
  → Stack đã tràn và ghi đè lên vùng mà LR được save trước đó
  → Dấu hiệu điển hình của STACK OVERFLOW

Bước 4: Tính toán
  STM32F4 stack: bắt đầu từ 0x20020000, kích thước 0x400
  → Stack bottom = 0x20020000 - 0x400 = 0x2001FC00
  → Còn lấy thêm 4096 bytes → SP = 0x2001FC00 - 0x1000 = 0x2001EC00
  → Vượt quá stack bottom → tràn vào BSS/Data segment!
```

#### Root Cause
Mảng `uint8_t buffer[4096]` khai báo trên stack vượt quá stack size (1024 bytes). Stack tràn xuống vùng RAM của `.bss` và `.data`, corrupt dữ liệu global.

#### Fix
```c
// Option 1: Static allocation
static uint8_t buffer[4096];  // Không dùng stack

// Option 2: Heap allocation
void process_data(void)
{
    uint8_t *buffer = malloc(4096);
    if (buffer == NULL) { return; }
    // ... dùng buffer
    free(buffer);
}

// Option 3: Tăng stack size (startup_stm32f4xx.s hoặc linker script)
// Stack_Size EQU 0x2000   ; Tăng từ 0x400 lên 0x2000

// Option 4: Stack overflow detection - MPU hoặc stack canary
#define STACK_CANARY 0xDEADBEEF
uint32_t stack_canary __attribute__((section(".stack_bottom"))) = STACK_CANARY;

void check_stack_integrity(void)
{
    if (stack_canary != STACK_CANARY) {
        // Stack overflow detected!
        Error_Handler();
    }
}
```

---

### VÍ DỤ 3: Corrupted Return Address

#### Symptom
- Firmware crash khi return từ function
- PC nhảy đến địa chỉ ngẫu nhiên, không phải function nào cả
- Thường xảy ra sau khi có buffer overflow (viết quá array boundary)

#### Code gây lỗi
```c
void vulnerable_function(const char *input)
{
    char local_buf[16];
    
    // BUG: Không kiểm tra length!
    // Nếu strlen(input) > 15, sẽ tràn local_buf
    // và ghi đè lên LR đã được save trên stack
    strcpy(local_buf, input);  // UNSAFE!
    
    // ... xử lý local_buf
}  // ← CRASH khi return! CPU load LR bị corrupt làm PC
```

#### Stack layout trước khi crash
```
Stack (higher addr = older)
┌──────────────────────────┐ ← SP ban đầu trước khi vào function
│  LR (saved by PUSH)      │  = 0x080023AB (return to caller)
│  R4, R5... (saved)       │
├──────────────────────────┤
│  local_buf[15]           │ ← char local_buf[16]
│  ...                     │
│  local_buf[0]            │ ← strcpy bắt đầu từ đây
├──────────────────────────┤ ← SP sau khi function enter
```

Khi `input` quá dài:
```
strcpy ghi bytes 0..15: vào local_buf[0..15]  → OK
strcpy ghi byte 16:     vào địa chỉ ngay sau local_buf
strcpy ghi byte 20..23: ghi đè LR!
strcpy ghi byte 24+:    ghi đè R4, R5, v.v.
```

#### Register Dump

```
=== HARDFAULT REGISTER DUMP ===
--- Stack Frame ---
R0   = 0x20001A00
R1   = 0x00000010
R2   = 0x20001A10
R3   = 0x00000000
R12  = 0x41414141   ← 'AAAA' → Input là chuỗi 'A' lặp lại!
LR   = 0x41414141   ← LR bị ghi đè bằng 'AAAA'
PC   = 0x41414141   ← CPU cố execute tại 0x41414141 → không tồn tại!
xPSR = 0x01000000

--- Fault Status Registers ---
HFSR = 0x40000000   (FORCED)
CFSR = 0x00020000
  UFSR:
    Bit 17 (INVSTATE) = 1 → Invalid state!
```

#### Suy Luận Từng Bước
```
Bước 1: PC = 0x41414141 = 'AAAA' (ASCII)
  → PC chứa giá trị ASCII 'A' lặp lại
  → Đây không phải địa chỉ hợp lệ
  → Ai đặt PC = 'AAAA'? → CPU load từ LR khi return

Bước 2: LR = 0x41414141 = 'AAAA'
  → LR bị ghi đè bằng 'AAAA'
  → LR được đặt trên stack khi PUSH
  → Stack bị ghi đè bằng 'AAAA'

Bước 3: R12 = 0x41414141
  → R12 cũng bị ghi đè → buffer overflow trên stack

Bước 4: Tìm code dùng strcpy/memcpy không kiểm tra length
  → vulnerable_function() với char local_buf[16]
  → 'A' * 32 bytes tràn qua buf, ghi đè saved registers
```

#### Root Cause
`strcpy()` không kiểm tra độ dài, tràn `local_buf[16]`, ghi đè `LR` trên stack bằng dữ liệu từ `input`.

#### Fix
```c
void safe_function(const char *input)
{
    char local_buf[16];
    
    // Option 1: strncpy
    strncpy(local_buf, input, sizeof(local_buf) - 1);
    local_buf[sizeof(local_buf) - 1] = '\0';
    
    // Option 2: snprintf
    snprintf(local_buf, sizeof(local_buf), "%s", input);
    
    // Option 3: Kiểm tra trước
    if (strlen(input) >= sizeof(local_buf)) {
        return;  // Error
    }
    strcpy(local_buf, input);  // Now safe
}
```

---

## 17.5 Debug Checklist — HardFault trong 5 Phút

```
HardFault xảy ra
     │
     ▼
[1] Đọc HFSR
     ├── FORCED = 1? → Đọc CFSR
     ├── VECTTBL = 1? → Vector table corrupt/invalid address
     └── DEBUGEVT = 1? → Debug event (hiếm)
     │
     ▼
[2] Đọc CFSR
     ├── BFSR.PRECISERR? → Đọc BFAR → địa chỉ truy cập sai
     ├── BFSR.IMPRECISERR? → Khó debug (buffered write), flush write buffer
     ├── BFSR.STKERR? → Stack overflow (SP quá thấp khi exception)
     ├── UFSR.DIVBYZERO? → Chia cho 0, tìm phép chia trong code
     ├── UFSR.INVSTATE? → PC invalid hoặc Thumb bit sai
     ├── UFSR.UNDEFINSTR? → Execute tại vùng invalid
     ├── UFSR.NOCP? → Dùng FPU khi chưa enable
     └── MMFSR.DACCVIOL? → MPU violation
     │
     ▼
[3] Đọc PC từ stack frame
     → Tìm instruction gây fault trong disassembly
     → addr2line -e firmware.elf <PC_value>
     │
     ▼
[4] Đọc LR từ stack frame
     → Tìm caller (hàm nào đã gọi hàm gây fault)
     │
     ▼
[5] Kiểm tra SP hợp lệ không
     → SP phải nằm trong vùng RAM được cấp cho stack
     → SP lệch nhiều = stack overflow
```

---

# CHƯƠNG 18: RTOS CONTEXT SWITCH

## 18.1 Tại Sao Cần Hiểu Context Switch?

Khi bạn debug RTOS application:
- Task A đang chạy, nhưng trong debugger lại thấy Task B
- Local variable của Task A bị thay đổi
- Stack usage báo 95% trong một task
- Task không chạy đúng priority

Tất cả đều liên quan đến **context switch** — cơ chế cho phép nhiều task "chạy song song" trên một CPU.

## 18.2 Khái Niệm Context

**Context** của một task = tất cả thông tin cần thiết để resume task đó:

```
Task Context = {
    R0, R1, R2, R3,        // General purpose registers
    R4, R5, R6, R7,        // Callee-saved registers
    R8, R9, R10, R11,      // Callee-saved registers
    R12,                    // Scratch register
    SP (Stack Pointer),    // Con trỏ stack của task
    LR (Link Register),    // Return address
    PC (Program Counter),  // Điểm task đang thực thi
    xPSR                   // Processor state (flags, mode)
}
```

Lưu context = save các registers này.  
Restore context = load các registers này.

## 18.3 MSP vs PSP — Quyết Định Thiết Kế Quan Trọng

Cortex-M có HAI stack pointers:

```
MSP (Main Stack Pointer)   — Reset value: top of stack từ vector table
PSP (Process Stack Pointer) — Default value: undefined

                    CONTROL register bit 1
                    ┌─────┬───────────────────────────┐
                    │  0  │ Thread mode dùng MSP       │
                    │  1  │ Thread mode dùng PSP ★     │
                    └─────┴───────────────────────────┘
                              ★ RTOS dùng mode này
```

### Tại Sao RTOS Dùng PSP Cho Task?

```
Không có RTOS (bare metal):
┌──────────────────────────────────────────────┐
│              SINGLE STACK                     │
│  [main code] [ISR frames] [function calls]   │
│              MSP dùng cho tất cả             │
└──────────────────────────────────────────────┘

Có RTOS:
┌──────────────────────┐  ┌──────────────────────┐
│    KERNEL STACK      │  │    TASK A STACK       │
│  [interrupt frames]  │  │  [task A locals]      │
│  [OS internal]       │  │  [task A context]     │
│     MSP              │  │      PSP              │
└──────────────────────┘  └──────────────────────┘
                            ┌──────────────────────┐
                            │    TASK B STACK       │
                            │  [task B locals]      │
                            │  [task B context]     │
                            │      PSP (switched)   │
                            └──────────────────────┘
```

**Lợi ích:**
1. **Isolation:** Lỗi trong task không corrupt kernel stack
2. **Stack monitoring:** Biết chính xác stack usage từng task
3. **MPU protection:** Có thể protect mỗi task stack riêng
4. **Simplicity:** Kernel luôn dùng MSP → dễ debug kernel

### Exception/Interrupt Luôn Dùng MSP

```
CONTROL.SPSEL = 1 (Thread mode dùng PSP)

Task A đang chạy (PSP = 0x20007F00)
         │
         ▼ Interrupt xảy ra
CPU tự động switch về MSP
(EXC_RETURN trong LR cho biết cần switch lại PSP)
         │
         ▼ ISR chạy trên MSP (Kernel stack)
         │
         ▼ ISR return
CPU đọc EXC_RETURN, switch về PSP
Task A tiếp tục chạy (PSP = 0x20007F00)
```

**EXC_RETURN** — Magic value trong LR khi vào exception:

```
0xFFFFFFF9: Return to Thread mode, use MSP
0xFFFFFFFD: Return to Thread mode, use PSP ← RTOS tasks
0xFFFFFFF1: Return to Handler mode, use MSP ← nested interrupts
```

## 18.4 Context Switch Flow Chi Tiết

### Hardware Auto-Save (xảy ra tự động khi interrupt)

```c
// Khi Task A đang chạy và SysTick interrupt xảy ra:
// Hardware tự động push lên PSP của Task A:
//   [xPSR, PC, LR, R12, R3, R2, R1, R0]  (8 registers = 32 bytes)
```

### Software Save by RTOS (phần RTOS phải làm)

```c
// Trong SysTick_Handler (PendSV_Handler thực ra):
// RTOS phải tự save các registers còn lại:
//   [R11, R10, R9, R8, R7, R6, R5, R4]  (8 registers = 32 bytes)
```

### Tại Sao Dùng PendSV Cho Context Switch?

```
SysTick → Scheduler chạy → Tìm task tiếp theo
        → Trigger PendSV (lowest priority interrupt)
        → Chờ tất cả interrupt khác xử lý xong
        → PendSV_Handler: thực hiện context switch
```

PendSV được dùng vì nó là interrupt priority thấp nhất, đảm bảo context switch chỉ xảy ra khi không có interrupt nào khác đang chạy.

## 18.5 Full Context Switch — Assembly Thực Tế

```asm
;=== PHASE 1: Hardware auto-push khi interrupt ===
; CPU hardware tự động:
;   Push [xPSR, PC, LR, R12, R3, R2, R1, R0] vào PSP (Task A)
;   Switch sang MSP (kernel mode)

;=== PHASE 2: PendSV Handler (RTOS context switch) ===

PendSV_Handler:
    ; B1: Đọc PSP của Task A (task đang bị preempt)
    MRS    R0, PSP

    ; B2: Save R4-R11 của Task A vào stack của Task A
    STMDB  R0!, {R4-R11}       ; R0 giảm 32 bytes, save R11..R4

    ; B3: Save PSP mới của Task A vào TCB
    LDR    R1, =current_task
    LDR    R1, [R1]
    STR    R0, [R1]            ; Lưu SP vào TCB->sp

    ; B4: Load next_task
    LDR    R1, =next_task
    LDR    R1, [R1]
    LDR    R0, [R1]            ; R0 = next_task->sp

    ; B5: Update current_task = next_task
    LDR    R2, =current_task
    STR    R1, [R2]

    ; B6: Restore R4-R11 của Task B từ stack của Task B
    LDMIA  R0!, {R4-R11}       ; Load R4..R11, R0 tăng 32 bytes

    ; B7: Cập nhật PSP để trỏ vào Task B stack
    MSR    PSP, R0

    ; B8: Return - CPU hardware sẽ restore R0-R3, R12, LR, PC, xPSR
    ORR    LR, #0xD            ; EXC_RETURN = 0xFFFFFFFD
    BX     LR
```

## 18.6 TCB — Task Control Block

```c
typedef struct {
    uint32_t *sp;          // Stack pointer (PHẢI là member đầu tiên!)
    uint32_t  priority;
    TaskState state;
    char      name[16];
    // ... các field khác
} TCB_t;

// Vì sao sp phải là member đầu tiên?
// Assembly code: LDR R0, [R1]  → load TCB_t.sp
// Nếu sp ở offset 0: [R1] + 0 → đúng
// Nếu sp ở offset N: cần LDR R0, [R1, #N] → phức tạp hơn
```

## 18.7 Debug RTOS Issues với Register Knowledge

```
Vấn đề: Task A đọc sai dữ liệu sau khi resume

Kiểm tra:
1. Dừng tại điểm Task A resume
2. Xem PSP đang trỏ đúng vào stack Task A chưa
3. Kiểm tra R4-R11 đã được restore đúng chưa
4. Kiểm tra PC đúng vị trí Task A dừng không

Vấn đề: Context switch loop (task liên tục bị preempt)

Kiểm tra:
1. SysTick frequency (quá cao = quá nhiều context switch)
2. Task priority (hai task cùng priority có thể round-robin nhanh)
3. Task đang block trên mutex/semaphore

Vấn đề: Stack corruption trong RTOS task

Kiểm tra:
1. TCB stack watermark: fill stack với pattern 0xA5A5A5A5
2. Sau thời gian chạy, đếm số 0xA5A5A5A5 còn lại
3. FreeRTOS: uxTaskGetStackHighWaterMark()
```

---

# CHƯƠNG 19: CÁC ASSEMBLY INSTRUCTION CẦN BIẾT

## 19.1 Tại Sao Cần Biết Assembly?

- Đọc disassembly khi debug (PC trỏ đến instruction nào)
- Hiểu compiler optimization (code C thành assembly gì)
- Viết startup code, context switch, critical section
- Tối ưu performance-critical code

> **[CẦN BIẾT]** Phần này. Không cần thuộc, nhưng cần đọc được.
> **[KHÔNG CẦN]** Viết entire firmware bằng assembly.

## 19.2 Nhóm 1: Data Movement

### MOV — Move

```
Syntax:    MOV Rd, <src>
Purpose:   Copy giá trị vào register
Input:     Immediate hoặc register
Output:    Rd = src
Flags:     MOVS: set N, Z; không set C, V

Ví dụ:
  MOV  R0, #42         ; R0 = 42
  MOV  R0, #0xFF       ; R0 = 255
  MOV  R1, R0          ; R1 = R0
  MOVS R0, #0          ; R0 = 0, Z flag = 1

C tương đương:
  uint32_t r0 = 42;
  uint32_t r1 = r0;
```

### LDR — Load Register

```
Syntax:    LDR Rd, [Rn]          ; Load từ địa chỉ Rn
           LDR Rd, [Rn, #offset] ; Load từ địa chỉ Rn + offset
           LDR Rd, =<value>       ; Pseudo: load literal value
Purpose:   Đọc dữ liệu từ bộ nhớ vào register
Input:     Địa chỉ bộ nhớ
Output:    Rd = Memory[Rn + offset]
Flags:     Không ảnh hưởng

Ví dụ:
  LDR  R0, [R1]         ; R0 = *(uint32_t*)R1
  LDR  R0, [R1, #4]     ; R0 = *(uint32_t*)(R1 + 4)
  LDR  R0, [R1, R2]     ; R0 = *(uint32_t*)(R1 + R2)
  LDR  R0, =0xDEADBEEF  ; Pseudo: đặt value vào literal pool

Variants:
  LDRB  Rd, [Rn]  ; Load byte (zero-extend)
  LDRH  Rd, [Rn]  ; Load halfword (zero-extend)
  LDRSB Rd, [Rn]  ; Load signed byte (sign-extend)
  LDRSH Rd, [Rn]  ; Load signed halfword (sign-extend)

C tương đương:
  uint32_t r0 = *((uint32_t*)R1);      // LDR R0, [R1]
  uint32_t r0 = *((uint32_t*)(R1+4));  // LDR R0, [R1, #4]
```

### STR — Store Register

```
Syntax:    STR Rd, [Rn]
           STR Rd, [Rn, #offset]
Purpose:   Ghi dữ liệu từ register vào bộ nhớ
Input:     Rd (data), Rn (địa chỉ)
Output:    Memory[Rn + offset] = Rd
Flags:     Không ảnh hưởng

Ví dụ:
  STR  R0, [R1]         ; *(uint32_t*)R1 = R0
  STR  R0, [R1, #8]     ; *(uint32_t*)(R1 + 8) = R0
  STRB R0, [R1]         ; *(uint8_t*)R1 = R0 (chỉ byte thấp nhất)
  STRH R0, [R1]         ; *(uint16_t*)R1 = R0

C tương đương:
  *((uint32_t*)R1) = r0;         // STR R0, [R1]
  *((uint32_t*)(R1+8)) = r0;     // STR R0, [R1, #8]
```

### PUSH / POP — Stack Operations

```
Syntax:    PUSH {register_list}
           POP  {register_list}
Purpose:   Save/restore registers lên/từ stack
Input:     Register list
Output:    SP giảm/tăng tương ứng (Full Descending Stack)

PUSH {R4, R5, LR}    ; SP -= 12; [SP]=R4, [SP+4]=R5, [SP+8]=LR
POP  {R4, R5, PC}    ; R4,R5,PC=[SP],[SP+4],[SP+8]; SP += 12
                     ; POP {PC} = RETURN FUNCTION!

C tương đương (PUSH {R4, LR}):
  stack[--sp] = LR;
  stack[--sp] = R4;

C tương đương (POP {R4, PC}):
  R4 = stack[sp++];
  PC = stack[sp++];  // ← RETURN
```

### STMDB / LDMIA — Store/Load Multiple (dùng trong context switch)

```
STMDB R0!, {R4-R11}
  ; Store Multiple, Decrement Before
  ; Lưu R4..R11 vào stack, R0 giảm 32 bytes

LDMIA R0!, {R4-R11}
  ; Load Multiple, Increment After
  ; Load R4..R11, R0 tăng 32 bytes
```

---

## 19.3 Nhóm 2: Arithmetic

### ADD / ADDS — Addition

```
Syntax:    ADD  Rd, Rn, <op2>   ; No flag update
           ADDS Rd, Rn, <op2>   ; Update flags (N, Z, C, V)
Purpose:   Cộng hai giá trị
Flags (ADDS):
  N: set nếu kết quả < 0 (bit 31 = 1)
  Z: set nếu kết quả = 0
  C: set nếu carry out (unsigned overflow)
  V: set nếu signed overflow

Ví dụ:
  ADD  R0, R1, R2      ; R0 = R1 + R2
  ADD  R0, R0, #4      ; R0 = R0 + 4
  ADDS R0, R1, R2      ; R0 = R1 + R2, update flags
  ADC  R0, R1, R2      ; R0 = R1 + R2 + Carry (64-bit add)

C tương đương:
  r0 = r1 + r2;        // ADD
  r0 = r0 + 4;         // ADD R0, R0, #4
```

### SUB / SUBS — Subtraction

```
Syntax:    SUB  Rd, Rn, <op2>
           SUBS Rd, Rn, <op2>
Purpose:   Trừ
Output:    Rd = Rn - op2
Flags (SUBS): N, Z, C (borrow!), V
  C = 1: NO borrow; C = 0: borrow xảy ra

Ví dụ:
  SUB  R0, R1, R2      ; R0 = R1 - R2
  SUB  SP, SP, #0x20   ; Allocate 32 bytes stack
  SUBS R0, R0, #1      ; R0--, set Z nếu = 0 (dùng trong loop)
```

### MUL — Multiply

```
Syntax:    MUL Rd, Rn, Rm
Purpose:   Nhân 32-bit × 32-bit → kết quả 32-bit thấp
Output:    Rd = (Rn × Rm)[31:0]

Ví dụ:
  MUL  R0, R1, R2      ; R0 = R1 * R2 (lower 32 bits)
  SMULL R0, R1, R2, R3 ; [R1:R0] = R2 × R3 (signed 64-bit)
  UMULL R0, R1, R2, R3 ; [R1:R0] = R2 × R3 (unsigned 64-bit)

C tương đương:
  r0 = (uint32_t)(r1 * r2);
  int64_t result = (int64_t)r2 * r3; // SMULL
```

---

## 19.4 Nhóm 3: Comparison và Branch

### CMP — Compare

```
Syntax:    CMP Rn, <op2>
Purpose:   So sánh (Rn - op2), chỉ update flags, không ghi kết quả
Flags:     N, Z, C, V (giống SUBS)

Ví dụ:
  CMP R0, #0           ; Set Z nếu R0 == 0
  CMP R0, R1           ; Set Z nếu R0 == R1

C tương đương:
  // CMP R0, #5 + BEQ label → if (r0 == 5) goto label
```

### TST — Test Bits

```
Syntax:    TST Rn, <op2>
Purpose:   AND nhưng chỉ update flags (Z = 1 nếu AND result = 0)

Ví dụ:
  TST R0, #0x01        ; Test bit 0: Z=1 nếu bit 0 = 0

C tương đương:
  if (r0 & 0x01) { ... }   // TST R0, #0x01 + BNE
```

### Branch Instructions

```
B  <label>     ; Unconditional branch
BEQ <label>    ; Branch if Equal (Z = 1)
BNE <label>    ; Branch if Not Equal (Z = 0)
BGT <label>    ; Branch if Greater Than (signed)
BLT <label>    ; Branch if Less Than (signed)
BGE <label>    ; Branch if Greater or Equal (signed)
BLE <label>    ; Branch if Less or Equal (signed)
BHI <label>    ; Branch if Higher (unsigned)
BLO <label>    ; Branch if Lower (unsigned)
BCS <label>    ; Branch if Carry Set
BCC <label>    ; Branch if Carry Clear
BMI <label>    ; Branch if Minus (N=1)
BPL <label>    ; Branch if Plus (N=0)

Ví dụ - for loop:
  MOV  R0, #0          ; i = 0
loop:
  CMP  R0, #10         ; i < 10?
  BGE  loop_end        ; if i >= 10: exit
  ; loop body
  ADD  R0, R0, #1      ; i++
  B    loop            ; goto loop
loop_end:
```

### BL / BX / BLX — Call và Return

```
BL <label>   ; Function call: LR = PC+4, PC = label
BX LR        ; Return từ function: PC = LR
BX Rm        ; Branch đến địa chỉ trong register (function pointer)
BLX Rm       ; Call function pointer: LR = PC+4, PC = Rm

Ví dụ:
  BL foo           ; Call foo()
  BX LR            ; return;
  LDR R0, =fp
  BLX R0           ; (*fp)();
```

---

## 19.5 Nhóm 4: Bit Manipulation

```
AND{S} Rd, Rn, <op2>   ; Rd = Rn & op2    (mask bits)
ORR{S} Rd, Rn, <op2>   ; Rd = Rn | op2    (set bits)
EOR{S} Rd, Rn, <op2>   ; Rd = Rn ^ op2    (toggle bits)
BIC{S} Rd, Rn, <op2>   ; Rd = Rn & ~op2   (clear bits)
LSL{S} Rd, Rn, #n      ; Rd = Rn << n     (shift left, fill 0)
LSR{S} Rd, Rn, #n      ; Rd = Rn >> n     (shift right, fill 0)
ASR{S} Rd, Rn, #n      ; Rd = Rn >> n     (arithmetic, fill sign)

Ví dụ thực tế:
  ORR  R0, R0, #(1<<5) ; Set bit 5:   r0 |= (1<<5)
  BIC  R0, R0, #(1<<5) ; Clear bit 5: r0 &= ~(1<<5)
  EOR  R0, R0, #(1<<3) ; Toggle bit 3: r0 ^= (1<<3)
  AND  R0, R0, #0x0F   ; Mask 4 bits: r0 &= 0x0F
  LSL  R0, R1, #3      ; Multiply by 8: r0 = r1 << 3
  LSR  R0, R1, #2      ; Divide by 4: r0 = r1 >> 2 (unsigned)
  ASR  R0, R1, #1      ; Signed divide by 2: r0 = (int)r1 >> 1
```

---

## 19.6 Nhóm 5: Special Instructions

```
MRS Rd, <special>    ; Đọc special register vào Rd
MSR <special>, Rn    ; Ghi Rn vào special register
  Special: APSR, IPSR, EPSR, PRIMASK, FAULTMASK,
           BASEPRI, CONTROL, MSP, PSP

CPSID I    ; Disable interrupts (PRIMASK = 1)
CPSIE I    ; Enable interrupts  (PRIMASK = 0)

ISB        ; Instruction Synchronization Barrier (flush pipeline)
DSB        ; Data Synchronization Barrier (wait memory writes)
DMB        ; Data Memory Barrier (memory ordering)

WFI        ; Wait For Interrupt (sleep until interrupt)
WFE        ; Wait For Event (sleep until event/interrupt)

Ví dụ:
  MRS  R0, PRIMASK     ; R0 = interrupt mask state
  CPSID I              ; Enter critical section
  ; ... critical code ...
  CPSIE I              ; Exit critical section
  
  STR  R0, [R1]        ; Write peripheral
  DSB                  ; Ensure write completes
  
  MSR  CONTROL, R0     ; Change CONTROL
  ISB                  ; Ensure CONTROL takes effect
```

---

# CHƯƠNG 20: 15 COMMON MISCONCEPTIONS

## Tổng Quan

Dưới đây là 15 hiểu lầm phổ biến nhất về CPU registers và ARM Cortex-M. Mỗi kỹ sư Embedded đều đã từng mắc ít nhất một trong số này.

---

### MISCONCEPTION #1: "PC luôn chứa địa chỉ instruction đang thực thi"

```
❌ HIỂU SAI:
"Khi CPU đang execute instruction tại 0x08001000,
 thì PC = 0x08001000"

✅ HIỂU ĐÚNG:
PC = địa chỉ instruction SẼ được fetch TIẾP THEO (do pipeline).
Trên Cortex-M3/M4 (3-stage pipeline: Fetch-Decode-Execute):
  Đang Execute tại 0x08001000
  → PC = 0x08001008 (đã fetch instruction +4 và +8 bytes trước)

NHƯNG khi hardware lưu PC vào stack frame khi exception:
  → PC saved = địa chỉ instruction BỊ INTERRUPTED (instruction gây lỗi)
  → Đây là giá trị bạn dùng để debug!
```

**Ví dụ:**
```c
void foo(void) {
    // 0x08001000: PUSH {R4, LR}
    // 0x08001002: MOV R4, #5
    // 0x08001004: BL bar  ← gây crash
    // 0x08001008: (next instruction)
    bar();          // Nếu crash TRONG bar(), LR = 0x08001009
}
```

---

### MISCONCEPTION #2: "LR chỉ chứa return address"

```
❌ HIỂU SAI:
"LR = return address, đơn giản vậy thôi"

✅ HIỂU ĐÚNG:
LR có nhiều vai trò khác nhau:
1. Return address sau BL/BLX (vai trò thông thường)
2. EXC_RETURN khi đang trong exception handler
   (giá trị đặc biệt 0xFFFFFFF1/FD/F9)
3. Có thể là UNDEFINED nếu function không call function khác
   (leaf function → compiler không save/restore LR)
4. Trong RTOS: LR của task stack frame trỏ vào "task exit" handler
```

**Ví dụ:**
```c
// Leaf function: compiler KHÔNG push LR
void led_toggle(void) {
    GPIOA->ODR ^= (1<<5);  // Không call function nào khác
    // Assembly: LDR/EOR/STR, BX LR (dùng LR trực tiếp)
}

// Non-leaf: compiler PUSH LR, POP PC
void blink(void) {
    led_toggle();  // BL → LR bị thay đổi
    // Assembly: PUSH {LR}, BL led_toggle, POP {PC}
}
```

---

### MISCONCEPTION #3: "SP chỉ là biến địa chỉ bình thường"

```
❌ HIỂU SAI:
"SP là uint32_t chứa địa chỉ, có thể set tùy ý"

✅ HIỂU ĐÚNG:
SP có những ràng buộc nghiêm ngặt:
1. Phải WORD-ALIGNED (chia hết cho 4) mọi lúc
2. Phải DOUBLE-WORD ALIGNED (chia hết cho 8) khi vào exception
3. Phải trỏ vào vùng RAM hợp lệ
4. Có 2 SP: MSP và PSP (chỉ 1 cái active tại 1 thời điểm)
5. Nhiều instructions giả định SP tuân theo Full Descending convention
```

---

### MISCONCEPTION #4: "R0-R3 luôn chứa function arguments"

```
❌ HIỂU SAI:
"Sau khi gọi function, R0-R3 là arguments tôi đã truyền vào"

✅ HIỂU ĐÚNG:
R0-R3 là CALLER-SAVED (scratch) registers:
- R0: argument 1 VÀ return value
- R1: argument 2 VÀ bị phá sau function call
- R2: argument 3 VÀ bị phá sau function call
- R3: argument 4 VÀ bị phá sau function call

Sau khi function return, R0-R3 có thể chứa bất kỳ giá trị nào!
Chỉ R0 (và R1 cho 64-bit return) có giá trị xác định = return value.
```

**Ví dụ:**
```c
int result = foo(1, 2, 3, 4);  // R0=1, R1=2, R2=3, R3=4 trước BL
// Sau khi foo() return:
//   R0 = return value của foo()
//   R1, R2, R3 = UNDEFINED (có thể bị foo thay đổi)
//   R4-R11 = PRESERVED (foo phải restore nếu có thay đổi)
```

---

### MISCONCEPTION #5: "xPSR chỉ chứa Zero Flag"

```
❌ HIỂU SAI:
"xPSR chỉ là flags N, Z, C, V"

✅ HIỂU ĐÚNG:
xPSR = APSR | IPSR | EPSR (3 registers cùng 1 địa chỉ)

Bit 31: N (Negative flag)
Bit 30: Z (Zero flag)
Bit 29: C (Carry flag)
Bit 28: V (Overflow flag)
Bit 27: Q (Saturation flag, Cortex-M4)
Bit 24: T (Thumb execution state) ← CRITICAL!
         T=1: Thumb mode (bắt buộc trên Cortex-M)
         T=0: ARM mode → INVSTATE fault!
Bit 8-0: Exception number (0=Thread, 1-15=system, 16+=IRQ)

xPSR = 0x01000000 → Thread mode, Thumb, no exception
xPSR = 0x01000010 → Exception #16 = IRQ0 đang active
```

---

### MISCONCEPTION #6: "CPU thực thi trực tiếp C code"

```
❌ HIỂU SAI:
"CPU hiểu và chạy C code"

✅ HIỂU ĐÚNG:
CPU chỉ hiểu machine code (binary 0/1).
C code → Compiler → Assembly → Assembler → Machine code → CPU
```

**Ví dụ:**
```c
a = b + c;  // 1 dòng C → có thể 1-4+ instructions:

// -O0:
LDR R0, [SP, #8]    ; Load b
LDR R1, [SP, #4]    ; Load c
ADD R0, R0, R1      ; R0 = b + c
STR R0, [SP, #0]    ; Store a

// -O2 (b, c đã trong registers):
ADD R0, R1, R2      ; Chỉ 1 instruction!
```

---

### MISCONCEPTION #7: "Peripheral register = RAM bình thường"

```
❌ HIỂU SAI:
"Tôi ghi uint32_t vào địa chỉ peripheral giống ghi RAM"

✅ HIỂU ĐÚNG:
Peripheral registers (Memory-mapped I/O) có hành vi ĐẶC BIỆT:

1. SIDE EFFECTS: Đọc có thể clear flag (UART status register)
2. WRITE-ONLY: Một số registers không đọc được
3. READ-ONLY: Một số registers không ghi được
4. ATOMIC REQUIREMENT: Phải write toàn bộ 32-bit
5. SEQUENCING: Phải write theo đúng thứ tự
6. VOLATILE: Bắt buộc dùng volatile pointer
```

```c
// SAI: Compiler có thể optimize away (cache register)
uint32_t *UART_SR = (uint32_t*)0x40011000;
while (*UART_SR & TX_EMPTY == 0) { }  // INFINITE LOOP!

// ĐÚNG: volatile bắt buộc đọc lại từ hardware mỗi lần
volatile uint32_t *UART_SR = (volatile uint32_t*)0x40011000;
while ((*UART_SR & TX_EMPTY) == 0) { }  // OK
```

---

### MISCONCEPTION #8: "Interrupt = gọi function thông thường"

```
❌ HIỂU SAI:
"ISR giống function bình thường, tôi có thể gọi bất kỳ code nào"

✅ HIỂU ĐÚNG:
ISR KHÁC function thông thường:
1. Được CPU gọi tự động, không phải software call
2. Context (R0-R12, LR, PC, xPSR) được HARDWARE save/restore
3. Không có arguments, không có return value
4. Phải chạy NHANH (không block, sleep, wait)
5. Stack dùng có thể là MSP, không phải PSP (task stack)
6. Re-entrant issues với global variables

CÁC LỖI PHỔ BIẾN TRONG ISR:
  - Gọi printf/malloc/free (không re-entrant)
  - Delay/sleep
  - Gọi blocking RTOS call (osMutexAcquire với timeout != 0)
  - Xử lý quá nhiều (quá thời gian)
```

---

### MISCONCEPTION #9: "Tất cả registers được hardware auto-save khi interrupt"

```
❌ HIỂU SAI:
"Khi interrupt xảy ra, CPU save tất cả R0-R15"

✅ HIỂU ĐÚNG:
Hardware chỉ auto-save 8 registers:
  xPSR, PC, LR, R12, R3, R2, R1, R0

R4-R11 (callee-saved) KHÔNG được hardware save!
RTOS hoặc ISR phải tự save/restore R4-R11 nếu cần.

Lý do thiết kế:
- Tiết kiệm stack space (8 registers thay vì 16)
- ISR đơn giản không cần R4-R11
- ISR phức tạp tự save khi cần: PUSH {R4-R11}

FPU (Cortex-M4F): Chỉ S0-S15, FPSCR lazy-saved.
S16-S31 KHÔNG được auto-save.
```

---

### MISCONCEPTION #10: "PC += 4 luôn xảy ra sau mỗi instruction"

```
❌ HIỂU SAI:
"CPU luôn tăng PC thêm 4 sau mỗi instruction"

✅ HIỂU ĐÚNG:
Trên Cortex-M (Thumb mode):
- 16-bit Thumb instruction: PC += 2
- 32-bit Thumb-2 instruction: PC += 4
- Branch instruction: PC = branch target
- BL: LR = PC + 4, PC = function address
- Interrupt: PC được save, PC = vector table entry
- Exception return: PC = restored value from stack
- Pipeline: PC thực sự đã "ahead" 4 bytes
```

---

### MISCONCEPTION #11: "Stack chỉ dùng cho local variables"

```
❌ HIỂU SAI:
"Stack = nơi chứa local variables"

✅ HIỂU ĐÚNG:
Stack dùng cho:
1. Local variables ✓
2. Function arguments khi có hơn 4 args (arg 5+ push lên stack)
3. Saved registers (PUSH {R4-R11, LR})
4. Exception stack frame (hardware auto-push 8 registers)
5. Temporary values từ compiler (register spilling)
6. Return address (qua LR hoặc stack frame)
7. Alignment padding
8. RTOS context (R4-R11 của task)
```

---

### MISCONCEPTION #12: "PC nằm trong vùng code → không crash"

```
❌ HIỂU SAI:
"Nếu PC trong 0x08000000-0x080FFFFF, firmware sẽ không crash"

✅ HIỂU ĐÚNG:
PC trong Flash hợp lệ không đảm bảo không crash:
1. Execute data/padding như code → UNDEFINSTR fault
2. Execute tại offset lẻ (Thumb instruction misaligned)
3. Execute section không phải code (vtable, strings...)
4. Đúng code nhưng SAI context (registers corrupt → sai behavior)
5. Đúng code nhưng xử lý sai dữ liệu (NULL pointer trong function)
```

---

### MISCONCEPTION #13: "LR bị sai = function call chain bị sai"

```
❌ HIỂU SAI:
"Nếu LR sai → trace function call chain sẽ sai"

✅ HIỂU ĐÚNG:
LR chỉ chứa return address của CURRENT function.
Để trace full call chain cần đọc STACK (saved LR trên stack), không chỉ LR.

Call chain: main() → A() → B() → C() [crash]

  SP → [stack frame của C: saved LR = return-to-B]
       [stack frame của B: saved LR = return-to-A]
       [stack frame của A: saved LR = return-to-main]

LR hiện tại = return address từ C về B
Để biết A và main, phải walk stack frame!
Debugger làm điều này với "stack unwinding" (DWARF debug info).
```

---

### MISCONCEPTION #14: "Mọi Cortex-M đều giống nhau"

```
❌ HIỂU SAI:
"Code cho STM32F4 (Cortex-M4) chạy được trên STM32G0 (Cortex-M0+)"

✅ HIỂU ĐÚNG:
Feature          M0/M0+    M3      M4      M7
Thumb-2          Subset    Full    Full    Full
DSP instructions  No       No      Yes     Yes
FPU              No        No    Optional  Yes (DP)
Divide (HW)      No        Yes     Yes     Yes
Bit-band         No        Yes     Yes     Yes
MPU              Optional  8 reg   8 reg   16 reg

Nguy hiểm:
- Code dùng SDIV/UDIV trên M0 → UNDEFINSTR HardFault
- Code dùng FPU instruction trên M4 không enable FPU → NOCP HardFault
- Code dùng unaligned access trên M0 → HARDFAULT
```

---

### MISCONCEPTION #15: "Debug assembly = debug C từng dòng"

```
❌ HIỂU SAI:
"Khi step trong debugger, tôi đang step từng dòng C"

✅ HIỂU ĐÚNG:
"Step" trong debugger thực ra:
1. Source-level step: debugger map PC về source dòng C
   - Cần debug info (DWARF) trong ELF file
   - -O0 compile: gần đúng 1-1
   - -O2 compile: có thể skip dòng, re-order, không nhất quán

2. Instruction-level step: step từng assembly instruction
   - Chính xác tuyệt đối
   - Cần biết đọc assembly

Với -O2 (production code):
  - Một dòng C có thể thành 0 instructions (inlined, constant-folded)
  - Thứ tự execution khác thứ tự source (reordered)
  → Dùng instruction-level stepping khi debug production code
```

---

## Tóm Tắt 15 Misconceptions

```
╔═══╦═══════════════════════════════════╦══════════════════════════╗
║ # ║ Hiểu Sai                          ║ Thực Tế                  ║
╠═══╬═══════════════════════════════════╬══════════════════════════╣
║ 1 ║ PC = instruction hiện tại         ║ PC = instruction kế tiếp ║
║ 2 ║ LR chỉ là return address          ║ LR đa vai trò, EXC_RETURN║
║ 3 ║ SP là biến địa chỉ bình thường    ║ SP có ràng buộc align, 2SP║
║ 4 ║ R0-R3 luôn = function args        ║ R0-R3 bị destroy sau call║
║ 5 ║ xPSR chỉ là N/Z/C/V flags        ║ xPSR = APSR+IPSR+EPSR   ║
║ 6 ║ CPU hiểu C code                   ║ CPU chỉ hiểu machine code║
║ 7 ║ Peripheral = RAM bình thường      ║ MMIO có side effects     ║
║ 8 ║ ISR = function bình thường        ║ ISR khác về context/stack║
║ 9 ║ Hardware save tất cả registers    ║ Hardware chỉ save 8 regs ║
║10 ║ PC += 4 luôn xảy ra              ║ PC += 2 hoặc 4 hoặc jump ║
║11 ║ Stack = local variables           ║ Stack = nhiều thứ hơn    ║
║12 ║ PC trong Flash = safe             ║ Sai context vẫn crash    ║
║13 ║ LR sai = call chain sai           ║ Call chain nằm trên stack║
║14 ║ Mọi Cortex-M đều như nhau        ║ M0/M3/M4/M7 khác nhau   ║
║15 ║ Step = từng dòng C               ║ Step = instruction level  ║
╚═══╩═══════════════════════════════════╩══════════════════════════╝
```

---

# CHƯƠNG 21: REAL-WORLD CASE STUDIES

## Case Study 1: Function Call Chain Crash — Divide by Zero

### Scenario
Firmware chạy được 2 giờ sau khi deploy, bỗng dưng crash. Log cuối cùng là "Starting sensor read...".

### Code
```c
void read_all_sensors(void) {
    SensorData data;                    // Chưa khởi tạo!
    process_sensor_data(&data);
}

void process_sensor_data(SensorData *data) {
    if (data->type == SENSOR_TEMP) {
        calculate_temperature(data);    // CRASH HERE
    }
}

void calculate_temperature(SensorData *data) {
    float result = data->raw_value / data->scale_factor;  // ÷ 0!
}
```

### Register Dump

```
=== HARDFAULT DUMP ===
R0   = 0x20002A50   (pointer to SensorData)
R1   = 0x00000000   (0 - suspicious!)
R2   = 0x20002A58
R3   = 0x00000004
LR   = 0x08003421   (return address trong process_sensor_data)
PC   = 0x08003578   (instruction trong calculate_temperature)
xPSR = 0x41000000   (Z flag = 1, Thumb, Thread)

HFSR = 0x40000000   FORCED = 1
CFSR = 0x02000000
  UFSR.DIVBYZERO = 1 ← CHIA CHO 0!
```

### Suy Luận

```
Bước 1: CFSR.UFSR.DIVBYZERO = 1
  → Lỗi chia cho 0

Bước 2: PC = 0x08003578 → addr2line → calculate_temperature.c:23
  → Line 23: float result = data->raw_value / data->scale_factor;

Bước 3: data->scale_factor = 0 → chia cho 0!

Bước 4: Tại sao scale_factor = 0?
  → data = &local SensorData chưa khởi tạo trong read_all_sensors!
  → SensorData data; → data.scale_factor = 0 (uninitialized!)
```

### Root Cause
`SensorData data;` không được khởi tạo. `data.scale_factor = 0` → DIVBYZERO.

### Fix
```c
void read_all_sensors(void) {
    SensorData data = {0};                      // ← Initialize!
    data.scale_factor = DEFAULT_SCALE_FACTOR;   // ← Set valid value
    process_sensor_data(&data);
}
```

---

## Case Study 2: Stack Corruption Từ Buffer Overflow

### Scenario
STM32F4 xử lý UART data. Crash 100% khi nhận gói > 100 bytes.

### Code
```c
#define UART_BUF_SIZE 64

void UART_ProcessPacket(uint8_t *raw_data, uint16_t length)
{
    uint8_t local_buf[UART_BUF_SIZE];  // 64 bytes trên stack
    memcpy(local_buf, raw_data, length);  // BUG: length có thể > 64!
    parse_packet(local_buf);
}
```

### Register Dump

```
=== HARDFAULT DUMP ===
Received: length = 128 bytes, data = 'AAAA...' (128 x 'A')

R0   = 0x41414141   ← 'AAAA'
R1   = 0x41414141
R12  = 0x41414141
LR   = 0x41414141   ← LR bị ghi đè bởi 'A'*4
PC   = 0x41414140   ← PC = 0x41414140 (bit 0 = 0 → không Thumb!)
xPSR = 0x01000000

HFSR = 0x40000000   FORCED = 1
CFSR = 0x00020000   UFSR.INVSTATE = 1
```

### Suy Luận

```
Bước 1: PC = 0x41414140 = 'AAAT' (gần như 'AAAA')
  → Không phải Flash address
  → Giá trị này là ASCII data!

Bước 2: LR = R12 = R0 = 0x41414141 = 'AAAA'
  → Tất cả bị ghi đè bằng 'A'
  → Stack bị overwrite bằng 0x41

Bước 3: UFSR.INVSTATE = 1
  → PC bit 0 = 0 → ARM mode → Cortex-M không hỗ trợ → INVSTATE

Bước 4: memcpy(local_buf, data, 128) với local_buf[64]
  → 64 bytes vào local_buf (OK)
  → 64 bytes tiếp → ghi đè saved registers: R4-R11, LR...
  → Khi function return: POP {PC} → PC = 0x41414141 (từ stack bị corrupt)
```

### Root Cause
`memcpy` không giới hạn length. Buffer overflow ghi đè stack frame, corrupt saved LR.

### Fix
```c
void UART_ProcessPacket(uint8_t *raw_data, uint16_t length)
{
    uint8_t local_buf[UART_BUF_SIZE];
    if (length > UART_BUF_SIZE) {
        log_error("Packet too large: %d", length);
        return;
    }
    memcpy(local_buf, raw_data, length);
    parse_packet(local_buf);
}
```

---

## Case Study 3: NULL/Bad Pointer Qua Callback

### Scenario
Event callback system. Thỉnh thoảng crash khi trigger event.

### Code
```c
void event_dispatch(uint32_t event_id, void *event_data)
{
    for (int i = 0; i < handler_count; i++) {
        handlers[i].callback(event_id, event_data);  // callback có thể NULL!
    }
}

void event_unregister(uint32_t event_id) {
    for (int i = 0; i < handler_count; i++) {
        if (handlers[i].event_id == event_id) {
            handlers[i].callback = NULL;  // Set NULL nhưng không remove!
        }
    }
}
```

### Register Dump

```
=== HARDFAULT DUMP ===
R0   = 0x00000042   (event_id)
R1   = 0x20001800   (event_data - valid)
LR   = 0x080045AB   (return address trong event_dispatch)
PC   = 0x00000000   ← PC = 0! CPU cố execute tại địa chỉ 0

HFSR = 0x40000000
CFSR = 0x00008200   BFSR.PRECISERR=1, BFSR.BFARVALID=1
BFAR = 0x00000000   ← Cố truy cập địa chỉ 0x0
```

### Suy Luận

```
Bước 1: PC = 0x00000000
  → CPU đang "execute" tại địa chỉ 0
  → Ai jump đến 0? → Function pointer call!

Bước 2: handlers[i].callback(event_id, event_data)
  → Function pointer = 0 → BX R0 với R0 = 0 → PC = 0!

Bước 3: event_unregister() set callback = NULL
  → event_dispatch() không kiểm tra NULL trước khi gọi
```

### Root Cause
`event_unregister()` set `callback = NULL` nhưng không xóa handler. `event_dispatch()` không kiểm tra NULL.

### Fix
```c
void event_dispatch(uint32_t event_id, void *event_data)
{
    for (int i = 0; i < handler_count; i++) {
        if (handlers[i].callback != NULL &&      // ← Kiểm tra NULL
            handlers[i].event_id == event_id)
        {
            handlers[i].callback(event_id, event_data);
        }
    }
}
```

---

## Case Study 4: ISR Gây Fault (Blocking Function Trong ISR)

### Scenario
UART ISR nhận data và log ra. Crash ở 921600 bps.

### Code
```c
void USART1_IRQHandler(void)
{
    if (USART1->SR & USART_SR_RXNE) {
        uint8_t byte = USART1->DR;
        rx_buffer[rx_write_idx++] = byte;
        if (byte == '\n') {
            printf("[ISR] Received\r\n");  // BUG: blocking trong ISR!
        }
    }
}
```

### Register Dump

```
=== HARDFAULT DUMP ===
LR   = 0xFFFFFFF9   ← EXC_RETURN! Đang trong exception handler
PC   = 0x08007ABC   (trong printf → UART TX wait loop)
xPSR = 0x01000051   ← Exception #81 = USART1_IRQn active

HFSR = 0x40000000
CFSR = 0x00001000   BFSR.STKERR = 1

MSP = 0x20000058   ← Gần đáy MSP stack!
MSP stack size = 0x400, bottom = 0x20000000
→ Còn 88 bytes = gần hết!
```

### Suy Luận

```
Bước 1: LR = 0xFFFFFFF9 → đang trong Exception Handler, dùng MSP

Bước 2: PC trong printf() → ISR đang block chờ UART TX

Bước 3: TRONG LÚC printf() đang chờ: USART1 nhận byte tiếp
  → ISR re-enter! Hardware push 32 bytes lên MSP
  → Re-enter lần 2, 3, 4... → MSP exhausted

Bước 4: BFSR.STKERR = 1
  → Fault khi hardware đang push exception stack frame (MSP overflow)

Tại 921600 bps: 1 byte = 10.8µs
printf 20 bytes = 216µs → 20 ISR re-entry trong 216µs → stack overflow
```

### Root Cause
`printf()` trong ISR là blocking. Nested interrupts exhaust MSP stack.

### Fix
```c
// ISR chỉ lưu data, KHÔNG blocking!
void USART1_IRQHandler(void)
{
    if (USART1->SR & USART_SR_RXNE) {
        uint8_t byte = USART1->DR;
        rx_buffer[rx_write_idx++ & (BUF_SIZE-1)] = byte;
        if (byte == '\n') {
            rx_line_ready = true;  // Signal, không blocking
        }
    }
}

// Trong task/main loop:
void uart_task(void) {
    if (rx_line_ready) {
        rx_line_ready = false;
        printf("[TASK] Received line\r\n");  // Safe here
    }
}
```

---

## Case Study 5: RTOS Task Stack Corruption Gây Context Switch Fault

### Scenario
FreeRTOS, 3 tasks. Task B (comm) crash ngẫu nhiên, nhưng code của B hoàn toàn đúng.

### Code
```c
// Task sensor: stack = 512 bytes, có BUG
void sensor_task(void *param) {
    uint8_t large_buf[600];  // BUG: 600 > 512 bytes stack!
    // ... dùng large_buf
    vTaskDelay(pdMS_TO_TICKS(100));
}

// Task comm: stack = 1024 bytes, code ĐÚNG nhưng vẫn crash
void comm_task(void *param) {
    // ... code OK hoàn toàn
}
```

### Register Dump

```
=== HARDFAULT DUMP ===
Current FreeRTOS Task: "comm_task"

Stack Frame (PSP của comm_task):
  R0..R12 = 0xA5A5A5A5   ← FreeRTOS stack fill pattern!
  LR      = 0xA5A5A5A5   ← LR là stack canary!
  PC      = 0xA5A5A5A4   ← PC = canary (bit0=0 → INVSTATE)
  xPSR    = 0xA5A5A5A5

CFSR = 0x00020000   UFSR.INVSTATE = 1

Memory layout:
  sensor_task stack bottom: 0x20003000
  comm_task   stack bottom: 0x20003200  ← Ngay SAU sensor_task!
```

### Suy Luận

```
Bước 1: PC, LR = 0xA5A5A5A5 = FreeRTOS stack canary
  → comm_task stack chứa toàn 0xA5A5A5A5
  → comm_task stack bị ghi đè bằng canary pattern

Bước 2: Ai ghi đè comm_task stack?
  Memory layout:
  0x20003000: sensor_task stack (512 bytes)
  0x20003200: comm_task stack

  sensor_task dùng large_buf[600]:
  → Cần 600+ bytes nhưng chỉ có 512 → overflow!
  → Stack tràn từ 0x20003000 vào 0x20003200 (comm_task!)
  → Ghi đè comm_task stack với dữ liệu từ sensor_task

Bước 3: Khi context switch sang comm_task
  → FreeRTOS restore context từ comm_task stack bị corrupt
  → PC = 0xA5A5A5A4, bit0 = 0 → INVSTATE crash

Bước 4: Tại sao crash ở comm_task, không phải sensor_task?
  → sensor_task gây overflow KHÔNG crash ngay
  → Crash chỉ xảy ra khi switch sang comm_task và load PC sai
```

### Root Cause
`sensor_task` stack overflow tràn vào `comm_task` stack. Crash biểu hiện ở `comm_task` khi context switch.

### Fix
```c
// Fix 1: Tăng stack size cho sensor_task
xTaskCreate(sensor_task, "sensor",
            2048,  // Tăng từ 512 lên 2048 words
            NULL, 1, NULL);

// Fix 2: Static allocation thay vì stack
static uint8_t large_buf[600];

// Fix 3: Enable stack overflow detection
// FreeRTOSConfig.h:
#define configCHECK_FOR_STACK_OVERFLOW 2

void vApplicationStackOverflowHook(TaskHandle_t xTask, char *pcTaskName)
{
    printf("STACK OVERFLOW: %s\r\n", pcTaskName);
    while(1);
}

// Fix 4: Monitor watermark thường xuyên
UBaseType_t wm = uxTaskGetStackHighWaterMark(sensor_task_handle);
if (wm < STACK_WATERMARK_MIN) {
    log_warning("Stack low: %u words remaining", wm);
}
```

---

# CHƯƠNG 22: EXERCISES — 10 BÀI TẬP

## BÀI TẬP 1 (Level 1): Đọc Register Dump Cơ Bản

### Đề Bài
```
R0 = 0x00000005
LR = 0x080012F0
PC = 0x08001A44
xPSR = 0x01000000
HFSR = 0x40000000
CFSR = 0x00000200
BFAR = 0x00000000
```

**Câu hỏi:**
1. CPU đang ở mode nào (Thread hay Handler)?
2. Loại fault gì đã xảy ra?
3. Hàm nào đã gọi hàm gây fault?
4. BFAR có chứa địa chỉ hợp lệ không?

### Đáp Án

```
1. CPU ở Thread mode
   Căn cứ: xPSR bits 8-0 = 0x00 → exception number = 0 → Thread mode

2. BusFault → PRECISERR (precise bus fault)
   Căn cứ:
   - HFSR.FORCED = 1 → HardFault do escalate
   - CFSR = 0x00000200 → BFSR bit 9 (PRECISERR) = 1

3. Hàm tại địa chỉ 0x080012F0 đã gọi hàm gây fault
   Căn cứ: LR = 0x080012F0 = return address sau function call
   → Instruction tại ~0x080012EE gọi BL đến hàm bị crash

4. BFAR KHÔNG chứa địa chỉ hợp lệ
   Căn cứ: CFSR bit 15 (BFARVALID) = 0 (CFSR = 0x00000200, bit 15 = 0)
   Mặc dù BFAR = 0x00000000, nhưng BFARVALID = 0 → không tin được
   (BFAR có thể chứa giá trị cũ từ fault trước đó)
```

---

## BÀI TẬP 2 (Level 2): Phân Tích Stack Frame

### Đề Bài
Memory dump của stack khi HardFault (SP = 0x20007F00):

```
0x20007F00: 0x00000003  (R0)
0x20007F04: 0x20001000  (R1)
0x20007F08: 0x00000000  (R2)
0x20007F0C: 0x00000000  (R3)
0x20007F10: 0x00000000  (R12)
0x20007F14: 0x08003251  (LR)
0x20007F18: 0x08004A20  (PC)
0x20007F1C: 0x21000000  (xPSR)
```

**Câu hỏi:**
1. Instruction nào đang chạy khi fault?
2. Hàm nào sẽ được return về?
3. xPSR = 0x21000000 có bất thường không?

### Đáp Án

```
1. Instruction tại 0x08004A20 đang chạy khi fault
   PC từ stack frame = địa chỉ instruction gây fault
   → addr2line -e firmware.elf 0x08004A20 → source line

2. Return về 0x08003251 sau khi handler xử lý
   LR từ stack frame = return address của hàm bị crash
   → Instruction tại ~0x0800324E là BL đến hàm bị crash

3. xPSR = 0x21000000:
   Bit 31-28 (NZCV) = 0010 → C flag = 1 (carry set), N=Z=V=0
   Bit 24 (T) = 1 → Thumb mode ✓ (bình thường)
   Bits 8-0 = 0x00 → Thread mode ✓
   → KHÔNG bất thường. C=1 bình thường sau nhiều operations
```

---

## BÀI TẬP 3 (Level 3): Trace Call Chain

### Đề Bài
```
Stack walk:
Stack frame (fault): LR=0x08001A51, PC=0x08002B00
Saved LR trên stack:  0x08001200 (frame của caller)
Saved LR tiếp theo:   0x08000852 (frame của caller's caller)

addr2line:
  0x08002B00 → validate_input() validator.c:45
  0x08001A50 → process_data() processor.c:23   (LR-1)
  0x08001200 → handle_request() server.c:67    (LR-1)
  0x08000852 → main_loop() main.c:112          (LR-1)
```

**Câu hỏi:**
1. Vẽ call chain đầy đủ
2. Tại sao dùng LR-1 thay vì LR khi addr2line?
3. `validate_input()` crash tại line 45: `if (*ptr == MARKER)` — nguyên nhân?

### Đáp Án

```
1. Call chain:
   main_loop() [main.c:112]
       ↓
   handle_request() [server.c:67]
       ↓
   process_data() [processor.c:23]
       ↓
   validate_input() [validator.c:45]  ← CRASH

2. Tại sao LR-1?
   LR = địa chỉ instruction KẾ TIẾP sau BL (return address)
   BL instruction (4-byte Thumb-2): ở địa chỉ LR-4
   
   0x08001A4C: BL validate_input  ← CALL instruction
   0x08001A50: MOV R0, R0         ← Next instruction
   LR = 0x08001A51 (bit 0 set cho Thumb)
   
   addr2line 0x08001A51 → line của 0x08001A50 → sai!
   addr2line 0x08001A50 (LR-1 để strip bit0) → hoặc (LR & ~1) - 4
   → Đúng call site

3. Crash tại if (*ptr == MARKER):
   PC = 0x08002B00 = validate_input line 45 → dereference ptr
   R0 = 0x00000000 → ptr có thể = NULL
   → Dereference NULL → BusFault
   → Kiểm tra: BFAR = 0x00000000, BFARVALID = 1
   Root cause: validate_input() được gọi với NULL pointer
```

---

## BÀI TẬP 4 (Level 4): Phân Tích MSP/PSP

### Đề Bài
FreeRTOS. HardFault xảy ra.

```
LR (trong HardFault handler) = 0xFFFFFFFD
MSP = 0x20001FC0
PSP = 0x20003A80

Dump tại PSP (0x20003A80):
  R0=0x08001234  R1=0x00000001  LR=0x0801ABCD  PC=0x08005678
  xPSR = 0x01000000
```

**Câu hỏi:**
1. Stack frame nào chứa crash context: PSP hay MSP?
2. Instruction nào gây crash?
3. CPU đang ở Thread hay Handler mode trước khi crash?
4. Tại sao HardFault handler dùng MSP?

### Đáp Án

```
1. Stack frame tại PSP (0x20003A80) chứa crash context
   Căn cứ: LR = 0xFFFFFFFD → EXC_RETURN:
     Bit 2 = 1 → trước exception: đang dùng PSP
     Bit 3 = 1 → Thread mode
   → CPU ở Thread mode với PSP (RTOS task) → stack frame tại PSP

2. Instruction gây crash: tại 0x08005678
   PC từ PSP stack frame = 0x08005678

3. Thread mode
   Từ EXC_RETURN bit 3 = 1 → Thread mode
   Từ xPSR bits 8-0 = 0 → Thread mode

4. HardFault handler dùng MSP vì:
   - Tất cả exception handlers luôn dùng MSP
   - Khi vào exception: CONTROL.SPSEL bị clear → MSP active
   - EXC_RETURN trong LR ghi nhớ "trước khi vào exception, dùng PSP"
   - Khi exception return với BX LR (0xFFFFFFFD): CPU switch lại PSP
   
   Lý do thiết kế:
   - Exception handler (kernel) có stack riêng (MSP) = isolation
   - Task stack (PSP) không bị corrupt bởi exception stack usage
   - MPU có thể protect từng task stack riêng biệt
```

---

## BÀI TẬP 5 (Level 5): Decode CFSR Chi Tiết

### Đề Bài
```
CFSR = 0x00020000
```

**Câu hỏi:**
1. Decode hoàn toàn CFSR: bit nào set?
2. Loại fault là gì?
3. Nguyên nhân phổ biến?
4. BFAR/MMFAR có valid không?

### Đáp Án

```
1. Decode CFSR = 0x00020000:
   Binary: 0000_0000_0000_0010_0000_0000_0000_0000
   
   Bits 31-16 (UFSR): 0000_0000_0000_0010
     Bit 17 = 1 → INVSTATE ← SET!
     Tất cả bits khác = 0
   
   Bits 15-8 (BFSR): 0000_0000 → tất cả 0
   Bits  7-0 (MMFSR): 0000_0000 → tất cả 0

2. Fault: UsageFault → INVSTATE (Invalid State)
   UsageFault escalated thành HardFault (handler disabled by default)
   INVSTATE: CPU cố execute instruction khi EPSR.T = 0 (ARM mode)

3. Nguyên nhân phổ biến:
   a) Function pointer không có Thumb bit:
      void (*fp)(void) = (void(*)(void))0x08001234;  // bit0 = 0!
      fp();  // → INVSTATE!
      Đúng: fp = (void(*)(void))0x08001235; // bit0 = 1 (Thumb)
   
   b) Stack corruption → PC load giá trị even address
      (sau POP {PC}, PC bit0 = 0)
   
   c) BX Rm với Rm bit0 = 0

4. BFAR và MMFAR không valid
   INVSTATE là UsageFault (UFSR), không liên quan đến memory access
   → Không có địa chỉ memory nào để report
   → BFARVALID = 0, MMARVALID = 0 (CFSR không có các bits này set)
```

---

## BÀI TẬP 6 (Level 6): Tìm Bug Từ Assembly

### Đề Bài
```asm
; compute_checksum(uint8_t *buf, uint32_t len)
; R0 = buf, R1 = len
08001A00: PUSH    {R4, LR}
08001A02: MOV     R4, #0          ; checksum = 0
08001A04: CBZ     R1, 08001A14    ; if len == 0: goto end
08001A06: LDRB    R2, [R0]        ; Load byte từ *buf
08001A08: ADD     R4, R4, R2      ; checksum += *buf
08001A0A: ADD     R0, R0, #1      ; buf++
08001A0C: SUB     R1, R1, #1      ; len--
08001A0E: CBZ     R1, 08001A14    ; if len == 0: goto end
08001A10: LDRB    R2, [R0]        ; ← PC! CRASH HERE!
08001A12: B       08001A08
08001A14: MOV     R0, R4          ; return checksum
08001A16: POP     {R4, PC}
```

Caller gọi: `compute_checksum(NULL, 5)`.

**Câu hỏi:**
1. Tại sao crash tại 0x08001A10?
2. Fault register nào có giá trị quan trọng?
3. Fix code này.

### Đáp Án

```
1. Crash tại 0x08001A10 vì:
   Caller truyền buf = NULL (R0 = 0), len = 5 (R1 = 5)
   
   0x08001A04: CBZ R1, 08001A14 → R1=5 ≠ 0 → KHÔNG branch
   0x08001A06: LDRB R2, [R0] với R0=NULL=0
     → Load byte từ 0x00000000
     → Trên STM32F4: 0x00000000 aliased vào Flash → đọc được!
     → KHÔNG crash ngay
   
   0x08001A0A: ADD R0, R0, #1 → R0 = 0x00000001
   0x08001A0C: SUB R1, R1, #1 → R1 = 4
   0x08001A0E: CBZ R1=4 ≠ 0 → tiếp tục
   0x08001A10: LDRB R2, [R0] với R0 = 0x00000001
     → Load từ 0x00000001 (odd address, unaligned byte read = OK cho LDRB)
     → Hoặc tiếp tục: R0 tăng dần đến vùng không mapped
     → Crash tại R0 = một địa chỉ invalid nào đó

2. Fault registers:
   HFSR: FORCED = 1
   CFSR: BFSR.PRECISERR = 1, BFSR.BFARVALID = 1
   BFAR = địa chỉ cụ thể gây crash (giá trị R0 khi crash)
   
   Nếu MPU enable:
   CFSR: MMFSR.DACCVIOL = 1, MMFSR.MMARVALID = 1
   MMFAR = địa chỉ vi phạm MPU

3. Fix: Kiểm tra NULL trước khi dereference
   
   C code:
   uint32_t compute_checksum(uint8_t *buf, uint32_t len) {
       if (buf == NULL || len == 0) return 0;  // ← FIX
       uint32_t checksum = 0;
       for (uint32_t i = 0; i < len; i++) {
           checksum += buf[i];
       }
       return checksum;
   }
   
   Assembly fix (thêm vào đầu):
   08001A00: PUSH   {R4, LR}
   08001A02: MOV    R4, #0
   08001A04: CBZ    R0, 08001A14   ; ← THÊM: if buf == NULL: return 0
   08001A06: CBZ    R1, 08001A14   ; if len == 0: return 0
   ...
```

---

## BÀI TẬP 7 (Level 7): RTOS Stack Debug

### Đề Bài
FreeRTOS, 2 tasks. Task B luôn crash ngay sau lần đầu được schedule.

```
HardFault khi Task B được schedule:
PC   = 0x20005A00   ← trong SRAM!
LR   = 0x20005A08
xPSR = 0x01000000
CFSR = 0x00020000 (INVSTATE)
Task B TCB.sp = 0x20005A20
Task B stack buffer: 0x20005A00-0x20005B00 (256 bytes)
```

**Câu hỏi:**
1. Tại sao PC = 0x20005A00?
2. Chẩn đoán nguyên nhân
3. Cách fix

### Đáp Án

```
1. PC = 0x20005A00 trong SRAM vì:
   Khi context switch, CPU restore PC từ Task B's stack frame
   Stack frame của Task B bị corrupt hoặc setup sai
   → PC được load từ giá trị sai = 0x20005A00 (địa chỉ trong SRAM)
   INVSTATE vì: 0x20005A00 bit 0 = 0 → không Thumb → crash

2. Chẩn đoán:
   Task B stack buffer = 0x20005A00 - 0x20005B00
   Initial stack setup của FreeRTOS:
   - Stack top = 0x20005B00 (đỉnh stack)
   - Initial frame đặt từ top xuống
   - TCB.sp = stack_top - sizeof(initial_frame)
             = 0x20005B00 - (8+8)×4 = 0x20005B00 - 64 = 0x20005AC0
   
   Nhưng TCB.sp = 0x20005A20 ≠ 0x20005AC0
   → TCB.sp chỉ xuống 32 bytes từ top thay vì 64
   → Có thể chỉ R4-R11 được setup, không có hardware frame
   → Hoặc stack được initialize với sai offset
   
   Nguyên nhân phổ biến:
   - xTaskCreate với stack_size tính bằng BYTES thay vì WORDS
     → FreeRTOS dùng WORDS (4 bytes mỗi word)
     → xTaskCreate(task, "B", 64, ...) = 64 WORDS = 256 bytes → OK
     → xTaskCreate(task, "B", 64, ...) nếu hiểu là bytes → quá nhỏ!
   
   PC = 0x20005A00 = đáy stack buffer → PC load từ đáy stack = rác

3. Fix:
   // Dùng đủ stack và kiểm tra đúng unit
   xTaskCreate(task_b, "B",
               configMINIMAL_STACK_SIZE * 4,  // Dùng macro
               NULL, 2, &task_b_handle);
   
   // Verify sau khi create:
   UBaseType_t wm = uxTaskGetStackHighWaterMark(task_b_handle);
   configASSERT(wm > MIN_STACK_WATERMARK);
   
   // Enable stack overflow check:
   #define configCHECK_FOR_STACK_OVERFLOW 2
```

---

## BÀI TẬP 8 (Level 8): Imprecise BusFault Debug

### Đề Bài
```
HFSR = 0x40000000
CFSR = 0x00000400   (BFSR bit 10 = IMPRECISERR)
BFAR = 0x00000000   (BFARVALID = 0)
PC   = 0x080056AB   → disassembly: MOV R0, R0 (NOP)
```

Developer confused: MOV R0, R0 không thể gây lỗi!

**Câu hỏi:**
1. IMPRECISERR khác PRECISERR thế nào?
2. Tại sao PC không trỏ đến instruction gây lỗi?
3. Cách debug?

### Đáp Án

```
1. IMPRECISERR vs PRECISERR:
   
   PRECISERR:
   - CPU biết CHÍNH XÁC instruction nào gây fault
   - BFAR chứa địa chỉ hợp lệ (BFARVALID = 1)
   - Xảy ra với LOAD (LDR): CPU chờ kết quả trước khi tiếp tục
   
   IMPRECISERR:
   - CPU KHÔNG biết chính xác instruction nào gây fault
   - BFAR KHÔNG hợp lệ (BFARVALID = 0)
   - Xảy ra với STORE (STR): CPU có write buffer
     → STR vào write buffer → CPU tiếp tục execute
     → Vài instructions sau: buffer flush → lỗi detected
     → Tại thời điểm đó, PC đã ở instruction khác!
   
   Timeline minh họa:
   T=0: STR R0, [BAD_ADDR] ← Gây lỗi nhưng không biết ngay (write buffer)
   T=1: ADD R2, R3          ← Execute OK
   T=2: MOV R0, R0          ← Execute OK (PC ở đây)
   T=3: Write buffer flush  → BusFault detected! PC = T2 (MOV R0, R0)

2. PC không trỏ đến instruction lỗi vì write buffer:
   STR "hoàn thành ngay" từ góc nhìn CPU (vào buffer)
   Thực sự write lên bus xảy ra sau → error response → fault
   PC đã tiến đến instruction tiếp theo khi fault được detect

3. Cách debug:
   Option A: Thêm DSB sau STR nghi ngờ
     STR R0, [R1]
     DSB            ; Force flush write buffer NGAY
     ; Nếu fault xảy ra sau DSB: trở thành PRECISERR, PC gần instruction lỗi
   
   Option B: Disable write buffer (chỉ dùng khi debug!)
     // ACTLR.DISDEFWBUF = 1
     SCnSCB->ACTLR |= SCnSCB_ACTLR_DISDEFWBUF_Msk;
     // Tất cả STR thành precise → hiệu năng giảm, debug dễ hơn
   
   Option C: Thu hẹp phạm vi bằng cách comment từng block
```

---

## BÀI TẬP 9 (Level 9): FPU Fault

### Đề Bài
STM32F4 (Cortex-M4 với FPU). Code:
```c
float multiply(float a, float b) {
    return a * b;  // HardFault tại đây!
}
```

```
CFSR = 0x00080000
HFSR = 0x40000000
PC   = 0x080034A8  (trong multiply)
```

**Câu hỏi:**
1. Decode CFSR
2. Root cause là gì?
3. Fix thế nào?
4. Tại sao Cortex-M0 không có vấn đề này?

### Đáp Án

```
1. Decode CFSR = 0x00080000:
   Binary: 0000_0000_0000_1000_0000_0000_0000_0000
   Bits 31-16 (UFSR): 0000_0000_0000_1000
   Bit 19 = 1 → NOCP (No Coprocessor)!
   
   NOCP: Code cố dùng coprocessor (FPU = CP10/CP11) khi bị disable/restricted

2. Root cause: FPU chưa được enable!
   
   Sau reset: CPACR (0xE000ED88) mặc định:
     Bits 23:22 (CP11) = 00 → Access denied
     Bits 21:20 (CP10) = 00 → Access denied
   
   Code dùng VMUL.F32 (FPU instruction) → NOCP fault

3. Fix: Enable FPU trước khi dùng (trong SystemInit hoặc startup):
   
   // Cách 1: Trực tiếp
   SCB->CPACR |= ((3UL << 10*2) | (3UL << 11*2));
   
   // Cách 2: HAL (STM32)
   // Được tự động generate bởi CubeMX trong SystemInit():
   SCB->CPACR |= ((3UL << 20U)|(3UL << 22U));
   
   // Cách 3: Compile flags
   // -mfpu=fpv4-sp-d16 -mfloat-abi=hard
   // Startup code sẽ tự enable FPU nếu __FPU_PRESENT = 1

4. Tại sao Cortex-M0 không có vấn đề này:
   Cortex-M0/M0+ KHÔNG có FPU hardware!
   
   float a * b trên M0:
   Compiler tự generate SOFTWARE floating point library calls:
   → VMUL → gọi __aeabi_fmul() (soft-float function trong libgcc)
   → Không có FPU instruction nào
   → Không có NOCP fault
   
   Nhưng: chậm hơn 20-100x so với hardware FPU trên M4!
   
   Trên M4 với -mfloat-abi=soft hoặc softfp:
   → Giống M0: dùng software float library
   → Không NOCP, nhưng mất lợi ích của hardware FPU
```

---

## BÀI TẬP 10 (Level 10 — Senior): Phân Tích Toàn Diện

### Đề Bài
Production firmware STM32F407. Crash ngẫu nhiên sau 24-72h, chỉ ở môi trường nóng. Không tái hiện trong lab.

```
=== CRASH REPORT ===
Uptime: 67h 23m 14s
Temperature: 85°C
Last operation: "OTA update completed, verifying CRC"

R0  = 0x08040000   R1  = 0x00008000
LR  = 0x08012AB5
PC  = 0x08012A9C
xPSR= 0x61000000

HFSR = 0x40000000
CFSR = 0x00008100   (BFSR: BFARVALID=1, IBUSERR=1)
BFAR = 0x08040000   ← Chú ý!

Flash: 1MB (0x08000000 - 0x080FFFFF)
OTA firmware tại: 0x08040000, size: 0x8000 (32KB)
```

**Câu hỏi:**
1. Decode CFSR và xPSR
2. Root cause là gì?
3. Tại sao chỉ xảy ra ở 85°C?
4. Tại sao không tái hiện trong lab?
5. Fix

### Đáp Án

```
1. Decode:
   CFSR = 0x00008100:
   Bits 15-8 (BFSR): 0x81 = 1000_0001
     Bit 15: BFARVALID = 1 → BFAR chứa địa chỉ hợp lệ
     Bit  8: IBUSERR   = 1 → Instruction fetch bus error!
   → CPU cố FETCH INSTRUCTION từ địa chỉ BFAR = 0x08040000!
   
   xPSR = 0x61000000:
   Bit 30 (Z) = 1, Bit 29 (C) = 1, Bit 28 (V) = 0, Bit 31 (N) = 0
   Bit 24 (T) = 1 → Thumb mode ✓
   Bits 8-0 = 0 → Thread mode

2. Root cause:
   LR = 0x08012AB5 → addr2line → verify_and_jump()
   PC = 0x08012A9C → trong verify_and_jump(), execution point
   BFAR = 0x08040000 → CPU cố fetch instruction từ đây
   
   → Code đang cố jump đến OTA firmware entry
   
   Nguyên nhân 1 (phổ biến nhất): Jump đến sai địa chỉ
   OTA firmware vector table tại 0x08040000:
     [0x08040000]: 0x20020000  ← Initial MSP (không phải code!)
     [0x08040004]: 0x08040151  ← Reset handler (entry point)
   
   Code lỗi:
   void (*entry)(void) = (void(*)(void))0x08040000;
   entry();  // Jump đến MSP value, không phải code!
   
   → CPU fetch instruction từ 0x08040000 = đọc vector table
   → Giá trị tại đó (0x20020000) không phải code
   → Hoặc CPU interpret MSP value như Thumb address
   → IBUSERR khi fetch từ địa chỉ không valid/unexpected
   
   Nguyên nhân 2: Flash read error do timing (xem câu 3)

3. Tại sao chỉ ở 85°C:
   STM32F407 Flash wait states phụ thuộc Vcc và nhiệt độ:
   
   Vcc > 2.7V, HCLK = 168MHz:
   - T ≤ 30°C: 3 wait states có thể OK
   - T = 85°C:  cần 5 wait states!
   
   Nếu firmware config FLASH_ACR.LATENCY = 3 (cho lab 25°C):
   - Lab 25°C: 3 WS đủ → OK
   - Field 85°C: cần 5 WS nhưng chỉ có 3 → Flash read timing violation!
   → Flash trả về sai data khi CPU đọc instruction
   → Đặc biệt xảy ra khi CPU fetch từ OTA region (vùng mới flash)
   
   Thêm: Battery voltage drop + nhiệt độ cao = worst case timing

4. Tại sao không tái hiện trong lab:
   - Lab: T = 25°C, Vcc = 3.3V stable → 3 wait states đủ
   - Field: T = 85°C, Vcc có thể 3.0V (battery) → cần 5 WS
   
   STM32F4 Flash wait states table (RM0090):
   Vcc > 2.7V, 168MHz: cần 5 WS
   Nếu code set 3 WS → chỉ xảy ra flash timing error ở extreme condition
   → Lab không đạt extreme condition → không tái hiện

5. Fix:
   // a) Set đúng flash wait states
   __HAL_FLASH_SET_LATENCY(FLASH_LATENCY_5);
   // Hoặc: FLASH->ACR = (FLASH->ACR & ~FLASH_ACR_LATENCY) | FLASH_ACR_LATENCY_5WS;
   
   // b) Fix OTA jump entry point:
   // SAI:
   void (*entry)(void) = (void(*)(void))0x08040000;  // MSP value, not code!
   
   // ĐÚNG:
   uint32_t reset_vec = *(volatile uint32_t*)0x08040004;  // Reset handler
   if ((reset_vec & 0xFF000000) != 0x08000000) {
       log_error("Invalid OTA firmware");
       return ERROR;
   }
   void (*entry)(void) = (void(*)(void))(reset_vec | 0x1);  // Thumb bit
   
   // c) Verify flash CRC trước khi jump
   if (!verify_flash_crc(0x08040000, 0x8000)) {
       log_error("CRC mismatch, aborting boot");
       return ERROR;
   }
   
   // d) Full jump sequence:
   __disable_irq();
   // Set new vector table base
   SCB->VTOR = 0x08040000;
   // Load new MSP
   __set_MSP(*(uint32_t*)0x08040000);
   // Jump!
   entry();
```

---

# CHƯƠNG 23: CHEAT SHEET

```
╔══════════════════════════════════════════════════════════════════════════════╗
║          ARM CORTEX-M DEBUG CHEAT SHEET — 1 TRANG                          ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ REGISTERS                          CALLING CONVENTION (AAPCS)              ║
║ ┌────┬──────────────────────────┐  R0-R3:  Args 1-4, Return, SCRATCH       ║
║ │ R0 │ Arg1, Return value       │  R4-R11: Callee-SAVED (RTOS save these)  ║
║ │ R1 │ Arg2, Return (64-bit hi) │  R12:    Scratch (IP)                    ║
║ │ R2 │ Arg3                     │  R13/SP: Stack Pointer                   ║
║ │ R3 │ Arg4                     │  R14/LR: Link Register (return addr)     ║
║ │ R4 │ Callee-saved             │  R15/PC: Program Counter                 ║
║ │..  │ ...                      │                                           ║
║ │R11 │ Callee-saved             │  STACK POINTER RULES:                    ║
║ │R12 │ Scratch (IP)             │  • MUST be 4-byte aligned always         ║
║ │ SP │ MSP (kernel) / PSP(task) │  • MUST be 8-byte aligned on exception   ║
║ │ LR │ Return addr / EXC_RETURN │  • Full Descending (grows downward)      ║
║ │ PC │ Next instruction (ahead) │                                           ║
║ └────┴──────────────────────────┘                                           ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ HARDFAULT DEBUG CHECKLIST                                                   ║
║                                                                             ║
║ 1. HFSR @ 0xE000ED2C                                                        ║
║    FORCED=1? → Đọc CFSR (fault khác escalate)                              ║
║    VECTTBL=1? → Vector table corrupt                                        ║
║                                                                             ║
║ 2. CFSR @ 0xE000ED28                                                        ║
║    BITS 31-16 (UFSR):   BITS 15-8 (BFSR):   BITS 7-0 (MMFSR):            ║
║    25: DIVBYZERO        15: BFARVALID        7: MMARVALID                  ║
║    24: UNALIGNED        12: STKERR (OVF!)    4: MSTKERR                   ║
║    19: NOCP (no FPU)    10: IMPRECISERR      1: DACCVIOL                  ║
║    18: INVPC             9: PRECISERR        0: IACCVIOL                  ║
║    17: INVSTATE (T=0!)   8: IBUSERR                                         ║
║    16: UNDEFINSTR                                                            ║
║                                                                             ║
║ 3. BFAR @ 0xE000ED38 (valid nếu BFSR.BFARVALID=1)                         ║
║    MMFAR @ 0xE000ED34 (valid nếu MMFSR.MMARVALID=1)                        ║
║                                                                             ║
║ 4. PC từ stack frame → Instruction gây fault                                ║
║ 5. LR từ stack frame → Caller của function gây fault                        ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ EXC_RETURN VALUES (trong LR khi trong exception)                            ║
║ 0xFFFFFFF1: Handler mode, MSP (nested exception)                            ║
║ 0xFFFFFFF9: Thread mode,  MSP (bare metal)                                  ║
║ 0xFFFFFFFD: Thread mode,  PSP (RTOS task) ← most common                    ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ HARDWARE AUTO-SAVE ON EXCEPTION (Full Descending)                           ║
║ [SP+28]=xPSR  [SP+24]=PC   [SP+20]=LR   [SP+16]=R12                       ║
║ [SP+12]=R3    [SP+8]=R2    [SP+4]=R1    [SP+0]=R0  ← SP after push        ║
║ R4-R11: NOT saved by hardware! (RTOS saves in context switch)               ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ COMMON FAULTS QUICK DIAGNOSIS                                               ║
║ NULL ptr dereference → BFSR.PRECISERR, BFAR ≈ 0x0-0xFF                    ║
║ Stack overflow       → BFSR.STKERR or SP < stack_bottom                    ║
║ Bad function ptr     → UFSR.INVSTATE (PC even addr) or INVPC               ║
║ FPU not enabled      → UFSR.NOCP                                            ║
║ Divide by zero       → UFSR.DIVBYZERO                                       ║
║ Buffer overflow      → LR/PC = ASCII or canary pattern                      ║
║ Undef instruction    → UFSR.UNDEFINSTR                                      ║
║ ISR stack overflow   → BFSR.STKERR (khi exception stacking)                ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ QUICK ASSEMBLY REFERENCE                                                    ║
║ MOV R0,#5    R0=5          LDR R0,[R1]   R0=*R1                           ║
║ STR R0,[R1]  *R1=R0        PUSH{R4,LR}   Save R4,LR on stack              ║
║ POP {R4,PC}  Restore+RET   BL func       Call func, LR=next               ║
║ BX LR        Return        CMP R0,#5     Set flags (R0-5)                 ║
║ BEQ lbl      if Z=1 goto   MRS R0,PSP    R0 = PSP value                   ║
║ MSR PSP,R0   PSP = R0      AND R0,R1,#F  R0 = R1 & 0xF                   ║
║ ORR R0,R0,#1 R0 |= 1       LSL R0,R1,#3  R0 = R1 << 3                    ║
║ BIC R0,R0,#8 R0 &= ~8      DSB            Wait memory writes              ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ STM32F4 MEMORY MAP (quan trọng khi phân tích fault)                        ║
║ 0x00000000: Code region (aliased)   0x08000000: Flash (up to 1MB)          ║
║ 0x20000000: SRAM1 (112KB)           0x2001C000: SRAM2 (16KB)               ║
║ 0x40000000: APB1 peripherals        0x40010000: APB2 peripherals            ║
║ 0x40020000: AHB1 peripherals        0xE000E000: SysTick, NVIC              ║
║ 0xE000ED28: CFSR                    0xE000ED2C: HFSR                       ║
║ 0xE000ED34: MMFAR                   0xE000ED38: BFAR                       ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ CONTEXT SWITCH: WHAT HARDWARE SAVES vs RTOS SAVES                          ║
║ HARDWARE (auto):  R0, R1, R2, R3, R12, LR, PC, xPSR  (32 bytes)          ║
║ RTOS (software):  R4, R5, R6, R7, R8, R9, R10, R11   (32 bytes)          ║
║ Total per task context = 64 bytes minimum (no FPU)                         ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

---

# CHƯƠNG 24: SENIOR MENTAL MODEL

## 24.1 Tư Duy Của Senior Embedded Engineer

Senior không phải là người biết nhiều hơn. Senior là người **hỏi đúng câu hỏi** và **thu hẹp problem space nhanh**.

Dưới đây là 8 câu hỏi cốt lõi khi debug bất kỳ crash nào:

---

## 24.2 Câu Hỏi 1: "Fault xảy ra ở đâu?"

```
PC từ stack frame → Instruction cụ thể
→ addr2line → Source line

Nếu PC = địa chỉ không hợp lệ:
→ Ai đặt PC này? → LR hoặc stack frame bị corrupt
→ Quay lại câu hỏi: ai corrupt stack/LR?

Nếu PC hợp lệ:
→ Instruction đó đang làm gì?
→ Operands của nó đến từ đâu (registers)?
```

**Ví dụ tư duy:**
```
PC = 0x08002345 → LDR R0, [R1]
→ R1 = ??? (đọc từ stack frame)
→ R1 = 0x00000000 (NULL!)
→ Vậy ai truyền NULL vào R1?
→ R1 là argument 2 của function → caller truyền NULL
→ Đọc LR → caller là ai?
→ addr2line(LR-4) → caller source line
→ Tìm bug!
```

---

## 24.3 Câu Hỏi 2: "CPU đang ở context nào?"

```
EXC_RETURN trong LR của HardFault handler:
0xFFFFFFF1 → Nested exception (trong ISR, fault vào ISR khác)
0xFFFFFFF9 → Thread mode, MSP (bare metal main loop)
0xFFFFFFFD → Thread mode, PSP (RTOS task)

xPSR bits 8-0:
0x00       → Thread mode
0x01-0x0F  → System exception (SysTick=0xF, PendSV=0xE, ...)
0x10+      → External IRQ (0x10=IRQ0, 0x11=IRQ1, ...)
```

**Tại sao quan trọng?**
```
Nếu crash trong RTOS task (PSP):
→ Đọc PSP để lấy stack frame
→ Stack corruption ở task stack
→ Check task stack size
→ Check context switch code

Nếu crash trong ISR (MSP):
→ Check ISR đang làm gì không phù hợp
→ Check nested interrupt depth
→ Check MSP stack size
→ ISR blocking? printf? malloc?
```

---

## 24.4 Câu Hỏi 3: "Dữ Liệu Hay Code Bị Corrupt?"

```
                    ┌─────────────────────────────────┐
                    │         CRASH ROOT CAUSE        │
                    └───────────┬─────────────────────┘
                                │
              ┌─────────────────┼──────────────────┐
              ▼                 ▼                  ▼
       DATA corrupt       CODE corrupt        LOGIC error
              │                 │                  │
              ▼                 ▼                  ▼
       NULL/bad ptr       Flash wear/ECC      Race condition
       Buffer overflow    CRC mismatch        Uninitialized var
       Uninitialized      Flash latency       Integer overflow
       Stack overflow     Cosmic ray          Off-by-one
```

**Cách phân biệt:**
```
DATA corrupt:
  BFAR/MMFAR có địa chỉ dữ liệu bị truy cập
  PC trong Flash OK, nhưng register chứa giá trị rác
  LR/PC = ASCII value hoặc stack canary

CODE corrupt (flash issue):
  UFSR.UNDEFINSTR khi execute "valid" flash address
  Chỉ xảy ra ở temperature/voltage extreme
  Flash read CRC fail

LOGIC error:
  Không có fault register bất thường
  Behavior sai nhưng không crash (harder to find!)
```

---

## 24.5 Câu Hỏi 4: "Crash Có Tái Hiện Được Không?"

```
LUÔN tái hiện → Deterministic bug
  → Debug build + breakpoint + inspect
  → Thêm assert() để bắt sớm hơn

Phụ thuộc thời gian → Race condition
  → Disable interrupts và test từng phần
  → Thêm mutex/barrier
  → Kiểm tra shared data access

Phụ thuộc input → Input validation
  → Fuzzing test với input boundaries
  → Thêm input sanitization

Ngẫu nhiên, production only → Environment/Hardware
  → Temperature, voltage, EMI
  → Flash wait states, clock configuration
  → Watchdog + recovery logic
  → Flash/RAM integrity check
```

---

## 24.6 Câu Hỏi 5: "Stack Có Đủ Không?"

```
Tính stack usage worst case:
  Max stack = max_call_chain_depth × stack_per_frame
  
  stack_per_frame = saved_registers (32B) + LR (4B) 
                  + local_variables + alignment
  
  Interrupt thêm: 32B hardware frame mỗi lần nest
  
Rule of thumb: Stack = 4 × (calculated minimum)
```

**Công cụ kiểm tra:**
```bash
# Compile với stack usage tracking:
gcc -fstack-usage -c file.c
# → Tạo file.su với stack usage từng function

# Runtime (FreeRTOS):
uxTaskGetStackHighWaterMark(task_handle);
# Trả về số WORDS còn lại (0 = đã overflow!)

# GCC warning:
# -Wstack-usage=N  (warning nếu stack frame > N bytes)
```

---

## 24.7 Câu Hỏi 6: "Interrupt Handler Có An Toàn Không?"

```
ISR SAFETY CHECKLIST:
┌──────────────────────────────────────────────────────────┐
│ ✓ Không gọi blocking function (sleep, mutex với timeout) │
│ ✓ Không gọi printf/scanf (không re-entrant)             │
│ ✓ Không gọi malloc/free (heap không re-entrant)         │
│ ✓ Tất cả shared data protected (volatile, atomic, ...)   │
│ ✓ ISR execution time đủ ngắn                            │
│ ✓ FreeRTOS: dùng API FromISR (xQueueSendFromISR, ...)   │
│ ✓ Không vô tình enable nested interrupt nguy hiểm       │
│ ✓ MSP stack đủ cho nested interrupt worst case          │
└──────────────────────────────────────────────────────────┘

Tính MSP stack worst case:
  ISR nesting depth × 32 bytes (hardware frame) 
  + Mỗi ISR's local variables
  + Safety margin (2×)
```

---

## 24.8 Câu Hỏi 7: "Có Race Condition Không?"

```
Race condition xảy ra khi:
  2+ execution contexts (tasks/ISRs) access shared data
  Ít nhất 1 context WRITE vào shared data
  Không có proper synchronization

Dấu hiệu:
  Crash xảy ra ngẫu nhiên
  Crash phụ thuộc CPU frequency hoặc optimization level
  Bug biến mất khi thêm printf (timing thay đổi)
  Bug biến mất khi compile -O0

Kiểm tra:
  1. Tìm tất cả global/static variables
  2. Xem ai đọc/ghi vào từng variable
  3. >1 context access + có write → potential race condition

Fix:
  - __disable_irq() / __enable_irq() (critical section)
  - RTOS: mutex, semaphore, queue
  - Atomic: __LDREXW/__STREXW (Cortex-M Exclusive Access)
  - Data snapshot trong critical section
```

---

## 24.9 Câu Hỏi 8: "Có Tôi Đang Debug Đúng Bug Không?"

```
"Symptom ≠ Root Cause" — Nguyên tắc quan trọng nhất.

Symptom:    "comm_task crash"
Root cause: "sensor_task stack overflow corrupt comm_task stack"

Symptom:    "PC = random address"
Root cause: "buffer overflow overwrite saved LR on stack"

Symptom:    "data wrong sau context switch"
Root cause: "race condition giữa ISR và main task"

5-Why Technique:
Symptom: "HardFault INVSTATE"
Why 1: PC bit 0 = 0 → ARM mode
Why 2: PC load từ stack frame bị corrupt
Why 3: Stack bị ghi đè bởi buffer overflow
Why 4: strcpy() không check length
Why 5: Input không được validate trước khi dùng

Root cause: Missing input validation
Fix: Add input length check trước strcpy()
```

---

## 24.10 Mental Model Summary

```
╔═══════════════════════════════════════════════════════════════════╗
║              SENIOR DEBUG MENTAL MODEL — 8 QUESTIONS             ║
╠═══════════════════════════════════════════════════════════════════╣
║                                                                   ║
║  HardFault / Bug xảy ra                                          ║
║       │                                                           ║
║       ▼                                                           ║
║  Q1: "Fault ở đâu?" → PC + addr2line + disassembly              ║
║       │                                                           ║
║       ▼                                                           ║
║  Q2: "Context nào?" → EXC_RETURN + xPSR (Thread/Handler/ISR)    ║
║       │                                                           ║
║       ▼                                                           ║
║  Q3: "Data hay Code bị lỗi?" → CFSR + BFAR + MMFAR analysis    ║
║       │                                                           ║
║       ▼                                                           ║
║  Q4: "Tái hiện được không?" → Deterministic / Timing / Env      ║
║       │                                                           ║
║       ▼                                                           ║
║  Q5: "Stack đủ không?" → Watermark + Stack usage analysis        ║
║       │                                                           ║
║       ▼                                                           ║
║  Q6: "ISR an toàn không?" → ISR safety checklist               ║
║       │                                                           ║
║       ▼                                                           ║
║  Q7: "Race condition không?" → Shared data analysis             ║
║       │                                                           ║
║       ▼                                                           ║
║  Q8: "Đúng bug chưa?" → 5-Why, Symptom vs Root cause           ║
║       │                                                           ║
║       ▼                                                           ║
║  ROOT CAUSE → FIX → VERIFY → DOCUMENT → PREVENT RECURRENCE     ║
╚═══════════════════════════════════════════════════════════════════╝
```

---

## 24.11 Kỹ Năng Debug Theo Level

```
JUNIOR:
  ✓ Đặt breakpoint tại dòng C trong IDE
  ✓ Xem variable trong watch window
  ✓ Step over/into function
  ✗ Đọc register dump
  ✗ Hiểu HardFault

MID-LEVEL:
  + Đọc được register dump cơ bản (PC, LR, SP)
  + Viết HardFault handler đơn giản
  + Dùng addr2line để map PC → source
  + Phân biệt CFSR các flag cơ bản

SENIOR:
  + Đọc disassembly và hiểu từng instruction
  + Walk stack frame thủ công
  + Debug imprecise fault (DSB technique)
  + Debug race condition và timing issue
  + Debug production issue từ telemetry (no debugger)
  + Viết custom fault handler với full analysis
  + Phân tích GDB/Ozone dump file offline

PRINCIPAL:
  + Phân tích firmware từ binary dump (no source, no symbols)
  + Debug silicon errata issues
  + Phân tích EMI/ESD induced crash
  + Thiết kế architecture phòng tránh class of bugs
  + Mentor team về embedded debugging methodology
```

---

# TÀI LIỆU THAM KHẢO

## Tài Liệu Chính Thức ARM

1. **ARM Cortex-M3/M4 Technical Reference Manual**
   - Chương: Programmer's Model, Exception Model, Fault Handling
   - URL: developer.arm.com/documentation/ddi0403

2. **ARMv7-M Architecture Reference Manual**
   - Chi tiết về instruction set, registers, memory model, exception behavior
   - URL: developer.arm.com/documentation/ddi0403/ed

3. **Procedure Call Standard for the Arm Architecture (AAPCS)**
   - Calling convention, register usage, stack alignment rules
   - URL: developer.arm.com/documentation/ihi0042

4. **ARM Cortex-M4F Device Generic User Guide**
   - FPU registers, lazy stacking, DSP instructions

## Tài Liệu STM32F4

5. **RM0090 Reference Manual** (STM32F405/407/415/417)
   - Memory map, peripheral registers, fault handling registers
   - URL: st.com/resource/en/reference_manual/rm0090

6. **PM0214 Programming Manual** (STM32F3/F4 Cortex-M4)
   - Core registers, Thumb instruction set, exception handling in detail

## FreeRTOS

7. **FreeRTOS Reference Manual** — freertos.org
   - Task management, stack sizing, uxTaskGetStackHighWaterMark
   - Stack overflow detection hooks

8. **Mastering the FreeRTOS Real Time Kernel** (Richard Barry, free PDF)
   - Context switch internals, PendSV implementation, stack management

## Sách Kỹ Thuật

9. **"The Definitive Guide to ARM Cortex-M3 and Cortex-M4 Processors"**
   - Joseph Yiu — Sách tốt nhất và toàn diện nhất về Cortex-M

10. **"Programming Embedded Systems in C and C++"** 
    - Michael Barr — Best practices, defensive programming, debugging

11. **"Making Embedded Systems"** — Elecia White
    - Design patterns, debugging methodology

## Công Cụ Debug

12. **GDB for ARM**: `arm-none-eabi-gdb` — Free, powerful
13. **addr2line**: `arm-none-eabi-addr2line -e firmware.elf 0xADDRESS`
14. **objdump**: `arm-none-eabi-objdump --disassemble firmware.elf`
15. **SEGGER Ozone**: Debugger chuyên nghiệp, free tier có sẵn
16. **Percepio Tracealyzer**: RTOS trace visualization
17. **STM32CubeIDE**: Free IDE với debugger tích hợp, FaultAnalyzer view

---

# LỜI KẾT

## Hành Trình Từ Junior Đến Senior

Khi bắt đầu, một HardFault là thảm họa — firmware chết, không biết tại sao, reset và hope for the best. Qua thời gian, với mỗi bug được debug, mỗi register được hiểu rõ hơn, HardFault trở thành... một bài toán thú vị.

Tài liệu này không phải để bạn đọc một lần rồi thôi. Nó là **reference** — mỗi khi gặp HardFault, mở Chương 17. Mỗi khi viết RTOS code, xem lại Chương 18. Mỗi khi đọc disassembly, tra Chương 19.

## Những Điều Quan Trọng Nhất

```
1. PC từ stack frame = instruction gây fault (không phải PC register!)
2. CFSR cho biết LOẠI lỗi, BFAR/MMFAR cho biết ĐỊA CHỈ lỗi
3. HardFault thường là escalation từ fault khác → đọc CFSR trước
4. Stack overflow dấu hiệu: STKERR, SP < stack_bottom, LR/PC rác
5. Symptom ≠ Root Cause (crash ở task B nhưng bug ở task A)
6. ISR phải nhanh, không block, không printf, không malloc
7. PSP cho RTOS tasks, MSP cho kernel/exceptions — hai stack riêng biệt
8. R4-R11 KHÔNG được hardware save — RTOS phải save/restore thủ công
9. Imprecise fault: thêm DSB để convert thành precise fault
10. Production crash chỉ ở 85°C → check flash wait states!
```

## Lời Khuyên Cuối

**Debug là nghệ thuật đặt câu hỏi đúng.** Không phải về việc biết câu trả lời ngay, mà về việc biết cần hỏi điều gì tiếp theo.

Mỗi crash là cơ hội học hỏi. Mỗi bug được fix là kinh nghiệm tích lũy. Sau 1000 bugs, bạn sẽ nhìn register dump và biết ngay root cause — không phải vì bạn giỏi hơn, mà vì bạn đã từng thấy pattern đó trước đây.

**Chúc bạn debug thành công và crash ít thôi!**

---

*Tài liệu này là Phần 3 (Chương 17-24) của series "CPU và Registers trong ARM Cortex-M"*  
*Phần 1 (Chương 1-8): Kiến thức nền tảng*  
*Phần 2 (Chương 9-16): Nâng cao*  
*Phần 3 (Chương 17-24): Thực chiến*

---

**END OF DOCUMENT**
