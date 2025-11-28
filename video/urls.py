"""
视频OCR应用URL配置

定义视频处理相关的URL路由：
- /video/upload/ - 视频上传页面
- /video/list/ - 视频列表页面
- /video/<id>/process/ - 视频处理页面
- /video/<id>/result/ - 处理结果页面
- /video/api/<id>/status/ - 处理状态API
"""

from django.urls import path
from . import views

app_name = 'video'

urlpatterns = [
    path('upload/', views.video_upload, name='upload'),
    path('list/', views.video_list, name='list'),
    path('<int:video_id>/process/', views.video_process, name='process'),
    path('<int:video_id>/result/', views.video_result, name='result'),
    path('api/<int:video_id>/status/', views.video_status_api, name='status_api'),
]


