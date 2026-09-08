# 00_BUILD_ENVIRONMENT_SETUP

## 1. Mục Đích & Tổng Quan

Trong các dự án phần mềm nhúng thông thường, việc biên dịch (build) đôi khi chỉ cần một Makefile đơn giản và một trình biên dịch (compiler) như GCC. Tuy nhiên, trong môi trường AUTOSAR (Automotive Open System Architecture), hệ thống build (Build Environment) thường phức tạp hơn rất nhiều. Điều này xuất phát từ các yêu cầu khắt khe của ngành công nghiệp ô tô:

- **Tính khả chuyển (Portability) cao:** AUTOSAR yêu cầu phần mềm có thể chạy trên nhiều nền tảng vi điều khiển (MCU) khác nhau (như Infineon AURIX, NXP S32K, STM32, v.v.). Hệ thống build phải dễ dàng chuyển đổi qua lại giữa các toolchain mà không làm phá vỡ kiến trúc phần mềm.
- **Tự động hóa sinh mã (Code Generation):** Cấu trúc AUTOSAR phụ thuộc rất nhiều vào các file cấu hình (ARXML). Hệ thống build cần phải tích hợp chặt chẽ với các công cụ sinh mã (Code Generators) để tạo ra mã nguồn C/C++ từ các file ARXML trước khi bước vào giai đoạn biên dịch thực sự.
- **Tính nhất quán và truy xuất nguồn gốc (Traceability):** Các tiêu chuẩn an toàn chức năng (như ISO 26262) đòi hỏi quá trình build phải có khả năng tái tạo (reproducible) và lưu vết rõ ràng.
- **Quy mô dự án lớn:** Các dự án AUTOSAR thường có hàng ngàn file mã nguồn, đòi hỏi một hệ thống build mạnh mẽ có khả năng phân tích sự phụ thuộc (dependency) chính xác và hỗ trợ biên dịch song song (parallel build) để giảm thời gian build.

**Danh sách các công cụ cần thiết & Phiên bản khuyên dùng:**

| Công cụ / Tool | Phiên bản (Version) | Mục đích sử dụng |
| :--- | :--- | :--- |
| **Python** | `3.9.x` đến `3.11.x` | Môi trường thực thi cho SCons và các script sinh mã. Không nên dùng 3.12 ngay vì một số thư viện cũ có thể chưa tương thích hoàn toàn. |
| **SCons** | `4.x.x` | Hệ thống build chính (Build System) được sử dụng để quản lý quá trình biên dịch trong dự án này. |
| **GCC ARM Toolchain** | `10.x` hoặc `12.x` | Trình biên dịch C/C++ cho các vi điều khiển họ ARM Cortex (như STM32). |
| **MinGW / MSYS2** | Bản mới nhất | Cung cấp môi trường POSIX và các build tools cơ bản trên Windows (như `make`, `gcc` cho Windows). |
| **WSL2 (Ubuntu)** | `22.04 LTS` | Cung cấp môi trường Linux native trên Windows để mô phỏng và chạy các ứng dụng POSIX, hỗ trợ build tốt hơn cho các board POSIX. |
| **QEMU ARM** | `8.x` hoặc `9.x` (`SoftwareFreedomConservancy.QEMU`) | Trình giả lập phần cứng vi điều khiển ARM Cortex-M trên Windows (chạy trực tiếp file firmware nhị phân `.exe`/`.s19` của chip thật). |
| **SavvyCAN** | `v220` (64-bit) | Phần mềm phân tích mạng CAN bus, giải mã file DBC và vẽ đồ thị tín hiệu thời gian thực. |
| **Git** | `2.3x` trở lên | Quản lý phiên bản mã nguồn. |

---

### 1.1 Nguyên Tắc Vàng Pháp Y: Bắt Buộc Build Full Source Các Board Quan Trọng Trước Khi Trace Code

> ⚠️ **CẢNH BÁO QUAN TRỌNG DÀNH CHO KỸ SƯ AUTOSAR & NGƯỜI HỌC:**  
> **"Source code tĩnh KHÔNG đại diện cho runtime behavior nếu chưa được Build và Sinh mã thành công."**  
> *(Nguyên tắc số 1 & số 2 — Hiến chương Pháp y Gemini Forensic Constitution).*

#### Bản chất kiến trúc sinh mã trong AUTOSAR (Code Generation Mechanism):
1. **Các file cấu hình XML/ARXML chỉ là siêu dữ liệu Compile-Time:**  
   Các thẻ như `<ISR>`, `<TASK>`, `<ALARM>`, `<PDU>` trong các file XML (`infrastructure.xml`, `can1_isr.xml`, `isr_can.xml`, `autosar.arxml`) **hoàn toàn không được CPU nạp hay thực thi tại runtime**.
2. **Mã nguồn C cấu hình chỉ xuất hiện SAU KHI BUILD:**  
   Toàn bộ mã nguồn C thực thi (`Os_Cfg.c`, `Os_Cfg.h`, `CanIf_Cfg.c`, `CanIf_Cfg.h`, `Com_Cfg.c`, mảng con trỏ hàm ngắt tĩnh `tisr_pc[]`, bảng ánh xạ PDU, biến quản lý Task/Alarm...) **KHÔNG HỀ TỒN TẠI** trong kho mã nguồn tĩnh ban đầu. Chúng chỉ được sinh ra bởi các công cụ sinh mã Python (`GenOS.py`, `GenCanIf.py`, `GenCom.py`) nằm tại thư mục `as/com/as.tool/` khi trình biên dịch SCons quét các file cấu hình tương ứng của từng board.
3. **Linker Map File xác thực hàm nào thực sự tồn tại trong Binary:**  
   Chỉ khi biên dịch và liên kết thành công, Linker mới sinh ra file `.map` (vd: `stm32f107vc.map`, `lm3s6965evb.map`). File này là bằng chứng pháp y duy nhất xác nhận hàm nào được cấp phát địa chỉ bộ nhớ (`.text`), hàm nào bị loại bỏ do dead-code stripping (`--gc-sections`).

#### Hậu quả nghiêm trọng nếu Trace Code khi chưa Build:
* **Ảo giác mã nguồn (Code Hallucination):** Bạn sẽ tìm kiếm những hàm không tồn tại (ví dụ: tìm `Can_1_RxIsr` khi board đang cấu hình `CAN1_RX0_IRQHandler`, hoặc tìm bảng `tisr_pc` trên board QEMU `lm3s6965evb` vốn có `ISR_NUM = 0`).
* **Trace nhầm file mẫu (Demo / Dead Code):** Dẫn chứng nhầm các file thư viện bên thứ ba (như STM32CubeMX HAL `stm32f1xx_it.c`) trong khi hệ thống đang chạy MCAL AUTOSAR thuần túy, hoặc ngược lại.
* **Đứt gãy chuỗi gọi hàm:** Không thể đối chiếu địa chỉ và chỉ số mảng con trỏ hàm (`tisr_pc[intno - 16]()`).

#### Quy tắc bắt buộc trước khi trace bất kỳ Chuyên đề nào:
Trước khi phân tích dòng chảy mã nguồn trong bất kỳ tài liệu nào (`docs/theory/` hoặc `docs/hands_on_tasks/`), **BẮT BUỘC PHẢI CHẠY BUILD HOÀN CHỈNH CHO CÁC BOARD NỀN TẢNG**:
1. **`board=lm3s6965evb`**: Board ảo giả lập QEMU ARM Cortex-M3 (chuyên đề OS, Scheduler, Timer/Counter, Alarm, Conformance Classes, ComStack mô phỏng).
2. **`board=stm32f107vc`**: Board vi điều khiển phần cứng ARM Cortex-M3 (chuyên đề MCAL Driver, ngoại vi phần cứng, ngắt NVIC, USB-CAN Gateway).
3. **`board=posix`**: Board mô phỏng trên Linux / WSL2 (chuyên đề Native POSIX Threads & SocketCAN).

---

## 2. Windows Setup (Primary)

### 2.1 Python Installation

Python là xương sống của hệ thống build dựa trên SCons và các script Python sinh mã.
- **Tại sao chọn Python 3.9+ thay vì 3.12?** Python 3.9 hoặc 3.10 mang lại sự ổn định và tương thích tốt nhất với hầu hết các thư viện kỹ thuật số cũ. Python 3.12 loại bỏ một số module tiêu chuẩn cũ và thay đổi API, có thể làm gãy (break) các script legacy trong hệ sinh thái AUTOSAR.
- **Tải và Cài đặt:**
  1. Truy cập [python.org](https://www.python.org/downloads/) và tải bộ cài đặt Python 3.9.x hoặc 3.10.x.
  2. Khi chạy bộ cài, **BẮT BUỘC** phải tích chọn hộp kiểm: `Add Python 3.x to PATH` ở dưới cùng trước khi nhấn "Install Now".
- **Kiểm tra cài đặt (Verify):**
  Mở PowerShell hoặc Command Prompt và gõ:
  ```powershell
  python --version
  # Output mong đợi: Python 3.9.13 (hoặc tương tự)
  pip --version
  # Output mong đợi: pip 22.x.x from ... (python 3.9)
  ```
- **Cài đặt các gói phụ thuộc (Dependencies):**
  ```powershell
  pip install scons pyserial lxml jinja2
  ```
  *(Giải thích: `scons` là build tool, `pyserial` dùng để giao tiếp UART/Flash, `lxml` để parse XML/ARXML hiệu năng cao, `jinja2` là template engine dùng cho việc sinh code).*

### 2.2 SCons Build System

- **SCons là gì?** SCons là một công cụ xây dựng phần mềm (build tool) mã nguồn mở, thế hệ mới. Thay vì sử dụng ngôn ngữ đặc tả riêng biệt như Make hay CMake, SCons sử dụng trực tiếp ngôn ngữ Python.
- **Tại sao AUTOSAR lại ưa chuộng SCons?**
  1. **Tính linh hoạt:** Vì script của SCons là mã Python chuẩn, bạn có thể dễ dàng viết các logic phức tạp (như parse ARXML, gọi external tools) trực tiếp trong script build.
  2. **Quản lý dependency tự động:** SCons tích hợp sẵn bộ quét (scanner) cho C/C++ để tự động tìm ra các file header phụ thuộc mà không cần khai báo thủ công.
  3. **Đa nền tảng:** Chạy tốt trên cả Windows và Linux mà không cần cài đặt Cygwin (nếu chỉ dùng compiler có sẵn).
- **Cài đặt:**
  ```powershell
  pip install scons
  ```
- **Verify:**
  ```powershell
  scons --version
  ```
- **Cấu trúc cấu hình SCons:**
  - `SConstruct`: File gốc (tương đương Makefile ở thư mục root). Khi bạn gọi lệnh `scons`, nó sẽ tìm file này đầu tiên.
  - `SConscript`: Các file cấu hình con nằm ở các thư mục module (như `Com/SConscript`, `Os/SConscript`). Chúng được gọi bởi `SConstruct` để build từng thành phần riêng lẻ, giúp module hóa hệ thống build.

### 2.3 GCC ARM Toolchain (cho STM32 target)

Để biên dịch mã nguồn chạy trên vi điều khiển (VD: STM32), chúng ta cần trình biên dịch chéo (Cross-Compiler).
- **Bare-metal toolchain vs Linux toolchain:**
  - `arm-none-eabi-gcc`: Dùng cho hệ thống nhúng "bare-metal" hoặc chạy RTOS (như AUTOSAR OS, FreeRTOS). Nó không phụ thuộc vào hệ điều hành nền (OS-less).
  - `arm-linux-gnueabihf-gcc`: Dùng để compile các ứng dụng chạy trên hệ điều hành Linux nhúng.
  Trong AUTOSAR (trừ Adaptive AUTOSAR), chúng ta dùng loại bare-metal `arm-none-eabi-gcc`.
- **Cài đặt:**
  1. Tải toolchain từ [ARM Developer Website](https://developer.arm.com/downloads/-/arm-gnu-toolchain-downloads). Chọn bản dùng cho Windows (AArch32 bare-metal target - `arm-none-eabi`). Phiên bản 10.x thường rất ổn định.
  2. Chạy file `.exe` cài đặt. Nhớ chọn tùy chọn **Add path to environment variables** ở bước cuối.
- **Verify:**
  ```powershell
  arm-none-eabi-gcc --version
  ```

### 2.4 MinGW / MSYS2 (cho build tools trên Windows)

Đối với một số tác vụ cần biên dịch các công cụ hỗ trợ chạy trực tiếp trên Windows (Host tools) hoặc môi trường POSIX giả lập.
- **Cài đặt:** Tải từ [msys2.org](https://www.msys2.org/) và cài đặt vào thư mục mặc định `C:\msys64`.
- **Cài các gói (Packages):** Mở MSYS2 MSYS terminal và chạy:
  ```bash
  pacman -S mingw-w64-x86_64-toolchain make
  ```
- **PATH Configuration:** Cần thêm `C:\msys64\mingw64\bin` và `C:\msys64\usr\bin` vào biến môi trường PATH của Windows để PowerShell có thể nhận diện.

### 2.5 WSL2 (Recommended cho POSIX board)

Đối với quá trình mô phỏng (simulation) board POSIX (chạy AUTOSAR OS trên môi trường POSIX), việc sử dụng môi trường Linux thực thụ thông qua WSL2 (Windows Subsystem for Linux 2) mang lại hiệu năng cao và ít lỗi hơn rất nhiều so với dùng MSYS2.
- **Enable WSL2 & Cài Ubuntu:**
  Mở PowerShell as Administrator:
  ```powershell
  wsl --install
  ```
  *(Quá trình này sẽ tự động cài Ubuntu mặc định).*
- **Cài đặt Dependencies trong Ubuntu:**
  Mở terminal Ubuntu và chạy:
  ```bash
  sudo apt-get update
  sudo apt-get install build-essential python3 python3-pip scons gcc
  ```
- **Truy cập thư mục Windows từ WSL2:**
  Phân vùng ổ C của Windows được mount tự động tại `/mnt/c/`. Do đó, bạn có thể truy cập dự án bằng cách:
  ```bash
  cd /mnt/c/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main
  ```
- **Tại sao nên dùng WSL2 cho POSIX board?** AUTOSAR OS mô phỏng trên POSIX tận dụng các API hệ thống (signals, pthreads, timers) của Linux. Windows không có các khái niệm này một cách tự nhiên. WSL2 cung cấp một Kernel Linux thực sự, do đó OS chạy ổn định, chính xác về thời gian và dễ debug bằng GDB trên Linux hơn.

---

### 2.6 QEMU ARM Emulator (Giả Lập Vi Điều Khiển ARM Cortex-M Trên Windows)

QEMU (*Quick Emulator*) là phần mềm máy ảo / giả lập phần cứng mã nguồn mở tiêu chuẩn công nghiệp. `qemu-system-arm` cho phép bạn giả lập hoàn chỉnh một con chip vi điều khiển ARM Cortex-M3/M4 (CPU, Flash, RAM, NVIC Interrupts, Timers, UART) ngay trên Windows mà không cần bo mạch vật lý.

- **Tại sao QEMU ARM sát với máy thật nhất?**
  1. Chạy trực tiếp mã nhị phân máy ARM Thumb-2 do `arm-none-eabi-gcc` biên dịch.
  2. Mô phỏng đúng cơ chế chuyển ngữ cảnh của AUTOSAR OS (`PendSV`, `SVC`, cất thanh ghi `R0-R15`).
  3. Bắt đúng lỗi tràn Stack (HardFault) và giới hạn bộ nhớ vật lý của chip.
- **Cài đặt qua Windows Package Manager (winget):**
  Mở PowerShell và chạy lệnh:
  ```powershell
  winget install SoftwareFreedomConservancy.QEMU --accept-source-agreements --accept-package-agreements
  ```
- **Kiểm tra cài đặt (Verify):**
  ```powershell
  qemu-system-arm --version
  # Output mong đợi: QEMU emulator version 8.x / 9.x
  ```
- **Lệnh chạy Firmware ECU AUTOSAR trong QEMU:**
  ```powershell
  # Chạy firmware STM32/Cortex-M và chuyển hướng UART log ra màn hình console:
  qemu-system-arm -M lm3s6965evb -kernel as/build/nt/stm32f107vc/ascore/stm32f107vc.exe -serial stdio
  ```
- **Gỡ lỗi từng bước với GDB (Step-by-Step Hardware Debugging):**
  ```powershell
  # Terminal 1: Khởi động QEMU ở chế độ debug chờ GDB (cổng 1234):
  qemu-system-arm -M lm3s6965evb -kernel as/build/nt/stm32f107vc/ascore/stm32f107vc.exe -s -S -serial stdio

  # Terminal 2: Kết nối GDB để đặt breakpoint tại EcuM_Init() hoặc Com_SendSignal():
  arm-none-eabi-gdb as/build/nt/stm32f107vc/ascore/stm32f107vc.exe -ex "target remote localhost:1234"
  ```

### 2.7 SavvyCAN & Virtual Serial Ports (Cổng CAN Ảo Phục Vụ Kiểm Thử SIL)

Để kiểm thử truyền nhận mạng CAN, chẩn đoán UDS và nạp file DBC mà không cần phần cứng CAN Analyzer đắt tiền (như Vector VN1630 / PCAN):

- **Tải và Cài đặt SavvyCAN:**
  1. Tải bản Portable cho Windows từ GitHub: [SavvyCAN Releases](https://github.com/collin80/SavvyCAN/releases).
  2. Giải nén vào thư mục `C:\Users\liem.vu\tools\SavvyCAN\` và chạy `SavvyCAN.exe`.
- **Tạo Cặp Cổng Nối Tiếp Ảo (Virtual Serial Pair):**
  Sử dụng công cụ **com0com** hoặc **VSPE** để tạo 1 cặp cổng:
  * `COM1`: Dành cho ECU Simulator / Python test script bắn frame qua giao thức SLCAN.
  * `COM2`: Dành cho SavvyCAN kết nối đón bắt frame.
- **Cấu hình SavvyCAN:**
  * Menu `Connection` $\rightarrow$ `Open Connection Window` $\rightarrow$ `Add New Device Connection`.
  * Chọn kiểu: `SLCAN (Serial CAN)` | Cổng: `COM2` | Baudrate: `115200` | CAN Speed: `500000 bps`.
  * Gán file DBC: Vào `DBC File` $\rightarrow$ `DBC Manager` $\rightarrow$ Nạp file `Vehicle_Network.dbc` $\rightarrow$ Gán vào `Bus 0`.
  * Tích chọn `[x] Interpret Frames` để tự động giải mã các tín hiệu (*SoC, Điện áp, Tốc độ*).

---

## 3. Environment Configuration

### 3.1 PATH Variables (Windows)

Biến PATH cho biết hệ điều hành tìm kiếm các lệnh thực thi ở đâu.
- **Kiểm tra PATH hiện tại:**
  ```powershell
  $env:PATH -split ';' | Where-Object { $_ -match 'python|gcc|scons' }
  ```
- **Thiết lập PATH vĩnh viễn qua PowerShell:**
  (Yêu cầu chạy PowerShell với quyền Administrator):
  ```powershell
  # Lấy PATH cấp System
  $oldPath = [System.Environment]::GetEnvironmentVariable('PATH', 'Machine')
  # Thêm đường dẫn MSYS2
  $newPath = $oldPath + ';C:\msys64\mingw64\bin'
  [System.Environment]::SetEnvironmentVariable('PATH', $newPath, 'Machine')
  ```
  *(Lưu ý: Sau khi thay đổi, bạn phải mở lại cửa sổ PowerShell mới để nhận giá trị PATH mới).*

### 3.2 PYTHONPATH Configuration

- **Khi nào cần set PYTHONPATH?**
  Biến môi trường `PYTHONPATH` được sử dụng để chỉ định thư mục chứa các module Python tùy chỉnh (custom modules) mà không cài đặt qua `pip`. Trong dự án AUTOSAR, các công cụ sinh mã (code generators) thường sử dụng các script nằm rải rác. Nếu SCons hoặc một script báo lỗi `ModuleNotFoundError` đối với một module nội bộ, bạn cần khai báo PYTHONPATH.
- **Ví dụ cụ thể:**
  Nếu bộ sinh mã nằm ở `C:\Users\liem.vu\Liem.vuOD\Study_AUTOSAR-main\tools\scripts`, bạn cấu hình bằng:
  ```powershell
  $env:PYTHONPATH = "C:\Users\liem.vu\Liem.vuOD\Study_AUTOSAR-main\tools\scripts"
  ```
  Để thiết lập vĩnh viễn (User level):
  ```powershell
  [System.Environment]::SetEnvironmentVariable('PYTHONPATH', 'C:\Users\liem.vu\Liem.vuOD\Study_AUTOSAR-main\tools\scripts', 'User')
  ```

---

## 4. Hướng Dẫn Build Chi Tiết Các Board Quan Trọng Trước Khi Trace Code

Mọi quá trình phân tích và trace code trong dự án `Study_AUTOSAR` bắt buộc phải dựa trên các tệp đã được sinh ra (generated files) và liên kết thành công trong thư mục `as/build/nt/<board>/ascore/`. Dưới đây là quy trình build chi tiết cho từng board mục tiêu:

---

### 4.1 Board Ảo QEMU (`board=lm3s6965evb`) — Nghiên Cứu OS, Scheduler & Conformance Classes

Board này sử dụng kiến trúc ARM Cortex-M3 giả lập, là môi trường chính để chạy kiểm thử SIL (Software-in-the-Loop) và phân tích nhân hệ điều hành `askar`.

```powershell
# Bước 1: Mở Windows PowerShell và di chuyển vào thư mục as
cd C:\Users\liem.vu\Liem.vuOD\Study_AUTOSAR-main\as

# Bước 2: Thực hiện build mục tiêu board lm3s6965evb
scons board=lm3s6965evb
```

* **Sản phẩm sinh mã kiểm chứng bắt buộc (Must-Verify Artifacts):**
  1. `as/build/nt/lm3s6965evb/ascore/config/Os_Cfg.c` & `Os_Cfg.h`:
     * Chứa cấu hình tĩnh các Task (`TaskIdle`, `SchM_Startup`, `SchM_BswService`).
     * Chú ý: `#define ISR_NUM 0` (board này dùng CAN Polling qua `SCan.c`, không sinh mảng `tisr_pc`).
  2. `as/build/nt/lm3s6965evb/ascore/lm3s6965evb.map`: File bản đồ bộ nhớ để tra cứu địa chỉ các symbol.
  3. `as/build/nt/lm3s6965evb/ascore/lm3s6965evb.exe`: File firmware nhị phân ARM ELF chạy trực tiếp trên QEMU.

* **Lệnh khởi chạy giả lập QEMU:**
  ```powershell
  qemu-system-arm -M lm3s6965evb -kernel build/nt/lm3s6965evb/ascore/lm3s6965evb.exe -serial stdio
  ```

---

### 4.2 Board Phần Cứng Vi Điều Khiển Thật (`board=stm32f107vc`) — Nghiên Cứu MCAL & Ngắt NVIC

Board này đại diện cho vi điều khiển ô tô thực tế với đầy đủ phần cứng ngoại vi (CAN Controller, NVIC, Port, Dio, USB CDC).

```powershell
# Bước 1: Mở Windows PowerShell và di chuyển vào thư mục as
cd C:\Users\liem.vu\Liem.vuOD\Study_AUTOSAR-main\as

# Bước 2: Thực hiện build mục tiêu board stm32f107vc
scons board=stm32f107vc
```

* **Sản phẩm sinh mã kiểm chứng bắt buộc (Must-Verify Artifacts):**
  1. `as/build/nt/stm32f107vc/ascore/config/Os_Cfg.c` & `Os_Cfg.h`:
     * Chứa `#define ISR_NUM 68`.
     * Dòng 29: `extern void ISR_ATTR CAN1_RX0_IRQHandler (void);`
     * Dòng 602: `ISR_ADDR(CAN1_RX0_IRQHandler), /* 20 */` (được sinh ra từ `can1_isr.xml`).
  2. `as/build/nt/stm32f107vc/ascore/stm32f107vc.map`: File ánh xạ bộ nhớ kiểm chứng hàm `CAN1_RX0_IRQHandler` (tại `0x00010084`) và `HAL_CAN_IRQHandler` (tại `0x000104d8`).
  3. `as/build/nt/stm32f107vc/ascore/stm32f107vc.exe`: File firmware nhị phân nạp chip thật hoặc nạp qua ST-Link/J-Link.

---

### 4.3 Board Mô Phỏng POSIX (`board=posix`) — Nghiên Cứu Trên Môi Trường Linux / WSL2

Board này chạy trực tiếp trên Kernel Linux của WSL2, tận dụng cơ chế POSIX Thread (`pthread`) và SocketCAN.

```bash
# Thực hiện bên trong Ubuntu (WSL2)
cd /mnt/c/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as
scons board=posix
```

* **Sản phẩm sinh mã kiểm chứng:**
  * File thực thi native Linux: `build/posix/as`
  * Chạy thử: `./build/posix/as`

---

### 4.4 Bảng Tổng Hợp Sản Phẩm Sinh Mã Tĩnh Bắt Buộc Kiểm Chứng Trước Khi Trace Code

| Hạng mục kiểm tra | Board QEMU `lm3s6965evb` | Board Vi Điều Khiển Thật `stm32f107vc` | Board POSIX Simulator `posix` |
| :--- | :--- | :--- | :--- |
| **Mục đích nghiên cứu** | OS, Scheduling, Alarm, ECC2 | Hardware Interrupt, NVIC, MCAL, USB-CAN | SocketCAN, Linux simulation, POSIX Threads |
| **Lệnh Build** | `scons board=lm3s6965evb` | `scons board=stm32f107vc` | `scons board=posix` (WSL2) |
| **Trình biên dịch** | `arm-none-eabi-gcc` | `arm-none-eabi-gcc` | `gcc` (Ubuntu Native) |
| **File cấu hình sinh ra** | `build/nt/lm3s6965evb/ascore/config/Os_Cfg.c` | `build/nt/stm32f107vc/ascore/config/Os_Cfg.c` | `build/posix/config/Os_Cfg.c` |
| **Mảng con trỏ ngắt `tisr_pc`** | Không sinh ra (`ISR_NUM = 0`, dùng CAN Polling) | Sinh ra `tisr_pc[68]`, index 20 chứa `CAN1_RX0_IRQHandler` | Không có phần cứng NVIC |
| **Linker Map File** | `build/nt/lm3s6965evb/ascore/lm3s6965evb.map` | `build/nt/stm32f107vc/ascore/stm32f107vc.map` | `build/posix/as.map` |
| **File nhị phân cuối** | `lm3s6965evb.exe` (chạy trên QEMU) | `stm32f107vc.exe` (nạp chip thật) | `as` (chạy trên WSL2 terminal) |

---

### 4.5 Quy Trình Pháp Y 3 Bước Trước Khi Bắt Đầu Trace Code (Pre-Trace Verification Workflow)

Khi tiến hành đọc hiểu hoặc viết báo cáo phân tích mã nguồn cho bất kỳ chức năng nào:

1. **Bước 1 — Build Xác Thực:**  
   Chạy lệnh `scons board=<target>` tương ứng. Đảm bảo terminal kết thúc bằng `scons: done building targets.` mà không có lỗi.
2. **Bước 2 — Mở File C/H Đã Sinh Ra:**  
   Truy cập trực tiếp vào `as/build/nt/<target>/ascore/config/` để kiểm tra các file `Os_Cfg.c`, `CanIf_Cfg.c`, `Com_Cfg.c`. Đọc trực tiếp các macro, mảng con trỏ hàm, và tên hàm extern. **Tuyệt đối không suy đoán nội dung từ file XML.**
3. **Bước 3 — Đối Chiếu File `.map`:**  
   Mở file `<target>.map`, tìm kiếm symbol của hàm cần trace (ví dụ: `Ctrl+F` tìm `CAN1_RX0_IRQHandler`, `Can_RxIsr`, `Com_SendSignal`). Nếu symbol có địa chỉ thuộc phân vùng `.text`, hàm đó mới thực sự tham gia vào runtime execution.

---

## 5. Troubleshooting — Windows Specific

### Lỗi 1: `scons: command not found` (Hoặc 'scons' is not recognized)
- **Triệu chứng:** SCons không nhận ra lệnh sau khi đã chạy `pip install scons`.
- **Nguyên nhân:** Thư mục chứa các file thực thi (Scripts) của Python chưa được thêm vào biến môi trường PATH của Windows.
- **Fix (Cách khắc phục):**
  Thêm đường dẫn `C:\Users\<Your_User>\AppData\Local\Programs\Python\Python39\Scripts` (hoặc đường dẫn tương ứng với phiên bản Python của bạn) vào biến PATH trong System Properties của Windows. Khởi động lại terminal.

### Lỗi 2: `arm-none-eabi-gcc: No such file`
- **Triệu chứng:** Biên dịch lỗi ngay từ đầu khi chọn target là vi điều khiển (VD: `scons --board=stm32f107vc`).
- **Nguyên nhân:** Trình biên dịch ARM chưa được cài đặt, hoặc thư mục `bin` của nó chưa nằm trong biến PATH.
- **Fix:**
  Download toolchain từ [developer.arm.com](https://developer.arm.com/downloads/-/arm-gnu-toolchain-downloads). Cài đặt và đảm bảo tích chọn add vào PATH (hoặc thêm thủ công `C:\Program Files (x86)\Arm GNU Toolchain arm-none-eabi\10.3\bin` vào PATH).

### Lỗi 3: `ModuleNotFoundError: No module named 'lxml'`
- **Triệu chứng:** Các script parse ARXML thất bại và văng lỗi Python stack trace thiếu module.
- **Fix:**
  Mở terminal và chạy lệnh để cài đặt các thư viện thiếu:
  ```powershell
  pip install lxml pyserial jinja2
  ```

### Lỗi 4: `Permission denied` (Windows)
- **Triệu chứng:** SCons báo lỗi không thể ghi đè file object `.o` hoặc file thực thi `.exe`, hoặc lỗi Access Denied khi chạy script.
- **Nguyên nhân:** Có thể ứng dụng cũ vẫn đang chạy ngầm (chưa tắt) chiếm quyền khóa file, hoặc do phân quyền thư mục.
- **Fix:**
  - Đảm bảo bạn đã tắt chương trình đang chạy.
  - Chạy PowerShell với quyền Administrator (Run as Administrator).
  - Thay vì dùng Windows, chuyển sang dùng WSL2 sẽ hiếm khi gặp lỗi về lock file như vậy.

### Lỗi 5: Python version conflict
- **Vấn đề:** SCons yêu cầu Python 3.x, nhưng trong hệ thống có cài đặt sẵn Python 2.7 (do phần mềm khác yêu cầu) và biến PATH đang ưu tiên Python 2.7.
- **Triệu chứng:** Lỗi cú pháp Python ngay khi chạy SCons (như lỗi thiếu dấu ngoặc trong hàm `print()`).
- **Fix:**
  Sử dụng cách gọi Python 3 một cách rõ ràng (explicitly):
  ```powershell
  python3 -m scons
  ```
  Hoặc thiết lập một môi trường ảo (Virtual Environment):
  ```powershell
  python -m venv autosar_env
  autosar_env\Scripts\activate
  pip install scons
  scons
  ```

### Lỗi 7: "This app can't run on your PC" khi chạy file `.exe` trong thư mục `build/`
- **Triệu chứng:** Khi nhấp đúp hoặc chạy `as/build/nt/stm32f107vc/ascore/stm32f107vc.exe`, Windows hiện hộp thoại: *"This app can't run on your PC"*.
- **Nguyên nhân:** File `stm32f107vc.exe` là **Mã nhị phân máy ARM Cortex-M3 (ELF Firmware)** do `arm-none-eabi-gcc` biên dịch cho vi điều khiển nhúng, KHÔNG PHẢI là file thực thi Windows x86/x64. CPU máy tính (Intel/AMD) không thể chạy trực tiếp tập lệnh này mà không có trình giả lập.
- **Fix (Cách khắc phục):**
  1. Dùng trình giả lập **QEMU ARM** để chạy: `qemu-system-arm -M lm3s6965evb -kernel as/build/nt/stm32f107vc/ascore/stm32f107vc.exe -serial stdio`.
  2. Hoặc nạp file `stm32f107vc.exe.s19` vào bo mạch thật qua ST-Link / J-Link.
  3. Hoặc kiểm thử mạng qua kịch bản Software-in-the-Loop (`send_virtual_can.py`) kết nối với SavvyCAN.

### Lỗi 8: `OSError: 'pkg-config --cflags gtk+-3.0' exited 1` khi build target `posix` trên Windows
- **Triệu chứng:** Chạy `$env:BOARD="posix"; scons` trên Windows PowerShell bị văng lỗi thiếu `which`, `uname` và `pkg-config gtk+-3.0`.
- **Nguyên nhân:** Target `BOARD="posix"` được thiết kế riêng cho môi trường Linux/POSIX (yêu cầu thư viện đồ họa GTK3 và SocketCAN).
- **Fix:**
  - Trên Windows native: Dùng target vi điều khiển thực tế **`$env:BOARD="stm32f107vc"`** (sử dụng GCC ARM đã cài sẵn, build sạch 100%).
  - Nếu muốn chạy POSIX simulator: Mở **WSL2 (Ubuntu 22.04)** và chạy `export BOARD=posix && scons`.

### Lỗi 6: Long path issue trên Windows
- **Vấn đề:** Quá trình giải nén hoặc build báo lỗi không tìm thấy đường dẫn (Path too long).
- **Nguyên nhân:** Mặc định Windows giới hạn độ dài đường dẫn file (MAX_PATH) là 260 ký tự. Cấu trúc thư mục AUTOSAR thường có số tầng sâu và tên package dài.
- **Fix:**
  Mở PowerShell dưới quyền Admin và chạy lệnh sau để kích hoạt Long Paths:
  ```powershell
  Set-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem" -Name "LongPathsEnabled" -Value 1
  ```

---

## 6. Verification Checklist

Bạn hãy chạy tuần tự các lệnh sau trên PowerShell/WSL2 để đảm bảo môi trường đã hoàn toàn sẵn sàng.

| Lệnh Kiểm Tra (Command) | Môi Trường | Expected Output (Kết quả mong đợi) | Trạng Thái Thực Tế |
| :--- | :--- | :--- | :--- |
| `python --version` | Win | `Python 3.9.x` đến `3.12.x` | [x] Đã cấu hình & hoạt động (`Python 3.12.3`) |
| `pip --version` | Win | `pip 2x.x from ...` | [x] Đã cấu hình & hoạt động (`pip 25.2`) |
| `scons --version` | Win | `SCons by Steven Knight... v4.x.x` | [x] Đã cài đặt & hoạt động (`SCons v4.11.1`) |
| `arm-none-eabi-gcc --version` | Win | `arm-none-eabi-gcc 10.x` đến `14.x` | [x] Đã cài đặt qua winget & thêm PATH (`v14.2.Rel1`) |
| `qemu-system-arm --version` | Win | `QEMU emulator version 8.x` đến `11.x` | [x] Đã cài đặt qua winget & thêm PATH (`v11.1.0`) |
| `gcc --version` | Win (MSYS2) | `gcc (Rev6, Built by MSYS2...) 13.x` | [x] Đã cấu hình MSYS2 PATH & unzip (`v13.2.0`) |
| `python -c "import lxml, jinja2, serial, SCons; print('OK')"` | Win | `OK` (Không có lỗi báo đỏ) | [x] Đã cài đủ dependencies & polyfill `collections.abc` |
| `$env:BOARD="lm3s6965evb"; scons` | Win | `scons: done building targets.` | [x] Đã sinh mã & build thành công, chạy QEMU verified |
| `$env:BOARD="stm32f107vc"; scons` | Win | `scons: done building targets.` | [x] Đã sinh mã & build thành công firmware .exe & .s19 |

---

## 7. Hands-on Lab: Full Clean Build

Đây là bài thực hành giúp bạn kiểm chứng từ đầu tới cuối quy trình build một ứng dụng AUTOSAR cơ bản trên môi trường POSIX (bằng WSL2).

**Mục tiêu:** Xóa các bản build cũ, build lại toàn bộ từ đầu và chạy thành công mô phỏng.

**Step-by-step Exercise:**

1. **Mở WSL2 Terminal (Ubuntu).**
2. **Di chuyển tới thư mục gốc của AUTOSAR Build:**
   ```bash
   cd /mnt/c/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as
   ```
3. **Thực hiện lệnh Clean (Xóa toàn bộ object và executable cũ):**
   ```bash
   scons -c --board=posix
   ```
   *Expected Output:*
   ```text
   scons: Reading SConscript files ...
   scons: done reading SConscript files.
   scons: Cleaning targets ...
   Removed build/posix/obj/xxx.o
   ...
   scons: done cleaning targets.
   ```
4. **Tiến hành Full Build:**
   ```bash
   scons --board=posix
   ```
   *Expected Output:* Quá trình sẽ diễn ra lâu hơn bình thường (khoảng 10-30 giây tùy máy), hệ thống compile lại toàn bộ các file `.c`. Kết thúc bằng dòng: `scons: done building targets.`
5. **Kiểm tra file thực thi đã được sinh ra:**
   ```bash
   ls -la build/posix/as
   ```
   *Expected Output:* Hiển thị thông tin kích thước, quyền `rwxr-xr-x` của file `as`.
6. **Thực thi:**
   ```bash
   ./build/posix/as
   ```
   *Expected Output:* Các log khởi tạo của hệ điều hành AUTOSAR OS và các task bắt đầu in ra terminal. (Nhấn `Ctrl+C` để thoát).

---

## 8. Interview Questions về Build Systems (10 câu)

Dưới đây là 10 câu hỏi phỏng vấn thường gặp dành cho kỹ sư hệ thống/nhúng, tập trung vào Build Systems và AUTOSAR:

1. **Tại sao hệ sinh thái AUTOSAR lại ưa chuộng việc sử dụng SCons hơn là GNU Make truyền thống?**
   *Gợi ý trả lời:* SCons dùng Python cho phép viết logic scripting mạnh mẽ (ví dụ: parse XML trực tiếp), hỗ trợ tự động tìm C/C++ dependency (không cần `.d` files), và hỗ trợ đa nền tảng tự nhiên hơn.
2. **Khái niệm "Incremental Build" là gì? Nó giúp ích gì cho dự án lớn như AUTOSAR?**
   *Gợi ý trả lời:* Là quá trình chỉ biên dịch lại những file mã nguồn đã bị thay đổi (và những file phụ thuộc vào nó) kể từ lần build trước đó. Giúp giảm thiểu thời gian build từ hàng giờ xuống còn vài giây/phút trong giai đoạn phát triển.
3. **Làm thế nào để hệ thống build (như SCons hoặc Make) biết được một file `.c` cần được compile lại?**
   *Gợi ý trả lời:* Dựa vào timestamp (thời gian chỉnh sửa file cuối cùng) hoặc MD5 signature của file `.c` và tất cả các file header `.h` mà nó include so với file object `.o`.
4. **Trong chu trình phát triển AUTOSAR, quá trình Code Generation diễn ra ở giai đoạn nào của quá trình Build?**
   *Gợi ý trả lời:* Diễn ra ở giai đoạn đầu tiên (Pre-build step). Các tool (như DaVinci Configurator, EB tresos, hoặc script Python) sẽ đọc file cấu hình ARXML và sinh ra mã nguồn C/C++ tĩnh (static code) trước khi trình biên dịch (GCC) bắt đầu hoạt động.
5. **Bare-metal Toolchain (`arm-none-eabi-gcc`) khác biệt như thế nào so với Linux Toolchain (`arm-linux-gnueabihf-gcc`)?**
   *Gợi ý trả lời:* Bare-metal toolchain liên kết với thư viện C siêu nhẹ (newlib) không phụ thuộc vào hệ điều hành (không dùng được các hàm OS như `fork()`, `pthread()`). Linux toolchain liên kết với `glibc` và giả định target board chạy hệ điều hành Linux.
6. **Bạn xử lý thế nào khi dự án bị lỗi `Out of Memory` hoặc quá tải CPU khi thực hiện lệnh `make -j` hoặc `scons -j`?**
   *Gợi ý trả lời:* Việc song song hóa (parallel jobs) tốn rất nhiều RAM (mỗi process gcc tốn hàng trăm MB). Cần giới hạn số lượng luồng (VD: `scons -j4` thay vì `-j` vô hạn), hoặc tăng swap/pagefile, nâng cấp RAM cho máy tính.
7. **Sự khác biệt cơ bản giữa một hệ thống build (như Make, SCons, Ninja) và một hệ thống tạo dự án - meta-build system (như CMake)?**
   *Gợi ý trả lời:* Build system thực thi trực tiếp các lệnh để biên dịch. CMake không tự biên dịch, nó là meta-build system sinh ra cấu hình (như Makefile hoặc file của Ninja) và công cụ build thực sự sẽ dùng cấu hình đó.
8. **Trong AUTOSAR, khái niệm "Linker Script" (`.ld` hoặc `.lsl`) dùng để làm gì trong quá trình Linking?**
   *Gợi ý trả lời:* Chỉ định địa chỉ bộ nhớ vật lý của vi điều khiển. Xác định chính xác vị trí đặt các đoạn mã (Text/Code), dữ liệu khởi tạo (Data), biến chưa khởi tạo (BSS) vào RAM hoặc ROM/Flash.
9. **Điều gì xảy ra ở bước "Linking" (Liên kết)? Tại sao đôi khi compile tất cả `.c` thành công nhưng lại văng lỗi "Undefined Reference" lúc link?**
   *Gợi ý trả lời:* Linking gom các object files (`.o`) và thư viện (`.a`) lại. Lỗi "Undefined Reference" xảy ra khi compiler thấy khai báo hàm ở file header nên cho qua, nhưng Linker không tìm thấy định nghĩa (implementation) thực sự của hàm đó trong bất kỳ object file nào.
10. **Làm thế nào để đảm bảo tính "Reproducible Build" (Build có khả năng tái tạo) trong môi trường Automotive?**
    *Gợi ý trả lời:* Cần khóa chặt (lock) phiên bản cụ thể của Toolchain (GCC version), Build Tool (SCons version), khóa phiên bản OS (Docker container được ưu tiên), và cấu hình đường dẫn tương đối (relative paths) để khi build trên máy A hay máy B, hoặc tại thời điểm hiện tại và 10 năm sau vẫn ra đúng cùng một file binary bit-by-bit.

---
*(Tài liệu do Principal AUTOSAR Architect biên soạn - Ready for Production)*

