"""
Django应用配置文件（apps.py）

这个文件定义了video应用的配置类，用于配置应用的行为和属性。
每个Django应用都应该有一个AppConfig类。

AppConfig的作用：
1. 配置应用的元数据（名称、标签等）
2. 定义应用启动时的初始化逻辑
3. 配置应用的默认行为

重要概念：
- 应用（App）：Django项目的功能模块，如video应用处理视频相关功能
- 应用配置（AppConfig）：配置应用行为的类
- 应用注册：在settings.py的INSTALLED_APPS中注册应用

学习要点：
- 每个应用都应该有一个AppConfig类
- 可以在ready()方法中执行应用启动时的初始化代码
- default_auto_field用于设置应用内模型的默认主键类型
"""

# 导入Django的应用配置基类
# AppConfig是所有应用配置类的基类
from django.apps import AppConfig


class VideoConfig(AppConfig):
    """
    Video应用的配置类
    
    这个类配置了video应用的各种设置和行为。
    当Django启动时，会实例化这个类并调用其方法。
    
    常用配置项：
    - name: 应用的完整Python路径（必须）
    - default_auto_field: 应用内模型的默认主键字段类型
    - verbose_name: 应用的显示名称（用于管理后台）
    - label: 应用的简短标签（用于区分同名应用）
    
    可选方法：
    - ready(): 应用准备就绪时调用的方法，可以在这里执行初始化代码
    """
    
    # default_auto_field（默认自动主键字段）
    # 用途：指定应用内模型的默认主键字段类型
    # 如果模型没有显式指定主键，Django会使用这个类型
    # BigAutoField: 64位整数，范围更大（适合大型应用）
    # 注意：这个设置会覆盖settings.py中的DEFAULT_AUTO_FIELD（仅对本应用有效）
    default_auto_field = 'django.db.models.BigAutoField'
    
    # name（应用名称）
    # 用途：指定应用的完整Python路径
    # 这个值必须与应用的包名一致
    # 例如：如果应用在 video/ 目录下，name应该是 'video'
    # Django使用这个值来定位应用的位置
    name = 'video'
    
    # 可选：verbose_name（应用的显示名称）
    # 用途：在Django管理后台等地方显示的应用名称
    # 如果不设置，Django会使用name的值
    # verbose_name = '视频OCR应用'
    
    # 可选：ready()方法
    # 用途：应用准备就绪时调用的方法
    # 可以在这里执行应用启动时的初始化代码，例如：
    # - 注册信号处理器
    # - 初始化缓存
    # - 连接外部服务
    # 
    # def ready(self):
    #     import video.signals  # 导入信号处理器
