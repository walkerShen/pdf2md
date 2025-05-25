# 本地图片下载功能说明

## 功能概述

为了提供更好的用户体验，我们添加了本地图片下载功能。用户现在可以将 PDF 中提取的图片下载到本地，并获得使用本地路径的 Markdown 文件，无需依赖服务器来访问图片。

## 主要特性

### 🖼️ 图片下载功能

1. **单个图片下载**: 点击每张图片旁的"下载"按钮
2. **批量下载**: 点击"下载所有图片"按钮一次性下载所有图片
3. **完整包下载**: 点击"下载完整包"按钮同时下载 Markdown 文件和所有图片
4. **下载状态跟踪**: 已下载的图片会显示"已下载"状态

### 📝 本地路径 Markdown

- Markdown 文件中的图片链接使用相对路径（如 `![图片](image.png)`）
- 无需服务器即可在本地查看完整文档
- 兼容所有 Markdown 编辑器和查看器

## 使用方法

### 基本流程

1. **上传 PDF 文件**

   - 选择包含图片的 PDF 文件
   - 点击"转换为 Markdown"

2. **查看提取结果**

   - 在"提取的图片"区域查看所有图片信息
   - 每张图片显示文件名、页面位置和尺寸

3. **下载图片**

   - **单个下载**: 点击图片旁的"下载"按钮
   - **批量下载**: 点击"下载所有图片"按钮
   - **完整包**: 点击"下载完整包"按钮

4. **整理文件**
   - 将下载的图片文件放在与 Markdown 文件相同的目录下
   - 确保图片文件名与 Markdown 中的引用一致

### 文件组织建议

```
my-document/
├── document.md          # Markdown文件
├── document_page1_img1.png
├── document_page2_img1.png
└── document_page3_img1.png
```

## 技术实现

### 前端实现

#### 1. 图片下载功能

```javascript
// 下载单个图片
async downloadImage(image) {
  try {
    const response = await fetch(`http://localhost:5000/api/images/${image.filename}`);
    const blob = await response.blob();
    const url = URL.createObjectURL(blob);

    const a = document.createElement("a");
    a.href = url;
    a.download = image.filename;
    a.click();

    URL.revokeObjectURL(url);
    return true;
  } catch (error) {
    console.error("下载失败:", error);
    return false;
  }
}
```

#### 2. 批量下载功能

```javascript
// 下载所有图片
async downloadAllImages() {
  for (const image of this.extractedImages) {
    await this.downloadImage(image);
    // 添加延迟避免浏览器阻止多个下载
    await new Promise(resolve => setTimeout(resolve, 100));
  }
}
```

#### 3. 本地路径处理

```javascript
// 将API端点转换为本地相对路径
processImageLinksForLocal(markdownText) {
  return markdownText.replace(
    /!\[([^\]]*)\]\(([^)]+)\)/g,
    (match, altText, imagePath) => {
      if (imagePath.includes('/api/images/')) {
        const filename = imagePath.split('/').pop();
        return `![${altText}](${filename})`;
      }
      return match;
    }
  );
}
```

### UI 组件

#### 1. 图片信息显示

```html
<div class="image-info">
  <div class="image-header">
    <h3>📷 提取的图片 ({{ imageCount }} 张)</h3>
    <button @click="downloadAllImages">下载所有图片</button>
  </div>

  <div class="image-list">
    <div v-for="image in extractedImages" class="image-item">
      <div class="image-info-left">
        <span class="image-name">{{ image.filename }}</span>
        <span class="image-details"
          >第{{ image.page }}页 - {{ image.width }}×{{ image.height }}</span
        >
      </div>
      <button
        @click="downloadImage(image)"
        :class="{ 'downloaded': isImageDownloaded(image.filename) }"
      >
        {{ isImageDownloaded(image.filename) ? '已下载' : '下载' }}
      </button>
    </div>
  </div>
</div>
```

#### 2. 下载操作按钮

```html
<div class="output-actions">
  <button @click="copyToClipboard">复制 Markdown</button>
  <button @click="downloadMarkdown">下载 .md 文件</button>
  <button @click="downloadCompletePackage">下载完整包</button>
</div>
```

## 用户体验优化

### 1. 状态反馈

- **下载进度**: 显示下载成功/失败状态
- **已下载标记**: 已下载的图片按钮变为灰色"已下载"状态
- **批量下载反馈**: 显示成功下载的图片数量

### 2. 错误处理

- **网络错误**: 显示具体的错误信息
- **文件访问错误**: 提示用户检查文件权限
- **部分失败**: 在批量下载时显示成功/失败统计

### 3. 用户指导

- **完整包下载**: 自动提示用户将图片放在同一目录
- **文件组织**: 提供文件组织的最佳实践建议
- **兼容性说明**: 说明本地路径的兼容性

## 浏览器兼容性

### 支持的功能

- **Blob 下载**: Chrome 14+, Firefox 20+, Safari 6+
- **多文件下载**: 现代浏览器支持，可能需要用户确认
- **URL.createObjectURL**: 广泛支持

### 注意事项

1. **下载限制**: 某些浏览器可能限制同时下载多个文件
2. **用户确认**: 批量下载可能需要用户确认允许多个下载
3. **文件路径**: 下载的文件通常保存在用户的默认下载目录

## 优势对比

### 本地访问 vs 服务器访问

| 特性         | 本地访问    | 服务器访问    |
| ------------ | ----------- | ------------- |
| **离线使用** | ✅ 完全离线 | ❌ 需要服务器 |
| **文件管理** | ✅ 用户控制 | ❌ 依赖服务器 |
| **传输速度** | ✅ 本地读取 | ❌ 网络传输   |
| **隐私保护** | ✅ 本地存储 | ❌ 服务器存储 |
| **兼容性**   | ✅ 通用格式 | ❌ 特定 API   |
| **分享便利** | ✅ 打包分享 | ❌ 需要服务器 |

## 最佳实践

### 1. 文件组织

```
project-folder/
├── README.md
├── document.md
├── images/
│   ├── document_page1_img1.png
│   ├── document_page2_img1.png
│   └── ...
└── assets/
    └── other-files...
```

### 2. Markdown 编写

```markdown
# 文档标题

正文内容...

![重要图表](document_page1_img1.png)

更多内容...
```

### 3. 版本控制

- 将图片文件加入版本控制
- 使用相对路径确保团队协作
- 考虑图片文件大小对仓库的影响

## 未来扩展

1. **图片压缩**: 自动压缩大尺寸图片
2. **格式选择**: 支持 JPEG、WebP 等格式选择
3. **批量重命名**: 提供图片重命名选项
4. **文件夹结构**: 自动创建图片子目录
5. **ZIP 打包**: 将 Markdown 和图片打包为 ZIP 文件

这个本地下载功能大大提升了用户体验，使 PDF 转 Markdown 的结果更加实用和便携。
