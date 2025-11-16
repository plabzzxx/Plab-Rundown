"""
配置管理模块 - 简化版
只从 .env 文件读取配置
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Config(BaseSettings):
    """应用配置类 - 所有配置从 .env 读取"""

    # Gmail 配置
    gmail_credentials_path: str = Field(
        default="credentials/credentials.json",
        alias="GMAIL_CREDENTIALS_PATH"
    )
    gmail_token_path: str = Field(
        default="credentials/token.pickle",
        alias="GMAIL_TOKEN_PATH"
    )
    sender_email: str = Field(
        default="news@daily.therundown.ai",
        alias="SENDER_EMAIL"
    )
    gmail_max_results: int = Field(
        default=5,
        alias="GMAIL_MAX_RESULTS"
    )

    # AI 服务商配置
    ai_provider: str = Field(
        default="openai",
        alias="AI_PROVIDER"
    )

    # OpenAI 配置
    openai_api_key: Optional[str] = Field(default=None, alias="OPENAI_API_KEY")
    openai_model: str = Field(
        default="gpt-4o-mini",
        alias="OPENAI_MODEL"
    )
    openai_base_url: str = Field(
        default="https://api.openai.com/v1",
        alias="OPENAI_BASE_URL"
    )
    openai_temperature: float = Field(
        default=0.3,
        alias="OPENAI_TEMPERATURE"
    )
    openai_max_tokens: int = Field(
        default=4000,
        alias="OPENAI_MAX_TOKENS"
    )

    # Vertex AI 配置
    vertex_ai_project_id: Optional[str] = Field(default=None, alias="VERTEX_AI_PROJECT_ID")
    vertex_ai_location: str = Field(
        default="us-central1",
        alias="VERTEX_AI_LOCATION"
    )
    vertex_ai_model: str = Field(
        default="gemini-2.5-flash",
        alias="VERTEX_AI_MODEL"
    )

    # Google AI Studio 配置
    google_ai_api_key: Optional[str] = Field(default=None, alias="GOOGLE_AI_API_KEY")
    google_ai_model: str = Field(
        default="gemini-2.5-flash",
        alias="GOOGLE_AI_MODEL"
    )

    # 翻译配置
    translation_chunk_size: int = Field(
        default=3000,
        alias="TRANSLATION_CHUNK_SIZE"
    )

    # 固定标题翻译配置
    section_title_latest_developments: str = Field(
        default="今日要闻",
        alias="SECTION_TITLE_LATEST_DEVELOPMENTS"
    )
    section_title_quick_hits: str = Field(
        default="其他要闻",
        alias="SECTION_TITLE_QUICK_HITS"
    )
    subsection_title_trending_tools: str = Field(
        default="🛠️ 热门 AI 工具",
        alias="SUBSECTION_TITLE_TRENDING_TOOLS"
    )
    subsection_title_everything_else: str = Field(
        default="📰 今天人工智能领域的其他一切",
        alias="SUBSECTION_TITLE_EVERYTHING_ELSE"
    )

    # 微信公众号配置
    wechat_app_id: str = Field(alias="WECHAT_APP_ID")
    wechat_app_secret: str = Field(alias="WECHAT_APP_SECRET")
    wechat_auto_publish: bool = Field(
        default=False,
        alias="WECHAT_AUTO_PUBLISH"
    )
    wechat_author: str = Field(
        default="AI早报",
        alias="WECHAT_AUTHOR"
    )
    wechat_title_prefix: str = Field(
        default="【{date}AI早报】",
        alias="WECHAT_TITLE_PREFIX"
    )
    wechat_digest_length: int = Field(
        default=100,
        alias="WECHAT_DIGEST_LENGTH"
    )

    # 数据库配置
    database_url: str = Field(
        default="sqlite:///./data/plab_rundown.db",
        alias="DATABASE_URL"
    )

    # 调度配置
    schedule_enabled: bool = Field(
        default=True,
        alias="SCHEDULE_ENABLED"
    )
    schedule_time: str = Field(
        default="06:00",
        alias="SCHEDULE_TIME"
    )
    timezone: str = Field(
        default="Asia/Shanghai",
        alias="TIMEZONE"
    )

    # 日志配置
    log_level: str = Field(
        default="INFO",
        alias="LOG_LEVEL"
    )
    log_file: str = Field(
        default="logs/app.log",
        alias="LOG_FILE"
    )

    # 应用配置
    app_env: str = Field(
        default="development",
        alias="APP_ENV"
    )

    # 代理配置
    http_proxy: Optional[str] = Field(default=None, alias="HTTP_PROXY")
    https_proxy: Optional[str] = Field(default=None, alias="HTTPS_PROXY")

    # IMAP 邮箱配置
    email_username: Optional[str] = Field(default=None, alias="EMAIL_USERNAME")
    email_password: Optional[str] = Field(default=None, alias="EMAIL_PASSWORD")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"  # 忽略额外字段,避免验证错误

    def is_production(self) -> bool:
        """是否为生产环境"""
        return self.app_env.lower() == "production"

    def is_development(self) -> bool:
        """是否为开发环境"""
        return self.app_env.lower() == "development"


# 全局配置实例
_config: Optional[Config] = None


def get_config() -> Config:
    """获取全局配置实例"""
    global _config
    if _config is None:
        _config = Config()
    return _config
