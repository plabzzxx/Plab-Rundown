# 腾讯云服务器 Docker 部署指南

## 前置准备

### 1. 服务器要求
- 操作系统: Ubuntu 20.04+ / Debian 11+
- 内存: 至少 1GB
- 磁盘: 至少 10GB
- 已安装 Clash 代理 (如果需要访问 OpenAI)

### 2. 本地准备
确保你有以下文件:
- `credentials/credentials.json` - Gmail API 凭证
- `credentials/token.pickle` - Gmail 访问令牌
- `.env` - 环境变量配置

---

## 快速部署

### 步骤 1: 连接到服务器

```bash
ssh ubuntu@your-server-ip
```

### 步骤 2: 运行一键部署脚本

```bash
# 下载部署脚本
curl -O https://raw.githubusercontent.com/plabzzxx/Plab-Rundown/main/deploy/server-deploy.sh

# 添加执行权限
chmod +x server-deploy.sh

# 运行部署脚本
./server-deploy.sh
```

脚本会自动完成:
- ✅ 安装 Docker 和 Docker Compose
- ✅ 克隆项目代码
- ✅ 创建配置文件
- ✅ 检查代理配置
- ✅ 构建并启动容器

### 步骤 3: 配置环境变量

```bash
cd ~/plab-rundown
nano .env
```

必填配置项:
```bash
# Gmail API 配置
GMAIL_CREDENTIALS_PATH=credentials/credentials.json
GMAIL_TOKEN_PATH=credentials/token.pickle
SENDER_EMAIL=news@daily.therundown.ai

# AI 服务商配置
AI_PROVIDER=openai  # 或 google_ai
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4o-mini

# 微信公众号配置
WECHAT_APP_ID=your_app_id
WECHAT_APP_SECRET=your_app_secret

# 代理配置 (如果使用 Clash)
HTTP_PROXY=http://host.docker.internal:7890
HTTPS_PROXY=http://host.docker.internal:7890

# 应用配置
APP_ENV=production
SCHEDULE_ENABLED=true
SCHEDULE_TIME=06:00
TIMEZONE=Asia/Shanghai
```

### 步骤 4: 上传凭证文件

在**本地电脑**上运行:

```bash
# 上传 Gmail 凭证
scp credentials/credentials.json ubuntu@your-server-ip:~/plab-rundown/credentials/
scp credentials/token.pickle ubuntu@your-server-ip:~/plab-rundown/credentials/
```

### 步骤 5: 重启容器

```bash
cd ~/plab-rundown/deploy
docker-compose restart
```

---

## 代理配置

### 检查 Clash 状态

```bash
# 检查 Clash 服务
sudo systemctl status clash

# 启动 Clash
sudo systemctl start clash

# 设置开机自启
sudo systemctl enable clash
```

### 测试代理连接

```bash
# 测试 HTTP 代理 (Google)
curl -x http://127.0.0.1:7890 https://www.google.com

# 测试 HTTPS 代理 (OpenAI)
curl -x http://127.0.0.1:7890 https://api.openai.com
```

### 代理问题排查

如果 OpenAI SSL 有问题,可以:

**方案 1: 使用 Google AI (推荐)**
```bash
# 修改 .env
AI_PROVIDER=google_ai
GOOGLE_AI_API_KEY=your-google-ai-key
GOOGLE_AI_MODEL=gemini-1.5-flash
```

**方案 2: 修改 Clash 配置**
```yaml
# 在 Clash 配置中添加
tls:
  skip-cert-verify: false
```

**方案 3: 使用国内中转 API**
```bash
OPENAI_BASE_URL=https://your-proxy-url/v1
```

---

## 容器管理

### 查看容器状态
```bash
cd ~/plab-rundown/deploy
docker-compose ps
```

### 查看日志
```bash
# 实时查看日志
docker-compose logs -f

# 查看最近 100 行
docker-compose logs --tail=100

# 只看错误日志
docker-compose logs | grep ERROR
```

### 重启容器
```bash
docker-compose restart
```

### 停止容器
```bash
docker-compose down
```

### 重新构建并启动
```bash
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### 进入容器
```bash
docker exec -it plab-rundown bash
```

---

## 测试运行

### 运行测试脚本

```bash
cd ~/plab-rundown/deploy
chmod +x test-server.sh
./test-server.sh
```

### 手动运行工作流

```bash
# 在容器内运行
docker exec plab-rundown python test_workflow.py

# 查看输出
docker-compose logs -f
```

---

## 获取服务器 IP (配置微信白名单)

```bash
# 获取公网 IP
curl ifconfig.me

# 或
curl ip.sb
```

将获取到的 IP 添加到微信公众号后台的 IP 白名单中。

---

## 定时任务

容器会自动运行定时任务,每天北京时间 **早上 6:00** 执行。

查看下次执行时间:
```bash
docker-compose logs | grep "下次执行"
```

---

## 监控和维护

### 健康检查

```bash
# 检查健康状态
curl http://localhost:10000/health

# 应该返回: {"status": "ok"}
```

### 磁盘空间

```bash
# 查看磁盘使用
df -h

# 清理 Docker 缓存
docker system prune -a
```

### 日志管理

日志文件位于 `~/plab-rundown/logs/app.log`

```bash
# 查看日志大小
du -h ~/plab-rundown/logs/

# 清理旧日志
rm ~/plab-rundown/logs/*.log.1
```

---

## 故障排查

### 容器无法启动

1. 检查日志
```bash
docker-compose logs
```

2. 检查配置文件
```bash
cat ~/plab-rundown/.env
```

3. 检查凭证文件
```bash
ls -la ~/plab-rundown/credentials/
```

### 代理连接失败

1. 检查 Clash 状态
```bash
sudo systemctl status clash
```

2. 测试代理
```bash
curl -x http://127.0.0.1:7890 https://www.google.com
```

3. 切换到 Google AI
```bash
nano ~/plab-rundown/.env
# 修改 AI_PROVIDER=google_ai
docker-compose restart
```

### 微信发布失败

1. 检查 IP 白名单
```bash
curl ifconfig.me
```

2. 检查 AppID 和 AppSecret
```bash
grep WECHAT ~/plab-rundown/.env
```

3. 查看详细错误
```bash
docker-compose logs | grep -A 10 "微信"
```

---

## 更新项目

```bash
cd ~/plab-rundown
git pull
cd deploy
docker-compose down
docker-compose build
docker-compose up -d
```

---

## 卸载

```bash
# 停止并删除容器
cd ~/plab-rundown/deploy
docker-compose down

# 删除项目目录
rm -rf ~/plab-rundown

# 可选: 卸载 Docker
sudo apt-get remove docker docker-engine docker.io containerd runc
```

---

## 常见问题

### Q: 如何修改定时任务时间?

A: 编辑 `config/config.yaml`:
```yaml
scheduler:
  cron:
    hour: 6  # 修改为你想要的小时
    minute: 0
```
然后重启容器: `docker-compose restart`

### Q: 如何查看明天是否会执行?

A: 查看日志中的调度信息:
```bash
docker-compose logs | grep "下次执行"
```

### Q: 容器占用太多内存怎么办?

A: 限制容器内存:
```yaml
# 在 docker-compose.yml 中添加
services:
  plab-rundown:
    mem_limit: 512m
```

---

## 技术支持

- 📖 查看完整文档: [README.md](../README.md)
- 🐛 提交问题: [GitHub Issues](https://github.com/plabzzxx/Plab-Rundown/issues)

