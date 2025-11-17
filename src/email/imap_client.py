"""
IMAP 邮箱客户端
支持 QQ 邮箱、163 邮箱、Gmail IMAP 等
"""

import imaplib
import email
from email.header import decode_header
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import re

from .base import EmailClient
from ..utils.logger import get_logger

logger = get_logger(__name__)


class IMAPClient(EmailClient):
    """IMAP 邮箱客户端 (支持 QQ/163/Gmail IMAP)"""
    
    def __init__(
        self,
        server: str,
        username: str,
        password: str,
        port: int = 993,
        use_ssl: bool = True,
        folder: str = "INBOX"
    ):
        """
        初始化 IMAP 客户端
        
        Args:
            server: IMAP 服务器地址 (如 imap.qq.com)
            username: 邮箱账号
            password: 邮箱密码或授权码
            port: IMAP 端口 (默认 993)
            use_ssl: 是否使用 SSL (默认 True)
            folder: 邮箱文件夹 (默认 INBOX)
        """
        self.server = server
        self.username = username
        self.password = password
        self.port = port
        self.use_ssl = use_ssl
        self.folder = folder
        self.mail = None
        
        logger.info(f"初始化 IMAP 客户端: {server}:{port}")
        self._connect()
    
    def _connect(self) -> None:
        """连接到 IMAP 服务器"""
        try:
            if self.use_ssl:
                self.mail = imaplib.IMAP4_SSL(self.server, self.port)
            else:
                self.mail = imaplib.IMAP4(self.server, self.port)
            
            logger.info(f"连接到 IMAP 服务器: {self.server}")
            self.mail.login(self.username, self.password)
            logger.info("IMAP 登录成功")
            
            self.mail.select(self.folder)
            logger.info(f"选择邮箱文件夹: {self.folder}")
            
        except Exception as e:
            logger.error(f"IMAP 连接失败: {e}")
            raise
    
    def _decode_header(self, header_value: str) -> str:
        """解码邮件头部"""
        if not header_value:
            return ""
        
        decoded_parts = decode_header(header_value)
        result = []
        
        for part, encoding in decoded_parts:
            if isinstance(part, bytes):
                if encoding:
                    try:
                        result.append(part.decode(encoding))
                    except:
                        result.append(part.decode('utf-8', errors='ignore'))
                else:
                    result.append(part.decode('utf-8', errors='ignore'))
            else:
                result.append(str(part))
        
        return ''.join(result)
    
    def _parse_email_address(self, address: str) -> str:
        """从邮件地址字符串中提取纯邮箱地址"""
        # 匹配 <email@example.com> 或 email@example.com
        match = re.search(r'<(.+?)>|([^\s<>]+@[^\s<>]+)', address)
        if match:
            return match.group(1) or match.group(2)
        return address
    
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
            # 构建搜索条件
            date_since = (datetime.now() - timedelta(days=days_back)).strftime("%d-%b-%Y")
            search_criteria = f'(FROM "{sender}" SINCE {date_since})'
            
            logger.info(f"搜索邮件: {search_criteria}")
            
            # 搜索邮件
            status, messages = self.mail.search(None, search_criteria)
            
            if status != 'OK':
                logger.warning(f"搜索邮件失败: {status}")
                return []
            
            # 获取邮件 ID 列表
            email_ids = messages[0].split()
            
            if not email_ids:
                logger.info(f"未找到来自 {sender} 的邮件")
                return []
            
            # 限制返回数量,取最新的邮件
            email_ids = email_ids[-max_results:]

            logger.info(f"找到 {len(email_ids)} 封邮件")

            # 获取每封邮件的元数据
            emails = []
            for email_id in email_ids:
                try:
                    # 获取邮件头部信息
                    status, msg_data = self.mail.fetch(email_id, '(BODY[HEADER.FIELDS (SUBJECT FROM DATE)])')
                    if status == 'OK' and msg_data and msg_data[0]:
                        msg = email.message_from_bytes(msg_data[0][1])

                        # 提取元数据
                        subject = self._decode_header(msg.get('Subject', ''))
                        from_addr = self._decode_header(msg.get('From', ''))
                        date_str = msg.get('Date', '')

                        emails.append({
                            'id': email_id.decode(),
                            'subject': subject,
                            'from': from_addr,
                            'date': date_str
                        })
                    else:
                        # 如果获取失败,至少返回 ID
                        emails.append({'id': email_id.decode()})
                except Exception as e:
                    logger.warning(f"获取邮件 {email_id} 元数据失败: {e}")
                    emails.append({'id': email_id.decode()})

            return emails
        
        except Exception as e:
            logger.error(f"搜索邮件失败: {e}")
            raise
    
    def get_email_content(self, message_id: str) -> Dict[str, Any]:
        """
        获取邮件完整内容
        
        Args:
            message_id: 邮件 ID
        
        Returns:
            邮件详细信息 (格式兼容 Gmail API)
        """
        try:
            logger.info(f"获取邮件内容: {message_id}")
            
            # 获取邮件数据
            status, msg_data = self.mail.fetch(message_id, '(RFC822)')
            
            if status != 'OK':
                logger.error(f"获取邮件失败: {status}")
                raise Exception(f"获取邮件失败: {status}")
            
            # 解析邮件
            email_body = msg_data[0][1]
            email_message = email.message_from_bytes(email_body)
            
            # 提取邮件头部信息
            subject = self._decode_header(email_message.get('Subject', ''))
            from_addr = self._decode_header(email_message.get('From', ''))
            date_str = email_message.get('Date', '')
            
            logger.info(f"邮件主题: {subject}")
            logger.info(f"发件人: {from_addr}")
            
            # 提取邮件正文
            html_content = None
            text_content = None
            
            if email_message.is_multipart():
                for part in email_message.walk():
                    content_type = part.get_content_type()
                    
                    if content_type == 'text/html':
                        try:
                            html_content = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                        except:
                            pass
                    elif content_type == 'text/plain':
                        try:
                            text_content = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                        except:
                            pass
            else:
                content_type = email_message.get_content_type()
                payload = email_message.get_payload(decode=True)
                
                if payload:
                    if content_type == 'text/html':
                        html_content = payload.decode('utf-8', errors='ignore')
                    elif content_type == 'text/plain':
                        text_content = payload.decode('utf-8', errors='ignore')
            
            # 构建返回数据 (兼容 Gmail API 格式)
            result = {
                'id': message_id,
                'payload': {
                    'headers': [
                        {'name': 'Subject', 'value': subject},
                        {'name': 'From', 'value': from_addr},
                        {'name': 'Date', 'value': date_str}
                    ],
                    'parts': []
                }
            }
            
            # 添加邮件正文部分
            if html_content:
                result['payload']['parts'].append({
                    'mimeType': 'text/html',
                    'body': {
                        'data': html_content
                    }
                })
            
            if text_content:
                result['payload']['parts'].append({
                    'mimeType': 'text/plain',
                    'body': {
                        'data': text_content
                    }
                })
            
            # 如果没有 parts,直接放在 body 中
            if not result['payload']['parts'] and html_content:
                result['payload']['body'] = {
                    'data': html_content
                }
                result['payload']['mimeType'] = 'text/html'
            
            return result
        
        except Exception as e:
            logger.error(f"获取邮件内容失败: {e}")
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
            最新邮件的完整内容,如果没有则返回 None
        """
        # 获取所有邮件
        messages = self.search_emails(sender, max_results=50, days_back=days_back)

        if not messages:
            logger.warning(f"未找到来自 {sender} 的邮件")
            return None

        # 按日期排序,找到最新的
        from email.utils import parsedate_to_datetime

        latest_message = None
        latest_date = None

        for msg in messages:
            date_str = msg.get('date')
            if date_str:
                try:
                    msg_date = parsedate_to_datetime(date_str)
                    if latest_date is None or msg_date > latest_date:
                        latest_date = msg_date
                        latest_message = msg
                except Exception as e:
                    logger.warning(f"解析日期失败: {date_str}, {e}")

        if latest_message:
            message_id = latest_message['id']
            logger.info(f"找到最新邮件: {latest_message.get('subject')} ({latest_message.get('date')})")
            return self.get_email_content(message_id)

        # 如果没有日期信息,返回第一个
        message_id = messages[0]['id']
        return self.get_email_content(message_id)

    def extract_email_data(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        从邮件对象中提取邮件数据 (兼容 Gmail API 格式)

        Args:
            message: 邮件对象 (IMAP 格式)

        Returns:
            提取的邮件数据 (Gmail API 兼容格式)
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
            'thread_id': message.get('threadId', message['id']),  # IMAP 没有 threadId,用 id 代替
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
            HTML 内容,如果没有则返回 None
        """
        try:
            message = self.get_email_content(message_id)
            payload = message.get('payload', {})

            # IMAP 返回的内容已经是解码后的字符串,直接从 parts 中提取
            parts = payload.get('parts', [])

            # 优先查找 text/html 部分
            for part in parts:
                if part.get('mimeType') == 'text/html':
                    body = part.get('body', {})
                    html_content = body.get('data', '')
                    if html_content:
                        return html_content

            # 如果没有 parts,检查 body
            if not parts:
                body = payload.get('body', {})
                if payload.get('mimeType') == 'text/html':
                    return body.get('data', '')

            logger.warning("未找到 HTML 内容")
            return None

        except Exception as e:
            logger.error(f"获取邮件 HTML 失败: {e}")
            return None

    def __del__(self):
        """析构函数,关闭连接"""
        try:
            if self.mail:
                self.mail.close()
                self.mail.logout()
                logger.info("IMAP 连接已关闭")
        except:
            pass

