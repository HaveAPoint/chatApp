"""
ASGI配置文件（asgi.py）

ASGI（Asynchronous Server Gateway Interface）是WSGI的异步版本。
这个文件定义了ASGI应用对象，用于支持异步功能和WebSocket连接。

ASGI vs WSGI：
- WSGI: 同步接口，一次只能处理一个请求
- ASGI: 异步接口，可以同时处理多个请求，支持WebSocket、HTTP/2等

ASGI的优势：
1. 支持异步处理，性能更好
2. 支持WebSocket连接（实时通信）
3. 支持HTTP/2服务器推送
4. 支持长时间运行的连接

使用场景：
- 需要WebSocket功能（如实时聊天、实时通知）
- 需要处理大量并发连接
- 需要异步I/O操作（如异步数据库查询）

常用ASGI服务器：
- Uvicorn: 基于uvloop的快速ASGI服务器
- Daphne: Django Channels推荐的ASGI服务器
- Hypercorn: 支持HTTP/2的ASGI服务器

使用示例（Uvicorn）：
    uvicorn chatApp.asgi:application

注意：
- 如果项目不需要异步功能或WebSocket，使用WSGI即可
- ASGI服务器通常比WSGI服务器消耗更多资源
- Django Channels（WebSocket框架）需要ASGI

更多信息：
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

# 导入os模块，用于设置环境变量
import os

# 导入Django的ASGI应用获取函数
from django.core.asgi import get_asgi_application

# 设置Django设置模块的环境变量
# 必须在导入Django之前设置，告诉Django使用哪个设置文件
# 'chatApp.settings' 指向 chatApp/settings.py 文件
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chatApp.settings')

# ASGI应用对象
# 这是ASGI服务器调用的入口点
# get_asgi_application() 返回一个ASGI兼容的应用对象
# 这个对象接收scope（连接信息）、receive（接收消息）、send（发送消息）作为参数
# ASGI服务器会调用这个对象来处理HTTP请求和WebSocket连接
application = get_asgi_application()
