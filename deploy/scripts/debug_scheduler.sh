#!/bin/bash
# 调试定时任务脚本 - 检查 Docker 容器中的定时任务配置

echo "=========================================="
echo "🔍 Plab-Rundown 定时任务调试工具"
echo "=========================================="
echo ""

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 容器名称
CONTAINER_NAME="plab-rundown"

# 检查容器是否运行
echo -e "${BLUE}[1/7] 检查容器状态${NC}"
echo "----------------------------------------"
if docker ps | grep -q "$CONTAINER_NAME"; then
    echo -e "${GREEN}✅ 容器正在运行${NC}"
    docker ps --filter "name=$CONTAINER_NAME" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
else
    echo -e "${RED}❌ 容器未运行${NC}"
    echo "请先启动容器: cd ~/plab-rundown/deploy && docker-compose up -d"
    exit 1
fi
echo ""

# 检查容器内的时区
echo -e "${BLUE}[2/7] 检查容器时区${NC}"
echo "----------------------------------------"
CONTAINER_TZ=$(docker exec $CONTAINER_NAME date +"%Z %z")
CONTAINER_TIME=$(docker exec $CONTAINER_NAME date +"%Y-%m-%d %H:%M:%S")
echo "容器时区: $CONTAINER_TZ"
echo "容器时间: $CONTAINER_TIME"
echo ""

# 检查宿主机时区
echo -e "${BLUE}[3/7] 检查宿主机时区${NC}"
echo "----------------------------------------"
HOST_TZ=$(date +"%Z %z")
HOST_TIME=$(date +"%Y-%m-%d %H:%M:%S")
echo "宿主机时区: $HOST_TZ"
echo "宿主机时间: $HOST_TIME"
echo ""

# 检查 config.yaml 是否存在
echo -e "${BLUE}[4/7] 检查配置文件${NC}"
echo "----------------------------------------"
if docker exec $CONTAINER_NAME test -f /app/config/config.yaml; then
    echo -e "${GREEN}✅ config.yaml 存在${NC}"
    echo ""
    echo "配置内容 (scheduler 部分):"
    docker exec $CONTAINER_NAME grep -A 10 "scheduler:" /app/config/config.yaml || echo "未找到 scheduler 配置"
else
    echo -e "${RED}❌ config.yaml 不存在${NC}"
    echo -e "${YELLOW}⚠️  将使用默认配置: 每天 9:00 执行${NC}"
fi
echo ""

# 检查环境变量
echo -e "${BLUE}[5/7] 检查环境变量${NC}"
echo "----------------------------------------"
echo "SCHEDULE_ENABLED: $(docker exec $CONTAINER_NAME printenv SCHEDULE_ENABLED)"
echo "SCHEDULE_TIME: $(docker exec $CONTAINER_NAME printenv SCHEDULE_TIME)"
echo "TIMEZONE: $(docker exec $CONTAINER_NAME printenv TIMEZONE)"
echo ""

# 检查健康检查接口
echo -e "${BLUE}[6/7] 检查调度器状态 (健康检查接口)${NC}"
echo "----------------------------------------"
HEALTH_CHECK=$(curl -s http://localhost:10000/health 2>/dev/null)
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ 健康检查接口正常${NC}"
    echo ""
    echo "$HEALTH_CHECK" | python3 -m json.tool 2>/dev/null || echo "$HEALTH_CHECK"
else
    echo -e "${RED}❌ 健康检查接口无法访问${NC}"
    echo "请检查容器是否正常运行"
fi
echo ""

# 查看最近的日志
echo -e "${BLUE}[7/7] 查看最近的容器日志${NC}"
echo "----------------------------------------"
echo "最近 30 行日志:"
docker logs --tail 30 $CONTAINER_NAME
echo ""

# 总结
echo "=========================================="
echo -e "${GREEN}调试信息收集完成!${NC}"
echo "=========================================="
echo ""
echo "📝 下一步操作建议:"
echo ""
echo "1. 如果 config.yaml 不存在:"
echo "   - 将本地的 config/config.yaml 复制到服务器"
echo "   - 重启容器: docker-compose restart"
echo ""
echo "2. 如果时区不正确:"
echo "   - 检查 Dockerfile 中的 TZ 环境变量"
echo "   - 重新构建镜像: docker-compose build"
echo ""
echo "3. 查看完整日志:"
echo "   docker logs -f $CONTAINER_NAME"
echo ""
echo "4. 进入容器调试:"
echo "   docker exec -it $CONTAINER_NAME bash"
echo ""
echo "5. 手动触发一次任务测试:"
echo "   docker exec $CONTAINER_NAME python -c 'from src.scheduler.main import run_daily_workflow; run_daily_workflow()'"
echo ""

