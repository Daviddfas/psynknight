#!/bin/bash

echo "正在启动多模态服务器..."

# 设置PYTHONPATH以确保使用本地安装的包
export PYTHONPATH="$PWD:$PYTHONPATH"

# 检查ffmpeg文件夹是否存在
FFMPEG_DIR="$PWD/ffmpeg_files"
if [ -d "$FFMPEG_DIR" ]; then
    echo "检测到本地ffmpeg目录: $FFMPEG_DIR"
    
    # 查找ffmpeg可执行文件
    FFMPEG_EXEC=""
    
    # 尝试查找可能的ffmpeg可执行文件路径
    for POSSIBLE_PATH in "$FFMPEG_DIR/ffmpeg" "$FFMPEG_DIR/ffmp/ffmpeg" "$FFMPEG_DIR/*/ffmpeg" "$FFMPEG_DIR/*/*/ffmpeg" "$FFMPEG_DIR/*/*/*/ffmpeg"; do
        if [ -f "$POSSIBLE_PATH" ] && [ -x "$POSSIBLE_PATH" ]; then
            FFMPEG_EXEC="$POSSIBLE_PATH"
            break
        elif [ -f "$POSSIBLE_PATH" ]; then
            # 如果文件存在但没有执行权限，添加执行权限
            chmod +x "$POSSIBLE_PATH"
            if [ -x "$POSSIBLE_PATH" ]; then
                FFMPEG_EXEC="$POSSIBLE_PATH"
                break
            fi
        fi
    done
    
    if [ -n "$FFMPEG_EXEC" ]; then
        echo "找到ffmpeg可执行文件: $FFMPEG_EXEC"
        # 将ffmpeg目录添加到PATH
        export PATH="$(dirname "$FFMPEG_EXEC"):$PATH"
        echo "已将本地ffmpeg添加到PATH环境变量"
    else
        echo "警告: 在ffmpeg_files目录中未找到可执行的ffmpeg文件"
        echo "请确认ffmpeg可执行文件已上传到服务器，并具有正确的权限"
        echo "您可以运行以下命令查找ffmpeg文件:"
        echo "find $FFMPEG_DIR -name ffmpeg -type f"
        echo ""
        echo "找到后，请确保它有执行权限:"
        echo "chmod +x /path/to/your/ffmpeg"
        echo ""
        echo "按Enter键继续启动服务器..."
        read
    fi
else
    echo "警告: 未检测到本地ffmpeg目录，音频处理功能可能无法正常工作。"
    echo "请确认ffmpeg_files目录已上传到服务器，或者按照以下步骤安装ffmpeg:"
    echo "1. 对于CentOS/RHEL: sudo yum install epel-release && sudo yum install ffmpeg ffmpeg-devel"
    echo "2. 对于Ubuntu/Debian: sudo apt update && sudo apt install ffmpeg"
    echo ""
    echo "详细安装步骤请参考 ffmpeg安装指南.md 文档"
    echo ""
    echo "按Enter键继续启动服务器..."
    read
fi

echo "启动服务器..."
python3 multimodal_server.py