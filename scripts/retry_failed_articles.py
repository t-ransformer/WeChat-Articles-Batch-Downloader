#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
重试失败的文章转换
"""

import os
import glob
import sys

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from utils.wechat_to_pdf_perfect import convert_wechat_article_to_pdf_perfect, get_url_from_markdown

# 失败的文件列表
failed_files = [
    '乐器发声原理之——木管_·_长笛篇_20260106_181546.md',
    '什么是音色？_20260106_180252.md',
    '关于主动降噪耳机，你想知道的一切（一）_20260106_181150.md',
    '关于主动降噪耳机，你想知道的一切（三）_20260106_184422.md',
    '关于主动降噪耳机，你想知道的一切（二）：前馈自适应_20260106_184520.md',
    '关于主动降噪耳机，你想知道的一切（五）_20260106_181558.md',
    '关于主动降噪耳机，你想知道的一切（六）：半自适应降噪耳机_20260106_181329.md',
    '关于主动降噪耳机，你想知道的一切（四）_20260106_181222.md',
    '分贝（dB）是什么海鲜，以及1+1≠2_20260106_180309.md',
    '声学AI番外篇：基于物理的神经网络_20260106_180930.md',
    '声学发展史之——智能声学_20260106_181800.md',
    '多普勒，那个和声音赛跑的男人_20260106_180517.md',
    '当声学遇见凝聚态（二）_20260106_180450.md',
    '心跳的声音：人体器官交响乐系列（一）_20260106_181649.md',
]

markdown_dir = '/Users/fanyumeng/Documents/公众号/公众号文章导出/WeChat-Articles-Batch-Downloader/output/markdown'
output_dir = '/Users/fanyumeng/Documents/公众号/公众号文章导出/WeChat-Articles-Batch-Downloader/output/pdf_perfect'

os.makedirs(output_dir, exist_ok=True)

print("=" * 60)
print("重试失败的文章转换")
print("=" * 60)
print()

success_count = 0
failed_count = 0

for idx, filename in enumerate(failed_files, 1):
    md_file = os.path.join(markdown_dir, filename)
    
    if not os.path.exists(md_file):
        print(f"[{idx}/{len(failed_files)}] ❌ 文件不存在: {filename}")
        failed_count += 1
        continue
    
    print(f"\n[{idx}/{len(failed_files)}] 处理: {filename}")
    print("-" * 60)
    
    # 提取URL
    url = get_url_from_markdown(md_file)
    
    if not url:
        print(f"  ❌ 仍然无法提取URL")
        failed_count += 1
        # 显示文件前几行帮助调试
        with open(md_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()[:10]
            print("  文件前10行:")
            for i, line in enumerate(lines, 1):
                print(f"    {i}: {line.rstrip()[:80]}")
        continue
    
    print(f"  ✅ 找到URL: {url[:80]}...")
    
    # 生成PDF路径
    pdf_filename = os.path.splitext(filename)[0] + '.pdf'
    pdf_path = os.path.join(output_dir, pdf_filename)
    
    # 转换
    try:
        success = convert_wechat_article_to_pdf_perfect(url, pdf_path)
        
        if success:
            success_count += 1
            file_size = os.path.getsize(pdf_path) / 1024 / 1024
            print(f"  ✅ 成功！文件大小: {file_size:.2f} MB")
        else:
            failed_count += 1
            print(f"  ❌ 转换失败")
    
    except Exception as e:
        failed_count += 1
        print(f"  ❌ 发生错误: {str(e)}")

print(f"\n{'='*60}")
print("重试完成！")
print(f"{'='*60}")
print(f"✅ 成功: {success_count}")
print(f"❌ 失败: {failed_count}")
print(f"{'='*60}")

