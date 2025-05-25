# PDF 转 Markdown 项目架构文档

## 系统概述

本项目是一个 Web 应用，用于将 PDF 文件转换为 Markdown 格式。系统采用前后端分离架构：

- 后端：基于 Flask 的 RESTful API 服务
- 前端：基于 Vue.js 3 的单页面应用

## 技术栈

- **后端**：Python + Flask + PyMuPDF
- **前端**：Vue.js 3 + 原生 CSS + Fetch API
- **API 通信**：HTTP REST API，JSON 数据格式

## 系统架构图

```
┌─────────────────┐    HTTP/JSON    ┌─────────────────┐
│                 │ ──────────────> │                 │
│   前端 (Vue.js) │                 │  后端 (Flask)   │
│                 │ <────────────── │                 │
└─────────────────┘                 └─────────────────┘
        │                                   │
        │                                   │
        v                                   v
┌─────────────────┐                 ┌─────────────────┐
│   浏览器存储     │                 │  临时文件存储    │
│   (Blob/File)   │                 │  (temp_uploads) │
└─────────────────┘                 └─────────────────┘
```

## 后端架构

### 目录结构

```
backend/
│
├── app/                  # 应用程序包
│   ├── __init__.py       # 应用初始化
│   ├── routes.py         # API路由和端点
│   └── converter.py      # PDF到Markdown转换逻辑
│
├── temp_uploads/         # 临时文件存储目录
├── run.py                # 应用入口
├── requirements.txt      # 项目依赖
└── README.md             # 项目文档
```

### 核心组件

#### 1. 应用初始化 (`app/__init__.py`)

- 创建和配置 Flask 应用实例
- 注册跨域资源共享(CORS)支持
- 注册蓝图和路由

#### 2. API 路由 (`app/routes.py`)

- 定义 API 端点和路由规则
- 实现请求处理和响应生成
- 管理临时文件存储
- 主要端点:
  - `/health` - 健康检查
  - `/api/upload_pdf` - PDF 上传和验证
  - `/api/convert_pdf_to_md` - PDF 转 Markdown

#### 3. 转换逻辑 (`app/converter.py`)

- 实现 PDF 文件解析和格式分析
- 实现智能文本提取和格式识别
- 实现高质量 Markdown 格式转换
- 主要函数:
  - `pdf_to_markdown()` - 转换入口点
  - `convert_elements_to_markdown()` - 文本元素转换为 Markdown
  - `format_text_element()` - 单个文本元素格式化
  - `post_process_markdown()` - Markdown 后处理优化

### 数据流

1. 客户端上传 PDF 文件到`/api/convert_pdf_to_md`端点
2. 后端验证文件类型和大小
3. 将文件临时保存到服务器
4. 使用 PyMuPDF 提取 PDF 文本内容和格式信息
5. 分析字体大小、样式等格式特征
6. 智能识别标题、段落、列表等结构
7. 将文本处理为规范的 Markdown 格式
8. 进行后处理优化（空行、列表格式等）
9. 返回转换后的 Markdown 内容给客户端
10. 删除临时 PDF 文件

### 安全考量

- 使用`secure_filename`防止路径遍历攻击
- 限制文件大小(50MB)防止拒绝服务攻击
- 使用 UUID 生成唯一文件名防止文件覆盖
- 处理完成后立即删除临时文件保护用户隐私

## 前端架构

### 目录结构

```
frontend/
│
├── index.html          # 主HTML文件
├── styles.css          # CSS样式文件
├── app.js              # Vue.js应用逻辑
└── README.md           # 项目文档
```

### 核心组件

#### 1. 主应用 (`index.html`)

- HTML5 语义化结构
- Vue.js 3 应用容器
- 响应式布局设计
- 组件化 UI 结构

#### 2. 样式系统 (`styles.css`)

- 现代化 CSS 设计
- 响应式布局(Grid + Flexbox)
- 渐变背景和卡片式设计
- 动画和过渡效果
- 移动设备适配

#### 3. 应用逻辑 (`app.js`)

- Vue.js 3 Composition API
- 响应式状态管理
- 文件处理和验证
- API 通信和错误处理
- 用户交互逻辑

### 功能模块

#### 1. 文件上传模块

- **文件选择**: 点击选择和拖拽上传
- **文件验证**: 类型检查(PDF)和大小限制(50MB)
- **状态管理**: 文件选择状态和 UI 反馈
- **错误处理**: 验证失败的用户提示

#### 2. 转换处理模块

- **API 通信**: 使用 Fetch API 与后端通信
- **状态管理**: 转换进度和加载状态
- **错误处理**: 网络错误和服务器错误处理
- **用户反馈**: 加载指示器和状态提示

#### 3. 结果展示模块

- **内容显示**: Markdown 文本的格式化显示
- **复制功能**: 使用 Clipboard API 复制到剪贴板
- **下载功能**: 生成 Blob 并触发浏览器下载
- **文件命名**: 基于原 PDF 文件名生成.md 文件名

#### 4. 用户界面模块

- **响应式设计**: 适配不同屏幕尺寸
- **视觉反馈**: 按钮状态、悬停效果、动画
- **错误提示**: 统一的错误消息显示和关闭
- **无障碍支持**: 语义化 HTML 和键盘导航

### 状态管理

```javascript
data() {
    return {
        selectedFile: null,        // 当前选择的文件
        markdownContent: '',       // 转换后的Markdown内容
        isConverting: false,       // 转换状态标识
        isDragOver: false,         // 拖拽悬停状态
        errorMessage: '',          // 错误消息
        copyButtonText: '复制 Markdown',  // 复制按钮文本
        originalFilename: ''       // 原始文件名
    }
}
```

## API 规范

### 健康检查

- **端点**: `/health`
- **方法**: GET
- **响应**:
  ```json
  {
    "status": "ok",
    "message": "后端正在运行"
  }
  ```

### PDF 上传

- **端点**: `/api/upload_pdf`
- **方法**: POST
- **参数**: multipart/form-data 表单，包含 file 字段
- **响应**:
  ```json
  {
    "status": "success",
    "message": "PDF文件上传成功。",
    "file_id": "<uuid>",
    "original_filename": "<filename>.pdf"
  }
  ```

### PDF 到 Markdown 转换

- **端点**: `/api/convert_pdf_to_md`
- **方法**: POST
- **参数**: multipart/form-data 表单，包含 file 字段
- **响应**:
  ```json
  {
    "status": "success",
    "message": "PDF成功转换为Markdown。",
    "filename": "<filename>.pdf",
    "markdown_content": "# 转换后的Markdown内容..."
  }
  ```

## 部署架构

### 开发环境

```
开发者机器
├── 后端服务 (localhost:5000)
└── 前端应用 (file:// 或本地服务器)
```

### 生产环境建议

```
云服务器
├── 反向代理 (Nginx)
├── 后端服务 (Gunicorn + Flask)
├── 前端静态文件
└── SSL证书 (HTTPS)
```

## 性能考量

### 后端性能

- **文件处理**: 使用流式处理大文件
- **内存管理**: 及时释放 PDF 文档对象
- **并发处理**: Flask 的多线程支持
- **文件清理**: 自动删除临时文件

### 前端性能

- **资源加载**: CDN 加载 Vue.js 库
- **文件处理**: 客户端文件验证减少服务器负载
- **用户体验**: 异步处理和进度反馈
- **缓存策略**: 浏览器缓存静态资源

## 安全架构

### 后端安全

- **文件验证**: 严格的文件类型和大小检查
- **路径安全**: 使用 secure_filename 防止路径遍历
- **临时文件**: UUID 命名和自动清理
- **CORS 配置**: 限制跨域访问

### 前端安全

- **输入验证**: 客户端文件类型和大小验证
- **XSS 防护**: 避免直接插入用户内容
- **HTTPS**: 生产环境使用加密传输
- **CSP**: 内容安全策略防止脚本注入

## 未来扩展计划

1. 改进 Markdown 转换:

   - 支持标题识别
   - 支持列表识别
   - 支持表格转换
   - 支持图像提取和引用

2. 性能优化:

   - 添加缓存机制
   - 实现异步处理大型文件
   - 使用 WebWorkers 处理文件

3. 功能增强:

   - 添加 OCR 功能支持图像 PDF
   - 支持批量处理
   - 提供自定义转换选项
   - 实现用户账户系统

4. 部署优化:
   - Docker 容器化
   - 微服务架构
   - CDN 部署
   - 负载均衡
