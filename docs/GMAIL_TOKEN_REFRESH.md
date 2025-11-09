# Gmail Token 自动刷新说明

## 问题背景

Gmail OAuth token 有两种类型:
- **Access Token**: 有效期 1 小时,用于实际 API 调用
- **Refresh Token**: 长期有效,用于自动获取新的 Access Token

## 自动刷新机制

本项目已经实现了 **自动刷新** 功能:

1. ✅ 当 Access Token 过期时,自动使用 Refresh Token 刷新
2. ✅ 刷新成功后,自动保存新的 token 到文件
3. ✅ 下次启动时直接使用刷新后的 token

**理论上,只要 Refresh Token 有效,就不需要手动重新授权。**

## 什么时候需要手动重新授权?

只有在以下情况下才需要手动重新授权:

1. **Refresh Token 被撤销**
   - 在 Google 账户中手动撤销了应用授权
   - Google 检测到安全问题自动撤销

2. **Refresh Token 过期**
   - 长期未使用(通常 6 个月)
   - Google 账户密码被修改

3. **首次部署**
   - 第一次在新环境中运行

## 如何手动重新授权?

### 方法 1: 使用刷新脚本(推荐)

在**本地 Windows 机器**上执行:

```bash
# 进入项目目录
cd e:\xProject\Plab-Rundown

# 运行刷新脚本
uv run python scripts/refresh_gmail_token.py
```

脚本会:
1. 自动删除旧的 token
2. 打开浏览器进行授权
3. 保存新的 token
4. 提示你如何上传到服务器

### 方法 2: 手动操作

```bash
# 1. 删除旧的 token
rm credentials/token.pickle

# 2. 重新生成 token
uv run python -c "from src.gmail.client import GmailClient; GmailClient(credentials_path='credentials/credentials.json')"

# 3. 完成浏览器授权

# 4. 上传到服务器
scp credentials/token.pickle root@你的服务器IP:/root/Plab-Rundown/credentials/

# 5. 重启 Docker 容器
ssh root@你的服务器IP
cd /root/Plab-Rundown/deploy
docker-compose restart
```

## 常见错误及解决方案

### 错误 1: `Token has been expired or revoked`

**原因**: Refresh Token 已过期或被撤销

**解决方案**: 按照上面的步骤重新授权

### 错误 2: `could not locate runnable browser`

**原因**: 在 Docker 容器中无法打开浏览器

**解决方案**: 
- ✅ 在本地重新生成 token
- ✅ 上传到服务器
- ❌ 不要在服务器上直接运行授权流程

### 错误 3: `invalid_grant: Bad Request`

**原因**: 
- credentials.json 和 token.pickle 不匹配
- 或者 Google 项目配置有变化

**解决方案**:
1. 删除 `credentials/token.pickle`
2. 重新下载 `credentials/credentials.json` (如果有变化)
3. 重新授权

## 最佳实践

### 1. 定期检查 Token 状态

可以在本地运行测试,确保 token 有效:

```bash
uv run python -c "
from src.gmail.client import GmailClient
client = GmailClient(credentials_path='credentials/credentials.json')
print('✅ Gmail token 有效')
"
```

### 2. 备份 Token 文件

将 `credentials/token.pickle` 备份到安全的地方,避免丢失。

### 3. 监控日志

定期检查服务器日志,看是否有 token 刷新的记录:

```bash
# 查看最近的 token 刷新日志
docker logs plab-rundown | grep "令牌刷新"
```

如果看到:
- `令牌刷新成功` - ✅ 正常
- `令牌刷新失败` - ❌ 需要重新授权

## 技术细节

### Token 刷新流程

```python
# 1. 加载已保存的 token
creds = pickle.load(open('credentials/token.pickle', 'rb'))

# 2. 检查是否过期
if creds.expired and creds.refresh_token:
    # 3. 使用 refresh_token 刷新
    creds.refresh(Request())
    
    # 4. 保存新的 token
    pickle.dump(creds, open('credentials/token.pickle', 'wb'))
```

### Token 文件结构

`token.pickle` 包含:
- `token`: Access Token (1小时有效)
- `refresh_token`: Refresh Token (长期有效)
- `token_uri`: Token 刷新 API 地址
- `client_id`: OAuth 客户端 ID
- `client_secret`: OAuth 客户端密钥
- `scopes`: 授权范围

## 故障排查

### 1. 查看详细日志

```bash
# 查看容器日志
docker logs plab-rundown --tail 100

# 查看应用日志
tail -100 /root/Plab-Rundown/logs/app.log
```

### 2. 测试 Gmail API 连接

在服务器上执行:

```bash
docker exec plab-rundown python -c "
from src.gmail.client import GmailClient
try:
    client = GmailClient(credentials_path='credentials/credentials.json')
    print('✅ Gmail 连接成功')
except Exception as e:
    print(f'❌ Gmail 连接失败: {e}')
"
```

### 3. 检查 credentials.json

确保 `credentials/credentials.json` 存在且格式正确:

```bash
cat credentials/credentials.json | python -m json.tool
```

## 相关链接

- [Google OAuth 2.0 文档](https://developers.google.com/identity/protocols/oauth2)
- [Gmail API 文档](https://developers.google.com/gmail/api)
- [Google Cloud Console](https://console.cloud.google.com/)

