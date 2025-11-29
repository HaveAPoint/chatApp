"""
视频OCR应用URL配置文件（urls.py）

这个文件定义了video应用的所有URL路由规则。
URL路由将URL路径映射到对应的视图函数。

URL路由工作原理：
1. 用户在浏览器中访问URL（如：/video/upload/）
2. Django从根URL配置（chatApp/urls.py）开始匹配
3. 匹配到 'video/' 前缀后，会包含这个文件（include('video.urls')）
4. Django继续在这个文件中匹配剩余的URL部分
5. 找到匹配的规则后，调用对应的视图函数

URL路径说明：
- 这些路径是相对于根URL配置中的 'video/' 前缀的
- 例如：'upload/' 实际对应的完整URL是 /video/upload/
- 路径参数（如 <int:video_id>）会被传递给视图函数

URL命名和反向解析：
- name参数用于给URL命名，方便在代码和模板中反向生成URL
- 使用命名空间（app_name）可以避免不同应用之间的URL名称冲突
- 在模板中使用：{% url 'video:upload' %}
- 在代码中使用：reverse('video:upload')
"""

# 导入Django URL路由函数
from django.urls import path
# 导入当前应用的视图函数
# . 表示当前包（video应用）
from . import views

# ============================================================================
# URL命名空间（URL Namespace）
# ============================================================================
# app_name定义了应用的URL命名空间
# 作用：避免不同应用之间的URL名称冲突
# 
# 使用示例：
# - 在模板中：{% url 'video:upload' %} 生成 /video/upload/
# - 在代码中：reverse('video:upload') 生成 /video/upload/
# 
# 如果没有命名空间，两个应用都定义了name='upload'的URL会冲突
# 有了命名空间，可以使用 'video:upload' 和 'blog:upload' 区分
app_name = 'video'

# ============================================================================
# URL路由配置（URL Patterns）
# ============================================================================
# urlpatterns列表定义了所有URL路由规则
# Django按顺序从上到下匹配URL，找到第一个匹配的规则就停止

urlpatterns = [
    # 视频上传页面
    # URL: /video/upload/
    # 视图函数: views.video_upload
    # URL名称: 'upload'（完整名称：'video:upload'）
    # 说明：处理视频文件上传的页面
    path('upload/', views.video_upload, name='upload'),
    
    # 视频列表页面
    # URL: /video/list/
    # 视图函数: views.video_list
    # URL名称: 'list'（完整名称：'video:list'）
    # 说明：显示所有已上传视频的列表页面
    path('list/', views.video_list, name='list'),
    
    # 视频处理页面（带路径参数）
    # URL: /video/<video_id>/process/（例如：/video/1/process/）
    # 视图函数: views.video_process
    # URL名称: 'process'（完整名称：'video:process'）
    # 路径参数说明：
    #   <int:video_id>: 路径参数，必须是整数
    #   - int: 类型转换器，将URL中的字符串转换为整数
    #   - video_id: 参数名称，会作为关键字参数传递给视图函数
    #   例如：访问 /video/123/process/ 时，视图函数会收到 video_id=123
    # 支持的转换器：
    #   - str: 字符串（默认，可以省略）
    #   - int: 整数
    #   - slug: 字母、数字、连字符、下划线
    #   - uuid: UUID格式
    #   - path: 包含斜杠的字符串
    path('<int:video_id>/process/', views.video_process, name='process'),
    
    # 处理结果页面（带路径参数）
    # URL: /video/<video_id>/result/（例如：/video/1/result/）
    # 视图函数: views.video_result
    # URL名称: 'result'（完整名称：'video:result'）
    # 说明：显示视频OCR处理结果的页面
    path('<int:video_id>/result/', views.video_result, name='result'),
    
    # 处理状态API（带路径参数）
    # URL: /video/api/<video_id>/status/（例如：/video/api/1/status/）
    # 视图函数: views.video_status_api
    # URL名称: 'status_api'（完整名称：'video:status_api'）
    # 说明：返回JSON格式的视频处理状态，用于AJAX轮询
    # 注意：这是一个API端点，返回JSON而不是HTML页面
    path('api/<int:video_id>/status/', views.video_status_api, name='status_api'),
]

# ============================================================================
# URL反向解析示例
# ============================================================================
# 在视图函数中生成URL：
#   from django.urls import reverse
#   url = reverse('video:process', args=[video_id])
#   或使用关键字参数：
#   url = reverse('video:process', kwargs={'video_id': video_id})
#
# 在模板中生成URL：
#   {% url 'video:process' video_id %}
#   或使用关键字参数：
#   {% url 'video:process' video_id=video.id %}
#
# 重定向到URL：
#   from django.shortcuts import redirect
#   return redirect('video:process', video_id=video.id)





