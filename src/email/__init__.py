"""
邮箱服务模块
支持多种邮箱服务: Gmail API, IMAP (QQ/163/Gmail)
"""

from .base import EmailClient
from .factory import create_email_client

__all__ = ['EmailClient', 'create_email_client']

