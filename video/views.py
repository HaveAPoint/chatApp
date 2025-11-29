"""
视频OCR应用视图模块（views.py）

Django视图（View）是处理HTTP请求并返回HTTP响应的函数或类。
这个模块包含了所有处理视频上传和OCR处理的视图函数。

视图的作用：
1. 接收HTTP请求（request对象）
2. 处理业务逻辑（如数据库操作、文件处理）
3. 返回HTTP响应（HTML页面、JSON数据等）

视图类型：
- 函数视图（Function-based Views）：使用函数定义，简单直观
- 类视图（Class-based Views）：使用类定义，功能更强大，代码复用性更好

本模块提供的视图函数：
1. video_upload: 视频上传视图（GET显示表单，POST处理上传）
2. video_process: 视频处理视图（GET显示处理页面，POST开始处理）
3. video_result: 处理结果查看视图（显示OCR识别结果）
4. video_list: 视频列表视图（显示所有视频）
5. video_status_api: 状态API视图（返回JSON格式的处理状态）

处理流程：
1. 用户上传视频 -> VideoFile模型保存
2. 直接上传视频到API进行OCR识别
3. 保存OCR结果 -> 更新VideoFile的ocr_text_summary
"""

# ============================================================================
# 导入标准库模块
# ============================================================================
import os  # 操作系统接口，用于文件路径操作
import logging  # 日志记录模块，用于记录程序运行信息

# ============================================================================
# 导入Django核心模块
# ============================================================================
# render: 渲染模板并返回HTTP响应（用于返回HTML页面）
# get_object_or_404: 获取对象，如果不存在则返回404错误
# redirect: 重定向到指定URL
from django.shortcuts import render, get_object_or_404, redirect

# JsonResponse: 返回JSON格式的HTTP响应（用于API）
# HttpResponse: 返回基本的HTTP响应
from django.http import JsonResponse, HttpResponse

# require_http_methods: 装饰器，限制视图只接受指定的HTTP方法
from django.views.decorators.http import require_http_methods

# csrf_exempt: 装饰器，禁用CSRF保护（通常用于API端点）
from django.views.decorators.csrf import csrf_exempt

# settings: Django设置对象，用于访问settings.py中的配置
from django.conf import settings

# default_storage: Django默认文件存储后端
# ContentFile: 内存中的文件对象
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

# ============================================================================
# 导入应用模块
# ============================================================================
# 导入模型类（用于数据库操作）
from .models import VideoFile, VideoFrame, OCRResult

# 导入工具函数
from .utils import (
    check_ffmpeg_available,  # 检查FFmpeg是否可用
    get_video_info,  # 获取视频信息
    merge_ocr_results  # 合并OCR结果
)

# 导入API客户端相关函数
from utils.api_client import get_api_client, process_video_ocr

# 导入配置常量
from config.api_config import MODELS  # 模型配置
from config.api_config import MAX_VIDEO_SIZE, SUPPORTED_VIDEO_FORMATS  # 文件限制配置

# ============================================================================
# 日志记录器
# ============================================================================
# 创建日志记录器，用于记录程序运行信息
# __name__ 是当前模块的名称（video.views）
# 日志会显示是哪个模块记录的，便于调试
logger = logging.getLogger(__name__)


def video_upload(request):
    """
    视频上传视图函数
    
    Django视图函数接收request对象作为第一个参数，返回HTTP响应。
    request对象包含请求的所有信息：方法、参数、文件、用户等。
    
    处理用户上传视频文件的请求。
    支持GET（显示上传表单）和POST（处理上传文件）。
    
    GET请求：
        - 显示视频上传表单页面
        - 用户可以在表单中选择视频文件并上传
        
    POST请求：
        - 接收上传的视频文件
        - 验证文件格式和大小
        - 保存VideoFile模型到数据库
        - 获取视频基本信息（时长、分辨率等）
        - 重定向到处理页面
        
    Args:
        request: Django HTTP请求对象
            - request.method: HTTP方法（'GET'或'POST'）
            - request.FILES: 上传的文件字典
            - request.POST: POST请求的表单数据字典
        
    Returns:
        HttpResponse: 
            - GET请求：返回上传表单页面（HTML）
            - POST成功：重定向到处理页面
            - POST失败：返回错误信息页面（HTML）
    """
    # 检查HTTP请求方法
    # Django视图函数需要根据请求方法执行不同的逻辑
    if request.method == 'POST':
        # ====================================================================
        # POST请求：处理文件上传
        # ====================================================================
        
        # 检查是否上传了文件
        # request.FILES是包含所有上传文件的字典
        # 'video_file'是表单中文件输入框的name属性
        if 'video_file' not in request.FILES:
            # 如果没有上传文件，返回错误信息
            # render()函数渲染模板并返回HTTP响应
            # 第一个参数：request对象
            # 第二个参数：模板文件路径（相对于templates目录）
            # 第三个参数：传递给模板的上下文数据（字典）
            return render(request, 'video/upload.html', {
                'error': '请选择要上传的视频文件'
            })
        
        # 获取上传的文件对象
        # request.FILES['video_file']返回一个UploadedFile对象
        # 这个对象包含文件内容、文件名、大小等信息
        video_file = request.FILES['video_file']
        
        # 获取视频标题
        # request.POST.get()获取POST数据，如果不存在则使用默认值
        # 如果用户没有输入标题，使用文件名作为标题
        title = request.POST.get('title', video_file.name)
        
        # ====================================================================
        # 文件验证
        # ====================================================================
        
        # 验证文件大小
        # video_file.size是文件大小（字节）
        # MAX_VIDEO_SIZE是配置的最大文件大小（100MB）
        if video_file.size > MAX_VIDEO_SIZE:
            # 文件过大，返回错误信息
            # 计算并显示最大文件大小（MB）
            return render(request, 'video/upload.html', {
                'error': f'文件大小超过限制（最大{MAX_VIDEO_SIZE / (1024*1024)}MB）'
            })
        
        # 验证文件格式
        # os.path.splitext()分离文件名和扩展名
        # [1]获取扩展名部分（包含点号，如'.mp4'）
        # .lower()转换为小写，统一格式
        file_ext = os.path.splitext(video_file.name)[1].lower()
        # 检查扩展名是否在支持的格式列表中
        if file_ext not in SUPPORTED_VIDEO_FORMATS:
            return render(request, 'video/upload.html', {
                'error': f'不支持的视频格式。支持的格式：{", ".join(SUPPORTED_VIDEO_FORMATS)}'
            })
        
        # ====================================================================
        # 保存文件到数据库
        # ====================================================================
        try:
            # 使用Django ORM创建数据库记录
            # VideoFile.objects.create()是创建并保存模型实例的快捷方法
            # 参数对应模型的字段名
            # Django会自动处理文件上传，将文件保存到MEDIA_ROOT目录
            video = VideoFile.objects.create(
                title=title,  # 视频标题
                video_file=video_file,  # 视频文件（Django会自动保存）
                file_size=video_file.size,  # 文件大小（字节）
                status='uploaded'  # 状态：已上传
            )
            # 注意：create()方法会自动保存到数据库，不需要调用save()
            
            # ================================================================
            # 获取视频信息（可选，需要FFmpeg）
            # ================================================================
            # 检查系统是否安装了FFmpeg（视频处理工具）
            if check_ffmpeg_available():
                try:
                    # 获取视频文件的完整路径
                    # video.video_file.path返回文件在服务器上的完整路径
                    video_path = video.video_file.path
                    
                    # 调用工具函数获取视频信息（时长、分辨率等）
                    video_info = get_video_info(video_path)
                    
                    # 更新视频模型的字段
                    # .get()方法安全地获取字典值，如果不存在返回None
                    video.duration = video_info.get('duration')
                    
                    # 设置分辨率（格式：宽x高，如"1920x1080"）
                    if video_info.get('width') and video_info.get('height'):
                        video.resolution = f"{video_info['width']}x{video_info['height']}"
                    
                    # 保存更新后的信息到数据库
                    video.save()
                except Exception as e:
                    # 如果获取视频信息失败，记录警告但不中断流程
                    # 视频信息不是必需的，即使获取失败也可以继续处理
                    logger.warning(f"获取视频信息失败: {e}")
            
            # 记录成功日志
            # logger.info()记录信息级别的日志
            logger.info(f"视频上传成功: {video.id} - {video.title}")
            
            # 重定向到处理页面
            # redirect()函数生成重定向响应（HTTP 302）
            # 'video:process'是URL名称（命名空间:名称）
            # video_id是路径参数，会传递给视图函数
            return redirect('video:process', video_id=video.id)
            
        except Exception as e:
            # 如果发生任何异常，记录错误并返回错误页面
            logger.error(f"视频上传失败: {e}")
            return render(request, 'video/upload.html', {
                'error': f'上传失败: {str(e)}'
            })
    
    # ========================================================================
    # GET请求：显示上传表单
    # ========================================================================
    # 如果请求方法是GET，渲染上传表单页面
    # 不传递额外的上下文数据，模板会显示空表单
    return render(request, 'video/upload.html')


def video_process(request, video_id):
    """
    视频处理视图函数 - 直接上传视频到API进行OCR识别
    
    这个视图处理视频的OCR识别任务，直接将整个视频文件上传到API。
    支持GET（显示处理页面）和POST（开始处理）。
    
    处理流程：
    1. 获取视频文件路径
    2. 初始化API客户端
    3. 直接上传视频文件到API进行OCR识别
    4. 获取OCR识别结果
    5. 更新VideoFile状态和结果到数据库
    
    Args:
        request: Django HTTP请求对象
        video_id: 视频文件的ID（从URL路径参数获取）
            - 这个参数来自urls.py中的路径参数：<int:video_id>
            - Django会自动将URL中的数字转换为整数并传递给视图函数
        
    Returns:
        HttpResponse: 
            - GET请求：返回处理页面（HTML）
            - POST成功：返回JSON格式的处理结果
            - POST失败：返回JSON格式的错误信息
    """
    # 从数据库获取视频对象
    # get_object_or_404()是Django的快捷函数
    # 如果对象不存在，自动返回404错误页面
    # 参数：模型类、查询条件（id=video_id）
    video = get_object_or_404(VideoFile, id=video_id)
    
    if request.method == 'POST':
        # ====================================================================
        # POST请求：开始处理视频OCR
        # ====================================================================
        
        # 检查视频是否正在处理中
        # 防止重复处理同一个视频
        if video.status == 'processing':
            # 返回JSON格式的错误响应
            # JsonResponse自动将字典转换为JSON格式
            # status=400表示客户端错误（Bad Request）
            return JsonResponse({'error': '视频正在处理中'}, status=400)
        
        try:
            # ================================================================
            # 更新视频状态为"处理中"
            # ================================================================
            video.status = 'processing'  # 设置状态为处理中
            video.error_message = None  # 清空之前的错误信息
            video.save()  # 保存到数据库
            
            # ================================================================
            # 获取视频文件路径
            # ================================================================
            # video.video_file.path返回文件在服务器上的完整路径
            # 例如：/path/to/media/uploaded_videos/2024/01/01/video.mp4
            video_path = video.video_file.path
            
            # ================================================================
            # 初始化API客户端
            # ================================================================
            # get_api_client()返回配置好的OpenAI兼容API客户端
            # 客户端包含API密钥、基础URL等配置信息
            api_client = get_api_client()
            
            # ================================================================
            # 选择使用的AI模型
            # ================================================================
            # 从POST请求中获取模型名称，如果没有则使用默认模型
            model = request.POST.get('model', MODELS['vision']['default'])
            # 验证模型名称，如果不是支持的模型则使用默认模型
            if model != MODELS['vision']['doubao_vision']:
                model = MODELS['vision']['default']
            
            # 记录开始处理的日志
            logger.info(f"开始处理视频OCR，视频ID: {video.id}, 模型: {model}")
            
            # ================================================================
            # 调用API进行OCR识别
            # ================================================================
            # 记录开始时间，用于计算处理耗时
            import time
            start_time = time.time()
            
            # 调用API处理视频OCR
            # process_video_ocr()函数会：
            # 1. 读取视频文件
            # 2. 将视频编码为base64
            # 3. 发送到API进行OCR识别
            # 4. 返回识别结果
            ocr_response = process_video_ocr(
                api_client,  # API客户端
                video_path,  # 视频文件路径
                model=model  # 使用的模型
            )
            
            # 计算处理耗时（秒）
            processing_time = time.time() - start_time
            
            # ================================================================
            # 保存OCR结果到数据库
            # ================================================================
            # ocr_response['content']包含OCR识别的文字内容
            video.ocr_text_summary = ocr_response['content']
            video.status = 'completed'  # 更新状态为已完成
            
            # 记录处理完成时间
            # timezone.now()返回当前时区的时间（时区感知的datetime对象）
            from django.utils import timezone
            video.processed_at = timezone.now()
            
            # 保存更新到数据库
            video.save()
            
            # 记录处理完成的日志
            logger.info(f"视频处理完成: {video.id}, 耗时: {processing_time:.2f}秒, Token: {ocr_response['usage']['total_tokens']}")
            
            # 返回JSON格式的成功响应
            # 前端JavaScript可以使用这个响应更新页面
            return JsonResponse({
                'success': True,
                'message': '处理完成',
                'processing_time': round(processing_time, 2),  # 处理耗时（秒）
                'token_usage': ocr_response['usage'],  # API使用的token统计
                'model_used': ocr_response['model']  # 使用的模型名称
            })
            
        except Exception as e:
            # ================================================================
            # 处理失败：更新状态并返回错误信息
            # ================================================================
            logger.error(f"视频处理失败: {e}")
            
            # 更新视频状态为失败，并保存错误信息
            video.status = 'failed'
            video.error_message = str(e)  # 保存错误信息，便于调试
            video.save()
            
            # 返回JSON格式的错误响应
            # status=500表示服务器内部错误
            return JsonResponse({
                'error': f'处理失败: {str(e)}'
            }, status=500)
    
    # ========================================================================
    # GET请求：显示处理页面
    # ========================================================================
    # 获取视频相关的所有帧
    # video.frames是反向关联（related_name='frames'）
    # .all()返回所有关联的VideoFrame对象
    frames = video.frames.all()
    
    # 获取视频相关的所有OCR结果
    # OCRResult.objects.filter()是Django ORM的查询方法
    # frame__video是跨关联查询（通过frame字段访问video字段）
    # 等价于SQL：WHERE frame.video_id = video.id
    ocr_results = OCRResult.objects.filter(frame__video=video)
    
    # 准备传递给模板的上下文数据
    # 模板可以使用这些变量渲染页面
    context = {
        'video': video,  # 视频对象
        'frames': frames,  # 视频帧列表
        'ocr_results': ocr_results,  # OCR结果列表
        'ffmpeg_available': check_ffmpeg_available(),  # FFmpeg是否可用
        'vision_model': MODELS['vision']['default']  # 默认视觉模型
    }
    
    # 渲染处理页面模板
    return render(request, 'video/process.html', context)


def video_result(request, video_id):
    """
    视频处理结果查看视图函数
    
    显示视频OCR识别的最终结果页面。
    包括所有帧的OCR结果和合并后的摘要。
    
    Args:
        request: Django HTTP请求对象
        video_id: 视频文件的ID（从URL路径参数获取）
        
    Returns:
        HttpResponse: 结果展示页面（HTML）
    """
    # 从数据库获取视频对象，如果不存在则返回404
    video = get_object_or_404(VideoFile, id=video_id)
    
    # ========================================================================
    # 获取所有OCR结果（按时间排序）
    # ========================================================================
    # OCRResult.objects.filter()查询所有相关的OCR结果
    # frame__video=video: 跨关联查询，获取该视频的所有OCR结果
    # .select_related('frame'): 优化查询，一次性加载关联的frame对象
    #   避免N+1查询问题（如果不使用，每个OCR结果都会单独查询frame）
    # .order_by('frame__timestamp'): 按帧的时间戳排序
    #   这样结果会按视频播放顺序显示
    ocr_results = OCRResult.objects.filter(
        frame__video=video
    ).select_related('frame').order_by('frame__timestamp')
    
    # ========================================================================
    # 准备合并OCR结果的数据
    # ========================================================================
    # 将OCR结果转换为字典列表，便于合并函数处理
    ocr_data = []
    for ocr in ocr_results:
        ocr_data.append({
            'text': ocr.text_content,  # OCR识别的文字
            'timestamp': ocr.frame.timestamp  # 该帧的时间戳
        })
    
    # 合并OCR结果（解决重复和残缺字问题）
    # merge_ocr_results()函数会：
    # 1. 将时间相近且内容相似的OCR结果合并
    # 2. 避免重复显示相同的文字
    # 3. 处理文字在帧边界被截断的问题
    # 注意：这个函数需要从utils导入，但当前代码中可能缺少导入
    # 如果函数不存在，这里会报错，需要确保函数已定义或导入
    merged_results = merge_ocr_results(ocr_data) if ocr_data else []
    
    # ========================================================================
    # 准备模板上下文数据
    # ========================================================================
    context = {
        'video': video,  # 视频对象
        'ocr_results': ocr_results,  # 所有OCR结果（未合并）
        'merged_results': merged_results,  # 合并后的OCR结果
        'ocr_text_summary': video.ocr_text_summary  # 视频的OCR文字摘要
    }
    
    # 渲染结果页面模板
    return render(request, 'video/result.html', context)


def video_list(request):
    """
    视频列表视图函数
    
    显示所有已上传的视频文件列表。
    这是视频应用的首页，用户可以在这里查看所有视频。
    
    Args:
        request: Django HTTP请求对象
        
    Returns:
        HttpResponse: 视频列表页面（HTML）
    """
    # ========================================================================
    # 查询所有视频对象
    # ========================================================================
    # VideoFile.objects.all()获取所有VideoFile对象
    # .order_by('-created_at')按创建时间倒序排列
    #   负号(-)表示降序，最新的视频在前面
    #   如果不加负号，则是升序（最旧的在前）
    videos = VideoFile.objects.all().order_by('-created_at')
    
    # 注意：这里没有使用分页，如果视频很多可能会影响性能
    # 生产环境建议使用Django的分页功能：
    # from django.core.paginator import Paginator
    # paginator = Paginator(videos, 20)  # 每页20个
    
    # ========================================================================
    # 准备模板上下文数据
    # ========================================================================
    context = {
        'videos': videos  # 视频列表（QuerySet对象）
    }
    
    # 渲染列表页面模板
    return render(request, 'video/list.html', context)


@require_http_methods(["GET"])  # 装饰器：限制只接受GET请求
def video_status_api(request, video_id):
    """
    视频处理状态API视图函数
    
    这是一个API端点，返回JSON格式的视频处理状态。
    主要用于前端AJAX轮询，实时获取视频处理进度。
    
    AJAX轮询的工作原理：
    1. 前端JavaScript定时（如每2秒）发送GET请求到这个API
    2. API返回当前的处理状态（processing/completed/failed）
    3. 前端根据状态更新页面显示
    4. 如果状态是completed，停止轮询并显示结果
    
    Args:
        request: Django HTTP请求对象
        video_id: 视频文件的ID（从URL路径参数获取）
        
    Returns:
        JsonResponse: 包含视频状态的JSON响应
            {
                'id': 视频ID,
                'status': 处理状态,
                'error_message': 错误信息（如果有）,
                'processed_at': 处理完成时间,
                'frames_count': 帧数量,
                'ocr_results_count': OCR结果数量
            }
    """
    # 从数据库获取视频对象
    video = get_object_or_404(VideoFile, id=video_id)
    
    # 返回JSON格式的响应
    # JsonResponse会自动将Python字典转换为JSON格式
    return JsonResponse({
        'id': video.id,  # 视频ID
        'status': video.status,  # 处理状态（uploaded/processing/completed/failed）
        'error_message': video.error_message,  # 错误信息（如果有）
        # 处理完成时间（ISO格式字符串）
        # .isoformat()将datetime对象转换为ISO 8601格式字符串
        # 例如：'2024-01-01T12:00:00+08:00'
        'processed_at': video.processed_at.isoformat() if video.processed_at else None,
        # 视频帧数量
        # .count()返回关联对象的数量（不加载所有对象，性能更好）
        'frames_count': video.frames.count(),
        # OCR结果数量
        # 使用filter().count()查询该视频的所有OCR结果数量
        'ocr_results_count': OCRResult.objects.filter(frame__video=video).count()
    })
