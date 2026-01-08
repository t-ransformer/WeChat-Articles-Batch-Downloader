#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
合并NVH相关文章和音频工程相关文章
1. 将所有NVH、汽车、噪声相关的文章合并到"NVH"分类
2. 将音频工程相关的文章（包括拉斯维加斯球、汽车座椅里的音响等）合并到"音频工程"分类
"""

import json
import os
import re
from collections import defaultdict


def merge_catalogs():
    """合并分类"""
    print("=" * 60)
    print("合并NVH和音频工程分类")
    print("=" * 60)
    
    # 读取当前分类结果
    json_file = '/Users/fanyumeng/Documents/公众号/公众号文章导出/WeChat-Articles-Batch-Downloader/output/catalogs/classification_result_new_by_domains.json'
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    catalogs = data.get('catalogs', {})
    articles_info = data.get('articles', {})
    
    # 收集所有文章
    all_articles = {}
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
    
    # 创建新的分类
    new_catalogs = {}
    
    # 1. 收集NVH相关文章
    nvh_articles = []
    nvh_keywords = []
    
    # 需要合并的分类
    catalogs_to_merge_nvh = ['噪声控制工程', '汽车声学工程']
    
    for catalog_name in catalogs_to_merge_nvh:
        if catalog_name in catalogs:
            articles = catalogs[catalog_name].get('articles', [])
            nvh_articles.extend(articles)
            print(f"  从 '{catalog_name}' 合并 {len(articles)} 篇文章到 NVH")
    
    # 从其他分类中查找NVH相关的文章（更精确的匹配）
    # NVH相关：明确提到NVH，或者汽车+噪声/振动组合
    for article_id, article_info in all_articles.items():
        title = article_info['title'].lower()
        keywords = [k.lower() for k in article_info.get('keywords', [])]
        all_text = title + ' ' + ' '.join(keywords)
        
        # 排除已经在NVH列表中的文章
        if article_id in nvh_articles:
            continue
        
        # 明确提到NVH
        is_nvh = False
        if 'nvh' in all_text:
            is_nvh = True
        # 汽车 + 噪声/振动组合
        elif ('汽车' in all_text or '车载' in all_text) and ('噪声' in all_text or '噪音' in all_text or '振动' in all_text or 'nvh' in all_text):
            is_nvh = True
        # 汽车音频相关的噪声控制（如"为什么很多汽车工程师都说NVH是玄学"）
        elif re.search(r'汽车.*nvh|汽车.*噪声|汽车.*噪音', all_text):
            is_nvh = True
        
        if is_nvh:
            nvh_articles.append(article_id)
            print(f"  发现NVH相关文章: {article_info['title']}")
    
    # 去重
    nvh_articles = list(dict.fromkeys(nvh_articles))
    
    # 收集NVH分类的关键词
    for article_id in nvh_articles[:10]:
        if article_id in articles_info:
            keywords = articles_info[article_id].get('keywords', [])
            nvh_keywords.extend(keywords[:3])
    nvh_keywords = list(dict.fromkeys(nvh_keywords))[:15]
    
    # 重新收集NVH的关键词（因为文章列表可能已调整）
    nvh_keywords = []
    for article_id in nvh_articles[:10]:
        if article_id in articles_info:
            keywords = articles_info[article_id].get('keywords', [])
            nvh_keywords.extend(keywords[:3])
    nvh_keywords = list(dict.fromkeys(nvh_keywords))[:15]
    
    new_catalogs['NVH'] = {
        'description': 'NVH（噪声、振动与声振粗糙度）：汽车NVH、噪声控制、振动控制',
        'keywords': nvh_keywords,
        'article_count': len(nvh_articles),
        'articles': nvh_articles
    }
    
    print(f"\n✅ NVH分类: {len(nvh_articles)} 篇文章")
    
    # 从NVH中移除应该属于音频工程的文章（汽车音频相关但不是NVH的）
    nvh_to_move = []
    for article_id in nvh_articles[:]:
        article_info = all_articles.get(article_id)
        if not article_info:
            continue
        title = article_info['title'].lower()
        keywords = [k.lower() for k in article_info.get('keywords', [])]
        all_text = title + ' ' + ' '.join(keywords)
        
        # 如果标题明确提到"汽车音频"或"音频"，应该归音频工程（除非标题明确提到NVH）
        if '汽车音频' in title or ('汽车' in title and '音频' in title):
            # 标题中没有明确提到NVH的，归音频工程
            if 'nvh' not in title:
                nvh_to_move.append(article_id)
                nvh_articles.remove(article_id)
                print(f"  从NVH移到音频工程: {article_info['title']}")
        # 如果是汽车+声音/音频相关（但不是噪声/振动），也应该归音频工程
        elif ('汽车' in title and ('音频' in title or '声音' in title)) and 'nvh' not in title:
            # 标题中没有明确提到噪声/振动的，归音频工程
            if '噪声' not in title and '噪音' not in title and '振动' not in title:
                nvh_to_move.append(article_id)
                nvh_articles.remove(article_id)
                print(f"  从NVH移到音频工程: {article_info['title']}")
    
    print(f"  调整后NVH分类: {len(nvh_articles)} 篇文章")
    
    # 2. 收集音频工程相关文章
    audio_engineering_articles = []
    audio_keywords = []
    
    # 需要合并的分类
    catalogs_to_merge_audio = ['音频工程', '产品介绍类']
    
    for catalog_name in catalogs_to_merge_audio:
        if catalog_name in catalogs:
            articles = catalogs[catalog_name].get('articles', [])
            audio_engineering_articles.extend(articles)
            print(f"  从 '{catalog_name}' 合并 {len(articles)} 篇文章到 音频工程")
    
    # 从其他分类中查找音频工程相关的文章（更精确的匹配）
    audio_keywords_pattern = [
        r'sphere|拉斯维加斯|16万个喇叭',
        r'汽车座椅.*音响|嵌在.*音响',
        r'软件定义音频|汽车音频最好的时代',
        r'空间音频.*普及|空间音频.*样子|杜比空间音频',
        r'3d音频|虚拟声学|音频技术'
    ]
    
    for article_id, article_info in all_articles.items():
        title = article_info['title'].lower()
        keywords = [k.lower() for k in article_info.get('keywords', [])]
        all_text = title + ' ' + ' '.join(keywords)
        
        # 排除已经在音频工程列表中的文章
        if article_id in audio_engineering_articles:
            continue
        
        # 检查是否包含音频工程相关关键词
        if any(re.search(kw, all_text) for kw in audio_keywords_pattern):
            # 排除NVH相关的（已经在NVH分类中）
            if article_id not in nvh_articles:
                audio_engineering_articles.append(article_id)
                print(f"  发现音频工程相关文章: {article_info['title']}")
    
    # 添加从NVH移过来的文章
    audio_engineering_articles.extend(nvh_to_move)
    
    # 去重
    audio_engineering_articles = list(dict.fromkeys(audio_engineering_articles))
    
    # 收集音频工程分类的关键词
    for article_id in audio_engineering_articles[:10]:
        if article_id in articles_info:
            keywords = articles_info[article_id].get('keywords', [])
            audio_keywords.extend(keywords[:3])
    audio_keywords = list(dict.fromkeys(audio_keywords))[:15]
    
    new_catalogs['音频工程'] = {
        'description': '音频工程：音频技术、空间音频、3D音频、音频产品、音频系统',
        'keywords': audio_keywords,
        'article_count': len(audio_engineering_articles),
        'articles': audio_engineering_articles
    }
    
    print(f"\n✅ 音频工程分类: {len(audio_engineering_articles)} 篇文章")
    
    # 3. 保留其他分类（排除已合并的分类）
    excluded_catalogs = set(catalogs_to_merge_nvh + catalogs_to_merge_audio)
    
    for catalog_name, catalog_info in catalogs.items():
        if catalog_name not in excluded_catalogs:
            new_catalogs[catalog_name] = catalog_info
    
    # 打印分类统计
    print("\n最终分类统计：")
    for category, catalog_info in sorted(new_catalogs.items(), key=lambda x: x[1]['article_count'], reverse=True):
        print(f"  {category}: {catalog_info['article_count']} 篇")
    
    # 构建新的分类结果
    new_result = {
        'total_articles': len(all_articles),
        'total_catalogs': len(new_catalogs),
        'catalogs': new_catalogs,
        'articles': articles_info
    }
    
    # 保存结果
    output_file = json_file.replace('_by_domains.json', '_merged.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(new_result, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 合并完成！")
    print(f"输出文件: {output_file}")
    
    return output_file, new_result


if __name__ == '__main__':
    output_file, data = merge_catalogs()
    
    # 生成Markdown
    from convert_classification_to_markdown import convert_json_to_markdown
    md_file = convert_json_to_markdown(output_file)
    print(f"✅ Markdown文件已生成: {md_file}")

