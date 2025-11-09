#!/usr/bin/env python3
"""
Gmail Token 刷新脚本
用于在本地重新生成 Gmail OAuth token

使用方法:
    uv run python scripts/refresh_gmail_token.py
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.gmail.client import GmailClient
from src.utils.logger import get_logger

logger = get_logger(__name__)


def main():
    """主函数"""
    print("=" * 70)
    print("📧 Gmail Token 刷新工具")
    print("=" * 70)
    print()
    
    credentials_path = "credentials/credentials.json"
    token_path = "credentials/token.pickle"
    
    # 检查 credentials.json 是否存在
    if not Path(credentials_path).exists():
        print(f"❌ 错误: 找不到 {credentials_path}")
        print()
        print("请先从 Google Cloud Console 下载 OAuth 凭证文件:")
        print("1. 访问 https://console.cloud.google.com/")
        print("2. 选择你的项目")
        print("3. 进入 APIs & Services > Credentials")
        print("4. 下载 OAuth 2.0 Client ID 的 JSON 文件")
        print(f"5. 保存为 {credentials_path}")
        return 1
    
    print(f"✅ 找到凭证文件: {credentials_path}")
    print()
    
    # 删除旧的 token
    token_file = Path(token_path)
    if token_file.exists():
        print(f"🗑️  删除旧的 token: {token_path}")
        token_file.unlink()
        print()
    
    print("🔐 开始 OAuth 授权流程...")
    print("⚠️  浏览器将自动打开,请完成授权")
    print()
    
    try:
        # 初始化 Gmail 客户端(会自动触发授权流程)
        gmail_client = GmailClient(
            credentials_path=credentials_path,
            token_path=token_path
        )
        
        print()
        print("=" * 70)
        print("✅ Token 生成成功!")
        print("=" * 70)
        print()
        print(f"Token 已保存到: {token_path}")
        print()
        print("📤 下一步: 上传 token 到服务器")
        print()
        print("在本地执行以下命令:")
        print(f"    scp {token_path} root@你的服务器IP:/root/Plab-Rundown/{token_path}")
        print()
        print("然后重启 Docker 容器:")
        print("    cd /root/Plab-Rundown/deploy")
        print("    docker-compose restart")
        print()
        
        return 0
        
    except Exception as e:
        print()
        print("=" * 70)
        print("❌ Token 生成失败!")
        print("=" * 70)
        print()
        print(f"错误信息: {e}")
        print()
        return 1


if __name__ == "__main__":
    sys.exit(main())

