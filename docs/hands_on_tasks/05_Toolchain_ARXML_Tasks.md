# CHUYÊN ĐỀ 05: TOOLCHAIN & ARXML - THỰC HÀNH CẤU HÌNH VÀ TẠO MÃ TỰ ĐỘNG

## Cấu trúc source thực tế
- `as/com/as.tool/config.infrastructure.gui/` (GUI configurator)
- `as/com/as.tool/config.infrastructure.system/` (System gen tools)
- `as/com/as.tool/lua/` (Code generators)
- `as/com/as.infrastructure/system/EcuM/` (EcuM module)
- `as/com/as.infrastructure/system/BswM/` (BswM module)
- `as/com/as.infrastructure/system/SchM/` (Schedule Manager)
- Build: `scons --board=posix`

---

## TASK 5.1: Parse ARXML — Extract Signal & SWC List (~3h, Intermediate)

**Objective**: Viết Python script đọc file ARXML (nếu có trong `as/`) và extract danh sách signals.

- **Tìm file ARXML trong repo**:
  ```powershell
  Get-ChildItem -Path .\as -Recurse -Filter '*.arxml' | Select-Object FullName
  ```
- **Nếu không có ARXML sẵn** → Tạo mock ARXML mẫu khoảng 30 dòng với 3 signals.
- **Python script dùng `xml.etree.ElementTree` parse ARXML**:
  ```python
  import xml.etree.ElementTree as ET
  
  def parse_arxml(filepath):
      tree = ET.parse(filepath)
      root = tree.getroot()
      ns = {'ar': 'http://autosar.org/schema/r4.0'}
      signals = root.findall('.//ar:I-SIGNAL', ns)
      for sig in signals:
          name = sig.find('ar:SHORT-NAME', ns)
          length = sig.find('ar:LENGTH', ns)
          print(f'Signal: {name.text}, Length: {length.text} bits')
  ```
- **Output**: File CSV với các cột (Signal Name, Length, DataType, InitValue).
- **Success**: Script parse được ≥3 signals từ ARXML.

---

## TASK 5.2: Generate OIL Config from Template (~2h, Intermediate)

**Objective**: Tạo công cụ sinh tự động file `app.oil` từ JSON config.

- **JSON input**:
  ```json
  {
    "tasks": [
      {"name": "Task_10ms", "priority": 5, "stack": 512, "type": "BASIC"},
      {"name": "Task_Diag", "priority": 3, "stack": 1024, "type": "EXTENDED"},
      {"name": "Task_100ms", "priority": 2, "stack": 512, "type": "BASIC"}
    ],
    "os": {"conformance_class": "ECC2"}
  }
  ```
- **Python script với Jinja2 template**:
  ```python
  from jinja2 import Template
  
  OIL_TEMPLATE = '''
  OS MyOS {
    STATUS = EXTENDED;
    CONFORMANCETYPE = {{ os.conformance_class }};
  };
  {% for task in tasks %}
  TASK {{ task.name }} {
    PRIORITY = {{ task.priority }};
    SCHEDULE = FULL;
    STACK_DEFINES = TRUE;
    STACKSIZE = {{ task.stack }};
    TYPE = {{ task.type }};
  };
  {% endfor %}
  '''
  ```
- **Success**: Generated OIL file có đúng số tasks, priorities.

---

## TASK 5.3: EcuM Startup Flow Trace (~2h, Intermediate)

**Objective**: Trace toàn bộ boot sequence từ `main()` → `EcuM_Init` → `StartOS` → `EcuM_StartupTwo` → `Rte_Start`.

- **Files cần đọc**:
  - `as/com/as.infrastructure/system/EcuM/EcuM.c` (tìm `EcuM_Init`, `EcuM_StartupTwo`)
  - `as/com/as.application/board.posix/simulator/simulator.c` (`main()` cho POSIX)
- **Thêm printf timestamp vào mỗi phase để đo thời gian**:
  ```c
  #include <time.h>
  printf("[%ld ms] EcuM_Init() entry\n", clock() * 1000 / CLOCKS_PER_SEC);
  ```
- **Vẽ sequence diagram startup đầy đủ với thời gian mỗi phase**.
- **Xác định BSW modules nào init trong Phase 1 (Pre-OS) vs Phase 2 (Post-OS)**.
- **Success**: Sequence diagram đúng thứ tự, mỗi phase < 100ms.

---

## TASK 5.4: BswM Mode Switch — STARTUP to RUN (~3h, Advanced)

**Objective**: Trace cơ chế BswM chuyển trạng thái từ STARTUP sang RUN mode.

- **Files**: `as/com/as.infrastructure/system/BswM/BswM.c`
- **Tìm**: `BswM_Init()`, `BswM_RequestMode()`, `BswM_MainFunction()`
- **Implement logging để track mode transitions**:
  ```c
  void BswM_ActionList_RunMode(void) {
      printf("[BswM] Switching to RUN mode...\n");
      Com_IpduGroupStart(ComConf_IpduGroup_All, FALSE);
      printf("[BswM] COM groups enabled\n");
  }
  ```
- **Trigger**: `NvM_ReadAll()` complete → BswM nhận callback → switch to RUN.
- **Verify**: Sau khi switch, COM bắt đầu gửi periodic PDUs.
- **Success**: Log hiển thị đúng thứ tự mode switch.

---

## TASK 5.5 (Extension): Mock ARXML → Auto-generate RTE Code (~6h, Advanced)

**Objective**: Simulate quy trình DaVinci bằng Python script.

- **Bước 1**: Tạo mock ARXML với 2 SWCs và 1 S/R Interface.
- **Bước 2**: Python script parse ARXML → generate mock `Rte.h` với đúng function signatures.
- **Generated Rte.h**:
  ```c
  /* AUTO-GENERATED: DO NOT EDIT */
  extern Std_ReturnType Rte_Read_PPort_Speed_Speed(uint16 *data);
  extern Std_ReturnType Rte_Write_RPort_Torque_Torque(uint16 data);
  ```
- **Bước 3**: Viết SWC application code gọi generated `Rte.h`.
- **Bước 4**: Compile thành công.
- **Success**: SWC code compile với generated `Rte.h`.
