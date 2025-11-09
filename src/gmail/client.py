"""
Gmail API 客户端
用于连接 Gmail 并获取邮件
"""

import os
import pickle
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import httplib2

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from ..utils.logger import get_logger

logger = get_logger(__name__)

# Gmail API 权限范围
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']


def _log_proxy_info() -> None:
    """
    记录代理配置信息
    注意：Google API 客户端会自动读取 HTTP_PROXY/HTTPS_PROXY 环境变量
    """
    http_proxy = os.getenv('HTTP_PROXY') or os.getenv('http_proxy')
    https_proxy = os.getenv('HTTPS_PROXY') or os.getenv('https_proxy')

    if http_proxy or https_proxy:
        logger.info(f"检测到代理配置:")
        if http_proxy:
            logger.info(f"  HTTP_PROXY: {http_proxy}")
        if https_proxy:
            logger.info(f"  HTTPS_PROXY: {https_proxy}")
        logger.info("  Google API 客户端将自动使用这些代理设置")
    else:
        logger.info("未配置代理，将直接连接")


class GmailClient:
    """Gmail API 客户端类"""
    
    def __init__(
        self,
        credentials_path: str,
        token_path: str = "credentials/token.pickle"
    ):
        """
        初始化 Gmail 客户端
        
        Args:
            credentials_path: OAuth 凭证文件路径
            token_path: 访问令牌保存路径
        """
        self.credentials_path = credentials_path
        self.token_path = token_path
        self.service = None
        self._authenticate()
    
    def _authenticate(self) -> None:
        """
        执行 OAuth 认证
        支持两种方式：
        1. 本地开发：使用 token.pickle 文件
        2. Render 部署：使用环境变量中的 token 信息
        """
        creds = None

        # 方式 1: 尝试从环境变量加载 token（Render 部署）
        gmail_token_json = os.getenv('GMAIL_TOKEN_JSON')
        if gmail_token_json:
            logger.info("从环境变量加载 Gmail token")
            try:
                import json
                token_data = json.loads(gmail_token_json)
                creds = Credentials(
                    token=token_data.get('token'),
                    refresh_token=token_data.get('refresh_token'),
                    token_uri=token_data.get('token_uri'),
                    client_id=token_data.get('client_id'),
                    client_secret=token_data.get('client_secret'),
                    scopes=token_data.get('scopes')
                )
                logger.info("从环境变量加载 token 成功")
            except Exception as e:
                logger.warning(f"从环境变量加载 token 失败: {e}")
                creds = None

        # 方式 2: 尝试从文件加载已保存的令牌（本地开发）
        if not creds and os.path.exists(self.token_path):
            logger.info(f"加载已保存的访问令牌: {self.token_path}")
            with open(self.token_path, 'rb') as token:
                creds = pickle.load(token)

        # 如果没有有效凭证，执行认证流程
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                logger.info("刷新过期的访问令牌")
                try:
                    creds.refresh(Request())
                    logger.info("令牌刷新成功")

                    # 🔧 修复: 刷新成功后保存新的 token
                    if not gmail_token_json:  # 只在本地环境保存文件
                        os.makedirs(os.path.dirname(self.token_path), exist_ok=True)
                        with open(self.token_path, 'wb') as token:
                            pickle.dump(creds, token)
                        logger.info(f"✅ 刷新后的令牌已保存: {self.token_path}")

                except Exception as e:
                    logger.error(f"令牌刷新失败: {e}")
                    # 如果刷新失败且在服务器环境，抛出错误
                    if gmail_token_json or os.getenv('RENDER') or os.getenv('DOCKER_CONTAINER'):
                        raise RuntimeError(
                            "Gmail token 刷新失败。请在本地重新授权:\n"
                            "1. 在本地执行: uv run python -c \"from src.gmail.client import GmailClient; GmailClient()\"\n"
                            "2. 完成浏览器授权\n"
                            "3. 上传新的 credentials/token.pickle 到服务器"
                        )
                    creds = None

            # 如果还是没有有效凭证，执行 OAuth 流程（仅本地）
            if not creds:
                # 检查是否在服务器环境（没有浏览器）
                if gmail_token_json or os.getenv('RENDER') or os.getenv('DOCKER_CONTAINER'):
                    raise RuntimeError(
                        "在服务器环境中无法执行 OAuth 浏览器授权流程。\n"
                        "请在本地完成授权:\n"
                        "1. 在本地执行: uv run python -c \"from src.gmail.client import GmailClient; GmailClient()\"\n"
                        "2. 完成浏览器授权\n"
                        "3. 上传新的 credentials/token.pickle 到服务器"
                    )

                logger.info("执行 OAuth 认证流程")
                if not os.path.exists(self.credentials_path):
                    raise FileNotFoundError(
                        f"凭证文件不存在: {self.credentials_path}\n"
                        "请从 Google Cloud Console 下载 credentials.json"
                    )

                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, SCOPES
                )
                creds = flow.run_local_server(port=0)

                # 保存令牌供下次使用
                os.makedirs(os.path.dirname(self.token_path), exist_ok=True)
                with open(self.token_path, 'wb') as token:
                    pickle.dump(creds, token)
                logger.info(f"访问令牌已保存: {self.token_path}")

                # 打印 token 信息供 Render 部署使用
                self._print_token_for_deployment(creds)

        # 构建 Gmail API 服务
        # 注意：代理通过环境变量 HTTP_PROXY/HTTPS_PROXY 配置
        # Google API 客户端会自动读取这些环境变量
        self.service = build('gmail', 'v1', credentials=creds)
        logger.info("Gmail API 客户端初始化成功")

    def _print_token_for_deployment(self, creds: Credentials) -> None:
        """
        打印 token 信息供 Render 部署使用
        """
        import json
        token_data = {
            'token': creds.token,
            'refresh_token': creds.refresh_token,
            'token_uri': creds.token_uri,
            'client_id': creds.client_id,
            'client_secret': creds.client_secret,
            'scopes': creds.scopes
        }
        token_json = json.dumps(token_data)

        print("\n" + "="*60)
        print("🔑 Gmail Token 信息（用于 Render 部署）")
        print("="*60)
        print("\n请将以下内容设置为 Render 环境变量 GMAIL_TOKEN_JSON：\n")
        print(token_json)
        print("\n" + "="*60 + "\n")
    
    def search_emails(
        self,
        sender: str,
        max_results: int = 10,
        days_back: int = 1
    ) -> List[Dict[str, Any]]:
        """
        搜索来自指定发件人的邮件
        
        Args:
            sender: 发件人邮箱地址
            max_results: 最大返回数量
            days_back: 搜索最近几天的邮件
        
        Returns:
            邮件列表
        """
        try:
            # 构建搜索查询
            query = f"from:{sender}"
            if days_back > 0:
                query += f" newer_than:{days_back}d"
            
            logger.info(f"搜索邮件: {query}")
            
            # 调用 Gmail API
            results = self.service.users().messages().list(
                userId='me',
                q=query,
                maxResults=max_results
            ).execute()
            
            messages = results.get('messages', [])
            logger.info(f"找到 {len(messages)} 封邮件")
            
            return messages
        
        except HttpError as error:
            logger.error(f"Gmail API 错误: {error}")
            raise
    
    def get_email_content(self, message_id: str) -> Dict[str, Any]:
        """
        获取邮件完整内容
        
        Args:
            message_id: 邮件 ID
        
        Returns:
            邮件详细信息
        """
        try:
            logger.info(f"获取邮件内容: {message_id}")
            
            message = self.service.users().messages().get(
                userId='me',
                id=message_id,
                format='full'
            ).execute()
            
            return message
        
        except HttpError as error:
            logger.error(f"获取邮件失败: {error}")
            raise
    
    def get_latest_email(
        self,
        sender: str,
        days_back: int = 1
    ) -> Optional[Dict[str, Any]]:
        """
        获取来自指定发件人的最新邮件
        
        Args:
            sender: 发件人邮箱地址
            days_back: 搜索最近几天的邮件
        
        Returns:
            最新邮件的完整内容，如果没有则返回 None
        """
        messages = self.search_emails(sender, max_results=1, days_back=days_back)
        
        if not messages:
            logger.warning(f"未找到来自 {sender} 的邮件")
            return None
        
        message_id = messages[0]['id']
        return self.get_email_content(message_id)
    
    def extract_email_data(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        从 Gmail API 响应中提取邮件数据

        Args:
            message: Gmail API 返回的邮件对象

        Returns:
            提取的邮件数据
        """
        headers = message['payload']['headers']

        # 提取邮件头信息
        subject = next(
            (h['value'] for h in headers if h['name'].lower() == 'subject'),
            'No Subject'
        )
        sender = next(
            (h['value'] for h in headers if h['name'].lower() == 'from'),
            'Unknown'
        )
        date_str = next(
            (h['value'] for h in headers if h['name'].lower() == 'date'),
            ''
        )

        return {
            'id': message['id'],
            'thread_id': message['threadId'],
            'subject': subject,
            'sender': sender,
            'date': date_str,
            'snippet': message.get('snippet', ''),
            'payload': message['payload']
        }

    def get_email_html(self, message_id: str) -> Optional[str]:
        """
        获取邮件的 HTML 内容

        Args:
            message_id: 邮件 ID

        Returns:
            HTML 内容，如果没有则返回 None
        """
        try:
            message = self.get_email_content(message_id)

            # 导入 EmailParser 来提取 HTML
            from .parser import EmailParser
            parser = EmailParser()

            payload = message.get('payload', {})
            html_content, _ = parser._extract_content(payload)

            return html_content

        except Exception as e:
            logger.error(f"获取邮件 HTML 失败: {e}")
            return None

