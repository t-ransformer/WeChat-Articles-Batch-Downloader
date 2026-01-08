#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
处理所有未完成的文章
1. 重新处理有截图但可能PDF不完整的文章
2. 处理还没有PDF的文章
"""

import os
import glob
import sys
import time
from wechat_to_pdf_perfect import convert_wechat_article_to_pdf_perfect, get_url_from_markdown

markdown_dir = '/Users/fanyumeng/Documents/公众号/公众号文章导出/WeChat-Articles-Batch-Downloader/output/markdown'
pdf_dir = '/Users/fanyumeng/Documents/公众号/公众号文章导出/WeChat-Articles-Batch-Downloader/output/pdf_perfect'

os.makedirs(pdf_dir, exist_ok=True)

print("=" * 70)
print("处理所有未完成的文章")
print("=" * 70)

# 1. 找到所有Markdown文件
md_files = glob.glob(os.path.join(markdown_dir, '*.md'))
md_files.sort()

print(f"\n总文章数: {len(md_files)}")

# 2. 找到所有PDF文件（用于检查哪些已完成）
existing_pdfs = set()
for pdf in glob.glob(os.path.join(pdf_dir, '*.pdf')):
    pdf_name = os.path.basename(pdf)
    # 移除扩展名，用于匹配
    existing_pdfs.add(pdf_name.replace('.pdf', ''))

# 3. 找到所有截图文件（需要重新处理）
screenshots = glob.glob(os.path.join(pdf_dir, '*_screenshot.png'))
screenshot_bases = set()
for screenshot in screenshots:
    base = os.path.basename(screenshot).replace('_screenshot.png', '')
    screenshot_bases.add(base)

print(f"已有PDF: {len(existing_pdfs)}")
print(f"有截图（需重新处理）: {len(screenshot_bases)}")

# 4. 找出需要处理的文章
to_process = []
to_retry = []

for md_file in md_files:
    md_name = os.path.basename(md_file).replace('.md', '')
    
    # 检查是否有对应的PDF
    has_pdf = False
    for pdf_base in existing_pdfs:
        # 模糊匹配（移除时间戳）
        md_clean = md_name.split('_2026')[0] if '_2026' in md_name else md_name
        pdf_clean = pdf_base.split('_2026')[0] if '_2026' in pdf_base else pdf_base
        
        if md_clean in pdf_clean or pdf_clean in md_clean or md_name in pdf_base:
            has_pdf = True
            break
    
    # 检查是否有截图（需要重新处理）
    has_screenshot = False
    for screenshot_base in screenshot_bases:
        md_clean = md_name.split('_2026')[0] if '_2026' in md_name else md_name
        screenshot_clean = screenshot_base.split('_2026')[0] if '_2026' in screenshot_base else screenshot_base
        
        if md_clean in screenshot_clean or screenshot_clean in md_clean:
            has_screenshot = True
            break
    
    if has_screenshot:
        to_retry.append(md_file)
    elif not has_pdf:
        to_process.append(md_file)

print(f"\n需要重新处理（有截图）: {len(to_retry)}")
print(f"需要新处理（无PDF）: {len(to_process)}")
print(f"总计需要处理: {len(to_retry) + len(to_process)}")

# 5. 先处理需要重新处理的（有截图的）
if to_retry:
    print(f"\n{'='*70}")
    print("第一步：重新处理有截图的文章")
    print(f"{'='*70}\n")
    
    for idx, md_file in enumerate(to_retry, 1):
        md_filename = os.path.basename(md_file)
        print(f"\n[{idx}/{len(to_retry)}] 重新处理: {md_filename}")
        print("-" * 70)
        
        # 删除对应的截图和PDF
        md_base = md_filename.replace('.md', '')
        for screenshot in screenshots:
            if md_base.split('_2026')[0] in os.path.basename(screenshot):
                os.remove(screenshot)
                print(f"  已删除截图: {os.path.basename(screenshot)}")
        
        # 删除对应的PDF
        for pdf in glob.glob(os.path.join(pdf_dir, '*.pdf')):
            pdf_base = os.path.basename(pdf).replace('.pdf', '')
            if md_base.split('_2026')[0] in pdf_base.split('_2026')[0]:
                os.remove(pdf)
                print(f"  已删除旧PDF: {os.path.basename(pdf)}")
        
        # 提取URL并转换
        url = get_url_from_markdown(md_file)
        if not url:
            print(f"  ❌ 无法提取URL")
            continue
        
        print(f"  URL: {url[:80]}...")
        
        try:
            success = convert_wechat_article_to_pdf_perfect(url, pdf_dir)
            if success:
                print(f"  ✅ 重新处理成功")
            else:
                print(f"  ❌ 重新处理失败")
        except Exception as e:
            print(f"  ❌ 发生错误: {str(e)}")
        
        time.sleep(2)  # 避免请求过快

# 6. 处理新的文章
if to_process:
    print(f"\n{'='*70}")
    print("第二步：处理新的文章")
    print(f"{'='*70}\n")
    
    success_count = 0
    failed_count = 0
    
    for idx, md_file in enumerate(to_process, 1):
        md_filename = os.path.basename(md_file)
        print(f"\n[{idx}/{len(to_process)}] 处理: {md_filename}")
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
        
        # 每10个文件显示进度
        if idx % 10 == 0:
            print(f"\n进度: [{idx}/{len(to_process)}] 成功 {success_count}, 失败 {failed_count}\n")
        
        time.sleep(2)  # 避免请求过快

# 7. 最终统计
print(f"\n{'='*70}")
print("处理完成！")
print(f"{'='*70}")

final_pdfs = len(glob.glob(os.path.join(pdf_dir, '*.pdf')))
final_screenshots = len(glob.glob(os.path.join(pdf_dir, '*_screenshot.png')))

print(f"总文章数: {len(md_files)}")
print(f"最终PDF数量: {final_pdfs}")
print(f"剩余截图数量: {final_screenshots}")
print(f"完成率: {final_pdfs / len(md_files) * 100:.1f}%")
print(f"{'='*70}")

