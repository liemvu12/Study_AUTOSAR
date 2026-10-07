# BÁO CÁO KỸ THUẬT & SOURCE DIFF: TASK 2.3 — CẤU HÌNH BASIC TASK & ALARM ĐỊNH KỲ

> 📅 **Ngày thực hiện:** 15/09/2026  
> 🏷️ **Loại tài liệu:** Task Implementation & Source Diff / OS Configuration  
> 📌 **File Diff tương ứng:** [`fix.diff`](fix.diff)  
> 🎯 **Tuân thủ quy tắc:** [`rule.md`](../rule.md) (Rule 2: ARXML là Nguồn Chân Lý Duy Nhất & Rule 1: Tuyệt đối không sửa file sinh tự động `Os_Cfg.*`).

---

## 1. BỐI CẢNH & MỤC TIÊU KỸ THUẬT (TASK 2.3)

* **Nhiệm vụ:** Thực thi 2 bước đầu tiên của **Task 2.3**: Thiết lập 2 Basic Task (`Task_Periodic_50ms` và `Task_QueueTester`) cùng 1 Alarm chu kỳ 50ms (`Alarm_Periodic_50ms`) bằng cơ chế cấu hình mô hình hóa AUTOSAR.
* **Quy chuẩn kỹ nghệ & Quyết định Kiến trúc (Single Source of Truth):**
  - Nhằm tuân thủ triệt để nguyên lý phân tầng kiến trúc phần mềm ô tô và tránh làm "ô nhiễm" tệp khung xương BSW dùng chung (`autosar.arxml`), toàn bộ cấu hình của 2 Task và 1 Alarm này **được đặt chính thức và duy nhất trong tệp cấu hình tầng Ứng Dụng: [`as/release/ascore/app/app.xml`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/release/ascore/app/app.xml)**.
  - Tệp này tương ứng 1-1 với file mã nguồn C ứng dụng [`as/release/ascore/app/app.c`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/release/ascore/app/app.c).
  - Không được phép sửa tay file `Os_Cfg.h` hay `Os_Cfg.c`.

---

## 2. CÁC THAY ĐỔI CHI TIẾT ĐÃ THỰC HIỆN (STEP-BY-STEP)

### 🔹 Bước 1: Khai báo Task & Alarm trong Tệp Ứng Dụng `app.xml`

Trong tệp [`as/release/ascore/app/app.xml`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/release/ascore/app/app.xml), tại khối thẻ `<AS><Os>`, bổ sung trực tiếp bên cạnh `TaskApp` và `AlarmApp`:

```xml
		<!-- ================= TASK 2.3: BASIC TASK & ALARM ================= -->
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

---

### 🔹 Bước 2: Kích hoạt công cụ sinh mã ArGen với SCons

Thực thi lệnh biên dịch tại thư mục `as`:
```powershell
cd as
$env:BOARD="lm3s6965evb"
$env:RELEASE="ascore"
scons
```

**Chuỗi xử lý tự động của hệ thống:**
1. Hàm `PreProcess()` trong `building.py` thu thập cả `autosar.arxml` lẫn `app.xml`.
2. Generator Python [`GenOS.py`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/com/as.tool/config.infrastructure.system/argen/GenOS.py) thực hiện cơ chế Multi-file XML Aggregation, tự động quét gom các thẻ `<Task>` và `<Alarm>` từ cả 2 file để sinh ra:
   - [`as/build/nt/lm3s6965evb/ascore/config/Os_Cfg.h`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/build/nt/lm3s6965evb/ascore/config/Os_Cfg.h)
   - [`as/build/nt/lm3s6965evb/ascore/config/Os_Cfg.c`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/build/nt/lm3s6965evb/ascore/config/Os_Cfg.c)

### 🔹 Bước 3: Cài đặt logic Task trong mã C ứng dụng `app.c`

Trong tệp [`as/release/ascore/app/app.c`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/release/ascore/app/app.c), bổ sung thân hàm cho `Task_Periodic_50ms` và `Task_QueueTester`:

```c
/* ========================================================================= */
/* TASK 2.3: Basic Task & Alarm Periodic 50ms + Conformance Test (BCC1/BCC2) */
/* ========================================================================= */
static uint32_t task_instance_counter = 0;

TASK(Task_Periodic_50ms)
{
	task_instance_counter++;
	printf("   --> [Task_Periodic_50ms] Running instance #%u\n", (unsigned int)task_instance_counter);
	(void)TerminateTask();
}

TASK(Task_QueueTester)
{
	StatusType ret;

	printf("\n=================================================================\n");
	printf("[TASK 2.3] TESTING OSEK CONFORMANCE CLASS (BCC1 vs BCC2)\n");
	printf("=================================================================\n");

	/* Lần 1: Kích hoạt Task_Periodic_50ms đưa vào trạng thái READY */
	printf("[Tester] Activating Task_Periodic_50ms (Call 1)...\n");
	ret = ActivateTask(Task_Periodic_50ms);
	printf("         --> Result: ret = %s (Task moved to READY state)\n", (ret == E_OK) ? "E_OK" : "ERROR");

	/* Lần 2: Task đang READY (chưa kịp chạy vì Priority 2 < 5), kích hoạt tiếp */
	printf("[Tester] Activating Task_Periodic_50ms (Call 2 - Burst activation)...\n");
	ret = ActivateTask(Task_Periodic_50ms);
	if (ret == E_OS_LIMIT)
	{
		printf("         --> Result: E_OS_LIMIT! (BCC1 Verified: Activation Limit = 1 Reached!)\n");
	}
	else if (ret == E_OK)
	{
		printf("         --> Result: E_OK! (BCC2 Verified: Activation Queued Successfully!)\n");
	}
	else
	{
		printf("         --> Result: Unexpected error code %u\n", (unsigned int)ret);
	}

	printf("=================================================================\n\n");
	(void)TerminateTask();
}
```

---

## 3. KẾT QUẢ XÁC MINH & ĐỐI SOÁT (VERIFICATION)

### ✅ Đối soát 1: Bảng ID tự động sinh trong `Os_Cfg.h`

Mở file [`Os_Cfg.h`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/build/nt/lm3s6965evb/ascore/config/Os_Cfg.h), các định danh mới đã xuất hiện chính xác:

```c
#define TASK_ID_Task_Periodic_50ms               6   /* priority = 2 */
#define TASK_ID_Task_QueueTester                 7   /* priority = 5 */
#define TASK_NUM                                 8

#define ALARM_ID_Alarm_Periodic_50ms              2
#define ALARM_NUM                                 3
```

### ✅ Đối soát 2: Khai báo mảng thực thi trong `Os_Cfg.c`

Mở file [`Os_Cfg.c`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/build/nt/lm3s6965evb/ascore/config/Os_Cfg.c):
- `TaskConstArray[6]`: Entry point `TaskMainTask_Periodic_50ms`, stack 512 bytes, `maxActivation = 1`.
- `TaskConstArray[7]`: Entry point `TaskMainTask_QueueTester`, stack 512 bytes, `appModeMask = (0 | (OSDEFAULTAPPMODE))`.
- `AlarmConstArray[2]`: Tên `"Alarm_Periodic_50ms"`, counter `&CounterConstArray[COUNTER_ID_OsClock]`, chu kỳ `period = 50`, `start = 50`.

### ✅ Đối soát 3: Kết quả biên dịch & Linker sạch 100%
Khi chạy lại lệnh build `scons`:
```powershell
LINK build\nt\lm3s6965evb\ascore\lm3s6965evb.exe
scons: done building targets.
```
$\longrightarrow$ Quá trình biên dịch và liên kết kết thúc với mã lỗi `0` (Success 100%), không còn lỗi thiếu symbol.

### ✅ Đối soát 4: Kết quả thực nghiệm sống trên máy ảo QEMU ARM Cortex-M3
Chạy lệnh mô phỏng QEMU:
```powershell
qemu-system-arm -M lm3s6965evb -kernel as/build/nt/lm3s6965evb/ascore/lm3s6965evb.exe -nographic -serial mon:stdio
```

**Log thực thi đầu ra trên cổng Serial:**
```text
=================================================================
[TASK 2.3] TESTING OSEK CONFORMANCE CLASS (BCC1 vs BCC2)
=================================================================
[Tester] Activating Task_Periodic_50ms (Call 1)...
         --> Result: ret = E_OK (Task moved to READY state)
[Tester] Activating Task_Periodic_50ms (Call 2 - Burst activation)...
         --> Result: E_OS_LIMIT! (BCC1 Verified: Activation Limit = 1 Reached!)
=================================================================

   --> [Task_Periodic_50ms] Running instance #1
   --> [Task_Periodic_50ms] Running instance #2
   --> [Task_Periodic_50ms] Running instance #3
   --> [Task_Periodic_50ms] Running instance #4
   --> [Task_Periodic_50ms] Running instance #5
   ...
```
👉 **Kết quả chứng minh:**
1. `Task_QueueTester` bẫy thành công mã lỗi **`E_OS_LIMIT`** khi kích hoạt dồn dập trong chế độ **BCC1** (`Activation="1"`).
2. Sau khi Tester kết thúc, `Task_Periodic_50ms` chạy instance #1.
3. `Alarm_Periodic_50ms` đều đặn đánh thức `Task_Periodic_50ms` chạy tuần hoàn mỗi 50ms một cách tự động (Declarative Autostart).

---

## 4. CẤU TRÚC THƯ MỤC BEFORE / AFTER

```
03_task_2_3_basic_task_alarm_bcc_configuration/
├── README.md                                          # Báo cáo kỹ thuật chi tiết
├── fix.diff                                           # Git diff chuẩn của cả app.xml và app.c
├── src_before/                                        # Trạng thái gốc trước khi sửa
│   └── as/release/ascore/app/
│       ├── app.c
│       └── app.xml
└── src_after/                                         # Trạng thái sau khi thêm Task & Alarm
    └── as/release/ascore/app/
        ├── app.c
        └── app.xml
```

---

## 5. 💡 PHÂN TÍCH KIẾN TRÚC: TẠI SAO ĐẶT CHUNG VÀO `autosar.arxml` VỚI `SchM_Startup`? CÓ CHỖ NÀO THÍCH HỢP HƠN KHÔNG?

Một câu hỏi kiến trúc cực kỳ sắc bén thường được đặt ra:  
> *"Task `Task_QueueTester` và `Task_Periodic_50ms` là logic ứng dụng phục vụ bài lab, vốn dĩ không có quan hệ họ hàng gì với các Task hạ tầng BSW như `SchM_Startup` hay `SchM_BswService`. Tại sao lại hướng dẫn đặt chúng vào cùng file `autosar.arxml`? Thiết kế này có hợp lý không và có chỗ nào thích hợp hơn không?"*

### 1️⃣ Nhận Định Bản Chất: Phản Biện Là Hoàn Toàn Chính Xác!
Về mặt nguyên lý thiết kế phần mềm ô tô chuẩn mực (**Separation of Concerns & Architecture Layering**):
- `SchM_Startup` và `SchM_BswService` thuộc **Tầng Hạ Tầng BSW (BSW Infrastructure / RTE SchM)**, nhiệm vụ là điều phối khởi động và chạy tuần hoàn các stack mạng CAN, Com, NvM...
- `Task_Periodic_50ms` và `Task_QueueTester` thuộc **Tầng Ứng Dụng (Application Layer)**, chạy trong `app.c` để thực nghiệm cơ chế lập lịch OS.
- Việc đặt chung hai tầng này vào cùng một file ARXML thô là một sự vi phạm tính đóng gói module (**Configuration Layering Pollution**).

### 2️⃣ Vậy Tại Sao Thiết Kế Ban Đầu Của Task 2.3 Lại Chọn `autosar.arxml`?
Có 2 lý do thực tế trong ngữ cảnh đào tạo và kiến trúc của kho mã nguồn `as`:

1. **Lý do sư phạm (Pedagogical Shortcut):**  
   - Task 2.3 nằm ở **Chuyên đề 02 (OS & MCAL)**. Mục tiêu cốt tử của bài học này là giúp học viên hiểu nhanh cơ chế **BCC1 vs BCC2**, hàng đợi kích hoạt `Activation`, và trải nghiệm vòng lặp cơ bản: *Sửa XML $\to$ Chạy SCons $\to$ Đối soát `Os_Cfg.h`*.  
   - Cơ chế gộp nhiều file XML (*Multi-file XML Aggregation*) và cây phân cấp phức tạp chỉ được giảng dạy chuyên sâu tại **Chuyên đề 05 (Toolchain & ECU Integration)**.  
   - Nếu ngay từ Task 2.3 đã yêu cầu học viên phân tích cây phụ thuộc đa tầng giữa `autosar.arxml`, `app.xml`, `canif.xml`, `infrastructure.xml`, người học sẽ bị "ngợp" trước luồng build của SCons mà xao nhãng mục tiêu OS chính. Do đó, `autosar.arxml` (tệp xương sống luôn được nạp ở mọi board) được chọn làm **"Lối đi tắt sư phạm an toàn" (Fail-safe path)**.
2. **Vai trò lịch sử của `autosar.arxml` trong repo `as`:**  
   - Tác giả framework `as` đặt `autosar.arxml` tại `com/as.application/common/` như một "System-level Base Template" chứa khung xương tối thiểu để OS có thể boot được (`OsOS`, `OsClock`, `OsDefaultApp`).

---

### 3️⃣ Nếu Không Đặt Ở Đó, Chỗ Nào THÍCH HỢP HƠN NHIỀU?

#### 🅰️ Chỗ Thích Hợp Nhất Trong Kho Mã Nguồn `Study_AUTOSAR`:
👉 **[`as/release/ascore/app/app.xml`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/release/ascore/app/app.xml)**!
- **Bằng chứng kiến trúc:**  
  1. Thư mục `release/ascore/app/` là lãnh địa riêng của **Tầng Ứng Dụng** thuộc bản phát hành `ascore`.
  2. File [`app.xml`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/release/ascore/app/app.xml) đã được định nghĩa sẵn thẻ `<AS><Os>` chứa `TaskApp` và `AlarmApp`:
     ```xml
     <AS>
         <Os>
             <Task Name="TaskApp" ... />
             <Alarm Name="AlarmApp" ... />
             <!-- ĐẶT Task_Periodic_50ms VÀ Task_QueueTester VÀO ĐÂY LÀ CHUẨN MỰC NHẤT! -->
         </Os>
     </AS>
     ```
  3. Mã C thực thi của các task này nằm trọn vẹn trong [`as/release/ascore/app/app.c`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/release/ascore/app/app.c).  
  $\to$ Đặt vào `app.xml` tạo nên sự **gắn kết 1-1 hoàn hảo giữa file cấu hình ứng dụng (`app.xml`) và file mã nguồn C ứng dụng (`app.c`)**, giữ cho file dùng chung `autosar.arxml` hoàn toàn trong sạch!

#### 🅱️ Chỗ Thích Hợp Trong Các Dự Án AUTOSAR Công Nghiệp Thực Tế (Vector DaVinci / EB tresos):
Trong các dự án sản xuất xe ô tô hàng loạt (OEM / Tier-1):
- **Tuyệt đối không có file ARXML nguyên khối (Monolithic ARXML) dùng chung cho cả BSW lẫn App.**
- Hệ thống được chia tách thành các gói mô tả phân quyền rõ rệt:
  1. **Nhóm BSW (BSW Team):** Bàn giao file **`SchM_BswMD.arxml`** (hoặc `Os_BswMD.arxml`) chỉ mô tả các tác vụ hạ tầng (`SchM_Startup`, `SchM_BswService`, `Can_MainFunction`).
  2. **Nhóm Ứng Dụng (SWC Team):** Bàn giao file **`App_SWCD.arxml`** mô tả các Software Component, Runnable Entities, Ports độc lập không phụ thuộc OS.
  3. **Kỹ Sư Tích Hợp Hệ Thống (System Integrator):** Sử dụng DaVinci Configurator để map Runnable vào các `OsTask` trong file phân đoạn cấu hình ECU: **`Os.ecuc.arxml`**.
- Hai nhóm làm việc hoàn toàn độc lập thông qua giao ước hợp đồng (ARXML Interface Contract).

> 🧭 **Tham chiếu quy tắc chuẩn:**  
> Đọc thêm [**Mục 5: Bộ Quy Luật Thiết Kế Chủ Động & Cây Quyết Định 3 Bước Định Vị File XML/C** trong `rule.md`](../rule.md#5-🧭-bộ-quy-luật-thiết-kế-nguyên-tắc-chia-task-chia-file-xml-và-định-vị-file-c-trong-tương-lai) và [**Mục 3.6: Kiến Trúc Hợp Nhất Cấu Hình Đa Tệp** trong Chuyên Đề 05](../../theory/05_Toolchain_ARXML_And_ECU_Integration.md#36-kiến-trúc-hợp-nhất-cấu-hình-đa-tệp-multi-file-xml-aggregation--cơ-chế-đóng-gói-module-trong-dự-án-as).

---

## 6. 🔬 GIẢI PHÃU CƠ CHẾ RUNTIME: AUTOSTART ALARM & STATE TRAPPING CỦA `TASK_QUEUETESTER`

### 1️⃣ Khởi tạo Alarm: Declarative Autostart vs Lệnh C Thủ Công (`SchM_StartupHook`)
- **`AlarmApp` (cần code C thủ công):** Trong `app.xml`, `AlarmApp` đặt `Autostart="False"`. Toolchain sinh ra `appModeMask = 0`, nên Kernel OS không tự khởi động nó khi boot. Do đó, mã nguồn `app.c` phải tự gọi `OsSetRelAlarm(AlarmApp, ...)` bên trong hàm `SchM_StartupHook()`.
- **`Alarm_Periodic_50ms` (tự động 100%):** Được khai báo `Autostart="True"` kèm `OSDEFAULTAPPMODE`, `Period="50"`, `StartTime="50"`. Bộ sinh mã sinh ra `appModeMask = (0 | (OSDEFAULTAPPMODE))`. Khi `StartOS()` được gọi, hàm nhân Kernel `Os_InitAlarm()` tại `alarm.c:L390-L393` tự động duyệt mảng và kích hoạt `SetAbsAlarm()` ngay lập tức. **Nhà phát triển hoàn toàn không cần viết bất kỳ hàm khởi tạo C nào.**

### 2️⃣ Khai báo thân hàm `TASK(Task_Periodic_50ms)` & Tự động Trigger
- Macro `TASK(Task_Periodic_50ms)` mở rộng thành `void TaskMainTask_Periodic_50ms(void)`.
- Trong `Os_Cfg.c`, Toolchain sinh hàm action:
  ```c
  static void Alarm_Periodic_50ms_Action(void) { (void)ActivateTask(TASK_ID_Task_Periodic_50ms); }
  ```
- Mỗi khi `OsClock` đếm đủ chu kỳ 50ms, ngắt timer làm Alarm hết hạn $\to$ Kernel gọi `Alarm_Periodic_50ms_Action()` $\to$ `Task_Periodic_50ms` tự động được kích hoạt vào hàng đợi Ready Queue. Developer chỉ cần viết thân hàm nghiệp vụ và kết thúc bằng `TerminateTask()`.

### 3️⃣ Cơ chế Bẫy Trạng Thái (State Trapping Mechanism) Của `Task_QueueTester`
- **Bố cục ưu tiên:** `Task_QueueTester` có `Priority = 5` (Autostart), còn `Task_Periodic_50ms` có `Priority = 2`.
- **Bẫy tiếm quyền (Non-preemption Trap):** Vì Priority 5 > Priority 2, khi `Task_QueueTester` gọi `ActivateTask(Task_Periodic_50ms)` lần 1, Task 50ms chuyển sang trạng thái `READY` nhưng **không thể tiếm quyền CPU** của Tester $\to$ Bắt buộc phải nằm chờ trong Ready Queue.
- **Bẫy kích hoạt dồn dập (Burst Activation Trap):** Ngay sau đó, Tester gọi tiếp `ActivateTask(Task_Periodic_50ms)` lần 2 khi instance 1 vẫn đang chờ:
  - **Với BCC1 (`Activation="1"`):** Giới hạn kích hoạt tối đa là 1. Kernel từ chối yêu cầu thứ 2 và trả về mã lỗi **`E_OS_LIMIT`**!
  - **Với BCC2 (`Activation="3"`):** Kernel cho phép hàng đợi kích hoạt đa tầng $\to$ Xếp yêu cầu thứ 2 vào Activation Queue và trả về **`E_OK`**!
- **Giải phóng CPU:** Khi Tester gọi `TerminateTask()`, `Task_Periodic_50ms` mới chính thức được cấp CPU để chạy. Sau đó, `Alarm_Periodic_50ms` vẫn tiếp tục duy trì chu kỳ 50ms vĩnh viễn.

