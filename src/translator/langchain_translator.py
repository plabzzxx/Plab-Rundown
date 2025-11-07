"""
基于 LangChain 的翻译器
使用 OpenAI 或其他 LLM 进行英译中
支持多个 AI 服务商：OpenAI, Vertex AI, Google AI Studio
"""

from typing import Optional, List, Union
import os

from langchain_openai import ChatOpenAI
from langchain_google_vertexai import ChatVertexAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage

from ..utils.logger import get_logger
from ..utils.config import get_config

logger = get_logger(__name__)


class LangChainTranslator:
    """
    LangChain 翻译器类
    支持多个 AI 服务商：OpenAI, Vertex AI, Google AI Studio
    """

    # 默认翻译提示词
    DEFAULT_SYSTEM_PROMPT = """你是一位专业的 AI 领域翻译专家，精通英文和中文。
你的任务是将英文内容准确、流畅地翻译成中文。"""

    DEFAULT_TRANSLATION_TEMPLATE = """请将以下英文内容翻译成中文。

⚠️ 重要要求：
1. 准确翻译 AI、机器学习、大语言模型等专业术语
2. 语言流畅自然，符合中文阅读习惯
3. **对于专用词汇和公司名称，保持原文不翻译**，包括但不限于：
   - 公司名称：OpenAI、Google、Meta、Anthropic、xAI、Pomelli、Canva、Udio 等
   - 产品名称：ChatGPT、Gemini、Claude、Sora、Copilot、Perplexity 等
   - 人名：保持原文（如 Sam Altman、Elon Musk、Ilya Sutskever 等）
   - 技术术语：如果是专有名词或品牌名称，保持原文
4. 保持数字、日期、专有名词的准确性
5. **只输出翻译后的纯文本** - 不要添加任何HTML标签、markdown标记(如```html)、解释或说明
6. **直接输出翻译结果** - 不要有任何前缀、后缀或格式标记

原文：
{content}

翻译结果："""
    
    def __init__(
        self,
        provider: Optional[str] = None,
        temperature: float = 0.3,
        max_tokens: int = 4000,
        chunk_size: int = 3000,
        system_prompt: Optional[str] = None,
        translation_template: Optional[str] = None
    ):
        """
        初始化翻译器

        Args:
            provider: AI 服务商 (openai, vertex_ai, google_ai)，如果为 None 则从配置读取
            temperature: 温度参数，控制输出的随机性
            max_tokens: 最大生成 token 数
            chunk_size: 分段翻译的字符数阈值
            system_prompt: 系统提示词
            translation_template: 翻译提示词模板
        """
        # 加载配置
        config = get_config()

        # 确定使用的服务商
        self.provider = provider or config.ai_provider
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.chunk_size = chunk_size

        # 根据服务商初始化 LLM
        self.llm = self._init_llm(config)

        # 设置提示词
        self.system_prompt = system_prompt or self.DEFAULT_SYSTEM_PROMPT
        self.translation_template = translation_template or self.DEFAULT_TRANSLATION_TEMPLATE

        logger.info(f"翻译器初始化成功: provider={self.provider}, temperature={temperature}")

    def _init_llm(self, config) -> Union[ChatOpenAI, ChatVertexAI, ChatGoogleGenerativeAI]:
        """
        根据配置初始化 LLM

        Args:
            config: 配置对象

        Returns:
            初始化的 LLM 实例
        """
        if self.provider == "openai":
            if not config.openai_api_key:
                raise ValueError("未设置 OPENAI_API_KEY")

            logger.info(f"使用 OpenAI: model={config.openai_model}")
            print(f"DEBUG: 正在使用的API Key为: '{config.openai_api_key}'")
            return ChatOpenAI(
                api_key=config.openai_api_key,
                model=config.openai_model,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                base_url=config.openai_base_url
            )

        elif self.provider == "vertex_ai":
            if not config.vertex_ai_project_id:
                raise ValueError("未设置 VERTEX_AI_PROJECT_ID")

            logger.info(f"使用 Vertex AI: model={config.vertex_ai_model}, project={config.vertex_ai_project_id}")
            return ChatVertexAI(
                model=config.vertex_ai_model,
                project=config.vertex_ai_project_id,
                location=config.vertex_ai_location,
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )

        elif self.provider == "google_ai":
            if not config.google_ai_api_key:
                raise ValueError("未设置 GOOGLE_AI_API_KEY")

            logger.info(f"使用 Google AI Studio: model={config.google_ai_model}")
            return ChatGoogleGenerativeAI(
                model=config.google_ai_model,
                google_api_key=config.google_ai_api_key,
                temperature=self.temperature,
                max_output_tokens=self.max_tokens
            )

        else:
            raise ValueError(f"不支持的 AI 服务商: {self.provider}，支持的服务商: openai, vertex_ai, google_ai")
    
    def translate(self, text: str) -> str:
        """
        翻译文本
        
        Args:
            text: 要翻译的英文文本
        
        Returns:
            翻译后的中文文本
        """
        if not text or not text.strip():
            logger.warning("输入文本为空")
            return ""
        
        # 如果文本较短，直接翻译
        if len(text) <= self.chunk_size:
            return self._translate_chunk(text)
        
        # 如果文本较长，分段翻译
        logger.info(f"文本较长 ({len(text)} 字符)，将分段翻译")
        return self._translate_long_text(text)
    
    def _translate_chunk(self, text: str) -> str:
        """
        翻译单个文本块
        
        Args:
            text: 要翻译的文本
        
        Returns:
            翻译结果
        """
        try:
            # 构建提示词
            prompt = self.translation_template.format(content=text)
            
            # 调用 LLM
            messages = [
                SystemMessage(content=self.system_prompt),
                HumanMessage(content=prompt)
            ]
            
            logger.info(f"开始翻译 ({len(text)} 字符)...")
            response = self.llm.invoke(messages)
            
            translated = response.content.strip()
            logger.info(f"翻译完成 ({len(translated)} 字符)")
            
            return translated
        
        except Exception as e:
            logger.error(f"翻译失败: {e}")
            raise
    
    def _translate_long_text(self, text: str) -> str:
        """
        分段翻译长文本
        
        Args:
            text: 要翻译的长文本
        
        Returns:
            翻译结果
        """
        # 按段落分割
        paragraphs = text.split('\n\n')
        
        translated_paragraphs = []
        current_chunk = []
        current_length = 0
        
        for para in paragraphs:
            para_length = len(para)
            
            # 如果当前块加上这个段落会超过阈值，先翻译当前块
            if current_length + para_length > self.chunk_size and current_chunk:
                chunk_text = '\n\n'.join(current_chunk)
                translated = self._translate_chunk(chunk_text)
                translated_paragraphs.append(translated)
                
                current_chunk = [para]
                current_length = para_length
            else:
                current_chunk.append(para)
                current_length += para_length
        
        # 翻译最后一个块
        if current_chunk:
            chunk_text = '\n\n'.join(current_chunk)
            translated = self._translate_chunk(chunk_text)
            translated_paragraphs.append(translated)
        
        # 合并所有翻译结果
        result = '\n\n'.join(translated_paragraphs)
        logger.info(f"长文本翻译完成，共 {len(translated_paragraphs)} 个块")
        
        return result
    
    def translate_with_context(
        self,
        text: str,
        context: Optional[str] = None
    ) -> str:
        """
        带上下文的翻译
        
        Args:
            text: 要翻译的文本
            context: 上下文信息（例如：文章主题、背景等）
        
        Returns:
            翻译结果
        """
        if context:
            enhanced_template = f"""上下文信息：{context}

{self.translation_template}"""
            
            original_template = self.translation_template
            self.translation_template = enhanced_template
            
            try:
                result = self.translate(text)
                return result
            finally:
                self.translation_template = original_template
        else:
            return self.translate(text)
    
    def batch_translate(self, texts: List[str]) -> List[str]:
        """
        批量翻译
        
        Args:
            texts: 要翻译的文本列表
        
        Returns:
            翻译结果列表
        """
        results = []
        total = len(texts)
        
        for i, text in enumerate(texts, 1):
            logger.info(f"翻译进度: {i}/{total}")
            translated = self.translate(text)
            results.append(translated)
        
        return results

