#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
实时监控处理进度
"""

import os
import glob
import time
from datetime import datetime

def get_stats():
    """获取统计信息"""
    pdf_dir = '/Users/fanyumeng/Documents/公众号/公众号文章导出/WeChat-Articles-Batch-Downloader/output/pdf_perfect'
    markdown_dir = '/Users/fanyumeng/Documents/公众号/公众号文章导出/WeChat-Articles-Batch-Downloader/output/markdown'
    
    md_files = glob.glob(os.path.join(markdown_dir, '*.md'))
    pdf_files = glob.glob(os.path.join(pdf_dir, '*.pdf'))
    screenshots = glob.glob(os.path.join(pdf_dir, '*_screenshot.png'))
    
    return {
        'total': len(md_files),
        'pdfs': len(pdf_files),
        'screenshots': len(screenshots),
        'percentage': len(pdf_files) / len(md_files) * 100 if md_files else 0
    }

def main():
    print("=" * 70)
    print("实时监控处理进度")
    print("=" * 70)
    print("按 Ctrl+C 停止监控\n")
    
    last_pdf_count = 0
    
    try:
        while True:
            stats = get_stats()
            current_time = datetime.now().strftime('%H:%M:%S')
            
            # 检测新完成的文件
            new_files = stats['pdfs'] - last_pdf_count if last_pdf_count > 0 else 0
            
            print(f"\r[{current_time}] PDF: {stats['pdfs']}/{stats['total']} ({stats['percentage']:.1f}%) | "
                  f"截图: {stats['screenshots']} | "
                  f"剩余: {stats['total'] - stats['pdfs']}", end='', flush=True)
            
            if new_files > 0:
                print(f" | ✅ 新完成 {new_files} 个")
            
            last_pdf_count = stats['pdfs']
            
            # 检查是否完成
            if stats['pdfs'] >= stats['total']:
                print(f"\n\n✅ 所有文章处理完成！")
                break
            
            time.sleep(5)
    
    except KeyboardInterrupt:
        print("\n\n监控已停止")

if __name__ == '__main__':
    main()

