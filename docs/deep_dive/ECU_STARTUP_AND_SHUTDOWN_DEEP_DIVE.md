# ECU STARTUP & SHUTDOWN DEEP DIVE
**Tác giả:** Principal BSW Integration Engineer
**Kinh nghiệm:** 15 năm trong lĩnh vực AUTOSAR & Automotive Software

Tài liệu này cung cấp một cái nhìn sâu sắc, toàn diện và ở mức chuyên gia về quá trình khởi động (Startup) và tắt (Shutdown) của một Electronic Control Unit (ECU) theo tiêu chuẩn AUTOSAR. 

---

## 1. Complete Startup Sequence (Chuỗi khởi động hoàn chỉnh)

Dưới đây là bức tranh toàn cảnh về quá trình khởi động của một ECU, từ lúc có điện cho đến khi Application Software (ASW) bắt đầu chạy các Runnables.

`	ext
POWER ON
  |
  ▼
[Hardware Reset]
  - Startup code (crt0.s / startup.s)
  - Copy .data section từ Flash → RAM
  - Zero-fill .bss section
  - Stack pointer initialization
  |
  ▼
main() — Application entry point
  |
  ▼
EcuM_Init()  ← Phase 1: Pre-OS Init
  ├── EcuM_AL_DriverInitZero()   ← Init không cần config (Mcu, Wdg)
  │     ├── Mcu_Init(&Mcu_Config)
  │     └── Wdg_Init(&Wdg_Config)
  ├── EcuM_AL_DriverInitOne()    ← Init cần clock (Port, Dio, Can)
  │     ├── Port_Init(&Port_Config)
  │     ├── Dio_Init()
  │     └── Can_Init(&Can_Config)
  └── NvM_ReadAll()              ← Start async NvM read
  |
  ▼
StartOS(OSDEFAULTAPPMODE)  ← Chuyển sang OS control
  |
  ▼
[OS Running]
  |
  ▼
EcuM_StartupTwo()  ← Phase 2: Post-OS Init (trong Task)
  ├── NvM_GetErrorStatus()  ← Chờ NvM_ReadAll complete
  ├── CanIf_Init()
  ├── CanTp_Init()
  ├── PduR_Init()
  ├── Com_Init()
  ├── Dcm_Init()
  ├── Dem_Init()
  └── BswM_RequestMode(ECUM_STATE_RUN)
  |
  ▼
BswM_MainFunction()  ← Evaluate mode rules
  └── ActionList: Com_IpduGroupStart() — Enable CAN Tx
  |
  ▼
Rte_Start()  ← Activate all Runnables
  |
  ▼
[APPLICATION RUNNING]
  Runnables execute periodically via SchM
`

---

## 2. Phase Analysis chi tiết

### Phase 0 — Reset & Startup Code (trước main())
Đây là giai đoạn thuần túy phụ thuộc vào kiến trúc vi điều khiển (MCU) và Compiler, xảy ra ngay sau khi MCU thoát khỏi trạng thái Reset.

- **Startup code (C runtime init):** File hợp ngữ Startup ([`as/com/as.infrastructure/system/kernel/askar/portable/cortex-m/startup.S: L319-L352`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/com/as.infrastructure/system/kernel/askar/portable/cortex-m/startup.S#L319-L352)) chịu trách nhiệm chuẩn bị toàn bộ phần cứng và vùng nhớ trước khi hàm C đầu tiên được phép chạy.
- **Interrupt vector table:** Thiết lập Vector Table Base Register (VTOR) trỏ đến bảng vector ngắt trong Flash.
- **Stack setup:** Gán địa chỉ đỉnh của vùng RAM (`knl_system_stack_top`) cho Stack Pointer (SP) để các hàm C có thể gọi lẫn nhau.
- **Initialization of Data:** Copy vùng nhớ có khởi tạo (khai báo biến toàn cục/static có gán giá trị khác 0) từ Flash (`__etext`) sang RAM (`__data_start__` đến `__data_end__`).
- **Zero-fill .bss:** Xóa (ghi 0) toàn bộ các biến toàn cục không khởi tạo hoặc gán bằng 0 (`__bss_start__` đến `__bss_end__`).
- **Tại sao không được có global variable với constructor trước EcuM?** Trong C++, các static/global objects sẽ tự động gọi constructor trước khi vào main(). Trong Automotive, điều này rất nguy hiểm vì lúc này MCU clock chưa ổn định, watchdog chưa được cấu hình, có thể gây reset liên tục. Do đó, mã nguồn BSW chuẩn AUTOSAR phải dùng thuần C hoặc C++ không có global constructors.

#### 🔍 Giải Phẫu Chi Tiết: Vùng Nhớ Nào Chạy Trên RAM, Vùng Nào Trên ROM & Lý Do Bản Chất

Trong vi điều khiển ô tô, bộ nhớ được chia thành các phân đoạn (Sections) vật lý theo chỉ đạo của Linker Script ([`as/com/as.application/board.stm32f107vc/script/linker-common.lds: L8-L69`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/com/as.application/board.stm32f107vc/script/linker-common.lds#L8-L69)):

| Phân Vùng (Section) | Nơi Lưu Trữ Khi Tắt Điện (LMA) | Nơi Chạy / Truy Xuất Khi Hoạt Động (VMA) | Dữ Liệu Chứa Bên Trong & Ví Dụ Trong Codebase | Lý Do Kỹ Thuật Bản Chất |
| :--- | :---: | :---: | :--- | :--- |
| **`.text`** (Code) | **FLASH ROM** | **FLASH ROM** (XIP) | Toàn bộ mã máy nhị phân thực thi của các hàm C (`main`, `Can_Init`, `Swc_Gauge_Step`), bảng vector ngắt (`.isr_vector`). | 1. **Bất biến (Non-volatile):** Mã lệnh không bị mất khi xe tắt máy.<br>2. **Dung lượng lớn:** Flash ROM rộng (vài trăm KB đến nhiều MB) chứa đủ code BSW phức tạp.<br>3. **Bảo vệ mã lệnh (Hardware Write-Protection):** Flash bị khóa ghi ở runtime, tránh con trỏ hoang (wild pointer) phá hủy code.<br>4. **XIP (eXecute-In-Place):** CPU Cortex-M fetch lệnh trực tiếp từ Flash qua bus I-Code, khởi động tức thì trong vài micro-second. |
| **`.rodata`** (Constants) | **FLASH ROM** | **FLASH ROM** | Hằng số `const`, chuỗi ký tự, các struct cấu hình sinh từ ARXML ([`CanIf_Config`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/build/nt/stm32f107vc/ascore/config/CanIf_Cfg.c#L509), [`ComConfiguration`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/build/nt/stm32f107vc/ascore/config/Com_PbCfg.c#L517)). | 1. **Dữ liệu chỉ đọc:** Không bao giờ thay đổi trong suốt vòng đời xe.<br>2. **Tiết kiệm RAM:** Các bảng cấu hình ARXML rất lớn (hàng chục KB), nếu copy vào RAM sẽ làm cạn kiệt RAM ngay lập tức. |
| **`.data`** (Initialized Variables) | **FLASH ROM** (`AT(__etext)`) | **RAM** (`0x20000000`) | Biến toàn cục / static **có khởi tạo giá trị ban đầu khác 0** (ví dụ: `Can_Global.initRun = CAN_UNINIT;`, timer ban đầu). | 1. **Lưu trữ gốc ở Flash:** Để khi tắt điện không mất giá trị khởi động.<br>2. **Thực thi ở RAM:** Khi xe chạy, giá trị các biến này thay đổi hàng triệu lần $\rightarrow$ Bắt buộc phải nằm ở RAM để đọc/ghi chu kỳ đơn (Single-cycle access).<br>3. `Reset_Handler` copy từ Flash sang RAM trước khi gọi `main()`. |
| **`.bss`** (Zero-init Variables) | **Không chiếm Flash** | **RAM** | Biến toàn cục / static **không khởi tạo hoặc khởi tạo = 0** (ví dụ: bộ đệm I-PDU [`TxMsgBmsStatus_IPduBuffer[8]`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/build/nt/stm32f107vc/ascore/config/Com_PbCfg.c#L139), mảng RingBuffer [`rbBuf_canifRx`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/com/as.infrastructure/communication/CanIf/CanIf.c#L142)). | 1. **Tiết kiệm dung lượng Flash:** Không cần lưu hàng nghìn byte `0x00` vào file Hex.<br>2. **Biến runtime động:** Chứa toàn bộ dữ liệu thay đổi khi xe lăn bánh $\rightarrow$ Nằm ở RAM.<br>3. `Reset_Handler` quét sạch (zero-fill) vùng này về 0 khi boot. |
| **`.stack`** (Ngăn Xếp) | **Không chiếm Flash** | **RAM** | Biến cục bộ trong hàm, địa chỉ quay về (`LR`), ngữ cảnh thanh ghi khi xảy ra ngắt ISR (`R0-R3, R12, LR, PC, xPSR`). | 1. **Tốc độ đẩy/rút (Push/Pop) cực nhanh** theo từng chu kỳ xung nhịp CPU.<br>2. Kích thước biến động liên tục theo độ sâu lời gọi hàm $\rightarrow$ 100% nằm ở RAM. |
| **`.ramcode`** *(Ngoại lệ đặc biệt)* | **FLASH ROM** | **RAM** | Các hàm Flash Driver xóa/ghi Flash (`Fls_Write`, `Fls_Erase`) hoặc hàm nạp Firmware của Bootloader. | **Nguy cơ Read-While-Write (RWW) Hazard:** Phần cứng vi điều khiển KHÔNG THỂ vừa nạp mã lệnh từ Flash vừa thực thi xóa/ghi trên chính chip Flash đó. Bắt buộc phải copy mã máy của hàm lên RAM để CPU chạy trên RAM khi thao tác với Flash! |
| **`.noinit`** *(Ngoại lệ đặc biệt)* | **Không chiếm Flash** | **RAM** | Vùng nhớ RAM đặc biệt lưu cờ nhảy Bootloader (`FBL_REPROGRAMMING_FLAG`), Crash Dump khi xe gặp tai nạn hoặc mã lỗi Reset. | Startup `Reset_Handler` **bỏ qua không xóa về 0** khi Reset ấm (Warm Reset), giúp phần mềm giữ nguyên dấu vết lỗi sau cú crash hoặc nhảy từ App sang Bootloader. |

> 📚 **Đọc thêm chuyên sâu:** Để xem giải phẫu chi tiết kỹ thuật đọc file bản đồ bộ nhớ `.map`, kỹ thuật Struct Packing Audit và cách khắc phục lỗi tràn RAM (`region 'RAM' overflowed`), vui lòng đọc thêm tại tài liệu chuyên khảo: [`docs/supplementary_knowledge/03_Linker_Script_And_Memory_Mapping_Masterclass.md`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/docs/supplementary_knowledge/03_Linker_Script_And_Memory_Mapping_Masterclass.md#L96-L144).

### Phase 1 — EcuM Pre-OS (EcuM_Init)
EcuM_Init chạy trong ngữ cảnh của hàm main(), trước khi OS được khởi động. Interrupt lúc này vẫn đang bị disable.

- **Tại sao PHẢI init Mcu trước mọi thứ khác?** Module MCU (Microcontroller Unit) chịu trách nhiệm cấu hình hệ thống Clock (PLL) và Power. Nếu không có Clock ổn định, các thiết bị ngoại vi (Port, CAN, SPI) không thể hoạt động.
- **Clock tree setup:** Khởi tạo từ thạch anh ngoài (external crystal), nhân tần số qua PLL (Phase-Locked Loop), sau đó chia tần số qua các prescaler để cung cấp PCLK cho bus ngoại vi.
- **Cấu hình Flash Wait States & Prefetch Buffer trong Mcu_Init:** Khi PLL nhân xung nhịp lên 72MHz (hoặc 300MHz trên Infineon AURIX), tốc độ truy xuất Flash ROM (~30ns) không theo kịp xung CPU. Trước khi chuyển clock sang PLL, hàm MCAL `Mcu_Init` bắt buộc phải tăng độ trễ Flash lên 2 Wait States (`FLASH_ACR_LATENCY_2`) và bật Prefetch Buffer (`FLASH_ACR_PRFTBE`) ([`as/com/as.infrastructure/arch/stm32f1/mcal/Mcu.c: L137-L143`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/com/as.infrastructure/arch/stm32f1/mcal/Mcu.c#L137-L143)) để CPU không bị nghẽn bus hoặc sập HardFault (Xem giải thích chi tiết tại [01_AUTOSAR_Layered_Architecture_And_VFB_Masterclass.md: Mục 3.1.1-B.4](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/docs/theory/01_AUTOSAR_Layered_Architecture_And_VFB_Masterclass.md#311-chuyên-đề-sâu-giải-phẫu-bộ-nhớ-vi-điều-khiển-ô-tô--bảng-phân-bổ-ramrom-quy-luật-bán-dẫn--khởi-động--100ms)).
- **Tại sao Port phải init sau Mcu?** Port cấu hình các chân I/O (alternate functions). Các thanh ghi của Port cần Clock (do MCU cấp) mới có thể ghi được.
- **Wdg init: Tại sao Watchdog phải là module đầu tiên?** Theo tiêu chuẩn an toàn ISO 26262, Watchdog phải được bật càng sớm càng tốt để phát hiện lỗi treo hệ thống ngay từ những dòng code khởi tạo đầu tiên.
- **NvM_ReadAll() async pattern:** Việc đọc toàn bộ dữ liệu từ EEPROM/Data Flash tốn hàng chục đến hàng trăm mili-giây. Thay vì block CPU, NvM_ReadAll() chỉ khởi tạo các Job trong hàng đợi. Việc đọc thực tế sẽ được xử lý bởi các Task của OS sau này, giúp tối ưu hóa thời gian khởi động (parallel init).

### Phase 2 — OS Init (StartOS)
Giai đoạn chuyển giao quyền điều khiển từ main() sang RTOS (Real-Time Operating System).

- **OS kernel setup:** Khởi tạo các cấu trúc dữ liệu của OS (Task control blocks, Alarms, Counters, Resources).
- **Task creation:** Tạo các Task dựa trên cấu hình OIL (OSEK Implementation Language) / ARXML.
- **Idle task:** Một background task có độ ưu tiên thấp nhất luôn chạy khi không có task nào khác cần CPU, thường dùng để tiết kiệm năng lượng (WFI - Wait For Interrupt) hoặc tính toán CPU Load.
- **AUTOSAR hook - StartupHook():** Hàm hook này được gọi *sau* khi OS đã init xong cơ bản nhưng *trước* khi bất kỳ Task nào được kích hoạt. Thường dùng để khởi động các timer OS, activate các base task ban đầu của BSW.

### Phase 3 — EcuM Post-OS (EcuM_StartupTwo)
Chạy bên trong ngữ cảnh của một OS Task (thường là một BSW init task có độ ưu tiên cao). Lúc này OS tick và ngắt đã hoạt động.

- **Tại sao phần này chạy trong task chứ không phải trước StartOS?** Hầu hết các module Communication stack (CAN, SPI) và Memory stack cần interrupt và OS features (như delay, mutex, resource) để hoạt động bình thường, do đó phải chạy sau khi OS đã start.
- **NvM_GetErrorStatus() blocking wait pattern:** Task khởi tạo sẽ có một vòng lặp gọi NvM_MainFunction và kiểm tra trạng thái của block NvM_ReadAll. Nó sẽ chờ (block) cho đến khi toàn bộ NVRAM data được nạp vào RAM.
- **Init order: CanIf → CanTp → PduR → Com:** Các module lower layer phải được init trước các upper layer. CanIf (Interface) giao tiếp với driver Can. CanTp (Transport) cần CanIf. PduR (Router) định tuyến gói tin từ CanIf/CanTp lên Com (Communication). Nếu init sai thứ tự sẽ dẫn tới hard fault hoặc NULL pointer.
- **Tại sao Dem phải init sau Com?** DEM (Diagnostic Event Manager) thường cần truyền các bản tin lỗi qua mạng (DTC events) thông qua COM. Ngoài ra, DEM cần kết quả khởi tạo từ NvM (để nạp historic DTCs) nên nó phải init khá trễ.

### Phase 4 — BswM Mode Switch
BswM (Basic Software Mode Manager) đóng vai trò là "bộ não" điều phối trạng thái của hệ thống sau khi các module đã init xong.

- **BswM là state machine của BSW:** Nó đánh giá các luật (Rules) dựa trên đầu vào (Mode Request) và kích hoạt các hành động (ActionLists).
- **Mode Request từ EcuM:** Sau khi EcuM_StartupTwo hoàn thành, nó gửi một request tới BswM báo rằng nó đã vào trạng thái ECUM_STATE_RUN.
- **Ví dụ Rule:** 
  IF NvM_ReadAll.Complete AND EcuM.State == RUN THEN execute ActionList_ComStart
  Trong ActionList_ComStart sẽ gọi hàm Com_IpduGroupStart() để cho phép CAN gửi/nhận tín hiệu.

### Phase 5 — Rte_Start
Bắt đầu vòng đời của tầng Application (ASW).

- **Generated code từ ARXML:** RTE (Runtime Environment) là code được sinh tự động dựa trên software components (SWC) architecture.
- **Activate TriggerPoints:** RTE sẽ kết nối các cổng (ports) giữa các SWC, khởi tạo các biến nội bộ.
- **SchM schedule:** Scheduler Manager sẽ bắt đầu gọi các Runnables (hàm chức năng của ASW) dựa trên các Timer events (ví dụ: Task 10ms, Task 50ms). Hệ thống chính thức bước vào trạng thái vận hành bình thường (NORMAL OPERATION).

### Phase 6 — Giải Phẫu Bên Trong Thân Hàm `_Init()`: 4 Nhiệm Vụ Sống Còn Của Mọi Module BSW

Một câu hỏi kỹ nghệ bản lề là: *"Khi `EcuM_AL_DriverInitZero/One` hoặc `EcuM_StartupTwo` gọi hàng loạt hàm `Mcu_Init(&Mcu_Config)`, `Can_Init(&Can_Config)`, `CanIf_Init(&CanIf_Config)`, `PduR_Init(&PduR_Config)`, `Com_Init(&Com_Config)`, thì bản chất bên trong thân các hàm này thực sự làm những gì?"*

Toàn bộ các hàm khởi tạo trong thế giới AUTOSAR Classic đều tuân thủ nguyên tắc **Tách biệt tuyệt đối giữa Thuật toán thực thi (Generic Logic) và Dữ liệu cấu hình (Configuration Data)**. Chúng thực thi 4 nhiệm vụ sống còn:

```text
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                   MÔ HÌNH 4 BƯỚC KHỞI TẠO BẮT BUỘC TRONG MỌI HÀM _INIT() CỦA AUTOSAR             │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘

   [ BẢNG CẤU HÌNH TỪ ARXML ]                 [ HÀM KHỞI TẠO BSW ]               [ TÁC ĐỘNG VÙNG NHỚ RAM ]
  (Nằm trong Flash / ROM tĩnh)                (Chạy 1 lần khi Boot)                 (Biến nội bộ BSW)

  1. Bảng Pointer/Data Cfg        ──► Module_Init(ConfigPtr)      ──► Gán: Module_ConfigPtr = ConfigPtr; (Anchor)
  2. Cấp phát mảng tĩnh RAM       ──► Binding Buffer              ──► Gán: RuntimePtr = RAM_Buffer; (Binding)
  3. Tham số chu kỳ / Default     ──► Set Initial Values          ──► Gán: Timer = Period; Data = InitVal;
  4. Máy trạng thái Module        ──► FSM Transition              ──► Gán: Module_State = INITIALIZED;
```

#### 1. Neo con trỏ cấu hình (Pointer Anchoring):
* **Bản chất:** Bảng dữ liệu cấu hình sinh ra từ ARXML (như `CanIf_Config`, `PduR_Config`, `ComConfiguration`) được đặt tại vùng nhớ Flash ROM (`const`).
* **Hành vi:** Hàm `_Init` lưu địa chỉ con trỏ `ConfigPtr` vào biến nội bộ `static`:
  - `Can.c: L403-L413`: `Can_Global.config = config;` và `Can_Global.initRun = CAN_READY;`
  - `CanIf.c: L480`: `CanIf_ConfigPtr = ConfigPtr;`
  - `PduR.c: L66`: `PduRConfig = ConfigPtr;`
  - `Com.c: L236`: `ComConfig = config;`
* **Mục đích:** Hàng triệu chu kỳ thực thi runtime sau đó (`Com_SendSignal`, `CanIf_Transmit`, `PduR_CanIfRxIndication`) không cần truyền lại tham số cấu hình mà truy xuất trực tiếp $O(1)$ qua con trỏ đã neo.

#### 2. Liên kết Bộ đệm RAM (RAM Buffer Binding):
* **Bản chất:** File cấu hình sinh ra từ ARXML là `const` (chỉ đọc, nằm ở Flash ROM). Để hệ thống nhận/phát và xử lý dữ liệu động, mỗi tầng BSW bắt buộc phải sở hữu các vùng đệm RAM đọc/ghi riêng biệt. Hàm `_Init` thực hiện liên kết (binding) các đối tượng quản lý runtime với các mảng RAM tĩnh này:
  - **MCAL CAN ([Can.c: L423-L464](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/com/as.infrastructure/arch/stm32f1/mcal/Can.c#L423-L464)):** Liên kết con trỏ `canUnit = GET_PRIVATE_DATA(ctlrId)` vào mảng RAM `CanUnit[ctlrId]` và xây dựng bảng tra cứu phần cứng trong RAM `Can_Global.CanHTHMap[hoh->CanObjectId]`.
  - **CanIf ([CanIf.c: L496-L498](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/com/as.infrastructure/communication/CanIf/CanIf.c#L496-L498)):** Khởi tạo các bộ đệm vòng FIFO trong RAM `RB_INIT(canifRx)`, `RB_INIT(canifTx)`, `RB_INIT(canifTxInd)` và cấu trúc kênh `CanIf_Global.channelData[]`.
  - **CanTp ([CanTp.c: L1107-L1120](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/com/as.infrastructure/communication/CanTp/CanTp.c#L1107-L1120)):** Gắn cấu hình N-SDU vào mảng RAM runtime `runtimeData = &CanTpRunTimeData.runtimeDataList[...]` chứa bộ đệm tạm thời `canFrameBuffer` và con trỏ `pdurBuffer`.
  - **PduR ([PduR.c: L90-L130](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/com/as.infrastructure/communication/PduR/PduR.c#L90-L130)):** Quản lý bộ đệm hàng đợi FIFO `PduRTxBuffer_type` (cho Gateway/Buffered routing) hoặc bypass hoàn toàn ở chế độ Direct Zero-Cost (`TxBufferRef = NULL`).
  - **COM ([Com.c: L274](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/com/as.infrastructure/communication/Com/Com.c#L274)):** Liên kết `IPdu->ComIPduDataPtr` với mảng RAM tĩnh `TxMsgBmsStatus_IPduBuffer[8]` ([Com_PbCfg.c: L139](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/build/nt/stm32f107vc/ascore/config/Com_PbCfg.c#L139)) và nạp dữ liệu mặc định.
  - **OS System:** Khởi tạo Task Control Block và liên kết con trỏ hàng đợi ưu tiên vào các mảng RAM tĩnh `ReadyFIFO_prio*` và Stack RAM riêng biệt `Task_Stack_*`.

#### 3. Thiết lập giá trị ban đầu (Initial Values & Hardware Registers):
* **Hành vi:**
  - Với MCAL (`Can_Init`): Nạp trực tiếp các tham số Baudrate (BRP, TS1, TS2) và bộ lọc vào thanh ghi phần cứng (`CAN_BTR`, `CAN_FMR`).
  - Với BSW (`Com_Init`): Đọc trường `InitialValue` trong ARXML để nạp giá trị mặc định cho toàn bộ Signals trước khi xe lăn bánh, thiết lập các bộ đếm thời gian chu kỳ (`ComTxModeTimePeriodTimer`).

#### 4. Kích hoạt Máy trạng thái (FSM State Transition & DET Validation):
* **Hành vi:** Đổi cờ trạng thái module từ `UNINIT` sang `INITIALIZED` (hoặc `ONLINE` / `STOPPED`).
* **Mục đích:** Toàn bộ các API runtime của AUTOSAR đều có macro kiểm tra hợp lệ của Development Error Tracer (DET), ví dụ: `VALIDATE_NO_RV(CanIf_Global.initRun, CANIF_RXINDICATION_ID, CANIF_E_UNINIT)`. Nếu bước 4 không hoàn tất, toàn bộ các lời gọi truyền nhận sau đó sẽ bị DET chặn đứng và loại bỏ (Drop) ngay lập tức!

---

## 3. Shutdown Sequence

Quá trình Shutdown quan trọng không kém Startup, đảm bảo an toàn dữ liệu và tắt phần cứng một cách êm ái.

`	ext
Shutdown Request (KL15 off / ECUReset UDS)
  |
  ▼
EcuM_GoDown()
  ├── Rte_Stop()            ← Deactivate runnables
  ├── Com_IpduGroupStop()   ← Stop CAN transmission
  ├── NvM_WriteAll()        ← Persist data to flash
  ├── Wait NvM_WriteAll complete (timeout!)
  ├── Dem_Shutdown()
  └── EcuM_AL_DriverRestart() ← Power down
  |
  ▼
ShutdownOS()
`

- **Tại sao NvM_WriteAll phải xong trước shutdown?** Các dữ liệu quan trọng như số ODO, lịch sử lỗi (DTC), learned values (vị trí bướm ga) cần được lưu xuống Flash/EEPROM. Nếu cúp điện đột ngột, dữ liệu này sẽ mất hoặc bị corrupt.
- **Timeout handling:** Việc ghi Flash tốn thời gian. Tuy nhiên, năng lượng từ tụ điện của ECU chỉ duy trì được vài chục mili-giây sau khi mất nguồn (power loss). Do đó phải có một cơ chế Timeout. Nếu NvM ghi quá lâu, hệ thống phải force shutdown hoặc hardware sẽ tự sập nguồn.
- **KL15 event vs Software reset:** 
  - **KL15 (Ignition off):** Đây là một quá trình shutdown thông thường (graceful shutdown), có đủ thời gian để xử lý NvM.
  - **Software reset (UDS 0x11 ECUReset):** Do tester gửi qua mạng CAN. Không cắt nguồn mà chỉ reset MCU bằng lệnh phần mềm (NVIC_SystemReset()). NvM vẫn phải được lưu trước khi gọi reset.

---

## 4. Debug Scenarios (Các kịch bản sửa lỗi thực tế)

Dưới đây là kinh nghiệm 15 năm debug trên các bench test:

### Scenario 1: ECU không boot (No CAN message, No power consumption)
- **Symptom:** Mạch có điện nhưng không chạy, dòng tiêu thụ rất nhỏ hoặc liên tục nhảy (loop reset).
- **Check list:** 
  1. Kiểm tra nguồn cấp (LDO 5V, 3.3V) và chân Reset của MCU có bị kéo xuống GND không.
  2. Dùng Oscilloscope đo thạch anh (Crystal) xem có dao động không.
  3. Kiểm tra Watchdog: Watchdog kích hoạt quá sớm trong khi MCU clock chưa kịp lock PLL.
- **Breakpoint strategy:** Đặt breakpoint tại main() → Nếu không hit, lỗi ở startup.s. Nếu hit, step qua từng hàm trong EcuM_Init(), thường chết ở Mcu_InitClock().

### Scenario 2: Task không chạy sau StartOS
- **Symptom:** Code chạy qua StartOS() nhưng sau đó treo vào Idle Task, các task chức năng không được gọi.
- **Check list:** 
  1. Kiểm tra cấu hình OIL: Các Base Task có được set AUTOSTART = TRUE không?
  2. Trong StartupHook(), có gọi ActivateTask(BswInitTask) hay SetRelAlarm() không?
- **Advanced tool:** Sử dụng OS Hooks (PreTaskHook, PostTaskHook) đẩy ra UART hoặc dùng các công cụ trace (Lauterbach, SEGGER SystemView) để xem OS có chuyển ngữ cảnh (context switch) thành công không.

### Scenario 3: Startup time quá lâu (> 500ms)
- **Symptom:** CAN network quản lý yêu cầu ECU phải gửi bản tin đầu tiên trong vòng 100ms sau khi bật khóa, nhưng thực tế mất tới 600ms.
- **Root cause:** Kẻ thủ phạm phổ biến nhất là NvM_ReadAll(). Đọc vài KB dữ liệu qua bus SPI chặn toàn bộ các module khác.
- **Optimization:** Tách NvM_ReadAll() thành các phase nhỏ. Chỉ block những dữ liệu cực kỳ quan trọng ở Phase 2, các dữ liệu không quan trọng (như fault log) sẽ được khởi tạo ngầm sau khi CAN đã bật và Rte đã chạy. Sử dụng GPIO toggle đo thời gian thực thi của từng hàm Init để tìm nút thắt.

### Scenario 4: Data corruption sau power cycle
- **Symptom:** Bật tắt nguồn liên tục, đọc lại DTC thấy báo lỗi Data Checksum Error hoặc các biến NvM bị gán về giá trị Default.
- **Root cause:** Quá trình cúp nguồn diễn ra nhanh hơn thời gian NvM_WriteAll() kịp hoàn thành. Sector flash đang ghi dở bị sập nguồn.
- **Solution:** Tạo một Shutdown Task có độ ưu tiên cao nhất, block tất cả task khác, dùng polling (không dùng ngắt) để đẩy data xuống SPI/Flash nhanh nhất có thể. Đảm bảo hardware có đủ tụ (Capacitor) duy trì điện áp trong ít nhất 100ms sau khi rớt KL15.

---

## 5. Code Examples thực tế

Các đoạn mã dưới đây mô phỏng kiến trúc thực tế của AUTOSAR:

**EcuM_Init() skeleton:**
`c
void EcuM_Init(void) {
    /* Phase 1: Basic setup */
    Mcu_Init(&Mcu_Config);
    Mcu_InitClock(McuConf_McuClockSettingConfig_0);
    while(Mcu_GetPllStatus() != MCU_PLL_LOCKED);
    Mcu_DistributePllClock();
    
    Wdg_Init(&Wdg_Config); /* Safety first */
    
    /* Phase 2: Peripherals */
    Port_Init(&Port_Config);
    Dio_Init(&Dio_Config);
    Can_Init(&Can_Config);
    
    /* Start Async NvM Reading */
    NvM_ReadAll();
    
    /* Transfer control to OS */
    StartOS(OSDEFAULTAPPMODE);
    /* Should never reach here */
    while(1);
}
`

**StartupHook() implementation:**
`c
void StartupHook(void) {
    /* Called by OS before any task starts */
    ActivateTask(Task_BswInit);
    /* Start OS tick timer */
    Os_StartTickTimer();
}
`

**EcuM_StartupTwo() với NvM wait loop:**
`c
TASK(Task_BswInit) {
    /* Init Communication Stack */
    CanIf_Init(&CanIf_Config);
    CanTp_Init(&CanTp_Config);
    PduR_Init(&PduR_Config);
    Com_Init(&Com_Config);
    
    /* Wait for NvM to complete reading */
    NvM_RequestResultType NvmResult;
    do {
        NvM_MainFunction(); /* Process flash reading */
        MemIf_MainFunction();
        NvM_GetErrorStatus(0, &NvmResult); /* 0 = Block 0 (Multi-block) */
    } while (NvmResult == NVM_REQ_PENDING);
    
    /* Init Diagnostics */
    Dem_Init();
    Dcm_Init();
    
    /* Request BswM to move to RUN state */
    BswM_RequestMode(BswM_EcuM_User, ECUM_STATE_RUN);
    
    TerminateTask();
}
`

**BswM ActionList implementation:**
`c
void BswM_Action_StartCommunication(void) {
    /* Generated code based on BswM Rules */
    Com_IpduGroupStart(ComConf_ComIPduGroup_TxGroup);
    Com_IpduGroupStart(ComConf_ComIPduGroup_RxGroup);
    CanSM_RequestComMode(CanSM_Network_0, COMM_FULL_COMMUNICATION);
    Rte_Start();
}
`

---

## 6. Source Code Mapping trong repo

Trong hệ thống mã nguồn AUTOSAR điển hình (ví dụ như mã nguồn mở Arctic Core hay các repo tương tự), bạn có thể tìm thấy việc triển khai ở các file sau:

- **Entry Point / Main:**
  s/com/as.application/board.posix/simulator/simulator.c (hoặc main.c ở các board thực tế)
  *Tìm kiếm int main(void) và xem hàm gọi EcuM_Init().*

- **EcuM Module (Mạch máu khởi động):**
  s/com/as.infrastructure/system/EcuM/EcuM.c
  *Tìm hàm EcuM_Init() và EcuM_StartupTwo(). Đây là nơi các sequence được thực thi.*

- **BswM Module (Quản lý trạng thái):**
  s/com/as.infrastructure/system/BswM/BswM.c
  *Tìm hàm BswM_MainFunction(). Nó chứa state machine lớn để chuyển mode dựa trên các Request.*

- **OS Wrapper / Kernel:**
  s/com/as.infrastructure/system/kernel/Os.c
  *Các hàm như StartOS(), ActivateTask(), và phần xử lý context switch.*

- **MCU Driver (Cấu hình core):**
  s/com/as.infrastructure/arch/stm32f1/mcal/Mcu.c
  *Khởi tạo Clock Tree, PLL, và thanh ghi hệ thống cho dòng chip cụ thể (STM32).*

---

## 7. Sequence Diagram (Mermaid)

`mermaid
sequenceDiagram
    participant Main
    participant EcuM
    participant Drivers
    participant NvM
    participant OS
    participant BswM
    participant RTE
    participant ASW

    Note over Main: Power On / Reset
    Main->>EcuM: EcuM_Init()
    activate EcuM
    EcuM->>Drivers: Mcu_Init(), Wdg_Init()
    EcuM->>Drivers: Port_Init(), Can_Init()
    EcuM->>NvM: NvM_ReadAll()
    Note over NvM: Async request initiated
    EcuM->>OS: StartOS()
    deactivate EcuM
    
    activate OS
    OS-->>OS: StartupHook()
    OS->>EcuM: Task_BswInit executes EcuM_StartupTwo()
    activate EcuM
    
    loop Wait for NvM
        EcuM->>NvM: NvM_MainFunction()
        EcuM->>NvM: NvM_GetErrorStatus()
    end
    
    EcuM->>Drivers: CanIf, PduR, Com Init
    EcuM->>BswM: BswM_RequestMode(RUN)
    deactivate EcuM
    
    BswM-->>BswM: Evaluate Rule: NvM OK & EcuM RUN
    BswM->>Drivers: Com_IpduGroupStart()
    BswM->>RTE: Rte_Start()
    activate RTE
    RTE->>ASW: Trigger Runnables
    activate ASW
    Note over ASW: ECU Application is running normally
`

---

## 8. Interview Q&A — 25 câu hỏi phỏng vấn cấp chuyên gia

Dưới đây là 25 câu hỏi hóc búa để kiểm tra kiến thức về ECU Startup & Shutdown, được tuyển chọn từ thực tế phỏng vấn các vị trí Senior/Principal BSW.

1. **Sự khác biệt giữa EcuM_Init và EcuM_StartupTwo là gì? Tại sao phải chia ra hai phase?**
   *Đáp án:* EcuM_Init chạy trước khi OS khởi động (interrupt bị disable, không có cơ chế timeout/mutex). EcuM_StartupTwo chạy như một task của OS, có thể tận dụng scheduler và interrupt. Chia ra để đảm bảo các module cần OS phải khởi tạo sau OS.

2. **Watchdog timer phải được khởi tạo ở đâu trong quá trình startup? Tại sao?**
   *Đáp án:* Ngay những dòng đầu tiên của EcuM_Init, thường là sau khi có clock cơ bản. Để đảm bảo hệ thống không bị treo vô hạn trong quá trình khởi tạo các ngoại vi khác.

3. **Nếu PLL không lock được (Mcu_GetPllStatus không trả về LOCKED), ECU nên xử lý thế nào?**
   *Đáp án:* Có thể nhảy vào một Safe State loop vô hạn và đợi Watchdog reset lại MCU, hoặc chạy ở chế độ clock thấp (internal RC oscillator) và báo lỗi DEM qua mạng.

4. **Tại sao NvM_ReadAll là hàm bất đồng bộ (asynchronous)?**
   *Đáp án:* Đọc từ flash/EEPROM rất chậm. Bất đồng bộ giúp CPU không bị block, có thể tiếp tục khởi tạo các module khác hoặc OS.

5. **Làm thế nào để đo đếm chính xác thời gian khởi động (Startup Time) bằng phần cứng?**
   *Đáp án:* Dùng một chân GPIO. Kéo High ngay tại lệnh đầu tiên của main(). Kéo Low khi kết thúc Rte_Start(). Dùng Oscilloscope đo bề rộng xung (pulse width).

6. **Trong AUTOSAR, khi nào thì hàm StartupHook được OS gọi?**
   *Đáp án:* Được gọi sau khi OS đã khởi tạo xong các cấu trúc dữ liệu cơ bản (scheduler, interrupts init) nhưng TRƯỚC KHI bất kỳ task nào được chạy.

7. **Thứ tự khởi tạo các module CAN Stack là gì?**
   *Đáp án:* Can (Driver) -> CanIf -> CanTp / LinIf -> PduR -> Com. Từ dưới lên trên.

8. **Tại sao Port_Init phải gọi sau Mcu_Init?**
   *Đáp án:* Port_Init ghi vào các thanh ghi để cấu hình chân I/O. Các thanh ghi này thuộc ngoại vi cần tín hiệu Clock từ MCU cấp. Nếu MCU chưa bật clock (trong Mcu_Init), ghi vào sẽ gây bus fault.

9. **BswM Mode Request khác gì với BswM Mode Indication?**
   *Đáp án:* Request là một module yêu cầu chuyển đổi trạng thái (ví dụ EcuM yêu cầu RUN). Indication là báo cáo trạng thái hiện tại từ một module gửi đến BswM.

10. **Làm thế nào RTE biết khi nào cần kích hoạt (activate) các Runnables của ASW?**
    *Đáp án:* Thông qua các Rte Trigger Points được sinh ra từ ARXML dựa trên Events (như TimingEvent 10ms, DataReceivedEvent). SchM (Scheduler) của BSW sẽ quản lý các timer OS để gọi vào Rte.

11. **Sự khác biệt giữa việc tắt nguồn cưỡng bức (Loss of Battery) và tắt nguồn có kiểm soát (KL15 Off)?**
    *Đáp án:* KL15 Off (Ignition Off) cho phép ECU chạy code shutdown bình thường (lưu NvM, tắt mạng). Loss of Battery thường ngắt điện đột ngột, ECU chỉ có vài ms dựa trên tụ điện, đòi hỏi cơ chế Early Power Loss detection và ghi NvM cấp tốc.

12. **Nếu NvM_WriteAll treo trong quá trình Shutdown, ECU có bị kẹt mãi mãi không tắt được không?**
    *Đáp án:* Không, phải có cơ chế Shutdown Watchdog hoặc Hardware Timer cắt nguồn mạch (như tắt chip nguồn SBC). Nếu phần mềm treo, SBC sẽ ngắt nguồn VCC.

13. **Điều gì xảy ra nếu một biến C++ global có Constructor được biên dịch cùng với EcuM?**
    *Đáp án:* Compiler sẽ chèn mã gọi các constructor này TRƯỚC hàm main(). Lúc này Watchdog và Clock chưa khởi tạo, CPU có thể treo hoặc bị Watchdog reset liên tục.

14. **Khi một ECU reset thông qua lệnh chẩn đoán (UDS 0x11 ECUReset), luồng chạy sẽ như thế nào?**
    *Đáp án:* Dcm nhận request -> gọi BswM Request Reset -> BswM chạy Action List Shutdown -> gọi EcuM_GoDown -> Lưu NvM -> gọi Mcu_PerformReset (lệnh reset bằng phần mềm).

15. **Pre-Task Hook và Post-Task Hook của OS thường được dùng để làm gì trong giai đoạn Startup?**
    *Đáp án:* Dùng để profiling (đo thời gian thực thi của từng task) bằng cách lưu timestamp, hoặc phát hiện lỗi nếu một Init Task chạy quá thời gian quy định.

16. **Vì sao phải cấu hình .bss là vùng nhớ gán giá trị 0 thay vì để rác?**
    *Đáp án:* Chuẩn ngôn ngữ C quy định các biến global không khởi tạo (uninitialized) mặc định phải bằng 0. Nếu không zero-fill .bss, code có thể chạy sai do biến toàn cục chứa giá trị ngẫu nhiên từ RAM.

17. **Dcm (Diagnostic Communication Manager) nên được khởi tạo ở giai đoạn nào của quá trình khởi động?**
    *Đáp án:* Ở EcuM_StartupTwo (Post-OS), sau khi Com và NvM (DTC memory) đã khởi tạo xong, để nó có thể phản hồi các thông điệp chẩn đoán trên mạng.

18. **Nếu thạch anh (Crystal) bị hỏng vật lý, ECU làm sao boot?**
    *Đáp án:* Nhiều MCU hiện đại có Clock Security System (CSS). Nếu không thấy xung thạch anh ngoài, MCU tự động chuyển sang dao động nội (Internal RC Oscillator) và có thể kích hoạt ngắt NMI (Non-Maskable Interrupt).

19. **Phân biệt giữa EcuM_AL_DriverInitZero và EcuM_AL_DriverInitOne?**
    *Đáp án:* InitZero chứa các hàm init bắt buộc nhất (không phụ thuộc vào post-build config) như base MCU, Watchdog. InitOne khởi tạo các ngoại vi cần thiết lập pin/clock nhưng chưa cần OS.

20. **Tại sao không nên dùng malloc/free (Dynamic Memory Allocation) trong hệ thống nhúng ô tô?**
    *Đáp án:* Gây phân mảnh bộ nhớ (fragmentation), khó đoán thời gian thực thi, dễ dẫn đến out-of-memory exception trong quá trình boot. AUTOSAR quy định cấp phát tĩnh.

21. **Trong BswM, một Rule có thể chứa nhiều Action List không?**
    *Đáp án:* Có. Một rule có thể gán các action list riêng cho kết quả True và False (True Action List, False Action List).

22. **SchM_Init có vai trò gì?**
    *Đáp án:* Khởi tạo BSW Scheduler, một thành phần sinh tự động của Rte, giúp lập lịch thực thi các MainFunctions của các module BSW (như Com_MainFunction_Rx, Can_MainFunction_Read).

23. **Nếu có 2 Core (Multicore MCU), Startup Sequence thay đổi thế nào?**
    *Đáp án:* Master Core sẽ boot trước (chạy EcuM_Init), thiết lập bộ nhớ chung. Sau đó Master Core đánh thức (wake-up) Slave Cores. Mỗi core sẽ chạy hàm StartOS riêng của nó nhưng đồng bộ với nhau qua các Spinlocks.

24. **Khi mạng CAN chưa sẵn sàng (Network Off), làm sao ECU nhận được gói tin đánh thức (Wake-up)?**
    *Đáp án:* Thông qua CAN Transceiver (Hardware). Transceiver sẽ phát hiện biến thiên điện áp trên dây CAN và kéo chân INH hoặc WAKE của MCU xuống Low/High, tạo ngắt phần cứng đánh thức MCU khỏi chế độ Sleep.

25. **Nếu khách hàng yêu cầu boot ECU trong 50ms, bạn tối ưu gì đầu tiên?**
    *Đáp án:* Tối tắt/bỏ qua việc đọc toàn bộ flash (NvM_ReadAll). Chuyển sang đọc On-Demand (chỉ đọc khối nào cần). Khởi tạo tối thiểu hóa (chỉ init CAN và xử lý tin nhắn đầu tiên), các module khác init sau.
