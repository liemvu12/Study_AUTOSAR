# CHỨNG MINH CẤP ĐỘ 4: ECC2 (EXTENDED CONFORMANCE CLASS 2)
## Cấu Hình Mặc Định Của Dự Án ascore — Đầy Đủ Tính Năng Đa Nhiệm Cao Cấp Nhất

---

### 1. ⚙️ CẤU HÌNH THỰC TẾ TRONG `autosar.arxml` CỦA DỰ ÁN `as`:

Trong file [`as/com/as.application/common/autosar.arxml: L18-L48`](../../../as/com/as.application/common/autosar.arxml#L18-L48):
1. **Có Extended Tasks với Event:** `TaskApp` và `TaskNmInd` có `<EventList>` chứa nhiều sự kiện (`Event1`..`Event5`, `EventNmNormal`..`EventRingData`).
2. **Có các Task trùng Priority:** `SchM_Startup` (Priority = 7) và `TaskNmInd` (Priority = 7) cùng chia sẻ một mức ưu tiên.
3. **Có Task hỗ trợ đa kích hoạt:** `TaskCanIf` có `Activation="5"`.

---

### 2. 📄 MÃ C SINH RA THỰC TẾ TRONG `ascore/config/`:

#### File [`as/build/nt/lm3s6965evb/ascore/config/Os_Cfg.h: L40-L72`](../../../as/build/nt/lm3s6965evb/ascore/config/Os_Cfg.h#L40-L72):
```c
/* as/build/nt/lm3s6965evb/ascore/config/Os_Cfg.h */

#define OS_STATUS EXTENDED

#define PRIORITY_NUM (OS_PTHREAD_PRIORITY+9)
#define ACTIVATION_SUM (11+OS_PTHREAD_NUM)

#define MULTIPLY_TASK_PER_PRIORITY   /* <── [ECC2] CHO PHÉP TaskNmInd & SchM_Startup CHUNG PRIO 7 */
#define SEQUENCE_MASK 0x7u           /* <── [ECC2] PHÂN XỬ FIFO CHO CÁC TASK TRÙNG PRIORITY */
#define SEQUENCE_SHIFT 3
#define MULTIPLY_TASK_ACTIVATION     /* <── [ECC2] CHO PHÉP TaskCanIf KÍCH HOẠT NHIỀU LẦN (max = 5) */

#define TASK_ID_TaskApp          0   /* priority = 5 */
#define TASK_ID_TaskCanIf        1   /* priority = 9 */
#define TASK_ID_TaskNmInd        2   /* priority = 7 <── TRÙNG PRIORITY VỚI SchM_Startup */
#define TASK_ID_TaskIdle         3   /* priority = 0 */
#define TASK_ID_SchM_Startup     4   /* priority = 7 <── TRÙNG PRIORITY VỚI TaskNmInd */
#define TASK_ID_SchM_BswService  5   /* priority = 8 */
#define TASK_NUM                 6

#define EVENT_MASK_TaskApp_Event1       0x01
#define EVENT_MASK_TaskApp_Event2       0x02
#define EVENT_MASK_TaskNmInd_EventNmNormal  0x01

#define EXTENDED_TASK                /* <── [ECC2] BẬT TÍNH NĂNG EXTENDED TASK CHO TaskApp & TaskNmInd */
```

---

### 3. 🔍 BẢNG ĐỐI CHIẾU 6 TASKS THỰC TẾ TRONG `Os_Cfg.c` VỚI QUY TẮC ECC2:

Trong file [`as/build/nt/lm3s6965evb/ascore/config/Os_Cfg.c: L130-L240`](../../../as/build/nt/lm3s6965evb/ascore/config/Os_Cfg.c#L130-L240):

| Tên Task | Phân Loại Task | Con Trỏ `pEventVar` | Thuộc Tính `maxActivation` | `appModeMask` (Autostart) | Trạng Thái & Cơ Chế Hoạt Động |
| :--- | :---: | :---: | :---: | :---: | :--- |
| `TaskApp` | **Extended** | `&TaskApp_EventVar` | 1 | 0 | Chạy kiểm tra hiệu năng, chờ sự kiện. |
| `TaskCanIf` | **Basic** | `NULL` | **5 (Đa kích hoạt)** | 0 | Chờ kích hoạt từ driver CAN, xếp hàng tối đa 5 gói tin. |
| `TaskNmInd` | **Extended** | `&TaskNmInd_EventVar`| 1 | `OSDEFAULTAPPMODE` | Tự động khởi động, gọi `WaitEvent()` chờ tín hiệu NM. |
| `TaskIdle` | **Basic** | `NULL` | 1 | `OSDEFAULTAPPMODE` | Tự động khởi động, chạy vòng lặp nền khi rảnh rỗi. |
| `SchM_Startup` | **Basic** | `NULL` | 1 | `OSDEFAULTAPPMODE` | Tự động chạy khởi tạo BSW Phase 2 rồi `TerminateTask`. |
| `SchM_BswService`| **Basic** | `NULL` | 1 | 0 | Kích hoạt định kỳ 10ms bởi `Alarm_BswService`. |

---

### 💡 KẾT LUẬN CHỨNG MINH:
1. Dự án `ascore` đang chạy ở chuẩn **ECC2** — cấp độ cao cấp và toàn diện nhất của AUTOSAR OS.
2. Khi muốn đưa hệ thống về **BCC1, BCC2, hoặc ECC1** cho các ECU khác: Kỹ sư chỉ cần chỉnh sửa file `autosar.arxml` (bỏ EventList, đổi Priority, đổi Activation) và chạy tool `GenOS.py` $\rightarrow$ Mã nguồn C sinh ra sẽ **tự động co giãn theo đúng luật của từng cấp độ** mà không cần sửa 1 dòng code Kernel nào!
