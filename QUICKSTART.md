# 快速开始指南

**只需2步，一键完成！**

## 步骤1：安装依赖

```bash
# 创建虚拟环境（推荐）
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# 或
venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

## 步骤2：一键下载

1. 从 [wechat-article-exporter](https://down.mptext.top) 导出Excel文件
2. 运行：
   ```bash
   python wechat_article_downloader.py 微信公众号文章.xlsx
   ```

**完成！** 文章会自动下载到 `output/` 目录。

## 查看结果

下载的文件在 `output/` 目录：
- `output/markdown/` - Markdown格式文章
- `output/images/` - 下载的图片

在支持Markdown的编辑器中打开 `.md` 文件即可查看文章和图片。
