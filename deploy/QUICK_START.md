# 🚀 快速部署指南

## 服务器端操作 (腾讯云)

### 1️⃣ 连接服务器
```bash
ssh ubuntu@your-server-ip
```

### 2️⃣ 一键部署
```bash
# 下载并运行部署脚本
curl -fsSL https://raw.githubusercontent.com/plabzzxx/Plab-Rundown/main/deploy/server-deploy.sh | bash
```

或者手动执行:
```bash
# 克隆项目
git clone https://github.com/plabzzxx/Plab-Rundown.git ~/plab-rundown
cd ~/plab-rundown

# 运行部署脚本
chmod +x deploy/server-deploy.sh
./deploy/server-deploy.sh
```

### 3️⃣ 配置环境变量
```bash
cd ~/plab-rundown
cp .env.production.example .env
nano .env
```

填写必要配置:
- `OPENAI_API_KEY` 或 `GOOGLE_AI_API_KEY`
- `WECHAT_APP_ID` 和 `WECHAT_APP_SECRET`
- 如果使用 Clash 代理,取消注释 `HTTP_PROXY` 和 `HTTPS_PROXY`

---

## 本地端操作

### 4️⃣ 上传凭证文件
```bash
# 在本地电脑运行
scp credentials/credentials.json ubuntu@your-server-ip:~/plab-rundown/credentials/
scp credentials/token.pickle ubuntu@your-server-ip:~/plab-rundown/credentials/
```

---

## 服务器端继续

### 5️⃣ 启动服务
```bash
cd ~/plab-rundown/deploy
docker-compose up -d
```

### 6️⃣ 查看状态
```bash
# 查看容器状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

### 7️⃣ 运行测试
```bash
# 运行测试脚本
chmod +x test-server.sh
./test-server.sh

# 或手动测试
docker exec plab-rundown python test_workflow.py
```

### 8️⃣ 获取服务器 IP (配置微信白名单)
```bash
curl ifconfig.me
```

将获取到的 IP 添加到微信公众号后台的 IP 白名单。

---

## 常用命令

### 查看日志
```bash
cd ~/plab-rundown/deploy
docker-compose logs -f
```

### 重启服务
```bash
docker-compose restart
```

### 停止服务
```bash
docker-compose down
```

### 更新代码
```bash
cd ~/plab-rundown
git pull
cd deploy
docker-compose down
docker-compose build
docker-compose up -d
```

### 进入容器
```bash
docker exec -it plab-rundown bash
```

---

## 代理配置 (可选)

### 如果使用 Clash

1. 检查 Clash 状态
```bash
sudo systemctl status clash
```

2. 启动 Clash
```bash
sudo systemctl start clash
sudo systemctl enable clash
```

3. 测试代理
```bash
curl -x http://127.0.0.1:7890 https://www.google.com
```

4. 在 .env 中配置代理
```bash
HTTP_PROXY=http://host.docker.internal:7890
HTTPS_PROXY=http://host.docker.internal:7890
```

### 如果 OpenAI 有问题

切换到 Google AI:
```bash
nano ~/plab-rundown/.env

# 修改
AI_PROVIDER=google_ai
GOOGLE_AI_API_KEY=your-key-here
GOOGLE_AI_MODEL=gemini-1.5-flash

# 重启
cd ~/plab-rundown/deploy
docker-compose restart
```

---

## 验证部署

### ✅ 检查清单

- [ ] 容器正在运行: `docker-compose ps`
- [ ] 健康检查通过: `curl http://localhost:10000/health`
- [ ] 日志无错误: `docker-compose logs`
- [ ] 测试工作流成功: `docker exec plab-rundown python test_workflow.py`
- [ ] 服务器 IP 已添加到微信白名单
- [ ] 定时任务已设置为早上 6:00

---

## 下一步

等待明天早上 6:00,检查:
1. 微信公众号草稿箱是否有新文章
2. 查看日志确认执行情况: `docker-compose logs | grep "工作流"`

---

## 需要帮助?

- 📖 详细文档: [TENCENT_CLOUD_DEPLOY.md](./TENCENT_CLOUD_DEPLOY.md)
- 🐛 问题反馈: [GitHub Issues](https://github.com/plabzzxx/Plab-Rundown/issues)

