"""
视频OCR应用视图模块

该模块提供视频上传和OCR处理的视图函数，包括：
1. 视频上传视图
2. 视频处理视图（异步处理）
3. 处理结果查看视图
4. API视图（用于AJAX请求）

处理流程：
1. 用户上传视频 -> VideoFile模型保存
2. 后台任务提取视频帧 -> VideoFrame模型保存
3. 对每帧进行OCR识别 -> OCRResult模型保存
4. 合并OCR结果 -> 更新VideoFile的ocr_text_summary
"""

import os
import logging
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from .models import VideoFile, VideoFrame, OCRResult
from .utils import (
    check_ffmpeg_available,
    get_video_info
)
from utils.api_client import get_api_client, process_video_ocr
from config.api_config import MODELS
from config.api_config import MAX_VIDEO_SIZE, SUPPORTED_VIDEO_FORMATS

logger = logging.getLogger(__name__)


def video_upload(request):
    """
    视频上传视图
    
    处理用户上传视频文件的请求。
    支持GET（显示上传表单）和POST（处理上传文件）。
    
    GET请求：
        - 显示视频上传表单页面
        
    POST请求：
        - 接收上传的视频文件
        - 验证文件格式和大小
        - 保存VideoFile模型
        - 获取视频基本信息（时长、分辨率等）
        - 重定向到处理页面
        
    Args:
        request: Django HTTP请求对象
        
    Returns:
        HttpResponse: 上传表单页面或重定向响应
    """
    if request.method == 'POST':
        # 处理文件上传
        if 'video_file' not in request.FILES:
            return render(request, 'video/upload.html', {
                'error': '请选择要上传的视频文件'
            })
        
        video_file = request.FILES['video_file']
        title = request.POST.get('title', video_file.name)
        
        # 验证文件大小
        if video_file.size > MAX_VIDEO_SIZE:
            return render(request, 'video/upload.html', {
                'error': f'文件大小超过限制（最大{MAX_VIDEO_SIZE / (1024*1024)}MB）'
            })
        
        # 验证文件格式
        file_ext = os.path.splitext(video_file.name)[1].lower()
        if file_ext not in SUPPORTED_VIDEO_FORMATS:
            return render(request, 'video/upload.html', {
                'error': f'不支持的视频格式。支持的格式：{", ".join(SUPPORTED_VIDEO_FORMATS)}'
            })
        
        try:
            # 保存视频文件
            video = VideoFile.objects.create(
                title=title,
                video_file=video_file,
                file_size=video_file.size,
                status='uploaded'
            )
            
            # 获取视频信息（需要FFmpeg）
            if check_ffmpeg_available():
                try:
                    video_path = video.video_file.path
                    video_info = get_video_info(video_path)
                    
                    video.duration = video_info.get('duration')
                    if video_info.get('width') and video_info.get('height'):
                        video.resolution = f"{video_info['width']}x{video_info['height']}"
                    video.save()
                except Exception as e:
                    logger.warning(f"获取视频信息失败: {e}")
                    # 继续处理，即使获取信息失败
            
            logger.info(f"视频上传成功: {video.id} - {video.title}")
            return redirect('video:process', video_id=video.id)
            
        except Exception as e:
            logger.error(f"视频上传失败: {e}")
            return render(request, 'video/upload.html', {
                'error': f'上传失败: {str(e)}'
            })
    
    # GET请求：显示上传表单
    return render(request, 'video/upload.html')


def video_process(request, video_id):
    """
    视频处理视图 - 直接上传视频
    
    处理视频的OCR识别任务，直接上传整个视频文件到API。
    支持GET（显示处理页面）和POST（开始处理）。
    
    处理流程：
    1. 直接上传视频文件到API
    2. 获取OCR识别结果
    3. 更新VideoFile状态和结果
    
    Args:
        request: Django HTTP请求对象
        video_id: 视频文件的ID
        
    Returns:
        HttpResponse: 处理页面或处理结果
    """
    video = get_object_or_404(VideoFile, id=video_id)
    
    if request.method == 'POST':
        # 开始处理
        if video.status == 'processing':
            return JsonResponse({'error': '视频正在处理中'}, status=400)
        
        try:
            # 更新状态
            video.status = 'processing'
            video.error_message = None
            video.save()
            
            # 获取视频路径
            video_path = video.video_file.path
            
            # 初始化API客户端
            api_client = get_api_client()
            
            # 选择模型
            model = request.POST.get('model', MODELS['vision']['default'])
            if model != MODELS['vision']['doubao_vision']:
                model = MODELS['vision']['default']
            
            logger.info(f"开始处理视频OCR，视频ID: {video.id}, 模型: {model}")
            
            # 直接上传视频进行OCR识别
            import time
            start_time = time.time()
            
            ocr_response = process_video_ocr(
                api_client,
                video_path,
                model=model
            )
            
            processing_time = time.time() - start_time
            
            # 保存OCR结果
            video.ocr_text_summary = ocr_response['content']
            video.status = 'completed'
            from django.utils import timezone
            video.processed_at = timezone.now()
            video.save()
            
            logger.info(f"视频处理完成: {video.id}, 耗时: {processing_time:.2f}秒, Token: {ocr_response['usage']['total_tokens']}")
            
            return JsonResponse({
                'success': True,
                'message': '处理完成',
                'processing_time': round(processing_time, 2),
                'token_usage': ocr_response['usage'],
                'model_used': ocr_response['model']
            })
            
        except Exception as e:
            logger.error(f"视频处理失败: {e}")
            video.status = 'failed'
            video.error_message = str(e)
            video.save()
            
            return JsonResponse({
                'error': f'处理失败: {str(e)}'
            }, status=500)
    
    # GET请求：显示处理页面
    frames = video.frames.all()
    ocr_results = OCRResult.objects.filter(frame__video=video)
    
    context = {
        'video': video,
        'frames': frames,
        'ocr_results': ocr_results,
        'ffmpeg_available': check_ffmpeg_available(),
        'vision_model': MODELS['vision']['default']
    }
    
    return render(request, 'video/process.html', context)


def video_result(request, video_id):
    """
    视频处理结果查看视图
    
    显示视频OCR识别的最终结果。
    
    Args:
        request: Django HTTP请求对象
        video_id: 视频文件的ID
        
    Returns:
        HttpResponse: 结果展示页面
    """
    video = get_object_or_404(VideoFile, id=video_id)
    
    # 获取所有OCR结果（按时间排序）
    ocr_results = OCRResult.objects.filter(
        frame__video=video
    ).select_related('frame').order_by('frame__timestamp')
    
    # 获取合并后的结果
    ocr_data = []
    for ocr in ocr_results:
        ocr_data.append({
            'text': ocr.text_content,
            'timestamp': ocr.frame.timestamp
        })
    
    merged_results = merge_ocr_results(ocr_data) if ocr_data else []
    
    context = {
        'video': video,
        'ocr_results': ocr_results,
        'merged_results': merged_results,
        'ocr_text_summary': video.ocr_text_summary
    }
    
    return render(request, 'video/result.html', context)


def video_list(request):
    """
    视频列表视图
    
    显示所有已上传的视频文件列表。
    
    Args:
        request: Django HTTP请求对象
        
    Returns:
        HttpResponse: 视频列表页面
    """
    videos = VideoFile.objects.all().order_by('-created_at')
    
    context = {
        'videos': videos
    }
    
    return render(request, 'video/list.html', context)


@require_http_methods(["GET"])
def video_status_api(request, video_id):
    """
    视频处理状态API
    
    提供视频处理状态的JSON API，用于AJAX轮询。
    
    Args:
        request: Django HTTP请求对象
        video_id: 视频文件的ID
        
    Returns:
        JsonResponse: 包含视频状态的JSON响应
    """
    video = get_object_or_404(VideoFile, id=video_id)
    
    return JsonResponse({
        'id': video.id,
        'status': video.status,
        'error_message': video.error_message,
        'processed_at': video.processed_at.isoformat() if video.processed_at else None,
        'frames_count': video.frames.count(),
        'ocr_results_count': OCRResult.objects.filter(frame__video=video).count()
    })
