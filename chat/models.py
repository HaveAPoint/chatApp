"""
聊天应用模型

该模块定义了聊天功能相关的数据模型：
- Conversation: 存储对话会话信息
- Message: 存储单条消息记录

模型关系：
Conversation (1) -> (N) Message

功能说明：
- 支持单次问答模式：每次对话独立，不保留历史
- 支持多轮对话模式：保留对话历史，支持上下文理解
"""

from django.db import models
from django.contrib.auth.models import User


class Conversation(models.Model):
    """
    对话会话模型
    
    存储一个对话会话的基本信息，包括：
    - 会话标题（可选）
    - 对话模式（单次/多轮）
    - 创建和更新时间
    
    模式说明：
    - 'single': 单次问答模式，每次消息独立处理
    - 'multi': 多轮对话模式，保留历史上下文
    """
    
    # 模式选择
    MODE_CHOICES = [
        ('single', '单次问答'),
        ('multi', '多轮对话'),
    ]
    
    # 基本信息
    title = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        verbose_name='会话标题',
        help_text='对话会话的标题（可选）'
    )
    
    # 对话模式
    mode = models.CharField(
        max_length=10,
        choices=MODE_CHOICES,
        default='multi',
        verbose_name='对话模式',
        help_text='单次问答：每次独立；多轮对话：保留历史'
    )
    
    # 用户关联（可选，如果不需要用户系统可以移除）
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='conversations',
        verbose_name='用户',
        help_text='创建该会话的用户（可选）'
    )
    
    # 使用的模型
    model_used = models.CharField(
        max_length=100,
        default='gemini-3-pro-preview',
        verbose_name='使用的模型',
        help_text='该会话使用的AI模型名称'
    )
    
    # 时间戳
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='创建时间',
        help_text='会话创建的时间'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='更新时间',
        help_text='最后更新的时间'
    )
    
    class Meta:
        verbose_name = '对话会话'
        verbose_name_plural = '对话会话'
        ordering = ['-updated_at']  # 按更新时间倒序排列
        indexes = [
            models.Index(fields=['user', 'updated_at']),  # 用户和时间索引
            models.Index(fields=['mode']),  # 模式索引
        ]
    
    def __str__(self):
        """返回模型的字符串表示"""
        title = self.title or f"会话 {self.id}"
        return f"{title} ({self.get_mode_display()})"
    
    def get_message_count(self):
        """获取该会话的消息数量"""
        return self.messages.count()
    
    def get_last_message(self):
        """获取最后一条消息"""
        return self.messages.order_by('-created_at').first()


class Message(models.Model):
    """
    消息模型
    
    存储对话中的单条消息，包括：
    - 消息角色（用户/AI）
    - 消息内容
    - 时间戳
    - API使用统计
    
    角色说明：
    - 'user': 用户发送的消息
    - 'assistant': AI回复的消息
    - 'system': 系统消息（可选）
    """
    
    # 角色选择
    ROLE_CHOICES = [
        ('user', '用户'),
        ('assistant', '助手'),
        ('system', '系统'),
    ]
    
    # 关联会话
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name='messages',
        verbose_name='所属会话',
        help_text='该消息所属的对话会话'
    )
    
    # 消息内容
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        verbose_name='消息角色',
        help_text='消息的发送者角色'
    )
    content = models.TextField(
        verbose_name='消息内容',
        help_text='消息的文本内容'
    )
    
    # API使用统计
    prompt_tokens = models.IntegerField(
        null=True,
        blank=True,
        verbose_name='提示词Token数',
        help_text='本次请求消耗的提示词Token数量'
    )
    completion_tokens = models.IntegerField(
        null=True,
        blank=True,
        verbose_name='完成Token数',
        help_text='本次响应消耗的完成Token数量'
    )
    total_tokens = models.IntegerField(
        null=True,
        blank=True,
        verbose_name='总Token数',
        help_text='本次请求消耗的总Token数量'
    )
    
    # 时间戳
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='创建时间',
        help_text='消息创建的时间'
    )
    
    class Meta:
        verbose_name = '消息'
        verbose_name_plural = '消息'
        ordering = ['conversation', 'created_at']  # 按会话和时间排序
        indexes = [
            models.Index(fields=['conversation', 'created_at']),  # 会话和时间索引
            models.Index(fields=['role']),  # 角色索引
        ]
    
    def __str__(self):
        """返回模型的字符串表示"""
        content_preview = self.content[:50] + "..." if len(self.content) > 50 else self.content
        return f"{self.get_role_display()}: {content_preview}"
    
    def is_user_message(self):
        """判断是否为用户消息"""
        return self.role == 'user'
    
    def is_assistant_message(self):
        """判断是否为AI回复"""
        return self.role == 'assistant'
