#!/bin/bash
# 服务器测试脚本

set -e

echo "========================================"
echo "  Plab-Rundown 服务器测试"
echo "========================================"
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "1. 检查容器状态"
echo "----------------------------------------"
docker-compose ps

echo ""
echo "2. 检查容器健康状态"
echo "----------------------------------------"
if docker ps --filter "name=plab-rundown" --filter "health=healthy" | grep -q plab-rundown; then
    echo -e "${GREEN}✓ 容器健康状态正常${NC}"
else
    echo -e "${YELLOW}⚠ 容器可能未完全启动或不健康${NC}"
fi

echo ""
echo "3. 测试健康检查端点"
echo "----------------------------------------"
if curl -s http://localhost:10000/health | grep -q "ok"; then
    echo -e "${GREEN}✓ 健康检查端点正常${NC}"
else
    echo -e "${RED}✗ 健康检查端点失败${NC}"
fi

echo ""
echo "4. 查看最近的日志"
echo "----------------------------------------"
docker-compose logs --tail=50

echo ""
echo "5. 检查代理配置"
echo "----------------------------------------"
echo "测试容器内的代理连接..."

# 测试 Google (HTTP)
if docker exec plab-rundown curl -x http://host.docker.internal:7890 -s --max-time 5 https://www.google.com > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Google 可访问 (HTTP 代理正常)${NC}"
else
    echo -e "${RED}✗ Google 不可访问 (HTTP 代理可能有问题)${NC}"
fi

# 测试 OpenAI (HTTPS)
if docker exec plab-rundown curl -x http://host.docker.internal:7890 -s --max-time 5 https://api.openai.com > /dev/null 2>&1; then
    echo -e "${GREEN}✓ OpenAI 可访问 (HTTPS 代理正常)${NC}"
else
    echo -e "${YELLOW}⚠ OpenAI 不可访问 (HTTPS 代理可能有问题)${NC}"
    echo "  建议: 使用 Google AI (Gemini) 作为替代方案"
fi

echo ""
echo "6. 运行完整工作流测试"
echo "----------------------------------------"
read -p "是否运行完整工作流测试? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "运行测试..."
    docker exec plab-rundown python test_workflow.py
    echo -e "${GREEN}测试完成${NC}"
fi

echo ""
echo "========================================"
echo "测试完成"
echo "========================================"

