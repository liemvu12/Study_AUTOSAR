# CHUYÊN ĐỀ BỔ TRỢ 03: CẨM NANG TOÀN DIỆN VỀ LINKER SCRIPT & ÁNH XẠ BỘ NHỚ (MEMORY MAPPING)
## (Masterclass: Linker Script, Memory Layout & Forensic Debugging for Automotive Embedded Engineers)

> 📌 **Vị trí tài liệu:** [`docs/supplementary_knowledge/03_Linker_Script_And_Memory_Mapping_Masterclass.md`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/docs/supplementary_knowledge/03_Linker_Script_And_Memory_Mapping_Masterclass.md)  
> 🎯 **Đối tượng mục tiêu:** Kỹ sư phần mềm nhúng (C/C++), BSW Developer, BSW Integration Engineer muốn làm chủ hoàn toàn khâu cấp phát bộ nhớ vật lý, tự tin debug các lỗi sập chip (HardFault / MPU Fault / Tràn RAM), và vượt qua các buổi phỏng vấn kỹ thuật cấp độ Senior trong ngành ô tô.  
> 🔧 **Mã nguồn thực nghiệm đối chiếu:**  
> - Linker Scripts: [`as/com/as.application/board.lm3s6965evb/script/linker.lds`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/com/as.application/board.lm3s6965evb/script/linker.lds), [`board.stm32f107vc/script/linker-app.lds`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/com/as.application/board.stm32f107vc/script/linker-app.lds), [`linker-boot.lds`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/com/as.application/board.stm32f107vc/script/linker-boot.lds), [`linker-flsdrv.lds`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/com/as.application/board.stm32f107vc/script/linker-flsdrv.lds).  
> - Startup Assembly: [`as/com/as.infrastructure/system/kernel/askar/portable/cortex-m/startup.S`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/com/as.infrastructure/system/kernel/askar/portable/cortex-m/startup.S).  
> - Bản đồ bộ nhớ thực tế: [`as/build/nt/lm3s6965evb/ascore/lm3s6965evb.map`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/build/nt/lm3s6965evb/ascore/lm3s6965evb.map).  
> 📜 **Tài liệu tham chiếu:** [Chuyên đề 05 Mục 3.5 & Mục 3.6](../../theory/05_Toolchain_ARXML_And_ECU_Integration.md#35--nghịch-lý-linker-script-trong-toolchain--ecu-integration-so-sánh-toàn-diện-autosar-linker-vs-bare-metal-vs-linuxzephyr) và [Quy tắc 3 (`rule.md`)](../../hands_on_tasks/task_fix/rule.md).

---

## 📑 MỤC LỤC CHI TIẾT

1. [Bản Chất Kỹ Nghệ: Linker Script Là Gì & Vai Trò Trong Chuỗi Toolchain Ô Tô](#1-bản-chất-kỹ-nghệ-linker-script-là-gì--vai-trò-trong-chuỗi-toolchain-ô-tô)
2. [NĂNG LỰC 1: Đọc Hiểu, Bóc Tách Cú Pháp & Tùy Biến Linker Script Thực Chiến](#2-năng-lực-1-đọc-hiểu-bóc-tách-cú-pháp--tùy-biến-linker-script-thực-chiến)
   - [2.1 Lệnh Cấu Hình Bộ Nhớ Vật Lý `MEMORY`](#21-lệnh-cấu-hình-bộ-nhớ-vật-lý-memory)
   - [2.2 Lệnh Phân Bổ Section `SECTIONS` & 4 Phân Đoạn Nền Tảng Của C](#22-lệnh-phân-bổ-section-sections--4-phân-đoạn-nền-tảng-của-c)
   - [2.3 Giải Mã Cặp Khái Niệm Cốt Tử: VMA (Run Address) vs LMA (Load Address)](#23-giải-mã-cặp-khái-niệm-cốt-tử-vma-run-address-vs-lma-load-address)
   - [2.4 Bằng Chứng Pháp Y: Mối Quan Hệ Giữa `linker.lds` Và Hợp Ngữ `startup.S`](#24-bằng-chứng-pháp-y-mối-quan-hệ-giữa-linkerlds-và-hợp-ngữ-startups)
   - [2.5 Kỹ Thuật Bảo Vệ Biến: `KEEP()`, `ALIGN()` & Phân Vùng `.noinit`](#25-kỹ-thuật-bảo-vệ-biến-keep-align--phân-vùng-noinit)
   - [2.6 Giải Phẫu 3 Tệp Linker Script Thực Tế: App vs Bootloader vs RAM Flash Driver](#26-giải-phẫu-3-tệp-linker-script-thực-tế-app-vs-bootloader-vs-ram-flash-driver)
3. [NĂNG LỰC 2: Giải Mã Tệp Bản Đồ Bộ Nhớ (.map) & Kỹ Nghệ Forensic Debug Khi Chip Sập](#3-năng-lực-2-giải-mã-tệp-bản-đồ-bộ-nhớ-map--kỹ-nghệ-forensic-debug-khi-chip-sập)
   - [3.1 Bản Chất File `.map` & So Sánh Bộ Ba Công Cụ: `.hex` vs `.elf` vs `.map`](#31-bản-chất-file-map--so-sánh-bộ-ba-công-cụ-hex-vs-elf-vs-map)
   - [3.2 File `.map` Có Trong Mọi Hệ Thống Nhúng Không? (Tính Phổ Quát & So Sánh Toolchains)](#32-file-map-có-trong-mọi-hệ-thống-nhúng-không-tính-phổ-quát--so-sánh-toolchains)
   - [3.3 Tần Suất Gặp & 6 Tình Huống Bắt Buộc Làm Việc Với File `.map` Trong Dự Án Thực Tế](#33-tần-suất-gặp--6-tình-huống-bắt-buộc-làm-việc-với-file-map-trong-dự-án-thực-tế)
   - [3.4 Giải Phẫu Chi Tiết 5 Phân Khu Cơ Thể Của File `lm3s6965evb.map` Thực Nghiệm](#34-giải-phẫu-chi-tiết-5-phân-khu-cơ-thể-của-file-lm3s6965evbmap-thực-nghiệm)
   - [3.5 Tuyệt Chiêu "Pháp Y Bộ Nhớ": Đọc `.map` Bắt Bệnh Đẳng Cấp Senior](#35-tuyệt-chiêu-pháp-y-bộ-nhớ-đọc-map-bắt-bệnh-đẳng-cấp-senior)
   - [3.6 Kịch Bản Cứu Hộ 1: Xử Lý Lỗi Tràn Bộ Nhớ (`region 'RAM' overflowed`)](#36-kịch-bản-cứu-hộ-1-xử-lý-lỗi-tràn-bộ-nhớ-region-ram-overflowed)
   - [3.7 Kịch Bản Cứu Hộ 2: Điều Tra Sập Nguồn (HardFault / BusFault / MemManage Fault)](#37-kịch-bản-cứu-hộ-2-điều-tra-sập-nguồn-hardfault--busfault--memmanage-fault)
   - [3.8 Kịch Bản Cứu Hộ 3: Tràn Ngăn Xếp Task (Stack Overflow & Tràn Đè Biến Toàn Cục)](#38-kịch-bản-cứu-hộ-3-tràn-ngăn-xếp-task-stack-overflow--tràn-đè-biến-toàn-cục)
4. [NĂNG LỰC 3: Bộ Câu Hỏi Phỏng Vấn Thực Chiến Chuyên Sâu (Senior BSW / ECU Integration)](#4-năng-lực-3-bộ-câu-hỏi-phỏng-vấn-thực-chiến-chuyên-sâu-senior-bsw--ecu-integration)
5. [Tổng Kết & Checklist Kiểm Tra Linker Script Trước Khi Release Firmware](#5-tổng-kết--checklist-kiểm-tra-linker-script-trước-khi-release-firmware)

---

## 1. Bản Chất Kỹ Nghệ: Linker Script Là Gì & Vai Trò Trong Chuỗi Toolchain Ô Tô

Trong quá trình phát triển phần mềm nhúng, trình biên dịch (Compiler) chỉ có tầm nhìn cục bộ trong từng file C riêng lẻ. Khi biên dịch `app.c` hay `Can.c`, compiler chuyển đổi mã nguồn thành file đối tượng nhị phân (`app.o`, `Can.o`) chứa các phân đoạn mã lệnh và biến nhưng **chưa hề có địa chỉ bộ nhớ vật lý thực tế** (địa chỉ tạm thời chỉ là `0x00000000`).

**Trình liên kết (Linker)** kết hợp cùng **Linker Script (`.ld`, `.lds`, `.lsl`)** chính là **"Kiến trúc sư trưởng quy hoạch đô thị"**:
- Linker Script nắm giữ toàn bộ bản đồ bộ nhớ vật lý của con chip (Bao nhiêu KB Flash, bao nhiêu KB SRAM, nằm ở địa chỉ nào trên bus).
- Linker đọc Linker Script, gom hàng trăm file `.o` và các thư viện tĩnh (`.a`), gán địa chỉ vật lý chính xác cho từng biến, từng hàm, rồi xuất ra file nhị phân cuối cùng (`.elf`, `.hex`, `.s19`) để nạp vào ECU.

```
 [MÃ NGUỒN C & H]         [COMPILER GCC]           [OBJECT FILES]               [LINKER SCRIPT]
  app.c, Can.c,      ──►   arm-none-eabi-gcc   ──►  app.o, Can.o,         │     linker.lds
  Os_Cfg.c, Mcu.c          -c -O2                   Os_Cfg.o, Mcu.o       │     (Quy hoạch Flash/RAM)
                                                          │               │              │
                                                          └───────────────┼──────────────┘
                                                                          ▼
                                                                  [LINKER GNU ld]
                                                               arm-none-eabi-ld / gcc
                                                                          │
                                                      ┌───────────────────┴───────────────────┐
                                                      ▼                                       ▼
                                            [FIRMWARE NHỊ PHÂN]                     [BẢN ĐỒ ÁNH XẠ BỘ NHỚ]
                                            lm3s6965evb.elf / .hex                  lm3s6965evb.map
                                            (Nạp vào Flash vi điều khiển)           (Báo cáo chi tiết từng Byte)
```

> ⚠️ **Sự khác biệt trong ngành ô tô (AUTOSAR):**  
> Khác với lập trình vi điều khiển thông thường (nơi bạn chỉ bấm Run và phó mặc cho Keil MDK tự xếp RAM/Flash), trong tiêu chuẩn ô tô **ISO 26262 ASIL-D**, bộ nhớ phải được kiểm soát tuyệt đối: vùng nào chạy RAM, vùng nào chống ghi, phân vùng MPU nào của phanh ABS, phân vùng nào của radio giải trí. Nắm vững Linker Script là yêu cầu phân định giữa kỹ sư cơ bản và chuyên gia tích hợp BSW.

---

## 2. NĂNG LỰC 1: Đọc Hiểu, Bóc Tách Cú Pháp & Tùy Biến Linker Script Thực Chiến

Để đạt được năng lực đọc hiểu và tùy biến mọi file Linker Script trong các dự án xe hơi, chúng ta cùng giải phẫu trực tiếp tệp Linker Script thực tế của dự án: [`as/com/as.application/board.lm3s6965evb/script/linker.lds`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/com/as.application/board.lm3s6965evb/script/linker.lds).

### 2.1 Lệnh Cấu Hình Bộ Nhớ Vật Lý `MEMORY`

Lệnh `MEMORY` định nghĩa các khối bộ nhớ vật lý thực tế có mặt trên silicon của chip:

```lds
/* Trích từ: as/com/as.application/board.lm3s6965evb/script/linker.lds (Dòng 8 - 12) */
MEMORY
{
    FLASH (rx) : ORIGIN = 0x00000000, LENGTH = 256K
    RAM (rwx)  : ORIGIN = 0x20000000, LENGTH = 64K
}
```

* **`FLASH (rx)`**: Tên phân vùng nhớ Flash ROM.
  - `(rx)`: Thuộc tính cấp quyền (Attributes). `r` = Read (Được phép đọc), `x` = Execute (Được phép thực thi mã lệnh). Flash không có cờ `w` (Write) vì CPU không thể ghi trực tiếp vào Flash như RAM.
  - `ORIGIN = 0x00000000`: Địa chỉ bắt đầu của Flash trên bản đồ bus nhớ vi điều khiển ARM Cortex-M.
  - `LENGTH = 256K`: Dung lượng tối đa của Flash ($256 \times 1024 = 262.144$ bytes). Nếu mã vượt quá giới hạn này, Linker sẽ chặn đứng bằng lỗi Overflow.
* **`RAM (rwx)`**: Tên phân vùng nhớ tĩnh SRAM.
  - `(rwx)`: `r` = Read, `w` = Write (Đọc ghi biến số), `x` = Execute (Được phép thực thi code trên RAM nếu có code nạp động).
  - `ORIGIN = 0x20000000`: Địa chỉ bắt đầu của SRAM trong chuẩn kiến trúc ARM Cortex-M.
  - `LENGTH = 64K`: Dung lượng RAM khả dụng là 64KB ($65.536$ bytes).

---

### 2.2 Lệnh Phân Bổ Section `SECTIONS` & 4 Phân Đoạn Nền Tảng Của C

Lệnh `SECTIONS` chỉ đạo Linker gom các phân đoạn từ các file `.o` đầu vào (Input Sections) và sắp xếp vào các phân đoạn đầu ra (Output Sections) nằm trong vùng nhớ vật lý tương ứng:

```lds
/* Trích từ: as/com/as.application/board.lm3s6965evb/script/linker.lds (Dòng 19 - 48) */
SECTIONS
{
    .text :
    {
        KEEP(*(.isr_vector))
        *(.startup*)
        *(.text*)
        *(.rodata*)
    } > FLASH

    __etext = .;

    .data : AT (__etext)
    {
        . = ALIGN(4);
        __data_start__ = .;
        *(.data*)
        __data_end__ = .;
    } > RAM

    .bss :
    {
        . = ALIGN(4);
        __bss_start__ = .;
        *(.bss*)
        *(COMMON)
        . = ALIGN(4);
        __bss_end__ = .;
    } > RAM
}
```

Bảng phân bổ 4 phân đoạn kinh điển của ngôn ngữ C:

| Phân Đoạn (Section) | Kiểu Dữ Liệu Chứa Bên Trong | Vị Trí Lưu Trữ Khi Tắt Điện (LMA) | Vị Trí Thực Thi Khi Hoạt Động (VMA) | Ví Dụ Cụ Thể Trong Code |
| :--- | :--- | :---: | :---: | :--- |
| **`.text`** | Mã máy thực thi (Executable Machine Code), Bảng Vector ngắt. | **FLASH** | **FLASH** | Thân hàm `TASK(TaskApp)`, hàm `Can_Init()`. |
| **`.rodata`** | Hằng số chỉ đọc (Read-Only Data), chuỗi string. | **FLASH** | **FLASH** | `const TaskConstType TaskConstArray[...]`, `"TaskApp"`. |
| **`.data`** | Biến toàn cục / static **có khởi tạo giá trị ban đầu khác 0**. | **FLASH** | **RAM** | `uint32 g_system_timer = 100;`, `rbV_canin`. |
| **`.bss`** | Biến toàn cục / static **không khởi tạo hoặc khởi tạo bằng 0**. | **Không chiếm Flash** | **RAM** | `uint8 CanIf_Global;`, `TaskApp_Stack[2048]`. |

---

### 2.3 Giải Mã Cặp Khái Niệm Cốt Tử: VMA (Run Address) vs LMA (Load Address)

Đây là khái niệm then chốt mà 100% các cuộc phỏng vấn Embedded Senior đều đào sâu:
- **VMA (Virtual / Run Memory Address):** Địa chỉ mà chương trình mong đợi biến hoặc hàm nằm ở đó khi CPU đang chạy (`> RAM`). Mọi con trỏ, biến trong code C đều biên dịch trỏ về địa chỉ VMA.
- **LMA (Load Memory Address):** Địa chỉ mà phân đoạn đó thực sự được ghi vào chip khi nạp qua cổng J-Link/Debugger (`AT (...)`).

```
                              BẢN CHẤT CỦA PHÂN ĐOẠN .data
     VÙNG NHỚ FLASH (LMA)                                      VÙNG NHỚ SRAM (VMA)
┌─────────────────────────────┐                           ┌─────────────────────────────┐
│ .text (Mã thực thi)         │                           │ (Trống lúc chưa cấp nguồn)  │
├─────────────────────────────┤                           │                             │
│ .rodata (Hằng số const)     │                           ├─────────────────────────────┤
├─────────────────────────────┤                           │ .data (VMA = 0x20000000)    │
│ __etext (Cuối Flash)        │                           │ Biến có giá trị ban đầu     │
├─────────────────────────────┤  Khi CPU Boot (Startup):  │ r0 = __data_start__         │
│ .data (Giá trị khởi tạo gốc)│ ────────Copy sang───────► │ r3 = __data_end__           │
│ LMA = __etext (0x000172d4)  │                           ├─────────────────────────────┤
└─────────────────────────────┘                           │ .bss (Xóa về 0)             │
                                                          └─────────────────────────────┘
```

👉 **Tại sao `.data` bắt buộc phải có 2 địa chỉ khác nhau (`> RAM AT (__etext)`)?**
- Vì RAM là bộ nhớ khả biến (Volatile), khi tắt khóa điện xe hơi thì toàn bộ RAM bị xóa sạch. Giá trị khởi tạo gốc (ví dụ biến `g_timeout = 5000`) bắt buộc phải được lưu cố định trong Flash tại vị trí `__etext` (LMA).
- Nhưng khi CPU chạy, biến đó phải được sửa đổi tự do, do đó nó phải nằm trong SRAM tại `0x20000000` (VMA).

---

### 2.4 Bằng Chứng Pháp Y: Mối Quan Hệ Giữa `linker.lds` Và Hợp Ngữ `startup.S`

Làm thế nào dữ liệu từ Flash nhảy sang RAM? Hệ điều hành không tự làm điều này, mà được thực thi bởi đoạn mã hợp ngữ khởi động tại [`as/com/as.infrastructure/system/kernel/askar/portable/cortex-m/startup.S`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/com/as.infrastructure/system/kernel/askar/portable/cortex-m/startup.S#L319-L352):

```assembly
/* Trích từ: as/com/as.infrastructure/system/kernel/askar/portable/cortex-m/startup.S */
reset_handler:
    ldr  sp, =knl_system_stack_top /* 1. Thiết lập đỉnh ngăn xếp hệ thống từ Linker Script */

    /* 2. Sao chép phân đoạn .data từ Flash (LMA) sang SRAM (VMA) */
    ldr  r0, =__data_start__  /* r0 = 0x20000000 (Đầu RAM) */
    ldr  r3, =__data_end__    /* r3 = 0x200001c4 (Cuối data RAM) */
    ldr  r5, =__etext         /* r5 = 0x000172d4 (Đầu data lưu trong Flash) */
    movs r1, #0
    b    LoopCopyDataInit

CopyDataInit:
    ldr  r4, [r5, r1]         /* Đọc 4 bytes từ Flash */
    str  r4, [r0, r1]         /* Ghi 4 bytes vào SRAM */
    adds r1, r1, #4           /* Tăng con trỏ */

LoopCopyDataInit:
    adds r2, r0, r1
    cmp  r2, r3               /* Đã copy hết kích thước .data chưa? */
    bcc  CopyDataInit

    /* 3. Xóa phân đoạn .bss về số 0 hoàn toàn trong SRAM */
    ldr  r2, =__bss_start__   /* r2 = 0x200001c4 */
    b    LoopFillZerobss

FillZerobss:
    movs r3, #0               /* Nạp số 0 */
    str  r3, [r2], #4         /* Ghi số 0 vào SRAM và tăng địa chỉ */

LoopFillZerobss:
    ldr  r3, = __bss_end__    /* r3 = 0x2000758c */
    cmp  r2, r3
    bcc  FillZerobss

    /* 4. Nhảy vào hàm main() của ứng dụng */
    bl  main
    b   .
```

> 🔍 **Phát hiện cốt tử:**  
> Các biến `__etext`, `__data_start__`, `__data_end__`, `__bss_start__`, `__bss_end__`, `knl_system_stack_top` **không phải là các biến số C hay hằng số định nghĩa trong code**. Chúng là **các nhãn địa chỉ thuần túy do Linker Script tính toán và xuất ra**. Trình hợp ngữ `startup.S` sử dụng chỉ thị `ldr r0, =__data_start__` để nạp chính xác địa chỉ vật lý đó vào thanh ghi CPU!

---

### 2.5 Kỹ Thuật Bảo Vệ Biến: `KEEP()`, `ALIGN()` & Phân Vùng `.noinit`

1. **Chỉ thị `KEEP(*(.isr_vector))`:**  
   - Khi biên dịch với cờ tối ưu hóa loại bỏ code thừa của Linker (`-Wl,--gc-sections`), Linker sẽ tự động quét và xóa sạch các hàm/biến không có ai gọi trong mã nguồn.
   - Bảng vector ngắt `.isr_vector` chỉ được phần cứng CPU đọc khi có ngắt chứ không có hàm C nào gọi nó. Nếu thiếu `KEEP()`, **Linker sẽ xóa sạch Vector Table $\rightarrow$ Chip bị "chết não" ngay khi khởi động!**
2. **Chỉ thị `. = ALIGN(4)`:**  
   - Buộc địa chỉ hiện tại phải chia hết cho 4 bytes (32-bit). CPU ARM Cortex-M truy cập dữ liệu 32-bit nhanh nhất và không bị lỗi phần cứng `UsageFault` khi dữ liệu được canh hàng 4 bytes.
3. **Phân vùng đặc thù `.noinit` (Biến lưu vết tai nạn xe):**  
   - Mặc định Startup sẽ xóa sạch SRAM về 0 (`LoopFillZerobss`). Nhưng nếu xe vừa gặp tai nạn hoặc ECU vừa bị Reset do Watchdog, ta cần lưu giữ mã lỗi chẩn đoán (DTC) và dữ liệu hộp đen vào RAM để gửi về máy quét OBD-II.
   - Khi đó, kỹ sư cấu hình phân đoạn `(NOLOAD)`:
     ```lds
     .noinit (NOLOAD) :
     {
         *(.noinit*)
     } > RAM
     ```
     Thuộc tính `(NOLOAD)` ra lệnh cho Linker: Hãy cấp phát địa chỉ trong RAM nhưng **cấm sinh mã khởi tạo hoặc xóa về 0 trong Startup**.

---

### 2.6 Giải Phẫu 3 Tệp Linker Script Thực Tế: App vs Bootloader vs RAM Flash Driver

Kho mã nguồn `Study_AUTOSAR` cung cấp 3 ví dụ kinh điển minh chứng cho 3 kịch bản phần mềm trên xe hơi:

#### 1. Bản Chạy Bình Thường (App Mode) — [`linker.lds`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/com/as.application/board.lm3s6965evb/script/linker.lds)
- Chiếm dụng toàn bộ Flash từ `0x00000000` (256KB) và RAM từ `0x20000000` (64KB). Chạy độc lập trên simulator QEMU hoặc nạp trực tiếp qua mạch nạp J-Link.

#### 2. Bản Nạp Bootloader (FBL Mode) — [`linker-boot.lds`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/com/as.application/board.stm32f107vc/script/linker-boot.lds)
```lds
MEMORY
{
    FLASH (rx)   : ORIGIN = 0x00000000, LENGTH = 64K   /* Dành riêng cho Bootloader */
    APPCODE (rx) : ORIGIN = 0x00010000, LENGTH = 192K  /* Dành cho Application */
    RAM (rwx)    : ORIGIN = 0x20001000, LENGTH = 60K   /* Dành 4KB RAM đầu cho cờ Boot */
}
application_main = 0x00010401; /* Địa chỉ Reset Handler của ứng dụng để Bootloader nhảy sang */
```
- Phân chia Flash làm 2 nửa: Nửa đầu 64KB chứa Bootloader, nửa sau 192KB chứa firmware chính. Khi bật nguồn, Bootloader kiểm tra tính toàn vẹn (CRC/Signature), nếu hợp lệ sẽ nhảy sang địa chỉ `application_main`.

#### 3. Bản Nạp Động Flash Driver Vào RAM — [`linker-flsdrv.lds`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/com/as.application/board.stm32f107vc/script/linker-flsdrv.lds)
```lds
MEMORY
{
    FLASH (rx) : ORIGIN = 0x20000000, LENGTH = 4K  /* <--- KỲ LẠ: FLASH LẠI Ở ĐỊA CHỈ SRAM! */
}
```
- **Giải mã bí ẩn kỹ nghệ:** Khi xóa/ghi Flash chip, hiện tượng Read-While-Write (RWW) cấm CPU đọc lệnh từ Flash. Do đó, mã máy của Flash Driver được công cụ chẩn đoán UDS truyền qua mạng CAN và nạp tạm thời vào địa chỉ `0x20000000` trong SRAM để CPU chạy trực tiếp trên RAM!

---

## 3. NĂNG LỰC 2: Giải Mã Tệp Bản Đồ Bộ Nhớ (.map) & Kỹ Nghệ Forensic Debug Khi Chip Sập

---

### 3.1 Bản Chất File `.map` & So Sánh Bộ Ba Công Cụ: `.hex` vs `.elf` vs `.map`

Khi kết thúc quá trình build một dự án nhúng (như lệnh `scons` trong dự án `as`), Toolchain (Compiler + Linker) sẽ nhả ra nhiều tệp tin ở thư mục đầu ra [`as/build/nt/lm3s6965evb/ascore/`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/build/nt/lm3s6965evb/ascore/). Mỗi tệp sinh ra phục vụ một mục đích chuyên biệt trong vòng đời phát triển:

```
                      ┌──────────────────────────────────────────────┐
                      │              TRÌNH LIÊN KẾT                  │
                      │         (GNU Linker: arm-none-eabi-ld)       │
                      └──────────────────────┬───────────────────────┘
                                             │
            ┌────────────────────────────────┼────────────────────────────────┐
            ▼                                ▼                                ▼
  ┌───────────────────┐            ┌───────────────────┐            ┌───────────────────┐
  │   FILE .hex/.bin  │            │     FILE .elf     │            │     FILE .map     │
  │ (Mã máy nạp chip) │            │  (Gỡ lỗi Debug)   │            │(Sổ cái kế toán RAM│
  │                   │            │                   │            │ & ROM cho Kỹ sư)  │
  └─────────┬─────────┘            └─────────┬─────────┘            └─────────┬─────────┘
            ▼                                ▼                                ▼
┌───────────────────────┐        ┌───────────────────────┐        ┌───────────────────────┐
│ • Dành cho máy nạp:   │        │ • Dành cho Debugger:  │        │ • Dành cho CON NGƯỜI: │
│   J-Link, ST-Link,    │        │   GDB, Lauterbach,    │        │   Kỹ sư BSW, Reviewer,│
│   UDS Flasher         │        │   Ozone, Keil GUI     │        │   Script phân tích CI │
│ • KHÔNG có tên biến   │        │ • Chứa bảng DWARF     │        │ • Văn bản thuần túy   │
│ • KHÔNG có hàm/source │        │ • Ánh xạ dòng code C  │        │ • Soi từng byte RAM,  │
│ • Chỉ có dữ liệu hex  │        │ • File nhị phân nặng  │        │   địa chỉ hàm, lỗi sập│
└───────────────────────┘        └───────────────────────┘        └───────────────────────┘
```

#### 📊 Bảng Đối Chiếu Toàn Diện Bộ Ba Tệp Xuất Xưởng

| Tiêu Chí So Sánh | Tệp `.hex` / `.s19` / `.bin` | Tệp `.elf` / `.axf` / `.out` | Tệp `.map` (Memory Map) |
| :--- | :--- | :--- | :--- |
| **Bản chất định dạng** | Dữ liệu mã máy thuần túy (ASCII Hex Records hoặc Raw Binary). | Nhị phân tiêu chuẩn ELF (*Executable and Linkable Format*). | **Plaintext (Văn bản thuần túy đọc được bằng mọi Text Editor).** |
| **Công cụ sinh ra** | `arm-none-eabi-objcopy` trích xuất từ file `.elf`. | Trình liên kết Linker (`arm-none-eabi-ld`, `armlink`). | **Trình liên kết Linker (thông qua flag `-Map`).** |
| **Đối tượng sử dụng** | **Máy nạp vi điều khiển** (Flasher, J-Link, ST-Link, Bootloader qua CAN UDS). | **Trình gỡ lỗi phần cứng** (GDB Server, Lauterbach TRACE32, SEGGER Ozone). | **Kỹ sư nhúng, BSW Integrator, Kiến trúc sư hệ thống, CI/CD Script.** |
| **Tên biến & Tên hàm?** | ❌ **Hoàn toàn KHÔNG** (chỉ có byte dữ liệu vô hồn). | ✅ **CÓ** (Lưu trong bảng biểu tượng Symbol Table nhị phân). | ✅ **CÓ 100%** (Hiển thị rõ ràng bằng chữ cái tiếng Anh). |
| **Địa chỉ vật lý?** | ✅ CÓ (Địa chỉ nạp ROM để mạch nạp biết ghi vào đâu). | ✅ CÓ (Cả địa chỉ nạp ROM LMA lẫn địa chỉ chạy RAM VMA). | ✅ **CÓ CHI TIẾT ĐẾN TỪNG BYTE** (Kèm kích thước dạng Hex). |
| **Thông tin File gốc?** | ❌ KHÔNG (không biết byte nào sinh ra từ file C nào). | ✅ CÓ (Liên kết dòng code C với địa chỉ hợp ngữ DWARF). | ✅ **CÓ** (Chỉ rõ hàm/biến này trích từ file `.o` nào). |
| **Mục đích sinh ra** | Nạp vào Flash ROM để CPU khởi động và chạy. | Cắm Debugger đặt breakpoint, soi biến, xem thanh ghi CPU. | **Báo cáo "thu chi tài chính" của bộ nhớ, kiểm toán RAM/ROM.** |

> [!IMPORTANT]
> **Giải Đáp Cốt Tử: File `.map` Có Được Nạp Vào Vi Điều Khiển & Chạy Lúc Runtime Không?**  
> **CHÍNH XÁC LÀ KHÔNG BAO GIỜ!**  
> - **Chỉ có tệp mã máy (`.hex` / `.bin` hoặc firmware trích từ `.elf`) được nạp lên chip:** Mạch nạp (J-Link, ST-Link) hoặc UDS Bootloader chỉ đọc dữ liệu byte nhị phân 0 và 1 từ file `.hex`/`.bin` để ghi vào các ô nhớ Flash vật lý. Vi điều khiển chỉ có thể thực thi các xung điện áp tương ứng với các lệnh máy này.  
> - **File `.map` chỉ ở lại trên máy tính (PC) của lập trình viên:** Nó là một tệp văn bản ASCII thuần túy (*plaintext*). Vi điều khiển không có bộ nhớ hay trình thông dịch để chứa hay đọc các file chữ tiếng Anh như `.map`. Nó **hoàn toàn không chiếm dù chỉ 1 bit** trong Flash/RAM của ECU trên xe và CPU **hoàn toàn không biết tới sự tồn tại** của file `.map`.  
> - **Ẩn dụ dễ nhớ:** File `.map` là *Bản vẽ thiết kế kiến trúc và Hóa đơn vật tư xây dựng* nằm trên bàn của kỹ sư. File `.hex` là *Ngôi nhà thật* được xây bằng gạch vữa. Người ta vào ở trong ngôi nhà chứ không mang bản vẽ xây nhà nhồi vào trong cột bê tông!

---

### 3.2 File `.map` Có Trong Mọi Hệ Thống Nhúng Không? (Tính Phổ Quát & So Sánh Toolchains)

> 💡 **Khẳng định đanh thép:**  
> **File `.map` CÓ MẶT TRONG 100% CÁC HỆ THỐNG NHÚNG TRÊN THẾ GIỚI!**  
> Nó hoàn toàn **KHÔNG PHẢI** là phát minh riêng của AUTOSAR, mà là chuẩn mực công nghiệp bất biến của mọi trình liên kết (Linker) từ thuở sơ khai của ngành điện toán nhúng.

#### 1. Tại sao máy tính (PC / Server) ít quan tâm nhưng Hệ thống nhúng bắt buộc phải có `.map`?
- **Trên máy tính cá nhân (x86 Windows/Linux):** Bộ nhớ RAM tính bằng Gigabyte, hệ điều hành có Bộ quản lý bộ nhớ ảo (**MMU - Virtual Memory**). Ứng dụng chạy trên không gian ảo, thiếu RAM thì đẩy sang Swap/Page file trên ổ cứng. Lập trình viên thông thường chẳng cần biết biến của mình nằm ở địa chỉ vật lý nào.
- **Trên Hệ thống nhúng (Embedded Microcontroller):**
  - Vi điều khiển có tài nguyên phần cứng vật lý cực kỳ hữu hạn và cố định (Ví dụ: `lm3s6965evb` có đúng 256KB Flash và 64KB SRAM; nhiều chip nhỏ chỉ có 2KB RAM).
  - Không có bộ nhớ ảo Swap. Tràn 1 byte RAM là sập hệ thống (Crash/HardFault).
  - Các khối ngoại vi (CAN, DMA, Ethernet) bắt buộc phải đọc/ghi vào các địa chỉ RAM vật lý nhất định (Non-cacheable RAM hoặc DMA Buffer).
  - Do đó, kỹ sư nhúng **bắt buộc phải có "bản đồ địa chính" (.map)** để quản lý từng milimet không gian bộ nhớ.

#### 2. Bảng Tra Cứu Cờ Kích Hoạt File `.map` Trên Các Toolchain Nhúng Toàn Cầu

Bất kể bạn làm việc với vi điều khiển 8-bit, 16-bit, 32-bit hay DSP, mọi Toolchain thương mại lẫn mã nguồn mở đều có tùy chọn xuất file `.map`:

| Toolchain / Compiler | Cờ Kích Hoạt (Linker Flags) | Tên Tệp Xuất Ra | Môi Trường Điển Hình |
| :--- | :--- | :--- | :--- |
| **GNU GCC (`ld`)** | `-Wl,-Map=output.map,--cref` | `*.map` | GCC ARM, Dự án `as`, QEMU, Linux Kernel (`System.map`) |
| **Arm Compiler / Keil MDK (`armlink`)** | `--map --list=project.map --symbols` | `*.map` trong `Listings/` | STM32, NXP LPC, Bosch Body ECU |
| **IAR Embedded Workbench (`ilinkarm`)** | `--map project.map` | `*.map` trong `Output/` | Renesas RH850, NXP S32K, Thiết bị Y tế |
| **Tasking VX-toolset (`ltc`)** | `--map-file=project.map` | `*.map` | **Infineon TriCore AURIX** (ECU Động cơ, Khung gầm, Phanh ô tô) |
| **Green Hills MULTI (`elxr`)** | `-map=project.map` | `*.map` | **Hệ thống An toàn cao cấp ASIL D**, Gateway, ADAS Radar |
| **Texas Instruments (TI CGT)** | `-m project.map` | `*.map` | TI C2000, TMS570, DSP Radar ô tô |

*Bằng chứng trong mã nguồn dự án:* Trong tệp [`as/com/as.application/board.lm3s6965evb/SConscript:15`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/com/as.application/board.lm3s6965evb/SConscript#L15), cờ `-Map` được kích hoạt trực tiếp:
```python
asenv.Append(LINKFLAGS='-Map %s/lm3s6965evb.map'%(BDIR))
```

---

### 3.3 Tần Suất Gặp & 6 Tình Huống Bắt Buộc Làm Việc Với File `.map` Trong Dự Án Thực Tế

> ⏱️ **Tần suất làm việc thực tế:**  
> **CỰC KỲ CAO (Daily $\to$ Weekly).**  
> Trong một dự án phần mềm ô tô (Tier-1 / OEM), bạn sẽ mở và làm việc với file `.map` trung bình **3 đến 5 lần mỗi tuần** khi phát triển tính năng, và **100% bắt buộc** trong mỗi đợt Audit kiểm thử xuất xưởng (Pre-release gate).

Dưới đây là **6 Tình huống thực chiến sống còn** mà không một kỹ sư nhúng nào có thể né tránh việc mở file `.map`:

```
                 6 TÌNH HUỐNG THỰC CHIẾN BẮT BUỘC DÙNG FILE .map
                                       │
     ┌──────────────────┬──────────────┴──────────────┬──────────────────┐
     ▼                  ▼                             ▼                  ▼
[1. BUILD THẤT BẠI]  [2. RUNTIME CRASH]         [3. AN TOÀN ASIL D]  [4. ĐO LƯỜNG A2L]
  Tràn RAM/Flash       Sập HardFault / BusFault   Quy hoạch vùng MPU    Hiệu chuẩn CANape
  Linker dừng build    Truy vết biến bị đè        Cô lập phân vùng OS   Định vị địa chỉ biến
```

1. **Khi Build Thất Bại Do Tràn Bộ Nhớ (`region 'RAM' overflowed by XXX bytes`):**  
   Linker quăng lỗi và hủy bỏ việc sinh file `.elf`. Bạn không có file nhị phân để chạy, debugger vô tác dụng. File `.map` là **manh mối duy nhất** giúp bạn tìm ra ai là thủ phạm vừa nhét thêm mảng dữ liệu khổng lồ vào RAM.
2. **Khi Vi Điều Khiển Bị Sập Nguồn Bất Tử (HardFault / BusFault / MemManage Fault):**  
   Khi chip sập, bạn dừng debugger và đọc thanh ghi `PC` (Program Counter) hoặc `BFAR` (BusFault Address Register) thấy một con số lục phân (ví dụ `0x0000730c` hoặc `0x20004964`). Bạn mở file `.map`, tìm kiếm địa chỉ này để bắt quả tang ngay lập tức: *Hàm nào đang thực thi thì sập? Biến nào nằm ở địa chỉ đó vừa bị con trỏ hoang dã ghi đè?*
3. **Khi Giám Sát Ngân Sách Bộ Nhớ (Memory Budget Tracking) Trong CI/CD Pipeline:**  
   Các hãng xe lớn quy định ngưỡng trần bộ nhớ nghiêm ngặt: *Trước khi xuất xưởng, Flash không được vượt quá 80%, RAM không được vượt quá 75%* (để dành 25% cho bản cập nhật FOTA tương lai). Các script Python tự động trên GitLab CI sẽ bóc tách file `.map` sau mỗi commit để vẽ biểu đồ tăng trưởng dung lượng.
4. **Khi Thiết Lập Phân Vùng Bảo Vệ Phần Cứng MPU Cho Tiêu Chuẩn ISO 26262 ASIL D:**  
   MPU đòi hỏi địa chỉ bắt đầu và kích thước phân vùng phải căn chỉnh nghiêm ngặt (thường là lũy thừa của 2). Kỹ sư BSW phải soi file `.map` để lấy địa chỉ chính xác của `Task_Periodic_50ms_Stack` và các phân vùng ứng dụng nhằm điền vào bảng cấu hình MPU Driver.
5. **Khi Sinh Tệp Hiệu Chuẩn Tham Số A2L (Calibration với CANape / ETAS INCA):**  
   Để các kỹ sư chạy thử nghiệm trên xe thật có thể can thiệp thay đổi tham số động cơ qua giao thức XCP/CCP, phần mềm máy tính cần file `.a2l` ghi rõ địa chỉ RAM/ROM của từng biến. Tool sinh file A2L đọc trực tiếp file `.map` và `.elf` để phân giải địa chỉ.
6. **Khi Kiểm Toán Mã Rác / Mã Chết (Dead Code Elimination Audit):**  
   Soi xét mục `Discarded input sections` của file `.map` để chứng minh các đoạn mã thử nghiệm, các hàm debug không dùng đã bị Linker xóa sổ hoàn toàn, không chiếm dụng dù chỉ 1 byte Flash trên xe thương mại.

---

### 3.4 Giải Phẫu Chi Tiết 5 Phân Khu Cơ Thể Của File `lm3s6965evb.map` Thực Nghiệm

Mở tệp thực tế [`as/build/nt/lm3s6965evb/ascore/lm3s6965evb.map`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/build/nt/lm3s6965evb/ascore/lm3s6965evb.map) (dài 5.193 dòng), cấu trúc tệp được chia thành **5 Phân khu cơ thể kinh điển** của GNU Linker:

```
┌────────────────────────────────────────────────────────────────────────┐
│ PHÂN KHU 1: DISCARDED INPUT SECTIONS (Dòng 1 - 1818)                   │
│ • Danh sách tất cả các hàm, biến bị Linker "trảm" do không có ai dùng │
├────────────────────────────────────────────────────────────────────────┤
│ PHÂN KHU 2: MEMORY CONFIGURATION (Dòng 1819 - 1825)                    │
│ • Khai báo không gian vật lý của phần cứng chip (FLASH 256K, RAM 64K)  │
├────────────────────────────────────────────────────────────────────────┤
│ PHÂN KHU 3: LINKER SCRIPT AND MEMORY MAP (Dòng 1826 - 4234) [TRỌNG TÂM]│
│ • Chi tiết từng Section: .text, .rodata, .data, .bss, .init_stack      │
│ • Từng biến, hàm, VMA, LMA, kích thước (Hex), file .o sở hữu          │
├────────────────────────────────────────────────────────────────────────┤
│ PHÂN KHU 4: BÃY ĐỆM LÃNG PHÍ BỘ NHỚ (*fill*)                           │
│ • Các khoảng hở byte đệm rác sinh ra do căn chỉnh ALIGN                │
├────────────────────────────────────────────────────────────────────────┤
│ PHÂN KHU 5: DANH SÁCH FILE NGUỒN LOAD & BẢNG TRA CHÉO KÝ HIỆU (CREF)   │
│ • Danh sách file .o tham gia build và quan hệ gọi hàm/biến liên file   │
└────────────────────────────────────────────────────────────────────────┘
```

#### 1️⃣ Phân khu 1: `Discarded input sections` (Dòng 1 – 1818)
Liệt kê những khối mã máy và biến đã bị loại bỏ hoàn toàn nhờ cờ tối ưu hóa Linker `-Wl,--gc-sections`:
```map
Discarded input sections

 .text.Can_GetChar
                0x00000000       0x14 build\nt\lm3s6965evb\ascore\com\as.infrastructure\arch\lm3s\mcal\Can.o
 .text.ADCIntRegister
                0x00000000       0x50 build\nt\lm3s6965evb\ascore\com\as.infrastructure\arch\lm3s\DriverLib\src\adc.o
```
- **Ý nghĩa:** Hàm `Can_GetChar` (kích thước `0x14` = 20 bytes) trong file `Can.o` không được bất kỳ module nào gọi $\rightarrow$ Linker loại bỏ (địa chỉ gán về `0x00000000`). Nhờ đó tiết kiệm 20 bytes Flash!

#### 2️⃣ Phân khu 2: `Memory Configuration` (Dòng 1819 – 1825)
Xác nhận giới hạn vật lý của con chip theo chỉ thị `MEMORY` trong Linker Script:
```map
Memory Configuration

Name             Origin             Length             Attributes
FLASH            0x00000000         0x00040000         xr
RAM              0x20000000         0x00010000         xrw
*default*        0x00000000         0xffffffff
```
- `FLASH`: Bắt đầu từ `0x00000000`, độ dài `0x00040000` (256 KB), thuộc tính thực thi & đọc (`xr`).
- `RAM`: Bắt đầu từ `0x20000000`, độ dài `0x00010000` (64 KB), thuộc tính thực thi, đọc & ghi (`xrw`).

#### 3️⃣ Phân khu 3: `Linker script and memory map` (Dòng 1826 – 4234) — Phân khu Trọng yếu nhất
Đây là nơi ghi lại sự ra đời của từng byte bộ nhớ. Cú pháp chuẩn của từng dòng:
```map
[Tên Section / Biến]     [Địa chỉ VMA]    [Kích thước Size]   [Địa chỉ LMA nạp]  [File .o sở hữu]
```

Trích xuất các mốc địa chỉ thực tế then chốt từ tệp `lm3s6965evb.map`:

* **Khối Mã Máy `.text` (Flash ROM):**
  ```map
  .text           0x00000000    0x172d4
   .isr_vector    0x00000000      0x400 build\...\startup.o
                  0x00000000                __vector_table
   .startup       0x00000400       0x48 build\...\startup.o
                  0x00000400                reset_handler
   .text.D_Init   0x00000448       0x16 build\...\OsekNm_Cfg.o
                  0x00000448                D_Init
  ```
  $\rightarrow$ Toàn bộ code `.text` chiếm `0x172d4` (94.932 bytes ~ 92.7 KB). Vector ngắt nằm chuẩn xác tại `0x00000000`, hàm khởi động `reset_handler` bắt đầu tại `0x00000400`.

* **Khối Biến Khởi Tạo `.data` (RAM có giá trị ban đầu từ Flash):**
  ```map
  0x000172d4                __etext = .

  .data           0x20000000      0x1c4 load address 0x000172d4
                  0x20000000                        . = ALIGN (0x4)
                  0x20000000                        __data_start__ = .
   .data.ComMLsUser_ChannleList
                  0x20000000        0x4 build\...\ComM_Cfg.o
   .data.rbV_canin
                  0x20000008        0x8 build\...\SCan.o
                  0x200001c4                        __data_end__ = .
  ```
  $\rightarrow$ VMA tại `0x20000000`, kích thước `0x1c4` (452 bytes). Địa chỉ nạp LMA nằm tại Flash `0x000172d4` (ngay sau nhãn `__etext`).

* **Khối Biến Bằng Không `.bss` (SRAM thuần túy):**
  ```map
  .bss            0x200001c4     0x73c8 load address 0x00017498
                  0x200001c4                        __bss_start__ = .
   *(.bss*)
   .bss.Task_Periodic_50ms_Stack
                  0x20004960      0x200 build\...\Os_Cfg.o
   .bss.Task_QueueTester_Stack
                  0x20004b60      0x200 build\...\Os_Cfg.o
   .bss.xcpOdtEntryDYN
                  0x2000558c     0x2000 build\...\Xcp_Cfg.o
                  0x2000758c                        __bss_end__ = .
  ```
  $\rightarrow$ Toàn bộ `.bss` chiếm tới `0x73c8` (29.640 bytes ~ 28.9 KB).  
  $\rightarrow$ Hai task của Task 2.3 ta vừa tạo xuất hiện rực rỡ tại đây: `Task_Periodic_50ms_Stack` chiếm `0x200` bytes (512 bytes) tại `0x20004960`, và `Task_QueueTester_Stack` chiếm `0x200` bytes tại `0x20004b60`!

* **Khối Ngăn Xếp Hệ Thống `.init_stack`:**
  ```map
  .init_stack     0x20007590      0x400 load address 0x0001e864
                  0x20007590                        knl_system_stack = .
   *fill*         0x20007590      0x400 
                  0x20007990                        knl_system_stack_top = .
  ```
  $\rightarrow$ Đỉnh ngăn xếp hệ thống `knl_system_stack_top` nằm tại địa chỉ `0x20007990`.

#### 4️⃣ Phân khu 4: Bẫy Đệm Lãng Phí Bộ Nhớ (`*fill*`)
Trong file map xuất hiện các dòng bí ẩn mang tên `*fill*`:
```map
.text.Can_SetControllerMode
               0x00001454       0x26 build\...\SCan.o
*fill*         0x0000147a        0x2 
.text.Can_Write
               0x0000147c      0x140 build\...\SCan.o
```
- **Bản chất kỹ nghệ:** Hàm `Can_SetControllerMode` kết thúc tại `0x0000147a` (địa chỉ không chia hết cho 4). Lệnh tiếp theo `Can_Write` yêu cầu căn hàng 4 bytes (`ALIGN(4)`). Linker bắt buộc phải chèn thêm **2 byte rác vô nghĩa** (`*fill* 2 bytes`) để đẩy địa chỉ lên `0x0000147c`. Nếu trong một dự án có hàng nghìn biến/hàm lẻ hàng, dung lượng lãng phí có thể lên tới nhiều Kilobyte!

#### 5️⃣ Phân khu 5: Danh Sách File Đối Tượng (`LOAD`) & Bảng Tra Chéo Ký Hiệu (`--cref`)
Từ dòng 4235 trở đi, Linker liệt kê tường minh toàn bộ các file `.o` được nạp vào tiến trình liên kết:
```map
LOAD build\nt\lm3s6965evb\ascore\com\as.application\board.lm3s6965evb\common\Mcu_Cfg.o
LOAD build\nt\lm3s6965evb\ascore\config\Os_Cfg.o
...
```
Nếu thêm cờ `--cref` (*Cross Reference Table*), Linker sẽ in ra bảng ma trận: Biến `SchM_Actived` được định nghĩa ở `SchM.o` và đang được những file nào (`app.o`, `EcuM.o`) tham chiếu tới.

---

### 3.5 Tuyệt Chiêu "Pháp Y Bộ Nhớ": Đọc `.map` Bắt Bệnh Đẳng Cấp Senior

Một kỹ sư Senior không đọc tuần tự từ dòng 1 đến dòng 5.000 của file `.map`. Họ sử dụng **3 tuyệt chiêu tra cứu pháp y** sau:

#### 🎯 Tuyệt chiêu 1: Săn lùng "Quái vật ngốn RAM tĩnh" (Hunting Static Memory Hogs at Build-Time)

> ⚠️ **Làm rõ rạch ròi bản chất kỹ nghệ (Build-Time Static vs Runtime Dynamic):**  
> File `.map` là sản phẩm của Linker nên nó **chỉ phản ánh 100% Bộ nhớ tĩnh (Static Allocation)** được tính toán tại thời điểm **Build** (tổng dung lượng các biến toàn cục `.data`, `.bss`, các mảng Stack tĩnh được cấp phát trước cho từng Task và OS System Stack). File `.map` **hoàn toàn không thể** đo lường mức độ co giãn ngăn xếp cục bộ (local call stack) hay con trỏ động khi CPU đang chạy thực tế trên xe.  
> Vì vậy, khái niệm *"Khi RAM sắp cạn"* ở đây được định nghĩa chuẩn xác là: **Khi tổng dung lượng cấp phát tĩnh (`.data` + `.bss` + `.init_stack`) tiệm cận ngưỡng trần ngân sách dự án (ví dụ > 80% RAM) hoặc khi vượt quá 100% khiến Linker quăng lỗi đỏ `region 'RAM' overflowed` ngay trên máy tính của dev!**

Để truy tìm nhanh những thủ phạm chiếm dụng RAM tĩnh lớn nhất trong tệp `.map`, mở file trong VS Code và nhấn `Ctrl + F` với chế độ Regular Expression (Regex):
- Tìm các biến trong `.bss` có kích thước tĩnh từ 1KB trở lên (`>= 0x400` bytes):
  ```regex
  \.bss\.\w+\s+0x2000\w+\s+0x[4-9a-fA-F0-9]{3,}
  ```
- Kết quả từ `lm3s6965evb.map` chỉ điểm ngay:
  ```map
  .bss.xcpOdtEntryDYN
                 0x2000558c     0x2000 build\...\Xcp_Cfg.o
  ```
  $\rightarrow$ Biến cấu hình giao thức XCP `xcpOdtEntryDYN` đang ngốn tới **8.192 bytes (8KB RAM - chiếm 12.5% toàn bộ RAM tĩnh của ECU!)**. Nếu dự án này không cần calibration XCP trên xe thực tế, ta có thể giảm cấu hình XCP trong XML để thu hồi ngay 8KB RAM tĩnh.

#### 🎯 Tuyệt chiêu 2: Bắt Quả Tang Hiện Tượng Lệch Hàng Cấu Trúc (Struct Packing Audit)
Khi khai báo một cấu trúc dữ liệu:
```c
struct BadStruct {
    uint8_t  flag;      /* 1 byte */
    /* Linker bí mật chèn 3 bytes đệm (*fill*) vào đây! */
    uint32_t timestamp; /* 4 bytes */
    uint16_t id;        /* 2 bytes */
    /* Linker bí mật chèn thêm 2 bytes đệm (*fill*) vào cuối! */
}; /* Tổng kích thước bị đội lên 12 bytes thay vì 7 bytes! */
```
Mở file `.map`, tìm kiếm tên struct đó và quan sát các dòng `*fill*`.  
👉 **Cách khắc phục chuẩn Senior:** Sắp xếp lại thứ tự khai báo biến trong struct theo quy tắc "to đứng trước, nhỏ đứng sau" (32-bit $\to$ 16-bit $\to$ 8-bit), biến struct từ 12 bytes về đúng 8 bytes mà không tốn 1 byte đệm rác nào!

#### 🎯 Tuyệt chiêu 3: Truy Vết "Kẻ Láng Giềng Độc Ác" Khi Con Trỏ Bị Ghi Đè (Memory Corruption Forensics)
Đây là kỹ năng phân định đẳng cấp: Giả sử biến cờ an toàn phanh `g_BrakeActive` bỗng nhiên bị nhảy về giá trị rác khiến xe phanh gấp vô cớ. Đặt watchpoint không bắt được vì do DMA hoặc ngắt ngầm ghi đè.  
1. Mở file `.map`, tìm địa chỉ của `g_BrakeActive`:
   ```map
   0x20002100                g_BrakeActive
   ```
2. Soi ngay **biến láng giềng nằm ngay phía trước nó** trong `.map`:
   ```map
   .bss.Can_RxFifoBuffer
                  0x20002080       0x80 build\...\Can.o
   ```
3. Phân tích số học: `Can_RxFifoBuffer` bắt đầu từ `0x20002080`, độ dài `0x80` (128 bytes).  
   Địa chỉ kết thúc của nó = `0x20002080 + 0x80 = 0x20002100` $\rightarrow$ **Chính là vạch xuất phát của `g_BrakeActive`!**
4. **Kết luận phá án:** Lập trình viên xử lý hàm nhận CAN đã viết vòng lặp `for(i=0; i<=128; i++)` (vượt biên mảng 1 phần tử), ghi đúng 1 byte số 129 tràn sang đè nát biến `g_BrakeActive`!  
   *Không có file `.map`, bạn sẽ vĩnh viễn không bao giờ tìm ra lỗi này dù có ngồi debug hàng tháng trời!*

---

### 3.6 Kịch Bản Cứu Hộ 1: Xử Lý Lỗi Tràn Bộ Nhớ (`region 'RAM' overflowed`)

#### Hiện tượng lỗi:
Khi thêm một mảng buffer lớn trong code, trình biên dịch báo lỗi đỏ:
```bash
arm-none-eabi/bin/ld.exe: region 'RAM' overflowed by 2048 bytes
collect2.exe: error: ld returned 1 exit status
scons: *** [build/nt/lm3s6965evb/ascore/lm3s6965evb.exe] Error 1
```

#### Quy trình 3 bước xử lý chuẩn Senior:
1. **Bước 1: Mở tệp `.map` và nhảy đến phân đoạn `.bss`:**  
   Tìm dòng tổng kết kích thước `.bss` và `.data`. Kích thước SRAM vượt quá `64K` (`0x10000`).
2. **Bước 2: Truy tìm "Kẻ tội đồ" ngốn RAM:**  
   Lọc các biến có cột Size lớn nhất trong `.map`. Ví dụ:
   ```map
   .bss.large_diagnostic_buffer
                  0x20006000     0x2000 build\...\diag_app.o
   ```
   $\rightarrow$ Phát hiện file `diag_app.c` vừa khai báo một biến tĩnh `uint8 large_diagnostic_buffer[8192]` chiếm tới 8KB RAM!
3. **Bước 3: Giải pháp kỹ thuật khắc phục:**
   - **Tối ưu hóa Stack của Task:** Mở `autosar.arxml` hoặc `app.xml`, kiểm tra các Task đang để `StackSize="2048"`. Nếu Task đó chỉ chạy vài lệnh đơn giản, giảm xuống `StackSize="512"` $\rightarrow$ Tiết kiệm ngay 1.5KB RAM mỗi Task.
   - **Tái sử dụng Buffer (Union / Shared Memory):** Nếu 2 chức năng chẩn đoán và flash không bao giờ chạy đồng thời, cho chúng dùng chung một vùng nhớ `union`.
   - **Chuyển bảng tra cứu sang Flash:** Kiểm tra xem mảng dữ liệu có bị quên từ khóa `const` không. Thêm `const` sẽ đẩy mảng từ RAM (`.data`) sang Flash (`.rodata`).

---

### 3.7 Kịch Bản Cứu Hộ 2: Điều Tra Sập Nguồn (HardFault / BusFault / MemManage Fault)

#### Nguyên nhân kỹ thuật từ Linker Script:
1. **Lệch căn chỉnh địa chỉ (Alignment Mismatch):**  
   - Vi điều khiển bật tính năng bẫy lỗi chia cho 0 hoặc truy cập dữ liệu không thẳng hàng (UNALIGN_TRP trong CCR register). Nếu một biến 32-bit bị Linker xếp ở địa chỉ lẻ (ví dụ `0x20000001`), lệnh đọc lệnh `LDR` sẽ quăng ngay ngoại lệ **UsageFault** hoặc **HardFault**.
   - 👉 **Cách sửa:** Luôn thêm `. = ALIGN(4);` trước và sau các phân đoạn trong Linker Script.
2. **Vi phạm phân vùng bảo vệ bộ nhớ MPU (MemManage Fault):**  
   - Trong chuẩn ISO 26262 ASIL-D, phần cứng MPU yêu cầu phân vùng bảo vệ phải có kích thước là lũy thừa của 2 ($2^N$: 32B, 64B, 128B, 1KB, 4KB...).
   - Nếu Linker Script cấp phát một Task Stack dài 1.500 bytes (không phải lũy thừa 2), driver MPU sẽ thiết lập sai thanh ghi `MPU_RASR` $\rightarrow$ Khi Task vừa switch context, CPU kích hoạt **MemManage Fault** lập tức!

---

### 3.8 Kịch Bản Cứu Hộ 3: Tràn Ngăn Xếp Task (Stack Overflow & Tràn Đè Biến Toàn Cục)

Trong kiến trúc bộ nhớ, nếu Stack được xếp liền kề biến dữ liệu:
```
[VÙNG BIẾN TOÀN CỤC .bss] ◄────── [STACK CỦA TASK PHÁNH ABS (Đi xuống ▼)]
```
Khi Task gọi hàm đệ quy hoặc khai báo mảng cục bộ quá lớn, đỉnh Stack sẽ đè thủng ranh giới và ghi đè vào biến toàn cục của hệ thống phanh $\rightarrow$ Gây tai nạn thảm khốc!

👉 **Biện pháp cứu hộ trong Linker Script & OS:**
1. **Cấu hình Stack Protection Zone (MPU Guard Region):** Cấu hình Linker Script chèn một vùng đệm trống 32 bytes giữa các Stack và đặt quyền truy cập là `NOACCESS`. Nếu Task tràn 1 byte, MPU sẽ bắt sống và reset an toàn.
2. **Kiểm tra tệp `.map`:** Luôn đảm bảo khoảng cách giữa đỉnh Stack và đáy vùng nhớ tiếp theo không bị đè lên nhau.

---

## 4. NĂNG LỰC 3: Bộ Câu Hỏi Phỏng Vấn Thực Chiến Chuyên Sâu (Senior BSW / ECU Integration)

Dưới đây là 10 câu hỏi phỏng vấn phân loại ứng viên cấp độ Senior tại Bosch, Denso, VinFast, LG, Aptiv:

#### ❓ Câu 1: Sự khác biệt bản chất giữa VMA và LMA trong Linker Script là gì?
> **Trả lời:**  
> VMA (*Virtual/Run Memory Address*) là địa chỉ bộ nhớ mà đối tượng (hàm hoặc biến) cư trú khi chương trình đang thực thi. LMA (*Load Memory Address*) là địa chỉ lưu trữ thực tế của đối tượng đó trong bộ nhớ Flash ROM khi nạp firmware.  
> Đối với `.text` và `.rodata`, VMA trùng LMA (đều ở Flash). Đối với `.data`, VMA nằm ở RAM nhưng LMA nằm ở Flash; mã khởi động Startup sẽ copy dữ liệu từ LMA sang VMA khi bật nguồn.

#### ❓ Câu 2: Tại sao hàm xóa/ghi Flash (`Fls`) trong AUTOSAR thường phải được cấu hình chạy trên RAM (`.ramcode`)?
> **Trả lời:**  
> Do giới hạn phần cứng của chip nhớ Flash gọi là **Read-While-Write (RWW) restriction**. Khi mạch sạc nội bộ của chip đang thực hiện thao tác xóa sector hoặc nạp điện áp ghi Flash, toàn bộ Flash Bank đó bị khóa bus. Nếu CPU cố tình đọc lệnh tiếp theo từ Flash, phần cứng sẽ phát sinh lỗi **BusFault / Data Abort**.  
> Do đó, Linker Script phải định vị các hàm điều khiển Flash vào phân đoạn `.ramcode` với `LMA ở Flash` nhưng `VMA ở RAM`. Khi chạy, CPU thực thi mã lệnh 100% trên SRAM để Flash được tự do xóa ghi.

#### ❓ Câu 3: Khi biên dịch, Linker báo lỗi: `region 'RAM' overflowed by 512 bytes`. Là một kỹ sư BSW Integration, bạn giải quyết thế nào?
> **Trả lời:**  
> 1. Mở tệp ánh xạ `.map` sinh ra từ lần build gần nhất, điều hướng đến phân đoạn `.bss` và `.data`.  
> 2. Tìm kiếm các đối tượng có kích thước lớn nhất (tìm các mảng buffer, biến toàn cục mới thêm).  
> 3. Đánh giá xem có biến mảng nào quên khai báo `const` không (nếu có, thêm `const` để đẩy sang Flash).  
> 4. Rà soát cấu hình kích thước Stack của các Task trong file XML/ARXML. Giảm bớt dung lượng Stack của các Task đơn giản.  
> 5. Áp dụng kỹ thuật dùng chung bộ nhớ (`union`) hoặc cấu hình phân vùng `(NOLOAD)` cho các buffer chẩn đoán không dùng đồng thời.

#### ❓ Câu 4: Chỉ thị `KEEP()` trong Linker Script dùng để làm gì? Điều gì xảy ra nếu quên đặt `KEEP(*(.isr_vector))`?
> **Trả lời:**  
> Chỉ thị `KEEP()` báo cho trình liên kết biết: tuyệt đối không được xóa bỏ phân đoạn này kể cả khi bật cờ tối ưu hóa loại bỏ mã thừa `--gc-sections` (Garbage Collection).  
> Bảng Vector Ngắt (`.isr_vector`) chỉ được phần cứng CPU truy xuất gián tiếp qua con trỏ phần cứng lúc có ngắt, không có hàm C nào gọi trực tiếp nó. Nếu không có `KEEP()`, Linker coi đó là "dead code" và xóa sạch bảng ngắt, khiến CPU không thể khởi động được (chết ngay tại Reset).

#### ❓ Câu 5: Phân đoạn `.noinit` trong Linker Script của ô tô có ý nghĩa sống còn gì?
> **Trả lời:**  
> Mọi biến trong `.bss` đều bị mã Startup xóa về `0` khi bật nguồn. Tuy nhiên, trong ECU xe hơi, khi xảy ra sự cố (Watchdog Reset, Crash, lỗi phần mềm), hệ thống cần ghi lại mã lỗi chẩn đoán (DTC), dữ liệu đóng băng (Freeze Frame) hoặc trạng thái ECU vào RAM trước khi reset.  
> Phân đoạn `.noinit` được gắn cờ `(NOLOAD)` trong Linker Script để ngăn mã Startup ghi đè số `0`. Nhờ đó, sau khi chip khởi động lại, phần mềm có thể đọc được nguyên nhân gây reset trước đó và gửi báo cáo về máy quét UDS.

#### ❓ Câu 6: Tại sao tiêu chuẩn an toàn chức năng ISO 26262 ASIL-D lại yêu cầu căn chỉnh địa chỉ theo Lũy thừa của 2 (Power-of-2 Alignment)?
> **Trả lời:**  
> Vì kiến trúc phần cứng của Bộ bảo vệ bộ nhớ (MPU - Memory Protection Unit) trên vi điều khiển ô tô (ARM Cortex-M/R, Infineon TriCore) sử dụng cơ chế mặt nạ địa chỉ (Base Address & Size Mask). Phần cứng MPU yêu cầu biên giới của mỗi vùng bảo vệ phải bắt đầu tại địa chỉ chia hết cho kích thước của vùng đó ($2^N$: 32B, 64B, 128B... 4KB...).  
> Linker Script bắt buộc phải dùng chỉ thị `. = ALIGN(size)` để đảm bảo vùng nhớ của các OS-Application ASIL-D không bị lệch boundary, tránh gây ra ngoại lệ `MemManage Fault`.

#### ❓ Câu 7: Phân biệt sự khác nhau giữa biến `knl_system_stack_top` định nghĩa trong Linker Script và biến C thông thường?
> **Trả lời:**  
> Một biến C thông thường chiếm một ô nhớ cụ thể trong RAM và lưu trữ một giá trị dữ liệu bên trong ô nhớ đó.  
> Ngược lại, `knl_system_stack_top` trong Linker Script chỉ là một **Nhãn Biểu Tượng (Symbol Label)** đại diện cho một con số địa chỉ trên thanh ghi địa chỉ của Linker, nó **hoàn toàn không chiếm dụng bộ nhớ RAM**. Trong mã Assembly/C, việc lấy giá trị của nó thực chất là lấy địa chỉ mà nó đang đứng (`&knl_system_stack_top`).

#### ❓ Câu 8: Phân vùng `.calib` trong Linker Script của hệ thống ECU động cơ/pin dùng để làm gì?
> **Trả lời:**  
> Dùng để chứa các tham số hiệu chuẩn xe (Bản đồ góc đánh lửa, tỷ lệ pha xăng gió, ngưỡng bảo vệ quá nhiệt pin BMS).  
> Linker Script ghim phân vùng này tại một địa chỉ Flash cố định tuyệt đối. Nhờ đó, các kỹ sư Calibration hiện trường có thể dùng công cụ INCA / CANape qua giao thức XCP để nạp đè file thông số mới (`.hex` tham số) mà không cần phải biên dịch lại toàn bộ mã nguồn của ECU.

#### ❓ Câu 9: Trình tự thực thi của vi điều khiển từ lúc có nguồn đến khi vào hàm `main()` diễn ra như thế nào dựa trên Linker Script?
> **Trả lời:**  
> 1. Phần cứng đọc địa chỉ `0x00000000` (Vector 00) nạp vào con trỏ ngăn xếp `SP` (`knl_system_stack_top`).  
> 2. Đọc địa chỉ `0x00000004` (Vector 01) nạp vào con trỏ lệnh `PC` (`reset_handler`).  
> 3. `reset_handler` chạy: nạp các nhãn `__etext`, `__data_start__`, `__data_end__` từ Linker Script để copy `.data` từ Flash sang RAM.  
> 4. Nạp các nhãn `__bss_start__`, `__bss_end__` để xóa vùng `.bss` về 0.  
> 5. Gọi lệnh nhảy `bl main` để bàn giao quyền điều khiển cho chương trình C.

#### ❓ Câu 10: Tệp `.map` được sinh ra khi nào? Kỹ sư BSW dùng nó vào những tình huống nào?
> **Trả lời:**  
> Tệp `.map` được Linker sinh ra ở giai đoạn cuối cùng của quá trình build (Linking Phase).  
> Kỹ sư BSW sử dụng tệp `.map` trong 3 trường hợp:  
> 1. Khi build thất bại do tràn RAM/Flash (Overflow): để phân tích module nào ngốn bộ nhớ.  
> 2. Khi debug lỗi sập chip (HardFault / Data Abort): lấy giá trị thanh ghi `PC` / `LR` bị lỗi đối soát vào `.map` để tìm chính xác dòng code C gây crash.  
> 3. Khi nghiệm thu phần mềm (Memory Budgeting Review): đối soát dung lượng RAM/Flash thực tế với hạn mức kỹ thuật của dự án.

---

## 5. Tổng Kết & Checklist Kiểm Tra Linker Script Trước Khi Release Firmware

Trước khi bàn giao một bản build firmware ECU cho đội kiểm thử trên xe (Vehicle Test), kỹ sư tích hợp bắt buộc phải thực hiện bảng kiểm tra an toàn sau:

```markdown
### 📋 CHECKLIST KIỂM TRA BỘ NHỚ VẬT LÝ & LINKER SCRIPT:
- [ ] 1. Địa chỉ ORIGIN và LENGTH trong lệnh MEMORY có khớp 100% với Datasheet phần cứng của vi điều khiển không?
- [ ] 2. Bảng Vector Ngắt có chỉ thị `KEEP(*(.isr_vector))` chống cờ trảm rác `--gc-sections` chưa?
- [ ] 3. Tất cả các phân đoạn `.data` và `.bss` có lệnh `. = ALIGN(4)` để đảm bảo căn chỉnh 32-bit không?
- [ ] 4. Phân đoạn `.data` có chỉ thị nạp `AT (__etext)` để lưu giá trị gốc trong Flash không?
- [ ] 5. Dung lượng System Stack (`knl_system_stack_size`) và Task Stacks có đủ lớn để chống tràn không?
- [ ] 6. Các hàm điều khiển ghi xóa Flash (`Fls`) đã được gán vào phân đoạn `.ramcode` để chạy trên RAM chưa?
- [ ] 7. Mở file `.map`, kiểm tra dung lượng RAM trống còn tối thiểu 15% – 20% (Headroom Safety Margin) không?
- [ ] 8. Các phân vùng bảo vệ MPU có tuân thủ quy tắc kích thước lũy thừa của 2 ($2^N$) theo ISO 26262 chưa?
```

> 💡 **Kết luận cốt tử:**  
> Linker Script không phải là một file cấu hình thụ động, mà là **xương sống điều phối bộ nhớ vật lý của toàn bộ chiếc xe**. Làm chủ Linker Script chính là chìa khóa mở cánh cửa trở thành một **Kỹ Sư Kiến Trúc BSW / ECU Integration Đẳng Cấp Cao** trong ngành công nghiệp ô tô toàn cầu!
