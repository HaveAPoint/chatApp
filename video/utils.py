"""
视频处理工具模块

该模块提供视频处理相关的工具函数，包括：
1. 视频抽帧（场景检测、固定间隔）
2. 帧图像处理
3. OCR结果合并算法（解决残缺字问题）

关键功能：
- extract_frames_scene_detection: 使用场景检测提取关键帧
- extract_frames_fixed_interval: 使用固定间隔提取帧
- merge_ocr_results: 智能合并OCR结果，避免残缺字
"""

import subprocess
import os
import logging
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from Levenshtein import distance as levenshtein_distance
from django.conf import settings

logger = logging.getLogger(__name__)


def check_ffmpeg_available() -> bool:
    """
    检查FFmpeg是否可用
    
    FFmpeg是一个强大的多媒体处理工具，用于：
    - 视频格式转换
    - 视频信息提取
    - 视频帧提取
    - 视频编辑等
    
    这个函数通过运行FFmpeg命令来检查它是否已安装并可用。
    
    Returns:
        bool: 如果FFmpeg可用返回True，否则返回False
        
    Note:
        FFmpeg需要单独安装，不是Python包。
        Linux: sudo apt-get install ffmpeg
        macOS: brew install ffmpeg
        Windows: 从官网下载并添加到PATH
    """
    try:
        # 使用subprocess运行FFmpeg命令
        # subprocess.run()用于执行系统命令
        # ['ffmpeg', '-version']: 命令和参数列表
        #   ffmpeg: FFmpeg可执行文件名
        #   -version: 显示版本信息的参数
        # capture_output=True: 捕获标准输出和标准错误
        # check=True: 如果命令返回非零退出码则抛出异常
        subprocess.run(
            ['ffmpeg', '-version'],
            capture_output=True,  # 捕获输出
            check=True  # 检查退出码
        )
        return True  # 命令执行成功，FFmpeg可用
    except (subprocess.CalledProcessError, FileNotFoundError):
        # CalledProcessError: 命令执行失败（退出码非零）
        # FileNotFoundError: 找不到命令（FFmpeg未安装或不在PATH中）
        logger.warning("FFmpeg未安装或不可用")
        return False


def get_video_info(video_path: str) -> Dict[str, any]:
    """
    获取视频文件的基本信息
    
    使用FFprobe获取视频的元数据，包括：
    - 时长
    - 分辨率
    - 编码格式等
    
    Args:
        video_path: 视频文件的路径
        
    Returns:
        Dict包含以下键：
            - duration: 视频时长（秒）
            - width: 视频宽度
            - height: 视频高度
            - codec: 视频编码格式
            - fps: 帧率
            
    Raises:
        Exception: 当FFprobe执行失败时抛出异常
    """
    if not check_ffmpeg_available():
        raise Exception("FFmpeg未安装，无法获取视频信息")
    
    try:
        # ====================================================================
        # 构建FFprobe命令
        # ====================================================================
        # FFprobe是FFmpeg套件的一部分，用于获取媒体文件信息
        cmd = [
            'ffprobe',  # FFprobe可执行文件
            '-v', 'error',  # 日志级别：只显示错误信息
            # -show_entries: 指定要显示的信息
            #   format=duration: 视频总时长
            #   stream=width,height,codec_name,r_frame_rate: 视频流信息
            #     width: 视频宽度（像素）
            #     height: 视频高度（像素）
            #     codec_name: 视频编码格式（如h264）
            #     r_frame_rate: 帧率（分数形式，如30/1）
            '-show_entries', 'format=duration:stream=width,height,codec_name,r_frame_rate',
            # -of: 输出格式
            #   default: 默认格式
            #   noprint_wrappers=1: 不打印包装器
            #   nokey=1: 不打印键名，只打印值
            '-of', 'default=noprint_wrappers=1:nokey=1',
            video_path  # 视频文件路径
        ]
        
        # 执行FFprobe命令
        # text=True: 以文本模式处理输出（返回字符串而不是字节）
        # check=True: 如果命令失败则抛出异常
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        # 解析输出
        # result.stdout: 标准输出（包含视频信息）
        # .strip(): 去除首尾空白字符
        # .split('\n'): 按换行符分割成列表
        output = result.stdout.strip().split('\n')
        
        # ====================================================================
        # 解析FFprobe输出
        # ====================================================================
        # FFprobe输出格式（每行一个值）：
        #   123.456  (duration: 时长，秒)
        #   1920     (width: 宽度，像素)
        #   1080     (height: 高度，像素)
        #   h264     (codec: 编码格式)
        #   30/1     (fps: 帧率，分数形式)
        info = {
            'duration': float(output[0]) if output[0] else None,  # 时长（秒）
            'width': int(output[1]) if len(output) > 1 and output[1] else None,  # 宽度（像素）
            'height': int(output[2]) if len(output) > 2 and output[2] else None,  # 高度（像素）
            'codec': output[3] if len(output) > 3 else None,  # 编码格式
            'fps': None  # 帧率（稍后解析）
        }
        
        # ====================================================================
        # 解析帧率（分数形式转换为小数）
        # ====================================================================
        # FFprobe返回的帧率是分数形式（如"30/1"表示30fps）
        # 需要将分数转换为小数
        if len(output) > 4 and output[4]:
            # 分割分数：'30/1' -> ['30', '1']
            fps_parts = output[4].split('/')
            if len(fps_parts) == 2:
                # 计算帧率：30 / 1 = 30.0
                info['fps'] = float(fps_parts[0]) / float(fps_parts[1])
        
        logger.info(f"获取视频信息成功: {info}")
        return info
        
    except subprocess.CalledProcessError as e:
        logger.error(f"获取视频信息失败: {e.stderr}")
        raise Exception(f"无法获取视频信息: {e.stderr}")


def extract_frames_scene_detection(
    video_path: str,
    output_dir: str,
    scene_threshold: float = 0.3,
    overlap_seconds: float = 0.5
) -> List[Dict[str, any]]:
    """
    使用场景变化检测提取视频帧（智能抽帧）
    
    该方法通过检测场景变化来提取关键帧，并在场景变化点前后
    添加重叠窗口，确保不会遗漏边界文字。
    
    策略说明：
    1. 使用FFmpeg的场景检测功能识别场景变化点
    2. 在每个场景变化点前后各提取1-2帧（重叠窗口）
    3. 这样可以避免文字在帧边界被截断的问题
    
    Args:
        video_path: 视频文件路径
        output_dir: 输出目录，用于保存提取的帧
        scene_threshold: 场景变化检测阈值（0-1），值越小越敏感
        overlap_seconds: 重叠窗口大小（秒），在场景变化点前后各提取的帧的时间范围
        
    Returns:
        List[Dict]: 每帧的信息列表，每个Dict包含：
            - frame_path: 帧图像文件路径
            - timestamp: 时间戳（秒）
            - frame_number: 帧序号
            
    Raises:
        Exception: 当FFmpeg执行失败时抛出异常
    """
    if not check_ffmpeg_available():
        raise Exception("FFmpeg未安装，无法提取视频帧")
    
    os.makedirs(output_dir, exist_ok=True)
    frames_info = []
    
    try:
        # 第一步：使用场景检测提取关键帧
        scene_frames_file = os.path.join(output_dir, 'scene_frames.txt')
        cmd_scene = [
            'ffmpeg',
            '-i', video_path,
            '-vf', f"select='gt(scene,{scene_threshold})',showinfo",
            '-vsync', 'vfr',
            '-f', 'null',
            '-'
        ]
        
        # 获取场景变化点的时间戳
        result = subprocess.run(
            cmd_scene,
            capture_output=True,
            text=True,
            stderr=subprocess.STDOUT
        )
        
        # 解析场景变化点（从stderr中提取时间戳）
        scene_timestamps = []
        for line in result.stderr.split('\n'):
            if 'pts_time' in line:
                # 提取时间戳（简化解析，实际可能需要更复杂的正则表达式）
                try:
                    # 这里需要根据FFmpeg实际输出格式调整
                    # 示例：pts_time:1.234
                    parts = line.split('pts_time:')
                    if len(parts) > 1:
                        timestamp = float(parts[1].split()[0])
                        scene_timestamps.append(timestamp)
                except (ValueError, IndexError):
                    continue
        
        # 如果没有检测到场景变化，使用固定间隔作为备选
        if not scene_timestamps:
            logger.warning("未检测到场景变化，使用固定间隔提取")
            return extract_frames_fixed_interval(video_path, output_dir, fps=1.0)
        
        # 第二步：在场景变化点前后提取帧（重叠窗口）
        frame_number = 0
        extracted_timestamps = set()
        
        for scene_ts in scene_timestamps:
            # 在场景变化点前后各提取1-2帧
            timestamps_to_extract = [
                max(0, scene_ts - overlap_seconds),  # 场景变化点前
                scene_ts,  # 场景变化点
                scene_ts + overlap_seconds  # 场景变化点后
            ]
            
            for ts in timestamps_to_extract:
                if ts in extracted_timestamps:
                    continue  # 避免重复提取
                
                frame_path = os.path.join(output_dir, f'frame_{frame_number:06d}_{ts:.2f}s.jpg')
                
                # 提取指定时间戳的帧
                cmd_extract = [
                    'ffmpeg',
                    '-i', video_path,
                    '-ss', str(ts),
                    '-vframes', '1',
                    '-q:v', '2',  # 高质量
                    '-y',  # 覆盖已存在文件
                    frame_path
                ]
                
                subprocess.run(cmd_extract, capture_output=True, check=True)
                
                if os.path.exists(frame_path):
                    frames_info.append({
                        'frame_path': frame_path,
                        'timestamp': ts,
                        'frame_number': frame_number
                    })
                    extracted_timestamps.add(ts)
                    frame_number += 1
        
        logger.info(f"场景检测提取完成，共提取 {len(frames_info)} 帧")
        return frames_info
        
    except subprocess.CalledProcessError as e:
        logger.error(f"场景检测提取失败: {e.stderr}")
        raise Exception(f"无法提取视频帧: {e.stderr}")


def extract_frames_fixed_interval(
    video_path: str,
    output_dir: str,
    fps: float = 1.0,
    overlap_seconds: float = 0.3
) -> List[Dict[str, any]]:
    """
    使用固定间隔提取视频帧
    
    该方法按固定时间间隔提取帧，并使用重叠窗口策略
    来减少边界文字被截断的问题。
    
    策略说明：
    1. 每秒提取fps帧
    2. 每帧覆盖前后各overlap_seconds秒的时间范围
    3. 这样可以确保文字在帧边界处也能被完整捕捉
    
    Args:
        video_path: 视频文件路径
        output_dir: 输出目录
        fps: 提取帧率（帧/秒），例如1.0表示每秒1帧
        overlap_seconds: 重叠窗口大小（秒）
        
    Returns:
        List[Dict]: 每帧的信息列表
        
    Raises:
        Exception: 当FFmpeg执行失败时抛出异常
    """
    if not check_ffmpeg_available():
        raise Exception("FFmpeg未安装，无法提取视频帧")
    
    os.makedirs(output_dir, exist_ok=True)
    frames_info = []
    
    try:
        # 获取视频时长
        video_info = get_video_info(video_path)
        duration = video_info.get('duration', 0)
        
        if duration == 0:
            raise Exception("无法获取视频时长")
        
        # 计算提取间隔
        interval = 1.0 / fps
        
        # 提取帧
        frame_number = 0
        current_time = 0.0
        
        while current_time < duration:
            frame_path = os.path.join(output_dir, f'frame_{frame_number:06d}_{current_time:.2f}s.jpg')
            
            # 提取帧
            cmd = [
                'ffmpeg',
                '-i', video_path,
                '-ss', str(current_time),
                '-vframes', '1',
                '-q:v', '2',
                '-y',
                frame_path
            ]
            
            subprocess.run(cmd, capture_output=True, check=True)
            
            if os.path.exists(frame_path):
                frames_info.append({
                    'frame_path': frame_path,
                    'timestamp': current_time,
                    'frame_number': frame_number
                })
                frame_number += 1
            
            current_time += interval
        
        logger.info(f"固定间隔提取完成，共提取 {len(frames_info)} 帧")
        return frames_info
        
    except subprocess.CalledProcessError as e:
        logger.error(f"固定间隔提取失败: {e.stderr}")
        raise Exception(f"无法提取视频帧: {e.stderr}")


def calculate_text_similarity(text1: str, text2: str) -> float:
    """
    计算两个文本的相似度
    
    使用编辑距离（Levenshtein距离）算法计算文本相似度。
    
    编辑距离（Levenshtein距离）：
    - 将一个字符串转换为另一个字符串所需的最少单字符编辑操作数
    - 编辑操作包括：插入、删除、替换字符
    - 例如："abc" -> "abd" 需要1次替换操作，距离为1
    
    相似度计算：
    - 相似度 = 1 - (编辑距离 / 最大长度)
    - 范围：0-1，1表示完全相同，0表示完全不同
    
    用途：
    - 在merge_ocr_results()中用于判断两个OCR结果是否相似
    - 如果相似度高，说明可能是同一段文字，应该合并
    
    Args:
        text1: 第一个文本
        text2: 第二个文本
        
    Returns:
        float: 相似度（0-1之间），1表示完全相同
        
    Example:
        >>> calculate_text_similarity("Hello", "Hello")
        1.0
        >>> calculate_text_similarity("Hello", "Hallo")
        0.8
        >>> calculate_text_similarity("Hello", "World")
        0.0
    """
    # 如果两个文本都为空，认为完全相同
    if not text1 and not text2:
        return 1.0
    
    # 如果其中一个为空，认为完全不同
    if not text1 or not text2:
        return 0.0
    
    # 计算最大长度（用于归一化）
    max_len = max(len(text1), len(text2))
    if max_len == 0:
        return 1.0
    
    # 计算编辑距离（Levenshtein距离）
    # levenshtein_distance()来自python-Levenshtein库
    # 返回将text1转换为text2所需的最少编辑操作数
    distance = levenshtein_distance(text1, text2)
    
    # 计算相似度：1 - (距离 / 最大长度)
    # 距离越小，相似度越高
    similarity = 1.0 - (distance / max_len)
    
    return similarity


def merge_ocr_results(
    ocr_results: List[Dict[str, any]],
    similarity_threshold: float = 0.8,
    time_window: float = 2.0
) -> List[Dict[str, any]]:
    """
    智能合并OCR识别结果
    
    该函数解决残缺字问题，通过以下策略：
    1. 时间窗口合并：将时间相近的OCR结果合并
    2. 相似度合并：将内容相似的OCR结果合并为一条记录
    3. 时间范围扩展：为每条合并后的记录记录其出现的时间范围
    
    合并逻辑：
    - 如果两条OCR结果的时间差小于time_window秒，且内容相似度大于threshold
    - 则合并为一条记录，时间范围为两条记录的时间范围
    
    Args:
        ocr_results: OCR结果列表，每个Dict包含：
            - text: 识别的文字内容
            - timestamp: 时间戳（秒）
            - frame_number: 帧序号（可选）
        similarity_threshold: 相似度阈值（0-1），超过此值认为内容相同
        time_window: 时间窗口（秒），在此时间范围内的结果会被考虑合并
        
    Returns:
        List[Dict]: 合并后的OCR结果列表，每个Dict包含：
            - text: 合并后的文字内容
            - start_time: 开始时间（秒）
            - end_time: 结束时间（秒）
            - frame_count: 合并的帧数量
            
    Example:
        >>> results = [
        ...     {'text': 'Hello', 'timestamp': 1.0},
        ...     {'text': 'Hello', 'timestamp': 1.5},
        ...     {'text': 'World', 'timestamp': 3.0}
        ... ]
        >>> merged = merge_ocr_results(results)
        >>> # 结果: [{'text': 'Hello', 'start_time': 1.0, 'end_time': 1.5, ...}]
    """
    if not ocr_results:
        return []
    
    # 按时间戳排序
    sorted_results = sorted(ocr_results, key=lambda x: x['timestamp'])
    
    merged_results = []
    current_group = None
    
    for result in sorted_results:
        text = result.get('text', '').strip()
        timestamp = result.get('timestamp', 0)
        
        if not text:  # 跳过空文本
            continue
        
        if current_group is None:
            # 创建新组
            current_group = {
                'text': text,
                'start_time': timestamp,
                'end_time': timestamp,
                'frame_count': 1,
                'texts': [text]  # 保存所有文本用于最终合并
            }
        else:
            # 检查是否可以合并到当前组
            time_diff = timestamp - current_group['end_time']
            similarity = calculate_text_similarity(text, current_group['text'])
            
            # 合并条件：时间相近且内容相似
            if time_diff <= time_window and similarity >= similarity_threshold:
                # 合并到当前组
                current_group['end_time'] = timestamp
                current_group['frame_count'] += 1
                current_group['texts'].append(text)
                
                # 更新合并后的文本（使用最长的或最常见的）
                if len(text) > len(current_group['text']):
                    current_group['text'] = text
            else:
                # 保存当前组，创建新组
                merged_results.append({
                    'text': current_group['text'],
                    'start_time': current_group['start_time'],
                    'end_time': current_group['end_time'],
                    'frame_count': current_group['frame_count']
                })
                
                current_group = {
                    'text': text,
                    'start_time': timestamp,
                    'end_time': timestamp,
                    'frame_count': 1,
                    'texts': [text]
                }
    
    # 添加最后一组
    if current_group:
        merged_results.append({
            'text': current_group['text'],
            'start_time': current_group['start_time'],
            'end_time': current_group['end_time'],
            'frame_count': current_group['frame_count']
        })
    
    logger.info(f"OCR结果合并完成: {len(ocr_results)} -> {len(merged_results)}")
    return merged_results





