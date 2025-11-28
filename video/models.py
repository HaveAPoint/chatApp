"""
视频OCR应用模型

该模块定义了视频处理和OCR相关的数据模型：
- VideoFile: 存储上传的视频文件信息
- VideoFrame: 存储从视频中提取的帧信息
- OCRResult: 存储OCR识别结果

模型关系：
VideoFile (1) -> (N) VideoFrame
VideoFrame (1) -> (1) OCRResult
"""

from django.db import models
from django.core.validators import FileExtensionValidator
from pathlib import Path
import os


class VideoFile(models.Model):
    """
    视频文件模型
    
    存储用户上传的视频文件信息，包括：
    - 文件路径和元数据
    - 处理状态
    - 创建和更新时间
    
    状态说明：
    - 'uploaded': 已上传，等待处理
    - 'processing': 正在处理中
    - 'completed': 处理完成
    - 'failed': 处理失败
    """
    
    # 状态选择
    STATUS_CHOICES = [
        ('uploaded', '已上传'),
        ('processing', '处理中'),
        ('completed', '已完成'),
        ('failed', '处理失败'),
    ]
    
    # 基本信息
    title = models.CharField(
        max_length=200,
        verbose_name='视频标题',
        help_text='视频文件的标题或名称'
    )
    video_file = models.FileField(
        upload_to='uploaded_videos/%Y/%m/%d/',
        verbose_name='视频文件',
        validators=[FileExtensionValidator(allowed_extensions=['mp4', 'avi', 'mov', 'mkv', 'webm'])],
        help_text='上传的视频文件（支持mp4, avi, mov, mkv, webm格式）'
    )
    
    # 元数据
    file_size = models.BigIntegerField(
        verbose_name='文件大小（字节）',
        help_text='视频文件的大小，单位：字节'
    )
    duration = models.FloatField(
        null=True,
        blank=True,
        verbose_name='视频时长（秒）',
        help_text='视频的时长，单位：秒'
    )
    resolution = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        verbose_name='分辨率',
        help_text='视频分辨率，格式：宽x高（如：1920x1080）'
    )
    
    # 处理状态
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='uploaded',
        verbose_name='处理状态',
        help_text='视频处理的当前状态'
    )
    error_message = models.TextField(
        null=True,
        blank=True,
        verbose_name='错误信息',
        help_text='如果处理失败，存储错误信息'
    )
    
    # OCR结果摘要（合并后的最终结果）
    ocr_text_summary = models.TextField(
        null=True,
        blank=True,
        verbose_name='OCR文字摘要',
        help_text='从视频中提取的所有文字内容的合并结果'
    )
    
    # 时间戳
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='创建时间',
        help_text='视频上传的时间'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='更新时间',
        help_text='最后更新的时间'
    )
    processed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='处理完成时间',
        help_text='OCR处理完成的时间'
    )
    
    class Meta:
        verbose_name = '视频文件'
        verbose_name_plural = '视频文件'
        ordering = ['-created_at']  # 按创建时间倒序排列
        indexes = [
            models.Index(fields=['status', 'created_at']),  # 状态和时间索引
        ]
    
    def __str__(self):
        """返回模型的字符串表示"""
        return f"{self.title} ({self.status})"
    
    def get_file_name(self):
        """获取文件名（不含路径）"""
        return os.path.basename(self.video_file.name)
    
    def get_file_size_mb(self):
        """获取文件大小（MB）"""
        return round(self.file_size / (1024 * 1024), 2)
    
    def get_duration_formatted(self):
        """获取格式化的时长（时:分:秒）"""
        if not self.duration:
            return None
        hours = int(self.duration // 3600)
        minutes = int((self.duration % 3600) // 60)
        seconds = int(self.duration % 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


class VideoFrame(models.Model):
    """
    视频帧模型
    
    存储从视频中提取的帧信息，用于OCR处理。
    每帧包含：
    - 时间戳（在视频中的位置）
    - 帧图像文件路径
    - 提取方法（场景检测/固定间隔等）
    """
    
    video = models.ForeignKey(
        VideoFile,
        on_delete=models.CASCADE,
        related_name='frames',
        verbose_name='所属视频',
        help_text='该帧所属的视频文件'
    )
    
    # 帧信息
    frame_number = models.IntegerField(
        verbose_name='帧序号',
        help_text='帧在视频中的序号'
    )
    timestamp = models.FloatField(
        verbose_name='时间戳（秒）',
        help_text='该帧在视频中的时间位置，单位：秒'
    )
    frame_image = models.ImageField(
        upload_to='frames/%Y/%m/%d/',
        verbose_name='帧图像',
        help_text='提取的帧图像文件'
    )
    
    # 提取方法
    extraction_method = models.CharField(
        max_length=50,
        default='scene_detection',
        verbose_name='提取方法',
        help_text='帧提取的方法（scene_detection: 场景检测, fixed_interval: 固定间隔）'
    )
    
    # 时间戳
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='创建时间'
    )
    
    class Meta:
        verbose_name = '视频帧'
        verbose_name_plural = '视频帧'
        ordering = ['video', 'timestamp']  # 按视频和时间戳排序
        indexes = [
            models.Index(fields=['video', 'timestamp']),  # 视频和时间戳索引
        ]
    
    def __str__(self):
        """返回模型的字符串表示"""
        return f"帧 {self.frame_number} @ {self.timestamp:.2f}s (视频: {self.video.title})"
    
    def get_timestamp_formatted(self):
        """获取格式化的时间戳（时:分:秒.毫秒）"""
        hours = int(self.timestamp // 3600)
        minutes = int((self.timestamp % 3600) // 60)
        seconds = self.timestamp % 60
        return f"{hours:02d}:{int(minutes):02d}:{seconds:05.2f}"


class OCRResult(models.Model):
    """
    OCR识别结果模型
    
    存储对视频帧进行OCR识别后的结果。
    每个OCRResult对应一个VideoFrame，包含：
    - 识别的文字内容
    - 识别置信度（如果有）
    - 处理时间
    """
    
    frame = models.OneToOneField(
        VideoFrame,
        on_delete=models.CASCADE,
        related_name='ocr_result',
        verbose_name='所属帧',
        help_text='该OCR结果对应的视频帧'
    )
    
    # OCR结果
    text_content = models.TextField(
        verbose_name='识别文字',
        help_text='从该帧中识别出的文字内容'
    )
    confidence = models.FloatField(
        null=True,
        blank=True,
        verbose_name='置信度',
        help_text='OCR识别的置信度（0-1之间）'
    )
    
    # 处理信息
    model_used = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name='使用的模型',
        help_text='用于OCR识别的AI模型名称'
    )
    processing_time = models.FloatField(
        null=True,
        blank=True,
        verbose_name='处理时间（秒）',
        help_text='OCR处理所花费的时间'
    )
    
    # 时间戳
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='创建时间'
    )
    
    class Meta:
        verbose_name = 'OCR识别结果'
        verbose_name_plural = 'OCR识别结果'
        ordering = ['frame__video', 'frame__timestamp']
        indexes = [
            models.Index(fields=['frame']),  # 帧索引
        ]
    
    def __str__(self):
        """返回模型的字符串表示"""
        text_preview = self.text_content[:50] + "..." if len(self.text_content) > 50 else self.text_content
        return f"OCR结果 @ {self.frame.timestamp:.2f}s: {text_preview}"
