"""
测试工作流脚本
直接运行 run_daily_workflow 函数
"""
import sys
import os
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.scheduler.main import run_daily_workflow
from src.utils.logger import setup_logging

if __name__ == "__main__":
    # 初始化日志系统
    log_level = os.getenv("LOG_LEVEL", "INFO")
    log_file = os.getenv("LOG_FILE", "logs/app.log")
    setup_logging(log_level=log_level, log_file=log_file)

    print("开始测试工作流...")
    try:
        run_daily_workflow()
        print("\n工作流执行完成！")
    except Exception as e:
        print(f"\n❌ 工作流执行失败: {e}")
        import traceback
        traceback.print_exc()

