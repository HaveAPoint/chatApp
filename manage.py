#!/usr/bin/env python
"""
Django项目管理脚本（manage.py）

这个文件是Django项目的命令行管理工具，用于执行各种管理任务。
它是每个Django项目的入口点，提供了丰富的命令行功能。

主要功能：
1. 运行开发服务器：python manage.py runserver
2. 数据库迁移：python manage.py migrate
3. 创建超级用户：python manage.py createsuperuser
4. 创建应用：python manage.py startapp <app_name>
5. 运行测试：python manage.py test
6. 收集静态文件：python manage.py collectstatic

工作原理：
- 设置Django设置模块的环境变量
- 导入Django的管理命令执行器
- 将命令行参数传递给Django处理

学习要点：
- 这是Django项目的标准入口文件，每个Django项目都有这个文件
- 通过这个文件可以访问Django的所有管理命令
- 第一行的shebang（#!/usr/bin/env python）使得文件可以直接执行
"""

# 导入必要的标准库模块
import os  # 用于操作系统相关功能，如环境变量
import sys  # 用于系统相关参数和函数，如命令行参数


def main():
    """
    Django管理命令的主入口函数
    
    这个函数负责：
    1. 设置Django设置模块的环境变量
    2. 导入并执行Django的管理命令
    
    工作流程：
    1. 设置DJANGO_SETTINGS_MODULE环境变量，告诉Django使用哪个设置文件
    2. 尝试导入Django的管理模块
    3. 如果导入失败，给出友好的错误提示
    4. 如果成功，执行命令行参数对应的Django命令
    
    环境变量说明：
    - DJANGO_SETTINGS_MODULE: 指定Django设置模块的路径
      'chatApp.settings' 表示使用 chatApp 目录下的 settings.py 文件
      这个环境变量必须在导入Django之前设置
    
    异常处理：
    - 如果Django未安装或不在Python路径中，会抛出ImportError
    - 常见原因：忘记激活虚拟环境、Django未安装、Python路径配置错误
    """
    # 设置Django设置模块的环境变量
    # setdefault: 如果环境变量已存在则不修改，不存在则设置为指定值
    # 这允许用户通过环境变量覆盖默认设置（用于不同环境：开发/测试/生产）
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chatApp.settings')
    
    try:
        # 导入Django的管理命令执行器
        # 这个模块负责解析命令行参数并执行对应的Django命令
        # 必须在设置环境变量之后导入，因为Django在导入时会读取环境变量
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        # 如果导入失败，抛出更友好的错误信息
        # 这通常发生在以下情况：
        # 1. Django未安装（pip install django）
        # 2. 虚拟环境未激活（source venv/bin/activate）
        # 3. Django不在PYTHONPATH中
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    
    # 执行Django管理命令
    # sys.argv: 包含命令行参数的列表
    # 例如：python manage.py runserver -> sys.argv = ['manage.py', 'runserver']
    # execute_from_command_line会解析这些参数并执行对应的命令
    execute_from_command_line(sys.argv)


# Python程序的入口点
# 当直接运行此文件时（python manage.py），会执行main()函数
# 如果作为模块导入（import manage），则不会执行main()
# 这是Python的标准做法，确保脚本既可以独立运行，也可以被导入
if __name__ == '__main__':
    main()
