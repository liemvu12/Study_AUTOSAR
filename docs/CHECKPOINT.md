# 📍 CHECKPOINT REGISTRY — DAILY CHANGE LOG
## Nhật Ký Theo Dõi Thay Đổi Theo Ngày (Daily Project Change Tracker)

> 📌 **Mục đích:** Ghi nhận danh sách tất cả các tệp (files) và thư mục (folders) được tạo mới hoặc chỉnh sửa theo từng ngày cụ thể.
> ⚠️ **Quy tắc bắt buộc (Mandatory Rule):** Mỗi khi thực hiện bất kỳ thay đổi nào trong ngày, **BẮT BUỘC phải cập nhật danh sách vào file `CHECKPOINT.md` này trước khi commit và push lên GitLab**.

## 📅 NGÀY 08/09/2026 (HÔM NAY) — THAY ĐỔI SO VỚI NGÀY 07/09/2026

> 🎯 **Trọng tâm hôm nay:**  
> • **Bổ sung Phân biệt rạch ròi ECU (Electronic Control Unit) vs MCU (Microcontroller Unit) vào Chuyên đề 01 (Mục 3.0 & Glossary)**:
>   - Giải mã bản chất kỹ nghệ: Phân định rạch ròi giữa MCU (con chip bán dẫn silicon tích hợp CPU/RAM/Flash/Ngoại vi logic đóng vai trò "Bộ não") vs ECU (toàn bộ hộp thiết bị hoàn chỉnh đóng vỏ nhôm IP67, gồm nguồn PMIC/SBC 12V/24V, mạch bảo vệ TVS/EMC, Transceiver CAN/LIN/Ethernet, mạch công suất MOSFET/H-Bridge và giắc cắm Harness đóng vai trò "Toàn bộ cơ thể").
>   - Bảng so sánh đối chiếu 8 tiêu chí kỹ thuật (Bản chất, Kích thước, Dòng/Nguồn điện, Ngoại vi, Chuẩn kiểm nghiệm AEC-Q100 vs ISO 16750/IP67, Số lượng MCU trên 1 ECU, Chuỗi cung ứng Silicon Vendors vs Tier-1 Suppliers).
>   - Ánh xạ vào kiến trúc phân tầng AUTOSAR: MCU gắn liền tầng MCAL (`Mcu`, `Port`, `Dio`, `Can`), ECU gắn liền tầng ECU Abstraction (`CanIf`, `IoHwAb`) và Service (`EcuM`).
> • Tái cấu trúc phân bổ chuyên đề chuẩn mực: **Bổ sung Phân tích Linker Script vào Chuyên đề 05 (Toolchain & ECU Integration)** và tinh gọn Chuyên đề 02:  
>   - **Bổ sung Mục 3.5 Chuyên Đề 05: Nghịch Lý Linker Script Trong Toolchain & ECU Integration (So Sánh Toàn Diện AUTOSAR Linker vs Bare-Metal vs Linux/Zephyr)**:
>     * Đặt đúng trọng tâm kiến trúc: Linker Script và Memory Layout là sản phẩm then chốt của giai đoạn Toolchain & ECU Integration, không thuộc phạm vi hẹp của driver MCAL hay nhân OS.
>     * Giải mã nghịch lý kỹ nghệ: Dù không dùng macro gom hàm đăng ký động vào section kiểu `.initcall`, Linker Script trong AUTOSAR Classic lại phức tạp, đồ sộ và khắt khe bậc nhất thế giới nhúng (dài hàng nghìn đến hàng chục nghìn dòng trong dự án thương mại).
>     * Bóc tách 4 trọng trách kỹ nghệ sống còn của kỹ sư ECU Integration: (1) Đặc tả MemMap.h hàng trăm sections chi tiết; (2) Phân vùng bảo vệ bộ nhớ MPU căn chỉnh lũy thừa 2 (Power-of-2 Alignment) cách ly an toàn ASIL-D; (3) Phân bổ tĩnh bộ nhớ vi điều khiển đa lõi (DSPR0/1 trên Infineon AURIX, D-TCM trên ARM Cortex-R, Global Non-cacheable Shared RAM); (4) Phân đoạn nạp Firmware: Bootloader, Vùng Calibration cố định địa chỉ tuyệt đối cho CANape/INCA, và Vùng RAM Code (`.ramcode` / `linker-flsdrv.lds` ở `0x20000000`) khắc phục hiện tượng Read-While-Write (RWW) của Flash.
>     * Thiết lập bảng so sánh đối chiếu 7 tiêu chí giữa 3 thế giới kiến trúc: Bare-Metal thông thường vs General OS (Linux/Zephyr) vs Automotive AUTOSAR Classic.
>     * Phân tích minh chứng pháp y 3 file Linker Script thực tế trong `Study_AUTOSAR`: `linker-app.lds`, `linker-boot.lds`, và `linker-flsdrv.lds`.
>     * Bổ sung Câu hỏi phỏng vấn số 61 & 62 (Expert Level) về Linker Script & RAM Code trong Chuyên đề 05; chuẩn hóa Bảng kiểm tra ECU Integration Checklist (Mục 8).
>   - **Tinh gọn Chuyên Đề 02 & Tái Cấu Trúc Mục 9 Theo Thứ Tự Khởi Tạo Chuẩn Của EcuM**:
>     * Tinh gọn: Thay thế phân tích Linker Script cồng kềnh bằng Architecture Callout Note dẫn link trực tiếp sang Chuyên đề 05 Mục 3.5, giữ cho Chuyên đề 02 tập trung tuyệt đối vào OS Kernel và MCAL.
>     * **Bổ sung Mục 9.1 Trọng Trách Kỹ Nghệ: Thứ Tự Khởi Tạo Chuẩn Của 9 Module MCAL Trong Chu Trình EcuM (Hardware Dependency & Power-On Sequencing)**:
>       - Giải mã chuỗi phụ thuộc phần cứng (Silicon Dependency Pipeline) 3 giai đoạn: `DriverInitZero` (Mcu, Wdg) ──► `DriverInitOne` (Port, Dio, Gpt, Fls) ──► `StartupTwo` (Spi, Adc, Can).
>       - Bóc tách bản chất kỹ nghệ vì sao `Mcu` bắt buộc phải là số 1 (cấp clock APB/AHB và khóa PLL, tránh Bus Fault), `Wdg` số 2 (chống bootloop/deadlock), `Port` số 3 (PinMux nối chân ra ngoài trước khi khởi tạo Dio/Can/Spi/Adc), và `Can` số 9 (khởi tạo cuối cùng khi ComStack sẵn sàng, tránh bắn frame rác/lỗi Bus Off lên mạng xe).
>       - **Minh định ranh giới kiến trúc (Architectural Scope Notice)**: Làm rõ MCAL là mã thực thi bị động (Passive Implementation), không thể tự chạy mà phải do `EcuM` (BSW Service Layer) làm nhạc trưởng điều phối; mở ngoặc ghi chú rạch ròi tầng kiến trúc cho từng thực thể (`[Tầng MCAL]`, `[BSW Service Layer: EcuM, Com, PduR, NvM]`, `[ECU Abstraction: CanIf, Fee]`, `[OS Kernel: StartOS]`) giúp người đọc không bị ngộ nhận.
>     * **Tái sắp xếp toàn bộ thứ tự 9 Module MCAL (Mục 9.2 đến 9.10) khớp 100% với chu kỳ boot**:
>       1. Module 1: `Mcu Driver` (`Mcu.h`) — Khối Clock Gen (PLL), Reset & Power Management
>       2. Module 2: `Wdg Driver` (`Wdg.h` & `WdgIf.h`) — Khối Hardware Watchdog Timers
>       3. Module 3: `Port Driver` (`Port.h`) — Khối Pin Multiplexer (PinMux) & I/O Pad Control
>       4. Module 4: `Dio Driver` (`Dio.h`) — Khối GPIO Data Registers
>       5. Module 5: `Gpt Driver` (`Gpt.h`) — Khối Hardware Timers & Prescalers
>       6. Module 6: `Fls Driver` (`Fls.h`) — Khối Flash Memory Controller & High-Voltage Charge Pump
>       7. Module 7: `Spi Driver` (`Spi.h`) — Khối SPI Controller, Shift Registers & FIFOs
>       8. Module 8: `Adc Driver` (`Adc.h`) — Khối ADC Core, Analog Mux & Sequencer / DMA
>       9. Module 9: `Can Driver` (`Can.h`) — Khối CAN Protocol Engine & Message RAM / Mailboxes
>     * **Đồng bộ Ma trận ánh xạ tổng thể 9.11** và **Mục lục chi tiết đầu file** theo đúng thứ tự khởi tạo 1 đến 9.
>   - **Bổ sung Mục 9.0 Cẩm Nang Đọc Hiểu, Cấu Trúc File Driver & 6 Nhóm Function Cốt Lõi**:
>     * Phân tích hệ sinh thái tập tin của một module MCAL: Static Code (`<Mod>.h`, `<Mod>.c`, `<Mod>_Types.h`, `<Mod>_Cbk.h`) vs Generated Code (`<Mod>_Cfg.h`, `<Mod>_Cfg.c` / `<Mod>_PBcfg.c`).
>     * Giải mã chuyên sâu Cơ chế Bao hàm Bắc cầu (Transitive Inclusion Rule): Bóc tách nguyên nhân vì sao file source C như `Port.c` không include trực tiếp `Port_Cfg.h` hay `Port_Types.h` mà được nạp gián tiếp qua trục bao hàm trung tâm `Port.h` tuân thủ nghiêm ngặt tiêu chuẩn `@req PORT131` và `@req PORT130`; Thiết lập 4 bằng chứng pháp y bất khả chối cãi (Type Dependency của `Port_ConfigType`, Preprocessor Macro của `PORT_DEV_ERROR_DETECT`, SCons Build Include Path `-I`, và Preprocessed Output `gcc -E`).
>     * Phân tích chuyên sâu Vì sao AUTOSAR Classic MCAL hoàn toàn không dùng Macro đăng ký driver động (như Linux `module_platform_driver` hay Zephyr `DEVICE_DEFINE`): Bóc tách 3 lý do sống còn của tiêu chuẩn an toàn ô tô ISO 26262 ASIL-D (100% Deterministic Power/Clock Sequencing, triệt tiêu rủi ro con trỏ hàm động trong RAM tránh nhiễu SEU, và cơ chế gọi tập trung tường minh qua `EcuM_AL_DriverInitZero` / `EcuM_AL_DriverInitOne`).
>     * Giải phẫu 8 phân vùng kinh điển bên trong file source code driver `<Mod>.c` (Header/Req, Includes, Version Check, Local Macros, Static State, Private Prototypes, Standard Public APIs, ISRs).
>     * Cung cấp Cẩm nang 4 bước đọc hiểu và trace code MCAL dành cho kỹ sư (Data-First ──► Hardware-Binding ──► Task-Driven Runtime ──► Event/Scheduled Flow).
>     * Chuẩn hóa 6 nhóm Function cốt lõi (API Archetypes): Khởi tạo/Vòng đời, Quản lý Chế độ/Trạng thái, Thao tác Dữ liệu Runtime, Lập lịch Polling MainFunction, Ngắt ISR/Callback, Cấu hình lại Runtime.
>   - **Chuẩn hóa các tiểu mục 9.1 đến 9.9 phân tích chức năng theo các Function quan trọng**:
>     * Từng module MCAL (`Port`, `Dio`, `Gpt`, `Adc`, `Spi`, `Can`, `Wdg`, `Mcu`, `Fls`) được tái cấu trúc nhất quán: Khối Silicon IP đại diện ──► Phân tích chi tiết chức năng bám sát theo các Function quan trọng của từng nhóm hàm ──► Minh chứng mã nguồn thực tế trong `Study_AUTOSAR` (`parai/as`).
>   - **Khắc phục lỗi đánh số thứ tự chương mục**: Chuyển đổi toàn bộ các tiểu mục con từ `8.1, 8.2...` thành `9.0, 9.1, 9.2, 9.3, 9.4, 9.5, 9.6, 9.7, 9.8, 9.9, 9.10` đảm bảo tính nhất quán, liền mạch khoa học.
>   - **Định danh chuẩn xác khối phần cứng đại diện (Silicon IP)** cho từng driver MCAL:
>     * **Port Driver (`Port.h`)** $\rightarrow$ Đại diện trực tiếp cho khối **Pin Multiplexer (PinMux) / I/O Pad Configuration Unit** (AFIO/AFR trên STM32, SIU/SIUL2 PCR/MSCR trên NXP MPC56xx/S32K, Port Logic Pn_IOCR trên Infineon AURIX). Phân tích chuyên sâu bản chất dồn kênh chuyển mạch tín hiệu ngoại vi và cô lập mạch đệm số (Digital Input Buffer Disconnect) khi dùng chân Analog ADC.
>     * **Dio Driver (`Dio.h`)** $\rightarrow$ Đại diện cho khối **GPIO Data Registers & Atomic Bit Manipulation** (`IDR`, `ODR`, `BSRR/BRR`, `GPDO/GPDI`). Phân định rạch ròi bản chất giữa Port (cấu hình multiplexer/hướng chân) và Dio (đọc/ghi điện thế logic số 0/1 mức cao, xử lý nguyên tử chống Race Condition).
>     * **Gpt Driver (`Gpt.h`)** $\rightarrow$ Đại diện cho khối **Hardware Timers / Counters & Clock Prescalers** (TIM2..5 trên STM32, PIT/FTM/eTimer trên NXP, STM/GTM trên AURIX).
>     * **Adc Driver (`Adc.h`)** $\rightarrow$ Đại diện cho khối **ADC Peripheral Core (SAR), Analog Multiplexer, Sample & Hold (S&H), Sequencer & DMA Engine**.
>     * **Spi Driver (`Spi.h`)** $\rightarrow$ Đại diện cho khối **Synchronous Serial Controller, Shift Registers & Hardware Tx/Rx FIFOs / DMA**.
>     * **Can Driver (`Can.h`)** $\rightarrow$ Đại diện cho khối **CAN Protocol Engine (MAC, Bit Timing Logic, Error Management) & Message RAM / Hardware Mailboxes**.
>     * **Wdg Driver (`Wdg.h` & `WdgIf.h`)** $\rightarrow$ Đại diện cho khối **Hardware Watchdog Timers (Independent Watchdog IWDG nuôi bằng thạch anh độc lập LSI, Window Watchdog WWDG, Safe Watchdog SWT)**.
>     * **Mcu Driver (`Mcu.h`)** $\rightarrow$ Đại diện cho khối **Clock Generation Module (CGM: Oscillators, Phase-Locked Loop PLL, Clock Prescalers), Reset Generation Module (RGM), & Power Management Controller (PMC/PMU)**.
>     * **Fls Driver (`Fls.h`)** $\rightarrow$ Đại diện cho khối **Embedded Flash Memory Controller (FMC / Flash Sequencer) & High-Voltage Charge Pump Unit**.
>   - **Bổ sung Ma trận ánh xạ tổng thể (Mapping Matrix)**: Đối chiếu 9 module MCAL với khối Silicon IP, tên gọi phần cứng và thanh ghi tiêu biểu trên STMicroelectronics (STM32), NXP (MPC56xx/S32K), và Infineon (AURIX TriCore).
>   - **Đối chiếu minh chứng mã nguồn thực tế trong `Study_AUTOSAR` (`parai/as`)**: Trích dẫn cụ thể file C và dòng code thực tế ([Port.c](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/com/as.infrastructure/arch/stm32f1/mcal/Port.c), [Port_Cfg.c](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/com/as.application/board.stm32f107vc/common/Port_Cfg.c), [Dio.c](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/com/as.infrastructure/arch/stm32f1/mcal/Dio.c), [Mcu.c](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/com/as.infrastructure/arch/stm32f1/mcal/Mcu.c), [Flash.c](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/com/as.infrastructure/arch/stm32f1/mcal/Flash.c), [Can.c](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/com/as.infrastructure/arch/stm32f1/mcal/Can.c)).

### 📝 Tệp Chỉnh Sửa Hôm Nay (Modified Today):
1. `docs/theory/01_AUTOSAR_Layered_Architecture_And_VFB_Masterclass.md` (Bổ sung Mục 3.0 giải phẫu phân biệt rạch ròi ECU vs MCU, bảng đối chiếu 8 tiêu chí kỹ thuật, cập nhật Glossary và Mục lục)
2. `docs/theory/05_Toolchain_ARXML_And_ECU_Integration.md` (Bổ sung Mục 3.5 phân tích toàn diện Nghịch lý Linker Script, bảng so sánh 7 tiêu chí AUTOSAR vs Bare-Metal vs Linux/Zephyr, phân tích 3 file .lds thực tế trong Study_AUTOSAR; bổ sung Câu hỏi phỏng vấn 61-62 và Bảng kiểm tra ECU Integration Checklist Mục 8)
3. `docs/theory/02_AUTOSAR_OS_And_MCAL_Deep_Dive.md` (Đại tu toàn diện Mục 9 MCAL Drivers theo đúng thứ tự khởi tạo chuẩn EcuM; tinh gọn phần Linker Script bằng Callout Note trỏ sang Chuyên đề 05 Mục 3.5)
4. `CHECKPOINT.md` (Cập nhật nhật ký theo dõi ngày 08/09/2026)
5. `docs/CHECKPOINT.md` (Đồng bộ nhật ký theo dõi ngày 08/09/2026)

---

## 📅 NGÀY 07/09/2026 — THAY ĐỔI SO VỚI NGÀY 03/09/2026

> 🎯 **Trọng tâm hôm nay:**  
> • Tinh chỉnh và làm sâu sắc thêm **Chuyên đề 02 (AUTOSAR OS & MCAL)**:  
>   - Bổ sung chi tiết luồng xử lý ngắt ISR Category 2 từ MCAL `Can_RxIsr` ──► `CanIf_RxIndication` ──► `scheduleRxIndication` ──► `CanIf_OsekNmUserRxIndication` ──► `NM_RxIndication` ──► `SetEvent(TASK_ID_TaskNmInd, EventNmNormal)`.
>   - Phân tích chi tiết cơ chế định tuyến PDU OSEK NM (`0x400`) qua `autosar.arxml`, bộ sinh mã `GenCanIf.py` và cấu hình tĩnh C89 trong `CanIf_Cfg.c`.
>   - Làm rõ chuỗi đánh thức và chuyển trạng thái từ WAITING sang READY của Extended Task `TaskNmInd` cùng cơ chế ngắt quyền Preemption khi thoát ISR trong `ExitISR()`.
>   - Chứng minh bản chất pháp y: Phân định ranh giới tuyệt đối giữa Cấu hình tĩnh Compile-Time (XML) và Mã nguồn C thực thi tại Runtime; bóc tách code sinh mã của `GenOS.py: L516-L534` và mảng C `tisr_pc[68]` trong `Os_Cfg.c: L602`; chuẩn hóa chỉ số ngắt Cortex-M IRQ 20 (Exception 36) gọi `tisr_pc[36 - 16]() = tisr_pc[20]()`; làm rõ nguyên nhân `board.lm3s6965evb` có `ISR_NUM = 0` và không sinh mảng `tisr_pc` do dùng CAN Polling qua `SCan.c`.
>   - **Chuẩn hóa Case Study 2 bám sát 100% mã nguồn C đã được sinh ra và biên dịch thực tế**:
>     1. **Bước 1**: Hardware CAN RX & Cortex-M Stacking (`{R0-R3, R12, LR, PC, xPSR}`).
>     2. **Bước 2**: Entry Vector Table (`startup.S: L87` - `knl_isr_process`).
>     3. **Bước 3**: Wrapper Assembly OS (`portableS.S: L126-L150 & L235-L240` - `EnterISR`, `mrs r0, ipsr`, `bl knl_isr_handler`).
>     4. **Bước 4**: OS C Dispatcher (`portable.c: L118-L130` - `knl_isr_handler(intno)` tính toán `intno - 16 = 20` gọi `tisr_pc[20]()`).
>     5. **Bước 5**: Bảng con trỏ hàm sinh mã thực tế (`Os_Cfg.c: L29 & L602` - `extern CAN1_RX0_IRQHandler`, `tisr_pc[20] = ISR_ADDR(CAN1_RX0_IRQHandler)` sinh ra từ `can1_isr.xml` do `board.stm32f107vc/SConscript` nạp `USB_CAN`).
>     6. **Bước 6**: ISR Handler trung gian (`stm32f1xx_it.c: L214-L223` - `CAN1_RX0_IRQHandler()` gọi `HAL_CAN_IRQHandler(&hcan1)`).
>     7. **Bước 7**: HAL CAN Handler (`stm32f1xx_hal_can.c: L1279-L1286` - `HAL_CAN_IRQHandler()` kiểm tra cờ FIFO0 và gọi `CAN_Receive_IT(hcan, CAN_FIFO0)`).
>     8. **Bước 8**: Đọc dữ liệu phần cứng Mailbox FIFO0 (`stm32f1xx_hal_can.c: L1565-L1680` - đọc `sFIFOMailBox[0]`, giải phóng FIFO và gọi `HAL_CAN_RxCpltCallback(hcan)`).
>     9. **Bước 9**: Application Gateway Callback (`usbd_cdc_if.c: L492-L546` - `HAL_CAN_RxCpltCallback()` đẩy gói tin nhận từ bus vật lý vào ringbuffer `canout` để truyền USB CDC lên PC).
>     10. **Bước 10**: Chuỗi Return Call Stack về lại Assembly Wrapper (`portableS.S: L240` - `b ExitISR`).
>     11. **Bước 11**: ExitISR Epilogue & Context Switch Preemption (`portableS.S: L173-L218` - phân tích điều kiện rẽ nhánh `bge l_nopreempt` trong mô hình Gateway do ngắt không gọi OS API, đối chiếu với `bl Sched_Preempt` khi có `SetEvent` trong kiến trúc MCAL nguyên bản).
>     12. **Bước 12**: Task được phục hồi hoặc cấp CPU tiếp tục thực thi qua `knl_start_dispatch`.
>   - **Phân định pháp y 2 kiến trúc tiếp nhận CAN trong codebase**:
>     * **Mô hình A (Bản build thực tế `board.stm32f107vc` - USB-CAN Gateway Dongle)**: Phân lập rạch ròi 2 hàng đợi: `canout` (Physical CAN RX ──► USB Transmit lên PC cho SavvyCAN) và `canin` (PC mô phỏng gửi qua USB Receive ──► `CDC_Receive_FS` ──► `SCan.c: Can_MainFunction_Read` ──► `CanIf_RxIndication` ──► `SetEvent`).
>     * **Mô hình B (AUTOSAR MCAL nguyên bản `arch/stm32f1/mcal/Can.c`)**: `Can_1_RxIsr()` gọi trực tiếp `Can_RxIsr()` ──► `CanIf_RxIndication()` ngay trong ISR Top-Half ──► `SetEvent()` kích hoạt cướp quyền tức thì tại `ExitISR()`.
>   - **Bổ sung Case Study 3 — Dòng chảy trọn vẹn từ Hardware (Tầng thấp nhất) đến Application (Tầng cao nhất: SWC & Extended Task)**:
>     * Khắc phục cảm giác đứt đoạn khi ngắt chỉ dừng lại ở ringbuffer Gateway `canout`.
>     * Thiết lập chuỗi bàn giao liên tục xuyên suốt 7 tầng kiến trúc: Tầng 0 (Chân vi điều khiển CAN_RX) ──► Tầng 1 (Mailbox FIFO0 & NVIC IRQ 20) ──► Tầng 2 (Vector Table & OS Wrapper `knl_isr_process`) ──► Tầng 3 (MCAL `Can_RxIsr`) ──► Tầng 4 (`CanIf_RxIndication` lọc phần mềm theo `CanIfRxPduConfigData`) ──► Tầng 5 (`PduR` & `Com` / `OsekNm`) ──► Tầng 6 (Application Layer: `Swc_Gauge.c` gọi `Com_ReceiveSignal(COM_SID_VehicleSpeed)` điều khiển kim táp-lô, và `OsekNm_Cfg.c: TaskNmInd` thoát `WaitEvent()` thực thi logic mạng).

### 📝 Tệp Chỉnh Sửa Hôm Nay (Modified Today):
1. `docs/theory/00_BUILD_ENVIRONMENT_SETUP.md` (Bổ sung Mục 1.1 Nguyên Tắc Vàng Pháp Y: Bắt buộc build full source các board nền tảng trước khi trace code; Nâng cấp toàn diện Mục 4 thành Hướng dẫn build chi tiết các board quan trọng: board=lm3s6965evb, board=stm32f107vc, board=posix; Cung cấp bảng tổng hợp sản phẩm sinh mã tĩnh và Quy trình pháp y 3 bước kiểm chứng file C/H/Map trước khi trace code)
2. `docs/theory/02_AUTOSAR_OS_And_MCAL_Deep_Dive.md` (Bổ sung cảnh báo đặc tả kiến trúc mục tiêu ngay đầu Case Study 2: xác nhận rõ đây là luồng USB-CAN Gateway giao tiếp giữa ECU với máy tính PC qua USB CDC; Hiệu đính chi tiết dòng code Os_Cfg.c: L602; Tinh gọn tài liệu bằng cách loại bỏ Case Study 3 bị trùng lặp, thay bằng liên kết tham chiếu chuẩn mực sang Chuyên đề 03 Mục 4.3 để giữ trọn vẹn trọng tâm chuyên đề về OS & MCAL)
3. `docs/theory/03_Communication_Stack_And_CAN_Protocol.md` (Bổ sung Mục 4.3 Case Study Chuyên Sâu: Chuỗi gọi hàm thực tế trong codebase cho luồng nhận tín hiệu chuẩn truyền thống từ Hardware Pin ──► MCAL Can_RxIsr ──► CanIf_RxIndication ──► PduR ──► Com_RxIndication ──► Com_RxProcessSignals ──► Swc_Gauge đọc tín hiệu VehicleSpeed hiển thị đồng hồ táp-lô; Phân tích song song luồng OSEK NM đánh thức TaskNmInd; Cung cấp bảng so sánh đối chiếu giữa 2 mô hình USB-CAN Gateway Dongle và MCAL Standalone ECU)
4. `CHECKPOINT.md` (Cập nhật nhật ký theo dõi ngày 07/09/2026)
5. `docs/CHECKPOINT.md` (Đồng bộ nhật ký theo dõi ngày 07/09/2026)

---

## 📅 NGÀY 03/09/2026 — THAY ĐỔI SO VỚI NGÀY 28/08/2026

> 🎯 **Trọng tâm hôm nay:**  
> • Bổ sung và tinh chỉnh chuyên sâu tài liệu chuyên khảo nâng cao trong phân vùng kiến thức bổ trợ (`docs/supplementary_knowledge/`):  
>   - Chuyên đề toàn diện 18 chương về **Interrupt Vector Table (IVT), NVIC & Hệ Điều Hành AUTOSAR OS (`askar`)**:
>     + Tinh chỉnh 100% tài liệu bám sát phục vụ mục tiêu học tập dự án `Study_AUTOSAR` (`as`), loại bỏ hoàn toàn các nội dung lan man ngoài lề (FreeRTOS, x86, RISC-V, STM32Cube HAL).
>     + Phân tích mã nguồn Assembly Startup thực tế (`startup.S`), Linker Script (`linker.lds`, `linker-app.lds`, `linker-boot.lds`), file ánh xạ (`lm3s6965evb.map`).
>     + Bóc tách chu trình xử lý ngắt 3 tầng trong `as`: `__vector_table` ──► Assembly Wrapper `portableS.S` (`knl_isr_process`, `EnterISR`, `ExitISR`) ──► C Dispatcher `portable.c` (`knl_isr_handler`, bảng con trỏ hàm phát sinh `tisr_pc[]`) ──► MCAL Driver (`Can_RxIsr`).
>     + Làm rõ tam giác vàng ngoại lệ AUTOSAR OS: SVCall (`knl_start_dispatch` #11), SysTick (`knl_system_tick` #15), PendSV (`knl_dispatch_entry` #14), và 4 cấp độ khóa ngắt OSEK/AUTOSAR.
>     + Kiến trúc Bootloader ô tô `asboot` và chuyển giao quyền sang Application `ascore` (9 bước nhảy chuẩn UDS ISO 14229 & VTOR relocation).
>     + So sánh kiến trúc ngắt các dòng vi điều khiển ô tô chuyên dụng: ARM Cortex-M (NVIC) vs Infineon AURIX TriCore (BIV, CSA, IR) vs Renesas RH850 (INTBP, INTC) vs Cortex-A (GIC, AUTOSAR Adaptive).
>     + Vòng đời khởi tạo 5 giai đoạn: Hardware Vector Table ──► `reset_handler` ──► `EcuM_Init` (MCAL `Mcu_Init`, `Port_Init`, `Can_Init`) ──► `StartOS` ──► `SchM_Startup`.
>     + Mẫu thiết kế BSW Top-Half/Bottom-Half (`Can_RxIsr` ──► `CanIf` ──► `SetEvent` ──► `Task_Communication` ──► `PduR` ──► `Com`) và hàng đợi vòng lock-free `cirq_buffer.c`.
>     + Bộ bài tập 10 cấp độ thực chiến trên QEMU `lm3s6965evb`, Senior Mindset và Master Debug Checklist cho kỹ sư AUTOSAR BSW Integration.

### 📄 Tệp & Thư Mục Tạo Mới Hôm Nay (Created Today):
1. `docs/supplementary_knowledge/` (Thư mục kiến thức bổ trợ kỹ nghệ nhúng nâng cao)
2. `docs/supplementary_knowledge/01_Interrupt_Vector_Table_Deep_Dive.md` (Chuyên đề chuyên sâu 18 chương về Interrupt Vector Table, NVIC & Hệ Điều Hành AUTOSAR OS)

### 📝 Tệp Chỉnh Sửa Hôm Nay (Modified Today):
1. `docs/supplementary_knowledge/01_Interrupt_Vector_Table_Deep_Dive.md` (Rà soát toàn diện và chuẩn hóa 18 chương phục vụ dự án Study_AUTOSAR; Bổ sung Mục 3.5 chuyên sâu về bản chất "Gán địa chỉ vào Vector Table" vs "Kích hoạt ngắt thủ công", giải phẫu mô hình 3 Tầng Cầu Dao Bảo Vệ phần cứng, phân loại chi tiết các Core Exception bắt buộc phải bật thủ công, và dẫn chứng 3 ví dụ thực tế vị trí gán vector vs vị trí kích hoạt trong repo as: SysTick, Core Faults SCB->SHCSR, và CAN Controller NVIC)
2. `docs/theory/04_Diagnostic_UDS_And_Memory_Stack.md` (Bổ sung Mục 6 chuyên sâu về Kiến trúc Bootloader ô tô asboot, Ứng dụng chính ascore, và Vùng Lưu Trữ Firmware Dự Phòng FOTA / Anti-Brick; Bổ sung Mục 6.0 cắt nghĩa bản chất nạp bàn thí nghiệm JTAG/SWD/QEMU vs xe thật UDS Bootloader và lý do bắt buộc phải sửa ORIGIN trong file linker.lds khi chạy standalone ascore; Phân tích mã nguồn thật pbl_core.c, bl_core.c, bl_sessec.c; Chu trình nạp Flash UDS 8 bước; Cơ chế A/B Dual-Bank Swapping và Safe State Rollback)
3. `docs/theory/02_AUTOSAR_OS_And_MCAL_Deep_Dive.md` (Tái cấu trúc sư phạm chuyên đề 02: Hoán đổi vị trí Mục 2 và Mục 3 để đẩy Chuỗi khởi động SchM_Startup và TaskIdle lên ngay sau Basic/Extended Task; Khôi phục tiêu đề Mục 4 PCP và làm sạch mục lục trùng lặp; Bổ sung phân tích chi tiết Bước 2 về ngắt phần cứng Timer: bóc tách chuỗi gọi hàm từ NVIC SysTick Entry [15] -> knl_system_tick -> knl_system_tick_handler -> SignalCounter(0); So sánh phân định bản chất Core Exception 15 vs External IRQs đi qua knl_isr_handler & bảng tisr_pc; Dẫn chứng địa chỉ thực tế từ file map và kiểm thử QEMU thực chiến)
4. `CHECKPOINT.md` (Cập nhật nhật ký theo dõi ngày 03/09/2026)
5. `docs/CHECKPOINT.md` (Cập nhật nhật ký theo dõi ngày 03/09/2026)

---

## 📅 NGÀY 28/08/2026

> 🎯 **Trọng tâm hôm nay:**  
> • Nâng cấp chuyên sâu **Chuyên đề 02 (AUTOSAR OS & MCAL)**:  
>   - Đưa định nghĩa và so sánh Basic Task vs Extended Task lên đầu tài liệu, kèm mã nguồn C gốc (`SchM_BswService` trong `SchM.c` & `TaskNmInd` trong `OsekNm_Cfg.c`).  
>   - Phân tích bản chất kỹ nghệ 4 Cấp Độ Tuân Thủ (**Conformance Classes: BCC1, BCC2, ECC1, ECC2**) qua mã nguồn C thật, cấu trúc dữ liệu (`TaskConstType`, `TaskVarType`, `pEventVar`, `activation`) và cờ tiền xử lý trong `Os_Cfg.h` / `kernel_internal.h` / `sched-bubble.c`.  
>   - Làm rõ sự khác biệt giữa Task Autostart (`SchM_Startup`), Task Idle (`TaskIdle`), Task chu kỳ Alarm (`SchM_BswService`) và vẽ chuỗi **Function-Call-Function Trace** khởi tạo Task khi ECU boot (`StartOS` ──► `Os_TaskInit` ──► `ActivateTask` ──► `Sched_GetReady` ──► `Os_PortStartFirstDispatch` ──► `TASK(SchM_Startup)`).

### 📄 Tệp Tạo Mới Hôm Nay (Created Today):
1. `docs/theory/02_conformance_classes_proof/00_CONFORMANCE_CLASSES_MASTER_PROOF.md` (Tệp tổng quan phương pháp luận chứng minh & cơ chế tính toán cấp độ của Toolchain GenOS.py)
2. `docs/theory/02_conformance_classes_proof/01_BCC1_Proof_And_Config.md` (Tệp chứng minh cấp độ BCC1: Cấu hình ARXML, Single Shared Stack, loại bỏ 100% event.c)
3. `docs/theory/02_conformance_classes_proof/02_BCC2_Proof_And_Config.md` (Tệp chứng minh cấp độ BCC2: Đa nhiệm trùng Priority, Hàng đợi activation, thuật toán FIFO Sequence trong sched-bubble.c)
4. `docs/theory/02_conformance_classes_proof/03_ECC1_Proof_And_Config.md` (Tệp chứng minh cấp độ ECC1: Đa nhiệm hướng sự kiện WaitEvent, Dedicated Stack)
5. `docs/theory/02_conformance_classes_proof/04_ECC2_Proof_And_Config.md` (Tệp chứng minh cấp độ ECC2: Cấu hình thực tế 6 Tasks dự án ascore)

### 📝 Tệp Chỉnh Sửa Hôm Nay (Modified Today):
1. `docs/theory/02_AUTOSAR_OS_And_MCAL_Deep_Dive.md` (Hiệu đính và xác thực 100% mã nguồn gốc cho Mục 1.3: Thay thế hàm giả định bằng chuỗi SignalCounter() trong counter.c và Alarm_BswService_Action() trong Os_Cfg.c; Mục 1.4: Đơn nhân vs Đa nhân & Preemptive nesting; Mục 1.5: So sánh AUTOSAR Task vs FreeRTOS Thread; Mục 2: 4 Conformance Classes mã C thật; Mục 3: Task Autostart SchM_Startup, Mục 3.3: Case Study thực chiến toàn diện cho TaskIdle từ infrastructure.xml, Os_Cfg.c, Os.c; Mục 5: Bổ sung Case Study Function-Call-Function chi tiết từ Hardware Trigger, Vector Table, OS Wrapper portableS.S, Can_RxIsr, SetEvent đến Preemption Dispatch cho ISR Category 1 và ISR Category 2)
2. `CHECKPOINT.md` (Cập nhật nhật ký theo dõi ngày 28/08/2026)
3. `docs/CHECKPOINT.md` (Cập nhật nhật ký theo dõi ngày 28/08/2026)

---

## 📅 NGÀY 27/08/2026 (HÔM QUA)

> 🎯 **Trọng tâm hôm nay:**  
> • Tách bạch và quy hoạch lại cấu trúc môn học: Chuyển toàn bộ bài toán **Trace Dòng Chảy CAN 6 Tầng Toàn Diện** từ Chuyên đề 01 sang đúng vị trí chuyên môn tại **Chuyên đề 03 (Task 3.1 & Solutions 02)**.  
> • Khởi tạo tệp theo dõi Checkpoint nhật ký theo ngày.

### 📄 Tệp Tạo Mới Hôm Nay (Created Today):
1. `CHECKPOINT.md` (Tệp nhật ký theo dõi thay đổi dự án ở thư mục gốc)
2. `docs/CHECKPOINT.md` (Tệp nhật ký theo dõi thay đổi dự án trong thư mục docs/)
3. `docs/hands_on_tasks/solutions/02_ComStack_CAN_Solutions.md` (File lời giải riêng biệt cho Chuyên Đề 03: ComStack & CAN 6 tầng)

### 📝 Tệp Chỉnh Sửa Hôm Nay (Modified Today):
1. `docs/hands_on_tasks/00_MASTER_PLAN_INDEX.md` (Cập nhật liên kết file lời giải Solutions 02 và phân bổ 7 tasks ComStack)
2. `docs/hands_on_tasks/01_Architecture_VFB_Tasks.md` (Đồng bộ chuẩn xác 5 tasks VFB nền tảng: Task 1.1 Boot, Task 1.2 Hooks/Callbacks, Task 1.3 Linker Script & Memory, Task 1.4 BSW Init Order, Task 1.5 RTE Ports)
3. `docs/hands_on_tasks/solutions/01_Architecture_VFB_Solutions.md` (Bổ sung giải thích bản chất vật lý & kiến trúc cho Task 1.4: vì sao Mcu_Init và Port_Init bắt buộc chạy trước Can_Init và Com_Init; trích xuất mã nguồn gốc MemMap.h và Det.c cho Task 1.3)
4. `docs/hands_on_tasks/03_ComStack_CAN_Tasks.md` (Bổ sung Task 3.1: Trace 6 tầng End-to-End ComStack gốc `TxMsgTime 0x101`, `OSEK_NM 0x401`, `RxMsgAbsInfo 0x102`)
5. `docs/theory/02_AUTOSAR_OS_And_MCAL_Deep_Dive.md` (Bổ sung Mục 0: Bức tranh toàn cảnh 100+ ECU và 1.500-3.000+ linh kiện ô tô, bảng chip phần cứng thực tế từ 512B RAM đến 32GB RAM; làm rõ bản chất 4 Conformance Classes; thay thế toàn bộ Pseudo-code/Task giả lập bằng mã nguồn gốc)
6. `docs/theory/05_Toolchain_ARXML_And_ECU_Integration.md` (Bổ sung Mục 3.4: Giải thích bản chất ARXML sinh ra cả RTE và mã cấu hình BSW *_Cfg.c, phân định BSW Static Core dùng chung vs BSW Generated Config, quy tắc vàng cấm sửa tay generated code)

---

## 📅 NGÀY 26/08/2026 (HÔM QUA)

> 🎯 **Trọng tâm hôm qua:**  
> • Bổ sung 2 Chuyên đề Lý thuyết & Bài tập mới về **LIN Protocol (Chuyên đề 11 & Task 07)** và **Automotive Ethernet/SOME/IP/DoIP (Chuyên đề 12 & Task 08)** dựa trên frame gốc trong `autosar.arxml`.  
> • Xác thực 100% dòng chảy BSW COM gốc cho `TxMsgTime (0x101)` và cơ chế chuyển tiếp SchM Alarm.  
> • Chuẩn hóa 2 file DBC tương thích hoàn toàn với SavvyCAN.  
> • Khôi phục mã nguồn `app.c` về nguyên bản sạch sẽ của tác giả.

### 📄 Tệp Tạo Mới Ngày 26/08/2026:
1. `docs/theory/11_LIN_Protocol_And_LinStack_Deep_Dive.md`
2. `docs/theory/12_Automotive_Ethernet_SOMEIP_DoIP_Deep_Dive.md`
3. `docs/hands_on_tasks/07_LIN_Stack_Tasks.md`
4. `docs/hands_on_tasks/08_Ethernet_SOMEIP_DoIP_Tasks.md`
5. `docs/hands_on_tasks/solutions/03_LIN_Ethernet_Solutions.md`
6. `docs/samples/CANIF_CHL_LS.dbc`

### 📝 Tệp Chỉnh Sửa Ngày 26/08/2026:
1. `docs/theory/00_AUTOSAR_READING_ROADMAP.md`
2. `docs/theory/10_CAN_DBC_Format_And_Tools.md`
3. `docs/hands_on_tasks/00_MASTER_PLAN_INDEX.md`
4. `docs/hands_on_tasks/solutions/01_Architecture_VFB_Solutions.md`
5. `docs/samples/Vehicle_Network.dbc`
6. `as/release/ascore/app/app.c`
7. `docs/hands_on_tasks/task_fix/02_fix_savvycan_slcan_streaming_integration/src_after/as/release/ascore/app/app.c`

---

## 📅 NGÀY 25/08/2026

> 🎯 **Trọng tâm:**  
> • Tích hợp Dual UART cho QEMU ARM Cortex-M3 (UART0: Log hệ thống, UART1: SLCAN phát frame CAN).  
> • Thiết lập môi trường mô phỏng SIL giữa QEMU và phần mềm SavvyCAN qua Virtual COM (COM1 $\leftrightarrow$ COM2).  
> • Xây dựng quy tắc `rule.md` và thư mục lưu trữ bản sửa lỗi `task_fix/` với đối chiếu `src_before` và `src_after`.

### 📂 Thư Mục Tạo Mới Ngày 25/08/2026:
* `docs/hands_on_tasks/task_fix/01_fix_qemu_board_lm3s6965evb_target/`
* `docs/hands_on_tasks/task_fix/02_fix_savvycan_slcan_streaming_integration/`
* `docs/hands_on_tasks/task_fix/03_enable_full_bsw_and_hook_logging/`

### 📄 Tệp Tạo Mới Ngày 25/08/2026:
1. `docs/hands_on_tasks/task_fix/01_fix_qemu_board_lm3s6965evb_target/README.md`
2. `docs/hands_on_tasks/task_fix/01_fix_qemu_board_lm3s6965evb_target/fix.diff`
3. `docs/hands_on_tasks/task_fix/02_fix_savvycan_slcan_streaming_integration/README.md`
4. `docs/hands_on_tasks/task_fix/02_fix_savvycan_slcan_streaming_integration/fix.diff`
5. `docs/hands_on_tasks/task_fix/03_enable_full_bsw_and_hook_logging/README.md`
6. `docs/hands_on_tasks/task_fix/03_enable_full_bsw_and_hook_logging/fix.diff`

### 📝 Tệp Chỉnh Sửa Ngày 25/08/2026:
1. `as/com/as.infrastructure/arch/common/mcal/SCan.c`
2. `as/com/as.infrastructure/arch/lm3s/mcal/Mcu.c`
3. `as/com/as.infrastructure/arch/lm3s/DriverLib/src/hibernate.c`
4. `as/com/as.infrastructure/arch/lm3s/SConscript`
5. `as/com/as.tool/config.infrastructure.system/building.py`
6. `docs/hands_on_tasks/01_Architecture_VFB_Tasks.md`
7. `docs/hands_on_tasks/solutions/01_Architecture_VFB_Solutions.md`
8. `docs/theory/00_BUILD_ENVIRONMENT_SETUP.md`
9. `docs/theory/01_AUTOSAR_Layered_Architecture_And_VFB_Masterclass.md`

---

## 📅 NGÀY 24/08/2026

> 🎯 **Trọng tâm:**  
> • Khởi tạo toàn bộ bộ khung 10 chuyên đề lý thuyết AUTOSAR Masterclass.  
> • Tạo 6 tệp Kế hoạch bài tập thực hành (`01_Architecture_VFB_Tasks.md` $
ightarrow$ `06_RealWorld_BMS_VCU_Tasks.md`).  
> • Thiết lập các thư mục tài liệu `docs/deep_dive/`, `docs/career/`, `docs/reference/`, `docs/samples/`, `docs/theory/`.  
> • Viết file `task_fix/rule.md` quy định kỷ luật phát triển và bảo tồn mã nguồn.

### 📄 Tệp Tạo Mới Tiêu Biểu Ngày 24/08/2026:
* 10 tệp lý thuyết `docs/theory/00` $
ightarrow$ `docs/theory/10`
* 6 tệp bài tập thực hành `docs/hands_on_tasks/01` $
ightarrow$ `docs/hands_on_tasks/06`
* `docs/hands_on_tasks/00_MASTER_PLAN_INDEX.md`
* `docs/hands_on_tasks/task_fix/rule.md`
* `docs/samples/Vehicle_Network.dbc`
* `docs/samples/ARXML_EXPLAINED.md`
* `docs/reference/python_can_scripts/` (01 $
ightarrow$ 06 scripts)

---

## 📅 NGÀY 21/08/2026 (INITIAL SETUP)
* Khởi tạo dự án ban đầu với các bảng checklist Excel và cấu hình VSCode.
