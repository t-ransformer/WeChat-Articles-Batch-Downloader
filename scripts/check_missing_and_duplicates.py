#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查缺失的文章和重复的PDF文件
对比Markdown文件夹和PDF文件夹
"""

import os
import glob
import re

markdown_dir = '/Users/fanyumeng/Documents/公众号/公众号文章导出/WeChat-Articles-Batch-Downloader/output/markdown'
pdf_dir = '/Users/fanyumeng/Documents/公众号/公众号文章导出/WeChat-Articles-Batch-Downloader/output/pdf_perfect'

print("=" * 70)
print("检查缺失的文章和重复的PDF")
print("=" * 70)

# 1. 获取所有Markdown文件
md_files = glob.glob(os.path.join(markdown_dir, '*.md'))
md_bases = {}
for md_file in md_files:
    md_name = os.path.basename(md_file).replace('.md', '')
    # 提取文章标题（移除时间戳）
    md_clean = md_name.split('_2026')[0] if '_2026' in md_name else md_name
    md_bases[md_clean] = md_file

print(f"\nMarkdown文件总数: {len(md_files)}")

# 2. 获取所有PDF文件
pdf_files = glob.glob(os.path.join(pdf_dir, '*.pdf'))
pdf_bases = {}
for pdf_file in pdf_files:
    pdf_name = os.path.basename(pdf_file).replace('.pdf', '')
    # 提取文章标题（移除时间戳）
    pdf_clean = pdf_name.split('_2026')[0] if '_2026' in pdf_name else pdf_name
    if pdf_clean not in pdf_bases:
        pdf_bases[pdf_clean] = []
    pdf_bases[pdf_clean].append(pdf_file)

print(f"PDF文件总数: {len(pdf_files)}")

# 3. 找出重复的PDF
print(f"\n{'='*70}")
print("重复的PDF文件:")
print(f"{'='*70}")

duplicates = []
for pdf_clean, files in pdf_bases.items():
    if len(files) > 1:
        duplicates.append((pdf_clean, files))

if duplicates:
    print(f"\n发现 {len(duplicates)} 组重复文件:\n")
    for pdf_clean, files in duplicates:
        print(f"重复组: {pdf_clean}")
        for f in files:
            size = os.path.getsize(f) / 1024 / 1024
            mtime = os.path.getmtime(f)
            print(f"  - {os.path.basename(f)} ({size:.2f} MB)")
        print()
else:
    print("✅ 没有发现重复文件")

# 4. 找出缺失的文章
print(f"\n{'='*70}")
print("缺失的文章（有Markdown但没有PDF）:")
print(f"{'='*70}")

missing = []
for md_clean, md_file in md_bases.items():
    # 检查是否有对应的PDF
    has_pdf = False
    for pdf_clean in pdf_bases.keys():
        # 模糊匹配
        if md_clean in pdf_clean or pdf_clean in md_clean:
            has_pdf = True
            break
    
    if not has_pdf:
        missing.append((md_clean, md_file))

if missing:
    print(f"\n发现 {len(missing)} 篇缺失的文章:\n")
    for idx, (md_clean, md_file) in enumerate(missing, 1):
        print(f"{idx}. {os.path.basename(md_file)}")
else:
    print("\n✅ 所有文章都有对应的PDF文件")

# 5. 统计
print(f"\n{'='*70}")
print("统计摘要")
print(f"{'='*70}")
print(f"Markdown文件: {len(md_files)}")
print(f"PDF文件: {len(pdf_files)}")
print(f"重复组数: {len(duplicates)}")
print(f"缺失文章: {len(missing)}")
print(f"完成率: {(len(md_files) - len(missing)) / len(md_files) * 100:.1f}%")
print(f"{'='*70}")

# 6. 生成清理脚本建议
if duplicates:
    print(f"\n建议运行清理脚本:")
    print(f"  python3 cleanup_duplicate_pdfs.py")

