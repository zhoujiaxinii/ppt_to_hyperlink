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
```

### 本地开发环境

```bash
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

### 处理PPTX文件
**POST** `/process_pptx`

**请求体:**
```json
{
    "pptx_url": "https://example.com/your-file.pptx"
}
```

## ⚙️ 配置说明

### 腾讯云COS配置

在使用云存储功能前，需要配置腾讯云COS信息。可以通过环境变量传递配置：

```bash
export COS_SECRET_ID=your_secret_id
export COS_SECRET_KEY=your_secret_key
export COS_REGION=your_region      # 例如: ap-nanjing
export COS_BUCKET=your_bucket      # 例如: my-bucket-123456789
```

## 🐳 Docker部署

```bash
# 构建镜像
docker build -t ppt-hyperlink-converter .

# 运行容器
docker run -d \
  --name ppt-api \
  -p 5000:5000 \
  -e COS_SECRET_ID=your_secret_id \
  -e COS_SECRET_KEY=your_secret_key \
  -e COS_REGION=your_region \
  -e COS_BUCKET=your_bucket \
  ppt-hyperlink-converter
```

## 📄 许可证

本项目采用MIT许可证，详情请见 [LICENSE](LICENSE) 文件。

## 🙏 致谢

- [python-pptx](https://github.com/scanny/python-pptx) - 用于PPTX文件处理
- [Flask](https://github.com/pallets/flask) - Web框架
- [腾讯云COS SDK](https://github.com/tencentyun/cos-python-sdk-v5) - 云存储SDK