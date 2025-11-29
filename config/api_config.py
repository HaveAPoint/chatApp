"""
API配置模块（api_config.py）

该模块负责管理豆包多模态API的配置信息，包括：
- API端点地址
- API密钥（从环境变量读取）
- 模型名称配置
- 其他API相关参数

环境变量配置：
- ARK_API_KEY: API密钥（必须设置）
  设置方法：
    Linux/macOS: export ARK_API_KEY='your-api-key'
    Windows: set ARK_API_KEY=your-api-key
    或在.env文件中设置（推荐）

配置说明：
- base_url: 豆包多模态API的基础端点
- api_key: 从环境变量 ARK_API_KEY 中读取API密钥
- models: 支持的模型列表（豆包多模态模型）
"""

import os  # 用于访问环境变量

# ============================================================================
# API基础配置
# ============================================================================

# API_BASE_URL: API基础端点地址
# 这是豆包多模态API的服务器地址
# 所有API请求都会发送到这个地址
API_BASE_URL = "https://ark.cn-beijing.volces.com/api/v3"

# API_KEY: API密钥
# 从环境变量 ARK_API_KEY 中读取
# os.environ.get(): 获取环境变量，如果不存在则返回默认值（空字符串）
# 
# 安全提示：
# - 不要将API密钥硬编码在代码中
# - 不要将API密钥提交到版本控制系统（Git）
# - 使用环境变量或配置文件（.env）存储密钥
# 
# 设置方法：
# 1. 临时设置（当前终端会话）：
#    export ARK_API_KEY='your-api-key'
# 2. 永久设置（添加到 ~/.bashrc 或 ~/.zshrc）：
#    echo 'export ARK_API_KEY="your-api-key"' >> ~/.bashrc
# 3. 使用.env文件（推荐，需要python-dotenv库）：
#    在项目根目录创建.env文件，添加：ARK_API_KEY=your-api-key
API_KEY = os.environ.get("ARK_API_KEY", "")

# ============================================================================
# 模型配置
# ============================================================================

# DEFAULT_MODEL: 默认使用的AI模型
# 这是豆包多模态模型的最新版本，支持视频和图片输入
# 模型名称格式：doubao-seed-版本号-日期
DEFAULT_MODEL = "doubao-seed-1-6-251015"

# ENABLE_DEEP_THINKING: 是否启用深度思考
# 深度思考是豆包模型的高级功能，可以提高回答质量
# True: 启用深度思考（可能增加响应时间）
# False: 禁用深度思考（响应更快）
ENABLE_DEEP_THINKING = True

# MODELS: 支持的模型列表
# 这是一个字典，包含所有可用的模型配置
# 结构：
#   {
#       '模型类别': {
#           '模型名称': '模型ID',
#           'default': '默认模型ID'
#       }
#   }
# 
# 当前配置：
#   - vision: 视觉模型（支持图片和视频）
#     - doubao_vision: 豆包视觉模型
#     - default: 默认视觉模型
MODELS = {
    'vision': {  # 视觉模型类别
        'doubao_vision': DEFAULT_MODEL,  # 豆包视觉模型
        'default': DEFAULT_MODEL,  # 默认视觉模型
    }
}

# ============================================================================
# API请求配置
# ============================================================================

# API_TIMEOUT: API请求超时时间（秒）
# 如果API请求超过这个时间还没有响应，会抛出超时异常
# 300秒 = 5分钟
# 视频处理可能需要较长时间，所以设置较长的超时时间
# 如果网络较慢或视频较大，可能需要增加这个值
API_TIMEOUT = 300  # 5分钟

# ============================================================================
# 文件上传限制
# ============================================================================

# MAX_VIDEO_SIZE: 最大视频文件大小（字节）
# 100 * 1024 * 1024 = 100MB
# 这是上传视频文件的最大大小限制
# 超过这个大小的文件会被拒绝上传
# 注意：API可能还有自己的大小限制（通常更小，如15MB）
MAX_VIDEO_SIZE = 100 * 1024 * 1024  # 100MB

# SUPPORTED_VIDEO_FORMATS: 支持的视频格式列表
# 这是允许上传的视频文件扩展名列表
# 只有这些格式的视频文件才能上传
# 支持的格式：
#   - .mp4: MPEG-4视频格式（最常用）
#   - .avi: Audio Video Interleave格式
#   - .mov: QuickTime视频格式（Apple）
#   - .mkv: Matroska视频格式
#   - .webm: WebM视频格式（Web标准）
SUPPORTED_VIDEO_FORMATS = ['.mp4', '.avi', '.mov', '.mkv', '.webm']

