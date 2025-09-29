@echo off
echo 正在启动多模态服务器...

REM 设置PYTHONPATH以确保使用本地安装的包而不是conda环境
set PYTHONPATH=%CD%;%PYTHONPATH%

REM 不再需要强制安装依赖，因为我们已经在代码中处理了兼容性问题

REM 检查是否已安装ffmpeg
where ffmpeg >nul 2>&1
if %errorlevel% neq 0 (
    echo 警告: 未检测到ffmpeg，音频处理功能可能无法正常工作。
    echo 请访问 https://ffmpeg.org/download.html 下载并安装ffmpeg，
    echo 或者运行以下命令安装: pip install ffmpeg-python
    echo.
    echo 详细安装步骤请参考 ffmpeg安装指南.md 文档
    echo.
    echo 按任意键继续启动服务器...
    pause >nul
)

echo 启动服务器...
python multimodal_server.py

pause