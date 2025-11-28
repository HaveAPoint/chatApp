# 豆包多模态API设置说明

## 环境变量设置

### 设置 ARK_API_KEY

在启动服务器前，必须设置环境变量 `ARK_API_KEY`：

```bash
# 方法1：临时设置（当前终端会话有效）
export ARK_API_KEY='your-ark-api-key-here'

# 方法2：在启动命令中设置
ARK_API_KEY='your-ark-api-key-here' python manage.py runserver

# 方法3：永久设置（推荐）
# 编辑 ~/.bashrc 或 ~/.zshrc
echo 'export ARK_API_KEY="your-ark-api-key-here"' >> ~/.bashrc
source ~/.bashrc
```

### 验证环境变量

```bash
# 检查环境变量是否设置
echo $ARK_API_KEY

# 如果输出为空，说明未设置
```

## 启动服务器

```bash
# 1. 确保已设置环境变量
export ARK_API_KEY='your-api-key'

# 2. 激活虚拟环境
source .venv/bin/activate

# 3. 启动服务器
python manage.py runserver
```

## API配置信息

- **API端点**: `https://ark.cn-beijing.volces.com/api/v3`
- **模型终端**: 默认 `doubao-seed-1-6-251015`，如需修改请在代码中调整
- **API密钥**: 从环境变量 `ARK_API_KEY` 读取

## 注意事项

1. **必须设置环境变量**：如果未设置 `ARK_API_KEY`，程序会抛出 `ValueError` 异常
2. **视频格式**：支持 MP4、AVI、MOV、MKV、WEBM
3. **文件大小限制**：最大 100MB
4. **处理方式**：直接上传整个视频文件，无需抽帧

## 测试

运行测试脚本验证配置：

```bash
python test_video_upload.py
```

如果环境变量未设置，会提示错误信息。


