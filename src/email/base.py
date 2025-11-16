"""
邮箱客户端抽象基类
定义所有邮箱客户端必须实现的接口
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any


class EmailClient(ABC):
    """邮箱客户端抽象基类"""
    
    @abstractmethod
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
            邮件列表,每个邮件包含 id 等基本信息
        """
        pass
    
    @abstractmethod
    def get_email_content(self, message_id: str) -> Dict[str, Any]:
        """
        获取邮件完整内容
        
        Args:
            message_id: 邮件 ID
        
        Returns:
            邮件详细信息,包含 payload 等完整数据
        """
        pass
    
    @abstractmethod
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
        pass

