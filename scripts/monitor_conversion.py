#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
实时监控批量转换进度
"""

import os
import glob
import time
import subprocess
from datetime import datetime

def get_progress():
    """获取转换进度"""
    pdf_dir = '/Users/fanyumeng/Documents/公众号/公众号文章导出/WeChat-Articles-Batch-Downloader/output/pdf_perfect'
    md_dir = '/Users/fanyumeng/Documents/公众号/公众号文章导出/WeChat-Articles-Batch-Downloader/output/markdown'
    
    pdf_files = set([os.path.basename(f).replace('.pdf', '') 
                     for f in glob.glob(os.path.join(pdf_dir, '*.pdf'))])
    md_files = set([os.path.basename(f).replace('.md', '') 
                    for f in glob.glob(os.path.join(md_dir, '*.md'))])
    
    total = len(md_files)
    completed = len(pdf_files)
    remaining = total - completed
    percentage = (completed / total * 100) if total > 0 else 0
    
    # 获取最新生成的PDF文件
    pdf_paths = glob.glob(os.path.join(pdf_dir, '*.pdf'))
    latest_pdf = None
    if pdf_paths:
        latest_pdf = max(pdf_paths, key=os.path.getmtime)
        latest_time = datetime.fromtimestamp(os.path.getmtime(latest_pdf))
        latest_name = os.path.basename(latest_pdf)
    else:
        latest_time = None
        latest_name = None
    
    return {
        'total': total,
        'completed': completed,
        'remaining': remaining,
        'percentage': percentage,
        'latest_file': latest_name,
        'latest_time': latest_time
    }

def check_process():
    """检查进程是否运行"""
    try:
        result = subprocess.run(
            ['ps', 'aux'],
            capture_output=True,
            text=True
        )
        lines = result.stdout.split('\n')
        for line in lines:
            if 'batch_wechat_to_pdf' in line and 'grep' not in line:
                parts = line.split()
                if len(parts) > 1:
                    return {'running': True, 'pid': parts[1]}
        return {'running': False, 'pid': None}
    except:
        return {'running': False, 'pid': None}

def main():
    """主监控循环"""
    print("=" * 70)
    print("实时监控批量转换进度")
    print("=" * 70)
    print()
    
    last_count = 0
    error_count = 0
    
    while True:
        # 检查进程状态
        process = check_process()
        
        # 获取进度
        progress = get_progress()
        
        # 清屏（可选）
        # os.system('clear')
        
        print(f"\r[{datetime.now().strftime('%H:%M:%S')}] ", end='')
        
        if not process['running']:
            print("⚠️  进程未运行！")
            break
        
        print(f"进度: {progress['completed']}/{progress['total']} ({progress['percentage']:.1f}%) | ", end='')
        print(f"剩余: {progress['remaining']} | ", end='')
        
        if progress['latest_file']:
            print(f"最新: {progress['latest_file'][:40]}...")
        else:
            print("等待中...")
        
        # 检测新完成的文件
        if progress['completed'] > last_count:
            new_files = progress['completed'] - last_count
            print(f"  ✅ 新完成 {new_files} 个文件！")
            last_count = progress['completed']
        
        # 检查是否完成
        if progress['remaining'] == 0:
            print("\n" + "=" * 70)
            print("✅ 所有文件转换完成！")
            print("=" * 70)
            break
        
        time.sleep(5)  # 每5秒更新一次

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n监控已停止")

