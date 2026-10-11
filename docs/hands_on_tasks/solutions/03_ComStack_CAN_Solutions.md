# LỜI GIẢI TOÀN DIỆN CHUYÊN ĐỀ 03 — COMMUNICATION STACK & CAN PROTOCOL
## Đáp Án Thực Hành Chi Tiết 11 Tasks: End-to-End CAN Trace, Bit Timing, CanIf, CanTp, COM, Bus Load, Physical Oscilloscope, ARXML Toolchain, CanSM Bus-Off & System ARXML RTE Routing

> 📚 **Tài liệu lý thuyết đối chiếu:** [`docs/theory/03_Communication_Stack_And_CAN_Protocol.md`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/docs/theory/03_Communication_Stack_And_CAN_Protocol.md)  
> 📑 **Ma trận gói tin & DBC:** [`docs/theory/10_CAN_DBC_Format_And_Tools.md`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/docs/theory/10_CAN_DBC_Format_And_Tools.md)  
> 🔧 **Mã nguồn gốc đối chiếu:** [`as/com/as.infrastructure/communication/`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/com/as.infrastructure/communication/)  
> 🎯 **File nhiệm vụ:** [`docs/hands_on_tasks/03_ComStack_CAN_Tasks.md`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/docs/hands_on_tasks/03_ComStack_CAN_Tasks.md)

---

## 📡 LỜI GIẢI TASK 3.1: Trace Dòng Chảy CAN Message 6 Tầng Toàn Diện Trong Mã Nguồn Gốc (Tx & Rx Path)

> 🎯 **Mục tiêu:** Trace 1 thông điệp CAN xuyên suốt 6 tầng kiến trúc AUTOSAR theo cả 2 chiều hoàn toàn dựa trên **mã nguồn gốc có sẵn của dự án `as` (100% Native Code Base & Exact Call Trees)**:
> 1. **Chiều Gửi (Tx Path):** Trace dòng chảy gói tin thời gian gốc **`TxMsgTime` (CAN ID: `0x101`)** qua toàn bộ ngăn xếp BSW COM và gói tin quản trị mạng gốc **`OSEK_NM_TX` (CAN ID: `0x401`)** từ Lõi BSW $\longrightarrow$ PduR $\longrightarrow$ CanIf $\longrightarrow$ MCAL Driver $\longrightarrow$ Dây Bus CAN vật lý.
> 2. **Chiều Nhận (Rx Path):** Trace dòng chảy gói tin tốc độ xe gốc **`RxMsgAbsInfo` (CAN ID: `0x102`)** từ Khung mạng vật lý MCAL $\longrightarrow$ CanIf $\longrightarrow$ PduR $\longrightarrow$ COM $\longrightarrow$ RTE $\longrightarrow$ Application SWC (`widget_refresh.c`).

---

### 📤 PHẦN A: CHIỀU GỬI GÓI TIN CAN GỐC (TX PATH: NATIVE BSW COM & NM $\longrightarrow$ HARDWARE)

> 💡 **Khởi tạo gói tin Tx gốc trong cấu hình dự án (`autosar.arxml`):**
> Gói tin CAN Tx gốc được định nghĩa trong [`as/com/as.application/common/autosar.arxml: L352`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/com/as.application/common/autosar.arxml#L352) là **`TxMsgTime` (CAN ID: `0x101`, DLC: 8 bytes)** với thuộc tính `TxMode="PERIODIC"`, `TimePeriodFactor="100"` (chu kỳ 100ms) và dữ liệu khởi tạo `SystemTime` (`2013-12-15 19:49:00`, Unused byte `0x5A`).

#### 1. Chuỗi Gọi Hàm Function-Call-Function Chiều Gửi Chuẩn COM Stack (`TxMsgTime` 0x101):
```text
┌────────────────────────────────────────────────────────────────────────────────────────────────┐
│  🚗 QUY TRÌNH THỰC THI 6 TẦNG AUTOSAR COM TX NGUYÊN BẢN (KHÔNG CẦN APP TRIGGER):                │
└────────────────────────────────────────────────────────────────────────────────────────────────┘

1. [BSW INITIALIZATION & IPDU GROUP ACTIVATION]
   TASK(SchM_Startup) (as/com/as.infrastructure/system/SchM/SchM.c: L439-L441)
        │
        ├── 1. Com_Init(&ComConfiguration)
        └── 2. Com_IpduGroupStart(COM_DEFAULT_IPDU_GROUP, True)  ──► Kích hoạt PduGroup1
                │
                ▼
2. [BSW COM LAYER — CHU KỲ PHÁT TỰ ĐỘNG (PERIODIC TRANSMISSION)]
   ALARM(Alarm_BswService) (SchM.c: L561) kích hoạt mỗi 10ms -> TASK(SchM_BswService) (SchM.c: L522)
   -> Gọi SCHM_MAINFUNCTION_COMTX() -> Com_MainFunctionTx() (Com_Sched.c: L98-L148)
        │
        ├── 1. Đếm lùi timer chu kỳ: timerDec(Arc_IPdu->Com_Arc_TxIPduTimers.ComTxModeTimePeriodTimer)
        └── 2. Khi hết chu kỳ 100ms (Timer == 0) -> TỰ ĐỘNG GỌI:
            └──► Com_Internal_TriggerIPduSend(COM_ID_TxMsgTime) (Com_Com.c: L198)
                    │
                    ├── Lấy bộ đệm TxMsgTime_IPduBuffer (8 bytes: [0x07, 0xDD, 0x0C, 0x0F, 0x13, 0x31, 0x00, 0x5A])
                    └── [DÒNG 236]: Gọi PduR_ComTransmit(PDUR_ID_TxMsgTime, &PduInfoPackage)
                            │
                            ▼
3. [PDU ROUTER LAYER (PduR)]
   PduR_ComTransmit() -> PduR_ARC_RouteTransmit()
   (as/com/as.infrastructure/communication/PduR/PduR.c: L85 & PduR_Routing.c: L59)
        │
        └── Tra bảng định tuyến pduRoutingTable[PDUR_ID_TxMsgTime]
            ──► [DÒNG 59]: Gọi CanIf_Transmit(PDUR_ID2_TxMsgTime, PduInfoPtr)
                │
                ▼
4. [CAN INTERFACE LAYER (CanIf)]
   CanIf_Transmit() (as/com/as.infrastructure/communication/CanIf/CanIf.c: L774-L785)
        │
        ├── Tra cấu hình CanIfTxPduConfigData trong CanIf_Cfg.c (Dòng 168):
        │   • CAN ID: 0x101 (Chuẩn 11-bit)
        │   • DLC: 8 bytes
        │   • Mailbox HTH: Can0Hth
        └── [DÒNG 785]: Gọi MCAL Driver: Can_Write(Can0Hth, &canPdu)
                │
                ▼
5. [MCAL CAN DRIVER & HARDWARE OUTPUT]
   Can_Write() (as/com/as.infrastructure/arch/common/mcal/SCan.c: L83-L108)
        └── Định dạng khung SLCAN "t101807DD0C0F1331005A" và bắn ra UART1 sang SavvyCAN!
```

---

### 📥 PHẦN B: CHIỀU NHẬN GÓI TIN CAN GỐC (RX PATH: HARDWARE $\longrightarrow$ SWC)

```text
┌────────────────────────────────────────────────────────────────────────────────────────────────┐
│  📥 QUY TRÌNH THỰC THI 6 TẦNG AUTOSAR CAN RX NGUYÊN BẢN:                                       │
└────────────────────────────────────────────────────────────────────────────────────────────────┘

1. [HARDWARE ISR / MCAL POLLING]
   Can_MainFunction_Read() (as/com/as.infrastructure/arch/common/mcal/SCan.c: L171)
        │
        └── Nhận gói tin từ thanh ghi Mailbox / Serial Buffer
            ──► [DÒNG 171]: Gọi CanIf_RxIndication(pdu.busid, SCANID(pdu.canid), pdu.dlc, pdu.data)
                │
                ▼
2. [CAN INTERFACE LAYER (CanIf)]
   CanIf_RxIndication() -> scheduleRxIndication()
   (as/com/as.infrastructure/communication/CanIf/CanIf.c: L350 & L1145)
        │
        ├── So khớp mặt nạ Software Filter Mask (Khớp đúng CAN ID 0x102)
        ├── Kiểm tra độ dài DLC (CanDlc >= 8 bytes)
        └── [DÒNG 403]: Match CANIF_USER_TYPE_CAN_PDUR -> Gọi PduR_CanIfRxIndication()
                │
                ▼
3. [PDU ROUTER LAYER (PduR)]
   PduR_CanIfRxIndication() -> PduR_ARC_RouteTransmit()
   (as/com/as.infrastructure/communication/PduR/PduR_Routing.c: L64)
        │
        └── Tra bảng Routing Table -> Chuyển tiếp lên Com_RxIndication()
                │
                ▼
4. [COM LAYER (Interaction Layer)]
   Com_RxIndication() -> Com_RxProcessSignals()
   (as/com/as.infrastructure/communication/Com/Com_Com.c: L263-L290)
        │
        └── [DÒNG 290]: Tách I-PDU 8 bytes thành từng tín hiệu riêng lẻ (VehicleSpeed, TachoSpeed)
            và lưu giá trị mới vào RAM Signal Buffer
                │
                ▼
5. [RUNTIME ENVIRONMENT (RTE)]
   Rte_Read_RPort_Speed_Speed(&speed) (Rte.c)
        │
        └── Gọi Com_ReceiveSignal(COM_SID_VehicleSpeed, &speed) (Com_Com.c: L72)
                │
                ▼
6. [APPLICATION SWC — VIRTUAL CLUSTER]
   widget_refresh.c: L48 (Hàm vẽ táp-lô: RefreshClusterSpeedPointer)
        └── Nhận giá trị speed từ CAN -> Tính góc quay kim đồng hồ hiển thị lên màn hình táp-lô!
```

---

## ⏱️ LỜI GIẢI TASK 3.2: Tính Toán Bit Timing & Kiểm Chứng Sample Point

### 1. Python Script Tính Toán Tự Động:
```python
def calculate_can_bit_timing(f_osc_hz, baudrate, target_sample_point=0.875):
    bit_time_s = 1.0 / baudrate
    best_match = None
    min_diff = 1.0
    
    # Số lượng Time Quanta (TQ) thường từ 8 đến 25
    for total_tq in range(8, 26):
        brp = f_osc_hz / (baudrate * total_tq)
        if brp.is_integer() and 1 <= brp <= 1024:
            brp = int(brp)
            sync_seg = 1
            # Sample Point = (sync_seg + prop_seg + phase_seg1) / total_tq
            # Đặt seg1 = prop_seg + phase_seg1
            seg1 = round(total_tq * target_sample_point) - sync_seg
            seg2 = total_tq - sync_seg - seg1
            
            if 1 <= seg1 <= 16 and 1 <= seg2 <= 8:
                actual_sp = (sync_seg + seg1) / total_tq
                diff = abs(actual_sp - target_sample_point)
                if diff < min_diff:
                    min_diff = diff
                    best_match = (brp, seg1, seg2, total_tq, actual_sp)
                    
    return best_match

# Chạy thử cho STM32F107 (f_osc = 36 MHz, Baudrate = 500 kbps)
result = calculate_can_bit_timing(36000000, 500000, 0.875)
print(f"STM32F107: BRP={result[0]}, Seg1={result[1]}, Seg2={result[2]}, Total TQ={result[3]}, SP={result[4]*100:.1f}%")
# Kết quả: BRP=3, Seg1=12, Seg2=2 (tổng 16 TQ, Sample Point = (1+13)/16 = 87.5%)
```

---

## 📬 LỜI GIẢI TASK 3.3: Khảo Sát CAN Driver MCAL — HTH / HRH & Ring Buffer

1. **Ý nghĩa struct `Can_PduType`:**
   Chứa thông tin của một gói tin CAN: ID (chuẩn hoặc mở rộng), DLC (độ dài dữ liệu), con trỏ mảng byte dữ liệu `sdu`, và chỉ số bộ xử lý phần cứng `swPduHandle`.
2. **Luồng thực thi trong `Can_Write()`:**
   - MCAL kiểm tra trạng thái bộ điều khiển CAN (phải ở trạng thái `CAN_CS_STARTED`).
   - Nếu phần cứng có Mailbox rảnh: nạp ID, DLC, và Data vào các thanh ghi của Mailbox rồi set bit yêu cầu truyền (`TXREQ`).
   - Nếu Mailbox bận: trả về `CAN_BUSY` để CanIf giữ gói tin trong hàng đợi bộ đệm.
3. **Bảo vệ vùng nhớ găng (`Irq_Save` / `Irq_Restore`):**
   Ngăn ngừa race condition giữa luồng phát của Task thông thường và luồng ngắt ISR khi cùng thao tác đẩy/rút dữ liệu trên Ring Buffer.

---

## 🛡️ LỜI GIẢI TASK 3.4: CanIf Software Acceptance Filter

1. **Phân tích công thức Bitmask:**
   ```c
   if ((CanId & entry->CanIfCanRxPduCanIdMask) == entry->CanIfCanRxPduCanId)
   ```
   - `CanIfCanRxPduCanIdMask = 0x7FF` (Tất cả 11-bit đều là 1): Bộ lọc yêu cầu **khớp chính xác 100%** CAN ID (Exact Match).
   - Nếu `Mask = 0x7F0`: 4 bit cuối là 0 (Don't care), cho phép nhận một dải gồm 16 ID liên tiếp từ `0x730` đến `0x73F`.
2. **Tại sao cần Software Filtering?**
   Phần cứng vi điều khiển chỉ có số lượng Mailbox giới hạn (thường từ 14 đến 32 bộ lọc). Mạng CAN trên xe có thể có hàng trăm ID khác nhau, do đó CanIf phải triển khai bộ lọc phần mềm để phân phối tiếp lên các module cấp cao.

---

## 📦 LỜI GIẢI TASK 3.5: CanTp Multi-Frame Transmission (ISO 15765-2 DoCAN)

```text
  UDS Client (Tester)                           ECU (CanTp Server)
         │                                              │
         │─── First Frame: FF (Payload > 8B, DL=64B) ──►│
         │    PCI = 0x10, 0x40 (Total Length = 64)      │ (CanTp cấp phát buffer Rx)
         │                                              │
         │◄── Flow Control: FC (CTS, BS=8, STmin=1ms) ──│
         │    PCI = 0x30, BS=8, STmin=1ms               │
         │                                              │
         │─── Consecutive Frame: CF 1 (SeqNum = 1) ────►│
         │─── Consecutive Frame: CF 2 (SeqNum = 2) ────►│
         │    ... (Giãn cách tối thiểu STmin = 1ms)     │
         │─── Consecutive Frame: CF 8 (SeqNum = 8) ────►│
         │                                              │
         │◄── Flow Control: FC (Tiếp tục CTS) ──────────│ (ECU đọc xong 8 frames, báo gửi tiếp)
         │                                              │
```

---

## 🔀 LỜI GIẢI TASK 3.6: COM — Signal Packing & Endianness

1. **Đoạn mã C trích xuất tín hiệu không làm biến dạng bit lân cận:**
   ```c
   /* Trích xuất tín hiệu GearPosition (4-bit, Byte 2, bits [7:4]) */
   uint8 raw_byte = pdu_buffer[2];
   uint8 gear = (raw_byte >> 4) & 0x0F;

   /* Đóng gói lại tín hiệu Gear mới vào PDU */
   pdu_buffer[2] = (pdu_buffer[2] & 0x0F) | ((new_gear & 0x0F) << 4);
   ```
2. **Khác biệt Intel (Little Endian) vs Motorola (Big Endian):**
   - **Intel:** Byte thấp ở địa chỉ thấp (LSB First). Start Bit quy định vị trí của LSB.
   - **Motorola:** Byte cao ở địa chỉ thấp (MSB First). Start Bit quy định vị trí của MSB.

---

## 📊 LỜI GIẢI TASK 3.7: Bus Load Calculation & Overload Monitoring

1. **Python Script Tính Bus Load:**
   ```python
   def can_bus_load(num_frames, bit_length, baudrate, cycle_s):
       bits_per_sec = (num_frames * bit_length) / cycle_s
       load_percent = (bits_per_sec / baudrate) * 100.0
       return load_percent

   # 10 frames * 130 bits, baudrate 500 kbps, chu kỳ 10ms (0.01s)
   load = can_bus_load(10, 130, 500000, 0.01)
   print(f"Bus Load: {load:.2f}%") # 26.00%
   ```
2. **Cơ chế giám sát trong CAN ISR:**
   Đếm số lượng khung hình nhận được trong cửa sổ 1 giây (`g_frame_count`). Nếu `g_frame_count * 130 > 500000 * 0.7` ($\text{Load} > 70\%$), gọi callback cảnh báo lên hệ thống chẩn đoán DEM.

---

## 🔬 LỜI GIẢI TASK 3.8: Tầng Vật Lý, Trở Kháng Đầu Cuối 120Ω & Bắt Bệnh Sóng Oscilloscope

### Phần A: Đo Kiểm Trở Kháng Đầu Cuối Bằng Đồng Hồ VOM
1. **Tại sao chỉ 2 ECU đầu/cuối có trở $120\Omega$?**  
   Đường trục chính CAN là một đường dây truyền sóng cao tần có trở kháng đặc tính $Z_0 \approx 120\Omega$. Điện trở $120\Omega$ đặt ở 2 đầu xa nhất để hấp thụ hoàn toàn năng lượng sóng, triệt tiêu hiện tượng dội ngược (Signal Reflection). Nút giữa nếu gắn thêm trở sẽ phá vỡ tổng trở bus.
2. **Tổng trở tương đương chuẩn:**  
   $$R_{\text{bus}} = 120\Omega \parallel 120\Omega = 60\Omega$$
3. **Khi cắm nhầm ECU thứ 3 có trở $120\Omega$:**  
   $$R_{\text{bus\_mới}} = 120\Omega \parallel 120\Omega \parallel 120\Omega = 40\Omega$$
   - Dòng điện vi sai: $I_{\text{diff}} = \frac{2.0\text{V}}{40\Omega} = 50\text{mA}$ (tăng $50\%$ so với mức chuẩn $33.3\text{mA}$).
   - **Hậu quả:** Transceiver bị quá tải nhiệt, bảo vệ ngắt quá dòng kích hoạt làm sụt áp vi sai $V_{\text{diff}} < 1.5\text{V}$, bus sinh Error Frame chập chờn.

### Phần B: Giải Mã Dạng Sóng Thực Tế Trên Màn Hình Máy Hiện Sóng
1. **Mức điện áp:**  
   - Điện áp tĩnh (Recessive): Cả CAN_H và CAN_L cùng nằm tại vạch **$+2.5\text{V}$** ($V_{\text{diff}} = 0.0\text{V}$).  
   - Điện áp Dominant: CAN_H vọt lên **$+3.5\text{V}$**, CAN_L tụt xuống **$+1.5\text{V}$** ($V_{\text{diff}} = +2.0\text{V}$).
2. **Tốc độ Baudrate:**  
   $$\text{Baudrate} = \frac{1}{T_{\text{bit}}} = \frac{1}{2.0 \times 10^{-6}\text{ s}} = 500,000\text{ bps} = 500\text{ kbps}$$
3. **Sườn xung:**  
   - Sườn lên nhanh ($t_{\text{rise}} < 50\text{ns}$) do transistor chủ động cấp dòng (**Active Drive**).  
   - Sườn xuống thoai thoải hơn ($50\text{ns} - 100\text{ns}$) do phụ thuộc vào quá trình xả dòng tự nhiên qua điện trở kết thúc $60\Omega$ và tụ ký sinh của dây (**Passive Release**).

### Phần C: Bảng Bắt Bệnh 4 Dị Tật Tín Hiệu

| Dị tật sóng trên Oscilloscope | Nguyên nhân gốc rễ | Giải pháp khắc phục |
| :--- | :--- | :--- |
| **Sóng có xung gai rung gợn (Ringing $> 4.0\text{V}$)** | **Mất 1 điện trở đầu cuối** (đo VOM ra $120\Omega$). Đầu cáp hở làm sóng dội ngược. | Kiểm tra lại 2 đầu giắc cắm của BMS và BCM, hàn bổ sung trở $120\Omega$. |
| **Biên độ vi sai thấp ($V_{\text{diff}} < 1.2\text{V}$)** | **Thừa điện trở đầu cuối** (đo VOM ra $40\Omega$ hoặc $30\Omega$). | Rút từng ECU ra đo để tìm ECU trung gian nào đang bị bật nhầm công tắc trở kết thúc. |
| **Đường $2.5\text{V}$ bị dời lên $3.8\text{V}$ (Ground Shift)** | **Lệch điện áp mass** giữa các ECU do cọc tiếp địa vỏ xe bị rỉ sét. | Vệ sinh lại điểm bắt ốc mass khung xe (Chassis Grounding). |
| **CAN_H hoặc CAN_L ghim ở $0\text{V}$ hoặc $12\text{V}$** | Chạm chập dây cáp: Short-to-GND hoặc Short-to-VBAT. | Dùng VOM thang đo thông mạch để định vị đoạn dây bị tróc vỏ chạm mass hoặc chạm nguồn. |

---

## 🛠️ LỜI GIẢI TASK 3.9: Cấu Hình ARXML & Sinh Mã C Bằng Python Toolchain (`argen`)

### 1. Thêm gói tin mới vào `autosar.arxml`:
Mở file [`as/com/as.application/common/autosar.arxml`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/com/as.application/common/autosar.arxml), chèn đoạn XML sau vào thẻ `<CanIf><TxPduList>`:
```xml
<Pdu Comment="BMS Pack Status Frame" DataLengthCode="8" 
     EcuCPduRef="TxBmsPackStatus" HthRef="LS_Hth" 
     Identifier="0x250" Name="BmsPackStatus" 
     TransmitNotifier="PduR" UserNotification="CanIf_User" />
```
Đồng thời thêm vào `<PduR><RoutineList>` tuyến chuyển tiếp:
```xml
<Source Comment="*" Module="Com" Name="ComBmsStatus" PduRef="TxBmsPackStatus">
    <DestinationList Max="TBD">
        <Destination Comment="*" Module="CanIf" Name="CanIfBmsStatus" PduRef="TxBmsPackStatus" />
    </DestinationList>
</Source>
```

### 2. Lệnh Chạy Bộ Sinh Mã Python:
```powershell
cd C:\Users\liem.vu\Liem.vuOD\Study_AUTOSAR-main\as\com\as.tool\config.infrastructure.system
python -m argen.GenCanIf autosar.arxml
python -m argen.GenPduR autosar.arxml
```

### 3. Kiểm chứng kết quả trong `CanIf_Cfg.c`:
Mảng `CanIfTxPduConfigData` được sinh ra tự động có thêm phần tử:
```c
{
    .CanIfTxPduId            = PDUR_ID2_TxBmsPackStatus,
    .CanIfCanTxPduIdCanId    = 0x250,
    .CanIfCanTxPduIdDlc      = 8,
    .CanIfTxPduIdCanIdType   = CANIF_CAN_ID_TYPE_11,
    .CanIfUserTxConfirmation = PduR_CanIfTxConfirmation,
    .CanIfCanTxPduHthRef     = &CanIfHthConfigData_CANIF_CHL_LS[0]
}
```

---

## 🔄 LỜI GIẢI TASK 3.10: Fault Confinement & Bus-Off Recovery CanSM State Machine

### 1. Quy tắc tăng/giảm bộ đếm lỗi TEC và REC:
- **Khi truyền bị lỗi (Transmitter Error):** TEC tăng $+8$. Khi truyền thành công: TEC giảm $-1$.
- **Khi nhận bị lỗi (Receiver Error):** REC tăng $+1$. Khi nhận thành công: REC giảm $-1$.
- **3 trạng thái lỗi:**
  - $\text{Error Active}$ ($\text{TEC, REC} \le 96$): Node hoạt động bình thường, phát Active Error Flag (6 bit Dominant liên tiếp).
  - $\text{Error Passive}$ ($96 < \text{TEC, REC} \le 255$): Node có dấu hiệu lỗi, chỉ được phát Passive Error Flag (6 bit Recessive), không làm ảnh hưởng đến bus.
  - $\text{Bus-Off}$ ($\text{TEC} > 255$): Node bị cách ly hoàn toàn khỏi đường bus để bảo vệ toàn mạng.

### 2. Chuỗi Callback Khi Xảy Ra Bus-Off:
```text
Hardware Interrupt (TEC > 255) 
    └──► Can_MainFunction_BusOff() 
            └──► CanIf_ControllerBusOff(ControllerId) 
                    └──► CanSM_ControllerBusOff(ControllerId)
```

### 3. Máy Trạng Thái Hồi Sinh Bus Của CanSM:
1. Khi nhận sự kiện Bus-Off, CanSM chuyển từ `CANSM_BSM_S_FULLCOM` sang `CANSM_BSM_S_BUS_OFF_CHECK`.
2. CanSM khởi động bộ định thời **BorTimeL1 (Fast Recovery = 50ms)**: Cho phép thử hồi phục nhanh trong trường hợp nhiễu nhất thời.
3. Khi hết hạn timer, CanSM gọi API MCAL:
   ```c
   Can_SetControllerMode(ControllerId, CAN_T_START);
   ```
4. Nếu bộ điều khiển vẫn tiếp tục bị Bus-Off liên tiếp quá số lần quy định (`BorCounterL1ToL2`), CanSM tự động chuyển sang chế độ phục hồi chậm **BorTimeL2 (Slow Recovery = 3000ms)** để chống lặp vô hạn gây nghẽn mạng toàn xe.

---

## 🏗️ LỜI GIẢI TASK 3.11: Kiến Trúc Sư Hệ Thống (System Architect) — Phân Bổ SWC Vào ECU Trong System ARXML & Điều Hướng RTE (Intra-ECU vs Inter-ECU)

> 🎯 **Mục tiêu:** Giải mã cơ chế cốt lõi của AUTOSAR: **Hành vi điều phối dữ liệu của RTE (truy cập RAM nội bộ vs bắn gói tin CAN qua ComStack) được quyết định hoàn toàn ở giai đoạn thiết kế toàn xe (Design-Time / VFB Level) thông qua file System ARXML.**

---

### 📄 PHẦN A: ĐỐI CHIẾU CẤU TRÚC SYSTEM ARXML TRONG 2 KỊCH BẢN

#### 1. Kịch Bản 1 (Intra-ECU Mapping: Cả 2 SWC cùng nằm trên `ECU_VCU`):
Trong file System ARXML, cả hai thành phần `SWC_Pedal` và `SWC_Motor` được gán vào cùng một thực thể `ECU-INSTANCE`:

```xml
<!-- System ARXML: Gán cả 2 SWC vào cùng 1 ECU VCU -->
<SWC-TO-ECU-MAPPING>
    <SHORT-NAME>SwcMapping_VCU_Intra</SHORT-NAME>
    <COMPONENT-IREFS>
        <COMPONENT-IREF>
            <CONTEXT-COMPOSITION-REF DEST="ROOT-SW-COMPOSITION-PROTOTYPE">/Vehicle/RootComposition</CONTEXT-COMPOSITION-REF>
            <TARGET-COMPONENT-REF DEST="SW-COMPONENT-PROTOTYPE">/Vehicle/RootComposition/SWC_Pedal_Prototype</TARGET-COMPONENT-REF>
        </COMPONENT-IREF>
        <COMPONENT-IREF>
            <CONTEXT-COMPOSITION-REF DEST="ROOT-SW-COMPOSITION-PROTOTYPE">/Vehicle/RootComposition</CONTEXT-COMPOSITION-REF>
            <TARGET-COMPONENT-REF DEST="SW-COMPONENT-PROTOTYPE">/Vehicle/RootComposition/SWC_Motor_Prototype</TARGET-COMPONENT-REF>
        </COMPONENT-IREF>
    </COMPONENT-IREFS>
    <ECU-INSTANCE-REF DEST="ECU-INSTANCE">/Vehicle/HardwareTopology/ECU_VCU</ECU-INSTANCE-REF>
</SWC-TO-ECU-MAPPING>
```

👉 **Lý do không cần `<DATA-MAPPING>`:** Vì cả hai Component Prototype cùng tham chiếu tới `ECU_VCU`, đường kết nối VFB (`ASSEMBLY-SW-CONNECTOR`) nằm hoàn toàn trong ranh giới bộ nhớ của 1 vi điều khiển. Toolchain nhận diện đây là liên kết nội bộ (Intra-ECU), do đó không cần ánh xạ sang bất kỳ `I-SIGNAL` hay mạng CAN nào!

---

#### 2. Kịch Bản 2 (Inter-ECU Mapping: `SWC_Pedal` ở `ECU_VCU`, `SWC_Motor` ở `ECU_Inverter`):
Khi kiến trúc sư tách `SWC_Motor` sang `ECU_Inverter`, file ARXML bắt buộc phải cấu hình thêm 3 khối định nghĩa:

```xml
<!-- 1. Phân bổ SWC vào 2 ECU khác nhau -->
<SWC-TO-ECU-MAPPING>
    <SHORT-NAME>SwcMapping_VCU</SHORT-NAME>
    <COMPONENT-IREFS>
        <COMPONENT-IREF>
            <TARGET-COMPONENT-REF DEST="SW-COMPONENT-PROTOTYPE">/Vehicle/RootComposition/SWC_Pedal_Prototype</TARGET-COMPONENT-REF>
        </COMPONENT-IREF>
    </COMPONENT-IREFS>
    <ECU-INSTANCE-REF DEST="ECU-INSTANCE">/Vehicle/HardwareTopology/ECU_VCU</ECU-INSTANCE-REF>
</SWC-TO-ECU-MAPPING>

<SWC-TO-ECU-MAPPING>
    <SHORT-NAME>SwcMapping_Inverter</SHORT-NAME>
    <COMPONENT-IREFS>
        <COMPONENT-IREF>
            <TARGET-COMPONENT-REF DEST="SW-COMPONENT-PROTOTYPE">/Vehicle/RootComposition/SWC_Motor_Prototype</TARGET-COMPONENT-REF>
        </COMPONENT-IREF>
    </COMPONENT-IREFS>
    <ECU-INSTANCE-REF DEST="ECU-INSTANCE">/Vehicle/HardwareTopology/ECU_Inverter</ECU-INSTANCE-REF>
</SWC-TO-ECU-MAPPING>

<!-- 2. DATA-MAPPING: Ánh xạ cổng VFB vào tín hiệu mạng CAN -->
<DATA-MAPPING>
    <SENDER-RECEIVER-TO-SIGNAL-MAPPING>
        <DATA-ELEMENT-IREF>
            <CONTEXT-PORT-REF DEST="P-PORT-PROTOTYPE">/Vehicle/RootComposition/SWC_Pedal_Prototype/PPort_PedalPosition</CONTEXT-PORT-REF>
            <TARGET-DATA-PROTOTYPE-REF DEST="VARIABLE-DATA-PROTOTYPE">PedalVal</TARGET-DATA-PROTOTYPE-REF>
        </DATA-ELEMENT-IREF>
        <SYSTEM-SIGNAL-REF DEST="SYSTEM-SIGNAL">/Vehicle/Communication/ISig_PedalPosition</SYSTEM-SIGNAL-REF>
    </SENDER-RECEIVER-TO-SIGNAL-MAPPING>
</DATA-MAPPING>

<!-- 3. Đóng gói I-SIGNAL vào CAN I-PDU (CAN ID: 0x180) -->
<I-SIGNAL-TO-I-PDU-MAPPING>
    <SHORT-NAME>ISigMapping_PedalPos</SHORT-NAME>
    <I-SIGNAL-REF DEST="I-SIGNAL">/Vehicle/Communication/ISig_PedalPosition</I-SIGNAL-REF>
    <PACKING-BYTE-ORDER>MOST-SIGNIFICANT-BYTE-FIRST</PACKING-BYTE-ORDER>
    <START-POSITION>0</START-POSITION>
    <I-PDU-REF DEST="I-SIGNAL-I-PDU">/Vehicle/Communication/TxPedalPdu_0x180</I-PDU-REF>
</I-SIGNAL-TO-I-PDU-MAPPING>
```

---

### 💻 PHẦN B: ĐỐI CHIẾU MÃ NGUỒN C SINH RA TRONG `Rte.c`

| Tiêu chí | Kịch bản 1: Intra-ECU (Chung Hộp VCU) | Kịch bản 2: Inter-ECU (VCU ──► CAN ──► Inverter) |
| :--- | :--- | :--- |
| **Bản chất kỹ thuật** | Giao tiếp qua biến tĩnh trên RAM vi điều khiển | Giao tiếp qua ngăn xếp BSW ComStack và mạng CAN |
| **Độ trễ truyền tải** | **$< 10\,\text{ns}$** (vài chu kỳ lệnh CPU đọc/ghi RAM) | **$1 - 10\,\text{ms}$** (độ trễ đóng gói Com + tranh chấp bus CAN) |
| **Mã C sinh ra tại Bên Gửi (`Rte_Write`)** | ```c<br>/* Rte.c trên VCU (Kịch bản 1) */<br>static uint16 Rte_Buffer_PedalVal = 0;<br><br>Std_ReturnType Rte_Write_PPort_PedalPosition_PedalVal(uint16 data)<br>{<br>    /* Ghi trực tiếp vào biến RAM */<br>    Rte_Buffer_PedalVal = data;<br>    return RTE_E_OK;<br>}<br>``` | ```c<br>/* Rte.c trên VCU (Kịch bản 2) */<br>#include "Com.h"<br><br>Std_ReturnType Rte_Write_PPort_PedalPosition_PedalVal(uint16 data)<br>{<br>    /* Tự động gọi ComStack để gửi CAN */<br>    return Com_SendSignal(COM_SID_ISig_PedalPosition, &data);<br>}<br>``` |
| **Mã C sinh ra tại Bên Nhận (`Rte_Read`)** | ```c<br>/* Rte.c trên VCU (Kịch bản 1) */<br>Std_ReturnType Rte_Read_RPort_PedalPosition_PedalVal(uint16* data)<br>{<br>    /* Đọc trực tiếp từ biến RAM */<br>    *data = Rte_Buffer_PedalVal;<br>    return RTE_E_OK;<br>}<br>``` | ```c<br>/* Rte.c trên Inverter (Kịch bản 2) */<br>#include "Com.h"<br><br>Std_ReturnType Rte_Read_RPort_PedalPosition_PedalVal(uint16* data)<br>{<br>    /* Đọc từ bộ đệm của ComStack */<br>    return Com_ReceiveSignal(COM_SID_ISig_PedalPosition, data);<br>}<br>``` |

👉 **Nhận xét cốt lõi:**  
RTE Generator (ví dụ [`GenRte.py`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/com/as.tool/config.infrastructure.system/argen/GenRte.py) trong dự án `as`) đọc file ARXML và tự động quyết định hàm C được sinh ra:
* Nếu phát hiện cùng ECU $\longrightarrow$ Sinh mã ghi RAM nội bộ.
* Nếu phát hiện khác ECU $\longrightarrow$ Tự động chèn lời gọi `Com_SendSignal()` / `Com_ReceiveSignal()`.

---

### 🧠 PHẦN C: THẨM ĐỊNH KIẾN TRÚC & CÂU HỎI PHỎNG VẤN CHUYÊN SÂU

#### 1. Chứng Minh Tính "Location Transparency" (Độc Lập Vị Trí Tuyệt Đối):
Xét mã nguồn C của `SWC_Pedal.c`:
```c
#include "Rte_Pedal.h"

void Pedal_Runnable(void)
{
    uint16 raw_pedal = Read_Pedal_Sensors();
    /* Gọi duy nhất hợp đồng RTE chuẩn hóa */
    Rte_Write_PPort_PedalPosition_PedalVal(raw_pedal);
}
```
* **Bằng chứng độc lập vị trí:** Dù hệ thống xe chuyển từ Kịch bản 1 (chung ECU) sang Kịch bản 2 (tách sang 2 ECU nối mạng CAN), file `SWC_Pedal.c` và `SWC_Motor.c` **giữ nguyên vẹn 100%, không cần sửa đổi dù chỉ 1 ký tự**! Toàn bộ sự biến đổi cơ chế từ RAM sang mạng CAN được giải quyết ngầm bên trong file sinh mã `Rte.c`.
* **Nếu không có AUTOSAR (Lập trình nhúng truyền thống):** Kỹ sư sẽ phải xóa bỏ câu lệnh gán biến `motor_cmd = pedal_val;`, thay bằng việc `#include "Can.h"` và viết lại hàm gọi ngoại vi `Can_Write(0x180, ...)`. Khi đó, mã nguồn thuật toán bị gắn chết vào phần cứng CAN, mất khả năng tái sử dụng.

#### 2. Cơ Chế Phát Hiện Mất Kết Nối Trên Mạng CAN Hướng Nội Dung (Content-Addressed):
* **Bản chất của CAN:** Mạng CAN truyền thông theo kiểu phát sóng (Broadcast), khung CAN `0x180` được bắn lên dây bus mà không quan tâm ai nhận. Vì vậy, hàm `Com_SendSignal()` trên VCU chỉ xác nhận việc nạp dữ liệu vào buffer gửi của BSW thành công, **hoàn toàn không thể biết được hộp Inverter còn sống hay đã bị mất nguồn**.
* **Giải pháp an toàn của AUTOSAR:**
  1. Trong cấu hình ARXML tại hộp nhận `ECU_Inverter`, kỹ sư cấu hình thuộc tính giám sát thời gian chết:
     `<TIMEOUT>0.1</TIMEOUT>` ($100\,\text{ms}$) kèm thuộc tính `<TIMEOUT-SUBSTITUTION-VALUE>0</TIMEOUT-SUBSTITUTION-VALUE>`.
  2. Module BSW `Com` trên Inverter khởi động bộ đếm lùi thời gian mỗi khi nhận được khung `0x180`.
  3. Nếu đứt dây CAN hoặc VCU mất nguồn khiến quá $100\,\text{ms}$ không có khung CAN đến:
     * Module `Com` kích hoạt cờ Timeout và trả về mã lỗi cho RTE.
     * Khi `SWC_Motor` gọi hàm `Rte_Read()`, hàm này trả về giá trị:
       ```c
       Std_ReturnType status = Rte_Read_RPort_PedalPosition_PedalVal(&pedal);
       if (status == RTE_E_TIMEOUT) {
           /* Ngắt mô-men xoắn khẩn cấp để đảm bảo an toàn Fail-Safe! */
           Emergency_Brake_SafeState();
       }
       ```
  4. 👉 Đây chính là cơ chế bảo vệ an toàn tối thượng theo tiêu chuẩn **ISO 26262 ASIL-D** trong hệ thống truyền động ô tô!
