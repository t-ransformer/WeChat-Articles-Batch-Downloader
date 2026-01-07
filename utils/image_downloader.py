"""
图片下载模块
用于下载文章中的图片并更新路径
"""
import os
import re
import time
import requests
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from config import (
    IMAGES_DIR, USER_AGENT, 
    IMAGE_TIMEOUT, IMAGE_MAX_SIZE, INVALID_CHARS
)


class ImageDownloader:
    """图片下载器"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': USER_AGENT
        })
        
        # 确保图片目录存在
        os.makedirs(IMAGES_DIR, exist_ok=True)
    
    def sanitize_filename(self, filename):
        """
        清理文件名，移除非法字符
        
        Args:
            filename: 原始文件名
            
        Returns:
            str: 清理后的文件名
        """
        for char in INVALID_CHARS:
            filename = filename.replace(char, '_')
        # 移除多余的空格和下划线
        filename = re.sub(r'[_\s]+', '_', filename)
        return filename.strip('_')
    
    def get_image_extension(self, url, content_type=None):
        """
        获取图片扩展名
        
        Args:
            url: 图片URL
            content_type: HTTP响应中的Content-Type
            
        Returns:
            str: 扩展名（如 .jpg）
        """
        # 从Content-Type获取
        if content_type:
            type_map = {
                'image/jpeg': '.jpg',
                'image/jpg': '.jpg',
                'image/png': '.png',
                'image/gif': '.gif',
                'image/webp': '.webp',
                'image/bmp': '.bmp'
            }
            if content_type in type_map:
                return type_map[content_type]
        
        # 从URL获取
        parsed = urlparse(url)
        path = parsed.path
        if '.' in path:
            ext = os.path.splitext(path)[1].lower()
            if ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp']:
                return ext
        
        # 默认返回.jpg
        return '.jpg'
    
    def download_image(self, url, save_path):
        """
        下载单张图片
        
        Args:
            url: 图片URL
            save_path: 保存路径
            
        Returns:
            bool: 是否成功
        """
        try:
            response = self.session.get(url, timeout=IMAGE_TIMEOUT, stream=True)
            response.raise_for_status()
            
            # 检查文件大小
            content_length = response.headers.get('Content-Length')
            if content_length and int(content_length) > IMAGE_MAX_SIZE:
                print(f"警告: 图片过大，跳过 {url}")
                return False
            
            # 下载图片
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            # 验证文件大小
            if os.path.getsize(save_path) > IMAGE_MAX_SIZE:
                os.remove(save_path)
                print(f"警告: 下载的图片过大，已删除 {save_path}")
                return False
            
            return True
        except Exception as e:
            print(f"下载图片失败 {url}: {str(e)}")
            return False
    
    def download_images_from_html(self, html_content, article_dir, article_index=0):
        """
        从HTML中提取并下载所有图片
        
        Args:
            html_content: HTML内容
            article_dir: 文章所在目录（图片保存到这里）
            article_index: 文章索引（用于区分多篇文章）
            
        Returns:
            tuple: (更新后的HTML内容, 图片路径映射字典)
        """
        soup = BeautifulSoup(html_content, 'lxml')
        images = soup.find_all('img')
        
        image_map = {}  # 原始URL -> 本地路径的映射
        image_counter = 0
        
        for img in images:
            src = img.get('src') or img.get('data-src')
            if not src:
                continue
            
            # 处理相对URL
            original_src = src
            if src.startswith('//'):
                src = 'https:' + src
            elif src.startswith('/'):
                src = 'https://mp.weixin.qq.com' + src
            
            # 跳过data URI和内联图片
            if src.startswith('data:'):
                continue
            
            # 如果已经下载过，直接使用
            if original_src in image_map:
                local_path = image_map[original_src]
            else:
                # 下载图片
                image_counter += 1
                ext = self.get_image_extension(src)
                # 使用简单的数字编号
                filename = f"{image_counter}{ext}"
                save_path = os.path.join(article_dir, filename)
                
                if self.download_image(src, save_path):
                    # 使用相对路径（图片和markdown在同一目录）
                    local_path = filename
                    image_map[original_src] = local_path
                    # 也映射处理后的URL
                    if src != original_src:
                        image_map[src] = local_path
                else:
                    # 下载失败，保持原URL
                    local_path = original_src
            
            # 更新img标签的src
            img['src'] = local_path
            # 移除data-src属性（如果存在）
            if 'data-src' in img.attrs:
                del img['data-src']
        
        return str(soup), image_map
    
    def update_html_images(self, html_content, image_map):
        """
        更新HTML中的图片路径
        
        Args:
            html_content: HTML内容
            image_map: 图片路径映射字典
            
        Returns:
            str: 更新后的HTML内容
        """
        soup = BeautifulSoup(html_content, 'lxml')
        
        for img in soup.find_all('img'):
            src = img.get('src') or img.get('data-src')
            if src and src in image_map:
                img['src'] = image_map[src]
                if 'data-src' in img.attrs:
                    del img['data-src']
        
        return str(soup)

