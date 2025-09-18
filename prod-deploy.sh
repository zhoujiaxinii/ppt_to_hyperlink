#!/bin/bash

# 生产环境部署脚本
# 用法: bash prod-deploy.sh [server-ip] [username]

set -e

SERVER_IP=$1
USERNAME=$2

if [ -z "$SERVER_IP" ] || [ -z "$USERNAME" ]; then
    echo "用法: bash prod-deploy.sh <server-ip> <username>"
    echo "例如: bash prod-deploy.sh 192.168.1.100 ubuntu"
    exit 1
fi

echo "=== PPT Hyperlink Converter 生产环境部署 ==="
echo "目标服务器: $USERNAME@$SERVER_IP"
echo

# 创建部署包
echo "📦 创建部署包..."
cd ..
tar --exclude='*.tar.gz' --exclude='.git' -czf ppt_hyperlink_deploy.tar.gz ppt_hyperlink/

# 传输到服务器
echo "📤 传输到服务器..."
scp ppt_hyperlink_deploy.tar.gz $USERNAME@$SERVER_IP:/home/$USERNAME/

# 在服务器上执行部署
echo "⚙️  在服务器上执行部署..."
ssh $USERNAME@$SERVER_IP << 'EOF'
    set -e

    echo "=== 服务器部署脚本 ==="

    # 解压部署包
    echo "📦 解压部署包..."
    cd /home/$USER
    tar -xzf ppt_hyperlink_deploy.tar.gz
    cd ppt_hyperlink/

    # 检查Docker是否安装
    if ! command -v docker &> /dev/null; then
        echo "❌ Docker未安装，正在安装..."
        sudo apt update
        sudo apt install -y docker.io docker-compose || sudo yum install -y docker docker-compose
        sudo systemctl start docker
        sudo systemctl enable docker
        sudo usermod -aG docker $USER
    fi

    # 构建并启动服务
    echo "🔨 构建并启动服务..."
    docker-compose down 2>/dev/null || true
    docker-compose build
    docker-compose up -d

    # 等待服务启动
    echo "⏳ 等待服务启动..."
    sleep 15

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

    # 清理部署包
    echo "🧹 清理部署包..."
    cd /home/$USER
    rm ppt_hyperlink_deploy.tar.gz

    echo "✅ 生产环境部署完成！"
EOF

echo "✅ 生产环境部署脚本执行完成！"