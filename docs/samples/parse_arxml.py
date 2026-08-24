import xml.etree.ElementTree as ET
import os

# Namespace of AUTOSAR R4.0
namespace = {'ar': 'http://autosar.org/schema/r4.0'}

def parse_arxml(file_path):
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return

    print(f"--- Parsing ARXML: {file_path} ---")
    tree = ET.parse(file_path)
    root = tree.getroot()

    # Find all Application Software Component Types
    swc_types = root.findall('.//ar:APPLICATION-SW-COMPONENT-TYPE', namespace)
    for swc in swc_types:
        short_name_elem = swc.find('ar:SHORT-NAME', namespace)
        swc_name = short_name_elem.text if short_name_elem is not None else "Unknown"
        print(f"\n[SWC]: {swc_name}")
        
        # Ports
        print("  Ports:")
        p_ports = swc.findall('.//ar:P-PORT-PROTOTYPE', namespace)
        for p in p_ports:
            p_name = p.find('ar:SHORT-NAME', namespace).text
            print(f"    - Provide Port: {p_name}")
            
        r_ports = swc.findall('.//ar:R-PORT-PROTOTYPE', namespace)
        for r in r_ports:
            r_name = r.find('ar:SHORT-NAME', namespace).text
            print(f"    - Require Port: {r_name}")

        # Runnables
        print("  Runnables:")
        runnables = swc.findall('.//ar:RUNNABLE-ENTITY', namespace)
        for r in runnables:
            r_name = r.find('ar:SHORT-NAME', namespace).text
            symbol = r.find('ar:SYMBOL', namespace).text
            print(f"    - {r_name} (Symbol: {symbol})")
            
    print("-" * 40 + "\n")

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    system_arxml = os.path.join(current_dir, 'System_Sample.arxml')
    bms_arxml = os.path.join(current_dir, 'SWCD_BMS_Sample.arxml')
    
    parse_arxml(system_arxml)
    parse_arxml(bms_arxml)
