# 更新日志

## 2024-11-28 - 视频直接上传功能

### 主要变更

1. **API配置更新**
   - 更新API密钥为：`sk-XFQ6cHhxwLJXMIEFAS4cZ9Ly1O0hi4YO00Xd3TVIP0Fkqy9R`
   - 更新视频处理模型为：
     - `gemini-2.5-flash-image`（默认）

2. **视频处理方式变更**
   - **之前**：抽帧处理（场景检测或固定间隔）→ 逐帧OCR → 合并结果
   - **现在**：直接上传整个视频文件 → API直接处理 → 返回结果
   - 简化了处理流程，提高了效率
   - 不再需要FFmpeg进行抽帧（但仍用于获取视频信息）

3. **代码修改**
   - `config/api_config.py`：更新API密钥和模型配置
   - `utils/api_client.py`：实现 `process_video_ocr()` 函数，支持直接上传视频
   - `video/views.py`：简化 `video_process()` 视图，移除抽帧逻辑
   - `video/templates/video/process.html`：更新UI，改为模型选择

### 技术细节

- 视频文件通过base64编码后以data URL格式发送到API
- 使用 `image_url` 类型（某些API将视频视为特殊图像格式）
- 支持多种视频格式：MP4、AVI、MOV、MKV、WEBM
- 自动识别MIME类型

### 测试状态

- ✅ 单元测试通过（7个测试）
- ✅ API客户端初始化成功
- ✅ 开发服务器启动成功
- ⏳ 等待实际视频文件测试

### 使用说明

1. 访问 http://127.0.0.1:8000/video/upload/ 上传视频
2. 点击"开始处理"（使用默认模型 gemini-2.5-flash-image）
3. 等待API处理完成
4. 查看识别结果

### 注意事项

- 视频文件大小限制：100MB
- 处理时间取决于视频长度和API响应速度
- 如果API不支持直接视频输入，可能需要调整实现方式

