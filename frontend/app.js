const { createApp } = Vue;

createApp({
  data() {
    return {
      selectedFile: null,
      markdownContent: "",
      extractedImages: [],
      imageCount: 0,
      isConverting: false,
      isDragOver: false,
      errorMessage: "",
      copyButtonText: "复制 Markdown",
      originalFilename: "",
      downloadedImages: [], // 记录已下载的图片
    };
  },
  methods: {
    // 触发文件选择
    triggerFileSelect() {
      document.getElementById("pdfUpload").click();
    },

    // 处理文件选择
    handleFileSelect(event) {
      const file = event.target.files[0];
      this.validateAndSetFile(file);
    },

    // 处理拖拽悬停
    handleDragOver(event) {
      this.isDragOver = true;
    },

    // 处理拖拽离开
    handleDragLeave(event) {
      this.isDragOver = false;
    },

    // 处理文件拖放
    handleDrop(event) {
      this.isDragOver = false;
      const files = event.dataTransfer.files;
      if (files.length > 0) {
        this.validateAndSetFile(files[0]);
      }
    },

    // 验证并设置文件
    validateAndSetFile(file) {
      if (!file) return;

      // 检查文件类型
      if (
        file.type !== "application/pdf" &&
        !file.name.toLowerCase().endsWith(".pdf")
      ) {
        this.showError("请选择PDF文件。");
        return;
      }

      // 检查文件大小 (50MB)
      const maxSize = 50 * 1024 * 1024;
      if (file.size > maxSize) {
        this.showError("文件大小超过50MB限制。");
        return;
      }

      this.selectedFile = file;
      this.originalFilename = file.name;
      this.clearError();
      this.clearOutput();
    },

    // 清除文件选择
    clearFile() {
      this.selectedFile = null;
      this.originalFilename = "";
      document.getElementById("pdfUpload").value = "";
      this.clearOutput();
    },

    // 清除输出内容
    clearOutput() {
      this.markdownContent = "";
      this.extractedImages = [];
      this.imageCount = 0;
      this.downloadedImages = [];
      this.copyButtonText = "复制 Markdown";
    },

    // 转换PDF到Markdown
    async convertToMarkdown() {
      if (!this.selectedFile) return;

      this.isConverting = true;
      this.clearError();

      try {
        const formData = new FormData();
        formData.append("file", this.selectedFile);

        const response = await fetch(
          "http://localhost:5000/api/convert_pdf_to_md",
          {
            method: "POST",
            body: formData,
          }
        );

        const result = await response.json();

        if (response.ok && result.status === "success") {
          this.markdownContent = result.markdown_content;
          this.originalFilename = result.filename;

          // 保存提取的图片信息
          this.extractedImages = result.images || [];
          this.imageCount = result.image_count || 0;

          // 确保每个图片对象有完整的信息
          this.extractedImages = this.extractedImages.map((img) => {
            // 确保path字段存在
            if (!img.path) {
              img.path = `${img.filename}`;
            }
            return img;
          });

          // 处理Markdown中的图片链接，使其指向本地路径
          if (this.extractedImages.length > 0) {
            this.markdownContent = this.processImageLinksForLocal(
              this.markdownContent
            );
          }
        } else {
          this.showError(result.message || "转换失败，请重试。");
        }
      } catch (error) {
        console.error("转换错误:", error);
        this.showError("网络错误或服务器无响应。请检查后端服务是否正在运行。");
      } finally {
        this.isConverting = false;
      }
    },

    // 转换PDF到裁剪图片
    async convertToImages() {
      if (!this.selectedFile) return;

      this.isConverting = true;
      this.clearError();

      try {
        const formData = new FormData();
        formData.append("file", this.selectedFile);

        const response = await fetch(
          "http://localhost:5000/api/convert_pdf_to_images",
          {
            method: "POST",
            body: formData,
          }
        );

        if (response.ok) {
          // 获取文件名
          const contentDisposition = response.headers.get('Content-Disposition');
          let filename = 'cropped_images.zip';
          if (contentDisposition) {
            const filenameMatch = contentDisposition.match(/filename="?([^"]+)"?/);
            if (filenameMatch) {
              filename = filenameMatch[1];
            }
          }

          // 下载文件
          const blob = await response.blob();
          const url = URL.createObjectURL(blob);
          
          const a = document.createElement('a');
          a.href = url;
          a.download = filename;
          document.body.appendChild(a);
          a.click();
          document.body.removeChild(a);
          
          // 清理URL对象
          URL.revokeObjectURL(url);
          
          // 显示成功消息
          this.showSuccess(`裁剪图片压缩包已成功下载: ${filename}`);
        } else {
          const result = await response.json();
          this.showError(result.message || "裁剪失败，请重试。");
        }
      } catch (error) {
        console.error("裁剪错误:", error);
        this.showError("网络错误或服务器无响应。请检查后端服务是否正在运行。");
      } finally {
        this.isConverting = false;
      }
    },

    // 转换PDF到Word
    async convertToWord() {
      if (!this.selectedFile) return;

      this.isConverting = true;
      this.clearError();

      try {
        const formData = new FormData();
        formData.append("file", this.selectedFile);

        const response = await fetch(
          "http://localhost:5000/api/convert_pdf_to_word",
          {
            method: "POST",
            body: formData,
          }
        );

        if (response.ok) {
          // 获取文件名
          const contentDisposition = response.headers.get('Content-Disposition');
          let filename = 'converted.docx';
          if (contentDisposition) {
            const filenameMatch = contentDisposition.match(/filename="?([^"]+)"?/);
            if (filenameMatch) {
              filename = filenameMatch[1];
            }
          }

          // 下载文件
          const blob = await response.blob();
          const url = URL.createObjectURL(blob);
          
          const a = document.createElement('a');
          a.href = url;
          a.download = filename;
          document.body.appendChild(a);
          a.click();
          document.body.removeChild(a);
          
          // 清理URL对象
          URL.revokeObjectURL(url);
          
          // 显示成功消息
          this.showSuccess(`Word文档已成功下载: ${filename}`);
        } else {
          const result = await response.json();
          this.showError(result.message || "转换失败，请重试。");
        }
      } catch (error) {
        console.error("转换错误:", error);
        this.showError("网络错误或服务器无响应。请检查后端服务是否正在运行。");
      } finally {
        this.isConverting = false;
      }
    },

    // 下载单个图片
    async downloadImage(image) {
      try {
        const response = await fetch(
          `http://localhost:5000/api/images/${image.filename}`
        );
        if (!response.ok) {
          throw new Error(`下载失败: ${response.status}`);
        }

        const blob = await response.blob();
        const url = URL.createObjectURL(blob);

        const a = document.createElement("a");
        a.href = url;
        a.download = image.filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);

        // 清理URL对象
        URL.revokeObjectURL(url);

        // 标记为已下载
        if (!this.downloadedImages.includes(image.filename)) {
          this.downloadedImages.push(image.filename);
        }

        return true;
      } catch (error) {
        console.error(`下载图片 ${image.filename} 失败:`, error);
        this.showError(`下载图片 ${image.filename} 失败: ${error.message}`);
        return false;
      }
    },

    // 下载所有图片
    async downloadAllImages() {
      if (this.extractedImages.length === 0) {
        this.showError("没有图片可下载");
        return;
      }

      let successCount = 0;
      let totalCount = this.extractedImages.length;

      for (const image of this.extractedImages) {
        const success = await this.downloadImage(image);
        if (success) {
          successCount++;
        }
        // 添加小延迟避免浏览器阻止多个下载
        await new Promise((resolve) => setTimeout(resolve, 100));
      }

      if (successCount === totalCount) {
        alert(`成功下载 ${successCount} 张图片！`);
      } else {
        alert(`下载完成：成功 ${successCount}/${totalCount} 张图片`);
      }
    },

    // 复制到剪贴板
    async copyToClipboard() {
      if (!this.markdownContent) return;

      try {
        await navigator.clipboard.writeText(this.markdownContent);
        this.copyButtonText = "已复制！";

        // 2秒后恢复按钮文本
        setTimeout(() => {
          this.copyButtonText = "复制 Markdown";
        }, 2000);
      } catch (error) {
        console.error("复制失败:", error);
        this.showError("复制失败，请手动选择文本复制。");
      }
    },

    // 下载Markdown文件
    downloadMarkdown() {
      if (!this.markdownContent) return;

      // 生成文件名
      let filename = "converted.md";
      if (this.originalFilename) {
        const baseName = this.originalFilename.replace(/\.pdf$/i, "");
        filename = `${baseName}.md`;
      }

      // 创建Blob并下载
      const blob = new Blob([this.markdownContent], { type: "text/markdown" });
      const url = URL.createObjectURL(blob);

      const a = document.createElement("a");
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);

      // 清理URL对象
      URL.revokeObjectURL(url);
    },

    // 下载完整包（Markdown + 图片）
    async downloadCompletePackage() {
      if (!this.markdownContent) {
        this.showError("没有内容可下载");
        return;
      }

      // 先下载所有图片
      if (this.extractedImages.length > 0) {
        await this.downloadAllImages();

        // 等待一下确保图片下载完成
        await new Promise((resolve) => setTimeout(resolve, 500));
      }

      // 然后下载Markdown文件
      this.downloadMarkdown();

      // 显示说明
      const imageInfo =
        this.extractedImages.length > 0
          ? `\n\n请将下载的图片文件放在与Markdown文件相同的目录下，以确保图片正确显示。`
          : "";

      alert(`下载完成！${imageInfo}`);
    },

    // 下载ZIP压缩包（包含Markdown和图片）
    async downloadZipPackage() {
      if (!this.markdownContent) {
        this.showError("没有内容可下载");
        return;
      }

      this.showError(
        `正在创建压缩包...（包含Markdown和${this.imageCount}张图片）`
      );

      try {
        // 准备请求数据
        const requestData = {
          markdown_content: this.markdownContent,
          images: this.extractedImages,
          filename: this.originalFilename || "converted",
        };

        // 发送请求到后端创建ZIP包
        const response = await fetch(
          "http://localhost:5000/api/create_package",
          {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify(requestData),
          }
        );

        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.message || "创建压缩包失败");
        }

        // 下载生成的ZIP文件
        const blob = await response.blob();
        const url = URL.createObjectURL(blob);

        // 准备文件名
        const baseFilename = this.originalFilename
          ? this.originalFilename.replace(/\.pdf$/i, "")
          : "converted";
        const zipFilename = `${baseFilename}_package.zip`;

        // 创建下载链接并触发下载
        const a = document.createElement("a");
        a.href = url;
        a.download = zipFilename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);

        // 清理URL对象
        URL.revokeObjectURL(url);

        // 清除错误提示
        this.clearError();

        // 显示成功消息
        setTimeout(() => {
          alert(
            `压缩包下载成功！\n包含Markdown文件和${this.imageCount}张图片。\n文件名：${zipFilename}`
          );
        }, 500);
      } catch (error) {
        console.error("下载压缩包失败:", error);
        this.showError(`下载压缩包失败: ${error.message}`);
      }
    },

    // 格式化文件大小
    formatFileSize(bytes) {
      if (bytes === 0) return "0 Bytes";

      const k = 1024;
      const sizes = ["Bytes", "KB", "MB", "GB"];
      const i = Math.floor(Math.log(bytes) / Math.log(k));

      return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
    },

    // 显示错误消息
    showError(message) {
      this.errorMessage = message;
    },

    // 显示成功消息
    showSuccess(message) {
      // 清除错误消息
      this.clearError();
      // 显示成功提示
      alert(message);
    },

    // 清除错误消息
    clearError() {
      this.errorMessage = "";
    },

    // 处理Markdown中的图片链接（本地路径版本）
    processImageLinksForLocal(markdownText) {
      // 将API端点链接转换为本地相对路径
      return markdownText.replace(
        /!\[([^\]]*)\]\(([^)]+)\)/g,
        (match, altText, imagePath) => {
          // 如果是API端点，提取文件名并转换为相对路径
          if (imagePath.includes("/api/images/")) {
            const filename = imagePath.split("/").pop();
            return `![${altText}](${filename})`;
          }
          // 如果已经是相对路径，保持不变
          return match;
        }
      );
    },

    // 检查图片是否已下载
    isImageDownloaded(filename) {
      return this.downloadedImages.includes(filename);
    },
  },

  mounted() {
    // 防止页面默认的拖放行为
    document.addEventListener("dragover", (e) => e.preventDefault());
    document.addEventListener("drop", (e) => e.preventDefault());
  },
}).mount("#app");
