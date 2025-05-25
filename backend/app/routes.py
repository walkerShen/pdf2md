from flask import Blueprint, jsonify, request, current_app, send_file
import os
import uuid
from werkzeug.utils import secure_filename
from app.converter import pdf_to_markdown

main_bp = Blueprint('main', __name__)

# 创建临时文件存储目录
TEMP_UPLOAD_FOLDER = os.path.abspath('temp_uploads')
if not os.path.exists(TEMP_UPLOAD_FOLDER):
    os.makedirs(TEMP_UPLOAD_FOLDER)

# 文件大小限制 (50MB)
MAX_CONTENT_LENGTH = 50 * 1024 * 1024

@main_bp.route('/health', methods=['GET'])
def health_check():
    """健康检查端点，返回200 OK状态和简单的JSON响应"""
    return jsonify({
        "status": "ok",
        "message": "后端正在运行"
    }), 200

@main_bp.route('/api/upload_pdf', methods=['POST'])
def upload_pdf():
    """PDF上传和验证端点"""
    
    # 检查是否有文件在请求中
    if 'file' not in request.files:
        return jsonify({
            "status": "error",
            "message": "未找到文件。请确保使用'file'字段上传PDF文件。"
        }), 400
    
    file = request.files['file']
    
    # 检查文件名是否为空
    if file.filename == '':
        return jsonify({
            "status": "error",
            "message": "未选择文件。"
        }), 400
    
    # 检查文件类型
    if not file.filename.lower().endswith('.pdf') or file.mimetype != 'application/pdf':
        return jsonify({
            "status": "error",
            "message": "无效的文件类型。只接受PDF文件。"
        }), 415
    
    # 检查文件大小
    content_length = request.content_length
    if content_length and content_length > MAX_CONTENT_LENGTH:
        return jsonify({
            "status": "error",
            "message": f"文件大小超过50MB限制。"
        }), 413
    
    # 生成安全的文件名并保存文件
    filename = secure_filename(file.filename)
    temp_file_id = str(uuid.uuid4())
    temp_filepath = os.path.join(TEMP_UPLOAD_FOLDER, f"{temp_file_id}_{filename}")
    
    file.save(temp_filepath)
    
    return jsonify({
        "status": "success",
        "message": "PDF文件上传成功。",
        "file_id": temp_file_id,
        "original_filename": filename,
        "temp_filepath": temp_filepath
    }), 201

@main_bp.route('/api/convert_pdf_to_md', methods=['POST'])
def convert_pdf_to_md():
    """PDF到Markdown转换端点"""
    
    # 使用与upload_pdf相同的验证逻辑
    if 'file' not in request.files:
        return jsonify({
            "status": "error",
            "message": "未找到文件。请确保使用'file'字段上传PDF文件。"
        }), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({
            "status": "error",
            "message": "未选择文件。"
        }), 400
    
    if not file.filename.lower().endswith('.pdf') or file.mimetype != 'application/pdf':
        return jsonify({
            "status": "error",
            "message": "无效的文件类型。只接受PDF文件。"
        }), 415
    
    content_length = request.content_length
    if content_length and content_length > MAX_CONTENT_LENGTH:
        return jsonify({
            "status": "error",
            "message": f"文件大小超过50MB限制。"
        }), 413
    
    try:
        # 保存上传的文件到临时目录
        filename = secure_filename(file.filename)
        temp_file_id = str(uuid.uuid4())
        temp_filepath = os.path.join(TEMP_UPLOAD_FOLDER, f"{temp_file_id}_{filename}")
        
        # 确保目录存在
        os.makedirs(TEMP_UPLOAD_FOLDER, exist_ok=True)
        
        print(f"保存文件到: {temp_filepath}")
        print(f"TEMP_UPLOAD_FOLDER: {TEMP_UPLOAD_FOLDER}")
        print(f"当前工作目录: {os.getcwd()}")
        
        file.save(temp_filepath)
        
        # 验证文件是否成功保存
        if not os.path.exists(temp_filepath):
            raise FileNotFoundError(f"文件保存失败: {temp_filepath}")
        
        print(f"文件保存成功，大小: {os.path.getsize(temp_filepath)} bytes")
        
        # 转换PDF到Markdown（包含图片提取）
        # 使用绝对路径确保路径正确
        abs_temp_filepath = os.path.abspath(temp_filepath)
        print(f"转换文件绝对路径: {abs_temp_filepath}")
        conversion_result = pdf_to_markdown(abs_temp_filepath)
        
        # 转换完成后删除临时PDF文件（但保留提取的图片）
        if os.path.exists(abs_temp_filepath):
            os.remove(abs_temp_filepath)
            print(f"已删除临时文件: {abs_temp_filepath}")
        
        # 检查转换结果格式
        if isinstance(conversion_result, dict):
            markdown_content = conversion_result.get("markdown_content", "")
            extracted_images = conversion_result.get("images", [])
            
            return jsonify({
                "status": "success",
                "message": "PDF成功转换为Markdown。",
                "filename": filename,
                "markdown_content": markdown_content,
                "images": extracted_images,
                "image_count": len(extracted_images)
            }), 200
        else:
            # 兼容旧格式（如果返回的是字符串）
            return jsonify({
                "status": "success",
                "message": "PDF成功转换为Markdown。",
                "filename": filename,
                "markdown_content": conversion_result,
                "images": [],
                "image_count": 0
            }), 200
        
    except Exception as e:
        # 确保即使在出错时也删除临时文件
        if 'abs_temp_filepath' in locals() and os.path.exists(abs_temp_filepath):
            os.remove(abs_temp_filepath)
            print(f"错误时删除临时文件: {abs_temp_filepath}")
        elif 'temp_filepath' in locals() and os.path.exists(temp_filepath):
            os.remove(temp_filepath)
            print(f"错误时删除临时文件: {temp_filepath}")
        
        print(f"转换错误详情: {str(e)}")
        import traceback
        traceback.print_exc()
        
        return jsonify({
            "status": "error",
            "message": f"转换过程中出错：{str(e)}"
        }), 500

@main_bp.route('/api/images/<path:filename>', methods=['GET'])
def serve_image(filename):
    """提供提取的图片文件"""
    try:
        # 查找图片文件
        for root, dirs, files in os.walk(TEMP_UPLOAD_FOLDER):
            if filename in files:
                file_path = os.path.join(root, filename)
                return send_file(file_path, as_attachment=False)
        
        return jsonify({
            "status": "error",
            "message": "图片文件未找到"
        }), 404
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"获取图片时出错：{str(e)}"
        }), 500 