import fitz  # PyMuPDF
import re
import os
import uuid
from PIL import Image
import io

def pdf_to_markdown(pdf_path):
    """
    将PDF文件转换为格式化的Markdown文本，包含图片提取
    
    参数:
        pdf_path (str): PDF文件的路径
        
    返回:
        dict: 包含markdown内容和图片信息的字典
    """
    try:
        # 验证文件路径
        print(f"尝试打开PDF文件: {pdf_path}")
        print(f"文件是否存在: {os.path.exists(pdf_path)}")
        print(f"当前工作目录: {os.getcwd()}")
        
        if not os.path.exists(pdf_path):
            return {
                "markdown_content": f"文件不存在: {pdf_path}",
                "images": []
            }
        
        # 打开PDF文件
        doc = fitz.open(pdf_path)
        
        if doc.page_count == 0:
            return {
                "markdown_content": "未找到内容。PDF文件为空。",
                "images": []
            }
        
        # 创建图片存储目录
        base_filename = os.path.splitext(os.path.basename(pdf_path))[0]
        images_dir = os.path.join(os.path.dirname(pdf_path), f"{base_filename}_images")
        if not os.path.exists(images_dir):
            os.makedirs(images_dir)
        
        # 提取文本块和格式信息
        text_elements = []
        extracted_images = []
        
        for page_num in range(doc.page_count):
            page = doc[page_num]
            
            # 提取图片
            page_images = extract_images_from_page(page, page_num, images_dir, base_filename)
            extracted_images.extend(page_images)
            
            # 获取文本字典，包含格式信息
            text_dict = page.get_text("dict")
            
            # 处理每个文本块
            for block in text_dict["blocks"]:
                if "lines" in block:  # 文本块
                    for line in block["lines"]:
                        for span in line["spans"]:
                            if span["text"].strip():
                                text_elements.append({
                                    "text": span["text"],
                                    "font_size": span["size"],
                                    "font_flags": span["flags"],
                                    "bbox": span["bbox"],
                                    "page": page_num + 1
                                })
        
        # 关闭文档
        doc.close()
        
        if not text_elements and not extracted_images:
            return {
                "markdown_content": "未找到文本或图片内容。",
                "images": []
            }
        
        # 处理文本元素，转换为Markdown
        markdown_text = convert_elements_to_markdown(text_elements, extracted_images)
        
        return {
            "markdown_content": markdown_text,
            "images": extracted_images
        }
    
    except Exception as e:
        # 记录错误并返回错误消息
        error_msg = f"转换过程中出错: {str(e)}"
        print(error_msg)
        return {
            "markdown_content": error_msg,
            "images": []
        }

def extract_images_from_page(page, page_num, images_dir, base_filename):
    """
    从PDF页面提取图片
    
    参数:
        page: PDF页面对象
        page_num: 页面编号
        images_dir: 图片保存目录
        base_filename: 基础文件名
        
    返回:
        list: 提取的图片信息列表
    """
    images = []
    image_list = page.get_images()
    
    for img_index, img in enumerate(image_list):
        try:
            # 获取图片数据
            xref = img[0]
            pix = fitz.Pixmap(page.parent, xref)
            
            # 跳过CMYK图片（转换复杂）
            if pix.n - pix.alpha < 4:
                # 生成唯一的图片文件名
                img_filename = f"{base_filename}_page{page_num + 1}_img{img_index + 1}.png"
                img_path = os.path.join(images_dir, img_filename)
                
                # 保存图片
                if pix.alpha:
                    pix = fitz.Pixmap(fitz.csRGB, pix)
                
                pix.save(img_path)
                
                # 记录图片信息
                images.append({
                    "filename": img_filename,
                    "path": img_path,
                    "page": page_num + 1,
                    "index": img_index + 1,
                    "width": pix.width,
                    "height": pix.height
                })
                
            pix = None  # 释放内存
            
        except Exception as e:
            print(f"提取第{page_num + 1}页第{img_index + 1}张图片时出错: {str(e)}")
            continue
    
    return images

def convert_elements_to_markdown(text_elements, extracted_images):
    """
    将文本元素转换为格式化的Markdown，包含图片引用
    
    参数:
        text_elements (list): 包含格式信息的文本元素列表
        extracted_images (list): 提取的图片信息列表
        
    返回:
        str: 格式化的Markdown文本
    """
    if not text_elements and not extracted_images:
        return ""
    
    # 如果只有图片没有文本
    if not text_elements:
        markdown_lines = []
        for img in extracted_images:
            markdown_lines.append(f"![图片 {img['index']}]({img['filename']})")
            markdown_lines.append(f"*第{img['page']}页 - 图片{img['index']} ({img['width']}x{img['height']})*")
        return "\n\n".join(markdown_lines)
    
    # 分析字体大小，确定标题级别
    font_sizes = [elem["font_size"] for elem in text_elements]
    avg_font_size = sum(font_sizes) / len(font_sizes)
    max_font_size = max(font_sizes)
    
    # 定义标题阈值
    title_threshold = avg_font_size * 1.2
    subtitle_threshold = avg_font_size * 1.1
    
    markdown_lines = []
    current_paragraph = []
    last_y = None
    current_page = 1
    
    # 按页面组织图片
    images_by_page = {}
    for img in extracted_images:
        page = img['page']
        if page not in images_by_page:
            images_by_page[page] = []
        images_by_page[page].append(img)
    
    for i, elem in enumerate(text_elements):
        text = elem["text"].strip()
        font_size = elem["font_size"]
        font_flags = elem["font_flags"]
        bbox = elem["bbox"]
        page = elem["page"]
        
        if not text:
            continue
        
        # 检查是否切换到新页面，如果是则插入该页面的图片
        if page != current_page:
            # 完成当前段落
            if current_paragraph:
                paragraph_text = " ".join(current_paragraph).strip()
                if paragraph_text:
                    markdown_lines.append(paragraph_text)
                current_paragraph = []
            
            # 插入前一页的图片（如果有）
            if current_page in images_by_page:
                markdown_lines.append("")  # 添加空行
                for img in images_by_page[current_page]:
                    markdown_lines.append(f"![图片 {img['index']}]({img['filename']})")
                    markdown_lines.append(f"*第{img['page']}页 - 图片{img['index']} ({img['width']}x{img['height']})*")
                markdown_lines.append("")  # 添加空行
            
            current_page = page
            last_y = None  # 重置Y坐标
        
        # 检测换行（基于y坐标变化）
        current_y = bbox[1]  # y0坐标
        line_break = False
        
        if last_y is not None:
            y_diff = abs(current_y - last_y)
            if y_diff > font_size * 0.8:  # 行间距大于字体大小的80%
                line_break = True
        
        # 处理当前段落
        if line_break and current_paragraph:
            # 完成当前段落
            paragraph_text = " ".join(current_paragraph).strip()
            if paragraph_text:
                markdown_lines.append(paragraph_text)
            current_paragraph = []
        
        # 判断文本类型并格式化
        formatted_text = format_text_element(text, font_size, font_flags, 
                                           title_threshold, subtitle_threshold, avg_font_size)
        
        # 如果是标题，直接添加到结果中
        if formatted_text.startswith('#'):
            if current_paragraph:
                paragraph_text = " ".join(current_paragraph).strip()
                if paragraph_text:
                    markdown_lines.append(paragraph_text)
                current_paragraph = []
            markdown_lines.append(formatted_text)
        else:
            # 添加到当前段落
            current_paragraph.append(formatted_text)
        
        last_y = current_y
    
    # 处理最后一个段落
    if current_paragraph:
        paragraph_text = " ".join(current_paragraph).strip()
        if paragraph_text:
            markdown_lines.append(paragraph_text)
    
    # 插入最后一页的图片（如果有）
    if current_page in images_by_page:
        markdown_lines.append("")  # 添加空行
        for img in images_by_page[current_page]:
            markdown_lines.append(f"![图片 {img['index']}]({img['filename']})")
            markdown_lines.append(f"*第{img['page']}页 - 图片{img['index']} ({img['width']}x{img['height']})*")
    
    # 后处理：清理和优化
    processed_lines = post_process_markdown(markdown_lines)
    
    return "\n\n".join(processed_lines)

def format_text_element(text, font_size, font_flags, title_threshold, subtitle_threshold, avg_font_size):
    """
    根据字体信息格式化文本元素
    """
    # 清理文本
    text = re.sub(r'\s+', ' ', text.strip())
    
    # 检测标题
    if font_size >= title_threshold:
        if font_size >= title_threshold * 1.3:
            return f"# {text}"
        elif font_size >= title_threshold * 1.1:
            return f"## {text}"
        else:
            return f"### {text}"
    elif font_size >= subtitle_threshold:
        return f"#### {text}"
    
    # 检测粗体 (font_flags & 16 表示粗体)
    if font_flags & 16:
        return f"**{text}**"
    
    # 检测斜体 (font_flags & 2 表示斜体)
    if font_flags & 2:
        return f"*{text}*"
    
    # 检测列表项
    if re.match(r'^[\d]+\.', text):  # 数字列表
        return text
    elif re.match(r'^[•·▪▫‣⁃]\s*', text):  # 项目符号列表
        return re.sub(r'^[•·▪▫‣⁃]\s*', '- ', text)
    elif re.match(r'^[-*+]\s+', text):  # 已经是Markdown列表格式
        return text
    
    return text

def post_process_markdown(lines):
    """
    后处理Markdown文本，优化格式
    """
    processed = []
    
    for i, line in enumerate(lines):
        if not line.strip():
            continue
        
        # 处理列表项
        if re.match(r'^[\d]+\.', line) or line.startswith('- '):
            # 确保列表项前后有适当的空行
            if processed and not processed[-1].startswith(('- ', '1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.', '0.')):
                if not processed[-1].startswith('#'):
                    processed.append('')  # 在列表前添加空行
            processed.append(line)
        else:
            processed.append(line)
    
    # 移除多余的空行
    final_lines = []
    for line in processed:
        if line.strip() or (final_lines and final_lines[-1].strip()):
            final_lines.append(line)
    
    return final_lines 