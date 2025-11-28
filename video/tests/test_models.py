"""
视频模型单元测试

测试覆盖：
1. VideoFile模型的基本功能
2. VideoFrame模型的基本功能
3. OCRResult模型的基本功能
4. 模型之间的关系
5. 模型方法（如格式化方法）

运行测试：
    python manage.py test video.tests.test_models
"""

from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from video.models import VideoFile, VideoFrame, OCRResult
import os
import tempfile


class VideoFileModelTestCase(TestCase):
    """VideoFile模型测试类"""
    
    def setUp(self):
        """测试前准备"""
        # 创建一个临时视频文件用于测试
        self.test_video_content = b'fake video content'
        self.test_video = SimpleUploadedFile(
            "test_video.mp4",
            self.test_video_content,
            content_type="video/mp4"
        )
    
    def test_video_file_creation(self):
        """
        测试视频文件创建
        
        验证：
        - 可以成功创建VideoFile实例
        - 默认状态为'uploaded'
        - 时间戳自动设置
        """
        video = VideoFile.objects.create(
            title="测试视频",
            video_file=self.test_video,
            file_size=1024 * 1024,  # 1MB
            duration=60.0
        )
        
        self.assertEqual(video.title, "测试视频")
        self.assertEqual(video.status, 'uploaded')
        self.assertEqual(video.file_size, 1024 * 1024)
        self.assertEqual(video.duration, 60.0)
        self.assertIsNotNone(video.created_at)
        self.assertIsNotNone(video.updated_at)
    
    def test_video_file_str(self):
        """测试模型的字符串表示"""
        video = VideoFile.objects.create(
            title="测试视频",
            video_file=self.test_video,
            file_size=1024
        )
        
        expected_str = "测试视频 (uploaded)"
        self.assertEqual(str(video), expected_str)
    
    def test_get_file_name(self):
        """测试获取文件名方法"""
        video = VideoFile.objects.create(
            title="测试视频",
            video_file=self.test_video,
            file_size=1024
        )
        
        filename = video.get_file_name()
        self.assertTrue(filename.endswith(".mp4"))
        self.assertIn("test_video", filename)
    
    def test_get_file_size_mb(self):
        """测试获取文件大小（MB）方法"""
        video = VideoFile.objects.create(
            title="测试视频",
            video_file=self.test_video,
            file_size=5 * 1024 * 1024  # 5MB
        )
        
        size_mb = video.get_file_size_mb()
        self.assertEqual(size_mb, 5.0)
    
    def test_get_duration_formatted(self):
        """测试获取格式化时长方法"""
        video = VideoFile.objects.create(
            title="测试视频",
            video_file=self.test_video,
            file_size=1024,
            duration=3661.0  # 1小时1分1秒
        )
        
        formatted = video.get_duration_formatted()
        self.assertEqual(formatted, "01:01:01")
    
    def test_status_choices(self):
        """测试状态选择"""
        video = VideoFile.objects.create(
            title="测试视频",
            video_file=self.test_video,
            file_size=1024,
            status='processing'
        )
        
        self.assertEqual(video.status, 'processing')
        self.assertIn(video.status, [choice[0] for choice in VideoFile.STATUS_CHOICES])


class VideoFrameModelTestCase(TestCase):
    """VideoFrame模型测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.test_video = SimpleUploadedFile(
            "test_video.mp4",
            b'fake video content',
            content_type="video/mp4"
        )
        self.video = VideoFile.objects.create(
            title="测试视频",
            video_file=self.test_video,
            file_size=1024
        )
        
        self.test_image = SimpleUploadedFile(
            "test_frame.jpg",
            b'fake image content',
            content_type="image/jpeg"
        )
    
    def test_video_frame_creation(self):
        """
        测试视频帧创建
        
        验证：
        - 可以成功创建VideoFrame实例
        - 与VideoFile的外键关系正确
        - 时间戳和帧序号正确设置
        """
        frame = VideoFrame.objects.create(
            video=self.video,
            frame_number=1,
            timestamp=10.5,
            frame_image=self.test_image,
            extraction_method='scene_detection'
        )
        
        self.assertEqual(frame.video, self.video)
        self.assertEqual(frame.frame_number, 1)
        self.assertEqual(frame.timestamp, 10.5)
        self.assertEqual(frame.extraction_method, 'scene_detection')
        self.assertIsNotNone(frame.created_at)
    
    def test_video_frame_str(self):
        """测试模型的字符串表示"""
        frame = VideoFrame.objects.create(
            video=self.video,
            frame_number=5,
            timestamp=25.5,
            frame_image=self.test_image
        )
        
        str_repr = str(frame)
        self.assertIn("帧 5", str_repr)
        self.assertIn("25.50", str_repr)
        self.assertIn(self.video.title, str_repr)
    
    def test_get_timestamp_formatted(self):
        """测试获取格式化时间戳方法"""
        frame = VideoFrame.objects.create(
            video=self.video,
            frame_number=1,
            timestamp=3661.5,  # 1小时1分1.5秒
            frame_image=self.test_image
        )
        
        formatted = frame.get_timestamp_formatted()
        self.assertIn("01:01:01.50", formatted)
    
    def test_frame_video_relationship(self):
        """测试帧与视频的关系"""
        frame1 = VideoFrame.objects.create(
            video=self.video,
            frame_number=1,
            timestamp=1.0,
            frame_image=self.test_image
        )
        frame2 = VideoFrame.objects.create(
            video=self.video,
            frame_number=2,
            timestamp=2.0,
            frame_image=self.test_image
        )
        
        # 测试反向关系
        frames = self.video.frames.all()
        self.assertEqual(frames.count(), 2)
        self.assertIn(frame1, frames)
        self.assertIn(frame2, frames)


class OCRResultModelTestCase(TestCase):
    """OCRResult模型测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.test_video = SimpleUploadedFile(
            "test_video.mp4",
            b'fake video content',
            content_type="video/mp4"
        )
        self.video = VideoFile.objects.create(
            title="测试视频",
            video_file=self.test_video,
            file_size=1024
        )
        
        self.test_image = SimpleUploadedFile(
            "test_frame.jpg",
            b'fake image content',
            content_type="image/jpeg"
        )
        self.frame = VideoFrame.objects.create(
            video=self.video,
            frame_number=1,
            timestamp=10.0,
            frame_image=self.test_image
        )
    
    def test_ocr_result_creation(self):
        """
        测试OCR结果创建
        
        验证：
        - 可以成功创建OCRResult实例
        - 与VideoFrame的一对一关系正确
        - 文字内容和元数据正确设置
        """
        ocr_result = OCRResult.objects.create(
            frame=self.frame,
            text_content="识别的文字内容",
            confidence=0.95,
            model_used="gemini-3-pro-preview",
            processing_time=1.5
        )
        
        self.assertEqual(ocr_result.frame, self.frame)
        self.assertEqual(ocr_result.text_content, "识别的文字内容")
        self.assertEqual(ocr_result.confidence, 0.95)
        self.assertEqual(ocr_result.model_used, "gemini-3-pro-preview")
        self.assertEqual(ocr_result.processing_time, 1.5)
        self.assertIsNotNone(ocr_result.created_at)
    
    def test_ocr_result_str(self):
        """测试模型的字符串表示"""
        long_text = "这是一段很长的文字内容，用于测试字符串截断功能" * 3
        ocr_result = OCRResult.objects.create(
            frame=self.frame,
            text_content=long_text
        )
        
        str_repr = str(ocr_result)
        self.assertIn("OCR结果", str_repr)
        self.assertIn("10.00", str_repr)
        # 验证文字被截断
        self.assertIn("...", str_repr)
    
    def test_ocr_result_frame_relationship(self):
        """测试OCR结果与帧的一对一关系"""
        ocr_result = OCRResult.objects.create(
            frame=self.frame,
            text_content="测试文字"
        )
        
        # 测试反向关系
        self.assertEqual(self.frame.ocr_result, ocr_result)
        
        # 验证一对一关系：一个帧只能有一个OCR结果
        with self.assertRaises(Exception):
            OCRResult.objects.create(
                frame=self.frame,
                text_content="另一个结果"
            )



