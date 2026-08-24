# Python-CAN UDS Scripts — AUTOSAR Diagnostic Lab

> **Mục đích:** Tập hợp Python scripts để test UDS (Unified Diagnostic Services) với ECU qua CAN bus.  
> **Yêu cầu:** Python 3.9+, python-can, cantools, virtual CAN (vcan0 trên Linux/WSL2)

---

## ⚙️ Setup Virtual CAN (Linux / WSL2)

```bash
# Load vcan kernel module
sudo modprobe vcan

# Tạo virtual CAN interface
sudo ip link add dev vcan0 type vcan
sudo ip link set vcan0 up

# Verify
ip link show vcan0
# Expected: vcan0: <NOARP,UP,LOWER_UP> mtu 72 ...

# Install Python dependencies
pip install python-can cantools
```

---

## 📋 Script List

| Script | Service | Mô tả |
|--------|---------|-------|
| `01_session_control.py` | 0x10 | Chuyển sang Extended Diagnostic Session |
| `02_read_did.py` | 0x22 | Đọc VIN (0xF190) và ECU Serial Number |
| `03_security_access.py` | 0x27 | Seed/Key exchange để unlock session |
| `04_read_dtc.py` | 0x19 | Đọc danh sách DTCs với status byte |
| `05_clear_dtc.py` | 0x14 | Xóa tất cả DTCs |
| `06_can_sniffer.py` | N/A | Sniff CAN bus và decode với DBC file |

---

## 🚀 Cách Sử Dụng

```bash
# Bước 1: Setup vcan0 (xem hướng dẫn trên)

# Bước 2: Chạy AUTOSAR POSIX simulator (ECU giả lập)
cd Study_AUTOSAR-main/as
scons --board=posix
./build/posix/as &

# Bước 3: Chạy script test
python 01_session_control.py
python 02_read_did.py
python 03_security_access.py

# Bước 4: Sniff tất cả traffic
python 06_can_sniffer.py --channel vcan0
```

---

## 📖 UDS Address Configuration

```python
# Mặc định trong scripts:
TX_ID = 0x7DF   # Functional addressing (broadcast tới tất cả ECUs)
RX_ID = 0x7E8   # Physical response từ ECU đầu tiên (ECU address 0x00)

# Nếu ECU dùng physical addressing:
TX_ID = 0x7E0   # Physical request tới ECU cụ thể
RX_ID = 0x7E8   # ECU response
```

---

## 🐛 Troubleshooting

| Lỗi | Nguyên nhân | Fix |
|-----|------------|-----|
| `OSError: [Errno 19] No such device` | vcan0 chưa được tạo | Chạy `sudo ip link add dev vcan0 type vcan` |
| `Timeout: No response` | ECU không chạy hoặc sai address | Check simulator đang chạy, check TX_ID/RX_ID |
| `ModuleNotFoundError: can` | python-can chưa install | `pip install python-can` |
| `NRC 0x22 conditionsNotCorrect` | Sai session | Chạy 01_session_control.py trước |
| `NRC 0x35 invalidKey` | Key sai trong SecurityAccess | Check thuật toán seed/key trong ECU config |

---

## 🔗 Tài Liệu Liên Quan

- `docs/04_Diagnostic_UDS_And_Memory_Stack.md` — Lý thuyết UDS
- `docs/CHEATSHEET_QUICK_REFERENCE.md` — UDS service table nhanh
- `docs/DEBUGGING_AND_PROFILING_GUIDE.md` — Debug scenarios
