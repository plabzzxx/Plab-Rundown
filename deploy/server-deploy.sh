#!/bin/bash
# Plab-Rundown 服务器部署脚本 (Docker版本)
# 适用于腾讯云服务器

set -e

echo "========================================"
echo "  Plab-Rundown Docker 部署脚本"
echo "========================================"
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 项目目录
PROJECT_DIR="$HOME/plab-rundown"

# 检查是否为root用户
if [ "$EUID" -eq 0 ]; then 
    echo -e "${RED}请不要使用root用户运行此脚本${NC}"
    exit 1
fi

echo "步骤 1/6: 检查系统环境"
echo "----------------------------------------"

# 检查操作系统
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$NAME
    VER=$VERSION_ID
    echo "操作系统: $OS $VER"
else
    echo -e "${RED}无法识别操作系统${NC}"
    exit 1
fi

echo ""
echo "步骤 2/6: 安装 Docker 和 Docker Compose"
echo "----------------------------------------"

# 检查 Docker 是否已安装
if ! command -v docker &> /dev/null; then
    echo "Docker 未安装，正在安装..."
    
    # 安装 Docker
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    
    # 将当前用户添加到 docker 组
    sudo usermod -aG docker $USER
    
    echo -e "${GREEN}Docker 安装成功${NC}"
    echo -e "${YELLOW}注意: 需要重新登录才能使用 docker 命令${NC}"
else
    echo -e "${GREEN}Docker 已安装: $(docker --version)${NC}"
fi

# 检查 Docker Compose 是否已安装
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "Docker Compose 未安装，正在安装..."
    
    # 安装 Docker Compose
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    
    echo -e "${GREEN}Docker Compose 安装成功${NC}"
else
    echo -e "${GREEN}Docker Compose 已安装${NC}"
fi

echo ""
echo "步骤 3/6: 克隆/更新项目代码"
echo "----------------------------------------"

if [ -d "$PROJECT_DIR" ]; then
    echo "项目目录已存在，正在更新..."
    cd "$PROJECT_DIR"
    git pull
else
    echo "正在克隆项目..."
    git clone https://github.com/plabzzxx/Plab-Rundown.git "$PROJECT_DIR"
    cd "$PROJECT_DIR"
fi

echo -e "${GREEN}代码更新成功${NC}"

echo ""
echo "步骤 4/6: 配置环境变量"
echo "----------------------------------------"

if [ ! -f "$PROJECT_DIR/.env" ]; then
    echo "创建 .env 文件..."
    cp .env.example .env
    echo -e "${YELLOW}请编辑 .env 文件并填写配置信息${NC}"
    echo "运行: nano $PROJECT_DIR/.env"
    read -p "按回车键继续..."
else
    echo -e "${GREEN}.env 文件已存在${NC}"
fi

echo ""
echo "步骤 5/6: 检查代理配置"
echo "----------------------------------------"

# 检查 Clash 是否运行
if systemctl is-active --quiet clash 2>/dev/null; then
    echo -e "${GREEN}Clash 服务正在运行${NC}"
    
    # 测试代理
    echo "测试代理连接..."
    
    # 测试 HTTP 代理 (Google)
    if curl -x http://127.0.0.1:7890 -s --max-time 5 https://www.google.com > /dev/null 2>&1; then
        echo -e "${GREEN}✓ HTTP 代理正常 (Google 可访问)${NC}"
    else
        echo -e "${RED}✗ HTTP 代理失败 (Google 不可访问)${NC}"
    fi
    
    # 测试 HTTPS 代理 (OpenAI)
    if curl -x http://127.0.0.1:7890 -s --max-time 5 https://api.openai.com > /dev/null 2>&1; then
        echo -e "${GREEN}✓ HTTPS 代理正常 (OpenAI 可访问)${NC}"
    else
        echo -e "${YELLOW}⚠ HTTPS 代理可能有问题 (OpenAI 不可访问)${NC}"
        echo "  可能需要检查 Clash 配置或使用其他 AI 服务商"
    fi
else
    echo -e "${YELLOW}Clash 服务未运行${NC}"
    echo "如果需要使用代理访问 OpenAI，请先启动 Clash"
    echo "运行: sudo systemctl start clash"
fi

echo ""
echo "步骤 6/6: 构建并启动 Docker 容器"
echo "----------------------------------------"

cd "$PROJECT_DIR/deploy"

# 停止旧容器
if docker ps -a | grep -q plab-rundown; then
    echo "停止旧容器..."
    docker-compose down
fi

# 构建镜像
echo "构建 Docker 镜像..."
docker-compose build

# 启动容器
echo "启动容器..."
docker-compose up -d

echo ""
echo "========================================"
echo -e "${GREEN}部署完成!${NC}"
echo "========================================"
echo ""
echo "查看容器状态:"
echo "  docker-compose ps"
echo ""
echo "查看日志:"
echo "  docker-compose logs -f"
echo ""
echo "停止服务:"
echo "  docker-compose down"
echo ""
echo "重启服务:"
echo "  docker-compose restart"
echo ""
echo "进入容器:"
echo "  docker exec -it plab-rundown bash"
echo ""
echo "手动运行测试:"
echo "  docker exec plab-rundown python test_workflow.py"
echo ""
echo "========================================"

