# TASK PLAN Chuyên Đề 04: Diagnostic UDS & Memory Stack

## Cấu trúc source code tham khảo
- s/com/as.infrastructure/diagnostic/Dcm/ (DCM module)
- s/com/as.infrastructure/diagnostic/Dem/ (DEM module)
- s/com/as.infrastructure/diagnostic/Det/ (DET module)
- s/com/as.infrastructure/memory/NvM/ (NvM manager)
- s/com/as.infrastructure/memory/MemIf/ (Memory interface)
- s/com/as.infrastructure/memory/Fee/ (Flash EEPROM Emulation)
- s/com/as.infrastructure/memory/Ea/ (EEPROM Abstraction)

---

## TASK 4.1: DCM — Implement Service 0x22 Read DID (~3h, Intermediate)
**Objective**: Implement UDS Service 0x22 để đọc VIN (DID 0xF190).
- **UDS Request bytes**: 22 F1 90
- **UDS Response**: 62 F1 90 57 30 56 30 45 47 50 30 30 30 30 30 30 30 30 (17 bytes VIN)
- **Files**: s/com/as.infrastructure/diagnostic/Dcm/Dcm.c

**Các bước thực hiện**:
1. Tìm callback function Dcm_ReadDataByIdentifier() hoặc hàm tương đương.
2. Implement hàm callback trả về chuỗi VIN 17 ký tự.
3. Test bằng Python script gửi raw CAN frame qua virtual CAN interface.

**Python test script mẫu**:
`python
import socket

# Gửi UDS request 22 F1 90 qua CAN/UART simulator
request = bytes([0x22, 0xF1, 0x90])
# ... Gửi qua interface ...

# Parse response: nếu byte 0 == 0x62 → positive response
# response = can_recv()
# if response[0] == 0x62:
#     print("Positive Response!")
`

**Tiêu chí hoàn thành (Success)**:
- Response đúng format 62 F1 90 [VIN bytes].

**Lưu ý (Pitfall)**:
- Nếu DID chưa được config, hệ thống có thể trả về NRC 0x31 (requestOutOfRange).

---

## TASK 4.2: DCM — Service 0x27 SecurityAccess Seed/Key (~4h, Advanced)
**Objective**: Implement thuật toán bảo mật Seed/Key để unlock Extended Session.
- **Flow**: Tester gửi 27 01 → ECU trả seed 4 bytes → Tester tính Key → gửi 27 02 [Key]
- **Thuật toán mẫu**: Key = (Seed XOR 0x12345678) + 0xABCD
- **Files**: s/com/as.infrastructure/diagnostic/Dcm/Dcm.c

**Code C mẫu cho ECU side (server)**:
`c
static uint32 StoredSeed = 0;

Std_ReturnType Dcm_GetSeed(uint8 SecurityAccessType, uint8* Seed, uint16 SeedLen) {
    StoredSeed = (uint32)(GetSystemTick() ^ 0xDEAD);
    Seed[0] = (StoredSeed >> 24) & 0xFF;
    Seed[1] = (StoredSeed >> 16) & 0xFF;
    Seed[2] = (StoredSeed >> 8) & 0xFF;
    Seed[3] = (StoredSeed & 0xFF);
    return E_OK;
}

Std_ReturnType Dcm_CompareKey(uint8 SecurityAccessType, uint8* Key, uint16 KeyLen) {
    uint32 ExpectedKey = (StoredSeed ^ 0x12345678UL) + 0xABCDUL;
    uint32 ReceivedKey = (Key[0]<<24) | (Key[1]<<16) | (Key[2]<<8) | Key[3];
    return (ExpectedKey == ReceivedKey) ? E_OK : E_NOT_OK;
}
`

**Các bước thực hiện**:
1. Tích hợp code mẫu xử lý cho Service 0x27.
2. Viết Python script tính Key từ Seed để test.

**Tiêu chí hoàn thành (Success)**:
- Unlock thành công, gọi được Service  x2E Write DID.

**Lưu ý (Pitfall)**:
- Seed = 0 vulnerability.
- Attempt counter không reset khi unlock sai nhiều lần.

---

## TASK 4.3: DEM — Report DTC và Debounce (~3h, Intermediate)
**Objective**: Implement event monitoring với debounce, khi Over-temperature xảy ra sẽ set DTC P0A7E.
- **Files**: s/com/as.infrastructure/diagnostic/Dem/Dem.c

**Code mẫu**:
`c
/* Gọi trong task 10ms */
void Monitor_Temperature_Runnable(void) {
    uint8 temp = ADC_ReadTemperature();
    if (temp > 60) {
        Dem_SetEventStatus(DemConf_DemEventParameter_OverTemp, DEM_EVENT_STATUS_FAILED);
    } else {
        Dem_SetEventStatus(DemConf_DemEventParameter_OverTemp, DEM_EVENT_STATUS_PASSED);
    }
}
`

**Các bước thực hiện**:
1. Implement hàm giám sát nhiệt độ như mẫu.
2. Test: gọi Dem_SetEventStatus FAILED 10 lần liên tiếp để qua ngưỡng debounce.
3. Verify bằng UDS Request  x19 02 (đọc list DTC).

**Tiêu chí hoàn thành (Success)**:
- DTC status byte bit 3 (confirmedDTC) = 1 sau debounce threshold.

**Lưu ý (Pitfall)**:
- Debounce counter chưa đủ ngưỡng, DTC chưa confirmed.

---

## TASK 4.4: NvM — Save Calibration Data with Persistence (~4h, Advanced)
**Objective**: Lưu struct calibration 32 bytes vào Flash, verify sau power cycle (restart).
- **Files**: s/com/as.infrastructure/memory/NvM/NvM.c

**Struct cần lưu**:
`c
typedef struct {
    uint16 BatteryCapacity_mAh;
    uint8  ChargeThreshold_pct;
    uint8  DischargeThreshold_pct;
    uint32 TotalMileage_km;
    uint8  Padding[24];
} CalibrationData_t;
`

**Sequence bất đồng bộ**:
1. NvM_WriteBlock(NvMConf_Block_CalData, &CalData) → trả về E_OK ngay.
2. NvM_MainFunction() chạy trong background task xử lý ghi vào Flash.
3. Callback NvM_JobFinishedNotification() báo hoàn tất quá trình ghi.

**Các bước thực hiện**:
1. Hiện thực logic gọi hàm ghi bất đồng bộ.
2. Restart process (POSIX: kill và chạy lại).
3. Đảm bảo NvM_ReadAll() phục hồi đúng data.

**Tiêu chí hoàn thành (Success)**:
- Struct đọc lại đúng giá trị ban đầu, CRC check pass.

**Lưu ý (Pitfall)**:
- Không gọi NvM_WriteAll() trước shutdown có thể gây mất data.

---

## TASK 4.5: Fee — Wear Leveling Analysis (~3h, Advanced)
**Objective**: Hiểu cơ chế Wear Leveling của Fee, tránh brick Flash.
- **Files**: s/com/as.infrastructure/memory/Fee/Fee.c

**Các bước thực hiện**:
1. Trace các hàm: Fee_Write(), Fee_Read(), Fee_EraseImmediateBlock().
2. Mô phỏng ghi 100 lần block nhỏ, đếm số lần thao tác Flash erase.
3. Tính toán: Flash thường chịu 100.000 lần erase. Với 100 lần/ngày → tuổi thọ ~2.7 năm nếu không có wear leveling.
4. Verify Virtual Sector swap: Sector 1 đầy → copy dữ liệu active sang Sector 2 → erase Sector 1.

**Tiêu chí hoàn thành (Success)**:
- Code không làm brick flash (erase counter không tăng đột biến mỗi lần ghi dữ liệu nhỏ).

---

## TASK 4.6 (Extension): Freeze Frame — Snapshot On Fault (~4h, Advanced)
**Objective**: Khi DTC P0A7E xảy ra, chụp snapshot 5 signals lưu thành Freeze Frame.

**Snapshot data structure**:
`c
typedef struct {
    uint16 PackVoltage_100mV;
    sint16 PackCurrent_100mA;
    uint8  MaxCellTemp_C;
    uint8  SoC_pct;
    uint8  ContactorState;
} FreezeFrame_t;
`

**Các bước thực hiện**:
1. Config DEM module để tự động lưu Freeze Frame khi confirmDTC xảy ra.
2. Gắn kết 5 signals vào Record Data.
3. Đọc lại Freeze Frame bằng UDS Request  x19 04 [DTC_bytes].

**Tiêu chí hoàn thành (Success)**:
- Parse được 5 signals từ các byte raw của UDS response.
