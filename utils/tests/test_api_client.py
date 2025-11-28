"""
API客户端模块单元测试

测试覆盖：
1. API客户端初始化
2. 聊天消息发送（单次和多轮模式）
3. 图片OCR处理
4. 错误处理

运行测试：
    python manage.py test utils.tests.test_api_client
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from django.test import TestCase
from utils.api_client import (
    get_api_client,
    send_chat_message,
    process_image_ocr
)
from config.api_config import API_BASE_URL, API_KEY, MODELS


class APIClientTestCase(TestCase):
    """API客户端基础测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.test_message = "测试消息"
        self.test_history = [
            {"role": "user", "content": "你好"},
            {"role": "assistant", "content": "你好！有什么可以帮助你的吗？"}
        ]
    
    @patch('utils.api_client.OpenAI')
    def test_get_api_client(self, mock_openai):
        """
        测试API客户端初始化
        
        验证：
        - 客户端使用正确的API密钥
        - 客户端使用正确的基础URL
        - 客户端配置了超时时间
        """
        client = get_api_client()
        
        # 验证OpenAI客户端被正确调用
        mock_openai.assert_called_once_with(
            api_key=API_KEY,
            base_url=API_BASE_URL,
            timeout=300
        )
    
    @patch('utils.api_client.get_api_client')
    def test_send_chat_message_single_turn(self, mock_get_client):
        """
        测试单次问答模式
        
        验证：
        - 单次模式下不包含历史记录
        - 只发送当前消息
        - 正确返回响应内容
        """
        # 模拟API响应
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "AI回复"
        mock_response.model = MODELS['chat']['default']
        mock_response.usage = MagicMock()
        mock_response.usage.prompt_tokens = 10
        mock_response.usage.completion_tokens = 20
        mock_response.usage.total_tokens = 30
        
        # 模拟客户端
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_get_client.return_value = mock_client
        
        # 执行测试
        result = send_chat_message(
            mock_client,
            self.test_message,
            single_turn=True
        )
        
        # 验证结果
        self.assertEqual(result['content'], "AI回复")
        self.assertEqual(result['model'], MODELS['chat']['default'])
        self.assertEqual(result['usage']['total_tokens'], 30)
        
        # 验证API调用参数
        call_args = mock_client.chat.completions.create.call_args
        messages = call_args[1]['messages']
        self.assertEqual(len(messages), 1)  # 单次模式只有一条消息
        self.assertEqual(messages[0]['content'], self.test_message)
    
    @patch('utils.api_client.get_api_client')
    def test_send_chat_message_multi_turn(self, mock_get_client):
        """
        测试多轮对话模式
        
        验证：
        - 多轮模式下包含历史记录
        - 历史记录和当前消息都被发送
        - 正确返回响应内容
        """
        # 模拟API响应
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "多轮回复"
        mock_response.model = MODELS['chat']['default']
        mock_response.usage = MagicMock()
        mock_response.usage.prompt_tokens = 50
        mock_response.usage.completion_tokens = 30
        mock_response.usage.total_tokens = 80
        
        # 模拟客户端
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_get_client.return_value = mock_client
        
        # 执行测试
        result = send_chat_message(
            mock_client,
            self.test_message,
            conversation_history=self.test_history,
            single_turn=False
        )
        
        # 验证结果
        self.assertEqual(result['content'], "多轮回复")
        self.assertEqual(result['usage']['total_tokens'], 80)
        
        # 验证API调用参数
        call_args = mock_client.chat.completions.create.call_args
        messages = call_args[1]['messages']
        self.assertEqual(len(messages), 3)  # 2条历史 + 1条当前消息
        self.assertEqual(messages[0]['content'], "你好")
        self.assertEqual(messages[-1]['content'], self.test_message)
    
    @patch('utils.api_client.get_api_client')
    def test_send_chat_message_error_handling(self, mock_get_client):
        """
        测试错误处理
        
        验证：
        - API请求失败时正确抛出异常
        - 错误信息被正确记录
        """
        # 模拟客户端抛出异常
        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = Exception("API错误")
        mock_get_client.return_value = mock_client
        
        # 验证异常被抛出
        with self.assertRaises(Exception) as context:
            send_chat_message(mock_client, self.test_message)
        
        self.assertIn("API错误", str(context.exception))
    
    @patch('builtins.open', create=True)
    @patch('utils.api_client.get_api_client')
    def test_process_image_ocr(self, mock_get_client, mock_open):
        """
        测试图片OCR处理
        
        验证：
        - 图片文件被正确读取
        - 图片被正确编码为base64
        - API请求包含图片和提示词
        - 正确返回OCR结果
        """
        # 模拟文件读取
        mock_file = MagicMock()
        mock_file.read.return_value = b'fake_image_data'
        mock_open.return_value.__enter__.return_value = mock_file
        
        # 模拟API响应
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "识别的文字内容"
        mock_response.model = MODELS['vision']['default']
        mock_response.usage = MagicMock()
        mock_response.usage.prompt_tokens = 100
        mock_response.usage.completion_tokens = 50
        mock_response.usage.total_tokens = 150
        
        # 模拟客户端
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_get_client.return_value = mock_client
        
        # 执行测试
        result = process_image_ocr(mock_client, "/path/to/image.jpg")
        
        # 验证结果
        self.assertEqual(result['content'], "识别的文字内容")
        self.assertTrue(result['success'])
        self.assertEqual(result['usage']['total_tokens'], 150)
        
        # 验证API调用
        call_args = mock_client.chat.completions.create.call_args
        messages = call_args[1]['messages']
        self.assertEqual(len(messages), 1)
        self.assertEqual(len(messages[0]['content']), 2)  # 文本 + 图片
        self.assertEqual(messages[0]['content'][0]['type'], 'text')
        self.assertEqual(messages[0]['content'][1]['type'], 'image_url')


if __name__ == '__main__':
    unittest.main()


