#!/usr/bin/env python3
"""
调试路径和文件系统问题
"""

import os
import sys

def debug_paths():
    """调试路径问题"""
    print("=== 路径调试信息 ===")
    
    # 当前工作目录
    cwd = os.getcwd()
    print(f"当前工作目录: {cwd}")
    
    # 脚本所在目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    print(f"脚本所在目录: {script_dir}")
    
    # temp_uploads目录
    temp_uploads_relative = 'temp_uploads'
    temp_uploads_absolute = os.path.abspath(temp_uploads_relative)
    
    print(f"相对路径 temp_uploads: {temp_uploads_relative}")
    print(f"绝对路径 temp_uploads: {temp_uploads_absolute}")
    print(f"相对路径是否存在: {os.path.exists(temp_uploads_relative)}")
    print(f"绝对路径是否存在: {os.path.exists(temp_uploads_absolute)}")
    
    # 创建目录测试
    try:
        os.makedirs(temp_uploads_absolute, exist_ok=True)
        print(f"成功创建/确认目录: {temp_uploads_absolute}")
    except Exception as e:
        print(f"创建目录失败: {e}")
    
    # 列出目录内容
    if os.path.exists(temp_uploads_absolute):
        files = os.listdir(temp_uploads_absolute)
        print(f"目录内容 ({len(files)} 个文件):")
        for file in files[:10]:  # 只显示前10个文件
            file_path = os.path.join(temp_uploads_absolute, file)
            size = os.path.getsize(file_path) if os.path.isfile(file_path) else "目录"
            print(f"  - {file} ({size})")
        if len(files) > 10:
            print(f"  ... 还有 {len(files) - 10} 个文件")
    
    # 测试文件路径格式
    test_filename = "test_file.pdf"
    test_path_join = os.path.join(temp_uploads_absolute, test_filename)
    test_path_manual = temp_uploads_absolute + os.sep + test_filename
    
    print(f"\n=== 路径格式测试 ===")
    print(f"os.path.join: {test_path_join}")
    print(f"手动拼接: {test_path_manual}")
    print(f"路径分隔符: '{os.sep}'")
    
    # 系统信息
    print(f"\n=== 系统信息 ===")
    print(f"操作系统: {os.name}")
    print(f"平台: {sys.platform}")
    print(f"Python版本: {sys.version}")

if __name__ == "__main__":
    debug_paths() 