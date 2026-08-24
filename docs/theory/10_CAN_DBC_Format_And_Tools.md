# CAN DBC Format & Python Tools

## 1. DBC là gì và tại sao cần?

### Định nghĩa
DBC (viết tắt của **D**ata**B**ase cho **C**AN) là một định dạng file tiêu chuẩn công nghiệp được tạo ra bởi Vector Informatik (được biết đến như Vector CANdb++). File DBC lưu trữ tất cả các thông tin định nghĩa về mạng CAN của một hệ thống, bao gồm các Nodes (ECUs), Messages (khung truyền), và Signals (các tín hiệu vật lý bên trong Data payload).

### Tại sao cần DBC?
- **Thay thế Excel/Spreadsheet:** Trước đây kỹ sư thường dùng Excel để định nghĩa: byte 0 bit 1 là tín hiệu nhiệt độ... Rất dễ sai sót và khó tự động hóa.
- **Machine-readable:** File DBC là text thuần túy có cấu trúc chặt chẽ, các công cụ phần mềm (CANoe, CANalyzer) hoặc code (C code generator) có thể đọc (parse) trực tiếp để tự động sinh ra code encode/decode hoặc hiển thị lên đồ thị (graph) ở dạng vật lý.
- **Communication Contract:** Trong Automotive, OEM (Hãng xe) sẽ thiết kế toàn bộ mạng CAN của xe và gửi file DBC này cho các Tier-1 (Nhà cung cấp ECU). File DBC đóng vai trò là "Hợp đồng giao tiếp". ECU của bạn chỉ được phép phát/nhận đúng như những gì định nghĩa trong DBC.

---

## 2. DBC File Structure — Giải thích từng Section

DBC có cấu trúc theo dạng phân lớp (hierarchy) và sử dụng các từ khóa (keywords) để định nghĩa.
Một file DBC cơ bản có các phần chính sau:

```dbc
VERSION ""

NS_ :
    NS_DESC_
    CM_
    BA_DEF_
    BA_
    VAL_
    CAT_DEF_
    CAT_
    FILTER
    BA_DEF_DEF_
    EV_DATA_
    ENVVAR_DATA_
    SGTYPE_
    SGTYPE_VAL_
    BA_DEF_SGTYPE_
    BA_SGTYPE_
    SIG_TYPE_REF_
    VAL_TABLE_
    SIG_GROUP_
    SIG_VALTYPE_
    SIGTYPE_VALTYPE_
    BO_TX_BU_
    BA_DEF_REL_
    BA_REL_
    BA_DEF_DEF_REL_
    BU_SG_REL_
    BU_EV_REL_
    BU_BO_REL_
    SG_MUL_VAL_

BS_:

BU_: BMS VCU BCM

BO_ 384 BMS_Status: 8 BMS
 SG_ SoC : 0|8@1+ (0.5,0) [0|100] "%" VCU,BCM
 SG_ PackVoltage : 8|16@1+ (0.1,0) [0|5000] "V" VCU
 SG_ PackCurrent : 24|16@1- (0.1,0) [-3000|3000] "A" VCU
 SG_ FaultFlags : 40|8@1+ (1,0) [0|255] "" VCU,BCM
```

### Giải thích từng Field chi tiết
- `VERSION ""`: Phiên bản của file DBC (thường rỗng).
- `NS_`: Namespace declarations, định nghĩa các keywords hợp lệ phía sau.
- `BS_`: Bit timing (Tốc độ baudrate). Thường bị bỏ qua hoặc để trống vì thực tế baudrate cấu hình ở HW/Stack.
- `BU_` (Nodes): Danh sách các ECUs tham gia vào mạng. VD: `BMS VCU BCM`.
- `BO_` (Message Definition):
  - `BO_ 384 BMS_Status: 8 BMS`
  - `384` = CAN ID hệ cơ số 10 (Decimal). 384 đổi sang Hex là `0x180`.
  - `BMS_Status` = Tên của bản tin.
  - `8` = DLC (Data Length Code) - Chiều dài payload là 8 Bytes.
  - `BMS` = Transmitter (Node gửi bản tin này).
- `SG_` (Signal Definition):
  - Định dạng chung: `SG_ Name : startBit|length@byteOrder(factor,offset) [min|max] "unit" Receivers`
  - VD: `SG_ SoC : 0|8@1+ (0.5,0) [0|100] "%" VCU,BCM`
  - `SoC`: Tên tín hiệu (State of Charge).
  - `0|8`: `0` là Start bit (Bit bắt đầu), `8` là chiều dài (Length = 8 bits).
  - `@1+`:
    - Số đầu tiên: Byte Order. `1` = Intel (Little Endian), `0` = Motorola (Big Endian).
    - Dấu: `+` = Unsigned (Không dấu), `-` = Signed (Có dấu - Two's complement).
  - `(0.5,0)`: Resolution/Factor = `0.5`, Offset = `0`.
  - `[0|100]`: Giá trị vật lý tối thiểu (Min) = 0, Tối đa (Max) = 100.
  - `"%"`: Đơn vị (Unit).
  - `VCU,BCM`: Danh sách các Node nhận (Receivers) tín hiệu này.

---

## 3. Signal Encoding/Decoding (Intel vs Motorola)

Đây là phần lõi của kỹ thuật CAN giao tiếp. Trên đường truyền CAN, dữ liệu chỉ là các Byte Hex (Raw Value). Ta phải biến đổi Raw Value thành Physical Value (giá trị thực tế có ý nghĩa như V, A, km/h).

### Công thức:
**`Physical_Value = (Raw_Value * Factor) + Offset`**

- **Ví dụ Decoding (Nhận):** 
  - Tín hiệu SoC (Factor=0.5, Offset=0). Byte trên mạng CAN nhận được là `0xC8` (Dec: 200).
  - Physical SoC = 200 * 0.5 + 0 = 100 (%).
- **Ví dụ Encoding (Gửi):** 
  - Muốn gửi PackVoltage = 400.5V. (Factor=0.1, Offset=0).
  - `Raw_Value = (Physical_Value - Offset) / Factor` = (400.5 - 0) / 0.1 = 4005 (Dec) = `0x0FA5` (Hex).

### Byte Order (Intel vs Motorola)
- **Intel (Little Endian - `@1`):** Start bit được đếm từ LSB (Least Significant Bit) của tín hiệu. Dữ liệu mọc từ bit thấp lên bit cao theo thứ tự byte xuôi. Phổ biến nhất.
- **Motorola (Big Endian - `@0`):** Start bit được định nghĩa là MSB (Most Significant Bit) của tín hiệu. Dữ liệu chạy ngược từ bit cao xuống thấp, vắt ngang qua các byte theo chiều ngược. Gây nhầm lẫn rất cao khi tính toán bitmask.

### Signed Value (Số âm)
Nếu tín hiệu định nghĩa là có dấu `@1-` (ví dụ Dòng điện xả/sạc `PackCurrent`), Raw Value sử dụng biểu diễn bù hai (Two's complement).
VD: Length = 16 bits. Dải Raw: 0 đến 65535.
- Từ 0 đến 32767: Số dương.
- Từ 32768 đến 65535: Số âm (Thực tế là từ -32768 đến -1).

---

## 4. Other DBC Keywords (Thuộc tính nâng cao)

Ngoài định nghĩa Msg/Signal, DBC cho phép gắn metadata:

```dbc
CM_ SG_ 384 SoC "State of Charge of Battery Pack in percent"; -- Comment cho Signal SoC trong msg 384

BA_DEF_ SG_ "SystemSignalLongSymbol" STRING; -- Định nghĩa một thuộc tính (Attribute) dạng String
BA_ "BusType" "CAN"; -- Set thuộc tính toàn cục mạng là "CAN"
BA_ "GenMsgCycleTime" BO_ 384 100; -- Set thuộc tính Cycle Time cho Msg 384 là 100ms

VAL_ 384 FaultFlags 0 "No_Fault" 1 "Over_Voltage" 2 "Over_Temp" 3 "Under_Voltage"; -- Định nghĩa Enumeration cho Signal. Lúc hiển thị CANoe sẽ hiện chữ thay vì số.
```

---

## 5. Python `cantools` — Parse DBC mạnh mẽ nhất

Thư viện `cantools` là công cụ chuẩn mực trong Python để thao tác với file DBC: đọc, hiển thị, mã hóa và giải mã dữ liệu mạng.

```python
import cantools

# 1. Load DBC file
db = cantools.database.load_file('BMS_System.dbc')

# 2. List all messages
for msg in db.messages:
    print(f'Message: {msg.name}, ID: 0x{msg.frame_id:03X}, DLC: {msg.length}')
    for sig in msg.signals:
        endian = 'Intel' if sig.byte_order == 'little_endian' else 'Motorola'
        sign = 'Signed' if sig.is_signed else 'Unsigned'
        print(f'  Signal: {sig.name}, Start: {sig.start}, Length: {sig.length}, {endian}, {sign}')

# 3. Decode received frame (Nhận data từ CAN bus và giải mã)
msg = db.get_message_by_name('BMS_Status') # Tương ứng ID 0x180
# Giả sử Payload CAN nhận được:
raw_data = bytes([0xC8, 0xA5, 0x0F, 0x9C, 0xFF, 0x01, 0x00, 0x00])
decoded = msg.decode(raw_data)
print("Decoded Data:", decoded)  
# Output: {'SoC': 100.0, 'PackVoltage': 400.5, 'PackCurrent': -10.0, 'FaultFlags': 'Over_Voltage'}

# 4. Encode frame to send (Đóng gói Physical value thành Raw bytes để gửi)
data_to_send = {
    'SoC': 80.0,
    'PackVoltage': 350.0,
    'PackCurrent': 50.0,
    'FaultFlags': 0  # No_Fault
}
frame_bytes = msg.encode(data_to_send)
print("Encoded Bytes:", frame_bytes.hex())
```

---

## 6. `python-can` — Send/Receive trên Bus thực/ảo

Trong khi `cantools` dùng để dịch data, `python-can` dùng để tương tác trực tiếp với Driver phần cứng (Vector, PCAN, SocketCAN trên Linux).

```python
import can
import cantools

db = cantools.database.load_file('BMS_System.dbc')

# Kết nối vào Virtual CAN trên Linux (vcan0) hoặc phần cứng thực
# bustype='vector' cho card Vector, 'pcan' cho Peak, 'socketcan' cho Linux.
bus = can.interface.Bus(channel='vcan0', bustype='socketcan')

# --- RECEIVE LOOP ---
print("Waiting for messages...")
try:
    for msg in bus:
        print(f'Received ID: 0x{msg.arbitration_id:03X}, Data: {msg.data.hex()}')
        
        # Chỉ decode nếu ID có trong DBC
        try:
            decoded = db.decode_message(msg.arbitration_id, msg.data)
            print(f"  Decoded: {decoded}")
        except KeyError:
            print("  Unknown message ID")
            
except KeyboardInterrupt:
    print("Stopped.")

# --- SEND MESSAGE ---
bms_msg = db.get_message_by_name('BMS_Status')
data = bms_msg.encode({'SoC': 50, 'PackVoltage': 380.0, 'PackCurrent': 10.0, 'FaultFlags': 0})

can_msg = can.Message(
    arbitration_id=bms_msg.frame_id, 
    data=data, 
    is_extended_id=False # CAN 2.0A (11-bit ID)
)
bus.send(can_msg)
print(f"Message sent on {bus.channel_info}")
```

---

## 7. DBC vs ARXML

Trong Automotive hiện đại, chuẩn AUTOSAR sử dụng định dạng ARXML thay cho DBC.

| Tiêu chí | DBC (Vector CANdb) | ARXML (AUTOSAR XML) |
|----------|-------------------|---------------------|
| **Định dạng** | Text base thuần túy, cấu trúc keyword-based | XML Schema chặt chẽ, lồng nhau rất sâu |
| **Độ phổ biến** | Rất phổ biến, mọi tool nhỏ đều đọc được | Tiêu chuẩn bắt buộc cho dự án AUTOSAR |
| **Phạm vi** | Chỉ chứa thông tin mạng CAN/LIN | Chứa MỌI THỨ: CAN, LIN, Ethernet, Software Components, RTE, Topology |
| **Dung lượng** | Rất nhỏ (vài chục KB) | Rất lớn (hàng chục đến hàng trăm MB) |
| **Công cụ chỉnh sửa**| CANdb++, Notepad++ | Phải dùng DaVinci Configurator / EB Tresos |
| **Độ phức tạp** | Đơn giản, dễ đọc bằng mắt người | Cực kỳ phức tạp, không thể đọc bằng mắt thường |

**Workflow convert:** 
Trong nhiều dự án, OEM vẫn gửi DBC cho Tier-1 do dễ thảo luận. Tier-1 sẽ dùng tool (như Vector CANoe hoặc DaVinci) import DBC vào, tool sẽ tự động convert sang định nghĩa ARXML trong dự án.

---

## 8. Tạo mock DBC file cho BMS-VCU system

Dưới đây là nội dung mẫu lưu vào file `BMS_System.dbc` cho một hệ thống 2 node: BMS (Battery) và VCU (Vehicle Control Unit).

```dbc
VERSION ""

NS_ :
    BA_
    BA_DEF_
    VAL_

BS_:

BU_: BMS VCU

BO_ 256 VCU_Command: 8 VCU
 SG_ Target_Power : 0|16@1+ (1,0) [0|100000] "W" BMS
 SG_ WakeUp_Sleep_Cmd : 16|2@1+ (1,0) [0|3] "" BMS

BO_ 512 BMS_State1: 8 BMS
 SG_ SoC : 0|8@1+ (0.5,0) [0|100] "%" VCU
 SG_ SoH : 8|8@1+ (0.5,0) [0|100] "%" VCU
 SG_ Pack_Voltage : 16|16@1+ (0.1,0) [0|800] "V" VCU
 SG_ Pack_Current : 32|16@1- (0.1,0) [-1000|1000] "A" VCU
 SG_ Max_Temp : 48|8@1+ (1,-40) [-40|150] "C" VCU

BO_ 513 BMS_State2: 8 BMS
 SG_ Contactor_State : 0|2@1+ (1,0) [0|3] "" VCU
 SG_ Charge_Limit : 8|16@1+ (1,0) [0|500] "kW" VCU
 SG_ Discharge_Limit : 24|16@1+ (1,0) [0|500] "kW" VCU
 SG_ BMS_Fault_Code : 40|8@1+ (1,0) [0|255] "" VCU

CM_ BO_ 256 "Command from VCU to BMS";
CM_ SG_ 512 Max_Temp "Maximum temperature across all battery cells";

BA_DEF_ BO_ "GenMsgCycleTime" INT 0 65535;
BA_ "GenMsgCycleTime" BO_ 512 100;
BA_ "GenMsgCycleTime" BO_ 513 100;
BA_ "GenMsgCycleTime" BO_ 256 50;

VAL_ 256 WakeUp_Sleep_Cmd 0 "No_Cmd" 1 "Wake_Up" 2 "Sleep_Request" 3 "Reserved";
VAL_ 513 Contactor_State 0 "Open" 1 "Precharge" 2 "Closed" 3 "Error";
```

---

## 9. Interview Q&A — 15 câu hỏi về CAN & DBC

1. **Câu 1: Mục đích chính của file DBC là gì?**
   *Đáp:* Lưu trữ định nghĩa giao thức CAN (Nodes, Msg, Signals, Scaling factor) để các thiết bị và phần mềm có thể tự động hiểu cách encode/decode raw bytes thành giá trị vật lý.
2. **Câu 2: Offset và Factor trong DBC dùng để làm gì?**
   *Đáp:* Dùng để quy đổi dữ liệu: `Physical = Raw * Factor + Offset`. Nó giúp truyền các giá trị thập phân (như 12.5V) bằng số nguyên (Raw=125, Factor=0.1) trên mạng CAN để tiết kiệm băng thông.
3. **Câu 3: Giải thích Byte Order: Intel và Motorola?**
   *Đáp:* Intel (Little Endian): Byte thấp gửi trước, bit ghép từ thấp lên cao. Motorola (Big Endian): Byte cao gửi trước, hướng ghép bit ngược lại. Rất quan trọng khi cấu hình signal vắt qua nhiều byte.
4. **Câu 4: Ký hiệu `@1+` và `@0-` trong cấu trúc SG_ nghĩa là gì?**
   *Đáp:* `@1+`: Intel, Unsigned. `@0-`: Motorola, Signed (Có dấu).
5. **Câu 5: Nếu độ phân giải (Factor) là 0.1, giá trị Min là 0, Max là 25, ta cần bao nhiêu bit để truyền tín hiệu này?**
   *Đáp:* Max physical = 25 -> Max raw = (25-0)/0.1 = 250. Số 250 nhỏ hơn 255 (2^8 - 1), nên cần 8 bits (1 byte).
6. **Câu 6: Sự khác nhau giữa thư viện `python-can` và `cantools`?**
   *Đáp:* `python-can` xử lý ở tầng Data Link Layer (gửi/nhận raw CAN frame với hardware/virtual bus). `cantools` xử lý ở tầng Application (Parse DBC, encode/decode payload bytes thành Dictionary các giá trị vật lý).
7. **Câu 7: DBC có chứa định nghĩa cấu trúc dữ liệu của chẩn đoán (UDS/OBD) không?**
   *Đáp:* Thường là không. UDS/OBD sử dụng giao thức gửi nhận payload linh hoạt, nhiều frames (Transport Protocol). DBC chỉ định nghĩa 2 Msg ID cho Diagnostic (VD: ID `0x7E0` Tx, `0x7E8` Rx) với data là mảng 8 bytes thô (Payload), còn chi tiết bên trong do file định nghĩa chẩn đoán (ODX/CDD) quản lý.
8. **Câu 8: Một Msg CAN chuẩn 2.0A chứa tối đa bao nhiêu signals?**
   *Đáp:* DLC tối đa là 8 bytes = 64 bits. Số lượng signal phụ thuộc vào chiều dài của từng signal, nhưng tổng chiều dài không được vượt quá 64 bits. VD: Chứa được 64 signals 1-bit, hoặc 4 signals 16-bits.
9. **Câu 9: `VAL_` trong DBC có chức năng gì?**
   *Đáp:* Khai báo Enumeration (Bảng giá trị ánh xạ). Giúp biến các con số khô khan thành string có nghĩa (VD: 0=Off, 1=On) trên các phần mềm như CANoe.
10. **Câu 10: Node (BU_) trong mạng CAN được hiểu thế nào trong file DBC?**
    *Đáp:* Node đại diện cho một ECU vật lý. Mỗi bản tin (Msg) sẽ do 1 Node phát (Transmitter) và tín hiệu (Signal) trong đó sẽ có 1 hoặc nhiều Node nhận (Receivers).
11. **Câu 11: Làm sao để định nghĩa tín hiệu nhiệt độ từ -40 đến 150 độ C với độ phân giải 1 độ C?**
    *Đáp:* Offset = -40, Factor = 1. Raw_value = Physical - Offset = Physical - (-40) = Physical + 40. Dải Raw sẽ chạy từ 0 đến 190. Ta cần 8 bits. Định nghĩa: `SG_ Temp: 0|8@1+ (1,-40) [-40|150] "C"`.
12. **Câu 12: Mạng CAN FD có dùng file DBC được không?**
    *Đáp:* Có. DBC hỗ trợ DLC lớn hơn (lên tới 64 bytes) cho CAN FD, mặc dù định dạng ARXML hiện nay được ưu tiên hơn cho mạng hiện đại.
13. **Câu 13: Khi một node nhận được bản tin không có định nghĩa trong DBC, nó sẽ xử lý thế nào?**
    *Đáp:* Phần mềm BSW/CAN driver của node sẽ filter ở hardware hoặc ở mức Basic Software, bản tin đó sẽ bị loại bỏ (Dropped) mà không đi lên tầng Application (RTE).
14. **Câu 14: ARXML và DBC, định dạng nào bảo mật hơn?**
    *Đáp:* Cả hai đều là plain text, không có mã hóa bản thân định dạng. Bảo mật (SecOC, mã hóa payload) nằm ở tầng phần mềm thực thi, không nằm ở bản thân file DBC/ARXML. Tuy nhiên ARXML chứa full architecture nên nếu lộ sẽ rủi ro lộ IP cao hơn.
15. **Câu 15: Bạn có gặp lỗi khi Decode file DBC bằng Python không và nguyên nhân thường là gì?**
    *Đáp:* Có. Thường là do Key Error (Msg ID nhận được không có trong database), hoặc lỗi do tín hiệu Multiplexing (tín hiệu lồng nhau - MUX), hoặc do file DBC chưa cập nhật đúng phiên bản với firmware đang chạy trên ECU.
