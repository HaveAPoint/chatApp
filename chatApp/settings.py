"""
Django项目配置文件（settings.py）

这个文件包含了Django项目的所有配置信息，是Django项目的核心配置文件。
Django在启动时会读取这个文件中的所有设置。

重要概念：
- 设置文件定义了项目的数据库、应用、中间件、模板等配置
- 可以通过环境变量覆盖某些设置（用于不同环境：开发/测试/生产）
- 生产环境必须修改SECRET_KEY和DEBUG设置

配置文件结构：
1. 路径配置：项目根目录路径
2. 安全设置：密钥、调试模式、允许的主机
3. 应用配置：已安装的应用列表
4. 中间件配置：请求处理中间件
5. URL配置：根URL配置
6. 模板配置：模板引擎设置
7. 数据库配置：数据库连接信息
8. 密码验证：用户密码验证规则
9. 国际化：语言和时区设置
10. 静态文件：CSS、JS、图片等静态资源
11. 媒体文件：用户上传的文件

学习要点：
- 每个Django项目都必须有这个文件
- 修改配置后通常需要重启开发服务器
- 某些配置（如INSTALLED_APPS）的顺序很重要

更多信息：
- https://docs.djangoproject.com/en/4.2/topics/settings/
- https://docs.djangoproject.com/en/4.2/ref/settings/
"""

# 导入Path类，用于处理文件路径
# pathlib是Python 3.4+引入的现代路径处理库，比os.path更易用
from pathlib import Path

# ============================================================================
# 路径配置
# ============================================================================

# 项目根目录路径
# __file__: 当前文件的路径（settings.py的路径）
# .resolve(): 解析为绝对路径
# .parent: 获取父目录（chatApp目录）
# .parent: 再次获取父目录（项目根目录）
# 例如：如果settings.py在 /home/user/project/chatApp/settings.py
# 那么BASE_DIR就是 /home/user/project/
# 这个路径用于构建项目中其他文件的相对路径
BASE_DIR = Path(__file__).resolve().parent.parent


# ============================================================================
# 安全设置（Security Settings）
# ============================================================================
# 注意：以下设置仅适用于开发环境，生产环境必须修改！

# SECRET_KEY（密钥）
# 用途：用于加密签名、会话、CSRF令牌等安全相关功能
# 重要性：这是Django最重要的安全设置之一
# 警告：
#   - 生产环境必须使用随机生成的强密钥
#   - 绝对不能将密钥提交到版本控制系统（Git）
#   - 建议使用环境变量存储：SECRET_KEY = os.environ.get('SECRET_KEY')
#   - 如果密钥泄露，必须立即更换，所有用户会话将失效
# 生成新密钥：python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
SECRET_KEY = 'django-insecure-k)+^3uqfau7^e7vi-r=tult@b@d79txe@nhv+@^(ps^y7d-5zf'

# DEBUG（调试模式）
# 用途：控制Django是否显示详细的错误页面
# True（开发模式）：
#   - 显示详细的错误信息和堆栈跟踪
#   - 自动重新加载代码更改
#   - 显示所有SQL查询
# False（生产模式）：
#   - 只显示通用错误页面
#   - 性能更好
#   - 更安全（不暴露内部信息）
# 警告：生产环境必须设置为False！
DEBUG = True

# ALLOWED_HOSTS（允许的主机）
# 用途：指定哪些主机/域名可以访问此Django站点
# 安全功能：防止HTTP Host头攻击
# 开发环境：通常为空列表[]，允许所有主机
# 生产环境：必须设置为实际域名，例如：['example.com', 'www.example.com']
# 注意：如果DEBUG=False，此列表不能为空
ALLOWED_HOSTS = []


# ============================================================================
# 应用配置（Application Definition）
# ============================================================================

# INSTALLED_APPS（已安装的应用列表）
# 用途：告诉Django哪些应用是项目的一部分
# 顺序：某些应用可能依赖其他应用，顺序很重要
# 
# Django内置应用说明：
# - django.contrib.admin: Django管理后台，提供Web界面管理数据
# - django.contrib.auth: 用户认证系统，处理用户登录、权限等
# - django.contrib.contenttypes: 内容类型框架，用于通用关系
# - django.contrib.sessions: 会话框架，用于存储用户会话数据
# - django.contrib.messages: 消息框架，用于显示一次性消息（如成功提示）
# - django.contrib.staticfiles: 静态文件管理，收集和提供CSS、JS等文件
#
# 自定义应用：
# - video: 本项目的视频OCR应用，包含视频上传、处理、OCR识别等功能
INSTALLED_APPS = [
    # Django内置应用（按依赖顺序排列）
    'django.contrib.admin',          # 管理后台
    'django.contrib.auth',           # 用户认证系统
    'django.contrib.contenttypes',   # 内容类型框架
    'django.contrib.sessions',       # 会话框架
    'django.contrib.messages',       # 消息框架
    'django.contrib.staticfiles',    # 静态文件管理
    
    # 自定义应用
    'video',  # 视频OCR应用 - 处理视频上传、OCR识别等功能
]

# MIDDLEWARE（中间件）
# 用途：在请求和响应之间执行的中间件组件
# 工作原理：请求从上到下经过中间件，响应从下到上返回
# 顺序很重要：每个中间件可能依赖前面的中间件
#
# 中间件说明（按执行顺序）：
# 1. SecurityMiddleware: 安全相关功能，如HTTPS重定向、安全头设置
# 2. SessionMiddleware: 会话管理，在请求中提供session对象
# 3. CommonMiddleware: 通用功能，如URL规范化、禁止用户代理
# 4. CsrfViewMiddleware: CSRF保护，防止跨站请求伪造攻击
# 5. AuthenticationMiddleware: 用户认证，在请求中提供user对象
# 6. MessageMiddleware: 消息框架，处理一次性消息（如成功提示）
# 7. XFrameOptionsMiddleware: 防止点击劫持攻击
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',           # 安全中间件
    'django.contrib.sessions.middleware.SessionMiddleware',    # 会话中间件
    'django.middleware.common.CommonMiddleware',                # 通用中间件
    'django.middleware.csrf.CsrfViewMiddleware',               # CSRF保护中间件
    'django.contrib.auth.middleware.AuthenticationMiddleware',  # 认证中间件
    'django.contrib.messages.middleware.MessageMiddleware',    # 消息中间件
    'django.middleware.clickjacking.XFrameOptionsMiddleware',  # 点击劫持保护中间件
]

# ROOT_URLCONF（根URL配置）
# 用途：指定Django项目的根URL配置文件
# 值：Python模块路径，指向包含urlpatterns的模块
# 工作原理：Django从该文件开始匹配URL路由
ROOT_URLCONF = 'chatApp.urls'  # 指向 chatApp/urls.py 文件

# TEMPLATES（模板配置）
# 用途：配置Django模板引擎
# 模板：用于生成HTML页面的文件，通常使用Django模板语言（DTL）
TEMPLATES = [
    {
        # 模板后端：使用Django内置的模板引擎
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        
        # 模板目录：指定查找模板的目录列表
        # BASE_DIR / 'templates' 表示项目根目录下的templates文件夹
        # Django会按顺序在这些目录中查找模板文件
        'DIRS': [BASE_DIR / 'templates'],
        
        # 应用目录：是否在每个应用的templates目录中查找模板
        # True表示会在每个INSTALLED_APPS的templates子目录中查找
        # 例如：video/templates/video/upload.html
        'APP_DIRS': True,
        
        # 模板选项
        'OPTIONS': {
            # 上下文处理器：自动向所有模板添加变量的函数
            # 这些变量在所有模板中都可以直接使用，无需手动传递
            'context_processors': [
                'django.template.context_processors.debug',      # 添加debug变量
                'django.template.context_processors.request',    # 添加request对象
                'django.contrib.auth.context_processors.auth',   # 添加user对象（当前登录用户）
                'django.contrib.messages.context_processors.messages',  # 添加messages（消息列表）
            ],
        },
    },
]

# WSGI_APPLICATION（WSGI应用）
# 用途：指定WSGI应用对象，用于部署到生产服务器
# WSGI：Web Server Gateway Interface，Python Web应用的标准接口
# 值：指向wsgi.py模块中的application变量
WSGI_APPLICATION = 'chatApp.wsgi.application'

# ============================================================================
# 数据库配置（Database Configuration）
# ============================================================================
# Django使用ORM（对象关系映射），可以通过Python代码操作数据库
# 不需要直接写SQL，Django会自动生成SQL语句

# DATABASES（数据库配置）
# 用途：配置项目使用的数据库
# 支持多种数据库：SQLite、PostgreSQL、MySQL、Oracle等
DATABASES = {
    # 'default'是默认数据库连接的名称
    'default': {
        # 数据库引擎：指定使用哪种数据库
        # sqlite3是轻量级文件数据库，适合开发和测试
        # 生产环境建议使用PostgreSQL或MySQL
        'ENGINE': 'django.db.backends.sqlite3',
        
        # 数据库文件路径
        # SQLite将数据存储在单个文件中
        # BASE_DIR / 'db.sqlite3' 表示项目根目录下的db.sqlite3文件
        'NAME': BASE_DIR / 'db.sqlite3',
        
        # 注意：SQLite不需要USER、PASSWORD、HOST等配置
        # 其他数据库需要额外配置，例如：
        # 'USER': 'your_username',
        # 'PASSWORD': 'your_password',
        # 'HOST': 'localhost',
        # 'PORT': '5432',
    }
}


# ============================================================================
# 密码验证（Password Validation）
# ============================================================================
# 用途：定义用户密码的验证规则，提高密码安全性
# 这些验证器在用户创建或修改密码时自动执行

AUTH_PASSWORD_VALIDATORS = [
    {
        # 验证密码与用户属性（用户名、邮箱等）的相似度
        # 防止用户使用与用户名相似的弱密码
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        # 验证密码最小长度
        # 默认最小长度为8个字符
        # 可以通过OPTIONS自定义：{'OPTIONS': {'min_length': 10}}
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        # 验证密码是否为常见密码
        # 检查密码是否在常见密码列表中（如"password123"）
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        # 验证密码是否完全由数字组成
        # 防止用户使用纯数字密码（如"12345678"）
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# ============================================================================
# 国际化设置（Internationalization）
# ============================================================================
# 用途：配置项目的语言、时区等国际化相关设置

# LANGUAGE_CODE（语言代码）
# 用途：设置项目的默认语言
# 'zh-hans': 简体中文
# 其他选项：'en-us'（英语）、'zh-hant'（繁体中文）、'ja'（日语）等
# 注意：需要确保对应的语言包已安装
LANGUAGE_CODE = 'zh-hans'

# TIME_ZONE（时区）
# 用途：设置项目的默认时区
# 'Asia/Shanghai': 中国标准时间（UTC+8）
# 其他选项：'UTC'（协调世界时）、'America/New_York'（美国东部时间）等
# 注意：时区设置影响datetime字段的显示和存储
TIME_ZONE = 'Asia/Shanghai'

# USE_I18N（启用国际化）
# 用途：是否启用Django的国际化框架
# True: 启用多语言支持，可以使用翻译功能
# False: 禁用国际化，只使用默认语言
USE_I18N = True

# USE_TZ（使用时区）
# 用途：是否启用时区支持
# True: Django会使用时区感知的datetime对象
#      所有datetime字段会存储为UTC时间，显示时转换为本地时区
# False: 使用本地时间，不进行时区转换
# 建议：生产环境应设置为True
USE_TZ = True


# ============================================================================
# 静态文件配置（Static Files）
# ============================================================================
# 静态文件：CSS样式表、JavaScript脚本、图片等不会改变的文件
# 这些文件在开发和生产环境中的处理方式不同

# STATIC_URL（静态文件URL前缀）
# 用途：指定静态文件在URL中的前缀
# 例如：如果STATIC_URL = 'static/'，那么CSS文件的URL是 /static/css/style.css
# 注意：这个值必须以斜杠结尾
STATIC_URL = 'static/'

# STATIC_ROOT（静态文件收集目录）
# 用途：运行 collectstatic 命令后，所有静态文件会被收集到这个目录
# 生产环境：Web服务器（如Nginx）会直接从这个目录提供静态文件
# 开发环境：Django会自动处理静态文件，不需要运行collectstatic
# 注意：这个目录不应该在版本控制中，应该在.gitignore中忽略
STATIC_ROOT = BASE_DIR / 'staticfiles'

# ============================================================================
# 媒体文件配置（Media Files）
# ============================================================================
# 媒体文件：用户上传的文件，如视频、图片等
# 与静态文件的区别：静态文件是项目的一部分，媒体文件是用户上传的

# MEDIA_URL（媒体文件URL前缀）
# 用途：指定媒体文件在URL中的前缀
# 例如：如果MEDIA_URL = 'media/'，那么上传的视频URL是 /media/videos/video.mp4
# 注意：这个值必须以斜杠结尾
MEDIA_URL = 'media/'

# MEDIA_ROOT（媒体文件存储目录）
# 用途：指定用户上传文件的存储位置
# 例如：视频文件会存储在 MEDIA_ROOT/uploaded_videos/ 目录下
# 注意：这个目录不应该在版本控制中，应该在.gitignore中忽略
MEDIA_ROOT = BASE_DIR / 'media'

# ============================================================================
# 文件上传限制（File Upload Limits）
# ============================================================================

# FILE_UPLOAD_MAX_MEMORY_SIZE（文件上传内存限制）
# 用途：指定文件在内存中处理的最大大小（字节）
# 104857600 = 100MB
# 小于此大小的文件会完全加载到内存中处理
# 大于此大小的文件会先保存到临时文件，然后处理
FILE_UPLOAD_MAX_MEMORY_SIZE = 104857600  # 100MB

# DATA_UPLOAD_MAX_MEMORY_SIZE（数据上传内存限制）
# 用途：指定非文件数据（如表单数据）在内存中处理的最大大小（字节）
# 104857600 = 100MB
# 防止恶意用户发送过大的POST请求
DATA_UPLOAD_MAX_MEMORY_SIZE = 104857600  # 100MB

# ============================================================================
# 默认主键字段类型（Default Primary Key Field Type）
# ============================================================================

# DEFAULT_AUTO_FIELD（默认自动主键字段）
# 用途：指定Django模型自动生成的主键字段类型
# BigAutoField: 64位整数，范围更大（适合大型应用）
# AutoField: 32位整数（Django 3.2之前的默认值）
# 注意：这个设置只影响新创建的模型，已有模型不受影响
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
