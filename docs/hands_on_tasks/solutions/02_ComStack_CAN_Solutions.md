# LỜI GIẢI TOÀN DIỆN CHUYÊN ĐỀ 03 — COMMUNICATION STACK & CAN PROTOCOL
## Đáp Án Thực Hành Chi Tiết 6 Tầng: End-to-End CAN Trace, Bit Timing, CanIf, CanTp, COM & Bus Load

> 📚 **Tài liệu lý thuyết đối chiếu:** [`docs/theory/03_Communication_Stack_And_CAN_Protocol.md`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/docs/theory/03_Communication_Stack_And_CAN_Protocol.md)  
> 📑 **Ma trận gói tin & DBC:** [`docs/theory/10_CAN_DBC_Format_And_Tools.md`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/docs/theory/10_CAN_DBC_Format_And_Tools.md)  
> 🔧 **Mã nguồn gốc đối chiếu:** [`as/com/as.infrastructure/communication/`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/com/as.infrastructure/communication/)  
> 🎯 **File nhiệm vụ:** [`docs/hands_on_tasks/03_ComStack_CAN_Tasks.md`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/docs/hands_on_tasks/03_ComStack_CAN_Tasks.md)

---

<a id="task-13"></a>
## 📡 LỜI GIẢI TASK 1.3: Trace Dòng Chảy CAN Message 6 Tầng Toàn Diện Trong Mã Nguồn Gốc (Tx & Rx Path)
> 🎯 **Mục tiêu:** Trace 1 thông điệp CAN xuyên suốt 6 tầng kiến trúc AUTOSAR theo cả 2 chiều hoàn toàn dựa trên **mã nguồn gốc có sẵn của dự án `as` (100% Native Code Base & Exact Call Trees)**:
> 1. **Chiều Gửi (Tx Path):** Trace dòng chảy gói tin thời gian gốc **`TxMsgTime` (CAN ID: `0x101`)** qua toàn bộ ngăn xếp BSW COM và gói tin quản trị mạng gốc **`OSEK_NM_TX` (CAN ID: `0x401`)** từ Lõi BSW $\longrightarrow$ PduR $\longrightarrow$ CanIf $\longrightarrow$ MCAL Driver $\longrightarrow$ Dây Bus CAN vật lý.
> 2. **Chiều Nhận (Rx Path):** Trace dòng chảy gói tin tốc độ xe gốc **`RxMsgAbsInfo` (CAN ID: `0x102`)** từ Khung mạng vật lý MCAL $\longrightarrow$ CanIf $\longrightarrow$ PduR $\longrightarrow$ COM $\longrightarrow$ RTE $\longrightarrow$ Application SWC (`widget_refresh.c`).

---

### 📤 PHẦN A: CHIỀU GỬI GÓI TIN CAN GỐC (TX PATH: NATIVE BSW COM & NM $\longrightarrow$ HARDWARE)

> 💡 **Khởi tạo gói tin Tx gốc trong cấu hình dự án (`autosar.arxml`):**
> Gói tin CAN Tx gốc được định nghĩa trong `as/com/as.application/common/autosar.arxml` (Dòng 352) là **`TxMsgTime` (CAN ID: `0x101`, DLC: 8 bytes)** với thuộc tính `TxMode="PERIODIC"`, `TimePeriodFactor="100"` (chu kỳ 100ms) và dữ liệu khởi tạo `SystemTime` (`2013-12-15 19:49:00`, Unused byte `0x5A`).

#### 1. Chuỗi Gọi Hàm Function-Call-Function Chiều Gửi Chuẩn COM Stack (`TxMsgTime` 0x101):
```
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

#### 1.1 Chi Tiết Cơ Chế Chuyển Tiếp Từ Khởi Tạo Boot (`Com_IpduGroupStart`) Sang Chu Kỳ BSW (`ALARM(Alarm_BswService)`):

> ❓ **Câu hỏi kỹ nghệ chuyên sâu:**  
> *"Làm sao hệ thống chuyển tiếp từ lệnh khởi tạo `Com_IpduGroupStart(COM_DEFAULT_IPDU_GROUP, True)` trong Task Startup sang sự kiện ngắt chu kỳ `ALARM(Alarm_BswService)` để kích hoạt `TASK(SchM_BswService)`?"*

```
┌────────────────────────────────────────────────────────────────────────────────────────────────┐
│  🗺️ SƠ ĐỒ 4 GIAI ĐOẠN CHUYỂN TIẾP TỪ STARTUP BOOT SANG CHU KỲ BSW COM TX:                     │
└────────────────────────────────────────────────────────────────────────────────────────────────┘

 [ GIAI ĐOẠN 1: TASK(SchM_Startup) — KHỞI TẠO HỆ THỐNG ]
 1. SetRelAlarm(ALARM_ID_Alarm_BswService, 10, 10);  (SchM.c: L433 - Đăng ký Alarm chu kỳ 10ms)
 2. Com_IpduGroupStart(COM_DEFAULT_IPDU_GROUP, True); (SchM.c: L441 - Bật cờ Com_Arc_IpduStarted = 1)
 3. OsTerminateTask(SchM_Startup);                   (SchM.c: L485 - Kết thúc Task Startup)
         │
         ▼ (Nhường quyền điều khiển cho OSEK OS Scheduler)
 [ GIAI ĐOẠN 2: PHẦN CỨNG & OS TICK — BỘ ĐẾM THỜI GIAN PHẦN CỨNG ]
 4. Phần cứng ARM Cortex-M SysTick ngắt mỗi 1ms ──► Gọi SignalCounter(OsClock)
 5. Bộ đếm OsClock tăng dần: 1ms ──► 2ms ──► ... ──► 10ms (Đạt mốc Alarm hết hạn!)
         │
         ▼
 [ GIAI ĐOẠN 3: OSEK OS ALARM MANAGER — XỬ LÝ SỰ KIỆN HẾT HẠN ]
 6. OS Kernel phát hiện ALARM_ID_Alarm_BswService hết hạn:
    ──► Tự động gọi Callback: ALARM(Alarm_BswService) (SchM.c: L561)
    ──► Thực thi: OsActivateTask(SchM_BswService); (Chuyển Task sang trạng thái READY)
         │
         ▼
 [ GIAI ĐOẠN 4: OS SCHEDULER — CHUYỂN NGỮ CẢNH & THỰC THI CHU KỲ BSW ]
 7. OS Scheduler cấp phát CPU cho TASK(SchM_BswService) (SchM.c: L491)
    ──► Gọi SCHM_MAINFUNCTION_COMTX() (SchM.c: L522)
    ──► Gọi Com_MainFunctionTx() (Com_Sched.c: L98)
    ──► Kiểm tra Com_Arc_IpduStarted == 1 ──► Hết 100ms thì TỰ ĐỘNG BẮN CAN ID 0x101!
```

* **Ý nghĩa bản chất 3 thành phần cốt lõi:**
  1. **`Com_IpduGroupStart()` là CÔNG TẮC NGUỒN:** Bật cờ cho phép (`Com_Arc_IpduStarted = 1`) cho bộ đệm `TxMsgTime_IPduBuffer`, chưa gửi dữ liệu ngay.
  2. **`SetRelAlarm()` là ĐỒNG HỒ HẸN GIỜ:** Đặt lịch định thời cho ngắt phần cứng gọi `ALARM(Alarm_BswService)` mỗi 10ms.
  3. **`ALARM(Alarm_BswService)` là NGƯỜI GÕ CỬA:** Đánh thức `TASK(SchM_BswService)` chuyển sang trạng thái `READY` để thực thi các hàm BSW MainFunctions.

---

#### 2. Trích Dẫn Mã Nguồn Gốc Minh Chứng Chiều Gửi (`TxMsgTime` & `OSEK_NM_TX`):

* **Tầng 1 (Kích hoạt I-PDU Group & Periodic Task):** [`as/com/as.infrastructure/system/SchM/SchM.c: L441 & L522`](../../as/com/as.infrastructure/system/SchM/SchM.c#L441)
  ```c
  /* Khởi động I-PDU Group khi boot */
  Com_IpduGroupStart(COM_DEFAULT_IPDU_GROUP, True);

  /* Định kỳ trong Task SchM_BswService (10ms) */
  TASK(SchM_BswService) {
      ...
      SCHM_MAINFUNCTION_COMTX();  /* <── DÒNG 522: Gọi Com_MainFunctionTx() */
      ...
  }
  ```

* **Tầng 2 (Tầng COM đếm timer và gửi chu kỳ):** [`as/com/as.infrastructure/communication/Com/Com_Sched.c: L144`](../../as/com/as.infrastructure/communication/Com/Com_Sched.c#L144) & [`Com_Com.c: L236`](../../as/com/as.infrastructure/communication/Com/Com_Com.c#L236)
  ```c
  /* Com_Sched.c: L144 */
  if (Arc_IPdu->Com_Arc_TxIPduTimers.ComTxModeTimePeriodTimer == 0) {
      Com_Internal_TriggerIPduSend(i); /* <── Tự động gọi khi hết 100ms */
  }

  /* Com_Com.c: L236 */
  Std_ReturnType Com_Internal_TriggerIPduSend(PduIdType ComTxPduId) {
      ...
      /* DÒNG 236: CHUYỂN TIẾP XUỐNG TẦNG PDU ROUTER */
      if (PduR_ComTransmit(IPdu->ArcIPduOutgoingId, &PduInfoPackage) == E_OK) { ... }
  }
  ```

* **Tầng 3 (Tầng PduR Routing):** [`as/com/as.infrastructure/communication/PduR/PduR_Routing.c: L59`](../../as/com/as.infrastructure/communication/PduR/PduR_Routing.c#L59)
  ```c
  Std_ReturnType PduR_ComTransmit(PduIdType ComTxPduId, const PduInfoType *PduInfoPtr) {
      /* DÒNG 59: Chuyển tiếp sang CanIf */
      return CanIf_Transmit(destination->DestPduId, PduInfoPtr);
  }
  ```

* **Tầng 4 (CanIf Cfg & Code):** [`as/build/nt/lm3s6965evb/ascore/config/CanIf_Cfg.c: L168-L180`](../../as/build/nt/lm3s6965evb/ascore/config/CanIf_Cfg.c#L168-L180) & [`CanIf.c: L774-L785`](../../as/com/as.infrastructure/communication/CanIf/CanIf.c#L774)
  ```c
  /* Cấu hình trong CanIf_Cfg.c */
  {
      .CanIfTxPduId          = PDUR_ID2_TxMsgTime,
      .CanIfCanTxPduIdCanId  = 0x101,  /* <── CAN ID 0x101 */
      .CanIfCanTxPduIdDlc    = 8,
      .CanIfCanTxPduHthRef   = &CanIfHthConfigData_CANIF_CHL_LS[0],
  }

  /* CanIf.c: L785 */
  Std_ReturnType CanIf_Transmit(PduIdType CanTxPduId, const PduInfoType *PduInfoPtr) {
      ...
      return Can_Write(entry->CanIfHthRef->CanIfHthIdSymRef, &canPdu);
  }
  ```

* **Tầng 5 & 6 (MCAL Driver & Hardware Output):** [`as/com/as.infrastructure/arch/common/mcal/SCan.c: L83-L108`](../../as/com/as.infrastructure/arch/common/mcal/SCan.c#L83-L108)
  ```c
  Can_ReturnType Can_Write(Can_HwHandleType Hth, Can_PduType *pduInfo) {
      /* Định dạng khung SLCAN ASCII: t<ID><DLC><DATA...> */
      offset = sprintf(slcan_buf, "t%03X%d", (unsigned int)pduInfo->id, (int)pduInfo->length);
      for (int i = 0; i < pduInfo->length; i++) {
          offset += sprintf(&slcan_buf[offset], "%02X", pduInfo->sdu[i]);
      }
      sprintf(&slcan_buf[offset], "\r");
      Can_SendSLCAN(slcan_buf); /* Đẩy ra UART1 sang SavvyCAN */
  }
  ```

#### 📊 Bằng Chứng Dữ Liệu CAN Tx Thực Tế Thu Được Từ QEMU UART1 (100% Mã Nguồn Gốc):
```text
t101807DD0C0F1331005A   <── Gói COM TxMsgTime (CAN ID: 0x101, Data: 2013-12-15 19:49:00, 0x5A)
t40180101000000000000   <── Gói OSEK Network Management (CAN ID: 0x401, Node ID = 1, OpCode = 1)
t50280050FFFFFFFFFFFF   <── Gói AUTOSAR Network Management (CAN ID: 0x502, Source Node = 80)
```

---

### 📥 PHẦN B: CHIỀU NHẬN GÓI TIN CAN GỐC (RX PATH: HARDWARE $\longrightarrow$ APPLICATION CLUSTER)

#### 1. Chuỗi Gọi Hàm Function-Call-Function Chiều Nhận (Rx Call Graph Gốc):
```
1. [MCAL CAN DRIVER & HARDWARE]
   Frame CAN từ Bus đến (CAN ID: 0x102 - RxMsgAbsInfo, Data: 8 bytes)
   Can_MainFunction_Read() -> Lấy frame từ buffer phần cứng
   (as/com/as.infrastructure/arch/common/mcal/SCan.c: L158-L174)
        │
        └──► [DÒNG 171]: Gọi Callback CanIf_RxIndication(busid, CanId, dlc, data)
                │
                ▼
2. [CAN INTERFACE LAYER (CanIf)]
   CanIf_RxIndication() -> scheduleRxIndication()
   (as/com/as.infrastructure/communication/CanIf/CanIf.c: L350 & L1145)
        │
        ├── Kiểm tra Software Filter Mask (So khớp đúng ID 0x102)
        ├── Kiểm tra độ dài DLC (CanDlc >= 8 bytes)
        └── [DÒNG 403]: Match CANIF_USER_TYPE_CAN_PDUR -> Gọi Callback PduR_CanIfRxIndication()
                │
                ▼
3. [PDU ROUTER LAYER (PduR)]
   PduR_CanIfRxIndication() -> PduR_ARC_RouteTransmit()
   (as/com/as.infrastructure/communication/PduR/PduR_CanIf.c: L21 & PduR_Routing.c: L64)
        │
        └── Tra bảng định tuyến Routing Table -> Chuyển tiếp lên Com_RxIndication()
                │
                ▼
4. [COM LAYER (Interaction Layer)]
   Com_RxIndication() -> Com_RxProcessSignals()
   (as/com/as.infrastructure/communication/Com/Com_Com.c: L263-L290)
        │
        └── [DÒNG 290]: Tách I-PDU 8 bytes thành từng Signal riêng lẻ (VehicleSpeed, TachoSpeed, Led1Sts)
            và lưu giá trị mới vào bộ đệm Signal Buffer trong RAM
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
        └── Nhận giá trị speed từ CAN -> Tính góc quay kim đồng hồ hiển thị lên màn hình!
```

#### 2. Trích Dẫn Mã Nguồn Gốc Chiều Nhận (Rx Path):

* **Tầng 6 (MCAL Driver):** [`as/com/as.infrastructure/arch/common/mcal/SCan.c: L171`](../../as/com/as.infrastructure/arch/common/mcal/SCan.c#L171)
  ```c
  void Can_MainFunction_Read( void ) {
      Can_SerialInPduType pdu;
      if(RB_POP(canin, &pdu, sizeof(pdu)) > 0) {
          /* DÒNG 171: MCAL GỌI CALLBACK CanIf_RxIndication BÁO LÊN CANIF */
          CanIf_RxIndication(pdu.busid, SCANID(pdu.canid), pdu.dlc, pdu.data);
      }
  }
  ```

* **Tầng 5 (CanIf):** [`as/com/as.infrastructure/communication/CanIf/CanIf.c: L403`](../../as/com/as.infrastructure/communication/CanIf/CanIf.c#L403)
  ```c
  static void scheduleRxIndication(...) {
      if ((CanId & entry->CanIfCanRxPduCanIdMask) == entry->CanIfCanRxPduCanId) {
          switch (entry->CanIfRxUserType) {
          case CANIF_USER_TYPE_CAN_PDUR:
          {
              PduInfoType pduInfo = { .SduLength = CanDlc, .SduDataPtr = (uint8*)CanSduPtr };
              /* DÒNG 403: GỌI TIẾP CALLBACK LÊN TẦNG PDU ROUTER */
              PduR_CanIfRxIndication(entry->CanIfCanRxPduId, &pduInfo);
              return;
          }
          }
      }
  }
  ```

* **Tầng 4 (PduR):** [`as/com/as.infrastructure/communication/PduR/PduR_Routing.c: L64`](../../as/com/as.infrastructure/communication/PduR/PduR_Routing.c#L64)
  ```c
  void PduR_CanIfRxIndication(PduIdType CanRxPduId, const PduInfoType* PduInfoPtr) {
      /* Tra bảng định tuyến và chuyển tiếp lên module COM */
      Com_RxIndication(destination->DestPduId, PduInfoPtr);
  }
  ```

* **Tầng 3 (COM Module):** [`as/com/as.infrastructure/communication/Com/Com_Com.c: L263-L290`](../../as/com/as.infrastructure/communication/Com/Com_Com.c#L263-L290)
  ```c
  void Com_RxIndication(PduIdType ComRxPduId, const PduInfoType* PduInfoPtr) {
      const ComIPdu_type *IPdu = GET_IPdu(ComRxPduId);
      memcpy(IPdu->ComIPduDataPtr, PduInfoPtr->SduDataPtr, IPdu->ComIPduSize);
      /* DÒNG 290: Giải nén I-PDU thành từng tín hiệu Signal riêng biệt */
      Com_RxProcessSignals(IPdu, Arc_IPdu);
  }
  ```

* **Tầng 2 & 1 (RTE & Application SWC):** [`as/release/ascore/SgDesign/virtual_cluster/src/widget_refresh.c: L48`](../../as/release/ascore/SgDesign/virtual_cluster/src/widget_refresh.c#L48)
  ```c
  void* RefreshClusterSpeedPointer(SgWidget* w) {
      uint16 speed;
      Rte_Read_RPort_Speed_Speed(&speed);  /* Đọc tốc độ xe nhận từ CAN */
      w->d = CalculateGaugeDegree(speed);  /* Quay kim tốc độ trên màn hình táp-lô! */
      return 0;
  }
  ```

---

### 🔄 BẢNG ĐỐI CHIẾU ĐỐI XỨNG 2 CHIỀU TRONG MÃ NGUỒN GỐC:

| Tầng Kiến Trúc AUTOSAR | 📤 Chiều Gửi Gốc (`TxMsgTime` 0x101) | 📥 Chiều Nhận Gốc (`RxMsgAbsInfo` 0x102) |
| :--- | :--- | :--- |
| **1. Application / Service** | `SchM_Startup` (`Com_IpduGroupStart`) | `RefreshClusterSpeedPointer()` (Vẽ kim táp-lô) |
| **2. Scheduler / Task** | `SchM_BswService` $
ightarrow$ `Com_MainFunctionTx` | `TaskApp` $
ightarrow$ Virtual Cluster Task |
| **3. Interaction (COM)** | `Com_Internal_TriggerIPduSend` | `Com_RxIndication()` $
ightarrow$ `Com_RxProcessSignals` |
| **4. PDU Router (PduR)** | `PduR_ComTransmit()` | `PduR_CanIfRxIndication()` |
| **5. CAN Interface (CanIf)**| `CanIf_Transmit()` (Tra `0x101`) | `CanIf_RxIndication()` (Lọc `0x102`) |
| **6. MCAL Driver (SCan)** | `Can_Write()` $
ightarrow$ Bắn ra UART1 SLCAN | `Can_MainFunction_Read()` $
ightarrow$ Đọc Mailbox |

---

