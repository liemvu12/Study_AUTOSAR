"""
01_session_control.py - UDS Service 0x10: DiagnosticSessionControl
===================================================================
Mục đích: Chuyển ECU sang Extended Diagnostic Session (0x03)
          để mở khóa các service nâng cao (0x27, 0x2E...).

Cách dùng:
    python 01_session_control.py

Yêu cầu:
    - pip install python-can
    - virtual CAN: sudo ip link add dev vcan0 type vcan && sudo ip link set vcan0 up
    - ECU simulator đang chạy trên vcan0
"""

import can
import time

# --- Cấu hình địa chỉ UDS ---
TX_ID = 0x7DF   # Functional addressing (broadcast)
RX_ID = 0x7E8   # ECU response ID (thay đổi nếu ECU dùng physical addressing)
CHANNEL = 'vcan0'
TIMEOUT_S = 1.0  # Timeout chờ response (giây)

# UDS Session Types
SESSION_DEFAULT  = 0x01  # DefaultSession
SESSION_EXTENDED = 0x03  # ExtendedDiagnosticSession
SESSION_PROG     = 0x02  # ProgrammingSession (flash update)

# UDS Response codes
POS_RESPONSE_OFFSET = 0x40  # Positive response = ServiceID + 0x40
NRC_RESPONSE_ID     = 0x7F  # Negative Response Code indicator

# NRC Table (phổ biến nhất)
NRC_TABLE = {
    0x10: "generalReject",
    0x11: "serviceNotSupported",
    0x12: "subFunctionNotSupported",
    0x13: "incorrectMessageLengthOrInvalidFormat",
    0x22: "conditionsNotCorrect",
    0x31: "requestOutOfRange",
    0x33: "securityAccessDenied",
    0x35: "invalidKey",
    0x36: "exceededNumberOfAttempts",
    0x37: "requiredTimeDelayNotExpired",
}


def interpret_nrc(nrc_byte: int) -> str:
    """Trả về tên của NRC code."""
    return NRC_TABLE.get(nrc_byte, f"Unknown NRC (0x{nrc_byte:02X})")


def send_uds_request(bus: can.Bus, request_data: list) -> list | None:
    """
    Gửi UDS request và chờ response.

    Args:
        bus: CAN bus instance
        request_data: List bytes của UDS request (không tính PCI byte)

    Returns:
        List bytes của response, hoặc None nếu timeout
    """
    # Tạo CAN frame với ISO 15765-2 Single Frame (SF)
    # Byte 0: PCI = 0x0N (SF, length = N)
    pci_byte = len(request_data) & 0x0F
    frame_data = [pci_byte] + request_data

    # Pad đến 8 bytes (CAN padding)
    while len(frame_data) < 8:
        frame_data.append(0xAA)  # padding byte

    msg = can.Message(
        arbitration_id=TX_ID,
        data=frame_data[:8],
        is_extended_id=False
    )

    bus.send(msg)
    hex_str = ' '.join(f'{b:02X}' for b in frame_data[:pci_byte + 1])
    print(f"  TX [0x{TX_ID:03X}]: {hex_str}")

    # Chờ response
    deadline = time.time() + TIMEOUT_S
    while time.time() < deadline:
        response = bus.recv(timeout=0.1)
        if response is None:
            continue
        if response.arbitration_id == RX_ID:
            resp_len = response.data[0] & 0x0F  # PCI byte: length
            resp_bytes = list(response.data[1:1 + resp_len])
            hex_str = ' '.join(f'{b:02X}' for b in resp_bytes)
            print(f"  RX [0x{RX_ID:03X}]: {hex_str}")
            return resp_bytes

    print("  ⏰ Timeout: Không nhận được response từ ECU")
    return None


def session_control(session_type: int = SESSION_EXTENDED) -> bool:
    """
    Gửi DiagnosticSessionControl request.

    Args:
        session_type: 0x01=Default, 0x02=Programming, 0x03=Extended

    Returns:
        True nếu thành công, False nếu thất bại
    """
    session_names = {
        SESSION_DEFAULT:  "Default",
        SESSION_PROG:     "Programming",
        SESSION_EXTENDED: "Extended",
    }
    name = session_names.get(session_type, f"Unknown(0x{session_type:02X})")

    print(f"\n[UDS 0x10] DiagnosticSessionControl → {name} Session")
    print(f"  Request: 10 {session_type:02X}")

    try:
        bus = can.interface.Bus(channel=CHANNEL, bustype='socketcan')
    except Exception as e:
        print(f"  ❌ Không thể mở CAN bus '{CHANNEL}': {e}")
        print(f"  💡 Tip: sudo ip link add dev {CHANNEL} type vcan && sudo ip link set {CHANNEL} up")
        return False

    try:
        response = send_uds_request(bus, [0x10, session_type])

        if response is None:
            return False

        # Kiểm tra Positive Response: 50 [session_type]
        if response[0] == (0x10 + POS_RESPONSE_OFFSET) and response[1] == session_type:
            print(f"  ✅ Session changed to {name} (0x{session_type:02X})")
            if len(response) >= 4:
                # P2 và P2* timing parameters (nếu có)
                p2_ms = (response[2] << 8 | response[3])
                print(f"  ℹ️  P2 server timing: {p2_ms} ms")
            return True

        # Kiểm tra Negative Response: 7F 10 NRC
        elif response[0] == NRC_RESPONSE_ID:
            nrc = response[2] if len(response) > 2 else 0
            print(f"  ❌ Negative Response: NRC=0x{nrc:02X} ({interpret_nrc(nrc)})")
            return False

        else:
            print(f"  ⚠️  Unexpected response: {' '.join(f'{b:02X}' for b in response)}")
            return False

    finally:
        bus.shutdown()


def demo_session_sequence():
    """Demo chuyển session: Default -> Extended -> Default."""
    print("=" * 60)
    print("DEMO: UDS Session Control Sequence")
    print("=" * 60)

    # Bước 1: Chuyển sang Extended Session
    success = session_control(SESSION_EXTENDED)

    if success:
        print("\n  ✅ Extended session active. Có thể dùng:")
        print("     - Service 0x27 (SecurityAccess)")
        print("     - Service 0x2E (WriteDataByIdentifier)")
        print("     - Service 0x85 (ControlDTCSetting)")

        # Giả lập làm gì đó trong extended session
        time.sleep(0.5)

        # Bước 2: Quay lại Default Session
        print("\n  ↩️  Trở về Default Session...")
        session_control(SESSION_DEFAULT)

    print("\n" + "=" * 60)


if __name__ == '__main__':
    demo_session_sequence()
