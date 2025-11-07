# Plab-Rundown 服务器部署指南

## 📋 目录

- [部署方式](#部署方式)
- [方式一: systemd 服务部署](#方式一-systemd-服务部署)
- [方式二: Docker 部署](#方式二-docker-部署)
- [配置说明](#配置说明)
- [常见问题](#常见问题)

---

## 🚀 部署方式

本项目支持两种部署方式:

1. **systemd 服务部署** - 推荐用于长期运行的生产环境
2. **Docker 容器部署** - 推荐用于快速部署和隔离环境

---

## 方式一: systemd 服务部署

### 1. 准备工作

确保服务器满足以下要求:
- Ubuntu 20.04+ 或其他 Linux 发行版
- Python 3.11+
- 至少 1GB 内存
- 至少 2GB 磁盘空间

### 2. 上传部署脚本

将项目代码上传到服务器:

```bash
# 方法 1: 使用 Git 克隆
cd /home/ubuntu
git clone <你的仓库地址> plab-rundown
cd plab-rundown

# 方法 2: 使用 scp 上传
# 在本地执行:
scp -r /path/to/plab-rundown ubuntu@your-server-ip:/home/ubuntu/
```

### 3. 运行部署脚本

```bash
cd /home/ubuntu/plab-rundown
chmod +x deploy/deploy.sh
bash deploy/deploy.sh
```

部署脚本会自动完成:
- ✅ 安装系统依赖 (Python 3.11, pip, git 等)
- ✅ 创建 Python 虚拟环境
- ✅ 安装 Python 依赖包
- ✅ 创建必要的目录
- ✅ 创建 systemd 服务
- ✅ 启用开机自启

### 4. 配置环境变量

编辑 `.env` 文件:

```bash
nano /home/ubuntu/plab-rundown/.env
```

必填配置项:

```bash
# Gmail API 配置
GMAIL_CREDENTIALS_PATH=credentials/credentials.json
GMAIL_TOKEN_PATH=credentials/token.pickle
SENDER_EMAIL=news@daily.therundown.ai

# AI 服务商配置
AI_PROVIDER=openai
OPENAI_API_KEY=sk-your-openai-api-key-here
OPENAI_MODEL=gpt-4o-mini

# 微信公众号配置
WECHAT_APP_ID=your_wechat_app_id
WECHAT_APP_SECRET=your_wechat_app_secret

# 应用配置
APP_ENV=production
SCHEDULE_ENABLED=true
SCHEDULE_TIME=09:00
TIMEZONE=Asia/Shanghai
```

### 5. 上传 Gmail 凭证文件

将 Gmail API 凭证文件上传到服务器:

```bash
# 在本地执行:
scp credentials/credentials.json ubuntu@your-server-ip:/home/ubuntu/plab-rundown/credentials/
scp credentials/token.pickle ubuntu@your-server-ip:/home/ubuntu/plab-rundown/credentials/
```

### 6. 启动服务

```bash
# 启动服务
sudo systemctl start plab-rundown

# 查看服务状态
sudo systemctl status plab-rundown

# 查看日志
tail -f /home/ubuntu/plab-rundown/logs/service.log
tail -f /home/ubuntu/plab-rundown/logs/app.log
```

### 7. 服务管理命令

```bash
# 启动服务
sudo systemctl start plab-rundown

# 停止服务
sudo systemctl stop plab-rundown

# 重启服务
sudo systemctl restart plab-rundown

# 查看状态
sudo systemctl status plab-rundown

# 查看日志
journalctl -u plab-rundown -f

# 禁用开机自启
sudo systemctl disable plab-rundown

# 启用开机自启
sudo systemctl enable plab-rundown
```

---

## 方式二: Docker 部署

### 1. 安装 Docker 和 Docker Compose

```bash
# 安装 Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 安装 Docker Compose
sudo apt-get install docker-compose-plugin

# 将当前用户添加到 docker 组
sudo usermod -aG docker $USER
newgrp docker
```

### 2. 准备项目文件

```bash
cd /home/ubuntu/plab-rundown
```

### 3. 配置环境变量

创建 `.env` 文件 (参考上面的配置说明)

### 4. 上传 Gmail 凭证文件

```bash
# 确保凭证文件在 credentials/ 目录下
ls -la credentials/
```

### 5. 构建并启动容器

```bash
# 进入 deploy 目录
cd deploy

# 构建镜像
docker compose build

# 启动容器 (后台运行)
docker compose up -d

# 查看容器状态
docker compose ps

# 查看日志
docker compose logs -f
```

### 6. Docker 管理命令

```bash
# 启动容器
docker compose up -d

# 停止容器
docker compose down

# 重启容器
docker compose restart

# 查看日志
docker compose logs -f plab-rundown

# 进入容器
docker compose exec plab-rundown bash

# 查看容器状态
docker compose ps

# 重新构建镜像
docker compose build --no-cache
```

---

## ⚙️ 配置说明

### 环境变量配置

| 变量名 | 说明 | 必填 | 默认值 |
|--------|------|------|--------|
| `GMAIL_CREDENTIALS_PATH` | Gmail API 凭证文件路径 | ✅ | `credentials/credentials.json` |
| `GMAIL_TOKEN_PATH` | Gmail API Token 文件路径 | ✅ | `credentials/token.pickle` |
| `SENDER_EMAIL` | 邮件发件人地址 | ✅ | `news@daily.therundown.ai` |
| `AI_PROVIDER` | AI 服务商 | ✅ | `openai` |
| `OPENAI_API_KEY` | OpenAI API Key | ✅ | - |
| `OPENAI_MODEL` | OpenAI 模型 | ❌ | `gpt-4o-mini` |
| `WECHAT_APP_ID` | 微信公众号 AppID | ✅ | - |
| `WECHAT_APP_SECRET` | 微信公众号 AppSecret | ✅ | - |
| `APP_ENV` | 应用环境 | ❌ | `development` |
| `SCHEDULE_ENABLED` | 是否启用定时任务 | ❌ | `true` |
| `SCHEDULE_TIME` | 定时任务执行时间 | ❌ | `09:00` |
| `TIMEZONE` | 时区 | ❌ | `Asia/Shanghai` |

### 定时任务配置

编辑 `config/config.yaml`:

```yaml
scheduler:
  enabled: true
  timezone: "Asia/Shanghai"
  
  # Cron 表达式：每天 9:00 执行
  cron:
    hour: 9
    minute: 0
  
  # 重试配置
  retry:
    max_attempts: 3
    delay_seconds: 300  # 5分钟
```

---

## 🔍 健康检查

服务启动后会在 `10000` 端口提供健康检查接口:

```bash
# 检查服务是否正常运行
curl http://localhost:10000/health

# 预期返回:
# {
#   "status": "healthy",
#   "scheduler": "running",
#   "next_run": "2025-11-04 09:00:00"
# }
```

---

## 📊 日志查看

### systemd 服务日志

```bash
# 查看服务日志
tail -f /home/ubuntu/plab-rundown/logs/service.log

# 查看应用日志
tail -f /home/ubuntu/plab-rundown/logs/app.log

# 查看 systemd 日志
journalctl -u plab-rundown -f
```

### Docker 容器日志

```bash
# 查看容器日志
docker compose logs -f plab-rundown

# 查看应用日志
tail -f ../logs/app.log
```

---

## 🐛 常见问题

### 1. 服务启动失败

**问题**: `systemctl status plab-rundown` 显示 `failed`

**解决方案**:
```bash
# 查看详细错误日志
journalctl -u plab-rundown -n 50

# 检查 Python 虚拟环境
source /home/ubuntu/plab-rundown/.venv/bin/activate
python --version

# 检查依赖是否安装完整
pip list
```

### 2. Gmail API 认证失败

**问题**: 日志显示 Gmail 认证错误

**解决方案**:
```bash
# 确保凭证文件存在
ls -la /home/ubuntu/plab-rundown/credentials/

# 检查文件权限
chmod 600 /home/ubuntu/plab-rundown/credentials/*

# 重新生成 token
# 在本地运行一次获取邮件,生成新的 token.pickle
```

### 3. 微信公众号发布失败

**问题**: 日志显示微信 API 调用失败

**解决方案**:
```bash
# 检查环境变量配置
cat /home/ubuntu/plab-rundown/.env | grep WECHAT

# 测试微信 API 连接
curl "https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=YOUR_APP_ID&secret=YOUR_APP_SECRET"
```

### 4. 定时任务未执行

**问题**: 到了设定时间但任务没有执行

**解决方案**:
```bash
# 检查调度器状态
curl http://localhost:10000/health

# 查看调度器日志
tail -f /home/ubuntu/plab-rundown/logs/app.log | grep scheduler

# 检查时区设置
timedatectl
```

---

## 🔄 更新部署

### systemd 服务更新

```bash
cd /home/ubuntu/plab-rundown

# 拉取最新代码
git pull

# 激活虚拟环境
source .venv/bin/activate

# 更新依赖
pip install -r requirements.txt

# 重启服务
sudo systemctl restart plab-rundown
```

### Docker 容器更新

```bash
cd /home/ubuntu/plab-rundown/deploy

# 拉取最新代码
git pull

# 重新构建并启动
docker compose down
docker compose build --no-cache
docker compose up -d
```

---

## 📞 技术支持

如有问题,请查看:
- 项目 README: `/home/ubuntu/plab-rundown/README.md`
- 日志文件: `/home/ubuntu/plab-rundown/logs/`
- GitHub Issues: <你的仓库地址>/issues

---

## 📝 许可证

MIT License

