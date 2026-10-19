# GÓI VÁ: CHUYỂN ĐỔI BOARD STM32F107VC VỀ KIẾN TRÚC AUTOSAR MCAL CHUẨN MỰC
## (CHUẨN HÓA DRIVER bxCAN THUẦN TÚY ──► TISR_PC VECTOR ──► CAN_1_RXISR / CAN_1_TXISR ──► CANIF)

> 📅 **Ngày thực hiện:** 15/10/2026  
> 🏷️ **Loại tài liệu:** Task Fix / Architecture Standardization & MCAL Migration  
> 📌 **File Diff tương ứng:** [`fix.diff`](fix.diff)  
> 🎯 **Tuân thủ quy tắc:** [`docs/hands_on_tasks/task_fix/rule.md`](../rule.md) (Rule 3 & Rule 4 - Vùng 3 Board Integration & Standard Architecture First).  
> 🎯 **Target Board:** `stm32f107vc` (ARM Cortex-M3 Physical Silicon / bxCAN).  

---

## 1. 🛑 BỐI CẢNH KIẾN TRÚC & NGUYÊN NHÂN GỐC RỄ (ROOT CAUSE ANALYSIS)

### 1.1 Hiện Tượng Trong Mã Nguồn Gốc:
Trong cấu hình gốc của repository, khi sinh mã cấu hình cho Target `BOARD="stm32f107vc"` (`RELEASE="ascore"`), bảng vector ngắt phần cứng của hệ điều hành `tisr_pc` trong tệp cấu hình sinh ra [as/build/nt/stm32f107vc/ascore/config/Os_Cfg.c](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/build/nt/stm32f107vc/ascore/config/Os_Cfg.c) ghi nhận:
```c
ISR_ADDR(CAN1_TX_IRQHandler),  /* 19 */
ISR_ADDR(CAN1_RX0_IRQHandler), /* 20 */
ISR_ADDR(CAN1_SCE_IRQHandler), /* 22 */
```
Khi truy vết mã nguồn, các hàm ngắt trên không thuộc tầng MCAL AUTOSAR mà dẫn chiếu trực tiếp vào thư viện STM32CubeMX HAL (`as/release/download/stm32f107vc/Src/stm32f1xx_it.c`) và gọi `HAL_CAN_IRQHandler()`, sau đó chuyển tiếp frame qua cổng USB CDC lên máy tính PC (`usbd_cdc_if.c`).

### 1.2 Phân Tích Nguyên Nhân Gốc Rễ (Root Cause):
1. **Mục đích thiết kế riêng của tác giả repo (`as` - Parai Wang):**
   * Board STM32F107VC nguyên bản được tác giả cấu hình với mục đích làm **Thiết bị phần cứng USB-CAN Adapter Dongle / Gateway** (kết nối USB sang CAN cho PC qua thư viện `aspy`).
   * Do đó, trong tệp cấu hình bo mạch [as/com/as.application/board.stm32f107vc/SConscript](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/com/as.application/board.stm32f107vc/SConscript), danh sách `MODULES` mặc định chứa:
     ```python
     MODULES = [
         ...,
         'SCAN',       # Virtual Soft-CAN
         ...,
         'USB', 'USB_CAN' # Kéo theo gói STM32CubeMX HAL download
     ]
     ```
2. **Hậu quả kiến trúc:**
   * Cấu hình này làm đứt gãy luồng xử lý chuẩn mực của AUTOSAR Classic, khiến vi điều khiển không sử dụng driver MCAL tiêu chuẩn ([arch/stm32f1/mcal/Can.c](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/com/as.infrastructure/arch/stm32f1/mcal/Can.c)), không gọi hàm ngắt chuẩn `Can_1_RxIsr()`, và không dispatch trực tiếp lên `CanIf_RxIndication()`.
   * Người học khi đối chiếu giữa giáo trình lý thuyết AUTOSAR Classic và code thật trên đĩa bị hoang mang và hiểu nhầm là "giáo án một đằng, thực tế một nẻo".

---

## 2. 🧩 BẢN ĐỒ CẤU HÌNH & THAY ĐỔI MÃ NGUỒN (CODE ARTIFACTS)

Gói vá can thiệp chính xác vào **VÙNG 3: Board Integration (`as/com/as.application/board.stm32f107vc/`)** tuân thủ Bảng phân định vùng mã nguồn tại [`rule.md`](../rule.md):

```
docs/hands_on_tasks/task_fix/08_fix_stm32f107_pure_autosar_mcal_migration/
├── README.md                                                   ← [Tài liệu kỹ thuật & Báo cáo xác thực]
├── fix.diff                                                    ← [Bản vá thống nhất Unified Patch]
├── src_before/                                                 ← [Mã nguồn gốc trước khi vá]
│   └── as/com/as.application/board.stm32f107vc/SConscript
└── src_after/                                                  ← [Mã nguồn chuẩn sau khi vá]
    └── as/com/as.application/board.stm32f107vc/SConscript
```

### Chi Tiết Di Chuyển Cấu Hình (Migration Details):
1. **Thay thế Module:**
   * Thay `'SCAN'` bằng `'CAN'`: Kích hoạt driver MCAL thuần túy [arch/stm32f1/mcal/Can.c](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/com/as.infrastructure/arch/stm32f1/mcal/Can.c) và cấu hình [common/Can_Lcfg.c](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/com/as.application/board.stm32f107vc/common/Can_Lcfg.c).
   * Loại bỏ `'USB'` và `'USB_CAN'`: Cắt đứt hoàn toàn sự phụ thuộc vào gói STM32CubeMX HAL (`Src/stm32f1xx_it.c`, `Src/can1_isr.xml`).
2. **Kích hoạt bảng Vector ngắt AUTOSAR chuẩn:**
   * Khi `'CAN'` có mặt trong `MODULES`, SConscript tự động kích hoạt tệp cấu hình ngắt chuẩn có sẵn [common/isr_can.xml](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/com/as.application/board.stm32f107vc/common/isr_can.xml):
     ```xml
     <Os>
         <ISR Name='Can_1_TxIsr' Vector='19'  Application="OsDefaultApp"/>
         <ISR Name='Can_1_RxIsr' Vector='20'  Application="OsDefaultApp"/>
         <ISR Name='Can_1_ErrIsr' Vector='22'  Application="OsDefaultApp"/>
     </Os>
     ```
3. **Loại bỏ các thành phần không cần thiết cho ECU:**
   * Loại bỏ `SDCARD`, `FATFS`, `VFS`, `DEV` để hệ thống tập trung hoàn toàn vào ComStack & MCAL CAN.

---

## 3. 🛠️ NỘI DUNG PATCH CHI TIẾT (SOURCE CODE DIFF)

Trích dẫn từ [`fix.diff`](fix.diff):

```diff
diff --git a/com/as.application/board.stm32f107vc/SConscript b/com/as.application/board.stm32f107vc/SConscript
index 8d50b8e..aa45c7b 100644
--- a/com/as.application/board.stm32f107vc/SConscript
+++ b/com/as.application/board.stm32f107vc/SConscript
@@ -9,12 +9,12 @@ BDIR = asenv['BDIR']
 
 MODULES = ['ECUM','SCHM','MCU',
            'DET','SHELL',
-           'SCAN','CANIF','PDUR','COM','COMM','CANTP','J1939TP',
+           'CAN','CANIF','PDUR','COM','COMM','CANTP','J1939TP',
            'CANNM','CANSM','NM','OSEKNM','XCP',
            'DCM',
            'PORT','DIO','DEMO_LED_APP',
            'ASKAR',
-           'USB','USB_CAN','COMMONXML'
+           'COMMONXML'
            ]
 
 ARCH='stm32f1'
@@ -25,7 +25,7 @@ MODULES += ['CLIB_MISCLIB','CLIB_STRTOK_R']
 MODULES += ['CLIB_STDIO_PRINTF']
 MODULES += ['CLIB_STDIO_CAN']
 
-MODULES += ['FATFS', 'VFS', 'DEV', 'SDCARD','CLIB_ASHEAP']
+MODULES += ['CLIB_ASHEAP']
 
 asenv.Append(CPPDEFINES='configTOTAL_HEAP_SIZE=0x4000')
```

---

## 4. 🔄 QUY TRÌNH BIÊN DỊCH VÀ XÁC THỰC KỸ THUẬT (BUILD & VERIFICATION)

### 4.1 Quy trình thực thi:
```powershell
# Bước 1: Di chuyển vào thư mục hệ thống
cd as

# Bước 2: Thiết lập môi trường và sinh mã sạch
$env:BOARD="stm32f107vc"
$env:RELEASE="ascore"
scons -h

# Bước 3: Biên dịch toàn bộ binary
scons
```

### 4.2 Kết quả xác thực trên các Artifact thực tế:
1. **Biên dịch & Liên kết:** Thành công 100% (`scons: done building targets.`), sinh ra `build\nt\stm32f107vc\ascore\stm32f107vc.exe`.
2. **Xác thực Linker Map File ([stm32f107vc.map](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/build/nt/stm32f107vc/ascore/stm32f107vc.map)):**
   * Driver MCAL thật được nạp: `LOAD build\nt\stm32f107vc\ascore\com\as.infrastructure\arch\stm32f1\mcal\Can.o`
   * Driver STD Peripheral CAN được nạp: `LOAD build\nt\stm32f107vc\ascore\com\as.infrastructure\arch\stm32f1\Libraries\STM32F10x_StdPeriph_Driver\src\stm32f10x_can.o`
   * Hàm ngắt `Can_1_RxIsr` được phân bổ địa chỉ thật: `0x00000800`
   * Hàm ngắt `Can_1_TxIsr` được phân bổ địa chỉ thật: `0x0000080c`
   * Tệp rác CubeMX HAL `stm32f1xx_it.o` và driver ảo `SCan.o` đã bị loại bỏ hoàn toàn.
3. **Xác thực bảng Vector Table ([Os_Cfg.c: L1047-L1050](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/build/nt/stm32f107vc/ascore/config/Os_Cfg.c#L1047-L1050)):**
   ```c
   ISR_ADDR(Can_1_TxIsr),  /* 19: Vector ngắt truyền CAN Tx */
   ISR_ADDR(Can_1_RxIsr),  /* 20: Vector ngắt nhận CAN Rx */
   ISR_ADDR(default_isr_handle), /* 21 */
   ISR_ADDR(Can_1_ErrIsr), /* 22: Vector ngắt lỗi CAN Error/BusOff */
   ```

---

## 5. 🌐 CHUỖI GỌI HÀM THỰC THI THỜI GIAN THỰC FINAL FLOW

Sau khi chuẩn hóa, luồng thực thi trên Silicon thật STM32F107VC hoàn toàn nhất quán 100% với lý thuyết chuẩn của AUTOSAR Classic:

```
[VẬT LÝ BUS CAN]
       │
       ▼
[bxCAN HARDWARE CONTROLLER] (Lọc ID, nạp FIFO0, giương cờ FMP0)
       │
       ▼
[NVIC VECTOR 20] (CAN1_RX0_IRQn)
       │
       ▼
[OS KERNEL] (knl_isr_handler -> tisr_pc[20]() tại Os_Cfg.c: L1048)
       │
       ▼
[MCAL CAN DRIVER] (Can_1_RxIsr() tại Can.c: L222 -> Can_RxIsr() tại Can.c: L308)
       │   - Đọc phần cứng: CAN_Receive(canHw, CAN_FIFO0, &RxMessage)
       │   - Gọi Top-Half Callback: GET_CALLBACKS()->RxIndication()
       ▼
[CAN INTERFACE] (CanIf_RxIndication() tại CanIf.c: L380)
       │   - Lọc phần mềm Mask/ID: CanIf_RxPduConfigData
       │   - Chuyển tiếp Router: PduR_CanIfRxIndication()
       ▼
[PDU ROUTER] (PduR_Logic.c: L85)
       │   - Tra bảng định tuyến RxMsgAbsInfo_PduRRoutingPath
       │   - Zero-Copy chuyển tiếp: Com_RxIndication()
       ▼
[COM SERVICES] (Com_Com.c: L645)
       │   - Lưu bộ đệm RAM: RxMsgAbsInfo_IPduBuffer
       │   - Com_MainFunction_Rx() bóc tách Signal VehicleSpeed
       ▼
[RTE & APPLICATION SWC GAUGE] (Rte_SwcGauge.c & app.c)
       │   - Rte_Read_PpVehicleSpeed_VehicleSpeed(&speed)
       │   - Điều khiển kim đồng hồ tốc độ trên Taplo
```
