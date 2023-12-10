#!/bin/bash

# 进入项目目录
cd /flask-neo4j

# 拉取最新的代码
git pull

# 安装依赖
pip install -r requirements.txt

# 重启应用
# 这取决于您如何运行您的 Flask 应用
# 例如，如果您使用的是 Gunicorn，则可能需要重启 Gunicorn 服务
# sudo systemctl restart your-gunicorn-service
