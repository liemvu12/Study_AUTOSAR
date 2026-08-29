# TASK PLAN Chuyên Đề 02: AUTOSAR OS & MCAL

## Cấu trúc Repository Thực Tế
- **Hệ điều hành AUTOSAR OS chính:** `as/com/as.infrastructure/system/kernel/askar/` (Chuẩn OSEK/AUTOSAR OS)
- **Các OS thay thế (Alternatives):** `as/com/as.infrastructure/system/kernel/` (trampoline, freertos, toppers_osek...)
- **Mục tiêu mô phỏng chính 1 (QEMU ARM Cortex-M3):** `as/com/as.application/board.lm3s6965evb/` (Target `lm3s6965evb`)
  - **MCAL Driver:** `as/com/as.infrastructure/arch/lm3s/mcal/` (`Mcu.c`, `Can.c`) & `as/com/as.infrastructure/arch/common/mcal/SCan.c`
  - **Lệnh Build:** `$env:BOARD="lm3s6965evb"; $env:RELEASE="ascore"; scons`
- **Mục tiêu mô phỏng chính 2 (PC POSIX Simulator):** `as/com/as.application/board.posix/simulator/simulator.c`
  - **MCAL Driver:** `as/com/as.infrastructure/arch/posix/mcal/` (`Dio.c`, `Port.c`, `Can.c`, `Mcu.c`, `Flash.c`)
  - **Lệnh Build:** `scons --board=posix`
- **Mục tiêu phần cứng mở rộng (Physical STM32 Board):** `as/com/as.application/board.stm32f107vc/` (`arch/stm32f1/mcal/`)

---

## TASK 2.1: Build OSEK OS từ Source Code (~2h, Beginner)
**Mục tiêu (Objective):** Compile Trampoline OS cho môi trường POSIX simulator để làm quen với hệ thống build.
**Lệnh thực thi (Commands):**
```bash
cd as
scons --board=posix
```
**Nhiệm vụ:**
1. Khảo sát các file mã nguồn cốt lõi của OS như `Os.h`, `Os.c` nằm trong thư mục `as/com/as.infrastructure/system/kernel/`.
2. Đọc hiểu và phân tích các API cốt lõi của tiêu chuẩn OSEK/VDX:
   - `ActivateTask`: Kích hoạt một task từ trạng thái Suspended sang Ready.
   - `ChainTask`: Kết thúc task hiện tại và kích hoạt một task khác (giảm overhead của scheduler).
   - `TerminateTask`: Kết thúc task hiện tại đang chạy.
   - `WaitEvent`: Chuyển Extended Task sang trạng thái Waiting để chờ một sự kiện (Event).
   - `SetEvent`: Kích hoạt một sự kiện cho một task khác.
   - `GetResource` / `ReleaseResource`: Chiếm dụng và giải phóng tài nguyên dùng chung, đi kèm cơ chế OSEK Priority Ceiling Protocol (PCP).
**Tiêu chí thành công (Success):** Quá trình build sinh ra file binary thành công, không phát sinh lỗi (errors).
**Các lỗi thường gặp (Pitfalls):** Thiếu các package Python cần thiết cho hệ thống build, hoặc phiên bản SCons không tương thích (đòi hỏi cấu hình đúng Python environment).

---

## TASK 2.2: Create Basic Task — Periodic Processing (~3h, Intermediate)
**Mục tiêu (Objective):** Khởi tạo một Basic Task thực thi định kỳ mỗi 100ms trong môi trường POSIX simulator.
**Các file cần chỉnh sửa (Files edit):**
- Cập nhật build script: `as/com/as.application/board.posix/SConscript`
- Tạo file nguồn mới: `as/com/as.application/board.posix/simulator/app_tasks.c`

**Cấu hình OIL (OIL config snippet cho Trampoline OS):**
```oil
ALARM Alarm_Task100ms {
    COUNTER = SystemTimer;
    ACTION = ACTIVATETASK {
        TASK = Task_Periodic_100ms;
    };
    AUTOSTART = TRUE {
        ALARMTIME = 100;
        CYCLETIME = 100;
        APPMODE = AppMode1;
    };
};

TASK Task_Periodic_100ms {
    PRIORITY = 2;
    AUTOSTART = FALSE;
    ACTIVATION = 1;
    SCHEDULE = NON;
};
```

**Mã nguồn mẫu (Code example):** Task đơn giản thực hiện toggle biến đếm (counter) và in ra giao diện UART/Console.
```c
#include "Os.h"
#include <stdio.h>

static uint32_t task_counter = 0;

TASK(Task_Periodic_100ms)
{
    task_counter++;
    printf("Task_Periodic_100ms dang chay, counter = %u\n", task_counter);
    TerminateTask();
}
```
*Lưu ý:* Cấu hình Alarm trong OIL sẽ tự động kích hoạt (activate) task này định kỳ mỗi 100ms (dựa trên SystemTimer).
**Tiêu chí thành công (Success):** Terminal in ra dòng log `printf` chính xác mỗi 100ms khi chạy POSIX simulator.

---

## TASK 2.3: Extended Task — Event-Driven CAN Reception (~4h, Intermediate)
**Mục tiêu (Objective):** Khởi tạo một Extended Task với nhiệm vụ chờ sự kiện (Event) từ ngắt nhận CAN (CAN Rx ISR) thay vì sử dụng phương pháp vòng lặp kiểm tra (polling).
**Lý thuyết cốt lõi:** Extended Task khác biệt với Basic Task ở trạng thái *Waiting*. Extended Task yêu cầu phân bổ ngăn xếp (stack) riêng biệt biệt lập nhằm lưu trữ ngữ cảnh thực thi (context) khi gọi hàm `WaitEvent()`, cho phép task "ngủ" chờ sự kiện mà không chiếm dụng CPU, trong khi Basic Task dùng chung stack với hệ thống.

**Cấu hình OIL (OIL config snippet):**
```oil
EVENT Event_CanRx { MASK = AUTO; };

TASK Task_CanRx_Handler {
    PRIORITY = 5;
    AUTOSTART = TRUE { APPMODE = AppMode1; };
    ACTIVATION = 1;
    SCHEDULE = FULL;
    EVENT = Event_CanRx;
};

ISR ISR_CanRx {
    CATEGORY = 2;
    PRIORITY = 10;
};
```

**Mã nguồn mẫu (Code example):** Sử dụng WaitEvent kết hợp Alarm watchdog bảo vệ chống kẹt (timeout).
```c
#include "Os.h"
#include <stdio.h>

TASK(Task_CanRx_Handler)
{
    EventMaskType event_mask;
    
    while(1)
    {
        /* Bắt đầu chờ sự kiện CAN Rx */
        WaitEvent(Event_CanRx);
        
        /* Đã nhận được sự kiện, lấy ra mask */
        GetEvent(Task_CanRx_Handler, &event_mask);
        ClearEvent(Event_CanRx);
        
        if (event_mask & Event_CanRx)
        {
            printf("Da nhan duoc ban tin CAN!\n");
            /* Xử lý CAN frame tại đây */
        }
    }
}

/* Ngắt nhận CAN (ISR Category 2) */
ISR(ISR_CanRx)
{
    /* Đọc thanh ghi phần cứng CAN, xác nhận ngắt */
    /* Kích hoạt sự kiện cho Extended Task */
    SetEvent(Task_CanRx_Handler, Event_CanRx);
}
```
**Phân tích Hiệu suất:** So sánh đo lường tải CPU (CPU load). Giải pháp Polling chạy vòng lặp `while(1)` tiêu tốn 100% CPU. Giải pháp Event-Driven cho phép task vào trạng thái sleep (0% CPU usage cho task này khi không có sự kiện), giúp tiết kiệm năng lượng và tài nguyên hệ thống xử lý các task ưu tiên thấp khác.
**Tiêu chí thành công (Success):** Task `Task_CanRx_Handler` chỉ thức dậy (wake up) khi ISR phát sự kiện (SetEvent), CPU load giảm thiểu rõ rệt.

---

## TASK 2.4: Resource & Priority Ceiling — Prevent Priority Inversion (~3h, Advanced)
**Mục tiêu (Objective):** Thiết lập 3 Tasks (Low, Medium, High priority) chia sẻ một tài nguyên dùng chung (Resource) nhằm kiểm chứng và vết (trace) hoạt động của giao thức Priority Ceiling Protocol (PCP).

**Cấu hình OIL:**
```oil
RESOURCE Shared_Data_Res { RESOURCEPROPERTY = STANDARD; };

TASK Task_Low { PRIORITY = 1; SCHEDULE = FULL; RESOURCE = Shared_Data_Res; };
TASK Task_Mid { PRIORITY = 2; SCHEDULE = FULL; };
TASK Task_High { PRIORITY = 3; SCHEDULE = FULL; RESOURCE = Shared_Data_Res; };
```

**Mã nguồn mẫu (Code example):** Trace thứ tự thực thi (execution order).
```c
#include "Os.h"
#include <stdio.h>

TASK(Task_Low)
{
    printf("[LOW] Start\n");
    GetResource(Shared_Data_Res); /* Ưu tiên tự động nâng lên Priority Ceiling (3) */
    printf("[LOW] Got Resource, executing critical section...\n");
    
    /* Mô phỏng ngắt kích hoạt High Task và Mid Task ở đây */
    ActivateTask(Task_High);
    ActivateTask(Task_Mid);
    
    printf("[LOW] Releasing Resource\n");
    ReleaseResource(Shared_Data_Res); /* Ưu tiên trở về 1, hệ thống chuyển ngữ cảnh sang High Task */
    printf("[LOW] End\n");
    TerminateTask();
}

TASK(Task_Mid)
{
    printf("[MID] Executing\n");
    TerminateTask();
}

TASK(Task_High)
{
    printf("[HIGH] Start\n");
    printf("[HIGH] Try GetResource\n");
    GetResource(Shared_Data_Res);
    printf("[HIGH] Got Resource\n");
    ReleaseResource(Shared_Data_Res);
    printf("[HIGH] End\n");
    TerminateTask();
}
```
**Chứng minh:** Nếu không có Resource (cơ chế mutex thông thường), Task High sẽ bị block bởi Task Low đang giữ khóa, và Task Mid (có quyền ưu tiên trung bình không cần khóa) sẽ cướp quyền CPU từ Task Low, dẫn đến việc Task High bị trì hoãn vô thời hạn bởi Task Mid (hiện tượng Đảo ngược mức ưu tiên - Priority Inversion). Khi sử dụng cơ chế OSEK PCP bằng API Get/ReleaseResource, mức ưu tiên của Task Low sẽ được đẩy lên ngang với Task High trong thời gian giữ Resource, ngăn chặn Task Mid ngắt ngang.
**Tiêu chí thành công (Success):** Task ưu tiên cao (High task) thực thi mượt mà, không bị chặn gián tiếp bởi Task ưu tiên trung bình (Medium task) khi dùng chung tài nguyên với Task ưu tiên thấp (Low task). Dòng log hiển thị đúng trình tự.

---

## TASK 2.5: MCAL Port/Dio — Read GPIO Input (~2h, Intermediate)
**Mục tiêu (Objective):** Phân tích mã nguồn lớp MCAL bằng cách đọc hiểu file `as/com/as.infrastructure/arch/lm3s/mcal/Mcu.c` (hoặc `arch/posix/mcal/Dio.c`, `arch/stm32f1/mcal/Dio.c`).
**Nhiệm vụ:**
- Tìm hiểu đặc tả các API tiêu chuẩn của AUTOSAR MCAL: `Port_Init()`, `Dio_ReadChannel()`, `Dio_WriteChannel()`.
- Phân tích sự phân tách trách nhiệm (separation of concerns): `Port` đảm nhận khởi tạo chức năng của chân (I/O, alternate function, pull-up/down, tốc độ), trong khi `Dio` chịu trách nhiệm đọc/ghi mức logic (High/Low) tại thời gian chạy (runtime). Do đó hàm `Port_Init()` buộc phải chạy trước hàm của module `Dio`.

**Mã nguồn mẫu (Code example):** Mô phỏng đọc trạng thái nút nhấn và điều khiển LED dựa trên các API.
```c
#include "Port.h"
#include "Dio.h"

/* Cấu hình các Port và Channel đã được định nghĩa trong cấu hình MCAL */
#define BUTTON_CHANNEL  DIO_CHANNEL_PA0
#define LED_CHANNEL     DIO_CHANNEL_PC13

void App_Init(void)
{
    /* 1. Khởi tạo chức năng các chân GPIO (Clock, Mode, Pull-up/Pull-down) */
    Port_Init(&Port_Config);
}

void App_Process_IO(void)
{
    Dio_LevelType btn_state;
    
    /* 2. Đọc mức logic của nút nhấn (Input) */
    btn_state = Dio_ReadChannel(BUTTON_CHANNEL);
    
    /* 3. Xử lý logic và ghi trạng thái ra LED (Output) */
    if (btn_state == STD_HIGH)
    {
        Dio_WriteChannel(LED_CHANNEL, STD_LOW);  /* Bật LED (Active Low) */
    }
    else
    {
        Dio_WriteChannel(LED_CHANNEL, STD_HIGH); /* Tắt LED */
    }
}
```
**Tiêu chí thành công (Success):** Code compile thành công qua SCons, người học giải thích được rõ ràng chức năng khác biệt giữa Port API và Dio API, cũng như trình tự bắt buộc của chúng.

---

## TASK 2.6 (Extension): Stack Overflow Detection (~3h, Advanced)
**Mục tiêu (Objective):** Cố ý cấu hình một task có kích thước bộ nhớ ngăn xếp (stack size) quá nhỏ nhằm gây tràn, sau đó phát triển và áp dụng cơ chế phát hiện tràn ngăn xếp (Stack Overflow) bằng kỹ thuật Stack Watermark (Pattern Fill).
**Phương pháp (Method):**
1. Ghi đè toàn bộ phân vùng bộ nhớ stack của task với một chuỗi giá trị pattern đặc biệt (VD: `0xDEADBEEF` hoặc `0xAA55AA55`) ở giai đoạn khởi tạo OS.
2. Kiểm tra phần ranh giới (boundary) hoặc đỉnh vùng stack lúc runtime định kỳ (thường là trong hook function như `PreTaskHook` hoặc Timer ISR). Nếu đoạn pattern tại biên bị thay đổi thành dữ liệu khác, chứng tỏ stack đã phát triển chạm đáy (hoặc vượt ranh giới) gây tràn.

**Mã nguồn mẫu (Code example):**
```c
#include "Os.h"
#include <stdio.h>

#define STACK_PATTERN 0xDEADBEEF
extern uint32_t Task_SmallStack_Bottom[]; /* Con trỏ tới phần đáy (địa chỉ thấp nhất) của stack */

void Os_FillStack(uint32_t* stack_start, uint32_t size_in_words)
{
    for(uint32_t i = 0; i < size_in_words; i++)
    {
        stack_start[i] = STACK_PATTERN;
    }
}

/* Sử dụng OS Hook để kiểm tra tràn stack trước khi chuyển context */
void PreTaskHook(void)
{
    TaskType current_task;
    GetTaskID(&current_task);
    
    if (current_task == Task_SmallStack)
    {
        /* Kiểm tra 4 từ đầu tiên (đáy ngăn xếp tùy kiến trúc) */
        if (Task_SmallStack_Bottom[0] != STACK_PATTERN ||
            Task_SmallStack_Bottom[1] != STACK_PATTERN)
        {
            printf("FATAL ERROR: Stack Overflow detected in Task_SmallStack!\n");
            /* Gọi ErrorHook hoặc Halt hệ thống, lưu Dump để debug */
            ShutdownOS(E_OS_STACKFAULT);
        }
    }
}

TASK(Task_SmallStack)
{
    volatile uint32_t dummy_buffer[100]; /* Cố tình cấp phát vùng nhớ lớn trên stack để gây tràn */
    dummy_buffer[0] = 1;
    dummy_buffer[99] = 2;
    
    /* Code xử lý ... */
    
    TerminateTask();
}
```
**Tiêu chí thành công (Success):** Cơ chế phần mềm phát hiện được tình trạng tràn stack và dừng hệ thống cảnh báo (Halt/Error log) trước khi hệ thống chạy sai lệnh và crash (HardFault) một cách không kiểm soát do corrupt bộ nhớ.
