"""
Markdown转换模块
将HTML内容转换为Markdown格式
"""
from markdownify import markdownify as md
from bs4 import BeautifulSoup


class MarkdownConverter:
    """Markdown转换器"""
    
    def __init__(self):
        # 配置markdownify的转换选项
        # 注意：不能同时使用strip和convert参数
        self.md_options = {
            'heading_style': 'ATX',  # 使用 # 格式的标题
            'bullets': '-',  # 使用 - 作为列表符号
        }
    
    def html_to_markdown(self, html_content):
        """
        将HTML转换为Markdown
        
        Args:
            html_content: HTML内容
            
        Returns:
            str: Markdown内容
        """
        # 清理HTML
        soup = BeautifulSoup(html_content, 'lxml')
        
        # 移除script和style标签
        for tag in soup(['script', 'style', 'iframe']):
            tag.decompose()
        
        # 处理图片标签，确保alt属性存在
        for img in soup.find_all('img'):
            if not img.get('alt'):
                src = img.get('src', '')
                # 使用文件名作为alt文本
                if '/' in src:
                    alt = src.split('/')[-1].split('.')[0]
                    img['alt'] = alt
                else:
                    img['alt'] = 'image'
        
        # 转换为Markdown
        html_str = str(soup)
        markdown_content = md(html_str, **self.md_options)
        
        # 后处理：清理多余的空行
        markdown_content = self._clean_markdown(markdown_content)
        
        return markdown_content
    
    def _clean_markdown(self, content):
        """
        清理Markdown内容
        
        Args:
            content: Markdown内容
            
        Returns:
            str: 清理后的Markdown内容
        """
        lines = content.split('\n')
        cleaned_lines = []
        prev_empty = False
        
        for line in lines:
            # 移除行尾空格
            line = line.rstrip()
            
            # 合并多个空行
            if not line:
                if not prev_empty:
                    cleaned_lines.append('')
                    prev_empty = True
            else:
                cleaned_lines.append(line)
                prev_empty = False
        
        # 移除开头和结尾的空行
        while cleaned_lines and not cleaned_lines[0]:
            cleaned_lines.pop(0)
        while cleaned_lines and not cleaned_lines[-1]:
            cleaned_lines.pop()
        
        return '\n'.join(cleaned_lines)
    
    def add_metadata(self, markdown_content, title, author, publish_time, url=None):
        """
        在Markdown开头添加元数据
        
        Args:
            markdown_content: Markdown内容
            title: 文章标题
            author: 作者
            publish_time: 发布时间
            url: 文章URL（可选）
            
        Returns:
            str: 添加元数据后的Markdown内容
        """
        metadata = []
        metadata.append(f"# {title}\n")
        metadata.append(f"**作者**: {author}  \n")
        metadata.append(f"**发布时间**: {publish_time}  \n")
        if url:
            metadata.append(f"**原文链接**: {url}  \n")
        metadata.append("\n---\n\n")
        
        return ''.join(metadata) + markdown_content

