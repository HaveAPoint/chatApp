"""
视频OCR应用模型模块（models.py）

Django模型（Model）是数据的单一、明确的信息来源。
它包含了存储的数据的基本字段和行为。

模型的作用：
1. 定义数据库表结构（字段、类型、约束）
2. 提供数据库操作的API（ORM：对象关系映射）
3. 定义数据验证规则
4. 定义模型之间的关系（外键、一对一、多对多）

Django ORM的优势：
- 不需要写SQL，使用Python代码操作数据库
- 自动处理数据库差异（SQLite、PostgreSQL、MySQL等）
- 提供数据验证和类型转换
- 支持数据库迁移（版本控制）

本模块定义的模型：
- VideoFile: 存储上传的视频文件信息
- VideoFrame: 存储从视频中提取的帧信息
- OCRResult: 存储OCR识别结果

模型关系：
VideoFile (1) -> (N) VideoFrame  # 一个视频有多个帧
VideoFrame (1) -> (1) OCRResult  # 一个帧对应一个OCR结果

学习要点：
- 每个模型类对应数据库中的一个表
- 每个字段对应表中的一列
- 模型之间的关系通过ForeignKey、OneToOneField等定义
- Meta类用于配置模型的元数据（表名、排序、索引等）
"""

# ============================================================================
# 导入Django模型相关模块
# ============================================================================
# models: Django模型基类和字段类型
from django.db import models

# FileExtensionValidator: 文件扩展名验证器
from django.core.validators import FileExtensionValidator

# Path: 路径处理类（用于文件路径操作）
from pathlib import Path

# os: 操作系统接口（用于文件操作）
import os


class VideoFile(models.Model):
    """
    视频文件模型类
    
    Django模型类必须继承自models.Model。
    这个类定义了视频文件的数据结构，对应数据库中的video_videofile表。
    
    存储用户上传的视频文件信息，包括：
    - 文件路径和元数据（文件名、大小、时长、分辨率等）
    - 处理状态（已上传、处理中、已完成、失败）
    - OCR识别结果摘要
    - 创建和更新时间
    
    状态说明：
    - 'uploaded': 已上传，等待处理
    - 'processing': 正在处理中（OCR识别进行中）
    - 'completed': 处理完成（OCR识别完成）
    - 'failed': 处理失败（OCR识别出错）
    
    数据库表名：
    - 默认表名：video_videofile（应用名_模型名小写）
    - 可以通过Meta.db_table自定义
    """
    
    # ========================================================================
    # 状态选择常量
    # ========================================================================
    # STATUS_CHOICES定义了status字段的可选值
    # 格式：[(数据库值, 显示名称), ...]
    # 数据库存储第一个值（如'uploaded'），显示时使用第二个值（如'已上传'）
    STATUS_CHOICES = [
        ('uploaded', '已上传'),      # 视频已上传，等待处理
        ('processing', '处理中'),    # 正在处理OCR识别
        ('completed', '已完成'),     # OCR处理完成
        ('failed', '处理失败'),      # OCR处理失败
    ]
    
    # ========================================================================
    # 基本信息字段
    # ========================================================================
    
    # title字段：视频标题
    # CharField: 字符串字段，用于存储短文本
    # max_length: 最大长度（字符数），数据库会限制长度
    # verbose_name: 字段的显示名称（用于管理后台、表单等）
    # help_text: 字段的帮助文本（显示在表单下方）
    title = models.CharField(
        max_length=200,  # 最大200个字符
        verbose_name='视频标题',  # 在管理后台显示为"视频标题"
        help_text='视频文件的标题或名称'  # 帮助提示文本
    )
    
    # video_file字段：视频文件
    # FileField: 文件字段，用于存储上传的文件
    # upload_to: 文件上传的目录路径
    #   - 'uploaded_videos/%Y/%m/%d/': 按年/月/日组织目录
    #   - %Y: 4位年份（如2024）
    #   - %m: 2位月份（01-12）
    #   - %d: 2位日期（01-31）
    #   - 例如：uploaded_videos/2024/01/15/video.mp4
    # validators: 验证器列表，用于验证上传的文件
    #   FileExtensionValidator: 验证文件扩展名
    #   allowed_extensions: 允许的文件扩展名列表
    video_file = models.FileField(
        upload_to='uploaded_videos/%Y/%m/%d/',  # 上传目录（按日期组织）
        verbose_name='视频文件',  # 显示名称
        validators=[FileExtensionValidator(allowed_extensions=['mp4', 'avi', 'mov', 'mkv', 'webm'])],  # 文件扩展名验证
        help_text='上传的视频文件（支持mp4, avi, mov, mkv, webm格式）'  # 帮助文本
    )
    
    # ========================================================================
    # 元数据字段
    # ========================================================================
    
    # file_size字段：文件大小
    # BigIntegerField: 大整数字段，用于存储大数值
    # 范围：-9223372036854775808 到 9223372036854775807
    # 用途：存储文件大小（字节），支持大文件（如几GB的视频）
    file_size = models.BigIntegerField(
        verbose_name='文件大小（字节）',  # 显示名称
        help_text='视频文件的大小，单位：字节'  # 帮助文本
    )
    
    # duration字段：视频时长
    # FloatField: 浮点数字段，用于存储小数
    # null=True: 允许数据库中的值为NULL（空值）
    # blank=True: 允许表单中不填写（空字符串）
    # 注意：null和blank的区别：
    #   - null: 数据库层面，是否允许NULL值
    #   - blank: 表单层面，是否允许空值
    #   通常同时设置null=True和blank=True表示字段可选
    duration = models.FloatField(
        null=True,  # 数据库允许NULL
        blank=True,  # 表单允许为空
        verbose_name='视频时长（秒）',  # 显示名称
        help_text='视频的时长，单位：秒'  # 帮助文本
    )
    
    # resolution字段：视频分辨率
    # CharField: 字符串字段
    # max_length=20: 最大长度20个字符（如"1920x1080"）
    # null=True, blank=True: 可选字段
    resolution = models.CharField(
        max_length=20,  # 最大20个字符
        null=True,  # 允许NULL
        blank=True,  # 允许为空
        verbose_name='分辨率',  # 显示名称
        help_text='视频分辨率，格式：宽x高（如：1920x1080）'  # 帮助文本
    )
    
    # ========================================================================
    # 处理状态字段
    # ========================================================================
    
    # status字段：处理状态
    # CharField: 字符串字段
    # choices: 限制字段值只能从STATUS_CHOICES中选择
    #   在管理后台会显示为下拉选择框
    # default: 默认值，创建新对象时如果没有指定则使用此值
    status = models.CharField(
        max_length=20,  # 最大20个字符
        choices=STATUS_CHOICES,  # 可选值列表
        default='uploaded',  # 默认值：已上传
        verbose_name='处理状态',  # 显示名称
        help_text='视频处理的当前状态'  # 帮助文本
    )
    
    # error_message字段：错误信息
    # TextField: 文本字段，用于存储长文本（无长度限制）
    # CharField vs TextField:
    #   - CharField: 有最大长度限制，适合短文本
    #   - TextField: 无长度限制，适合长文本
    error_message = models.TextField(
        null=True,  # 允许NULL
        blank=True,  # 允许为空
        verbose_name='错误信息',  # 显示名称
        help_text='如果处理失败，存储错误信息'  # 帮助文本
    )
    
    # ========================================================================
    # OCR结果字段
    # ========================================================================
    
    # ocr_text_summary字段：OCR文字摘要
    # TextField: 文本字段，用于存储长文本（OCR结果可能很长）
    # 存储从视频中提取的所有文字内容的合并结果
    ocr_text_summary = models.TextField(
        null=True,  # 允许NULL（处理前为空）
        blank=True,  # 允许为空
        verbose_name='OCR文字摘要',  # 显示名称
        help_text='从视频中提取的所有文字内容的合并结果'  # 帮助文本
    )
    
    # ========================================================================
    # 时间戳字段
    # ========================================================================
    
    # created_at字段：创建时间
    # DateTimeField: 日期时间字段，存储日期和时间
    # auto_now_add=True: 自动设置为对象创建时的时间
    #   只在创建时设置一次，之后不会改变
    # 用途：记录视频上传的时间
    created_at = models.DateTimeField(
        auto_now_add=True,  # 自动设置创建时间
        verbose_name='创建时间',  # 显示名称
        help_text='视频上传的时间'  # 帮助文本
    )
    
    # updated_at字段：更新时间
    # DateTimeField: 日期时间字段
    # auto_now=True: 每次保存对象时自动更新为当前时间
    #   每次调用save()时都会更新
    # 用途：记录最后修改的时间
    updated_at = models.DateTimeField(
        auto_now=True,  # 自动更新为当前时间
        verbose_name='更新时间',  # 显示名称
        help_text='最后更新的时间'  # 帮助文本
    )
    
    # processed_at字段：处理完成时间
    # DateTimeField: 日期时间字段
    # null=True, blank=True: 可选字段（处理完成前为空）
    # 用途：记录OCR处理完成的时间
    processed_at = models.DateTimeField(
        null=True,  # 允许NULL
        blank=True,  # 允许为空
        verbose_name='处理完成时间',  # 显示名称
        help_text='OCR处理完成的时间'  # 帮助文本
    )
    
    # ========================================================================
    # Meta类：模型元数据配置
    # ========================================================================
    # Meta类用于配置模型的元数据，不会创建数据库字段
    class Meta:
        # verbose_name: 模型的单数显示名称（用于管理后台）
        verbose_name = '视频文件'
        
        # verbose_name_plural: 模型的复数显示名称
        verbose_name_plural = '视频文件'
        
        # ordering: 默认排序方式
        # ['-created_at']: 按创建时间倒序排列（最新的在前）
        #   负号(-)表示降序，不加负号表示升序
        #   可以指定多个字段：['-created_at', 'title']
        ordering = ['-created_at']
        
        # indexes: 数据库索引
        # 索引可以加快查询速度，但会增加写入时间
        # 适合经常用于查询和过滤的字段组合
        indexes = [
            # 复合索引：状态和时间
            # 用于快速查询特定状态和时间的视频
            models.Index(fields=['status', 'created_at']),
        ]
    
    # ========================================================================
    # 模型方法
    # ========================================================================
    
    def __str__(self):
        """
        返回模型的字符串表示
        
        这个方法定义了对象在Python中的字符串表示。
        在管理后台、shell、调试等场景中会显示这个字符串。
        
        Returns:
            str: 对象的字符串表示，格式：标题 (状态)
        """
        return f"{self.title} ({self.status})"
    
    def get_file_name(self):
        """
        获取文件名（不含路径）
        
        从文件路径中提取文件名部分。
        例如：uploaded_videos/2024/01/15/video.mp4 -> video.mp4
        
        Returns:
            str: 文件名（不含路径）
        """
        # os.path.basename()从路径中提取文件名
        return os.path.basename(self.video_file.name)
    
    def get_file_size_mb(self):
        """
        获取文件大小（MB）
        
        将字节转换为MB（兆字节）。
        1 MB = 1024 * 1024 字节
        
        Returns:
            float: 文件大小（MB），保留2位小数
        """
        # 字节转MB：除以(1024 * 1024)
        # round()保留2位小数
        return round(self.file_size / (1024 * 1024), 2)
    
    def get_duration_formatted(self):
        """
        获取格式化的时长（时:分:秒）
        
        将秒数转换为易读的时间格式。
        例如：3661秒 -> "01:01:01"
        
        Returns:
            str: 格式化的时长（时:分:秒），如果duration为空则返回None
        """
        if not self.duration:
            return None
        
        # 计算小时、分钟、秒
        hours = int(self.duration // 3600)  # 总小时数
        minutes = int((self.duration % 3600) // 60)  # 剩余分钟数
        seconds = int(self.duration % 60)  # 剩余秒数
        
        # 格式化为"时:分:秒"（两位数）
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


class VideoFrame(models.Model):
    """
    视频帧模型类
    
    存储从视频中提取的帧信息，用于OCR处理。
    一个视频可以有多帧，每帧对应一个VideoFrame对象。
    
    每帧包含：
    - 所属视频（外键关联）
    - 时间戳（在视频中的位置）
    - 帧图像文件路径
    - 提取方法（场景检测/固定间隔等）
    - 帧序号
    """
    
    # ========================================================================
    # 外键关系字段
    # ========================================================================
    
    # video字段：所属视频（外键）
    # ForeignKey: 多对一关系，多个VideoFrame属于一个VideoFile
    #   在数据库中创建video_id字段（外键）
    # VideoFile: 关联的模型类
    # on_delete=models.CASCADE: 级联删除
    #   当VideoFile被删除时，相关的所有VideoFrame也会被删除
    #   其他选项：
    #     - PROTECT: 保护，如果有关联对象则不允许删除
    #     - SET_NULL: 设置为NULL（需要null=True）
    #     - SET_DEFAULT: 设置为默认值（需要default）
    # related_name='frames': 反向关联名称
    #   通过video.frames可以访问该视频的所有帧
    #   例如：video.frames.all() 获取所有帧
    video = models.ForeignKey(
        VideoFile,  # 关联的模型类
        on_delete=models.CASCADE,  # 级联删除
        related_name='frames',  # 反向关联名称
        verbose_name='所属视频',  # 显示名称
        help_text='该帧所属的视频文件'  # 帮助文本
    )
    
    # ========================================================================
    # 帧信息字段
    # ========================================================================
    
    # frame_number字段：帧序号
    # IntegerField: 整数字段，用于存储整数
    # 用途：标识帧在视频中的顺序（第几帧）
    frame_number = models.IntegerField(
        verbose_name='帧序号',  # 显示名称
        help_text='帧在视频中的序号'  # 帮助文本
    )
    
    # timestamp字段：时间戳
    # FloatField: 浮点数字段，用于存储小数
    # 用途：标识帧在视频中的时间位置（秒）
    # 例如：10.5表示视频的第10.5秒
    timestamp = models.FloatField(
        verbose_name='时间戳（秒）',  # 显示名称
        help_text='该帧在视频中的时间位置，单位：秒'  # 帮助文本
    )
    
    # frame_image字段：帧图像
    # ImageField: 图片字段，继承自FileField，专门用于存储图片
    # 会自动验证文件是否为图片格式
    # upload_to: 上传目录，按日期组织
    frame_image = models.ImageField(
        upload_to='frames/%Y/%m/%d/',  # 上传目录（按日期组织）
        verbose_name='帧图像',  # 显示名称
        help_text='提取的帧图像文件'  # 帮助文本
    )
    
    # ========================================================================
    # 提取方法字段
    # ========================================================================
    
    # extraction_method字段：提取方法
    # CharField: 字符串字段
    # default: 默认值，创建新对象时如果没有指定则使用此值
    # 可选值：
    #   - 'scene_detection': 场景检测（智能提取关键帧）
    #   - 'fixed_interval': 固定间隔（按固定时间间隔提取）
    extraction_method = models.CharField(
        max_length=50,  # 最大50个字符
        default='scene_detection',  # 默认值：场景检测
        verbose_name='提取方法',  # 显示名称
        help_text='帧提取的方法（scene_detection: 场景检测, fixed_interval: 固定间隔）'  # 帮助文本
    )
    
    # ========================================================================
    # 时间戳字段
    # ========================================================================
    
    # created_at字段：创建时间
    # DateTimeField: 日期时间字段
    # auto_now_add=True: 自动设置为对象创建时的时间
    created_at = models.DateTimeField(
        auto_now_add=True,  # 自动设置创建时间
        verbose_name='创建时间'  # 显示名称
    )
    
    # ========================================================================
    # Meta类：模型元数据配置
    # ========================================================================
    class Meta:
        verbose_name = '视频帧'  # 单数显示名称
        verbose_name_plural = '视频帧'  # 复数显示名称
        
        # ordering: 默认排序方式
        # ['video', 'timestamp']: 先按视频排序，再按时间戳排序
        #   这样可以按视频分组，每组内按时间顺序排列
        ordering = ['video', 'timestamp']
        
        # indexes: 数据库索引
        indexes = [
            # 复合索引：视频和时间戳
            # 用于快速查询特定视频的帧，并按时间排序
            models.Index(fields=['video', 'timestamp']),
        ]
    
    # ========================================================================
    # 模型方法
    # ========================================================================
    
    def __str__(self):
        """
        返回模型的字符串表示
        
        Returns:
            str: 对象的字符串表示，格式：帧 序号 @ 时间戳s (视频: 标题)
        """
        return f"帧 {self.frame_number} @ {self.timestamp:.2f}s (视频: {self.video.title})"
    
    def get_timestamp_formatted(self):
        """
        获取格式化的时间戳（时:分:秒.毫秒）
        
        将秒数转换为易读的时间格式。
        例如：3661.5秒 -> "01:01:01.50"
        
        Returns:
            str: 格式化的时间戳（时:分:秒.毫秒）
        """
        # 计算小时、分钟、秒
        hours = int(self.timestamp // 3600)  # 总小时数
        minutes = int((self.timestamp % 3600) // 60)  # 剩余分钟数
        seconds = self.timestamp % 60  # 剩余秒数（包含小数部分）
        
        # 格式化为"时:分:秒.毫秒"（小时和分钟两位数，秒保留2位小数）
        return f"{hours:02d}:{int(minutes):02d}:{seconds:05.2f}"


class OCRResult(models.Model):
    """
    OCR识别结果模型类
    
    存储对视频帧进行OCR识别后的结果。
    一个VideoFrame对应一个OCRResult（一对一关系）。
    
    每个OCRResult包含：
    - 所属帧（一对一关联）
    - 识别的文字内容
    - 识别置信度（如果有）
    - 使用的AI模型
    - 处理时间
    """
    
    # ========================================================================
    # 一对一关系字段
    # ========================================================================
    
    # frame字段：所属帧（一对一）
    # OneToOneField: 一对一关系，一个VideoFrame对应一个OCRResult
    #   在数据库中创建frame_id字段（唯一外键）
    #   与ForeignKey的区别：
    #     - ForeignKey: 多对一（多个对象可以关联同一个对象）
    #     - OneToOneField: 一对一（每个对象只能关联一个对象，且唯一）
    # VideoFrame: 关联的模型类
    # on_delete=models.CASCADE: 级联删除
    #   当VideoFrame被删除时，相关的OCRResult也会被删除
    # related_name='ocr_result': 反向关联名称
    #   通过frame.ocr_result可以访问该帧的OCR结果
    #   例如：frame.ocr_result 获取OCR结果（不是QuerySet，是单个对象）
    frame = models.OneToOneField(
        VideoFrame,  # 关联的模型类
        on_delete=models.CASCADE,  # 级联删除
        related_name='ocr_result',  # 反向关联名称
        verbose_name='所属帧',  # 显示名称
        help_text='该OCR结果对应的视频帧'  # 帮助文本
    )
    
    # ========================================================================
    # OCR结果字段
    # ========================================================================
    
    # text_content字段：识别文字
    # TextField: 文本字段，用于存储长文本（OCR结果可能很长）
    # 存储从该帧中识别出的所有文字内容
    text_content = models.TextField(
        verbose_name='识别文字',  # 显示名称
        help_text='从该帧中识别出的文字内容'  # 帮助文本
    )
    
    # confidence字段：置信度
    # FloatField: 浮点数字段
    # 存储OCR识别的置信度（0-1之间）
    #   0表示完全不确信，1表示完全确信
    # null=True, blank=True: 可选字段（某些API可能不返回置信度）
    confidence = models.FloatField(
        null=True,  # 允许NULL
        blank=True,  # 允许为空
        verbose_name='置信度',  # 显示名称
        help_text='OCR识别的置信度（0-1之间）'  # 帮助文本
    )
    
    # ========================================================================
    # 处理信息字段
    # ========================================================================
    
    # model_used字段：使用的模型
    # CharField: 字符串字段
    # 存储用于OCR识别的AI模型名称
    #   例如：'doubao-seed-1-6-251015'
    model_used = models.CharField(
        max_length=100,  # 最大100个字符
        null=True,  # 允许NULL
        blank=True,  # 允许为空
        verbose_name='使用的模型',  # 显示名称
        help_text='用于OCR识别的AI模型名称'  # 帮助文本
    )
    
    # processing_time字段：处理时间
    # FloatField: 浮点数字段
    # 存储OCR处理所花费的时间（秒）
    #   用于性能分析和优化
    processing_time = models.FloatField(
        null=True,  # 允许NULL
        blank=True,  # 允许为空
        verbose_name='处理时间（秒）',  # 显示名称
        help_text='OCR处理所花费的时间'  # 帮助文本
    )
    
    # ========================================================================
    # 时间戳字段
    # ========================================================================
    
    # created_at字段：创建时间
    # DateTimeField: 日期时间字段
    # auto_now_add=True: 自动设置为对象创建时的时间
    created_at = models.DateTimeField(
        auto_now_add=True,  # 自动设置创建时间
        verbose_name='创建时间'  # 显示名称
    )
    
    # ========================================================================
    # Meta类：模型元数据配置
    # ========================================================================
    class Meta:
        verbose_name = 'OCR识别结果'  # 单数显示名称
        verbose_name_plural = 'OCR识别结果'  # 复数显示名称
        
        # ordering: 默认排序方式
        # ['frame__video', 'frame__timestamp']: 跨关联排序
        #   先按帧所属的视频排序，再按帧的时间戳排序
        #   这样可以按视频分组，每组内按时间顺序排列
        ordering = ['frame__video', 'frame__timestamp']
        
        # indexes: 数据库索引
        indexes = [
            # 单字段索引：帧
            # 用于快速查询特定帧的OCR结果
            models.Index(fields=['frame']),
        ]
    
    # ========================================================================
    # 模型方法
    # ========================================================================
    
    def __str__(self):
        """
        返回模型的字符串表示
        
        Returns:
            str: 对象的字符串表示，格式：OCR结果 @ 时间戳s: 文字预览
        """
        # 如果文字内容超过50个字符，只显示前50个字符并加上省略号
        text_preview = self.text_content[:50] + "..." if len(self.text_content) > 50 else self.text_content
        return f"OCR结果 @ {self.frame.timestamp:.2f}s: {text_preview}"
