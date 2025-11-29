"""
视频视图单元测试

测试覆盖：
1. 视频上传视图
2. 视频处理视图
3. 视频结果查看视图
4. 视频列表视图
5. 状态API

运行测试：
    python manage.py test video.tests.test_views
"""

from django.test import TestCase, Client
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from video.models import VideoFile, VideoFrame, OCRResult
import json


class VideoViewsTestCase(TestCase):
    """视频视图测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.client = Client()
        self.test_video = SimpleUploadedFile(
            "test_video.mp4",
            b'fake video content',
            content_type="video/mp4"
        )
    
    def test_video_upload_get(self):
        """测试视频上传页面GET请求"""
        response = self.client.get(reverse('video:upload'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'video/upload.html')
    
    def test_video_upload_post_success(self):
        """测试视频上传POST请求（成功）"""
        response = self.client.post(reverse('video:upload'), {
            'title': '测试视频',
            'video_file': self.test_video
        })
        
        # 应该重定向到处理页面
        self.assertEqual(response.status_code, 302)
        
        # 验证视频已创建
        video = VideoFile.objects.get(title='测试视频')
        self.assertEqual(video.status, 'uploaded')
        self.assertEqual(video.file_size, len(b'fake video content'))
    
    def test_video_upload_post_no_file(self):
        """测试视频上传POST请求（无文件）"""
        response = self.client.post(reverse('video:upload'), {
            'title': '测试视频'
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '请选择要上传的视频文件')
    
    def test_video_list(self):
        """测试视频列表视图"""
        # 创建测试视频
        VideoFile.objects.create(
            title='测试视频1',
            video_file=self.test_video,
            file_size=1024
        )
        
        response = self.client.get(reverse('video:list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'video/list.html')
        self.assertContains(response, '测试视频1')
    
    def test_video_process_get(self):
        """测试视频处理页面GET请求"""
        video = VideoFile.objects.create(
            title='测试视频',
            video_file=self.test_video,
            file_size=1024
        )
        
        response = self.client.get(reverse('video:process', args=[video.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'video/process.html')
        self.assertContains(response, '测试视频')
    
    def test_video_result(self):
        """测试视频结果查看视图"""
        video = VideoFile.objects.create(
            title='测试视频',
            video_file=self.test_video,
            file_size=1024,
            status='completed'
        )
        
        response = self.client.get(reverse('video:result', args=[video.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'video/result.html')
    
    def test_video_status_api(self):
        """测试视频状态API"""
        video = VideoFile.objects.create(
            title='测试视频',
            video_file=self.test_video,
            file_size=1024,
            status='processing'
        )
        
        response = self.client.get(reverse('video:status_api', args=[video.id]))
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertEqual(data['id'], video.id)
        self.assertEqual(data['status'], 'processing')





