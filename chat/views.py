"""
聊天应用视图模块

该模块提供聊天功能的视图函数，包括：
1. 聊天界面视图
2. 发送消息API
3. 会话管理视图
4. 消息历史查看

功能说明：
- 支持单次问答模式：每次消息独立处理，不保留历史
- 支持多轮对话模式：保留对话历史，支持上下文理解
- 支持切换对话模式
"""

import json
import logging
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.csrf import ensure_csrf_cookie
from .models import Conversation, Message
from utils.api_client import get_api_client, send_chat_message
from config.api_config import MODELS

logger = logging.getLogger(__name__)


@ensure_csrf_cookie
def chat_index(request):
    """
    聊天主界面视图
    
    显示聊天界面，支持创建新会话或继续已有会话。
    
    Args:
        request: Django HTTP请求对象
        
    Returns:
        HttpResponse: 聊天界面页面
    """
    # 获取或创建默认会话
    conversation_id = request.GET.get('conversation_id')
    
    if conversation_id:
        conversation = get_object_or_404(Conversation, id=conversation_id)
    else:
        # 创建新会话
        conversation = Conversation.objects.create(
            title=None,
            mode='multi'  # 默认多轮对话
        )
    
    # 获取消息历史
    messages = conversation.messages.all().order_by('created_at')
    
    context = {
        'conversation': conversation,
        'messages': messages,
        'available_models': MODELS['chat']
    }
    
    return render(request, 'chat/index.html', context)


@require_http_methods(["POST"])
def send_message(request, conversation_id):
    """
    发送消息API
    
    处理用户发送的消息，调用AI API获取回复。
    支持单次和多轮两种模式。
    
    处理流程：
    1. 接收用户消息
    2. 根据会话模式构建消息历史
    3. 调用API获取AI回复
    4. 保存用户消息和AI回复到数据库
    
    Args:
        request: Django HTTP请求对象
        conversation_id: 会话ID
        
    Returns:
        JsonResponse: 包含AI回复的JSON响应
    """
    conversation = get_object_or_404(Conversation, id=conversation_id)
    
    try:
        # 解析请求数据
        data = json.loads(request.body)
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return JsonResponse({'error': '消息内容不能为空'}, status=400)
        
        # 保存用户消息
        user_msg = Message.objects.create(
            conversation=conversation,
            role='user',
            content=user_message
        )
        
        # 构建消息历史（用于多轮对话）
        conversation_history = []
        if conversation.mode == 'multi':
            # 多轮模式：获取历史消息
            history_messages = conversation.messages.filter(
                id__lt=user_msg.id
            ).order_by('created_at')
            
            for msg in history_messages:
                conversation_history.append({
                    'role': msg.role,
                    'content': msg.content
                })
        
        # 调用API获取回复
        api_client = get_api_client()
        
        response = send_chat_message(
            client=api_client,
            message=user_message,
            conversation_history=conversation_history,
            model=conversation.model_used,
            single_turn=(conversation.mode == 'single')
        )
        
        # 保存AI回复
        assistant_msg = Message.objects.create(
            conversation=conversation,
            role='assistant',
            content=response['content'],
            prompt_tokens=response['usage']['prompt_tokens'],
            completion_tokens=response['usage']['completion_tokens'],
            total_tokens=response['usage']['total_tokens']
        )
        
        # 更新会话时间戳
        conversation.save()
        
        logger.info(f"消息发送成功: 会话{conversation_id}, Token: {response['usage']['total_tokens']}")
        
        return JsonResponse({
            'success': True,
            'message': {
                'id': assistant_msg.id,
                'role': assistant_msg.role,
                'content': assistant_msg.content,
                'created_at': assistant_msg.created_at.isoformat(),
                'usage': {
                    'prompt_tokens': assistant_msg.prompt_tokens,
                    'completion_tokens': assistant_msg.completion_tokens,
                    'total_tokens': assistant_msg.total_tokens
                }
            }
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': '无效的JSON数据'}, status=400)
    except Exception as e:
        logger.error(f"发送消息失败: {e}")
        return JsonResponse({'error': f'处理失败: {str(e)}'}, status=500)


@require_http_methods(["POST"])
def create_conversation(request):
    """
    创建新会话API
    
    创建一个新的对话会话。
    
    Args:
        request: Django HTTP请求对象
        
    Returns:
        JsonResponse: 包含新会话信息的JSON响应
    """
    try:
        data = json.loads(request.body)
        title = data.get('title', '').strip()
        mode = data.get('mode', 'multi')
        model = data.get('model', MODELS['chat']['default'])
        
        # 验证模式
        if mode not in [choice[0] for choice in Conversation.MODE_CHOICES]:
            mode = 'multi'
        
        # 创建会话
        conversation = Conversation.objects.create(
            title=title or None,
            mode=mode,
            model_used=model
        )
        
        return JsonResponse({
            'success': True,
            'conversation': {
                'id': conversation.id,
                'title': conversation.title,
                'mode': conversation.mode,
                'model_used': conversation.model_used,
                'created_at': conversation.created_at.isoformat()
            }
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': '无效的JSON数据'}, status=400)
    except Exception as e:
        logger.error(f"创建会话失败: {e}")
        return JsonResponse({'error': f'创建失败: {str(e)}'}, status=500)


@require_http_methods(["POST"])
def update_conversation(request, conversation_id):
    """
    更新会话信息API
    
    更新会话的标题、模式或模型。
    
    Args:
        request: Django HTTP请求对象
        conversation_id: 会话ID
        
    Returns:
        JsonResponse: 更新结果
    """
    conversation = get_object_or_404(Conversation, id=conversation_id)
    
    try:
        data = json.loads(request.body)
        
        if 'title' in data:
            conversation.title = data['title'].strip() or None
        
        if 'mode' in data:
            mode = data['mode']
            if mode in [choice[0] for choice in Conversation.MODE_CHOICES]:
                conversation.mode = mode
        
        if 'model' in data:
            conversation.model_used = data['model']
        
        conversation.save()
        
        return JsonResponse({
            'success': True,
            'conversation': {
                'id': conversation.id,
                'title': conversation.title,
                'mode': conversation.mode,
                'model_used': conversation.model_used
            }
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': '无效的JSON数据'}, status=400)
    except Exception as e:
        logger.error(f"更新会话失败: {e}")
        return JsonResponse({'error': f'更新失败: {str(e)}'}, status=500)


def conversation_list(request):
    """
    会话列表视图
    
    显示所有对话会话的列表。
    
    Args:
        request: Django HTTP请求对象
        
    Returns:
        HttpResponse: 会话列表页面
    """
    conversations = Conversation.objects.all().order_by('-updated_at')
    
    context = {
        'conversations': conversations
    }
    
    return render(request, 'chat/list.html', context)


@require_http_methods(["GET"])
def get_messages(request, conversation_id):
    """
    获取消息历史API
    
    获取指定会话的所有消息。
    
    Args:
        request: Django HTTP请求对象
        conversation_id: 会话ID
        
    Returns:
        JsonResponse: 包含消息列表的JSON响应
    """
    conversation = get_object_or_404(Conversation, id=conversation_id)
    
    messages = conversation.messages.all().order_by('created_at')
    
    messages_data = []
    for msg in messages:
        messages_data.append({
            'id': msg.id,
            'role': msg.role,
            'content': msg.content,
            'created_at': msg.created_at.isoformat(),
            'usage': {
                'prompt_tokens': msg.prompt_tokens,
                'completion_tokens': msg.completion_tokens,
                'total_tokens': msg.total_tokens
            } if msg.total_tokens else None
        })
    
    return JsonResponse({
        'success': True,
        'messages': messages_data,
        'conversation': {
            'id': conversation.id,
            'title': conversation.title,
            'mode': conversation.mode,
            'model_used': conversation.model_used
        }
    })
