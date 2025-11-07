"""
完整工作流 - 从邮件获取到微信草稿箱推送
包含所有步骤：获取邮件 -> 剪切 -> 翻译 -> 格式化 -> 推送到微信
"""

import sys
import os
from pathlib import Path
from dotenv import load_dotenv
import yaml
import re
from datetime import datetime
import pytz
import requests
from bs4 import BeautifulSoup, NavigableString

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 加载环境变量
load_dotenv()

from src.gmail.client import GmailClient
from src.gmail.parser import EmailParser
from src.translator.langchain_translator import LangChainTranslator
from src.wechat.table_based_converter import TableBasedConverter
from src.wechat.publisher import WeChatPublisher
from src.utils.logger import setup_logging, get_logger
from src.utils.config import get_config

# 初始化日志
setup_logging(log_level="INFO", log_file="logs/app.log")
logger = get_logger(__name__)


def download_image(url: str, save_path: Path) -> bool:
    """下载图片"""
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        save_path.parent.mkdir(parents=True, exist_ok=True)
        with open(save_path, 'wb') as f:
            f.write(response.content)
        return True
    except Exception as e:
        logger.error(f"下载图片失败: {e}")
        return False


def clean_greeting(html_content: str) -> str:
    """清理欢迎语中的个人称呼"""
    patterns = [
        r'Good morning,\s+\w+\.',
        r'Good afternoon,\s+\w+\.',
        r'Good evening,\s+\w+\.',
        r'Hello,\s+\w+\.',
        r'Hi,\s+\w+\.',
    ]
    for pattern in patterns:
        html_content = re.sub(
            pattern,
            lambda m: m.group(0).split(',')[0] + '.',
            html_content,
            flags=re.IGNORECASE
        )
    return html_content


def get_title_with_prefix(original_title: str) -> str:
    """为标题添加日期前缀"""
    config_path = Path("config/config.yaml")
    if config_path.exists():
        with open(config_path, 'r', encoding='utf-8') as f:
            yaml_config = yaml.safe_load(f)
            title_prefix_template = yaml_config.get('wechat', {}).get('title_prefix', '【{date}AI早报】')
    else:
        title_prefix_template = '【{date}AI早报】'

    beijing_tz = pytz.timezone('Asia/Shanghai')
    now = datetime.now(beijing_tz)
    date_str = now.strftime('%m月%d日').lstrip('0').replace('月0', '月')
    title_prefix = title_prefix_template.replace('{date}', date_str)
    return f"{title_prefix}{original_title}"


def extract_title_and_digest(html_content: str) -> tuple:
    """从HTML中提取标题和摘要"""
    import emoji

    soup = BeautifulSoup(html_content, 'html.parser')

    # 提取第一个h3作为标题
    title_elem = soup.find('h3')
    title = title_elem.get_text(strip=True) if title_elem else "AI早报"

    # 去除emoji
    title = emoji.replace_emoji(title, '').strip()

    # 提取第一个有文本内容的段落作为摘要(跳过banner图片的p标签)
    digest = ""
    for p in soup.find_all('p'):
        # 跳过只包含图片的p标签
        if p.find('img') and not p.get_text(strip=True):
            continue
        text = p.get_text(strip=True)
        if text:
            digest = text
            break

    # 限制摘要长度
    if len(digest) > 100:
        digest = digest[:97] + "..."

    return title, digest


def main():
    """执行完整工作流: 获取邮件 -> 剪切 -> 翻译 -> 格式化 -> 推送到微信"""
    import sys
    import io

    # 设置stdout为UTF-8编码,避免Windows控制台emoji错误
    if sys.platform == 'win32':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    print("=" * 70)
    print("🚀 Plab-Rundown 完整工作流")
    print("=" * 70)
    print()

    try:
        # 加载配置
        config = get_config()

        # ============================================
        # 步骤 1: 下载最新邮件
        # ============================================
        print("📥 步骤 1: 下载最新邮件")
        # 开始时间
        start_time = datetime.now()
        print("开始时间:", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        print("-" * 70)

        gmail_client = GmailClient(
            credentials_path=config.gmail_credentials_path,
            token_path=config.gmail_token_path
        )
        parser = EmailParser()

        # 获取最新邮件
        logger.info(f"正在获取来自 {config.sender_email} 的最新邮件...")
        message = gmail_client.get_latest_email(
            sender=config.sender_email,
            days_back=7
        )

        if not message:
            logger.error("❌ 未找到邮件")
            print("\n❌ 未找到符合条件的邮件")
            print("请检查:")
            print("  1. Gmail API 凭据是否正确")
            print(f"  2. 是否有来自 {config.sender_email} 的邮件")
            print("  3. 邮件是否在最近7天内")
            return

        # 提取邮件数据
        email_data = gmail_client.extract_email_data(message)

        logger.info("✅ 成功获取邮件")
        logger.info(f"📧 主题: {email_data['subject']}")
        logger.info(f"👤 发件人: {email_data['sender']}")
        logger.info(f"📅 日期: {email_data['date']}")

        print("✅ 成功获取邮件")
        print(f"📧 主题: {email_data['subject']}")
        print(f"👤 发件人: {email_data['sender']}")
        print(f"📅 日期: {email_data['date']}")
        print()

        # 获取HTML内容
        html_content = gmail_client.get_email_html(email_data['id'])

        if not html_content:
            logger.error("❌ 无法解析邮件内容")
            print("\n❌ 无法解析邮件内容")
            return

        logger.info(f"✅ 邮件内容大小: {len(html_content)} 字符")
        print(f"✅ 邮件内容大小: {len(html_content)} 字符")
        print()

        # 保存原始HTML
        parser.save_html_to_file(html_content, "original_email", "data")
        print(f"💾 原始邮件已保存: data/original_email.html")
        print()

        # ============================================
        # 步骤 2: 剪切邮件内容
        # ============================================
        print("✂️  步骤 2: 剪切邮件内容")
        print("-" * 70)

        logger.info("正在剪切邮件内容...")
        clipped_html = parser.clip_email_html(html_content)

        logger.info(f"✅ 剪切后内容大小: {len(clipped_html)} 字符")
        print(f"✅ 剪切后内容大小: {len(clipped_html)} 字符")
        print()

        # 保存剪切后的HTML
        parser.save_html_to_file(clipped_html, "clipped_email", "data")
        print(f"💾 剪切后邮件已保存: data/clipped_email.html")
        print()

        # ============================================
        # 步骤 3: 清理欢迎语并翻译
        # ============================================
        print("🌐 步骤 3: 翻译内容")
        print("-" * 70)

        logger.info("清理欢迎语中的个人称呼...")
        clipped_html = clean_greeting(clipped_html)
        logger.info("✅ 欢迎语清理完成")
        print("✅ 欢迎语清理完成")
        print()

        # 初始化翻译器
        logger.info("初始化翻译器...")
        translator = LangChainTranslator()
        print("✅ 翻译器初始化完成")
        print()

        # 分块翻译
        logger.info("开始翻译邮件内容...")
        soup = BeautifulSoup(clipped_html, 'html.parser')

        # 找到所有文本节点
        text_nodes = []
        for elem in soup.find_all(string=True):
            if elem.parent.name in ['script', 'style', '[document]', 'head', 'title', 'meta']:
                continue
            text = str(elem).strip()
            if text and len(text) > 3 and any(c.isalpha() for c in text):
                text_nodes.append(elem)

        logger.info(f"📝 找到 {len(text_nodes)} 个需要翻译的文本节点")
        print(f"📝 找到 {len(text_nodes)} 个需要翻译的文本节点")
        print()

        # 固定标题映射
        fixed_titles = {
            "LATEST DEVELOPMENTS": os.getenv("SECTION_TITLE_LATEST_DEVELOPMENTS", "今日要闻"),
            "QUICK HITS": os.getenv("SECTION_TITLE_QUICK_HITS", "其他要闻"),
            "Trending AI Tools": os.getenv("SUBSECTION_TITLE_TRENDING_TOOLS", "🛠️ 热门 AI 工具"),
            "Everything else in AI today": os.getenv("SUBSECTION_TITLE_EVERYTHING_ELSE", "📰 今天人工智能领域的其他一切"),
        }

        # 翻译每个文本节点
        for i, text_node in enumerate(text_nodes, 1):
            original_text = str(text_node).strip()

            if i % 10 == 0 or i == 1:
                logger.info(f"[{i}/{len(text_nodes)}] 翻译中...")
                print(f"[{i}/{len(text_nodes)}] 翻译中...")

            # 检查是否是固定标题
            if original_text in fixed_titles:
                translated_text = fixed_titles[original_text]
                logger.info(f"使用固定翻译: {original_text} -> {translated_text}")
            else:
                translated_text = translator.translate(original_text)

            text_node.replace_with(NavigableString(translated_text))

        translated_html = str(soup)
        logger.info("✅ 翻译完成")
        print("✅ 翻译完成")
        print()

        # 保存翻译后的HTML
        parser.save_html_to_file(translated_html, "translated_email", "data")
        print(f"💾 翻译后邮件已保存: data/translated_email.html")
        print()

        # ============================================
        # 步骤 4: 格式化为微信公众号格式
        # ============================================
        print("📝 步骤 4: 格式化为微信公众号格式")
        print("-" * 70)

        # 从YAML配置读取是否自动发布
        auto_publish = False
        config_path = Path("config/config.yaml")
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                yaml_config = yaml.safe_load(f)
                auto_publish = yaml_config.get('wechat', {}).get('auto_publish', False)

        logger.info("初始化微信发布器...")
        publisher = WeChatPublisher(auto_publish=auto_publish)
        formatter = TableBasedConverter(publisher=publisher)

        logger.info("开始格式化...")
        formatted_html = formatter.convert(translated_html)
        logger.info(f"✅ 格式化完成")
        print("✅ 格式化完成")
        print()

        # 保存格式化后的HTML
        parser.save_html_to_file(formatted_html, "wechat_formatted", "data")
        print(f"💾 格式化后邮件已保存: data/wechat_formatted.html")
        print()

        # ============================================
        # 步骤 5: 推送到微信公众号
        # ============================================
        print("📤 步骤 5: 推送到微信公众号")
        print("-" * 70)

        # 提取标题和摘要
        title, digest = extract_title_and_digest(formatted_html)
        title = get_title_with_prefix(title)

        logger.info(f"标题: {title}")
        logger.info(f"摘要: {digest}")
        print(f"📌 标题: {title}")
        print(f"📝 摘要: {digest}")
        print()

        # 提取第一张图片作为封面
        soup = BeautifulSoup(formatted_html, 'html.parser')
        first_img = soup.find('img')

        thumb_media_id = None
        if first_img:
            img_url = first_img.get('src', '')
            if img_url and 'http' in img_url:
                logger.info(f"找到封面图片: {img_url[:80]}...")
                print(f"🖼️  找到封面图片")

                # 下载图片
                temp_thumb_path = Path("data/assets/temp_thumb.jpg")
                if download_image(img_url, temp_thumb_path):
                    # 上传封面图
                    logger.info("上传封面图...")
                    thumb_media_id = publisher.upload_thumb_image(str(temp_thumb_path))
                    logger.info(f"✅ 封面图上传成功")
                    print(f"✅ 封面图上传成功")

        # 从Config读取作者名称
        from src.utils.config import Config
        config = Config()
        author = config.wechat_author

        print()
        logger.info("发布文章到微信公众号...")
        print("📤 发布文章到微信公众号...")

        # 发布文章
        result = publisher.publish_article(
            title=title,
            content=formatted_html,
            author=author,
            digest=digest,
            thumb_media_id=thumb_media_id
        )

        print()
        print("=" * 70)
        if result.get('status') == 'published':
            logger.info("🎉 文章发布成功!")
            logger.info(f"Media ID: {result.get('media_id')}")
            logger.info(f"Publish ID: {result.get('publish_id')}")
            print("🎉 文章发布成功!")
            print(f"Media ID: {result.get('media_id')}")
            print(f"Publish ID: {result.get('publish_id')}")
        else:
            logger.info("✅ 文章已保存为草稿!")
            logger.info(f"Media ID: {result.get('media_id')}")
            print("✅ 文章已保存为草稿!")
            print(f"Media ID: {result.get('media_id')}")
            #结束时间，用时
            print(f"结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"用时: {datetime.now() - start_time}")
        print("=" * 70)
        print()

    except Exception as e:
        logger.error(f"❌ 工作流执行失败: {e}", exc_info=True)
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

