#!/usr/bin/env python
"""
测试视频直接上传OCR功能

该脚本用于测试直接上传视频文件到API进行OCR识别。
"""

import os
import sys
import django

# 设置Django环境
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chatApp.settings')
django.setup()

from utils.api_client import get_api_client, process_video_ocr
from config.api_config import MODELS

def test_video_ocr():
    """测试视频OCR功能"""
    print("=" * 60)
    print("测试视频直接上传OCR功能")
    print("=" * 60)
    
    # 检查是否有测试视频文件
    test_video_path = input("请输入视频文件路径（或按Enter跳过）: ").strip()
    
    if not test_video_path or not os.path.exists(test_video_path):
        print("\n未提供有效的视频文件，跳过实际API测试")
        print("测试API客户端初始化...")
        
        try:
            client = get_api_client()
            print("✓ API客户端初始化成功")
            print(f"  - API端点: {client.base_url}")
            print(f"  - 模型列表: {MODELS['vision']}")
        except Exception as e:
            print(f"✗ API客户端初始化失败: {e}")
            return False
        
        print("\n所有基础测试通过！")
        return True
    
    # 测试实际视频上传
    print(f"\n开始处理视频: {test_video_path}")
    print(f"文件大小: {os.path.getsize(test_video_path) / (1024*1024):.2f} MB")
    
    try:
        client = get_api_client()
        
        # 使用豆包多模态模型
        model = MODELS['vision']['default']
        print(f"使用模型: {model}")
        print("注意：需要设置环境变量 ARK_API_KEY")
        
        result = process_video_ocr(
            client,
            test_video_path,
            model=model
        )
        
        print("\n" + "=" * 60)
        print("OCR识别成功！")
        print("=" * 60)
        print(f"\n模型: {result['model']}")
        print(f"Token使用: {result['usage']['total_tokens']}")
        print(f"  - 提示词Token: {result['usage']['prompt_tokens']}")
        print(f"  - 完成Token: {result['usage']['completion_tokens']}")
        print("\n识别结果:")
        print("-" * 60)
        print(result['content'])
        print("-" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n✗ 处理失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_video_ocr()
    sys.exit(0 if success else 1)

