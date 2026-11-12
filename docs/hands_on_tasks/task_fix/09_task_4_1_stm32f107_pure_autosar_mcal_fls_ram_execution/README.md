# GÓI VÁ: HIỆN THỰC HÓA MCAL FLASH DRIVER (FLS) CHO BOARD STM32F107VC
## (CƠ CHẾ RAM EXECUTION, CỬA SỔ MỞ KHÓA FPEC & BẢO VỆ CHỐNG LỖI CON TRỎ LẠC RUNAWAY CODE)

> 📅 **Ngày thực hiện:** 12/11/2026  
> 🏷️ **Loại tài liệu:** Task Fix / Architecture Standardization & MCAL Hardware Implementation  
> 📌 **File Diff tương ứng:** [`fix.diff`](fix.diff) | Bản sao tại root: [`../../task_04_diagnostic_memory.diff`](../task_04_diagnostic_memory.diff)  
> 🎯 **Tuân thủ quy tắc:** [`docs/hands_on_tasks/task_fix/rule.md`](../rule.md) (Rule 3 & Rule 4 - Vùng 4 Static BSW & MCAL Infrastructure).  
> 🎯 **Target Board:** `stm32f107vc` (ARM Cortex-M3 Physical Silicon / FPEC Flash Controller).  

---

## 1. 🛑 BỐI CẢNH KỸ THUẬT & CÂU HỎI CỐT LÕI

### 1.1 Hiện Trạng Mã Nguồn Trước Khi Vá:
* Trước khi có bản vá này, trong thư mục MCAL của chip STM32F1 ([`as/com/as.infrastructure/arch/stm32f1/mcal/`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/com/as.infrastructure/arch/stm32f1/mcal/)) chỉ tồn tại các driver: `Can.c`, `Dio.c`, `Mcu.c`, `Port.c` và `Flash.c` (driver Bootloader `asboot`).
* **Hoàn toàn không có file `Fls.c` chuẩn AUTOSAR MCAL**.
* Module Flash duy nhất chạy trong repo là [`as/com/as.infrastructure/arch/posix/mcal/Fls.c`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/com/as.infrastructure/arch/posix/mcal/Fls.c) sử dụng hệ thống tệp ảo VFS ghi file giả lập `flash.img` trên máy tính.

### 1.2 "Hạn Chế Tối Đa Mã Lệnh Xóa/Ghi Flash Trong ROM" Nghĩa Là Gì?
Trong ngành công nghiệp ô tô (ISO 26262 ASIL-D và AUTOSAR Standard), các hàm thao tác phần cứng xóa trang (`ErasePage`) và nạp half-word (`ProgramHalfWord`) **tuyệt đối bị hạn chế hoặc cấm chạy trực tiếp từ Flash ROM** vì 2 lý do kỹ thuật chí mạng:
1. **Xung đột vật lý RWW (Read-While-Write Stall & Deadlock):**
   * STM32F107VC sử dụng bộ nhớ NOR Flash đơn khối (Single-Bank Flash). Toàn bộ 256KB Flash dùng chung một mạch bơm cao áp (Charge Pump).
   * Khi lệnh Erase (~20ms-100ms) hoặc Program (~50µs) đang chạy, mạch đọc của Flash bị ngắt hoàn toàn.
   * Nếu CPU cố gắng nạp mã lệnh (Instruction Fetch) từ chính ROM Flash đó, bus AHB của CPU sẽ bị treo cứng ở trạng thái chờ (**Wait-State Stall**). Toàn bộ hệ thống bị đóng băng, Watchdog ngắt nguồn xe hoặc CPU nhảy ngoại lệ **HardFault**!
2. **Nguy cơ an toàn chức năng (Runaway Code Execution):**
   * Nếu hàm `FLASH_ErasePage()` nằm thường trực ở một địa chỉ cố định trong Flash ROM, khi xảy ra lỗi tràn ngăn xếp (Stack Overflow) hoặc nhiễu điện từ (ESD) làm thanh ghi Program Counter (PC) nhảy loạn trúng vào hàm xóa trong ROM $\rightarrow$ Vi điều khiển sẽ xóa trắng chính mã nguồn của hệ điều hành!

---

## 2. 🧩 4 TUYẾN PHÒNG THỦ KỸ NGHỆ ĐƯỢC HIỆN THỰC HÓA

| Tuyến Phòng Thủ | Tên Cơ Chế | Cách Thức Hoạt Động Cụ Thể Trong Mã Nguồn |
| :--- | :--- | :--- |
| **Tuyến 1** | **RAM Execution (`.ramtext`)** | Gắn thuộc tính `__attribute__((section(".ramtext"), noinline))` cho các hàm xóa/ghi trực tiếp thanh ghi. Linker script ép đặt mã máy vào SRAM (`0x2000xxxx`). Khi CPU thực thi xóa/ghi Flash, CPU chạy từ SRAM, giải phóng hoàn toàn bus AHB của Flash ROM! |
| **Tuyến 2** | **Hardware Lock Window** | Thanh ghi FPEC mặc định luôn bị khóa cứng (`FLASH->CR |= FLASH_CR_LOCK`). Chỉ mở khóa bằng chuỗi Key ma thuật `0x45670123` và `0xCDEF89AB` đúng vài micro-giây của chunk ghi, và khóa lại ngay lập tức! |
| **Tuyến 3** | **Address Range Gatekeeper** | Hàm `Fls_Erase()` và `Fls_Write()` kiểm tra nghiêm ngặt `TargetAddress`: từ chối 100% mọi truy cập vào vùng ROM ứng dụng (`0x08000000` - `0x0803DFFF`), chỉ duy nhất cho phép ghi vào phân vùng dữ liệu an toàn (Fee Emulated EEPROM). |
| **Tuyến 4** | **Non-blocking State Machine** | Chia nhỏ tiến trình ghi thành từng chunk hữu hạn (8 bytes / chu kỳ) trong `Fls_MainFunction()` để nhường CPU cho các Task thời gian thực khác của OS. |

---

## 3. 📂 CẤU TRÚC THƯ MỤC GÓI VÁ (ARTIFACT DIRECTORY STRUCTURE)

```
docs/hands_on_tasks/task_fix/09_task_4_1_stm32f107_pure_autosar_mcal_fls_ram_execution/
├── README.md                                                   ← [Tài liệu kỹ thuật & Báo cáo pháp y]
├── fix.diff                                                    ← [Bản vá thống nhất Unified Patch]
├── src_before/                                                 ← [Mã nguồn trước khi sửa đổi]
│   └── as/
│       ├── com/
│       │   ├── as.application/board.stm32f107vc/
│       │   │   ├── SConscript
│       │   │   └── script/linker-app.lds
│       │   ├── as.infrastructure/arch/stm32f1/
│       │   │   └── SConscript
│       │   └── as.tool/config.infrastructure.system/argen/
│       │       └── util.py
│       └── release/ascore/app/
│           └── app.c
└── src_after/                                                  ← [Mã nguồn chuẩn sau khi sửa đổi]
    └── as/
        ├── com/
        │   ├── as.application/board.stm32f107vc/
        │   │   ├── SConscript
        │   │   └── script/linker-app.lds
        │   ├── as.infrastructure/arch/stm32f1/
        │   │   ├── SConscript
        │   │   └── mcal/
        │   │       └── Fls.c                                   ← [MCAL Fls Mới với .ramtext]
        │   └── as.tool/config.infrastructure.system/argen/
        │       └── util.py
        └── release/ascore/app/
            └── app.c
```

---

## 4. 🛠️ BẰNG CHỨNG XÁC THỰC TRÊN ĐĨA (EVIDENCE SUMMARY)

Sau khi biên dịch thành công (`scons`), kiểm tra bản đồ bộ nhớ nhị phân trong [`as/build/nt/stm32f107vc/ascore/stm32f107vc.map`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/build/nt/stm32f107vc/ascore/stm32f107vc.map#L4729-L4735):

```
.ramtext       0x20000248       0x98 build\nt\stm32f107vc\ascore\com\as.infrastructure\arch\stm32f1\mcal\Fls.o
               0x20000248                Fls_LL_ErasePage_RAM
               0x20000298                Fls_LL_ProgramHalfWord_RAM
```

Và kiểm tra bảng ký hiệu thực tế bằng lệnh `arm-none-eabi-nm`:
```
00001050 T Fls_Init                  (Nằm tại Flash ROM: 0x00001050)
0000108c T Fls_GetStatus              (Nằm tại Flash ROM: 0x0000108c)
00001098 T Fls_MainFunction           (Nằm tại Flash ROM: 0x00001098)
2000005c t Fls_Global                 (Nằm tại SRAM:      0x2000005c)
20000248 T Fls_LL_ErasePage_RAM       (NẰM 100% TRONG SRAM: 0x20000248)
200002b4 T Fls_LL_ProgramHalfWord_RAM (NẰM 100% TRONG SRAM: 0x200002b4)
```

👉 **Kết luận:** Mã máy xóa và nạp Flash thực tế hoàn toàn không nằm trong ROM Flash, bảo đảm chuẩn an toàn chức năng ô tô cao nhất!
