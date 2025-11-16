# 📧 邮箱服务配置指南

本项目支持两种邮箱服务:
1. **Gmail API** - 功能强大,但需要 OAuth 认证和代理
2. **IMAP** - 简单易用,支持 QQ/163/Gmail,不需要代理 ✅ 推荐

---

## 🎯 快速开始 - 使用 QQ 邮箱 (推荐)

### 步骤 1: 获取 QQ 邮箱授权码

1. 登录 [QQ 邮箱网页版](https://mail.qq.com)
2. 点击 **设置** → **账户**
3. 找到 **POP3/IMAP/SMTP/Exchange/CardDAV/CalDAV服务**
4. 开启 **IMAP/SMTP 服务**
5. 点击 **生成授权码**,按提示发送短信
6. **复制授权码** (16位字符,类似: `abcdEFGH1234ijkl`)

⚠️ **注意**: 授权码不是 QQ 密码!请妥善保管授权码。

### 步骤 2: 配置项目

编辑 `.env` 文件:

```bash
# IMAP 邮箱配置
EMAIL_USERNAME=your_qq_email@qq.com        # 你的 QQ 邮箱
EMAIL_PASSWORD=abcdEFGH1234ijkl            # 刚才获取的授权码
```

编辑 `config/config.yaml`:

```yaml
email:
  provider: "imap"                          # 使用 IMAP
  sender_email: "news@daily.therundown.ai"  # 订阅的邮件发件人
  
  imap:
    server: "imap.qq.com"                   # QQ 邮箱 IMAP 服务器
    port: 993
    use_ssl: true
    folder: "INBOX"
```

### 步骤 3: 测试

```bash
# 本地测试
uv run python workflow.py

# Docker 测试
docker exec plab-rundown python -c "from src.email.factory import create_email_client; client = create_email_client(); print('✅ 邮箱连接成功!')"
```

---

## 📮 其他邮箱服务配置

### 163 邮箱

**获取授权码**:
1. 登录 [163 邮箱](https://mail.163.com)
2. 设置 → POP3/SMTP/IMAP → 开启 IMAP 服务
3. 生成授权码

**配置**:
```yaml
# config/config.yaml
email:
  provider: "imap"
  imap:
    server: "imap.163.com"
    port: 993
```

```bash
# .env
EMAIL_USERNAME=your_email@163.com
EMAIL_PASSWORD=your_163_authorization_code
```

---

### Gmail IMAP

**开启 IMAP**:
1. 登录 Gmail
2. 设置 → 转发和 POP/IMAP → 启用 IMAP
3. 如果开启了两步验证,需要生成应用专用密码

**配置**:
```yaml
# config/config.yaml
email:
  provider: "imap"
  imap:
    server: "imap.gmail.com"
    port: 993
```

```bash
# .env
EMAIL_USERNAME=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
```

⚠️ **注意**: Gmail IMAP 在国内可能需要代理。

---

## 🔧 Gmail API 配置 (高级)

如果你需要使用 Gmail API (不推荐,除非有特殊需求):

### 步骤 1: 获取 OAuth 凭证

1. 访问 [Google Cloud Console](https://console.cloud.google.com)
2. 创建项目 → 启用 Gmail API
3. 创建 OAuth 2.0 凭证
4. 下载 `credentials.json` 到 `credentials/` 目录

### 步骤 2: 本地授权

```bash
uv run python -c "from src.email.gmail_client import GmailClient; GmailClient(credentials_path='credentials/credentials.json')"
```

浏览器会打开授权页面,完成授权后会生成 `credentials/token.pickle`。

### 步骤 3: 配置

```yaml
# config/config.yaml
email:
  provider: "gmail_api"
  gmail_api:
    credentials_path: "credentials/credentials.json"
    token_path: "credentials/token.pickle"
```

### 步骤 4: 上传到服务器

```bash
scp credentials/credentials.json root@your-server:/root/Plab-Rundown/credentials/
scp credentials/token.pickle root@your-server:/root/Plab-Rundown/credentials/
```

---

## 🚀 切换邮箱服务

只需修改 `config/config.yaml` 中的 `email.provider`:

```yaml
email:
  provider: "imap"        # 或 "gmail_api"
```

重启服务:

```bash
cd deploy
docker-compose restart
```

---

## ❓ 常见问题

### Q1: QQ 邮箱授权码在哪里找?

A: QQ 邮箱网页版 → 设置 → 账户 → 开启 IMAP/SMTP 服务 → 生成授权码

### Q2: 提示 "IMAP 连接失败"?

A: 检查:
1. 授权码是否正确 (不是 QQ 密码!)
2. 是否开启了 IMAP 服务
3. 服务器地址是否正确 (`imap.qq.com`)

### Q3: 为什么推荐 IMAP 而不是 Gmail API?

A: 
- ✅ IMAP 不需要代理 (国内服务器友好)
- ✅ 配置简单,不需要 OAuth 授权
- ✅ 支持多种邮箱服务 (QQ/163/Gmail)
- ❌ Gmail API 需要代理,配置复杂

### Q4: 可以同时配置多个邮箱吗?

A: 目前不支持。如果需要切换邮箱,修改 `.env` 中的 `EMAIL_USERNAME` 和 `EMAIL_PASSWORD` 即可。

---

## 📝 技术细节

### 代码架构

```
src/email/
├── base.py              # 抽象基类 (EmailClient 接口)
├── gmail_client.py      # Gmail API 实现
├── imap_client.py       # IMAP 实现
└── factory.py           # 工厂方法,根据配置创建客户端
```

### 接口兼容性

IMAP 客户端返回的数据格式与 Gmail API 兼容,因此切换邮箱服务不需要修改其他代码。

---

## 🎉 总结

**推荐配置**: QQ 邮箱 + IMAP

- 简单: 只需授权码,无需 OAuth
- 稳定: 不需要代理,国内服务器友好
- 免费: QQ 邮箱免费,无限制

如有问题,请查看日志: `logs/app.log`

