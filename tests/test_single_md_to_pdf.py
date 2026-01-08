#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试单个Markdown文件转换为PDF
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from markdown_to_pdf_with_local_images import convert_md_to_pdf_with_local_images

# 测试文件
md_file = '/Users/fanyumeng/Documents/公众号/公众号文章导出/WeChat-Articles-Batch-Downloader/output/markdown/-2dB的消声室_20260106_184543.md'
pdf_output = '/Users/fanyumeng/Documents/公众号/公众号文章导出/WeChat-Articles-Batch-Downloader/output/pdf_with_images/-2dB的消声室_20260106_184543.pdf'
images_dir = '/Users/fanyumeng/Documents/公众号/公众号文章导出/WeChat-Articles-Batch-Downloader/output/images'

os.makedirs(os.path.dirname(pdf_output), exist_ok=True)

print("测试单个文件转换...")
success = convert_md_to_pdf_with_local_images(md_file, pdf_output, images_dir)

if success:
    print(f"\n✅ 测试成功！PDF文件: {pdf_output}")
else:
    print(f"\n❌ 测试失败")

