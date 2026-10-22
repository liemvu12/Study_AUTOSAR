# CHUYÊN ĐỀ 02: AUTOSAR OS (OSEK/VDX Standard) & MCAL Core Deep Dive
## HANDS-ON TASK PLAN — 8 Tasks (~24 giờ thực hành)

> 📚 **Tài liệu lý thuyết đối chiếu:** [`docs/theory/02_AUTOSAR_OS_And_MCAL_Deep_Dive.md`](../theory/02_AUTOSAR_OS_And_MCAL_Deep_Dive.md)  
> 💡 **Bộ Lời Giải Mẫu Chi Tiết (Full Working Solutions):** [`docs/hands_on_tasks/solutions/02_OS_MCAL_Solutions.md`](solutions/02_OS_MCAL_Solutions.md)  
> 📜 **Quy tắc vàng & Nguồn chân lý (Golden Rules):** [`docs/hands_on_tasks/task_fix/rule.md`](task_fix/rule.md) (File ARXML là nguồn chân lý duy nhất)  
> 🔧 **Source code base:** [`as/com/as.infrastructure/system/kernel/`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/com/as.infrastructure/system/kernel/), [`as/com/as.infrastructure/arch/`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/com/as.infrastructure/arch/) & [`as/com/as.infrastructure/include/IoHwAb.h`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/com/as.infrastructure/include/IoHwAb.h)  
> ⏱️ **Tổng thời lượng:** ~24 giờ (Phân cấp từ Nhập môn $\rightarrow$ Trung cấp $\rightarrow$ Chuyên sâu)  

---

## 🎯 BẢNG ĐÁNH GIÁ TRỌNG SỐ & LỘ TRÌNH DÀNH CHO KỸ SƯ BASIC SOFTWARE (BSW ENGINEER)

> 💡 **Lời khuyên từ Principal AUTOSAR Architect:**  
> Trong kỹ nghệ ô tô tiêu chuẩn (Vector DaVinci, EB Tresos, hay ArGen của dự án `as`), **File ARXML/XML là Nguồn Chân Lý Duy Nhất (Single Source of Truth)**.  
> Cú pháp OIL (*OSEK Implementation Language*) chỉ là ngôn ngữ cổ điển của OSEK thập niên 90 mang tính tham khảo học thuật. Trong mọi bài tập thực chiến dưới đây, kỹ sư sẽ tuân thủ nghiêm ngặt **Quy trình 4 Bước Chuẩn OEM/Tier-1**:  
> **1. Khai báo thiết kế trong `autosar.arxml` $\longrightarrow$ 2. Chạy `scons` để ArGen sinh mã tự động $\longrightarrow$ 3. Verify đối soát trong `build/.../config/Os_Cfg.h` $\longrightarrow$ 4. Cài đặt thuật toán C trong tầng ứng dụng (`app.c`).**

### 📊 Ma Trận Trọng Số & Mức Độ Ưu Tiên (BSW Priority Matrix)

| Task | Tên Nhiệm Vụ | Mức Độ | Trọng Số BSW | Lý Do Kỹ Nghệ & Kỹ Năng Cốt Lõi |
| :--- | :--- | :--- | :---: | :--- |
| **Task 2.1** | **Build OSEK OS từ Source Code & Khảo Sát Kernel APIs** | 🟢 **Dễ (P1)** | **10%** | **Làm chủ Toolchain & Khởi động:** Nắm vững cấu trúc mã nguồn Kernel (`freeosek`, `trampoline`, `askar`), làm chủ quy trình biên dịch với SCons trên POSIX Simulator và QEMU ARM Cortex-M3. |
| **Task 2.2** | **MCAL Power-On Sequencing & Hardware Dependency** | 🟡 **Vừa (P1)** | **15%** | **Sống còn khi Bring-up bo mạch mới:** Hiểu và hiện thực hóa chuỗi phụ thuộc phần cứng bắt buộc: `Mcu` (Clock/PLL) $\rightarrow$ `Wdg` (Watchdog) $\rightarrow$ `Port` (PinMux) $\rightarrow$ `Dio` (GPIO). Tránh lỗi truy cập ngoại vi khi chưa cấp xung nhịp. |
| **Task 2.3** | **Basic Task Định Kỳ & Khảo Sát Conformance Classes (BCC1 vs BCC2)** | 🟢 **Dễ $\rightarrow$ Vừa (P2)** | **10%** | **Tối ưu hóa RAM & Hàng đợi Kích hoạt:** Cấu hình `<Task>` & `<Alarm>` trong `app.xml`, đối soát `Os_Cfg.h`, phân biệt Single Activation (`Activation="1"`) và Multiple Activations (`Activation="3"`). |
| **Task 2.4** | **Extended Task Event-Driven & Đối Chiếu Ngắt ISR Cat 1 vs Cat 2** | 🟡 **Vừa (P1)** | **15%** | **Đồng bộ hướng sự kiện & Phân cấp ngắt:** Khai báo Extended Task kèm `<Event>` trong `app.xml`, đối soát `EVENT_MASK_*` & `EXTENDED_TASK`, lập trình vòng lặp 4 bước `WaitEvent`/`GetEvent`/`ClearEvent`, kiểm chứng tiếm quyền khi mô phỏng ISR Cat 2 gọi `SetEvent`, mổ xẻ ngắt siêu tốc Cat 1 vs ngắt đồng bộ OS Cat 2. |
| **Task 2.5** | **Immediate Priority Ceiling (IPCP) & Chứng Minh Không Context Switch** | 🟡 **Vừa $\rightarrow$ Khó (P1)** | **15%** | **Triệt tiêu Deadlock & Hiểu sâu về Assembly:** Khai báo `<Resource>` trong ARXML, chứng minh Resource trong AUTOSAR luôn rảnh khi gọi `GetResource()`, thời gian thực thi $O(1)$, Context Switch chỉ diễn ra tại `ReleaseResource()`. |
| **Task 2.6** | **Schedule Table — Định Thời Đồng Bộ Đa Chu Kỳ BSW** | 🔴 **Khó (P2)** | **10%** | **Triệt tiêu Jitter trong mạng ô tô:** Thay thế hàng chục Alarm rời rạc bằng một Schedule Table duy nhất, phân bổ các Expiry Point đồng bộ cho các BSW `_MainFunction()` (10ms, 20ms, 50ms). |
| **Task 2.7** | **Bảo Vệ Bộ Nhớ & Bắt Lỗi Hệ Thống: Stack Watermark + ErrorHook & DET** | 🔴 **Khó (P2)** | **10%** | **An toàn chức năng ISO 26262:** Bật `ErrorHook` và `PostTaskHook` trong ARXML, dùng kỹ thuật Pattern Fill (`0xDEADBEEF`) phát hiện tràn ngăn xếp, bẫy lỗi hệ thống qua `ErrorHook` và `Det_ReportError`. |
| **Task 2.8** | **Hand-Coded `IoHwAb` Driver — Đọc ADC Thô, Lọc Số IIR, Cầu Phân Áp & Kích Relay/PWM** | 🔴 **Khó (P1)** | **15%** | **Cầu nối sống còn giữa Phần cứng & Ứng dụng:** Viết mã nguồn C tay 100% cho tầng `IoHwAb` bám sát [`IoHwAb.h`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/com/as.infrastructure/include/IoHwAb.h) & [`IoHwAb_Types.h`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/com/as.infrastructure/include/IoHwAb_Types.h), chuyển đổi ADC thô sang mV, lọc số chống nhiễu EMC, điều khiển Contactor/Relay và mở API chuẩn cho RTE/SWC. |

---

### 🗺️ Lộ Trình Học Tập Đề Xuất Cho Kỹ Sư:
1. **Giai đoạn 1 (Làm chủ Nền tảng & Bring-up):** Hoàn thành **Task 2.1 $\rightarrow$ Task 2.2** (Làm quen hệ điều hành và trình tự kích hoạt phần cứng).
2. **Giai đoạn 2 (Quản trị Tác vụ & Tài nguyên Hệ thống):** Hoàn thành **Task 2.3 $\rightarrow$ Task 2.4 $\rightarrow$ Task 2.5** (Nắm vững Basic/Extended Task, ISR và cơ chế IPCP).
3. **Giai đoạn 3 (Định thời Cấp cao, An toàn & Bắt lỗi):** Hoàn thành **Task 2.6 $\rightarrow$ Task 2.7** (Làm chủ Schedule Table và các kỹ thuật bảo vệ bộ nhớ chuẩn ASIL-D).

---

## 🛠️ CẤU TRÚC CHI TIẾT 7 BÀI TẬP THỰC HÀNH

---

### TASK 2.1: Build OSEK OS từ Source Code & Khảo Sát Kernel APIs (🟢 Dễ — ~2h)

#### 🎯 Mục tiêu:
Biên dịch thành công mã nguồn hệ điều hành từ thư mục gốc, khảo sát cấu trúc thư mục Kernel và đối chiếu các API tiêu chuẩn OSEK OS / AUTOSAR OS trên môi trường POSIX Simulator và QEMU ARM Cortex-M3.

#### 📖 Kiến thức cốt lõi:
- Hệ điều hành AUTOSAR OS trong dự án `as` được xây dựng dựa trên tiêu chuẩn **OSEK/VDX OS 2.2.3** và đặc tả **AUTOSAR OS SWS 4.x**.
- Mã nguồn Kernel nằm tại: [`as/com/as.infrastructure/system/kernel/`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/com/as.infrastructure/system/kernel/) (bao gồm `freeosek`, `trampoline`, `askar`).
- Các nhóm API cơ bản cần phân tích:
  1. **Quản lý Task:** `ActivateTask()`, `TerminateTask()`, `ChainTask()`, `GetTaskID()`, `GetTaskState()`.
  2. **Quản lý Tài nguyên (Resource):** `GetResource()`, `ReleaseResource()`.
  3. **Quản lý Sự kiện (Event):** `SetEvent()`, `ClearEvent()`, `GetEvent()`, `WaitEvent()`.
  4. **Kiểm soát Hệ thống:** `StartOS()`, `ShutdownOS()`.

#### 📋 Hướng dẫn từng bước:
1. **Biên dịch trên PC POSIX Simulator:**
   Mở PowerShell hoặc Bash tại thư mục `as/`:
   ```bash
   cd as
   scons --board=posix
   ```
2. **Biên dịch cho mục tiêu QEMU ARM Cortex-M3 (Board `lm3s6965evb`):**
   ```powershell
   $env:BOARD="lm3s6965evb"
   $env:RELEASE="ascore"
   scons
   ```
3. **Khảo sát mã nguồn thực tế:**
   - Mở file [`Os.h`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/com/as.infrastructure/include/Os.h) và [`as/com/as.infrastructure/system/kernel/freeosek/src/GetResource.c`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/com/as.infrastructure/system/kernel/freeosek/src/GetResource.c).
   - Tìm kiếm định nghĩa các mã trả về chuẩn: `E_OK`, `E_OS_ACCESS`, `E_OS_ID`, `E_OS_LIMIT`, `E_OS_RESOURCE`.

#### ✅ Tiêu chí thành công:
- Lệnh `scons` hoàn tất mà không báo lỗi, sinh ra file thực thi `./build/posix/as` (hoặc `ascore.elf` cho board QEMU).
- Kỹ sư giải thích được vai trò của 4 nhóm API lõi và chỉ ra được vị trí file `Os.h` trong dự án.

---

### TASK 2.2: MCAL Power-On Sequencing & Hardware Dependency (🟡 Vừa — ~2.5h)

#### 🎯 Mục tiêu:
Hiểu rõ và hiện thực hóa chuỗi khởi tạo phần cứng theo chuẩn **EcuM Driver Init List One**, bóc tách mối quan hệ phụ thuộc lẫn nhau giữa các module ngoại vi vi điều khiển: **`Mcu` $\rightarrow$ `Wdg` $\rightarrow$ `Port` $\rightarrow$ `Dio`**.

#### 📖 Kiến thức cốt lõi:
- **Nguyên lý Clock Gating:** Một module ngoại vi (GPIO, Timer, CAN) mặc định bị ngắt xung clock để tiết kiệm điện. Nếu đọc/ghi thanh ghi của nó trước khi `Mcu` cấp xung nhịp, CPU sẽ phát sinh lỗi **Bus Fault / HardFault**.
- **Nguyên lý PinMux (Port vs Dio):** Thanh ghi của khối `Dio` chỉ điều khiển mức logic (High/Low) tại đầu ra/vào. Để chân vi điều khiển thực sự hoạt động như một chân GPIO, khối `Port` phải chạy trước để cấu hình chức năng chân (GPIO Mode, Pull-up, Output Push-Pull).
- **Trình tự bắt buộc:**
  $$\mathbf{Mcu\_Init()} \longrightarrow \mathbf{Mcu\_InitClock()} \longrightarrow \mathbf{Wdg\_Init()} \longrightarrow \mathbf{Port\_Init()} \longrightarrow \mathbf{Dio\_Init()}$$

#### 📋 Hướng dẫn từng bước:
1. Khảo sát mã nguồn driver MCU tại: [`as/com/as.infrastructure/arch/lm3s/mcal/Mcu.c`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/com/as.infrastructure/arch/lm3s/mcal/Mcu.c) hoặc [`arch/posix/mcal/Dio.c`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/com/as.infrastructure/arch/posix/mcal/Dio.c).
2. Viết một hàm khởi tạo phần cứng hoàn chỉnh `EcuM_AL_DriverInitOne()` mô phỏng quy trình khởi tạo ECU thực tế:
   - Bước 1: Gọi `Mcu_Init(&McuModuleConfiguration)`.
   - Bước 2: Gọi `Mcu_InitClock(0)` và chờ vòng lặp kiểm tra `Mcu_GetPllStatus() == MCU_PLL_LOCKED`.
   - Bước 3: Phân phối xung nhịp bằng `Mcu_DistributePllClock()`.
   - Bước 4: Gọi `Wdg_Init(&WdgConfigData)` để bật Watchdog bảo vệ phần cứng.
   - Bước 5: Gọi `Port_Init(&PortConfigData)` để định tuyến các chân LED và Nút nhấn.
   - Bước 6: Gọi `Dio_WriteChannel(LED_CHANNEL, STD_LOW)` để bật đèn báo ECU Boot thành công.

#### 💻 Khung mã nguồn mẫu (Scaffold Code):
```c
#include "Mcu.h"
#include "Port.h"
#include "Dio.h"
#include <stdio.h>

void EcuM_AL_DriverInitOne(void)
{
    printf("[ECUM BOOT] Step 1: Initializing MCU Driver...\n");
    Mcu_Init(&McuModuleConfiguration);

    printf("[ECUM BOOT] Step 2: Initializing System Clock & PLL...\n");
    if (Mcu_InitClock(McuClockSettingConfig_0) == E_OK)
    {
        while (Mcu_GetPllStatus() != MCU_PLL_LOCKED)
        {
            /* Chờ khóa pha PLL ổn định */
        }
        Mcu_DistributePllClock();
        printf("[ECUM BOOT] System Clock is locked and distributed!\n");
    }

    printf("[ECUM BOOT] Step 3: Initializing Pin Multiplexer (Port)...\n");
    Port_Init(&Port_Config);

    printf("[ECUM BOOT] Step 4: Accessing Digital I/O (Dio)...\n");
    Dio_WriteChannel(DIO_CHANNEL_LED_STATUS, STD_HIGH);
    printf("[ECUM BOOT] Boot sequence finished safely. Ready for StartOS()!\n");
}
```

#### ✅ Tiêu chí thành công:
- Mã nguồn biên dịch thành công và in ra log theo đúng trình tự phân cấp từ thấp lên cao.
- Người học giải thích được: Tại sao không thể gọi `Dio_Init()` trước `Port_Init()`, và điều gì xảy ra ở mức phần cứng nếu bỏ qua `Mcu_DistributePllClock()`.

---

### TASK 2.3: Basic Task Định Kỳ & Khảo Sát Conformance Classes (BCC1 vs BCC2) (🟢 Dễ $\rightarrow$ 🟡 Vừa — ~3h)

#### 🎯 Mục tiêu:
1. Thiết lập một **Basic Task** thực thi định kỳ mỗi 50ms bằng **Alarm** thông qua quy trình cấu hình **ARXML $\rightarrow$ Code Gen $\rightarrow$ Verify**.
2. Thực nghiệm so sánh giữa hai cấp độ tuân thủ: **BCC1** (`Activation="1"`) và **BCC2** (`Activation="3"` với hàng đợi kích hoạt), quan sát mã lỗi hệ thống `E_OS_LIMIT`.

#### 📖 Kiến thức cốt lõi:
- **Quy tắc Nguồn chân lý (Rule 2):** Mọi Task và Alarm phải được mô hình hóa trong tệp XML/ARXML trước khi sinh mã. Với tác vụ tầng ứng dụng trong Task 2.3, tệp nguồn chân lý duy nhất được quy định là [`as/release/ascore/app/app.xml`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/release/ascore/app/app.xml).
- **BCC1 (Basic Conformance Class 1):** Mỗi Task chỉ được phép có tối đa 1 kích hoạt (`Activation="1"`). Nếu gọi `ActivateTask()` khi Task chưa chạy xong, OS sẽ trả về lỗi `E_OS_LIMIT`.
- **BCC2 (Basic Conformance Class 2):** Cho phép `Activation > 1`. Các yêu cầu kích hoạt được đưa vào **Activation Queue**.

> 💡 **Quyết định Thiết kế & Phân Tầng Kiến Trúc (Architecture Separation of Concerns):**  
> - **Nguyên lý:** Task ứng dụng (`Task_Periodic_50ms`, `Task_QueueTester`) tuyệt đối không được làm "ô nhiễm" (*pollution*) tệp khung xương BSW dùng chung ([`autosar.arxml`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/com/as.application/common/autosar.arxml)), nơi vốn chỉ dành cho tác vụ hạ tầng như `SchM_Startup`, `SchM_BswService`.  
> - **Quy chuẩn thực thi chuẩn mực duy nhất:** Toàn bộ cấu hình Task và Alarm của Task 2.3 được định nghĩa trực tiếp trong tệp cấu hình tầng Ứng Dụng: [`as/release/ascore/app/app.xml`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/release/ascore/app/app.xml), tương ứng 1-1 với file mã nguồn C [`as/release/ascore/app/app.c`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/release/ascore/app/app.c).  
> - Toolchain ArGen (`GenOS.py`) sử dụng cơ chế *Multi-file XML Aggregation* tự động quét gom cả `autosar.arxml` và `app.xml` để sinh ra cấu hình OS chuẩn xác.  
> *(Xem phân tích chi tiết tại [Mục 5 trong Báo cáo Task 2.3](task_fix/03_task_2_3_basic_task_alarm_bcc_configuration/README.md#5--phân-tích-kiến-trúc-tại-sao-đặt-chung-vào-autosararxml-với-schm_startup-có-chỗ-nào-thích-hợp-hơn-không)).*

#### 📋 Quy trình 4 bước thực hiện:

##### Bước 1: Khai báo Task & Alarm Trong Tệp Cấu Hình Ứng Dụng `app.xml`

Mở file [`as/release/ascore/app/app.xml`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/release/ascore/app/app.xml), tìm đến khối `<AS><Os>` và bổ sung 2 Task cùng 1 Alarm trực tiếp bên cạnh `TaskApp` và `AlarmApp`:

```xml
<!-- ================= TASK 2.3: BASIC TASK & ALARM ================= -->
<!-- Thử nghiệm 1 (BCC1): Đặt Activation="1" -->
<!-- Thử nghiệm 2 (BCC2): Đổi thành Activation="3" -->
<Task Name="Task_Periodic_50ms"  
    Activation="1" 
    Autostart="False" 
    Priority="2" 
    Schedule="FULL" 
    StackSize="512"
    Application="OsDefaultApp"
    Comment="*" />

<Task Name="Task_QueueTester"  
    Activation="1" 
    Autostart="True" 
    Priority="5" 
    Schedule="FULL" 
    StackSize="512"
    Application="OsDefaultApp"
    Comment="*" >
    <ApplicationModeList Max="TBD">
        <ApplicationMode Comment="*" Name="OSDEFAULTAPPMODE" />
    </ApplicationModeList>
</Task>

<Alarm Name="Alarm_Periodic_50ms" 
    Autostart="True" 
    Period="50" 
    StartTime="50" 
    Counter="OsClock" 
    Action="ActivateTask" 
    Task="Task_Periodic_50ms" 
    Event="TBD" 
    Callback="TBD" 
    Application="OsDefaultApp" 
    Comment="*" >
    <ApplicationModeList Max="TBD">
        <ApplicationMode Comment="*" Name="OSDEFAULTAPPMODE" />
    </ApplicationModeList>
</Alarm>
```

##### Bước 2: Sinh mã tự động với SCons
Tại thư mục `as/`, chạy lệnh:
```bash
scons
```
Công cụ sinh mã ArGen (`GenOS.py`) sẽ nạp và gộp đa tệp cấu hình XML (`autosar.arxml` + `app.xml`) thông qua cơ chế *Multi-file XML Aggregation* và tự động cập nhật các file trong `build/.../config/`.

##### Bước 3: Verify đối soát trong `Os_Cfg.h`
Mở file `build/nt/<board>/ascore/config/Os_Cfg.h`, kiểm tra sự xuất hiện của các định nghĩa tự động:
```c
/* =================== [ CHECK VERIFY OUTPUT ] =================== */
#define TASK_ID_Task_Periodic_50ms   <ID_Number>
#define TASK_ID_Task_QueueTester     <ID_Number>
#define ALARM_ID_Alarm_Periodic_50ms <ID_Number>
```

##### Bước 4: Viết mã nguồn ứng dụng C (`app.c`)
```c
#include "Os.h"
#include <stdio.h>

static uint32_t execution_count = 0;

TASK(Task_Periodic_50ms)
{
    execution_count++;
    printf("[BASIC TASK] Executing instance #%u\n", execution_count);
    TerminateTask();
}

TASK(Task_QueueTester)
{
    StatusType ret;
    printf("\n[TESTER] Activating Task_Periodic_50ms (Call 1)...\n");
    ret = ActivateTask(Task_Periodic_50ms);
    printf("--> Result 1: %s\n", (ret == E_OK) ? "E_OK" : "ERROR");

    printf("[TESTER] Activating Task_Periodic_50ms (Call 2)...\n");
    ret = ActivateTask(Task_Periodic_50ms);
    if (ret == E_OS_LIMIT) {
        printf("--> Result 2: E_OS_LIMIT (BCC1 Reached! Activation limit = 1)\n");
    } else if (ret == E_OK) {
        printf("--> Result 2: E_OK (BCC2 Queued successfully!)\n");
    }

    TerminateTask();
}
```

##### Bước 5: Chạy kiểm thử trên máy ảo QEMU ARM Cortex-M3
Tại thư mục `as/`, chạy lệnh mô phỏng với tham số đa hợp cổng Serial `mon:stdio` (để tránh xung đột console trên Windows):
```powershell
qemu-system-arm -M lm3s6965evb -kernel build/nt/lm3s6965evb/ascore/lm3s6965evb.exe -nographic -serial mon:stdio
```
*(Thoát QEMU bất kỳ lúc nào: Nhấn `Ctrl + A` rồi nhấn `X`)*.

#### ✅ Tiêu chí thành công:
- File `Os_Cfg.h` được sinh ra tự động đúng với khai báo trong ARXML.
- Console in ra đúng mã lỗi `E_OS_LIMIT` khi `Activation="1"` và `E_OK` khi tăng lên `Activation="3"`.
- Sau khi `Task_QueueTester` hoàn thành, `Alarm_Periodic_50ms` tự động kích hoạt `Task_Periodic_50ms` định kỳ mỗi 50ms (instance #1, #2, #3...).

---

### TASK 2.4: Extended Task Event-Driven & Đối Chiếu Ngắt ISR Cat 1 vs Cat 2 (🟡 Vừa — ~3.5h)

#### 🎯 Mục tiêu:
1. Lập trình **Extended Task** (`Task_CanRxHandler`) hướng sự kiện với `<Event>` khai báo chuẩn xác trong [`as/release/ascore/app/app.xml`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/release/ascore/app/app.xml), sử dụng cơ chế ngủ giải phóng CPU (`WaitEvent()`) và thức dậy xử lý tin nhắn khi nhận sự kiện.
2. Nắm vững chu trình 4 bước bắt buộc của Extended Task: `WaitEvent` $\rightarrow$ `GetEvent` $\rightarrow$ `ClearEvent` $\rightarrow$ Dispatch, hiểu rõ cạm bẫy 100% CPU Lockup nếu quên xóa cờ sự kiện.
3. Thực thi kiểm chứng trực tiếp trên QEMU với hàm mô phỏng ngắt ISR Cat 2 gọi `SetEvent()`, quan sát hiện tượng tiếm quyền (preemption) tức thì của Task ưu tiên cao từ trạng thái `WAITING` $\rightarrow$ `READY` $\rightarrow$ `RUNNING`.
4. Phân tích sự khác biệt kiến trúc giữa **ISR Category 1** (Trỏ trực tiếp Vector Table, không qua OS, cấm gọi OS API) và **ISR Category 2** (Được bọc bởi OS Wrapper, quản lý Stack Frame, cho phép gọi `SetEvent()`).

> 💡 **Quyết định kiến trúc & Single Source of Truth (`app.xml` vs `autosar.arxml`):**  
> Tương tự như Task 2.3, `Task_CanRxHandler` là tác vụ tầng Ứng dụng (Application Layer). Do đó, **nơi cấu hình duy nhất là [`as/release/ascore/app/app.xml`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/release/ascore/app/app.xml)**, tuyệt đối không can thiệp vào `autosar.arxml` (vốn là cấu hình chuẩn cho các dịch vụ nền tảng BSW Core). Bộ sinh mã ArGen của `as` sẽ tự động gom toàn bộ các thẻ `<Os>` từ cả hai file XML vào một không gian cấu hình thống nhất khi build.

#### 📋 Quy trình 5 bước thực hiện:

##### Bước 1: Khai báo Extended Task trong `app.xml`
Mở [`as/release/ascore/app/app.xml`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/release/ascore/app/app.xml) và thêm thẻ `<Task>` định nghĩa `Task_CanRxHandler` cùng thẻ con `<EventList>`:

```xml
		<!-- ================= TASK 2.4: EXTENDED TASK & EVENTS ================= -->
		<Task Name="Task_CanRxHandler"  
	    		Activation="1" 
				Autostart="True" 
				Priority="10" 
				Schedule="FULL" 
				StackSize="2048"
				Application="OsDefaultApp"
	     		Comment="*" >
			<ApplicationModeList Max="TBD">
				<ApplicationMode Comment="*" Name="OSDEFAULTAPPMODE" />
			</ApplicationModeList>
			<EventList Max="32">
				<Event Comment="*" Mask="0x01" Name="Event_CanFrameRx" />
				<Event Comment="*" Mask="0x02" Name="Event_CanError" />
			</EventList>
		</Task>
```

> 🔍 **Giải mã các thông số kiến trúc:**
> - `Activation="1"`: **Bắt buộc** đối với Extended Task theo chuẩn OSEK/AUTOSAR. Extended Task không hỗ trợ hàng đợi kích hoạt đa trọng (Multiple Activations) vì task sở hữu trạng thái `WAITING` với ngữ cảnh và stack riêng biệt.
> - `StackSize="2048"`: Cần Dedicated Stack riêng. Khác với Basic Task có thể chia sẻ stack, Extended Task khi bị block trong `WaitEvent()` vẫn phải lưu giữ nguyên vẹn con trỏ khung gọi hàm (Call Frame) và các biến cục bộ.
> - `Priority="10"`: Đặt độ ưu tiên cao hơn các tác vụ hiện có (`TaskApp` = 5, `Task_Periodic_50ms` = 2, `SchM_BswService` = 8) để khi nhận sự kiện, task lập tức tiếm quyền (preempt) thực thi ngay lập tức.
> - `Autostart="True"`: Cho phép task tự động chạy một lần lúc khởi động hệ thống để hoàn tất thiết lập ban đầu và chủ động gọi `WaitEvent()` đưa task vào trạng thái `WAITING`.

##### Bước 2: Chạy SCons sinh mã tự động
Mở PowerShell tại thư mục `as/` và chạy:
```powershell
scons
```

##### Bước 3: Verify đối soát trong `Os_Cfg.h` và `Os_Cfg.c`
Mở `as/build/nt/lm3s6965evb/ascore/config/Os_Cfg.h` và `Os_Cfg.c` để đối soát kết quả sinh mã từ ArGen:
```c
/* Tự động bật chế độ hỗ trợ Extended Task khi phát hiện có <EventList> */
#define EXTENDED_TASK

/* ID Task và Macro Event Mask */
#define TASK_ID_Task_CanRxHandler                       8   /* priority = 10 */
#define EVENT_MASK_Task_CanRxHandler_Event_CanFrameRx   0x01
#define EVENT_MASK_Task_CanRxHandler_Event_CanError     0x02

/* Khai báo Event trong Os_Cfg.c */
const EventMaskType Event_CanFrameRx = EVENT_MASK_Task_CanRxHandler_Event_CanFrameRx;
const EventMaskType Event_CanError   = EVENT_MASK_Task_CanRxHandler_Event_CanError;
```

##### Bước 4: Viết mã nguồn C ứng dụng (`app.c`)
Mở [`as/release/ascore/app/app.c`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/release/ascore/app/app.c) và cài đặt vòng lặp sự kiện chuẩn mực kèm bộ kiểm chứng mô phỏng ISR Cat 2:

```c
/* ========================================================================= */
/* TASK 2.4: Extended Task Event-Driven & ISR Cat 1 vs Cat 2 Verification    */
/* ========================================================================= */
static volatile uint32_t rx_can_message_id = 0;

/* Chu trình 4 bước chuẩn mực của Extended Task */
TASK(Task_CanRxHandler)
{
	EventMaskType active_events;
	printf("[Task_CanRxHandler] Initialized (Prio 10). Calling WaitEvent()...\n");

	while (1)
	{
		/* BƯỚC 1: Ngủ giải phóng 100% CPU, chuyển sang trạng thái WAITING */
		(void)WaitEvent(Event_CanFrameRx | Event_CanError);

		/* BƯỚC 2: Thức dậy khi có Event, đọc mask sự kiện đã được kích hoạt */
		(void)GetEvent(Task_CanRxHandler, &active_events);

		/* BƯỚC 3: XÓA CỜ SỰ KIỆN — CỰC KỲ QUAN TRỌNG ĐỂ TRÁNH 100% CPU LOCKUP! */
		(void)ClearEvent(active_events);

		/* BƯỚC 4: Xử lý nghiệp vụ tương ứng */
		if (active_events & Event_CanFrameRx)
		{
			printf("   --> [Task_CanRxHandler] WAKEUP from WAITING state!\n");
			printf("   --> [Task_CanRxHandler] CAN Rx Frame processed: ID = 0x%X\n", (unsigned int)rx_can_message_id);
		}
		if (active_events & Event_CanError)
		{
			printf("   --> [Task_CanRxHandler] CAN Bus Error handled!\n");
		}
	}
	(void)TerminateTask();
}

/* Hàm kiểm chứng mô phỏng hành vi ISR Cat 2 (Được OS quản lý, gọi SetEvent) */
void Simulate_ISR_CanRx_Cat2(uint32_t can_id)
{
	printf("\n[ISR Cat 2 Simulation] CAN Rx Interrupt Triggered! ID = 0x%X\n", (unsigned int)can_id);
	rx_can_message_id = can_id;
	
	/* Kích hoạt Event đánh thức Task_CanRxHandler */
	printf("[ISR Cat 2 Simulation] Calling SetEvent(Task_CanRxHandler, Event_CanFrameRx)...\n");
	(void)SetEvent(Task_CanRxHandler, Event_CanFrameRx);
	printf("[ISR Cat 2 Simulation] Interrupt Handler completed.\n\n");
}

/* Mẫu định nghĩa ISR Cat 1: Trỏ trực tiếp Vector Table, TUYỆT ĐỐI CẤM gọi OS API */
ISR(ISR_Hardware_FastTimer)
{
	/* Chỉ thực hiện thao tác phần cứng siêu tốc (< 1 microsecond) */
	/* CẤM GỌI SetEvent() hoặc bất kỳ OS API nào tại đây! */
}
```

> ⚠️ **Cảnh báo lỗi Kỹ thuật kinh điển (Must-Know Pitfall):**  
> Nếu kỹ sư quên gọi `ClearEvent(active_events)` ở Bước 3, cờ sự kiện trong TCB (Task Control Block) vẫn giữ nguyên giá trị `1`. Khi vòng lặp quay lại gọi `WaitEvent()`, Kernel kiểm tra thấy sự kiện vẫn đang pending nên **không đưa task vào trạng thái WAITING** mà trả về ngay lập tức!  
> Hậu quả: `Task_CanRxHandler` (Priority 10) sẽ chạy vòng lặp `while(1)` vô tận ở tần số tối đa, chiếm đoạt 100% thời gian CPU và bỏ đói (Starvation) toàn bộ các task thấp hơn, dẫn đến Watchdog reset hệ thống!

##### Bước 5: Chạy kiểm chứng trên QEMU với cờ `-serial mon:stdio`
```powershell
qemu-system-arm -M lm3s6965evb -kernel build/nt/lm3s6965evb/ascore/lm3s6965evb.exe -nographic -serial mon:stdio
```
*(Thoát QEMU: Nhấn tổ hợp phím `Ctrl + A` rồi bấm `X`)*

#### ✅ Tiêu chí thành công:
1. `Task_CanRxHandler` khởi động thành công với Priority 10, in thông điệp khởi tạo rồi chuyển sang trạng thái `WAITING`, nhường CPU cho các task có mức ưu tiên thấp hơn (`Task_QueueTester`, `Task_Periodic_50ms`, `TaskApp`).
2. Khi gọi `Simulate_ISR_CanRx_Cat2()`, `SetEvent()` lập tức đánh thức `Task_CanRxHandler` chuyển từ `WAITING` $\rightarrow$ `READY` $\rightarrow$ tiếm quyền CPU sang `RUNNING`.
3. Extended Task xử lý thành công tin nhắn CAN ID `0x180`, gọi `ClearEvent()` dọn dẹp cờ và an toàn quay lại trạng thái `WAITING`.
4. Kỹ sư giải thích được nguyên nhân sâu xa ở tầng Hợp ngữ vì sao ISR Category 1 bị nghiêm cấm gọi OS API ("The Cat 1 Catastrophe").

#### 💡 CÂU HỎI PHỎNG VẤN KIẾN TRÚC SƯ BSW (Architect Interview — Phiên Bản Trả Lời Ngắn Gọn 45 Giây):
> ❓ **Câu hỏi:** *"Tại sao không thiết kế 100% ngắt thành Cat 1 để hệ thống siêu nhanh? Vì sao bắt buộc phải có Cat 2?"*

#### 🎯 Câu Trả Lời Chuẩn Mực (3 Điểm Cốt Tử):
Thiết kế 100% Cat 1 là sai lầm vì **Cat 1 chỉ nhanh lúc vào ngắt, nhưng phá nát hệ thống thời gian thực** do 3 lý do cốt tử:

1. **Không thể đánh thức Task (Mất mô hình Top-Half / Bottom-Half):**
   - Cat 1 bị cấm gọi OS API (`SetEvent`, `ActivateTask`).
   - Nếu dùng Cat 1, kỹ sư buộc phải ôm toàn bộ logic nặng (ComStack, CRC, tính toán) vào trong ngắt gây **nghẽn CPU, tăng Jitter và bỏ đói các ngắt khác**; hoặc phải dùng cờ Polling **lãng phí 30–50% CPU**.
   - *Cat 2 giải quyết:* Ngắt Cat 2 chỉ làm việc nhẹ 2µs rồi gọi `SetEvent` giao việc nặng lại cho Task chạy dưới quyền Scheduler.
2. **Không thể tiếm quyền đổi Task khi thoát ngắt (Mất Immediate Preemption):**
   - Cat 1 thoát ngắt (`bx lr`) **bắt buộc phải quay về Task cũ đang chạy dở** (dù đó là Task Idle).
   - *Cat 2 giải quyết:* Hàm bọc `ExitISR` kiểm tra và **lập tức chuyển quyền sang Task ưu tiên cao hơn** (ví dụ: Task Phanh khẩn cấp vừa nhận tín hiệu) mà không cần đợi Task cũ chạy xong.
3. **Lãng phí RAM Stack (Stack Bloat):**
   - Cat 1 chạy trực tiếp trên ngăn xếp của Task bị ngắt, khiến mọi Task đều phải phình to kích thước Stack để phòng ngắt lồng nhau (Nested IRQ).
   - *Cat 2 giải quyết:* Tự động tráo sang **1 ngăn xếp ngắt dùng chung duy nhất (`knl_system_stack_top`)**, tiết kiệm 40–60% RAM tĩnh toàn vi điều khiển.

> 📚 **Tài liệu lý thuyết đối chiếu:**  
> Toàn bộ lý thuyết nền tảng về vòng đời Extended Task, cơ chế vòng lặp `while(1)` / `for(;;) `, giải mã phanh hãm `WaitEvent()` nhả 100% CPU và Case Study thực tế từ codebase (`TaskShell` & `EventShellInput` từ XML $\to$ Runtime Trigger) được trình bày chi tiết tại:  
> 👉 [`docs/theory/02_AUTOSAR_OS_And_MCAL_Deep_Dive.md` (Mục 1.4)](../theory/02_AUTOSAR_OS_And_MCAL_Deep_Dive.md#14--vòng-đời-bất-tử-của-1-extended-task-bản-chất-vòng-lặp-while1--for-cơ-chế-giải-phóng-cpu-tại-waitevent)  
> 💡 **Lời giải chi tiết bài tập Task 2.4:** Xem tại [`docs/hands_on_tasks/solutions/02_OS_MCAL_Solutions.md` (Task 2.4)](solutions/02_OS_MCAL_Solutions.md#lời-giải-task-24-extended-task-event-driven--đối-chiếu-ngắt-isr-cat-1-vs-cat-2).

---

### TASK 2.5: Immediate Priority Ceiling (IPCP) & Chứng Minh Không Context Switch (🟡 Vừa $\rightarrow$ 🔴 Khó — ~3.5h)

#### 🎯 Mục tiêu:
1. Khai báo Resource dùng chung trong file cấu hình tầng ứng dụng ([`app.xml`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/release/ascore/app/app.xml)) và xây dựng kịch bản 3 Task (`Task_Low`, `Task_Mid`, `Task_High`) nhằm triệt tiêu hiện tượng **Priority Inversion** (Nghịch đảo độ ưu tiên).
2. **Chứng minh thực nghiệm:** Lệnh `GetResource()` trong AUTOSAR OS **hoàn toàn KHÔNG gây Context Switch** (tài nguyên luôn rảnh $O(1)$), Context Switch chỉ diễn ra tại `ReleaseResource()`.

> 📚 **Tài liệu lý thuyết đối chiếu chuyên sâu:**  
> • Để hiểu tường tận **"Resource thực chất là gì trong ECU xe hơi"** (tại sao Resource $\neq$ Vùng đệm dữ liệu, cấu trúc siêu nhẹ chỉ 2 bytes RAM, 4 thực thể phần cứng/phần mềm được bảo vệ):  
> 👉 [`docs/theory/02_AUTOSAR_OS_And_MCAL_Deep_Dive.md` (Mục 4.0: Bản Chất Cốt Tử: "Resource Trong AUTOSAR/OSEK Thực Chất Là Gì?")](../theory/02_AUTOSAR_OS_And_MCAL_Deep_Dive.md#40-bản-chất-cốt-tử-resource-trong-autosarosek-thực-chất-là-gì).  
> • Để phân biệt rạch ròi **Mutex (có Ownership) vs Semaphore (báo hiệu Signalling) vs AUTOSAR Resource**, giải mã chi tiết cơ chế khóa nâng quyền tĩnh (IPCP), kế thừa ưu tiên động (PIP), cấu trúc Hàng đợi chờ trong RAM (Wait Queue), giải phẫu Context Switch và kịch bản Deadlock AB-BA:  
> 👉 [`docs/supplementary_knowledge/04_Mutex_Semaphore_vs_AUTOSAR_Resource_Deep_Dive.md`](../supplementary_knowledge/04_Mutex_Semaphore_vs_AUTOSAR_Resource_Deep_Dive.md).

#### 📋 Quy trình 4 bước thực hiện:

##### Bước 1: Khai báo trong Nguồn Chân Lý Ứng Dụng `app.xml`
Tuân thủ nguyên tắc đóng gói kiến trúc (không sửa `autosar.arxml` của BSW Core), mở [`as/release/ascore/app/app.xml`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/release/ascore/app/app.xml) và thêm cấu hình:

```xml
		<!-- ================= TASK 2.5: IPCP & RESOURCE TIMELINE ================= -->
		<Resource Name="Res_SharedBuffer" 
			Priority="3" 
			Application="OsDefaultApp" 
			Comment="*" />

		<Task Name="Task_Low"  
	    		Activation="1" 
				Autostart="True" 
				Priority="1" 
				Schedule="FULL" 
				StackSize="1024"
				Application="OsDefaultApp" 
	     		Comment="*" >
			<ApplicationModeList Max="TBD">
				<ApplicationMode Comment="*" Name="OSDEFAULTAPPMODE" />
			</ApplicationModeList>
			<ResourceList>
				<Resource Name="Res_SharedBuffer" />
			</ResourceList>
		</Task>

		<Task Name="Task_Mid"  
	    		Activation="1" 
				Autostart="False" 
				Priority="2" 
				Schedule="FULL" 
				StackSize="1024"
				Application="OsDefaultApp" 
	     		Comment="*" />

		<Task Name="Task_High"  
	    		Activation="1" 
				Autostart="False" 
				Priority="3" 
				Schedule="FULL" 
				StackSize="1024"
				Application="OsDefaultApp" 
	     		Comment="*" >
			<ResourceList>
				<Resource Name="Res_SharedBuffer" />
			</ResourceList>
		</Task>
```

> ⚠️ **Cạm bẫy Kỹ thuật Lõi (Core Kernel Pitfall — Bắt buộc phải có `<ResourceList>` trong Task):**  
> Trong bộ sinh mã [`GenOS.py: L41-L51`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/com/as.tool/config.infrastructure.system/argen/GenOS.py#L41-L51), hàm `fixupRes()` quét qua `ResourceList` của từng Task để tự động tính Ceiling Priority. Đồng thời tại [`GenOS.py: L300-L314`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/com/as.tool/config.infrastructure.system/argen/GenOS.py#L300-L314), ArGen sinh ra hàm `Task_Low_CheckAccess(ResID)`.  
> Nếu kỹ sư quên khai báo thẻ `<ResourceList>` bên trong `<Task>`, hàm `CheckAccess()` sẽ trả về `FALSE` $\to$ Kernel [`resource.c: L85`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/com/as.infrastructure/system/kernel/askar/kernel/resource.c#L85) lập tức trả về lỗi **`E_OS_ACCESS`**, khiến lệnh `GetResource()` thất bại!

##### Bước 2: Chạy SCons sinh mã tự động
```bash
scons
```

##### Bước 3: Verify đối soát trong `build/.../config/Os_Cfg.h` & `Os_Cfg.c`
Mở `build/nt/lm3s6965evb/ascore/config/Os_Cfg.h` và `Os_Cfg.c`:
```c
/* Kiểm tra ID Resource và Task trong Os_Cfg.h */
#define RES_ID_Res_SharedBuffer   <Number>
#define TASK_ID_Task_Low          <Number>
#define TASK_ID_Task_Mid          <Number>
#define TASK_ID_Task_High         <Number>

/* Kiểm tra quyền truy cập sinh ra trong Os_Cfg.c */
static boolean Task_Low_CheckAccess(ResourceType ResID)
{
    ...
    case RES_ID_Res_SharedBuffer:
        bAccess = TRUE;
    ...
}
```

##### Bước 4: Viết mã nguồn C kiểm chứng Timeline (`as/release/ascore/app/app.c`)
```c
#include "Os.h"
#include <stdio.h>

TASK(Task_Low)
{
    printf("\n[TIMELINE 1] Task_Low starts (Static Priority = 1)\n");
    
    /* GỌI GETRESOURCE: ĐỘ ƯU TIÊN LẬP TỨC LÊN CEILING (3) - ZERO CONTEXT SWITCH! */
    GetResource(Res_SharedBuffer);
    printf("[TIMELINE 2] Task_Low GOT Resource -> ActualPriority elevated to 3 (NO Context Switch!)\n");

    /* KÍCH HOẠT TASK HIGH (Prio 3) VÀ TASK MID (Prio 2) */
    printf("[TIMELINE 3] Activating Task_High (Prio 3) & Task_Mid (Prio 2)...\n");
    ActivateTask(Task_High);
    ActivateTask(Task_Mid);

    /* VÌ TASK LOW ĐANG GIỮ CEILING = 3, CẢ MID VÀ HIGH ĐỀU KHÔNG THỂ TIẾM QUYỀN */
    printf("[TIMELINE 4] Task_Low still executing! Neither High nor Mid could preempt!\n");

    /* NHẢ RESOURCE: CHÍNH TẠI ĐÂY KERNEL MỚI THỰC HIỆN CONTEXT SWITCH */
    printf("[TIMELINE 5] Calling ReleaseResource()...\n");
    ReleaseResource(Res_SharedBuffer);
    /* Context Switch sang Task_High xảy ra ngay lập tức! */

    printf("[TIMELINE 8] Task_Low resumed and finished.\n");
    TerminateTask();
}

TASK(Task_High)
{
    printf("[TIMELINE 6] Task_High DISPATCHED! Resource is ALREADY FREE. GetResource is instant O(1)!\n");
    GetResource(Res_SharedBuffer);
    ReleaseResource(Res_SharedBuffer);
    TerminateTask();
}

TASK(Task_Mid)
{
    printf("[TIMELINE 7] Task_Mid executing (Prio 2)\n");
    TerminateTask();
}
```

##### Bước 5: Chạy kiểm chứng trên QEMU
```powershell
qemu-system-arm -M lm3s6965evb -kernel build/nt/lm3s6965evb/ascore/lm3s6965evb.exe -nographic -serial mon:stdio
```

#### ✅ Tiêu chí thành công:
1. Chuỗi log in ra chuẩn xác 100% thứ tự timeline: `[TIMELINE 1] -> [2] -> [3] -> [4] -> [5] -> [6] -> [7] -> [8]`.
2. Kỹ sư chứng minh được: Tại `[TIMELINE 2]`, `GetResource` chỉ nâng `RunningVar->priority` mà không gọi `Os_PortDispatch()`. Context Switch chỉ diễn ra tại `[TIMELINE 5]` khi gọi `ReleaseResource()`.

---

### TASK 2.6: Schedule Table — Định Thời Đồng Bộ Đa Chu Kỳ BSW (🔴 Khó — ~3.5h)

#### 🎯 Mục tiêu:
1. Hiểu rõ sự khác biệt giữa chuẩn **OSEK/VDX 2.2.3** (chỉ có Alarm) và **AUTOSAR OS SC2/SC4** (hỗ trợ Schedule Table phần cứng) và nguyên nhân vì sao phải phân biệt.
2. Hiện thực hóa mô hình **Software Cyclic Schedule Table Dispatcher (Chuẩn Automotive Tier-1)** điều phối các BSW Runnables (10ms CAN, 20ms COM, 50ms Diag) trên một trục thời gian đồng bộ với các **Expiry Points** so le tĩnh, triệt tiêu hoàn toàn Phase Jitter.

#### 📖 Kiến thức cốt lõi & Khảo sát Codebase:

##### 1. Chuẩn OSEK/VDX 2.2.3 Là Gì? AUTOSAR OS SC2/SC4 Là Gì? Tại Sao Bắt Buộc Phải Phân Biệt?
* **OSEK/VDX 2.2.3 (ISO 17356-3):**  
  Là chuẩn hệ điều hành thời gian thực nguyên thủy của ngành công nghiệp ô tô Đức (BMW, Bosch, Daimler, VW) từ thập niên 1990.
  - *Đặc tính:* Cực kỳ gọn nhẹ (Kernel chỉ tốn ~2–5 KB Flash và vài trăm bytes RAM), thời gian thực thi tất định cao.
  - *Công cụ định thời:* Chỉ hỗ trợ **Counter & Alarm**.
  - *Hạn chế:* **KHÔNG CÓ** bảng định thời Schedule Table, **KHÔNG CÓ** bảo vệ phân vùng bộ nhớ phần cứng (MPU), và **KHÔNG CÓ** cơ chế giới hạn thời gian chạy của Task (Timing Protection).
* **4 Cấp Độ Mở Rộng AUTOSAR OS (Scalability Classes - SC1 đến SC4):**  
  AUTOSAR Classic OS lấy chuẩn OSEK làm lõi và chuẩn hóa thành 4 cấp độ:
  - **SC1 (Scalability Class 1):** Chính là **OSEK/VDX thuần túy** (chỉ có Basic/Extended Task, Alarm, Resource).
  - **SC2 (Scalability Class 2):** SC1 + **Schedule Table** + **Timing Protection** (bảo vệ giới hạn thời gian thực thi WCET, ngắt task chạy quá giờ).
  - **SC3 (Scalability Class 3):** SC1 + **Memory Protection (MPU)** (phân vùng bộ nhớ RAM/ROM giữa các OS-Application).
  - **SC4 (Scalability Class 4):** Cấp cao nhất = SC1 + **Schedule Table** + **Timing Protection** + **Memory Protection** (dành cho ECU an toàn tối cao ASIL-D: Phanh, Lái, Động cơ).
* **Tại sao bắt buộc phải phân biệt trong dự án này?**  
  - Target vi điều khiển `lm3s6965evb` sử dụng nhân **`askar`** ([`board.lm3s6965evb/Kconfig: L4`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/com/as.application/board.lm3s6965evb/Kconfig#L4)), là nhân **OSEK thuần túy (thuộc lớp SC1)**.
  - Nhân `askar` và bộ sinh mã `GenOS.py` **hoàn toàn không hỗ trợ các thẻ XML `<ScheduleTable>` và hàm API `StartScheduleTableRel()` của SC2/SC4**. Nếu cố tình gọi, trình liên kết (Linker) sẽ báo lỗi `undefined reference` ngay lập tức!
  - Vì vậy, kỹ sư Tier-1 phải áp dụng giải pháp kiến trúc: **Software Cyclic Schedule Table Dispatcher**.

---

##### 2. Mô Hình Software Cyclic Schedule Table Dispatcher (Chuẩn Automotive Tier-1) Là Gì, Có Tác Dụng Gì?
* **Thảm họa khi dùng nhiều Alarm riêng rẽ (Naive Multiple Alarms):**  
  Giả sử hệ thống tạo 3 Alarm độc lập: `Alarm_10ms` (CAN), `Alarm_20ms` (COM), `Alarm_50ms` (Diag).
  - Giống như việc đặt 3 chiếc đồng hồ báo thức độc lập trong phòng ngủ.
  - Đúng tại thời điểm **bội số chung $t = 100\text{ms}$**, cả 3 Alarm cùng reo inh ỏi một lúc!
  - Cả 3 tác vụ cùng ùa vào hàng đợi `ReadyQueue` $\rightarrow$ Gây nghẽn CPU (CPU Load Spike), tăng đỉnh RAM Stack đột ngột và làm trễ hạn thời gian thực (Deadline Miss).
* **Mô hình Dispatcher (Bảng Giờ Tàu Hỏa):**  
  Thay vì đặt nhiều Alarm, nhà ga chỉ dùng **1 người điều phối trung tâm** cầm đồng hồ chính xác 10ms:
  - Hệ thống chỉ cần **duy nhất 1 Base Alarm 10ms** kích hoạt tác vụ chủ `Task_SchedTableDispatcher` (Priority cao).
  - Dispatcher duy trì biến đếm nhịp `schedule_tick` chạy tuần hoàn từ `0` đến `9` (tạo thành một chu kỳ lớn **Major Cycle = $10 \times 10\text{ms} = 100\text{ms}$**).
  - Tại mỗi nhịp (tick), Dispatcher tra cứu thời khóa biểu cố định và kích hoạt các tác vụ tương ứng:
    - *Mọi nhịp (0..9):* Kích hoạt `Task_Can_10ms` (Chu kỳ 10ms).
    - *Nhịp 2, 4, 6, 8:* Kích hoạt `Task_Com_20ms` (Chu kỳ 20ms).
    - *Nhịp 5 (hoặc 1, 6):* Kích hoạt `Task_Diag_50ms` (Chu kỳ 50ms).
* **Tác dụng kỹ nghệ cốt tử:**
  1. **San phẳng tải CPU (Load Balancing):** Phân bổ đều việc thực thi ra các khe thời gian, triệt tiêu hoàn toàn đỉnh nhọn quá tải CPU.
  2. **Tiết kiệm RAM & Timer Interrupts:** Thay vì tốn RAM cho hàng chục cấu trúc Alarm của OS, chỉ tốn đúng 1 Alarm.
  3. **Tương thích 100% trên mọi nhân OSEK SC1:** Đạt được tính năng Schedule Table của SC2/SC4 trên các vi điều khiển giá rẻ mà không cần mua license kernel đắt đỏ.

---

##### 3. Expiry Points So Le Tĩnh & Cơ Chế Triệt Tiêu Hoàn Toàn Phase Jitter

> 💡 **Bản chất cốt tử: Cắt nghĩa Jitter, Độ nặng của Task & Sức mạnh phần cứng MCU:**
> * **Jitter thực chất là gì?**  
>   Jitter **KHÔNG PHẢI** là việc *"có bao nhiêu task cùng chạy trong một thời điểm"*. Jitter là **độ biến thiên (sự dao động/không ổn định) về mặt thời gian giữa các chu kỳ**:
>   $$\text{Phase Jitter} = |T_{\text{thực tế}} - T_{\text{danh định}}| = t_{\text{response\_max}} - t_{\text{response\_min}}$$
>   - Nếu chu kỳ nào Task COM cũng bị trễ đúng $1.0\text{ms}$ do nhường Task CAN chạy trước: Vì độ trễ này là **hằng số bất biến ở mọi chu kỳ** (20ms $\to$ 21ms, 40ms $\to$ 41ms, 60ms $\to$ 61ms), khoảng cách giữa các lần gửi gói tin vẫn chuẩn xác tuyệt đối $20.000\text{ms}$ $\implies$ **Jitter vẫn bằng $0\mu\text{s}$!**
>   - Nhưng nếu tại mốc $100\text{ms}$, có thêm Task Diag chen vào khiến COM bị trễ $4.0\text{ms}$ (thay vì $1.0\text{ms}$): Chu kỳ gửi tin sẽ bị co giãn giật cục ($20\text{ms} \to 23\text{ms} \to 17\text{ms}$) $\implies$ **Đó chính là Jitter** làm vi phạm thời gian lấy mẫu trên bus CAN!
> * **Số lượng Task có thể cùng READY phụ thuộc vào đâu?**  
>   Việc một khe thời gian (ví dụ nhịp Base Alarm 10ms) có thể chứa bao nhiêu Task cùng READY phụ thuộc vào 2 yếu tố kỹ thuật:
>   1. **Độ nặng của Task (WCET — Worst-Case Execution Time):** Thời gian thực thi dài nhất trong kịch bản tệ nhất (tốn bao nhiêu chu kỳ CPU/microsecond).
>   2. **Độ mạnh của phần cứng MCU:** Tần số xung nhịp (Clock MHz/GHz), kiến trúc tập lệnh (Cortex-M3, R5, AURIX TriCore), bộ đệm Cache và bộ gia tốc phần cứng.
>   - **Quy tắc vàng lập ngân sách thời gian (Timing Budgeting của Tier-1):**  
>     Tổng thời gian chạy của tất cả các task cùng READY trong 1 tick không bao giờ được vượt quá độ rộng của tick ($\sum \text{WCET} < \text{Tick Period} = 10\text{ms}$). Thực tế, kỹ sư luôn khống chế tổng tải $\le 65\% - 70\%$ CPU Load trong 1 tick để dành **$30\% - 35\%$ Headroom** cho ngắt phần cứng ISR và bù đắp suy hao nhiệt độ!

* **Phase Jitter (Hiện tượng co giãn thời gian phản hồi do lệch pha / trùng pha) là gì?**
  - Khi hai tác vụ chu kỳ bội số (20ms COM và 50ms Diag) vô tình trùng pha kích hoạt:
    - Ở mốc $t = 50\text{ms}$: Task Diag chạy một mình một ngựa, tốn đúng **$2\text{ms}$** để gửi xong gói tin.
    - Ở mốc $t = 100\text{ms}$: Cả Task COM 20ms và Task Diag 50ms cùng thức dậy. Task Diag bị Task COM chen ngang, khiến nó mất tới **$7\text{ms}$** mới xong!
    - **Hậu quả trên bus CAN:** Khoảng cách giữa các frame CAN bị co giãn thất thường (lúc 50ms, lúc 55ms, lúc 48ms). Hiện tượng này gọi là **Phase Jitter**. Trên mạng CAN ô tô, Phase Jitter vượt quá 10% sẽ khiến các ECU khác ghi nhận lỗi **Mất giao tiếp (Timeout DTC Code)**!
* **Expiry Points So Le Tĩnh (Static Staggered Expiry Points):**
  - **Expiry Point:** Là một mốc thời gian cố định (offset mili-giây) nằm trên trục Major Cycle 100ms mà tại đó một hành vi định sẵn phải diễn ra.
  - **So le tĩnh:** Kỹ sư kiến trúc **chủ động phân bổ các mốc kích hoạt vào các nhịp lệch nhau**, không bao giờ để các tác vụ chu kỳ dài chạm mặt nhau ở cùng một thời điểm:

```
          MÔ HÌNH PHÂN BỔ EXPIRY POINTS SO LE TRÊN TRỤC THỜI GIAN 100ms
    Tick Counter (0..9):   [0]      [1]      [2]      [3]      [4]      [5]      [6]      [7]      [8]      [9]
    Trục thời gian (ms):   0ms     10ms     20ms     30ms     40ms     50ms     60ms     70ms     80ms     90ms
    ─────────────────────────────────────────────────────────────────────────────────────────────────────────────
    Task_Can_10ms  (10ms):  ●        ●        ●        ●        ●        ●        ●        ●        ●        ●
    Task_Com_20ms  (20ms):  -        -        ●        -        ●        -        ●        -        ●        -
    Task_Diag_50ms (50ms):  -        -        -        -        -        ●        -        -        -        -
```

* **Cơ chế triệt tiêu Phase Jitter:**
  - Nhìn vào bảng: Tại nhịp 2, 4, 6, 8, `Task_Com_20ms` luôn chạy trong cùng một điều kiện tải CPU cố định $\rightarrow$ Thời gian hoàn tất luôn là hằng số.
  - Tại nhịp 5, `Task_Diag_50ms` chạy mà không bị trùng với nhịp của `Task_Com_20ms` $\rightarrow$ Không có hiện tượng chen ngang bất ngờ.
  - **Kết quả:** Độ biến thiên thời gian (Jitter) bằng $0\mu\text{s}$ $\rightarrow$ Đạt tính tất định hoàn hảo (**Zero Phase Jitter**), tín hiệu CAN/COM phát ra đều như nhịp đồng hồ Thụy Sĩ!

---

##### 4. Bảng Ma Trận Đối Chiếu Khái Niệm Chuẩn Ngành Xe Hơi:

| Khái Niệm | Bản Chất Kỹ Thuật | Ứng Dụng Trong Task 2.6 |
| :--- | :--- | :--- |
| **OSEK/VDX SC1** | Chuẩn OS tinh gọn, chỉ có Counter/Alarm, không hỗ trợ Schedule Table phần cứng. | Bo mạch `lm3s6965evb` chạy nhân `askar` SC1, cấm gọi API `StartScheduleTableRel()`. |
| **AUTOSAR SC2/SC4** | Chuẩn OS cao cấp, hỗ trợ Schedule Table, Timing Protection (SC2/SC4) và Memory Protection (SC3/SC4). | Dành cho chip có phần cứng MPU/Timer bảo vệ ASIL-D. |
| **Schedule Table Dispatcher** | Dùng 1 Alarm 10ms điều phối biến đếm `schedule_tick` (0..9) trên Major Cycle 100ms. | Giải pháp phần mềm chuẩn Tier-1 mang Schedule Table lên vi điều khiển SC1. |
| **Expiry Points So Le** | Phân chia các mốc kích hoạt Task 10ms, 20ms, 50ms so le nhau trên trục thời gian. | Loại bỏ va chạm tài nguyên tại các mốc bội số chung (100ms). |
| **Triệt Tiêu Phase Jitter** | Giữ cho thời gian hoàn tất và chu kỳ gửi gói tin của từng task là hằng số cố định. | Đảm bảo tính toàn vẹn tín hiệu CAN và chống lỗi Timeout DTC trên bus xe hơi. |

---

#### 📋 Quy trình 4 bước thực hiện:

##### Bước 1: Khai báo Dispatcher và các Task chu kỳ trong `app.xml`
Mở [`as/release/ascore/app/app.xml`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/release/ascore/app/app.xml):

```xml
		<!-- ================= TASK 2.6: SCHEDULE TABLE DISPATCHER ================= -->
		<Task Name="Task_SchedTableDispatcher"  
	    		Activation="1" 
				Autostart="False" 
				Priority="9" 
				Schedule="FULL" 
				StackSize="1024"
				Application="OsDefaultApp"
	     		Comment="*" />

		<Task Name="Task_Can_10ms"  
	    		Activation="1" 
				Autostart="False" 
				Priority="8" 
				Schedule="FULL" 
				StackSize="1024"
				Application="OsDefaultApp"
	     		Comment="*" />

		<Task Name="Task_Com_20ms"  
	    		Activation="1" 
				Autostart="False" 
				Priority="6" 
				Schedule="FULL" 
				StackSize="1024"
				Application="OsDefaultApp"
	     		Comment="*" />

		<Task Name="Task_Diag_50ms"  
	    		Activation="1" 
				Autostart="False" 
				Priority="4" 
				Schedule="FULL" 
				StackSize="1024"
				Application="OsDefaultApp"
	     		Comment="*" />

		<Alarm Name="Alarm_SchedTable" 
			Autostart="True" 
			Period="10" 
			StartTime="10" 
			Counter="OsClock" 
			Action="ActivateTask" 
			Task="Task_SchedTableDispatcher" 
			Event="TBD" 
			Callback="TBD" 
			Application="OsDefaultApp" 
			Comment="*" >
			<ApplicationModeList Max="TBD">
				<ApplicationMode Comment="*" Name="OSDEFAULTAPPMODE" />
			</ApplicationModeList>
		</Alarm>
```

##### Bước 2: Chạy SCons sinh mã tự động
```bash
scons
```

##### Bước 3: Verify đối soát trong `Os_Cfg.h`
Kiểm tra các định danh được sinh tự động:
```c
#define TASK_ID_Task_SchedTableDispatcher  <Number>
#define TASK_ID_Task_Can_10ms              <Number>
#define TASK_ID_Task_Com_20ms              <Number>
#define TASK_ID_Task_Diag_50ms             <Number>
#define ALARM_ID_Alarm_SchedTable          <Number>
```

##### Bước 4: Viết mã nguồn C Dispatcher Table Chuẩn Tier-1 (`as/release/ascore/app/app.c`)

Mô hình kiến trúc được chuẩn hóa gồm **4 thành phần cốt lõi** theo tiêu chuẩn kỹ nghệ Tier-1 Automotive:
1. **Data Model:** Định nghĩa kiểu dữ liệu `SchedTable_ExpiryPoint_Type` mô tả mốc thời gian và Runnable ủy thác.
2. **BSW Runnables:** Các hàm nghiệp vụ thực tế độc lập (`Bsw_Runnable_Can_10ms`, `Bsw_Runnable_Com_20ms`, `Bsw_Runnable_Diag_50ms`).
3. **Static Lookup Table:** Mảng tĩnh `Software_Schedule_Table[]` phân bổ các Expiry Points so le tuyệt đối trên Major Cycle 100ms (COM chiếm tick chẵn `0, 2, 4, 6, 8`, Diag chiếm tick lẻ `5` $\to$ vĩnh viễn không bao giờ va chạm tài nguyên).
4. **Dispatcher Engine:** Hàm `SchedTable_Dispatcher_Step(uint32_t tick)` tra cứu bảng và kích hoạt Task chính xác mà không dùng logic rẽ nhánh lồng nhau.

```c
#include "Os.h"
#include <stdio.h>

/* ========================================================================= */
/* TASK 2.6: TIER-1 SOFTWARE CYCLIC SCHEDULE TABLE DISPATCHER ARCHITECTURE   */
/* ========================================================================= */

/* --- THÀNH PHẦN 1: ĐỊNH NGHĨA CẤU TRÚC DỮ LIỆU EXPIRY POINT (AUTOSAR DATA MODEL) --- */
typedef struct {
	uint32_t offset_tick;               /* Mốc Expiry Point (0..9, mỗi tick = 10ms) */
	uint32_t offset_ms;                 /* Mốc thời gian danh định trên Major Cycle (0..90ms) */
	TaskType task_id;                   /* Task OS được ủy thác thực thi */
	const char* task_name;              /* Tên Task OS */
	const char* runnable_name;          /* Tên Runnable BSW */
} SchedTable_ExpiryPoint_Type;

/* --- THÀNH PHẦN 2: CÁC HÀM BSW RUNNABLE THỰC THI NGHIỆP VỤ --- */
static void Bsw_Runnable_Can_10ms(void)
{
	/* Xử lý tầng giao vận CAN: Mailbox Rx/Tx, Polling & Thông điệp khẩn cấp */
}

static void Bsw_Runnable_Com_20ms(void)
{
	/* Xử lý tầng tương tác COM: Đóng gói tín hiệu PDU, Routing và Giám sát Deadline */
}

static void Bsw_Runnable_Diag_50ms(void)
{
	/* Xử lý tầng chẩn đoán DCM: Quản lý phiên UDS, Security Access, Đọc/Ghi DTC */
}

/* --- THÀNH PHẦN 3: BẢNG THỜI KHÓA BIỂU ĐỊNH THỜI CỐ ĐỊNH (STATIC SCHEDULE TABLE) --- */
/* Phân bổ các Expiry Points so le tĩnh trên Major Cycle 100ms (10 Ticks)              */
static const SchedTable_ExpiryPoint_Type Software_Schedule_Table[] = {
	/* Tick 0 ( 0ms): CAN + COM */
	{ 0,  0, TASK_ID_Task_Can_10ms,  "Task_Can_10ms",  "Can_MainFunction_Write/Read" },
	{ 0,  0, TASK_ID_Task_Com_20ms,  "Task_Com_20ms",  "Com_MainFunctionTx/Rx" },

	/* Tick 1 (10ms): CAN */
	{ 1, 10, TASK_ID_Task_Can_10ms,  "Task_Can_10ms",  "Can_MainFunction_Write/Read" },

	/* Tick 2 (20ms): CAN + COM */
	{ 2, 20, TASK_ID_Task_Can_10ms,  "Task_Can_10ms",  "Can_MainFunction_Write/Read" },
	{ 2, 20, TASK_ID_Task_Com_20ms,  "Task_Com_20ms",  "Com_MainFunctionTx/Rx" },

	/* Tick 3 (30ms): CAN */
	{ 3, 30, TASK_ID_Task_Can_10ms,  "Task_Can_10ms",  "Can_MainFunction_Write/Read" },

	/* Tick 4 (40ms): CAN + COM */
	{ 4, 40, TASK_ID_Task_Can_10ms,  "Task_Can_10ms",  "Can_MainFunction_Write/Read" },
	{ 4, 40, TASK_ID_Task_Com_20ms,  "Task_Com_20ms",  "Com_MainFunctionTx/Rx" },

	/* Tick 5 (50ms): CAN + Diag (So le tĩnh: Diag chiếm tick lẻ 5, COM chiếm tick chẵn) */
	{ 5, 50, TASK_ID_Task_Can_10ms,  "Task_Can_10ms",  "Can_MainFunction_Write/Read" },
	{ 5, 50, TASK_ID_Task_Diag_50ms, "Task_Diag_50ms", "Dcm_MainFunction (UDS Session)" },

	/* Tick 6 (60ms): CAN + COM */
	{ 6, 60, TASK_ID_Task_Can_10ms,  "Task_Can_10ms",  "Can_MainFunction_Write/Read" },
	{ 6, 60, TASK_ID_Task_Com_20ms,  "Task_Com_20ms",  "Com_MainFunctionTx/Rx" },

	/* Tick 7 (70ms): CAN */
	{ 7, 70, TASK_ID_Task_Can_10ms,  "Task_Can_10ms",  "Can_MainFunction_Write/Read" },

	/* Tick 8 (80ms): CAN + COM */
	{ 8, 80, TASK_ID_Task_Can_10ms,  "Task_Can_10ms",  "Can_MainFunction_Write/Read" },
	{ 8, 80, TASK_ID_Task_Com_20ms,  "Task_Com_20ms",  "Com_MainFunctionTx/Rx" },

	/* Tick 9 (90ms): CAN */
	{ 9, 90, TASK_ID_Task_Can_10ms,  "Task_Can_10ms",  "Can_MainFunction_Write/Read" },
};

#define SCHED_TABLE_EXPIRY_COUNT  (sizeof(Software_Schedule_Table) / sizeof(Software_Schedule_Table[0]))
#define MAJOR_CYCLE_TICKS         10

static uint32_t schedule_tick = 0;
static uint32_t major_cycle_count = 0;
static uint32_t current_offset_ms = 0;

/* --- THÀNH PHẦN 4: ĐỘNG CƠ ĐIỀU PHỐI BẢNG ĐỊNH THỜI (SCHEDULE TABLE DISPATCHER ENGINE) --- */
static void SchedTable_Dispatcher_Step(uint32_t tick)
{
	uint32_t i;
	for (i = 0; i < SCHED_TABLE_EXPIRY_COUNT; i++)
	{
		if (Software_Schedule_Table[i].offset_tick == tick)
		{
			/* Kích hoạt Task theo Expiry Point tra cứu được từ Bảng */
			(void)ActivateTask(Software_Schedule_Table[i].task_id);
		}
	}
}

/* Task Dispatcher đóng vai trò như một Schedule Table Engine được kích hoạt bởi Base Alarm 10ms */
TASK(Task_SchedTableDispatcher)
{
	current_offset_ms = schedule_tick * 10;

	if (schedule_tick == 0 && major_cycle_count < 2)
	{
		printf("\n=================================================================\n");
		printf("[TASK 2.6] SCHEDULE TABLE MAJOR CYCLE #%lu (100ms Window - Table Lookup Engine)\n", 
		       (unsigned long)(major_cycle_count + 1));
		printf("=================================================================\n");
	}

	/* THỰC THI BỘ ĐIỀU PHỐI BẢNG: Tra cứu và kích hoạt các Expiry Points của tick hiện tại */
	SchedTable_Dispatcher_Step(schedule_tick);

	schedule_tick = (schedule_tick + 1) % MAJOR_CYCLE_TICKS;
	if (schedule_tick == 0)
	{
		major_cycle_count++;
	}

	(void)TerminateTask();
}

/* Các OS Tasks đóng vai trò Wrapper thực thi các BSW Runnables */
TASK(Task_Can_10ms)
{
	Bsw_Runnable_Can_10ms();
	if (major_cycle_count < 2)
	{
		printf("  [SCHED TABLE | Offset %2lums] Executing Task_Can_10ms  (Priority 8, Runnable: Can_MainFunction)\n", 
		       (unsigned long)current_offset_ms);
	}
	(void)TerminateTask();
}

TASK(Task_Com_20ms)
{
	Bsw_Runnable_Com_20ms();
	if (major_cycle_count < 2)
	{
		printf("  [SCHED TABLE | Offset %2lums] Executing Task_Com_20ms  (Priority 6, Runnable: Com_MainFunction)\n", 
		       (unsigned long)current_offset_ms);
	}
	(void)TerminateTask();
}

TASK(Task_Diag_50ms)
{
	Bsw_Runnable_Diag_50ms();
	if (major_cycle_count < 2)
	{
		printf("  [SCHED TABLE | Offset %2lums] Executing Task_Diag_50ms (Priority 4, Runnable: Dcm_MainFunction)\n", 
		       (unsigned long)current_offset_ms);
	}
	(void)TerminateTask();
}
```

#### ✅ Tiêu chí thành công:
1. Hệ thống biên dịch và liên kết thành công 100% không gặp lỗi `undefined reference to StartScheduleTableRel`.
2. Khởi chạy trên QEMU Cortex-M3 (`qemu-system-arm -M lm3s6965evb -kernel build/nt/lm3s6965evb/ascore/lm3s6965evb.exe -nographic -serial mon:stdio`), trace log xác nhận:
   - `Task_Com_20ms` và `Task_Diag_50ms` **không bao giờ va chạm nhau** tại bất kỳ tick nào.
   - Tại các mốc chẵn, `Task_Can_10ms` (Prio 8) luôn chạy trước `Task_Com_20ms` (Prio 6), đảm bảo chu kỳ thực tế của COM luôn chuẩn xác tuyệt đối $20.000\text{ms}$ ($\text{Phase Jitter} = 0\mu\text{s}$).

```text
=================================================================
[TASK 2.6] SCHEDULE TABLE MAJOR CYCLE #1 (100ms Window - Table Lookup Engine)
=================================================================
  [SCHED TABLE | Offset  0ms] Executing Task_Can_10ms  (Priority 8, Runnable: Can_MainFunction)
  [SCHED TABLE | Offset  0ms] Executing Task_Com_20ms  (Priority 6, Runnable: Com_MainFunction)
  [SCHED TABLE | Offset 10ms] Executing Task_Can_10ms  (Priority 8, Runnable: Can_MainFunction)
  [SCHED TABLE | Offset 20ms] Executing Task_Can_10ms  (Priority 8, Runnable: Can_MainFunction)
  [SCHED TABLE | Offset 20ms] Executing Task_Com_20ms  (Priority 6, Runnable: Com_MainFunction)
  [SCHED TABLE | Offset 30ms] Executing Task_Can_10ms  (Priority 8, Runnable: Can_MainFunction)
  [SCHED TABLE | Offset 40ms] Executing Task_Can_10ms  (Priority 8, Runnable: Can_MainFunction)
  [SCHED TABLE | Offset 40ms] Executing Task_Com_20ms  (Priority 6, Runnable: Com_MainFunction)
  [SCHED TABLE | Offset 50ms] Executing Task_Can_10ms  (Priority 8, Runnable: Can_MainFunction)
  [SCHED TABLE | Offset 50ms] Executing Task_Diag_50ms (Priority 4, Runnable: Dcm_MainFunction)
  [SCHED TABLE | Offset 60ms] Executing Task_Can_10ms  (Priority 8, Runnable: Can_MainFunction)
  [SCHED TABLE | Offset 60ms] Executing Task_Com_20ms  (Priority 6, Runnable: Com_MainFunction)
  [SCHED TABLE | Offset 70ms] Executing Task_Can_10ms  (Priority 8, Runnable: Can_MainFunction)
  [SCHED TABLE | Offset 80ms] Executing Task_Can_10ms  (Priority 8, Runnable: Can_MainFunction)
  [SCHED TABLE | Offset 80ms] Executing Task_Com_20ms  (Priority 6, Runnable: Com_MainFunction)
  [SCHED TABLE | Offset 90ms] Executing Task_Can_10ms  (Priority 8, Runnable: Can_MainFunction)
```

---

### TASK 2.7: Bảo Vệ Bộ Nhớ & Bắt Lỗi Hệ Thống: Stack Watermark + ErrorHook & DET (🔴 Khó — ~3h)

#### 🎯 Mục tiêu:
1. Hiểu rõ cấu trúc ngăn xếp của vi điều khiển ARM Cortex-M3 (Full Descending Stack) và cơ chế gọi Hook của nhân hệ điều hành [`askar`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/com/as.infrastructure/system/kernel/askar/).
2. Ứng dụng kỹ thuật **Stack Watermark (Pattern Fill `0xDEADBEEF`)** tại đáy ngăn xếp của Task để phát hiện sớm lỗi tràn ngăn xếp (Stack Overflow) trong `PostTaskHook()`, chuyển tiếp mã lỗi hệ thống sang **DET (Default Error Tracer)** trong `ErrorHook()`.

#### 📋 Quy trình 4 bước thực hiện:

##### Bước 1: Khảo sát cấu hình Hook sẵn có trong `autosar.arxml` & `Os_Cfg.h`
Trong [`as/com/as.application/common/autosar.arxml: L5`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/com/as.application/common/autosar.arxml#L5), thẻ `<General>` đã khai báo sẵn:
```xml
<General Comment="Not Used" Conformance="ECC1" 
         ErrorHook="ErrorHook" 
         PostTaskHook="PostTaskHook" 
         PreTaskHook="PreTaskHook" 
         ShutdownHook="ShutdownHook" 
         StartupHook="StartupHook" 
         Status="EXTENDED" />
```
Khi chạy `scons`, file `build/.../config/Os_Cfg.h` đã sinh sẵn:
```c
#define OS_USE_ERROR_HOOK
#define OS_USE_POSTTASK_HOOK
#define OS_USE_STARTUP_HOOK
#define OS_USE_SHUTDOWN_HOOK
```

##### Bước 2: Khảo sát vị trí cài đặt Hook trong `as/release/ascore/app/app.c`
> ⚠️ **Cảnh báo lỗi Multiple Definition Linker Error:**  
> Trong file [`as/release/ascore/app/app.c: L418-L478`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/release/ascore/app/app.c#L418-L478), các hàm `void ErrorHook(StatusType ercd)` và `void PostTaskHook(void)` **đã được định nghĩa sẵn**. Kỹ sư không viết thêm hàm mới mà sẽ **cập nhật trực tiếp thân hàm** này.

##### Bước 3: Cài đặt Watermark và Hook giám sát trong `app.c`
Mở [`as/release/ascore/app/app.c`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/release/ascore/app/app.c), include thêm thư viện DET và kernel internal:

```c
#include "Det.h"
#include "Modules.h"

#define STACK_WATERMARK_PATTERN 0xDEADBEEFU

/* Mở rộng hàm PostTaskHook() có sẵn tại app.c: L470 */
void PostTaskHook(void)
{
#ifdef USE_TRACE
    TaskType TaskID;
    GetTaskID(&TaskID);
    Trace_PerfStop(TaskID);
#endif

    /* ASIL-D STACK OVERFLOW MONITOR */
    TaskType current_task;
    GetTaskID(&current_task);

    if (current_task < TASK_NUM)
    {
        /* Trên Cortex-M (Descending Stack), pStack trỏ vào đáy mảng (vùng tràn nguy hiểm nhất) */
        uint32_t *stack_bottom = (uint32_t*)TaskConstArray[current_task].pStack;
        if (stack_bottom != NULL && stack_bottom[0] != STACK_WATERMARK_PATTERN)
        {
            printf("\n[CRITICAL ASIL-D] STACK OVERFLOW DETECTED in Task ID %u (%s)!\n", 
                   (unsigned int)current_task, TaskConstArray[current_task].name);
            printf("                 Watermark Corrupted: Expected 0x%08X, Found 0x%08lX\n", 
                   STACK_WATERMARK_PATTERN, (unsigned long)stack_bottom[0]);
            ShutdownOS(E_OS_SYS_STACK);
        }
    }
}

/* Mở rộng hàm ErrorHook() có sẵn tại app.c: L418 */
void ErrorHook(StatusType ercd)
{
    OSServiceIdType service_id = OSErrorGetServiceId();
    printf("[OS ERROR HOOK] System Error Caught! Service ID = %u, Error Code = %u\n", 
           (unsigned int)service_id, (unsigned int)ercd);

    /* Chuyển tiếp lỗi sang tầng DET (Default Error Tracer) chuẩn AUTOSAR */
    Det_ReportError(MODULE_ID_OS, 0, (uint8)service_id, (uint8)ercd);

    if (E_OS_CALLEVEL == ercd)
    {
        ShutdownOS(E_OS_CALLEVEL);
    }
}
```

##### Bước 4: Hàm gieo mầm Watermark trước khi khởi động OS (`app.c`)
Trong hàm khởi tạo trước `StartOS()`, đặt mầm kiểm tra cho tất cả các Task:
```c
void Initialize_Task_Stack_Watermarks(void)
{
    for (TaskType id = 0; id < TASK_NUM; id++)
    {
        uint32_t *stack_bottom = (uint32_t*)TaskConstArray[id].pStack;
        if (stack_bottom != NULL)
        {
            stack_bottom[0] = STACK_WATERMARK_PATTERN;
        }
    }
}
```

#### ✅ Tiêu chí thành công:
1. `PostTaskHook` truy cập hợp lệ con trỏ stack thực tế của Task qua `TaskConstArray[current_task].pStack` mà không gây HardFault.
2. Khi giả lập tràn ngăn xếp (ghi đè `stack_bottom[0] = 0x12345678`), `PostTaskHook` phát hiện sự sai lệch ngay lập tức khi Task nhả CPU và gọi `ShutdownOS(E_OS_SYS_STACK)`.
3. Mọi mã lỗi OS phát sinh đều được `ErrorHook` ghi nhận và chuyển tiếp an toàn sang `Det_ReportError(MODULE_ID_OS, ...)`.

---

### TASK 2.8: Hand-Coded `IoHwAb` Driver — Đọc ADC Thô, Lọc Số IIR, Cầu Phân Áp & Kích Relay/PWM (🔴 Khó — ~4h)

#### 🎯 Mục tiêu:
Viết tay 100% mã nguồn C cho module **`IoHwAb` (I/O Hardware Abstraction)** theo chuẩn AUTOSAR bám sát [`as/com/as.infrastructure/include/IoHwAb.h`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/com/as.infrastructure/include/IoHwAb.h) và [`IoHwAb_Types.h`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/com/as.infrastructure/include/IoHwAb_Types.h). Module này đóng vai trò là "chiếc cầu nối độc quyền" giữa các driver MCAL (`Adc`, `Dio`, `Pwm`) với các ứng dụng điều khiển xe trên tầng RTE (`SWC_PedalSensor`, `SWC_ContactorControl`).

#### 📖 Kiến thức cốt lõi & Vị trí kiến trúc:
1. **Tại sao `IoHwAb` bắt buộc phải viết tay (Hand-coded in-house)?**
   * Tầng MCAL do hãng chip cung cấp chỉ trả về giá trị thô: ADC trả về Ticks ($0 - 4095$), GPIO chỉ biết High/Low.
   * Tầng Application (SWC) chỉ được phép xử lý giá trị vật lý: Điện áp chân ga ($0 - 5000\text{ mV}$), Góc mở bướm ga ($0 - 100\%$), Dòng điện đóng Contactor ($A$).
   * Tầng `IoHwAb` là nơi duy nhất chứa **bí mật phần cứng bo mạch PCB**: Sơ đồ cầu phân áp điện trở, hệ số cảm biến nhiệt độ NTC, thuật toán lọc số chống nhiễu EMC, và mạch kích Transistor đóng relay.
2. **Các API chuẩn trong `as/` đối chiếu:**
   * [`as/com/as.infrastructure/include/IoHwAb.h`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/com/as.infrastructure/include/IoHwAb.h):
     * `IOHWAB_INIT_ID = 0x10` $\implies$ `void IoHwAb_Init(void)`
     * `IOHWAB_ANALOG_GET_ID = 0x20` $\implies$ `Std_ReturnType IoHwAb_Analog_Get(IoHwAb_SignalType Signal, IoHwAb_AnalogValueType *Value, IoHwAb_StatusType *Status)`
     * `IOHWAB_DIGITAL_SET_ID = 0x31` $\implies$ `Std_ReturnType IoHwAb_Digital_Set(IoHwAb_SignalType Signal, IoHwAb_LevelType Level)`
     * `IOHWAB_PWMDUTY_SET_ID = 0x40` $\implies$ `Std_ReturnType IoHwAb_PwmDuty_Set(IoHwAb_SignalType Signal, IoHwAb_DutyType Duty)`
   * [`as/com/as.infrastructure/include/IoHwAb_Types.h`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/com/as.infrastructure/include/IoHwAb_Types.h):
     * `IoHwAb_LevelType` (`STD_LOW`, `STD_HIGH`)
     * `IoHwAb_DutyType` ($0$ đến $1000\text{ per mille}$ theo `IOHWAB_DUTY_MAX`)
     * `IoHwAb_QualityType` (`IOHWAB_INIVAL`, `IOHWAB_ERR`, `IOHWAB_BAD`, `IOHWAB_GOOD`)

#### 📋 Hướng dẫn từng bước & Cài đặt mã nguồn C:

##### Bước 1: Khai báo Signal ID & Trạng thái lưu trữ bộ lọc (`IoHwAb_Cfg.h` & `IoHwAb.c`)
```c
/* as/com/as.infrastructure/include/IoHwAb_Cfg.h */
#ifndef IOHWAB_CFG_H_
#define IOHWAB_CFG_H_

#define IOHWAB_SIGNAL_PEDAL_MAIN     0   /* Cảm biến chân ga 1 (ADC Channel 0) */
#define IOHWAB_SIGNAL_PEDAL_SUB      1   /* Cảm biến chân ga 2 (ADC Channel 1) */
#define IOHWAB_SIGNAL_MAIN_CONTACTOR 2   /* Rơ-le Contactor pin 400V (DIO Pin 5) */
#define IOHWAB_SIGNAL_COOLING_FAN    3   /* Quạt làm mát Inverter (PWM Channel 2) */

#endif
```

##### Bước 2: Hiện thực thuật toán giải mã phần cứng & Bộ lọc số IIR (`IoHwAb.c`)
```c
/* as/com/as.infrastructure/system/IoHwAb/IoHwAb.c */
#include "IoHwAb.h"
#include "IoHwAb_Types.h"
#include "IoHwAb_Cfg.h"
#include "Adc.h"
#include "Dio.h"
#include "Pwm.h"

/* Bộ đệm lưu trữ giá trị lọc số (IIR Low-Pass Filter) */
static sint32 Filtered_Pedal_Main_mV = 0;
static sint32 Filtered_Pedal_Sub_mV  = 0;
static boolean IoHwAb_Initialized    = FALSE;

void IoHwAb_Init(void) {
    Filtered_Pedal_Main_mV = 0;
    Filtered_Pedal_Sub_mV  = 0;
    IoHwAb_Initialized = TRUE;
}

/* 
 * Thuật toán đọc ADC & Chuyển đổi vật lý:
 * Mạch cầu chia áp bo mạch PCB: R1 = 10k, R2 = 10k -> V_pin = V_adc * 2
 * ADC 12-bit: Vref = 3300 mV, Max Ticks = 4095
 */
Std_ReturnType IoHwAb_Analog_Get(IoHwAb_SignalType Signal, IoHwAb_AnalogValueType *Value, IoHwAb_StatusType *Status) {
    if (!IoHwAb_Initialized || Value == NULL || Status == NULL) {
        return E_NOT_OK;
    }

    if (Signal == IOHWAB_SIGNAL_PEDAL_MAIN) {
        /* Đọc giá trị thô từ MCAL ADC Group */
        Adc_ValueGroupType raw_ticks = Adc_ReadGroup_Sample(0); // Giả lập đọc ADC Ch0
        
        /* Chuyển sang điện áp chân chip (mV) */
        sint32 raw_voltage_mV = (sint32)((uint32)raw_ticks * 3300UL / 4095UL);
        
        /* Áp dụng tỷ lệ cầu phân áp phần cứng: V_input = V_adc * (R1 + R2) / R2 = V_adc * 2 */
        sint32 physical_voltage_mV = raw_voltage_mV * 2;

        /* Áp dụng bộ lọc số IIR Low-Pass: y[n] = 0.25 * x[n] + 0.75 * y[n-1] */
        Filtered_Pedal_Main_mV = (physical_voltage_mV * 25 + Filtered_Pedal_Main_mV * 75) / 100;

        *Value = Filtered_Pedal_Main_mV;
        
        /* Đánh giá tính toàn vẹn phần cứng (Electrical Diagnostic) */
        if (raw_ticks < 50 || raw_ticks > 4050) {
            /* Dây cảm biến bị chạm mass hoặc chạm nguồn 5V */
            Status->quality = IOHWAB_ERR;
        } else {
            Status->quality = IOHWAB_GOOD;
        }
        return E_OK;
    }
    return E_NOT_OK;
}

/* Điều khiển Digital: Đóng ngắt Contactor pin cao áp */
Std_ReturnType IoHwAb_Digital_Set(IoHwAb_SignalType Signal, IoHwAb_LevelType Level) {
    if (!IoHwAb_Initialized) return E_NOT_OK;

    if (Signal == IOHWAB_SIGNAL_MAIN_CONTACTOR) {
        Dio_LevelType dio_level = (Level == IOHWAB_HIGH) ? STD_HIGH : STD_LOW;
        Dio_WriteChannel(DIO_CHANNEL_CONTACTOR, dio_level);
        return E_OK;
    }
    return E_NOT_OK;
}

/* Điều khiển PWM: Băm xung quạt làm mát Inverter (0 đến 1000 per mille) */
Std_ReturnType IoHwAb_PwmDuty_Set(IoHwAb_SignalType Signal, IoHwAb_DutyType Duty) {
    if (!IoHwAb_Initialized || Duty > IOHWAB_DUTY_MAX) return E_NOT_OK;

    if (Signal == IOHWAB_SIGNAL_COOLING_FAN) {
        /* Chuyển đổi Duty 0-1000 per mille sang giá trị MCAL PWM (0-0x8000) */
        uint16 mcal_duty = (uint16)((uint32)Duty * 0x8000UL / 1000UL);
        Pwm_SetDutyCycle(PWM_CHANNEL_FAN, mcal_duty);
        return E_OK;
    }
    return E_NOT_OK;
}
```

##### Bước 3: Ánh xạ API từ tầng RTE / SWC gọi xuống `IoHwAb`
Trong tầng ứng dụng VCU (`SWC_PedalSensor.c` hoặc `SWC_ContactorControl.c`), Application không được phép gọi trực tiếp `Adc_ReadGroup()` hay `Dio_WriteChannel()`, mà bắt buộc phải gọi qua giao diện `IoHwAb`:
```c
/* SWC_PedalSensor.c */
void PedalSensor_Runnable_10ms(void) {
    IoHwAb_AnalogValueType pedal_mV;
    IoHwAb_StatusType status;
    
    Std_ReturnType ret = IoHwAb_Analog_Get(IOHWAB_SIGNAL_PEDAL_MAIN, &pedal_mV, &status);
    if (ret == E_OK && status.quality == IOHWAB_GOOD) {
        /* Gửi giá trị điện áp đã lọc sạch lên thuật toán VCU */
        Rte_Write_PedalVoltage_mV(pedal_mV);
    } else {
        /* Báo lỗi cảm biến sang Dem */
        Dem_SetEventStatus(DTC_PEDAL_SENSOR_CIRCUIT_FAIL, DEM_EVENT_STATUS_FAILED);
    }
}
```

#### ✅ Tiêu chí thành công:
1. Module `IoHwAb` biên dịch độc lập không phụ thuộc vào nền tảng vi điều khiển bên dưới.
2. Bộ lọc số IIR triệt tiêu hoàn toàn các gai nhiễu điện từ giả lập (spikes) trên tín hiệu ADC.
3. Khi ngắt dây cảm biến ($ADC < 50\text{ ticks}$), `IoHwAb` trả về `IOHWAB_ERR`, bảo vệ xe không bị tăng ga ngoài ý muốn.
4. Điều khiển Contactor và Quạt PWM tuân thủ chính xác thang đo `IOHWAB_DUTY_MAX = 1000u`.

---

## 🔗 BỘ LỜI GIẢI TOÀN DIỆN THAM KHẢO

👉 **[`docs/hands_on_tasks/solutions/02_OS_MCAL_Solutions.md`](solutions/02_OS_MCAL_Solutions.md)**  
*(Cung cấp 100% mã nguồn XML cấu hình gốc, file Header sinh ra đối soát, và mã nguồn C hoàn chỉnh).*
