#!/bin/bash

# PPT Hyperlink Converter 部署脚本
# 用法: bash deploy.sh

set -e

echo "=== PPT Hyperlink Converter 部署脚本 ==="
echo

# 检查Docker是否安装
if ! command -v docker &> /dev/null; then
    echo "❌ Docker未安装，请先安装Docker"
    exit 1
fi

# 检查docker-compose是否安装
if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose未安装，请先安装docker-compose"
    exit 1
fi

# 停止现有容器
echo "🛑 停止现有容器..."
docker-compose down 2>/dev/null || true

# 构建镜像
echo "🔨 构建Docker镜像..."
docker-compose build

# 启动服务
echo "🚀 启动服务..."
docker-compose up -d

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 10

# 健康检查
echo "🔍 进行健康检查..."
if curl -f http://localhost:5000/health > /dev/null 2>&1; then
    echo "✅ 服务启动成功！"
    echo "📊 API端点: http://localhost:5000"
    echo "🏥 健康检查: http://localhost:5000/health"
else
    echo "❌ 服务启动失败，请检查日志"
    docker-compose logs
    exit 1
fi

# 显示运行状态
echo
echo "📈 容器状态:"
docker-compose ps

echo
echo "📋 查看日志: docker-compose logs -f"
echo "🛑 停止服务: docker-compose down"
echo "🔄 重启服务: docker-compose restart"
echo

echo "✅ 部署完成！"