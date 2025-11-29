"""
Django管理后台配置文件（admin.py）

这个文件用于将模型注册到Django管理后台，提供Web界面管理数据库中的数据。
Django管理后台是一个自动生成的管理界面，可以方便地查看、添加、修改、删除数据。

管理后台的作用：
1. 提供Web界面管理数据库数据，无需编写额外的管理页面
2. 自动生成表单，支持数据的增删改查
3. 支持用户权限管理，可以控制不同用户的操作权限
4. 支持数据过滤、搜索、排序等功能

使用步骤：
1. 导入要注册的模型
2. 创建ModelAdmin类（可选，用于自定义管理界面）
3. 使用admin.site.register()注册模型

访问管理后台：
1. 创建超级用户：python manage.py createsuperuser
2. 启动开发服务器：python manage.py runserver
3. 访问：http://localhost:8000/admin/
4. 使用超级用户账号登录

学习要点：
- 所有需要管理的模型都应该在这里注册
- ModelAdmin类可以自定义列表显示、搜索、过滤等功能
- 可以使用装饰器@admin.register()简化注册代码
"""

# 导入Django管理后台模块
from django.contrib import admin

# 导入要注册的模型
# 注意：这里注释掉了，因为需要先导入模型
# from .models import VideoFile, VideoFrame, OCRResult

# ============================================================================
# 模型注册示例
# ============================================================================
# 以下代码展示了如何将模型注册到Django管理后台
# 取消注释并导入模型后即可使用

# 方式一：简单注册（使用默认配置）
# admin.site.register(VideoFile)
# admin.site.register(VideoFrame)
# admin.site.register(OCRResult)

# 方式二：使用装饰器注册（推荐）
# @admin.register(VideoFile)
# class VideoFileAdmin(admin.ModelAdmin):
#     pass

# 方式三：自定义管理界面（推荐用于复杂模型）
# @admin.register(VideoFile)
# class VideoFileAdmin(admin.ModelAdmin):
#     """
#     VideoFile模型的管理后台配置
#     
#     这个类自定义了VideoFile模型在管理后台的显示和行为。
#     """
#     
#     # list_display: 列表页面显示的字段
#     # 这些字段会在管理后台的列表页面显示为列
#     list_display = ['id', 'title', 'status', 'created_at', 'file_size']
#     
#     # list_filter: 列表页面的过滤器
#     # 用户可以通过这些字段快速过滤数据
#     list_filter = ['status', 'created_at']
#     
#     # search_fields: 搜索字段
#     # 用户可以在搜索框中输入关键词搜索这些字段
#     search_fields = ['title', 'ocr_text_summary']
#     
#     # list_editable: 可编辑字段
#     # 这些字段可以直接在列表页面编辑，无需进入详情页
#     list_editable = ['status']
#     
#     # readonly_fields: 只读字段
#     # 这些字段在编辑页面显示为只读，不能修改
#     readonly_fields = ['created_at', 'updated_at', 'processed_at']
#     
#     # fieldsets: 字段分组
#     # 将字段分组显示，使界面更清晰
#     fieldsets = (
#         ('基本信息', {
#             'fields': ('title', 'video_file', 'file_size')
#         }),
#         ('视频信息', {
#             'fields': ('duration', 'resolution')
#         }),
#         ('处理状态', {
#             'fields': ('status', 'error_message', 'processed_at')
#         }),
#         ('OCR结果', {
#             'fields': ('ocr_text_summary',)
#         }),
#     )
#     
#     # date_hierarchy: 日期层次导航
#     # 在列表页面顶部显示日期导航，方便按日期筛选
#     date_hierarchy = 'created_at'
#     
#     # ordering: 默认排序
#     # 列表页面的默认排序方式
#     ordering = ['-created_at']  # 按创建时间倒序排列
#     
#     # list_per_page: 每页显示数量
#     list_per_page = 20

# @admin.register(VideoFrame)
# class VideoFrameAdmin(admin.ModelAdmin):
#     """VideoFrame模型的管理后台配置"""
#     list_display = ['id', 'video', 'frame_number', 'timestamp', 'created_at']
#     list_filter = ['extraction_method', 'created_at']
#     search_fields = ['video__title']  # 通过关联字段搜索
#     readonly_fields = ['created_at']
#     ordering = ['video', 'timestamp']

# @admin.register(OCRResult)
# class OCRResultAdmin(admin.ModelAdmin):
#     """OCRResult模型的管理后台配置"""
#     list_display = ['id', 'frame', 'text_content', 'confidence', 'model_used', 'created_at']
#     list_filter = ['model_used', 'created_at']
#     search_fields = ['text_content']
#     readonly_fields = ['created_at']
#     ordering = ['frame__video', 'frame__timestamp']

# ============================================================================
# 内联管理（Inline Admin）
# ============================================================================
# 内联管理允许在父模型的编辑页面中直接编辑关联的子模型
# 例如：在VideoFile的编辑页面中直接编辑VideoFrame

# from django.contrib.admin import TabularInline  # 表格形式的内联
# from django.contrib.admin import StackedInline  # 堆叠形式的内联

# class VideoFrameInline(TabularInline):
#     """在VideoFile编辑页面中内联显示VideoFrame"""
#     model = VideoFrame
#     extra = 0  # 默认显示的空表单数量
#     fields = ['frame_number', 'timestamp', 'extraction_method']
#     readonly_fields = ['created_at']

# class OCRResultInline(StackedInline):
#     """在VideoFrame编辑页面中内联显示OCRResult"""
#     model = OCRResult
#     extra = 0
#     fields = ['text_content', 'confidence', 'model_used']
#     readonly_fields = ['created_at']

# 然后在VideoFileAdmin中添加：
# inlines = [VideoFrameInline]

# 在VideoFrameAdmin中添加：
# inlines = [OCRResultInline]
