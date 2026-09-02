# 🔌 INTERRUPT VECTOR TABLE — TỪ JUNIOR+ ĐẾN SENIOR EMBEDDED ENGINEER

> **Tác giả:** Senior Embedded Systems Engineer / Firmware Architect  
> **Cấp độ:** Junior+ → Senior Embedded  
> **Hướng tiếp cận:** Engineering thực tế: WHY → WHAT → HOW → HARDWARE → CODE → MEMORY → DEBUG → PRODUCTION  
> **Nền tảng:** ARM Cortex-M + Bare-metal + FreeRTOS

---

## 📑 MỤC LỤC

1. [Chương 1: Mental Model — Cái Nhìn Toàn Cảnh Về Interrupt & Vector Table](#ch1)
2. [Chương 2: Interrupt Vector Table Ở Cấp Memory](#ch2)
3. [Chương 3: ARM Cortex-M Deep Dive](#ch3)
4. [Chương 4: Code Thực Tế — Startup + Linker Script + ISR](#ch4)
5. [Chương 5: Interrupt Flow Ở Cấp CPU Core](#ch5)
6. [Chương 6: Interrupt Priority, Preemption & Sub-Priority](#ch6)
7. [Chương 7: Interrupt & RTOS (FreeRTOS Architecture)](#ch7)
8. [Chương 8: Bootloader & Multi-Image Architecture](#ch8)
9. [Chương 9: Debugging Vector Table — 5 Case Study Thực Tế](#ch9)
10. [Chương 10: Quy Trình Debug Chuyên Sâu Với GDB](#ch10)
11. [Chương 11: 15+ Sai Lầm Phổ Biến (Misconceptions) Của Junior](#ch11)
12. [Chương 12: So Sánh Kiến Trúc CPU (Cortex-M vs Cortex-A vs RISC-V vs x86)](#ch12)
13. [Chương 13: Phân Tích Toàn Diện Startup Code Thực Tế](#ch13)
14. [Chương 14: Thiết Kế Interrupt Handling Chuẩn Senior](#ch14)
15. [Chương 15: Phân Tích Hiệu Năng & Hệ Thống Real-Time](#ch15)
16. [Chương 16: 10 Bài Tập Thực Chiến Tăng Dần Độ Khó (Level 1 → 10)](#ch16)
17. [Chương 17: Senior Mindset — Thấu Hiểu Bản Chất Thay Vì Học Thuộc](#ch17)
18. [Chương 18: Master Debug Checklist & Tài Liệu Tham Khảo](#ch18)

---

<a name="ch1"></a>
## CHƯƠNG 1: MENTAL MODEL — CÁI NHÌN TOÀN CẢNH

### 1.1 Interrupt Là Gì Ở Cấp Độ Hardware?

#### 🎯 WHY — Tại Sao Cơ Chế Interrupt Tồn Tại?
CPU là một cỗ máy xử lý tuần tự (sequential machine) — nó chỉ có thể thực thi từng lệnh một tại một thời điểm. Tuy nhiên, thế giới vật lý bên ngoài (các ngoại vi peripherals, cảm biến sensors, bus truyền thông mạng) lại xảy ra hoàn toàn bất đồng bộ (asynchronously):
- Một byte dữ liệu UART 115200 baud bay đến thanh ghi RX mỗi **86.8 micro giây**.
- CPU đang thực hiện thuật toán tính toán ma trận hoặc giải mã tốn **1 mili giây**.
- Nếu CPU liên tục đọc thăm dò thanh ghi UART (polling / busy-waiting), 99% tài nguyên tính toán bị lãng phí.
- Nguy hiểm hơn: nếu CPU bận xử lý tác vụ khác quá 86.8 µs, byte dữ liệu tiếp theo sẽ ghi đè và làm mất dữ liệu (Overrun Error).

#### 💡 GIẢI PHÁP: CƠ CHẾ NGẮT PHẦN CỨNG (HARDWARE INTERRUPT)
Hardware Interrupt là một đường dây vật lý (physical trace/wire) nối từ ngoại vi (Peripheral) đến bộ điều khiển ngắt (Interrupt Controller) và CPU core. Khi có sự kiện:
1. Ngoại vi kéo đường tín hiệu ngắt (IRQ line) lên mức tích cực (Active High/Low).
2. CPU tạm dừng luồng thực thi chính một cách an toàn.
3. CPU chuyển ngữ cảnh sang thực thi chương trình con phục vụ ngắt (**ISR — Interrupt Service Routine**).
4. Sau khi ISR xử lý xong, CPU khôi phục lại trạng thái ban đầu và tiếp tục chạy chương trình chính như chưa hề có sự gián đoạn.

```
+------------------+        +------------------+        +------------------+
|   PERIPHERAL     |        |    INTERRUPT      |        |      CPU         |
|                  |        |   CONTROLLER      |        |                  |
|  UART RX buffer  |------->|     (NVIC)        |------->|  Đang xử lý      |
|  Timer overflow  |  IRQ   |                   |  nIRQ  |  main thread     |
|  ADC conversion  | (Line) |  - Priority Mgmt  | (Core) |                  |
|  GPIO edge       |        |  - Masking/Enable |        |  TẠM DỪNG        |
+------------------+        +------------------+        |  Nhảy vào ISR    |
                                                         +------------------+
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
| **Hệ điều hành RTOS chuyển Task** | Khi hết lượt chạy (SysTick) hoặc có Task ưu tiên cao hơn thức dậy. | **Entry [14] (PendSV)**<br>& **Entry [15] (SysTick)** | CPU đọc Entry [14]/[15] để chạy mã nguồn đổi ngữ cảnh (Context Switching) của FreeRTOS / AUTOSAR OS. |
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
* **Bản chất:** Là một giá trị địa chỉ vùng nhớ RAM (thường là địa chỉ cuối cùng của SRAM, ví dụ `0x20020000`).
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
* Tạo ngắt định kỳ (thường là 1 ms = 1000 Hz) để làm nguồn nhịp (Timebase Tick) cho hệ điều hành FreeRTOS / AUTOSAR OS.

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

### 3.5 Câu Hỏi Kiểm Tra Tư Duy — Chương 3

1. **Câu 1:** Nếu trong thanh ghi `NVIC->ISER` đã set bit Enable cho `TIM2_IRQn`, nhưng trong mảng Vector Table tại ô nhớ tương ứng với TIM2 lại chứa giá trị `0x00000000` (NULL). Chuyện gì sẽ xảy ra chính xác khi bộ đếm Timer đếm tràn?
2. **Câu 2:** Tại sao các hệ điều hành FreeRTOS và AUTOSAR OS đều bắt buộc phải gán độ ưu tiên của ngắt `PendSV` ở mức thấp nhất trong toàn bộ hệ thống? Nếu gán PendSV mức ưu tiên cao hơn ngắt UART RX thì hậu quả nghiêm trọng nào sẽ xảy ra?
3. **Câu 3:** Cả `SVC` và `PendSV` đều là các cơ chế kích hoạt ngắt bằng phần mềm (Software Exception). Tại sao hệ điều hành cần phân tách thành 2 loại ngắt này mà không dùng chung một loại?

---

<a name="ch4"></a>
## CHƯƠNG 4: CODE THỰC TẾ — STARTUP + LINKER SCRIPT + ISR

### 4.1 Khai Báo Vector Table Chuẩn Bằng Ngôn Ngữ C

Dưới đây là mã nguồn C chuẩn công nghiệp để định nghĩa bảng Vector Table cho ARM Cortex-M4 (STM32F4):

```c
/* =========================================================================
 * File: startup_stm32f407xx.c
 * Định nghĩa bảng Vector Table và Startup Code chuẩn Bare-Metal
 * ========================================================================= */

#include <stdint.h>

/* Kiểu dữ liệu con trỏ hàm đại diện cho các hàm phục vụ ngắt */
typedef void (*const Exception_Handler_t)(void);

/* Khai báo đỉnh Stack Pointer được định nghĩa từ Linker Script */
extern uint32_t _estack;

/* Khai báo hàm khởi động hệ thống */
void Reset_Handler(void);
void Default_Handler(void);

/* Khai báo các Exception Handlers hệ thống (Dạng Weak Alias trỏ về Default_Handler) */
void NMI_Handler(void)          __attribute__((weak, alias("Default_Handler")));
void HardFault_Handler(void)    __attribute__((weak, alias("Default_Handler")));
void MemManage_Handler(void)    __attribute__((weak, alias("Default_Handler")));
void BusFault_Handler(void)     __attribute__((weak, alias("Default_Handler")));
void UsageFault_Handler(void)   __attribute__((weak, alias("Default_Handler")));
void SVC_Handler(void)          __attribute__((weak, alias("Default_Handler")));
void DebugMon_Handler(void)     __attribute__((weak, alias("Default_Handler")));
void PendSV_Handler(void)       __attribute__((weak, alias("Default_Handler")));
void SysTick_Handler(void)      __attribute__((weak, alias("Default_Handler")));

/* Khai báo các Ngoại vi IRQ Handlers (Chip-Specific) */
void WWDG_IRQHandler(void)      __attribute__((weak, alias("Default_Handler")));
void USART1_IRQHandler(void)    __attribute__((weak, alias("Default_Handler")));
void TIM2_IRQHandler(void)      __attribute__((weak, alias("Default_Handler")));
void CAN1_RX0_IRQHandler(void)  __attribute__((weak, alias("Default_Handler")));

/* =========================================================================
 * BẢNG VECTOR TABLE CHÍNH THỨC
 * - __attribute__((section(".isr_vector"))): Ép đặt vào section riêng trong Flash
 * - __attribute__((used)): Ngăn cản trình biên dịch xóa bỏ khi bật tối ưu hóa (-O2/-O3)
 * ========================================================================= */
__attribute__((section(".isr_vector"), used))
const Exception_Handler_t g_pfnVectors[] = {
    /* Stack Pointer ban đầu (Nạp trực tiếp vào MSP khi Reset) */
    (Exception_Handler_t)(&_estack),

    /* 15 Core Exception Handlers của ARM Cortex-M */
    Reset_Handler,             /* Exception #1: Reset Handler */
    NMI_Handler,               /* Exception #2: Non-Maskable Interrupt */
    HardFault_Handler,         /* Exception #3: HardFault Handler */
    MemManage_Handler,         /* Exception #4: MPU Memory Manage Fault */
    BusFault_Handler,          /* Exception #5: Bus Fault */
    UsageFault_Handler,        /* Exception #6: Usage Fault */
    0, 0, 0, 0,                /* Exception #7-10: Reserved */
    SVC_Handler,               /* Exception #11: SVCall Handler */
    DebugMon_Handler,          /* Exception #12: Debug Monitor */
    0,                         /* Exception #13: Reserved */
    PendSV_Handler,            /* Exception #14: Pendable Request for System Service */
    SysTick_Handler,           /* Exception #15: System Tick Timer */

    /* Các External Interrupt Handlers (Bắt đầu từ Exception #16 = IRQ 0) */
    WWDG_IRQHandler,           /* IRQ 0: Window Watchdog */
    0,                         /* IRQ 1: PVD */
    0,                         /* IRQ 2: TAMP_STAMP */
    0,                         /* IRQ 3: RTC_WKUP */
    0,                         /* IRQ 4: FLASH */
    0,                         /* IRQ 5: RCC */
    0,                         /* IRQ 6: EXTI0 */
    /* ... các vector khác ... */
    TIM2_IRQHandler,           /* IRQ 28: TIM2 Global Interrupt */
    0,                         /* IRQ 29: TIM3 */
    0,                         /* IRQ 30: TIM4 */
    0,                         /* IRQ 31: I2C1_EV */
    0,                         /* IRQ 32: I2C1_ER */
    0,                         /* IRQ 33: I2C2_EV */
    0,                         /* IRQ 34: I2C2_ER */
    0,                         /* IRQ 35: SPI1 */
    0,                         /* IRQ 36: SPI2 */
    USART1_IRQHandler,         /* IRQ 37: USART1 Global Interrupt */
    CAN1_RX0_IRQHandler,       /* IRQ 19: CAN1 RX0 */
};

/* Default Handler xử lý khi ngắt xảy ra mà chưa có hàm triển khai cụ thể */
void Default_Handler(void) {
    /* Khi CPU chạy vào đây, nghĩa là có một interrupt được bật nhưng chưa viết hàm xử lý */
    while (1) {
        /* Đặt breakpoint tại đây khi debug */
    }
}
```

---

### 4.2 Cơ Chế Weak Symbol & Alias (Cực Kỳ Quan Trọng)

```c
void TIM2_IRQHandler(void) __attribute__((weak, alias("Default_Handler")));
```

**Bản chất hoạt động ở cấp độ Linker:**
1. Thuộc tính `weak` báo cho Linker biết: Đây chỉ là định nghĩa **mặc định có độ ưu tiên thấp**.
2. Thuộc tính `alias("Default_Handler")` báo cho Linker biết: Nếu trong toàn bộ dự án **KHÔNG CÓ** file nào khác định nghĩa hàm `TIM2_IRQHandler`, hãy trỏ symbol `TIM2_IRQHandler` tới địa chỉ của hàm `Default_Handler`.
3. Khi lập trình viên viết hàm `void TIM2_IRQHandler(void) { ... }` trong file `main.c` hoặc `timer.c`:
   * Trình biên dịch tạo ra một **Strong Symbol** cho `TIM2_IRQHandler`.
   * Linker tự động ghi đè Strong Symbol này vào vị trí tương ứng trong bảng Vector Table, thay thế hoàn toàn alias cũ mà không gây lỗi trùng tên hàm (Multiple Definition Error).

---

### 4.3 Phân Tích Linker Script Chi Tiết

Linker Script là "kiến trúc sư" quyết định chính xác Vector Table và mã nguồn nằm ở đâu trong bộ nhớ vật lý:

```ld
/* =========================================================================
 * File: stm32f407vg.ld — Linker Script cho ARM Cortex-M4
 * ========================================================================= */

/* Khai báo điểm vào đầu tiên của chương trình */
ENTRY(Reset_Handler)

/* Khai báo kích thước Stack và Heap */
_Min_Heap_Size  = 0x200;  /* 512 Bytes */
_Min_Stack_Size = 0x400;  /* 1024 Bytes / 1 KB */

/* ĐỊNH NGHĨA KHÔNG GIAN BỘ NHỚ VẬT LÝ */
MEMORY
{
    FLASH (rx)  : ORIGIN = 0x08000000, LENGTH = 1024K  /* 1 MB Flash */
    RAM   (xrw) : ORIGIN = 0x20000000, LENGTH = 128K   /* 128 KB SRAM */
}

/* ĐỊNH NGHĨA ĐỈNH CỦA STACK (Cuối vùng RAM) */
_estack = ORIGIN(RAM) + LENGTH(RAM);  /* = 0x20020000 */

/* ĐỊNH NGHĨA PHÂN BỐ CÁC SECTION VÀO BỘ NHỚ */
SECTIONS
{
    /* 1. BẢNG VECTOR NGẮT PHẢI NẰM TẠI VỊ TRÍ ĐẦU TIÊN CỦA FLASH */
    .isr_vector :
    {
        . = ALIGN(4);
        KEEP(*(.isr_vector))  /* LỆNH BẮT BUỘC: Ngăn Linker xóa bỏ mảng này */
        . = ALIGN(4);
    } > FLASH

    /* 2. MÃ NGUỒN CHƯƠNG TRÌNH VÀ DỮ LIỆU HẰNG SỐ */
    .text :
    {
        . = ALIGN(4);
        *(.text)           /* Tất cả mã thực thi (.text) từ các file .o */
        *(.text*)          /* Tất cả sub-sections của code */
        *(.rodata)         /* Dữ liệu chỉ đọc (Hằng số const, chuỗi text) */
        *(.rodata*)
        . = ALIGN(4);
        _etext = .;        /* Đánh dấu kết thúc phần code trong Flash */
    } > FLASH

    /* 3. DỮ LIỆU CÓ KHỞI TẠO (INITIALIZED DATA) */
    /* Lưu trữ giá trị ban đầu trong FLASH (LMA), nhưng thực thi trong RAM (VMA) */
    _sidata = LOADADDR(.data);

    .data :
    {
        . = ALIGN(4);
        _sdata = .;        /* Địa chỉ bắt đầu .data trong RAM */
        *(.data)
        *(.data*)
        . = ALIGN(4);
        _edata = .;        /* Địa chỉ kết thúc .data trong RAM */
    } > RAM AT> FLASH

    /* 4. DỮ LIỆU KHÔNG KHỞI TẠO (BSS - PHẢI ĐƯỢC XÓA VỀ 0 KHI BOOT) */
    .bss :
    {
        . = ALIGN(4);
        _sbss = .;         /* Địa chỉ bắt đầu .bss trong RAM */
        *(.bss)
        *(.bss*)
        *(COMMON)
        . = ALIGN(4);
        _ebss = .;         /* Địa chỉ kết thúc .bss trong RAM */
    } > RAM

    /* 5. VÙNG BỘ NHỚ USER STACK VÀ HEAP */
    ._user_heap_stack :
    {
        . = ALIGN(8);
        PROVIDE ( end = . );
        . = . + _Min_Heap_Size;
        . = . + _Min_Stack_Size;
        . = ALIGN(8);
    } > RAM
}
```

---

### 4.4 Quy Trình Biên Dịch & Liên Kết Đầy Đủ (Toolchain Flow)

```
[SOURCE CODE]
startup.c, main.c, timer.c
     │
     ▼ (arm-none-eabi-gcc -c -mcpu=cortex-m4 -mthumb -O2)
[OBJECT FILES (.o)]
startup.o (chứa .isr_vector), main.o, timer.o (chứa TIM2_IRQHandler Strong Symbol)
     │
     ▼ (arm-none-eabi-ld -T stm32f407vg.ld)
[EXECUTABLE ELF FILE (.elf)]
- Bảng ký hiệu hoàn chỉnh (Symbol Table).
- .isr_vector được cố định tuyệt đối tại địa chỉ 0x08000000.
- TIM2_IRQHandler Strong Symbol ghi đè hoàn toàn Default_Handler.
     │
     ▼ (arm-none-eabi-objcopy -O binary firmware.elf firmware.bin)
[RAW BINARY (.bin)]
File nhị phân thuần túy nạp trực tiếp vào ô nhớ Flash từ 0x08000000:
- 4 bytes đầu: Giá trị Initial Stack Pointer (0x20020000).
- 4 bytes tiếp theo: Địa chỉ Reset_Handler (0x08000109).
- Byte thứ 0xB0 - 0xB3: Địa chỉ TIM2_IRQHandler.
```

---

### 4.5 Hàm Khởi Động Reset_Handler Thực Tế (Startup Sequence)

```c
/* Hàm thực thi đầu tiên sau khi bật nguồn */
void Reset_Handler(void) {
    uint32_t *pSrc, *pDest;

    /* 1. Copy toàn bộ dữ liệu .data từ Flash sang RAM */
    pSrc  = &_sidata;  /* Điểm bắt đầu trong Flash */
    pDest = &_sdata;   /* Điểm bắt đầu trong RAM */
    while (pDest < &_edata) {
        *pDest++ = *pSrc++;
    }

    /* 2. Xóa sạch toàn bộ vùng nhớ .bss về 0 */
    pDest = &_sbss;
    while (pDest < &_ebss) {
        *pDest++ = 0UL;
    }

    /* 3. Cấu hình phần cứng lõi (FPU, System Clock) */
    SystemInit();

    /* 4. Nhảy vào hàm main() của ứng dụng */
    main();

    /* 5. Phòng thủ: Nếu main() thoát, khóa CPU trong vòng lặp */
    while (1) {
        __NOP();
    }
}
```

---

### 4.6 Quy Trình Bật Ngắt Ngoại Vi Toàn Diện (7 Bước Bắt Buộc)

```c
/* Cấu hình ngắt Timer 2 (TIM2 Update Interrupt) chuẩn xác 100% */
void TIM2_Interrupt_Init(void) {
    /* BƯỚC 1: Cấp Clock cho ngoại vi TIM2 trên Bus APB1 */
    RCC->APB1ENR |= RCC_APB1ENR_TIM2EN;

    /* BƯỚC 2: Cấu hình tham số phần cứng (Prescaler & Auto-Reload) */
    TIM2->PSC = 8400 - 1;    /* Clock 84 MHz / 8400 = 10 kHz */
    TIM2->ARR = 10000 - 1;   /* Đếm 10000 xung = Đúng chu kỳ 1 giây */
    TIM2->CNT = 0;

    /* BƯỚC 3: Bật cờ ngắt Update Interrupt bên trong ngoại vi */
    TIM2->DIER |= TIM_DIER_UIE;

    /* BƯỚC 4: Thiết lập mức ưu tiên ngắt trong NVIC (Priority = 5) */
    NVIC_SetPriority(TIM2_IRQn, 5);

    /* BƯỚC 5: Kích hoạt kênh ngắt TIM2_IRQn trong thanh ghi NVIC->ISER */
    NVIC_EnableIRQ(TIM2_IRQn);

    /* BƯỚC 6: Bật bộ đếm Timer bắt đầu chạy */
    TIM2->CR1 |= TIM_CR1_CEN;

    /* BƯỚC 7: Đảm bảo ngắt toàn cục đã được mở (Clear PRIMASK) */
    __enable_irq();
}
```

---

### 4.7 Câu Hỏi Kiểm Tra Tư Duy — Chương 4

1. **Câu 1:** Từ khóa `KEEP(*(.isr_vector))` trong Linker Script đóng vai trò sống còn như thế nào? Điều gì sẽ xảy ra nếu lập trình viên xóa bỏ lệnh `KEEP()` và biên dịch dự án với cờ tối ưu hóa loại bỏ hàm rác `-Wl,--gc-sections`?
2. **Câu 2:** Thuộc tính `__attribute__((weak))` được xử lý ở giai đoạn nào: **Compiler** hay **Linker**? Nếu cả file `startup.c` và file `main.c` đều định nghĩa hàm `void TIM2_IRQHandler(void)` mà **KHÔNG CÓ** từ khóa `weak`, trình biên dịch/liên kết sẽ báo lỗi gì?
3. **Câu 3:** Trong hàm `Reset_Handler`, nếu vòng lặp copy `.data` từ Flash sang RAM bị lỗi hoặc bị bỏ qua, một biến toàn cục được khai báo `int g_timeout_counter = 100;` sẽ có giá trị bao nhiêu khi hàm `main()` bắt đầu chạy?

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
> *(Hoàn toàn ngược lại với quy ước Task Priority trong FreeRTOS: Task số lớn = Ưu tiên cao).*

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
__set_BASEPRI(5 << (8 - __NVIC_PRIO_BITS));  /* Thường dùng trong FreeRTOS */
__set_BASEPRI(0);                            /* Hủy bỏ lọc ngưỡng, mở lại toàn bộ */

/* 3. FAULTMASK: Khóa cả HardFault (Chỉ dùng trong các tình huống cứu hộ đặc biệt) */
__set_FAULTMASK(1);
```

---

### 6.5 Câu Hỏi Kiểm Tra Tư Duy — Chương 6

1. **Câu 1:** Trong hệ thống có IRQ_A (Preemption Prio = 2, Sub-Prio = 0) và IRQ_B (Preemption Prio = 2, Sub-Prio = 1). Khi IRQ_B đang thực thi, IRQ_A được kích hoạt. IRQ_A có thể preempt (cắt ngang) IRQ_B để chạy trước hay không? Tại sao?
2. **Câu 2:** Tại sao FreeRTOS lại sử dụng thanh ghi `BASEPRI` để bảo vệ các vùng Critical Section (`taskENTER_CRITICAL()`) thay vì dùng lệnh khóa toàn cục `__disable_irq()` (`PRIMASK`)?
3. **Câu 3:** Khái niệm "Tail-Chaining" giúp tiết kiệm bao nhiêu chu kỳ xung nhịp và tại sao nó lại là tính năng mang tính cách mạng cho các hệ thống vi điều khiển thời gian thực?

---

<a name="ch7"></a>
## CHƯƠNG 7: INTERRUPT & RTOS (FREERTOS ARCHITECTURE)

### 7.1 Tại Sao Tuyệt Đối Không Được Dùng API Chuẩn Trong ISR?

Một lỗi kinh điển của lập trình viên Junior là gọi hàm `xSemaphoreGive(sem)` hoặc `xQueueSend(queue, &data, 0)` bên trong hàm ISR.

```
HẬU QUẢ CHÍNH XÁC KHI GỌI API CHUẨN TRONG ISR:

1. VI PHẠM KHÓA CRITICAL SECTION:
   `xQueueSend()` bên trong gọi `taskENTER_CRITICAL()`. Hàm này thao tác với biến đếm
   `uxCriticalNesting` vốn CHỈ DÀNH RIÊNG CHO THREAD CONTEXT. Khi gọi trong ISR (Handler Mode),
   biến đếm này bị sai lệch, dẫn tới deadlock hệ thống!

2. GỌI BỘ LẬP LỊCH SAI THỜI ĐIỂM:
   Nếu việc gửi Queue đánh thức một Task có độ ưu tiên cao hơn, `xQueueSend()` sẽ gọi `portYIELD()`.
   Lệnh này yêu cầu chuyển ngữ cảnh NGAY LẬP TỨC trong khi CPU VẪN ĐANG NẰM TRONG HANDLER MODE
   CỦA PHẦN CỨNG ➔ Kích hoạt lỗi HardFault hoặc làm sập RTOS Kernel!
```

#### 💡 GIẢI PHÁP: LUÔN DÙNG CÁC API CÓ ĐUÔI `...FromISR()`
Các API `FromISR` được thiết kế chuyên biệt cho Handler Mode:
- Không sử dụng `taskENTER_CRITICAL()` mà dùng cơ chế lưu trạng thái ngắt an toàn.
- Không tự ý gọi chuyển ngữ cảnh mà thông báo qua con trỏ `pxHigherPriorityTaskWoken`.

---

### 7.2 Mẫu Thiết Kế Chuẩn ISR Trong FreeRTOS (Design Pattern)

```c
/* Hàm ngắt UART RX xử lý chuẩn mực công nghiệp với FreeRTOS */
void USART1_IRQHandler(void) {
    BaseType_t xHigherPriorityTaskWoken = pdFALSE;
    uint8_t rx_data;

    /* 1. Kiểm tra cờ ngắt phần cứng RXNE (Read data register not empty) */
    if (USART1->SR & USART_SR_RXNE) {
        rx_data = (uint8_t)(USART1->DR & 0xFF);  /* Đọc dữ liệu (Tự động xóa cờ RXNE) */

        /* 2. Đưa dữ liệu vào Queue từ trong ISR */
        xQueueSendFromISR(g_uart_rx_queue, &rx_data, &xHigherPriorityTaskWoken);
    }

    /* 3. BẮT BUỘC: Yêu cầu chuyển đổi ngữ cảnh nếu có Task ưu tiên cao hơn được đánh thức */
    portYIELD_FROM_ISR(xHigherPriorityTaskWoken);
    /* Nếu xHigherPriorityTaskWoken == pdTRUE:
       Hàm này sẽ set bit PENDSVSET trong thanh ghi SCB->ICSR.
       Ngay khi hàm USART1_IRQHandler kết thúc (BX LR), CPU sẽ chuyển thẳng sang
       PendSV_Handler để chuyển ngữ cảnh sang Task xử lý dữ liệu ngay lập tức! */
}
```

---

### 7.3 Tam Giác Vàng Của FreeRTOS: SysTick, PendSV, SVCall

```
+===================================================================================+
|                    KIẾN TRÚC ĐIỀU PHỐI RTOS QUA 3 EXCEPTION                       |
+===================================================================================+

 1. SVC (Supervisor Call - Exception #11):
    • Thực thi với lệnh: `SVC #0`.
    • Nhiệm vụ: Khởi động Task đầu tiên khi gọi `vTaskStartScheduler()`.
    • Chuyển CPU từ Privileged Mode sang Unprivileged Mode để chạy ứng dụng an toàn.

 2. SysTick Timer (Exception #15 - Priority = configLIBRARY_LOWEST_INTERRUPT_PRIORITY):
    • Tạo ngắt định kỳ mỗi 1 ms (configTICK_RATE_HZ = 1000).
    • Tăng biến đếm thời gian `xTickCount`.
    • Kiểm tra các Task đang Delay (`vTaskDelay`) hoặc Timeout.
    • Nếu có Task ưu tiên cao sẵn sàng: Kéo cờ `SCB->ICSR |= SCB_ICSR_PENDSVSET_Msk`.

 3. PendSV (Pendable Service - Exception #14 - LUÔN CÓ PRIORITY THẤP NHẤT = 255):
    • Đóng vai trò là "Cỗ máy chuyển đổi ngữ cảnh" (Context Switch Engine).
    • Chỉ được phép chạy khi TẤT CẢ các ngắt phần cứng khác đã hoàn thành.
    • Thực thi mã nguồn Assembly:
        - Lưu các thanh ghi {R4-R11} của Task cũ vào vùng nhớ Stack (PSP).
        - Cập nhật con trỏ `pxCurrentTCB->pxTopOfStack = PSP`.
        - Lấy `pxCurrentTCB` mới (Task có độ ưu tiên cao nhất trong Ready List).
        - Nạp lại {R4-R11} từ Stack của Task mới.
        - Gán PSP = `pxCurrentTCB->pxTopOfStack`.
        - Thực hiện `BX LR` (0xFFFFFFFD) ➔ CPU tự động nạp {R0-R3, R12, LR, PC, xPSR}
          và bắt đầu chạy Task mới!
+===================================================================================+
```

---

### 7.4 Cấu Hình `configMAX_SYSCALL_INTERRUPT_PRIORITY` (Cực Kỳ Quan Trọng)

Trong file `FreeRTOSConfig.h`:

```c
/* Ngưỡng ưu tiên ngắt cao nhất được phép gọi API FreeRTOS (ví dụ = 5) */
#define configLIBRARY_MAX_SYSCALL_INTERRUPT_PRIORITY   5
```

```
PHÂN CHIA TẦNG NGẮT TRONG HỆ THỐNG EMBEDDED:

Priority 0 - 4 (CAO HƠN configMAX_SYSCALL):
  • Các ngắt cực kỳ khẩn cấp, thời gian thực tuyệt đối (Zero-Latency ISRs):
    - Điều khiển băm xung Motor FOC (20 kHz PWM).
    - Bảo vệ ngắt mạch phần cứng quá dòng / quá nhiệt.
  • KHÔNG BAO GIỜ bị RTOS khóa (Kernel Critical Section không thể chạm tới).
  • TUYỆT ĐỐI KHÔNG ĐƯỢC GỌI BẤT KỲ API NÀO CỦA FREERTOS (Kể cả ...FromISR)!

Priority 5 - 15 (THẤP HƠN HOẶC BẰNG configMAX_SYSCALL):
  • Các ngắt thông thường (UART, CAN, SPI, I2C, Timer định thời).
  • Có thể gọi an toàn các hàm API có đuôi `...FromISR`.
  • Sẽ bị tạm dừng trong khoảng thời gian rất ngắn khi RTOS chạy Critical Section.
```

---

### 7.5 Câu Hỏi Kiểm Tra Tư Duy — Chương 7

1. **Câu 1:** Điều gì sẽ xảy ra nếu một kỹ sư vô tình cấu hình ngắt CAN RX có mức ưu tiên `Priority = 3` (cao hơn `configMAX_SYSCALL = 5`) và bên trong ISR gọi hàm `xQueueSendFromISR()`?
2. **Câu 2:** Tại sao `PendSV` bắt buộc phải có mức ưu tiên thấp nhất trong hệ thống? Nếu gán `PendSV` mức ưu tiên cao nhất, điều gì sẽ xảy ra khi một ngắt UART đang nhận dở gói tin thì bị PendSV cắt ngang để đổi Task?
3. **Câu 3:** Phân tích cơ chế hoạt động của `portYIELD_FROM_ISR(xHigherPriorityTaskWoken)`. Tại sao lệnh này không thực hiện chuyển Task ngay lập tức trong thân hàm ISR mà lại thông qua `PendSV`?

---

<a name="ch8"></a>
## CHƯƠNG 8: BOOTLOADER & MULTI-IMAGE ARCHITECTURE

### 8.1 Sơ Đồ Phân Vùng Bộ Nhớ Flash (Dual-Image Layout)

```
SƠ ĐỒ BỘ NHỚ FLASH KHI CÓ BOOTLOADER VÀ APPLICATION:

Địa chỉ Flash
0x08100000 +------------------------------------------+  <-- HẾT FLASH (1 MB)
           |  Vùng Lưu Trữ Firmware Mới (OTA Buffer)  |
0x08080000 +------------------------------------------+
           |  APPLICATION FIRMWARE                    |
           |  • Bảng Vector Table của App (512B)     |  <-- NẰM TẠI 0x08008000
           |    [0] Initial Stack Pointer của App     |
           |    [1] Reset_Handler của App             |
           |  • Mã thực thi (.text) của App           |
           |  • Hằng số (.rodata) của App             |
0x08008000 +------------------------------------------+  <-- ĐỊA CHỈ BẮT ĐẦU APP
           |  BOOTLOADER FIRMWARE                     |
           |  • Bảng Vector Table của Bootloader      |  <-- NẰM TẠI 0x08000000
           |    [0] Initial Stack Pointer của BL      |
           |    [1] Reset_Handler của BL              |
           |  • Logic kiểm tra OTA, Flash Read/Write  |
0x08000000 +------------------------------------------+  <-- BẮT ĐẦU FLASH VẬT LÝ
```

---

### 8.2 Quy Trình 9 Bước Nhảy Từ Bootloader Sang Application Chuẩn Senior

Dưới đây là hàm chuyển giao quyền thực thi từ Bootloader sang Application an toàn tuyệt đối 100%:

```c
#define APPLICATION_START_ADDRESS   (0x08008000UL)

typedef void (*pFunction)(void);

void Jump_To_Application(void) {
    uint32_t app_stack_pointer;
    uint32_t app_reset_handler_addr;
    pFunction app_entry;

    /* BƯỚC 1: Đọc giá trị Initial Stack Pointer của App tại Entry [0] */
    app_stack_pointer = *(__IO uint32_t*)APPLICATION_START_ADDRESS;

    /* BƯỚC 2: Kiểm tra tính hợp lệ của Stack Pointer (Phải nằm trong không gian SRAM 0x20000000 - 0x20020000) */
    if ((app_stack_pointer & 0xFFFE0000) != 0x20000000) {
        /* Firmware Application bị rỗng hoặc lỗi nạp -> Không thể nhảy! */
        Error_Handler();
    }

    /* BƯỚC 3: Đọc địa chỉ hàm Reset_Handler của App tại Entry [1] */
    app_reset_handler_addr = *(__IO uint32_t*)(APPLICATION_START_ADDRESS + 4);
    app_entry = (pFunction)app_reset_handler_addr;

    /* BƯỚC 4: Khóa toàn bộ ngắt toàn cục trước khi dọn dẹp hệ thống */
    __disable_irq();

    /* BƯỚC 5: Tắt toàn bộ ngắt phần cứng trong NVIC và xóa sạch trạng thái Pending */
    for (int i = 0; i < 8; i++) {
        NVIC->ICER[i] = 0xFFFFFFFF;  /* Disable all IRQ channels */
        NVIC->ICPR[i] = 0xFFFFFFFF;  /* Clear all Pending flags */
    }

    /* BƯỚC 6: Tắt bộ đếm SysTick để không làm gián đoạn quá trình Boot của App */
    SysTick->CTRL = 0;
    SysTick->LOAD = 0;
    SysTick->VAL  = 0;

    /* BƯỚC 7: TÁI ĐỊNH VỊ VECTOR TABLE SANG APPLICATION */
    SCB->VTOR = APPLICATION_START_ADDRESS;

    /* BƯỚC 8: Thiết lập thanh ghi Main Stack Pointer (MSP) sang vùng nhớ Stack của App */
    __set_MSP(app_stack_pointer);

    /* BƯỚC 9: Thiết lập trạng thái thanh ghi CONTROL = 0 (Privileged Mode, sử dụng MSP) */
    __set_CONTROL(0);
    __ISB();  /* Flush pipeline lệnh */

    /* BƯỚC 10: Mở lại ngắt toàn cục và nhảy thẳng vào Reset_Handler của Application */
    __enable_irq();
    app_entry();

    /* Đoạn code phòng thủ: Không bao giờ được chạy tới đây */
    while (1) {
        __NOP();
    }
}
```

---

### 8.3 5 Lỗi Kinh Điển Khi Làm Bootloader Khiến App Bị Crash

| Lỗi Phổ Biến | Nguyên Nhân Bản Chất | Cách Khắc Phục Chuẩn Senior |
|---|---|---|
| **Lỗi 1: HardFault ngay khi App kích hoạt ngắt đầu tiên** | Bootloader nhảy vào App nhưng quên không cập nhật thanh ghi `SCB->VTOR = 0x08008000`. Khi có ngắt, CPU vẫn tra cứu Vector Table của Bootloader! | Bắt buộc gán `SCB->VTOR = APPLICATION_START_ADDRESS` trước khi nhảy. |
| **Lỗi 2: Lỗi tràn Stack bí ẩn sau vài phút App hoạt động** | Bootloader quên không gọi `__set_MSP(app_stack_pointer)`, khiến App tiếp tục chạy trên vùng Stack cũ kỹ của Bootloader. | Nạp `__set_MSP()` từ Entry [0] của Application. |
| **Lỗi 3: App bị treo cứng ngay khi vừa khởi động** | Các ngoại vi của Bootloader (UART, Timer) vẫn đang chạy và sinh ngắt dở dang. App chưa khởi tạo xong driver nhưng đã bị ngắt thừa của Bootloader ập vào! | Gọi `HAL_DeInit()` hoặc tắt toàn bộ Clock ngoại vi và tắt NVIC trước khi nhảy. |
| **Lỗi 4: FreeRTOS trong App không thể chuyển ngữ cảnh** | SysTick của Bootloader vẫn chạy nền, xung đột trực tiếp với SysTick Driver của App. | Tắt sạch `SysTick->CTRL = 0` trước khi thực hiện lệnh nhảy. |
| **Lỗi 5: UsageFault INVSTATE** | Địa chỉ hàm `Reset_Handler` bị mất bit LSB (Thumb bit 0 = 0). | Đảm bảo Entry [1] của App luôn là số lẻ (Ví dụ `0x08008109`). |

---

### 8.4 Câu Hỏi Kiểm Tra Tư Duy — Chương 8

1. **Câu 1:** Tại sao nếu chỉ dùng con trỏ hàm để gọi `((void(*)(void))0x08008004)()` mà không nạp lại thanh ghi `MSP` và `VTOR` thì Application vẫn có thể chạy được hàm `main()` nhưng sẽ crash ngay khi có ngắt xảy ra?
2. **Câu 2:** Tại sao địa chỉ bắt đầu của Application trong Flash (ví dụ `0x08008000` hay `0x08010000`) bắt buộc phải chia hết cho `0x200` (512 bytes) hoặc `0x400` (1024 bytes)?
3. **Câu 3:** Trong các hệ thống an toàn cao (Automotive ECU), trước khi nhảy vào Application, Bootloader cần thực hiện các bước xác thực phần mềm (Secure Boot) nào?

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
* ✅ **Cách hiểu đúng:** Trong kiến trúc ARM Cortex-M, **SỐ CÀNG NHỎ THÌ MỨC ƯU TIÊN CÀNG CAO** (Priority 0 là cao nhất). Hoàn toàn ngược lại với quy ước Task Priority trong FreeRTOS.
* 🧠 **Vì sao dễ nhầm:** Nhầm lẫn giữa NVIC Hardware Priority và RTOS Software Task Priority.
* 🔧 **Hậu quả Production:** Đặt nhầm ngắt an toàn khẩn cấp (Emergency Stop) thành ưu tiên thấp nhất, khiến hệ thống phản ứng chậm trễ khi có sự cố.

---

### ❌ Misconception 4: "Có thể gọi `xSemaphoreGive()` bình thường trong ISR"
* ❌ **Sai ở đâu:** Dùng chung API của Thread Context vào trong Handler Context của ISR.
* ✅ **Cách hiểu đúng:** Bắt buộc phải dùng `xSemaphoreGiveFromISR()` kèm cờ `pxHigherPriorityTaskWoken` và `portYIELD_FROM_ISR()`.
* 🧠 **Vì sao dễ nhầm:** Nhìn cú pháp hàm tương tự nhau.
* 🔧 **Hậu quả Production:** Gây sai lệch biến đếm `uxCriticalNesting`, deadlock Kernel hoặc HardFault ngẫu nhiên rất khó tái hiện.

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

<a name="ch12"></a>
## CHƯƠNG 12: SO SÁNH KIẾN TRÚC CPU

### 12.1 Bảng So Sánh Toàn Diện: Cortex-M vs Cortex-A vs RISC-V vs x86

| Đặc Tính Kiến Trúc | ARM Cortex-M (Microcontroller) | ARM Cortex-A (Application Processor) | RISC-V (RV32I / RV64I) | Intel/AMD x86-64 |
|---|---|---|---|---|
| **Cơ Chế Bảng Vector** | **Mảng con trỏ hàm (Array of Function Pointers)**. | **Mảng câu lệnh nhảy (Array of Branch Instructions)**. | **Vectored Mode** (Array) hoặc **Direct Mode** (Single Trap Handler). | **IDT (Interrupt Descriptor Table)** chứa 256 Gate Descriptors (16 bytes/entry). |
| **Vị Trí Bảng Vector** | Thanh ghi `SCB->VTOR` (Flash/RAM). | Thanh ghi `VBAR` (Virtual Address trong MMU). | Thanh ghi CSR `mtvec` (Machine Trap-Vector Base). | Thanh ghi `IDTR` (Nạp qua lệnh `LIDT`). |
| **Lưu Ngữ Cảnh (Context Saving)** | **Phần cứng tự động 100% (Hardware Auto-stacking 8 regs)**. | **Phần mềm (Software OS)** phải lưu toàn bộ qua lệnh `STMFD` / `PUSH`. | **Phần mềm (Software Assembly)** lưu qua các lệnh `sw`/`sd` vào Stack. | **Phần cứng lưu một phần** (SS, RSP, RFLAGS, CS, RIP), OS lưu các thanh ghi đa năng. |
| **Bộ Điều Khiển Ngắt** | **NVIC** (Tích hợp sâu trong lõi CPU). | **GIC (Generic Interrupt Controller)** nằm ngoài CPU core. | **PLIC** (Platform-Level) hoặc **CLIC** (Core-Local). | **APIC (Advanced Programmable Interrupt Controller)**. |
| **Chế Độ Thực Thi** | 2 chế độ: **Thread Mode** (App) và **Handler Mode** (ISR). | 4 mức đặc quyền: **EL0** (User), **EL1** (Kernel), **EL2** (Hypervisor), **EL3** (TrustZone). | 3 chế độ: **U-Mode** (User), **S-Mode** (Supervisor), **M-Mode** (Machine). | 4 đặc quyền Rings: **Ring 0** (Kernel) đến **Ring 3** (User). |
| **Độ Trễ Ngắt (Latency)** | **Cực thấp và xác định (Deterministic: 12 cycles)**. | Cao hơn (Tùy thuộc vào OS Pipeline, Cache, TLB Miss). | Tùy thuộc phần cứng (CLIC cho độ trễ thấp như NVIC). | Biến thiên lớn do kiến trúc phức tạp và Context Switching. |

---

<a name="ch13"></a>
## CHƯƠNG 13: PHÂN TÍCH TOÀN DIỆN STARTUP CODE THỰC TẾ

### 13.1 Giải Phẫu Từng Dòng Lệnh Của Bảng `g_pfnVectors`

```c
/* =========================================================================
 * PHÂN TÍCH CẤP ĐỘ COMPILER & LINKER:
 * ========================================================================= */

/* 1. Đặt mảng vào Section riêng để Linker Script định vị tại 0x08000000 */
__attribute__((section(".isr_vector"), used))
const Exception_Handler_t g_pfnVectors[] = {

    /* Entry [0]: Giá trị đỉnh Stack (Initial Main Stack Pointer - MSP)
     * - Linker Symbol: `&_estack` lấy địa chỉ cuối vùng SRAM (0x20020000).
     * - Khi CPU Reset, phần cứng đọc 4 bytes này và gán trực tiếp vào thanh ghi SP. */
    (Exception_Handler_t)(&_estack),

    /* Entry [1]: Con trỏ hàm Reset_Handler
     * - Trình biên dịch tạo mã máy cho Reset_Handler tại địa chỉ Flash (ví dụ 0x08000108).
     * - Do cờ biên dịch `-mthumb`, Compiler tự động bật Bit 0 = 1 ➔ Giá trị thực = 0x08000109.
     * - CPU nạp giá trị này vào PC khi bật nguồn để bắt đầu chạy mã nguồn C! */
    Reset_Handler,

    /* Entry [2 - 15]: Các Exception Handlers cốt lõi của ARM */
    NMI_Handler,
    HardFault_Handler,
    MemManage_Handler,
    BusFault_Handler,
    UsageFault_Handler,
    0, 0, 0, 0,                /* Reserved entries theo quy chuẩn ARM */
    SVC_Handler,
    DebugMon_Handler,
    0,
    PendSV_Handler,
    SysTick_Handler,

    /* Entry [16+]: Các kênh External Interrupts của vi điều khiển */
    WWDG_IRQHandler,
    PVD_IRQHandler,
    /* ... */
};
```

---

### 13.2 Cơ Chế Boot Toàn Diện Của MCU Từ Khi Bật Nguồn

```
[BƯỚC 1: CẤP NGUỒN VẬT LÝ (POWER-ON RESET)]
Điện áp VDD tăng ổn định. Bộ giám sát nguồn (Power-On Reset Circuit) giải phóng tín hiệu Reset nội bộ.
     │
[BƯỚC 2: PHẦN CỨNG NẠP MSP VÀ PC BAN ĐẦU]
1. CPU Core đọc 4 bytes tại địa chỉ 0x00000000 (Được ánh xạ từ 0x08000000 của Flash).
   ➔ Nạp giá trị `0x20020000` vào thanh ghi `MSP`.
2. CPU Core đọc 4 bytes tại địa chỉ 0x00000004.
   ➔ Nạp giá trị `0x08000109` vào thanh ghi `PC` (và set cờ Thumb bit trong EPSR).
     │
[BƯỚC 3: THỰC THI HÀM RESET_HANDLER()]
CPU bắt đầu chạy các lệnh đầu tiên trong hàm Reset_Handler():
1. Copy toàn bộ phân vùng `.data` từ Flash (LMA) sang RAM (VMA) để khởi tạo các biến toàn cục có giá trị ban đầu.
2. Xóa sạch phân vùng `.bss` trong RAM về giá trị `0` để khởi tạo các biến toàn cục không gán giá trị.
3. Gọi hàm `SystemInit()` để cấu hình thạch anh dao động ngoại (HSE), nhân tần số PLL, và bật FPU.
     │
[BƯỚC 4: NHẢY VÀO HÀM MAIN()]
Gọi hàm `main()` của ứng dụng. Hệ thống bước vào luồng thực thi chính thức.
```

<a name="ch14"></a>
## CHƯƠNG 14: THIẾT KẾ INTERRUPT HANDLING CHUẨN SENIOR

### 14.1 Triết Lý Thiết Kế ISR Của Firmware Architect

> [!TIP]
> **Quy Tắc Tối Thượng Của ISR:**  
> **"VÀO NHANH ➔ LÀM ÍT ➔ BÁO HIỆU ➔ THOÁT NGAY!"**  
> *(Get In ➔ Do Minimum ➔ Defer Work ➔ Get Out!)*

#### 📋 Những Việc ĐƯỢC PHÉP Làm Trong ISR:
1. Đọc dữ liệu khẩn cấp từ thanh ghi ngoại vi (1 byte UART DR, giá trị ADC DR).
2. Xóa cờ ngắt phần cứng của ngoại vi (Clear Interrupt Flag).
3. Đẩy dữ liệu vào Ring Buffer (Lock-Free) hoặc Queue của RTOS.
4. Gửi tín hiệu đánh thức Task (Give Semaphore / Set Event Flags).
5. Yêu cầu chuyển ngữ cảnh (`portYIELD_FROM_ISR()`) nếu cần.

#### 🚫 Những Việc TUYỆT ĐỐI CẤM Làm Trong ISR:
1. **Tuyệt đối không gọi hàm Delay (`HAL_Delay`, `vTaskDelay`, busy loops).**
2. **Tuyệt đối không sử dụng Mutex (`xSemaphoreTake` với Mutex vì Mutex có cơ chế Priority Inheritance chỉ dành cho Task).**
3. **Tuyệt đối không cấp phát bộ nhớ động (`malloc`, `free`, `pvPortMalloc`).**
4. **Tuyệt đối không in chuỗi qua UART blocking (`printf`).**
5. **Tuyệt đối không thực hiện các thuật toán tính toán nặng (Mã hóa, lọc số học, giải mã JSON).**

---

### 14.2 3 Mẫu Thiết Kế (Design Patterns) Xử Lý Ngắt Kinh Điển

#### 🌟 PATTERN 1: Mô Hình Ngắt Hai Nửa (Top-Half / Bottom-Half Architecture)

```
[TOP-HALF (CHẠY TRONG ISR - HANDLER MODE)]
• Thời gian thực thi: < 5 micro giây.
• Nhiệm vụ: Đọc phần cứng, xóa cờ ngắt, gửi Semaphore/Queue.
     │
     ▼ (xSemaphoreGiveFromISR + portYIELD_FROM_ISR)
[BOTTOM-HALF (CHẠY TRONG RTOS TASK - THREAD MODE)]
• Thời gian thực thi: Tùy ý (hàng chục mili-giây).
• Nhiệm vụ: Xử lý logic nghiệp vụ, tính toán CRC, lưu Flash, gọi API mạng.
```

#### 🌟 PATTERN 2: Lock-Free Single-Producer Single-Consumer (SPSC) Ring Buffer
Mô hình truyền dữ liệu tốc độ cao giữa 1 ISR (Producer) và 1 Task (Consumer) mà **KHÔNG CẦN KHÓA MUTEX / CRITICAL SECTION**:

```c
#define RING_BUFFER_SIZE  256  /* Bắt buộc là lũy thừa của 2 để dùng phép AND bit */
#define RING_BUFFER_MASK  (RING_BUFFER_SIZE - 1)

typedef struct {
    uint8_t  buffer[RING_BUFFER_SIZE];
    volatile uint32_t head;  /* Chỉ do ISR (Producer) ghi */
    volatile uint32_t tail;  /* Chỉ do Task (Consumer) ghi */
} SPSC_RingBuffer_t;

SPSC_RingBuffer_t g_uart_rb = { .head = 0, .tail = 0 };

/* Thực thi trong ISR (Producer) */
void USART1_IRQHandler(void) {
    if (USART1->SR & USART_SR_RXNE) {
        uint8_t byte = (uint8_t)USART1->DR;
        uint32_t next_head = (g_uart_rb.head + 1) & RING_BUFFER_MASK;

        if (next_head != g_uart_rb.tail) {
            g_uart_rb.buffer[g_uart_rb.head] = byte;
            __DMB();  /* Data Memory Barrier: Đảm bảo dữ liệu ghi xong trước khi tăng head */
            g_uart_rb.head = next_head;
        } else {
            /* Buffer bị đầy (Buffer Overflow) -> Ghi nhận lỗi */
        }
    }
}

/* Thực thi trong Task (Consumer) */
bool RingBuffer_ReadByte(uint8_t *out_data) {
    if (g_uart_rb.head == g_uart_rb.tail) {
        return false;  /* Buffer rỗng */
    }
    *out_data = g_uart_rb.buffer[g_uart_rb.tail];
    __DMB();
    g_uart_rb.tail = (g_uart_rb.tail + 1) & RING_BUFFER_MASK;
    return true;
}
```

#### 🌟 PATTERN 3: Zero-Copy Double-Buffering (Ping-Pong Buffer) Kết Hợp DMA
Sử dụng DMA để chuyển dữ liệu trực tiếp từ ngoại vi vào RAM mà **KHÔNG TỐN MỘT CHU KỲ CPU NÀO**. CPU chỉ nhận ngắt khi toàn bộ khối dữ liệu lớn (Block) đã sẵn sàng:

```
[NGOẠI VI ADC] ──(DMA Stream Chuyển Tự Động)──> [ BUFFER PING (1024 Samples) ] (Đang nạp)
                                                  [ BUFFER PONG (1024 Samples) ] (Task đang xử lý)
     │
     ▼ (Khi nạp xong Buffer Ping)
[DMA TRANSFER COMPLETE INTERRUPT (ISR)]
• ISR chỉ làm 1 việc duy nhất: Tráo đổi con trỏ Ping <-> Pong (Swap Buffer).
• Đánh thức Task xử lý Buffer Ping vừa nạp xong.
• Tải trọng CPU giảm từ 80% xuống dưới 2%!
```

---

<a name="ch15"></a>
## CHƯƠNG 15: PHÂN TÍCH HIỆU NĂNG & HỆ THỐNG REAL-TIME

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

### 15.3 Bài Toán Thiết Kế Ngân Sách CPU (CPU Load Budget Case Study)

#### 🚗 Đề bài: Thiết kế hệ thống nhúng điều khiển xe điện (EV Controller) trên vi điều khiển 168 MHz:
- **Ngoại vi 1:** UART Telemetry tốc độ **115200 baud** (1 byte mỗi 86.8 µs).
- **Ngoại vi 2:** Timer điều khiển vòng lặp định thời **1 kHz** (chu kỳ 1 ms).
- **Ngoại vi 3:** Bộ chuyển đổi ADC giám sát dòng điện pin **20 kHz** (chu kỳ 50 µs).

```
TÍNH TOÁN TẢI TRỌNG CPU (CPU LOAD ANALYSIS):

1. Phân tích cách thiết kế KÉM (Junior Approach - Xử lý từng byte trong ISR):
   • UART ISR (tốn 6 µs/lần): Load = 6 µs / 86.8 µs = 6.91%
   • Timer ISR (tốn 20 µs/lần): Load = 20 µs / 1000 µs = 2.00%
   • ADC ISR (tốn 15 µs/lần): Load = 15 µs / 50 µs = 30.00%
   ==> TỔNG TẢI TRỌNG ISR = 38.91% CPU chỉ dùng để phục vụ ngắt!
   ==> Nguy cơ: Jitter rất lớn, Task xử lý thuật toán chính bị trễ deadline!

2. Phân tích cách thiết kế XUẤT SẮC (Senior Architect Approach):
   • UART: Sử dụng DMA Circular + IDLE Line Interrupt.
     CPU chỉ ngắt 1 lần khi nhận đủ 1 gói tin 128 bytes (Load < 0.1%).
   • Timer: Tối ưu ISR rút gọn còn 1.5 µs (Load = 0.15%).
   • ADC: Sử dụng DMA Ping-Pong Buffer 1000 samples.
     CPU chỉ ngắt 1 lần mỗi 50 ms (Load < 0.05%).
   ==> TỔNG TẢI TRỌNG ISR GIẢM XUỐNG DƯỚI 0.5% CPU!
   ==> Hệ thống mượt mà, độ trễ tiệm cận 0, đáp ứng tuyệt đối chuẩn Real-Time!
```

---

<a name="ch16"></a>
## CHƯƠNG 16: 10 BÀI TẬP THỰC CHIẾN TĂNG DẦN ĐỘ KHÓ (LEVEL 1 → 10)

> [!IMPORTANT]
> **Hướng Dẫn:** Các bài tập dưới đây không cung cấp đáp án có sẵn. Bạn hãy tự tay debug, phân tích file `.map`, dùng GDB đọc thanh ghi và đo lường trên phần cứng/QEMU để rèn luyện tư duy Firmware Architect.

---

### 🟢 Level 1: Khám Phá Bảng Vector Table Thực Tế Qua GDB
* **Problem:** Dùng GDB kết nối vào target đang chạy firmware STM32F4.
* **Context:** Firmware đang chạy có bật ngắt TIM2 và USART1.
* **Constraints:** Không được mở mã nguồn C, chỉ được dùng lệnh GDB.
* **Expected Behavior:** Tìm ra địa chỉ chính xác của `TIM2_IRQHandler` và `USART1_IRQHandler`. Xác định giá trị Initial Stack Pointer nạp vào MSP.
* **What You Should Investigate:** Lệnh `x/64xw 0x08000000`, `x/xw 0xE000ED08`, `info symbol <address>`.

---

### 🟢 Level 2: Viết Trình Phục Vụ Ngắt Timer Bare-Metal Không Dùng HAL
* **Problem:** Viết hàm ngắt `TIM6_DAC_IRQHandler` để đảo trạng thái LED sau mỗi 500 ms mà không sử dụng bất kỳ hàm thư viện nào của STM32Cube HAL.
* **Context:** Board STM32F4 Discovery (Clock APB1 = 42 MHz, Timer Clock = 84 MHz).
* **Constraints:** Phải tự cấu hình trực tiếp qua thanh ghi: `RCC->APB1ENR`, `TIM6->PSC`, `TIM6->ARR`, `TIM6->DIER`, `NVIC->ISER`.
* **Expected Behavior:** LED nhấp nháy chính xác tần số 1 Hz. ISR thực thi dưới 15 chu kỳ xung nhịp.
* **What You Should Investigate:** Cơ chế xóa cờ ngắt `TIM6->SR`, thứ tự bật ngắt trong NVIC.

---

### 🟡 Level 3: Tự Động Bắt Lỗi Kẹt Trong `Default_Handler`
* **Problem:** Firmware thỉnh thoảng bị kẹt trong `Default_Handler` sau khi chạy được vài phút.
* **Context:** Dự án có tích hợp nhiều module ngoại vi nhưng một số ngắt chưa được viết hàm ISR.
* **Constraints:** Phải sửa đổi hàm `Default_Handler` để khi có lỗi, nó tự động in Exception Number qua UART hoặc lưu vào RAM trước khi dừng.
* **Expected Behavior:** Xác định được chính xác Exception Number nào là thủ phạm gây lỗi mà không cần mò mẫm.
* **What You Should Investigate:** Đọc thanh ghi `IPSR` (`__get_IPSR()`), tra cứu số IRQ.

---

### 🟡 Level 4: Tái Định Vị Vector Table Vào SRAM Tại Runtime
* **Problem:** Sau khi boot từ Flash, hãy copy toàn bộ bảng Vector Table vào vùng đầu SRAM (`0x20000000`), sau đó trỏ thanh ghi VTOR vào RAM.
* **Context:** Yêu cầu hệ thống cần thay đổi con trỏ hàm ngắt động khi chạy các chế độ test khác nhau.
* **Constraints:** Đảm bảo thỏa mãn quy tắc căn chỉnh địa chỉ (Alignment Rule) của VTOR. Không làm gián đoạn ngắt SysTick đang chạy.
* **Expected Behavior:** Ghi đè con trỏ hàm `TIM2_IRQHandler` trong RAM và quan sát CPU thực thi hàm mới mà không cần nạp lại Flash.
* **What You Should Investigate:** `memcpy`, `SCB->VTOR`, lệnh rào cản `__DSB()` và `__ISB()`.

---

### 🟡 Level 5: Xây Dựng Trình Chẩn Đoán HardFault Chuyên Nghiệp
* **Problem:** Viết một `HardFault_Handler` bằng Assembly kết hợp C để bóc tách toàn bộ khung thanh ghi Auto-stacking khi hệ thống bị crash.
* **Context:** Thiết bị lắp ngoài hiện trường (không thể cắm cáp Debug JTAG/SWD), chỉ có thể lưu log vào bộ nhớ Flash/EEPROM.
* **Constraints:** Phải phân biệt chính xác CPU đang dùng `MSP` hay `PSP` trước khi trích xuất giá trị `{R0-R3, R12, LR, PC, xPSR}`.
* **Expected Behavior:** In ra được chính xác địa chỉ câu lệnh (PC) gây ra lỗi và mã lỗi trong thanh ghi `SCB->CFSR`.
* **What You Should Investigate:** Kiểm tra Bit 2 của `EXC_RETURN` trong `LR`, đọc `SCB->CFSR`, `SCB->BFAR`.

---

### 🟠 Level 6: Xây Dựng Bootloader Tải Kép & Nhảy Ứng Dụng An Toàn
* **Problem:** Viết Bootloader tại `0x08000000` và Application tại `0x08008000`. Khi nhấn nút, ở lại Bootloader; khi thả nút, nhảy vào App.
* **Context:** Ứng dụng Application có sử dụng FreeRTOS và nhiều ngắt ngoại vi.
* **Constraints:** Sau khi nhảy vào App, toàn bộ ngắt của App phải hoạt động 100% trơn tru, không bị ảnh hưởng bởi Bootloader.
* **Expected Behavior:** Hoàn thành đầy đủ chuỗi 9 bước chuyển giao quyền: Reset NVIC, Reset SysTick, cập nhật MSP, nạp VTOR và nhảy Reset_Handler.
* **What You Should Investigate:** Hàm `Jump_To_Application()`, file Linker Script của Application (`ORIGIN = 0x08008000`).

---

### 🟠 Level 7: Thiết Kế Ring Buffer Lock-Free Tốc Độ Cao Cho UART RX
* **Problem:** Nhận luồng dữ liệu UART liên tục ở tốc độ **921600 baud** mà không bị mất bất kỳ byte nào (Zero Loss), CPU load < 5%.
* **Context:** Dữ liệu cảm biến truyền liên tục không ngừng nghỉ.
* **Constraints:** Không dùng hàm khóa Critical Section trong hàm ngắt.
* **Expected Behavior:** Sử dụng mô hình Single-Producer Single-Consumer (SPSC) Ring Buffer kết hợp rào cản bộ nhớ `__DMB()`.
* **What You Should Investigate:** Bitwise index wrapping (`& (SIZE - 1)`), từ khóa `volatile`, kiểm tra tràn bộ đệm.

---

### 🔴 Level 8: Phân Tích & Sửa Lỗi Nghẽn Bộ Lập Lịch FreeRTOS Do Ngắt
* **Problem:** Một hệ thống FreeRTOS có 1 Task điều khiển màn hình (Prio 2) và 1 Task xử lý mạng CAN (Prio 5). Khi gói tin CAN bay đến dồn dập, Task màn hình bị "đơ" hoàn toàn trong 2 giây.
* **Context:** Kỹ sư trước đó đã viết hàm `CAN_RX_IRQHandler` gửi dữ liệu vào Queue nhưng không dùng `portYIELD_FROM_ISR()`.
* **Constraints:** Phân tích bản chất tại sao việc thiếu `portYIELD_FROM_ISR` lại gây ra hiện tượng nghẽn lập lịch.
* **Expected Behavior:** Tối ưu lại ISR để Task CAN (Prio 5) xử lý tức thời và trả lại quyền cho Task màn hình mượt mà.
* **What You Should Investigate:** Cơ chế hoạt động của `xHigherPriorityTaskWoken` và ngắt `PendSV`.

---

### 🔴 Level 9: Thiết Kế Hệ Thống Ngắt Cho Hộp Điều Khiển Động Cơ Ô Tô (ECU)
* **Problem:** Thiết kế phân bổ toàn bộ mức ưu tiên (Priority Assignment Matrix) cho MCU STM32H7 (480 MHz) điều khiển xe điện:
  - Ngắt bảo vệ ngắt mạch quá dòng Inverter (Yêu cầu phản ứng < 1 µs).
  - Ngắt băm xung PWM điều khiển động cơ 20 kHz.
  - Ngắt nhận bản tin CAN FD an toàn (100 µs).
  - Ngắt định thời hệ thống FreeRTOS SysTick (1 ms).
  - Ngắt ghi log chẩn đoán UART (10 ms).
* **Constraints:** Xác định rõ `configMAX_SYSCALL_INTERRUPT_PRIORITY` nằm ở đâu và ngắt nào được phép gọi API FreeRTOS.
* **What You Should Investigate:** Preemption Priority vs Sub-Priority, Zero-Latency Interrupts.

---

### 🔴 Level 10: Điều Tra & Xử Lý Bug Bộ Nhớ Bí Ẩn Trên Thiết Bị Production
* **Problem:** Xe điện xuất xưởng chạy thử ngoài đường thực tế: Cứ sau khoảng 3 đến 4 tiếng hoạt động liên tục thì xe bị mất tín hiệu chân ga trong 200 ms rồi tự phục hồi. Hiện tượng xảy ra hoàn toàn ngẫu nhiên.
* **Context:** Không thể gắn Debugger. Chỉ có file Log ghi nhận trong bộ nhớ Flash vòng lặp (Blackbox Log).
* **Constraints:** Lập luận và đưa ra 4 giả thuyết gốc rễ (Root Cause Hypothesis) liên quan đến: Interrupt Storm, Priority Inversion, Tràn Stack ngầm trong nested interrupts, và tranh chấp biến chia sẻ thiếu `volatile`/`__DMB()`.
* **What You Should Investigate:** Xây dựng phương án chẩn đoán khoanh vùng và khắc phục triệt để.

---

<a name="ch17"></a>
## CHƯƠNG 17: SENIOR MINDSET — THẤU HIỂU BẢN CHẤT THAY VÌ HỌC THUỘC

### 10 Cặp Tư Duy Đối Nghịch Giữa Junior và Senior:

| # | Chủ Đề | Tư Duy Junior (Bề Nổi / Học Vẹt) | Tư Duy Senior Architect (Bản Chất Hệ Thống) |
|---|---|---|---|
| 1 | **Vector Table** | "Là danh sách các hàm ngắt trong file startup." | "Là giao diện phần cứng kết nối giữa không gian địa chỉ bộ nhớ và cơ chế phân giải ngoại lệ của CPU. Được quản lý bởi Linker Script và có thể tái định vị linh hoạt bằng VTOR." |
| 2 | **NVIC** | "Là hàm `HAL_NVIC_EnableIRQ()` trong thư viện." | "Là bộ điều phối phần cứng đa tầng trong lõi CPU chịu trách nhiệm phân xử ưu tiên, lồng ngắt (Nesting), nối đuôi ngắt (Tail-Chaining) và lọc ngưỡng khóa ngắt." |
| 3 | **Hàm ISR** | "Là một hàm C bình thường được gọi khi có sự kiện." | "Là một Exception Handler chạy ở Handler Mode với đặc quyền cao nhất, sử dụng Main Stack Pointer (MSP), tự động lưu trữ 8 thanh ghi và thoát ngắt bằng mã EXC_RETURN." |
| 4 | **Bật Ngắt** | "Chỉ cần gọi hàm Enable ngắt là xong." | "Là một chuỗi liên hoàn 7 mắt xích: Clock ➔ GPIO Pin ➔ Ngoại vi ➔ Cờ ngoại vi ➔ Mức ưu tiên ➔ Kênh NVIC ➔ Cờ ngắt toàn cục." |
| 5 | **Priority** | "Số lớn là ưu tiên cao." | "Hiểu rõ quy ước ngược: Trong ARM, số càng nhỏ ưu tiên càng cao. Nắm vững ranh giới giữa Preemption Priority và Sub-Priority." |
| 6 | **FreeRTOS & ISR** | "Gọi API nào cũng được miễn là code chạy." | "Tuyệt đối phân tách Handler Context và Thread Context. Luôn dùng API `...FromISR` và hiểu rõ vai trò điều phối trì hoãn của PendSV." |
| 7 | **HardFault** | "Lỗi khó hiểu, nhấn nút Reset cho nhanh." | "Là công cụ chẩn đoán giá trị nhất của CPU. Bóc tách khung Stack, đọc các thanh ghi CFSR/HFSR/BFAR để tìm ra chính xác dòng code và nguyên nhân gây lỗi." |
| 8 | **Độ Trễ Ngắt** | "Ngắt là chạy tức thời, không có độ trễ." | "Độ trễ ngắt là một hàm số xác định: Phụ thuộc chu kỳ lưu ngữ cảnh (12 cycles), trạng thái bus bộ nhớ, độ sâu ngắt lồng nhau và thời gian khóa Critical Section." |
| 9 | **Bootloader Jump** | "Chỉ cần ép kiểu con trỏ hàm rồi gọi địa chỉ App." | "Là một quy trình chuyển giao quyền nghiêm ngặt: Dọn dẹp ngoại vi cũ, tắt NVIC, vô hiệu hóa SysTick, nạp lại MSP từ Vector App, cấu hình VTOR và kiểm tra tính toàn vẹn Secure Boot." |
| 10 | **Tối Ưu Hóa** | "Code ngắn trong file C là tối ưu." | "Tối ưu hóa ở cấp độ vi kiến trúc: Đưa công việc nặng xuống Task (Bottom-Half), sử dụng DMA + Ring Buffer, tận dụng Tail-Chaining và đồng bộ rào cản bộ nhớ." |

---

<a name="ch18"></a>
## CHƯƠNG 18: MASTER DEBUG CHECKLIST & TÀI LIỆU THAM KHẢO

### 18.1 Master Checklist 20 Bước Chẩn Đoán Ngắt Chuyên Nghiệp

```
[GIAI ĐOẠN 1: THIẾT KẾ & LIÊN KẾT (BUILD TIME)]
 [ ] 1. Mảng `.isr_vector` có lệnh `KEEP()` trong Linker Script chưa?
 [ ] 2. Địa chỉ ORIGIN của Flash trong Linker Script có khớp với không gian nhớ phần cứng không?
 [ ] 3. Tên hàm ISR trong file `.c` có khớp 100% từng ký tự hoa/thường với file startup không?
 [ ] 4. Nếu dùng C++, hàm ISR đã được bọc trong khối `extern "C"` chưa?
 [ ] 5. Các biến chia sẻ giữa ISR và Main Thread đã có từ khóa `volatile` chưa?

[GIAI ĐOẠN 2: KHỞI TẠO HỆ THỐNG (RUNTIME INITIALIZATION)]
 [ ] 6. Bus Clock của ngoại vi đã được kích hoạt trong thanh ghi `RCC` chưa?
 [ ] 7. Các chân GPIO Alternate Function đã được cấu hình đúng Mode chưa?
 [ ] 8. Cờ ngắt nội bộ ngoại vi (ví dụ `UIE` trong Timer, `RXNEIE` trong UART) đã bật chưa?
 [ ] 9. Kênh ngắt trong NVIC (`NVIC->ISER`) đã được Enable chưa?
 [ ] 10. Mức ưu tiên ngắt trong NVIC (`NVIC->IPR`) đã được thiết lập đúng chưa?
 [ ] 11. Thanh ghi `SCB->VTOR` đã trỏ đúng vào địa chỉ của bảng Vector Table hiện tại chưa?
 [ ] 12. Cờ ngắt toàn cục đã được mở (`__enable_irq()`, PRIMASK = 0) chưa?

[GIAI ĐOẠN 3: THỰC THI HÀM ISR (IN-FLIGHT EXECUTION)]
 [ ] 13. Hàm ISR đã có lệnh xóa cờ ngắt phần cứng của ngoại vi (Clear Interrupt Flag) chưa?
 [ ] 14. Có lệnh đọc lại thanh ghi hoặc `__DSB()` để khắc phục độ trễ Write Buffer của Bus không?
 [ ] 15. Trong FreeRTOS, các hàm gọi trong ISR có đúng là phiên bản `...FromISR` không?
 [ ] 16. Đã gọi `portYIELD_FROM_ISR(xHigherPriorityTaskWoken)` ở cuối hàm ISR chưa?
 [ ] 17. Mức ưu tiên của ngắt có thấp hơn hoặc bằng `configMAX_SYSCALL_INTERRUPT_PRIORITY` khi dùng RTOS API không?

[GIAI ĐOẠN 4: CHẨN ĐOÁN SỰ CỐ & CRASH (FAULT RECOVERY)]
 [ ] 18. Khi rơi vào `Default_Handler`, đã đọc thanh ghi `IPSR` để xác định Exception Number chưa?
 [ ] 19. Khi rơi vào `HardFault`, đã trích xuất địa chỉ câu lệnh lỗi (Stacked PC) và đọc `SCB->CFSR` chưa?
 [ ] 20. Dung lượng Stack (MSP / Task PSP) có đủ lớn để chứa các khung ngắt lồng nhau (Nested Stacking) không?
```

---

### 18.2 Sơ Đồ Khái Niệm Tổng Thể (Master Mental Model)

```
+==================================================================================================+
|                        SƠ ĐỒ TỔNG QUAN KIẾN TRÚC XỬ LÝ NGẮT EMBEDDED                             |
+==================================================================================================+
                                                                                                    
   [NGOẠI VI PHẦN CỨNG] ──────(Kéo tín hiệu điện áp IRQ Line)──────┐                               
   (Timer, UART, CAN, ADC)                                         │                               
                                                                   ▼                               
                                           +─────────────────────────────────+                      
                                           |   NVIC (INTERRUPT CONTROLLER)   |                      
                                           | • Lọc kênh ngắt: NVIC->ISER     |                      
                                           | • Phân xử mức ưu tiên: NVIC->IPR|                      
                                           | • Quản lý Pending / Active      |                      
                                           +─────────────────────────────────+                      
                                                                   │                                
                                               (Gửi Exception Number & nIRQ)                        
                                                                   │                                
                                                                   ▼                                
                                           +─────────────────────────────────+                      
                                           |     LÕI CPU (ARM CORTEX-M)      |                      
                                           | • Kết thúc câu lệnh hiện tại    |                      
                                           | • Auto-stacking 8 thanh ghi     |                      
                                           | • Tra cứu SCB->VTOR             |                      
                                           +─────────────────────────────────+                      
                                                                   │                                
                                        (Đọc địa chỉ con trỏ hàm 32-bit từ Flash)                   
                                                                   │                                
                                                                   ▼                                
                                           +─────────────────────────────────+                      
                                           |   BẢNG VECTOR TABLE TRONG FLASH |                      
                                           | [0] Initial Stack Pointer (MSP) |                      
                                           | [1] Reset_Handler Address       |                      
                                           | ...                             |                      
                                           | [N] Peripheral_IRQHandler Addr  |                      
                                           +─────────────────────────────────+                      
                                                                   │                                
                                                     (Nhảy vào thực thi mã C)                       
                                                                   │                                
                                                                   ▼                                
                                           +─────────────────────────────────+                      
                                           |  HÀM PHỤC VỤ NGẮT (ISR IN C)    |                      
                                           | • Xóa cờ ngắt phần cứng         |                      
                                           | • Đẩy dữ liệu vào RingBuffer    |                      
                                           | • Đánh thức RTOS Task (FromISR) |                      
                                           | • Thoát ngắt bằng lệnh BX LR    |                      
                                           +─────────────────────────────────+                      
                                                                   │                                
                                                 (Auto-unstacking & Khôi phục)                      
                                                                   │                                
                                                                   ▼                                
                                           +─────────────────────────────────+                      
                                           |   CHƯƠNG TRÌNH CHÍNH / RTOS     |                      
                                           | • Task xử lý tiếp tục chạy      |                      
                                           +─────────────────────────────────+                      
+==================================================================================================+
```

---

### 18.3 Tài Liệu Tham Khảo Kỹ Thuật (Official References)

1. **ARM Limited:** *ARMv7-M Architecture Reference Manual* (DDI 0403E.e).
2. **ARM Limited:** *Cortex-M4 Technical Reference Manual* (DDI 0439D).
3. **Joseph Yiu:** *The Definitive Guide to ARM Cortex-M3 and Cortex-M4 Processors* (3rd Edition, Newnes).
4. **STMicroelectronics:** *PM0214 Programming Manual — STM32F3/F4/F7/L4 Cortex-M4 programming manual*.
5. **Real Time Engineers Ltd:** *FreeRTOS Reference Manual & Kernel Architecture Guide*.
6. **MISRA C:2012:** *Guidelines for the use of the C language in critical systems*.
7. **ISO 26262-6:** *Road vehicles — Functional safety — Part 6: Product development at the software level*.

---

*Tài liệu kỹ thuật chuyên sâu này được biên soạn cho mục đích nghiên cứu, đào tạo và phát triển hệ thống nhúng chất lượng cao. Bản quyền nội dung thuộc về Dự án Nghiên cứu & Phát triển Embedded Firmware Kiến trúc Chuyên sâu.*
