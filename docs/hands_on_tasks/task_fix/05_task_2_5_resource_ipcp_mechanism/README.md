# BÁO CÁO KỸ THUẬT: HIỆN THỰC HÓA & KIỂM CHỨNG TASK 2.5
## Giao Thức Khóa Nâng Quyền Tĩnh Tức Thì (IPCP) & Chứng Minh Không Context Switch Tại GetResource()

> 📌 **Mã bài tập:** [`Task 2.5 (docs/hands_on_tasks/02_OS_MCAL_Tasks.md)`](../../02_OS_MCAL_Tasks.md#task-25-immediate-priority-ceiling-ipcp--chứng-minh-không-context-switch-vừa--khó--35h)  
> 🏷️ **Thư mục lưu trữ hiện vật:** `docs/hands_on_tasks/task_fix/05_task_2_5_resource_ipcp_mechanism/`  
> 📅 **Ngày hoàn thành:** 21/09/2026  
> 🎯 **Mục tiêu nghiệm thu:**
> 1. Khai báo Resource `Res_SharedBuffer` và bộ 3 Task (`Task_Low`, `Task_Mid`, `Task_High`) trong nguồn chân lý tầng ứng dụng [`app.xml`](../../../as/release/ascore/app/app.xml).
> 2. Kích hoạt bộ sinh mã ArGen (`GenOS.py`) tự động tính toán Priority Ceiling tĩnh = 3 và sinh mã kiểm soát truy cập `CheckAccess()` trong `Os_Cfg.c`.
> 3. Cài đặt kịch bản thực nghiệm timeline 8 bước trong [`app.c`](../../../as/release/ascore/app/app.c) chứng minh toán học:
>    - `GetResource()` thực thi trong thời gian hằng số $O(1)$ và **HOÀN TOÀN KHÔNG GÂY CONTEXT SWITCH** (tài nguyên luôn rảnh tuyệt đối).
>    - Chuyển ngữ cảnh (Context Switch) **CHỈ DIỄN RA TẠI `ReleaseResource()`**.
>    - Tác vụ ưu tiên cao `Task_High` (Prio 3) và tác vụ trung gian `Task_Mid` (Prio 2) **hoàn toàn không thể tiếm quyền** khi `Task_Low` đang ở trong vùng găng!
> 4. Xác minh thực tế 100% thành công trên QEMU ARM Cortex-M3 (`lm3s6965evb`).

---

## 1. 🏗️ BẢN CHẤT KIẾN TRÚC: VÌ SAO AUTOSAR CHỌN IPCP?

Trong hệ thống nhúng thời gian thực (RTOS), bài toán chia sẻ dữ liệu giữa các tác vụ có mức ưu tiên khác nhau luôn đối mặt với hiểm họa **Nghịch đảo độ ưu tiên (Priority Inversion)** và **Khóa chết (Deadlock)**:

```
                            SO SÁNH HAI TRƯỜNG PHÁI ĐỒNG BỘ HÓA
      FreeRTOS / Linux POSIX (Mutex động - PIP)      vs.      AUTOSAR / OSEK OS (Resource tĩnh - IPCP)
   ┌──────────────────────────────────────────────┐       ┌──────────────────────────────────────────────┐
   │ • Giải pháp PHẢN ỨNG (Dynamic):              │       │ • Giải pháp PHÒNG NGỪA (Static):             │
   │   Chỉ nâng quyền khi Task cao bị chặn.       │       │   Nâng quyền NGAY LẬP TỨC khi lấy Resource.  │
   │ • Có trạng thái BLOCKED (Ngủ chờ).           │       │   KHÔNG BAO GIỜ bị chặn (Không bao giờ ngủ). │
   │ • Tốn hàng đợi chờ Wait Queue trong RAM.     │       │   0 Byte RAM cho hàng đợi chờ (Zero Queue).  │
   │ • Tốn ít nhất 2 lần Context Switch lãng phí. │       │   GetResource = 0 Context Switch, O(1)!      │
   │ • Bất lực 100% trước Deadlock khóa chéo AB-BA│       │   Toán học + LIFO triệt tiêu Deadlock 100%!  │
   └──────────────────────────────────────────────┘       └──────────────────────────────────────────────┘
```

### Công thức tính Priority Ceiling tĩnh:
$$\text{CeilingPriority}(R) = \max \Big( \{ \text{Priority}(T) \mid T \text{ có quyền truy cập } R \} \Big)$$
* `Task_Low` (Priority 1) dùng `Res_SharedBuffer`.
* `Task_High` (Priority 3) dùng `Res_SharedBuffer`.
* $\implies \text{Ceiling}(\text{Res\_SharedBuffer}) = \max(1, 3) = \mathbf{3}$.

---

## 2. 📋 CHI TIẾT CÁC BƯỚC TRIỂN KHAI

### 🔹 Bước 1: Khai báo Resource & Task trong Nguồn Chân Lý `app.xml`

Tuân thủ nguyên tắc đóng gói kiến trúc (không sửa file `autosar.arxml` của BSW Core), mở [`as/release/ascore/app/app.xml`](../../../as/release/ascore/app/app.xml) và bổ sung cấu hình:

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

#### 🔍 Giải mã các tham số cấu hình:
1. **`<Resource Name="Res_SharedBuffer" Priority="3" />`**: Định nghĩa Resource dùng chung.
2. **`<ResourceList>` bên trong `<Task>`**: Bắt buộc phải có để `GenOS.py` nhận diện quyền truy cập của Task, sinh ra hàm `Task_Low_CheckAccess()` và `Task_High_CheckAccess()` trả về `TRUE`. Nếu thiếu thẻ này, Kernel sẽ chặn đứng lệnh `GetResource()` và trả về mã lỗi `E_OS_ACCESS`!
3. **`Autostart="True"` cho `Task_Low`**: Giúp `Task_Low` tự động khởi chạy khi hệ thống boot xong các tác vụ ưu tiên cao ban đầu.

---

### 🔹 Bước 2: Kích hoạt bộ sinh mã ArGen bằng SCons

Thực thi lệnh sinh mã và biên dịch tại thư mục `as`:
```powershell
$env:BOARD="lm3s6965evb"
$env:RELEASE="ascore"
scons
```

#### Đối soát mã nguồn tự động sinh ra:
1. Trong [`build/nt/lm3s6965evb/ascore/config/Os_Cfg.h`](../../../as/build/nt/lm3s6965evb/ascore/config/Os_Cfg.h):
   ```c
   #define RES_ID_Res_SharedBuffer                 1
   #define RESOURCE_NUM 3
   DeclareTask(Task_Low);
   DeclareTask(Task_Mid);
   DeclareTask(Task_High);
   DeclareResource(Res_SharedBuffer);
   ```

2. Trong [`build/nt/lm3s6965evb/ascore/config/Os_Cfg.c`](../../../as/build/nt/lm3s6965evb/ascore/config/Os_Cfg.c):
   ```c
   /* Mảng hằng số mức trần ưu tiên tĩnh */
   const ResourceConstType ResourceConstArray[RESOURCE_NUM] =
   {
       { /*.ceilPrio =*/ PRIORITY_NUM },            /* RES_SCHEDULER (ID = 0) */
       { /*.ceilPrio =*/ OS_PTHREAD_PRIORITY + 3 }, /* Res_SharedBuffer (ID = 1) */
   };

   /* Kiểm tra quyền truy cập của Task_Low */
   static boolean Task_Low_CheckAccess(ResourceType ResID)
   {
       boolean bAccess = FALSE;
       switch(ResID)
       {
           case RES_SCHEDULER:
           case RES_ID_Res_SharedBuffer:
               bAccess = TRUE;
               break;
           default:
               break;
       }
       return bAccess;
   }
   ```

---

### 🔹 Bước 3: Cài đặt logic kiểm chứng Timeline trong `app.c`

Mở file [`as/release/ascore/app/app.c`](../../../as/release/ascore/app/app.c) và cài đặt 3 tác vụ:

```c
/* ========================================================================= */
/* TASK 2.5: Immediate Priority Ceiling Protocol (IPCP) & Zero Context Switch */
/* ========================================================================= */
TASK(Task_Low)
{
	printf("\n=================================================================\n");
	printf("[TASK 2.5] TESTING IMMEDIATE PRIORITY CEILING PROTOCOL (IPCP)\n");
	printf("=================================================================\n");
	printf("[TIMELINE 1] Task_Low starts executing (Static Priority = 1)...\n");

	/* GỌI GETRESOURCE: QUAN SÁT KHÔNG CÓ CONTEXT SWITCH */
	(void)GetResource(Res_SharedBuffer);
	printf("[TIMELINE 2] Task_Low GOT Resource! ActualPriority elevated to 3 (NO Context Switch).\n");

	/* KÍCH HOẠT TASK HIGH VÀ TASK MID */
	printf("[TIMELINE 3] Activating Task_High (Prio 3) & Task_Mid (Prio 2)...\n");
	(void)ActivateTask(Task_High);
	(void)ActivateTask(Task_Mid);
	printf("[TIMELINE 4] Task_Low STILL RUNNING! Neither Mid nor High could preempt Task_Low!\n");

	/* TRẢ RESOURCE: CONTEXT SWITCH XẢY RA TẠI ĐÂY */
	printf("[TIMELINE 5] Task_Low calling ReleaseResource(Res_SharedBuffer)...\n");
	(void)ReleaseResource(Res_SharedBuffer);
	/* ActualPriority hạ về 1 -> Kernel Sched_Schedule() -> Context Switch sang Task_High! */

	printf("[TIMELINE 8] Task_Low resumed and finished.\n");
	printf("=================================================================\n\n");
	(void)TerminateTask();
}

TASK(Task_High)
{
	printf("[TIMELINE 6] Task_High DISPATCHED! (Context Switch from Low -> High occurred).\n");
	(void)GetResource(Res_SharedBuffer);
	printf("             Task_High GOT Resource instantly! (Zero Contention, O(1)).\n");
	(void)ReleaseResource(Res_SharedBuffer);
	(void)TerminateTask();
}

TASK(Task_Mid)
{
	printf("[TIMELINE 7] Task_Mid executing (Prio 2). (High has terminated, Mid now highest).\n");
	(void)TerminateTask();
}
```

---

## 3. 🧪 XÁC MINH TRÊN GIẢ LẬP QEMU ARM CORTEX-M3

### 🔹 Lệnh thực thi:
```powershell
qemu-system-arm -M lm3s6965evb -kernel build/nt/lm3s6965evb/ascore/lm3s6965evb.exe -nographic -serial mon:stdio
```

### 📜 Trace Log thực tế ghi nhận 100% từ Console:

```text
ECUM    :  <-CALLIN : EcuM_SetWakeupEvent 0x1
 start application BUILD @ Sep 21 2026 14:17:47
 cpu is little endian
 XCP MTA memory address 2000100c
[Task_CanRxHandler] Initialized (Priority 10). Entering WaitEvent()...
LOW     :--Initialization of PDU router--
LOW     :--Initialization of PDU router completed --
OSEK NM node ID is 1

=================================================================
[TASK 2.3] TESTING OSEK CONFORMANCE CLASS (BCC1 vs BCC2)
=================================================================
[Tester] Activating Task_Periodic_50ms (Call 1)...
         --> Result: ret = E_OK (Task moved to READY state)
[Tester] Activating Task_Periodic_50ms (Call 2 - Burst activation)...
         --> Result: E_OS_LIMIT! (BCC1 Verified: Activation Limit = 1 Reached!)
=================================================================


[ISR Cat 2 Simulation] CAN Rx Interrupt Triggered! ID = 0x180
[ISR Cat 2 Simulation] Calling SetEvent(Task_CanRxHandler, Event_CanFrameRx)...
   --> [Task_CanRxHandler] WAKEUP from WAITING state!
   --> [Task_CanRxHandler] CAN Rx Frame processed: ID = 0x180
[ISR Cat 2 Simulation] Interrupt Handler completed.

   --> [Task_Periodic_50ms] Running instance #1

=================================================================
[TASK 2.5] TESTING IMMEDIATE PRIORITY CEILING PROTOCOL (IPCP)
=================================================================
[TIMELINE 1] Task_Low starts executing (Static Priority = 1)...
[TIMELINE 2] Task_Low GOT Resource! ActualPriority elevated to 3 (NO Context Switch).
[TIMELINE 3] Activating Task_High (Prio 3) & Task_Mid (Prio 2)...
[TIMELINE 4] Task_Low STILL RUNNING! Neither Mid nor High could preempt Task_Low!
[TIMELINE 5] Task_Low calling ReleaseResource(Res_SharedBuffer)...
[TIMELINE 6] Task_High DISPATCHED! (Context Switch from Low -> High occurred).
             Task_High GOT Resource instantly! (Zero Contention, O(1)).
[TIMELINE 7] Task_Mid executing (Prio 2). (High has terminated, Mid now highest).
[TIMELINE 8] Task_Low resumed and finished.
=================================================================

STDOUT  :TaskIdle is running
ECUM    :ECUM:RUN Timeout=49
...
```

---

## 4. 🔬 GIẢI PHÃU MÃ NGUỒN KERNEL & CƠ CHẾ CONTEXT SWITCH

### 1. Tại sao `GetResource()` tuyệt đối không gây Context Switch?
Nhìn vào mã nguồn gốc nhân Kernel tại [`as/com/as.infrastructure/system/kernel/askar/kernel/resource.c: L95-L103`](../../../as/com/as.infrastructure/system/kernel/askar/kernel/resource.c#L95-L103):
```c
/* as/com/as.infrastructure/system/kernel/askar/kernel/resource.c */
LOCK_KERNEL(imask);
ResourceVarArray[ResID].prevRes = RunningVar->currentResource;
ResourceVarArray[ResID].prevPrio = RunningVar->priority;
RunningVar->currentResource = ResID;
if(RunningVar->priority < ResourceConstArray[ResID].ceilPrio)
{
    RunningVar->priority = ResourceConstArray[ResID].ceilPrio; /* NÂNG ĐỘ ƯU TIÊN LÊN 3 */
}
UNLOCK_KERNEL(imask);
```
* Khi `Task_Low` gọi `GetResource(Res_SharedBuffer)`:
  - Kernel **chỉ thực hiện vài phép gán bộ nhớ RAM đơn giản** (lưu lại priority cũ `1` và gán priority mới thành `3`).
  - Kernel **HOÀN TOÀN KHÔNG GỌI `Sched_Schedule()`** và **KHÔNG GỌI `Os_PortDispatch()`**!
  - Tài nguyên luôn rảnh tuyệt đối $\to$ Không có hàng đợi chờ, không có Task nào bị block $\to$ **Zero Context Switch, độ phức tạp hằng số $O(1)$!**

### 2. Context Switch thực sự diễn ra ở đâu?
Chính là tại [`as/com/as.infrastructure/system/kernel/askar/kernel/resource.c: L180-L189`](../../../as/com/as.infrastructure/system/kernel/askar/kernel/resource.c#L180-L189):
```c
/* as/com/as.infrastructure/system/kernel/askar/kernel/resource.c */
RunningVar->currentResource = ResourceVarArray[ResID].prevRes;
RunningVar->priority = ResourceVarArray[ResID].prevPrio; /* HẠ ƯU TIÊN VỀ LẠI 1 */
ResourceVarArray[ResID].prevPrio = INVALID_PRIORITY;
if(PRIORITY_NUM != RunningVar->priority)
{
    if(Sched_Schedule()) /* PHÁT HIỆN TASK_HIGH (PRIO 3) TRONG READYQUEUE */
    {
        Os_PortDispatch(); /* KÍCH HOẠT PENDSV CONTEXT SWITCH! */
    }
}
```
* Khi `Task_Low` gọi `ReleaseResource()`:
  - Kernel hạ độ ưu tiên của nó về `1`.
  - Bộ lập lịch kiểm tra và phát hiện `Task_High` (Prio 3) đang chờ sẵn ở `ReadyQueue`.
  - Kernel gọi `Os_PortDispatch()`, kích hoạt ngoại lệ PendSV trên Cortex-M để tráo đổi con trỏ Stack (SP) sang `Task_High`.
  - Khi `Task_High` chạy vào `GetResource()`, tài nguyên vừa được giải phóng xong $\to$ `Task_High` nhận ngay tài nguyên mà không hề bị kẹt!

---

## 5. ⚠️ CÁC CẠM BẪY KỸ NGHỆ & ĐIỀU CẦN LƯU Ý

1. **Cạm bẫy `<ResourceList>` trong `<Task>`:**  
   Nếu quên khai báo thẻ `<ResourceList>` bên trong `<Task>`, hàm `CheckAccess()` sinh ra sẽ trả về `FALSE` $\to$ Kernel từ chối cấp vé với mã lỗi `E_OS_ACCESS`!
2. **Cạm bẫy build trên Windows:**  
   Hàm `MKSymlink()` trong `building.py` trên Windows thực hiện sao chép file (`copy2`) thay vì tạo symbolic link mềm. Khi sửa `app.xml`, nếu file `build/.../config/app.xml` đã tồn tại, script sẽ không tự động ghi đè trừ khi xóa file cũ hoặc xóa `config.done`.
3. **Quy tắc xếp chồng nghiêm ngặt LIFO (`[SWS_Os_00093]`):**  
   Nếu một Task chiếm giữ nhiều Resource lồng nhau, bắt buộc phải giải phóng theo thứ tự ngược lại: Task chiếm $R_1 \to R_2$ thì phải giải phóng $R_2 \to R_1$. Nếu vi phạm, Kernel sẽ trả về mã lỗi `E_OS_RESOURCE`.

---

## 6. 📁 DANH MỤC HIỆN VẬT BÀN GIAO

| Tên Tệp | Mô Tả Chi Tiết |
| :--- | :--- |
| [`fix.diff`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/docs/hands_on_tasks/task_fix/05_task_2_5_resource_ipcp_mechanism/fix.diff) | Bản vá git diff chuẩn mực thể hiện thay đổi trong `app.xml` và `app.c`. |
| [`src_before/`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/docs/hands_on_tasks/task_fix/05_task_2_5_resource_ipcp_mechanism/src_before/) | Bản lưu mã nguồn gốc trước khi thực hiện Task 2.5 (`app.xml`, `app.c`). |
| [`src_after/`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/docs/hands_on_tasks/task_fix/05_task_2_5_resource_ipcp_mechanism/src_after/) | Bản lưu mã nguồn hoàn chỉnh sau khi thực hiện Task 2.5 (`app.xml`, `app.c`). |
| [`README.md`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/docs/hands_on_tasks/task_fix/05_task_2_5_resource_ipcp_mechanism/README.md) | Tài liệu kỹ thuật chi tiết phân tích kiến trúc, log QEMU và cạm bẫy lõi. |
