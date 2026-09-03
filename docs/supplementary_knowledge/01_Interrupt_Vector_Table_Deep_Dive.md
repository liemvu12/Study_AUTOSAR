# 🔌 CHUYÊN KHẢO KIẾN TRÚC PHẦN CỨNG: BẢNG VECTOR NGẮT (INTERRUPT VECTOR TABLE), NVIC & HỆ ĐIỀU HÀNH AUTOSAR OS (ASKAR)

> **Tài liệu bổ trợ chuyên sâu cho dự án Study_AUTOSAR**  
> **Tác giả:** Senior Automotive Embedded Engineer / AUTOSAR BSW Architect  
> **Mục tiêu:** Bóc tách bản chất từ phần cứng silicon (ARM Cortex-M NVIC / Infineon TriCore / Renesas RH850) ➔ Hợp ngữ Startup ➔ Linker Script ➔ Bộ điều phối ngắt AUTOSAR OS (`askar`) ➔ Tầng MCAL Drivers (`Can.c`, `Mcu.c`) ➔ Ngăn xếp ComStack BSW.  
> **Nền tảng thực nghiệm:** 100% mã nguồn gốc từ dự án `as` (Board `lm3s6965evb`, `stm32f107vc`, nhân `askar`, MCAL CAN/LIN/ETH).

---

## 📑 MỤC LỤC

1. [Chương 1: Mental Model — Cái Nhìn Toàn Cảnh Về Ngắt & Vector Table Trong ECU Ô Tô](#ch1)
2. [Chương 2: Interrupt Vector Table Ở Cấp Bộ Nhớ (Flash, RAM, VTOR & Alignment)](#ch2)
3. [Chương 3: Vi Kiến Trúc NVIC & ARM Cortex-M Core Deep Dive](#ch3)
4. [Chương 4: Code Thực Tế Trong Dự Án as — Startup + Linker Script + ISR](#ch4)
5. [Chương 5: Interrupt Flow Ở Cấp CPU Core (Auto-Stacking & EXC_RETURN)](#ch5)
6. [Chương 6: Cấu Hình Mức Ưu Tiên Ngắt (Priority, Preemption & Sub-Priority)](#ch6)
7. [Chương 7: Cơ Chế Ngắt Trong Hệ Điều Hành AUTOSAR OS (askar) — ISR Cat 1 vs Cat 2 & Preemption](#ch7)
8. [Chương 8: Kiến Trúc Bootloader Ô Tô & Tái Định Vị Vector Table (AUTOSAR asboot & FOTA)](#ch8)
9. [Chương 9: Debugging Vector Table — 5 Case Study Thực Tế Trong Phát Triển ECU](#ch9)
10. [Chương 10: Quy Trình Debug Chuyên Sâu Với GDB & QEMU Trong Dự Án as](#ch10)
11. [Chương 11: 15+ Sai Lầm Phổ Biến Của Kỹ Sư Khi Làm Việc Với Ngắt & AUTOSAR OS](#ch11)
12. [Chương 12: So Sánh Kiến Trúc Ngắt Các Dòng Chip Ô Tô (Cortex-M vs AURIX TriCore vs RH850 vs Cortex-A)](#ch12)
13. [Chương 13: Vòng Đời Khởi Tạo Hệ Thống Từ Vector Table Đến AUTOSAR OS Runtime (`reset_handler` ──► `EcuM_Init` ──► `StartOS`)](#ch13)
14. [Chương 14: Nguyên Tắc Thiết Kế Ngắt Chuẩn Mực Trong AUTOSAR BSW & MCAL Drivers](#ch14)
15. [Chương 15: Phân Tích Hiệu Năng Thời Gian Thực (WCET, Jitter & CPU Load Budget)](#ch15)
16. [Chương 16: 10 Bài Tập Thực Chiến Tăng Dần Độ Khó Trên Dự Án as](#ch16)
17. [Chương 17: Senior Automotive Mindset — Thấu Hiểu Bản Chất Từ Phần Cứng Đến BSW](#ch17)
18. [Chương 18: Master Debug Checklist Cho Kỹ Sư AUTOSAR & Tài Liệu Tham Khảo](#ch18)

---

<a name="ch1"></a>
## CHƯƠNG 1: MENTAL MODEL — CÁI NHÌN TOÀN CẢNH

### 1.1 Interrupt Là Gì Ở Cấp Độ Hardware?

#### 🎯 WHY — Tại Sao Cơ Chế Interrupt Là Sinh Mạng Của Hệ Thống Ô Tô (ECU)?
CPU trong một ECU ô tô (Engine Controller, Inverter Traction, Brake System, Gateway) là một cỗ máy xử lý tuần tự (sequential machine). Tuy nhiên, các sự kiện an toàn và động lực học bên ngoài xe lại xảy ra hoàn toàn bất đồng bộ (asynchronous) với yêu cầu phản ứng tính bằng micro-giây:
- Một bản tin mạng CAN FD điều khiển góc lái hoặc phanh khẩn cấp truyền tới Controller Mailbox cần phản hồi trong **50 micro-giây**.
- Cảm biến góc quay trục khuỷu hoặc cảm biến tốc độ bánh xe (Wheel Speed Sensor) kích hoạt ngắt Timer Input Capture mỗi **100 micro-giây** để tính toán góc phun nhiên liệu / thời điểm mở van.
- Mạch giám sát dòng điện pha Inverter (Shunt Resistor) kích hoạt ngắt ADC Watchdog khi dòng điện vượt ngưỡng an toàn để bảo vệ transistor công suất IGBT/SiC trong vòng **dưới 2 micro-giây**.
- Nếu CPU liên tục đọc thăm dò (polling / busy-waiting), nó sẽ chiếm dụng 100% tải tính toán, dẫn đến trễ deadline và vi phạm nghiêm trọng tiêu chuẩn an toàn chức năng ISO 26262 ASIL-D.

#### 💡 GIẢI PHÁP: CƠ CHẾ NGẮT PHẦN CỨNG (HARDWARE INTERRUPT)
Hardware Interrupt là một đường dây vật lý (physical silicon wire) nối từ các khối ngoại vi (CAN Controller, ADC, Timers) đến bộ điều khiển ngắt (NVIC) và CPU core:
1. Ngoại vi kéo đường tín hiệu ngắt (IRQ line) lên mức tích cực (Active High).
2. CPU tạm dừng luồng thực thi chính (Main Thread / OS Task) một cách an toàn.
3. CPU chuyển sang Handler Mode để thực thi chương trình con phục vụ ngắt (**ISR — Interrupt Service Routine**, ví dụ `Can_RxIsr`).
4. Sau khi ISR xử lý xong, CPU khôi phục lại trạng thái ban đầu và tiếp tục chạy chương trình chính.

```
+--------------------+        +--------------------+        +--------------------+
|  AUTOMOTIVE PERIPH |        | INTERRUPT CNTRLR   |        |   CPU CORE (ARM)   |
|                    |        |     (NVIC)         |        |                    |
|  CAN RX Mailbox    |------->|                    |------->|  Đang chạy Task    |
|  ADC Current Sense |  IRQ   |  - Phân xử ưu tiên |  nIRQ  |  ComStack / ASW    |
|  Wheel Speed Timer | (Line) |  - Lọc BASEPRI     | (Core) |                    |
|  Watchdog Warning  |        |  - Kích hoạt vector|        |  TẠM DỪNG          |
+--------------------+        +--------------------+        |  Nhảy vào MCAL ISR |
                                                            +--------------------+
```

---

### 1.2 Phân Biệt 6 Khái Niệm Cốt Lõi: Interrupt, Exception, Trap, Fault, Reset, Software Interrupt

Đây là điểm mà các kỹ sư Junior và Mid-level thường xuyên nhầm lẫn trong các buổi phỏng vấn kỹ thuật:

| Thuật Ngữ | Tính Chất | Nguồn Gốc Phát Sinh | Ví Dụ Điển Hình |
|---|---|---|---|
| **Interrupt (Ngắt)** | **Asynchronous** (Bất đồng bộ) | Tín hiệu phần cứng từ bên ngoài CPU core. Không thể dự đoán chính xác thời điểm xảy ra theo dòng lệnh. | UART RX, Timer Update, CAN Message RX, GPIO Exti. |
| **Exception (Ngoại lệ)** | **Thuật ngữ bao quát (Umbrella Term)** | Mọi sự kiện khiến CPU thay đổi chế độ thực thi (Mode switch) để chạy một đoạn handler riêng biệt. | ARM Cortex-M gọi chung cả Reset, Faults, SVC, SysTick và IRQ là **Exceptions**. |
| **Trap (Bẫy lệnh)** | **Synchronous** (Đồng bộ) | Phát sinh có chủ đích bởi chính câu lệnh mà CPU vừa thực thi. Hoàn toàn tái hiện được tại vị trí lệnh đó. | Lệnh gọi hàm hệ điều hành `SVC #0`, lệnh dừng điểm ngắt `BKPT`. |
| **Fault (Lỗi phần cứng)** | **Synchronous / Asynchronous** | CPU phát hiện vi phạm kiến trúc, lỗi truy cập bộ nhớ hoặc giải mã lệnh không hợp lệ. | Chia cho 0 (`DIVBYZERO`), truy cập địa chỉ rác (`BusFault`), vi phạm vùng bảo vệ MPU (`MemManage`). |
| **Reset** | **Khởi tạo lại phần cứng** | Tín hiệu phần cứng khôi phục CPU về trạng thái ban đầu. Luôn có mức ưu tiên cao nhất tuyệt đối (-3). | Bật nguồn (POR), chân NRST, Watchdog Timeout, Software Reset. |
| **Software Interrupt** | **Kích hoạt bằng phần mềm** | Phần mềm ghi vào thanh ghi phần cứng của Interrupt Controller để giả lập tín hiệu IRQ. | Ghi vào thanh ghi `NVIC->STIR` hoặc set bit pending trong `SCB->ICSR` (PendSV). |

```
BẢNG PHÂN LOẠI EXCEPTION TRÊN ARM CORTEX-M:
Exception # | Tên Exception           | Loại        | Mức Ưu Tiên (Priority)
------------|-------------------------|-------------|-------------------------
1           | Reset                   | Reset       | -3 (Cao nhất tuyệt đối)
2           | NMI (Non-Maskable Int)  | Interrupt   | -2 (Không thể mask)
3           | HardFault               | Fault       | -1 (Cố định)
4           | MemManage               | Fault       | Cấu hình được (0-255)
5           | BusFault                | Fault       | Cấu hình được
6           | UsageFault              | Fault       | Cấu hình được
7-10        | Reserved                | -           | -
11          | SVCall (SVC)            | Trap        | Cấu hình được
12          | DebugMonitor            | Debug Trap  | Cấu hình được
13          | Reserved                | -           | -
14          | PendSV                  | SW Interrupt| Cấu hình được (Thường thấp nhất)
15          | SysTick                 | Interrupt   | Cấu hình được
16+ (IRQ0+) | External Peripherals    | HW Interrupt| Cấu hình được
```

---

### 1.3 Chu Trình Xử Lý Ngắt Chi Tiết (Hardware Execution Flow)

Dưới đây là luồng hoạt động chuẩn xác từng bước ở cấp độ vi kiến trúc phần cứng khi một ngắt xảy ra:

```
[BƯỚC 1: NGOẠI VI TRIGGER SỰ KIỆN]
Ngoại vi hoàn thành tác vụ (ví dụ: Timer đếm tràn ARR, UART nhận đủ 8 bit data).
Cờ sự kiện phần cứng (Hardware Flag) được set (ví dụ: TIM2->SR bit UIF = 1).
    │
    ▼
[BƯỚC 2: TÍN HIỆU IRQ TRUYỀN ĐẾN INTERRUPT CONTROLLER]
Ngoại vi kích hoạt đường dây tín hiệu vật lý nối thẳng đến NVIC.
    │
    ▼
[BƯỚC 3: NVIC KIỂM ĐỊNH ĐIỀU KIỆN (ARBITRATION & FILTERING)]
NVIC thực hiện các bước kiểm tra phần cứng:
1. Ngoại vi này có được bật trong NVIC không? (Kiểm tra bit trong NVIC->ISER).
2. Priority của ngắt này có cao hơn ngắt đang thực thi (nếu có) không?
3. Mức ưu tiên có bị chặn bởi thanh ghi BASEPRI / PRIMASK không?
Nếu đủ điều kiện ➔ NVIC kéo đường nIRQ nối vào CPU core và chuyển trạng thái ngắt thành PENDING.
    │
    ▼
[BƯỚC 4: CPU CORE CHẤP NHẬN NGẮT (INTERRUPT ACCEPTANCE)]
CPU core kết thúc chu kỳ thực thi của câu lệnh HIỆN TẠI (hoặc hủy lệnh nếu hỗ trợ ngắt đa chu kỳ).
CPU chuyển từ Thread Mode sang Handler Mode (Luôn chạy ở đặc quyền Privileged).
    │
    ▼
[BƯỚC 5: LƯU TRỮ NGỮ CẢNH TỰ ĐỘNG (AUTO-STACKING HARDWARE)]
Hardware CPU tự động đẩy (PUSH) 8 thanh ghi quan trọng xuống Stack (MSP hoặc PSP):
{R0, R1, R2, R3, R12, LR, PC, xPSR} (Tổng cộng 32 bytes = 8 words).
    │
    ▼
[BƯỚC 6: TRA CỨU VECTOR BẢNG NGẮT (VECTOR TABLE LOOKUP)]
CPU đọc địa chỉ cơ sở của bảng ngắt từ thanh ghi VTOR (Vector Table Offset Register).
CPU tính toán địa chỉ chứa con trỏ hàm ISR: Address = VTOR + (Exception_Number * 4).
CPU đọc 4 bytes tại địa chỉ này từ Flash/RAM ➔ Lấy được địa chỉ vào của hàm ISR.
    │
    ▼
[BƯỚC 7: THIẾT LẬP THANH GHI VÀ NHẢY VÀO ISR]
1. PC được gán bằng địa chỉ ISR (bit 0 tự động nạp vào Thumb state bit của EPSR).
2. LR (Link Register) được gán giá trị đặc biệt gọi là EXC_RETURN (ví dụ: 0xFFFFFFF9).
3. NVIC chuyển trạng thái ngắt từ PENDING sang ACTIVE.
    │
    ▼
[BƯỚC 8: THỰC THI HÀM ISR (C CODE)]
Mã nguồn hàm ngắt do lập trình viên viết được thực thi.
Bắt buộc phải xóa cờ ngắt của ngoại vi (Clear Peripheral Interrupt Flag).
    │
    ▼
[BƯỚC 9: KẾT THÚC NGẮT VÀ TRỞ VỀ (EXCEPTION RETURN)]
Hàm ISR thực hiện lệnh kết thúc hàm (BX LR).
CPU nhận diện giá trị EXC_RETURN trong thanh ghi LR (bit 31:28 = 0xF).
    │
    ▼
[BƯỚC 10: TỰ ĐỘNG KHÔI PHỤC NGỮ CẢNH (AUTO-UNSTACKING)]
Hardware CPU tự động POP 8 thanh ghi {R0-R3, R12, LR, PC, xPSR} từ Stack trở lại CPU core.
SP tự động tăng 32 bytes trở về vị trí cũ.
    │
    ▼
[BƯỚC 11: CHƯƠNG TRÌNH CHÍNH TIẾP TỤC]
CPU nạp lại Program Counter (PC) từ giá trị vừa khôi phục và tiếp tục chạy mã nguồn bình thường.
```

---

### 1.4 Câu Hỏi Kiểm Tra Tư Duy — Chương 1

1. **Câu 1:** Một Timer Interrupt kích hoạt đúng lúc CPU đang thực thi câu lệnh nhân đa chu kỳ `MUL R0, R1, R2`. CPU sẽ xử lý thế nào? Đúng hay sai khi cho rằng *"CPU sẽ lập tức cắt ngang câu lệnh đang chạy dở để vào ngắt ngay chu kỳ đó"*?
2. **Câu 2:** Có phải mọi ngắt phần cứng khi được kích hoạt thì CPU đều nhảy vào ISR ngay lập tức không? Hãy phân tích ít nhất 3 rào cản phần cứng/phần mềm có thể trì hoãn việc thực thi ISR.
3. **Câu 3:** Một kỹ sư Junior khẳng định: *"Tôi đã bật Enable Interrupt trong thanh ghi NVIC->ISER của MCU rồi, chắc chắn ngắt sẽ hoạt động"*. Hãy chỉ ra ít nhất 4 điều kiện tiên quyết khác còn thiếu khiến ngắt vẫn không thể chạy.

---

<a name="ch2"></a>
## CHƯƠNG 2: INTERRUPT VECTOR TABLE Ở CẤP MEMORY

### 2.1 Interrupt Vector Table Là Gì Ở Cấp Độ Byte Bộ Nhớ?

* **KHÔNG PHẢI:** Một danh sách chuỗi ký tự tên hàm (Function Name Strings).
* **KHÔNG PHẢI:** Một khối logic phần cứng nằm bên trong NVIC.
* **BẢN CHẤT CHÍNH XÁC:** Là một **mảng tĩnh (Array) chứa các địa chỉ con trỏ 32-bit liên tiếp** nằm trong không gian nhớ (Flash hoặc RAM). Mỗi phần tử 4-byte chứa địa chỉ của hàm ISR tương ứng với Exception Vector đó.

```c
/* Bản chất của Vector Table trong bộ nhớ chỉ là một mảng hằng số 32-bit: */
const uint32_t Vector_Table[] = {
    0x20020000,   /* [0] Initial Main Stack Pointer (MSP) Value */
    0x08000109,   /* [1] Reset_Handler Address (0x08000108 | Thumb bit 1) */
    0x08000215,   /* [2] NMI_Handler Address */
    0x08000221,   /* [3] HardFault_Handler Address */
    /* ... các exception khác ... */
    0x08001501,   /* [44] TIM2_IRQHandler Address (Exception #44 / IRQ28) */
};
```

---

### 2.2 Vị Trí Của Vector Table Trong Sơ Đồ Bộ Nhớ (Memory Map)

```
SƠ ĐỒ BỘ NHỚ CHI TIẾT (VÍ DỤ STM32F4 / CORTEX-M4):

Địa chỉ cao
0xFFFFFFFF +------------------------------------+
           |  Cortex-M Internal Peripherals     |
           |  (NVIC, SCB, SysTick, MPU...)       |
0xE0000000 +------------------------------------+
           |  Chip-Specific Peripherals         |
           |  (USART, TIM, CAN, SPI, GPIO...)   |
0x40000000 +------------------------------------+
           |  Internal SRAM (128 KB)            |
           |  .data, .bss, Heap, Stack          |
0x20000000 +------------------------------------+
           |                                    |
           |  Internal Flash (1024 KB / 1 MB)   |
           |  .text (Code), .rodata (Constants) |
           |                                    |
0x08000000 +------------------------------------+  <-- BẮT ĐẦU FLASH VẬT LÝ
           |  Vector Table (Kích thước ~400B)   |
           |  [0] Initial MSP Value (4 Bytes)   |  <-- Nạp vào SP khi Boot
           |  [1] Reset_Handler Addr (4 Bytes)  |  <-- Nạp vào PC khi Boot
           |  [2] NMI_Handler Addr (4 Bytes)    |
           |  [3] HardFault_Handler Addr        |
           |  ...                               |
           |  [44] TIM2_IRQHandler Addr        |
0x08000000 +------------------------------------+
           |                                    |
0x00000000 +------------------------------------+  <-- VÙNG BOOT ALIAS
           |  Boot Alias Memory Area            |  <-- Ánh xạ tới 0x08000000 khi Boot từ Flash
0x00000000 +------------------------------------+
Địa chỉ thấp
```

#### ❓ Tại Sao Vector Table Luôn Nằm Ở Đầu Flash?
Khi phần cứng ARM Cortex-M cấp nguồn (Power-On Reset), CPU hoàn toàn chưa chạy bất kỳ dòng code nào và thanh ghi VTOR mặc định bằng `0x00000000`. Phần cứng CPU được "hardwired" bất di bất dịch theo kiến trúc ARM:
1. Đọc **4 bytes tại địa chỉ 0x00000000** ➔ Tự động gán vào thanh ghi **MSP (Main Stack Pointer)**.
2. Đọc **4 bytes tại địa chỉ 0x00000004** ➔ Tự động gán vào thanh ghi **PC (Program Counter)**.
3. Nhảy thẳng đến địa chỉ trong PC để thực thi lệnh đầu tiên của `Reset_Handler`.

Do đó, Vector Table bắt buộc phải nằm tại địa chỉ `0x00000000` (hoặc vùng Flash được ánh xạ / alias tới `0x00000000`).

---

### 2.3 Cấu Trúc Của Từng Entry Trong Vector Table — Cẩm Nang Dành Cho Người Mới Bắt Đầu

#### 🔰 2.3.1 "Entry" Là Gì? (Mental Model Dễ Hiểu)

Nếu coi **Vector Table** là một cuốn **"Danh bạ điện thoại"** hoặc một **"Kệ tủ có đánh số ngăn"**:
* Mỗi **"Entry"** (mục nhập / phần tử) chính là **một ô nhớ 32-bit (đúng 4 bytes)** nằm liên tiếp nhau trong bảng.
* Trong lập trình C, nếu Vector Table là một mảng `uint32_t Vector_Table[N]`, thì mỗi `Vector_Table[i]` chính là một **Entry thứ `i`**.

```
VÍ DỤ TRỰC QUAN VỀ KHÁI NIỆM "ENTRY":

    BẢNG VECTOR TABLE (CUỐN DANH BẠ ĐỊA CHỈ TRONG FLASH):
    Địa chỉ Flash    Vị trí Entry      Nội dung chứa bên trong (4 bytes)       Ý nghĩa / Tác dụng
    ┌────────────┬──────────────────┬───────────────────────────────────────┬──────────────────────────────────────────┐
    │ 0x08000000 │    Entry [0]     │ 0x20020000 (Địa chỉ đỉnh RAM)         │ Nạp vào Main Stack Pointer (MSP) khi Boot │
    ├────────────┼──────────────────┼───────────────────────────────────────┼──────────────────────────────────────────┤
    │ 0x08000004 │    Entry [1]     │ 0x08000109 (Địa chỉ Reset_Handler)    │ Nạp vào Program Counter (PC) khi Boot    │
    ├────────────┼──────────────────┼───────────────────────────────────────┼──────────────────────────────────────────┤
    │ 0x08000008 │    Entry [2]     │ 0x08000215 (Địa chỉ NMI_Handler)      │ Nhảy tới khi có sự cố khẩn cấp (NMI)     │
    ├────────────┼──────────────────┼───────────────────────────────────────┼──────────────────────────────────────────┤
    │ 0x0800000C │    Entry [3]     │ 0x08000221 (Địa chỉ HardFault_Handler)│ Nhảy tới khi code bị crash (HardFault)   │
    ├────────────┼──────────────────┼───────────────────────────────────────┼──────────────────────────────────────────┤
    │    ...     │       ...        │                  ...                  │                   ...                    │
    ├────────────┼──────────────────┼───────────────────────────────────────┼──────────────────────────────────────────┤
    │ 0x080000B0 │    Entry [44]    │ 0x08001501 (Địa chỉ TIM2_IRQHandler)  │ Nhảy tới khi Timer 2 đếm tràn            │
    └────────────┴──────────────────┴───────────────────────────────────────┴──────────────────────────────────────────┘
```

---

#### 🎯 2.3.2 Tác Dụng Của Từng Entry Là Gì?
Khi có một sự kiện phần cứng xảy ra (ví dụ: cấp nguồn, lỗi chia cho 0, hoặc Timer đếm tràn), **CPU không hề biết mã xử lý (code C) của bạn nằm ở dòng nào hay file nào trong bộ nhớ Flash rộng lớn hàng Megabyte**.

Tác dụng của từng Entry là đóng vai trò như một **"Tấm biển chỉ đường trực tiếp" (Direct Pointer)**:
1. Mỗi loại ngắt/ngoại lệ được phần cứng gắn chết với một **Số thứ tự ngoại lệ (Exception Number)** cố định.
   > 📌 **Lưu ý cốt lõi (Phân định Cố định vs Khả trình):**  
   > • **Số thứ tự ô nhớ (Slot Index / Exception Number) là CỐ ĐỊNH 100% trong Silicon:**  
   >   - *Entry 1 → 15:* Do hãng **ARM** gắn chết trong kiến trúc lõi CPU (Reset, NMI, HardFault, SVC, SysTick).  
   >   - *Entry 16 trở đi (IRQ0, IRQ1...):* Do **Hãng sản xuất chip (ST, NXP, TI...)** kéo đường dây kim loại vật lý trong vi mạch bán dẫn từ từng ngoại vi (CAN, UART, SPI, Timer) vào các chân cố định của khối NVIC. Lập trình viên **KHÔNG THỂ** thay đổi hay hoán đổi số thứ tự này.  
   > • **Cái "KHẢ TRÌNH / ĐĂNG KÝ ĐƯỢC" thực chất là:**  
   >   - **Địa chỉ con trỏ hàm (Handler Address):** Giá trị ghi *bên trong* ô nhớ đó trỏ tới hàm C nào (đăng ký tĩnh bằng cách viết hàm C trùng tên ghi đè `[WEAK]`, hoặc đăng ký động bằng cách dời bảng ngắt sang RAM qua thanh ghi `VTOR`).  
   >   - **Mức độ ưu tiên (Interrupt Priority):** Lập trình được mức ưu tiên cho từng IRQ qua hàm `NVIC_SetPriority()`.
2. CPU chỉ cần nhìn vào số thứ tự này, tra đúng **Entry số đó**, lấy địa chỉ ghi bên trong và nhảy thẳng tới hàm thực thi mà **không cần chạy bất kỳ lệnh `if / else` hay `switch / case` nào**.

---

#### ⏱️ 2.3.3 CPU Sử Dụng Từng Entry Khi Nào Và Như Thế Nào?

```
CÔNG THỨC PHẦN CỨNG CPU TỰ ĐỘNG TÍNH TOÁN ĐỊA CHỈ ENTRY:
Địa chỉ ô nhớ của Entry = VTOR + (Exception_Number × 4 bytes)
```

CPU sẽ tự động đọc Entry trong các thời điểm cụ thể:

| Loại Sự Kiện | Thời Điểm CPU Đọc Entry | Entry Được Sử Dụng | Hành Động Cụ Thể Của Phần Cứng CPU |
|---|---|---|---|
| **Vừa bật nguồn / Nhấn nút Reset** | Ngay tại chu kỳ xung nhịp đầu tiên khi cấp nguồn. | **Entry [0] & Entry [1]** | 1. Đọc Entry [0] $\rightarrow$ Nạp thẳng vào thanh ghi **MSP** (Chuẩn bị bộ nhớ Stack).<br>2. Đọc Entry [1] $\rightarrow$ Nạp thẳng vào thanh ghi **PC** (Nhảy vào chạy `Reset_Handler`). |
| **Code bị lỗi phần cứng** | Khi code bị chia cho 0, truy cập ô nhớ cấm, hoặc tràn stack. | **Entry [3] (HardFault)**<br>hoặc **[4, 5, 6]** | CPU ngưng chạy code thường, đọc Entry tương ứng và nhảy vào hàm bẫy lỗi để cô lập sự cố. |
| **Hệ điều hành RTOS chuyển Task** | Khi hết lượt chạy (SysTick) hoặc có Task ưu tiên cao hơn thức dậy. | **Entry [14] (PendSV)**<br>& **Entry [15] (SysTick)** | CPU đọc Entry [14]/[15] để chạy mã nguồn đổi ngữ cảnh (Context Switching) của AUTOSAR OS (nhân askar). |
| **Ngoại vi hoàn thành tác vụ** | Khi có dữ liệu UART bay tới, Timer đếm tràn, hoặc nút bấm GPIO được nhấn. | **Entry [16 + IRQn]**<br>*(Ví dụ TIM2 là IRQ 28 $\rightarrow$ Entry 44)* | CPU tạm dừng code chính, tra Entry [44] lấy địa chỉ hàm `TIM2_IRQHandler`, chạy xử lý xong rồi quay về. |

---

#### 🔬 2.3.4 Phân Tích Cấu Trúc Chi Tiết: 2 Loại Entry Trong Bảng

Mọi Entry trong Vector Table đều chiếm đúng **32-bit (4 bytes)**, nhưng được chia làm **2 loại mang bản chất hoàn toàn khác nhau**:

```
CẤU TRÚC PHẦN CỨNG CỦA 2 LOẠI ENTRY:

1. ENTRY [0] — ĐỈNH NGĂN XẾP (INITIAL STACK POINTER):
   Bit [31:0] : Chứa GIÁ TRỊ ĐỊA CHỈ Ô NHỚ ĐỈNH RAM (Ví dụ 0x20020000).
   ⚠️ LƯU Ý  : Đây là GIÁ TRỊ THÔ (RAW VALUE), TUYỆT ĐỐI KHÔNG PHẢI CON TRỎ HÀM!

2. ENTRY [1 ĐẾN N] — CON TRỎ HÀM PHỤC VỤ NGẮT (ISR FUNCTION POINTER):
    31                                                     1   0
   ┌────────────────────────────────────────────────────────┬───┐
   │         Địa chỉ thực tế của hàm ISR trong Flash        │ 1 │  <-- Luôn luôn là Bit 1 (Thumb Bit)
   └────────────────────────────────────────────────────────┴───┘
   • Bit [31:1] : Địa chỉ bắt đầu của hàm mã máy (luôn luôn là địa chỉ chẵn chia hết cho 2 hoặc 4).
   • Bit [0]    : THUMB INDICATOR BIT (BẮT BUỘC PHẢI BẰNG 1).
```

##### 1. Entry [0] — Initial Main Stack Pointer (MSP)
* **Bản chất:** Là một giá trị địa chỉ vùng nhớ RAM (thường là địa chỉ cao nhất của SRAM, ví dụ `0x20005000` hoặc `0x20020000`).
* **Cắt nghĩa "Đỉnh bộ nhớ RAM mới chính thức được thiết lập" nghĩa là gì?**
  * Trong kiến trúc ARM Cortex-M, ngăn xếp hoạt động theo cơ chế **Full-Descending Stack (Ngăn xếp phát triển từ trên đỉnh cao xuống đáy thấp)**:
    ```
    ĐỊA CHỈ CAO (ĐỈNH RAM)  ──► [ 0x2000_5000 ] ◄── Entry [0] nạp giá trị này vào thanh ghi MSP
                                │   [Stack Frame]  │     (Mỗi lần PUSH biến cục bộ: MSP trừ dần 4 bytes)
                                │         ▼        │
                                │   (Vùng trống)   │
                                │         ▲        │
                                │   [Vùng .bss]    │
    ĐỊA CHỈ THẤP (ĐÁY RAM)  ──► [ 0x2000_0000 ]     (Chứa biến toàn cục .data và .bss)
    ```
  * **Trước khi đọc Entry [0]:** Thanh ghi `MSP` chứa giá trị rác (hoặc `0x00000000`). CPU hoàn toàn "mù", không biết RAM nằm ở đâu, nếu có hàm nào gọi PUSH hay tạo biến cục bộ thì CPU sẽ ghi bừa vào địa chỉ rác gây treo chip ngay tức khắc.
  * **Sau khi đọc Entry [0]:** Thanh ghi `MSP` được "cắm mỏ neo" chính xác vào nóc cao nhất của RAM (`0x20005000`). Kể từ thời khắc này, hệ thống đã có một vùng nhớ ngăn xếp hợp lệ, an toàn 100% để sẵn sàng lưu trữ biến cục bộ và ngữ cảnh CPU khi hàm C đầu tiên bắt đầu chạy.
* **Tại sao CPU cần Entry này đầu tiên?**  
  Trong ngôn ngữ C, khi CPU thực thi bất kỳ hàm nào (kể cả hàm `main` hay hàm con), CPU đều cần bộ nhớ Stack để: lưu biến cục bộ, lưu địa chỉ trả về của hàm, và truyền tham số. Nếu chưa có Stack Pointer, CPU không thể chạy bất kỳ dòng code C nào. Vì vậy, phần cứng ARM Cortex-M được thiết kế để tự động nạp SP từ Entry [0] trước cả khi nạp con trỏ lệnh PC từ Entry [1].

##### 2. Entry [1 đến N] — Exception / Interrupt Handler Function Pointers
* **Bản chất:** Là các **con trỏ hàm (Function Pointers)** trỏ tới địa chỉ của các hàm xử lý ngắt (`Reset_Handler`, `HardFault_Handler`, `SysTick_Handler`, `TIM2_IRQHandler`,...).
* **Giải mã "Bí ẩn Thumb Bit (LSB = 1)" cho Newbie:**
  * Lõi ARM Cortex-M chỉ hỗ trợ tập lệnh **Thumb-2** (các lệnh 16-bit và 32-bit thu gọn), **không hỗ trợ tập lệnh ARM 32-bit cổ điển**.
  * Trong kiến trúc ARM, để CPU biết cần giải mã mã máy theo tập lệnh Thumb, địa chỉ nhảy tới bắt buộc phải có **Bit 0 (LSB) được set lên 1**.
  * *Ví dụ thực tế:*  
    Hàm `Reset_Handler` được biên dịch nằm tại địa chỉ ô nhớ chẵn `0x08000108` trong Flash. Khi nạp vào Entry [1] của Vector Table, trình biên dịch (Compiler/Linker) sẽ tự động cộng thêm 1 thành `0x08000109`.  
    Khi CPU đọc `0x08000109`:
    - CPU dùng **Bit 0 = 1** để kích hoạt cờ Thumb state (`T-bit` trong thanh ghi trạng thái EPSR).
    - CPU bỏ bit 0 đi và nhảy tới thực thi lệnh tại địa chỉ chẵn `0x08000108`.
  * 🛑 *Hậu quả nếu mất Thumb Bit (Bit 0 = 0):* CPU sẽ lầm tưởng đây là tập lệnh ARM 32-bit cổ điển, phát hiện kiến trúc Cortex-M không hỗ trợ và lập tức kích hoạt lỗi **UsageFault (INVSTATE)** làm sập hệ thống ngay lập tức!

---

### 2.4 Cơ Chế Tái Định Vị Vector Table (Vector Table Relocation — VTOR)

#### ❓ 2.4.1 Tại Sao Lại Cần VTOR? Chạy Giá Trị Mặc Định Có Gì Không Ổn?

* **Giá trị mặc định là gì?**  
  Khi vừa bật nguồn hoặc Reset, phần cứng ARM Cortex-M luôn gán giá trị mặc định cho thanh ghi VTOR là `0x00000000` (hoặc trỏ tới địa chỉ đầu bộ nhớ Flash `0x08000000`). Nếu hệ thống của bạn là một firmware đơn giản chỉ có duy nhất một file nhị phân chạy từ đầu Flash đến cuối Flash thì **chạy mặc định là HOÀN TOÀN ỔN**.

* **Vậy thì chạy mặc định SẼ BỊ LỖI NẶNG (KHÔNG ỔN) trong các trường hợp nào?**  
  Trong các hệ thống nhúng chuyên nghiệp và phần mềm ô tô (Automotive ECU), hệ thống **bắt buộc phải có nhiều hơn một chương trình cùng tồn tại trong bộ nhớ**:

  1. **Hệ thống có Bootloader và Ứng dụng (OTA / Firmware Update) — Tình huống kinh điển nhất:**
     ```
     BỘ NHỚ FLASH ĐƯỢC CHIA LÀM 2 VÙNG ĐỘC LẬP:
     0x0800_0000 ┌────────────────────────────────────────────────────────┐
                 │ [BOOTLOADER] (Chương trình nạp firmware qua CAN/OTA)   │
                 │ ──► Sở hữu Bảng Vector Table riêng của Bootloader      │
     0x0801_0000 ├────────────────────────────────────────────────────────┤
                 │ [APPLICATION] (Chương trình điều khiển xe chính: ECU)  │
                 │ ──► Sở hữu Bảng Vector Table riêng của Application     │
                 └────────────────────────────────────────────────────────┘
     ```
     * **Cái bẫy nếu không có VTOR:**  
       Bootloader chạy xong kiểm tra hợp lệ và nhảy sang Application tại `0x0801_0000`. Khi xe đang vận hành, một ngắt truyền thông CAN hoặc SysTick của RTOS xảy ra.  
       Nếu CPU vẫn dùng địa chỉ mặc định (`0x0800_0000`), CPU sẽ tra bảng và nhảy vào hàm xử lý ngắt của **Bootloader** (vốn đã dừng chạy từ lâu) thay vì hàm của **Application** $\rightarrow$ **Hệ thống bị sập (Crash / HardFault) hoặc mất kiểm soát ngay lập tức!**  
     * **Giải pháp nhờ VTOR:**  
       Trước khi nhảy sang Application, phần mềm chỉ cần ghi: `SCB->VTOR = 0x08010000;`. Lập tức CPU đổi "tấm biển chỉ đường", mọi ngắt xảy ra từ thời điểm này sẽ tra đúng bảng vector của Application!

  2. **Tăng tốc độ phản hồi ngắt lên tối đa (RAM Vector Table & Zero Wait-State):**  
     Bộ nhớ Flash thường chậm hơn xung nhịp CPU (cần 2 - 5 chu kỳ chờ Flash Wait-States). Bằng cách copy Vector Table lên RAM (`0x2000_0000`) và set `VTOR = 0x2000_0000`, CPU tra cứu bảng ngắt với tốc độ **0 wait-state** (cực nhanh, giảm độ trễ Jitter cho hệ thống điều khiển động cơ / Inverter).

  3. **Đăng ký hàm ngắt động tại Runtime (Dynamic ISR Registration):**  
     Bộ nhớ Flash là Read-Only khi CPU đang chạy thường, bạn không thể thay đổi con trỏ hàm ngắt. Khi dời bảng ngắt lên RAM qua VTOR, bạn có thể tự do ghi đè con trỏ hàm ngắt bất kỳ lúc nào để chuyển đổi chế độ hoạt động linh hoạt.

---

#### ⚙️ 2.4.2 Cách Thức Hoạt Động & Mã Nguồn C Relocation

Trên Cortex-M3/M4/M7/M33, thanh ghi **VTOR (Vector Table Offset Register)** nằm tại địa chỉ `0xE000ED08`. Thanh ghi này cho phép phần mềm thay đổi địa chỉ cơ sở của Vector Table tại runtime:

```c
#define SCB_VTOR   (*((volatile uint32_t*)0xE000ED08))

/* Di chuyển Vector Table sang vùng nhớ mới của Application */
void Relocate_Vector_Table(uint32_t new_base_address) {
    __disable_irq();           /* Tạm khóa ngắt để đảm bảo an toàn */
    SCB_VTOR = new_base_address;
    __DSB();                   /* Data Synchronization Barrier: Đảm bảo ghi xong VTOR */
    __ISB();                   /* Instruction Synchronization Barrier: Flush pipeline */
    __enable_irq();            /* Mở lại ngắt */
}
```

> [!IMPORTANT]
> **Quy Tắc Căn Chỉnh Địa Chỉ Của VTOR (Alignment Rule):**  
> Địa chỉ nạp vào VTOR bắt buộc phải được căn chỉnh (aligned) theo kích thước của Vector Table làm tròn lên lũy thừa của 2:  
> $\text{Alignment} = 2^{\lceil \log_2(\text{Số lượng Exception} \times 4) \rceil}$  
> Ví dụ: MCU có 16 Exception hệ thống + 84 External IRQs = 100 entries $\times$ 4 = 400 bytes ➔ Cần căn chỉnh tối thiểu theo biên **512 bytes** (Địa chỉ phải chia hết cho `0x200`, bit [8:0] của địa chỉ phải bằng 0).

---

### 2.5 Câu Hỏi Kiểm Tra Tư Duy — Chương 2

1. **Câu 1:** CPU Cortex-M đọc giá trị tại Entry [0] của Vector Table để làm gì? Điều gì sẽ xảy ra nếu một kỹ sư vô tình đặt con trỏ hàm `Reset_Handler` vào Entry [0] và đặt địa chỉ Stack vào Entry [1]?
2. **Câu 2:** Một vi điều khiển có tổng cộng 64 External Interrupts. Kích thước tối thiểu của Vector Table là bao nhiêu bytes và yêu cầu căn chỉnh địa chỉ (alignment) khi gán vào thanh ghi VTOR là bao nhiêu?
3. **Câu 3:** Tại sao trong file `.map` hoặc khi dùng GDB kiểm tra Vector Table, địa chỉ của mọi hàm ISR như `SysTick_Handler` hay `USART1_IRQHandler` luôn là số lẻ (kết thúc bằng 1, 3, 5, 7, 9, B, D, F)?

---

<a name="ch3"></a>
## CHƯƠNG 3: ARM CORTEX-M DEEP DIVE

### 3.1 Toàn Bộ Danh Mục Exception Chuẩn Trên Cortex-M

ARM Cortex-M định nghĩa 15 Exception hệ thống (Core Exceptions) cùng tối đa 240 External Interrupts:

```
VỊ TRÍ BẢNG VECTOR EXCEPTION CỦA ARM CORTEX-M:

Vector Index | Exception # | Tên Exception      | Mức Ưu Tiên     | Mô Tả Kỹ Thuật
-------------|-------------|--------------------|-----------------|---------------------------------------------------
0            | 0           | Initial SP         | Không áp dụng   | Giá trị khởi tạo cho Main Stack Pointer (MSP)
1            | 1           | Reset              | -3 (Cố định)    | Thực thi khi Power-on, chân Reset, Watchdog
2            | 2           | NMI                | -2 (Cố định)    | Non-Maskable Interrupt (Không thể bị mask)
3            | 3           | HardFault          | -1 (Cố định)    | Lỗi hệ thống nghiêm trọng / Fault Escalation
4            | 4           | MemManage Fault    | Cấu hình được   | Vi phạm phân quyền vùng nhớ do MPU quản lý
5            | 5           | BusFault           | Cấu hình được   | Lỗi phần cứng bus (AHB/APB), lỗi đọc ghi ô nhớ
6            | 6           | UsageFault         | Cấu hình được   | Lệnh Undefined, chia cho 0, Unaligned access
7 - 10       | 7 - 10      | Reserved           | -               | Dành riêng cho mở rộng phần cứng tương lai
11           | 11          | SVCall (SVC)       | Cấu hình được   | System Service Call kích hoạt bằng lệnh `SVC`
12           | 12          | DebugMonitor       | Cấu hình được   | Điểm dừng Debugger khi không dùng Halt mode
13           | 13          | Reserved           | -               | Dành riêng
14           | 14          | PendSV             | Cấu hình được   | Pendable Service Request (Dùng cho RTOS Context)
15           | 15          | SysTick            | Cấu hình được   | Bộ đếm nhịp hệ thống 24-bit (RTOS System Tick)
16           | 16 (IRQ0)   | WWDG               | Cấu hình được   | External Interrupt 0 (Window Watchdog)
17           | 17 (IRQ1)   | PVD                | Cấu hình được   | External Interrupt 1 (Power Voltage Detector)
...          | ...         | ...                | ...             | ...
N+15         | N+15 (IRQN) | Peripheral_IRQn    | Cấu hình được   | External Interrupt N (Ngoại vi của hãng chip)
```

---

### 3.2 Phân Tích Chuyên Sâu 4 Exception Hệ Thống Quan Trọng Nhất

#### 1. HardFault (Exception #3) — "Tòa Án Tối Cao" Của CPU
* **Mức ưu tiên:** Cố định ở mức `-1` (chỉ xếp sau Reset và NMI).
* **Nguyên nhân:** Xảy ra khi một Fault khác (MemManage, BusFault, UsageFault) bị kích hoạt nhưng chưa được bật (disabled trong `SCB->SHCSR`), hoặc khi một lỗi mới xảy ra ngay bên trong chính Fault Handler đang chạy (Fault Escalation).
* **Thanh ghi chẩn đoán bắt buộc phải đọc khi điều tra HardFault:**
  * `SCB->HFSR` (HardFault Status Register): Cho biết lỗi do bộ phân giải bảng vector (`VECTTBL`) hay bị ép từ fault khác (`FORCED`).
  * `SCB->CFSR` (Configurable Fault Status Register): Bóc tách chi tiết thành `MMFSR` (MemManage), `BFSR` (BusFault), `UFSR` (UsageFault).
  * `SCB->BFAR` (BusFault Address Register): Chứa địa chỉ ô nhớ gây lỗi bus chính xác.
  * `SCB->MMFAR` (MemManage Address Register): Chứa địa chỉ ô nhớ vi phạm quyền truy cập MPU.

#### 2. SVCall — Supervisor Call (Exception #11)
* Được kích hoạt đồng bộ bằng phần mềm thông qua lệnh Assembly: `SVC #imm8`.
* **Ứng dụng thực tế:** Được các hệ điều hành thời gian thực (RTOS) sử dụng để chuyển đổi từ **Unprivileged Thread Mode** (tác vụ người dùng bị hạn chế quyền) sang **Privileged Handler Mode** nhằm khởi động bộ lập lịch OS hoặc yêu cầu dịch vụ hạt nhân.

#### 3. PendSV — Pendable Service Call (Exception #14)
* Được kích hoạt bất đồng bộ bằng cách set bit `PENDSVSET` trong thanh ghi `SCB->ICSR`.
* **Quy tắc thiết kế RTOS:** Luôn luôn cấu hình mức ưu tiên của PendSV ở mức **THẤP NHẤT TUYỆT ĐỐI (Lowest Priority)** trong toàn bộ hệ thống.
* **Lý do kỹ nghệ:** Trì hoãn việc chuyển đổi ngữ cảnh (Context Switching) cho đến khi **TẤT CẢ** các ngắt phần cứng quan trọng khác (UART, Timer, CAN) đã xử lý xong hoàn toàn. Điều này ngăn chặn việc làm gián đoạn các ISR thời gian thực.

#### 4. SysTick (Exception #15)
* Bộ đếm thời gian 24-bit tích hợp sẵn bên trong lõi ARM Cortex-M (không phụ thuộc vào ngoại vi của từng nhà sản xuất chip như ST, NXP, TI).
* Tạo ngắt định kỳ (thường là 1 ms = 1000 Hz) để làm nguồn nhịp (Timebase Tick) cho hệ điều hành AUTOSAR OS (nhân askar).

---

### 3.3 Mối Quan Hệ Giữa CPU, NVIC, Vector Table & ISR

```
+===================================================================================+
|                          KIẾN TRÚC XỬ LÝ NGẮT CỦA CORTEX-M                         |
+===================================================================================+

 1. NGOẠI VI (PERIPHERAL)
    [Timer / UART / CAN / GPIO] ──(Kéo đường vật lý IRQ Line)──┐
                                                               │
 2. INTERRUPT CONTROLLER (NVIC - HARDWARE TRONG LÕI CPU)      │
    ┌──────────────────────────────────────────────────────────┘
    │  • Thanh ghi ISER / ICER: Bật / Tắt từng kênh ngắt phần cứng.
    │  • Thanh ghi IPR: Quản lý mức ưu tiên (Priority 0 đến 255).
    │  • Thanh ghi ISPR / ICPR: Quản lý trạng thái chờ (Pending).
    │  • Thanh ghi IABR: Quản lý trạng thái đang chạy (Active).
    │  ==> NVIC chọn ra ngắt có ưu tiên cao nhất và gửi "Exception #" tới CPU Core.
    │
 3. CPU CORE (EXCEPTION EXECUTION ENGINE)
    ┌──────────────────────────────────────────────────────────┘
    │  • Kiểm tra cờ ngắt toàn cục: PRIMASK, BASEPRI, FAULTMASK.
    │  • Tự động PUSH {R0-R3, R12, LR, PC, xPSR} xuống Stack (Auto-stacking).
    │  • Đọc thanh ghi SCB->VTOR để xác định địa chỉ cơ sở của Vector Table.
    │  • Tính toán địa chỉ: Target_Addr = VTOR + (Exception # * 4).
    │
 4. BẢNG VECTOR NGẮT (VECTOR TABLE TRONG FLASH / RAM)
    ┌──────────────────────────────────────────────────────────┘
    │  • CPU đọc giá trị 32-bit tại Target_Addr.
    │  • Giá trị này chính là con trỏ hàm trỏ tới địa chỉ của hàm ISR.
    │
 5. HÀM PHỤC VỤ NGẮT (ISR IN C CODE)
    ┌──────────────────────────────────────────────────────────┘
    │  • CPU nạp địa chỉ vừa đọc vào thanh ghi PC và bắt đầu thực thi code ISR.
    │  • Gán thanh ghi LR = EXC_RETURN (ví dụ 0xFFFFFFF9).
+===================================================================================+
```

---

### 3.4 Bảng Phân Tích: NVIC Khác Vector Table Như Thế Nào?

| Tiêu Chí Phân Biệt | NVIC (Nested Vectored Interrupt Controller) | Vector Table (Bảng Vector Ngắt) |
|---|---|---|
| **Bản chất** | **Phần cứng (Hardware IP Block)** tích hợp sâu trong CPU core. | **Cấu trúc dữ liệu phần mềm (Software Data Array)** do lập trình viên/Linker định nghĩa. |
| **Vị trí lưu trữ** | Vùng thanh ghi ngoại vi hệ thống `0xE000E100` – `0xE000ECFC`. | Nằm trong bộ nhớ Flash (thường từ `0x08000000`) hoặc RAM. |
| **Nhiệm vụ chính** | Bật/tắt ngắt, phân xử ưu tiên (Arbitration), quản lý trạng thái Pending/Active, kích hoạt tín hiệu ngắt tới CPU. | Cung cấp địa chỉ thực thi của từng hàm ISR tương ứng với từng Exception Number. |
| **Cách truy cập** | Đọc/ghi qua các thanh ghi điều khiển MMIO (`NVIC->ISER`, `NVIC->IPR`). | CPU core tự động đọc dữ liệu 32-bit thông qua bus bộ nhớ dựa vào thanh ghi `VTOR`. |
| **Khả năng cấu hình** | Có thể bật/tắt, thay đổi độ ưu tiên linh hoạt bất kỳ lúc nào tại runtime. | Cố định trong Flash sau khi nạp code (chỉ có thể trỏ sang RAM nếu dùng VTOR). |

---

### 3.5 Bản Chất Kỹ Nghệ: "Gán Địa Chỉ Vào Vector Table" vs "Kích Hoạt Ngắt Thủ Công" — Mô Hình 3 Tầng Cầu Dao Phần Cứng

> 💡 **Câu hỏi chạm đáy bản chất kiến trúc ARM Cortex-M:**  
> *"Các ngoại lệ Core Exceptions (từ Entry 0 đến 15 trong Vector Table) vốn là các ngắt nội tại của CPU và vị trí của chúng đã được hardcode trong kiến trúc ARM. Vậy tại sao ta vẫn phải dùng lệnh kích hoạt thủ công (như `SysTickIntEnable()`)? Gán địa chỉ hàm vào bảng Vector Table thôi chưa đủ hay sao?"*

#### 1. Ẩn Dụ Kỹ Thuật: "Kéo Dây Dẫn" (Vector Table) vs "Bật Cầu Dao" (Interrupt Gate)

* **Gán địa chỉ vào Vector Table (`startup.S`):**  
  Giống như việc người thợ điện **kéo sẵn sợi dây điện từ bóng đèn về tủ điều khiển trung tâm**. Sợi dây điện này là một đường dẫn tĩnh, cung cấp câu trả lời cho câu hỏi: *"NẾU có tín hiệu ngắt xảy ra, CPU phải nhảy tới địa chỉ nào để thực thi?"*. Tuy nhiên, bản thân sợi dây dẫn không tự sinh ra dòng điện và không thể tự kích hoạt bóng đèn sáng.
* **Kích hoạt ngắt thủ công (Enable Bits trong MMIO Registers):**  
  Đây chính là thao tác **gạt chiếc cầu dao (Aptomat)**! Mọi khối ngoại vi và ngoại lệ trong vi điều khiển (kể cả bộ đếm SysTick nội tại) đều được thiết kế kèm một hoặc nhiều bit "công tắc hở mạch" (Gate). Nếu phần mềm không chủ động ghi vào thanh ghi để đóng cầu dao, tín hiệu ngắt sẽ bị chặn lại ngay tại ngưỡng cửa phần cứng và không bao giờ được chuyển tới lõi CPU.

---

#### 2. Phân Cấp Các Core Exceptions (0..15): Cái Nào Tự Chạy, Cái Nào BẮT BUỘC Bật Thủ Công?

Trong dải 16 Exception đầu tiên của ARM Cortex-M, phần cứng chia làm 2 nhóm với cơ chế vận hành hoàn toàn trái ngược:

| Nhóm Ngoại Lệ | Danh Sách Exceptions | Trạng Thái Mặc Định Khi Reset | Có Cần Kích Hoạt Thủ Công Không? |
| :--- | :--- | :--- | :--- |
| 🔴 **Nhóm 1: Cưỡng Bức Bật (Permanent / Non-Maskable)** | • **Reset** (Entry [1])<br>• **NMI** (Entry [2])<br>• **HardFault** (Entry [3]) | **LUÔN LUÔN BẬT** (Hardwired) | **KHÔNG CẦN (và KHÔNG THỂ TẮT)**. Phần cứng ARM thiết kế cứng, hễ có xung kích hoạt là bắt buộc CPU nhảy vào handler. |
| 🟡 **Nhóm 2: Có Thể Cấu Hình (Configurable Core Exceptions)** | • **MemManage** (Entry [4])<br>• **BusFault** (Entry [5])<br>• **UsageFault** (Entry [6])<br>• **SysTick** (Entry [15]) | **MẶC ĐỊNH BỊ ĐÓNG BĂNG (DISABLED 100%)** | **BẮT BUỘC PHẢI BẬT THỦ CÔNG QUA CODE C!**<br>Nếu không bật, ngắt sẽ không bao giờ chạy, hoặc sẽ bị ép leo thang (Fault Escalation) thành `HardFault`! |
| 🔵 **Nhóm 3: Kích Hoạt Bằng Phần Mềm (Software-Triggered)** | • **SVCall** (Entry [11])<br>• **PendSV** (Entry [14]) | Chờ lệnh phần mềm | Không có cầu dao On/Off, mà kích hoạt trực tiếp khi code gọi lệnh `SVC #0` hoặc ghi bit `PENDSVSET` vào `SCB->ICSR`. |

---

#### 3. Mô Hình "3 Tầng Cầu Dao Bảo Vệ" (Three-Tier Gate Architecture)

Để một tín hiệu ngắt từ thế giới bên ngoài (hoặc từ khối đếm SysTick) có thể thực sự ngắt ngang luồng lệnh của CPU và nhảy vào hàm C của bạn, nó bắt buộc phải vượt qua **3 tầng cầu dao nối tiếp nhau**:

```
+===================================================================================================+
|               MÔ HÌNH 3 TẦNG CẦU DAO BẢO VỆ NGẮT TRONG VI ĐIỀU KHIỂN ARM CORTEX-M                 |
+===================================================================================================+

   [1. NGUỒN PHÁT NGẮT: SYSTICK TIMER / CAN / UART / GPIO]
        │
        ▼ (Tạo sự kiện ngắt: đếm tràn, nhận byte, nhận CAN frame)
   [CẦU DAO TẦNG 1: TẠI BẢN THÂN NGOẠI VI (PERIPHERAL LEVEL)]
        ├── SysTick: Bit TICKINT trong thanh ghi SysTick->CTRL (Bật bởi SysTickIntEnable)
        └── CAN:     Bit CAN_IER trong Controller (Bật bởi CANIntEnable)
        │
        ▼ (Tín hiệu vượt qua Cầu dao Tầng 1 đi tới NVIC)
   [CẦU DAO TẦNG 2: TẠI BỘ ĐIỀU KHIỂN TRUNG TÂM (NVIC LEVEL)]
        ├── Core Exceptions: Các bit trong thanh ghi SCB->SHCSR (MEMFAULTENA, BUSFAULTENA...)
        └── External IRQs:   Các bit trong thanh ghi NVIC->ISER[i] (Bật bởi IntEnable / NVIC_EnableIRQ)
        │
        ▼ (NVIC phân xử ưu tiên và gửi yêu cầu Exception # tới CPU Core)
   [CẦU DAO TẦNG 3: CẦU DAO TỔNG TOÀN CỤC (CPU CORE GLOBAL INTERRUPT)]
        └── Cờ ngắt trong thanh ghi PRIMASK của CPU Core (Bật bởi Irq_Enable / cpsie i)
        │
        ▼ (CẢ 3 CẦU DAO ĐỀU ĐÓNG)
   [CPU TRA CỨU BẢNG VECTOR TABLE TRONG FLASH VÀ NHẢY VÀO HÀM ISR]
+===================================================================================================+
```

---

#### 4. Dẫn Chứng Thực Tế 100% Trong Dự Án `as`: Vị Trí Gán Địa Chỉ vs Vị Trí Kích Hoạt Thủ Công

Dưới đây là 3 trường hợp điển hình nhất trong mã nguồn dự án `as`, chứng minh rõ ràng vị trí gán địa chỉ tĩnh trong Vector Table và vị trí code C kích hoạt thủ công:

##### 📍 Trường Hợp 1: Ngắt Lõi Hệ Thống — SysTick Timer (Exception 15)
* **Vị trí gán địa chỉ tĩnh trong Vector Table:**  
  Tệp [`as/com/as.infrastructure/system/kernel/askar/portable/cortex-m/startup.S: L64`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/com/as.infrastructure/system/kernel/askar/portable/cortex-m/startup.S#L64):
  ```arm
  /* Entry [15] trong __vector_table được gán chết địa chỉ hàm knl_system_tick */
  .word     knl_system_tick                      /* 15: Systick handler             */
  ```
* **Vị trí kích hoạt thủ công trong MCAL (`Mcu.c` & `systick.c`):**  
  Tệp [`as/com/as.infrastructure/arch/lm3s/mcal/Mcu.c: L128-L130`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/com/as.infrastructure/arch/lm3s/mcal/Mcu.c#L128-L130) trong hàm `Mcu_DistributePllClock()`:
  ```c
  /* 1. Nạp chu kỳ đếm 1ms */
  SysTickPeriodSet(McuE_GetSystemClock() / 1000);

  /* 2. BẬT CẦU DAO PHÁT NGẮT: Ghi bit TICKINT = 1 trong thanh ghi NVIC_ST_CTRL */
  SysTickIntEnable(); 

  /* 3. BẬT CẦU DAO BỘ ĐẾM: Ghi bit ENABLE = 1 trong thanh ghi NVIC_ST_CTRL */
  SysTickEnable();
  ```
  Bản chất mã nguồn hàm `SysTickIntEnable()` trong [`DriverLib/src/systick.c: L158-L164`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/com/as.infrastructure/arch/lm3s/DriverLib/src/systick.c#L158-L164):
  ```c
  void SysTickIntEnable(void)
  {
      /* Ghi bit NVIC_ST_CTRL_INTEN (Bit 1) vào thanh ghi điều khiển SysTick */
      HWREG(NVIC_ST_CTRL) |= NVIC_ST_CTRL_INTEN;
  }
  ```
  *⚠️ Nếu bạn bỏ quên hàm `SysTickIntEnable()`:* Bộ đếm SysTick vẫn đếm ngược về 0 rồi tự nạp lại bình thường, cờ `COUNTFLAG` vẫn bật lên, nhưng **CPU sẽ KHÔNG BAO GIỜ nhảy vào `knl_system_tick`**, hệ điều hành `askar` đứng im và không thể lập lịch đa nhiệm!

##### 📍 Trường Hợp 2: Ngắt Ngoại Lệ Lỗi Phần Cứng (UsageFault, BusFault, MemManage — Exceptions 4, 5, 6)
* **Vị trí gán địa chỉ tĩnh trong Vector Table:**  
  Tệp [`startup.S: L53-L55`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/com/as.infrastructure/system/kernel/askar/portable/cortex-m/startup.S#L53-L55):
  ```arm
  .word     mpu_fault_handler                    /* 04: MPU Fault Handler           */
  .word     bus_fault_handler                    /* 05: Bus Fault Handler           */
  .word     usage_fault_handler                  /* 06: Usage Fault Handler         */
  ```
* **Vị trí kích hoạt thủ công trong thanh ghi hệ thống `SCB->SHCSR`:**  
  Khi khởi động, ARM quy định các fault này mặc định bị **vô hiệu hóa**. Để CPU có thể điều hướng chính xác lỗi mà không bị ép nhảy thẳng vào `HardFault`, tầng OS Port (`portable.c`) hoặc System Init phải thực hiện:
  ```c
  /* Địa chỉ thanh ghi SCB->SHCSR = 0xE000ED24 */
  #define SCB_SHCSR (*((volatile uint32_t*)0xE000ED24))
  #define SCB_SHCSR_MEMFAULTENA   (1 << 16)
  #define SCB_SHCSR_BUSFAULTENA   (1 << 17)
  #define SCB_SHCSR_USGFAULTENA   (1 << 18)

  /* BẬT CẦU DAO CHO PHÉP 3 LOẠI FAULT BẮN VÀO HANDLER RIÊNG */
  SCB_SHCSR |= (SCB_SHCSR_MEMFAULTENA | SCB_SHCSR_BUSFAULTENA | SCB_SHCSR_USGFAULTENA);
  ```

##### 📍 Trường Hợp 3: Ngắt Ngoại Vi CAN Controller (CAN0 — IRQ 21 / Vector 37)
* **Vị trí gán địa chỉ tĩnh trong Vector Table:**  
  Tệp [`startup.S: L88`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/com/as.infrastructure/system/kernel/askar/portable/cortex-m/startup.S#L88):
  ```arm
  .word     knl_isr_process                      /* 37: CAN0 Controller */
  ```
* **Vị trí kích hoạt thủ công qua đủ 3 tầng cầu dao trong MCAL:**
  1. **Cầu dao Tầng 1 (Tại CAN Module):**  
     Trong [`as/com/as.infrastructure/arch/lm3s/DriverLib/src/can.c: L315`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/com/as.infrastructure/arch/lm3s/DriverLib/src/can.c#L315):
     ```c
     CANIntEnable(CAN0_BASE, CAN_INT_MASTER | CAN_INT_ERROR | CAN_INT_STATUS);
     ```
  2. **Cầu dao Tầng 2 (Tại NVIC):**  
     Trong [`as/com/as.infrastructure/arch/lm3s/DriverLib/src/interrupt.c`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/com/as.infrastructure/arch/lm3s/DriverLib/src/interrupt.c):
     ```c
     IntEnable(INT_CAN0); /* Ghi bit vào thanh ghi NVIC->ISER[0] */
     ```
  3. **Cầu dao Tầng 3 (Cầu dao tổng CPU):**  
     Trong [`as/com/as.infrastructure/system/kernel/askar/portable/cortex-m/startup.S: L365`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/com/as.infrastructure/system/kernel/askar/portable/cortex-m/startup.S#L365):
     ```arm
     Irq_Enable:
         cpsie i       /* Xóa cờ PRIMASK, cho phép CPU tiếp nhận ngắt */
         bx lr
     ```

---

### 3.6 Câu Hỏi Kiểm Tra Tư Duy — Chương 3

1. **Câu 1:** Nếu trong thanh ghi `NVIC->ISER` đã set bit Enable cho `TIM2_IRQn`, nhưng trong mảng Vector Table tại ô nhớ tương ứng với TIM2 lại chứa giá trị `0x00000000` (NULL). Chuyện gì sẽ xảy ra chính xác khi bộ đếm Timer đếm tràn?
2. **Câu 2:** Tại sao các hệ điều hành hệ điều hành AUTOSAR OS (nhân askar) bắt buộc phải gán độ ưu tiên của ngắt `PendSV` ở mức thấp nhất trong toàn bộ hệ thống? Nếu gán PendSV mức ưu tiên cao hơn ngắt UART RX thì hậu quả nghiêm trọng nào sẽ xảy ra?
3. **Câu 3:** Cả `SVC` và `PendSV` đều là các cơ chế kích hoạt ngắt bằng phần mềm (Software Exception). Tại sao hệ điều hành cần phân tách thành 2 loại ngắt này mà không dùng chung một loại?

---

<a name="ch4"></a>
## CHƯƠNG 4: CODE THỰC TẾ TRONG DỰ ÁN AS — STARTUP + LINKER SCRIPT + ISR

> 🛡️ **Cam kết dữ liệu thực tế (100% Verified Source Code):**  
> Toàn bộ mã nguồn, tên nhãn, hằng số và số dòng trong chương này được trích xuất trực tiếp 100% từ mã nguồn gốc của hệ điều hành `askar` và kiến trúc phần cứng trong dự án `as`:
> - Assembly Startup: [`as/com/as.infrastructure/system/kernel/askar/portable/cortex-m/startup.S`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/com/as.infrastructure/system/kernel/askar/portable/cortex-m/startup.S)
> - Linker Script: [`as/com/as.application/board.lm3s6965evb/script/linker.lds`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/com/as.application/board.lm3s6965evb/script/linker.lds) & [`board.stm32f107vc/script/linker-app.lds`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/com/as.application/board.stm32f107vc/script/linker-app.lds)
> - OS Interrupt Wrapper: [`as/com/as.infrastructure/system/kernel/askar/portable/cortex-m/portableS.S`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/com/as.infrastructure/system/kernel/askar/portable/cortex-m/portableS.S)
> - Interrupt Dispatcher: [`as/com/as.infrastructure/system/kernel/askar/portable/cortex-m/portable.c`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/com/as.infrastructure/system/kernel/askar/portable/cortex-m/portable.c)
> - Memory Map Thực Tế: [`as/build/nt/lm3s6965evb/ascore/lm3s6965evb.map`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/build/nt/lm3s6965evb/ascore/lm3s6965evb.map)

---

### 4.1 Khai Báo Bảng Vector Table Thực Tế Trong Dự Án `as` (`startup.S`)

Trong dự án `as`, nhân hệ điều hành `askar` định nghĩa bảng Vector Table chuẩn xác bằng hợp ngữ GNU Assembly trong tệp [`startup.S: L45-L115`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/com/as.infrastructure/system/kernel/askar/portable/cortex-m/startup.S#L45-L115):

```assembly
/******************************************************************************
* File: as/com/as.infrastructure/system/kernel/askar/portable/cortex-m/startup.S
* Vector table for a Cortex M3. Vectors start at addr 0x0.
******************************************************************************/
	.syntax unified
	.cpu cortex-m3
	.thumb

	.section .isr_vector,"a",%progbits
	.type __vector_table, %object
	.global __vector_table

__vector_table:
	/*    Internal Exceptions Vector Define                                          */
	.word     knl_system_stack_top   			   /* 00: Top of Main Stack (MSP)     */
	.word     reset_handler                        /* 01: Reset Handler (PC khởi động)*/
	.word     nmi_handler                      	   /* 02: NMI Handler                 */
	.word     hard_fault_handler                   /* 03: Hard Fault Handler          */
	.word     mpu_fault_handler                    /* 04: MPU Fault Handler           */
	.word     bus_fault_handler                    /* 05: Bus Fault Handler           */
	.word     usage_fault_handler                  /* 06: Usage Fault Handler         */
	.word     0                                    /* 07: Reserved                    */
	.word     0                                    /* 08: Reserved                    */
	.word     0                                    /* 09: Reserved                    */
	.word     0                                    /* 10: Reserved                    */
	.word     knl_start_dispatch                   /* 11: SVCall Handler (Gọi SVC)    */
	.word     debug_monitor_handler                /* 12: Debug Monitor Handler       */
	.word     0                                    /* 13: Reserved                    */
	.word     knl_dispatch_entry                   /* 14: PendSV Handler (Đổi Context)*/
	.word     knl_system_tick                      /* 15: Systick Handler (Nhịp OS)   */

	/*    External Interrupts Vector Define (Bắt đầu từ Entry 16 = IRQ 0)            */
	.word     knl_isr_process                      /* 16: IRQ 0                       */
	.word     knl_isr_process                      /* 17: IRQ 1                       */
	.word     knl_isr_process                      /* 18: IRQ 2                       */
	.word     knl_isr_process                      /* 19: IRQ 3 (CAN, UART, TIM...)   */
	/* ... toàn bộ các IRQ còn lại (20 đến 255) đều trỏ vào knl_isr_process ... */
```

#### 🔍 Điểm Khác Biệt Cốt Lõi Của Kiến Trúc AUTOSAR OS So Với Bare-Metal:
1. **Entry 00 (`knl_system_stack_top`):** Không dùng biến tự tạo bừa bãi mà trỏ thẳng vào nhãn `knl_system_stack_top` — đỉnh stack hệ thống do Linker Script cấp phát riêng cho nhân OS `askar`.
2. **Entry 11, 14, 15:** Trỏ trực tiếp vào các hàm lõi của hệ điều hành:
   * Entry 11 trỏ vào `knl_start_dispatch` (kích hoạt bằng lệnh `SVC` khi gọi `StartOS()`).
   * Entry 14 trỏ vào `knl_dispatch_entry` (kích hoạt bằng `PendSV` để thực hiện Context Switch giữa các Task).
   * Entry 15 trỏ vào `knl_system_tick` (kích hoạt nhịp định thời SysTick 1ms cho bộ đếm Alarms).
3. **Toàn bộ External Interrupts (16 → 255) đều trỏ vào `knl_isr_process`:** Trong bare-metal, mỗi IRQ trỏ đến 1 hàm riêng (`USART1_IRQHandler`, `TIM2_IRQHandler`). Nhưng trong AUTOSAR OS, **tất cả ngắt ngoại vi đều đi qua hàm bọc duy nhất `knl_isr_process`** để bảo toàn Stack, tăng bộ đếm lồng ngắt `ISR2Counter++` và kiểm soát cướp quyền (Preemption) trước khi nhảy vào hàm Driver thật!

---

### 4.2 Cơ Chế Macro `WEAK` Symbol Trong Dự Án `as` (`startup.S`)

Tại [`startup.S: L20-L25`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/com/as.infrastructure/system/kernel/askar/portable/cortex-m/startup.S#L20-L25), dự án `as` sử dụng Macro hợp ngữ định nghĩa bẫy lỗi cho các hàm ngắt chưa được hiện thực:

```assembly
.macro DEFAULT_ISR_HANDLER name=
  .thumb_func
  .weak \name
\name:
1: b 1b /* endless loop */
.endm
```

Và khai báo tự động ở cuối tệp [`startup.S: L387-L396`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/com/as.infrastructure/system/kernel/askar/portable/cortex-m/startup.S#L387-L396):

```assembly
DEFAULT_ISR_HANDLER knl_isr_process
DEFAULT_ISR_HANDLER nmi_handler
DEFAULT_ISR_HANDLER hard_fault_handler
DEFAULT_ISR_HANDLER mpu_fault_handler
DEFAULT_ISR_HANDLER bus_fault_handler
DEFAULT_ISR_HANDLER usage_fault_handler
DEFAULT_ISR_HANDLER debug_monitor_handler
DEFAULT_ISR_HANDLER knl_system_tick
DEFAULT_ISR_HANDLER knl_dispatch_entry
```

#### 💡 Nguyên lý hoạt động ở cấp độ Linker:
* Từ khóa `.weak \name`: Khai báo symbol này có độ ưu tiên liên kết thấp nhất.
* Khi hệ thống liên kết với file C khác (ví dụ `portableS.S` định nghĩa nhãn mạnh `knl_isr_process:` hoặc `hardfault.c` định nghĩa `void hard_fault_handler(void)`), Linker sẽ tự động lấy nhãn mạnh đó ghi đè vào bảng Vector Table.
* Nếu không có ai định nghĩa, CPU khi gặp sự cố sẽ nhảy vào vòng lặp vô tận `1: b 1b` để bảo toàn hiện trường cho lập trình viên cắm mạch nạp GDB vào debug.

---

### 4.3 Phân Tích Linker Script Thực Tế Của Dự Án `as` (`linker.lds`)

Dưới đây là toàn văn kịch bản liên kết nguyên bản tại [`as/com/as.application/board.lm3s6965evb/script/linker.lds`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/com/as.application/board.lm3s6965evb/script/linker.lds):

```ld
/* Linker script to configure memory regions for lm3s6965evb / stm32f107vc */
MEMORY
{
    FLASH (rx) : ORIGIN = 0x00000000, LENGTH = 256K
    RAM (rwx)  : ORIGIN = 0x20000000, LENGTH = 64K
}

ENTRY(reset_handler)

knl_system_stack_size = 1024;

SECTIONS
{
    /* 1. SECTION .text: Đặt Bảng Vector Table ở vị trí 0x00000000 đầu Flash */
    .text :
    {
        KEEP(*(.isr_vector))    /* BẮT BUỘC: Giữ lại bảng Vector, cấm Linker xóa */
        *(.startup*)            /* Chứa hàm reset_handler và code khởi động */
        *(.text*)               /* Toàn bộ mã nguồn hàm C */
        *(.rodata*)             /* Toàn bộ hằng số, chuỗi ký tự */
    } > FLASH

    __etext = .;                /* Đánh dấu vị trí kết thúc phần code trong Flash */
        
    /* 2. SECTION .data: Dữ liệu biến toàn cục có khởi tạo */
    /* VMA trong RAM (0x20000000), nhưng LMA nạp tại Flash sau __etext */
    .data : AT (__etext)
    {
        . = ALIGN(4);
        __data_start__ = .;     /* Điểm bắt đầu .data trong RAM */
        *(.data*)
        __data_end__ = .;       /* Điểm kết thúc .data trong RAM */
    } > RAM

    /* 3. SECTION .bss: Biến toàn cục chưa khởi tạo (Phải xóa về 0) */
    .bss :
    {
        . = ALIGN(4);
        __bss_start__ = .;      /* Điểm bắt đầu .bss trong RAM */
        *(.bss*)
        *(COMMON)
        . = ALIGN(4);
        __bss_end__ = .;        /* Điểm kết thúc .bss trong RAM */
    } > RAM
    
    /* 4. SECTION .init_stack: Cấp phát ngăn xếp hệ thống cho OS */
    .init_stack ALIGN(16) (NOLOAD) : 
    {   
       knl_system_stack     = .; 
       . = . + knl_system_stack_size;   
       knl_system_stack_top = .; /* Điểm cao nhất của Stack -> Nạp vào Entry 00 */
    } > RAM
}
```

---

### 4.4 Bằng Chứng Thực Tế: Đối Soát Bản Đồ Bộ Nhớ Từ File `.map` Thật

Kiểm tra trực tiếp tệp bản đồ liên kết do GCC sinh ra tại [`as/build/nt/lm3s6965evb/ascore/lm3s6965evb.map`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/build/nt/lm3s6965evb/ascore/lm3s6965evb.map):

```
Linker script and memory map

                0x00000400                        knl_system_stack_size = 0x400

.text           0x00000000    0x171dc
 *(.isr_vector)
 .isr_vector    0x00000000      0x400 build\...\startup.o
                0x00000000                __vector_table
 *(.startup*)
 .startup       0x00000400       0x48 build\...\startup.o
                0x00000400                reset_handler
...
                0x000171dc                        __etext = .

.data           0x20000000      0x1c4 load address 0x000171dc
                0x20000000                        __data_start__ = .
...
                0x200001c4                        __data_end__ = .

.bss            0x200001c4     0x6f88
                0x200001c4                        __bss_start__ = .
...
                0x2000714c                        __bss_end__ = .

.init_stack     0x20007150      0x400 load address 0x0001e32c
                0x20007150                        knl_system_stack = .
                0x20007550                        . = (. + knl_system_stack_size)
                0x20007550                        knl_system_stack_top = .
```

#### 🎯 Phân tích đối soát từng byte:
1. `__vector_table` được đặt tuyệt đối tại **`0x00000000`**, chiếm đúng **`0x400` bytes (1024 bytes = 256 vector $\times$ 4 bytes)**.
2. `reset_handler` nằm ngay sau bảng vector tại địa chỉ **`0x00000400`**.
3. `knl_system_stack_top` được tính toán tại **`0x20007550`**. Đây chính là giá trị thô 32-bit được ghi vào ô nhớ đầu tiên `0x00000000` (Entry [0]) của chip!

---

### 4.5 Mã Nguồn Khởi Động `reset_handler` Thực Tế Trong Dự Án `as`

Đoạn mã máy đầu tiên chạy khi bật nguồn được hiện thực bằng hợp ngữ tối ưu tại [`startup.S: L316-L352`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/com/as.infrastructure/system/kernel/askar/portable/cortex-m/startup.S#L316-L352):

```assembly
	.section	.startup
	.weak	reset_handler
	.type	reset_handler, %function
reset_handler:
	/* BƯỚC 1: Nạp con trỏ Stack MSP */
	ldr  sp, =knl_system_stack_top

	/* BƯỚC 2: Khởi tạo dữ liệu RAM - Copy phân vùng .data từ Flash sang SRAM */
	ldr  r0, =__data_start__  /* r0 = 0x20000000 (Địa chỉ bắt đầu RAM) */
	ldr  r3, =__data_end__    /* r3 = 0x200001c4 (Địa chỉ kết thúc RAM) */
	ldr  r5, =__etext        /* r5 = 0x000171dc (Địa chỉ lưu trong Flash) */
	movs r1, #0
	b    LoopCopyDataInit

CopyDataInit:
	ldr  r4, [r5, r1]          /* Đọc 4 bytes từ Flash */
	str  r4, [r0, r1]          /* Ghi 4 bytes vào SRAM */
	adds r1, r1, #4            /* Tăng chỉ số offset thêm 4 */

LoopCopyDataInit:
	adds r2, r0, r1            /* r2 = vị trí hiện tại đang copy */
	cmp  r2, r3                /* Đã chạm tới __data_end__ chưa? */
	bcc  CopyDataInit          /* Chưa tới -> Tiếp tục vòng lặp copy */

	/* BƯỚC 3: Xóa sạch phân vùng .bss về 0 */
	ldr  r2, =__bss_start__   /* r2 = 0x200001c4 */
	b    LoopFillZerobss

FillZerobss:
	movs r3, #0
	str  r3, [r2], #4          /* Ghi giá trị 0 vào ô nhớ RAM và tăng r2 lên 4 */

LoopFillZerobss:
	ldr  r3, = __bss_end__    /* r3 = 0x2000714c */
	cmp  r2, r3                /* Đã xóa xong tới __bss_end__ chưa? */
	bcc  FillZerobss           /* Chưa xong -> Tiếp tục ghi số 0 */

	/* BƯỚC 4: Nhảy vào hàm main() để khởi động AUTOSAR BSW */
	bl  main
	b   .                      /* Phòng thủ: Nếu main() thoát, khóa CPU tại đây */
.size reset_handler, .-reset_handler
```

---

### 4.6 Cơ Chế Định Tuyến Ngắt Ngoại Vi 3 Tầng Thực Tế Trong Dự Án `as`

Khác với bare-metal chỉ gọi trực tiếp hàm C, dự án `as` tổ chức ngắt qua **3 tầng bảo vệ kiến trúc**:

```
[BƯỚC 1: VECTOR TABLE TRỎ VÀO OS ASSEMBLY WRAPPER]
__vector_table (startup.S: L67)
    └── .word knl_isr_process
            │
            ▼
[BƯỚC 2: TẦNG BẢO TOÀN NGỮ CẢNH TRONG HỆ ĐIỀU HÀNH]
knl_isr_process (portableS.S: L235-L240):
    mov r3, lr
    bl  EnterISR           /* 1. Tăng ISR2Counter++, lưu thanh ghi r4-r11 của Task */
    mrs r0, ipsr           /* 2. Đọc thanh ghi phần cứng IPSR -> Lấy số hiệu ngắt intno */
    bl  knl_isr_handler    /* 3. Nhảy sang hàm điều phối viết bằng C */
    b   ExitISR            /* 4. Đánh giá Preemption và khôi phục ngữ cảnh Task */
            │
            ▼
[BƯỚC 3: TẦNG ĐIỀU PHỐI C VÀ GỌI DRIVER THẬT]
knl_isr_handler(int intno) (portable.c: L118-L130):
    void knl_isr_handler(int intno) {
    #if (ISR_NUM > 0)
        /* Kiểm tra số hiệu ngắt hợp lệ trong mảng cấu hình */
        if((intno > 15) && (intno < (16 + ISR_NUM)) && (tisr_pc[intno - 16] != NULL)) {
            tisr_pc[intno - 16]();  /* ──► GỌI TRỰC TIẾP HÀM MCAL DRIVER (Can_RxIsr...) */
        } else
    #endif
        {
            ShutdownOS(0xFF);       /* Ngắt không hợp lệ -> Dừng hệ thống an toàn */
        }
    }
```

* **Mảng `tisr_pc[]` được tạo ra ở đâu?**  
  Được công cụ phát sinh mã tự động `GenOS.py` ([L522-L533](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/com/as.tool/config.infrastructure.system/argen/GenOS.py#L522-L533)) quét từ file cấu hình ARXML (`OsIsr` entries) và sinh tự động vào tệp `Os_Cfg.c`. Nhờ đó, việc thêm bớt ngắt ngoại vi không bao giờ phải sửa code Assembly của hệ điều hành!

---

### 4.7 Câu Hỏi Kiểm Tra Tư Duy — Chương 4

1. **Câu 1:** Trong tệp `linker.lds` của dự án `as`, tại sao mục `.init_stack` lại có thuộc tính `(NOLOAD)`? Nếu bỏ từ khóa `(NOLOAD)`, file nhị phân nạp vào Flash `.bin` sẽ bị phình to thêm như thế nào?
2. **Câu 2:** Tại sao trong `startup.S`, sau khi copy `.data` và xóa `.bss`, lệnh gọi sang `main()` lại dùng lệnh `bl main` mà sau đó lại có thêm lệnh `b .`? Lệnh `b .` đóng vai trò phòng vệ gì?
3. **Câu 3:** Tại sao trong `startup.S`, tất cả các External Interrupts từ vector 16 đến 255 đều trỏ chung vào một nhãn `knl_isr_process` thay vì trỏ trực tiếp vào từng hàm Driver riêng biệt? Cơ chế này giải quyết bài toán gì cho AUTOSAR OS?

<a name="ch5"></a>
## CHƯƠNG 5: INTERRUPT FLOW Ở CẤP CPU CORE

### 5.1 Lưu Trữ Ngữ Cảnh Tự Động (Hardware Context Stacking)

Kỹ năng cốt lõi phân biệt giữa Senior và Junior là sự thấu hiểu chính xác phần cứng làm gì ở chu kỳ xung nhịp (clock cycle level) khi có ngắt:

```
TRƯỚC KHI VÀO NGẮT:              SAU KHI AUTO-STACKING (32 BYTES):
Bộ nhớ Stack (RAM):              Bộ nhớ Stack (RAM):
                                 +------------------+  <-- SP cũ (Vị trí cao hơn)
                                 |       xPSR       |  [SP + 28] (Thanh ghi trạng thái)
                                 |        PC        |  [SP + 24] (Địa chỉ lệnh trở về)
                                 |        LR        |  [SP + 20] (Link Register cũ)
                                 |       R12        |  [SP + 16] (Intra-procedure scratch)
                                 |        R3        |  [SP + 12] (Tham số hàm 4)
                                 |        R2        |  [SP + 8]  (Tham số hàm 3)
                                 |        R1        |  [SP + 4]  (Tham số hàm 2)
                                 |        R0        |  [SP + 0]  (Tham số hàm 1 / Return val)
                                 +------------------+  <-- SP mới (Thấp hơn 32 bytes)
```

#### ❓ Tại Sao Phần Cứng Chỉ Lưu 8 Thanh Ghi {R0-R3, R12, LR, PC, xPSR}?
Theo chuẩn giao tiếp hàm của ARM (**AAPCS — ARM Architecture Procedure Call Standard**):
- **Caller-Saved Registers {R0-R3, R12}:** Là các thanh ghi tạm (scratch registers) mà bất kỳ hàm C nào cũng được quyền ghi đè tùy ý mà không cần khôi phục. Vì ngắt có thể nhảy vào bất kỳ lúc nào, phần cứng CPU bắt buộc phải tự động lưu 5 thanh ghi này cùng {LR, PC, xPSR}.
- **Callee-Saved Registers {R4-R11}:** Là các thanh ghi lưu biến cục bộ. Nếu hàm ISR của lập trình viên có sử dụng `R4-R11`, trình biên dịch GCC sẽ tự động chèn lệnh Assembly `PUSH {R4-R11}` ở đầu hàm ISR (Prologue) và `POP {R4-R11}` ở cuối hàm ISR (Epilogue).
- **Kết quả:** Tiết kiệm tối đa chu kỳ lưu trữ phần cứng (chỉ mất đúng 12 chu kỳ xung nhịp trên Cortex-M4 để hoàn tất context saving).

---

### 5.2 Giá Trị Ma Thuật EXC_RETURN Trong Thanh Ghi LR

Khi CPU bước chân vào hàm ISR, thanh ghi `LR` (Link Register) **KHÔNG CHỨA ĐỊA CHỈ TRỞ VỀ** như hàm C thông thường. Thay vào đó, CPU nạp một mã trạng thái phần cứng đặc biệt gọi là **EXC_RETURN**:

| Giá Trị EXC_RETURN | Chế Độ Trở Về (Return Mode) | Stack Pointer Sử Dụng | Loại Khung Ngữ Cảnh (Stack Frame) |
|---|---|---|---|
| `0xFFFFFFF1` | **Handler Mode** (Nested Interrupt) | **MSP** (Main Stack Pointer) | Standard 8 Registers (Không có FPU) |
| `0xFFFFFFF9` | **Thread Mode** (Về chương trình chính) | **MSP** (Main Stack Pointer) | Standard 8 Registers (Không có FPU) |
| `0xFFFFFFFD` | **Thread Mode** (Về RTOS Task) | **PSP** (Process Stack Pointer) | Standard 8 Registers (Không có FPU) |
| `0xFFFFFFE1` | **Handler Mode** (Nested Interrupt) | **MSP** (Main Stack Pointer) | Extended Frame (Bao gồm 16 thanh ghi FPU S0-S15) |
| `0xFFFFFFE9` | **Thread Mode** (Về chương trình chính) | **MSP** (Main Stack Pointer) | Extended Frame (Bao gồm FPU) |
| `0xFFFFFFED` | **Thread Mode** (Về RTOS Task) | **PSP** (Process Stack Pointer) | Extended Frame (Bao gồm FPU) |

#### ⚙️ Cơ Chế Thoát Ngắt (Exception Return Mechanism)
Khi hàm ISR thực hiện lệnh `BX LR`:
1. CPU kiểm tra 4 bit cao nhất `LR[31:28]`. Nếu bằng `0xF`, CPU nhận biết đây là **Lệnh Thoát Ngắt (Exception Return)**, không phải lệnh nhảy hàm thông thường.
2. CPU đọc các bit cấu hình trong `EXC_RETURN` để xác định: Cần unstack từ `MSP` hay `PSP`? Trở về `Thread Mode` hay `Handler Mode`? Có cần khôi phục thanh ghi thực số thực FPU không?
3. Phần cứng tự động POP 8 thanh ghi và nạp lại Program Counter (PC) một cách mượt mà.

---

### 5.3 Mô Phỏng Ngắt Timer Từng Chu Kỳ (Step-by-Step Hardware Trace)

```
[THỜI ĐIỂM T0] Bộ đếm phần cứng TIM2 chạm ngưỡng ARR. Cờ phần cứng TIM2->SR (UIF) bật lên 1.
               Đường dây ngắt vật lý TIM2_IRQn gửi tín hiệu điện áp tới NVIC.
     │
[THỜI ĐIỂM T1] NVIC kiểm tra NVIC->ISER[0] bit 28 = 1 (Enabled).
               NVIC kiểm tra Priority của TIM2 (ví dụ Priority = 5) cao hơn mức hiện tại.
               NVIC gửi tín hiệu nIRQ tới CPU Core và đánh dấu TIM2 là PENDING.
     │
[THỜI ĐIỂM T2] CPU Core hoàn thành chu kỳ của câu lệnh hiện tại.
               CPU Core chấp nhận ngắt.
     │
[THỜI ĐIỂM T3] [GIAI ĐOẠN AUTO-STACKING: 12 CYCLES]
               CPU PUSH {R0-R3, R12, LR, PC, xPSR} xuống bộ nhớ Stack của Task.
               SP giảm 32 bytes.
               Thanh ghi LR được gán giá trị EXC_RETURN = 0xFFFFFFFD.
     │
[THỜI ĐIỂM T4] [GIAI ĐOẠN VECTOR FETCH]
               CPU đọc VTOR (0x08000000) + (Exception 44 * 4) = 0x080000B0.
               CPU nạp địa chỉ hàm TIM2_IRQHandler (0x08001235) vào PC.
               NVIC chuyển trạng thái TIM2 từ PENDING sang ACTIVE.
     │
[THỜI ĐIỂM T5] [GIAI ĐOẠN ISR EXECUTION (C CODE)]
               CPU thực thi mã nguồn hàm TIM2_IRQHandler():
               void TIM2_IRQHandler(void) {
                   if (TIM2->SR & TIM_SR_UIF) {
                       TIM2->SR &= ~TIM_SR_UIF;  /* BẮT BUỘC: Xóa cờ ngắt phần cứng */
                       g_system_ticks++;
                   }
               }
     │
[THỜI ĐIỂM T6] [GIAI ĐOẠN EXCEPTION RETURN]
               Hàm ISR thực hiện lệnh kết thúc: `BX LR` (LR = 0xFFFFFFFD).
               CPU phát hiện EXC_RETURN -> Thực hiện Auto-Unstacking từ PSP.
               SP tăng 32 bytes. Khôi phục {R0-R3, R12, LR, PC, xPSR}.
     │
[THỜI ĐIỂM T7] CPU Core tiếp tục chạy lệnh của RTOS Task tại địa chỉ PC vừa khôi phục.
```

---

### 5.4 Câu Hỏi Kiểm Tra Tư Duy — Chương 5

1. **Câu 1:** Nếu trong hàm `TIM2_IRQHandler()`, lập trình viên quên không viết dòng lệnh xóa cờ `TIM2->SR &= ~TIM_SR_UIF;`, hiện tượng gì sẽ xảy ra ngay sau khi CPU thực thi lệnh `BX LR` để thoát ngắt?
2. **Câu 2:** Khi một ngắt xảy ra, Stack Pointer giảm đi 32 bytes. Nếu trước thời điểm ngắt, Stack chỉ còn trống đúng 16 bytes trước khi chạm đáy bộ nhớ RAM, CPU sẽ phản ứng như thế nào và thanh ghi nào sẽ ghi nhận lỗi?
3. **Câu 3:** Tại sao giá trị `EXC_RETURN` lại có dạng `0xFFFFFFFx` với các bit cao đều là `1`? Điều gì ngăn cản việc một hàm C thông thường vô tình có địa chỉ trả về trùng với `0xFFFFFFFx`?

---

<a name="ch6"></a>
## CHƯƠNG 6: INTERRUPT PRIORITY, PREEMPTION & SUB-PRIORITY

### 6.1 Cấu Trúc Priority Trong ARM Cortex-M

> [!WARNING]
> **Quy Tắc Vàng Về Priority Trong ARM Cortex-M:**  
> **SỐ CÀNG NHỎ ➔ MỨC ĐỘ ƯU TIÊN CÀNG CAO!**  
> * Priority `0`: Mức ưu tiên cao nhất trong các ngắt cấu hình được.  
> * Priority `255`: Mức ưu tiên thấp nhất.  
> *(Hoàn toàn ngược lại với quy ước Task Priority trong AUTOSAR OS: Task số lớn = Ưu tiên cao).*

#### 🔹 Phân Bố Bit Priority (Priority Grouping)
ARM Cortex-M quy định mỗi ngắt có một thanh ghi Priority 8-bit (`NVIC->IPR[x]`). Tuy nhiên, hầu hết các nhà sản xuất chip (STMicroelectronics, NXP, TI) chỉ cài đặt **4 bits cao nhất [7:4]** để tiết kiệm phần cứng silicon (hỗ trợ 16 mức ưu tiên từ 0, 16, 32, ... đến 240).

Thanh ghi `SCB->AIRCR` (trường `PRIGROUP`) cho phép chia 4 bits này thành 2 phần:
1. **Preemption Priority (Mức Ưu Tiên Chiếm Quyền):** Ngắt có Preemption Priority cao hơn (số nhỏ hơn) CÓ THỂ cắt ngang (preempt) một ngắt có Preemption Priority thấp hơn đang chạy (Nested Interrupt).
2. **Sub-Priority (Mức Ưu Tiên Phụ):** Khi 2 ngắt có CÙNG Preemption Priority kích hoạt đồng thời, ngắt nào có Sub-Priority nhỏ hơn sẽ được CPU phục vụ trước. **Sub-Priority KHÔNG BAO GIỜ có quyền chiếm quyền (preempt) ngắt đang chạy.**

---

### 6.2 Sơ Đồ Chiếm Quyền Ngắt Lồng Nhau (Nested Preemption Timeline)

```
KỊCH BẢN:
- Ngắt IRQ1 (Priority thấp = 3, ví dụ UART RX)
- Ngắt IRQ2 (Priority cao = 1, ví dụ Motor PWM Fault)

Trục Thời Gian:
Main Thread  |===A===|                                     |=========C========|
             |       |                                     |
IRQ1 (Prio 3)|       |===B1===|                   |===B2===|
             |       |        |                   |
IRQ2 (Prio 1)|       |        |========D=========|
             |       |        |                  |
             +-------+--------+------------------+---------+------------------>
             t0      t1       t2                 t3        t4                 Time

- t0: Main Thread đang chạy bình thường (Khối A).
- t1: IRQ1 xảy ra. CPU Auto-stacking -> Chạy ISR1 (Khối B1).
- t2: IRQ2 (Priority = 1, cao hơn 3) ập tới! CPU lập tức PREEMPT (cắt ngang) ISR1!
      CPU đẩy thêm một khung Auto-stacking thứ hai lên Stack -> Chạy ISR2 (Khối D).
- t3: ISR2 kết thúc (BX LR) -> CPU Auto-unstacking quay trở lại thực thi nốt ISR1 (Khối B2).
- t4: ISR1 kết thúc (BX LR) -> CPU khôi phục lại Main Thread ban đầu (Khối C).
```

---

### 6.3 Hai Kỹ Thuật Tối Ưu Phần Cứng Độc Quyền Của Cortex-M

#### ⚡ 1. Tail-Chaining (Nối Đuôi Ngắt Không Cần Restore Context)
Khi một ngắt hoàn thành, nếu phần cứng phát hiện vẫn còn một ngắt khác đang ở trạng thái Pending:
- **Cách làm thông thường (Naive):** POP 8 thanh ghi (12 cycles) ➔ PUSH lại 8 thanh ghi (12 cycles) = Tốn 24 cycles lãng phí!
- **Cortex-M Tail-Chaining:** CPU **BỎ QUA HOÀN TOÀN** bước POP và PUSH. CPU giữ nguyên khung Stack và nhảy thẳng tới fetch Vector của ngắt tiếp theo. **Chỉ tốn đúng 6 chu kỳ xung nhịp!**

```
KHÔNG CÓ TAIL-CHAINING (TỐN 24+ CYCLES OVERHEAD):
[ ISR 1 Chạy ] ──> [ POP Stack (12 cyc) ] ──> [ PUSH Stack (12 cyc) ] ──> [ ISR 2 Chạy ]

CÓ TAIL-CHAINING TRÊN CORTEX-M (CHỈ TỐN ĐÚNG 6 CYCLES):
[ ISR 1 Chạy ] ──> [ Tail-Chain Fetch (6 cyc) ] ──> [ ISR 2 Chạy ]
```

#### ⚡ 2. Late-Arrival (Tiếp Nhận Ngắt Ưu Tiên Cao Đến Muộn)
Khi CPU đang trong quá trình Auto-stacking 12 chu kỳ để chuẩn bị vào một ngắt ưu tiên thấp (IRQ1), nếu có một ngắt ưu tiên cao hơn (IRQ2) ập tới:
- CPU **KHÔNG HỦY** quá trình stacking đang diễn ra.
- CPU tận dụng chính khung Stack vừa lưu để chuyển hướng nạp Vector của IRQ2 vào thực thi trước!

---

### 6.4 Các Thanh Ghi Khóa Ngắt Hệ Thống: PRIMASK, BASEPRI, FAULTMASK

```c
/* 1. PRIMASK: Khóa TOÀN BỘ ngắt có thể cấu hình được (Chỉ NMI và HardFault chạy được) */
__set_PRIMASK(1);   /* Khóa tất cả ngắt (Vào Critical Section) */
/* Đoạn code an toàn không bao giờ bị ngắt */
__set_PRIMASK(0);   /* Mở lại ngắt */

/* 2. BASEPRI: Chỉ khóa các ngắt có Priority THẤP HƠN HOẶC BẰNG một ngưỡng */
/* Ví dụ: Khóa tất cả ngắt có Priority từ 5 đến 255 (Priority 0, 1, 2, 3, 4 vẫn được chạy!) */
__set_BASEPRI(5 << (8 - __NVIC_PRIO_BITS));  /* Dùng trong SuspendOSInterrupts() của AUTOSAR OS */
__set_BASEPRI(0);                            /* Hủy bỏ lọc ngưỡng, mở lại toàn bộ */

/* 3. FAULTMASK: Khóa cả HardFault (Chỉ dùng trong các tình huống cứu hộ đặc biệt) */
__set_FAULTMASK(1);
```

---

### 6.5 Câu Hỏi Kiểm Tra Tư Duy — Chương 6

1. **Câu 1:** Trong hệ thống có IRQ_A (Preemption Prio = 2, Sub-Prio = 0) và IRQ_B (Preemption Prio = 2, Sub-Prio = 1). Khi IRQ_B đang thực thi, IRQ_A được kích hoạt. IRQ_A có thể preempt (cắt ngang) IRQ_B để chạy trước hay không? Tại sao?
2. **Câu 2:** Tại sao hệ điều hành AUTOSAR OS lại sử dụng thanh ghi `BASEPRI` để thực thi dịch vụ `SuspendOSInterrupts()` thay vì dùng lệnh khóa toàn cục `__disable_irq()` (`PRIMASK` / `DisableAllInterrupts()`)? Cơ chế này bảo vệ các ngắt ISR Category 1 khẩn cấp (Zero Latency) như thế nào?
3. **Câu 3:** Khái niệm "Tail-Chaining" giúp tiết kiệm bao nhiêu chu kỳ xung nhịp và tại sao nó lại là tính năng mang tính cách mạng cho các hệ thống vi điều khiển thời gian thực?

---

<a name="ch7"></a>
## CHƯƠNG 7: CƠ CHẾ NGẮT TRONG HỆ ĐIỀU HÀNH AUTOSAR OS (`askar`)

Trong chuẩn AUTOSAR OS (dựa trên tiêu chuẩn OSEK/VDX OS) và được hiện thực cụ thể qua nhân `askar` của dự án `as`, cơ chế ngắt không đơn giản là gọi hàm C từ NVIC mà được chuẩn hóa thành **2 cấp độ ngắt: ISR Category 1 và ISR Category 2**:

---

### 7.1 Phân Biệt Tuyệt Đối: ISR Category 1 vs ISR Category 2 Trong Chuẩn AUTOSAR

| Tiêu Chí So Sánh | ISR Category 1 (Cat 1) | ISR Category 2 (Cat 2) |
|---|---|---|
| **Mục Đích Sử Dụng** | Các tác vụ cực kỳ khẩn cấp, thời gian thực siêu khắc nghiệt (Inverter PWM Current Loop, Over-voltage Emergency). | Các tác vụ ngắt thông thường liên kết với ngăn xếp BSW (CAN Rx, Lin Rx, Ethernet Rx, ADC End-of-Conversion). |
| **Độ Trễ Ngắt (Latency)** | **Zero Latency** (Độ trễ gần như bằng 0, không chịu sự can thiệp của OS). | Có độ trễ nhỏ do phải đi qua tầng vỏ bọc (OS Wrapper: `EnterISR` & `ExitISR`). |
| **Sử Dụng API AUTOSAR** | **TUYỆT ĐỐI CẤM**: Không được phép gọi bất kỳ API nào của AUTOSAR OS. | **ĐƯỢC PHÉP**: Gọi các API điều phối (`SetEvent`, `ActivateTask`, `IncrementCounter`). |
| **Chiếm Quyền (Rescheduling)** | Không thể kích hoạt bộ lập lịch khi ngắt kết thúc. | **Tự động kích hoạt bộ lập lịch (Rescheduling)** tại `ExitISR` nếu có Task ưu tiên cao hơn được đánh thức. |
| **Ngăn Xếp Sử Dụng (Stack)** | Dùng ngăn xếp ngắt phần cứng (MSP). | Dùng ngăn xếp ngắt hệ thống chuyên dụng (`knl_system_stack`). |
| **Cơ Chế Khóa Ngắt** | Chỉ bị vô hiệu hóa bởi `DisableAllInterrupts()` (PRIMASK). | Bị vô hiệu hóa bởi `SuspendOSInterrupts()` (`BASEPRI`). |

---

### 7.2 Cơ Chế Điều Phối Ngắt Thực Tế Trong Dự Án `as` (`portableS.S` & `portable.c`)

Trong dự án `as`, toàn bộ các ngắt ngoại vi từ NVIC được dẫn truyền qua hàm bọc hợp ngữ `knl_isr_process` tại [`as/com/as.infrastructure/system/kernel/askar/portable/cortex-m/portableS.S`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/com/as.infrastructure/system/kernel/askar/portable/cortex-m/portableS.S):

```
+===================================================================================================+
|                    CHU KỲ SỐNG CỦA MỘT NGẮT ISR CATEGORY 2 TRONG ASKAR OS                         |
+===================================================================================================+

   [Xung Ngắt Ngoại Vi Phần Cứng: CAN RX]
              │
              ▼
   [NVIC Kích Hoạt Vector Table Entry [16+]]
              │  (Phần cứng tự động PUSH {R0-R3, R12, LR, PC, xPSR} xuống MSP)
              ▼
   [Hàm Bọc Hợp Ngữ: knl_isr_process (portableS.S: L128)]
              │
              ├─► 1. `mov r3, lr`  (Lưu EXC_RETURN)
              ├─► 2. `bl EnterISR` (Lưu {r4-r11}, tăng biến đếm lồng ngắt `ISR2Counter++`)
              │
              ├─► 3. `mrs r0, ipsr` (Đọc Exception Number đang hoạt động vào r0)
              ├─► 4. `bl knl_isr_handler` (Nhảy vào hàm C Dispatcher trong portable.c)
              │         │
              │         ▼
              │   [C Dispatcher: knl_isr_handler(int intno) (portable.c: L106)]
              │         │
              │         ├─► Tra cứu bảng hàm: `tisr_pc[intno - 16]()`
              │         ├─► Thực thi Driver ngắt: `Can_RxIsr()`
              │         │     - Đọc frame CAN từ phần cứng Mailbox.
              │         │     - Xóa cờ ngắt phần cứng.
              │         │     - Đánh thức Task giao tiếp: `SetEvent(Task_Com, EVENT_CAN_RX)`.
              │         │
              │         └─► Thoát hàm C, quay trở lại assembly
              │
              └─► 5. `b ExitISR` (portableS.S: L164)
                        │
                        ├─► Giảm biến đếm: `ISR2Counter--`
                        ├─► KIỂM TRA ĐIỀU KIỆN CƯỚP QUYỀN:
                        │   Nếu `ISR2Counter == 0` VÀ `knl_dispatch_started == 1`:
                        │   ➔ GỌI `Sched_Preempt`!
                        │   ➔ Kích hoạt ngắt `PendSV` để tráo đổi Task ưu tiên cao hơn!
                        │
                        └─► `pop {r4-r11, pc}` (Thoát hoàn toàn Handler Mode, trả CPU cho Task mới)
+===================================================================================================+
```

---

### 7.3 Tam Giác Vàng Của AUTOSAR OS: SysTick, PendSV, SVCall

Hệ điều hành `askar` sử dụng chính xác 3 ngoại lệ hệ thống của ARM Cortex-M tại các vị trí cố định trong bảng Vector Table để vận hành bộ máy lập lịch thời gian thực:

1. **SVCall (`knl_start_dispatch` — Exception #11):**
   - Kích hoạt thông qua lệnh hợp ngữ `SVC #0` khi ứng dụng gọi `StartOS(OSDEFAULTAPPMODE)`.
   - Chức năng: Thiết lập con trỏ ngăn xếp cho Task đầu tiên, chuyển CPU từ Privileged sang Unprivileged (nếu dùng MPU), và chính thức bắt đầu vận hành hệ điều hành.
2. **SysTick (`knl_system_tick` — Exception #15):**
   - Định thời nhịp hệ thống (thường cấu hình chu kỳ 1 ms).
   - Gọi hàm C `knl_system_tick_handler()` tại [`portable.c`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/com/as.infrastructure/system/kernel/askar/portable/cortex-m/portable.c).
   - Tăng các bộ đếm Counter (`CounterTrigger()`), kích hoạt các Alarm định kỳ của AUTOSAR để khởi chạy các Task tuần hoàn của ComStack và RTE.
3. **PendSV (`knl_dispatch_entry` — Exception #14):**
   - **Luôn được cấu hình mức ưu tiên thấp nhất trong NVIC (Priority = 0xFF)**.
   - Là cỗ máy chuyển đổi ngữ cảnh (Context Switch Engine). Khi một Task bị cướp quyền hoặc tự nguyện nhường quyền, OS kích hoạt bit `PENDSVSET` trong thanh ghi `SCB->ICSR`.
   - `knl_dispatch_entry` chỉ chạy khi toàn bộ các ngắt phần cứng đã xử lý xong, đảm bảo tính toàn vẹn tuyệt đối của dữ liệu.

---

### 7.4 4 Cấp Độ Khóa Ngắt Trong Tiêu Chuẩn AUTOSAR OS

Chuẩn OSEK / AUTOSAR OS cung cấp 4 API quản lý khóa ngắt phục vụ việc bảo vệ vùng găng (Critical Section):

```
+-----------------------------------------------------------------------------------+
|               PHÂN CẤP CÁC API KHÓA NGẮT TRONG AUTOSAR OS                         |
+-----------------------------------------------------------------------------------+

1. `DisableAllInterrupts()` / `EnableAllInterrupts()`:
   • Cơ chế phần cứng: Ghi vào thanh ghi `PRIMASK` (`CPSID i` / `CPSIE i`).
   • Phạm vi khóa: Khóa TOÀN BỘ ngắt ngoại vi phần cứng (kể cả ISR Cat 1 và Cat 2),
     chỉ trừ NMI và HardFault.
   • Khuyến cáo: Chỉ dùng trong trường hợp cực đoan, thời gian thực thi < 1 µs.

2. `SuspendAllInterrupts()` / `ResumeAllInterrupts()`:
   • Cơ chế: Hỗ trợ lồng nhau (Nesting) thông qua biến đếm nội bộ của OS.
   • Khóa toàn bộ ngắt phần cứng tương tự PRIMASK nhưng cho phép gọi nhiều lần lồng nhau.

3. `SuspendOSInterrupts()` / `ResumeOSInterrupts()`:
   • Cơ chế phần cứng: Ghi vào thanh ghi `BASEPRI` (`MSR BASEPRI, r0`).
   • Phạm vi khóa: CHỈ khóa các ngắt có Priority thấp hơn hoặc bằng ngưỡng OS quy định
     (tức là CHỈ khóa các ngắt ISR Category 2).
   • ĐIỂM SỐNG CÒN: Các ngắt ISR Category 1 (Priority cao hơn BASEPRI) VẪN CHẠY BÌNH THƯỜNG!
   • Ứng dụng: Dùng để đồng bộ dữ liệu giữa các Task và ISR Category 2 trong BSW.

4. `ClearEvent()` / `WaitEvent()`:
   • Cơ chế lập lịch: Chuyển Task sang trạng thái WAITING, giải phóng hoàn toàn CPU
     để các Task khác chạy cho đến khi có ngắt ISR Cat 2 gọi `SetEvent()`.
+-----------------------------------------------------------------------------------+
```

---

### 7.5 Câu Hỏi Kiểm Tra Tư Duy — Chương 7

1. **Câu 1:** Trong dự án `as`, tại sao hàm `knl_isr_process` không gọi trực tiếp hàm xử lý của MCAL Driver mà phải đi qua `EnterISR` và `ExitISR`?
2. **Câu 2:** Nếu một kỹ sư gọi hàm `WaitEvent(EVENT_CAN_RX)` bên trong hàm ngắt `Can_RxIsr()`, hệ điều hành `askar` sẽ hành xử như thế nào và lỗi gì sẽ phát sinh?
3. **Câu 3:** Tại sao trong kiến trúc AUTOSAR, các thuật toán bảo vệ quá dòng động cơ điện bắt buộc phải cấu hình là **ISR Category 1** thay vì Category 2?

---

<a name="ch8"></a>
## CHƯƠNG 8: KIẾN TRÚC BOOTLOADER Ô TÔ & TÁI ĐỊNH VỊ VECTOR TABLE (AUTOSAR ASBOOT & FOTA)

### 8.1 Sơ Đồ Phân Vùng Flash ECU Trong Dự Án `as` (`asboot` vs `ascore`)

Trong sản xuất phần mềm ECU ô tô theo chuẩn AUTOSAR, bộ nhớ Flash của vi điều khiển được phân chia nghiêm ngặt giữa **AUTOSAR Bootloader (`asboot`)** và **Ứng dụng chính (`ascore`)**:

```
SƠ ĐỒ PHÂN VÙNG BỘ NHỚ FLASH THỰC TẾ TRONG DỰ ÁN AS (STM32F107VC):

Địa chỉ Flash
0x08040000 +------------------------------------------+  <-- HẾT FLASH VẬT LÝ (256 KB)
           |  Vùng Lưu Trữ Firmware Dự Phòng / OTA    |
0x08010000 +------------------------------------------+
           |  APPLICATION FIRMWARE (`ascore`)         |  (Cấu hình bởi `linker-app.lds`)
           |  • Bảng Vector Table của App (1024B)     |  <-- TỌA ĐỘ VĂNG RA TẠI 0x08010000
           |    [0] `knl_system_stack_top` của App    |
           |    [1] `reset_handler` của App           |
           |  • AUTOSAR BSW Stack & Application Tasks  |
0x08010000 +------------------------------------------+  <-- ĐỊA CHỈ NHẢY (APP_START_ADDR)
           |  BOOTLOADER FIRMWARE (`asboot`)          |  (Cấu hình bởi `linker-boot.lds`)
           |  • Bảng Vector Table của Bootloader      |  <-- NẰM TẠI ĐỊA CHỈ MẶC ĐỊNH 0x08000000
           |    [0] `knl_system_stack_top` của BL     |
           |    [1] `reset_handler` của BL            |
           |  • UDS ISO 14229 Diagnostic Protocol     |
           |  • CAN Driver Flash Programming Kernel   |
0x08000000 +------------------------------------------+  <-- BẮT ĐẦU FLASH VẬT LÝ
```

---

### 8.2 Quy Trình 9 Bước Chuyển Giao Quyền Từ `asboot` Sang `ascore`

Mã nguồn thực tế trong [`as/com/as.infrastructure/boot/common/bl_core.c`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/com/as.infrastructure/boot/common/bl_core.c) thực hiện chuyển giao quyền thực thi sang Application theo quy chuẩn an toàn ô tô:

```c
#define APPLICATION_START_ADDRESS   (0x08010000UL)

typedef void (*pFunction)(void);

void Jump_To_Application(void) {
    uint32_t app_stack_pointer;
    uint32_t app_reset_handler_addr;
    pFunction app_entry;

    /* BƯỚC 1: Đọc giá trị Initial Stack Pointer của App tại Entry [0] */
    app_stack_pointer = *(__IO uint32_t*)APPLICATION_START_ADDRESS;

    /* BƯỚC 2: Kiểm tra tính hợp lệ của Stack Pointer (Phải nằm trong không gian SRAM 0x20000000) */
    if ((app_stack_pointer & 0xFFFE0000) != 0x20000000) {
        /* Firmware Application bị rỗng hoặc lỗi nạp (Corrupted App) -> Ở lại Bootloader */
        return;
    }

    /* BƯỚC 3: Đọc địa chỉ hàm reset_handler của App tại Entry [1] */
    app_reset_handler_addr = *(__IO uint32_t*)(APPLICATION_START_ADDRESS + 4);
    app_entry = (pFunction)app_reset_handler_addr;

    /* BƯỚC 4: Khóa toàn bộ ngắt toàn cục để đóng băng hệ thống */
    Irq_Disable();

    /* BƯỚC 5: Tắt toàn bộ ngắt phần cứng trong NVIC và xóa sạch trạng thái Pending */
    for (int i = 0; i < 8; i++) {
        NVIC->ICER[i] = 0xFFFFFFFF;  /* Disable all IRQ channels */
        NVIC->ICPR[i] = 0xFFFFFFFF;  /* Clear all Pending flags */
    }

    /* BƯỚC 6: Tắt bộ đếm SysTick để không sinh ngắt đè vào quá trình Boot của App */
    SysTick->CTRL = 0;
    SysTick->LOAD = 0;
    SysTick->VAL  = 0;

    /* BƯỚC 7: TÁI ĐỊNH VỊ VECTOR TABLE SANG APPLICATION */
    SCB->VTOR = APPLICATION_START_ADDRESS;

    /* BƯỚC 8: Thiết lập Main Stack Pointer (MSP) trỏ vào đỉnh Stack của App */
    __set_MSP(app_stack_pointer);

    /* BƯỚC 9: Đồng bộ pipeline lệnh và nhảy thẳng vào reset_handler của Application */
    __ISB();
    __DSB();
    Irq_Enable();
    app_entry();

    /* Đoạn code phòng thủ: Không bao giờ được chạy tới đây */
    while (1) {
        __NOP();
    }
}
```

---

### 8.3 5 Lỗi Kinh Điển Khi Nạp Firmware ECU Khiến Ứng Dụng Crash

| Lỗi Phổ Biến | Nguyên Nhân Bản Chất Trong ECU Ô Tô | Cách Khắc Phục Chuẩn Senior |
|---|---|---|
| **Lỗi 1: HardFault ngay khi App nhận frame CAN đầu tiên** | Bootloader nhảy vào App nhưng quên cập nhật thanh ghi `SCB->VTOR = 0x08010000`. Khi có ngắt CAN RX, CPU vẫn tra cứu Vector Table của Bootloader và nhảy vào ô nhớ rác! | Bắt buộc nạp `SCB->VTOR = APPLICATION_START_ADDRESS` trước khi gọi `app_entry()`. |
| **Lỗi 2: Lỗi tràn Stack bí ẩn trong nhân OS `askar`** | Bootloader quên gọi `__set_MSP(app_stack_pointer)`, khiến App tiếp tục chạy trên vùng Stack còn sót lại của Bootloader thay vì `knl_system_stack`. | Nạp `__set_MSP()` trực tiếp từ Entry [0] của Application. |
| **Lỗi 3: App bị treo cứng trong vòng lặp vô tận** | CAN Controller của Bootloader vẫn đang chạy ngắt dở dang. App chưa khởi tạo xong `Can_Init()` nhưng đã bị ngắt tồn đọng của Bootloader ập vào. | Tắt toàn bộ Clock ngoại vi và tắt NVIC (`NVIC->ICER`) trước khi chuyển giao quyền. |
| **Lỗi 4: AUTOSAR OS không thể cướp quyền (No Preemption)** | SysTick của Bootloader vẫn chạy nền, xung đột trực tiếp với bộ định thời `knl_system_tick` của hệ điều hành `askar`. | Tắt sạch thanh ghi `SysTick->CTRL = 0` trước khi nhảy. |
| **Lỗi 5: UsageFault INVSTATE** | Địa chỉ hàm `reset_handler` trong file `.bin` bị mất bit LSB (Thumb bit 0 = 0 do lỗi liên kết Linker). | Đảm bảo Entry [1] của App luôn là địa chỉ lẻ (Bit 0 = 1). |

---

### 8.4 Câu Hỏi Kiểm Tra Tư Duy — Chương 8

1. **Câu 1:** Trong tiêu chuẩn chẩn đoán ô tô UDS (ISO 14229), sau khi hoàn tất nạp Flash qua chuỗi dịch vụ `$34` (RequestDownload) ➔ `$36` (TransferData) ➔ `$37` (RequestTransferExit), tại sao ECU thường phát sinh lệnh `$11 01` (ECU Reset) thay vì nhảy trực tiếp vào App bằng con trỏ hàm?
2. **Câu 2:** Tại sao thanh ghi `SCB->VTOR` khi được gán địa chỉ `0x08010000` lại bắt buộc địa chỉ này phải chia hết cho 512 hoặc 1024 bytes (Alignment Rule)? Nếu đặt App bắt đầu tại `0x08010080`, chuyện gì sẽ xảy ra với các hàm ngắt?
3. **Câu 3:** Trong các hệ thống an toàn ô tô (Automotive ECU), trước khi nhảy vào Application, Bootloader cần thực hiện các bước xác thực phần mềm (Secure Boot - Checksum CRC32 / RSA Signature) nào để ngăn ngừa firmware giả mạo?

---

<a name="ch9"></a>
## CHƯƠNG 9: DEBUGGING VECTOR TABLE — 5 CASE STUDY THỰC TẾ

### 🐞 CASE STUDY 1: Interrupt Không Bao Giờ Nhảy Vào ISR

#### 📋 Quy Trình Chẩn Đoán 9 Bước Chuẩn Senior (Elimination Checklist):

```
[BƯỚC 1: KIỂM TRA PERIPHERAL CLOCK]
- Đọc thanh ghi RCC->APB1ENR / APB2ENR / AHB1ENR tương ứng.
- Nếu Clock ngoại vi chưa bật (bit = 0) ➔ Ngoại vi chết lâm sàng, không thể sinh ngắt!
- Fix: `RCC->APB1ENR |= RCC_APB1ENR_TIM2EN;`

[BƯỚC 2: KIỂM TRA CỜ SỰ KIỆN PHẦN CỨNG (HARDWARE FLAG)]
- Dùng Debugger đọc thanh ghi trạng thái (TIM2->SR, USART1->SR).
- Cờ sự kiện (UIF, RXNE) có bật lên 1 khi có tín hiệu vật lý không?
- Nếu cờ không bật ➔ Lỗi cấu hình thông số ngoại vi (Prescaler, Baudrate, GPIO Pin Alternate Function).

[BƯỚC 3: KIỂM TRA PERIPHERAL INTERRUPT ENABLE (NGOẠI VI NỘI BỘ)]
- Đọc thanh ghi DIER / CR1 của ngoại vi (TIM2->DIER bit UIE = 1?).
- Nếu cờ sự kiện bật nhưng bit Interrupt Enable = 0 ➔ Ngoại vi không kéo đường dây IRQ.
- Fix: `TIM2->DIER |= TIM_DIER_UIE;`

[BƯỚC 4: KIỂM TRA NVIC ENABLE REGISTER]
- Dùng GDB đọc: `x/8xw 0xE000E100` (NVIC->ISER).
- Kênh IRQ của ngoại vi (ví dụ TIM2_IRQn = 28) có bit tương ứng bằng 1 không?
- Fix: `NVIC_EnableIRQ(TIM2_IRQn);`

[BƯỚC 5: KIỂM TRA LỌC NGƯỠNG PRIORITY (BASEPRI & PRIMASK)]
- Đọc thanh ghi BASEPRI: Mức ưu tiên của ngắt có bị chặn bởi BASEPRI của RTOS không?
- Đọc thanh ghi PRIMASK: Có đoạn mã nào đang khóa ngắt toàn cục (`__disable_irq()`) mà quên mở không?
- Fix: `__set_BASEPRI(0);` và `__enable_irq();`

[BƯỚC 6: KIỂM TRA THANH GHI VTOR]
- Đọc thanh ghi: `x/xw 0xE000ED08` (SCB->VTOR).
- Giá trị VTOR có đúng là `0x08000000` (hoặc địa chỉ bắt đầu của App `0x08008000`) không?
- Nếu VTOR trỏ ra địa chỉ rác ➔ CPU tra cứu sai bảng Vector.

[BƯỚC 7: KIỂM TRA GIÁ TRỊ TRONG VECTOR TABLE TẠI RUNTIME]
- Tính toán địa chỉ Vector: Target = VTOR + (Exception_Num * 4).
- Dùng GDB đọc 4 bytes tại Target: Giá trị có phải là con trỏ hàm ISR hợp lệ trong Flash không?
- Bit 0 của con trỏ hàm có bằng 1 (Thumb bit) không?

[BƯỚC 8: KIỂM TRA TÊN HÀM VÀ EXTERN "C"]
- Kiểm tra xem tên hàm ISR trong file `.c` có bị sai chính tả (Typo) so với tên trong startup code không.
- Nếu viết bằng C++, đã có bọc `extern "C"` chưa? (Nếu thiếu `extern "C"`, C++ Name Mangling sẽ đổi tên hàm khiến Linker không thể nhận diện!).

[BƯỚC 9: KIỂM TRA LINKER SECTION KEEP()]
- Kiểm tra file `.map` và disasm `.elf`: Mảng `.isr_vector` có bị Linker Garbage Collection `-Wl,--gc-sections` xóa bỏ không?
```

---

### 🐞 CASE STUDY 2: CPU Bị Kẹt Trong `Default_Handler` (Vòng Lặp Vô Tận)

#### 🔍 Cơ Chế Bẫy Lỗi Trong `Default_Handler`
Khi CPU nhảy vào `Default_Handler`, nghĩa là **CÓ MỘT INTERRUPT ĐÃ XẢY RA NHƯNG CHƯA ĐƯỢC VIẾT HÀM XỬ LÝ (Hoặc bị sai tên hàm)**.

```c
/* Nâng cấp Default_Handler chuẩn Senior để tự động chẩn đoán chính xác IRQ nào gây lỗi: */
void Default_Handler(void) {
    /* Đọc thanh ghi IPSR (Interrupt Program Status Register) để lấy Exception Number */
    volatile uint32_t active_exception = __get_IPSR() & 0x1FF;
    volatile int active_irq_number = (int)active_exception - 16;

    /* TẠI ĐÂY: Dừng Debugger để xem biến active_irq_number!
       - Nếu active_exception == 15  -> SysTick_Handler bị thiếu hoặc sai tên!
       - Nếu active_irq_number == 28 -> TIM2_IRQHandler bị thiếu hoặc sai tên!
       - Nếu active_irq_number == 37 -> USART1_IRQHandler bị thiếu hoặc sai tên!
    */
    __BKPT(0);  /* Kích hoạt điểm dừng phần cứng Debugger */
    while (1) {
        /* Chờ kỹ sư kết nối GDB kiểm tra biến */
    }
}
```

---

### 🐞 CASE STUDY 3: CPU Rơi Vào `HardFault` Ngay Sau Khi Interrupt Xảy Ra

#### 🔬 Bảng Ma Trận Nguyên Nhân & Cách Phân Biệt:

```
NGUYÊN NHÂN 1: Lỗi Phân Giải Vector Table (Vector Table Read Fault)
• Thanh ghi chẩn đoán: `SCB->HFSR` có bit `VECTTBL` (Bit 1) = 1.
• Bản chất: CPU gặp lỗi Bus khi cố gắng đọc 4 bytes con trỏ hàm trong Vector Table (VTOR trỏ vào vùng nhớ không tồn tại).
• Cách fix: Kiểm tra lại giá trị nạp vào VTOR và bộ nhớ Flash/RAM.

NGUYÊN NHÂN 2: Lỗi Tràn Khung Ngữ Cảnh (Stacking Error / Stack Overflow)
• Thanh ghi chẩn đoán: `SCB->CFSR` có bit `STKERR` (Bit 12) = 1 hoặc `MSTKERR` (Bit 4) = 1.
• Bản chất: Khi ngắt kích hoạt, CPU tự động PUSH 32 bytes xuống Stack. Tuy nhiên, con trỏ Stack Pointer (MSP/PSP) đã chạm đáy RAM hoặc vượt ra ngoài vùng nhớ MPU cho phép!
• Cách fix: Tăng dung lượng Stack của Task / System Stack trong Linker Script.

NGUYÊN NHÂN 3: Mất Thumb Bit Trong Con Trỏ Hàm ISR
• Thanh ghi chẩn đoán: `SCB->CFSR` có bit `INVSTATE` (Bit 17) = 1 trong trường UsageFault.
• Bản chất: Con trỏ hàm trong Vector Table có Bit 0 = 0 (Địa chỉ chẵn). CPU cố gắng chuyển sang chế độ ARM State vốn không được hỗ trợ trên Cortex-M!
• Cách fix: Đảm bảo địa chỉ con trỏ hàm luôn được cộng thêm 1 (Bit 0 = 1).
```

---

### 🐞 CASE STUDY 4: Firmware Chạy Đúng Ở Debug (-O0) Nhưng Sập Ở Release (-O2)

#### 🔬 Phân Tích 3 Bản Chất Kỹ Nghệ:

```c
/* NGUYÊN NHÂN A: Thiếu từ khóa 'volatile' cho biến chia sẻ giữa ISR và Main Thread */
/* SAI: */
uint8_t g_packet_ready = 0;

void USART1_IRQHandler(void) {
    g_packet_ready = 1;  /* Ghi trong ISR */
}

void Process_Task(void) {
    /* Ở mức tối ưu -O2, Compiler nhận thấy biến g_packet_ready không bị thay đổi
       trong thân vòng lặp -> Compiler TỐI ƯU HÓA ĐỌC BIẾN NÀY VÀO MỘT THANH GHI CPU (R4)
       VÀ KHÔNG BAO GIỜ ĐỌC LẠI TỪ RAM NỮA! Vòng lặp trở thành while(1) vô tận! */
    while (!g_packet_ready) {
        /* Busy wait */
    }
}

/* ĐÚNG CHUẨN: */
volatile uint8_t g_packet_ready = 0;  /* Ép Compiler luôn đọc từ ô nhớ RAM */
```

```c
/* NGUYÊN NHÂN B: Thiếu rào cản bộ nhớ (Memory Barrier) */
volatile uint8_t  g_data_ready = 0;
uint32_t          g_sensor_data = 0;

void Sensor_IRQHandler(void) {
    g_sensor_data = SENSOR->DATA;  /* Đọc dữ liệu */
    __DMB();                       /* Data Memory Barrier: Đảm bảo g_sensor_data được ghi xong */
    g_data_ready = 1;              /* Bật cờ sẵn sàng */
}
```

```c
/* NGUYÊN NHÂN C: Cờ ngắt chưa kịp xóa đã thoát ISR do độ trễ Bus (Write Buffer Latency) */
void TIM2_IRQHandler(void) {
    if (TIM2->SR & TIM_SR_UIF) {
        TIM2->SR &= ~TIM_SR_UIF;  /* Lệnh ghi xóa cờ */
        /* Ở mức -O2, code chạy cực nhanh. Lệnh ghi vào thanh ghi ngoại vi qua bus APB1
           chưa kịp hoàn tất trên phần cứng thì CPU đã thực thi lệnh BX LR thoát ngắt!
           Cờ UIF vẫn còn = 1 trên ngoại vi ➔ CPU bị ngắt lại ngay lập tức (Interrupt Storm)! */
        
        /* FIX SENIOR: Thêm lệnh đọc lại thanh ghi hoặc DSB để ép Bus hoàn tất lệnh ghi */
        (void)TIM2->SR;  /* Dummy read để đồng bộ Bus */
    }
}
```

---

<a name="ch10"></a>
## CHƯƠNG 10: QUY TRÌNH DEBUG CHUYÊN SÂU VỚI GDB

### 10.1 15 Lệnh GDB Bắt Buộc Của Kỹ Sư Senior

```gdb
# 1. Đọc 16 phần tử đầu tiên của bảng Vector Table tại đầu Flash
(gdb) x/16xw 0x08000000

# 2. Đọc thanh ghi VTOR để kiểm tra vị trí hiện tại của Vector Table
(gdb) x/1xw 0xE000ED08

# 3. Đọc thanh ghi ICSR (Interrupt Control and State Register) để xem ngắt nào đang Pending/Active
(gdb) x/1xw 0xE000ED04

# 4. Đọc toàn bộ thanh ghi trạng thái lỗi CFSR (Configurable Fault Status Register)
(gdb) x/1xw 0xE000ED28

# 5. Đọc thanh ghi HFSR (HardFault Status Register)
(gdb) x/1xw 0xE000ED2C

# 6. Đọc thanh ghi BFAR (BusFault Address Register - Ô nhớ gây lỗi Bus)
(gdb) x/1xw 0xE000ED34

# 7. Đọc thanh ghi MMFAR (MemManage Address Register - Ô nhớ vi phạm MPU)
(gdb) x/1xw 0xE000ED38

# 8. Xem toàn bộ giá trị các thanh ghi CPU Core hiện tại
(gdb) info registers

# 9. Đọc 8 giá trị trong khung Auto-stacking từ con trỏ Stack Pointer ($sp)
(gdb) x/8xw $sp

# 10. Xem địa chỉ lệnh bị ngắt (Stacked PC nằm ở vị trí thứ 7 trong khung Stack)
(gdb) print/x *(uint32_t*)($sp + 24)

# 11. Tìm tên hàm và dòng mã nguồn tương ứng với địa chỉ bị lỗi
(gdb) info line *(*(uint32_t*)($sp + 24))
(gdb) list *(*(uint32_t*)($sp + 24))

# 12. Kiểm tra CPU đang ở Thread Mode hay Handler Mode (Đọc thanh ghi xPSR)
(gdb) print/x $xpsr & 0x1FF

# 13. Xem danh sách các kênh ngắt đang được Enable trong NVIC (ISER 0 đến 2)
(gdb) x/3xw 0xE000E100

# 14. Xem danh sách các kênh ngắt đang ở trạng thái Active trong NVIC (IABR 0 đến 2)
(gdb) x/3xw 0xE000E300

# 15. Disassemble 10 lệnh Assembly tại vị trí hàm ISR hiện tại
(gdb) x/10i $pc
```

---

### 10.2 Giải Mã Thanh Ghi Lỗi CFSR (Configurable Fault Status Register)

Thanh ghi `SCB->CFSR` (Địa chỉ `0xE000ED28`) là "hộp đen" quý giá nhất khi xảy ra Crash:

```
CẤU TRÚC 32-BIT CỦA THANH GHI CFSR:

 31          25 24 23         19 18 17 16 15        9 8 7          1 0
+--------------+--+-------------+--+--+--+-----------+-+------------+-+
| UsageFault   |D | Unaligned   |N |I |I | BusFault  |P| MemManage  |I|
| Status (UFSR)|I | Access (24) |O |N |N | (BFSR)    |R| (MMFSR)    |A|
|              |V |             |C |V |V |           |E|            |C|
|              |0 |             |P |P |S |           |C|            |C|
|              |(25)            |(19)|C|(17)|         |(9)           |(0)
+--------------+--+-------------+--+--+--+-----------+-+------------+-+

CÁC BIT QUAN TRỌNG NHẤT:
• Bit 25 (DIVBYZERO) : Lỗi chia cho 0 trong phần mềm.
• Bit 24 (UNALIGNED) : Truy cập dữ liệu 32-bit tại địa chỉ không chia hết cho 4.
• Bit 18 (INVPC)     : Lỗi EXC_RETURN không hợp lệ khi thoát ngắt.
• Bit 17 (INVSTATE)  : CPU cố gắng chạy tập lệnh ARM 32-bit thay vì Thumb (Mất Thumb Bit 0).
• Bit 16 (UNDEFINSTR): CPU gặp lệnh rác không thể giải mã (Nhảy vào vùng Flash rác).
• Bit 15 (BFARVALID) : Địa chỉ trong thanh ghi BFAR là hợp lệ -> Đọc ngay BFAR để tìm thủ phạm!
• Bit 12 (STKERR)    : Lỗi Bus khi CPU tự động PUSH Stack lúc vào ngắt (Tràn Stack!).
• Bit 11 (UNSTKERR)  : Lỗi Bus khi CPU tự động POP Stack lúc thoát ngắt.
• Bit 9  (PRECISERR) : Truy cập ô nhớ bị cấm hoặc ngoại vi chưa cấp Clock.
• Bit 7  (MMARVALID) : Địa chỉ trong MMFAR là hợp lệ -> Vi phạm phân vùng bảo vệ MPU!
```

---

<a name="ch11"></a>
## CHƯƠNG 11: 15+ SAI LẦM PHỔ BIẾN (MISCONCEPTIONS) CỦA JUNIOR

### ❌ Misconception 1: "Vector Table chính là NVIC"
* ❌ **Sai ở đâu:** Nghĩ rằng bảng Vector Table là một phần cứng tích hợp bên trong NVIC.
* ✅ **Cách hiểu đúng:** NVIC là khối **Hardware** quản lý logic (bật/tắt, priority, pending). Vector Table là một **Mảng dữ liệu phần mềm** nằm trong bộ nhớ Flash/RAM. NVIC chỉ gửi Exception Number tới CPU, còn CPU tự đọc mảng Vector Table để lấy địa chỉ hàm ISR.
* 🧠 **Vì sao dễ nhầm:** Cả hai đều cùng xuất hiện trong tài liệu về ngắt.
* 🔧 **Hậu quả Production:** Cấu hình sai thứ tự khởi tạo, không biết cách relocate Vector Table khi viết Bootloader.

---

### ❌ Misconception 2: "Bật `NVIC_EnableIRQ()` là đủ để ngắt hoạt động"
* ❌ **Sai ở đâu:** Cho rằng chỉ cần bật NVIC là ngoại vi sẽ tự động sinh ngắt.
* ✅ **Cách hiểu đúng:** Cần thỏa mãn đủ chuỗi **7 mắt xích phần cứng**: (1) Cấp Clock ngoại vi, (2) Cấu hình chân GPIO, (3) Cấu hình tham số ngoại vi, (4) Bật cờ ngắt nội bộ ngoại vi (DIER/CR), (5) Cấu hình Priority, (6) Bật kênh trong NVIC, (7) Mở ngắt toàn cục (`__enable_irq()`).
* 🧠 **Vì sao dễ nhầm:** Thư viện HAL đôi khi gom chung các bước khiến lập trình viên mất đi cái nhìn gốc rễ.
* 🔧 **Hậu quả Production:** Mất hàng giờ đồng hồ vô ích để debug mà không hiểu tại sao ngắt không chạy.

---

### ❌ Misconception 3: "Priority số lớn hơn là ưu tiên cao hơn"
* ❌ **Sai ở đâu:** Nghĩ rằng Priority 15 ưu tiên hơn Priority 0.
* ✅ **Cách hiểu đúng:** Trong kiến trúc ARM Cortex-M NVIC, **SỐ CÀNG NHỎ THÌ MỨC ƯU TIÊN PHẦN CỨNG CÀNG CAO** (Priority 0 là cao nhất).  
  ⚠️ **CỰC KỲ NGUY HIỂM TRONG DỰ ÁN AUTOSAR:** Trong hệ điều hành AUTOSAR OS (`askar`), quy ước mức ưu tiên của Task lại **HOÀN TOÀN NGƯỢC LẠI**: Task có Priority số lớn hơn sẽ được ưu tiên chạy trước (High Priority Number = High Priority)! Kỹ sư nhúng rất hay nhầm lẫn giữa ARM NVIC Priority và AUTOSAR Task Priority.
* 🧠 **Vì sao dễ nhầm:** Hai hệ thống định nghĩa thứ tự ưu tiên đối lập nhau 180 độ.
* 🔧 **Hậu quả Production:** Cấu hình nhầm ngắt an toàn phanh/lái thành ưu tiên thấp nhất, hoặc Task xử lý khẩn cấp không thể cướp quyền Task thông thường.

---

### ❌ Misconception 4: "Có thể gọi `WaitEvent()` hoặc `TerminateTask()` trong hàm ngắt MCAL ISR"
* ❌ **Sai ở đâu:** Nghĩ rằng hàm ngắt có thể dừng chờ sự kiện hoặc tự kết thúc một Task.
* ✅ **Cách hiểu đúng:** Trong chuẩn AUTOSAR OS, hàm ngắt (kể cả ISR Category 2) chạy trong Handler Mode trên ngăn xếp hệ thống `knl_system_stack`. Nó **KHÔNG PHẢI LÀ MỘT TASK** nên không có cấu trúc TCB để lưu trạng thái ngủ (WAITING). Gọi `WaitEvent()` trong ISR sẽ làm sập lõi CPU ngay lập tức! ISR chỉ được phép gọi `SetEvent()` hoặc `ActivateTask()` để báo hiệu cho Task khác.
* 🧠 **Vì sao dễ nhầm:** Tưởng rằng mọi hàm của OS đều có thể gọi ở mọi nơi.
* 🔧 **Hậu quả Production:** Hệ điều hành `askar` kích hoạt Panic/ShutdownOS(0xFF), xe dừng hoạt động đột ngột giữa đường.

---

### ❌ Misconception 5: "Vector Table bắt buộc phải cố định tại địa chỉ 0x00000000"
* ❌ **Sai ở đâu:** Cho rằng không thể thay đổi vị trí Vector Table sau khi nạp code.
* ✅ **Cách hiểu đúng:** Cortex-M3/M4/M7/M33 trang bị thanh ghi `SCB->VTOR` cho phép di chuyển Vector Table tới bất kỳ vị trí nào trong Flash hoặc RAM tại runtime.
* 🧠 **Vì sao dễ nhầm:** Học trên các dòng vi điều khiển 8-bit cũ (8051, PIC) hoặc Cortex-M0 (vốn không có VTOR).
* 🔧 **Hậu quả Production:** Không thể phát triển kiến trúc Bootloader OTA hoặc cập nhật ISR động trong RAM.

---

### ❌ Misconception 6: "Viết sai tên hàm ISR thì Trình biên dịch sẽ báo lỗi Compile"
* ❌ **Sai ở đâu:** Nghĩ rằng compiler sẽ kiểm tra lỗi chính tả của tên hàm ngắt.
* ✅ **Cách hiểu đúng:** Do cơ chế **Weak Alias**, nếu viết sai tên hàm (ví dụ `Tim2_IRQHandler` thay vì `TIM2_IRQHandler`), Linker sẽ âm thầm trỏ Vector Table về `Default_Handler`. Chương trình biên dịch 100% thành công mà không có bất kỳ cảnh báo nào!
* 🧠 **Vì sao dễ nhầm:** Nghĩ rằng C Compiler kiểm soát toàn bộ định danh hàm.
* 🔧 **Hậu quả Production:** Thiết bị treo cứng trong `Default_Handler` ngay khi sự kiện ngắt đầu tiên kích hoạt.

---

### ❌ Misconception 7: "Interrupt luôn luôn ngắt ngang CPU ngay lập tức"
* ❌ **Sai ở đâu:** Nghĩ rằng độ trễ ngắt (Interrupt Latency) luôn luôn bằng 0.
* ✅ **Cách hiểu đúng:** Ngắt có thể bị trì hoãn bởi: (1) CPU đang bận hoàn tất câu lệnh hiện tại, (2) CPU đang nằm trong vùng Critical Section (`BASEPRI` / `PRIMASK`), (3) Một ngắt khác có Priority cao hơn đang thực thi.
* 🧠 **Vì sao dễ nhầm:** Khái niệm "Real-Time" bị hiểu nhầm thành "Tức thời vô hạn".
* 🔧 **Hậu quả Production:** Bỏ sót xung ngắt tốc độ cao hoặc tính toán sai lệch ngân sách thời gian thực (Timing Budget).

---

### ❌ Misconception 8: "Không cần xóa cờ ngắt ngoại vi trong ISR nếu hàm quá ngắn"
* ❌ **Sai ở đâu:** Bỏ qua dòng lệnh xóa cờ ngắt phần cứng (ví dụ `TIM2->SR &= ~TIM_SR_UIF;`).
* ✅ **Cách hiểu đúng:** Nếu không xóa cờ ngắt, đường tín hiệu IRQ line vẫn duy trì mức tích cực ➔ Ngay khi CPU thoát ngắt bằng `BX LR`, nó sẽ bị NVIC kéo quay trở lại ISR ngay lập tức ➔ Tạo ra cơn bão ngắt (**Interrupt Storm**), khóa chặt chương trình chính!
* 🧠 **Vì sao dễ nhầm:** Tưởng rằng CPU tự động xóa cờ ngắt của ngoại vi.
* 🔧 **Hậu quả Production:** CPU quá tải 100% trong ISR, hệ thống tê liệt hoàn toàn.

---

### ❌ Misconception 9: "Dùng hàm `printf()` trong ISR để debug rất tiện"
* ❌ **Sai ở đâu:** Gọi `printf()` qua UART blocking hoặc `malloc()` bên trong hàm ngắt.
* ✅ **Cách hiểu đúng:** `printf()` tốn hàng mili-giây để truyền chuỗi byte qua UART, phá nát tính thời gian thực của toàn bộ hệ thống và có nguy cơ tràn Stack của ngắt.
* 🧠 **Vì sao dễ nhầm:** Thói quen debug trên môi trường PC/Desktop.
* 🔧 **Hậu quả Production:** Mất dữ liệu của các ngoại vi khác, kích hoạt Watchdog Timeout reset vi điều khiển.

---

### ❌ Misconception 10: "Mọi dòng ARM Cortex-M đều xử lý ngắt giống hệt nhau"
* ❌ **Sai ở đâu:** Nghĩ rằng code startup và cấu hình ngắt trên Cortex-M0 giống hệt Cortex-M4/M7.
* ✅ **Cách hiểu đúng:** Cortex-M0/M0+ không có thanh ghi VTOR, chỉ hỗ trợ 2-bit Priority (4 mức), không hỗ trợ Fault Handlers phân tách. Trong khi Cortex-M4/M7 hỗ trợ VTOR, FPU Context Stacking, và MPU.
* 🧠 **Vì sao dễ nhầm:** Cùng mang thương hiệu "Cortex-M".
* 🔧 **Hậu quả Production:** Lỗi biên dịch hoặc crash phần cứng khi porting code giữa các dòng vi điều khiển khác nhau.

---

### ❌ Misconception 11: "Có thể sửa tay file `Os_Cfg.c` hoặc `Can_Cfg.c` khi muốn đổi số Vector hoặc thêm ngắt"
* ❌ **Sai ở đâu:** Tự ý mở các file mã nguồn phát sinh `*_Cfg.c` và sửa tay bảng con trỏ hàm ngắt `tisr_pc[]` hoặc hàm ngắt `Can_RxIsr`.
* ✅ **Cách hiểu đúng:** Trong quy trình phát triển AUTOSAR, các file có đuôi `*_Cfg.c` và `*_Cfg.h` là **MÃ PHÁT SINH TỰ ĐỘNG (GENERATED CODE)** bởi công cụ phát sinh (trong dự án `as` là script Python `GenOS.py`, trong công nghiệp là Vector DaVinci Configurator hoặc EB tresos). Mọi thay đổi về ngắt, độ ưu tiên, gán kênh ngoại vi BẮT BUỘC phải thực hiện trên file cấu hình mô hình **ARXML**! Nếu sửa tay file C, lần build tiếp theo công cụ sinh mã sẽ ghi đè toàn bộ, làm biến mất các sửa đổi của bạn.
* 🧠 **Vì sao dễ nhầm:** Thói quen lập trình Bare-metal / Arduino sửa trực tiếp vào file C.
* 🔧 **Hậu quả Production:** Mất sạch mã nguồn cấu hình khi tích hợp CI/CD tự động, gây sai lệch cấu hình ngắt trên các ECU xuất xưởng.

---

<a name="ch12"></a>
## CHƯƠNG 12: SO SÁNH KIẾN TRÚC NGẮT CÁC DÒNG CHIP Ô TÔ PHỔ BIẾN TRONG AUTOSAR

Trong ngành công nghiệp ô tô, kiến trúc xử lý ngắt và cấu trúc bảng Vector Table có sự khác biệt sâu sắc giữa các họ vi điều khiển chuyên dụng:

| Đặc Tính Kỹ Thuật | ARM Cortex-M (M3/M4/M7/M33) | Infineon AURIX TriCore (TC2xx/TC3xx/TC4xx) | Renesas RH850 (G3M/G3K/G4MH) | ARM Cortex-A (AUTOSAR Adaptive) |
|---|---|---|---|---|
| **Vị Trí Sử Dụng Trong Xe** | Body Controller (BCM), Gateway, BMS, Thermal Management, VCU. | Hệ truyền động (Powertrain), Inverter động cơ điện, Phanh điện tử ESP, ADAS Radar. | Trợ lực lái (EPS), Đồng hồ taplo (Cluster), Body Domain Controller (BCM). | Bộ tính toán hiệu năng cao (HPC), Buồng lái thông minh (Cockpit IVI), Autonomous Driving. |
| **Cơ Chế Bảng Vector** | **Mảng con trỏ hàm 32-bit (Array of Function Pointers)**. | **Bảng BIV (Base Interrupt Vector)** chứa các khối lệnh nhảy/thực thi cách nhau 32 bytes. | Thanh ghi **INTBP** trỏ bảng Direct Vector (16/32 bytes/entry) hoặc Table Reference. | Thanh ghi **VBAR_ELx** chứa 16 vector ngoại lệ cho 4 loại ngoại lệ ở 4 trạng thái EL. |
| **Bộ Điều Khiển Ngắt** | **NVIC** (Nested Vectored Interrupt Controller) tích hợp sâu trong Core. | **Interrupt Router (IR)** kết hợp các thanh ghi **SRC (Service Request Control)**. | **Interrupt Controller (INTC)** hỗ trợ 16 mức ưu tiên kênh và phân cấp EI/FE. | **GIC (Generic Interrupt Controller - GICv2/v3/v4)** nằm ngoài CPU Core. |
| **Lưu Ngữ Cảnh (Context Saving)** | **Phần cứng tự động (Hardware Auto-stacking 8 thanh ghi)** vào MSP/PSP (12 cycles). | **Tự động lưu vào Context Save Areas (CSA)** theo kiến trúc Lower/Upper Context. | Phần cứng lưu PC & PSW vào thanh ghi phụ (EIPC/FEPC); phần mềm lưu thanh ghi đa năng. | **Phần mềm (Software OS)** lưu thủ công toàn bộ thanh ghi vào Kernel Stack. |
| **Cấp Độ An Toàn ISO 26262** | Thường đạt tới ASIL-B / ASIL-C (ASIL-D nếu có Dual Core Lockstep). | **Chuẩn ASIL-D thuần túy** (Multi-Core Lockstep, MPU, Memory Protection chuyên sâu). | **Chuẩn ASIL-B đến ASIL-D** (Dual Core Lockstep, ECC Protection). | Thường chạy ASIL-B (cần phối hợp MCU Safety Co-processor để giám sát an toàn). |

---

### 12.2 Điểm Cần Lưu Ý Khi Porting AUTOSAR OS Giữa Các Dòng Vi Điều Khiển:
1. **Từ Cortex-M sang TriCore:** Cortex-M lưu ngữ cảnh vào ngăn xếp RAM tuần tự (Linear Stack), trong khi TriCore phân bổ ngữ cảnh thành các khối liên kết động gọi là **Context Save Area (CSA)**. Khi tràn CSA trên TriCore, CPU sẽ kích hoạt bẫy `Context Management Trap` thay vì HardFault như ARM.
2. **Từ Cortex-M sang RH850:** Trên RH850, bảng ngắt hỗ trợ 2 chế độ: Direct Vector (mã lệnh nhảy thực thi trực tiếp) và Table Reference (đọc con trỏ hàm). Kỹ sư BSW phải cấu hình đúng bit trong thanh ghi `INTCFG` để khớp với Linker Script.

---

<a name="ch13"></a>
## CHƯƠNG 13: VÒNG ĐỜI KHỞI TẠO HỆ THỐNG TỪ VECTOR TABLE ĐẾN AUTOSAR OS RUNTIME (`reset_handler` ──► `EcuM_Init` ──► `StartOS`)

Trong dự án `as`, toàn bộ vòng đời khởi động của một ECU từ khi có xung điện áp đầu tiên đến khi các Task ứng dụng chạy ổn định diễn ra qua **5 giai đoạn đồng bộ nghiêm ngặt**:

```
+===================================================================================================+
|                    CHUỖI KHỞI ĐỘNG ĐẦY ĐỦ CỦA ECU Ô TÔ TRONG DỰ ÁN AS                             |
+===================================================================================================+

[GIAI ĐOẠN 1: PHẦN CỨNG TRA CỨU BẢNG VECTOR TABLE BAN ĐẦU (0x00000000)]
   1. CPU Core đọc Entry [0] ➔ Nạp `knl_system_stack_top` (0x20007550) vào thanh ghi MSP.
   2. CPU Core đọc Entry [1] ➔ Nạp `reset_handler` (0x00000401) vào thanh ghi PC.
         │
         ▼
[GIAI ĐOẠN 2: THỰC THI ASSEMBLY STARTUP - startup.S: L316-L352]
   1. Đảm bảo MSP = `knl_system_stack_top`.
   2. Copy phân vùng `.data` từ Flash (`__etext`) sang RAM (`__data_start__` ➔ `__data_end__`).
   3. Xóa phân vùng `.bss` trong RAM về 0 (`__bss_start__` ➔ `__bss_end__`).
   4. Thực thi lệnh rẽ nhánh: `bl main`.
         │
         ▼
[GIAI ĐOẠN 3: ECU STATE MANAGER KHỞI TẠO MCAL BSW - release/ascore/app/main.c]
   Hàm `main()` được gọi và kích hoạt cỗ máy trạng thái ECU:
   1. `EcuM_Init()` bắt đầu chạy.
   2. Gọi `Mcu_Init(&Mcu_Config)` ➔ Thiết lập bộ nhân tần số PLL, phân phối Clock cho các Bus ngoại vi.
   3. Gọi `Port_Init(&Port_Config)` ➔ Cấu hình các chân GPIO (Chân CAN TX/RX, Pin điều khiển Relay).
   4. Gọi `Can_Init(&Can_Config)` ➔ Cấu hình bộ điều khiển mạng CAN (Bit timing, Mailboxes, Filter).
   5. Bật ngắt ngoại vi trong thanh ghi NVIC (`NVIC_EnableIRQ(CAN_IRQn)`).
         │
         ▼
[GIAI ĐOẠN 4: KÍCH HOẠT HỆ ĐIỀU HÀNH AUTOSAR OS - StartOS()]
   1. `EcuM` gọi hàm `StartOS(OSDEFAULTAPPMODE)`.
   2. Hệ điều hành `askar` khởi tạo bảng Task TCB, Resource, Counter và gán Task đầu tiên vào READY.
   3. Phát lệnh phần mềm `SVC #0` ➔ Kích hoạt Entry [11] trong Vector Table (`knl_start_dispatch`).
   4. `knl_start_dispatch` nạp con trỏ Stack của Task đầu tiên và chuyển CPU sang Thread Mode!
         │
         ▼
[GIAI ĐOẠN 5: BẬT NHỊP ĐỊNH THỜI SYSTICK & CHẠY APPLICATION TASKS]
   1. Kích hoạt ngắt định kỳ 1ms SysTick (`knl_system_tick` tại Entry [15]).
   2. BSW Scheduler (`SchM`) bắt đầu điều phối các hàm chu kỳ:
      - `Can_MainFunction_Write()` / `Can_MainFunction_Read()` (Chu kỳ 5ms/10ms).
      - `Com_MainFunction_Rx()` / `Com_MainFunction_Tx()` (Chu kỳ 10ms).
      - `CanSM_MainFunction()` (Chu kỳ 20ms).
   3. Hệ thống ECU ô tô chính thức bước vào trạng thái vận hành ổn định (`RUN State`)!
+===================================================================================================+
```

<a name="ch14"></a>
## CHƯƠNG 14: NGUYÊN TẮC THIẾT KẾ NGẮT CHUẨN MỰC TRONG AUTOSAR BSW & MCAL DRIVERS

### 14.1 Triết Lý Phân Tầng Xử Lý Ngắt Trong AUTOSAR BSW

Trong kiến trúc AUTOSAR, tầng MCAL Driver và BSW tuân thủ nghiêm ngặt nguyên tắc **phân chia trách nhiệm hai nửa (Top-Half / Bottom-Half)** để bảo vệ tính thời gian thực của xe:

```
[TOP-HALF: MCAL ISR (HANDLER MODE - FAST EXECUTION)]
• Mã nguồn: `Can_RxIsr()` trong `as/com/as.infrastructure/arch/stm32f1/mcal/Can.c`
• Thời gian thực thi: < 5 micro giây.
• Nhiệm vụ bắt buộc:
  1. Đọc thanh ghi phần cứng (CAN_FIFO0 mailbox).
  2. Xóa cờ ngắt phần cứng (`CAN_ClearITPendingBit`).
  3. Đẩy dữ liệu thô vào Buffer của tầng Interface: `CanIf_RxIndication()`.
  4. Đánh thức Task xử lý: `SetEvent(Task_Communication, EVENT_CAN_RX)`.
  5. Thoát ngắt ngay lập tức!
       │
       ▼ (Chuyển giao điều phối qua ExitISR & PendSV)
[BOTTOM-HALF: AUTOSAR OS TASK (THREAD MODE - DEFERRED PROCESSING)]
• Mã nguồn: `TASK(Task_Communication)` hoặc `Com_MainFunction_Rx()`
• Thời gian thực thi: 1 mili-giây đến 10 mili-giây.
• Nhiệm vụ xử lý nghiệp vụ:
  1. Tầng PDU Router: `PduR_CanIfRxIndication()`.
  2. Tầng COM: `Com_RxIndication()` bóc tách các Signal (Tín hiệu chân ga, tốc độ xe, nhiệt độ pin).
  3. Chuyển tín hiệu qua RTE (Runtime Environment) tới các Software Component (SWC).
```

#### 🚫 5 Điều Tuyệt Đối CẤM Làm Trong MCAL ISR:
1. **Tuyệt đối cấm vòng lặp chờ (Busy-Wait Loop / Polling):** Không chờ ngoại vi phản hồi trong ISR.
2. **Tuyệt đối cấm gọi các OS API gây chặn (`WaitEvent()`, `TerminateTask()`):** Làm sập bộ lập lịch của AUTOSAR OS.
3. **Tuyệt đối cấm cấp phát bộ nhớ động (`malloc`, `free`):** Gây phân mảnh RAM và thời gian thực thi bất định (Non-deterministic timing).
4. **Tuyệt đối cấm giải mã tín hiệu phức tạp (DBC Signal Unpack) trong ISR:** Đẩy toàn bộ việc giải mã cho hàm `Com_MainFunction_Rx()`.
5. **Tuyệt đối cấm in Log blocking qua UART (`printf`):** Gây trễ hàng mili-giây, dẫn đến mất frame CAN tiếp theo.

---

### 14.2 Cơ Chế Bộ Đệm Vòng Khóa Không Chờ (Lock-Free RingBuffer) Trong Dự Án `as`

Tại [`as/com/as.infrastructure/clib/cirq_buffer.c`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/com/as.infrastructure/clib/cirq_buffer.c), dự án `as` hiện thực cấu trúc hàng đợi vòng tròn an toàn tuyệt đối cho luồng 1-Producer (MCAL ISR) và 1-Consumer (AUTOSAR Task) mà **KHÔNG CẦN KHÓA NGẮT CRITICAL SECTION**:

```c
#define CIRQ_BUFFER_SIZE  256  /* Kích thước là lũy thừa của 2 */
#define CIRQ_BUFFER_MASK  (CIRQ_BUFFER_SIZE - 1)

typedef struct {
    uint8_t  data[CIRQ_BUFFER_SIZE];
    volatile uint32_t head;  /* Chỉ ghi bởi Producer (MCAL ISR) */
    volatile uint32_t tail;  /* Chỉ ghi bởi Consumer (AUTOSAR Task) */
} CirqBuffer_t;

/* Ghi dữ liệu trong MCAL ISR (Producer) */
int CirqBuffer_Push(CirqBuffer_t *rb, uint8_t byte) {
    uint32_t next_head = (rb->head + 1) & CIRQ_BUFFER_MASK;
    if (next_head == rb->tail) {
        return -1; /* Bộ đệm đầy (Buffer Overflow) */
    }
    rb->data[rb->head] = byte;
    __DMB();       /* Data Memory Barrier: Đảm bảo dữ liệu đã vào RAM trước khi tăng index */
    rb->head = next_head;
    return 0;
}

/* Đọc dữ liệu trong AUTOSAR Task (Consumer) */
int CirqBuffer_Pop(CirqBuffer_t *rb, uint8_t *pByte) {
    if (rb->head == rb->tail) {
        return -1; /* Bộ đệm rỗng */
    }
    *pByte = rb->data[rb->tail];
    __DMB();
    rb->tail = (rb->tail + 1) & CIRQ_BUFFER_MASK;
    return 0;
}
```

---

<a name="ch15"></a>
## CHƯƠNG 15: PHÂN TÍCH HIỆU NĂNG & HỆ THỐNG REAL-TIME TRONG ECU Ô TÔ

### 15.1 Các Chỉ Số Đo Lường Thời Gian Thực (Timing Metrics)

```
                       THỜI GIAN ĐÁP ỨNG TOÀN DIỆN (TOTAL RESPONSE TIME)
│◄───────────────────────────────────────────────────────────────────────────────────►│
│                                                                                     │
├─────────────────┼───────────────────────────┼───────────────────┼───────────────────┤
│ Interrupt       │ ISR Execution Time        │ Context Switch    │ Task Execution    │
│ Latency         │ (Thời gian chạy ISR)      │ Latency           │ Time (Xử lý Task) │
│ (Độ trễ ngắt)   │                           │ (Đổi ngữ cảnh)    │                   │
└─────────────────┴───────────────────────────┴───────────────────┴───────────────────┘
▲                 ▲                           ▲                   ▲
│                 │                           │                   │
Event Xảy Ra      Bắt Đầu Lệnh Đầu ISR        Bắt Đầu PendSV      Task Bắt Đầu Chạy
```

1. **Interrupt Latency (Độ trễ ngắt):** Khoảng thời gian từ khi tín hiệu điện áp IRQ được kích hoạt vật lý đến khi lệnh đầu tiên trong hàm ISR được thực thi. Trên Cortex-M4 chạy ở 168 MHz: $12 	ext{ cycles} pprox 71.4 	ext{ ns}$.
2. **Interrupt Jitter (Độ trôi ngắt):** Sự biến thiên sai lệch của độ trễ ngắt giữa các lần ngắt khác nhau (do ảnh hưởng của pipeline, flash wait states, cache miss, hoặc lệnh atomic).
3. **WCET (Worst-Case Execution Time):** Thời gian thực thi trong tình huống xấu nhất của hàm ngắt. Đây là tham số bắt buộc phải chứng minh trong chứng chỉ an toàn chức năng ô tô ISO 26262 (ASIL-D).

---

### 15.2 Bài Toán Thiết Kế Ngân Sách Tải CPU Cho Hộp Điều Khiển Động Cơ Xe Điện (VCU)

#### 🚗 Đề bài: Thiết kế hệ thống nhúng VCU chạy trên MCU 168 MHz:
- **Ngắt 1 (PWM Motor Inverter):** Tần số **20 kHz** (Chu kỳ 50 µs) ➔ Cấu hình **ISR Category 1** (Thời gian xử lý: 2 µs).
- **Ngắt 2 (CAN FD Bus 500 kbps / 2 Mbps):** Tần số ngắt trung bình **5 kHz** ➔ Cấu hình **ISR Category 2** (`Can_RxIsr` tốn 3 µs).
- **Ngắt 3 (SysTick định thời OS):** Tần số **1 kHz** (Chu kỳ 1 ms) ➔ `knl_system_tick` tốn 1.5 µs.

```
TÍNH TOÁN NGÂN SÁCH TẢI CPU (CPU LOAD BUDGET):

1. Tải trọng ISR Category 1 (PWM):
   Load = 2 µs / 50 µs = 4.00% CPU
2. Tải trọng ISR Category 2 (CAN FD):
   Load = 3 µs × 5000 = 1.50% CPU
3. Tải trọng Nhịp OS SysTick:
   Load = 1.5 µs / 1000 µs = 0.15% CPU

===> TỔNG TẢI TRỌNG PHỤC VỤ NGẮT: 5.65% CPU!
===> DÀNH 94.35% NĂNG LỰC CPU CHO: Thuật toán điều khiển FOC, BSW ComStack, Chẩn đoán UDS và Quản lý năng lượng!
```

---

<a name="ch16"></a>
## CHƯƠNG 16: 10 BÀI TẬP THỰC CHIẾN TĂNG DẦN ĐỘ KHÓ TRÊN DỰ ÁN AS

> [!IMPORTANT]
> **Hướng Dẫn:** Các bài tập dưới đây bám sát kiến trúc mã nguồn của dự án `as`. Bạn hãy tự tay debug trên QEMU (`lm3s6965evb`), đọc file `.map`, phân tích thanh ghi và viết code bổ sung vào dự án để rèn luyện kỹ năng BSW Integration.

---

### 🟢 Level 1: Khám Phá Bảng Vector Table Thực Tế Của Dự Án `as` Qua GDB
* **Problem:** Khởi động mô phỏng QEMU: `make -C as/build/nt/lm3s6965evb/ascore run` và kết nối GDB.
* **Expected Behavior:** Đọc 16 phần tử đầu tiên tại `0x00000000`. So sánh giá trị đọc được với file `lm3s6965evb.map` để xác nhận địa chỉ của `knl_system_stack_top`, `reset_handler`, `knl_start_dispatch` và `knl_isr_process`.

---

### 🟢 Level 2: Truy Vết Chuỗi Khởi Động `reset_handler` Trong `startup.S`
* **Problem:** Đặt Hardware Breakpoint tại `reset_handler` trong GDB.
* **Expected Behavior:** Step từng bước (lệnh `si`) qua vòng lặp `LoopCopyDataInit` và `LoopFillZerobss`. Kiểm tra giá trị các biến toàn cục trong RAM tại `0x20000000` trước và sau khi copy.

---

### 🟡 Level 3: Bắt Lỗi Ngắt Rác Bằng `ShutdownOS(0xFF)` Trong `portable.c`
* **Problem:** Trong file `portable.c: L118`, khi ngắt xảy ra mà không nằm trong dải `tisr_pc[]`, hệ điều hành gọi `ShutdownOS(0xFF)`.
* **Expected Behavior:** Giả lập kích hoạt một IRQ chưa cấu hình trong ARXML. Đọc giá trị thanh ghi `IPSR` tại `ShutdownOS` để xác định chính xác số hiệu ngắt vi phạm.

---

### 🟡 Level 4: Tái Định Vị Vector Table VTOR Sang SRAM Trong Dự Án `as`
* **Problem:** Sau khi `ascore` boot, hãy copy 1024 bytes của `__vector_table` từ Flash lên đầu SRAM và ghi địa chỉ mới vào `SCB->VTOR`.
* **Expected Behavior:** Thay đổi con trỏ ngắt SysTick trong SRAM để trỏ sang một hàm đo đạc hiệu năng mà không cần nạp lại Flash.

---

### 🟡 Level 5: Bóc Tách Khung Ngữ Cảnh Khi Bị `HardFault` Trong Nhân `askar`
* **Problem:** Cố tình tạo lỗi chia cho 0 hoặc truy cập con trỏ NULL trong một Task của AUTOSAR OS.
* **Expected Behavior:** Viết đoạn code bóc tách khung Stack `MSP`/`PSP` trong `hard_fault_handler`, đọc `SCB->CFSR` để tìm ra đúng dòng code C gây ra sự cố.

---

### 🟠 Level 6: Kiểm Tra Cơ Chế Chuyển Giao Quyền Từ `asboot` Sang `ascore`
* **Problem:** Phân tích quy trình nhảy của Bootloader tại [`bl_core.c`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/com/as.infrastructure/boot/common/bl_core.c).
* **Expected Behavior:** Dùng GDB xác nhận rằng trước khi nhảy vào `ascore`, thanh ghi `SCB->VTOR` đã được gán bằng địa chỉ App và `MSP` đã được cập nhật từ Entry [0] của App.

---

### 🟠 Level 7: Tích Hợp Lock-Free RingBuffer Cho Driver Truyền Thông MCAL
* **Problem:** Tích hợp module [`cirq_buffer.c`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/com/as.infrastructure/clib/cirq_buffer.c) vào hàm ngắt `Can_RxIsr`.
* **Expected Behavior:** Đảm bảo khi các frame CAN gửi liên tục ở chu kỳ 100 µs, không có frame nào bị mất dữ liệu và không cần dùng `SuspendAllInterrupts()`.

---

### 🔴 Level 8: Phân Tích & Sửa Lỗi Nghẽn Lập Lịch AUTOSAR OS Do Ngắt CAN Dồn Dập
* **Problem:** Khi CAN Bus bị nghẽn (Bus Load 90%), Task chẩn đoán UDS (`Dcm`) bị chậm trễ không phản hồi kịp thời gian P2Server.
* **Expected Behavior:** Tối ưu hóa lại `Can_RxIsr` và chu trình `ExitISR` để Task có độ ưu tiên cao được cướp quyền ngay khi bản tin UDS đến.

---

### 🔴 Level 9: Thiết Kế Ma Trận Phân Bổ Mức Ưu Tiên Ngắt Chuẩn AUTOSAR Cho ECU Xe Điện
* **Problem:** Thiết lập phân bổ Priority trong NVIC cho hệ thống điều khiển VCU:
  - Ngắt bảo vệ quá dòng động cơ (ISR Category 1 - Zero Latency).
  - Ngắt nhận CAN FD khẩn cấp (ISR Category 2 - Priority cao).
  - Ngắt nhịp định thời `SysTick` 1ms (`knl_system_tick`).
  - Ngắt truyền thông UART / Lin.
* **Expected Behavior:** Chứng minh các ngắt ISR Cat 1 không bao giờ bị ảnh hưởng khi BSW gọi `SuspendOSInterrupts()`.

---

### 🔴 Level 10: Điều Tra Lỗi Tràn Ngăn Xếp Hệ Thống `knl_system_stack` Do Ngắt Lồng Nhau
* **Problem:** Trong file `linker-app.lds`, `knl_system_stack_size = 1024` bytes. Khi chạy thử nghiệm xe ngoài hiện trường, thỉnh thoảng hệ thống bị Reset ngẫu nhiên do HardFault.
* **Expected Behavior:** Sử dụng kỹ thuật Stack Painting (Điền mẫu `0xA5A5A5A5`) để đo độ sâu ngăn xếp tối đa khi nhiều ngắt lồng nhau xảy ra đồng thời.

---

<a name="ch17"></a>
## CHƯƠNG 17: SENIOR AUTOMOTIVE MINDSET — THẤU HIỂU BẢN CHẤT TỪ PHẦN CỨNG ĐẾN BSW

### 10 Cặp Tư Duy Đối Nghịch Giữa Junior và Senior Trong Dự Án AUTOSAR:

| # | Chủ Đề | Tư Duy Junior (Bề Nổi / Sách Vở) | Tư Duy Senior Architect (Kỹ Nghệ Ô Tô) |
|---|---|---|---|
| 1 | **Vector Table** | "Là danh sách các hàm ngắt trong file startup." | "Là giao diện phần cứng kết nối giữa không gian nhớ và nhân CPU. Trong AUTOSAR, nó liên kết trực tiếp với Linker Script và chuyển tiếp vào hàm bọc `knl_isr_process` của OS." |
| 2 | **NVIC** | "Là hàm bật tắt ngắt trong thư viện HAL." | "Là bộ điều phối phần cứng đa tầng trong lõi CPU, quyết định thứ tự cướp quyền phần cứng trước khi chuyển giao cho bộ lập lịch phần mềm của AUTOSAR OS." |
| 3 | **Hàm ISR** | "Là hàm C thực thi toàn bộ logic nhận dữ liệu." | "Chỉ là tầng Top-Half cực nhanh: Đọc phần cứng, xóa cờ, đưa PDU vào hàng đợi và kích hoạt Task Bottom-Half xử lý qua `ExitISR`." |
| 4 | **Bật Ngắt** | "Chỉ cần gọi hàm Enable ngắt là xong." | "Là một chuỗi liên hoàn 7 mắt xích: Clock ➔ Pin Mux ➔ Ngoại vi ➔ Cờ ngoại vi ➔ Priority ➔ Kênh NVIC ➔ Mở cờ ngắt toàn cục." |
| 5 | **Priority** | "Số lớn là ưu tiên cao." | "Hiểu rõ sự đối lập: ARM NVIC số nhỏ ưu tiên cao, trong khi AUTOSAR OS Task số lớn là ưu tiên cao. Không bao giờ được nhầm lẫn!" |
| 6 | **AUTOSAR OS & ISR** | "Gọi API nào cũng được trong hàm ngắt." | "Phân định nghiêm ngặt: ISR Cat 1 cấm tuyệt đối OS API; ISR Cat 2 chỉ được gọi `SetEvent`, `ActivateTask` và cấm `WaitEvent`." |
| 7 | **HardFault** | "Lỗi khó hiểu, reset chip cho xong." | "Là công cụ chẩn đoán giá trị nhất của CPU. Bóc tách khung Auto-stacking, đọc CFSR/BFAR để tìm chính xác dòng code và nguyên nhân gây lỗi." |
| 8 | **Độ Trễ Ngắt** | "Ngắt là chạy tức thời, không có độ trễ." | "Độ trễ là hàm số xác định: 12 chu kỳ auto-stacking + thời gian `EnterISR` + độ sâu ngắt lồng nhau + thời gian khóa `SuspendOSInterrupts`." |
| 9 | **Bootloader Jump** | "Chỉ cần ép kiểu con trỏ hàm rồi nhảy." | "Là một quy trình bàn giao quyền nghiêm ngặt: Tắt ngoại vi cũ, tắt NVIC, dừng SysTick, nạp MSP mới từ Entry [0] của App, và cấu hình VTOR." |
| 10 | **Cấu Hình ISR** | "Sửa trực tiếp tên hàm trong file `*_Cfg.c`." | "Tuyệt đối cấm sửa file phát sinh mã! Mọi cấu hình ngắt phải được khai báo chuẩn xác trong mô hình ARXML qua công cụ cấu hình BSW." |

---

<a name="ch18"></a>
## CHƯƠNG 18: MASTER DEBUG CHECKLIST CHO KỸ SƯ AUTOSAR & TÀI LIỆU THAM KHẢO

### 18.1 Master Checklist 20 Bước Chẩn Đoán Ngắt Chuyên Nghiệp Trong AUTOSAR ECU

```
[GIAI ĐOẠN 1: THIẾT KẾ & LIÊN KẾT (BUILD TIME)]
 [ ] 1. Mảng `.isr_vector` có lệnh `KEEP()` trong Linker Script chưa?
 [ ] 2. Địa chỉ ORIGIN của Flash trong Linker Script có khớp với không gian nhớ phần cứng không?
 [ ] 3. Tên hàm ISR trong tệp MCAL Driver có khớp 100% với tên khai báo trong bảng cấu hình `tisr_pc[]` không?
 [ ] 4. Nếu dùng C++, hàm ISR đã được bọc trong khối `extern "C"` chưa?
 [ ] 5. Các biến chia sẻ giữa ISR và OS Task đã có từ khóa `volatile` và rào cản `__DMB()` chưa?

[GIAI ĐOẠN 2: KHỞI TẠO HỆ THỐNG (RUNTIME INITIALIZATION)]
 [ ] 6. Bus Clock của ngoại vi (CAN, ADC, Timer) đã được kích hoạt trong `Mcu_Init()` chưa?
 [ ] 7. Các chân GPIO Alternate Function đã được cấu hình đúng Mode trong `Port_Init()` chưa?
 [ ] 8. Cờ ngắt nội bộ ngoại vi (ví dụ `CAN_IT_FMP0` trong `Can.c`) đã bật chưa?
 [ ] 9. Kênh ngắt trong NVIC (`NVIC->ISER`) đã được Enable chưa?
 [ ] 10. Mức ưu tiên ngắt trong NVIC (`NVIC->IPR`) đã được thiết lập đúng chưa?
 [ ] 11. Thanh ghi `SCB->VTOR` đã trỏ đúng vào địa chỉ của bảng Vector Table hiện tại chưa?
 [ ] 12. Cờ ngắt toàn cục đã được mở (`Irq_Enable()`, PRIMASK = 0) chưa?

[GIAI ĐOẠN 3: THỰC THI HÀM ISR (IN-FLIGHT EXECUTION)]
 [ ] 13. Hàm ISR đã có lệnh xóa cờ ngắt phần cứng của ngoại vi (`CAN_ClearITPendingBit`) chưa?
 [ ] 14. Có lệnh đọc lại thanh ghi hoặc `__DSB()` để khắc phục độ trễ Write Buffer của Bus không?
 [ ] 15. Trong AUTOSAR OS, các hàm gọi trong ISR Cat 2 có vi phạm danh mục cấm (`WaitEvent`, `TerminateTask`) không?
 [ ] 16. Hàm `ExitISR` trong `portableS.S` đã kiểm tra cờ `ISR2Counter == 0` trước khi gọi `Sched_Preempt()` chưa?
 [ ] 17. Mức ưu tiên ngắt phần cứng của ISR Cat 2 có nằm dưới ngưỡng của `SuspendOSInterrupts()` không?

[GIAI ĐOẠN 4: CHẨN ĐOÁN SỰ CỐ & CRASH (FAULT RECOVERY)]
 [ ] 18. Khi rơi vào `ShutdownOS(0xFF)`, đã đọc thanh ghi `IPSR` để xác định Exception Number chưa?
 [ ] 19. Khi rơi vào `HardFault`, đã trích xuất địa chỉ câu lệnh lỗi (Stacked PC) và đọc `SCB->CFSR` chưa?
 [ ] 20. Dung lượng `knl_system_stack` (1024 bytes) có đủ lớn để chứa các khung ngắt lồng nhau (Nested Stacking) không?
```

---

### 18.2 Sơ Đồ Khái Niệm Tổng Thể Trong Hệ Thống AUTOSAR (Master Mental Model)

```
+==================================================================================================+
|                  SƠ ĐỒ TỔNG QUAN KIẾN TRÚC XỬ LÝ NGẮT AUTOSAR TRONG DỰ ÁN AS                     |
+==================================================================================================+
                                                                                                    
   [NGOẠI VI Ô TÔ PHẦN CỨNG] ──────(Kéo tín hiệu điện áp IRQ Line)───┐                             
   (CAN Controller, FlexRay, ADC)                                    │                             
                                                                     ▼                             
                                            +──────────────────────────────────+                   
                                            |    NVIC (INTERRUPT CONTROLLER)   |                   
                                            | • Lọc kênh ngắt: NVIC->ISER      |                   
                                            | • Phân xử mức ưu tiên: NVIC->IPR |                   
                                            | • Quản lý Pending / Active       |                   
                                            +──────────────────────────────────+                   
                                                                     │                             
                                                (Gửi Exception Number & nIRQ)                      
                                                                     │                             
                                                                     ▼                             
                                            +──────────────────────────────────+                   
                                            |      LÕI CPU (ARM CORTEX-M)      |                   
                                            | • Kết thúc câu lệnh hiện tại     |                   
                                            | • Auto-stacking 8 thanh ghi      |                   
                                            | • Tra cứu SCB->VTOR              |                   
                                            +──────────────────────────────────+                   
                                                                     │                             
                                          (Đọc con trỏ từ Flash __vector_table)                    
                                                                     │                             
                                                                     ▼                             
                                            +──────────────────────────────────+                   
                                            | BẢNG VECTOR TABLE TRONG FLASH    |                   
                                            | [0] knl_system_stack_top         |                   
                                            | [1] reset_handler                |                   
                                            | [16+] .word knl_isr_process      |                   
                                            +──────────────────────────────────+                   
                                                                     │                             
                                                      (Nhảy vào Assembly OS Wrapper)               
                                                                     │                             
                                                                     ▼                             
                                            +──────────────────────────────────+                   
                                            |  TẦNG WRAPPER OS (portableS.S)   |                   
                                            | • EnterISR: ISR2Counter++        |                   
                                            | • Đọc IPSR -> intno              |                   
                                            | • Gọi knl_isr_handler(intno)     |                   
                                            +──────────────────────────────────+                   
                                                                     │                             
                                                       (Tra bảng tisr_pc[intno-16])                
                                                                     │                             
                                                                     ▼                             
                                            +──────────────────────────────────+                   
                                            |   MCAL DRIVER ISR (Can_RxIsr)    |                   
                                            | • Xóa cờ ngắt phần cứng          |                   
                                            | • Gọi CanIf_RxIndication()       |                   
                                            | • SetEvent(Task_Com, EVENT_RX)   |                   
                                            +──────────────────────────────────+                   
                                                                     │                             
                                                        (Quay lại ExitISR)                         
                                                                     │                             
                                                                     ▼                             
                                            +──────────────────────────────────+                   
                                            |    THOÁT NGẮT VÀ CƯỚP QUYỀN      |                   
                                            | • ISR2Counter--                  |                   
                                            | • Sched_Preempt() -> PendSV      |                   
                                            | • Kích hoạt Task có Prio cao hơn |                   
                                            +──────────────────────────────────+                   
+==================================================================================================+
```

---

### 18.3 Tài Liệu Tham Khảo Kỹ Thuật Chính Thức

1. **AUTOSAR Consortium:** *Specification of Operating System (AUTOSAR SWS OS, Classic Platform Release 4.4.0)*.
2. **AUTOSAR Consortium:** *Specification of CAN Driver (AUTOSAR SWS CAN Driver, Release 4.4.0)*.
3. **ARM Limited:** *ARMv7-M Architecture Reference Manual* (DDI 0403E.e).
4. **ARM Limited:** *Cortex-M3 / Cortex-M4 Technical Reference Manual*.
5. **Joseph Yiu:** *The Definitive Guide to ARM Cortex-M3 and Cortex-M4 Processors* (Newnes).
6. **ISO 26262-6:** *Road vehicles — Functional safety — Part 6: Product development at the software level*.
7. **ISO 14229-1:** *Road vehicles — Unified diagnostic services (UDS) — Part 1: Application layer*.

---

*Tài liệu kỹ thuật chuyên sâu này được biên soạn độc quyền cho mục đích nghiên cứu, đào tạo và phát triển hệ thống phần mềm ô tô AUTOSAR BSW. Toàn bộ mã nguồn thực nghiệm được kiểm chứng 100% trên dự án Study_AUTOSAR (`as`).*
