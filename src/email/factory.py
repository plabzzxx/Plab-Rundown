"""
邮箱客户端工厂
根据配置创建对应的邮箱客户端 (Gmail API 或 IMAP)
"""

import os
import yaml
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

from .base import EmailClient
from .gmail_client import GmailClient
from .imap_client import IMAPClient
from ..utils.logger import get_logger

# 加载环境变量
load_dotenv()

logger = get_logger(__name__)


def create_email_client(
    config_path: str = "config/config.yaml",
    provider: Optional[str] = None
) -> EmailClient:
    """
    根据配置创建邮箱客户端
    
    Args:
        config_path: 配置文件路径
        provider: 强制指定邮箱服务类型 (gmail_api | imap),如果为 None 则从配置文件读取
    
    Returns:
        EmailClient: Gmail API 或 IMAP 客户端
    
    Raises:
        ValueError: 不支持的邮箱服务类型
        FileNotFoundError: 配置文件不存在
    """
    # 读取配置文件
    config_file = Path(config_path)
    
    if not config_file.exists():
        logger.warning(f"配置文件不存在: {config_path}, 使用默认配置")
        email_config = {}
    else:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
            email_config = config.get('email', {})
    
    # 确定邮箱服务类型
    if provider is None:
        provider = email_config.get('provider', 'gmail_api')
    
    logger.info(f"使用邮箱服务: {provider}")
    
    # 根据类型创建客户端
    if provider == 'gmail_api':
        return _create_gmail_client(email_config)
    elif provider == 'imap':
        return _create_imap_client(email_config)
    else:
        raise ValueError(f"不支持的邮箱服务类型: {provider}")


def _create_gmail_client(email_config: dict) -> GmailClient:
    """
    创建 Gmail API 客户端
    
    Args:
        email_config: 邮箱配置
    
    Returns:
        GmailClient
    """
    gmail_config = email_config.get('gmail_api', {})
    
    # 从配置或环境变量获取凭证路径
    credentials_path = (
        gmail_config.get('credentials_path') or
        os.getenv('GMAIL_CREDENTIALS_PATH', 'credentials/credentials.json')
    )
    
    token_path = (
        gmail_config.get('token_path') or
        os.getenv('GMAIL_TOKEN_PATH', 'credentials/token.pickle')
    )
    
    logger.info(f"创建 Gmail API 客户端")
    logger.info(f"  凭证路径: {credentials_path}")
    logger.info(f"  Token 路径: {token_path}")
    
    return GmailClient(
        credentials_path=credentials_path,
        token_path=token_path
    )


def _create_imap_client(email_config: dict) -> IMAPClient:
    """
    创建 IMAP 客户端
    
    Args:
        email_config: 邮箱配置
    
    Returns:
        IMAPClient
    """
    imap_config = email_config.get('imap', {})
    
    # 从配置获取 IMAP 服务器信息
    server = imap_config.get('server')
    port = imap_config.get('port', 993)
    use_ssl = imap_config.get('use_ssl', True)
    folder = imap_config.get('folder', 'INBOX')
    
    # 从环境变量获取账号密码
    username = os.getenv('EMAIL_USERNAME')
    password = os.getenv('EMAIL_PASSWORD')
    
    # 验证必填参数
    if not server:
        raise ValueError("IMAP 服务器地址未配置 (config.yaml -> email.imap.server)")
    
    if not username:
        raise ValueError("邮箱账号未配置 (环境变量 EMAIL_USERNAME)")
    
    if not password:
        raise ValueError("邮箱密码/授权码未配置 (环境变量 EMAIL_PASSWORD)")
    
    logger.info(f"创建 IMAP 客户端")
    logger.info(f"  服务器: {server}:{port}")
    logger.info(f"  账号: {username}")
    logger.info(f"  SSL: {use_ssl}")
    logger.info(f"  文件夹: {folder}")
    
    return IMAPClient(
        server=server,
        username=username,
        password=password,
        port=port,
        use_ssl=use_ssl,
        folder=folder
    )

