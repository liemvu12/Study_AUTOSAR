#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
ARXML Tree View Compatibility Converter for Study_AUTOSAR
Chức năng: Chuyển đổi các file ARXML định dạng rút gọn (dùng Name="...")
           thành định dạng chuẩn có thẻ <SHORT-NAME>...</SHORT-NAME>
           giúp hiển thị trọn vẹn 100% trên extension "ARXML Tree View" (VS Code).
=============================================================================
Cách sử dụng:
  1. Tự động chuyển đổi toàn bộ target build:
     python tools/convert_arxml_tree.py

  2. Chuyển đổi một file cụ thể:
     python tools/convert_arxml_tree.py <đường_dẫn_file.arxml> [file_đích.arxml]
=============================================================================
"""

import sys
import os
import re
import xml.etree.ElementTree as ET

# Đảm bảo in tiếng Việt trên console Windows không bị lỗi font CP1252
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

def clean_preprocessor_directives(text):
    """Lọc bỏ các directive C-Preprocessor (#ifdef, #ifndef, #else, #endif) nếu gặp file template thô."""
    lines = text.splitlines()
    output_lines = []
    skip = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('#ifdef USE_SMP'):
            skip = True  # Bỏ nhánh SMP để giữ CPU_CORE_NUMBER=1
            continue
        elif stripped.startswith('#else') and skip:
            skip = False
            continue
        elif stripped.startswith('#endif') and skip:
            skip = False
            continue
        elif stripped.startswith('#'):
            # Bỏ qua các chỉ thị #ifdef khác, giữ code bên trong
            continue
        if not skip:
            output_lines.append(line)
    return '\n'.join(output_lines)

def convert_arxml(input_path, output_path=None):
    if not os.path.isfile(input_path):
        print(f"[ERROR] Không tìm thấy file: {input_path}")
        return False

    if output_path is None:
        base, ext = os.path.splitext(input_path)
        output_path = f"{base}_tree{ext}"

    print(f"[*] Đang chuyển đổi: {input_path} -> {output_path}")

    with open(input_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    # Nếu file chứa #ifdef, lọc trước khi parse XML
    if '#ifdef' in content or '#ifndef' in content:
        print("    [Notice] Phát hiện macro #ifdef, đang tiền xử lý...")
        content = clean_preprocessor_directives(content)

    try:
        root = ET.fromstring(content)
    except Exception as e:
        print(f"[ERROR] Không thể phân tích cú pháp XML: {e}")
        return False

    def add_short_names(elem):
        # Nếu element có thuộc tính Name, tạo thẻ <SHORT-NAME>
        name = elem.get('Name')
        if name:
            sn = ET.Element('SHORT-NAME')
            sn.text = str(name)
            elem.insert(0, sn)
        else:
            # Đối với container cha không có Name (ví dụ <OS>, <TaskList>, <Can>), dùng tên thẻ làm SHORT-NAME
            if elem != root:
                sn = ET.Element('SHORT-NAME')
                sn.text = str(elem.tag)
                elem.insert(0, sn)

        for child in list(elem):
            if child.tag != 'SHORT-NAME':
                add_short_names(child)

    add_short_names(root)

    # Format thụt dòng (indentation) đẹp mắt
    try:
        ET.indent(root, space="  ", level=0)
    except AttributeError:
        pass  # Python < 3.9 không có ET.indent

    tree = ET.ElementTree(root)
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    tree.write(output_path, encoding='utf-8', xml_declaration=True)
    print(f"[SUCCESS] Đã tạo thành công: {output_path}")
    return True

def auto_convert_build_targets(project_root):
    """Tìm và chuyển đổi tất cả file autosar.arxml trong as/build/nt/."""
    build_dir = os.path.join(project_root, 'as', 'build', 'nt')
    if not os.path.isdir(build_dir):
        print(f"[INFO] Thư mục build chưa tồn tại: {build_dir}")
        return

    count = 0
    for root, dirs, files in os.walk(build_dir):
        for f in files:
            if f == 'autosar.arxml':
                input_file = os.path.join(root, f)
                output_file = os.path.join(root, 'autosar_tree.arxml')
                if convert_arxml(input_file, output_file):
                    count += 1

    print(f"\n[DONE] Đã chuyển đổi tự động {count} file autosar.arxml trong thư mục build!")

if __name__ == '__main__':
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    if len(sys.argv) == 1:
        # Chế độ tự động
        print("=== TỰ ĐỘNG CHUYỂN ĐỔI TOÀN BỘ FILE BUILD AUTOSAR SANG ĐỊNH DẠNG TREE VIEW ===")
        auto_convert_build_targets(project_root)
        # Đồng thời tạo bản tree cho file template nguồn nếu cần tra cứu
        common_arxml = os.path.join(project_root, 'as', 'com', 'as.application', 'common', 'autosar.arxml')
        if os.path.isfile(common_arxml):
            common_out = os.path.join(project_root, 'as', 'com', 'as.application', 'common', 'autosar_tree.arxml')
            convert_arxml(common_arxml, common_out)
    elif len(sys.argv) == 2:
        convert_arxml(sys.argv[1])
    elif len(sys.argv) >= 3:
        convert_arxml(sys.argv[1], sys.argv[2])
