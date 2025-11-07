"""
微信公众号发布器
用于调用微信公众平台 API 发布文章
"""

import os
import time
import json
from pathlib import Path
from typing import Optional, Dict, Any
import requests

from ..utils.logger import get_logger

logger = get_logger(__name__)


class WeChatPublisher:
    """微信公众号发布器"""
    
    # 微信 API 基础 URL
    BASE_URL = "https://api.weixin.qq.com/cgi-bin"
    
    def __init__(
        self,
        app_id: Optional[str] = None,
        app_secret: Optional[str] = None,
        auto_publish: bool = False
    ):
        """
        初始化微信发布器
        
        Args:
            app_id: 微信公众号 AppID
            app_secret: 微信公众号 AppSecret
            auto_publish: 是否自动发布（False 则保存为草稿）
        """
        self.app_id = app_id or os.getenv("WECHAT_APP_ID")
        self.app_secret = app_secret or os.getenv("WECHAT_APP_SECRET")
        self.auto_publish = auto_publish
        
        if not self.app_id or not self.app_secret:
            raise ValueError("未设置微信公众号 AppID 或 AppSecret")
        
        self.access_token = None
        self.token_expires_at = 0
        
        logger.info("微信发布器初始化成功")
    
    def get_access_token(self, force_refresh: bool = False) -> str:
        """
        获取访问令牌
        
        Args:
            force_refresh: 是否强制刷新
        
        Returns:
            access_token
        """
        # 如果 token 未过期且不强制刷新，直接返回
        if not force_refresh and self.access_token and time.time() < self.token_expires_at:
            return self.access_token
        
        logger.info("获取新的 access_token")
        
        url = f"{self.BASE_URL}/token"
        params = {
            "grant_type": "client_credential",
            "appid": self.app_id,
            "secret": self.app_secret
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if "access_token" not in data:
                error_msg = data.get("errmsg", "未知错误")
                raise Exception(f"获取 access_token 失败: {error_msg}")
            
            self.access_token = data["access_token"]
            # access_token 有效期 7200 秒，提前 5 分钟刷新
            self.token_expires_at = time.time() + data.get("expires_in", 7200) - 300
            
            logger.info("access_token 获取成功")
            return self.access_token
        
        except Exception as e:
            logger.error(f"获取 access_token 失败: {e}")
            raise
    
    def upload_thumb_image(self, image_path: str) -> str:
        """
        上传封面图片素材(用于文章封面)

        Args:
            image_path: 本地图片路径

        Returns:
            封面图片的 media_id
        """
        access_token = self.get_access_token()
        url = f"{self.BASE_URL}/material/add_material"

        params = {
            "access_token": access_token,
            "type": "thumb"  # 封面图类型
        }

        try:
            # 读取本地图片
            logger.info(f"读取封面图片: {image_path}")
            with open(image_path, 'rb') as f:
                image_data = f.read()

            # 上传到微信服务器
            files = {
                "media": ("thumb.jpg", image_data, "image/jpeg")
            }

            logger.info("上传封面图到微信服务器")
            response = requests.post(url, params=params, files=files, timeout=30)
            response.raise_for_status()
            data = response.json()

            if "media_id" not in data:
                error_msg = data.get("errmsg", "未知错误")
                raise Exception(f"上传封面图失败: {error_msg}")

            media_id = data["media_id"]
            logger.info(f"封面图上传成功: media_id={media_id}")
            return media_id

        except Exception as e:
            logger.error(f"上传封面图失败: {e}")
            raise

    def upload_image(self, image_url: str) -> str:
        """
        上传图片素材

        Args:
            image_url: 图片 URL 或本地文件路径

        Returns:
            微信服务器上的图片 URL
        """
        access_token = self.get_access_token()
        url = f"{self.BASE_URL}/material/add_material"

        params = {
            "access_token": access_token,
            "type": "image"
        }

        try:
            # 检查是否是本地文件路径
            from pathlib import Path
            if Path(image_url).exists():
                # 本地文件
                logger.info(f"读取本地图片: {image_url}")
                with open(image_url, 'rb') as f:
                    img_content = f.read()
                filename = Path(image_url).name
            else:
                # 下载图片
                logger.info(f"下载图片: {image_url}")
                img_response = requests.get(image_url, timeout=30)
                img_response.raise_for_status()
                img_content = img_response.content
                filename = "image.jpg"

            # 上传到微信服务器
            files = {
                "media": (filename, img_content, "image/jpeg")
            }

            logger.info("上传图片到微信服务器")
            response = requests.post(url, params=params, files=files, timeout=30)
            response.raise_for_status()
            data = response.json()

            if "url" not in data:
                error_msg = data.get("errmsg", "未知错误")
                raise Exception(f"上传图片失败: {error_msg}")

            media_url = data["url"]
            logger.info(f"图片上传成功: {media_url}")
            return media_url

        except Exception as e:
            logger.error(f"上传图片失败: {e}")
            raise
    
    def create_draft(
        self,
        title: str,
        content: str,
        author: str = "The Rundown AI 中文版",
        digest: Optional[str] = None,
        thumb_media_id: Optional[str] = None,
        source_url: Optional[str] = None
    ) -> str:
        """
        创建草稿
        
        Args:
            title: 文章标题
            content: 文章内容（HTML 格式）
            author: 作者
            digest: 摘要
            thumb_media_id: 封面图片素材 ID
            source_url: 原文链接
        
        Returns:
            草稿的 media_id
        """
        access_token = self.get_access_token()
        url = f"{self.BASE_URL}/draft/add"
        
        params = {"access_token": access_token}
        
        # 如果没有提供摘要，从内容中提取前 100 字
        if not digest:
            # 简单提取纯文本
            import re
            text = re.sub(r'<[^>]+>', '', content)
            digest = text[:100] + "..." if len(text) > 100 else text
        
        # 构建文章数据
        article = {
            "title": title,
            "author": author,
            "digest": digest,
            "content": content,
            "content_source_url": source_url or "",
            "need_open_comment": 0,  # 不打开评论
            "only_fans_can_comment": 0  # 所有人可评论
        }
        
        # 如果有封面图
        if thumb_media_id:
            article["thumb_media_id"] = thumb_media_id
        
        payload = {"articles": [article]}

        # 调试:保存发送的内容
        debug_file = Path("data/debug_wechat_request.json")
        debug_file.parent.mkdir(parents=True, exist_ok=True)
        with open(debug_file, 'w', encoding='utf-8') as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
        logger.info(f"已保存请求数据到: {debug_file}")

        try:
            logger.info(f"创建草稿: {title}")
            # 手动序列化JSON以保留emoji字符
            json_data = json.dumps(payload, ensure_ascii=False)
            headers = {'Content-Type': 'application/json; charset=utf-8'}
            response = requests.post(url, params=params, data=json_data.encode('utf-8'), headers=headers, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            if "media_id" not in data:
                error_msg = data.get("errmsg", "未知错误")
                raise Exception(f"创建草稿失败: {error_msg}")
            
            media_id = data["media_id"]
            logger.info(f"草稿创建成功: media_id={media_id}")
            return media_id
        
        except Exception as e:
            logger.error(f"创建草稿失败: {e}")
            raise
    
    def publish_article(
        self,
        title: str,
        content: str,
        author: str = "The Rundown AI 中文版",
        digest: Optional[str] = None,
        thumb_media_id: Optional[str] = None,
        source_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        发布文章
        
        Args:
            title: 文章标题
            content: 文章内容（HTML 格式）
            author: 作者
            digest: 摘要
            thumb_media_id: 封面图片素材 ID
            source_url: 原文链接
        
        Returns:
            发布结果
        """
        # 先创建草稿
        media_id = self.create_draft(
            title=title,
            content=content,
            author=author,
            digest=digest,
            thumb_media_id=thumb_media_id,
            source_url=source_url
        )
        
        # 如果设置为自动发布
        if self.auto_publish:
            return self._publish_draft(media_id)
        else:
            logger.info("已保存为草稿，未自动发布")
            return {
                "status": "draft",
                "media_id": media_id,
                "message": "文章已保存为草稿"
            }
    
    def _publish_draft(self, media_id: str) -> Dict[str, Any]:
        """
        发布草稿
        
        Args:
            media_id: 草稿的 media_id
        
        Returns:
            发布结果
        """
        access_token = self.get_access_token()
        url = f"{self.BASE_URL}/freepublish/submit"
        
        params = {"access_token": access_token}
        payload = {"media_id": media_id}
        
        try:
            logger.info(f"发布草稿: media_id={media_id}")
            response = requests.post(url, params=params, json=payload, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            if data.get("errcode", 0) != 0:
                error_msg = data.get("errmsg", "未知错误")
                raise Exception(f"发布失败: {error_msg}")
            
            publish_id = data.get("publish_id", "")
            logger.info(f"文章发布成功: publish_id={publish_id}")
            
            return {
                "status": "published",
                "media_id": media_id,
                "publish_id": publish_id,
                "message": "文章发布成功"
            }
        
        except Exception as e:
            logger.error(f"发布草稿失败: {e}")
            raise
    
    def format_content(
        self,
        markdown_content: str,
        add_source: bool = True,
        source_text: str = "本文翻译自 The Rundown AI 每日通讯"
    ) -> str:
        """
        格式化内容为微信公众号 HTML 格式
        
        Args:
            markdown_content: Markdown 格式的内容
            add_source: 是否添加来源说明
            source_text: 来源说明文本
        
        Returns:
            HTML 格式的内容
        """
        # 简单的 Markdown 到 HTML 转换
        # 实际使用中可能需要更复杂的转换库
        html = markdown_content
        
        # 替换标题
        html = html.replace('# ', '<h1>').replace('\n', '</h1>\n', 1)
        html = html.replace('## ', '<h2>').replace('\n', '</h2>\n', 1)
        html = html.replace('### ', '<h3>').replace('\n', '</h3>\n', 1)
        
        # 替换段落
        paragraphs = html.split('\n\n')
        html = ''.join([f'<p>{p}</p>' for p in paragraphs if p.strip()])
        
        # 添加来源说明
        if add_source:
            html += f'<p><em>{source_text}</em></p>'
        
        return html

