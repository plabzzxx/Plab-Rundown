"""
定时任务主程序
用于在Render上运行定时任务
"""
import sys
import os
from pathlib import Path
from dotenv import load_dotenv
import yaml

# 设置UTF-8编码
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# 加载环境变量（override=True 确保覆盖系统环境变量）
load_dotenv(override=True)

from src.scheduler.tasks import TaskScheduler
from src.utils.logger import get_logger
from src.gmail.client import GmailClient
from src.gmail.parser import EmailParser
from src.translator.langchain_translator import LangChainTranslator
from src.wechat.table_based_converter import TableBasedConverter
from src.wechat.publisher import WeChatPublisher
from bs4 import BeautifulSoup
import re
from datetime import datetime
import pytz
import requests

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


def extract_title_and_digest(html_content: str) -> tuple[str, str]:
    """从HTML中提取标题和摘要"""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # 提取第一个h3作为标题
    title_elem = soup.find('h3')
    title = title_elem.get_text(strip=True) if title_elem else "AI早报"
    
    # 提取第一个段落作为摘要
    first_p = soup.find('p')
    digest = first_p.get_text(strip=True) if first_p else ""
    
    # 限制摘要长度
    if len(digest) > 100:
        digest = digest[:97] + "..."
    
    return title, digest


def run_daily_workflow():
    """执行每日工作流"""
    logger.info("=" * 70)
    logger.info("🚀 开始执行每日工作流")
    logger.info("=" * 70)
    
    try:
        # 第一步: 获取最新邮件
        logger.info("\n📧 第一步: 获取最新邮件")
        logger.info("-" * 70)

        # 初始化 Gmail 客户端（credentials_path 在 GitHub Actions 中不需要，会使用环境变量）
        credentials_path = os.getenv('GMAIL_CREDENTIALS_PATH', 'credentials/credentials.json')
        gmail_client = GmailClient(credentials_path=credentials_path)
        parser = EmailParser()
        
        # 从配置读取发件人
        config_path = Path("config/config.yaml")
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                yaml_config = yaml.safe_load(f)
                sender_email = yaml_config.get('gmail', {}).get('sender_email', 'news@daily.therundown.ai')
        else:
            sender_email = 'news@daily.therundown.ai'
        
        logger.info(f"查找发件人: {sender_email}")
        # 使用 get_latest_email 方法直接获取最新邮件
        # 策略选项：
        # - days_back=1: 获取最近1天内的最新邮件（更严格，确保是当天的）
        # - days_back=7: 获取最近7天内的最新邮件（更宽松，避免漏掉邮件）
        # email_data = gmail_client.get_latest_email(sender=sender_email, days_back=1)  # 原策略：最近1天
        email_data = gmail_client.get_latest_email(sender=sender_email, days_back=7)  # 当前策略：最近7天

        if not email_data:
            logger.warning("未找到邮件,跳过本次执行")
            return

        logger.info("成功获取最新邮件")

        # 解析邮件内容
        parsed_email = parser.parse_email(email_data)
        html_content = parsed_email.get('html')

        if not html_content:
            logger.error("邮件内容为空,跳过本次执行")
            return

        logger.info(f"✅ 邮件内容大小: {len(html_content)} 字符")

        # 第二步: 剪切邮件内容
        logger.info("\n✂️  第二步: 剪切邮件内容")
        logger.info("-" * 70)

        clipped_html = parser.clip_email_html(html_content)
        logger.info(f"✅ 剪切后内容大小: {len(clipped_html)} 字符")
        
        # 保存剪切后的HTML
        parser.save_html_to_file(clipped_html, "clipped_email", "data")
        
        # 第三步: 清理欢迎语并翻译
        logger.info("\n🌐 第三步: 翻译内容")
        logger.info("-" * 70)
        
        logger.info("清理欢迎语中的个人称呼...")
        clipped_html = clean_greeting(clipped_html)
        logger.info("✅ 欢迎语清理完成")
        
        # 初始化翻译器
        translator = LangChainTranslator()
        
        # 分块翻译
        from bs4 import NavigableString
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

            # 检查是否是固定标题
            if original_text in fixed_titles:
                translated_text = fixed_titles[original_text]
                logger.info(f"使用固定翻译: {original_text} -> {translated_text}")
            else:
                translated_text = translator.translate(original_text)

            text_node.replace_with(NavigableString(translated_text))
        
        translated_html = str(soup)
        logger.info("✅ 翻译完成")
        
        # 保存翻译后的HTML
        parser.save_html_to_file(translated_html, "translated_email", "data")
        
        # 第四步: 格式化为微信格式
        logger.info("\n📝 第四步: 格式化为微信公众号格式")
        logger.info("-" * 70)
        
        # 从YAML配置读取是否自动发布
        auto_publish = False
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                yaml_config = yaml.safe_load(f)
                auto_publish = yaml_config.get('wechat', {}).get('auto_publish', False)
        
        publisher = WeChatPublisher(auto_publish=auto_publish)
        formatter = TableBasedConverter(publisher=publisher)
        formatted_html = formatter.convert(translated_html)
        
        logger.info(f"✅ 格式化完成")
        
        # 保存格式化后的HTML
        parser.save_html_to_file(formatted_html, "wechat_formatted", "data")
        
        # 第五步: 推送到微信公众号
        logger.info("\n📤 第五步: 推送到微信公众号")
        logger.info("-" * 70)
        
        # 提取标题和摘要
        title, digest = extract_title_and_digest(formatted_html)
        title = get_title_with_prefix(title)
        
        logger.info(f"标题: {title}")
        logger.info(f"摘要: {digest}")
        
        # 提取第一张图片作为封面
        soup = BeautifulSoup(formatted_html, 'html.parser')
        first_img = soup.find('img')
        
        thumb_media_id = None
        if first_img:
            img_url = first_img.get('src', '')
            if img_url and 'http' in img_url:
                logger.info(f"找到封面图片: {img_url[:80]}...")
                
                # 下载图片
                temp_thumb_path = Path("data/assets/temp_thumb.jpg")
                if download_image(img_url, temp_thumb_path):
                    # 上传封面图
                    thumb_media_id = publisher.upload_thumb_image(str(temp_thumb_path))
                    logger.info(f"✅ 封面图上传成功")
        
        # 从Config读取作者名称
        from src.utils.config import Config
        config = Config()
        author = config.wechat_author
        
        # 发布文章
        result = publisher.publish_article(
            title=title,
            content=formatted_html,
            author=author,
            digest=digest,
            thumb_media_id=thumb_media_id
        )
        
        logger.info("=" * 70)
        if result.get('status') == 'published':
            logger.info("🎉 文章发布成功!")
            logger.info(f"Media ID: {result.get('media_id')}")
            logger.info(f"Publish ID: {result.get('publish_id')}")
        else:
            logger.info("🎉 草稿创建成功!")
            logger.info(f"Media ID: {result.get('media_id')}")
            logger.info("✅ 请登录微信公众号后台查看草稿箱")
        logger.info("=" * 70)
        
    except Exception as e:
        logger.error(f"工作流执行失败: {e}", exc_info=True)


def main():
    """主函数"""
    logger.info("🚀 Plab-Rundown 定时任务启动")

    # 加载配置
    config_path = Path("config/config.yaml")
    if config_path.exists():
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
            scheduler_config = config.get('scheduler', {})
    else:
        scheduler_config = {
            'timezone': 'Asia/Shanghai',
            'cron': {'hour': 9, 'minute': 0}
        }

    # 创建调度器
    timezone = scheduler_config.get('timezone', 'Asia/Shanghai')
    scheduler = TaskScheduler(timezone=timezone)

    # 添加每日任务
    cron_config = scheduler_config.get('cron', {})
    hour = cron_config.get('hour', 9)
    minute = cron_config.get('minute', 0)

    scheduler.add_daily_task(
        task_func=run_daily_workflow,
        hour=hour,
        minute=minute,
        task_id='daily_rundown'
    )

    logger.info(f"✅ 已设置每日任务: {hour:02d}:{minute:02d} ({timezone})")

    # 启动调度器
    scheduler.start()

    # 启动健康检查HTTP服务器 (Render需要)
    port = int(os.getenv('PORT', 10000))
    start_health_server(port, scheduler)

    # 保持运行
    logger.info("✅ 调度器运行中,按 Ctrl+C 退出")
    scheduler.keep_alive()


def start_health_server(port: int, scheduler: TaskScheduler):
    """启动健康检查HTTP服务器"""
    from http.server import HTTPServer, BaseHTTPRequestHandler
    import threading

    class HealthHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path == '/health' or self.path == '/':
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()

                # 获取调度器状态
                jobs = scheduler.scheduler.get_jobs()
                status = {
                    'status': 'healthy',
                    'scheduler_running': scheduler.is_running,
                    'jobs_count': len(jobs),
                    'jobs': [
                        {
                            'id': job.id,
                            'name': job.name,
                            'next_run': str(job.next_run_time) if job.next_run_time else None
                        }
                        for job in jobs
                    ]
                }

                import json
                self.wfile.write(json.dumps(status, indent=2).encode())
            else:
                self.send_response(404)
                self.end_headers()

        def log_message(self, format, *args):
            # 禁用默认日志输出
            pass

    def run_server():
        server = HTTPServer(('0.0.0.0', port), HealthHandler)
        logger.info(f"✅ 健康检查服务器启动: http://0.0.0.0:{port}/health")
        server.serve_forever()

    # 在后台线程运行HTTP服务器
    thread = threading.Thread(target=run_server, daemon=True)
    thread.start()


if __name__ == "__main__":
    main()

