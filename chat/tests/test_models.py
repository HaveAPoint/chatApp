"""
聊天模型单元测试

测试覆盖：
1. Conversation模型的基本功能
2. Message模型的基本功能
3. 模型之间的关系
4. 模型方法

运行测试：
    python manage.py test chat.tests.test_models
"""

from django.test import TestCase
from django.contrib.auth.models import User
from chat.models import Conversation, Message


class ConversationModelTestCase(TestCase):
    """Conversation模型测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
    
    def test_conversation_creation(self):
        """
        测试对话会话创建
        
        验证：
        - 可以成功创建Conversation实例
        - 默认模式为'multi'
        - 时间戳自动设置
        """
        conversation = Conversation.objects.create(
            title="测试会话",
            mode='multi',
            user=self.user
        )
        
        self.assertEqual(conversation.title, "测试会话")
        self.assertEqual(conversation.mode, 'multi')
        self.assertEqual(conversation.user, self.user)
        self.assertIsNotNone(conversation.created_at)
        self.assertIsNotNone(conversation.updated_at)
    
    def test_conversation_str(self):
        """测试模型的字符串表示"""
        conversation = Conversation.objects.create(
            title="测试会话",
            mode='single'
        )
        
        expected_str = "测试会话 (单次问答)"
        self.assertEqual(str(conversation), expected_str)
    
    def test_conversation_without_title(self):
        """测试无标题的会话"""
        conversation = Conversation.objects.create(mode='multi')
        
        str_repr = str(conversation)
        self.assertIn("会话", str_repr)
        self.assertIn(str(conversation.id), str_repr)
    
    def test_get_message_count(self):
        """测试获取消息数量方法"""
        conversation = Conversation.objects.create(title="测试会话")
        
        # 创建几条消息
        Message.objects.create(
            conversation=conversation,
            role='user',
            content="你好"
        )
        Message.objects.create(
            conversation=conversation,
            role='assistant',
            content="你好！"
        )
        
        self.assertEqual(conversation.get_message_count(), 2)
    
    def test_get_last_message(self):
        """测试获取最后一条消息方法"""
        conversation = Conversation.objects.create(title="测试会话")
        
        msg1 = Message.objects.create(
            conversation=conversation,
            role='user',
            content="第一条"
        )
        msg2 = Message.objects.create(
            conversation=conversation,
            role='assistant',
            content="第二条"
        )
        
        last_msg = conversation.get_last_message()
        self.assertEqual(last_msg, msg2)
    
    def test_mode_choices(self):
        """测试模式选择"""
        conversation = Conversation.objects.create(mode='single')
        self.assertEqual(conversation.mode, 'single')
        self.assertIn(conversation.mode, [choice[0] for choice in Conversation.MODE_CHOICES])


class MessageModelTestCase(TestCase):
    """Message模型测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.conversation = Conversation.objects.create(
            title="测试会话",
            mode='multi'
        )
    
    def test_message_creation(self):
        """
        测试消息创建
        
        验证：
        - 可以成功创建Message实例
        - 与Conversation的外键关系正确
        - 角色和内容正确设置
        """
        message = Message.objects.create(
            conversation=self.conversation,
            role='user',
            content="测试消息内容",
            prompt_tokens=10,
            completion_tokens=20,
            total_tokens=30
        )
        
        self.assertEqual(message.conversation, self.conversation)
        self.assertEqual(message.role, 'user')
        self.assertEqual(message.content, "测试消息内容")
        self.assertEqual(message.prompt_tokens, 10)
        self.assertEqual(message.completion_tokens, 20)
        self.assertEqual(message.total_tokens, 30)
        self.assertIsNotNone(message.created_at)
    
    def test_message_str(self):
        """测试模型的字符串表示"""
        message = Message.objects.create(
            conversation=self.conversation,
            role='user',
            content="这是一段很长的消息内容，用于测试字符串截断功能"
        )
        
        str_repr = str(message)
        self.assertIn("用户", str_repr)
        self.assertIn("...", str_repr)  # 验证截断
    
    def test_is_user_message(self):
        """测试判断用户消息方法"""
        user_msg = Message.objects.create(
            conversation=self.conversation,
            role='user',
            content="用户消息"
        )
        assistant_msg = Message.objects.create(
            conversation=self.conversation,
            role='assistant',
            content="AI回复"
        )
        
        self.assertTrue(user_msg.is_user_message())
        self.assertFalse(assistant_msg.is_user_message())
    
    def test_is_assistant_message(self):
        """测试判断AI回复方法"""
        user_msg = Message.objects.create(
            conversation=self.conversation,
            role='user',
            content="用户消息"
        )
        assistant_msg = Message.objects.create(
            conversation=self.conversation,
            role='assistant',
            content="AI回复"
        )
        
        self.assertFalse(user_msg.is_assistant_message())
        self.assertTrue(assistant_msg.is_assistant_message())
    
    def test_message_conversation_relationship(self):
        """测试消息与会话的关系"""
        msg1 = Message.objects.create(
            conversation=self.conversation,
            role='user',
            content="消息1"
        )
        msg2 = Message.objects.create(
            conversation=self.conversation,
            role='assistant',
            content="消息2"
        )
        
        # 测试反向关系
        messages = self.conversation.messages.all()
        self.assertEqual(messages.count(), 2)
        self.assertIn(msg1, messages)
        self.assertIn(msg2, messages)
    
    def test_message_ordering(self):
        """测试消息排序"""
        msg1 = Message.objects.create(
            conversation=self.conversation,
            role='user',
            content="第一条"
        )
        msg2 = Message.objects.create(
            conversation=self.conversation,
            role='assistant',
            content="第二条"
        )
        
        messages = list(self.conversation.messages.all())
        self.assertEqual(messages[0], msg1)
        self.assertEqual(messages[1], msg2)


