# BÁO CÁO KỸ THUẬT: TÍCH HỢP DUAL UART - VỪA IN LOG TERMINAL VỪA BẮN CAN SANG SAVVYCAN

> 📅 **Ngày cập nhật:** 25/08/2026  
> 🏷️ **Loại tài liệu:** Task Fix / Dual UART Architecture & Virtual CAN Integration  
> 📌 **File Diff tương ứng:** [fix.diff](fix.diff)  
> 📂 **Thư mục mã nguồn:** [src_before/](src_before/) $\leftrightarrow$ [src_after/](src_after/)  
> 🎯 **Tuân thủ quy tắc:** [rule.md](../rule.md) (Rule 3 & Rule 4).

---

## 1. THỰC TẾ NGÀNH Ô TÔ: TẠI SAO ECU THẬT PHẢI CẤU HÌNH TỰ BẬT LOG UART?

Trong quy trình phát triển phần mềm ô tô tiêu chuẩn (tuân thủ **ASPICE** và **ISO 26262 An Toàn Chức Năng**), các hãng chia phần mềm thành **2 phiên bản hoàn toàn khác nhau**:

### 1.1 Phiên bản Thương Mại Hàng Loạt (Production / Release Build - Nạp lên xe bán cho khách):
* **100% CỔNG UART LOG BỊ TẮT HOẶC XÓA BỎ.**
* **3 Lý do kỹ thuật sống còn:**
  1. **Nghẽn CPU làm trễ chu kỳ an toàn (Real-time Overhead):** Hàm `printf` trên vi điều khiển rất nặng (tốn từ $0.5\text{ ms} - 2\text{ ms}$ để format chuỗi). Nếu một Task phanh ABS hoặc điều khiển túi khí chạy chu kỳ $1\text{ ms}$ mà bị `printf` chiếm CPU, xe sẽ mất lái hoặc bung túi khí muộn $\rightarrow$ **Vi phạm nghiêm trọng ASIL-D**.
  2. **Bảo mật an ninh mạng (Automotive Cybersecurity - ISO 21434):** Không được để lộ thông tin bộ nhớ, khóa bảo mật (Security Keys) qua chân UART vật lý để tránh hacker cắm dây đọc trộm dữ liệu.
  3. **Tiết kiệm chân chip (Pin Limitation):** Các chân UART sẽ được tái sử dụng làm chân điều khiển GPIO hoặc cảm biến khác.
* *Cách đọc log trên xe thương mại:* Kỹ sư và thợ sửa xe đọc log chuẩn qua **UDS 0x19 (DTC mã lỗi)**, **Freeze Frame** hoặc module chuẩn **AUTOSAR DLT (Diagnostic Log and Trace)** qua cáp chẩn đoán OBD-II / Ethernet.

### 1.2 Phiên bản Thử Nghiệm / Nghiên Cứu (Debug / Development Build):
* Trong giai đoạn kỹ sư đang code và debug phần mềm trên bàn thí nghiệm (HIL / SIL Testbench), kỹ sư **BẮT BUỘC phải bật 1 hoặc nhiều cổng UART** (hoặc dùng mạch nạp JTAG Segger RTT / ARM ITM) để xem OS có bị quá tải không, thứ tự boot của BSW có đúng không.
* Vì vậy, mã nguồn tầng MCAL luôn cung cấp hàm cấu hình UART để lập trình viên tự bật/tắt theo cờ cấu hình.

---

## 2. CĂN CỨ KỸ THUẬT: TẠI SAO CHẮC CHẮN SỬA `Mcu.c` SẼ KÍCH HOẠT CỔNG LOG?

Việc cấu hình kích hoạt UART hoàn toàn dựa trên **3 dấu vết kỹ thuật (Traceability)** có sẵn trong mã nguồn dự án và đặc tả phần cứng của chip Texas Instruments Cortex-M3 (LM3S):

### 📌 Dấu vết 1: Chuỗi khởi tạo phần cứng từ hàm `main()`
Khi hệ thống boot, chuỗi gọi hàm diễn ra chính xác như sau:
1. `main()` $\rightarrow$ gọi `EcuM_Init()` $\rightarrow$ gọi hàm MCAL **`Mcu_InitClock(0)`** nằm trong file `as/com/as.infrastructure/arch/lm3s/mcal/Mcu.c`.
2. Tại hàm `Mcu_InitClock()`:
   ```c
   void Mcu_InitClock( const Mcu_ClockType ClockSetting ) {
       ...
       Usart_Init(); // 👈 ĐÂY CHÍNH LÀ NƠI KHỞI TẠO NGOẠI VI UART KHI CHIP VỪA BẬT NGUỒN
   }
   ```
👉 **Kết luận 1:** File `Mcu.c` là file **duy nhất** nắm quyền cấp xung clock và thiết lập chân GPIO cho bộ UART khi vi điều khiển vừa thức dậy.

### 📌 Dấu vết 2: Cơ chế "Retargeting" của thư viện C Runtime (`printf`)
Trong hệ thống nhúng, hàm `printf("...")` của trình biên dịch GCC **không tự in ra màn hình được**. Nó bắt buộc phải tìm một hàm phần cứng cấp thấp tên là **`__putchar(char ch)`** để đẩy từng ký tự ra ngoài.

Trong file `as/com/as.infrastructure/arch/lm3s/mcal/Mcu.c`, hàm này đã được định nghĩa sẵn:
```c
void __putchar(char ch)
{
    UARTCharPut(UART0_BASE, ch); // 👈 Đẩy ký tự vào thanh ghi truyền của UART0
}
```
👉 **Kết luận 2:** Toàn bộ lệnh `printf()` trong toàn bộ dự án đều chảy về hàm `__putchar()` trong `Mcu.c` để ghi vào cổng `UART0`.

### 📌 Dấu vết 3: Bản đồ thanh ghi phần cứng (Memory-Mapped I/O) của chip LM3S
Theo Datasheet của dòng vi điều khiển TI Stellaris LM3S (và mã nguồn mô phỏng của QEMU ARM):
* **`UART0_BASE = 0x4000C000`** (Nối vào chân PA0/PA1).
* **`UART1_BASE = 0x4000D000`** (Nối vào chân PD2/PD3).

Khi thêm đoạn mã sau vào `Mcu.c`:
```c
/* 1. Cấp xung cho khối phần cứng UART1 và Port D */
SysCtlPeripheralEnable(SYSCTL_PERIPH_UART1);
SysCtlPeripheralEnable(SYSCTL_PERIPH_GPIOD);

/* 2. Cấu hình chân PD2/PD3 làm chân truyền nhận UART1 */
GPIOPinTypeUART(GPIO_PORTD_BASE, GPIO_PIN_2 | GPIO_PIN_3);

/* 3. Cài đặt tốc độ Baudrate 115200 */
UARTConfigSetExpClk(UART1_BASE, SysCtlClockGet(), 115200, (UART_CONFIG_WLEN_8 | UART_CONFIG_STOP_ONE | UART_CONFIG_PAR_NONE));
```
👉 **Kết luận 3:** 
* Thanh ghi phần cứng `0x4000D000` (UART1) được kích hoạt 100%. 
* Khi chạy QEMU, tham số `-serial chardev:can0` (cổng serial thứ 2 trên dòng lệnh) sẽ tự động bắt lấy toàn bộ byte ghi vào địa chỉ `UART1_BASE` và bắn ra cổng `COM1` $\rightarrow$ SavvyCAN!

---

## 3. GIẢI PHÁP TỔNG THỂ: KIẾN TRÚC DUAL UART ĐỘC LẬP TRÊN QEMU

```
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│                          KIẾN TRÚC DUAL UART PHẦN CỨNG TRÊN QEMU                            │
│                                                                                             │
│  ┌────────────────────── VI ĐIỀU KHIỂN ARM CORTEX-M3 (QEMU) ─────────────────────────────┐  │
│  │                                                                                        │  │
│  │  [CỔNG 1: UART0] ──► printf(">>> [CAN Tx Event]...") ──► [TERMINAL CONSOLE (stdio)]    │  │
│  │                                                           (Xem Log khởi động & Debug)  │  │
│  │                                                                                        │  │
│  │  [CỔNG 2: UART1] ──► Can_SendSLCAN("t1808...\r") ────► [CỔNG ẢO COM1 ===> COM2]       │  │
│  │                                                           (SavvyCAN bắt & Vẽ đồ thị)   │  │
│  └────────────────────────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 4. CHI TIẾT CÁC THAY ĐỔI MÃ NGUỒN (`src_before` $\rightarrow$ `src_after`)

### 🔹 1. Khởi tạo đồng thời UART0 & UART1 trong `arch/lm3s/mcal/Mcu.c`
* **`UART0` (Chân PA0/PA1):** Dành riêng cho `printf` xuất ra màn hình console.
* **`UART1` (Chân PD2/PD3):** Dành riêng cho hàm `Can_SendSLCAN()` xuất gói tin nhị phân SLCAN.

### 🔹 2. Tách luồng truyền trong `arch/common/mcal/SCan.c`
Trong hàm `Can_Write()`:
1. Đóng gói chuỗi SLCAN (`t1808...`) $\rightarrow$ Gửi sang **`UART1`** (`Can_SendSLCAN`) $\rightarrow$ Bắn vào `COM1` $\rightarrow$ `COM2` $\rightarrow$ **SavvyCAN**.
2. Format chuỗi log tiếng Anh $\rightarrow$ Gửi sang **`UART0`** (`printf`) $\rightarrow$ In ra **màn hình Console Terminal**.

### 🔹 3. Tích hợp chu trình phát BMS & VCU trong `release/ascore/app/app.c`
* Task ứng dụng `TaskApp` định kỳ mỗi 100ms gửi 2 frame **BMS (ID `0x180`)** và **VCU (ID `0x200`)** khớp với file `Vehicle_Network.dbc`.

---

## 5. CÂU LỆNH CHẠY QEMU KÍCH HOẠT DUAL UART

```powershell
cd "C:\Users\liem.vu\Liem.vuOD\Study_AUTOSAR-main"
& "C:\Program Files\qemu\qemu-system-arm.exe" -M lm3s6965evb -kernel "as/build/nt/lm3s6965evb/ascore/lm3s6965evb.exe" -nographic -monitor none -serial mon:stdio -chardev serial,id=can0,path=COM1 -serial chardev:can0
```

* **Tham số `-serial mon:stdio`:** Nối UART0 vào màn hình Terminal (In log khởi động, log Task, log debug).
* **Tham số `-chardev serial,id=can0,path=COM1 -serial chardev:can0`:** Nối UART1 vào cổng `COM1` của SavvyCAN.

---

## 6. KẾT QUẢ ĐẠT ĐƯỢC

1. **Trên màn hình Terminal:**
   ```text
    start application BUILD @ Aug 25 2026
    cpu is little endian
    XCP MTA memory address 20000f70
   OSEK NM node ID is 1
   STDOUT  :TaskIdle is running
   >>> [CAN Tx Event] ID=0x101 DLC=8 Data=[07 DD 0C 0F 13 31 00 5A]
   >>> [CAN Tx Event] ID=0x180 DLC=8 Data=[4F 64 10 0E 96 00 41 00]
   >>> [CAN Tx Event] ID=0x200 DLC=8 Data=[03 2A 00 78 00 00 50 01]
   ```
2. **Trên màn hình SavvyCAN:**
   * Frame `0x180 BMS_Status` và `0x200 VCU_TorqueCmd` đổ về liên tục, giải mã đúng theo file DBC và vẽ đồ thị thời gian thực!
