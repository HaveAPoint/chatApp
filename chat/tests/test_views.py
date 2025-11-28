"""
聊天视图单元测试

测试覆盖：
1. 聊天主界面视图
2. 发送消息API
3. 创建会话API
4. 更新会话API
5. 获取消息API

运行测试：
    python manage.py test chat.tests.test_views
"""

from django.test import TestCase, Client
from django.urls import reverse
from chat.models import Conversation, Message
import json
from unittest.mock import patch, MagicMock


class ChatViewsTestCase(TestCase):
    """聊天视图测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.client = Client()
    
    def test_chat_index(self):
        """测试聊天主界面"""
        conversation = Conversation.objects.create(mode='multi')
        
        response = self.client.get(reverse('chat:index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'chat/index.html')
    
    def test_chat_index_with_conversation(self):
        """测试指定会话的聊天界面"""
        conversation = Conversation.objects.create(mode='multi')
        
        response = self.client.get(
            reverse('chat:conversation', args=[conversation.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, str(conversation.id))
    
    @patch('chat.views.get_api_client')
    @patch('chat.views.send_chat_message')
    def test_send_message(self, mock_send_message, mock_get_client):
        """测试发送消息API"""
        conversation = Conversation.objects.create(mode='multi')
        
        # 模拟API响应
        mock_send_message.return_value = {
            'content': 'AI回复',
            'usage': {
                'prompt_tokens': 10,
                'completion_tokens': 20,
                'total_tokens': 30
            }
        }
        
        response = self.client.post(
            reverse('chat:send_message', args=[conversation.id]),
            data=json.dumps({'message': '你好'}),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertEqual(data['message']['content'], 'AI回复')
        
        # 验证消息已保存
        self.assertEqual(Message.objects.count(), 2)  # 用户消息 + AI回复
    
    def test_send_message_empty(self):
        """测试发送空消息"""
        conversation = Conversation.objects.create(mode='multi')
        
        response = self.client.post(
            reverse('chat:send_message', args=[conversation.id]),
            data=json.dumps({'message': ''}),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertIn('error', data)
    
    def test_create_conversation(self):
        """测试创建会话API"""
        response = self.client.post(
            reverse('chat:create_conversation'),
            data=json.dumps({
                'title': '新会话',
                'mode': 'multi'
            }),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertEqual(data['conversation']['title'], '新会话')
        
        # 验证会话已创建
        conversation = Conversation.objects.get(id=data['conversation']['id'])
        self.assertEqual(conversation.title, '新会话')
    
    def test_update_conversation(self):
        """测试更新会话API"""
        conversation = Conversation.objects.create(mode='multi')
        
        response = self.client.post(
            reverse('chat:update_conversation', args=[conversation.id]),
            data=json.dumps({
                'title': '更新后的标题',
                'mode': 'single'
            }),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        
        # 验证会话已更新
        conversation.refresh_from_db()
        self.assertEqual(conversation.title, '更新后的标题')
        self.assertEqual(conversation.mode, 'single')
    
    def test_get_messages(self):
        """测试获取消息API"""
        conversation = Conversation.objects.create(mode='multi')
        
        Message.objects.create(
            conversation=conversation,
            role='user',
            content='用户消息'
        )
        Message.objects.create(
            conversation=conversation,
            role='assistant',
            content='AI回复'
        )
        
        response = self.client.get(
            reverse('chat:get_messages', args=[conversation.id])
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertEqual(len(data['messages']), 2)
    
    def test_conversation_list(self):
        """测试会话列表视图"""
        Conversation.objects.create(title='会话1', mode='multi')
        Conversation.objects.create(title='会话2', mode='single')
        
        response = self.client.get(reverse('chat:list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'chat/list.html')
        self.assertContains(response, '会话1')
        self.assertContains(response, '会话2')


