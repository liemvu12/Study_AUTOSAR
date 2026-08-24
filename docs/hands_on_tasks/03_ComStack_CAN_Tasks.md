# TASK PLAN: Chuyên Đề 03 - Communication Stack & CAN

**Cấu trúc source code thực tế:**
- s/com/as.infrastructure/communication/CanIf/ (CanIf.c, CanIf.h)
- s/com/as.infrastructure/communication/CanTp/ (CanTp.c)
- s/com/as.infrastructure/communication/PduR/ (PduR.c)
- s/com/as.infrastructure/communication/Com/ (Com.c)
- s/com/as.infrastructure/arch/stm32f1/mcal/Can.c (CAN MCAL Driver)
- Build: scons --board=posix

---

## TASK 3.1: CAN Bit Timing Calculation
**Thời gian ước tính:** ~1h
**Mức độ:** Beginner

**Mục tiêu (Objective):** Tính toán BTR0/BTR1 registers cho baudrate 500 kbps tại clock 36MHz (STM32F107).

**Lý thuyết & Công thức:**
- Bit Time = 1 / Baudrate
- 1 Bit Time = Sync_Seg + Prop_Seg + Phase_Seg1 + Phase_Seg2
- Target: Sample Point = 87.5%, SJW = 1 TQ

**Yêu cầu công việc:**
1. Viết Python script tính toán và verify các giá trị cấu hình bit timing.
2. Verify kết quả đầu ra (Ví dụ cho 36MHz/500kbps: BRP=3, TS1=11, TS2=2).

**Python Script Example:**
`python
def calculate_can_timing(clock, baudrate, target_sample_point):
    # Logic tính toán mẫu
    bit_time = clock / baudrate
    brp = 3
    ts1 = 11
    ts2 = 2
    return brp, ts1, ts2

brp, ts1, ts2 = calculate_can_timing(36000000, 500000, 87.5)
print(f"BRP={brp}, TS1={ts1}, TS2={ts2}")
`

**Kết quả kỳ vọng (Success Criteria):** Sample Point đạt giá trị tính toán nằm trong khoảng 75% - 87.5%.

---

## TASK 3.2: Read CAN Driver Source Code — Config Mailbox
**Thời gian ước tính:** ~3h
**Mức độ:** Intermediate

**Mục tiêu (Objective):** Đọc và phân tích s/com/as.infrastructure/arch/stm32f1/mcal/Can.c.

**Yêu cầu công việc:**
1. Tìm hiểu struct Can_PduType, HTH (Hardware Transmit Handle), HRH (Hardware Receive Handle).
2. Trace hàm Can_Write(): Phân tích đường đi từ API call xuống việc ghi vào thanh ghi phần cứng.
3. Viết đoạn code config mailbox và gọi Can_Write() để gửi frame CAN ID=0x123.

**Code Snippet Example:**
`c
#include "Can.h"

void Send_Can_Frame_0x123(void) {
    Can_PduType PduInfo;
    uint8 payload[8] = {0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08};
    
    PduInfo.id = 0x123;
    PduInfo.length = 8;
    PduInfo.sdu = payload;
    PduInfo.swPduHandle = 0;
    
    /* HTH=0 (Giả sử Handle 0 map với Transmit Mailbox 0) */
    Can_ReturnType ret = Can_Write(0, &PduInfo);
}
`

**Kết quả kỳ vọng (Success Criteria):** Code compile thành công, giải thích được HTH/HRH mapping.
**Pitfall cần tránh:** Nhầm lẫn cấu hình HTH vs HRH, lỗi không xử lý điều kiện Mailbox Full.

---

## TASK 3.3: CanIf Software Acceptance Filter
**Thời gian ước tính:** ~2h
**Mức độ:** Intermediate

**Mục tiêu (Objective):** Đọc CanIf source, hiểu cơ chế lọc CAN ID bằng software.
**Files:** s/com/as.infrastructure/communication/CanIf/CanIf.c

**Yêu cầu công việc:**
1. Tìm hàm CanIf_RxIndication() - trace từ ISR CAN báo nhận, đẩy lên CanIf.
2. Viết config để chỉ nhận CAN ID trong range 0x100-0x1FF, reject ngoài range.
3. Viết code kiểm tra bằng counter: đếm số lượng accepted vs rejected frames.

**Code Snippet Example:**
`c
uint32 accepted_frames = 0;
uint32 rejected_frames = 0;

void CanIf_RxIndication(uint8 Hrh, Can_IdType CanId, uint8 CanDlc, const uint8 *CanSduPtr) {
    if(CanId >= 0x100 && CanId <= 0x1FF) {
        accepted_frames++;
        // Tiếp tục gọi lên lớp trên, vd: PduR_RxIndication(...);
    } else {
        rejected_frames++; // Frame bị reject
    }
}
`

**Kết quả kỳ vọng (Success Criteria):** Frame ngoài range bị reject, counter chạy đúng.

---

## TASK 3.4: CanTp Multi-Frame Transmission
**Thời gian ước tính:** ~4h
**Mức độ:** Advanced

**Mục tiêu (Objective):** Trace và implement việc gửi UDS request 20 bytes qua CanTp phân mảnh.
**Files:** s/com/as.infrastructure/communication/CanTp/CanTp.c

**Yêu cầu công việc:**
1. Trace các PCI frame types: SF (≤7 bytes), FF (first frame), CF (consecutive frame), FC (flow control).
2. Thiết lập cấu hình: BS=3, STmin=10ms.
3. Vẽ sequence diagram minh họa tiến trình phân mảnh.
4. Code ví dụ gửi 20 bytes: tạo buffer 20 bytes và gọi CanTp_Transmit().

**Sequence Diagram:**
`mermaid
sequenceDiagram
    participant Sender
    participant Receiver
    Sender->>Receiver: FF (First Frame)
    Receiver-->>Sender: FC (CTS, BS=3, STmin=10ms)
    Sender->>Receiver: CF1 (Consecutive Frame 1)
    Note over Sender: Wait STmin (10ms)
    Sender->>Receiver: CF2 (Consecutive Frame 2)
    Note over Sender: Wait STmin (10ms)
    Sender->>Receiver: CF3 (Consecutive Frame 3)
    Receiver-->>Sender: FC (Wait/CTS)
    Sender->>Receiver: CF4 (Consecutive Frame 4)
`

**Code Snippet Example:**
`c
void Send_Diagnostic_Request(void) {
    PduInfoType PduInfo;
    uint8 uds_data[20] = { 0x22, 0xF1, 0x90, 0x00, /* ... */ };
    
    PduInfo.SduDataPtr = uds_data;
    PduInfo.SduLength = 20;
    
    CanTp_Transmit(CANTP_TX_UDS_ID, &PduInfo);
}
`

**Kết quả kỳ vọng (Success Criteria):** Trace được toàn bộ sequence chuẩn theo ISO 15765-2 (ISOTP).

---

## TASK 3.5: COM — Signal Packing into I-PDU
**Thời gian ước tính:** ~3h
**Mức độ:** Advanced

**Mục tiêu (Objective):** Config COM module pack 3 signals vào 1 I-PDU 8 bytes.

**Cấu hình Signals:**
- **VehicleSpeed**: 16-bit, byte 0-1, big-endian, factor=0.1 km/h.
- **GearPosition**: 4-bit, byte 2 bits [7:4].
- **DoorStatus**: 1-bit, byte 2 bit [3].

**Yêu cầu công việc:**
1. Đọc và hiểu s/com/as.infrastructure/communication/Com/Com.c.
2. Viết code gọi Com_SendSignal(ComConf_Signal_Speed, &speed).
3. Verify byte layout bằng printf hex dump I-PDU.

**Code Snippet Example:**
`c
void Update_Signals(void) {
    uint16 speed = 1000; /* speed=100 km/h (nếu factor=0.1 -> 1000) */
    uint8 gear = 3;
    uint8 door = 1;
    
    Com_SendSignal(ComConf_Signal_Speed, &speed);
    Com_SendSignal(ComConf_Signal_Gear, &gear);
    Com_SendSignal(ComConf_Signal_Door, &door);
}

void Hex_Dump_PDU(uint8* pdu_buffer) {
    printf("I-PDU: ");
    for(int i=0; i<8; i++) {
        printf("0x%02X ", pdu_buffer[i]);
    }
    printf("\n");
}
`

**Kết quả kỳ vọng (Success Criteria):** Hex dump đúng layout (ví dụ 0x00 0x64 cho speed=100 km/h tùy factor và endianness).
**Pitfall cần tránh:** Lỗi Byte order (Intel vs Motorola) và signal bit inversion.

---

## TASK 3.6 (Extension): Bus Load Calculation & Monitoring
**Thời gian ước tính:** ~2h
**Mức độ:** Advanced

**Mục tiêu (Objective):** Đo và tính toán bus load với N frames định kỳ trên đường truyền.

**Công thức:**
BusLoad = (N_frames * BitLength_worst_case) / (Baudrate * Cycle_ms * 0.001)

**Yêu cầu công việc:**
1. Viết Python script tính toán: ví dụ 10 frames * 130 bits / (500000 * 0.01) = 26%.
2. Implement counter đếm frames/giây trong CAN ISR.
3. Alert nếu bus load đo được > 80%.

**Python Script & C Code Snippet:**
`python
def calc_bus_load():
    n_frames = 10
    bit_length = 130
    baudrate = 500000
    cycle_ms = 10
    load = (n_frames * bit_length) / (baudrate * (cycle_ms / 1000.0)) * 100
    print(f"Bus Load: {load}%")
    
calc_bus_load()
`

`c
uint32 frame_count = 0;

void Can_Rx_ISR(void) {
    frame_count++;
}

void Monitor_BusLoad_Task(void) {
    // Gọi định kỳ 1s
    float load = (float)(frame_count * 130) / (500000.0 * 1.0) * 100.0;
    if(load > 80.0) {
        printf("ALERT: Bus Load Critical (%.1f%%)\n", load);
    }
    frame_count = 0; // Reset counter
}
`

**Kết quả kỳ vọng (Success Criteria):** Hiển thị được bus load thực tế và cảnh báo đúng điều kiện.

