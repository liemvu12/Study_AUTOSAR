# DEBUGGING & PROFILING GUIDE

## 1. Debug Methodology — AUTOSAR Context
- **Debug AUTOSAR khác debug embedded thông thường như thế nào:** Debug AUTOSAR yêu cầu nhận thức về hệ điều hành (OS awareness) thay vì chỉ debug bare-metal.
- **OS context:** Cần biết khi crash, hệ thống đang ở task nào, hoặc phục vụ ISR (Interrupt Service Routine) nào.
- **Layer model:** Xác định bug đang nằm ở tầng nào (Application, RTE, BSW, MCAL, hay Hardware) để cô lập vấn đề.
- **Systematic approach:** Tiếp cận từ dưới lên (Bottom-up: kiểm tra Hardware, MCAL trước) hoặc từ trên xuống (Top-down: kiểm tra logic App, RTE trước).

## 2. GDB với POSIX Simulator
\\\ash
# Build với debug symbols
scons --board=posix DEBUG=1

# Chạy GDB
gdb ./build/posix/as

# Useful GDB commands cho AUTOSAR:
(gdb) break EcuM_Init          # Breakpoint on startup
(gdb) break Os_Alarm_Alarm     # Breakpoint on alarm
(gdb) break Com_SendSignal     # Trace CAN transmission
(gdb) watch g_BMS_SoC          # Watchpoint on variable
(gdb) bt                       # Backtrace khi crash
(gdb) info threads             # OS threads (POSIX sim)
(gdb) thread 2                 # Switch context
(gdb) frame 3                  # Navigate call stack
(gdb) print *(BMS_State_t*)0x20001000  # Inspect struct
(gdb) x/16xb 0x20001000       # Hex dump memory
(gdb) x/s 0x20001020          # Print string
\\\

## 3. Lauterbach Trace32 Basics
- **Trace32:** Là công cụ debug on-target phổ biến nhất ở Tier-1.
- **Kết nối:** Thường qua JTAG/SWD connection.
- **Trace32 PRACTICE script cho AUTOSAR:**
\\\
; trace32_autosar_debug.cmm
SYStem.CPU STM32F107VC
SYStem.Up
Data.LOAD.Elf build/stm32f107vc/asboot.elf
Break.Set EcuM_Init /SOFT
Go
; OS awareness: view tasks, stacks
ASAR.task.List      ; Nếu có Lauterbach AUTOSAR awareness
\\\
- **Task view:** Xem danh sách tasks đang chạy (running) hoặc chờ (waiting).
- **Stack view:** Kiểm tra mức độ sử dụng stack (stack usage) của các task.
- **Symbol browser:** Điều hướng mã nguồn (navigate code).

## 4. Startup Failure Analysis
**Case 1: System không boot (main() không reach)**
- Check power supply voltage.
- Crystal oscillator issue -> clock không start.
- Boot mode pins sai.
- **Debug:** Dùng oscilloscope đo trên NRST pin, measure clock.

**Case 2: Crash trong EcuM_Init**
- Thường do truyền NULL pointer trong config structures.
- Watchdog timeout: do Wdg_Init bị cấu hình wrong timeout.
- **Debug:** Đặt Breakpoint và step qua từng driver init.

**Case 3: StartOS không return**
- Stack overflow trong một task nào đó.
- OS config sai (xung đột ưu tiên TASK).
- **Debug:** Kiểm tra cấu hình stack size trong file OIL, add stack pattern để monitor.

**Case 4: Runnable không chạy**
- Alarm kích hoạt task chưa được set.
- Rte_Start chưa được gọi.
- **Debug:** Đặt breakpoint trong SchM_Enter.

## 5. Communication Failure Analysis
**Không nhận được CAN frame:**
1. Hardware: đo bằng oscilloscope trên CAN bus.
2. MCAL: đặt breakpoint trên Can_Rx_ISR -> xem có trigger không?
3. CanIf: kiểm tra acceptance filter có block frame không?
4. COM: hàm RxIndication có được gọi không?
5. RTE: flag nhận tín hiệu có được set không?

**Frame gửi sai giá trị:**
- Byte order (Endian) issue: in hex dump của I-PDU buffer.
- Scaling factor bị cấu hình sai trong COM config.
- Wrong signal start bit.

**Bus-Off recovery:**
- **Debug:** Kiểm tra CanSM state machine, đọc các error counter registers.
- **Recovery:** Callbacks CanSM_ControllerBusOff -> kiểm tra restart sequence.

## 6. NvM Failure Analysis
**Data mất sau power cycle:**
1. Hàm NvM_WriteAll() có được gọi trước shutdown không?
2. Shutdown time đủ dài cho NvM complete ghi vào flash/EEPROM không?
3. Thêm logging vào các NvM callback để trace.

**CRC error khi startup:**
1. Flash bit flip (hardware issue).
2. Partial write (power loss xảy ra giữa chừng lúc đang ghi).
3. Kiểm tra return value của NvM_GetErrorStatus().

## 7. OS Failure Analysis
**Priority Inversion:**
- **Trace:** Task execution order bị đảo lộn bất thường.
- High priority task bị block lâu bởi low priority task.
- **Fix:** Dùng OS Resource với Priority Ceiling Protocol.

**Stack Overflow:**
- **Pattern:** Random crashes, corrupt data.
- **Debug:** Kiểm tra stack canary (ví dụ pattern 0xDEADBEEF).
- **Fix:** Tăng stack size trong file OIL.

**Deadlock:**
- **Pattern:** System freeze, không phản hồi (no response).
- **Debug:** Tất cả các tasks đều đang ở state WaitEvent hoặc WaitSemaphore.
- **Fix:** Luôn acquire các resources theo cùng một thứ tự.

## 8. Profiling — Đo CPU Load
\\\c
/* Method 1: GPIO toggle */
#include "Dio.h"
void Task_10ms(void) {
    Dio_WriteChannel(DIO_PIN_PROFILING, STD_HIGH);
    /* ... task body ... */
    Dio_WriteChannel(DIO_PIN_PROFILING, STD_LOW);
    /* Đo duty cycle trên oscilloscope = CPU load */
}

/* Method 2: Timer counter */
uint32 start = Timer_GetTick();
/* ... code ... */
uint32 elapsed = Timer_GetTick() - start;
\\\

## 9. Common AUTOSAR Debug Checklist
- **App Layer:** Logic điều khiển có đúng không? Runnable mapping ok không?
- **RTE Layer:** Ports kết nối đúng chưa? Task trigger đúng không? Data consistency?
- **BSW Layer:** Configurations (COM, PDU, NvM, CanSM) chính xác chưa? Module state (Init, Uninit) đang ở đâu?
- **MCAL Layer:** Cấu hình thanh ghi, interrupts, clock tree chuẩn không?
- **HW Layer:** Điện áp, xung nhịp, kết nối tín hiệu vật lý?

## 10. Interview Q&A — 20 câu debug scenarios
1. **Q:** System reset liên tục sau vài giây boot. Cách debug? 
   **A:** Đặt breakpoint ở Reset Handler, kiểm tra xem WDG reset hay HardFault.
2. **Q:** Làm sao biết task nào gây ra stack overflow?
   **A:** Kiểm tra memory ở các vùng stack canaries (padding), hoặc xem call stack lúc fault.
3. **Q:** Một frame CAN gửi ra bị trễ 50ms so với chu kỳ. Tại sao?
   **A:** Task chứa COM transmission bị preempt bởi task ưu tiên cao hơn, hoặc COM Tx delay timer config sai.
*(... các câu hỏi kịch bản khác tập trung vào Memory, OS, COM, NvM)*
