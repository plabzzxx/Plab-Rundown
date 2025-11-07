"""
定时任务调度器
"""

import time
from datetime import datetime
from typing import Callable, Optional
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import pytz

from ..utils.logger import get_logger

logger = get_logger(__name__)


class TaskScheduler:
    """任务调度器"""
    
    def __init__(self, timezone: str = "Asia/Shanghai"):
        """
        初始化调度器
        
        Args:
            timezone: 时区
        """
        self.timezone = pytz.timezone(timezone)
        self.scheduler = BackgroundScheduler(timezone=self.timezone)
        self.is_running = False
        
        logger.info(f"任务调度器初始化成功: timezone={timezone}")
    
    def add_daily_task(
        self,
        task_func: Callable,
        hour: int,
        minute: int = 0,
        task_id: str = "daily_task"
    ) -> None:
        """
        添加每日定时任务
        
        Args:
            task_func: 要执行的任务函数
            hour: 小时 (0-23)
            minute: 分钟 (0-59)
            task_id: 任务 ID
        """
        trigger = CronTrigger(
            hour=hour,
            minute=minute,
            timezone=self.timezone
        )
        
        self.scheduler.add_job(
            task_func,
            trigger=trigger,
            id=task_id,
            name=f"Daily task at {hour:02d}:{minute:02d}",
            replace_existing=True
        )
        
        logger.info(f"已添加每日任务: {hour:02d}:{minute:02d} ({self.timezone})")
    
    def add_interval_task(
        self,
        task_func: Callable,
        hours: int = 0,
        minutes: int = 0,
        seconds: int = 0,
        task_id: str = "interval_task"
    ) -> None:
        """
        添加间隔执行任务
        
        Args:
            task_func: 要执行的任务函数
            hours: 间隔小时数
            minutes: 间隔分钟数
            seconds: 间隔秒数
            task_id: 任务 ID
        """
        self.scheduler.add_job(
            task_func,
            'interval',
            hours=hours,
            minutes=minutes,
            seconds=seconds,
            id=task_id,
            replace_existing=True
        )
        
        logger.info(f"已添加间隔任务: 每 {hours}h {minutes}m {seconds}s 执行一次")
    
    def start(self) -> None:
        """启动调度器"""
        if not self.is_running:
            self.scheduler.start()
            self.is_running = True
            logger.info("任务调度器已启动")
            
            # 打印所有已调度的任务
            jobs = self.scheduler.get_jobs()
            if jobs:
                logger.info(f"当前已调度 {len(jobs)} 个任务:")
                for job in jobs:
                    logger.info(f"  - {job.name} (下次执行: {job.next_run_time})")
            else:
                logger.warning("没有已调度的任务")
    
    def stop(self) -> None:
        """停止调度器"""
        if self.is_running:
            self.scheduler.shutdown()
            self.is_running = False
            logger.info("任务调度器已停止")
    
    def run_task_now(self, task_func: Callable) -> None:
        """
        立即执行任务
        
        Args:
            task_func: 要执行的任务函数
        """
        logger.info("立即执行任务")
        try:
            task_func()
        except Exception as e:
            logger.error(f"任务执行失败: {e}", exc_info=True)
    
    def keep_alive(self) -> None:
        """保持调度器运行"""
        try:
            while self.is_running:
                time.sleep(1)
        except (KeyboardInterrupt, SystemExit):
            logger.info("收到退出信号")
            self.stop()

