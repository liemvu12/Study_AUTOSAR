import sys, time, can

sys.stdout.reconfigure(encoding='utf-8')

def send_can_stream(port="COM1", baudrate=500000, count=10):
    print(f"[*] Connecting to Virtual CAN via SLCAN on {port} (Bitrate: {baudrate} bps)...")
    try:
        bus = can.interface.Bus(interface='slcan', channel=port, bitrate=baudrate)
        print("[+] Connected successfully! Broadcasting CAN frames...")
        
        for i in range(count):
            # Frame 1: BMS State (ID: 0x180 / Dec 384)
            # Data layout (Little Endian):
            # Byte 0: SoC (0-100%)
            # Byte 1: SoH (100%)
            # Byte 2-3: Pack Voltage (0.1V/bit -> 3600 = 360.0V -> 0x0E10 -> [0x10, 0x0E])
            # Byte 4-5: Pack Current (0.1A/bit -> 15.0A -> 150 -> 0x0096 -> [0x96, 0x00])
            # Byte 6: Max Cell Temp (Offset -40 -> 65 = 25 degC)
            # Byte 7: Fault Flags (0 = OK)
            soc = 80 - (i % 20)
            temp = 65 + (i % 5) # 25°C to 29°C
            msg_bms = can.Message(
                arbitration_id=0x180,
                data=[soc, 100, 0x10, 0x0E, 0x96, 0x00, temp, 0x00],
                is_extended_id=False
            )
            bus.send(msg_bms)
            
            # Frame 2: VCU Torque Command (ID: 0x200 / Dec 512)
            # Data layout (Little Endian):
            # Byte 0: Gear Mode (3 = DRIVE)
            # Byte 1-2: Target Speed (km/h -> [speed & 0xFF, 0x00])
            # Byte 3-4: Target Torque (Nm -> [120, 0x00])
            # Byte 5: Brake Pedal Pos (0%)
            # Byte 6: Accel Pedal Pos (40% -> 80 with factor 0.5)
            # Byte 7: Ready Status (1 = READY)
            speed = 40 + i
            msg_vcu = can.Message(
                arbitration_id=0x200,
                data=[0x03, speed & 0xFF, (speed >> 8) & 0xFF, 120, 0x00, 0x00, 80, 0x01],
                is_extended_id=False
            )
            bus.send(msg_vcu)
            
            real_temp = temp - 40
            print(f" -> [Frame #{i+1}] BMS(ID=0x180, SoC={soc}%, V=360.0V, T={real_temp}°C) | VCU(ID=0x200, Mode=DRIVE, Speed={speed} km/h, Torque=120Nm)")
            time.sleep(0.5)
            
        print("[+] Broadcast finished successfully!")
        bus.shutdown()
    except Exception as e:
        print(f"[-] Error: {e}")

if __name__ == "__main__":
    port = sys.argv[1] if len(sys.argv) > 1 else "COM1"
    count = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    send_can_stream(port=port, count=count)
