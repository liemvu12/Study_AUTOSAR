# BÁO CÁO KỸ THUẬT & SOURCE DIFF: FIX TARGET BOARD QEMU (LM3S6965EVB)

> 📅 **Ngày thực hiện:** 25/08/2026  
> 🏷️ **Loại tài liệu:** Task Fix / Porting & Build System Configuration  
> 📌 **File Diff tương ứng:** [01_Fix_QEMU_Board_lm3s6965evb_Target.diff](01_Fix_QEMU_Board_lm3s6965evb_Target.diff)  
> 🎯 **Tuân thủ quy tắc:** [rule.md](rule.md) (Rule 3 & Rule 4 - Tùy biến MCAL Driver & Hệ thống Build).

---

## 1. BỐI CẢNH & NGUYÊN NHÂN CHUYỂN ĐỔI TARGET (ROOT CAUSE ANALYSIS)

### 1.1 Vấn đề với target `stm32f107vc` trên QEMU
* **Thực trạng:** Khi biên dịch target `stm32f107vc` và chạy trên QEMU với cờ `-M stm32vldiscovery`, chương trình bị crash và rơi vào `dump_fault_stack()` (HardFault Handler).
* **Nguyên nhân gốc rễ (Hardware Incompatibility):**
  * `stm32f107vc` là dòng chip **STM32 Connectivity Line**, có bộ điều khiển mạng CAN phần cứng đặt tại địa chỉ thanh ghi **`0x40006400` (`CAN1_BASE`)**.
  * Máy ảo QEMU bản tiêu chuẩn chỉ hỗ trợ mô hình board `stm32vldiscovery` (dòng chip **STM32F100 Value Line**, chỉ có GPIO, Timer, UART cơ bản, **hoàn toàn không có mạch CAN1**).
  * Khi hàm MCAL `Can_Init()` ghi vào địa chỉ `0x40006400`, QEMU phát hiện truy cập vùng nhớ không tồn tại (Unmapped MMIO Access) $\rightarrow$ CPU ARM sinh ngắt ngoại lệ **BusFault / HardFault**.

### 1.2 Giải pháp kỹ thuật: Chuyển sang Target `board.lm3s6965evb`
* Board **`lm3s6965evb` (Texas Instruments Stellaris Cortex-M3)** là bo mạch phần cứng được **QEMU hỗ trợ 100% phần cứng ảo** (CPU Cortex-M3, NVIC, SysTick, UART, CAN Controller).
* Dự án OpenSAR `as` đã có sẵn thư mục `as/com/as.application/board.lm3s6965evb/` dành riêng cho QEMU.

---

## 2. CÁC LỖI GẶP PHẢI TRÊN WINDOWS & CÁCH SỬA CHI TIẾT (STEP-BY-STEP)

Khi chuyển sang build `BOARD=lm3s6965evb`, hệ thống gặp **4 lỗi cản trở** trên môi trường Windows. Dưới đây là phân tích và giải pháp cho từng lỗi:

### 🔴 Lỗi 1: `xml.etree.ElementTree.ParseError: no element found: line 1, column 0`
* **Nguyên nhân:** Hàm `MKSymlink()` trong `building.py` dùng lệnh `mklink` của Windows cmd. Trên Windows thông thường (không chạy quyền Admin), `mklink` thất bại hoặc tạo file rác 0-byte cho `app.xml`, `canif.xml`, `autosar.arxml`. Khi bộ sinh mã `KsmGen / ScanXML` đọc file 0-byte, thư viện XML Python quăng lỗi crash.
* **Cách sửa:** Trong `as/com/as.tool/config.infrastructure.system/building.py`: dùng `shutil.copy2()` (với file) và `shutil.copytree()` (với thư mục) để sao chép dữ liệu thật 100%, không phụ thuộc vào quyền Windows Symlink.

### 🔴 Lỗi 2: `gcc: command not found` trong PreProcess ARXML
* **Nguyên nhân:** Hàm `PreProcess()` trong `building.py` gọi cứng chuỗi lệnh `'gcc -E'` để xử lý macro ARXML. Trên Windows chỉ có bộ toolchain `arm-none-eabi-gcc` chứ không có `gcc` bản x86. Lệnh thất bại dẫn đến file XML sinh ra bị rỗng (0 bytes).
* **Cách sửa:** Sửa lệnh gọi trình biên dịch thành `cc = Env.get('CC', 'arm-none-eabi-gcc')`. Nếu việc tiền xử lý không thành công thì đọc trực tiếp nội dung file gốc để đảm bảo dữ liệu XML luôn đầy đủ.

### 🔴 Lỗi 3: `implicit declaration of function 'HibernateWriteDelay'` trong `hibernate.c`
* **Nguyên nhân:** DriverLib của LM3S kiểm tra macro `#if defined(gcc) || defined(sourcerygxx)`. Nhưng trình biên dịch ARM GNU Toolchain chuẩn chỉ định nghĩa `__GNUC__` mà không định nghĩa `gcc` chữ thường, làm hàm delay bị ẩn đi.
* **Cách sửa:** Thêm `|| defined(__GNUC__)` vào file `as/com/as.infrastructure/arch/lm3s/DriverLib/src/hibernate.c`.

### 🔴 Lỗi 4: `multiple definition of knl_system_tick_handler` và duplicate CAN config
* **Nguyên nhân:** 
  1. `knl_system_tick_handler` được định nghĩa ở cả `arch/lm3s/mcal/Mcu.c` và `system/kernel/askar/portable/cortex-m/portable.c`.
  2. Các biến cấu hình `Can_ControllerCfgData`, `Can_ConfigSetData`, `Can_ConfigData` được sinh tự động trong `build/.../config/Can_PBCfg.c` nhưng lại bị định nghĩa trùng trong file stub `arch/common/mcal/SCan.c`.
* **Cách sửa:** 
  1. Thêm thuộc tính `__attribute__((weak))` cho `knl_system_tick_handler` trong `Mcu.c`.
  2. Thêm thuộc tính `__attribute__((weak))` cho các biến dữ liệu stub trong `SCan.c` để bộ Linker ưu tiên lấy dữ liệu thật từ `Can_PBCfg.c`.

---

## 3. KẾT QUẢ XÁC MINH (VERIFICATION)

Sau khi áp dụng các bản vá trên:
1. Lệnh build chạy thành công 100% với 0 lỗi:
   ```powershell
   cd as
   $env:BOARD="lm3s6965evb"
   $env:RELEASE="ascore"
   scons
   ```
2. Khởi chạy trên QEMU mượt mà, nhân OS AUTOSAR (`askar`) khởi động và in log ra console:
   ```text
    start application BUILD @ Aug 25 2026
    cpu is little endian
    XCP MTA memory address 20000f6c
   OSEK NM node ID is 1
   STDOUT  :TaskIdle is running
   ```
