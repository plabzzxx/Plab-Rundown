# 🖥️ 服务器端快速设置指南

你已经连接到服务器了!按照以下步骤快速部署 Plab-Rundown。

---

## 📍 当前位置

```bash
pwd
# 输出: /home/ubuntu
```

---

## 🚀 快速部署 (3 步完成)

### 第 1 步: 获取项目代码

**选项 A: 从 Git 克隆 (推荐)**

```bash
# 克隆项目
git clone https://github.com/your-username/Plab-Rundown.git plab-rundown

# 进入项目目录
cd plab-rundown
```

**选项 B: 从本地上传**

如果你已经在本地准备好了代码,在**本地终端**执行:

```bash
# 上传整个项目
scp -r /path/to/Plab-Rundown ubuntu@your-server-ip:~/plab-rundown
```

然后在服务器上:

```bash
cd ~/plab-rundown
```

---

### 第 2 步: 运行一键部署脚本

```bash
# 给脚本添加执行权限
chmod +x deploy/deploy.sh

# 运行部署脚本
bash deploy/deploy.sh
```

脚本会自动:
- ✅ 安装 Python 3.11 和系统依赖
- ✅ 创建 Python 虚拟环境
- ✅ 安装所有 Python 依赖包
- ✅ 创建必要的目录
- ✅ 创建 systemd 服务
- ✅ 配置开机自启

**预计耗时: 3-5 分钟**

---

### 第 3 步: 配置环境变量和凭证

#### 3.1 配置环境变量

```bash
# 复制示例配置
cp .env.example .env

# 编辑配置文件
nano .env
```

**必填配置项:**

```bash
# Gmail API 配置
GMAIL_CREDENTIALS_PATH=credentials/credentials.json
GMAIL_TOKEN_PATH=credentials/token.pickle
SENDER_EMAIL=news@daily.therundown.ai

# OpenAI 配置
AI_PROVIDER=openai
OPENAI_API_KEY=sk-your-openai-api-key-here  # ⚠️ 必填
OPENAI_MODEL=gpt-4o-mini

# 微信公众号配置
WECHAT_APP_ID=your_wechat_app_id            # ⚠️ 必填
WECHAT_APP_SECRET=your_wechat_app_secret    # ⚠️ 必填

# 应用配置
APP_ENV=production
SCHEDULE_ENABLED=true
SCHEDULE_TIME=09:00
TIMEZONE=Asia/Shanghai
```

保存并退出: `Ctrl+X` → `Y` → `Enter`

#### 3.2 上传 Gmail 凭证文件

在**本地终端**执行:

```bash
# 上传 credentials.json
scp credentials/credentials.json ubuntu@your-server-ip:~/plab-rundown/credentials/

# 上传 token.pickle
scp credentials/token.pickle ubuntu@your-server-ip:~/plab-rundown/credentials/
```

回到服务器,验证文件已上传:

```bash
ls -la ~/plab-rundown/credentials/
```

应该看到:
```
-rw------- 1 ubuntu ubuntu  xxxx credentials.json
-rw------- 1 ubuntu ubuntu  xxxx token.pickle
```

---

## ✅ 启动服务

### 启动 Plab-Rundown 服务

```bash
# 启动服务
sudo systemctl start plab-rundown

# 查看服务状态
sudo systemctl status plab-rundown
```

如果看到 `Active: active (running)` 和绿色的 `●`,说明服务启动成功! 🎉

---

## 🔍 验证部署

### 1. 检查健康状态

```bash
curl http://localhost:10000/health
```

预期输出:
```json
{
  "status": "healthy",
  "scheduler": "running",
  "next_run": "2025-11-04 09:00:00",
  "timezone": "Asia/Shanghai"
}
```

### 2. 查看日志

```bash
# 查看应用日志
tail -f ~/plab-rundown/logs/app.log

# 查看服务日志
journalctl -u plab-rundown -f
```

按 `Ctrl+C` 退出日志查看

### 3. 使用状态检查脚本

```bash
chmod +x ~/plab-rundown/deploy/scripts/check_status.sh
bash ~/plab-rundown/deploy/scripts/check_status.sh
```

---

## 🧪 测试运行

手动运行一次工作流,测试是否正常:

```bash
chmod +x ~/plab-rundown/deploy/scripts/manual_run.sh
bash ~/plab-rundown/deploy/scripts/manual_run.sh
```

这会立即执行一次完整的工作流:
1. 📧 获取最新邮件
2. 🤖 AI 翻译
3. 📱 发布到微信公众号

---

## 📊 常用管理命令

### 服务管理

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
```

### 日志查看

```bash
# 实时查看应用日志
tail -f ~/plab-rundown/logs/app.log

# 查看最近 100 行
tail -n 100 ~/plab-rundown/logs/app.log

# 搜索错误
grep ERROR ~/plab-rundown/logs/app.log
```

### 手动运行

```bash
# 手动执行一次工作流
bash ~/plab-rundown/deploy/scripts/manual_run.sh

# 检查服务状态
bash ~/plab-rundown/deploy/scripts/check_status.sh

# 备份数据
bash ~/plab-rundown/deploy/scripts/backup.sh
```

---

## 🔧 配置定时任务

编辑配置文件:

```bash
nano ~/plab-rundown/config/config.yaml
```

修改定时任务设置:

```yaml
scheduler:
  enabled: true
  timezone: "Asia/Shanghai"
  
  # 每天 9:00 执行
  cron:
    hour: 9      # 修改这里改变执行时间
    minute: 0
```

保存后重启服务:

```bash
sudo systemctl restart plab-rundown
```

---

## 🐛 故障排查

### 服务启动失败

```bash
# 查看详细错误
journalctl -u plab-rundown -n 50

# 检查配置文件
cat ~/plab-rundown/.env

# 检查 Python 环境
source ~/plab-rundown/.venv/bin/activate
python --version
pip list
```

### Gmail 认证失败

```bash
# 检查凭证文件
ls -la ~/plab-rundown/credentials/

# 检查文件权限
chmod 600 ~/plab-rundown/credentials/*
```

### 查看完整日志

```bash
# 查看所有日志
cat ~/plab-rundown/logs/app.log

# 查看错误日志
grep -i error ~/plab-rundown/logs/app.log

# 查看最近的错误
tail -n 100 ~/plab-rundown/logs/app.log | grep -i error
```

---

## 🔄 更新部署

当代码有更新时:

```bash
cd ~/plab-rundown

# 拉取最新代码
git pull

# 激活虚拟环境
source .venv/bin/activate

# 更新依赖
pip install -r requirements.txt

# 重启服务
sudo systemctl restart plab-rundown

# 查看状态
sudo systemctl status plab-rundown
```

---

## 💾 数据备份

定期备份重要数据:

```bash
# 运行备份脚本
bash ~/plab-rundown/deploy/scripts/backup.sh

# 查看备份文件
ls -lh ~/backups/
```

备份包含:
- ✅ 环境变量 (.env)
- ✅ 配置文件 (config/)
- ✅ Gmail 凭证 (credentials/)
- ✅ 数据库文件
- ✅ 最近 7 天的日志

---

## 🔐 安全建议

### 1. 配置防火墙

```bash
# 安装 ufw
sudo apt-get install ufw

# 允许 SSH
sudo ufw allow 22

# 启用防火墙
sudo ufw enable

# 查看状态
sudo ufw status
```

### 2. 保护敏感文件

```bash
# 设置正确的文件权限
chmod 600 ~/plab-rundown/.env
chmod 600 ~/plab-rundown/credentials/*
```

### 3. 定期更新系统

```bash
# 更新系统包
sudo apt-get update
sudo apt-get upgrade -y
```

---

## 📋 部署检查清单

完成部署后,确认以下项目:

- [ ] ✅ 服务正在运行 (`systemctl status plab-rundown`)
- [ ] ✅ 健康检查正常 (`curl http://localhost:10000/health`)
- [ ] ✅ 环境变量已配置 (`.env` 文件)
- [ ] ✅ Gmail 凭证已上传 (`credentials/` 目录)
- [ ] ✅ 定时任务已配置 (`config/config.yaml`)
- [ ] ✅ 日志输出正常 (`tail -f logs/app.log`)
- [ ] ✅ 手动测试成功 (`manual_run.sh`)

---

## 🎉 部署完成!

恭喜!Plab-Rundown 已成功部署到服务器。

### 接下来会发生什么?

系统会在每天设定的时间 (默认 09:00) 自动执行:

1. 📧 从 Gmail 获取 The Rundown AI 最新邮件
2. 🤖 使用 OpenAI 将内容翻译成中文
3. 📱 自动发布到微信公众号草稿箱

### 需要帮助?

- 📖 查看详细文档: `~/plab-rundown/deploy/README.md`
- 📝 查看部署指南: `~/plab-rundown/DEPLOYMENT.md`
- 🔍 检查服务状态: `bash ~/plab-rundown/deploy/scripts/check_status.sh`
- 📊 查看日志: `tail -f ~/plab-rundown/logs/app.log`

---

**祝你使用愉快! 🚀**

