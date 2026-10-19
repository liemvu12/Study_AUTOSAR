# Lộ Trình Thực Hành EB tresos Studio (NXP S32K) — Thay Thế Vector DaVinci

> 📌 **Mục tiêu chuyên đề:** Hướng dẫn kỹ sư nhúng làm chủ công cụ cấu hình AUTOSAR chuẩn công nghiệp **EB tresos Studio** (tích hợp trong NXP S32 Design Studio) hoàn toàn miễn phí, hợp pháp, thay thế cho Vector DaVinci đắt đỏ.  
> 🎯 **Đối tượng mục tiêu:** Kỹ sư Junior / Mid Embedded Automotive muốn tự tay click cấu hình, import file DBC/ARXML và bấm nút sinh mã nguồn BSW (`*_Cfg.c`, `*_PBcfg.c`) chuẩn 100% AUTOSAR.  
> 🛠️ **Môi trường thực hành:** NXP S32 Design Studio (S32DS) + Real-Time Drivers (RTD) / EB tresos Studio cho dòng vi điều khiển ô tô **NXP S32K144 / S32K3**.

---

## 1. Bảng Đối Chiếu Tư Duy Giữa Vector DaVinci & EB tresos Studio

Cả hai công cụ đều tuân thủ nghiêm ngặt **AUTOSAR Methodology**, do đó các khái niệm và luồng làm việc là **tương đương 1:1**:

| Tiêu Chí / Khái Niệm | Hệ Sinh Thái Vector | Hệ Sinh Thái Elektrobit (EB tresos NXP) | Ý Nghĩa Kỹ Thuật Trong AUTOSAR |
| :--- | :--- | :--- | :--- |
| **Thiết kế SWC / Cổng VFB** | DaVinci Developer | System Importer / Artop Editor | Định nghĩa Software Components, Ports, Interfaces, Data Types |
| **Cấu hình BSW & MCAL** | DaVinci Configurator Pro | **EB tresos Studio** | Cấu hình Can, CanIf, PduR, Com, Mcu, Port, Os... |
| **Bản quyền / Giấy phép** | Khóa cứng Dongle (Hàng nghìn USD) | **Miễn phí khi đăng ký tài khoản NXP** | Hợp pháp $100\%$ cho cá nhân học tập và nghiên cứu |
| **Đầu vào thiết kế mạng** | File `.dbc` hoặc `.arxml` | File `.dbc` hoặc `.arxml` | Bảng mô tả thông điệp mạng xe (Baudrate, CAN ID, StartBit...) |
| **Đầu ra sinh mã (Code Gen)** | `Can_PBcfg.c`, `Com_Cfg.c` | `Can_PBcfg.c`, `Com_Cfg.c` | Các file C tĩnh chứa struct hằng số nạp vào Flash MCU |

---

## 2. Hướng Dẫn Tải & Cài Đặt Môi Trường Miễn Phí (NXP Official)

### Bước 1: Đăng ký tài khoản NXP
1. Truy cập [nxp.com](https://www.nxp.com/) và đăng ký tài khoản miễn phí (dùng email cá nhân hoặc công ty/trường học).
2. Xác thực email và đăng nhập.

### Bước 2: Tải S32 Design Studio (S32DS)
1. Tìm kiếm và tải: **S32 Design Studio for ARM (phiên bản v2022 hoặc mới nhất)**.
2. Cài đặt S32DS theo hướng dẫn (bao gồm cả trình biên dịch GCC ARM Embedded).

### Bước 3: Cài đặt gói Real-Time Drivers (RTD) & EB tresos
1. Trong giao diện S32DS, mở menu: `Help` $\to$ `S32DS Extensions and Updates`.
2. Chọn gói **S32K1xx Real-Time Drivers (RTD)** (hoặc S32K3xx RTD).
3. Trình cài đặt sẽ tự động tích hợp **EB tresos Studio** (thường nằm tại thư mục: `C:\NXP\S32DS.x.x\eclipse\plugins\com.nxp.s32ds.tresos...` hoặc cài đặt dạng standalone).
4. Khởi chạy EB tresos Studio từ S32DS hoặc qua biểu tượng shortcut.

---

## 3. Cấu Trúc Thư Mục Bộ Bài Tập Thực Hành

Thư mục bài tập được thiết kế đầy đủ tài nguyên cho 5 bài thực hành (5 Labs):

```text
docs/hands_on_tasks/eb_tresos_nxp_lab/
├── README.md                      <-- (Bạn đang đọc tài liệu này)
├── lab_instructions.md            <-- Hướng dẫn chi tiết từng cú click chuột trên GUI EB tresos
└── sample_assets/                 <-- Tài nguyên mẫu sẵn sàng import vào tool
    ├── vehicle_network.dbc        <-- File DBC chuẩn (BMS ID 0x100, VCU ID 0x200)
    └── vehicle_system.arxml       <-- File ARXML System Description chuẩn AUTOSAR 4.x
```

---

## 4. Lộ Trình 5 Bài Thực Hành (5 Hands-On Labs)

### 🧪 [LAB 1: Khởi Tạo Dự Án & Cấu Hình MCAL Cơ Bản (Mcu, Port, Dio)](lab_instructions.md#lab-1-khởi-tạo-dự-án-s32k144--mcal-cơ-bản)
* **Thời lượng:** ~2 giờ
* **Mục tiêu:** Tạo workspace mới trong EB tresos, chọn chip target NXP S32K144, add các module BSW nền tảng: `Mcu` (Clock $80\text{MHz}$), `Port` (chân CAN0_Tx: PTE5, CAN0_Rx: PTE4), `Dio`.
* **Kết quả:** Sinh mã `Mcu_PBcfg.c`, `Port_PBcfg.c` không có lỗi validation.

### 🧪 [LAB 2: Cấu Hình MCAL CAN Driver Đạt Chuẩn 500 kbps](lab_instructions.md#lab-2-cấu-hình-mcal-can-driver-500-kbps)
* **Thời lượng:** ~3 giờ
* **Mục tiêu:** Cấu hình module `Can`:
  * Thiết lập Controller: Clock Source, Prescaler, `PropSeg`, `PhaseSeg1`, `PhaseSeg2` để ra chính xác $500\text{ kbps}$ và Sample Point $80\%$.
  * Thiết lập Mailbox HOH: 1 Hardware Transmit Handle (`Can0Hth`) và 1 Hardware Receive Handle (`Can0Hrh`).
  * Cấu hình Hardware Filter: Mask & Acceptance Code cho ID `0x100` và `0x200`.
* **Kết quả:** Sinh mã `Can_PBcfg.c` và kiểm tra mảng struct `Can_HardwareObjectType`.

### 🧪 [LAB 3: Cấu Hình Toàn Bộ Ngăn Xếp ComStack (CanIf → PduR → COM)](lab_instructions.md#lab-3-cấu-hình-toàn-bộ-ngăn-xếp-comstack-canif--pdur--com)
* **Thời lượng:** ~4 giờ
* **Mục tiêu:** Kết nối các mắt xích của ComStack:
  1. `CanIf`: Ánh xạ `CanTxPdu` vào `Can0Hth`, `CanRxPdu` vào `Can0Hrh`.
  2. `PduR`: Tạo Routing Path chuyển tiếp từ `Com` xuống `CanIf` (Zero-cost optimization).
  3. `Com`: Tạo tín hiệu `BatteryVoltage` (16-bit) và `BatteryCurrent` (16-bit signed), gán vào `IPDU_BMS_Status` với chu kỳ truyền $50\text{ms}$ (`PERIODIC`).
* **Kết quả:** Bộ 3 file cấu hình `CanIf_Cfg.c`, `PduR_Cfg.c`, `Com_Cfg.c` khớp nối hoàn hảo.

### 🧪 [LAB 4: Import Tự Động Từ File DBC & ARXML](lab_instructions.md#lab-4-import-tự-động-từ-file-dbc--arxml)
* **Thời lượng:** ~2.5 giờ
* **Mục tiêu:** Sử dụng tính năng **System Importer** trong EB tresos:
  * Nạp file [`sample_assets/vehicle_network.dbc`](sample_assets/vehicle_network.dbc) và [`sample_assets/vehicle_system.arxml`](sample_assets/vehicle_system.arxml).
  * Quan sát EB tresos tự động tạo ra toàn bộ Signal, I-PDU, CAN ID mà không cần tạo bằng tay từng mục.
* **Kết quả:** Hiểu rõ cách các kỹ sư Tier-1 / OEM tiết kiệm hàng trăm giờ làm việc bằng cách nạp file mô tả mạng.

### 🧪 [LAB 5: Kiểm Tra Mã Nguồn Sinh Ra & Đối Chiếu Với Kho Code Study_AUTOSAR](lab_instructions.md#lab-5-kiểm-tra-mã-nguồn-sinh-ra--đối-chiếu-study_autosar)
* **Thời lượng:** ~2 giờ
* **Mục tiêu:** Nhấn nút **"Generate Project"** trong EB tresos:
  * Mở các file `.c` được sinh ra trong thư mục `output/generated/`.
  * Đặt cạnh các file tương ứng trong kho `Study_AUTOSAR-main/as/build/` và `as/com/as.infrastructure/communication/`.
  * Nhận diện chính xác các struct: `Com_Config`, `CanIfTxPduConfigData`, `PduR_Config`.

---

## 5. Bắt Đầu Ngay

Mở file hướng dẫn từng bước chi tiết tại:  
👉 **[HƯỚNG DẪN THỰC HÀNH TỪNG BƯỚC: lab_instructions.md](lab_instructions.md)**
