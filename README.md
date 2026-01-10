# 微信公众号文章批量下载工具

一个用于批量下载微信公众号文章并保存为Markdown格式的Python工具。支持多种输入方式：直接使用URL、URL列表文件或Excel文件批量下载。

## ✨ 功能特性

- ✅ 一键下载：从Excel文件直接下载，无需中间步骤
- ✅ 批量下载公众号文章
- ✅ 自动提取文章标题、作者、发布时间
- ✅ 下载文章中的所有图片到本地
- ✅ 支持多种格式：Markdown和PDF（可单独选择或同时生成）
- ✅ 保存为Markdown格式（包含图片引用，支持LaTeX数学公式）
- ✅ 生成PDF格式（完美保留排版和样式）
- ✅ 自动处理文件名中的非法字符
- ✅ 错误重试机制

## 🚀 快速开始（只需2步）

### 1. 安装依赖

```bash
# 创建虚拟环境（推荐）
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# 或
venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

### 2. 一键下载

**最简单的方式：直接使用URL**

```bash
# 单个URL
python wechat_article_downloader.py -u "https://mp.weixin.qq.com/s/xxxxx"

# 多个URL
python wechat_article_downloader.py -u "url1" "url2" "url3"
```

就这么简单！程序会自动：
1. 下载文章内容和所有图片
2. 转换为Markdown格式
3. 同时生成PDF格式（默认）

**其他方式：**
- 从URL列表文件：`python wechat_article_downloader.py -f urls.txt`
- 从Excel文件：`python wechat_article_downloader.py 微信公众号文章.xlsx`（如果使用exporter工具导出Excel）

## 📖 详细使用说明

### 方法1：直接指定URL（最简单，推荐）

直接复制粘贴文章URL即可下载：

```bash
# 单个URL
python wechat_article_downloader.py -u "https://mp.weixin.qq.com/s/xxxxx"

# 多个URL（一次下载多篇文章）
python wechat_article_downloader.py -u "url1" "url2" "url3"
```

**就这么简单！** 程序会自动完成所有操作。

### 方法2：从URL列表文件下载

如果您有多个URL，可以创建一个文本文件（每行一个URL）：

```bash
python wechat_article_downloader.py -f urls.txt
```

### 方法3：从Excel文件下载（可选）

如果您使用 [wechat-article-exporter](https://down.mptext.top) 等工具导出了Excel文件，也可以直接使用：

```bash
python wechat_article_downloader.py 微信公众号文章.xlsx
```

程序会自动识别Excel文件中的URL列并批量下载。

### 方法4：选择下载格式

您可以选择只下载Markdown、只下载PDF，或两者都下载（默认）：

```bash
# 仅下载Markdown格式
python wechat_article_downloader.py --format md 微信公众号文章.xlsx

# 仅下载PDF格式
python wechat_article_downloader.py --format pdf 微信公众号文章.xlsx

# 同时下载Markdown和PDF（默认）
python wechat_article_downloader.py --format both 微信公众号文章.xlsx
# 或直接省略 --format 参数
python wechat_article_downloader.py 微信公众号文章.xlsx
```

## 📁 输出结构

下载的文件会保存在 `output/` 目录下：

```
output/
├── markdown/    # Markdown格式文章
├── pdf/         # PDF格式文章（如果选择生成PDF）
└── images/      # 下载的图片
```

文件命名格式：
- Markdown: `文章标题_发布时间.md`
- PDF: `文章标题_发布时间.pdf`

Markdown文件中的图片使用相对路径 `images/xxx.jpg`，确保Markdown文件与images目录的相对位置正确。

**注意**：Markdown文件支持LaTeX数学公式（使用 `$...$` 和 `$$...$$` 格式），程序会自动修复常见的公式格式错误。

## ⚙️ 配置说明

首次使用请复制 `config.example.py` 为 `config.py`：

```bash
cp config.example.py config.py
```

编辑 `config.py` 可以修改以下配置（可选）：

- `REQUEST_TIMEOUT`: 请求超时时间（秒，默认30）
- `IMAGE_MAX_SIZE`: 图片最大下载大小（字节，默认10MB）
- `MAX_RETRIES`: 最大重试次数（默认3）
- `RETRY_DELAY`: 重试延迟（秒，默认2）

## ❓ 常见问题

### Q: 图片无法显示？

A: 确保Markdown文件与 `images/` 目录的相对位置正确。如果使用Markdown编辑器，确保编辑器支持相对路径的图片引用。

### Q: 下载速度慢怎么办？

A: 程序会自动控制请求频率，避免被封。如果太慢，可以：
- 检查网络连接
- 减少并发请求（修改代码中的延迟时间）

### Q: 如何批量下载多篇文章？

A: 有多种方式：
1. **直接使用URL**（最简单）：`python wechat_article_downloader.py -u "url1" "url2" "url3"`
2. **使用URL列表文件**：创建 `urls.txt` 文件，每行一个URL，然后运行 `python wechat_article_downloader.py -f urls.txt`
3. **使用Excel文件**（可选）：如果您使用 [wechat-article-exporter](https://down.mptext.top) 等工具导出了Excel文件，可以直接使用 `python wechat_article_downloader.py 文件名.xlsx`

### Q: 某些文章下载失败？

A: 可能是网络问题或文章已删除。程序会自动重试3次，如果仍然失败，会在最后统计中显示失败的URL。

### Q: Excel文件格式要求？

A: Excel文件应包含文章URL列（列名可能为"链接"、"URL"、"文章链接"等）。程序会自动识别包含 `mp.weixin.qq.com/s/` 的列。

### Q: 如何只下载Markdown或只下载PDF？

A: 使用 `--format` 参数：
- `--format md`：仅生成Markdown文件
- `--format pdf`：仅生成PDF文件
- `--format both`：同时生成两种格式（默认）

### Q: PDF生成失败怎么办？

A: PDF生成需要额外的依赖包。如果失败，请检查：
- 是否安装了所有依赖（`pip install -r requirements.txt`）
- 是否有足够的磁盘空间
- 如果PDF生成失败，程序会继续生成Markdown文件，不会影响整体下载流程

## 📦 依赖包说明

- `requests`: HTTP请求库
- `beautifulsoup4`: HTML解析库
- `markdownify`: HTML转Markdown转换库
- `lxml`: HTML解析器
- `Pillow`: 图片处理库
- `openpyxl`: Excel文件处理库（用于从Excel提取URL）
- `pdfkit` / `weasyprint`: PDF生成库（用于生成PDF格式）
- `markdown`: Markdown处理库（用于LaTeX公式支持）

## 🙏 致谢

- 感谢 [wechat-article-exporter](https://github.com/wechat-article/wechat-article-exporter) 项目提供参考思路

## 📝 许可证

MIT License

## ⚠️ 声明

通过本程序获取的公众号文章内容，版权归文章原作者所有，请合理使用。若发现侵权行为，请联系我们处理。
