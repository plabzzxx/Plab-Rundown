#!/usr/bin/env python3
"""测试邮件搜索 - 检查所有文件夹"""

from src.email.factory import create_email_client
from datetime import datetime, timedelta
import email

print('🔍 开始测试邮件搜索...\n')

# 创建邮箱客户端
client = create_email_client()
print(f'✅ 邮箱客户端创建成功: {type(client).__name__}\n')

# 测试1: 在 INBOX 搜索
print('📬 测试1: 在 INBOX 搜索邮件')
print('=' * 60)
emails = client.search_emails(sender='news@daily.therundown.ai', days_back=2, max_results=5)
print(f'找到 {len(emails)} 封邮件')
if emails:
    for i, email_data in enumerate(emails, 1):
        print(f'\n邮件 {i}:')
        print(f'  ID: {email_data.get("id", "N/A")}')
        print(f'  主题: {email_data.get("subject", "N/A")}')
        print(f'  日期: {email_data.get("date", "N/A")}')
else:
    print('❌ INBOX 中未找到邮件\n')

# 测试2: 列出所有文件夹
print('\n📁 测试2: 列出所有邮箱文件夹')
print('=' * 60)
imap = client.mail
status, folders = imap.list()
if status == 'OK':
    print('所有文件夹:')
    for folder in folders:
        folder_str = folder.decode() if isinstance(folder, bytes) else str(folder)
        print(f'  {folder_str}')
print()

# 测试3: 在所有文件夹中搜索
print('\n🔎 测试3: 在常见文件夹中搜索')
print('=' * 60)

# QQ邮箱的常见文件夹
common_folders = [
    'INBOX',           # 收件箱
    'Sent Messages',   # 已发送
    'Drafts',          # 草稿箱
    'Deleted Messages',# 已删除
    'Junk',            # 垃圾邮件
    'Archive',         # 归档
    'Archived',        # 归档(另一种命名)
]

for folder_name in common_folders:
    try:
        status, _ = imap.select(folder_name, readonly=True)
        if status == 'OK':
            print(f'\n✅ 文件夹 "{folder_name}" 存在')
            # 搜索最近2天的邮件
            since_date = (datetime.now() - timedelta(days=2)).strftime('%d-%b-%Y')
            status, messages = imap.search(None, f'(FROM "news@daily.therundown.ai" SINCE {since_date})')
            if status == 'OK':
                message_ids = messages[0].split()
                print(f'  找到 {len(message_ids)} 封邮件')
                if message_ids:
                    # 获取最新一封的信息
                    latest_id = message_ids[-1]
                    status, msg_data = imap.fetch(latest_id, '(BODY[HEADER.FIELDS (SUBJECT DATE)])')
                    if status == 'OK':
                        msg = email.message_from_bytes(msg_data[0][1])
                        print(f'  最新邮件主题: {msg.get("Subject", "N/A")}')
                        print(f'  日期: {msg.get("Date", "N/A")}')
        else:
            print(f'⚠️  文件夹 "{folder_name}" 不存在或无法访问')
    except Exception as e:
        print(f'❌ 检查文件夹 "{folder_name}" 时出错: {e}')

# 测试4: 搜索所有文件夹(包括自定义文件夹)
print('\n\n🔍 测试4: 在所有文件夹中搜索')
print('=' * 60)
if status == 'OK':
    for folder in folders:
        folder_str = folder.decode() if isinstance(folder, bytes) else str(folder)
        # 提取文件夹名称(去掉前缀)
        parts = folder_str.split('"')
        if len(parts) >= 3:
            folder_name = parts[-2]
        else:
            continue
        
        try:
            status, _ = imap.select(folder_name, readonly=True)
            if status == 'OK':
                since_date = (datetime.now() - timedelta(days=2)).strftime('%d-%b-%Y')
                status, messages = imap.search(None, f'(FROM "news@daily.therundown.ai" SINCE {since_date})')
                if status == 'OK':
                    message_ids = messages[0].split()
                    if message_ids:
                        print(f'\n✅ 在 "{folder_name}" 找到 {len(message_ids)} 封邮件')
                        # 获取最新一封的信息
                        latest_id = message_ids[-1]
                        status, msg_data = imap.fetch(latest_id, '(BODY[HEADER.FIELDS (SUBJECT DATE)])')
                        if status == 'OK':
                            msg = email.message_from_bytes(msg_data[0][1])
                            print(f'  最新邮件主题: {msg.get("Subject", "N/A")}')
                            print(f'  日期: {msg.get("Date", "N/A")}')
        except Exception as e:
            pass  # 忽略无法访问的文件夹

print('\n' + '=' * 60)
print('✅ 测试完成!')

