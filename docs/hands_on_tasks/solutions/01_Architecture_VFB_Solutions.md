# BỘ LỜI GIẢI MẪU CHI TIẾT (END-TO-END CODE TRACE): CHUYÊN ĐỀ 01
## Layered Architecture & Virtual Functional Bus (VFB) — Hands-On Solutions

> 📚 **Đề bài tương ứng:** [docs/hands_on_tasks/01_Architecture_VFB_Tasks.md](../01_Architecture_VFB_Tasks.md)  
> 💡 **Lời giải ComStack CAN 6 tầng:** Đã được quy hoạch chuyên biệt tại [docs/hands_on_tasks/solutions/02_ComStack_CAN_Solutions.md](02_ComStack_CAN_Solutions.md)  
> 🎯 **Mục tiêu:** Cung cấp lời giải mẫu chuẩn xác 100%, bám sát mã nguồn thực tế trong repo `as/`, trình bày dưới dạng chuỗi gọi hàm liên tục (**Function-Call-Function Trace**) kèm trích dẫn số dòng và tên file cụ thể.

---

## 📑 MỤC LỤC LỜI GIẢI
1. [LỜI GIẢI TASK 1.1: Trace Chu Trình Khởi Động ECU Toàn Diện](#task-11)
2. [LỜI GIẢI TASK 1.2: Trace 3 Cơ Chế Đặc Biệt (OS Hooks, BSW Callouts & Callbacks)](#task-12)
3. [LỜI GIẢI TASK 1.3: Phân Tích Linker Script & Phân Vùng Bộ Nhớ](#task-13)
4. [LỜI GIẢI TASK 1.4: Phân Tích Cây Phụ Thuộc & Thứ Tự Khởi Tạo BSW](#task-14)
5. [LỜI GIẢI TASK 1.5: Tự Động Hóa Bóc Tách RTE Port Mapping](#task-15)

---

<a id="task-11"></a>
## 🚀 LỜI GIẢI TASK 1.1: Trace Chu Trình Khởi Động ECU Toàn Diện
> 🎯 **Mục tiêu:** Lần vết từ điểm vào phần cứng (`reset_handler`) qua 5 giai đoạn đến khi hệ thống vào chế độ `RUN`.

### 1. Sơ Đồ Chuỗi Gọi Hàm End-to-End (Call Graph Tree):

```
[Phần Cứng Reset Vector] 
   │
   ▼
1. reset_handler()  (startup.S: L319)
   │  ├── ldr sp, =knl_system_stack_top
   │  ├── LoopCopyDataInit (Copy Flash -> RAM .data)
   │  ├── LoopFillZerobss  (Zero RAM .bss)
   │  └── bl main
   │
   ▼
2. main()  (release/ascore/app/main.c: L65)
   │  ├── ASENVINIT(argc, argv)
   │  └── EcuM_Init()
   │
   ▼
3. EcuM_Init()  [STARTUP I - Pre-OS Phase]  (EcuM.c: L175)
   │  ├── EcuM_AL_DriverInitZero()  (EcuM_Callout_Stubs.c: L203)
   │  │     └── Det_Init(), Det_Start()
   │  ├── InitOS()
   │  ├── Os_IsrInit()
   │  ├── EcuM_DeterminePbConfiguration() -> &EcuMConfig
   │  ├── EcuM_AL_DriverInitOne()  (EcuM_Callout_Stubs.c: L220)
   │  │     ├── Mcu_Init(ConfigPtr->McuConfig)
   │  │     ├── Mcu_InitClock(ConfigPtr->McuConfig->DefaultClockSettings)
   │  │     ├── Mcu_DistributePllClock()  (arch/lm3s/mcal/Mcu.c: L124)
   │  │     │     ├── Usart_Init() (L47: Bật UART0 Debug & UART1 CAN)
   │  │     │     └── SysTickEnable() (Kích hoạt ngắt nhịp hệ thống 1ms)
   │  │     └── Port_Init(), Gpt_Init(), Wdg_Init()
   │  ├── EcuM_SetWakeupEvent(ECUM_WKSOURCE_POWER) -> Log "ECUM : <-CALLIN : EcuM_SetWakeupEvent 0x1"
   │  ├── EcuM_SelectShutdownTarget(...)
   │  └── StartOS(appMode)  (kernel.c: L185)
   │
   ▼
4. StartOS()  [OS Startup Phase]  (kernel.c: L185)
   │  ├── Os_PortInit()
   │  ├── Os_TaskInit(Mode)
   │  ├── Os_AlarmInit(Mode)
   │  ├── OSStartupHook()  (kernel_internal.h: L152)
   │  │     └── StartupHook()  (release/ascore/app/app.c: L81)
   │  │           ├── printf(" start application BUILD @ ...\n")
   │  │           └── printf(" cpu is little endian\n")
   │  ├── Sched_GetReady()
   │  └── Os_PortStartFirstDispatch()  (Chuyển ngữ cảnh sang Task khởi động)
   │
   ▼
5. EcuM_StartupTwo()  [STARTUP II - Post-OS Phase]  (EcuM.c: L253)
      ├── SchM_Init()
      ├── EcuM_AL_DriverInitTwo()  (EcuM_Callout_Stubs.c: L315)
      │     ├── PduR_Init() -> Log "LOW :--Initialization of PDU router completed --"
      │     ├── Can_Init(), CanIf_Init(), Com_Init()
      │     └── Xcp_Init()  -> Log "XCP MTA memory address ..."
      ├── EcuM_AL_DriverInitThree() -> Dem_Init(), ComM_Init()
      ├── Rte_Start()
      └── [RUN Mode Active]: TaskIdle chạy -> Log "STDOUT :TaskIdle is running"
```

### 2. Trích Dẫn Mã Nguồn & Vị Trí Dòng Code Thực Tế:

#### 🔹 Giai đoạn 1: Vector Bật Nguồn & Khởi Tạo Bộ Nhớ (Reset Vector)
* **File:** [`as/com/as.application/board.lm3s6965evb/script/linker.lds`](../../as/com/as.application/board.lm3s6965evb/script/linker.lds#L15)
  ```c
  /* Dòng 15: Định nghĩa điểm vào thực thi đầu tiên của CPU */
  ENTRY(reset_handler)
  ```
* **File:** [`as/com/as.infrastructure/system/kernel/askar/portable/cortex-m/startup.S`](../../as/com/as.infrastructure/system/kernel/askar/portable/cortex-m/startup.S#L319-L351)
  ```asm
  reset_handler:
      ldr  sp, =knl_system_stack_top      /* Thiết lập đỉnh ngăn xếp hệ thống */
      ldr  r0, =__data_start__            /* Địa chỉ bắt đầu RAM .data */
      ldr  r3, =__data_end__              /* Địa chỉ kết thúc RAM .data */
      ldr  r5, =__etext                  /* Vị trí chứa data trên Flash */
      movs r1, #0
  LoopCopyDataInit:
      adds r2, r0, r1
      cmp  r2, r3
      bcc  CopyDataInit
      ldr  r2, =__bss_start__            /* Bắt đầu vùng RAM .bss */
  LoopFillZerobss:
      ldr  r3, = __bss_end__
      cmp  r2, r3
      bcc  FillZerobss
      bl  main                          /* Nhảy vào hàm main() trong C */
  ```

#### 🔹 Giai đoạn 2 & 3: `main()` và `EcuM_Init()` (Pre-OS)
* **File:** [`as/release/ascore/app/main.c`](../../as/release/ascore/app/main.c#L65-L71)
  ```c
  int main(int argc,char* argv[])
  {
      ASENVINIT(argc,argv);
      EcuM_Init();      /* Khởi tạo toàn bộ ngăn xếp AUTOSAR BSW */
      while(1);
      return 0;
  }
  ```
* **File:** [`as/com/as.infrastructure/system/EcuM/EcuM.c`](../../as/com/as.infrastructure/system/EcuM/EcuM.c#L175-L249)
  ```c
  void EcuM_Init(void) {
      set_current_state(ECUM_STATE_STARTUP_ONE);
      EcuM_AL_DriverInitZero();                     /* Khởi tạo DET */
      InitOS();
      Os_IsrInit();
      EcuM_World.config = EcuM_DeterminePbConfiguration();
      EcuM_AL_DriverInitOne(EcuM_World.config);     /* Khởi tạo Mcu, Clock, Port, Usart */
      EcuM_SetWakeupEvent(ECUM_WKSOURCE_POWER);     /* Báo sự kiện bật nguồn */
      StartOS(appMode);                             /* Trao quyền cho OS */
  }
  ```

#### 🔹 Giai đoạn 4: `StartOS()` và Kích Hoạt `StartupHook()`
* **File:** [`as/com/as.infrastructure/system/kernel/askar/kernel/kernel.c`](../../as/com/as.infrastructure/system/kernel/askar/kernel/kernel.c#L185)
  ```c
  void StartOS(AppModeType Mode) {
      Os_PortInit();
      Os_TaskInit(Mode);
      Os_AlarmInit(Mode);
      OSStartupHook();               /* Gọi hàm StartupHook() của ứng dụng */
      Sched_GetReady();
      Os_PortStartFirstDispatch();   /* Kích hoạt Task Autostart đầu tiên */
  }
  ```
* **File:** [`as/release/ascore/app/app.c`](../../as/release/ascore/app/app.c#L81-L93)
  ```c
  void StartupHook(void) {
      uint32 endian = 0xdeadbeef;
      printf(" start application BUILD @ %s %s\n", __DATE__, __TIME__);
      if(0xde == (*(uint8_t*)&endian))
          printf(" cpu is big endian\n");
      else
          printf(" cpu is little endian\n");
  }
  ```

#### 🔹 Giai đoạn 5: Task Autostart `SchM_Startup` Kích Hoạt `EcuM_StartupTwo()` (Post-OS)
Theo chuẩn AUTOSAR, sau khi OS bật xong, một Task khởi động đặc biệt (**Autostart Task**) sẽ được Scheduler dispatch đầu tiên để hoàn tất giai đoạn khởi tạo Post-OS:
* **File cấu hình:** [`as/build/nt/lm3s6965evb/ascore/config/Os_Cfg.c`](../../as/build/nt/lm3s6965evb/ascore/config/Os_Cfg.c#L204-L221)
  Task `SchM_Startup` được cấu hình cờ `.appModeMask = (0 | OSDEFAULTAPPMODE)` và độ ưu tiên cao nhất (`PTHREAD_PRIORITY + 7`) $\rightarrow$ Tự động chạy ngay khi `StartOS` hoàn tất.
* **File thực thi:** [`as/com/as.infrastructure/system/SchM/SchM.c`](../../as/com/as.infrastructure/system/SchM/SchM.c#L410-L435)
  ```c
  TASK(SchM_Startup) {
      OS_TASK_BEGIN();
      
      /* Gọi EcuM_StartupTwo để khởi tạo các BSW phụ thuộc OS và NvM */
      EcuM_StartupTwo();
      
      /* Thiết lập Timer chu kỳ cho BSW và chuyển EcuM sang RUN Mode */
      SetRelAlarm(ALARM_ID_Alarm_BswService, 10, SCHM_MAIN_ALARM_CYCLE);
      EcuM_RequestRUN(ECUM_USER_User_1);
      
      /* Chấm dứt Task khởi động */
      TerminateTask();
  }
  ```
* **File:** [`as/com/as.infrastructure/system/EcuM/EcuM.c`](../../as/com/as.infrastructure/system/EcuM/EcuM.c#L253-L300)
  Hàm `EcuM_StartupTwo()` gọi tiếp `EcuM_AL_DriverInitTwo()` $\rightarrow$ `PduR_Init()`, `Can_Init()`, `Xcp_Init()` $\rightarrow$ `Rte_Start()`. Khi `SchM_Startup` kết thúc, hệ thống nhường quyền cho các Task chu kỳ và `TaskIdle`!

---

### 3. 🧠 PHÂN TÍCH ĐỐI SÁNH KIẾN TRÚC: VÌ SAO CHU TRÌNH BOOT CỦA AUTOSAR (MCU) TINH GỌN HƠN EMBEDDED LINUX (MPU/SOC)?

Trong kỹ nghệ hệ thống nhúng, nhiều kỹ sư quen thuộc với Embedded Linux thường thắc mắc: *"Tại sao chu trình boot của AUTOSAR lại tinh gọn, không có các giai đoạn nạp đa tầng (Multi-stage Boot: BootROM $\rightarrow$ SPL $\rightarrow$ U-Boot $\rightarrow$ Kernel) như Linux?"*

Sự khác biệt mang tính bản chất này bắt nguồn từ **3 nguyên nhân kỹ nghệ cốt lõi**:

#### 🔹 3.1 Bản Chất Khác Biệt Về Phần Cứng (Hardware Architecture: MPU vs MCU)

```
┌───────────────────────────────────────────────────────────┐    ┌───────────────────────────────────────────────────────────┐
│              🐧 LINUX EMBEDDED (SoC / MPU)                │    │               🚗 CLASSIC AUTOSAR (MCU)                    │
│           (Cortex-A, Qualcomm, NXP i.MX8, x86)            │    │         (Cortex-M, Infineon TriCore, S32K, RH850)         │
├───────────────────────────────────────────────────────────┤    ├───────────────────────────────────────────────────────────┤
│ • Mã nguồn nằm trên ổ nhớ ngoài rời (eMMC, NAND, UFS).    │    │ • Mã nguồn nằm trên chip nhớ Flash NỘI BỘ (Internal Flash)│
│ • Bộ nhớ RAM là chip DDR3/DDR4/LPDDR5 ngoài rời (vài GB). │    │ • Bộ nhớ RAM là SRAM NỘI BỘ tích hợp sẵn (64KB - 4MB).   │
│ • Có bộ quản lý bộ nhớ ảo (MMU / Virtual Memory Paging).  │    │ • Bộ nhớ phẳng vật lý (Flat Physical Memory - ZERO MMU).  │
│ • Bắt buộc phải nạp/giải nén code từ ổ cứng lên DDR RAM.  │    │ • Thực thi trực tiếp trên Flash (Execute-In-Place - XIP). │
└───────────────────────────────────────────────────────────┘    └───────────────────────────────────────────────────────────┘
```

* **Tại sao Linux bắt buộc phải boot qua nhiều Phase?**
  1. **Lúc vừa cấp nguồn:** Chip SoC của Linux **chưa nhận diện được RAM DDR ngoài** (do chưa cấp xung clock, chưa căn chỉnh độ trễ tín hiệu *DDR Timing Training*).
  2. **Phase 0 (BootROM):** CPU chỉ có vài chục KB SRAM nội bộ, chỉ đủ nạp đoạn mã siêu nhỏ là **SPL (Secondary Program Loader)**.
  3. **Phase 1 (SPL / TF-A):** Cấu hình bộ điều khiển RAM DDR ngoài, chuyển chế độ bảo mật ARM TrustZone (Secure World $\leftrightarrow$ Normal World).
  4. **Phase 2 (U-Boot):** Sau khi DDR RAM sẵn sàng, U-Boot mới đọc ổ cứng eMMC, nạp Kernel (`zImage`/`Image`) và Device Tree (`.dtb`) lên RAM.
  5. **Phase 3 (Linux Kernel):** Bật MMU, giải nén kernel, mount RootFS và kích hoạt `systemd`.
  * ⏱️ *Thời gian khởi động:* Thường mất từ **$2\text{ giây}$ đến $30\text{ giây}$**.

* **Tại sao AUTOSAR trên Vi điều khiển (MCU) lại chạy thẳng được ngay?**
  * Chip MCU tích hợp CPU, Flash và RAM **chung trên một đế silicon duy nhất**.
  * Nhờ công nghệ **XIP (Execute-In-Place)**, con trỏ lệnh PC của CPU đọc và thực thi từng lệnh máy trực tiếp từ Flash nội bộ qua bus nội bộ tốc độ cao mà **không cần nạp lên RAM, không cần giải nén**.

#### 🔹 3.2 Yêu Cầu An Toàn Sống Còn Của Ô Tô (Cold Boot Timing $< 50\text{ ms}$ & ISO 26262 ASIL-D)
Trong ngành công nghiệp ô tô, tiêu chuẩn an toàn chức năng cao nhất (**ISO 26262 ASIL-D**) quy định:
* **Hệ thống Phanh khẩn cấp (ABS / ESP / Braking ECU):** Phải hoạt động và sẵn sàng phanh trong vòng **dưới $50\text{ ms}$** ngay khi xoay chìa khóa.
* **Hệ thống Túi khí (Airbag ECU):** Phải sẵn sàng kích nổ túi khí ngay lập tức nếu xe gặp va chạm trong giây đầu tiên.
* **Mạng CAN Bus toàn xe:** Mọi ECU phải phản hồi gói tin mạng trong vòng **$100\text{ ms}$**.

👉 Nếu dùng kiến trúc boot nhiều tầng kéo dài vài giây như Linux, xe hơi sẽ đối mặt với thảm họa an toàn nghiêm trọng trước khi hệ thống kịp khởi động xong!

#### 🔹 3.3 Tầng Bảo Mật Phần Cứng (HSM) & Flash Bootloader (FBL) Trong Xe Hơi Thực Tế
Trong các vi điều khiển ô tô thế hệ mới (Infineon AURIX TriCore TC397/TC4xx, NXP S32K3, ST Stellar), quy trình khởi động an toàn được xử lý bằng phần cứng chuyên biệt:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                   CHU TRÌNH BOOT AN TOÀN & BOOTLOADER TRONG ECU THỰC TẾ                │
│                                                                                        │
│  1. [LÕI BẢO MẬT PHẦN CỨNG RIÊNG BIỆT - HSM (Hardware Security Module)]:               │
│     • Lõi bảo mật (ARM Cortex-M0+ hoặc Crypto Engine) khởi động trước (~2-5ms).        │
│     • Xác thực Chữ ký số (Secure Boot / CMAC / ECDSA) của phân vùng Flash AUTOSAR.     │
│                                                                                        │
│  2. [PHÂN VÙNG NẠP FLASH BOOTLOADER (FBL - Target asboot)]:                            │
│     • Nằm ở phân vùng đầu Flash (ví dụ 0x00000000 - 0x00010000).                       │
│     • Kiểm tra cờ nạp phần mềm từ xa qua CAN (FOTA / Reprogramming Flag).              │
│     • Nếu KHÔNG có yêu cầu nạp code: Nhảy trực tiếp (Direct Jump) sang App trong < 1ms!│
│                                                                                        │
│  3. [PHÂN VÙNG ỨNG DỤNG AUTOSAR (Target ascore)]:                                      │
│     • reset_handler -> main() -> EcuM_Init() -> StartOS() -> EcuM_StartupTwo() -> RUN. │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

#### 🔹 3.4 Bảng Đối Chiếu Toàn Diện: Linux Embedded vs Classic AUTOSAR

| Tiêu Chí Kỹ Nghệ | 🐧 Embedded Linux (MPU / SoC) | 🚗 Classic AUTOSAR (MCU) |
| :--- | :--- | :--- |
| **Mục tiêu tối thượng** | **Tính toán khủng & Tính năng phong phú** (AI, Camera ADAS, Màn hình 3D, Mạng IP). | **Thời gian thực tiền định (Deterministic) & An toàn tuyệt đối (ASIL-D)**. |
| **Cơ chế nạp chương trình** | Đa tầng phức tạp (BootROM $\rightarrow$ SPL $\rightarrow$ U-Boot $\rightarrow$ Kernel). | Nhảy trực tiếp / XIP (Reset Vector $\rightarrow$ Flash $\rightarrow$ `main`). |
| **Quản lý bộ nhớ** | Bộ nhớ ảo MMU, phân trang động, nạp từ ổ đĩa eMMC. | Bộ nhớ vật lý phẳng (Flat Physical Memory), tĩnh 100%, không dùng `malloc`. |
| **Thời gian khởi động (Cold Boot)** | $2\text{ giây} - 30\text{ giây}$. | **$10\text{ ms} - 50\text{ ms}$ (Siêu nhanh)**. |
| **Cơ chế Bảo mật Khởi động** | ARM TrustZone, TF-A, OP-TEE (Phần mềm + Phần cứng). | **HSM / SHE (Lõi Crypto phần cứng độc lập)**. |

---

<a id="task-12"></a>
## 🛠️ LỜI GIẢI TASK 1.2: Trace 3 Cơ Chế Giao Tiếp Đặc Biệt (OS Hooks, BSW Callouts & MCAL Callbacks)
> 🎯 **Mục tiêu:** Chứng minh chi tiết bằng mã nguồn cách 3 cơ chế này được Setup (Cấu hình), Nơi được Call (Ai gọi và gọi khi nào), và Chuỗi Function-Call-Function vận hành end-to-end trong mã nguồn thực tế.

---

### 1. 🪝 CƠ CHẾ 1: OS HOOKS — Chuỗi Thực Thi Bắt Biến Cố Vòng Đời OS (3 Ví Dụ Điển Hình)
* **Bản chất kỹ thuật:** Trong RTOS, "Bắt sự kiện vòng đời" (Lifecycle Event Handling) **không dùng vòng lặp `while(1)` thăm dò (polling)** tốn CPU, mà **Nhân Hệ Điều Hành (OS Kernel) cài sẵn các điểm chặn (Hooks)** tại các bước chuyển trạng thái sống còn của CPU. Dưới đây là 3 Hook điển hình minh chứng cho 3 loại sự kiện khác nhau:

---

#### 🅰️ VÍ DỤ 1: `StartupHook()` — Bắt Sự Kiện Bật Nguồn Hệ Thống (Startup Lifecycle Event)
* **Setup trong ARXML:** File [`autosar.arxml`](../../as/build/nt/lm3s6965evb/ascore/config/autosar.arxml#L4) khai báo `<General StartupHook="StartupHook" ... />` $\rightarrow$ Toolchain sinh ra `#define OS_USE_STARTUP_HOOK` trong [`Os_Cfg.h`](../../as/build/nt/lm3s6965evb/ascore/config/Os_Cfg.h#L58).
* **Nơi Gọi (Caller) trong Kernel:**
  * **File:** [`as/com/as.infrastructure/system/kernel/askar/kernel/kernel.c`](../../as/com/as.infrastructure/system/kernel/askar/kernel/kernel.c#L183-L208) (Dòng 202):
    ```c
    void StartOS ( AppModeType Mode ) {
        ...
        Os_TaskInit(Mode);
        Os_AlarmInit(Mode);
        
        OSStartupHook();   /* <── DÒNG 202: NHÂN OS KÍCH HOẠT SỰ KIỆN BẬT NGUỒN! */
        
        Sched_GetReady();
        Os_PortStartFirstDispatch();
    }
    ```
  * **File:** [`as/com/as.infrastructure/system/kernel/askar/kernel/kernel_internal.h`](../../as/com/as.infrastructure/system/kernel/askar/kernel/kernel_internal.h#L150-L163):
    ```c
    #ifdef OS_USE_STARTUP_HOOK
    #define OSStartupHook() do {           \
        imask_t mask;                      \
        Irq_Save(mask);                    \  /* Khóa ngắt để bảo vệ nhân OS */
        CallLevel = TCL_STARTUP;           \  /* Đổi ngữ cảnh sang Startup */
        StartupHook();                     \  /* Nhảy sang thân hàm của Ứng dụng */
        CallLevel = TCL_TASK;              \
        Irq_Restore(mask);                 \  /* Mở lại ngắt */
    } while(0)
    ```
* **Thân hàm thực thi (Application Implementation):**
  * **File:** [`as/release/ascore/app/app.c`](../../as/release/ascore/app/app.c#L81-L93):
    ```c
    void StartupHook(void) {
        uint32 endian = 0xdeadbeef;
        printf(" start application BUILD @ %s %s\n", __DATE__, __TIME__);
        if(0xde == (*(uint8_t*)&endian))
            printf(" cpu is big endian\n");
        else
            printf(" cpu is little endian\n");
    }
    ```
* **Call Graph:**
  ```text
  StartOS() (kernel.c: L202)
     └──► OSStartupHook() (kernel_internal.h: L150)
             └──► StartupHook() (app.c: L81) ──► In log kiểm tra Endianess & Version Build
  ```

---

#### 🅱️ VÍ DỤ 2: `ErrorHook(StatusType ercd)` — Bắt Sự Kiện Lỗi Runtime Của Hệ Thống (VỚI SWITCH-CASE HANDLER!)
* **Setup trong ARXML:** File [`autosar.arxml`](../../as/build/nt/lm3s6965evb/ascore/config/autosar.arxml#L4) khai báo `ErrorHook="ErrorHook"`.
* **Nơi Gọi (Caller) trong Kernel khi phát hiện lỗi:**
  * Khi bất kỳ Task nào gọi sai API (ví dụ: Gọi `GetResource(RES_ID)` nhưng Resource đang bị Task khác chiếm giữ), nhân OS trong `resource.c` / `task.c` phát hiện `ercd = E_OS_RESOURCE` và gọi macro:
  * **File:** [`as/com/as.infrastructure/system/kernel/askar/kernel/kernel_internal.h`](../../as/com/as.infrastructure/system/kernel/askar/kernel/kernel_internal.h#L110-L124):
    ```c
    #define OSErrorTwo(api, param0, param1) do { \
        if(ercd != E_OK) {                       \
            imask_t mask;                        \
            Irq_Save(mask);                      \  /* Khóa ngắt */
            CallLevel = TCL_ERROR;               \  /* Đổi ngữ cảnh sang Xử lý lỗi */
            ErrorHook(ercd);                     \  /* <── GỌI HÀM BẮT LỖI CỦA KỸ SƯ! */
            CallLevel = savedLevel;              \
            Irq_Restore(mask);                   \
        }                                        \
    } while(0)
    ```
* **Thân hàm xử lý phân loại lỗi (Switch-Case Error Handler):**
  * **File:** [`as/release/ascore/app/app.c`](../../as/release/ascore/app/app.c#L340-L375):
    ```c
    void ErrorHook(StatusType ercd)
    {
        /* BỘ PHÂN LOẠI VÀ XỬ LÝ BIẾN CỐ LỖI HỆ ĐIỀU HÀNH */
        switch(ercd)
        {
            case E_OS_ACCESS:
                ASLOG(OS, ("ercd = %d E_OS_ACCESS: Truy cập tài nguyên trái phép!\r\n", ercd));
                break;
            case E_OS_CALLEVEL:
                ASLOG(OS, ("ercd = %d E_OS_CALLEVEL: Gọi API sai ngữ cảnh (từ ISR)!\r\n", ercd));
                break;
            case E_OS_ID:
                ASLOG(OS, ("ercd = %d E_OS_ID: TaskID hoặc ResourceID không tồn tại!\r\n", ercd));
                break;
            case E_OS_LIMIT:
                ASLOG(OS, ("ercd = %d E_OS_LIMIT: Kích hoạt Task vượt quá số lần cho phép!\r\n", ercd));
                break;
            case E_OS_RESOURCE:
                ASLOG(OS, ("ercd = %d E_OS_RESOURCE: Chiếm dụng Resource sai thứ tự!\r\n", ercd));
                break;
            case E_OS_STATE:
                ASLOG(OS, ("ercd = %d E_OS_STATE: Trạng thái Task không hợp lệ!\r\n", ercd));
                break;
            default:
                ASLOG(OS, ("ercd = %d Lỗi không xác định!\r\n", ercd));
                break;
        }
    }
    ```
* **Call Graph:**
  ```text
  GetResource(RES_LOCKED) (task.c / resource.c: ercd = E_OS_RESOURCE)
     └──► OSErrorTwo(GetResource, ...) (kernel_internal.h: L110)
             └──► ErrorHook(ercd) (app.c: L340)
                     └──► switch(ercd) -> Xử lý riêng biệt từng loại mã lỗi!
  ```

---

#### 🅲 VÍ DỤ 3: `PreTaskHook()` & `PostTaskHook()` — Bắt Sự Kiện Đổi Ngữ Cảnh Task (Context Switch Events)
* **Bản chất:** Được kích hoạt tự động **mỗi khi Scheduler nạp một Task vào CPU hoặc nhả Task ra khỏi CPU**.
* **Nơi Gọi trong Kernel:**
  * **File:** [`as/com/as.infrastructure/system/kernel/askar/kernel/kernel_internal.h`](../../as/com/as.infrastructure/system/kernel/askar/kernel/kernel_internal.h#L180-L208):
    ```c
    #define OSPreTaskHook() do { CallLevel = TCL_PREPOST; PreTaskHook(); } while(0)
    #define OSPostTaskHook() do { CallLevel = TCL_PREPOST; PostTaskHook(); } while(0)
    ```
* **Ứng dụng thực tế của Kỹ sư:**
  * Bắt thời điểm Task bắt đầu chạy để bấm giờ $
ightarrow$ tính toán **CPU Load** và kiểm tra **Stack Watermark (Tràn Stack)** trước khi chuyển giao CPU!

---

### 2. 🔌 CƠ CHẾ 2: BSW CALLOUT — Chuỗi Thực Thi `EcuM_AL_DriverInitZero()` & `DriverInitTwo()`
* **Bản chất:** Điểm neo mở (Stub) do module BSW dịch vụ gọi ra ngoài để kỹ sư tự tay khởi tạo các phần cứng đặc thù hoặc kích hoạt driver theo từng giai đoạn.

#### 🔹 Bước 1: Setup & Cấu hình (`EcuM_Cfg.h` & `asmconfig.h`)
* Bật các cờ `#define USE_DET`, `#define USE_CAN`, `#define USE_PDUR`, `#define USE_XCP` tương ứng với các module có mặt trên bo mạch.

#### 🔹 Bước 2: Nơi Gọi (Caller) Trong Luồng Boot (`EcuM.c` & `SchM.c`)
1. **Pre-OS Callout (`EcuM_AL_DriverInitZero`):**
   * **File:** [`as/com/as.infrastructure/system/EcuM/EcuM.c`](../../as/com/as.infrastructure/system/EcuM/EcuM.c#L175-L185) (Dòng 178):
     ```c
     void EcuM_Init(void) {
         set_current_state(ECUM_STATE_STARTUP_ONE);
         EcuM_AL_DriverInitZero();  /* <── DÒNG 178: GỌI CALLOUT KHỞI TẠO SỚM TRƯỚC KHI CÓ OS */
         InitOS();
         ...
     ```
2. **Post-OS Callout (`EcuM_AL_DriverInitTwo`):**
   * **File:** [`as/com/as.infrastructure/system/SchM/SchM.c`](../../as/com/as.infrastructure/system/SchM/SchM.c#L429) $
ightarrow$ gọi `EcuM_StartupTwo()` tại [`as/com/as.infrastructure/system/EcuM/EcuM.c`](../../as/com/as.infrastructure/system/EcuM/EcuM.c#L253-L275) (Dòng 270):
     ```c
     void EcuM_StartupTwo(void) {
         ...
         EcuM_AL_DriverInitTwo(EcuM_World.config); /* <── DÒNG 270: GỌI CALLOUT KHỞI TẠO BSW CẤP CAO */
         ...
     ```

#### 🔹 Bước 3: Thân Hàm Cài Đặt Trong Callout Stubs (`EcuM_Callout_Stubs.c`)
* **File:** [`as/com/as.infrastructure/system/EcuM/EcuM_Callout_Stubs.c`](../../as/com/as.infrastructure/system/EcuM/EcuM_Callout_Stubs.c#L203-L375):
  ```c
  /* Callout Pre-OS: Khởi tạo module Báo lỗi DET */
  void EcuM_AL_DriverInitZero(void) {
  #if defined(USE_DET)
      Det_Init();
      Det_Start();
  #endif
  }

  /* Callout Post-OS: Khởi tạo CAN, PduR, XCP */
  void EcuM_AL_DriverInitTwo(const EcuM_ConfigType* ConfigPtr) {
  #if defined(USE_CAN)
      Can_Init(ConfigPtr->CanConfig);
  #endif
  #if defined(USE_CANIF)
      CanIf_Init(ConfigPtr->CanIfConfig);
  #endif
  #if defined(USE_XCP)
      Xcp_Init(ConfigPtr->XcpConfig);
  #endif
  }
  ```

#### 🌳 Call Graph Function-Call-Function:
```text
[GIAI ĐOẠN 1: PRE-OS]
EcuM_Init() (EcuM.c: L178)
   └──► EcuM_AL_DriverInitZero() (EcuM_Callout_Stubs.c: L203)
           ├──► Det_Init()
           └──► Det_Start()

[GIAI ĐOẠN 2: POST-OS]
TASK(SchM_Startup) (SchM.c: L429)
   └──► EcuM_StartupTwo() (EcuM.c: L270)
           └──► EcuM_AL_DriverInitTwo() (EcuM_Callout_Stubs.c: L315)
                   ├──► Can_Init(ConfigPtr->CanConfig)
                   ├──► CanIf_Init(ConfigPtr->CanIfConfig)
                   └──► Xcp_Init(ConfigPtr->XcpConfig)
```

---

### 3. 📡 CƠ CHẾ 3: MCAL DRIVER CALLBACK — Chuỗi Thực Thi `CanIf_RxIndication()`
* **Bản chất:** Hàm thông báo bất đồng bộ (Asynchronous Notification) do tầng Driver phần cứng MCAL kích hoạt khi phần cứng nhận được frame dữ liệu, đẩy ngược lên các tầng trên.

#### 🔹 Bước 1: Setup & Cấu hình Bảng Routing (`CanIf_Cfg.c`)
* Trong file cấu hình sinh tự động `CanIf_Cfg.c`, mỗi Mailbox HRH (Hardware Receive Handle) được gắn với loại tầng trên nhận dữ liệu:
  ```c
  /* CanIf_Cfg.c: Cấu hình bảng PDU nhận */
  const CanIf_RxPduConfigType CanIfRxPduConfigData[] = {
      {
          .CanIfCanRxPduId   = COM_PDU_ID_VehicleStatus,
          .CanIfCanRxPduCanId = 0x180,
          .CanIfRxUserType   = CANIF_USER_TYPE_CAN_PDUR,  /* Đích đến là PduR */
      }
  };
  ```

#### 🔹 Bước 2: Nơi Kích Hoạt (Hardware Trigger trong Driver `SCan.c`)
* Khi phần cứng CAN nhận được gói tin, driver CAN đọc thanh ghi / buffer và gọi Callback `CanIf_RxIndication`:
* **File:** [`as/com/as.infrastructure/arch/common/mcal/SCan.c`](../../as/com/as.infrastructure/arch/common/mcal/SCan.c#L158-L174) (Dòng 171):
  ```c
  void Can_MainFunction_Read( void ) {
      Can_SerialInPduType pdu;
      ...
      if(RB_POP(canin, &pdu, sizeof(pdu)) > 0) {
          /* DÒNG 171: MCAL GỌI CALLBACK CanIf_RxIndication BÁO LÊN CANIF */
          CanIf_RxIndication(pdu.busid, SCANID(pdu.canid), pdu.dlc, pdu.data);
      }
  }
  ```

#### 🔹 Bước 3: Xử Lý Lọc ID & Đẩy Lên Tầng Trên Trong `CanIf.c`
* **File:** [`as/com/as.infrastructure/communication/CanIf/CanIf.c`](../../as/com/as.infrastructure/communication/CanIf/CanIf.c#L350-L405 & L1145):
  ```c
  void CanIf_RxIndication(uint16 Hrh, Can_IdType CanId, uint8 CanDlc, const uint8 *CanSduPtr) {
      /* 1. Nhận gói tin từ MCAL Driver */
      scheduleRxIndication(Hrh, CanId, CanDlc, CanSduPtr);
  }

  static void scheduleRxIndication(...) {
      /* 2. So khớp Software Filter Mask */
      if ((CanId & entry->CanIfCanRxPduCanIdMask) == entry->CanIfCanRxPduCanId) {
          
          /* 3. Kiểm tra User Type và gọi tiếp Callback của tầng trên */
          switch (entry->CanIfRxUserType) {
          case CANIF_USER_TYPE_CAN_PDUR:
          {
              PduInfoType pduInfo = { .SduLength = CanDlc, .SduDataPtr = (uint8*)CanSduPtr };
              
              /* DÒNG 403: GỌI TIẾP CALLBACK LÊN TẦNG PDU ROUTER */
              PduR_CanIfRxIndication(entry->CanIfCanRxPduId, &pduInfo);
              return;
          }
          case CANIF_USER_TYPE_CAN_TP:
              CanTp_RxIndication(entry->CanIfCanRxPduId, &CanTpRxPdu);
              return;
          }
      }
  }
  ```

#### 🔹 Bước 4: Tầng PduR Phân Phối Tiếp Lên Com (`PduR.c`)
* **File:** [`as/com/as.infrastructure/communication/PduR/PduR.c`](../../as/com/as.infrastructure/communication/PduR/PduR.c#L120):
  ```c
  void PduR_CanIfRxIndication(PduIdType RxPduId, const PduInfoType *PduInfoPtr) {
      /* Định tuyến gói tin sang module Com */
      Com_RxIndication(RxPduId, PduInfoPtr);
  }
  ```

#### 🌳 Call Graph Function-Call-Function Đầy Đủ (Rx Path):
```text
[PHẦN CỨNG CAN] Frame đến (ID: 0x180, Data: [0x01, 0x64, ...])
   │
   ▼
Can_MainFunction_Read() (SCan.c: L171)
   │
   └──► CanIf_RxIndication(Hrh, CanId, Dlc, Data) (CanIf.c: L1145)
           │
           └──► scheduleRxIndication() (CanIf.c: L350)
                   │ (Kiểm tra Filter Mask & DLC)
                   │
                   └──► PduR_CanIfRxIndication(PduId, &pduInfo) (CanIf.c: L403)
                           │
                           └──► Com_RxIndication(PduId, &pduInfo) (PduR.c: L120)
                                   │
                                   └──► Giải nén Signal vào bộ đệm ──► App gọi Rte_Read() lấy dữ liệu!
```

---

<a id="task-13"></a>
## 💾 LỜI GIẢI TASK 1.3: Phân Tích Linker Script & Phân Vùng Bộ Nhớ (.text, .bss, P2VAR, P2CONST, AUTOMATIC)

> 🎯 **Mục tiêu:** Phân tích cấu trúc phân đoạn bộ nhớ Flash/RAM trong file `linker.lds`, cơ chế trừu tượng hóa trình biên dịch của AUTOSAR trong `Compiler.h`, và nguyên lý ánh xạ bộ nhớ (`MemMap.h`) phục vụ an toàn chức năng ISO 26262.

---

### 1. Phân Tích Bản Đồ Phân Vùng Bộ Nhớ Vật Lý Trong [`linker.lds`](../../as/com/as.application/board.lm3s6965evb/script/linker.lds):

Trong kiến trúc ARM Cortex-M3 (Target `lm3s6965evb`), file linker script định nghĩa không gian địa chỉ bộ nhớ như sau:

* **Vùng nhớ Flash (`FLASH: rx`):** Bắt đầu tại `0x00000000`, độ lớn `256 KB` ($262.144 	ext{ bytes}$).
* **Vùng nhớ RAM (`RAM: rwx`):** Bắt đầu tại `0x20000000`, độ lớn `64 KB` ($65.536 	ext{ bytes}$).

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      BẢN ĐỒ PHÂN BỐ BỘ NHỚ VẬT LÝ (MEMORY MAP)               │
├─────────────────────────────────────────────────────────────────────────────┤
│ 0x00000000 ┌─────────────────────────────────────────────────────────────┐  │
│            │ FLASH ROM (256 KB) — Chỉ Đọc (Read-Only / Executable)       │  │
│            │  ├── .isr_vector (155 Vectors ngắt phần cứng ARM Cortex-M)  │  │
│            │  ├── .startup    (Mã lệnh hàm reset_handler)                │  │
│            │  ├── .text       (Mã nhị phân thực thi C của BSW & App SWC) │  │
│            │  └── .rodata     (Hằng số cấu hình, chuỗi ký tự, Table DBC) │  │
│            │  ═════════════════════════════════════════════════════════  │  │
│            │  [Bản sao khởi tạo của .data nằm ở cuối Flash: __etext]     │  │
│ 0x00040000 └─────────────────────────────────────────────────────────────┘  │
│                                                                             │
│ 0x20000000 ┌─────────────────────────────────────────────────────────────┐  │
│            │ SRAM (64 KB) — Đọc / Ghi (Read-Write / Data)                │  │
│            │  ├── .data       (__data_start__ -> __data_end__)           │  │
│            │  │               (Biến toàn cục/static CÓ khởi tạo giá trị) │  │
│            │  ├── .bss        (__bss_start__ -> __bss_end__)             │  │
│            │  │               (Biến toàn cục/static KHÔNG khởi tạo / =0) │  │
│            │  └── .init_stack (Ngăn xếp hệ thống 1024 Bytes)             │  │
│            │                  (knl_system_stack -> knl_system_stack_top) │  │
│ 0x20010000 └─────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### 2. Bảng So Sánh AUTOSAR Compiler Macros (`Compiler.h`) vs Standard C:

Để mã nguồn AUTOSAR có thể biên dịch được trên mọi loại Compiler công nghiệp (GCC, WindRiver Diab, Tasking, Green Hills Multi, IAR) mà không cần sửa code C, chuẩn AUTOSAR đưa ra tập macro trong [`as/com/as.infrastructure/include/Compiler.h`](../../as/com/as.infrastructure/include/Compiler.h):

| Macro AUTOSAR | Cú Pháp Standard C | Ý Nghĩa Kỹ Nghệ & Mục Đích An Toàn (ISO 26262) |
| :--- | :--- | :--- |
| `P2VAR(ptrtype, memclass, ptrclass)` | `ptrtype *` | Con trỏ trỏ tới dữ liệu có thể ghi đè (RAM). Tham số `memclass` xác định vùng nhớ biến đích (ví dụ: `AUTOMATIC` trên Stack hoặc `STATIC` trong RAM). |
| `P2CONST(ptrtype, memclass, ptrclass)`| `const ptrtype *` | Con trỏ trỏ tới vùng dữ liệu hằng số chỉ đọc (ROM/Flash). Trình biên dịch sẽ báo lỗi cú pháp nếu cố tình sửa dữ liệu qua con trỏ này. |
| `CONSTP2VAR(ptrtype, memclass, ptrclass)`| `ptrtype * const` | **Con trỏ hằng trỏ tới biến:** Bản thân địa chỉ của con trỏ được lưu cố định trong Flash ROM, nhưng giá trị mà nó trỏ tới nằm trong RAM và có thể thay đổi. |
| `CONSTP2CONST(ptrtype, memclass, ptrclass)`| `const ptrtype * const` | Con trỏ hằng trỏ tới dữ liệu hằng (Cả con trỏ và dữ liệu đích đều nằm cố định trong Flash). |
| `AUTOMATIC` | *(Trống)* | Khai báo biến cục bộ cấp phát trên Stack (Stack-allocated local variable). |
| `STATIC` | `static` | Giới hạn phạm vi biến/hàm trong nội bộ file (Internal Linkage), ngăn ngừa xung đột tên symbol toàn cục. |
| `CONST(type, memclass)` | `const type` | Định nghĩa biến hằng số chỉ đọc. |
| `VAR(type, memclass)` | `type` | Định nghĩa biến dữ liệu thông thường. |

---

### 3. Cơ Chế Phân Vùng Bộ Nhớ Độc Lập Trình Biên Dịch (`MemMap.h` Mechanism) Trong Mã Nguồn Gốc:

Trong mã nguồn gốc của dự án `as`, cơ chế phân vùng bộ nhớ độc lập trình biên dịch được định nghĩa chính thức tại [`as/com/as.infrastructure/include/MemMap.h`](../../as/com/as.infrastructure/include/MemMap.h) và được áp dụng trực tiếp trong các module BSW như [`as/com/as.infrastructure/diagnostic/Det/Det.c`](../../as/com/as.infrastructure/diagnostic/Det/Det.c#L35-L57), [`EcuM.c`](../../as/com/as.infrastructure/system/EcuM/EcuM.c#L83), [`CanNm.c`](../../as/com/as.infrastructure/communication/CanNm/CanNm.c#L56).

#### 🔹 3.1 Thiết Kế Chuẩn AUTOSAR vs Cài Đặt Thực Tế Trong `as/com/as.infrastructure/include/MemMap.h`:
File [`MemMap.h: L20-L65`](../../as/com/as.infrastructure/include/MemMap.h#L20-L65) giải thích trực tiếp cách chuyển đổi giữa chuẩn AUTOSAR truyền thống và tối ưu hóa cho trình biên dịch C99:

```c
/* as/com/as.infrastructure/include/MemMap.h: Dòng 26-62 */

/* Cách viết chuẩn AUTOSAR truyền thống:
 *     #define XXX_START_SEC_YYY
 *     #include "MemMap.h"
 *     int hello_1 = 123;
 *     #define XXX_STOP_SEC_YYY
 *     #include "MemMap.h"
 */

/* Trong MemMap.h của dự án, hệ thống chuyển đổi macro linh hoạt theo từng trình biên dịch: */
#if defined(__GNUC__) || defined(__DCC__)
    /* Dành cho GCC / Clang / Diab Compiler */
    #define SECTION_RAMLOG          __attribute__ ((section (".ramlog")))
    #define SECTION_RAM_NO_CACHE    __attribute__ ((section (".ram_no_cache")))
    #define SECTION_RAM_NO_INIT     __attribute__ ((section (".ram_no_init")))

#elif defined(__CWCC__)
    /* Dành cho Freescale CodeWarrior Compiler */
    #pragma section RW ".ramlog_data" ".ramlog_bss"
    #define SECTION_RAMLOG          __declspec(section ".ramlog_data")
    #define SECTION_RAM_NO_CACHE    __declspec(section ".ram_no_cache_data")
    #define SECTION_RAM_NO_INIT     __declspec(section ".ram_no_init_data")

#elif defined(__ICCHCS12__)
    /* Dành cho IAR Compiler */
    #define SECTION_RAMLOG          __no_init
#endif
```

#### 🔹 3.2 Ví Dụ Thực Tế Trong Mã Nguồn Module BSW DET ([`Det.c: L35-L57`](../../as/com/as.infrastructure/diagnostic/Det/Det.c#L35-L57)):
Trong module chẩn đoán lỗi BSW (Default Error Tracer - DET), biến mảng nhật ký lỗi `Det_RamLog` được ép buộc phân bổ vào phân vùng RAM không bị xóa khi reset (`.ramlog` / uninitialized RAM) thông qua macro của `MemMap.h`:

```c
/* as/com/as.infrastructure/diagnostic/Det/Det.c: Dòng 35 & 55-57 */

#include "MemMap.h"  /* <── DÒNG 35: NẠP ĐỊNH NGHĨA PHÂN VÙNG MEMMAP */

#if ( DET_USE_RAMLOG == STD_ON )
/* Biến đếm và Mảng lưu trữ Log lỗi của BSW được đặt vào vùng nhớ riêng biệt SECTION_RAMLOG */
SECTION_RAMLOG uint32 Det_RamlogIndex;
SECTION_RAMLOG Det_EntryType Det_RamLog[DET_RAMLOG_SIZE];
#endif
```

* **Ý nghĩa kỹ thuật thực tế:**  
  Khi vi điều khiển bị Reset (Watchdog Reset hoặc Software Reset), vùng RAM thông thường (`.bss` và `.data`) sẽ bị hàm `reset_handler` trong `startup.S` xóa sạch về 0. Nhờ đặt `Det_RamLog` vào vùng `SECTION_RAMLOG` (`.ramlog`), toàn bộ lịch sử các mã lỗi BSW xảy ra trước lúc Reset vẫn được giữ nguyên vẹn trong RAM để kỹ sư đọc ra phân tích nguyên nhân lỗi!

---

### 4. Ứng Dụng Trong An Toàn Chức Năng (ISO 26262 MPU Memory Partitioning):

Nhờ có phân vùng Section chi tiết, kỹ sư tích hợp có thể cấu hình **Bộ bảo vệ bộ nhớ phần cứng (Hardware MPU - Memory Protection Unit)**:
1. **Phân vùng ASIL-D (An toàn cao nhất):** Vùng RAM của Task Phanh (ABS/ESP) và BSW Core được gán quyền cấm ghi từ các Task thông thường.
2. **Phân vùng QM (Quality Management - Ứng dụng giải trí/Body):** Nếu một SWC điều khiển đèn trần bị lỗi tràn con trỏ (Wild Pointer / Buffer Overflow) cố tình ghi vào vùng nhớ của module COM/CAN, phần cứng MPU sẽ lập tức kích hoạt ngắt **MemManage Fault** và gọi `ErrorHook()` để cô lập lỗi, đảm bảo tính mạng cho hành khách trên xe!

---

<a id="task-14"></a>
## 🌳 LỜI GIẢI TASK 1.4: Phân Tích Cây Phụ Thuộc & Thứ Tự Khởi Tạo BSW Modules

> 🎯 **Mục tiêu:**  
> 1. Trích xuất thứ tự khởi tạo chuẩn của các module BSW từ `EcuM.c` và `EcuM_Callout_Stubs.c`.  
> 2. **Giải thích bản chất vật lý & kiến trúc:** Tại sao `Mcu_Init` và `Port_Init` bắt buộc phải chạy trước `Can_Init` và `Com_Init`?

---

### 1. Kịch Bản Python Phân Tích Thứ Tự Khởi Tạo BSW:

```python
# Script: parse_bsw_init_order.py
bsw_init_sequence = [
    {"Phase": "STARTUP I (Pre-OS)", "Module": "Det", "Callout": "EcuM_AL_DriverInitZero", "File": "EcuM_Callout_Stubs.c:L210"},
    {"Phase": "STARTUP I (Pre-OS)", "Module": "Mcu", "Callout": "EcuM_AL_DriverInitOne", "File": "EcuM_Callout_Stubs.c:L229"},
    {"Phase": "STARTUP I (Pre-OS)", "Module": "Port", "Callout": "EcuM_AL_DriverInitOne", "File": "EcuM_Callout_Stubs.c:L250"},
    {"Phase": "STARTUP I (Pre-OS)", "Module": "Gpt", "Callout": "EcuM_AL_DriverInitOne", "File": "EcuM_Callout_Stubs.c:L255"},
    {"Phase": "STARTUP I (Pre-OS)", "Module": "Wdg", "Callout": "EcuM_AL_DriverInitOne", "File": "EcuM_Callout_Stubs.c:L260"},
    {"Phase": "STARTUP I (Pre-OS)", "Module": "StartOS", "Callout": "EcuM_Init", "File": "EcuM.c:L248"},
    {"Phase": "STARTUP II (Post-OS)", "Module": "SchM", "Callout": "EcuM_StartupTwo", "File": "EcuM.c:L271"},
    {"Phase": "STARTUP II (Post-OS)", "Module": "WdgM", "Callout": "EcuM_StartupTwo", "File": "EcuM.c:L276"},
    {"Phase": "STARTUP II (Post-OS)", "Module": "NvM (ReadAll)", "Callout": "EcuM_AL_DriverInitTwo", "File": "EcuM_Callout_Stubs.c:L349"},
    {"Phase": "STARTUP II (Post-OS)", "Module": "Can", "Callout": "EcuM_AL_DriverInitTwo", "File": "EcuM_Callout_Stubs.c:L368"},
    {"Phase": "STARTUP II (Post-OS)", "Module": "CanIf", "Callout": "EcuM_AL_DriverInitTwo", "File": "EcuM_Callout_Stubs.c:L373"},
    {"Phase": "STARTUP II (Post-OS)", "Module": "PduR", "Callout": "EcuM_AL_DriverInitTwo", "File": "EcuM_Callout_Stubs.c:L395"},
    {"Phase": "STARTUP II (Post-OS)", "Module": "Com", "Callout": "EcuM_AL_DriverInitTwo", "File": "EcuM_Callout_Stubs.c:L415"},
    {"Phase": "STARTUP II (Post-OS)", "Module": "Dem", "Callout": "EcuM_AL_DriverInitThree", "File": "EcuM_Callout_Stubs.c:L454"},
    {"Phase": "STARTUP II (Post-OS)", "Module": "ComM", "Callout": "EcuM_AL_DriverInitThree", "File": "EcuM_Callout_Stubs.c:L459"},
    {"Phase": "STARTUP II (Post-OS)", "Module": "Rte_Start", "Callout": "EcuM_StartupTwo", "File": "EcuM.c:L299"}
]

print("=== THỨ TỰ KHỞI TẠO BSW CHUẨN TRONG AUTOSAR ===")
for idx, item in enumerate(bsw_init_sequence, 1):
    print(f"{idx:02d}. [{item['Phase']}] {item['Module']:<15} -> Gọi tại: {item['Callout']} ({item['File']})")
```

---

### 2. 🔍 Giải Thích Bản Chất Kỹ Nghệ: Tại Sao `Mcu_Init` & `Port_Init` Phải Chạy Trước `Can_Init` & `Com_Init`?

Trong kiến trúc hệ thống nhúng ô tô, thứ tự khởi tạo này là **bắt buộc tuyệt đối (Strict Hardware & Layer Dependency)** do các lý do vật lý và phân tầng phần mềm sau:

```
┌────────────────────────────────────────────────────────────────────────────────────────────────┐
│                   CHUỖI PHỤ THUỘC KHỞI TẠO BẮT BUỘC TRONG AUTOSAR                              │
│                                                                                                │
│  [1. Mcu_Init]          [2. Port_Init]          [3. Can_Init / CanIf]       [4. Com_Init]      │
│  • Cấp xung Clock bus   • Chuyển chân sang AF   • Cấu hình Mailbox HTH/HRH  • Đóng gói Signal  │
│  • Khóa PLL định tần    • Đánh thức Transceiver • Cấu hình Bộ lọc Filter    • Quản lý I-PDU    │
│         │                      │                         │                         │           │
│         └──────────────────────┴─────────────────────────┴─────────────────────────┘           │
│              (Nếu đảo lộn thứ tự -> Gây Hard Fault Crash hoặc Bus-Off tức thì!)                │
└────────────────────────────────────────────────────────────────────────────────────────────────┘
```

#### 🅰️ Lý do 1: `Mcu_Init` phải chạy trước `Can_Init` (Cấp Xung Nhịp & Tránh Bus Fault)
1. **Tránh lỗi phần cứng Bus Fault / Hard Fault:**  
   Sau khi vi điều khiển bật nguồn (Reset), toàn bộ các module ngoại vi (CAN, UART, SPI, ADC) đều ở trạng thái **bị ngắt xung Clock (Clock Gating)** để tiết kiệm năng lượng.  
   Hàm `Mcu_Init()` / `Mcu_DistributePllClock()` (trong `arch/lm3s/mcal/Mcu.c: L124`) kích hoạt cấp xung cho bus ngoại vi (`SYSCTL_RCGC0_CAN0`).  
   *Nếu `Can_Init()` cố tình truy cập vào các thanh ghi điều khiển của CAN Controller trước khi `Mcu_Init` cấp Clock, CPU sẽ lập tức bị ngắt **Bus Fault / Hard Fault Exception** làm treo cứng hệ thống.*
2. **Khóa Tần Số PLL để tính Bit Timing chính xác:**  
   Module `Can_Init()` tính toán tốc độ truyền mạng CAN (Baudrate 500 kbps) dựa trên tần số xung nhịp cơ sở của vi điều khiển:
   $$	ext{Baudrate} = rac{f_{	ext{CAN\_Clock}}}{	ext{BRP} 	imes 	ext{TimeQuanta}}$$
   `Mcu_Init` phải cấu hình thạch anh và khóa tần số PLL ổn định (ví dụ 80 MHz hoặc 36 MHz). Nếu `Can_Init` chạy trước khi PLL sẵn sàng, các thanh ghi chia tần số BTR0/BTR1 sẽ bị tính sai lệch hoàn toàn, khiến ECU rơi vào trạng thái **Bus-Off** ngay khi vừa cắm lên xe!

---

#### 🅱️ Lý do 2: `Port_Init` phải chạy trước `Can_Init` (Mở Cổng Vật Lý & Kích Hoạt Transceiver)
1. **Cấu hình Pin Multiplexing & Alternate Function (AF):**  
   Mặc định sau Reset, các chân vật lý của vi điều khiển được đặt ở chế độ **GPIO Input High-Impedance hoặc Analog** để bảo vệ chống chập mạch.  
   `Port_Init()` cấu hình các thanh ghi dồn kênh chân (Pin Muxing) chuyển chân $CAN\_TX / CAN\_RX$ sang chế độ **Alternate Function Push-Pull/Open-Drain** kết nối nội bộ vào CAN Controller.  
   *Nếu `Can_Init` chạy trước, CAN Controller dù có được bật nhưng tín hiệu vẫn bị cô lập bên trong lõi chip, không thể truyền ra ngoài chân cắm.*
2. **Đánh thức Chip CAN Transceiver (STB/EN Control Pin):**  
   Trên bo mạch ECU ô tô thật, chip thu phát vật lý CAN Transceiver (như NXP TJA1043 hay TJA1050) có chân Standby (`STB`) nối tới 1 chân GPIO của MCU. Khi xe tắt máy, Transceiver ở chế độ Sleep để không hao bình ắc quy.  
   `Port_Init()` phải cấu hình chân GPIO này và kéo chân `STB` xuống mức 0 để đánh thức Transceiver sang **Normal Communication Mode** trước khi `Can_Init` bắt đầu phát gói tin.

---

#### 🅲 Lý do 3: `Can_Init` & `CanIf_Init` phải chạy trước `Com_Init` (Sẵn Sàng Driver Trước Khi Xử Lý Tín Hiệu)
1. **Quy tắc phân tầng từ Dưới lên Trên (Bottom-Up Driver Readiness):**  
   `Can_Init()` thiết lập chế độ làm việc và Mailbox phần cứng HTH/HRH. `CanIf_Init()` nạp bảng ánh xạ `CanIfTxPduId` sang HTH.  
   Sau khi 2 module này hoàn tất, tầng MCAL và Interface mới sẵn sàng nhận lệnh truyền.
2. **Ngăn ngừa lỗi mất gói tin khởi động (Init PDU Drop):**  
   `Com_Init()` nạp dữ liệu ban đầu cho các tín hiệu và sẵn sàng phát các gói tin khởi động chu kỳ (`COM_PERIODIC`).  
   *Nếu `Com_Init` chạy trước khi Can/CanIf được khởi tạo, tầng COM sẽ kích hoạt lệnh `PduR_ComTransmit()` $
ightarrow$ `CanIf_Transmit()`, lúc này CanIf chưa có bảng cấu hình HTH sẽ trả về `E_NOT_OK`, làm mất hoàn toàn các frame khởi động đầu tiên của xe.*

---

<a id="task-15"></a>
## 📊 LỜI GIẢI TASK 1.6: Tự Động Hóa Bóc Tách RTE Port Mapping
> 🎯 **Mục tiêu:** Viết script trích xuất toàn bộ các cổng giao tiếp `Rte_Write` / `Rte_Read` thực tế trong mã nguồn.

### 1. Kịch Bản PowerShell Trích Xuất Dữ Liệu Tự Động:

```powershell
$results = @()
Get-ChildItem -Path .s\coms.application\swc -Recurse -Include '*.c' | ForEach-Object {
    $file = $_.FullName
    $swc = $_.BaseName
    Select-String -Path $file -Pattern '(Rte_Read|Rte_Write|Rte_IRead|Rte_IWrite)_([a-zA-Z0-9_]+)' | ForEach-Object {
        $results += [PSCustomObject]@{
            SWC         = $swc
            Direction   = $_.Matches.Groups[1].Value
            Port_Signal = $_.Matches.Groups[2].Value
            File_Path   = $_.Path
            Line_Number = $_.LineNumber
        }
    }
}
$results | Format-Table -AutoSize
```

### 2. Bảng Kết Quả Trích Xuất Thực Tế 100% Từ Source Code:

| SWC Component | Chiều Giao Tiếp (Direction) | Tên Port / Signal | File Nguồn | Dòng |
| :--- | :--- | :--- | :--- | :---: |
| `Swc_Telltale` | `Rte_Write` | `Telltale_AirbagState` | `as/com/as.application/swc/telltale/Swc_Telltale.c` | L37 |
| `Swc_Telltale` | `Rte_Write` | `Telltale_AutoCruiseState` | `as/com/as.application/swc/telltale/Swc_Telltale.c` | L41 |
| `Swc_Telltale` | `Rte_Write` | `Telltale_HighBeamState` | `as/com/as.application/swc/telltale/Swc_Telltale.c` | L45 |
| `Swc_Telltale` | `Rte_Write` | `Telltale_LowOilState` | `as/com/as.application/swc/telltale/Swc_Telltale.c` | L49 |
| `Swc_Telltale` | `Rte_Write` | `Telltale_PosLampState` | `as/com/as.application/swc/telltale/Swc_Telltale.c` | L53 |
| `Swc_Telltale` | `Rte_Write` | `Telltale_SeatbeltDriverState` | `as/com/as.application/swc/telltale/Swc_Telltale.c` | L57 |
| `Swc_Telltale` | `Rte_Write` | `Telltale_SeatbeltPassengerState` | `as/com/as.application/swc/telltale/Swc_Telltale.c` | L61 |
| `Swc_Telltale` | `Rte_Write` | `Telltale_TPMSState` | `as/com/as.application/swc/telltale/Swc_Telltale.c` | L65 |
| `Swc_Telltale` | `Rte_Write` | `Telltale_TurnLeftState` | `as/com/as.application/swc/telltale/Swc_Telltale.c` | L69 |
| `Swc_Telltale` | `Rte_Write` | `Telltale_TurnRightState` | `as/com/as.application/swc/telltale/Swc_Telltale.c` | L73 |
