#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
按照声学领域分类图重新分类文章
基于图片中的声学跨学科分类体系
"""

import json
import os
import re
from collections import defaultdict
from typing import Dict, List


def classify_by_acoustic_domain(title: str, keywords: List[str], content: str = "") -> str:
    """
    根据标题和关键词分类到声学领域
    
    基于图片中的分类：
    1. 基础物理声学 (Fundamental physical acoustics)
    2. 地球科学相关 (Earth sciences): Underwater sound, Seismic waves, Sound in atmosphere
    3. 工程相关 (Engineering): Electro-acoustics, Sonic/ultrasonic engineering, Shock and vibration, Noise, Room acoustics
    4. 艺术相关 (Arts): Musical scales and instruments, Communication, Psycho-acoustics
    5. 生命科学相关 (Life sciences): Hearing, Bioacoustics
    """
    title_lower = title.lower()
    keywords_lower = [k.lower() for k in keywords]
    all_text = (title + " " + " ".join(keywords)).lower()
    
    # 保留的特殊类别（不按领域分类）
    if re.search(r'发展史|历史|起源|演进|进化|简史|百年', title):
        return '历史系列类'
    
    if re.search(r'大咖|博士的日常|研究所系列', title):
        return '人物系列类'
    
    if re.search(r'大会|会议|论坛|报告|通知|发布|汇总|名单|议程|年度总结|年终总结|GAS|AES|创业.*汇总|融资', title):
        return '新闻资讯类'
    
    if re.search(r'什么是', title):
        return '基础知识类'
    
    # 产品介绍类（优先判断，因为产品可能涉及多个领域）
    product_keywords = [
        'airpods', 'sphere', '16万个喇叭', '拉斯维加斯',
        '关于主动降噪耳机.*一切', '降噪耳机', '主动降噪',
        '空间音频.*普及|空间音频.*样子', '杜比空间音频',
        '嵌在.*音响|座椅.*音响', '软件定义音频'
    ]
    if any(re.search(kw, title_lower) for kw in product_keywords):
        return '产品介绍类'
    
    # 1. 生命科学相关 (Life sciences)
    life_science_keywords = [
        'hearing', '听觉', '听力', '听阈', '耳朵', '耳蜗', '耳膜', '鼓膜',
        'bioacoustics', '生物声学', '生物医学', '医学超声', '超声', '超声波', 'b超',
        'physiology', '生理', '器官', '心跳', '声带', '发声', '说话', '口音',
        'voice', '人声', '语音', 'speech', 'communication'
    ]
    if any(kw in all_text for kw in life_science_keywords):
        # 排除产品介绍类（如"AirPods Pro 2：苹果终于下场助听器行业"）
        if re.search(r'airpods|助听器行业', title_lower):
            return '产品介绍类'
        # 进一步细分
        if any(kw in all_text for kw in ['超声', '超声波', 'b超', '医学', '生物医学']):
            return '生物医学声学'
        elif any(kw in all_text for kw in ['听觉', '听力', '听阈', '耳朵', '耳蜗', 'hearing']):
            # 排除产品介绍类（如"16万个喇叭"、"Sphere"）
            if re.search(r'sphere|16万个喇叭|拉斯维加斯', title_lower):
                return '产品介绍类'
            return '听觉科学'
        elif any(kw in all_text for kw in ['语音', 'speech', '说话', '口音', 'voice', '人声']):
            return '语音声学'
        else:
            return '生物声学'
    
    # 2. 艺术相关 (Arts)
    arts_keywords = [
        'psychoacoustics', '心理声学', '感知', '掩蔽', '临界频带',
        'music', '音乐', '音阶', '音调', '音色', '乐器', 'musical', 'instrument',
        'room acoustics', 'theater acoustics', '建筑声学', '室内声学', '房间声学',
        '混响', '消声室', '录音棚', '剧院', '剧场',
        'communication', '通信', 'communication'
    ]
    if any(kw in all_text for kw in arts_keywords):
        if any(kw in all_text for kw in ['心理声学', 'psychoacoustics', '感知', '掩蔽']):
            return '心理声学'
        elif any(kw in all_text for kw in ['音乐', 'music', '音阶', '音调', '音色', '乐器', 'musical']):
            return '音乐声学'
        elif any(kw in all_text for kw in ['建筑声学', '室内声学', '房间声学', 'room acoustics', '混响', '消声室', '录音棚']):
            return '建筑声学'
        else:
            return '通信声学'
    
    # 3. 工程相关 (Engineering)
    engineering_keywords = [
        'electro-acoustics', '电声学', 'electroacoustics',
        'ultrasonic', '超声工程', 'sonic engineering',
        'shock', 'vibration', '振动', '冲击',
        'noise', '噪声', '噪音', '降噪', '消声', '隔声', '噪声控制',
        'nvh', '汽车音频', '车载音频',
        'audio', '音频', '音质', '音效', '立体声', '空间音频', '3d音频', '虚拟声学',
        'signal processing', '信号处理', 'dsp', '采样', '采样率', 'fft', '滤波器',
        'microphone', '麦克风', 'speaker', '扬声器', '音箱', '喇叭',
        'headphone', '耳机', 'earphone', '耳返', '降噪耳机', 'anc',
        'product', '产品', '技术'
    ]
    if any(kw in all_text for kw in engineering_keywords):
        # 排除产品介绍类（已经在前面判断过了）
        if any(kw in all_text for kw in ['汽车音频', '车载音频', 'nvh', '汽车']):
            # 进一步判断：如果是产品介绍（如"嵌在汽车座椅里的音响"），归为产品介绍类
            if re.search(r'嵌在|座椅.*音响|汽车.*音响', title_lower):
                return '产品介绍类'
            return '汽车声学工程'
        elif any(kw in all_text for kw in ['噪声', 'noise', '降噪', '消声', '隔声', '噪声控制']):
            # 排除NVH（NVH归汽车声学）
            if 'nvh' not in all_text:
                return '噪声控制工程'
        elif any(kw in all_text for kw in ['信号处理', 'signal processing', 'dsp', '采样', '采样率', 'fft']):
            return '信号处理工程'
        elif any(kw in all_text for kw in ['音频', 'audio', '音质', '音效', '立体声', '空间音频', '3d音频']):
            # 排除产品介绍类
            if not re.search(r'空间音频.*普及|空间音频.*样子|杜比空间音频', title_lower):
                return '音频工程'
        elif any(kw in all_text for kw in ['麦克风', 'microphone', '扬声器', 'speaker', '音箱', '喇叭', '耳机', 'headphone']):
            # 排除产品介绍类（如"关于主动降噪耳机"）
            if not re.search(r'关于主动降噪耳机|airpods', title_lower):
                return '电声器件'
        elif any(kw in all_text for kw in ['超声工程', 'ultrasonic', 'sonic engineering']):
            return '超声工程'
        else:
            return '声学工程'
    
    # 4. 地球科学相关 (Earth sciences)
    earth_science_keywords = [
        'underwater sound', '水下声学', '水声',
        'seismic', '地震', '地震波',
        'atmosphere', '大气', '大气声学', 'sound in atmosphere',
        'oceanography', '海洋', '海', '海螺'
    ]
    if any(kw in all_text for kw in earth_science_keywords):
        if any(kw in all_text for kw in ['水下', 'underwater', '水声', '海洋', '海', '海螺']):
            return '水声学'
        elif any(kw in all_text for kw in ['地震', 'seismic', '地震波']):
            return '地震声学'
        elif any(kw in all_text for kw in ['大气', 'atmosphere', '大气声学']):
            return '大气声学'
        else:
            return '地球声学'
    
    # 5. 基础物理声学
    fundamental_keywords = [
        '声波', 'soundwave', '声压', 'sound pressure', '声强', 'sound intensity',
        '频率', 'frequency', '相位', 'phase', '振幅', 'amplitude',
        '频谱', 'spectrum', '谐波', 'harmonic', '共振', 'resonance',
        '声场', 'sound field', '声源', 'sound source', '声传播', 'sound propagation',
        '物理声学', 'fundamental physical acoustics', 'phonon', '声子'
    ]
    if any(kw in all_text for kw in fundamental_keywords):
        return '基础物理声学'
    
    # 默认：其他科普类
    return '其他科普类'


def reclassify_by_domains():
    """按照声学领域重新分类"""
    print("=" * 60)
    print("按照声学领域分类图重新分类")
    print("=" * 60)
    
    # 读取当前分类结果
    json_file = '/Users/fanyumeng/Documents/公众号/公众号文章导出/WeChat-Articles-Batch-Downloader/output/catalogs/classification_result_new_final.json'
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 收集所有文章
    all_articles = {}
    articles_info = data.get('articles', {})
    
    # 从所有分类中收集文章
    catalogs = data.get('catalogs', {})
    for catalog_name, catalog_info in catalogs.items():
        articles = catalog_info.get('articles', [])
        for article_id in articles:
            if article_id not in all_articles:
                all_articles[article_id] = {
                    'id': article_id,
                    'title': articles_info.get(article_id, {}).get('title', article_id),
                    'keywords': articles_info.get(article_id, {}).get('keywords', []),
                    'original_catalog': catalog_name
                }
    
    print(f"\n总共找到 {len(all_articles)} 篇文章")
    
    # 重新分类
    new_catalogs = defaultdict(lambda: {
        'description': '',
        'keywords': [],
        'article_count': 0,
        'articles': []
    })
    
    # 分类描述
    category_descriptions = {
        '基础物理声学': '基础物理声学：声波、声压、频率、相位等基础物理概念',
        '水声学': '地球科学 - 水声学：水下声学、海洋声学',
        '地震声学': '地球科学 - 地震声学：地震波、地震声学',
        '大气声学': '地球科学 - 大气声学：大气中的声音传播',
        '地球声学': '地球科学 - 地球声学：其他地球科学相关声学',
        '噪声控制工程': '工程 - 噪声控制工程：噪声、降噪、消声、隔声',
        '汽车声学工程': '工程 - 汽车声学工程：汽车音频、NVH',
        '信号处理工程': '工程 - 信号处理工程：数字信号处理、DSP、采样',
        '音频工程': '工程 - 音频工程：音频技术、空间音频、3D音频',
        '电声器件': '工程 - 电声器件：麦克风、扬声器、耳机等设备',
        '超声工程': '工程 - 超声工程：超声技术应用',
        '声学工程': '工程 - 声学工程：其他声学工程应用',
        '心理声学': '艺术 - 心理声学：听觉感知、心理声学',
        '音乐声学': '艺术 - 音乐声学：音乐、音阶、乐器',
        '建筑声学': '艺术/工程 - 建筑声学：房间声学、室内声学、混响',
        '通信声学': '艺术 - 通信声学：语音通信、通信技术',
        '产品介绍类': '介绍声学相关产品、技术和应用的文章',
        '听觉科学': '生命科学 - 听觉科学：听觉、听力、耳朵',
        '生物医学声学': '生命科学 - 生物医学声学：医学超声、生物医学',
        '语音声学': '生命科学 - 语音声学：语音、说话、人声',
        '生物声学': '生命科学 - 生物声学：生物声学',
        '历史系列类': '声学历史发展系列文章，介绍声学各领域的发展历程',
        '人物系列类': '介绍声学领域重要人物和专家的系列文章',
        '新闻资讯类': '声学行业新闻、会议、报告等资讯类文章',
        '基础知识类': '基础概念解释类文章，帮助读者理解声学基本概念',
        '其他科普类': '其他科普类文章',
    }
    
    print("\n正在重新分类...")
    for article_id, article_info in all_articles.items():
        title = article_info['title']
        keywords = article_info.get('keywords', [])
        
        category = classify_by_acoustic_domain(title, keywords)
        new_catalogs[category]['articles'].append(article_id)
        new_catalogs[category]['article_count'] = len(new_catalogs[category]['articles'])
        new_catalogs[category]['description'] = category_descriptions.get(category, '')
    
    # 为每个分类生成关键词（从前几篇文章中提取）
    for category, catalog_info in new_catalogs.items():
        category_keywords = []
        for article_id in catalog_info['articles'][:10]:
            if article_id in articles_info:
                keywords = articles_info[article_id].get('keywords', [])
                category_keywords.extend(keywords[:3])
        # 去重并限制数量
        category_keywords = list(dict.fromkeys(category_keywords))[:15]
        new_catalogs[category]['keywords'] = category_keywords
    
    # 打印分类统计
    print("\n分类统计：")
    for category, catalog_info in sorted(new_catalogs.items(), key=lambda x: x[1]['article_count'], reverse=True):
        print(f"  {category}: {catalog_info['article_count']} 篇")
    
    # 构建新的分类结果
    new_result = {
        'total_articles': len(all_articles),
        'total_catalogs': len(new_catalogs),
        'catalogs': dict(new_catalogs),
        'articles': articles_info
    }
    
    # 保存结果
    output_file = json_file.replace('_final.json', '_by_domains.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(new_result, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 重新分类完成！")
    print(f"输出文件: {output_file}")
    
    return output_file, new_result


if __name__ == '__main__':
    output_file, data = reclassify_by_domains()
    
    # 生成Markdown
    from convert_classification_to_markdown import convert_json_to_markdown
    md_file = convert_json_to_markdown(output_file)
    print(f"✅ Markdown文件已生成: {md_file}")

