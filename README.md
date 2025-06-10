# PDF 转 Markdown 转换器

一个现代化的 Web 应用，用于将 PDF 文件快速转换为 Markdown 格式。

## 🌟 项目特性

- 📄 **智能转换**: 使用 PyMuPDF 库精确提取 PDF 文本内容
- 📝 **多格式输出**: 支持转换为 Markdown 和 Word 文档格式
- 🎨 **现代 UI**: 基于 Vue.js 3 的响应式用户界面
- 🖱️ **拖拽上传**: 支持拖拽和点击两种文件上传方式
- 📋 **一键复制**: 快速复制转换后的 Markdown 内容
- 💾 **文件下载**: 下载转换后的.md 或 .docx 文件
- 🖼️ **图片保留**: 自动提取并保留 PDF 中的图片
- 🔒 **安全可靠**: 自动文件清理，保护用户隐私
- 📱 **响应式设计**: 完美适配桌面和移动设备

## 🚀 快速开始

### 环境要求

- Python 3.7+
- 现代浏览器 (Chrome 60+, Firefox 55+, Safari 12+, Edge 79+)

### 安装和运行

1. **克隆项目**

   ```bash
   git clone <repository-url>
   cd pdf2md
   ```

2. **启动后端服务**

   ```bash
   cd backend
   pip install -r requirements.txt
   python run.py
   ```

   后端服务将在 http://localhost:5000 启动

3. **打开前端应用**

   ```bash
   cd frontend
   # 在浏览器中打开 index.html
   # 或使用本地服务器
   python -m http.server 8080
   ```

4. **开始使用**
   - 选择或拖拽 PDF 文件到上传区域
   - 选择转换格式：
     - 点击"转换为 Markdown"按钮：生成 Markdown 格式文本，可复制或下载包含图片的压缩包
     - 点击"转换为 Word"按钮：直接下载 Word 文档，包含文本和图片
   - 查看、复制或下载转换结果

## 📁 项目结构

```
pdf2md/
│
├── backend/                 # 后端Flask应用
│   ├── app/
│   │   ├── __init__.py     # 应用初始化
│   │   ├── routes.py       # API路由
│   │   └── converter.py    # PDF转换逻辑
│   ├── temp_uploads/       # 临时文件存储
│   ├── run.py              # 应用入口
│   ├── requirements.txt    # Python依赖
│   └── README.md           # 后端文档
│
├── frontend/               # 前端Vue.js应用
│   ├── index.html          # 主页面
│   ├── styles.css          # 样式文件
│   ├── app.js              # 应用逻辑
│   └── README.md           # 前端文档
│
├── memory-bank/            # 项目文档
│   ├── game-design-document.md    # 需求文档
│   ├── tech-stack.md              # 技术栈说明
│   ├── implementation-plan.md     # 实施计划
│   ├── architecture.md            # 架构文档
│   └── progress.md                # 进度记录
│
└── README.md               # 项目概述
```

## 🛠️ 技术栈

### 后端

- **Python 3.7+**: 编程语言
- **Flask**: Web 框架
- **PyMuPDF (fitz)**: PDF 处理库
- **python-docx**: Word 文档生成库
- **Flask-CORS**: 跨域支持
- **Pillow**: 图片处理库

### 前端

- **Vue.js 3**: 前端框架
- **原生 CSS**: 样式设计
- **Fetch API**: HTTP 请求
- **File API**: 文件处理

## 🔧 API 文档

### 健康检查

```
GET /health
响应: {"status": "ok", "message": "后端正在运行"}
```

### PDF 转换

```
POST /api/convert_pdf_to_md
参数: multipart/form-data (file字段)
响应: {
  "status": "success",
  "filename": "document.pdf",
  "markdown_content": "转换后的Markdown内容..."
}
```

## 🎯 使用场景

- **文档转换**: 将 PDF 文档快速转换为可编辑的 Markdown 格式
- **内容提取**: 从 PDF 中提取文本内容用于进一步处理
- **格式迁移**: 将 PDF 格式的文档迁移到 Markdown 生态系统
- **批量处理**: 处理大量 PDF 文件的文本提取需求

## 🔒 安全特性

- **文件验证**: 严格的 PDF 文件类型和大小检查
- **临时存储**: 使用 UUID 命名，处理后自动删除
- **路径安全**: 防止路径遍历攻击
- **CORS 配置**: 限制跨域访问

## 📊 性能特点

- **高效转换**: 基于 PyMuPDF 的快速 PDF 解析
- **内存优化**: 及时释放文档对象，避免内存泄漏
- **并发支持**: Flask 多线程处理多个请求
- **客户端验证**: 减少服务器负载

## 🚧 开发状态

**当前版本**: MVP (最小可行产品) ✅

### 已完成功能

- ✅ PDF 文件上传和验证
- ✅ 基本 PDF 到 Markdown 转换
- ✅ 现代化用户界面
- ✅ 文件下载和复制功能
- ✅ 错误处理和用户反馈
- ✅ 响应式设计

### 计划功能

- 🔄 标题和列表识别
- 🔄 表格转换支持
- 🔄 图像提取和引用
- 🔄 OCR 功能集成
- 🔄 批量文件处理

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 📝 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 📞 联系方式

如有问题或建议，请通过以下方式联系：

- 提交 Issue
- 发送 Pull Request
- 邮件联系

## 🙏 致谢

- [PyMuPDF](https://pymupdf.readthedocs.io/) - 强大的 PDF 处理库
- [Vue.js](https://vuejs.org/) - 渐进式 JavaScript 框架
- [Flask](https://flask.palletsprojects.com/) - 轻量级 Web 框架

---

**享受 PDF 到 Markdown 的转换体验！** 🎉
