"""
Gmail 邮件获取模块
"""

from .client import GmailClient
from .parser import EmailParser

__all__ = ["GmailClient", "EmailParser"]

