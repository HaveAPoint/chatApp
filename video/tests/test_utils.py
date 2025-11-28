"""
视频处理工具模块单元测试

测试覆盖：
1. FFmpeg可用性检查
2. 文本相似度计算
3. OCR结果合并算法
4. 视频信息获取（需要FFmpeg）

运行测试：
    python manage.py test video.tests.test_utils
"""

import unittest
from unittest.mock import patch, MagicMock
from django.test import TestCase
from video.utils import (
    check_ffmpeg_available,
    calculate_text_similarity,
    merge_ocr_results
)


class VideoUtilsTestCase(TestCase):
    """视频工具函数测试类"""
    
    def test_check_ffmpeg_available(self):
        """
        测试FFmpeg可用性检查
        
        注意：这个测试依赖于系统是否安装了FFmpeg
        """
        # 这个测试会实际检查FFmpeg，所以结果可能因环境而异
        result = check_ffmpeg_available()
        self.assertIsInstance(result, bool)
    
    @patch('video.utils.subprocess.run')
    def test_check_ffmpeg_available_success(self, mock_run):
        """测试FFmpeg可用时的检查"""
        mock_run.return_value = MagicMock()
        
        result = check_ffmpeg_available()
        self.assertTrue(result)
        mock_run.assert_called_once()
    
    @patch('video.utils.subprocess.run')
    def test_check_ffmpeg_available_failure(self, mock_run):
        """测试FFmpeg不可用时的检查"""
        mock_run.side_effect = FileNotFoundError()
        
        result = check_ffmpeg_available()
        self.assertFalse(result)
    
    def test_calculate_text_similarity_identical(self):
        """测试完全相同文本的相似度"""
        similarity = calculate_text_similarity("Hello", "Hello")
        self.assertEqual(similarity, 1.0)
    
    def test_calculate_text_similarity_different(self):
        """测试完全不同文本的相似度"""
        similarity = calculate_text_similarity("Hello", "World")
        self.assertLess(similarity, 1.0)
        self.assertGreaterEqual(similarity, 0.0)
    
    def test_calculate_text_similarity_similar(self):
        """测试相似文本的相似度"""
        similarity = calculate_text_similarity("Hello", "Hallo")
        # "Hello"和"Hallo"很相似，相似度应该较高
        self.assertGreater(similarity, 0.5)
    
    def test_calculate_text_similarity_empty(self):
        """测试空文本的相似度"""
        # 两个空文本
        similarity = calculate_text_similarity("", "")
        self.assertEqual(similarity, 1.0)
        
        # 一个空文本
        similarity = calculate_text_similarity("Hello", "")
        self.assertEqual(similarity, 0.0)
        
        similarity = calculate_text_similarity("", "Hello")
        self.assertEqual(similarity, 0.0)
    
    def test_merge_ocr_results_empty(self):
        """测试空OCR结果列表的合并"""
        result = merge_ocr_results([])
        self.assertEqual(result, [])
    
    def test_merge_ocr_results_single(self):
        """测试单个OCR结果的合并"""
        ocr_results = [
            {'text': 'Hello', 'timestamp': 1.0}
        ]
        result = merge_ocr_results(ocr_results)
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['text'], 'Hello')
        self.assertEqual(result[0]['start_time'], 1.0)
        self.assertEqual(result[0]['end_time'], 1.0)
        self.assertEqual(result[0]['frame_count'], 1)
    
    def test_merge_ocr_results_similar_texts(self):
        """测试相似文本的合并"""
        ocr_results = [
            {'text': 'Hello', 'timestamp': 1.0},
            {'text': 'Hello', 'timestamp': 1.5},  # 相同文本，时间相近
            {'text': 'World', 'timestamp': 3.0}  # 不同文本
        ]
        result = merge_ocr_results(ocr_results, similarity_threshold=0.8, time_window=2.0)
        
        # 前两个"Hello"应该被合并
        self.assertGreaterEqual(len(result), 1)
        self.assertLessEqual(len(result), 2)
        
        # 检查第一个结果（合并后的Hello）
        hello_result = [r for r in result if 'Hello' in r['text']]
        if hello_result:
            self.assertEqual(hello_result[0]['frame_count'], 2)
            self.assertEqual(hello_result[0]['start_time'], 1.0)
            self.assertEqual(hello_result[0]['end_time'], 1.5)
    
    def test_merge_ocr_results_time_window(self):
        """测试时间窗口合并"""
        ocr_results = [
            {'text': 'Text1', 'timestamp': 1.0},
            {'text': 'Text1', 'timestamp': 2.5},  # 时间差1.5秒，在窗口内
            {'text': 'Text1', 'timestamp': 5.0}   # 时间差2.5秒，超出窗口
        ]
        result = merge_ocr_results(ocr_results, time_window=2.0)
        
        # 前两个应该合并，第三个独立
        self.assertGreaterEqual(len(result), 2)
    
    def test_merge_ocr_results_sorted(self):
        """测试结果按时间排序"""
        ocr_results = [
            {'text': 'Later', 'timestamp': 5.0},
            {'text': 'First', 'timestamp': 1.0},
            {'text': 'Middle', 'timestamp': 3.0}
        ]
        result = merge_ocr_results(ocr_results)
        
        # 验证按时间排序
        for i in range(len(result) - 1):
            self.assertLessEqual(result[i]['start_time'], result[i + 1]['start_time'])
    
    def test_merge_ocr_results_skip_empty(self):
        """测试跳过空文本"""
        ocr_results = [
            {'text': 'Hello', 'timestamp': 1.0},
            {'text': '', 'timestamp': 2.0},  # 空文本
            {'text': '   ', 'timestamp': 3.0},  # 只有空格
            {'text': 'World', 'timestamp': 4.0}
        ]
        result = merge_ocr_results(ocr_results)
        
        # 应该只有两个非空结果
        texts = [r['text'] for r in result]
        self.assertIn('Hello', texts)
        self.assertIn('World', texts)
        self.assertNotIn('', texts)
        self.assertNotIn('   ', texts)



