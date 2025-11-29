"""
video应用包初始化文件（__init__.py）

这个文件将video目录标记为Python包。
即使文件为空，也必须存在才能让Python识别这个目录为一个包。

包的作用：
1. 允许从其他模块导入这个包中的模块
2. 可以在这里定义包的初始化代码
3. 可以控制包的导入行为（__all__变量）

video应用包含的模块：
- models.py: 数据模型（VideoFile, VideoFrame, OCRResult）
- views.py: 视图函数（处理HTTP请求）
- urls.py: URL路由配置
- admin.py: Django管理后台配置
- apps.py: 应用配置类
- utils.py: 工具函数（视频处理、OCR结果合并等）

使用示例：
    from video.models import VideoFile
    from video.views import video_upload
    from video.utils import check_ffmpeg_available
"""

# 包初始化代码可以写在这里
# 例如：导入常用模块、设置默认配置等
# 当前不需要初始化代码，保持文件为空即可
