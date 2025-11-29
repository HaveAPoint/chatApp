"""
chatApp项目包初始化文件（__init__.py）

这个文件将chatApp目录标记为Python包。
这是Django项目的根包，包含项目的核心配置。

chatApp项目包含的模块：
- settings.py: Django项目配置文件（数据库、应用、中间件等）
- urls.py: 根URL路由配置（项目的URL入口）
- wsgi.py: WSGI应用配置（用于生产环境部署）
- asgi.py: ASGI应用配置（用于异步功能和WebSocket）

Django项目结构：
chatApp/
├── __init__.py      # 包初始化文件（本文件）
├── settings.py      # 项目配置
├── urls.py          # URL路由
├── wsgi.py          # WSGI配置
└── asgi.py          # ASGI配置

使用说明：
- 这个包通常不需要直接导入
- Django会自动加载settings.py中的配置
- 其他应用通过INSTALLED_APPS注册到这个项目
"""

# 包初始化代码可以写在这里
# 例如：设置默认配置、导入常用模块等
# 当前不需要初始化代码，保持文件为空即可
