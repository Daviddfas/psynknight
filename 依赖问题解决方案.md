# 多模态服务器依赖问题解决方案

## 问题描述

启动多模态服务器时出现以下错误：

```
ImportError: cannot import name 'url_quote' from 'werkzeug.urls'
```

这是因为系统安装的Werkzeug版本(3.x)与Flask 2.0.1不兼容。Flask 2.0.1需要Werkzeug 2.0.1版本。

## 已实施的解决方案

我们已经直接修改了`multimodal_server.py`文件，添加了兼容性代码来解决Werkzeug版本冲突问题：

1. 添加了当前目录到Python路径，确保使用本地安装的包
2. 尝试导入`url_quote`，如果失败则提供一个自定义实现
3. 将自定义实现添加到werkzeug.urls模块

这种方法不需要修改系统环境或创建虚拟环境，可以直接在现有环境中运行。

## 使用方法

直接运行`start_multimodal_server.bat`脚本启动服务器即可。脚本已经设置了必要的环境变量，确保使用本地安装的包。

## 注意事项

- 如果仍然遇到问题，可以尝试手动安装特定版本的Werkzeug：`pip install werkzeug==2.0.1 --force-reinstall`
- 确保使用的是项目所需的Python版本
- 如果使用conda环境，已经在代码中处理了可能的冲突