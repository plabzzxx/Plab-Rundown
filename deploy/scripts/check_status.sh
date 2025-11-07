#!/bin/bash
# 检查 Plab-Rundown 服务状态

echo "=========================================="
echo "🔍 Plab-Rundown 服务状态检查"
echo "=========================================="
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 1. 检查 systemd 服务状态
echo "1️⃣  systemd 服务状态:"
echo "----------------------------------------"
if systemctl is-active --quiet plab-rundown; then
    echo -e "${GREEN}✅ 服务正在运行${NC}"
    systemctl status plab-rundown --no-pager | head -n 10
else
    echo -e "${RED}❌ 服务未运行${NC}"
    systemctl status plab-rundown --no-pager | head -n 10
fi
echo ""

# 2. 检查健康检查接口
echo "2️⃣  健康检查接口:"
echo "----------------------------------------"
if curl -s http://localhost:10000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ 健康检查接口正常${NC}"
    curl -s http://localhost:10000/health | python3 -m json.tool
else
    echo -e "${RED}❌ 健康检查接口无响应${NC}"
fi
echo ""

# 3. 检查进程
echo "3️⃣  进程状态:"
echo "----------------------------------------"
if pgrep -f "src.scheduler.main" > /dev/null; then
    echo -e "${GREEN}✅ Python 进程正在运行${NC}"
    ps aux | grep "src.scheduler.main" | grep -v grep
else
    echo -e "${RED}❌ Python 进程未运行${NC}"
fi
echo ""

# 4. 检查日志
echo "4️⃣  最近日志 (最后 10 行):"
echo "----------------------------------------"
if [ -f "/home/ubuntu/plab-rundown/logs/app.log" ]; then
    tail -n 10 /home/ubuntu/plab-rundown/logs/app.log
else
    echo -e "${YELLOW}⚠️  日志文件不存在${NC}"
fi
echo ""

# 5. 检查磁盘空间
echo "5️⃣  磁盘空间:"
echo "----------------------------------------"
df -h /home/ubuntu/plab-rundown
echo ""

# 6. 检查内存使用
echo "6️⃣  内存使用:"
echo "----------------------------------------"
free -h
echo ""

echo "=========================================="
echo "✅ 状态检查完成"
echo "=========================================="

