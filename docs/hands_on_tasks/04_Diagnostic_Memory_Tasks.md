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
- Unlock thành công, gọi được Service 