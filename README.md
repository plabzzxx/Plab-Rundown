# Plab-Rundown - The Rundown AI 邮件翻译与公众号发布系统

## 项目概述

自动从 Gmail 获取 The Rundown AI 每日邮件，通过 AI 翻译后发布到微信公众号。

## 核心功能

1. **邮件获取** - 从 Gmail 获取 The Rundown AI 的每日邮件
2. **AI 翻译** - 使用 LangChain + OpenAI/Gemini 进行英译中
3. **微信发布** - 自动发布到微信公众号草稿箱
4. **定时执行** - 支持定时任务自动运行

## 技术栈

- **Python 3.11+**
- **LangChain + OpenAI/Gemini** - AI 翻译
- **Gmail API** - 邮件获取
- **微信公众号 API** - 内容发布
- **APScheduler** - 定时任务调度

---

## 🚀 部署方式

本项目支持三种部署方式:

### 1. GitHub Actions 部署 (无服务器)

适合不想维护服务器的用户。

**配置步骤:**

1. Fork 本仓库
2. 在 GitHub 仓库设置中添加以下 Secrets:
   - `GMAIL_TOKEN_JSON` - Gmail API Token (JSON 格式)
   - `OPENAI_API_KEY` - OpenAI API Key
   - `WECHAT_APP_ID` - 微信公众号 AppID
   - `WECHAT_APP_SECRET` - 微信公众号 AppSecret

3. 手动触发或等待定时运行 (每天 UTC 12:00 / 北京时间 20:00)

**详细文档:** 见上方原有说明

---

### 2. 服务器部署 (推荐)

适合需要更灵活控制的用户。

**快速开始:**

```bash
# 1. 连接到服务器
ssh ubuntu@your-server-ip

# 2. 克隆项目
git clone https://github.com/your-username/Plab-Rundown.git plab-rundown
cd plab-rundown

# 3. 运行一键部署脚本
chmod +x deploy/deploy.sh
bash deploy/deploy.sh

# 4. 配置环境变量
cp .env.example .env
nano .env  # 填写你的配置

# 5. 上传 Gmail 凭证 (在本地执行)
scp credentials/* ubuntu@your-server-ip:~/plab-rundown/credentials/

# 6. 启动服务
sudo systemctl start plab-rundown
```

**详细文档:**
- 📖 [服务器快速设置指南](deploy/SERVER_SETUP.md)
- 📖 [完整部署文档](deploy/README.md)
- 📖 [快速部署指南](DEPLOYMENT.md)

---

### 3. Docker 部署

适合喜欢容器化部署的用户。

**快速开始:**

```bash
# 1. 安装 Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 2. 准备项目
cd ~/plab-rundown
cp .env.example .env
nano .env  # 配置环境变量

# 3. 启动容器
cd deploy
docker compose up -d

# 4. 查看状态
docker compose ps
docker compose logs -f
```

**详细文档:** 见 [deploy/README.md](deploy/README.md)

---

## 📁 项目结构

```
Plab-Rundown/
├── src/                    # 源代码
│   ├── gmail/             # Gmail 邮件获取
│   ├── translator/        # AI 翻译
│   ├── wechat/            # 微信公众号发布
│   ├── scheduler/         # 定时任务调度
│   └── utils/             # 工具函数
├── config/                # 配置文件
├── credentials/           # Gmail API 凭证
├── deploy/                # 部署相关文件
│   ├── deploy.sh         # 一键部署脚本
│   ├── Dockerfile        # Docker 镜像
│   ├── docker-compose.yml # Docker Compose 配置
│   ├── scripts/          # 管理脚本
│   │   ├── check_status.sh   # 状态检查
│   │   ├── manual_run.sh     # 手动运行
│   │   └── backup.sh         # 数据备份
│   ├── README.md         # 详细部署文档
│   └── SERVER_SETUP.md   # 服务器快速设置
├── .env.example          # 环境变量示例
├── requirements.txt      # Python 依赖
├── DEPLOYMENT.md         # 快速部署指南
└── README.md            # 本文件
```

---

## ⚙️ 配置说明

### 环境变量

复制 `.env.example` 为 `.env` 并填写配置:

```bash
# Gmail API 配置
GMAIL_CREDENTIALS_PATH=credentials/credentials.json
GMAIL_TOKEN_PATH=credentials/token.pickle
SENDER_EMAIL=news@daily.therundown.ai

# AI 服务商 (openai / vertex_ai / google_ai)
AI_PROVIDER=openai
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4o-mini

# 微信公众号配置
WECHAT_APP_ID=your_app_id
WECHAT_APP_SECRET=your_app_secret

# 应用配置
APP_ENV=production
SCHEDULE_ENABLED=true
SCHEDULE_TIME=09:00
TIMEZONE=Asia/Shanghai
```

### 定时任务

编辑 `config/config.yaml`:

```yaml
scheduler:
  enabled: true
  timezone: "Asia/Shanghai"
  cron:
    hour: 9      # 每天 9:00 执行
    minute: 0
```

---

## 🔧 管理命令

### systemd 服务管理

```bash
# 启动/停止/重启
sudo systemctl start plab-rundown
sudo systemctl stop plab-rundown
sudo systemctl restart plab-rundown

# 查看状态和日志
sudo systemctl status plab-rundown
journalctl -u plab-rundown -f
```

### Docker 容器管理

```bash
cd deploy

# 启动/停止/重启
docker compose up -d
docker compose down
docker compose restart

# 查看日志
docker compose logs -f
```

### 实用脚本

```bash
# 检查服务状态
bash deploy/scripts/check_status.sh

# 手动运行一次工作流
bash deploy/scripts/manual_run.sh

# 备份数据
bash deploy/scripts/backup.sh
```

---

## 📊 健康检查

服务启动后访问健康检查接口:

```bash
curl http://localhost:10000/health
```

---

## 📖 文档索引

- 📘 [快速部署指南](DEPLOYMENT.md) - 5分钟快速部署
- 📗 [服务器设置指南](deploy/SERVER_SETUP.md) - 服务器端操作指南
- 📙 [详细部署文档](deploy/README.md) - 完整部署说明
- 📕 [环境变量示例](.env.example) - 配置参考

---

## 🐛 故障排查

查看日志:
```bash
# 应用日志
tail -f logs/app.log

# 服务日志 (systemd)
journalctl -u plab-rundown -f

# Docker 日志
docker compose logs -f
```

常见问题解决方案见 [deploy/README.md](deploy/README.md#常见问题)

---

## 📞 获取帮助

- 📖 查看文档: `deploy/` 目录下的各种文档
- 🐛 提交问题: GitHub Issues
- 📧 联系作者: 见项目信息

---

## 许可证

MIT License
