"""
数据库模块
用于记录已处理的邮件和执行日志
支持 Supabase (PostgreSQL)
"""

import os
from datetime import datetime
from typing import Optional, List
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import NullPool

from .logger import get_logger

logger = get_logger(__name__)

Base = declarative_base()


class ProcessedEmail(Base):
    """已处理邮件记录"""
    
    __tablename__ = "processed_emails"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    email_id = Column(String(255), unique=True, nullable=False, index=True)
    subject = Column(String(500))
    sender = Column(String(255))
    received_date = Column(DateTime)
    processed_date = Column(DateTime, default=datetime.now)
    wechat_media_id = Column(String(255))
    wechat_publish_id = Column(String(255))
    status = Column(String(50), default="success")  # success, failed, pending
    error_message = Column(Text)
    
    def __repr__(self):
        return f"<ProcessedEmail(email_id='{self.email_id}', subject='{self.subject}')>"


class ExecutionLog(Base):
    """执行日志"""
    
    __tablename__ = "execution_logs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    execution_time = Column(DateTime, default=datetime.now)
    status = Column(String(50))  # success, failed, partial
    email_count = Column(Integer, default=0)
    error_message = Column(Text)
    duration_seconds = Column(Integer)
    
    def __repr__(self):
        return f"<ExecutionLog(time='{self.execution_time}', status='{self.status}')>"


class Database:
    """数据库管理类 - 支持 Supabase PostgreSQL"""

    def __init__(self, database_url: Optional[str] = None):
        """
        初始化数据库

        Args:
            database_url: 数据库连接 URL，如果为 None 则从环境变量读取
        """
        # 从环境变量获取数据库 URL
        if database_url is None:
            database_url = os.getenv("DATABASE_URL")

        # 如果没有设置 DATABASE_URL，使用默认的 SQLite
        if not database_url:
            # 本地开发默认使用 SQLite
            database_url = "sqlite:///./data/plab_rundown.db"
            logger.info("未设置 DATABASE_URL，使用默认 SQLite 数据库")

        # Render PostgreSQL 使用 postgres:// 但 SQLAlchemy 需要 postgresql://
        if database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql://", 1)

        self.database_url = database_url

        # 根据数据库类型选择不同的配置
        is_sqlite = database_url.startswith("sqlite:")

        if is_sqlite:
            # SQLite 配置
            # 确保数据目录存在
            db_path = database_url.replace("sqlite:///", "")
            db_dir = os.path.dirname(db_path)
            if db_dir and not os.path.exists(db_dir):
                os.makedirs(db_dir, exist_ok=True)

            self.engine = create_engine(
                database_url,
                echo=False,
                connect_args={"check_same_thread": False}  # SQLite 特定配置
            )
            logger.info(f"数据库初始化成功 (SQLite): {db_path}")
        else:
            # PostgreSQL 配置（Render PostgreSQL）
            # 使用 NullPool 以避免连接池问题
            self.engine = create_engine(
                database_url,
                echo=False,
                poolclass=NullPool,
                connect_args={
                    "connect_timeout": 10,
                }
            )
            logger.info(f"数据库初始化成功 (PostgreSQL)")

        self.SessionLocal = sessionmaker(bind=self.engine)

        # 创建表
        self._create_tables()
    
    def _create_tables(self):
        """创建数据表"""
        Base.metadata.create_all(self.engine)
        logger.info("数据表创建完成")
    
    def get_session(self) -> Session:
        """获取数据库会话"""
        return self.SessionLocal()
    
    def is_email_processed(self, email_id: str) -> bool:
        """
        检查邮件是否已处理
        
        Args:
            email_id: 邮件 ID
        
        Returns:
            是否已处理
        """
        session = self.get_session()
        try:
            result = session.query(ProcessedEmail).filter_by(email_id=email_id).first()
            return result is not None
        finally:
            session.close()
    
    def add_processed_email(
        self,
        email_id: str,
        subject: str,
        sender: str,
        received_date: Optional[datetime] = None,
        wechat_media_id: Optional[str] = None,
        wechat_publish_id: Optional[str] = None,
        status: str = "success",
        error_message: Optional[str] = None
    ) -> ProcessedEmail:
        """
        添加已处理邮件记录
        
        Args:
            email_id: 邮件 ID
            subject: 邮件主题
            sender: 发件人
            received_date: 接收时间
            wechat_media_id: 微信素材 ID
            wechat_publish_id: 微信发布 ID
            status: 处理状态
            error_message: 错误信息
        
        Returns:
            ProcessedEmail 实例
        """
        session = self.get_session()
        try:
            email = ProcessedEmail(
                email_id=email_id,
                subject=subject,
                sender=sender,
                received_date=received_date,
                wechat_media_id=wechat_media_id,
                wechat_publish_id=wechat_publish_id,
                status=status,
                error_message=error_message
            )
            session.add(email)
            session.commit()
            logger.info(f"已记录处理邮件: {email_id}")
            return email
        except Exception as e:
            session.rollback()
            logger.error(f"记录处理邮件失败: {e}")
            raise
        finally:
            session.close()
    
    def get_processed_emails(
        self,
        limit: int = 10,
        status: Optional[str] = None
    ) -> List[ProcessedEmail]:
        """
        获取已处理邮件列表
        
        Args:
            limit: 返回数量限制
            status: 过滤状态
        
        Returns:
            ProcessedEmail 列表
        """
        session = self.get_session()
        try:
            query = session.query(ProcessedEmail)
            if status:
                query = query.filter_by(status=status)
            
            results = query.order_by(ProcessedEmail.processed_date.desc()).limit(limit).all()
            return results
        finally:
            session.close()
    
    def add_execution_log(
        self,
        status: str,
        email_count: int = 0,
        error_message: Optional[str] = None,
        duration_seconds: Optional[int] = None
    ) -> ExecutionLog:
        """
        添加执行日志
        
        Args:
            status: 执行状态
            email_count: 处理邮件数量
            error_message: 错误信息
            duration_seconds: 执行时长（秒）
        
        Returns:
            ExecutionLog 实例
        """
        session = self.get_session()
        try:
            log = ExecutionLog(
                status=status,
                email_count=email_count,
                error_message=error_message,
                duration_seconds=duration_seconds
            )
            session.add(log)
            session.commit()
            logger.info(f"已记录执行日志: status={status}")
            return log
        except Exception as e:
            session.rollback()
            logger.error(f"记录执行日志失败: {e}")
            raise
        finally:
            session.close()
    
    def get_execution_logs(self, limit: int = 10) -> List[ExecutionLog]:
        """
        获取执行日志列表
        
        Args:
            limit: 返回数量限制
        
        Returns:
            ExecutionLog 列表
        """
        session = self.get_session()
        try:
            results = session.query(ExecutionLog).order_by(
                ExecutionLog.execution_time.desc()
            ).limit(limit).all()
            return results
        finally:
            session.close()

