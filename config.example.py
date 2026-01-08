"""
配置文件模板
复制此文件为 config.py 并根据需要修改配置
"""
import os

# 项目根目录
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 输出目录
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
MARKDOWN_DIR = os.path.join(OUTPUT_DIR, "markdown")
IMAGES_DIR = os.path.join(OUTPUT_DIR, "images")
PDF_DIR = os.path.join(OUTPUT_DIR, "pdf")

# 请求配置
REQUEST_TIMEOUT = 30  # 请求超时时间（秒）
MAX_RETRIES = 3  # 最大重试次数
RETRY_DELAY = 2  # 重试延迟（秒）

# User-Agent
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

# 图片下载配置
IMAGE_TIMEOUT = 60  # 图片下载超时时间（秒）
IMAGE_MAX_SIZE = 10 * 1024 * 1024  # 图片最大下载大小（10MB）

# 文件名清理配置（移除非法字符）
INVALID_CHARS = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']

