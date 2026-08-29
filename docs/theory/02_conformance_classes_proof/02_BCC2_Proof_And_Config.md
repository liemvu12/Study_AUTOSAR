# CHỨNG MINH CẤP ĐỘ 2: BCC2 (BASIC CONFORMANCE CLASS 2)
## Đa Nhiệm Cơ Sở Nâng Cao: Nhiều Task Chung Độ Ưu Tiên & Hàng Đợi Kích Hoạt (FIFO Queue)

---

### 1. ⚙️ CÁCH CẤU HÌNH TRONG `autosar.arxml` ĐỂ RA CẤP ĐỘ BCC2:

Để sinh ra cấu hình **BCC2**, trong file `autosar.arxml`:
1. **Không có thẻ `<EventList>`** (Vẫn là Basic Tasks).
2. **Có ít nhất 2 Task có mức `Priority` bằng nhau** (ví dụ: `Task_CanTx` và `Task_CanRx` đều có `Priority="5"`).
3. **Có ít nhất 1 Task có `Activation > 1`** (ví dụ: `Activation="5"` cho phép gửi 5 yêu cầu kích hoạt liên tiếp).

```xml
<!-- autosar.arxml CẤU HÌNH CHUẨN BCC2 -->
<AUTOSAR>
  <OS>
    <General Conformance="BCC2" Status="EXTENDED" />
    <TaskList>
      <!-- 2 Task này CÙNG CHUNG Priority = 5 và có Activation = 5 -->
      <Task Name="Task_CanTx" Priority="5" Activation="5" Autostart="False" StackSize="1024" Schedule="FULL" />
      <Task Name="Task_CanRx" Priority="5" Activation="5" Autostart="False" StackSize="1024" Schedule="FULL" />
      
      <Task Name="TaskIdle"   Priority="0" Activation="1" Autostart="True"  StackSize="512"  Schedule="FULL" />
    </TaskList>
  </OS>
</AUTOSAR>
```

---

### 2. 📄 MÃ C SINH RA TRONG `Os_Cfg.h` & `Os_Cfg.c`:

Khi toolchain [`GenOS.py: L140-L176`](../../as/com/as.tool/config.infrastructure.system/argen/GenOS.py#L140-L176) đọc cấu hình này:
* `multiPrio = True` $\longrightarrow$ **Sinh ra `#define MULTIPLY_TASK_PER_PRIORITY`** kèm `SEQUENCE_MASK` và `SEQUENCE_SHIFT`.
* `multiAct = True` $\longrightarrow$ **Sinh ra `#define MULTIPLY_TASK_ACTIVATION`**.
* `withEvt = False` $\longrightarrow$ Không sinh `EXTENDED_TASK`.

#### File `Os_Cfg.h` sinh ra:
```c
/* Os_Cfg.h (BCC2 Mode) */

#define PRIORITY_NUM 6
#define ACTIVATION_SUM 12

#define MULTIPLY_TASK_PER_PRIORITY   /* <── BẬT TÍNH NĂNG NHIỀU TASK TRÙNG PRIORITY */
#define SEQUENCE_MASK 0x7u           /* <── MẶT NẠ PHÂN XỬ THỨ TỰ FIFO */
#define SEQUENCE_SHIFT 3             /* <── DỊCH 3 BITS ĐỂ CHỨA THỨ TỰ KÍCH HOẠT */
#define MULTIPLY_TASK_ACTIVATION     /* <── BẬT HÀNG ĐỢI KÍCH HOẠT NHIỀU LẦN */

#define TASK_ID_Task_CanTx   0   /* priority = 5 */
#define TASK_ID_Task_CanRx   1   /* priority = 5 (TRÙNG ĐỘ ƯU TIÊN VỚI Task_CanTx!) */
#define TASK_ID_TaskIdle     2   /* priority = 0 */
#define TASK_NUM             3
```

---

### 3. 🔍 BẰNG CHỨNG THUẬT TOÁN FIFO SCHEDULER TRONG `sched-bubble.c`:

Trong file [`as/com/as.infrastructure/system/kernel/askar/kernel/sched-bubble.c: L37-L73`](../../as/com/as.infrastructure/system/kernel/askar/kernel/sched-bubble.c#L37-L73):

```c
/* as/com/as.infrastructure/system/kernel/askar/kernel/sched-bubble.c */

#ifdef MULTIPLY_TASK_PER_PRIORITY
/* Khi 2 Task có cùng Priority (ví dụ Priority 5), thuật toán nhúng một số thứ tự giảm dần
 * PrioSeqVal vào 3 bits cuối: NEW_PRIORITY = (5 << 3) | (--PrioSeqVal[5] & 0x7)
 * Task nào được Activate trước sẽ có giá trị Sequence lớn hơn -> Nằm ở đỉnh Binary Heap -> Chạy trước! */
#define NEW_PRIORITY(prio) (((uint16)(prio)<<SEQUENCE_SHIFT)|((--PrioSeqVal[prio])&SEQUENCE_MASK))
#endif
```

* **Hàng đợi kích hoạt (`task.c: L170-L178`):**  
  Khi `ActivateTask(Task_CanTx)` được gọi liên tiếp 3 lần:
  ```c
  #ifdef MULTIPLY_TASK_ACTIVATION
  if(pTaskVar->activation < pTaskVar->pConst->maxActivation)
  {
      pTaskVar->activation++; /* Tăng biến đếm yêu cầu kích hoạt */
      Sched_AddReady(TaskID); /* Đưa tiếp vào hàng đợi chờ thực thi */
  }
  #endif
  ```
  $\longrightarrow$ Task sẽ tự động được chạy lại đúng 3 lần mà không bị lỗi `E_OS_LIMIT`!
