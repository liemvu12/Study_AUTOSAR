# TASK PLAN CHUYÊN ĐỀ 06: Real-World ECU Applications (BMS, VCU, Body)

## Giới Thiệu
Chuyên đề 06 tập trung vào việc mô phỏng và xây dựng các hệ thống nhúng thực tế trong ô tô (Real-World ECU Applications) dựa trên nền tảng AUTOSAR Classic. Các bài tập thực hành (hands-on tasks) được thiết kế xoay quanh ba hệ thống chính trị giá nhất: Battery Management System (BMS), Vehicle Control Unit (VCU) và Body Control Module (BCM). 

**Cấu trúc source code thực tế áp dụng trong chuyên đề:**
- s/com/as.application/board.posix/simulator/simulator.c: Entry point cho POSIX simulator main.
- s/com/as.application/board.posix/SConscript: Cấu hình build system.
- s/com/as.application/swc/: Thư mục chứa các Software Components.
- s/com/as.application/common/: Các tiện ích dùng chung (common utilities).
- Build target: scons --board=posix

---

## TASK 6.1: Mini BMS ECU — SoC Calculation & CAN Broadcast (~8h, Advanced)

**Objective:** Xây dựng hoàn chỉnh một module phần mềm quản lý pin (BMS) dạng mini với các tính năng cốt lõi: Coulomb Counting để tính State of Charge (SoC), lưu trữ dữ liệu bền vững (persistence) qua NvM và quản lý lỗi qua DEM (Diagnostic Event Manager).

**Architecture (Kiến trúc):** Hệ thống bao gồm 4 SWCs (Software Components):
1. CellSensing: Thu thập dữ liệu điện áp, dòng điện và nhiệt độ.
2. BatteryState: Xử lý thuật toán SoC và SoH.
3. SafetyManager: Quản lý an toàn, kiểm tra điều kiện vượt ngưỡng.
4. ContactorControl: Điều khiển đóng cắt relay (Contactor) dựa trên trạng thái an toàn.

### Step 1 (~2h): Định nghĩa cấu trúc dữ liệu và Header Files
Tạo file ms_types.h để chuẩn hóa các tham số hoạt động của hệ thống pin và mã lỗi chuẩn OBD-II.

`c
/* as/com/as.application/swc/bms/bms_types.h */
#ifndef BMS_TYPES_H
#define BMS_TYPES_H

#include "Std_Types.h"

/* Cấu trúc lưu trữ trạng thái tổng thể của hệ thống pin */
typedef struct {
    sint32 PackCurrent_mA;        /* Dòng điện tổng (+ sạc, - xả) */
    uint16 PackVoltage_100mV;     /* Điện áp tổng (Đơn vị 0.1V) */
    sint8  MaxCellTemp_C;         /* Nhiệt độ cell cao nhất (°C) */
    uint8  SoC_pct;               /* State of Charge hiện tại (0-100%) */
    uint32 AccumulatedCharge_mAs; /* Tích phân dòng điện phục vụ Coulomb Counting */
} BMS_State_t;

/* Định nghĩa các Diagnostic Trouble Codes (DTC) theo chuẩn hệ thống truyền động điện */
#define DTC_BMS_OVER_VOLTAGE    0xP0A00 /* Mạch điện áp pin cao vượt ngưỡng */
#define DTC_BMS_OVER_CURRENT    0xP0A78 /* Dòng điện hệ thống truyền động điện cao bất thường */
#define DTC_BMS_OVER_TEMP       0xP0A7E /* Hệ thống pin quá nhiệt */

#endif /* BMS_TYPES_H */
`

### Step 2 (~3h): Implement thuật toán Coulomb Counting
Thuật toán Coulomb Counting được thực thi theo chu kỳ cố định 10ms để đảm bảo độ chính xác của quá trình tích phân dòng điện.

`c
/* as/com/as.application/swc/bms/BatteryState.c */
#include "bms_types.h"

/* Giả định pack pin có dung lượng 100Ah = 100 * 3600 * 1000 mAs = 360,000,000 mAs */
#define PACK_CAPACITY_mAs 360000000UL

/* Hàm này được mapping vào một Task định kỳ chạy mỗi 10ms (Task_10ms) */
void BatteryState_Calculate_10ms(BMS_State_t* bms) {
    /* 
     * Tích phân dòng điện: Q = I × dt 
     * Với dt = 10ms = 0.01s (Do dòng tính bằng mA, dt cần chuyển đổi về giây)
     * Công thức: (mA * 10) / 1000 -> mAs
     */
    bms->AccumulatedCharge_mAs += (bms->PackCurrent_mA * 10) / 1000;
    
    /* 
     * Tính toán lượng điện còn lại và quy đổi ra SoC. 
     * Xử lý trường hợp tràn đáy (underflow) nếu xả kiệt dung lượng.
     */
    int32_t remaining_capacity = PACK_CAPACITY_mAs - bms->AccumulatedCharge_mAs;
    
    if (remaining_capacity < 0) {
        remaining_capacity = 0;
    }
    
    /* Cập nhật SoC với đơn vị phần trăm (0-100%) */
    bms->SoC_pct = (uint8)((remaining_capacity * 100) / PACK_CAPACITY_mAs);
}
`

### Step 3 (~1h): Tích hợp NvM Persistence
Sử dụng Non-Volatile Memory (NvM) để lưu trữ giá trị AccumulatedCharge_mAs mỗi khi hệ thống chuẩn bị tắt (Shutdown) và khôi phục khi khởi động (Startup). Điều này giúp BMS không bị mất đồng bộ SoC sau mỗi chu kỳ bật/tắt khóa điện.

### Step 4 (~1h): Safety Monitoring & Báo cáo sự kiện DEM
Kiểm tra các thông số hoạt động và ghi nhận Diagnostic Event thông qua module DEM của AUTOSAR.

`c
/* as/com/as.application/swc/bms/SafetyManager.c */
#include "bms_types.h"
#include "Dem.h" /* Diagnostic Event Manager */

void SafetyManager_CheckThresholds_10ms(const BMS_State_t* bms) {
    /* Kiểm tra quá nhiệt */
    if (bms->MaxCellTemp_C > 60) {
        /* Báo cáo lỗi P0A7E với trạng thái FAILED (xác nhận lỗi) */
        Dem_SetEventStatus(DTC_BMS_OVER_TEMP, DEM_EVENT_STATUS_FAILED);
    } else {
        /* Phục hồi trạng thái (PASSED) nếu nhiệt độ ổn định */
        Dem_SetEventStatus(DTC_BMS_OVER_TEMP, DEM_EVENT_STATUS_PASSED);
    }

    /* Tương tự, kiểm tra quá dòng (Over Current) > 200A */
    if (bms->PackCurrent_mA > 200000 || bms->PackCurrent_mA < -200000) {
        Dem_SetEventStatus(DTC_BMS_OVER_CURRENT, DEM_EVENT_STATUS_FAILED);
    } else {
        Dem_SetEventStatus(DTC_BMS_OVER_CURRENT, DEM_EVENT_STATUS_PASSED);
    }
}
`

### Step 5 (~1h): Định nghĩa và Broadcast CAN PDU
Sử dụng chuẩn giao tiếp CAN để phát sóng trạng thái pin cho các ECU khác (VD: VCU) mỗi 100ms. Khung truyền có định dạng cụ thể:

- **CAN ID**: 