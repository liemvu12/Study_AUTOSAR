# Tài Liệu Giải Thích Kiến Trúc ARXML (AUTOSAR 4.3)

Trong AUTOSAR, file ARXML đóng vai trò như là bản thiết kế của hệ thống. Dưới đây là giải thích chi tiết cho từng cấu trúc chính trong các file mẫu đã tạo.

## 1. AUTOSAR-PACKAGE (Cấu trúc phân cấp Package)
```xml
<AR-PACKAGE>
  <SHORT-NAME>BMS_VCU_System</SHORT-NAME>
</AR-PACKAGE>
```
**Giải thích:**
AR-PACKAGE là cách AUTOSAR tổ chức các cấu trúc theo dạng thư mục ảo (như namespace trong C++). Nó giúp phân chia quản lý component, datatype, interface sao cho không bị trùng lặp tên.

## 2. SHORT-NAME
```xml
<SHORT-NAME>BMS_SWC</SHORT-NAME>  <!-- ← Tên định danh, phải unique trong package -->
```
**Giải thích:**
SHORT-NAME là định danh của mọi phần tử (Element) trong AUTOSAR. Tên này bắt buộc phải độc nhất (Unique) trong một `AR-PACKAGE` cụ thể.

## 3. Các loại SW-COMPONENT-TYPE
- **APPLICATION-SW-COMPONENT-TYPE**: Là thành phần phần mềm chính chứa logic ứng dụng (như BMS_SWC và VCU_SWC).
- **SERVICE-SW-COMPONENT-TYPE**: Thường thuộc lớp BSW (Basic Software), cung cấp các dịch vụ hệ thống như NvM (Non-Volatile Memory) hoặc Diagnostic.
- **COMPOSITION-SW-COMPONENT-TYPE**: Một thành phần dạng hộp chứa (Container) dùng để ghép nối các Component nhỏ hơn với nhau tạo thành hệ thống lớn.

## 4. PORTS: P-PORT và R-PORT
```xml
<P-PORT-PROTOTYPE> <!-- Provide Port -->
  <SHORT-NAME>BMS_StatusPort</SHORT-NAME>
</P-PORT-PROTOTYPE>
<R-PORT-PROTOTYPE> <!-- Require Port -->
  <SHORT-NAME>BMS_TorqueLimitPort</SHORT-NAME>
</R-PORT-PROTOTYPE>
```
**Giải thích:**
- **P-PORT (Provide):** Cổng cung cấp thông tin/dịch vụ ra ngoài.
- **R-PORT (Require):** Cổng yêu cầu thông tin/dịch vụ từ bên ngoài để thực thi.

## 5. Các Loại Giao Diện (INTERFACES)
- **SENDER-RECEIVER-INTERFACE:** Giao tiếp bằng cách truyền Data (Ví dụ: SoC, Current, Voltage) đi. Giống kiểu broadcast/multicast (gửi/nhận không đồng bộ).
- **CLIENT-SERVER-INTERFACE:** Giao tiếp bằng cách gọi hàm. Một bên cung cấp Operation (Server), bên kia gọi Operation đó (Client).

## 6. DATA-ELEMENT
```xml
<VARIABLE-DATA-PROTOTYPE>
  <SHORT-NAME>StateOfCharge</SHORT-NAME>
  <TYPE-TREF DEST="IMPLEMENTATION-DATA-TYPE">/DataTypes/uint8</TYPE-TREF>
</VARIABLE-DATA-PROTOTYPE>
```
**Giải thích:**
- **InitValue**: Cho biết giá trị khởi tạo khi Component chưa nhận được dữ liệu.
- **Category**: Phân loại dạng dữ liệu (Value, Array, String).
- **SwDataDefProps**: Cung cấp thêm thuộc tính cho biến (Ví dụ: Range giới hạn, Đơn vị tính).

## 7. RUNNABLE-ENTITY
```xml
<RUNNABLE-ENTITY>
  <SHORT-NAME>BMS_MainRunnable</SHORT-NAME>
  <SYMBOL>Bms_MainFunction</SYMBOL> <!-- Hàm C thực tế sẽ được sinh ra -->
</RUNNABLE-ENTITY>
```
**Giải thích:**
Runnable Entity là đơn vị thực thi nhỏ nhất của AUTOSAR (tương đương với một Task/hàm).
Thuộc tính `SYMBOL` chính là tên hàm C thực tế mà tool (như DaVinci Developer) sẽ generate ra trong file code, ví dụ: `void Bms_MainFunction(void) {}`.

## 8. TIMING-EVENT
```xml
<TIMING-EVENT>
  <SHORT-NAME>TET_BMS_MainRunnable</SHORT-NAME>
  <PERIOD>0.01</PERIOD> <!-- Chu kỳ 10ms -->
</TIMING-EVENT>
```
**Giải thích:**
Dùng để kích hoạt một Runnable theo chu kỳ thời gian (định kì lặp lại) được cấu hình bằng `PERIOD`.

## 9. COMPOSITION (Lắp Ghép Hệ Thống)
Dùng `COMPOSITION-SW-COMPONENT-TYPE` và `ASSEMBLY-SW-CONNECTOR` để định nghĩa cách 1 cổng Provide (P-Port) nối với 1 cổng Require (R-Port) giữa hai SWC khác nhau. Đây là "Communication Matrix Mapping" mức độ Component.

## 10. Cách DaVinci Developer xử lý
- **DaVinci Developer** đọc file ARXML, trích xuất cấu trúc Interfaces, Ports, Data Elements.
- Sau đó, nó sinh ra file header `Rte.h` và `Rte_<SwcName>.h` chứa các macro/API như `Rte_Write_BMS_StatusPort_StateOfCharge()`.
- File C được sinh ra như những "Skeleton" (khung hàm rỗng dựa vào SYMBOL của Runnables) để lập trình viên tự thêm logic.
- Nó cũng có built-in validator để check cú pháp dựa trên **AUTOSAR XML Schema (XSD)**. Nếu sai cấu trúc XSD của AUTOSAR 4.3 thì sẽ báo lỗi không load được ARXML.
