# 📚 部署文件索引

本目录包含 Plab-Rundown 项目的所有部署相关文件和脚本。

---

## 📁 文件结构

```
deploy/
├── INDEX.md              # 本文件 - 部署文件索引
├── README.md             # 详细部署文档
├── SERVER_SETUP.md       # 服务器快速设置指南
├── deploy.sh             # 一键部署脚本
├── Dockerfile            # Docker 镜像配置
├── docker-compose.yml    # Docker Compose 配置
└── scripts/              # 管理脚本目录
    ├── check_status.sh   # 服务状态检查脚本
    ├── manual_run.sh     # 手动运行工作流脚本
    └── backup.sh         # 数据备份脚本
```

---

## 📖 文档说明

### 1. [README.md](README.md) - 详细部署文档

**适用场景:** 需要了解完整部署流程和配置细节

**内容包括:**
- ✅ systemd 服务部署完整指南
- ✅ Docker 容器部署完整指南
- ✅ 环境变量详细说明
- ✅ 定时任务配置
- ✅ 健康检查说明
- ✅ 日志查看方法
- ✅ 常见问题排查
- ✅ 更新部署流程

**推荐阅读:** ⭐⭐⭐⭐⭐

---

### 2. [SERVER_SETUP.md](SERVER_SETUP.md) - 服务器快速设置指南

**适用场景:** 已连接到服务器，需要快速部署

**内容包括:**
- ✅ 3 步快速部署流程
- ✅ 服务器端操作命令
- ✅ 配置文件编辑指南
- ✅ 服务管理命令
- ✅ 故障排查步骤
- ✅ 常用管理命令

**推荐阅读:** ⭐⭐⭐⭐⭐

---

### 3. [../DEPLOYMENT.md](../DEPLOYMENT.md) - 快速部署指南

**适用场景:** 5分钟快速部署

**内容包括:**
- ✅ 服务器要求
- ✅ 快速开始步骤
- ✅ Docker 快速部署
- ✅ 配置说明
- ✅ 健康检查
- ✅ 日志查看
- ✅ 故障排查
- ✅ 更新部署

**推荐阅读:** ⭐⭐⭐⭐

---

## 🔧 脚本说明

### 1. [deploy.sh](deploy.sh) - 一键部署脚本

**功能:** 自动完成服务器环境配置和服务安装

**执行步骤:**
1. 安装系统依赖 (Python 3.11, pip, git 等)
2. 创建 Python 虚拟环境
3. 安装 Python 依赖包
4. 创建必要的目录
5. 创建 systemd 服务
6. 配置开机自启

**使用方法:**
```bash
chmod +x deploy/deploy.sh
bash deploy/deploy.sh
```

**预计耗时:** 3-5 分钟

**适用系统:** Ubuntu 20.04+

---

### 2. [scripts/check_status.sh](scripts/check_status.sh) - 服务状态检查

**功能:** 全面检查服务运行状态

**检查项目:**
- ✅ systemd 服务状态
- ✅ 健康检查接口
- ✅ Python 进程状态
- ✅ 最近日志输出
- ✅ 磁盘空间使用
- ✅ 内存使用情况

**使用方法:**
```bash
chmod +x deploy/scripts/check_status.sh
bash deploy/scripts/check_status.sh
```

**输出示例:**
```
==========================================
🔍 Plab-Rundown 服务状态检查
==========================================

1️⃣  systemd 服务状态:
✅ 服务正在运行

2️⃣  健康检查接口:
✅ 健康检查接口正常
{
  "status": "healthy",
  "scheduler": "running"
}

...
```

---

### 3. [scripts/manual_run.sh](scripts/manual_run.sh) - 手动运行工作流

**功能:** 立即执行一次完整的工作流 (用于测试)

**执行流程:**
1. 📧 获取最新 Gmail 邮件
2. 🤖 AI 翻译成中文
3. 📱 发布到微信公众号草稿箱

**使用方法:**
```bash
chmod +x deploy/scripts/manual_run.sh
bash deploy/scripts/manual_run.sh
```

**适用场景:**
- 测试配置是否正确
- 验证服务是否正常
- 手动触发一次任务

---

### 4. [scripts/backup.sh](scripts/backup.sh) - 数据备份

**功能:** 备份重要数据和配置文件

**备份内容:**
- ✅ 环境变量 (.env)
- ✅ 配置文件 (config/)
- ✅ Gmail 凭证 (credentials/)
- ✅ 数据库文件
- ✅ 最近 7 天的日志

**使用方法:**
```bash
chmod +x deploy/scripts/backup.sh
bash deploy/scripts/backup.sh
```

**备份位置:** `/home/ubuntu/backups/`

**备份格式:** `plab-rundown-backup-YYYYMMDD_HHMMSS.tar.gz`

**自动清理:** 保留最近 7 个备份

---

## 🐳 Docker 文件说明

### 1. [Dockerfile](Dockerfile) - Docker 镜像配置

**基础镜像:** `python:3.11-slim`

**包含内容:**
- Python 3.11 运行环境
- 所有项目依赖
- 必要的系统工具

**构建命令:**
```bash
docker build -f deploy/Dockerfile -t plab-rundown .
```

---

### 2. [docker-compose.yml](docker-compose.yml) - Docker Compose 配置

**服务配置:**
- 容器名称: `plab-rundown`
- 端口映射: `10000:10000`
- 自动重启: `unless-stopped`
- 健康检查: 每 30 秒检查一次

**数据卷挂载:**
- `logs/` - 日志目录
- `data/` - 数据目录
- `credentials/` - 凭证目录
- `config/` - 配置目录

**使用命令:**
```bash
# 启动
docker compose up -d

# 停止
docker compose down

# 查看日志
docker compose logs -f
```

---

## 🚀 快速开始指南

### 新手推荐流程

1. **阅读文档** (5 分钟)
   - 先看 [../DEPLOYMENT.md](../DEPLOYMENT.md) 了解整体流程
   - 再看 [SERVER_SETUP.md](SERVER_SETUP.md) 了解具体操作

2. **准备环境** (2 分钟)
   - 连接到服务器
   - 上传项目代码

3. **运行部署** (3 分钟)
   - 执行 `deploy.sh` 一键部署
   - 配置 `.env` 环境变量
   - 上传 Gmail 凭证文件

4. **启动服务** (1 分钟)
   - 启动 systemd 服务
   - 检查服务状态

5. **验证部署** (2 分钟)
   - 运行 `check_status.sh` 检查状态
   - 运行 `manual_run.sh` 测试工作流

**总耗时:** 约 15 分钟

---

## 📋 部署检查清单

使用以下清单确保部署完整:

### 部署前检查

- [ ] 服务器满足最低要求 (Ubuntu 20.04+, 1GB RAM, 2GB 磁盘)
- [ ] 已准备好 Gmail API 凭证文件
- [ ] 已准备好 OpenAI API Key
- [ ] 已准备好微信公众号 AppID 和 AppSecret
- [ ] 已了解基本的 Linux 命令

### 部署中检查

- [ ] `deploy.sh` 脚本执行成功
- [ ] Python 虚拟环境创建成功
- [ ] 所有依赖安装完成
- [ ] `.env` 文件配置正确
- [ ] Gmail 凭证文件已上传
- [ ] systemd 服务创建成功

### 部署后检查

- [ ] 服务状态为 `active (running)`
- [ ] 健康检查接口返回正常
- [ ] 日志输出正常
- [ ] 手动运行测试成功
- [ ] 定时任务配置正确
- [ ] 已设置数据备份计划

---

## 🔍 故障排查流程

### 1. 服务无法启动

```bash
# 步骤 1: 查看服务状态
sudo systemctl status plab-rundown

# 步骤 2: 查看详细日志
journalctl -u plab-rundown -n 50

# 步骤 3: 检查配置文件
cat ~/.env
cat ~/plab-rundown/config/config.yaml

# 步骤 4: 检查 Python 环境
source ~/plab-rundown/.venv/bin/activate
python --version
pip list
```

### 2. 工作流执行失败

```bash
# 步骤 1: 手动运行测试
bash ~/plab-rundown/deploy/scripts/manual_run.sh

# 步骤 2: 查看应用日志
tail -f ~/plab-rundown/logs/app.log

# 步骤 3: 检查 API 凭证
ls -la ~/plab-rundown/credentials/
cat ~/.env | grep -E "OPENAI|WECHAT|GMAIL"
```

### 3. 定时任务未执行

```bash
# 步骤 1: 检查调度器状态
curl http://localhost:10000/health

# 步骤 2: 查看调度器日志
tail -f ~/plab-rundown/logs/app.log | grep scheduler

# 步骤 3: 检查时区设置
timedatectl
cat ~/plab-rundown/config/config.yaml | grep -A 5 scheduler
```

---

## 📞 获取帮助

### 文档资源

- 📘 [快速部署指南](../DEPLOYMENT.md)
- 📗 [服务器设置指南](SERVER_SETUP.md)
- 📙 [详细部署文档](README.md)
- 📕 [项目主 README](../README.md)

### 在线资源

- 🐛 GitHub Issues: 提交问题和 Bug
- 📧 项目作者: 见项目信息
- 📖 官方文档: 见项目仓库

### 日志位置

- 应用日志: `~/plab-rundown/logs/app.log`
- 服务日志: `journalctl -u plab-rundown`
- Docker 日志: `docker compose logs`

---

## 🎯 下一步

部署完成后，你可以:

1. **配置定时任务** - 编辑 `config/config.yaml` 设置执行时间
2. **设置数据备份** - 使用 `backup.sh` 定期备份数据
3. **监控服务状态** - 使用 `check_status.sh` 定期检查
4. **查看运行日志** - 使用 `tail -f logs/app.log` 监控运行
5. **优化配置** - 根据实际情况调整 AI 模型和参数

---

**祝你部署顺利! 🚀**

