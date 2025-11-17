#!/usr/bin/env python3
"""测试获取最新邮件"""

from src.email.factory import create_email_client
from datetime import datetime

print('🔍 获取最新邮件详情...\n')

# 创建邮箱客户端
client = create_email_client()
print(f'✅ 邮箱客户端创建成功: {type(client).__name__}\n')

# 搜索邮件
print('📬 搜索来自 news@daily.therundown.ai 的邮件')
print('=' * 60)
emails = client.search_emails(sender='news@daily.therundown.ai', days_back=3, max_results=10)
print(f'找到 {len(emails)} 封邮件\n')

if emails:
    # 显示所有邮件
    for i, email_data in enumerate(emails, 1):
        print(f'邮件 {i}:')
        print(f'  ID: {email_data.get("id", "N/A")}')
        print(f'  主题: {email_data.get("subject", "N/A")}')
        print(f'  发件人: {email_data.get("from", "N/A")}')
        print(f'  日期: {email_data.get("date", "N/A")}')
        print()
    
    # 获取最新一封的完整内容
    print('\n' + '=' * 60)
    print('📧 最新邮件完整信息:')
    print('=' * 60)
    latest = client.get_latest_email(sender='news@daily.therundown.ai', days_back=3)

    if latest:
        print(f'ID: {latest.get("id")}')

        # 从 headers 中提取信息
        headers = latest.get('payload', {}).get('headers', [])
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'N/A')
        from_addr = next((h['value'] for h in headers if h['name'] == 'From'), 'N/A')
        date_str = next((h['value'] for h in headers if h['name'] == 'Date'), 'N/A')

        print(f'主题: {subject}')
        print(f'发件人: {from_addr}')
        print(f'日期: {date_str}')

        # 检查是否有 HTML 内容
        html = client.get_email_html(latest.get("id"))
        if html:
            print(f'\n✅ HTML 内容长度: {len(html)} 字符')
            print(f'HTML 前 200 字符:\n{html[:200]}...')
        else:
            print('\n❌ 未找到 HTML 内容')
    else:
        print('❌ 未找到最新邮件')
else:
    print('❌ 未找到任何邮件')

print('\n' + '=' * 60)
print('✅ 测试完成!')

