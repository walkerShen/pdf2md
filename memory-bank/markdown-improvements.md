# Markdown 格式改进说明

## 改进概述

针对用户反馈的"生成 markdown 后的格式不正确"和"PDF 中的图片没有生成在 markdown 中"问题，我们对 PDF 转 Markdown 的转换逻辑进行了全面优化。

## 主要改进内容

### 1. 从简单文本块到智能格式分析

**之前的方法**:

- 仅提取 PDF 的文本块
- 简单地用双换行符连接所有文本
- 没有格式识别和处理

**改进后的方法**:

- 提取文本的同时获取格式信息（字体大小、样式、位置等）
- 分析字体特征来识别文档结构
- 智能处理不同类型的文本元素

### 2. 智能标题识别

**功能**:

- 基于字体大小自动识别标题层级
- 动态计算标题阈值（相对于平均字体大小）
- 生成规范的 Markdown 标题格式

**实现逻辑**:

```python
# 计算字体大小阈值
avg_font_size = sum(font_sizes) / len(font_sizes)
title_threshold = avg_font_size * 1.2
subtitle_threshold = avg_font_size * 1.1

# 根据字体大小生成标题
if font_size >= title_threshold * 1.3:
    return f"# {text}"        # H1
elif font_size >= title_threshold * 1.1:
    return f"## {text}"       # H2
else:
    return f"### {text}"      # H3
```

### 3. 文本格式保持

**支持的格式**:

- **粗体文本**: 检测字体标志位，转换为 `**粗体**`
- _斜体文本_: 检测斜体标志，转换为 `*斜体*`
- 普通文本: 保持原样

**实现方式**:

```python
# 检测粗体 (font_flags & 16)
if font_flags & 16:
    return f"**{text}**"

# 检测斜体 (font_flags & 2)
if font_flags & 2:
    return f"*{text}*"
```

### 4. 列表识别和转换

**支持的列表类型**:

- 数字列表: `1. 项目一`
- 项目符号列表: `• 项目` → `- 项目`
- 多种符号: `•`, `·`, `▪`, `▫`, `‣`, `⁃`

**转换示例**:

```
PDF中的: • 第一项
转换为:   - 第一项

PDF中的: 1. 第一项
保持为:   1. 第一项
```

### 5. 智能段落分割

**分割依据**:

- 基于文本的 Y 坐标变化
- 考虑字体大小的行间距
- 智能判断是否为新段落

**算法**:

```python
# 检测换行（基于y坐标变化）
y_diff = abs(current_y - last_y)
if y_diff > font_size * 0.8:  # 行间距大于字体大小的80%
    line_break = True
```

### 6. 图片提取和处理 (新增)

**功能特性**:

- 自动提取 PDF 中的所有图片
- 保存为 PNG 格式文件
- 在 Markdown 中生成图片引用
- 提供图片信息（尺寸、页面位置等）

**实现逻辑**:

```python
# 提取图片
def extract_images_from_page(page, page_num, images_dir, base_filename):
    images = []
    image_list = page.get_images()

    for img_index, img in enumerate(image_list):
        # 获取图片数据
        xref = img[0]
        pix = fitz.Pixmap(page.parent, xref)

        # 生成唯一文件名并保存
        img_filename = f"{base_filename}_page{page_num + 1}_img{img_index + 1}.png"
        pix.save(img_path)

        # 记录图片信息
        images.append({
            "filename": img_filename,
            "page": page_num + 1,
            "width": pix.width,
            "height": pix.height
        })
```

**图片处理特性**:

- **自动命名**: 基于原文件名和页面位置生成唯一文件名
- **格式转换**: 统一转换为 PNG 格式，确保兼容性
- **元数据保存**: 记录图片尺寸、页面位置等信息
- **API 访问**: 通过专用 API 端点提供图片文件访问
- **Markdown 集成**: 自动在相应位置插入图片引用

### 7. 后处理优化

**优化内容**:

- 列表项前后添加适当空行
- 移除多余的空行
- 确保文档结构清晰
- 优化整体可读性
- 按页面组织图片插入位置

## 转换效果对比

### 改进前

```
标题文本 正文内容继续 • 列表项一 • 列表项二 另一段文字
```

### 改进后

```markdown
# 标题文本

正文内容继续

- 列表项一
- 列表项二

![图片 1](document_page1_img1.png)
_第 1 页 - 图片 1 (800x600)_

另一段文字
```

## 技术实现细节

### 1. 格式信息提取

```python
# 获取文本字典，包含格式信息
text_dict = page.get_text("dict")

# 提取每个文本片段的详细信息
for span in line["spans"]:
    text_elements.append({
        "text": span["text"],
        "font_size": span["size"],
        "font_flags": span["flags"],
        "bbox": span["bbox"],
        "page": page_num + 1
    })
```

### 2. 图片提取流程

```python
# 创建图片存储目录
base_filename = os.path.splitext(os.path.basename(pdf_path))[0]
images_dir = os.path.join(os.path.dirname(pdf_path), f"{base_filename}_images")

# 按页面提取图片
for page_num in range(doc.page_count):
    page = doc[page_num]
    page_images = extract_images_from_page(page, page_num, images_dir, base_filename)
    extracted_images.extend(page_images)
```

### 3. API 端点设计

**新增 API 端点**:

- `GET /api/images/<filename>`: 提供图片文件访问
- `POST /api/convert_pdf_to_md`: 增强返回格式，包含图片信息

**返回格式**:

```json
{
  "status": "success",
  "markdown_content": "转换后的Markdown内容...",
  "images": [
    {
      "filename": "document_page1_img1.png",
      "page": 1,
      "width": 800,
      "height": 600
    }
  ],
  "image_count": 1
}
```

### 4. 前端图片处理

**功能增强**:

- 显示提取的图片信息列表
- 自动处理图片链接，指向 API 端点
- 在 Markdown 预览中正确显示图片

**链接处理**:

```javascript
// 将相对路径转换为API端点
processImageLinks(markdownText) {
  return markdownText.replace(
    /!\[([^\]]*)\]\(([^)]+)\)/g,
    (match, altText, imagePath) => {
      const filename = imagePath.split('/').pop();
      return `![${altText}](http://localhost:5000/api/images/${filename})`;
    }
  );
}
```

### 5. 错误处理

- 保持原有的错误处理机制
- 添加图片提取的异常处理
- 确保在图片处理失败时仍能生成文本内容
- 跳过无法处理的图片格式（如 CMYK）

## 用户体验改进

### 1. 更好的可读性

- 清晰的标题层级
- 合理的段落分割
- 规范的列表格式
- **新增**: 图片在适当位置的插入

### 2. 更准确的格式保持

- 保留原文档的视觉层次
- 维持重要文本的强调效果
- 转换后的文档结构更接近原文
- **新增**: 保留原文档中的图片内容

### 3. 更标准的 Markdown

- 符合 Markdown 规范
- 兼容各种 Markdown 编辑器
- 便于进一步编辑和处理
- **新增**: 标准的图片引用格式

### 4. 图片处理体验 (新增)

- **可视化反馈**: 显示提取的图片数量和信息
- **智能命名**: 基于页面和位置的有意义文件名
- **即时访问**: 通过 API 端点直接访问图片
- **完整信息**: 提供图片尺寸和位置信息

## 依赖更新

**新增依赖**:

- `Pillow==8.3.2`: 图片处理库

**更新的文件**:

- `backend/requirements.txt`: 添加 Pillow 依赖
- `backend/app/converter.py`: 图片提取逻辑
- `backend/app/routes.py`: 图片 API 端点
- `frontend/app.js`: 图片信息处理
- `frontend/index.html`: 图片信息显示
- `frontend/styles.css`: 图片信息样式

## 未来扩展方向

1. **图片处理增强**:

   - OCR 文字识别
   - 图片压缩优化
   - 多种格式支持
   - 图片标题自动生成

2. **表格识别**: 检测和转换 PDF 中的表格
3. **脚注处理**: 识别和转换脚注
4. **代码块**: 识别代码片段并格式化
5. **链接提取**: 保留 PDF 中的超链接

这些改进显著提升了 PDF 转 Markdown 的质量，特别是解决了图片丢失的问题，使生成的文档更加完整、规范、可读和实用。
