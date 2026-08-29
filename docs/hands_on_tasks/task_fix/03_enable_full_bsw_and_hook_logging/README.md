# BÁO CÁO KỸ THUẬT: KÍCH HOẠT NGUYÊN BẢN LOG NỘI BỘ BSW (ASLOG) VÀ LÀM RÕ DÒNG CHẢY ARXML -> OS HOOKS

> 📅 **Ngày thực hiện:** 25/08/2026  
> 🏷️ **Loại tài liệu:** Task Fix / Pure Native BSW Tracing & ARXML Hook Flow  
> 📌 **File Diff tương ứng:** [fix.diff](fix.diff)  
> 📂 **Thư mục so sánh Beyond Compare:** [src_before/](src_before/) $\leftrightarrow$ [src_after/](src_after/)  
> 🎯 **Tuân thủ quy tắc:** [rule.md](../rule.md) (100% Native - Không chèn `printf`, không can thiệp kernel, tuân thủ nguồn cấu hình ARXML).

---

## 1. BẢN CHẤT DÒNG CHẢY TỪ ARXML -> OS_CFG.H -> OS HOOKS (HOÀN TOÀN TỰ ĐỘNG)

Khi kiểm tra sâu vào chuỗi gọi hàm của nhân OS (`askar`), chúng ta thấy **hệ thống KHÔNG HỀ bị lỗi include và KHÔNG CẦN sửa bất kỳ dòng nào trong kernel**:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│               DÒNG CHẢY CẤU HÌNH AUTOSAR TỰ ĐỘNG (ARXML -> OS HOOKS)                   │
│                                                                                        │
│  1. File Cấu Hình Gốc (Single Source of Truth):                                        │
│     📄 as/com/as.application/common/autosar.arxml                                      │
│        <General StartupHook="StartupHook" ShutdownHook="ShutdownHook" ... />           │
│                                                                                        │
│  2. Toolchain Sinh Mã (Generator Script):                                              │
│     ⚙️  as/com/as.tool/config.infrastructure.system/argen/GenOS.py                      │
│        Quét ARXML -> Tự động sinh file cấu hình C:                                     │
│                                                                                        │
│  3. File Cấu Hình Sinh Tự Động (Auto-Generated Config):                                │
│     📄 as/build/nt/lm3s6965evb/ascore/config/Os_Cfg.h                                  │
│        #define OS_USE_STARTUP_HOOK                                                     │
│        #define OS_USE_SHUTDOWN_HOOK                                                    │
│                                                                                        │
│  4. Kết Nối Mã Nguồn Nhân OS (Standard Include Chain):                                 │
│     kernel.c -> kernel_internal.h -> Os.h -> Os_Cfg.h                                  │
│                                                                                        │
│  5. Thực Thi Hook Chuẩn:                                                               │
│     Khi StartOS() chạy -> Gọi macro OSStartupHook() -> Chạy StartupHook() trong app.c! │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

👉 **Kết luận:** Nhân OS và ARXML đã được nối kết hoàn hảo 100% từ đầu. Không có bất kỳ sự can thiệp bypass nào cần thiết ở tầng kernel!

---

## 2. FILE DUY NHẤT ĐƯỢC ĐIỀU CHỈNH: `asdebug.h`

Để mở khóa các dòng log kiểm tra lỗi và dòng chảy nội bộ của các module BSW (`EcuM`, `PduR`, `Com`, `Nm`), ta chỉ cần bật cờ `USE_ASLOG` trong file cấu hình debug:

* **File:** [`as/com/as.infrastructure/include/asdebug.h`](src_after/as/com/as.infrastructure/include/asdebug.h)
* **Thay đổi:**
  * Bật cờ `#define USE_ASLOG`.
  * Đưa các cấp độ `AS_LOG_INFO`, `AS_LOG_DEBUG`, `AS_LOG_ECUM`, `AS_LOG_COM`, `AS_LOG_OS` lên mức kích hoạt `1`.

---

## 3. LOG BOOT NGUYÊN BẢN 100% THỰC TẾ TRÊN TERA TERM

```text
ECUM    :  <-CALLIN : EcuM_SetWakeupEvent 0x1
 start application BUILD @ Aug 25 2026 16:11:07
 cpu is little endian
 XCP MTA memory address 20000f78
LOW     :--Initialization of PDU router--
LOW     :--Initialization of PDU router completed --
OSEK NM node ID is 1
STDOUT  :TaskIdle is running
ECUM    :ECUM:RUN Timeout=49
ECUM    :ECUM:RUN Timeout=48
...
```
