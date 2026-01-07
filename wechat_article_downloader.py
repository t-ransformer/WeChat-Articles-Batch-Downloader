#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
微信公众号文章批量下载工具
主程序
"""
import os
import sys
import argparse
from datetime import datetime
from config import MARKDOWN_DIR, INVALID_CHARS
from utils.html_parser import WeChatArticleParser
from utils.image_downloader import ImageDownloader
from utils.markdown_converter import MarkdownConverter


class WeChatArticleDownloader:
    """微信公众号文章下载器"""
    
    def __init__(self):
        self.parser = WeChatArticleParser()
        self.image_downloader = ImageDownloader()
        self.markdown_converter = MarkdownConverter()
        
        # 确保输出目录存在
        os.makedirs(MARKDOWN_DIR, exist_ok=True)
    
    def sanitize_filename(self, filename):
        """清理文件名"""
        for char in INVALID_CHARS:
            filename = filename.replace(char, '_')
        # 移除多余的空格和下划线
        import re
        filename = re.sub(r'[_\s]+', '_', filename)
        return filename.strip('_')
    
    def save_markdown(self, markdown_content, title, publish_time):
        """
        保存Markdown文件
        
        Args:
            markdown_content: Markdown内容
            title: 文章标题
            publish_time: 发布时间
        """
        # 格式化时间用于文件名
        try:
            dt = datetime.strptime(publish_time, '%Y-%m-%d %H:%M:%S')
            time_str = dt.strftime('%Y%m%d_%H%M%S')
        except:
            time_str = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # 使用简单的时间戳+索引作为文件名，避免中文编码问题
        # 标题保存在文件内容中，文件名只用时间戳
        filename = f"article_{time_str}.md"
        filepath = os.path.join(MARKDOWN_DIR, filename)
        
        # 确保内容以UTF-8编码保存
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        return filepath
    
    def _is_article_downloaded(self, url):
        """
        检查文章是否已下载
        
        Args:
            url: 文章URL
            
        Returns:
            bool: 是否已下载
        """
        # 从URL中提取文章ID
        from urllib.parse import urlparse
        try:
            parsed = urlparse(url)
            article_id = parsed.path.split('/s/')[-1] if '/s/' in parsed.path else None
            if not article_id:
                return False
        except:
            return False
        
        # 检查Markdown文件中是否包含这个URL
        if os.path.exists(MARKDOWN_DIR):
            for filename in os.listdir(MARKDOWN_DIR):
                if filename.endswith('.md'):
                    filepath = os.path.join(MARKDOWN_DIR, filename)
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            content = f.read()
                            if article_id in content or url in content:
                                return True
                    except:
                        continue
        return False
    
    def download_article(self, url, article_index=0, skip_existing=True):
        """
        下载单篇文章
        
        Args:
            url: 文章URL
            article_index: 文章索引
            skip_existing: 是否跳过已存在的文件（默认True）
            
        Returns:
            dict: 下载结果
        """
        # 检查是否已下载
        if skip_existing and self._is_article_downloaded(url):
            print(f"\n[{article_index + 1}] 跳过（已存在）: {url}")
            return {
                'success': True,
                'skipped': True,
                'url': url,
                'message': '文件已存在，已跳过'
            }
        
        try:
            print(f"\n[{article_index + 1}] 正在处理: {url}")
            
            # 1. 获取文章HTML
            print("  获取文章内容...")
            html_content = self.parser.fetch_article(url)
            
            # 2. 解析文章
            print("  解析文章信息...")
            article_data = self.parser.parse_article(html_content, url)
            title = article_data['title']
            author = article_data['author']
            publish_time = article_data['publish_time']
            content_html = article_data['content_html']
            
            print(f"  标题: {title}")
            print(f"  作者: {author}")
            print(f"  时间: {publish_time}")
            
            # 3. 创建文章目录（用"标题_作者"命名）
            # 清理文件名中的非法字符
            safe_title = self.sanitize_filename(title)
            safe_author = self.sanitize_filename(author)
            
            # 如果标题+作者太长，截断标题但保留完整作者名
            max_title_len = 50 - len(safe_author) - 1  # 减1是为了下划线
            if max_title_len < 10:
                max_title_len = 40  # 最少保留40字符给标题
            if len(safe_title) > max_title_len:
                safe_title = safe_title[:max_title_len]
            
            article_dir_name = f"{safe_title}_{safe_author}"
            article_dir = os.path.join(MARKDOWN_DIR, article_dir_name)
            os.makedirs(article_dir, exist_ok=True)
            
            # 4. 下载图片到文章目录
            print("  下载图片...")
            content_html, image_map = self.image_downloader.download_images_from_html(
                content_html, article_dir, article_index
            )
            print(f"  已下载 {len(image_map)} 张图片")
            
            # 5. 转换为Markdown
            print("  转换为Markdown...")
            markdown_content = self.markdown_converter.html_to_markdown(content_html)
            markdown_content = self.markdown_converter.add_metadata(
                markdown_content, title, author, publish_time, url
            )
            
            # 6. 保存Markdown文件到文章目录
            print("  保存文件...")
            md_filename = "article.md"
            md_path = os.path.join(article_dir, md_filename)
            with open(md_path, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            
            print(f"  ✓ 已保存到: {article_dir}")
            
            return {
                'success': True,
                'skipped': False,
                'title': title,
                'url': url,
                'article_dir': article_dir,
                'images_count': len(image_map)
            }
            
        except Exception as e:
            print(f"  ✗ 处理失败: {str(e)}")
            return {
                'success': False,
                'url': url,
                'error': str(e)
            }
    
    def download_from_file(self, file_path):
        """
        从文件读取URL列表并批量下载
        
        Args:
            file_path: URL列表文件路径（每行一个URL）
        """
        if not os.path.exists(file_path):
            print(f"错误: 文件不存在 {file_path}")
            return
        
        # 读取URL列表
        urls = []
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                url = line.strip()
                if url and url.startswith('http'):
                    urls.append(url)
        
        if not urls:
            print("错误: 文件中没有找到有效的URL")
            return
        
        print(f"找到 {len(urls)} 篇文章，开始下载...")
        print("=" * 60)
        
        # 统计已存在的文件
        skipped_count = 0
        results = []
        for i, url in enumerate(urls):
            result = self.download_article(url, i, skip_existing=True)
            results.append(result)
            if result.get('skipped'):
                skipped_count += 1
        
        if skipped_count > 0:
            print(f"\n已跳过 {skipped_count} 篇已存在的文章")
        
        # 打印统计信息
        self._print_summary(results)
    
    def download_from_urls(self, urls):
        """
        从URL列表批量下载
        
        Args:
            urls: URL列表
        """
        if not urls:
            print("错误: URL列表为空")
            return
        
        print(f"开始下载 {len(urls)} 篇文章...")
        print("=" * 60)
        
        skipped_count = 0
        results = []
        for i, url in enumerate(urls):
            result = self.download_article(url, i, skip_existing=True)
            results.append(result)
            if result.get('skipped'):
                skipped_count += 1
        
        if skipped_count > 0:
            print(f"\n已跳过 {skipped_count} 篇已存在的文章")
        
        # 打印统计信息
        self._print_summary(results)
    
    def _print_summary(self, results):
        """打印下载统计信息"""
        print("\n" + "=" * 60)
        print("下载完成！")
        print("=" * 60)
        
        success_count = sum(1 for r in results if r['success'] and not r.get('skipped', False))
        skipped_count = sum(1 for r in results if r.get('skipped', False))
        fail_count = len(results) - success_count - skipped_count
        
        print(f"总计: {len(results)} 篇")
        print(f"新下载: {success_count} 篇")
        print(f"已跳过: {skipped_count} 篇")
        print(f"失败: {fail_count} 篇")
        
        if fail_count > 0:
            print("\n失败的URL:")
            for r in results:
                if not r['success']:
                    print(f"  - {r['url']}: {r.get('error', '未知错误')}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='微信公众号文章批量下载工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 从Excel文件一键下载（推荐，最简单）
  python wechat_article_downloader.py 微信公众号文章.xlsx
  
  # 从文件读取URL列表
  python wechat_article_downloader.py -f urls.txt
  
  # 直接指定单个URL
  python wechat_article_downloader.py -u "https://mp.weixin.qq.com/s/xxx"
  
  # 指定多个URL
  python wechat_article_downloader.py -u "url1" "url2" "url3"
        """
    )
    
    parser.add_argument(
        'input',
        nargs='?',
        help='Excel文件路径（从wechat-exporter导出）或URL列表文件'
    )
    
    parser.add_argument(
        '-f', '--file',
        help='包含URL列表的文件路径（每行一个URL）'
    )
    
    parser.add_argument(
        '-u', '--urls',
        nargs='+',
        help='文章URL（可以指定多个）'
    )
    
    args = parser.parse_args()
    
    downloader = WeChatArticleDownloader()
    
    # 如果第一个参数是Excel文件，自动处理
    if args.input and args.input.endswith(('.xlsx', '.xls')):
        print("=" * 60)
        print("检测到Excel文件，自动提取URL并下载...")
        print("=" * 60)
        from extract_urls_from_excel import extract_urls_from_excel
        import tempfile
        
        temp_urls_file = os.path.join(tempfile.gettempdir(), 'wechat_urls_temp.txt')
        urls = extract_urls_from_excel(args.input, temp_urls_file)
        
        if urls and len(urls) > 0:
            print(f"\n成功提取 {len(urls)} 个URL，开始下载...\n")
            downloader.download_from_file(temp_urls_file)
            # 清理临时文件
            if os.path.exists(temp_urls_file):
                os.remove(temp_urls_file)
        else:
            print("错误: 未能从Excel文件中提取到任何URL")
            sys.exit(1)
    elif args.file:
        downloader.download_from_file(args.file)
    elif args.urls:
        downloader.download_from_urls(args.urls)
    elif args.input and os.path.exists(args.input):
        # 如果输入是普通文本文件，当作URL列表文件处理
        downloader.download_from_file(args.input)
    else:
        parser.print_help()
        print("\n错误: 请指定Excel文件、-f 或 -u 参数")
        sys.exit(1)


if __name__ == '__main__':
    main()

