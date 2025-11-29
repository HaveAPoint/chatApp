"""
WSGI配置文件（wsgi.py）

WSGI（Web Server Gateway Interface）是Python Web应用与Web服务器之间的标准接口。
这个文件定义了WSGI应用对象，用于在生产环境中部署Django项目。

WSGI的作用：
1. 提供Web服务器（如Nginx、Apache）与Django应用之间的桥梁
2. 将HTTP请求转换为Python对象，将响应转换为HTTP响应
3. 允许多个Web服务器使用同一个Django应用

部署流程：
1. Web服务器（如Nginx）接收HTTP请求
2. 通过WSGI服务器（如Gunicorn、uWSGI）调用WSGI应用
3. WSGI应用（本文件中的application）处理请求
4. 返回响应给Web服务器，最终返回给客户端

常用WSGI服务器：
- Gunicorn: 简单易用，适合大多数项目
- uWSGI: 功能强大，性能优秀
- mod_wsgi: Apache模块

使用示例（Gunicorn）：
    gunicorn chatApp.wsgi:application

注意：
- 开发环境（python manage.py runserver）不使用WSGI
- 生产环境必须使用WSGI服务器，不能直接运行Django
- 这个文件通常不需要修改

更多信息：
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

# 导入os模块，用于设置环境变量
import os

# 导入Django的WSGI应用获取函数
from django.core.wsgi import get_wsgi_application

# 设置Django设置模块的环境变量
# 必须在导入Django之前设置，告诉Django使用哪个设置文件
# 'chatApp.settings' 指向 chatApp/settings.py 文件
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chatApp.settings')

# WSGI应用对象
# 这是Web服务器调用的入口点
# get_wsgi_application() 返回一个WSGI兼容的应用对象
# 这个对象接收environ（环境变量）和start_response（响应函数）作为参数
# Web服务器会调用这个对象来处理HTTP请求
application = get_wsgi_application()
