"""
Markdown转换模块
将HTML内容转换为Markdown格式
"""
import re
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
        
        # 处理MathJax公式：提取LaTeX源码并替换为Markdown格式
        self._extract_and_replace_formulas(soup)
        
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
        
        # 修复公式中的转义字符
        # markdownify可能会转义特殊字符，我们需要在公式内部还原它们
        import re
        
        # 1. 修复行内公式中的转义：$...$ 内的转义字符
        def fix_inline_formula(match):
            formula_content = match.group(1)
            # 还原转义的特殊字符（markdownify可能会转义这些字符）
            formula_content = formula_content.replace('\\_', '_')  # 下划线
            formula_content = formula_content.replace('\\$', '$')  # 美元符号
            formula_content = formula_content.replace('\\*', '*')  # 星号（乘法符号）
            # 还原LaTeX命令的转义
            import re
            # 匹配所有反斜杠+字母的命令，将\\command替换为\command
            formula_content = re.sub(r'\\\\([a-zA-Z]+)', r'\\\1', formula_content)
            # 清理非断行空格
            formula_content = formula_content.replace('\xa0', ' ')
            return f'${formula_content}$'
        
        # 匹配行内公式 $...$，但排除块级公式的$$
        # 允许前面有空白字符
        markdown_content = re.sub(r'[ \xa0]*\$([^$\n]+?)\$', fix_inline_formula, markdown_content)
        
        # 2. 修复块级公式中的转义：$$...$$ 内的转义字符
        def fix_block_formula(match):
            formula_content = match.group(1)
            # 还原转义的特殊字符
            formula_content = formula_content.replace('\\_', '_')  # 下划线
            formula_content = formula_content.replace('\\$', '$')  # 美元符号
            formula_content = formula_content.replace('\\*', '*')  # 星号（乘法符号）
            # 还原LaTeX命令的转义（markdownify可能会转义反斜杠）
            # 使用正则表达式匹配所有LaTeX命令（\command格式），将\\command替换为\command
            import re
            # 匹配所有反斜杠+字母的命令，如 \frac, \sqrt, \sum 等
            formula_content = re.sub(r'\\\\([a-zA-Z]+)', r'\\\1', formula_content)
            # 清理首尾空白和非断行空格
            formula_content = formula_content.strip().replace('\xa0', ' ')
            return f'$$\n{formula_content}\n$$'
        
        # 匹配块级公式 $$...$$，允许前面有空白字符
        markdown_content = re.sub(r'[ \xa0]*\$\$\s*\n(.*?)\n\s*\$\$', fix_block_formula, markdown_content, flags=re.DOTALL)
        
        # 修复图片路径：markdown文件在markdown/目录，图片在images/目录
        # 需要将 images/ 改为 ../images/
        markdown_content = re.sub(r'!\[([^\]]*)\]\(images/([^)]+)\)', r'![\1](../images/\2)', markdown_content)
        
        # 后处理：清理多余的空行
        markdown_content = self._clean_markdown(markdown_content)
        
        return markdown_content
    
    def _extract_and_replace_formulas(self, soup):
        """
        提取MathJax公式并替换为Markdown LaTeX格式
        
        Args:
            soup: BeautifulSoup对象
        """
        # 查找所有mjx-container标签
        mjx_containers = soup.find_all('mjx-container')
        
        for mjx in mjx_containers:
            # 获取data-formula属性中的LaTeX源码
            formula = mjx.get('data-formula', '')
            if not formula:
                # 如果没有data-formula，尝试跳过
                continue
            
            # 判断是行内公式还是块级公式
            # 检查父标签和上下文
            is_block = self._is_block_formula(mjx)
            
            # 创建Markdown格式的公式
            if is_block:
                # 块级公式：使用$$...$$
                markdown_formula = f"$$\n{formula}\n$$"
            else:
                # 行内公式：使用$...$
                markdown_formula = f"${formula}$"
            
            # 替换mjx-container标签为Markdown公式
            # 创建一个新的文本节点
            from bs4 import NavigableString
            formula_text = NavigableString(markdown_formula)
            mjx.replace_with(formula_text)
    
    def _is_block_formula(self, mjx_tag):
        """
        判断公式是块级还是行内
        
        Args:
            mjx_tag: mjx-container标签
            
        Returns:
            bool: True表示块级公式，False表示行内公式
        """
        formula = mjx_tag.get('data-formula', '')
        
        # 检查父标签和上下文
        # mjx-container通常在span中，需要检查span的父标签（通常是p）
        span_parent = mjx_tag.parent
        parent = span_parent.parent if span_parent else None
        
        if parent:
            # 获取父标签中的所有文本（包括公式后的内容）
            parent_text = parent.get_text()
            
            # 检查公式后面是否有公式编号（如"(1)"、"(2)"、"(3)"等）
            # 找到公式在父文本中的位置
            formula_pos = parent_text.find(formula)
            if formula_pos >= 0:
                after_formula = parent_text[formula_pos + len(formula):].strip()
                # 如果公式后面主要是空白和编号（支持中文括号），很可能是块级公式
                if re.match(r'^\s*[（(]?\d+[）)]?\s*$', after_formula):
                    return True
            
            # 检查父标签的结构
            parent_name = parent.name.lower()
            if parent_name == 'p':
                # 获取p标签中除了公式外的其他内容
                # 需要检查span标签（mjx的父标签）的兄弟节点
                other_content = ''
                for child in parent.children:
                    # 跳过包含公式的span标签
                    if child == span_parent:
                        continue
                    # 检查child是否包含mjx_tag
                    if hasattr(child, 'find_all'):
                        mjx_found = child.find_all('mjx-container')
                        if mjx_tag in mjx_found:
                            continue
                    if hasattr(child, 'get_text'):
                        other_content += child.get_text()
                    elif isinstance(child, str):
                        other_content += child
                
                other_content = other_content.strip()
                # 如果其他内容主要是空白和公式编号（支持中文括号），是块级公式
                if re.match(r'^\s*[（(]?\d+[）)]?\s*$', other_content):
                    return True
                
                # 如果公式在段落开头，且后面主要是空白，可能是块级
                if parent_text.strip().startswith(formula):
                    # 检查公式后是否主要是空白和编号（支持中文括号）
                    remaining = parent_text[len(formula):].strip()
                    if re.match(r'^\s*[（(]?\d+[）)]?\s*$', remaining) or not remaining:
                        return True
                
                # 检查公式前后的兄弟节点内容（检查span的兄弟节点）
                before_formula = ''
                after_formula = ''
                found_formula = False
                for child in parent.children:
                    # 检查是否是包含公式的span标签
                    if child == span_parent:
                        found_formula = True
                        continue
                    # 检查child是否包含mjx_tag
                    if hasattr(child, 'find_all'):
                        mjx_found = child.find_all('mjx-container')
                        if mjx_tag in mjx_found:
                            found_formula = True
                            continue
                    text = ''
                    if hasattr(child, 'get_text'):
                        text = child.get_text()
                    elif isinstance(child, str):
                        text = child
                    
                    if not found_formula:
                        before_formula += text
                    else:
                        after_formula += text
                
                # 如果公式前后主要是空白，且后面有编号，是块级公式
                before_stripped = before_formula.strip()
                after_stripped = after_formula.strip()
                if (not before_stripped or len(before_stripped) < 5) and \
                   (re.match(r'^\s*[（(]?\d+[）)]?\s*$', after_stripped) or 
                    (not after_stripped and '=' in formula and len(formula) > 15)):
                    return True
        
        # 检查公式本身的特征
        # 如果公式包含等号且较长（通常块级公式更复杂），可能是块级
        if '=' in formula and len(formula) > 15:
            # 检查前面的兄弟节点
            prev_sibling = mjx_tag.previous_sibling
            if prev_sibling:
                if isinstance(prev_sibling, str):
                    prev_text = prev_sibling.strip()
                    # 如果前面主要是空白，可能是块级
                    if not prev_text or prev_text == '\n':
                        return True
            
            # 检查后面的兄弟节点
            next_sibling = mjx_tag.next_sibling
            if next_sibling:
                if isinstance(next_sibling, str):
                    next_text = next_sibling.strip()
                    # 如果后面主要是空白或公式编号（支持中文括号），可能是块级
                    if not next_text or re.match(r'^\s*[（(]?\d+[）)]?\s*$', next_text):
                        return True
        
        # 默认作为行内公式处理
        return False
    
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
        在Markdown末尾添加元数据
        
        Args:
            markdown_content: Markdown内容
            title: 文章标题
            author: 作者
            publish_time: 发布时间
            url: 文章URL（可选）
            
        Returns:
            str: 添加元数据后的Markdown内容
        """
        # 标题放在开头
        result = f"# {title}\n\n"
        
        # 正文内容
        result += markdown_content
        
        # 元数据放在末尾
        result += "\n\n---\n\n"
        result += f"**作者**: {author}  \n"
        result += f"**发布时间**: {publish_time}  \n"
        if url:
            result += f"**原文链接**: {url}  \n"
        
        return result

