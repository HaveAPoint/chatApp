"""
聊天应用URL配置

定义聊天功能相关的URL路由：
- /chat/ - 聊天主界面
- /chat/list/ - 会话列表
- /chat/<id>/ - 指定会话的聊天界面
- /chat/api/<id>/send/ - 发送消息API
- /chat/api/<id>/messages/ - 获取消息历史API
- /chat/api/create/ - 创建新会话API
- /chat/api/<id>/update/ - 更新会话API
"""

from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('', views.chat_index, name='index'),
    path('list/', views.conversation_list, name='list'),
    path('<int:conversation_id>/', views.chat_index, name='conversation'),
    path('api/<int:conversation_id>/send/', views.send_message, name='send_message'),
    path('api/<int:conversation_id>/messages/', views.get_messages, name='get_messages'),
    path('api/create/', views.create_conversation, name='create_conversation'),
    path('api/<int:conversation_id>/update/', views.update_conversation, name='update_conversation'),
]


