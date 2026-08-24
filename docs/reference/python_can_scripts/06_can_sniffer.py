"""
General CAN sniffer vá»›i DBC decode
DÃ¹ng cantools Ä‘á»ƒ decode dá»¯ liá»‡u thÃ´ (raw byte) sang tÃ­n hiá»‡u váº­t lÃ½.
"""
import can
import cantools

def sniff_and_decode(dbc_file: str, channel: str = 'vcan0'):
    try:
        db = cantools.database.load_file(dbc_file)
        bus = can.interface.Bus(channel=channel, bustype='socketcan')
        print(f"Sniffing on {channel} vá»›i DBC file '{dbc_file}'...")
        
        for msg in bus:
            try:
                # Decode message based on DBC
                decoded = db.decode_message(msg.arbitration_id, msg.data)
                name = db.get_message_by_frame_id(msg.arbitration_id).name
                print(f"[{msg.timestamp:.3f}] {name}: {decoded}")
            except Exception:
                # Náº¿u ID khÃ´ng cÃ³ trong DBC, in ra dáº¡ng Hex
                print(f"[{msg.timestamp:.3f}] ID=0x{msg.arbitration_id:03X}: {msg.data.hex().upper()}")
    except Exception as e:
        print(f"Lá»—i: {e}")

if __name__ == '__main__':
    # Äáº·t file DBC máº«u cá»§a báº¡n táº¡i Ä‘Ã¢y, vÃ­ dá»¥: 'network.dbc'
    sniff_and_decode('network.dbc', 'vcan0')
