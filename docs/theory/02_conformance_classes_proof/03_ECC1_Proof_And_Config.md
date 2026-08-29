# CHỨNG MINH CẤP ĐỘ 3: ECC1 (EXTENDED CONFORMANCE CLASS 1)
## Đa Nhiệm Hướng Sự Kiện (Event-Driven) Với Ngăn Xếp Riêng Biệt (Dedicated Stack)

---

### 1. ⚙️ CÁCH CẤU HÌNH TRONG `autosar.arxml` ĐỂ RA CẤP ĐỘ ECC1:

Để sinh ra cấu hình **ECC1**:
1. **Có ít nhất 1 Task chứa thẻ `<EventList>`** (Khai báo Extended Task).
2. **Mỗi Task phải có mức `Priority` riêng biệt** (không trùng nhau).
3. **Mọi Task đều có `Activation="1"`**.

```xml
<!-- autosar.arxml CẤU HÌNH CHUẨN ECC1 -->
<AUTOSAR>
  <OS>
    <General Conformance="ECC1" Status="EXTENDED" />
    <TaskList>
      <!-- Extended Task: Chờ sự kiện ngắt CAN, Priority 3, Activation 1 -->
      <Task Name="Task_CanRxEvent" Priority="3" Activation="1" Autostart="True" StackSize="1024" Schedule="FULL">
        <EventList>
          <Event Name="Event_CanFrameReceived" Mask="0x00000001" />
        </EventList>
      </Task>
      
      <!-- Basic Task: Chu kỳ 10ms, Priority 2, Activation 1 -->
      <Task Name="Task_10ms" Priority="2" Activation="1" Autostart="True" StackSize="512" Schedule="FULL" />
      
      <Task Name="TaskIdle" Priority="0" Activation="1" Autostart="True" StackSize="256" Schedule="FULL" />
    </TaskList>
  </OS>
</AUTOSAR>
```

---

### 2. 📄 MÃ C SINH RA TRONG `Os_Cfg.h` & `Os_Cfg.c`:

Khi toolchain [`GenOS.py: L192-L201`](../../as/com/as.tool/config.infrastructure.system/argen/GenOS.py#L192-L201) đọc cấu hình:
* `withEvt = True` $\longrightarrow$ **Sinh ra `#define EXTENDED_TASK`** và các định nghĩa `EVENT_MASK_*`.
* `multiPrio = False` $\longrightarrow$ Không sinh `MULTIPLY_TASK_PER_PRIORITY`.
* `multiAct = False` $\longrightarrow$ Không sinh `MULTIPLY_TASK_ACTIVATION`.

#### File `Os_Cfg.h` sinh ra:
```c
/* Os_Cfg.h (ECC1 Mode) */

#define EVENT_MASK_Task_CanRxEvent_Event_CanFrameReceived   0x01

#define EXTENDED_TASK   /* <── BẬT TÍNH NĂNG EXTENDED TASK & SỰ KIỆN EVENT */

#define TASK_ID_Task_CanRxEvent   0   /* priority = 3 */
#define TASK_ID_Task_10ms         1   /* priority = 2 */
#define TASK_ID_TaskIdle          2   /* priority = 0 */
#define TASK_NUM                  3
```

#### File `Os_Cfg.c` sinh ra:
```c
/* Os_Cfg.c (ECC1 Mode) */

/* BẮT BUỘC CÓ DEDICATED STACK VÀ BIẾN SỰ KIỆN CHO EXTENDED TASK */
static uint32_t Task_CanRxEvent_Stack[1024 / sizeof(uint32_t)];
static EventVarType Task_CanRxEvent_EventVar; /* Chứa biến .set và .wait */

static uint32_t Task_10ms_Stack[512 / sizeof(uint32_t)];

const TaskConstType TaskConstArray[TASK_NUM] =
{
    {
        .pStack       = Task_CanRxEvent_Stack,
        .stackSize    = sizeof(Task_CanRxEvent_Stack),
        .entry        = TaskMainTask_CanRxEvent,
        #ifdef EXTENDED_TASK
        .pEventVar    = &Task_CanRxEvent_EventVar, /* <── GẮN BIẾN SỰ KIỆN */
        #endif
        .name         = "Task_CanRxEvent",
        .initPriority = 3,
        .runPriority  = 3,
    },
    {
        .pStack       = Task_10ms_Stack,
        .stackSize    = sizeof(Task_10ms_Stack),
        .entry        = TaskMainTask_10ms,
        #ifdef EXTENDED_TASK
        .pEventVar    = NULL, /* Basic Task không có biến sự kiện */
        #endif
        .name         = "Task_10ms",
        .initPriority = 2,
        .runPriority  = 2,
    }
};
```

---

### 3. 🔍 BẰNG CHỨNG THỰC THI `WaitEvent()` TRONG `event.c`:

Trong file [`as/com/as.infrastructure/system/kernel/askar/kernel/event.c: L230-L268`](../../as/com/as.infrastructure/system/kernel/askar/kernel/event.c#L230-L268):
* Khi `Task_CanRxEvent` gọi `WaitEvent(0x01)`:
  * Kernel kiểm tra `pTaskVar->pConst->pEventVar != NULL` $\rightarrow$ Hợp lệ!
  * Kernel gán `pTaskVar->state = WAITING;`
  * Kernel lưu toàn bộ thanh ghi CPU vào `Task_CanRxEvent_Stack` và chuyển quyền điều khiển sang Task khác.
* Khi ngắt CAN đến và gọi `SetEvent(TASK_ID_Task_CanRxEvent, 0x01)`:
  * Kernel bật bit `set |= 0x01`.
  * Đưa `Task_CanRxEvent` từ `WAITING` trở lại `READY`.
  * Scheduler khôi phục Context từ Stack riêng và Task tiếp tục chạy ngay sau dòng `WaitEvent()`!
