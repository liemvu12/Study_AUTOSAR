# 📍 CHECKPOINT REGISTRY — DAILY CHANGE LOG
## Nhật Ký Theo Dõi Thay Đổi Theo Ngày (Daily Project Change Tracker)

> 📌 **Mục đích:** Ghi nhận danh sách tất cả các tệp (files) và thư mục (folders) được tạo mới hoặc chỉnh sửa theo từng ngày cụ thể.
> ⚠️ **Quy tắc bắt buộc (Mandatory Rule):** Mỗi khi thực hiện bất kỳ thay đổi nào trong ngày, **BẮT BUỘC phải cập nhật danh sách vào file `CHECKPOINT.md` này trước khi commit và push lên GitLab**.

---

## 📅 NGÀY 03/09/2026 (HÔM NAY) — THAY ĐỔI SO VỚI NGÀY 28/08/2026

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
3. docs/supplementary_knowledge/02_CPU_Registers_And_Instruction_Execution.md (Chuyên đề toàn diện 24 chương về CPU, Register Model, Instruction Execution, Stack Frame, Debugging và RTOS/AUTOSAR Context Switching)

### 📝 Tệp Chỉnh Sửa Hôm Nay (Modified Today):
1. `docs/supplementary_knowledge/01_Interrupt_Vector_Table_Deep_Dive.md` (Rà soát toàn diện và chuẩn hóa 18 chương phục vụ dự án Study_AUTOSAR; Bổ sung Mục 3.5 chuyên sâu về bản chất "Gán địa chỉ vào Vector Table" vs "Kích hoạt ngắt thủ công", giải phẫu mô hình 3 Tầng Cầu Dao Bảo Vệ phần cứng, phân loại chi tiết các Core Exception bắt buộc phải bật thủ công, và dẫn chứng 3 ví dụ thực tế vị trí gán vector vs vị trí kích hoạt trong repo as: SysTick, Core Faults SCB->SHCSR, và CAN Controller NVIC)
2. `docs/theory/04_Diagnostic_UDS_And_Memory_Stack.md` (Bổ sung Mục 6 chuyên sâu về Kiến trúc Bootloader ô tô asboot, Ứng dụng chính ascore, và Vùng Lưu Trữ Firmware Dự Phòng FOTA / Anti-Brick; Bổ sung Mục 6.0 cắt nghĩa bản chất nạp bàn thí nghiệm JTAG/SWD/QEMU vs xe thật UDS Bootloader và lý do bắt buộc phải sửa ORIGIN trong file linker.lds khi chạy standalone ascore; Phân tích mã nguồn thật pbl_core.c, bl_core.c, bl_sessec.c; Chu trình nạp Flash UDS 8 bước; Cơ chế A/B Dual-Bank Swapping và Safe State Rollback)
3. `docs/theory/02_AUTOSAR_OS_And_MCAL_Deep_Dive.md` (Tái cấu trúc sư phạm chuyên đề 02: Hoán đổi vị trí Mục 2 và Mục 3 để đẩy Chuỗi khởi động SchM_Startup và TaskIdle lên ngay sau Basic/Extended Task; Khôi phục tiêu đề Mục 4 PCP và làm sạch mục lục trùng lặp; Bổ sung phân tích chi tiết Bước 2 về ngắt phần cứng Timer: bóc tách chuỗi gọi hàm từ NVIC SysTick Entry [15] -> knl_system_tick -> knl_system_tick_handler -> SignalCounter(0); So sánh phân định bản chất Core Exception 15 vs External IRQs đi qua knl_isr_handler & bảng tisr_pc; Chuẩn hóa Mục 5 Case Study 1 về luồng ngắt ISR Category 1 với 100% mã nguồn thực tế trong repo as: ngắt bảo vệ phần cứng khẩn cấp PWM Fault qua PWMFaultIntRegister / IntRegister của DriverLib LM3S và ngắt ngoại lệ Core Exception hard_fault_handler trong startup.S / portable.c)
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
