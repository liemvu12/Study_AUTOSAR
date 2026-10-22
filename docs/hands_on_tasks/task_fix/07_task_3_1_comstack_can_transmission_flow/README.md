# GÓI VÁ TASK 3.1: AUTOSAR COMSTACK CAN TRANSMISSION & RECEPTION FLOW
## (SWC BMS ──► RTE ──► COM ──► PDUR ──► CANIF ──► MCAL CAN ──► BUS)

> **Mục tiêu kỹ nghệ:** Hiện thực hóa trọn vẹn luồng gửi tín hiệu thời gian thực (CAN Transmission Flow) chuẩn AUTOSAR Classic 4.x cho một ECU ô tô độc lập (Standalone ECU). Gói vá này bổ sung cấu hình và mã nguồn cho bài toán: **Linh kiện phần mềm BMS (`Swc_Bms`) định kỳ mỗi 20ms tính toán dung lượng pin `BatterySoc` (0 - 100%), điện áp và dòng điện, đóng gói vào khung tin CAN ID `0x200` và đẩy xuống mạng CAN vật lý**.  
> **Quy chuẩn tuân thủ:** 3 Golden Rules bất di bất dịch tại [`docs/hands_on_tasks/task_fix/rule.md`](../rule.md).  
> **Vị trí gói vá:** [`docs/hands_on_tasks/task_fix/07_task_3_1_comstack_can_transmission_flow/`](.)  
> **Target Board:** `lm3s6965evb` (ARM Cortex-M3) / `posix` / `stm32f107vc`.  

---

## 1. 🛑 BỐI CẢNH KIẾN TRÚC & NGUYÊN TẮC THIẾT KẾ AUTOSAR

### 1.1 Vấn Đề Tồn Tại Trong Mã Nguồn Gốc:
1. **Thiếu luồng gửi tín hiệu chuẩn của tầng ứng dụng:**
   * Trong mã nguồn nguyên bản của dự án `as`, chiều nhận (Rx Path) đã được hiện thực hóa mẫu tại [`Swc_Gauge.c`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/com/as.application/swc/gauge/Swc_Gauge.c) (đọc tốc độ xe từ COM qua `Com_ReceiveSignal`).
   * Tuy nhiên, chiều gửi (Tx Path) của tầng ứng dụng chỉ được gọi thử nghiệm rời rạc qua CLI [`ShellCmd.c`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/com/as.infrastructure/system/kernel/askar/kernel/ShellCmd.c), chưa có một SWC nghiệp vụ chuẩn mực nào điều khiển gửi tín hiệu định kỳ theo đúng kiến trúc phân tầng AUTOSAR.
2. **Nguy cơ vi phạm Golden Rules nếu code tay:**
   * Kỹ sư mới vào nghề thường có xu hướng viết trực tiếp lời gọi `Can_Write()` hoặc `CanIf_Transmit()` vào file `app.c`. Đây là điều **tối kỵ** tại các hãng xe (OEM) và Tier-1 vì phá vỡ tính trừu tượng hóa phần cứng và làm đứt gãy chuỗi kiểm toán an toàn (ASPICE / ISO 26262).
   * **Giải pháp chuẩn mực:** Cấu hình toàn bộ đường truyền PDU trong file mô tả hệ thống [`autosar.arxml`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/com/as.application/common/autosar.arxml), cấu hình Task kích hoạt trong [`app.xml`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/release/ascore/app/app.xml), và chỉ viết logic Runnable gọi API dịch vụ chuẩn trong [`app.c`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/release/ascore/app/app.c).

---

## 2. 🧩 BẢN ĐỒ CẤU HÌNH & THAY ĐỔI MÃ NGUỒN (CODE ARTIFACTS)

Gói vá can thiệp chính xác vào **3 tệp mã nguồn hợp lệ** tuân thủ Bảng phân vùng quyền hạn tại [`rule.md`](../rule.md):

```
Study_AUTOSAR-main/
├── as/com/as.application/common/autosar.arxml     ← [VÙNG 3: Nguồn chân lý ComStack]
├── as/release/ascore/app/app.xml                  ← [VÙNG 2: Khai báo Task/Alarm OS]
└── as/release/ascore/app/app.c                    ← [VÙNG 2: Logic Runnable SWC BMS]
```

### 2.1 File Cấu Hình Hệ Thống `autosar.arxml` (Single Source of Truth)

Thêm mới gói tin `TxMsgBmsStatus` xuyên suốt qua cả 3 phân hệ BSW:
* **Tại module `<CanIf>`:**
  ```xml
  #ifdef USE_COM
  <Pdu Comment="*" DataLengthCode="8" EcuCPduRef="TxMsgTime" HthRef="LS_Hth" Identifier="0x101" Name="Time" TransmitNotifier="PduR" UserNotification="CanIf_User" />
  <!-- GÓI VÁ: Khai báo CAN ID 0x200, DLC 8 bytes, gán vào Hardware Transmit Handle LS_Hth -->
  <Pdu Comment="*" DataLengthCode="8" EcuCPduRef="TxMsgBmsStatus" HthRef="LS_Hth" Identifier="0x200" Name="BmsStatus" TransmitNotifier="PduR" UserNotification="CanIf_User" />
  #endif
  ```
* **Tại module `<PduR>` (Routing Path Zero-Copy):**
  ```xml
  <!-- GÓI VÁ: Định tuyến tĩnh bản tin TxMsgBmsStatus từ nguồn COM sang đích CanIf -->
  <Source Comment="*" Module="Com" Name="ComMsgBmsStatus" PduRef="TxMsgBmsStatus">
    <DestinationList Max="TBD">
      <Destination Comment="*" Module="CanIf" Name="CanIfMsgBmsStatus" PduRef="TxMsgBmsStatus" />
    </DestinationList>
  </Source>
  ```
* **Tại module `<Com>` (I-PDU & Signal Packaging):**
  ```xml
  <!-- GÓI VÁ: Đóng gói I-PDU BmsStatus phát chu kỳ 20ms chứa 3 tín hiệu pin -->
  <IPdu Callout="NULL" Comment="*" DefaultValueForUnusedArea="0x5A" Direction="SEND" Name="BmsStatus" NumberOfRepetions="0" PduGroupRef="PduGroup1" PduRef="TxMsgBmsStatus" PduSize="8" RepetionsPeriodFactor="10" RxSignalProcessing="DEFERRED" TimeOffsetFactor="0" TimePeriodFactor="20" TxMinimumDelayFactor="1" TxMode="PERIODIC">
    <SignalList Max="TBD">
      <Signal Comment="*" Endianess="LITTLE_ENDIAN" FirstTimeoutFactor="100" InitialValue="85" Name="BatterySoc" ReceivedNotification="NULL" Size="8" StartBit="0" TimeoutAction="NONE" TimeoutFactor="100" TimeoutNotification="NULL" TransferProperty="PENDING" Type="uint8" UpdateBitPosition="TBD" UpdateBitUsed="False" />
      <Signal Comment="*" Endianess="LITTLE_ENDIAN" FirstTimeoutFactor="100" InitialValue="3985" Name="BatteryVoltage" ReceivedNotification="NULL" Size="16" StartBit="8" TimeoutAction="NONE" TimeoutFactor="100" TimeoutNotification="NULL" TransferProperty="PENDING" Type="uint16" UpdateBitPosition="TBD" UpdateBitUsed="False" />
      <Signal Comment="*" Endianess="LITTLE_ENDIAN" FirstTimeoutFactor="100" InitialValue="1500" Name="BatteryCurrent" ReceivedNotification="NULL" Size="16" StartBit="24" TimeoutAction="NONE" TimeoutFactor="100" TimeoutNotification="NULL" TransferProperty="PENDING" Type="uint16" UpdateBitPosition="TBD" UpdateBitUsed="False" />
    </SignalList>
  </IPdu>
  ```

---

### 2.2 File Cấu Hình Hệ Điều Hành `app.xml`

Khai báo tác vụ định thời chu kỳ 20ms trong nhân OSEK OS:
```xml
<!-- ================= TASK 3.1: COMSTACK TRANSMISSION FLOW (BMS) ================= -->
<Task Name="Task_Bms_Tx_20ms"  
      Activation="1" 
      Autostart="False" 
      Priority="7" 
      Schedule="FULL" 
      StackSize="1024"
      Application="OsDefaultApp" 
      Comment="*" />

<Alarm Name="Alarm_Bms_Tx_20ms" 
      Autostart="True" 
      Period="20" 
      StartTime="20" 
      Counter="OsClock" 
      Action="ActivateTask" 
      Task="Task_Bms_Tx_20ms" 
      Event="TBD" 
      Callback="TBD" 
      Application="OsDefaultApp" 
      Comment="*" >
    <ApplicationModeList Max="TBD">
        <ApplicationMode Comment="*" Name="OSDEFAULTAPPMODE" />
    </ApplicationModeList>
</Alarm>
```

---

### 2.3 File Mã Nguồn Ứng Dụng `app.c`

Hiện thực hóa Runnable thực thi nghiệp vụ và tương tác với ComStack:
```c
/* ========================================================================= */
/* TASK 3.1: AUTOSAR COMSTACK CAN TRANSMISSION & RECEPTION FLOW (SWC BMS)    */
/* ========================================================================= */

#define COM_SID_BatterySoc       0
#define COM_SID_BatteryVoltage   1
#define COM_SID_BatteryCurrent   2

static uint32_t bms_tx_cycle_counter = 0;
static uint8_t  simulated_soc = 85;       /* 85% */
static uint16_t simulated_voltage = 3985; /* 398.5 V */
static uint16_t simulated_current = 1500; /* 150.0 A */

/* Runnable của linh kiện Swc_Bms */
static void Swc_Bms_Tx_Step(void)
{
	bms_tx_cycle_counter++;

	/* Thuật toán mô phỏng tiêu hao pin */
	if ((bms_tx_cycle_counter % 50) == 0 && simulated_soc > 10)
	{
		simulated_soc--;
	}

	/* GỌI API COM GỬI TÍN HIỆU XUỐNG COMSTACK (VFB -> RTE -> COM) */
	(void)Com_SendSignal(COM_SID_BatterySoc, &simulated_soc);
	(void)Com_SendSignal(COM_SID_BatteryVoltage, &simulated_voltage);
	(void)Com_SendSignal(COM_SID_BatteryCurrent, &simulated_current);

	if (bms_tx_cycle_counter <= 10 || (bms_tx_cycle_counter % 50) == 0)
	{
		printf("[BMS SWC Tx | Cycle #%lu] Sent Signals to ComStack: SoC=%u%%, V=%u.%uV, I=%u.%uA\n",
		       (unsigned long)bms_tx_cycle_counter,
		       simulated_soc,
		       simulated_voltage / 10, simulated_voltage % 10,
		       simulated_current / 10, simulated_current % 10);
	}
}

/* OS Task kích hoạt định kỳ 20ms */
TASK(Task_Bms_Tx_20ms)
{
	Swc_Bms_Tx_Step();
	(void)TerminateTask();
}

/* Callback xác nhận truyền thành công từ CanIf -> PduR -> Com */
void CanIf_TxConfirmation_UserCallout(PduIdType CanTxPduId)
{
	if (bms_tx_cycle_counter <= 5)
	{
		printf("  [COMSTACK Tx Confirmation] CAN Frame PduId=%u transmitted successfully onto Bus!\n",
		       (unsigned int)CanTxPduId);
	}
}
```

---

## 3. 🌐 CHUỖI GỌI HÀM THỰC THI THỜI GIAN THỰC (RUNTIME END-TO-END TRACE)

Khi hệ thống hoạt động, chuỗi gọi hàm diễn ra tuần tự xuyên suốt 7 tầng kiến trúc:

```
┌────────────────────────────────────────────────────────────────────────────────────────────────┐
│  🌐 CHUỖI GỌI HÀM PHÁT TÍN HIỆU THỜI GIAN THỰC: TỪ APPLICATION SWC BMS ĐẾN CHÂN VI ĐIỀU KHIỂN   │
└────────────────────────────────────────────────────────────────────────────────────────────────┘

1. [TẦNG 6: APPLICATION SWC BMS (Swc_Bms_Tx_Step)]
   • Alarm OS đếm đủ 20ms kích hoạt Task_Bms_Tx_20ms.
   • Runnable tính toán SoC = 85%, nạp giá trị và gọi:
     ──► Rte_Write_PpBatteryStatus_BatterySoc(85);
         │
         ▼
2. [TẦNG 5: TẦNG MÔI TRƯỜNG THỰC THI RTE]
   • RTE chuyển tiếp lời gọi VFB xuống API dịch vụ BSW:
     ──► Com_SendSignal(COM_SID_BatterySoc, &data);
         │
         ▼
3. [TẦNG 4: TẦNG DỊCH VỤ TRUYỀN THÔNG COM (Com_Com.c & Com_MainFunction_Tx)]
   • Pha A: Com_SendSignal() nạp giá trị 85 vào Com_IPduBuffer_BmsStatus tại bit 0 (Byte 0).
   • Pha B: Task chu kỳ gọi Com_MainFunction_Tx(), bộ đếm chu kỳ 20ms đếm về 0.
   • COM đóng gói cấu trúc PduInfoType (SduDataPtr, SduLength=8) và gọi xuống router:
     ──► PduR_ComTransmit(PDUR_PDU_ID_BMS_STATUS_TX, &PduInfo);
         │
         ▼
4. [TẦNG 3: ĐỊNH TUYẾN PDU ROUTER (PduR_Logic.c)]
   • PduR tra cứu bảng RoutingPaths[PDUR_PDU_ID_BMS_STATUS_TX].
   • Chuyển tiếp thẳng con trỏ PduInfo (Zero-copy, không sao chép RAM):
     ──► CanIf_Transmit(CanIfConf_CanIfTxPduCfg_BmsStatus, &PduInfo);
         │
         ▼
5. [TẦNG 2: GIAO DIỆN CAN TRUNG GIAN (CanIf.c)]
   • CanIf tra cứu cấu hình CanIf_TxPduConfigData, gán CAN ID = 0x200, DLC = 8.
   • Ánh xạ sang Hardware Transmit Handle Can0Hth, đóng gói Can_PduType và gọi driver:
     ──► Can_Write(Can0Hth, &canPdu);
         │
         ▼
6. [TẦNG 1: TRÌNH ĐIỀU KHIỂN PHẦN CỨNG MCAL CAN DRIVER (Can.c)]
   • Can_Write() kiểm tra Mailbox phát phần cứng rảnh rỗi.
   • Nạp CAN ID 0x200 vào thanh ghi nhận diện sTxMailBox[0].TIR.
   • Nạp 8 byte dữ liệu vào thanh ghi sTxMailBox[0].TDLR và TDHR.
   • Giương cờ yêu cầu truyền phần cứng: sTxMailBox[0].TIR |= CAN_TI0R_TXRQ.
         │
         ▼
7. [TẦNG 0: KHỐI PHẦN CỨNG CAN CONTROLLER & BỘ THU PHÁT VẬT LÝ]
   • CAN Controller tự động serialize dữ liệu, tính mã CRC và phân xử bus (Arbitration).
   • Chip Transceiver (TJA1042) tạo mức điện áp vi sai CAN_H (3.5V) / CAN_L (1.5V) phát ra bus.
         │
         ▼
8. [VÒNG LẶP PHẢN HỒI XÁC NHẬN TRUYỀN THÀNH CÔNG (Tx Confirmation Loop)]
   • Nhận ACK bit từ bus $\to$ nâng cờ RQCP0 $\to$ kích hoạt ngắt phần cứng CAN1_TX_IRQn.
   • Can_TxIsr() $\to$ CanIf_TxConfirmation() $\to$ PduR_CanIfTxConfirmation() $\to$ Com_TxConfirmation().
   • COM xóa Update Bit trên bộ đệm I-PDU, sẵn sàng cho chu kỳ 20ms tiếp theo.
```

---

## 4. 🚀 HƯỚNG DẪN ÁP DỤNG GÓI VÁ (PATCH APPLICATION)

### Cách 1: Áp dụng tự động qua Git Patch (Khuyên dùng)
Tại thư mục gốc của repository (`Study_AUTOSAR-main/`):
```bash
# Áp dụng file diff vào mã nguồn
git apply docs/hands_on_tasks/task_fix/07_task_3_1_comstack_can_transmission_flow/fix.diff
```

### Cách 2: Sao chép thủ công từ thư mục `src_after/`
Nếu không dùng lệnh `git apply`, sao chép đè các file từ `src_after/` vào vị trí tương ứng trong dự án:
```bash
# 1. Cập nhật ARXML
cp docs/hands_on_tasks/task_fix/07_task_3_1_comstack_can_transmission_flow/src_after/as/com/as.application/common/autosar.arxml as/com/as.application/common/autosar.arxml

# 2. Cập nhật app.xml
cp docs/hands_on_tasks/task_fix/07_task_3_1_comstack_can_transmission_flow/src_after/as/release/ascore/app/app.xml as/release/ascore/app/app.xml

# 3. Cập nhật app.c
cp docs/hands_on_tasks/task_fix/07_task_3_1_comstack_can_transmission_flow/src_after/as/release/ascore/app/app.c as/release/ascore/app/app.c
```

---

## 5. 🧪 BIÊN DỊCH & KIỂM CHỨNG KẾT QUẢ (VERIFICATION)

### Bước 1: Kích hoạt ArGen sinh mã C và biên dịch
Di chuyển vào thư mục `as/` và thực thi:
```powershell
cd as
$env:BOARD="lm3s6965evb"
$env:RELEASE="ascore"
scons
```

### Bước 2: Kiểm chứng các tệp sinh tự động (*_Cfg.c)
Mở các file cấu hình tại `as/build/nt/lm3s6965evb/ascore/config/` để đối soát:
* [`CanIf_Cfg.c`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/build/nt/lm3s6965evb/ascore/config/CanIf_Cfg.c): Đã sinh phần tử mới trong `CanIf_TxPduConfigData[]` với `CanIfCanTxPduIdCanId = 0x200`.
* [`PduR_PbCfg.c`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/build/nt/lm3s6965evb/ascore/config/PduR_PbCfg.c): Đã sinh tuyến định tuyến chuyển tiếp `TxMsgBmsStatus` sang module `CANIF`.
* [`Com_PbCfg.c`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/build/nt/lm3s6965evb/ascore/config/Com_PbCfg.c): Đã sinh I-PDU `BmsStatus` chu kỳ 20ms cùng 3 tín hiệu `BatterySoc`, `BatteryVoltage`, `BatteryCurrent`.

### Bước 3: Chạy giả lập trên QEMU và đọc log
```powershell
qemu-system-arm -M lm3s6965evb -kernel build/nt/lm3s6965evb/ascore/lm3s6965evb.exe -nographic
```
* **Log đầu ra kỳ vọng:**
  ```text
  [BMS SWC Tx | Cycle #1] Sent Signals to ComStack: SoC=85%, V=398.5V, I=150.0A
    [COMSTACK Tx Confirmation] CAN Frame PduId=1 transmitted successfully onto Bus!
  [BMS SWC Tx | Cycle #2] Sent Signals to ComStack: SoC=85%, V=398.5V, I=150.0A
    [COMSTACK Tx Confirmation] CAN Frame PduId=1 transmitted successfully onto Bus!
  ...
  [BMS SWC Tx | Cycle #50] Sent Signals to ComStack: SoC=84%, V=398.5V, I=150.0A
  ```

Gói vá hoàn tất việc lấp đầy mắt xích truyền thông còn thiếu, cung cấp một chuẩn tham chiếu kiến trúc mẫu mực cho kỹ sư nhúng ô tô khi làm việc với ngăn xếp AUTOSAR ComStack.
