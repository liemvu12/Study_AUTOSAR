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

- **CAN ID**:  0x180
- **DLC**: 8 bytes
- **Layout**:
  - Byte 0: SoC (%)
  - Byte 1: SoH (%)
  - Byte 2-3: PackVoltage (đơn vị 0.1V)
  - Byte 4-5: PackCurrent (đơn vị 0.1A, signed)
  - Byte 6: MaxCellTemp (°C, sử dụng offset +40 để tránh số âm)
  - Byte 7: Fault flags bitmask

**Success Criteria:**
- Thuật toán Coulomb Counting tính toán giá trị SoC với sai số tối đa ±5% sau khi mô phỏng chạy xả liên tục trong 10 phút.
- Ghi nhận thành công mã lỗi DTC P0A7E trong bộ nhớ lỗi nếu nhiệt độ duy trì > 60°C trong 10 chu kỳ đo lặp lại.
- Tín hiệu CAN ID  0x180 được capture bằng socketCAN/vcan cho thấy layout bit chính xác.
- Restart lại tiến trình simulator (Power cycle) cho thấy hệ thống đọc lại và tiếp tục từ giá trị SoC cuối cùng mà không bị reset về 0.

---

## TASK 6.2: Mini VCU — Torque Request & Plausibility Check (~8h, Advanced)

**Objective:** Xây dựng phần mềm VCU (Vehicle Control Unit) phụ trách logic vận hành cốt lõi, bao gồm: kiểm tra tính hợp lệ của cảm biến chân ga chuẩn ASIL-D (Sensor Plausibility Check), điều phối mô-men xoắn (Torque Coordination) và quản lý chế độ số (Mode Management).

**Architecture:**
- SWC_PedalSensor: Thu thập dữ liệu từ cảm biến chân ga (2 đường tín hiệu ADC độc lập), kiểm tra Plausibility.
- SWC_TorqueCoordinator: Nội suy và tính toán Torque request dựa trên bản đồ mô-men xoắn và trạng thái truyền động.
- SWC_ModeManager: Quản lý các trạng thái hoạt động P (Park) - R (Reverse) - N (Neutral) - D (Drive).

### Step 1: Thuật toán Plausibility Check cảm biến chân ga
Một yêu cầu cơ bản trong tiêu chuẩn ISO 26262 là phải phát hiện được lỗi hỏng lệch (drift) hoặc ngắn mạch của các cảm biến an toàn. Chân ga sử dụng 2 biến trở, trong đó giá trị đường 2 luôn bằng một nửa đường 1.

`c
/* as/com/as.application/swc/vcu/PedalSensor.c */
#include "Dem.h"
#include "Std_Types.h"

#define DTC_VCU_PEDAL_MISMATCH 0xP2138 /* Bướm ga/Chân ga - Sai lệch điện áp mạch cảm biến D/E */

/* 
 * Sensor 1 (Main): Hoạt động từ 0.5V (500mV) đến 4.5V (4500mV) tương ứng 0-100%
 * Sensor 2 (Sub): Hoạt động từ 0.25V (250mV) đến 2.25V (2250mV)
 */
boolean PedalSensor_PlausibilityCheck(uint16 adc1_mV, uint16 adc2_mV) {
    /* Chuẩn hóa điện áp về tỷ lệ phần trăm hành trình bàn đạp (Normalize to percentage) */
    int32 pct1 = ((int32)adc1_mV - 500) * 100 / 4000;
    int32 pct2 = ((int32)adc2_mV - 250) * 100 / 2000;
    
    /* Xử lý chặn ngưỡng (Clamping) 0-100% */
    if (pct1 < 0) pct1 = 0; if (pct1 > 100) pct1 = 100;
    if (pct2 < 0) pct2 = 0; if (pct2 > 100) pct2 = 100;
    
    /* Tính toán độ lệch tuyệt đối giữa 2 cảm biến */
    int32 diff = pct1 - pct2;
    if (diff < 0) diff = -diff;
    
    /* Kiểm tra Plausibility: Mức độ sai lệch tối đa cho phép là 5% */
    if (diff > 5) {
        /* Báo lỗi, cắt mô-men xoắn để đảm bảo an toàn */
        Dem_SetEventStatus(DTC_VCU_PEDAL_MISMATCH, DEM_EVENT_STATUS_FAILED);
        return FALSE; 
    }
    
    /* Trạng thái bình thường */
    Dem_SetEventStatus(DTC_VCU_PEDAL_MISMATCH, DEM_EVENT_STATUS_PASSED);
    return TRUE;
}
`

### Step 2 & 3: Torque Coordination & Mode Switch State Machine
- Triển khai State Machine chuyển chế độ (PRND) có chống nhiễu (debounce) và đảm bảo điều kiện chuyển (ví dụ: chỉ được chuyển từ N sang D khi chân phanh đang được đạp).
- Trong chế độ Drive (D), Torque Request được tính toán tuyến tính theo hành trình chân ga. Khi ở chế độ Reverse (R), giới hạn Torque và tốc độ di chuyển thấp hơn. Nếu nhả hoàn toàn chân ga (0%), kích hoạt Regenerative Braking (Mô-men xoắn âm).

### Step 4: CAN Broadcast
Đóng gói tín hiệu Torque Command và trạng thái hoạt động VCU, gửi định kỳ qua CAN bus:
- **CAN ID**:  0x200
- Payload chứa giá trị Torque yêu cầu (Nm) tới Inverter động cơ.

**Success Criteria:**
- Giá trị Torque Request xuất ra CAN lập tức bằng 0 Nm nếu Plausibility Check thất bại (mô phỏng một tín hiệu ADC bị kẹt giá trị).
- Hệ thống tuân thủ chặt chẽ Torque Map trong các chế độ P/R/N/D.

---

## TASK 6.3: Mini BCM — Central Door Lock với Sleep/Wakeup (~8h, Advanced)

**Objective:** Xây dựng phần mềm Body Control Module (BCM) mô phỏng logic khóa cửa trung tâm, kết hợp chặt chẽ với cơ chế quản lý năng lượng (Power Management) bằng cách sử dụng các bản phân hệ EcuM (ECU State Manager) để xử lý Sleep và Wakeup.

**Features (Chức năng cốt lõi):**
- Tiếp nhận chuỗi lệnh khóa/mở cửa (Lock/Unlock) thông qua một bản tin CAN riêng biệt (CAN ID:  0x300).
- Điều khiển mức logic (GPIO simulation) để đóng ngắt 4 rơ-le khóa cửa.
- **Auto-Sleep:** Theo dõi hoạt động CAN. Nếu sau 30 giây không có bất kỳ frame CAN nào được thu nhận, ECU sẽ đi vào chế độ Sleep (ngủ đông) nhằm tiết kiệm năng lượng.
- **Wakeup Event:** Hệ thống bị đánh thức khi có tín hiệu trên bus CAN (Network Wakeup) hoặc bởi bộ định thời cục bộ (Timer).

### EcuM Sleep/Wakeup Sequence Implementation

`c
/* as/com/as.application/swc/bcm/BcmPowerManager.c */
#include "EcuM.h"
#include "NvM.h"
#include "CanIf.h"

/* 
 * Hàm xử lý tiến trình tắt thiết bị (Chuẩn bị vào Sleep) 
 * Được gọi khi bộ đếm inactivity vượt quá 30 giây 
 */
void BCM_GoToSleep(void) {
    printf("[BCM] Preparing for sleep mode...\n");
    
    /* 1. Lưu trữ tất cả dữ liệu hành vi (VD: Trạng thái cửa đang khóa hay mở) vào EEPROM */
    NvM_WriteAll(); 
    
    /* 2. Cấu hình phần cứng vi điều khiển (CAN Transceiver & Controller) sang chế độ năng lượng thấp */
    CanIf_SetControllerMode(CAN_0, CAN_CS_SLEEP);
    
    printf("[BCM] Entering Low Power Mode. All peripherals halted.\n");
    
    /* 3. Dừng hệ điều hành, đưa CPU vào trạng thái Halt (WFI - Wait For Interrupt) */
    EcuM_GoHalt();
}

/*
 * Hàm xử lý ngắt đánh thức (Wakeup Interrupt Handler)
 * Được hệ thống gọi ngay khi phát hiện sự kiện đánh thức hợp lệ
 */
void BCM_WakeupHandler(EcuM_WakeupSourceType source) {
    printf("[BCM] System Wakeup triggered from source: 0x%X\n", source);
    
    /* 
     * Xác thực nguồn đánh thức. Đảm bảo đây là nguồn hợp lệ (VD: Nút bấm thật, CAN Rx thật) 
     * chứ không phải là nhiễu xung gai (Spike/Glitch) trên đường truyền.
     */
    EcuM_ValidateWakeupEvent(source);
    
    /* Tiếp tục khôi phục cấu hình ngoại vi và đưa hệ thống về RUN mode */
}
`

**Success Criteria:**
- Phân tích nhật ký nguồn mô phỏng (Power consumption log) cho thấy tiêu thụ dòng rò dưới mức < 1mA trong suốt khoảng thời gian Sleep.
- Hệ thống xử lý đúng Sleep Sequence, không bị kẹt trong State Machine.
- **Pitfall Analysis:** Hệ thống phải giữ nguyên trạng thái khóa cửa sau chu kỳ Wakeup-Sleep. Nếu quên không gọi hàm NvM_WriteAll() trước lúc ngủ, bộ não BCM sẽ mất đồng bộ.

---

## TASK 6.4 (Extension): Full Integration Test — BMS + VCU + BCM (~12h, Advanced)

**Objective:** Tổng hợp và mô phỏng chạy song song cả 3 ECU (BMS, VCU, BCM) trên cùng một mạng mô phỏng CAN bus bằng cách sử dụng POSIX virtual CAN (can0) hoặc socketCAN trên nền tảng Linux.

**Kiến trúc truyền thông giả định (Message Flow Diagram):**
- **BMS** phát trạng thái: BMS_Status (0x180)
- **VCU** gửi lệnh điều khiển động cơ: VCU_TorqueCmd (0x200)
- **BCM** phát lệnh tiện nghi xe: BCM_DoorCmd (0x300)

### Test Scenarios (Các kịch bản tích hợp hệ thống)

1. **SoC Low Scenario (Kiểm soát năng lượng cạn kiệt):**
   - BMS tính toán và báo SoC < 20% qua  0x180.
   - VCU nhận gói tin CAN, tự động thực hiện giới hạn năng lượng, ép Torque Max Request xuống chỉ còn 50 Nm (Limp-home mode).
   
2. **Over-temp Scenario (Xử lý khủng hoảng nhiệt độ pin):**
   - Bộ BMS mô phỏng cảm biến nhiệt độ báo > 60°C liên tục.
   - VCU nhận diện cờ nhiệt độ cao qua bus CAN và ngay lập tức gửi lệnh Torque Request =  0 Nm, đồng thời dừng quá trình sạc hồi năng (Regen Braking) để không làm nóng pin thêm.

3. **Door Unlock Scenario (Đồng bộ khởi động mạng thông tin):**
   - BCM nhận lệnh Unlock vật lý (hoặc mô phỏng RF).
   - BCM phát sóng CAN Wakeup kèm message  0x300 báo mở cửa.
   - BMS và VCU, vốn đang ở chế độ Sleep, bị đánh thức qua mạng CAN, thực hiện boot sequence chuẩn bị sẵn sàng khởi hành.

4. **Night Park Scenario (Mô phỏng xe đỗ qua đêm):**
   - Không có bất cứ hoạt động ngoại vi nào (chân ga, nút bấm) trong suốt 60 giây.
   - BCM khởi tạo quá trình đi ngủ.
   - Sau khi CAN bus dừng phát các message chu kỳ, các node mạng BMS/VCU cũng tự động kích hoạt tiến trình EcuM_GoHalt() để bảo toàn dung lượng ắc quy 12V.

**Success Criteria (Tiêu chí thành công):**
- Tổng thể mạng ECU trao đổi dữ liệu mượt mà, không gặp hiện tượng Bus-off hay rớt frame dữ liệu.
- Phần mềm simulator chạy ổn định (stable) tối thiểu 30 phút liên tục trong bài test stress tải mà không xảy ra hiện tượng tràn bộ nhớ hay crash hệ thống.
- Các module phản ứng đúng logic như mô tả trong Test Scenarios khi có sự kiện chéo (Cross-ECU events).
