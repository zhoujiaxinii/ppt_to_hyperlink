# PPT文件超链接转换工具

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/)
[![Docker](https://img.shields.io/badge/docker-container-blue)](https://www.docker.com/)

## 📝 项目简介

PPT文件超链接转换工具是一个基于Flask的RESTful API服务，可以自动将PPTX文件中的媒体链接和游戏链接转换为可点击的超链接，并支持上传到云存储服务。

该工具主要用于教育、培训等场景，能够自动化处理包含大量媒体资源的PPT文件，提升工作效率。

## 🌟 核心功能

- 🔗 **媒体链接识别** - 自动识别PPTX中的音频、视频链接（.mp3, .mp4, .wav等）
- 🎮 **游戏链接识别** - 识别特定格式的游戏链接（index.html?data_url=...json）
- ⚡ **超链接转换** - 将识别的链接转换为可点击的超链接
- ☁️ **云存储集成** - 支持上传处理后的文件到腾讯云COS
- 🐳 **Docker支持** - 完整的容器化部署方案
- 📊 **API接口** - 提供RESTful API便于集成

## 🛠️ 技术栈

- **Python 3.8+** - 主要开发语言
- **Flask** - Web框架
- **python-pptx** - PowerPoint文件处理
- **requests** - HTTP请求处理
- **qcloud-cos-python-sdk-v5** - 腾讯云COS SDK
- **Docker** - 容器化部署

## 🚀 快速开始

### 使用Docker Compose（推荐）

```bash
# 克隆项目
git clone https://github.com/yourusername/ppt_to_hyperlink.git
cd ppt_to_hyperlink

# 构建并启动服务
docker-compose up --build -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

### 本地开发环境

```bash
# 克隆项目
git clone https://github.com/yourusername/ppt_to_hyperlink.git
cd ppt_to_hyperlink

# 安装依赖
pip install -r requirements.txt

# 设置环境变量（腾讯云COS配置）
export COS_SECRET_ID=your_secret_id
export COS_SECRET_KEY=your_secret_key
export COS_REGION=your_region
export COS_BUCKET=your_bucket

# 运行应用
python app.py
```

## 📡 API使用说明

### 基础信息
- **Base URL**: `http://localhost:5000`
- **Content-Type**: `application/json`

### 端点

#### 1. 处理PPTX文件
**POST** `/process_pptx`

**请求体:**
```json
{
    "pptx_url": "https://example.com/your-file.pptx"
}
```

**响应示例:**
```json
{
    "success": true,
    "message": "PPTX file processed successfully",
    "download_url": "https://your-bucket.cos.your-region.myqcloud.com/processed_pptx/hyperlink_converted_20240101_120000.pptx",
    "links_found": [
        "https://example.com/audio.mp3",
        "https://example.com/index.html?data_url=https://example.com/game.json"
    ],
    "links_converted": 2
}
```

#### 2. 健康检查
**GET** `/health`

**响应:**
```json
{
    "status": "healthy",
    "service": "PPT Hyperlink Converter"
}
```

#### 3. API文档
**GET** `/`

返回API的详细文档信息。

### 使用示例

#### cURL示例
```bash
curl -X POST \
     -H "Content-Type: application/json" \
     -d '{"pptx_url": "https://example.com/test.pptx"}' \
     http://localhost:5000/process_pptx
```

#### Python示例
```python
import requests

url = "http://localhost:5000/process_pptx"
payload = {
    "pptx_url": "https://example.com/test.pptx"
}

response = requests.post(url, json=payload)
result = response.json()

if result['success']:
    print(f"处理成功！下载链接: {result['download_url']}")
    print(f"找到 {result['links_converted']} 个链接")
else:
    print(f"处理失败: {result['message']}")
```

## ⚙️ 配置说明

### 腾讯云COS配置

在使用云存储功能前，需要配置腾讯云COS信息。可以通过以下方式配置：

1. **环境变量**（推荐）：
```bash
export COS_SECRET_ID=your_secret_id
export COS_SECRET_KEY=your_secret_key
export COS_REGION=your_region      # 例如: ap-nanjing
export COS_BUCKET=your_bucket      # 例如: my-bucket-123456789
```

2. **直接修改代码**：
在 `app.py` 中修改以下变量：
```python
COS_SECRET_ID = "your_secret_id"
COS_SECRET_KEY = "your_secret_key"
COS_REGION = "your_region"
COS_BUCKET = "your_bucket"
```

### Docker环境变量

使用Docker时，可以通过环境变量传递配置：

```bash
docker run -d \
  --name ppt-api \
  -p 5000:5000 \
  -e COS_SECRET_ID=your_secret_id \
  -e COS_SECRET_KEY=your_secret_key \
  -e COS_REGION=your_region \
  -e COS_BUCKET=your_bucket \
  ppt-hyperlink-converter
```

## 🔍 链接识别规则

### 媒体链接
支持以下格式的媒体文件：
- 音频：.mp3, .wav, .ogg
- 视频：.mp4, .avi, .mov, .wmv, .flv, .webm

### 游戏链接
识别以下格式的游戏链接：
```
https://domain.com/path/index.html?data_url=https://domain.com/path/game.json
```

## 📁 项目结构

```
ppt_to_hyperlink/
├── app.py                 # Flask API主程序
├── requirements.txt       # Python依赖包列表
├── Dockerfile            # Docker镜像构建文件
├── docker-compose.yml    # Docker Compose配置文件
├── README.md             # 项目说明文档
├── LICENSE               # MIT许可证
└── .gitignore            # Git忽略文件
```

## 🐳 Docker部署

### 构建镜像
```bash
docker build -t ppt-hyperlink-converter .
```

### 运行容器
```bash
docker run -d \
  --name ppt-api \
  -p 5000:5000 \
  -e COS_SECRET_ID=your_secret_id \
  -e COS_SECRET_KEY=your_secret_key \
  -e COS_REGION=your_region \
  -e COS_BUCKET=your_bucket \
  ppt-hyperlink-converter
```

### Docker Compose
```bash
# 启动服务
docker-compose up -d

# 停止服务
docker-compose down

# 查看日志
docker-compose logs -f
```

## 🔧 开发指南

### 本地开发

1. 克隆项目：
```bash
git clone https://github.com/yourusername/ppt_to_hyperlink.git
cd ppt_to_hyperlink
```

2. 创建虚拟环境：
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate     # Windows
```

3. 安装依赖：
```bash
pip install -r requirements.txt
```

4. 运行应用：
```bash
python app.py
```

### 代码结构

- `app.py` - 主应用文件，包含所有API端点和业务逻辑
- `requirements.txt` - Python依赖包列表
- `Dockerfile` - Docker镜像构建配置
- `docker-compose.yml` - Docker Compose配置

### 测试

可以使用测试脚本验证功能：

```bash
# 创建测试PPTX文件并运行测试
python test_local.py
```

## 📈 性能说明

- 支持大型PPTX文件处理
- 使用临时目录确保内存效率
- 支持流式文件下载
- 异步处理提高响应速度

## 🛡️ 安全建议

1. **API安全**：
   - 在生产环境中使用HTTPS
   - 添加API密钥认证（可选）
   - 限制请求频率

2. **云存储安全**：
   - 使用最小权限原则配置COS访问密钥
   - 定期轮换访问密钥
   - 启用COS访问日志

3. **系统安全**：
   - 保持系统和依赖包更新
   - 使用防火墙限制端口访问
   - 定期备份重要数据

## 📊 监控和日志

应用包含详细的日志记录，包括：
- 文件下载进度
- 链接提取结果
- 超链接转换过程
- COS上传状态

可以通过以下方式查看日志：

```bash
# Docker Compose
docker-compose logs -f

# Docker
docker logs -f ppt_api

# 本地运行
tail -f app.log
```

## 🐛 故障排除

### 常见问题

1. **Docker构建失败**
   - 检查网络连接
   - 确保Docker服务正常运行

2. **COS上传失败**
   - 验证访问密钥
   - 检查存储桶配置

3. **链接提取失败**
   - 确认PPTX文件格式正确
   - 检查文件是否损坏

### 调试模式

```bash
# 启用调试模式
export FLASK_ENV=development
export FLASK_DEBUG=1

# 重启服务
docker-compose restart
```

## 🤝 贡献指南

欢迎任何形式的贡献！请遵循以下步骤：

1. Fork项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启Pull Request

### 开发规范

- 遵循PEP 8 Python编码规范
- 添加适当的注释和文档
- 编写测试用例
- 确保所有测试通过

## 📄 许可证

本项目采用MIT许可证，详情请见 [LICENSE](LICENSE) 文件。

## 👥 作者

Your Name - [@your_twitter](https://twitter.com/your_twitter) - your.email@example.com

项目链接: [https://github.com/yourusername/ppt_to_hyperlink](https://github.com/yourusername/ppt_to_hyperlink)

## 🙏 致谢

- [python-pptx](https://github.com/scanny/python-pptx) - 用于PPTX文件处理
- [Flask](https://github.com/pallets/flask) - Web框架
- [腾讯云COS SDK](https://github.com/tencentyun/cos-python-sdk-v5) - 云存储SDK