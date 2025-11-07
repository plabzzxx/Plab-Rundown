"""
邮件内容解析器
用于解析 HTML 邮件内容并提取文本
"""

import base64
from typing import Dict, Any, Optional, Tuple
import re
import os
from pathlib import Path

from bs4 import BeautifulSoup
import html2text

from ..utils.logger import get_logger

logger = get_logger(__name__)


class EmailParser:
    """邮件内容解析器"""
    
    def __init__(self):
        """初始化解析器"""
        self.html_converter = html2text.HTML2Text()
        self.html_converter.ignore_links = False
        self.html_converter.ignore_images = False
        self.html_converter.body_width = 0  # 不自动换行
    
    def parse_email(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        解析邮件内容
        
        Args:
            message: Gmail API 返回的邮件对象
        
        Returns:
            解析后的邮件数据
        """
        payload = message.get('payload', {})
        
        # 提取 HTML 和纯文本内容
        html_content, text_content = self._extract_content(payload)
        
        # 如果有 HTML 内容，转换为 Markdown
        markdown_content = None
        if html_content:
            markdown_content = self._html_to_markdown(html_content)
        
        # 清理文本内容
        cleaned_text = self._clean_text(text_content or markdown_content or '')
        
        return {
            'html': html_content,
            'text': text_content,
            'markdown': markdown_content,
            'cleaned_text': cleaned_text
        }
    
    def _extract_content(
        self,
        payload: Dict[str, Any]
    ) -> Tuple[Optional[str], Optional[str]]:
        """
        从邮件 payload 中提取 HTML 和文本内容
        
        Args:
            payload: 邮件 payload
        
        Returns:
            (html_content, text_content) 元组
        """
        html_content = None
        text_content = None
        
        # 检查是否是多部分邮件
        if 'parts' in payload:
            for part in payload['parts']:
                mime_type = part.get('mimeType', '')
                
                if mime_type == 'text/html':
                    html_content = self._decode_body(part.get('body', {}))
                elif mime_type == 'text/plain':
                    text_content = self._decode_body(part.get('body', {}))
                
                # 递归处理嵌套的 parts
                if 'parts' in part:
                    nested_html, nested_text = self._extract_content(part)
                    if nested_html:
                        html_content = nested_html
                    if nested_text:
                        text_content = nested_text
        
        # 单部分邮件
        elif 'body' in payload:
            mime_type = payload.get('mimeType', '')
            body = payload.get('body', {})
            
            if mime_type == 'text/html':
                html_content = self._decode_body(body)
            elif mime_type == 'text/plain':
                text_content = self._decode_body(body)
        
        return html_content, text_content
    
    def _decode_body(self, body: Dict[str, Any]) -> Optional[str]:
        """
        解码邮件正文
        
        Args:
            body: 邮件正文对象
        
        Returns:
            解码后的文本
        """
        data = body.get('data')
        if not data:
            return None
        
        try:
            # Base64 URL-safe 解码
            decoded = base64.urlsafe_b64decode(data).decode('utf-8')
            return decoded
        except Exception as e:
            logger.error(f"解码邮件正文失败: {e}")
            return None
    
    def _html_to_markdown(self, html: str) -> str:
        """
        将 HTML 转换为 Markdown
        
        Args:
            html: HTML 内容
        
        Returns:
            Markdown 格式的文本
        """
        try:
            markdown = self.html_converter.handle(html)
            return markdown
        except Exception as e:
            logger.error(f"HTML 转 Markdown 失败: {e}")
            return html
    
    def _clean_text(self, text: str) -> str:
        """
        清理文本内容
        
        Args:
            text: 原始文本
        
        Returns:
            清理后的文本
        """
        if not text:
            return ""
        
        # 移除多余的空行
        text = re.sub(r'\n\s*\n\s*\n', '\n\n', text)
        
        # 移除行首行尾空白
        lines = [line.strip() for line in text.split('\n')]
        text = '\n'.join(lines)
        
        return text.strip()
    
    def extract_links(self, html: str) -> list:
        """
        从 HTML 中提取所有链接
        
        Args:
            html: HTML 内容
        
        Returns:
            链接列表
        """
        if not html:
            return []
        
        try:
            soup = BeautifulSoup(html, 'lxml')
            links = []
            
            for a_tag in soup.find_all('a', href=True):
                links.append({
                    'text': a_tag.get_text(strip=True),
                    'url': a_tag['href']
                })
            
            return links
        except Exception as e:
            logger.error(f"提取链接失败: {e}")
            return []
    
    def extract_images(self, html: str) -> list:
        """
        从 HTML 中提取所有图片

        Args:
            html: HTML 内容

        Returns:
            图片列表
        """
        if not html:
            return []

        try:
            soup = BeautifulSoup(html, 'lxml')
            images = []

            for img_tag in soup.find_all('img', src=True):
                images.append({
                    'alt': img_tag.get('alt', ''),
                    'src': img_tag['src']
                })

            return images
        except Exception as e:
            logger.error(f"提取图片失败: {e}")
            return []

    def save_html_to_file(
        self,
        html: str,
        filename: str,
        output_dir: str = "data/original"
    ) -> str:
        """
        将 HTML 内容保存到文件

        Args:
            html: HTML 内容
            filename: 文件名（不包含扩展名）
            output_dir: 输出目录

        Returns:
            保存的文件路径
        """
        if not html:
            logger.warning("HTML 内容为空，无法保存")
            return ""

        try:
            # 创建输出目录
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)

            # 生成文件路径
            file_path = output_path / f"{filename}.html"

            # 保存 HTML 文件
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(html)

            logger.info(f"HTML 已保存到: {file_path}")
            return str(file_path)

        except Exception as e:
            logger.error(f"保存 HTML 文件失败: {e}")
            raise

    def clip_email_html(self, html: str) -> str:
        """
        剪切邮件 HTML 内容，通过删除不需要的部分来保留原始结构

        策略：直接删除不需要的部分，而不是提取需要的部分
        这样可以完全保留原邮件的所有结构、样式和留白

        删除的部分：
        1. <body> 开始到 "Good morning" 容器开始之间的内容（Logo 和装饰）
        2. "COMMUNITY" 容器开始到 </body> 之间的内容（社区及之后）

        保留的部分：
        - 完整的 DOCTYPE, <html>, <head>, <body> 标签
        - 所有 CSS 样式定义
        - 从 "Good morning" 到 "QUICK HITS" 的所有内容
        - 原始的外层容器和留白

        Args:
            html: 完整的 HTML 内容

        Returns:
            剪切后的 HTML 内容（保留完整的原始结构）
        """
        if not html:
            logger.warning("HTML 内容为空，无法剪切")
            return ""

        try:
            # 1. 找到 <body> 标签的结束位置
            body_start = html.find("<body")
            if body_start == -1:
                logger.warning("未找到 <body> 标签")
                return html

            body_tag_end = html.find(">", body_start) + 1

            # 2. 找到 "Good morning" 的位置
            good_morning_pos = html.find("Good morning")
            if good_morning_pos == -1:
                logger.warning("未找到 'Good morning' 标记，返回原始内容")
                return html

            # 3. 向前查找 Good morning 所在的最外层容器的开始
            # 查找最近的 <tr><td><table 结构
            search_back = html[:good_morning_pos]
            first_part_end = search_back.rfind("<tr><td><table")
            if first_part_end == -1:
                logger.warning("未找到 Good morning 容器的开始标记")
                first_part_end = good_morning_pos

            # 4. 找到 "COMMUNITY" 的位置
            community_pos = html.find("COMMUNITY")
            if community_pos == -1:
                logger.warning("未找到 'COMMUNITY' 标记，使用原始内容的末尾")
                second_part_start = len(html)
            else:
                # 5. 向前查找 COMMUNITY 所在的最外层容器的开始
                search_back = html[:community_pos]
                second_part_start = search_back.rfind("<tr><td><table")
                if second_part_start == -1:
                    logger.warning("未找到 COMMUNITY 容器的开始标记")
                    second_part_start = community_pos

            # 6. 找到 </body> 的位置
            body_end = html.rfind("</body>")
            if body_end == -1:
                logger.warning("未找到 </body> 标签")
                body_end = len(html)

            # 7. 组合：保留 head 部分 + body 开始 + 需要的内容 + body 结束
            clipped_html = (
                html[:body_tag_end] +
                html[first_part_end:second_part_start] +
                html[body_end:]
            )

            logger.info(f"HTML 删除成功: {len(html)} -> {len(clipped_html)} 字符")
            logger.info(f"删除第一部分: [{body_tag_end}, {first_part_end}] ({first_part_end - body_tag_end} 字符)")
            logger.info(f"删除第二部分: [{second_part_start}, {body_end}] ({body_end - second_part_start} 字符)")

            return clipped_html

        except Exception as e:
            logger.error(f"HTML 剪切失败: {e}")
            return html

