# Hướng Dẫn Chi Tiết Từng Bước (Step-by-Step Lab Instructions)

> 💡 **Tài liệu tham chiếu:** Sử dụng kết hợp với các file mẫu trong thư mục `sample_assets/`:
> * File DBC: [`sample_assets/vehicle_network.dbc`](sample_assets/vehicle_network.dbc)
> * File ARXML: [`sample_assets/vehicle_system.arxml`](sample_assets/vehicle_system.arxml)

---

## LAB 1: Khởi Tạo Dự Án S32K144 & MCAL Cơ Bản

### 1.1 Tạo Workspace & Project Mới
1. Khởi động **EB tresos Studio** (từ S32DS hoặc qua shortcut).
2. Vào menu: `File` $\to$ `New` $\to$ `Configuration Project`.
3. Đặt tên dự án: `S32K144_ComStack_Practice`.
4. Tại bước **Target Selection**:
   * **Target:** `ARM`
   * **Derivate:** `S32K144`
   * **Sub-derivate:** `S32K144_LQFP100` (hoặc loại chân tương ứng)
5. Nhấn `Next`, tích chọn các module MCAL cơ bản:
   * ☑️ `Mcu`
   * ☑️ `Port`
   * ☑️ `Dio`
   * ☑️ `Resource` (nếu có yêu cầu từ RTD)
6. Nhấn `Finish` để hoàn tất tạo project.

### 1.2 Cấu Hình Module Mcu (Clock Hệ Thống 80 MHz)
1. Trong cửa sổ **Project Explorer**, mở rộng `S32K144_ComStack_Practice` $\to$ click đúp vào module `Mcu`.
2. Chuyển sang tab **McuModuleConfiguration**:
   * Chọn `McuClockSettingConfig`: Thiết lập nguồn clock SPLL ($80\text{MHz}$).
   * Kiểm tra thông số Clock cấp cho ngoại vi FlexCAN0: Phải đảm bảo bus clock cấp cho CAN là $40\text{MHz}$ hoặc $80\text{MHz}$ (ghi nhớ con số này để tính toán baudrate ở Lab 2).
3. Nhấn `Ctrl + S` để lưu cấu hình.

### 1.3 Cấu Hình Module Port (Chân Pin CAN)
1. Click đúp vào module `Port`.
2. Mở `PortConfigSet` $\to$ `PortContainer` $\to$ tìm cổng **Port E**:
   * **Pin PTE4 (CAN0_Rx):**
     * `PortPinDirection`: `PORT_PIN_IN`
     * `PortPinInitialMode`: `CAN0_RX` (chế độ Multiplexing của chân chip)
   * **Pin PTE5 (CAN0_Tx):**
     * `PortPinDirection`: `PORT_PIN_OUT`
     * `PortPinInitialMode`: `CAN0_TX`
3. Nhấn `Ctrl + S` lưu cấu hình.

---

## LAB 2: Cấu Hình MCAL CAN Driver (500 kbps)

### 2.1 Thêm Module CAN Vào Dự Án
1. Chuột phải vào tên Project trong Project Explorer $\to$ chọn `Module Configurations`.
2. Nhấn `Add` $\to$ tìm và chọn module `Can` $\to$ Nhấn `OK`.

### 2.2 Cấu Hình Bộ Chia Tần Số & Bit Timing (CanController)
Mục tiêu: Đạt tốc độ chuẩn **500 kbps** với Sample Point $80\%$, giả sử Clock ngoại vi cấp cho CAN là $f_{\text{CAN}} = 40\text{MHz}$:

$$\text{Bit Time} = \frac{1}{500,000\text{ Hz}} = 2.0\,\mu\text{s}$$
$$\text{Chọn tổng số Time Quanta: } N_{\text{total}} = 16\text{ Tq} \implies 1\text{ Tq} = \frac{2.0\,\mu\text{s}}{16} = 0.125\,\mu\text{s}$$
$$\text{Prescaler} = \frac{f_{\text{CAN}}}{f_{\text{Tq}}} = \frac{40\text{MHz}}{8\text{MHz}} = 5 \implies \text{Giá trị nạp thanh ghi: } \text{Prescaler} - 1 = 4$$

Phân bổ 16 Time Quanta (Sample point $80\% \implies$ lấy mẫu tại Tq thứ 13):
* `Sync_Seg` = 1 Tq (Cố định chuẩn ISO)
* `PropSeg` = 3 Tq
* `PhaseSeg1` = 8 Tq $\implies \text{Sample Point} = \frac{1 + 3 + 8}{16} = \frac{12}{16} = 75\% \sim 80\%$
* `PhaseSeg2` = 4 Tq
* `RJW` (Resynchronization Jump Width) = 2 Tq

**Các bước thao tác trong GUI EB tresos:**
1. Mở module `Can` $\to$ vào tab **CanConfigSet** $\to$ `CanController`.
2. Chọn `CanController_0`:
   * `CanControllerId`: `0`
   * `CanControllerActivation`: `TRUE`
   * `CanBusoffProcessing`: `INTERRUPT`
   * `CanRxProcessing`: `INTERRUPT`
   * `CanTxProcessing`: `INTERRUPT`
3. Mở tiếp `CanControllerBaudrateConfig`:
   * `CanControllerBaudRate`: `500` (kbps)
   * `CanControllerPrescaler`: `4` (tương ứng chia 5)
   * `CanControllerPropSeg`: `3`
   * `CanControllerSeg1`: `8`
   * `CanControllerSeg2`: `4`
   * `CanControllerSyncJumpWidth`: `2`

### 2.3 Cấu Hình Mailbox HOH (Hardware Object Handles)
1. Trong `CanConfigSet`, chuyển sang tab **CanHardwareObject**:
2. **Tạo HTH (Bộ đệm phát):**
   * Bấm nút `+` $\to$ Đặt tên: `CanHardwareObject_Tx`
   * `CanObjectType`: `TRANSMIT`
   * `CanHandleType`: `BASIC`
   * `CanIdType`: `STANDARD`
   * `CanObjectId`: `0`
   * `CanControllerRef`: Trỏ đến `CanController_0`
3. **Tạo HRH (Bộ đệm thu):**
   * Bấm nút `+` $\to$ Đặt tên: `CanHardwareObject_Rx`
   * `CanObjectType`: `RECEIVE`
   * `CanHandleType`: `BASIC`
   * `CanIdType`: `STANDARD`
   * `CanObjectId`: `1`
   * `CanControllerRef`: Trỏ đến `CanController_0`
4. Cấu hình Filter cho HRH:
   * `CanHwFilterCode`: `0x100` (Đón bản tin BMS)
   * `CanHwFilterMask`: `0x700` (Nhận dải ID `0x100` đến `0x1FF`)

---

## LAB 3: Cấu Hình Toàn Bộ Ngăn Xếp ComStack (CanIf → PduR → COM)

### 3.1 Cấu Hình Tầng CanIf (CAN Interface)
1. Thêm module `CanIf` vào project (`Module Configurations` $\to$ `Add CanIf`).
2. Mở module `CanIf`:
   * **CanIfCtrlDrvCfg:** Chọn driver `Can`, gắn controller ID `0`.
   * **CanIfHthCfg:** Tạo HTH tham chiếu đến `CanHardwareObject_Tx` của module Can.
   * **CanIfHrhCfg:** Tạo HRH tham chiếu đến `CanHardwareObject_Rx` của module Can.
   * **CanIfTxPduCfg (Gói truyền):**
     * `CanIfTxPduId`: `0` (Tên: `CanIfTxPdu_BMS_Status`)
     * `CanIfCanTxPduIdCanId`: `0x100` (CAN ID 256)
     * `CanIfCanTxPduHthRef`: Trỏ đến `CanIfHthCfg` vừa tạo
     * `CanIfUserTxConfirmation`: Chọn callback lên PduR
   * **CanIfRxPduCfg (Gói nhận):**
     * `CanIfRxPduId`: `0` (Tên: `CanIfRxPdu_VCU_Control`)
     * `CanIfCanRxPduCanId`: `0x200` (CAN ID 512)
     * `CanIfCanRxPduHrhRef`: Trỏ đến `CanIfHrhCfg` vừa tạo
     * `CanIfUserRxIndication`: Chọn callback lên PduR

### 3.2 Cấu Hình Tầng PduR (PDU Router)
1. Thêm module `PduR` vào project.
2. Mở `PduRBswModules`: Khai báo 2 module giao tiếp là `COM` và `CANIF`.
3. Mở **PduRRoutingTables** $\to$ `PduRRoutingPath`:
   * **Tuyến Tx (Từ COM xuống CAN):**
     * `PduRSrcPdu`: Trỏ đến I-PDU phát của module COM
     * `PduRDestPdu`: Trỏ đến `CanIfTxPdu_BMS_Status` của CanIf
   * **Tuyến Rx (Từ CAN lên COM):**
     * `PduRSrcPdu`: Trỏ đến `CanIfRxPdu_VCU_Control` của CanIf
     * `PduRDestPdu`: Trỏ đến I-PDU nhận của module COM

### 3.3 Cấu Hình Tầng COM (AUTOSAR COM)
1. Thêm module `Com` vào project.
2. Mở **ComIPdu**:
   * Tạo `ComIPdu_BMS_Status`:
     * `ComIPduDirection`: `SEND`
     * `ComIPduLength`: `8` (bytes)
     * `ComIPduType`: `NORMAL`
     * `ComTxModeTrue`:
       * `ComTxModeMode`: `PERIODIC`
       * `ComTxModeTimePeriod`: `0.05` ($50\text{ms}$)
3. Mở **ComSignal**:
   * **Tín hiệu 1: BatteryVoltage**
     * `ComBitPosition`: `0`
     * `ComBitSize`: `16`
     * `ComSignalType`: `UINT16`
     * `ComSignalEndianness`: `BIG_ENDIAN` (Motorola) hoặc `LITTLE_ENDIAN`
     * `ComIPduRef`: Trỏ vào `ComIPdu_BMS_Status`
     * `ComTransferProperty`: `PENDING` (chờ chu kỳ $50\text{ms}$ gửi)
   * **Tín hiệu 2: BatteryCurrent**
     * `ComBitPosition`: `16`
     * `ComBitSize`: `16`
     * `ComSignalType`: `SINT16` (Số nguyên có dấu)
     * `ComIPduRef`: Trỏ vào `ComIPdu_BMS_Status`
     * `ComTransferProperty`: `PENDING`

---

## LAB 4: Import Tự Động Từ File DBC & ARXML

Thay vì phải click tạo từng Signal và PDU bằng tay như Lab 3, ta sử dụng tính năng **System Importer**:

1. Trong EB tresos Studio, vào menu: `Project` $\to$ `Import` $\to$ chọn `AUTOSAR System Description (.arxml)`.
2. Trỏ đường dẫn đến file:
   `docs/hands_on_tasks/eb_tresos_nxp_lab/sample_assets/vehicle_system.arxml`
3. Tại màn hình **Import Options**:
   * Chọn `ECU Extract`: Chọn ECU cần cấu hình (ví dụ `BMS`).
   * Tích chọn: `Create ComStack Configuration Automatically`.
4. Nhấn `Finish`.
5. **Quan sát kết quả:**
   * Mở lại các module `Com`, `PduR`, `CanIf`: Toàn bộ các Signal `BatteryVoltage`, `BatteryCurrent`, I-PDU `IPDU_BMS_Status` và CAN ID `0x100` đã được tool tự động sinh ra và liên kết chính xác $100\%$!

---

## LAB 5: Sinh Mã Nguồn (Code Gen) & Đối Chiếu Với Kho Code Study_AUTOSAR

### 5.1 Kiểm Tra Lỗi Cấu Hình (Validation & Verification)
1. Trước khi sinh mã, bấm vào nút biểu tượng dấu tích xanh: **Verify Project** (hoặc `Project` $\to$ `Verify Project`).
2. Kiểm tra cửa sổ **Problems View**:
   * Nếu có dấu chấm than đỏ (Error): Click đúp vào lỗi để tool tự động nhảy đến thông số bị thiếu (ví dụ: quên gán reference, trùng ID). Sửa hết cho đến khi đạt `0 Errors`.

### 5.2 Sinh Mã C (Code Generation)
1. Bấm nút biểu tượng mũi tên xanh: **Generate Project** (hoặc phím tắt `Ctrl + G`).
2. Mở thư mục đầu ra của dự án (thường nằm tại `<project_dir>/output/generated/` hoặc `<project_dir>/generate/`):
   * `include/Can_PBcfg.h` và `src/Can_PBcfg.c`
   * `include/CanIf_Cfg.h` và `src/CanIf_Cfg.c`
   * `include/PduR_Cfg.h` và `src/PduR_Cfg.c`
   * `include/Com_Cfg.h` và `src/Com_Cfg.c`

### 5.3 Đối Chiếu Trực Tiếp Với Kho Mã Nguồn `Study_AUTOSAR-main`
Mở các file vừa sinh ra đặt cạnh các file tương ứng trong dự án học tập:

| File Sinh Ra Từ EB tresos | File Tương Ứng Trong `Study_AUTOSAR-main` | Điểm Tương Đồng Kiến Trúc Cần Quan Sát |
| :--- | :--- | :--- |
| `Can_PBcfg.c` | [`as/build/nt/lm3s6965evb/ascore/config/Can_PBcfg.c`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/build/nt/lm3s6965evb/ascore/config/Can_PBcfg.c) | Đều chứa mảng cấu hình `Can_HardwareObjectType` định nghĩa các mailbox HTH và HRH. |
| `CanIf_Cfg.c` | [`as/build/nt/lm3s6965evb/ascore/config/CanIf_Cfg.c`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/build/nt/lm3s6965evb/ascore/config/CanIf_Cfg.c) | Đều chứa mảng `CanIfTxPduConfigData` ánh xạ từ `CanTxPduId` sang `CanId = 0x100`. |
| `PduR_Cfg.c` | [`as/build/nt/lm3s6965evb/ascore/config/PduR_Cfg.c`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/build/nt/lm3s6965evb/ascore/config/PduR_Cfg.c) | Đều chứa bảng con trỏ định tuyến tĩnh `PduRRoutingPath_type`. |
| `Com_Cfg.c` | [`as/com/as.infrastructure/communication/Com/Com_Com.c`](file:///C:/Users/liem.vu/Liem.vuOD/Study_AUTOSAR-main/as/com/as.infrastructure/communication/Com/Com_Com.c) | Định nghĩa mảng struct `ComSignal_type` chứa vị trí StartBit và chiều dài bit của tín hiệu. |

---

## 🎯 Tổng Kết Thành Quả Kỹ Nghệ

Sau khi hoàn thành 5 bài Lab này, bạn đã:
1. Thành thạo quy trình làm việc chuẩn công nghiệp của **Elektrobit tresos Studio** — công cụ BSW phổ biến hàng đầu thế giới xe hơi.
2. Tự tay cấu hình từ tầng đáy vi điều khiển (Clock, Pin, Mailbox CAN 500k) xuyên qua các tầng router PduR đến tầng đóng gói tín hiệu COM.
3. Hiểu rõ sự kết nối thần kỳ: **File ARXML/DBC $\longrightarrow$ Tool EB tresos $\longrightarrow$ Code C sinh tự động $\longrightarrow$ Khung vi sai bay trên dây CAN vật lý**.
