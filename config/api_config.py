"""
API配置模块

该模块负责管理豆包多模态API的配置信息，包括：
- API端点地址
- API密钥（从环境变量读取）
- 模型名称配置
- 其他API相关参数

配置说明：
- base_url: 豆包多模态API的基础端点
- api_key: 从环境变量 ARK_API_KEY 中读取API密钥
- models: 支持的模型列表（豆包多模态模型）
"""

import os

# API基础配置 - 豆包多模态API
API_BASE_URL = "https://ark.cn-beijing.volces.com/api/v3"
API_KEY = os.environ.get("ARK_API_KEY", "")

# 默认使用官方提供的最新豆包多模态模型终端
DEFAULT_MODEL = "doubao-seed-1-6-251015"
ENABLE_DEEP_THINKING = True

# 支持的模型列表（当前仅使用多模态视觉模型）
MODELS = {
    'vision': {
        'doubao_vision': DEFAULT_MODEL,
        'default': DEFAULT_MODEL,
    }
}

# API请求超时设置（秒）
API_TIMEOUT = 300  # 5分钟，视频处理可能需要较长时间

# 文件上传限制
MAX_VIDEO_SIZE = 100 * 1024 * 1024  # 100MB
SUPPORTED_VIDEO_FORMATS = ['.mp4', '.avi', '.mov', '.mkv', '.webm']

