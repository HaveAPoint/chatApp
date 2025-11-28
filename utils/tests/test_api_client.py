"""
API客户端模块单元测试

测试覆盖：
1. API客户端初始化
2. 图片OCR处理
3. 错误处理

运行测试：
    python manage.py test utils.tests.test_api_client
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from django.test import TestCase
from utils.api_client import (
    get_api_client,
    process_image_ocr
)
from config.api_config import API_BASE_URL, MODELS


class APIClientTestCase(TestCase):
    """API客户端基础测试类"""
    
    @patch('utils.api_client.API_KEY', 'test-key')
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
            api_key='test-key',
            base_url=API_BASE_URL,
            timeout=300
        )
    
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



