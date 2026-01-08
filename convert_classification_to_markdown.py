#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
将分类结果JSON文件转换为易读的Markdown格式
"""

import json
import os
from pathlib import Path


def clean_title(title):
    """清理文章标题，移除时间戳"""
    # 移除末尾的时间戳格式：_YYYYMMDD_HHMMSS
    import re
    # 匹配末尾的时间戳模式
    pattern = r'_\d{8}_\d{6}$'
    cleaned = re.sub(pattern, '', title)
    # 将下划线替换为空格（可选，根据需求调整）
    # cleaned = cleaned.replace('_', ' ')
    return cleaned


def convert_json_to_markdown(json_path, output_path=None):
    """将分类结果JSON转换为Markdown格式"""
    
    # 读取JSON文件
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 生成Markdown内容
    md_lines = []
    
    # 标题和统计信息
    md_lines.append("# 文章分类结果\n")
    md_lines.append(f"**总文章数**: {data.get('total_articles', 0)} 篇\n")
    md_lines.append(f"**总分类数**: {data.get('total_catalogs', 0)} 个\n")
    md_lines.append("\n---\n")
    
    # 按文章数量排序分类
    catalogs = data.get('catalogs', {})
    sorted_catalogs = sorted(
        catalogs.items(),
        key=lambda x: x[1].get('article_count', 0),
        reverse=True
    )
    
    # 生成目录
    md_lines.append("## 目录\n")
    for idx, (catalog_name, catalog_info) in enumerate(sorted_catalogs, 1):
        articles = catalog_info.get('articles', [])
        article_count = len(articles)  # 使用实际文章数量
        md_lines.append(f"{idx}. [{catalog_name}](#{catalog_name.replace(' ', '-').replace('_', '-')}) ({article_count}篇)\n")
    md_lines.append("\n---\n")
    
    # 详细分类信息
    for idx, (catalog_name, catalog_info) in enumerate(sorted_catalogs, 1):
        md_lines.append(f"\n## {idx}. {catalog_name}\n")
        
        # 分类信息
        topic_id = catalog_info.get('topic_id', 'N/A')
        description = catalog_info.get('description', '')
        keywords = catalog_info.get('keywords', [])
        articles = catalog_info.get('articles', [])
        # 使用实际文章列表的长度
        article_count = len(articles)
        
        md_lines.append(f"**主题ID**: {topic_id}  \n")
        md_lines.append(f"**文章数量**: {article_count} 篇  \n")
        md_lines.append(f"**描述**: {description}  \n")
        
        if keywords:
            md_lines.append(f"**关键词**: {', '.join(keywords[:10])}  \n")  # 只显示前10个关键词
        
        md_lines.append("\n### 文章列表\n\n")
        
        # 如果有articles信息，尝试获取标题
        articles_info = data.get('articles', {})
        
        for article_idx, article_key in enumerate(articles, 1):
            # 尝试从articles对象中获取标题
            if article_key in articles_info:
                article_title = articles_info[article_key].get('title', article_key)
            else:
                article_title = clean_title(article_key)
            
            md_lines.append(f"{article_idx}. {article_title}\n")
        
        md_lines.append("\n---\n")
    
    # 写入Markdown文件
    if output_path is None:
        json_dir = os.path.dirname(json_path)
        output_path = os.path.join(json_dir, 'classification_result.md')
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(''.join(md_lines))
    
    print(f"✅ 转换完成！输出文件: {output_path}")
    return output_path


if __name__ == '__main__':
    # 设置路径 - 使用新的分类结果
    json_file = '/Users/fanyumeng/Documents/公众号/公众号文章导出/WeChat-Articles-Batch-Downloader/output/catalogs/classification_result_new.json'
    
    # 转换
    output_file = convert_json_to_markdown(json_file)
    
    # 同时生成一个带_new后缀的markdown文件
    if output_file:
        import shutil
        new_md_file = output_file.replace('.md', '_new.md')
        shutil.copy(output_file, new_md_file)
        print(f"✅ 同时生成新分类结果: {new_md_file}")

