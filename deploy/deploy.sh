#!/bin/bash
# Plab-Rundown 服务器部署脚本
# 适用于 Ubuntu 20.04+ 系统

set -e  # 遇到错误立即退出

echo "=========================================="
echo "🚀 Plab-Rundown 服务器部署脚本"
echo "=========================================="

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 项目配置
PROJECT_NAME="plab-rundown"
PROJECT_DIR="/home/ubuntu/${PROJECT_NAME}"
VENV_DIR="${PROJECT_DIR}/.venv"
SERVICE_NAME="plab-rundown"

# 检查是否为 root 用户
if [ "$EUID" -eq 0 ]; then 
    echo -e "${RED}❌ 请不要使用 root 用户运行此脚本${NC}"
    echo "使用普通用户运行: bash deploy.sh"
    exit 1
fi

echo -e "${GREEN}✅ 当前用户: $(whoami)${NC}"

# 1. 更新系统并安装依赖
echo ""
echo "=========================================="
echo "📦 步骤 1: 安装系统依赖"
echo "=========================================="

sudo apt-get update
sudo apt-get install -y \
    python3.11 \
    python3.11-venv \
    python3-pip \
    git \
    curl \
    wget \
    build-essential \
    libpq-dev \
    supervisor

echo -e "${GREEN}✅ 系统依赖安装完成${NC}"

# 2. 克隆或更新项目代码
echo ""
echo "=========================================="
echo "📥 步骤 2: 获取项目代码"
echo "=========================================="

if [ -d "$PROJECT_DIR" ]; then
    echo -e "${YELLOW}⚠️  项目目录已存在,拉取最新代码...${NC}"
    cd "$PROJECT_DIR"
    git pull
else
    echo "克隆项目代码..."
    cd /home/ubuntu
    # 替换为你的 Git 仓库地址
    read -p "请输入 Git 仓库地址 (或按回车跳过): " GIT_REPO
    if [ -n "$GIT_REPO" ]; then
        git clone "$GIT_REPO" "$PROJECT_NAME"
        cd "$PROJECT_DIR"
    else
        echo -e "${YELLOW}⚠️  跳过 Git 克隆,请手动上传代码到 ${PROJECT_DIR}${NC}"
        mkdir -p "$PROJECT_DIR"
        cd "$PROJECT_DIR"
    fi
fi

echo -e "${GREEN}✅ 项目代码准备完成${NC}"

# 3. 创建 Python 虚拟环境
echo ""
echo "=========================================="
echo "🐍 步骤 3: 创建 Python 虚拟环境"
echo "=========================================="

if [ ! -d "$VENV_DIR" ]; then
    python3.11 -m venv "$VENV_DIR"
    echo -e "${GREEN}✅ 虚拟环境创建成功${NC}"
else
    echo -e "${YELLOW}⚠️  虚拟环境已存在${NC}"
fi

# 激活虚拟环境
source "$VENV_DIR/bin/activate"

# 升级 pip
pip install --upgrade pip

echo -e "${GREEN}✅ Python 虚拟环境准备完成${NC}"

# 4. 安装 Python 依赖
echo ""
echo "=========================================="
echo "📦 步骤 4: 安装 Python 依赖"
echo "=========================================="

if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    echo -e "${GREEN}✅ Python 依赖安装完成${NC}"
else
    echo -e "${RED}❌ requirements.txt 文件不存在${NC}"
    exit 1
fi

# 5. 创建必要的目录
echo ""
echo "=========================================="
echo "📁 步骤 5: 创建必要的目录"
echo "=========================================="

mkdir -p "$PROJECT_DIR/logs"
mkdir -p "$PROJECT_DIR/data"
mkdir -p "$PROJECT_DIR/data/assets"
mkdir -p "$PROJECT_DIR/credentials"

echo -e "${GREEN}✅ 目录创建完成${NC}"

# 6. 配置环境变量
echo ""
echo "=========================================="
echo "⚙️  步骤 6: 配置环境变量"
echo "=========================================="

if [ ! -f "$PROJECT_DIR/.env" ]; then
    if [ -f "$PROJECT_DIR/.env.example" ]; then
        cp "$PROJECT_DIR/.env.example" "$PROJECT_DIR/.env"
        echo -e "${YELLOW}⚠️  已创建 .env 文件,请编辑配置:${NC}"
        echo "   nano $PROJECT_DIR/.env"
    else
        echo -e "${RED}❌ .env.example 文件不存在${NC}"
    fi
else
    echo -e "${GREEN}✅ .env 文件已存在${NC}"
fi

# 7. 创建 systemd 服务
echo ""
echo "=========================================="
echo "🔧 步骤 7: 创建 systemd 服务"
echo "=========================================="

SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"

sudo tee "$SERVICE_FILE" > /dev/null <<EOF
[Unit]
Description=Plab-Rundown - The Rundown AI 邮件翻译与公众号发布系统
After=network.target

[Service]
Type=simple
User=$(whoami)
WorkingDirectory=${PROJECT_DIR}
Environment="PATH=${VENV_DIR}/bin"
ExecStart=${VENV_DIR}/bin/python -m src.scheduler.main
Restart=always
RestartSec=10
StandardOutput=append:${PROJECT_DIR}/logs/service.log
StandardError=append:${PROJECT_DIR}/logs/service_error.log

[Install]
WantedBy=multi-user.target
EOF

echo -e "${GREEN}✅ systemd 服务文件创建成功${NC}"

# 8. 重载 systemd 并启用服务
echo ""
echo "=========================================="
echo "🚀 步骤 8: 启用并启动服务"
echo "=========================================="

sudo systemctl daemon-reload
sudo systemctl enable "$SERVICE_NAME"

echo -e "${GREEN}✅ 服务已启用(开机自启)${NC}"

# 9. 显示后续操作提示
echo ""
echo "=========================================="
echo "✅ 部署完成!"
echo "=========================================="
echo ""
echo -e "${YELLOW}📝 后续操作:${NC}"
echo ""
echo "1️⃣  配置环境变量:"
echo "   nano $PROJECT_DIR/.env"
echo ""
echo "2️⃣  配置 Gmail 凭证:"
echo "   将 credentials.json 和 token.pickle 上传到:"
echo "   $PROJECT_DIR/credentials/"
echo ""
echo "3️⃣  启动服务:"
echo "   sudo systemctl start $SERVICE_NAME"
echo ""
echo "4️⃣  查看服务状态:"
echo "   sudo systemctl status $SERVICE_NAME"
echo ""
echo "5️⃣  查看日志:"
echo "   tail -f $PROJECT_DIR/logs/service.log"
echo "   tail -f $PROJECT_DIR/logs/app.log"
echo ""
echo "6️⃣  停止服务:"
echo "   sudo systemctl stop $SERVICE_NAME"
echo ""
echo "7️⃣  重启服务:"
echo "   sudo systemctl restart $SERVICE_NAME"
echo ""
echo "=========================================="

