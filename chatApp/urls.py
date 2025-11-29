"""
Django项目根URL配置文件（urls.py）

这个文件是Django项目的URL路由入口，定义了URL与视图函数之间的映射关系。
当用户访问网站时，Django会根据URL在这里查找对应的视图函数并执行。

URL路由工作原理：
1. 用户访问URL（如：http://example.com/video/upload/）
2. Django从ROOT_URLCONF（settings.py中定义）开始匹配
3. 按顺序检查urlpatterns中的每个path()规则
4. 找到匹配的规则后，调用对应的视图函数
5. 视图函数处理请求并返回响应

重要概念：
- urlpatterns: URL模式列表，Django按顺序匹配
- path(): 定义URL路由规则
- include(): 包含其他应用的URL配置（URL分发）
- name: URL的命名，用于在模板和代码中反向解析URL

学习要点：
- URL匹配是从上到下的，第一个匹配的规则会被使用
- 可以使用正则表达式（re_path）进行更复杂的匹配
- URL命名空间可以避免不同应用之间的URL名称冲突

更多信息：
https://docs.djangoproject.com/en/4.2/topics/http/urls/
"""

# 导入Django URL路由相关的模块
from django.contrib import admin  # Django管理后台
from django.urls import path, include  # path用于定义URL路由，include用于包含其他URL配置
from django.views.generic import RedirectView  # 重定向视图，用于URL重定向
from django.conf import settings  # Django设置对象
from django.conf.urls.static import static  # 静态文件服务函数

# ============================================================================
# URL路由配置（URL Patterns）
# ============================================================================
# urlpatterns是Django URL路由的核心，定义了所有URL与视图的映射关系
# Django会按顺序从上到下匹配URL，找到第一个匹配的规则就停止

urlpatterns = [
    # Django管理后台URL
    # 访问 http://yourdomain.com/admin/ 可以进入Django管理后台
    # admin.site.urls 是Django自动生成的管理后台URL配置
    # 功能：提供Web界面管理数据库中的数据（需要超级用户权限）
    path('admin/', admin.site.urls),
    
    # 包含video应用的URL配置
    # include()函数用于将其他应用的URL配置包含进来（URL分发）
    # 'video/' 是URL前缀，所有video应用的URL都会以/video/开头
    # 'video.urls' 指向video应用的urls.py文件
    # 例如：video/urls.py中定义的'upload/'会变成 /video/upload/
    # 这样做的好处：
    #   1. 将不同应用的URL配置分离，便于管理
    #   2. 每个应用可以独立管理自己的URL
    #   3. 支持URL命名空间，避免URL名称冲突
    path('video/', include('video.urls')),
    
    # 根路径重定向
    # 当用户访问网站根路径（http://yourdomain.com/）时，自动重定向到视频列表页面
    # RedirectView.as_view(): 创建一个重定向视图
    # url='/video/list/': 重定向的目标URL
    # permanent=False: 临时重定向（HTTP 302），而不是永久重定向（HTTP 301）
    #   临时重定向：浏览器可能会继续访问原URL
    #   永久重定向：浏览器会记住新URL，以后直接访问新URL
    path('', RedirectView.as_view(url='/video/list/', permanent=False)),
]

# ============================================================================
# 开发环境静态文件和媒体文件服务
# ============================================================================
# 注意：以下配置仅在开发环境（DEBUG=True）下生效
# 生产环境应该使用Web服务器（如Nginx）来提供静态文件和媒体文件

if settings.DEBUG:
    # 开发环境下提供媒体文件服务
    # static()函数将URL路径映射到文件系统路径
    # settings.MEDIA_URL: URL前缀（如 'media/'）
    # settings.MEDIA_ROOT: 文件系统路径（如 /path/to/media/）
    # 作用：当访问 /media/videos/video.mp4 时，Django会从 media/videos/video.mp4 读取文件
    # 注意：生产环境必须配置Web服务器来提供媒体文件，不能依赖Django
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    
    # 开发环境下提供静态文件服务
    # settings.STATIC_URL: URL前缀（如 'static/'）
    # settings.STATIC_ROOT: 文件系统路径（如 /path/to/staticfiles/）
    # 作用：当访问 /static/css/style.css 时，Django会从 staticfiles/css/style.css 读取文件
    # 注意：
    #   - 开发环境Django会自动处理静态文件，不需要运行collectstatic
    #   - 生产环境必须运行 collectstatic 并配置Web服务器提供静态文件
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
