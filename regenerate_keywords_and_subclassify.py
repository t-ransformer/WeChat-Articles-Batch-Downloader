#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
重新生成关键词并细分"常识科普类"
1. 提取声学/音频相关的技术术语关键词
2. 基于新关键词对"常识科普类"进行细分
"""

import json
import os
import re
import jieba
import jieba.analyse
from collections import defaultdict, Counter
from typing import List, Dict, Set
import sys

# 添加项目路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(project_root, 'WeChat-Articles-Batch-Downloader'))
from utils.article_reader import ArticleReader


class AcousticKeywordExtractor:
    """声学关键词提取器"""
    
    def __init__(self):
        jieba.initialize()
        
        # 声学/音频相关的专业术语词典（名词）
        self.acoustic_terms = {
            # 基础声学概念
            '声学', '声音', '声波', '声压', '声强', '声速', '声场', '声源', '声传播',
            '音频', '音质', '音色', '音调', '音量', '音效', '音域', '音阶', '音程',
            '噪声', '噪音', '降噪', '消声', '隔声', '吸声', '噪声控制',
            '频率', '频率响应', '频域', '频谱', '频带', '基频', '谐波', '共振',
            '相位', '相位差', '相位响应',
            '振幅', '幅度', '响度', '分贝', 'dB', 'SPL',
            
            # 心理声学
            '听觉', '听力', '听阈', '听觉感知', '听觉系统', '耳蜗', '耳膜', '鼓膜',
            '心理声学', '感知', '掩蔽', '临界频带',
            
            # 建筑声学
            '建筑声学', '室内声学', '房间声学', '混响', '混响时间', 'RT60',
            '消声室', '隔声室', '录音棚', '声学设计', '声学材料',
            '吸声系数', '隔声量', '声学处理',
            
            # 信号处理
            '信号处理', '数字信号处理', 'DSP', '采样', '采样率', '量化', '编码',
            'FFT', '傅里叶变换', '滤波器', '低通', '高通', '带通', '带阻',
            '脉冲响应', '频率响应', '传递函数',
            
            # 音频技术
            '立体声', '单声道', '多声道', '环绕声', '空间音频', '全景声', '杜比',
            '双耳录音', '人头录音', 'HRTF', '3D音频', '虚拟声学',
            '可听化', 'Auralization',
            
            # 音频设备
            '麦克风', '话筒', '传声器', '扬声器', '音箱', '喇叭', '耳机', '耳返',
            '监听', '监听耳机', '降噪耳机', '主动降噪', 'ANC', '被动降噪',
            '功放', '放大器', '调音台', '声卡', '音频接口',
            
            # 汽车音频
            '汽车音频', '车载音频', 'NVH', '振动', '噪声振动', '声学包',
            
            # 生物医学声学
            '超声', '超声波', '医学超声', '生物医学超声', 'B超',
            
            # 其他
            '声学仿真', '声学建模', '声学测量', '声学测试', '声学分析',
            '声学超材料', '声学材料', '声学结构',
        }
        
        # 英文声学术语
        self.acoustic_terms_en = {
            'acoustics', 'sound', 'audio', 'acoustic', 'soundwave', 'soundwave',
            'frequency', 'phase', 'amplitude', 'spectrum', 'harmonic', 'resonance',
            'noise', 'noise reduction', 'ANC', 'DSP', 'FFT', 'HRTF',
            'reverberation', 'RT60', 'absorption', 'isolation',
            'microphone', 'speaker', 'headphone', 'earphone',
            'psychoacoustics', 'perception', 'hearing', 'auditory',
            'signal processing', 'sampling', 'filter', 'equalizer',
            'stereo', 'mono', 'surround', 'spatial audio', '3D audio',
            'ultrasound', 'NVH', 'vibration',
        }
        
        # 需要排除的词
        self.exclude_words = {
            'jpg', 'png', 'gif', 'jpeg', 'image', 'images', 'http', 'https', 'www',
            'com', 'cn', 'org', 'edu', 'pdf', 'html', 'htm',
            'the', 'of', 'and', 'or', 'in', 'on', 'at', 'to', 'for', 'a', 'an',
            'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had',
            'do', 'does', 'did', 'will', 'would', 'could', 'should',
            'this', 'that', 'these', 'those', 'it', 'its', 'they', 'them',
            'we', 'you', 'he', 'she', 'his', 'her', 'our', 'your', 'their',
            'thousands', 'hundreds', 'millions', 'billion',
            'wtp', 'ipa', 'per', 'etc', 'eg', 'ie', 'vs',
        }
        
        # 数字模式（排除）
        self.number_pattern = re.compile(r'^\d+[\.\d]*[a-z]*$', re.I)
    
    def extract_acoustic_keywords(self, text: str, topK: int = 15) -> List[str]:
        """
        提取声学/音频相关的关键词
        
        Args:
            text: 文本内容
            topK: 返回前K个关键词
            
        Returns:
            List[str]: 关键词列表（只包含声学相关的技术术语）
        """
        if not text or len(text.strip()) < 10:
            return []
        
        # 清理文本
        cleaned_text = self._clean_text(text)
        
        # 提取所有可能的关键词
        all_keywords = jieba.analyse.extract_tags(
            cleaned_text, 
            topK=topK * 3,  # 提取更多，然后过滤
            withWeight=False
        )
        
        # 过滤关键词
        acoustic_keywords = []
        seen = set()
        
        for kw in all_keywords:
            kw_lower = kw.lower().strip()
            
            # 跳过已见过的词
            if kw_lower in seen:
                continue
            
            # 排除停用词和无意义词
            if kw_lower in self.exclude_words:
                continue
            
            # 排除纯数字
            if self.number_pattern.match(kw):
                continue
            
            # 排除短数字（可能是图片编号）
            if len(kw) <= 2 and kw.isdigit():
                continue
            
            # 排除文件扩展名
            if kw_lower in ['jpg', 'png', 'gif', 'jpeg', 'pdf', 'html']:
                continue
            
            # 检查是否是声学术语
            is_acoustic = False
            
            # 检查中文声学术语
            if any(term in kw for term in self.acoustic_terms):
                is_acoustic = True
            
            # 检查英文声学术语（完整匹配或包含）
            for term in self.acoustic_terms_en:
                if term.lower() in kw_lower or kw_lower in term.lower():
                    is_acoustic = True
                    break
            
            # 检查是否包含声学相关的常见词根
            acoustic_roots = ['声', '音', '噪', '频', '波', '听', '耳', '响', '振']
            if any(root in kw for root in acoustic_roots):
                is_acoustic = True
            
            # 检查英文词是否看起来像技术术语（长度>=4，包含常见技术词根）
            if len(kw) >= 4 and any(root in kw_lower for root in ['acoust', 'audio', 'sound', 'noise', 'freq', 'phase', 'spectr', 'audio']):
                is_acoustic = True
            
            # 如果是声学相关且是名词（通过长度和特征判断）
            if is_acoustic:
                # 只保留长度>=2的词（排除单字，除非是专业术语）
                if len(kw) >= 2:
                    acoustic_keywords.append(kw)
                    seen.add(kw_lower)
                    if len(acoustic_keywords) >= topK:
                        break
        
        return acoustic_keywords[:topK]
    
    def _clean_text(self, text: str) -> str:
        """清理文本"""
        # 移除图片引用
        text = re.sub(r'!\[.*?\]\([^\)]+\)', '', text)
        # 移除链接
        text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
        # 移除图片路径
        text = re.sub(r'images/[^\s\)]+', '', text)
        # 移除URL
        text = re.sub(r'https?://[^\s\)]+', '', text)
        # 移除邮箱
        text = re.sub(r'\S+@\S+', '', text)
        # 移除3位以上数字（可能是图片编号）
        text = re.sub(r'\b\d{3,}\b', '', text)
        # 移除特殊字符但保留中英文和基本标点
        text = re.sub(r'[^\w\s\u4e00-\u9fff，。！？；：、]', ' ', text)
        return text


def regenerate_keywords_for_all_articles():
    """为所有文章重新生成关键词"""
    print("=" * 60)
    print("重新生成关键词")
    print("=" * 60)
    
    # 读取分类结果
    json_file = '/Users/fanyumeng/Documents/公众号/公众号文章导出/WeChat-Articles-Batch-Downloader/output/catalogs/classification_result_new.json'
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 读取所有文章
    markdown_dir = '/Users/fanyumeng/Documents/公众号/公众号文章导出/WeChat-Articles-Batch-Downloader/output/markdown'
    reader = ArticleReader(markdown_dir)
    articles = reader.read_all_articles()
    
    # 创建文章ID到文章内容的映射
    article_map = {article['id']: article for article in articles}
    
    # 初始化关键词提取器
    extractor = AcousticKeywordExtractor()
    
    # 重新提取关键词
    print("\n正在提取关键词...")
    updated_count = 0
    
    for article_id, article_info in data.get('articles', {}).items():
        if article_id in article_map:
            article = article_map[article_id]
            text_content = article.get('text_content', '')
            
            # 提取新关键词
            new_keywords = extractor.extract_acoustic_keywords(text_content, topK=15)
            
            # 更新文章信息
            article_info['keywords'] = new_keywords
            updated_count += 1
            
            if updated_count % 20 == 0:
                print(f"已处理 {updated_count} 篇文章...")
    
    print(f"\n✅ 已为 {updated_count} 篇文章重新生成关键词")
    
    # 保存更新后的分类结果
    output_file = json_file.replace('.json', '_with_new_keywords.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 已保存到: {output_file}")
    return output_file, data


def subclassify_popular_science(data: Dict) -> Dict:
    """
    对"常识科普类"进行细分
    
    Args:
        data: 分类结果数据
        
    Returns:
        Dict: 更新后的分类结果
    """
    print("\n" + "=" * 60)
    print("细分'常识科普类'")
    print("=" * 60)
    
    # 获取"常识科普类"的所有文章
    catalogs = data.get('catalogs', {})
    pop_science_articles = catalogs.get('常识科普类', {}).get('articles', [])
    
    if not pop_science_articles:
        print("未找到'常识科普类'文章")
        return data
    
    print(f"找到 {len(pop_science_articles)} 篇'常识科普类'文章")
    
    # 收集所有文章的关键词
    articles_info = data.get('articles', {})
    article_keywords_map = {}
    
    for article_id in pop_science_articles:
        if article_id in articles_info:
            keywords = articles_info[article_id].get('keywords', [])
            article_keywords_map[article_id] = keywords
    
    # 基于关键词进行聚类
    # 统计关键词频率
    keyword_freq = Counter()
    for keywords in article_keywords_map.values():
        for kw in keywords:
            keyword_freq[kw] += 1
    
    # 找出高频关键词作为分类依据
    common_keywords = [kw for kw, freq in keyword_freq.most_common(30) if freq >= 2]
    print(f"\n高频关键词: {', '.join(common_keywords[:20])}")
    
    # 基于关键词对文章进行分组
    subcategories = defaultdict(list)
    unclassified = []
    
    # 定义子分类规则（基于关键词）
    category_rules = {
        '听觉感知类': ['听觉', '听力', '听阈', '感知', '心理声学', '掩蔽', '临界频带', 'HRTF'],
        '声音传播类': ['声波', '声传播', '声场', '声源', '相位', '频率', '频谱', '共振'],
        '噪声控制类': ['噪声', '噪音', '降噪', '消声', '隔声', '吸声', '噪声控制', 'NVH'],
        '建筑声学类': ['建筑声学', '室内声学', '房间声学', '混响', '消声室', '隔声室', '录音棚', '声学材料'],
        '音频技术类': ['音频', '音质', '音色', '音效', '立体声', '空间音频', '3D音频', '虚拟声学', '可听化'],
        '信号处理类': ['信号处理', 'DSP', '采样', '采样率', 'FFT', '滤波器', '频率响应', '脉冲响应'],
        '音频设备类': ['麦克风', '扬声器', '音箱', '喇叭', '耳机', '耳返', '监听', '降噪耳机', 'ANC'],
        '汽车音频类': ['汽车音频', '车载音频', 'NVH', '振动', '声学包'],
        '生物医学声学类': ['超声', '超声波', '医学超声', '生物医学超声', 'B超'],
        '声学测量类': ['声学测量', '声学测试', '声学分析', '声学仿真', '声学建模'],
    }
    
    # 对每篇文章进行分类
    for article_id in pop_science_articles:
        keywords = article_keywords_map.get(article_id, [])
        keyword_set = set(k.lower() for k in keywords)
        
        # 计算每个类别的匹配分数
        category_scores = {}
        for category, category_keywords in category_rules.items():
            score = sum(1 for kw in category_keywords if kw.lower() in keyword_set)
            if score > 0:
                category_scores[category] = score
        
        # 选择得分最高的类别
        if category_scores:
            best_category = max(category_scores.items(), key=lambda x: x[1])[0]
            subcategories[best_category].append(article_id)
        else:
            unclassified.append(article_id)
    
    # 打印分类结果
    print("\n细分结果：")
    for category, articles in sorted(subcategories.items(), key=lambda x: len(x[1]), reverse=True):
        print(f"  {category}: {len(articles)} 篇")
    
    if unclassified:
        print(f"  未分类: {len(unclassified)} 篇")
    
    # 更新分类结果
    # 移除原来的"常识科普类"
    if '常识科普类' in catalogs:
        del catalogs['常识科普类']
    
    # 添加新的子分类
    for category, articles in subcategories.items():
        # 获取这些文章的关键词作为分类关键词
        category_keywords = []
        for article_id in articles[:5]:  # 只取前5篇的关键词
            if article_id in articles_info:
                category_keywords.extend(articles_info[article_id].get('keywords', [])[:3])
        
        # 去重并限制数量
        category_keywords = list(dict.fromkeys(category_keywords))[:10]
        
        catalogs[category] = {
            'description': f'常识科普类 - {category}',
            'keywords': category_keywords,
            'article_count': len(articles),
            'articles': articles
        }
    
    # 如果有未分类的文章，创建一个"其他科普类"
    if unclassified:
        catalogs['其他科普类'] = {
            'description': '常识科普类 - 其他',
            'keywords': [],
            'article_count': len(unclassified),
            'articles': unclassified
        }
    
    # 更新总数
    data['total_catalogs'] = len(catalogs)
    
    return data


if __name__ == '__main__':
    # 第一步：重新生成关键词
    new_json_file, data = regenerate_keywords_for_all_articles()
    
    # 第二步：细分"常识科普类"
    updated_data = subclassify_popular_science(data)
    
    # 保存最终结果
    final_output = new_json_file.replace('_with_new_keywords.json', '_final.json')
    with open(final_output, 'w', encoding='utf-8') as f:
        json.dump(updated_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 最终结果已保存到: {final_output}")
    
    # 生成Markdown
    from convert_classification_to_markdown import convert_json_to_markdown
    md_file = convert_json_to_markdown(final_output)
    print(f"✅ Markdown文件已生成: {md_file}")

