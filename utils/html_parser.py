"""
HTML解析模块
用于解析微信公众号文章的HTML内容
"""
import re
from datetime import datetime
from bs4 import BeautifulSoup
import requests
from config import USER_AGENT, REQUEST_TIMEOUT, MAX_RETRIES, RETRY_DELAY
import time


class WeChatArticleParser:
    """微信公众号文章解析器"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': USER_AGENT
        })
    
    def fetch_article(self, url):
        """
        获取文章HTML内容
        
        Args:
            url: 文章URL
            
        Returns:
            str: HTML内容
        """
        for attempt in range(MAX_RETRIES):
            try:
                response = self.session.get(url, timeout=REQUEST_TIMEOUT)
                response.raise_for_status()
                # 强制使用UTF-8编码（微信文章都是UTF-8）
                response.encoding = 'utf-8'
                return response.text
            except requests.RequestException as e:
                if attempt < MAX_RETRIES - 1:
                    time.sleep(RETRY_DELAY)
                    continue
                raise Exception(f"获取文章失败: {str(e)}")
    
    def parse_article(self, html_content, url=None):
        """
        解析文章内容
        
        Args:
            html_content: HTML内容
            url: 文章URL（可选）
            
        Returns:
            dict: 包含标题、作者、时间、正文HTML的字典
        """
        soup = BeautifulSoup(html_content, 'lxml')
        
        # 提取文章标题
        title = self._extract_title(soup)
        
        # 提取作者
        author = self._extract_author(soup)
        
        # 提取发布时间
        publish_time = self._extract_publish_time(soup)
        
        # 提取正文内容
        content_html = self._extract_content(soup)
        
        return {
            'title': title,
            'author': author,
            'publish_time': publish_time,
            'content_html': content_html,
            'url': url
        }
    
    def _extract_title(self, soup):
        """提取文章标题"""
        # 尝试多种方式获取标题
        title_selectors = [
            '#activity-name',
            '.rich_media_title',
            'h1#activity-name',
            'meta[property="og:title"]',
            'title'
        ]
        
        for selector in title_selectors:
            element = soup.select_one(selector)
            if element:
                if element.name == 'meta':
                    title = element.get('content', '').strip()
                else:
                    title = element.get_text().strip()
                if title:
                    return title
        
        return "未命名文章"
    
    def _extract_author(self, soup):
        """提取作者"""
        author_selectors = [
            '#meta_content .rich_media_meta_text',
            '.rich_media_meta_text',
            'meta[name="author"]',
            '#js_name'
        ]
        
        for selector in author_selectors:
            element = soup.select_one(selector)
            if element:
                if element.name == 'meta':
                    author = element.get('content', '').strip()
                else:
                    author = element.get_text().strip()
                if author:
                    return author
        
        return "未知作者"
    
    def _extract_publish_time(self, soup):
        """提取发布时间"""
        time_selectors = [
            '#publish_time',
            '.publish_time',
            'em#publish_time',
            'meta[property="article:published_time"]'
        ]
        
        for selector in time_selectors:
            element = soup.select_one(selector)
            if element:
                if element.name == 'meta':
                    time_str = element.get('content', '').strip()
                else:
                    time_str = element.get_text().strip()
                
                if time_str:
                    # 尝试解析时间
                    try:
                        # 处理微信公众号常见的时间格式
                        time_str = time_str.replace('年', '-').replace('月', '-').replace('日', '')
                        dt = datetime.strptime(time_str, '%Y-%m-%d %H:%M')
                        return dt.strftime('%Y-%m-%d %H:%M:%S')
                    except:
                        return time_str
        
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    def _extract_content(self, soup):
        """提取正文内容"""
        # 微信公众号文章正文通常在 #js_content 中
        content_selectors = [
            '#js_content',
            '.rich_media_content',
            '#js_article'
        ]
        
        content_html = None
        for selector in content_selectors:
            element = soup.select_one(selector)
            if element:
                content_html = str(element)
                break
        
        if not content_html:
            # 如果找不到，尝试获取body内容
            body = soup.find('body')
            if body:
                content_html = str(body)
        
        if content_html:
            # 清理不需要的标签和属性
            content_soup = BeautifulSoup(content_html, 'lxml')
            
            # 移除script和style标签
            for tag in content_soup(['script', 'style', 'iframe']):
                tag.decompose()
            
            # 清理一些不需要的属性
            for tag in content_soup.find_all(True):
                # 保留必要的属性
                attrs_to_keep = ['src', 'href', 'alt', 'title']
                tag.attrs = {k: v for k, v in tag.attrs.items() 
                           if k in attrs_to_keep or k.startswith('data-')}
            
            return str(content_soup)
        
        return "<p>无法提取文章内容</p>"
    
    def get_all_images(self, html_content):
        """
        从HTML中提取所有图片URL
        
        Args:
            html_content: HTML内容
            
        Returns:
            list: 图片URL列表
        """
        soup = BeautifulSoup(html_content, 'lxml')
        images = []
        
        for img in soup.find_all('img'):
            src = img.get('src') or img.get('data-src')
            if src:
                # 处理相对URL
                if src.startswith('//'):
                    src = 'https:' + src
                elif src.startswith('/'):
                    src = 'https://mp.weixin.qq.com' + src
                images.append(src)
        
        return images

