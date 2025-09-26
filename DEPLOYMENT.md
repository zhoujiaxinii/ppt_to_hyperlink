# PPT超链接转换器 - 服务器部署指南

## 🚀 快速部署

### 1. 系统要求
- Python 3.8 或更高版本
- pip 包管理器
- git (用于代码获取)
- 500MB 以上磁盘空间

### 2. 获取代码
```bash
git clone https://github.com/zhoujiaxinii/ppt_to_hyperlink.git
cd ppt_to_hyperlink
```

### 3. 安装依赖
```bash
pip install -r requirements.txt
```

### 4. 配置环境变量
在服务器上设置以下环境变量：

```bash
export COS_SECRET_ID="your_secret_id"
export COS_SECRET_KEY="your_secret_key"
export COS_REGION="your_region"  # 例如: "ap-nanjing"
export COS_BUCKET="your_bucket_name"
```

或者创建 `.env` 文件：
```bash
# .env 文件内容
COS_SECRET_ID=your_secret_id
COS_SECRET_KEY=your_secret_key
COS_REGION=your_region
COS_BUCKET=your_bucket_name
```

### 5. 启动服务
```bash
# 开发环境
python app.py

# 生产环境推荐使用 Gunicorn
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## 🛠️ 生产环境部署脚本

### 使用 Gunicorn + Nginx

1. 安装 Gunicorn 和 Nginx:
```bash
pip install gunicorn
# Ubuntu/Debian
sudo apt update && sudo apt install nginx
# CentOS/RHEL
sudo yum install nginx
```

2. 创建 Gunicorn 配置文件 `gunicorn.conf.py`:
```python
bind = "127.0.0.1:5000"
workers = 4
worker_class = "sync"
worker_connections = 1000
timeout = 60
keepalive = 2
max_requests = 1000
max_requests_jitter = 100
preload_app = True
```

3. 创建 Systemd 服务文件 `/etc/systemd/system/ppt-converter.service`:
```ini
[Unit]
Description=PPT Hyperlink Converter
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/path/to/ppt_to_hyperlink
EnvironmentFile=/path/to/ppt_to_hyperlink/.env
ExecStart=/path/to/venv/bin/gunicorn -c gunicorn.conf.py app:app
Restart=always

[Install]
WantedBy=multi-user.target
```

4. 配置 Nginx `/etc/nginx/sites-available/ppt-converter`:
```nginx
server {
    listen 80;
    server_name your_domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

5. 启动服务:
```bash
sudo systemctl start ppt-converter
sudo systemctl enable ppt-converter
sudo systemctl start nginx
sudo systemctl enable nginx
```

## 🔧 环境变量配置详解

| 变量名 | 必需 | 描述 | 示例值 |
|--------|------|------|--------|
| COS_SECRET_ID | 是 | 腾讯云COS访问密钥ID | 从腾讯云控制台获取 |
| COS_SECRET_KEY | 是 | 腾讯云COS密钥 | 从腾讯云控制台获取 |
| COS_REGION | 是 | COS存储桶地域 | 根据实际地域填写 |
| COS_BUCKET | 是 | COS存储桶名称 | 根据实际存储桶填写 |

## 📊 性能配置

### 推荐配置
```python
# app.py 中的配置常量
REQUEST_TIMEOUT = 15      # 请求超时时间(秒)
MAX_FILE_SIZE = 52428800  # 最大文件大小(50MB)
MAX_RETRIES = 2           # 最大重试次数
RETRY_DELAY = 0.5         # 重试延迟(秒)
API_TIMEOUT = 60          # API总超时时间(秒)
```

## 🔍 监控和日志

### 日志配置
应用默认输出 INFO 级别日志，包含：
- 处理时间统计
- 错误信息
- COS操作日志

### 健康检查端点
```
GET /health
```
返回:
```json
{
  "status": "healthy",
  "service": "PPT Hyperlink Converter"
}
```

### 性能监控
每个处理请求都会返回性能数据:
```json
{
  "performance": {
    "download_time": 0.53,
    "extract_time": 0.13,
    "hyperlink_time": 0.22,
    "upload_time": 1.62,
    "total_time": 2.51
  }
}
```

## 🔒 安全建议

1. 使用 HTTPS (通过Nginx配置SSL证书)
2. 设置防火墙规则，仅开放必要端口
3. 定期轮换COS密钥
4. 限制上传文件大小
5. 使用反向代理隐藏真实服务信息

## 🆘 故障排除

### 常见问题

1. **500 Internal Server Error**
   - 检查COS凭证是否正确配置
   - 查看应用日志获取详细错误信息

2. **处理超时**
   - 检查网络连接
   - 增加 `REQUEST_TIMEOUT` 值
   - 检查文件大小是否超出限制

3. **COS上传失败**
   - 验证COS配置信息
   - 检查存储桶权限设置
   - 确认网络连接正常

### 日志查看
```bash
# 开发环境
tail -f nohup.out

# 生产环境 (Systemd)
sudo journalctl -u ppt-converter -f
```