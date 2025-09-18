# PPT超链接转换器 - 生产环境部署脚本

set -e

# 配置变量
PROJECT_NAME="ppt-hyperlink-converter"
INSTALL_DIR="/opt/$PROJECT_NAME"
USER="www-data"
GROUP="www-data"

echo "🚀 开始部署 $PROJECT_NAME..."

# 1. 创建项目目录
echo "📁 创建项目目录..."
sudo mkdir -p $INSTALL_DIR
sudo chown $USER:$GROUP $INSTALL_DIR

# 2. 克隆代码
echo "📥 克隆代码..."
sudo -u $USER git clone https://github.com/zhoujiaxinii/ppt_to_hyperlink.git $INSTALL_DIR
cd $INSTALL_DIR

# 3. 创建虚拟环境
echo "🐍 创建Python虚拟环境..."
sudo -u $USER python3 -m venv venv
source venv/bin/activate

# 4. 安装依赖
echo "📦 安装依赖包..."
sudo -u $USER pip install -r requirements.txt
sudo -u $USER pip install gunicorn

# 5. 创建Gunicorn配置
echo "⚙️ 创建Gunicorn配置..."
sudo -u $USER tee gunicorn.conf.py > /dev/null <<EOF
bind = "127.0.0.1:5000"
workers = 4
worker_class = "sync"
worker_connections = 1000
timeout = 60
keepalive = 2
max_requests = 1000
max_requests_jitter = 100
preload_app = True
accesslog = "/var/log/$PROJECT_NAME/access.log"
errorlog = "/var/log/$PROJECT_NAME/error.log"
loglevel = "info"
EOF

# 6. 创建日志目录
echo "📝 创建日志目录..."
sudo mkdir -p /var/log/$PROJECT_NAME
sudo chown $USER:$GROUP /var/log/$PROJECT_NAME

# 7. 创建Systemd服务文件
echo "サービ 创建Systemd服务..."
sudo tee /etc/systemd/system/$PROJECT_NAME.service > /dev/null <<EOF
[Unit]
Description=PPT Hyperlink Converter
After=network.target

[Service]
User=$USER
Group=$GROUP
WorkingDirectory=$INSTALL_DIR
Environment=PATH=$INSTALL_DIR/venv/bin
ExecStart=$INSTALL_DIR/venv/bin/gunicorn -c gunicorn.conf.py app:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# 8. 重新加载Systemd配置
echo "🔄 重新加载Systemd配置..."
sudo systemctl daemon-reload

# 9. 启动服务
echo "🏁 启动服务..."
sudo systemctl enable $PROJECT_NAME
sudo systemctl start $PROJECT_NAME

# 10. 检查服务状态
echo "✅ 检查服务状态..."
sudo systemctl status $PROJECT_NAME --no-pager

echo "🎉 部署完成!"
echo "💡 请记得配置环境变量和Nginx反向代理"
echo "📝 日志文件位于: /var/log/$PROJECT_NAME/"
