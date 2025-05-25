#!/usr/bin/env python3
"""
测试文件上传和路径处理
"""

import os
import tempfile
from werkzeug.utils import secure_filename
import uuid

def test_path_handling():
    """测试路径处理"""
    print("=== 路径处理测试 ===")
    
    # 模拟当前的路径处理逻辑
    TEMP_UPLOAD_FOLDER = os.path.abspath('temp_uploads')
    print(f"TEMP_UPLOAD_FOLDER: {TEMP_UPLOAD_FOLDER}")
    
    # 确保目录存在
    os.makedirs(TEMP_UPLOAD_FOLDER, exist_ok=True)
    print(f"目录是否存在: {os.path.exists(TEMP_UPLOAD_FOLDER)}")
    
    # 模拟文件名处理
    original_filename = "2017-2024.pdf"
    filename = secure_filename(original_filename)
    temp_file_id = str(uuid.uuid4())
    temp_filepath = os.path.join(TEMP_UPLOAD_FOLDER, f"{temp_file_id}_{filename}")
    
    print(f"原始文件名: {original_filename}")
    print(f"安全文件名: {filename}")
    print(f"临时文件ID: {temp_file_id}")
    print(f"临时文件路径: {temp_filepath}")
    print(f"绝对路径: {os.path.abspath(temp_filepath)}")
    
    # 创建一个测试文件
    try:
        with open(temp_filepath, 'w') as f:
            f.write("测试内容")
        print(f"测试文件创建成功: {temp_filepath}")
        print(f"文件是否存在: {os.path.exists(temp_filepath)}")
        print(f"文件大小: {os.path.getsize(temp_filepath)} bytes")
        
        # 清理测试文件
        os.remove(temp_filepath)
        print("测试文件已删除")
        
    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()

def test_current_directory():
    """测试当前目录"""
    print("\n=== 当前目录测试 ===")
    print(f"当前工作目录: {os.getcwd()}")
    print(f"脚本所在目录: {os.path.dirname(os.path.abspath(__file__))}")
    
    # 列出当前目录内容
    try:
        files = os.listdir('.')
        print(f"当前目录文件数量: {len(files)}")
        for file in files[:5]:
            print(f"  - {file}")
        if len(files) > 5:
            print(f"  ... 还有 {len(files) - 5} 个文件")
    except Exception as e:
        print(f"列出目录失败: {e}")

if __name__ == "__main__":
    test_current_directory()
    test_path_handling() 