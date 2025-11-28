"""
API客户端模块

该模块封装了OpenAI兼容的API客户端，用于与豆包多模态API进行交互。
主要功能：
1. 初始化API客户端连接
2. 处理视频/图像OCR请求
3. 错误处理和重试机制
"""

from openai import OpenAI
from typing import Dict, Any
import logging
import os
from config.api_config import (
    API_BASE_URL,
    API_KEY,
    MODELS,
    API_TIMEOUT,
    ENABLE_DEEP_THINKING
)

logger = logging.getLogger(__name__)


def _get_completion_kwargs() -> Dict[str, Any]:
    """统一追加可选API特性（如深度思考）"""
    extra_kwargs = {}
    if ENABLE_DEEP_THINKING:
        extra_kwargs['extra_body'] = {"enable_deep_thinking": True}
    return extra_kwargs


def get_api_client() -> OpenAI:
    """
    获取配置好的OpenAI API客户端实例
    
    该函数创建一个连接到豆包多模态API的OpenAI客户端实例。
    客户端从环境变量 ARK_API_KEY 中读取API密钥。
    
    Returns:
        OpenAI: 配置好的API客户端实例
        
    Raises:
        ValueError: 如果ARK_API_KEY环境变量未设置
        
    Example:
        >>> client = get_api_client()
        >>> response = client.chat.completions.create(...)
    """
    if not API_KEY:
        raise ValueError(
            "ARK_API_KEY环境变量未设置。请设置环境变量："
            "export ARK_API_KEY='your-api-key'"
        )
    
    return OpenAI(
        api_key=API_KEY,
        base_url=API_BASE_URL,
        timeout=API_TIMEOUT
    )


def get_video_ocr_prompt() -> str:
    """生成视频OCR识别的prompt"""
    return f"""请分析目标视频，提取其中**非动态字幕、非平台水印**的所有画面文字，并严格按照以下规则输出：  
1. **文字分类**：分为「艺术字形式文字」和「非艺术字形式文字」两类；  
   - 艺术字：指经过设计排版的装饰性文字（包括但不限于海报艺术标题、竖排人物介绍、创意字体文本）；  
   - 非艺术字：指正式静态文本（包括但不限于医疗报告单、电脑界面、证件打印文字、竖排时间提醒等）；  
   - 请注意：两种文字可能互相包含，请不要漏掉任何文字。
2. **时间段标注**：每个文字条目需后置**精确时间段**（格式：时:分:秒 时:分:秒）；  
3. **内容完整性**：文字需完整转录（含标点、括号、大小写、特殊符号，保持原文样式）；  
4. **结构要求**：不分类型 结构输出为： 文字 视频文件名 开始时间 结束时间

请严格按照以上规则执行，只识别符合要求的文字内容。"""


def process_video_ocr(
    client: OpenAI,
    video_path: str,
    model: str = None,
    prompt: str = None
) -> Dict[str, Any]:
    """
    处理视频OCR请求 - 使用豆包多模态模型直接处理视频
    
    该函数直接将视频文件发送到豆包多模态API进行OCR识别。
    实际使用的模型由环境变量 ARK_VISION_MODEL 定义，可支持视频输入。
    
    Args:
        client: OpenAI客户端实例
        video_path: 视频文件的本地路径
        model: 使用的模型名称，如果为None则使用默认模型
        prompt: OCR识别的提示词
        
    Returns:
        Dict包含以下键：
            - content: OCR识别的文字内容
            - model: 使用的模型名称
            - success: 是否成功
            - usage: API使用统计信息
            
    Raises:
        Exception: 当API请求失败时抛出异常
        
    Example:
        >>> client = get_api_client()
        >>> result = process_video_ocr(client, "/path/to/video.mp4")
        >>> print(result['content'])
    """
    if model is None:
        model = MODELS['vision']['default']

    if prompt is None:
        prompt = get_video_ocr_prompt()
    
    try:
        import base64
        from pathlib import Path
        
        # 读取视频文件并编码为base64
        logger.info(f"开始处理视频OCR，文件: {video_path}, 模型: {model}")
        
        # 检查文件大小（base64编码会增加约33%大小）
        file_size = os.path.getsize(video_path)
        file_size_mb = file_size / (1024 * 1024)
        logger.info(f"视频文件大小: {file_size_mb:.2f} MB")
        
        # 建议限制：base64编码后不超过20MB（原始文件约15MB）
        if file_size > 15 * 1024 * 1024:  # 15MB
            logger.warning(f"视频文件较大 ({file_size_mb:.2f}MB)，base64编码后可能超过API限制")
        
        with open(video_path, 'rb') as f:
            video_bytes = f.read()
            video_data = base64.b64encode(video_bytes).decode('utf-8')
        
        # 记录base64编码后的长度
        base64_size_mb = len(video_data) / (1024 * 1024)
        logger.info(f"Base64编码后大小: {base64_size_mb:.2f} MB")
        
        # 获取文件扩展名以确定MIME类型
        file_ext = Path(video_path).suffix.lower()
        mime_type_map = {
            '.mp4': 'video/mp4',
            '.avi': 'video/x-msvideo',
            '.mov': 'video/quicktime',
            '.mkv': 'video/x-matroska',
            '.webm': 'video/webm'
        }
        mime_type = mime_type_map.get(file_ext, 'video/mp4')
        
        # 构建消息，包含视频
        # 豆包多模态模型使用 video_url 类型处理视频
        high_detail = {
            "detail": "high"
        }
        
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "video_url",
                        "video_url": {
                            "url": f"data:{mime_type};base64,{video_data}"
                        },
                        **high_detail
                    },
                    {
                        "type": "text",
                        "text": prompt
                    }
                ]
            }
        ]
        
        # 调用API
        logger.info(f"发送视频OCR请求到豆包API，模型: {model}")
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            **_get_completion_kwargs()
        )
        
        result = {
            'content': response.choices[0].message.content,
            'model': response.model,
            'usage': {
                'prompt_tokens': response.usage.prompt_tokens,
                'completion_tokens': response.usage.completion_tokens,
                'total_tokens': response.usage.total_tokens
            },
            'success': True
        }
        
        logger.info(f"视频OCR处理成功，消耗token: {result['usage']['total_tokens']}")
        return result
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"视频OCR处理失败: {error_msg}")
        
        # 提供更详细的错误信息
        if "Invalid base64" in error_msg or "InvalidParameter" in error_msg:
            raise Exception(
                f"视频格式错误或文件过大。"
                f"请确保：1) 视频文件小于15MB；2) 视频格式为MP4/MOV/AVI等标准格式；"
                f"3) 如果文件较大，请先压缩视频。"
                f"原始错误: {error_msg}"
            )
        raise


def process_image_ocr(
    client: OpenAI,
    image_path: str,
    model: str = None,
    prompt: str = "请识别并提取图片中的所有文字内容。"
) -> Dict[str, Any]:
    """
    处理单张图片的OCR请求
    
    该函数将图片文件发送到API进行OCR识别。
    用于处理从视频中提取的帧图像。
    
    Args:
        client: OpenAI客户端实例
        image_path: 图片文件的本地路径
        model: 使用的模型名称，如果为None则使用默认模型
        prompt: OCR识别的提示词
        
    Returns:
        Dict包含以下键：
            - content: OCR识别的文字内容
            - model: 使用的模型名称
            - success: 是否成功
            
    Raises:
        Exception: 当API请求失败时抛出异常
        
    Example:
        >>> client = get_api_client()
        >>> result = process_image_ocr(client, "/path/to/frame.jpg")
        >>> print(result['content'])
    """
    if model is None:
        model = MODELS['vision']['default']
    
    try:
        import base64
        from pathlib import Path
        
        # 读取图片文件
        with open(image_path, 'rb') as f:
            image_data = base64.b64encode(f.read()).decode('utf-8')
        
        # 构建消息，包含图片
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image_data}"
                        },
                        "detail": "high"
                    }
                ]
            }
        ]
        
        logger.info(f"开始处理图片OCR，文件: {image_path}")
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            **_get_completion_kwargs()
        )
        
        result = {
            'content': response.choices[0].message.content,
            'model': response.model,
            'usage': {
                'prompt_tokens': response.usage.prompt_tokens,
                'completion_tokens': response.usage.completion_tokens,
                'total_tokens': response.usage.total_tokens
            },
            'success': True
        }
        
        logger.info(f"图片OCR处理成功，消耗token: {result['usage']['total_tokens']}")
        return result
        
    except Exception as e:
        logger.error(f"图片OCR处理失败: {str(e)}")
        raise

