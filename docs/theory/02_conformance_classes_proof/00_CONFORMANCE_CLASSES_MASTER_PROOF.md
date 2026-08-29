# CHỨNG MINH THỰC CHIẾN 4 CẤP ĐỘ TUÂN THỦ (CONFORMANCE CLASSES) TRONG DỰ ÁN AS
## Masterclass Phân Tích & Hướng Dẫn Tái Cấu Hình Hệ Điều Hành OSEK OS / AUTOSAR OS

> 📚 **Tài liệu lý thuyết tham chiếu:** [docs/theory/02_AUTOSAR_OS_And_MCAL_Deep_Dive.md](../02_AUTOSAR_OS_And_MCAL_Deep_Dive.md)  
> 🔧 **Mã nguồn lõi đối soát:**  
> - Trình sinh mã Kernel OS: [`as/com/as.tool/config.infrastructure.system/argen/GenOS.py`](../../../as/com/as.tool/config.infrastructure.system/argen/GenOS.py)  
> - Thuật toán Scheduler: [`as/com/as.infrastructure/system/kernel/askar/kernel/sched-bubble.c`](../../../as/com/as.infrastructure/system/kernel/askar/kernel/sched-bubble.c)  
> - Cấu trúc dữ liệu Task & Event: [`as/com/as.infrastructure/system/kernel/askar/kernel/kernel_internal.h`](../../../as/com/as.infrastructure/system/kernel/askar/kernel/kernel_internal.h)  
> - File cấu hình ARXML gốc: [`as/com/as.application/common/autosar.arxml`](../../../as/com/as.application/common/autosar.arxml)  
> - File cấu hình sinh ra của dự án: [`as/build/nt/lm3s6965evb/ascore/config/Os_Cfg.h`](../../../as/build/nt/lm3s6965evb/ascore/config/Os_Cfg.h)

---

## 📑 MỤC LỤC BỘ TÀI LIỆU CHỨNG MINH

1. [Tổng quan cơ chế quyết định Conformance Class của Toolchain `GenOS.py`](#1-tong-quan)
2. [Chi Tiết Cấp Độ 1: BCC1 (Basic Conformance Class 1) — Tối Ưu Cho Vi Điều Khiển < 1KB RAM](01_BCC1_Proof_And_Config.md)
3. [Chi Tiết Cấp Độ 2: BCC2 (Basic Conformance Class 2) — Đa Nhiệm Cơ Sở Với Hàng Đợi FIFO](02_BCC2_Proof_And_Config.md)
4. [Chi Tiết Cấp Độ 3: ECC1 (Extended Conformance Class 1) — Đa Nhiệm Hướng Sự Kiện Event-Driven](03_ECC1_Proof_And_Config.md)
5. [Chi Tiết Cấp Độ 4: ECC2 (Extended Conformance Class 2) — Cấu Hình Mặc Định Hiện Tại Của Dự Án as](04_ECC2_Proof_And_Config.md)

---

<a id="1-tong-quan"></a>
## 1. ⚙️ TỔNG QUAN: CƠ CHẾ QUYẾT ĐỊNH CONFORMANCE CLASS CỦA TOOLCHAIN `GenOS.py`

Trong dự án `as`, cấp độ tuân thủ của nhân hệ điều hành **không phải được gán cứng bằng tay** mà do công cụ sinh mã [`GenOS.py: L140-L201`](../../../as/com/as.tool/config.infrastructure.system/argen/GenOS.py#L140-L201) tự động quét file `autosar.arxml` và tính toán theo logic toán học:

```python
# as/com/as.tool/config.infrastructure.system/argen/GenOS.py (Dòng 140-201)

# 1. Kiểm tra kích hoạt lặp (Multiple Activation)
if Integer(task.attrib['Activation']) > 1:
    multiAct = True  # -> Sinh ra #define MULTIPLY_TASK_ACTIVATION

# 2. Kiểm tra trùng độ ưu tiên (Multiple Tasks per Priority)
if prio in prioList:
    multiPrio = True # -> Sinh ra #define MULTIPLY_TASK_PER_PRIORITY
prioList.append(prio)

# 3. Kiểm tra sự kiện (EventList)
if len(task.findall('EventList')) > 0:
    withEvt = True   # -> Sinh ra #define EXTENDED_TASK
```

---

### 📊 BẢNG MA TRẬN 4 CẤP ĐỘ TRONG DỰ ÁN `as`:

| Cấp Độ Tuân Thủ | `withEvt` (`EXTENDED_TASK`) | `multiPrio` (`MULTIPLY_TASK_PER_PRIORITY`) | `multiAct` (`MULTIPLY_TASK_ACTIVATION`) | Đặc Tính Kỹ Thuật Trong Mã Nguồn C |
| :---: | :---: | :---: | :---: | :--- |
| 🟢 **BCC1** | ❌ `False` | ❌ `False` | ❌ `False` | Không có Event, `event.c` bị loại bỏ 100%, 1 Task/Priority, 1 Stack chung. |
| 🟡 **BCC2** | ❌ `False` | ✅ `True` | ✅ `True` | Không có Event, có hàng đợi kích hoạt `activation`, Scheduler dùng FIFO. |
| 🟠 **ECC1** | ✅ `True` | ❌ `False` | ❌ `False` | Có Extended Task (`WaitEvent`), mỗi Priority 1 Task, Dedicated Stack. |
| 🔴 **ECC2** | ✅ `True` | ✅ `True` | ✅ `True` | **(Cấu hình hiện tại)** Đầy đủ Event + Hàng đợi FIFO + Đa kích hoạt. |
