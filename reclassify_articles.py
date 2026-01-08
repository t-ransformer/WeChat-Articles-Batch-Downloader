#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
根据新的分类标准重新分类文章
分类标准：
1. 基础知识类：基础概念解释
2. 历史系列类：历史阐述系列
3. 人物系列类：介绍重要人物
4. 产品介绍类：介绍声学产品
5. 常识科普类：科普类文章、奇闻类
6. 新闻资讯类：时事新闻、行业动态
"""

import json
import os
import re
from collections import defaultdict


def clean_title(title):
    """清理文章标题，移除时间戳"""
    pattern = r'_\d{8}_\d{6}$'
    cleaned = re.sub(pattern, '', title)
    return cleaned


def classify_article(title):
    """
    根据标题特征分类文章
    
    Args:
        title: 文章标题
        
    Returns:
        str: 分类名称
    """
    title_clean = clean_title(title)
    
    # 1. 基础知识类：包含"什么是"、"什么是"等基础概念解释
    if re.search(r'什么是|什么是', title_clean):
        return '基础知识类'
    
    # 2. 历史系列类：包含"发展史"、"历史"、"起源"、"演进"、"进化"、"简史"等
    if re.search(r'发展史|历史|起源|演进|进化|简史|百年', title_clean):
        return '历史系列类'
    
    # 3. 人物系列类：包含"大咖"、"博士的日常"等人物介绍
    if re.search(r'大咖|博士的日常', title_clean):
        return '人物系列类'
    
    # 研究所系列也算人物/机构类
    if re.search(r'研究所系列|音频研究所系列', title_clean):
        return '人物系列类'
    
    # 航空噪声系列算科普类
    if re.search(r'航空噪声.*怎么破', title_clean):
        return '常识科普类'
    
    # 4. 产品介绍类：介绍具体产品（优先于新闻资讯类）
    product_keywords = [
        r'AirPods|降噪耳机|主动降噪耳机',
        r'嵌在.*音响|座椅.*音响',
        r'软件定义|空间音频|全景声|杜比',
        r'Sphere.*喇叭|16万个喇叭',
        r'关于主动降噪耳机.*一切',  # 降噪耳机系列
    ]
    for pattern in product_keywords:
        if re.search(pattern, title_clean):
            # 排除基础知识类（如"什么是监听耳机"）
            if not re.search(r'什么是', title_clean):
                return '产品介绍类'
    
    # 5. 新闻资讯类：时事新闻、行业动态、会议、报告等
    news_keywords = [
        r'大会|会议|论坛|报告|通知|发布|汇总|名单|议程',
        r'年度总结|年终总结',
        r'GAS|AES|苏州论剑',
        r'创业.*汇总|融资.*需求',  # 更具体的新闻类关键词
    ]
    for pattern in news_keywords:
        if re.search(pattern, title_clean):
            return '新闻资讯类'
    
    # 如果包含"行业"、"企业"、"公司"但不是产品介绍，算新闻资讯
    if re.search(r'行业|企业|公司', title_clean):
        # 排除产品介绍类
        if not re.search(r'AirPods|耳机|音响|音频产品', title_clean):
            return '新闻资讯类'
    
    # 汽车音频相关（可能是产品介绍，也可能是科普）
    if re.search(r'汽车音频|NVH', title_clean):
        # 如果是"为什么"开头的，算科普类
        if not re.search(r'为什么|怎么|如何', title_clean):
            # 排除新闻类（大会、论坛等）
            if not re.search(r'大会|论坛|论剑', title_clean):
                return '产品介绍类'
    
    # 6. 常识科普类：包含"为什么"、"怎样"、"如何"、"怎么"等科普问题
    # 以及"奇闻"类、"世界上最"等
    if re.search(r'为什么|怎样|如何|怎么', title_clean):
        # 排除产品介绍类中的"关于主动降噪耳机，你想知道的一切"
        if not re.search(r'关于主动降噪耳机.*一切', title_clean):
            return '常识科普类'
    
    # 奇闻类、世界之最类
    if re.search(r'世界上最|奇声异响|奇奇怪怪|海螺|沙漠|南极|维京|英国|克罗地亚', title_clean):
        return '常识科普类'
    
    # 其他科普类特征
    if re.search(r'人.*听到|人.*发出|说话|口音|心跳|器官|耳朵|声带', title_clean):
        return '常识科普类'
    
    # 如果包含"案例"、"应用"等，可能是科普或产品介绍
    if re.search(r'案例|应用|原理', title_clean):
        return '常识科普类'
    
    # 默认归类为常识科普类（因为大部分都是科普文章）
    return '常识科普类'


def reclassify_articles(json_path, output_path=None):
    """
    重新分类文章
    
    Args:
        json_path: 原始分类结果JSON文件路径
        output_path: 输出JSON文件路径
    """
    # 读取原始JSON文件
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 获取所有文章
    all_articles = {}
    
    # 从catalogs中提取所有文章
    catalogs = data.get('catalogs', {})
    for catalog_name, catalog_info in catalogs.items():
        articles = catalog_info.get('articles', [])
        for article_key in articles:
            if article_key not in all_articles:
                all_articles[article_key] = {
                    'title': clean_title(article_key),
                    'original_catalog': catalog_name
                }
    
    # 从articles对象中获取更多信息
    articles_info = data.get('articles', {})
    for article_key, article_info in articles_info.items():
        if article_key in all_articles:
            all_articles[article_key].update({
                'filename': article_info.get('filename', ''),
                'title': article_info.get('title', clean_title(article_key)),
                'catalog': article_info.get('catalog', ''),
            })
    
    print(f"总共找到 {len(all_articles)} 篇文章")
    
    # 重新分类
    new_catalogs = defaultdict(lambda: {
        'description': '',
        'keywords': [],
        'article_count': 0,
        'articles': []
    })
    
    for article_key, article_info in all_articles.items():
        title = article_info.get('title', clean_title(article_key))
        category = classify_article(title)
        
        new_catalogs[category]['articles'].append(article_key)
        new_catalogs[category]['article_count'] = len(new_catalogs[category]['articles'])
    
    # 生成描述和关键词
    category_descriptions = {
        '基础知识类': '基础概念解释类文章，帮助读者理解声学基本概念',
        '历史系列类': '声学历史发展系列文章，介绍声学各领域的发展历程',
        '人物系列类': '介绍声学领域重要人物和专家的系列文章',
        '产品介绍类': '介绍声学相关产品、技术和应用的文章',
        '常识科普类': '声学科普类文章，解答常见问题，介绍有趣现象',
        '新闻资讯类': '声学行业新闻、会议、报告等资讯类文章',
    }
    
    for category, catalog_info in new_catalogs.items():
        catalog_info['description'] = category_descriptions.get(category, '')
    
    # 构建新的分类结果
    new_result = {
        'total_articles': len(all_articles),
        'total_catalogs': len(new_catalogs),
        'catalogs': dict(new_catalogs),
        'articles': articles_info
    }
    
    # 保存结果
    if output_path is None:
        json_dir = os.path.dirname(json_path)
        output_path = os.path.join(json_dir, 'classification_result_new.json')
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(new_result, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 重新分类完成！")
    print(f"输出文件: {output_path}")
    print(f"\n分类统计：")
    for category, catalog_info in sorted(new_catalogs.items(), key=lambda x: x[1]['article_count'], reverse=True):
        print(f"  {category}: {catalog_info['article_count']} 篇")
    
    return output_path


if __name__ == '__main__':
    json_file = '/Users/fanyumeng/Documents/公众号/公众号文章导出/WeChat-Articles-Batch-Downloader/output/catalogs/classification_result.json'
    reclassify_articles(json_file)

