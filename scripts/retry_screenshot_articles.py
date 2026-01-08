#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
重新处理有截图的文章（可能内容不完整）
"""

import os
import glob
import sys

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from utils.wechat_to_pdf_perfect import convert_wechat_article_to_pdf_perfect, get_url_from_markdown

pdf_dir = '/Users/fanyumeng/Documents/公众号/公众号文章导出/WeChat-Articles-Batch-Downloader/output/pdf_perfect'
markdown_dir = '/Users/fanyumeng/Documents/公众号/公众号文章导出/WeChat-Articles-Batch-Downloader/output/markdown'

# 找到所有有截图的文件
screenshots = glob.glob(os.path.join(pdf_dir, '*_screenshot.png'))

print("=" * 60)
print("重新处理有截图的文章")
print("=" * 60)
print(f"\n找到 {len(screenshots)} 个有截图的文件\n")

success_count = 0
failed_count = 0

for idx, screenshot in enumerate(screenshots, 1):
    # 从截图文件名提取文章标题（去掉_screenshot.png）
    screenshot_name = os.path.basename(screenshot)
    # 尝试找到对应的Markdown文件
    # 截图文件名格式: 文章标题_screenshot.png
    # 但实际PDF文件名可能不同，需要从Markdown文件查找
    
    # 先删除旧的PDF和截图，强制重新生成
    pdf_file = screenshot.replace('_screenshot.png', '.pdf')
    old_pdf_exists = os.path.exists(pdf_file)
    
    print(f"[{idx}/{len(screenshots)}] 处理: {screenshot_name}")
    print("-" * 60)
    
    # 尝试从Markdown文件名匹配
    # 截图文件名可能包含时间戳，需要模糊匹配
    base_name = screenshot_name.replace('_screenshot.png', '')
    # 移除可能的时间戳部分
    base_name_clean = base_name.split('_2026')[0] if '_2026' in base_name else base_name
    
    # 查找匹配的Markdown文件
    md_files = glob.glob(os.path.join(markdown_dir, '*.md'))
    matched_md = None
    
    for md_file in md_files:
        md_name = os.path.basename(md_file).replace('.md', '')
        # 检查是否匹配（移除时间戳后）
        md_name_clean = md_name.split('_2026')[0] if '_2026' in md_name else md_name
        
        if base_name_clean in md_name_clean or md_name_clean in base_name_clean:
            matched_md = md_file
            break
    
    if not matched_md:
        print(f"  ⚠️  未找到匹配的Markdown文件")
        failed_count += 1
        continue
    
    print(f"  找到Markdown文件: {os.path.basename(matched_md)}")
    
    # 提取URL
    url = get_url_from_markdown(matched_md)
    if not url:
        print(f"  ❌ 无法提取URL")
        failed_count += 1
        continue
    
    print(f"  URL: {url[:80]}...")
    
    # 删除旧的PDF和截图
    if old_pdf_exists:
        os.remove(pdf_file)
        print(f"  已删除旧PDF")
    os.remove(screenshot)
    print(f"  已删除旧截图")
    
    # 重新转换
    try:
        success = convert_wechat_article_to_pdf_perfect(url, pdf_dir)
        
        if success:
            success_count += 1
            if os.path.exists(pdf_file):
                file_size = os.path.getsize(pdf_file) / 1024 / 1024
                print(f"  ✅ 成功！文件大小: {file_size:.2f} MB")
            else:
                # 检查是否有新的PDF文件（文件名可能不同）
                new_pdfs = glob.glob(os.path.join(pdf_dir, '*.pdf'))
                latest_pdf = max(new_pdfs, key=os.path.getmtime) if new_pdfs else None
                if latest_pdf:
                    file_size = os.path.getsize(latest_pdf) / 1024 / 1024
                    print(f"  ✅ 成功！新文件: {os.path.basename(latest_pdf)} ({file_size:.2f} MB)")
        else:
            failed_count += 1
            print(f"  ❌ 转换失败")
    
    except Exception as e:
        failed_count += 1
        print(f"  ❌ 发生错误: {str(e)}")
    
    print()

print(f"\n{'='*60}")
print("重新处理完成！")
print(f"{'='*60}")
print(f"✅ 成功: {success_count}")
print(f"❌ 失败: {failed_count}")
print(f"{'='*60}")

