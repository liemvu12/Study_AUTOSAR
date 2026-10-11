# CHỨNG MINH CẤP ĐỘ 1: BCC1 (BASIC CONFORMANCE CLASS 1)
## Cấu Hình Siêu Nhẹ Tối Ưu Cho Vi Điều Khiển Tài Nguyên Nhỏ (< 1KB RAM)

---

### 1. ⚙️ CÁCH CẤU HÌNH TRONG `autosar.arxml` ĐỂ RA CẤP ĐỘ BCC1:

Để dự án sinh ra mã nguồn chuẩn **BCC1**, trong file [`as/com/as.application/common/autosar.arxml`](../../as/com/as.application/common/autosar.arxml) phải thỏa mãn **3 điều kiện**:
1. **Không có bất kỳ thẻ `<EventList>` nào** trong tất cả các Task.
2. **Mỗi Task phải có mức `Priority` độc nhất**, không được trùng nhau (ví dụ: TaskA = 1, TaskB = 2, TaskC = 3).
3. **Mọi Task đều có `Activation="1"`**.

```xml
<!-- autosar.arxml CẤU HÌNH CHUẨN BCC1 -->
<AUTOSAR>
  <OS>
    <General Conformance="BCC1" Status="STANDARD" />
    <TaskList>
      <!-- Task 1: Basic Task chu kỳ 10ms, không có Event, Priority 2 -->
      <Task Name="Task_10ms" Priority="2" Activation="1" Autostart="True" StackSize="512" Schedule="NON" />
      
      <!-- Task 2: Basic Task chu kỳ 100ms, không có Event, Priority 1 -->
      <Task Name="Task_100ms" Priority="1" Activation="1" Autostart="True" StackSize="512" Schedule="NON" />
      
      <!-- Task 3: TaskIdle chạy khi rảnh rỗi, Priority 0 -->
      <Task Name="TaskIdle" Priority="0" Activation="1" Autostart="True" StackSize="256" Schedule="FULL" />
    </TaskList>
  </OS>
</AUTOSAR>
```

---

### 2. 📄 MÃ C SINH RA TRONG `Os_Cfg.h` & `Os_Cfg.c`:

Khi toolchain [`GenOS.py`](../../as/com/as.tool/config.infrastructure.system/argen/GenOS.py) đọc cấu hình trên:
* `withEvt = False` $\longrightarrow$ **KHÔNG sinh ra `#define EXTENDED_TASK`**.
* `multiPrio = False` $\longrightarrow$ **KHÔNG sinh ra `#define MULTIPLY_TASK_PER_PRIORITY`**.
* `multiAct = False` $\longrightarrow$ **KHÔNG sinh ra `#define MULTIPLY_TASK_ACTIVATION`**.

#### File `Os_Cfg.h` sinh ra:
```c
/* Os_Cfg.h (BCC1 Mode) */
#define TASK_ID_Task_10ms   0   /* priority = 2 */
#define TASK_ID_Task_100ms  1   /* priority = 1 */
#define TASK_ID_TaskIdle    2   /* priority = 0 */
#define TASK_NUM            3

/* KHÔNG CÓ BẤT KỲ ĐỊNH NGHĨA EVENT_MASK NÀO */
/* KHÔNG CÓ #define EXTENDED_TASK */
/* KHÔNG CÓ #define MULTIPLY_TASK_PER_PRIORITY */
/* KHÔNG CÓ #define MULTIPLY_TASK_ACTIVATION */
```

#### File `Os_Cfg.c` sinh ra:
```c
/* Os_Cfg.c (BCC1 Mode) */

/* CƠ CHẾ TIẾT KIỆM RAM: Dùng chung 1 vùng Stack duy nhất cho các Basic Task non-preemptive */
static uint32_t Task_SharedStack[512 / sizeof(uint32_t)];

const TaskConstType TaskConstArray[TASK_NUM] =
{
    {
        .pStack       = Task_SharedStack, /* DÙNG CHUNG STACK */
        .stackSize    = sizeof(Task_SharedStack),
        .entry        = TaskMainTask_10ms,
        /* .pEventVar hoàn toàn bị loại bỏ bởi preprocessor */
        .name         = "Task_10ms",
        .initPriority = 2,
        .runPriority  = 2,
    },
    {
        .pStack       = Task_SharedStack, /* DÙNG CHUNG STACK */
        .stackSize    = sizeof(Task_SharedStack),
        .entry        = TaskMainTask_100ms,
        .name         = "Task_100ms",
        .initPriority = 1,
        .runPriority  = 1,
    }
};
```

---

### 3. 🔍 BẰNG CHỨNG TRONG MÃ NGUỒN KERNEL `askar`:

1. **Loại bỏ 100% mã nguồn xử lý Event (`event.c`):**  
   File [`as/com/as.infrastructure/system/kernel/askar/kernel/event.c: L17 & L269`](../../as/com/as.infrastructure/system/kernel/askar/kernel/event.c#L17) được bọc bởi:
   ```c
   #ifdef EXTENDED_TASK
   /* Toàn bộ hàm SetEvent(), GetEvent(), WaitEvent(), ClearEvent() nằm ở đây */
   #endif /* EXTENDED_TASK */
   ```
   $\longrightarrow$ Trong chế độ **BCC1**, toàn bộ các hàm này **không được biên dịch vào Flash ROM (0 bytes ROM overhead)**!
2. **Thuật toán Scheduler siêu đơn giản $O(1)$:**  
   Vì không có trùng Priority, Scheduler trong [`sched-bubble.c: L42-L44`](../../as/com/as.infrastructure/system/kernel/askar/kernel/sched-bubble.c#L42-L44) sử dụng trực tiếp:
   ```c
   #define NEW_PRIORITY(prio) (prio)
   #define REAL_PRIORITY(prio) (prio)
   ```
   Không tốn phép tính dịch bit `SEQUENCE_SHIFT` hay mảng phụ `PrioSeqVal`.
