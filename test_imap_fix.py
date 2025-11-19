"""测试 IMAP base64 编码修复"""

from src.email.factory import create_email_client
from src.gmail.parser import EmailParser

def test_imap_base64():
    print("🧪 测试 IMAP base64 编码修复")
    print("=" * 70)
    
    # 创建客户端
    print("\n1️⃣ 创建 IMAP 客户端...")
    client = create_email_client()
    print("✅ 客户端创建成功")
    
    # 获取最新邮件
    print("\n2️⃣ 获取最新邮件...")
    email_data = client.get_latest_email('news@daily.therundown.ai', days_back=7)
    
    if not email_data:
        print("❌ 未找到邮件")
        return
    
    print(f"✅ 获取邮件成功: {email_data['id']}")
    
    # 检查 body.data 是否是 base64 编码
    payload = email_data.get('payload', {})
    parts = payload.get('parts', [])
    
    if parts:
        for part in parts:
            if part.get('mimeType') == 'text/html':
                body_data = part.get('body', {}).get('data', '')
                print(f"\n📊 HTML body.data 前 100 字符:")
                print(f"   {body_data[:100]}")
                
                # 检查是否是 base64 (base64 只包含 A-Z, a-z, 0-9, +, /, =)
                import re
                is_base64 = bool(re.match(r'^[A-Za-z0-9+/=]+$', body_data[:100]))
                print(f"   是否是 base64: {'✅ 是' if is_base64 else '❌ 否'}")
                break
    
    # 解析邮件
    print("\n3️⃣ 解析邮件...")
    parser = EmailParser()
    
    try:
        parsed = parser.parse_email(email_data)
        
        if parsed and parsed.get('html'):
            print(f"✅ 解析成功!")
            print(f"   HTML 长度: {len(parsed['html'])} 字符")
            print(f"   HTML 前 200 字符:")
            print(f"   {parsed['html'][:200]}")
        else:
            print("❌ 解析失败: HTML 内容为空")
    
    except Exception as e:
        print(f"❌ 解析失败: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 70)
    print("🎉 测试完成!")

if __name__ == '__main__':
    test_imap_base64()

