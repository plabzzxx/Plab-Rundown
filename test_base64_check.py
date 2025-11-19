"""检查 base64 编码"""

import base64

# 测试字符串
test_str = "PCFET0NUWVBFIGh0bWw-PGh0bWwgbGFuZz0iZW4iIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5L3hodG1sIiB4bWxuczp2"

print(f"测试字符串: {test_str}")
print(f"长度: {len(test_str)}")

# 检查字符
import re
is_base64_standard = bool(re.match(r'^[A-Za-z0-9+/=]+$', test_str))
is_base64_urlsafe = bool(re.match(r'^[A-Za-z0-9_-]+$', test_str))

print(f"\n标准 base64 (A-Z, a-z, 0-9, +, /, =): {is_base64_standard}")
print(f"URL-safe base64 (A-Z, a-z, 0-9, _, -): {is_base64_urlsafe}")

# 尝试解码
try:
    decoded = base64.urlsafe_b64decode(test_str).decode('utf-8')
    print(f"\n✅ URL-safe base64 解码成功!")
    print(f"解码结果: {decoded}")
except Exception as e:
    print(f"\n❌ URL-safe base64 解码失败: {e}")

try:
    decoded = base64.b64decode(test_str).decode('utf-8')
    print(f"\n✅ 标准 base64 解码成功!")
    print(f"解码结果: {decoded}")
except Exception as e:
    print(f"\n❌ 标准 base64 解码失败: {e}")

