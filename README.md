# Django 视频 OCR 应用

基于 Django 4.2 + Python 3.9，集成豆包多模态 API（OpenAI 兼容），实现视频画面文字提取功能。

## 功能特性

### 1. 视频画面字提取（OCR）
- **视频上传**：支持 MP4、AVI、MOV、MKV、WEBM 格式
- **智能抽帧**：
  - 场景检测模式：自动识别场景变化点，提取关键帧
  - 固定间隔模式：按指定频率提取帧
  - 重叠窗口策略：避免边界文字被截断
- **OCR识别**：使用豆包多模态API（doubao-seed-1-6-251015）识别视频帧中的文字
- **智能合并**：使用编辑距离算法合并相似文字，解决残缺字问题
- **结果展示**：按时间轴展示识别结果，支持复制导出

## 技术栈

- **后端框架**：Django 4.2
- **Python版本**：3.9
- **API客户端**：OpenAI SDK（兼容豆包多模态API）
- **视频处理**：FFmpeg
- **图像处理**：Pillow、OpenCV
- **文本相似度**：python-Levenshtein

## 项目结构

```
chatApp/
├── chatApp/              # 主项目配置
│   ├── settings.py       # Django设置
│   ├── urls.py          # 主URL配置
│   └── wsgi.py
├── video/                # 视频OCR应用
│   ├── models.py        # 数据模型（VideoFile, VideoFrame, OCRResult）
│   ├── views.py         # 视图函数
│   ├── urls.py          # URL路由
│   ├── utils.py         # 视频处理工具（抽帧、合并）
│   ├── tests/           # 单元测试
│   └── templates/       # 模板文件
├── config/              # 配置模块
│   └── api_config.py    # API配置
├── utils/                # 工具模块
│   ├── api_client.py    # API客户端封装
│   └── tests/           # 单元测试
├── templates/           # 基础模板
├── static/              # 静态文件（CSS、JS）
└── media/               # 媒体文件（上传的视频、提取的帧）
```

## 安装和运行

### 1. 环境要求
- Python 3.9
- FFmpeg（用于视频处理）
- 虚拟环境（推荐）

### 2. 安装依赖

```bash
# 激活虚拟环境
source .venv/bin/activate

# 安装Python依赖
pip install -r requirements.txt

# 安装FFmpeg（Ubuntu/Debian）
sudo apt-get install ffmpeg

# 安装FFmpeg（macOS）
brew install ffmpeg
```

### 3. 配置

编辑 `config/api_config.py` 配置API密钥和端点（已配置默认值）。

### 4. 数据库迁移

```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. 运行开发服务器

```bash
python manage.py runserver
```

访问 http://127.0.0.1:8000 查看应用。

## 使用说明

### 视频OCR功能

1. **上传视频**
   - 访问 `/video/upload/` 或点击导航栏的"视频OCR"
   - 选择视频文件（最大100MB）
   - 输入视频标题（可选）
   - 点击"上传视频"

2. **处理视频**
   - 上传成功后自动跳转到处理页面
   - 选择提取方式：
     - **场景检测**（推荐）：智能识别场景变化，避免遗漏关键帧
     - **固定间隔**：按指定频率提取帧
   - 点击"开始处理"
   - 等待处理完成（处理时间取决于视频长度和帧数）

3. **查看结果**
   - 处理完成后点击"查看结果"
   - 可以查看合并后的文字内容和详细的时间轴结果
   - 支持复制全部文字

## 核心算法说明

### 解决残缺字问题的策略

1. **场景检测 + 重叠窗口**
   - 使用FFmpeg的场景检测功能识别场景变化点
   - 在场景变化点前后各提取1-2帧（重叠窗口）
   - 确保边界文字不会被截断

2. **智能合并算法**
   - 使用编辑距离（Levenshtein距离）计算文本相似度
   - 将时间相近且内容相似的OCR结果合并
   - 记录每条文字的出现时间范围（开始时间-结束时间）
   - 避免简单去重导致的文字丢失

### OCR结果合并流程

```
提取帧 → OCR识别 → 时间对齐 → 相似度计算 → 智能合并 → 输出结果
```

## 测试

运行单元测试：

```bash
# 运行所有测试
python manage.py test

# 运行特定应用的测试
python manage.py test video
python manage.py test utils

# 运行特定测试文件
python manage.py test video.tests.test_models
```

## API配置

API配置位于 `config/api_config.py`：

- **API端点**：https://ark.cn-beijing.volces.com/api/v3
- **API密钥**：从环境变量 `ARK_API_KEY` 读取
- **支持模型**：
  - doubao-seed-1-6-251015（默认）

**重要**：使用前必须设置环境变量：
```bash
export ARK_API_KEY='your-api-key-here'
```

详细设置说明请参考 `SETUP.md`。

## 注意事项

1. **FFmpeg要求**：视频处理功能需要安装FFmpeg
2. **文件大小限制**：默认最大100MB，可在 `config/api_config.py` 中修改
3. **处理时间**：视频OCR处理可能需要较长时间，取决于视频长度和帧数
4. **API限制**：注意API的调用频率和token限制

## 开发说明

### 代码规范

- 所有模块都有详细的文档字符串和注释
- 遵循Django最佳实践
- 使用类型提示（Type Hints）提高代码可读性

### 扩展功能

- 可以添加用户认证系统
- 可以添加异步任务处理（Celery）提高性能
- 可以添加视频预览功能
- 可以添加OCR结果导出功能（PDF、TXT等）

## 许可证

本项目仅供学习和研究使用。

## 作者

开发时间：2024年

