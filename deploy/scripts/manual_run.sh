#!/bin/bash
# 手动运行一次工作流 (用于测试)

echo "=========================================="
echo "🚀 手动运行 Plab-Rundown 工作流"
echo "=========================================="
echo ""

# 项目目录
PROJECT_DIR="/home/ubuntu/plab-rundown"
VENV_DIR="${PROJECT_DIR}/.venv"

# 检查项目目录
if [ ! -d "$PROJECT_DIR" ]; then
    echo "❌ 项目目录不存在: $PROJECT_DIR"
    exit 1
fi

# 进入项目目录
cd "$PROJECT_DIR"

# 激活虚拟环境
if [ -f "$VENV_DIR/bin/activate" ]; then
    source "$VENV_DIR/bin/activate"
else
    echo "❌ 虚拟环境不存在: $VENV_DIR"
    exit 1
fi

# 运行工作流
echo "开始执行工作流..."
echo ""

python -c "
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path.cwd()
sys.path.insert(0, str(project_root))

# 导入并执行工作流
from src.scheduler.main import run_daily_workflow

print('=' * 70)
print('🎯 手动执行每日工作流')
print('=' * 70)

try:
    run_daily_workflow()
    print('=' * 70)
    print('✅ 工作流执行成功!')
    print('=' * 70)
except Exception as e:
    print('=' * 70)
    print(f'❌ 工作流执行失败: {e}')
    print('=' * 70)
    import traceback
    traceback.print_exc()
    sys.exit(1)
"

echo ""
echo "=========================================="
echo "✅ 执行完成"
echo "=========================================="

