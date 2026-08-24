"""
Security Access (Service 0x27)
Thá»±c hiá»‡n trao Ä‘á»•i Seed/Key
"""
import can

TX_ID = 0x7E0
RX_ID = 0x7E8

def calculate_key(seed_bytes):
    """TÃ­nh key: Key = (Seed XOR 0x12345678) + 0xABCD"""
    seed = int.from_bytes(seed_bytes, byteorder='big')
    key = (seed ^ 0x12345678) + 0xABCD
    # Äáº£m báº£o key náº±m trong 4 bytes
    key = key & 0xFFFFFFFF
    return key.to_bytes(4, byteorder='big')

def security_access(bus):
    # 1. Request Seed (27 01)
    req_seed = [0x27, 0x01]
    bus.send(can.Message(arbitration_id=TX_ID, data=req_seed, is_extended_id=False))
    print("Gá»­i Request Seed (27 01)")
    
    res1 = bus.recv(timeout=1.0)
    if not res1 or res1.arbitration_id != RX_ID:
        print("KhÃ´ng nháº­n Ä‘Æ°á»£c Seed response.")
        return
        
    if res1.data[0] == 0x67 and res1.data[1] == 0x01:
        seed = res1.data[2:6]
        print(f"Nháº­n Seed: {seed.hex().upper()}")
        
        # 2. TÃ­nh Key
        key = calculate_key(seed)
        print(f"TÃ­nh toÃ¡n Key: {key.hex().upper()}")
        
        # 3. Send Key (27 02)
        send_key = [0x27, 0x02] + list(key)
        bus.send(can.Message(arbitration_id=TX_ID, data=send_key, is_extended_id=False))
        print("Gá»­i Send Key (27 02)")
        
        res2 = bus.recv(timeout=1.0)
        if res2 and res2.arbitration_id == RX_ID:
            if res2.data[0] == 0x67 and res2.data[1] == 0x02:
                print("Security Access: THÃ€NH CÃ”NG (Unlocked)")
            elif res2.data[0] == 0x7F:
                print(f"Security Access: THáº¤T Báº I. NRC: 0x{res2.data[2]:02X}")
    elif res1.data[0] == 0x7F:
        print(f"Lá»—i Request Seed. NRC: 0x{res1.data[2]:02X}")

if __name__ == '__main__':
    bus = can.interface.Bus(channel='vcan0', bustype='socketcan')
    try:
        security_access(bus)
    finally:
        bus.shutdown()
