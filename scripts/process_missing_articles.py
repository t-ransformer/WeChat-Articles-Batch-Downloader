#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
处理缺失的14篇文章
"""

import os
import glob
import sys
import time
from wechat_to_pdf_perfect import convert_wechat_article_to_pdf_perfect, get_url_from_markdown

markdown_dir = '/Users/fanyumeng/Documents/公众号/公众号文章导出/WeChat-Articles-Batch-Downloader/output/markdown'
pdf_dir = '/Users/fanyumeng/Documents/公众号/公众号文章导出/WeChat-Articles-Batch-Downloader/output/pdf_perfect'

# 缺失的文章列表
missing_files = [
    '关于主动降噪耳机，你想知道的一切（五）_20260106_181558.md',
    '关于主动降噪耳机，你想知道的一切（二）：前馈自适应_20260106_184520.md',
    '什么是音色？_20260106_180252.md',
    '声学AI番外篇：基于物理的神经网络_20260106_180930.md',
    '声学发展史之——智能声学_20260106_181800.md',
    '心跳的声音：人体器官交响乐系列（一）_20260106_181649.md',
    '关于主动降噪耳机，你想知道的一切（四）_20260106_181222.md',
    '乐器发声原理之——木管_·_长笛篇_20260106_181546.md',
    '关于主动降噪耳机，你想知道的一切（一）_20260106_181150.md',
    '分贝（dB）是什么海鲜，以及1+1≠2_20260106_180309.md',
    '当声学遇见凝聚态（二）_20260106_180450.md',
    '多普勒，那个和声音赛跑的男人_20260106_180517.md',
    '关于主动降噪耳机，你想知道的一切（六）：半自适应降噪耳机_20260106_181329.md',
    '关于主动降噪耳机，你想知道的一切（三）_20260106_184422.md',
]

print("=" * 70)
print("处理缺失的14篇文章")
print("=" * 70)

os.makedirs(pdf_dir, exist_ok=True)

success_count = 0
failed_count = 0

for idx, filename in enumerate(missing_files, 1):
    md_file = os.path.join(markdown_dir, filename)
    
    if not os.path.exists(md_file):
        print(f"\n[{idx}/{len(missing_files)}] ❌ 文件不存在: {filename}")
        failed_count += 1
        continue
    
    print(f"\n[{idx}/{len(missing_files)}] 处理: {filename}")
    print("-" * 70)
    
    # 提取URL
    url = get_url_from_markdown(md_file)
    if not url:
        print(f"  ❌ 无法提取URL")
        failed_count += 1
        continue
    
    print(f"  URL: {url[:80]}...")
    
    # 转换
    try:
        success = convert_wechat_article_to_pdf_perfect(url, pdf_dir)
        if success:
            success_count += 1
            print(f"  ✅ 成功")
        else:
            failed_count += 1
            print(f"  ❌ 失败")
    except Exception as e:
        failed_count += 1
        print(f"  ❌ 发生错误: {str(e)}")
    
    # 每5个文件显示进度
    if idx % 5 == 0:
        print(f"\n进度: [{idx}/{len(missing_files)}] 成功 {success_count}, 失败 {failed_count}\n")
    
    time.sleep(2)  # 避免请求过快

print(f"\n{'='*70}")
print("处理完成！")
print(f"{'='*70}")
print(f"✅ 成功: {success_count}")
print(f"❌ 失败: {failed_count}")
print(f"{'='*70}")

