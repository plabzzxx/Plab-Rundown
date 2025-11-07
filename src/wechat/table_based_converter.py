"""基于Table结构的微信HTML转换器"""
import re
from typing import Optional, List, Dict
from bs4 import BeautifulSoup
from src.utils.logger import get_logger

logger = get_logger(__name__)


class TableBasedConverter:
    """基于Table结构提取内容并生成简洁HTML"""
    
    def __init__(self, publisher=None):
        """初始化转换器
        
        Args:
            publisher: 微信发布器实例,用于上传图片
        """
        self.publisher = publisher
        self.uploaded_images = {}  # 缓存已上传的图片
    
    def convert(self, html_content: str) -> str:
        """转换HTML为微信格式
        
        Args:
            html_content: 原始HTML内容
            
        Returns:
            转换后的HTML内容
        """
        logger.info("开始基于Table结构转换HTML...")
        
        soup = BeautifulSoup(html_content, 'html.parser')
        body = soup.find('body')
        
        if not body:
            logger.error("未找到body标签")
            return html_content
        
        # 提取所有顶层TR
        all_trs = body.find_all('tr', recursive=False)
        logger.info(f"找到 {len(all_trs)} 个顶层TR标签")
        
        # 构建新的HTML
        html_parts = []
        current_section = None  # 跟踪当前章节

        # 添加banner图片
        banner_html = self._add_banner_image()
        if banner_html:
            html_parts.append(banner_html)

        # 遍历所有TR,提取内容
        for i, tr in enumerate(all_trs, 1):
            td = tr.find('td')
            if not td:
                continue

            nested_table = td.find('table', recursive=False)
            if not nested_table:
                continue

            nested_tr = nested_table.find('tr')
            if not nested_tr:
                continue

            nested_td = nested_tr.find('td')
            if not nested_td:
                continue

            bgcolor = nested_td.get('bgcolor', '')

            # 黑色背景 = 章节标题
            if bgcolor == '#000000':
                section_title = nested_td.get_text(strip=True)
                current_section = section_title  # 记录当前章节
                html_parts.append(self._format_section_title(section_title))

            # 白色背景 = 内容块
            elif bgcolor == '#FFFFFF':
                # 检查是否是新闻块(有H4标题)
                h4 = nested_td.find('h4')
                h3 = nested_td.find('h3')

                if h4:
                    # 这是一条新闻 (LATEST DEVELOPMENTS)
                    news_html = self._format_news_block(nested_td)
                    if news_html:
                        html_parts.append(news_html)
                elif h3:
                    # 这是快速要点的子版块(有H3标题)
                    # 需要检查内容是在同一个td还是下一个tr中
                    # 传递顶层TR,而不是嵌套TR
                    subsection_html = self._format_quick_hits_subsection_with_next_tr(nested_td, tr)
                    if subsection_html:
                        html_parts.append(subsection_html)
                else:
                    # 这是简介或快讯
                    # 所有非新闻块都用边框包裹
                    content_html = self._format_content_block(nested_td, add_border=True)
                    if content_html:
                        html_parts.append(content_html)
        
        result = '\n'.join(html_parts)
        logger.info(f"HTML转换完成,长度: {len(result)} 字符")
        
        return result
    
    def _add_banner_image(self) -> str:
        """添加banner图片到文章开头"""
        from pathlib import Path

        banner_path = Path("data/assets/banner.png")
        if not banner_path.exists():
            logger.warning(f"Banner图片不存在: {banner_path}")
            return ""

        # 如果有publisher,上传图片并使用微信的图片URL
        if self.publisher:
            try:
                # 检查是否已经上传过
                if str(banner_path) in self.uploaded_images:
                    media_url = self.uploaded_images[str(banner_path)]
                else:
                    # 上传图片
                    media_url = self.publisher.upload_image(str(banner_path))
                    self.uploaded_images[str(banner_path)] = media_url

                logger.info(f"Banner图片上传成功: {media_url}")
                return f'<p style="text-align:center;margin:0;padding:0;"><img src="{media_url}" style="width:100%;display:block;" /></p>'
            except Exception as e:
                logger.error(f"上传banner图片失败: {e}")
                return ""
        else:
            # 没有publisher,使用本地路径(仅用于测试)
            logger.warning("没有publisher,使用本地路径")
            return f'<p style="text-align:center;margin:0;padding:0;"><img src="{banner_path}" style="width:100%;display:block;" /></p>'

    def _format_section_title(self, title: str) -> str:
        """格式化章节标题(黑色背景)"""
        return f'''<div style="background:#000;color:#fff;text-align:center;padding:12px;margin:20px 0;font-weight:bold;font-size:16px;">
{title}
</div>'''

    def _format_quick_hits_subsection_with_next_tr(self, td, current_tr):
        """格式化快速要点的子版块(带H3标题),内容可能在同一table的后续tr中

        Args:
            td: 包含H3标题的td元素(可能是嵌套的)
            current_tr: 顶层TR元素(不是嵌套TR)
        """
        parts = []

        # 提取H3标题
        h3 = td.find('h3')
        if h3:
            # 尝试从链接中提取标题文本(避免emoji重复)
            link = h3.find('a')
            if link:
                title_text = link.get_text(strip=True)
            else:
                title_text = h3.get_text(strip=True)
            parts.append(f'<h3 style="font-size:16px;font-weight:bold;color:#000;margin:10px 0;">{title_text}</h3>')
            logger.info(f"处理H3子版块: {title_text}")

        # 找到直接包含H3的TD(而不是传入的td,因为传入的td可能是更外层的)
        h3_td = h3.find_parent('td')

        # 首先尝试在H3的TD中查找内容
        ul = h3_td.find('ul')
        content_found = False

        if ul:
            # 找到ul列表
            list_items = ul.find_all('li', recursive=False)
            logger.info(f"在当前TD中找到UL列表,包含 {len(list_items)} 个LI项")
            for li in list_items:
                # 获取列表项的内部HTML（保留所有标签和样式）
                inner_html = ''.join(str(child) for child in li.children)
                text_content = li.get_text(strip=True)

                if text_content:
                    # 清理嵌套的p标签
                    inner_html_clean = inner_html.replace('<p style="mso-line-height-alt:150.0%;padding:0px;text-align:left;word-break:break-word;">', '').replace('</p>', '')
                    parts.append(f'<p style="font-size:15px;line-height:1.6;color:#333;margin:6px 0;padding-left:20px;"><span style="font-size:12px;">•</span> {inner_html_clean}</p>')
                    content_found = True

        # 如果H3的TD中没有找到内容,尝试在同一个table的后续tr中查找
        if not content_found:
            logger.info("当前TD中没有找到UL列表,尝试在同一table的后续TR中查找")
            # 找到包含H3的嵌套TR
            nested_tr = h3_td.find_parent('tr')
            if nested_tr:
                # 找到包含这个嵌套TR的table
                nested_table = nested_tr.find_parent('table')
                if nested_table:
                    # 查找这个table中H3所在TR之后的所有TR
                    all_trs = nested_table.find_all('tr', recursive=False)
                    logger.info(f"找到嵌套table,包含 {len(all_trs)} 个TR")
                    h3_tr_index = -1
                    for i, tr in enumerate(all_trs):
                        if tr == nested_tr:
                            h3_tr_index = i
                            break

                    logger.info(f"H3所在TR的索引: {h3_tr_index}")
                    # 处理H3之后的所有TR
                    if h3_tr_index >= 0:
                        subsequent_trs = all_trs[h3_tr_index + 1:]
                        logger.info(f"H3之后有 {len(subsequent_trs)} 个TR需要处理")
                        for idx, tr in enumerate(subsequent_trs):
                            logger.info(f"处理TR {h3_tr_index + 1 + idx + 1}")
                            tr_td = tr.find('td')
                            if tr_td:
                                logger.info(f"  找到TD")
                                # 首先检查是否有DIV包含UL (第一个H3的情况)
                                div = tr_td.find('div', recursive=False)
                                if div:
                                    ul_in_div = div.find('ul')
                                    if ul_in_div:
                                        logger.info(f"TR {h3_tr_index + 1 + idx + 1} 包含DIV>UL")
                                        list_items = ul_in_div.find_all('li', recursive=False)
                                        for li in list_items:
                                            inner_html = ''.join(str(child) for child in li.children)
                                            text_content = li.get_text(strip=True)
                                            if text_content:
                                                # 清理嵌套的p标签
                                                inner_html_clean = inner_html.replace('<p style="mso-line-height-alt:150.0%;padding:0px;text-align:left;word-break:break-word;">', '').replace('</p>', '')
                                                parts.append(f'<p style="font-size:15px;line-height:1.6;color:#333;margin:6px 0;padding-left:20px;"><span style="font-size:12px;">•</span> {inner_html_clean}</p>')
                                                content_found = True
                                else:
                                    # 如果没有DIV,查找P标签 (第二个H3的情况)
                                    p_tags = tr_td.find_all('p', recursive=False)
                                    if p_tags:
                                        logger.info(f"TR {h3_tr_index + 1 + idx + 1} 包含 {len(p_tags)} 个P标签")
                                        for p in p_tags:
                                            # 获取p标签的内部HTML（保留所有标签和样式）
                                            inner_html = ''.join(str(child) for child in p.children)
                                            text_content = p.get_text(strip=True)

                                            if text_content:
                                                logger.info(f"找到内容: {text_content[:50]}...")
                                                parts.append(f'<p style="font-size:15px;line-height:1.6;color:#333;margin:8px 0;">{inner_html}</p>')
                                                content_found = True

        if not parts or len(parts) == 1:  # 只有标题,没有内容
            logger.warning(f"H3子版块没有找到内容,只有标题")
            return ""

        logger.info(f"H3子版块格式化完成,包含 {len(parts)} 个部分")
        content = "\n".join(parts)
        return f'<div style="border:2px solid #000;border-radius:10px;padding:15px;margin:15px 0;background:#fff;">\n{content}\n</div>'

    def _format_quick_hits_subsection(self, td):
        """格式化快速要点的子版块(带H3标题) - 旧版本,保留兼容性"""
        parts = []

        # 提取H3标题
        h3 = td.find('h3')
        if h3:
            # 尝试从链接中提取标题文本(避免emoji重复)
            link = h3.find('a')
            if link:
                title_text = link.get_text(strip=True)
            else:
                title_text = h3.get_text(strip=True)
            parts.append(f'<h3 style="font-size:16px;font-weight:bold;color:#000;margin:10px 0;">{title_text}</h3>')

        # 提取列表项(可能是ul或者多个p标签)
        ul = td.find('ul')
        if ul:
            list_items = ul.find_all('li', recursive=False)
            for li in list_items:
                # 获取列表项的内部HTML（保留所有标签和样式）
                inner_html = ''.join(str(child) for child in li.children)
                text_content = li.get_text(strip=True)

                if text_content:
                    # 清理嵌套的p标签
                    inner_html_clean = inner_html.replace('<p style="mso-line-height-alt:150.0%;padding:0px;text-align:left;word-break:break-word;">', '').replace('</p>', '')
                    parts.append(f'<p style="font-size:15px;line-height:1.6;color:#333;margin:6px 0;padding-left:20px;"><span style="font-size:12px;">•</span> {inner_html_clean}</p>')
        else:
            # 如果没有ul,尝试查找所有p标签(用于"今天人工智能领域的其他一切"这种格式)
            p_tags = td.find_all('p', class_='dd', recursive=False)
            for p in p_tags:
                # 获取p标签的内部HTML（保留所有标签和样式）
                inner_html = ''.join(str(child) for child in p.children)
                text_content = p.get_text(strip=True)

                if text_content:
                    parts.append(f'<p style="font-size:15px;line-height:1.6;color:#333;margin:8px 0;">{inner_html}</p>')

        if not parts or len(parts) == 1:  # 只有标题,没有内容
            return ""

        content = "\n".join(parts)

        # 添加边框样式
        return f'''<div style="border:2px solid #000;border-radius:10px;padding:15px;margin:15px 0;background:#fff;">
{content}
</div>'''

    def _format_content_block(self, td, add_border: bool = False) -> str:
        """格式化普通内容块(简介或快讯) - 保留原有格式

        Args:
            td: BeautifulSoup td 元素
            add_border: 是否添加边框包裹整个内容块
        """
        parts = []
        has_divider = False
        divider_position = None  # 记录分割线应该在的位置

        # 检查是否有分割线 (font-size:0px;line-height:0px 的 td)
        divider_td = td.find('td', style=lambda s: s and 'line-height:0px' in s)
        if divider_td:
            has_divider = True

        # 提取所有段落 - 保留原有的HTML格式
        for p in td.find_all('p', recursive=True):
            # 检查是否是列表项的子元素，如果是则跳过
            if p.find_parent('li'):
                continue

            # 获取段落的内部HTML（保留所有标签和样式）
            inner_html = ''.join(str(child) for child in p.children)
            text_content = p.get_text(strip=True)

            if text_content and len(text_content) > 5:  # 过滤太短的文本
                # 检查是否是"在今天的人工智能动态中："标题
                if '在今天的人工智能动态中' in text_content or 'In today' in text_content:
                    # 在这个标题之前添加分割线
                    if has_divider and len(parts) > 0:
                        parts.append('<div style="border-top:2px solid #000;margin:15px 0;"></div>')
                    divider_position = len(parts)

                # 保留原有的样式，只调整外层样式
                parts.append(f'<p style="font-size:15px;line-height:1.6;color:#333;margin:8px 0;">{inner_html}</p>')

        # 提取列表 (In today's AI rundown: 部分) - 保留原有格式
        for ul in td.find_all('ul', recursive=True):
            list_items = []
            for li in ul.find_all('li', recursive=False):
                # 获取列表项的内部HTML（保留所有标签和样式）
                # 但要提取纯文本内容，避免嵌套的p标签
                inner_html = ''.join(str(child) for child in li.children)
                text_content = li.get_text(strip=True)

                if text_content:
                    # 清理嵌套的p标签，只保留内部内容
                    inner_html_clean = inner_html.replace('<p style="mso-line-height-alt:150.0%;padding:0px;text-align:left;word-break:break-word;">', '').replace('</p>', '')
                    # 使用更小的圆点符号 (•) 而不是 (●)
                    list_items.append(f'<p style="font-size:15px;line-height:1.6;color:#333;margin:6px 0;padding-left:20px;"><span style="font-size:12px;">•</span> {inner_html_clean}</p>')

            if list_items:
                # 要点列表内容
                list_content = '\n'.join(list_items)
                parts.append(list_content)

        if parts:
            content = '\n'.join(parts)

            # 统一添加边框包裹
            if add_border:
                return f'''<div style="border:2px solid #000;border-radius:10px;padding:15px;margin:15px 0;background:#fff;">
{content}
</div>'''
            else:
                return content + '\n<div style="height:20px;"></div>'

        return ''
    
    def _format_news_block(self, td) -> str:
        """格式化新闻块 - 保留原有格式"""
        parts = []

        # 1. 提取分类标签(H6) - 保留原有格式
        h6 = td.find('h6')
        if h6:
            inner_html = ''.join(str(child) for child in h6.children)
            parts.append(f'<p style="font-size:12px;color:#999;margin:5px 0;">{inner_html}</p>')

        # 2. 提取标题(H4) - 保留原有格式
        h4 = td.find('h4')
        if h4:
            inner_html = ''.join(str(child) for child in h4.children)
            parts.append(f'<h3 style="font-size:18px;font-weight:bold;color:#000;margin:10px 0;line-height:1.4;">{inner_html}</h3>')

        # 3. 提取图片
        img = td.find('img')
        if img:
            img_src = img.get('src', '')
            if img_src and 'http' in img_src:
                # 上传图片到微信服务器
                wechat_url = self._upload_image(img_src)
                if wechat_url:
                    parts.append(f'<p style="text-align:center;margin:15px 0;"><img src="{wechat_url}" style="max-width:100%;height:auto;"/></p>')

        # 4. 提取正文段落 - 保留原有格式
        for p in td.find_all('p', recursive=True):
            # 检查是否是列表项的子元素，如果是则跳过
            if p.find_parent('li'):
                continue

            text_content = p.get_text(strip=True)
            # 过滤掉"Image source"和太短的文本
            if text_content and len(text_content) > 10 and 'Image source' not in text_content:
                # 获取段落的内部HTML（保留所有标签和样式）
                inner_html = ''.join(str(child) for child in p.children)

                # 检查是否是粗体开头(如"The Rundown:", "The details:")
                if text_content.startswith('The Rundown:') or text_content.startswith('The details:') or text_content.startswith('Why it matters:'):
                    parts.append(f'<p style="font-size:15px;line-height:1.8;color:#333;margin:10px 0;"><strong>{inner_html}</strong></p>')
                else:
                    parts.append(f'<p style="font-size:15px;line-height:1.8;color:#333;margin:10px 0;">{inner_html}</p>')

        # 5. 提取列表 - 保留原有格式
        for ul in td.find_all('ul', recursive=True):
            for li in ul.find_all('li', recursive=False):
                inner_html = ''.join(str(child) for child in li.children)
                text_content = li.get_text(strip=True)
                if text_content:
                    # 清理嵌套的p标签
                    inner_html_clean = inner_html.replace('<p style="mso-line-height-alt:150.0%;padding:0px;text-align:left;word-break:break-word;">', '').replace('</p>', '')
                    # 使用更小的圆点符号
                    parts.append(f'<p style="font-size:14px;line-height:1.8;color:#555;margin:8px 0;padding-left:20px;"><span style="font-size:11px;">•</span> {inner_html_clean}</p>')

        # 6. 提取有序列表 - 保留原有格式
        for ol in td.find_all('ol', recursive=True):
            for i, li in enumerate(ol.find_all('li', recursive=False), 1):
                inner_html = ''.join(str(child) for child in li.children)
                text_content = li.get_text(strip=True)
                if text_content:
                    # 清理嵌套的p标签
                    inner_html_clean = inner_html.replace('<p style="mso-line-height-alt:150.0%;padding:0px;text-align:left;word-break:break-word;">', '').replace('</p>', '')
                    parts.append(f'<p style="font-size:14px;line-height:1.8;color:#555;margin:8px 0;padding-left:20px;">{i}. {inner_html_clean}</p>')

        if parts:
            # 用边框包裹新闻块
            content = '\n'.join(parts)
            return f'''<div style="border:2px solid #000;border-radius:10px;padding:15px;margin:15px 0;background:#fff;">
{content}
</div>'''

        return ''
    
    def _upload_image(self, img_url: str) -> Optional[str]:
        """上传图片到微信服务器
        
        Args:
            img_url: 图片URL
            
        Returns:
            微信图片URL,失败返回None
        """
        # 检查缓存
        if img_url in self.uploaded_images:
            return self.uploaded_images[img_url]
        
        if not self.publisher:
            logger.warning("未提供publisher,无法上传图片")
            return None
        
        try:
            logger.info(f"上传图片: {img_url[:80]}...")
            wechat_url = self.publisher.upload_image(img_url)
            if wechat_url:
                self.uploaded_images[img_url] = wechat_url
                logger.info(f"图片上传成功")
                return wechat_url
        except Exception as e:
            logger.error(f"上传图片失败: {e}")
        
        return None

