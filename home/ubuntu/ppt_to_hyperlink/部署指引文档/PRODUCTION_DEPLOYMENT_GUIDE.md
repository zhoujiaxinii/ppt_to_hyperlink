### **生产环境部署手册：PPT超链接转换服务**

#### **引言**

本手册将指导您完成在生产环境中部署“PPT超链接转换服务”的全过程。我们将使用 Docker 和 Docker Compose 进行容器化部署，通过 Nginx 作为反向代理来处理外部流量并启用 HTTPS 加密，利用 Let's Encrypt 获取免费的 SSL 证书，确保服务的安全、高效和稳定。

**技术栈概览：**
- **操作系统**: Ubuntu 22.04 LTS
- **容器化**: Docker, Docker Compose
- **Web 服务**: Flask (由项目提供)
- **反向代理**: Nginx
- **HTTPS**: Let's Encrypt (Certbot)

---

#### **第1步：服务器初始设置**

1.  **准备服务器**:
    - 您需要一台拥有公网IP的云服务器或VPS。
    - 确保您拥有服务器的 `root` 权限或一个具有 `sudo` 权限的用户。

2.  **创建部署用户** (推荐):
    - 为了安全，不建议直接使用 `root` 用户操作。
    ```bash
    # 以root用户登录后执行
    adduser deployer
    usermod -aG sudo deployer
    su - deployer
    ```
    - 后续所有命令都将默认使用 `deployer` 用户执行。

3.  **更新系统**:
    ```bash
    sudo apt-get update && sudo apt-get upgrade -y
    ```
---

#### **第2步：安装核心环境 (Docker & Nginx)**

1.  **安装 Docker**:
    - 我们将使用官方脚本来安装最新版本的 Docker。
    ```bash
    sudo apt-get install -y apt-transport-https ca-certificates curl software-properties-common
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    sudo apt-get update
    sudo apt-get install -y docker-ce docker-ce-cli containerd.io
    ```

2.  **将当前用户添加到 Docker 组**:
    - 这允许您无需 `sudo` 即可运行 `docker` 命令。
    ```bash
    sudo usermod -aG docker ${USER}
    ```
    - **重要**: 执行后需要**退出并重新登录服务器**以使用户组更改生效。

3.  **安装 Docker Compose**:
    ```bash
    sudo apt-get install -y docker-compose-v2
    ```
    - 验证安装：`docker compose version`

4.  **安装 Nginx**:
    - 我们将 Nginx 直接安装在宿主机上，用于管理证书和作为反向代理。
    ```bash
    sudo apt-get install -y nginx
    ```

---

#### **第3步：获取并配置项目**

1.  **克隆项目代码**:
    ```bash
    cd ~
    git clone https://github.com/your-github-username/ppt_to_hyperlink.git  # 替换为您的仓库地址
    cd ppt_to_hyperlink/home/ubuntu/ppt_to_hyperlink
    ```

2.  **创建生产环境变量文件**:
    - 生产环境的配置（尤其是密钥）应通过环境变量传入，而不是硬编码。`docker-compose` 可以通过一个 `.env` 文件来加载这些变量。
    ```bash
    # 在 home/ubuntu/ppt_to_hyperlink 目录下
    nano .env
    ```
    - 在打开的编辑器中，粘贴以下内容，并**替换为您自己的真实值**:
    ```ini
    # .env 文件内容

    # 腾讯云 COS 配置
    COS_SECRET_ID=your_cos_secret_id
    COS_SECRET_KEY=your_cos_secret_key
    COS_REGION=ap-guangzhou # 例如：ap-guangzhou
    COS_BUCKET=your-bucket-name-1250000000

    # 服务域名 (用于Nginx和HTTPS)
    DOMAIN_NAME=ppt-service.yourdomain.com
    ```
    - 按 `Ctrl+X`，然后按 `Y` 和 `Enter` 保存并退出。

3.  **创建生产用的 Docker Compose 文件**:
    - `docker-compose.yml` 文件适合开发，生产环境应有更严格的配置。
    ```bash
    # 在 home/ubuntu/ppt_to_hyperlink 目录下
    nano docker-compose.prod.yml
    ```
    - 粘贴以下内容：
    ```yaml
    # docker-compose.prod.yml
    version: '3.8'

    services:
      ppt_api:
        build:
          context: .
          dockerfile: Dockerfile
        # .env 文件会自动被 docker-compose 读取
        # env_file: .env
        restart: always
        # 不直接暴露端口，而是通过Nginx代理
        # ports:
        #   - "5000:5000"
        expose:
          - 5000
        volumes:
          # 挂载日志文件和上传目录，实现数据持久化
          - ./gunicorn.log:/app/gunicorn.log
          - ./app.log:/app/app.log
          - ./upload:/home/ubuntu/upload
        networks:
          - app-network

    networks:
      app-network:
        driver: bridge
    ```
    - 这个配置定义了应用服务 `ppt_api`，设置了总是在容器失败时自动重启，并通过内部网络 `app-network` 暴露端口 `5000`，等待 Nginx 的连接。

---

#### **第4步：配置 Nginx 反向代理**

1.  **创建 Nginx 配置文件**:
    ```bash
    sudo nano /etc/nginx/sites-available/ppt_service
    ```
    - 粘贴以下配置。注意，这里的 `ppt_api` 是 `docker-compose.prod.yml` 中定义的服务名，Docker 的内部 DNS 会将其解析到容器的 IP 地址。
    ```nginx
    # /etc/nginx/sites-available/ppt_service

    upstream ppt_api_server {
        # 'ppt_api' 必须与 docker-compose.prod.yml 文件中定义的服务名一致
        # Docker会自动将其解析到容器的内部IP
        # 这里我们假设 Docker 容器的 IP 是 172.x.x.x, 端口是5000,
        # Nginx需要能够访问到这个内部网络。
        # 为了简化，我们暂时使用localhost，后续通过docker网络连接。
        # 最稳妥的方式是直接让Nginx也加入Docker网络，或者直接代理到容器IP。
        # 为简单起见，我们先配置让Docker将端口映射到宿主机的一个非公开端口
        server 127.0.0.1:5001;
    }

    server {
        listen 80;
        listen [::]:80;

        # 替换为您的域名
        server_name ppt-service.yourdomain.com;

        location / {
            proxy_pass http://ppt_api_server;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
    ```

    *为了让 Nginx 能够访问到 Docker 容器，我们需要稍微调整 `docker-compose.prod.yml`，将端口映射到宿主机的 `127.0.0.1` 地址。*

    **修改 `docker-compose.prod.yml`**:
    ```bash
    nano docker-compose.prod.yml
    ```
    将 `expose` 部分注释掉或删除，添加 `ports` 部分：
    ```yaml
    # ...
    # expose:
    #  - 5000
    ports:
      # 只在宿主机的本地回环地址上暴露端口，不对外公开
      - "127.0.0.1:5001:5000"
    # ...
    ```

2.  **启用 Nginx 配置**:
    ```bash
    sudo ln -s /etc/nginx/sites-available/ppt_service /etc/nginx/sites-enabled/
    sudo nginx -t  # 测试配置是否正确
    sudo systemctl restart nginx # 重启Nginx
    ```

---

#### **第5步：启用 HTTPS (使用 Let's Encrypt)**

1.  **安装 Certbot**:
    ```bash
    sudo apt-get install -y certbot python3-certbot-nginx
    ```

2.  **获取 SSL 证书**:
    - Certbot 会自动修改您的 Nginx 配置以支持 HTTPS。
    ```bash
    # 将 your.domain.com 替换为您的真实域名
    sudo certbot --nginx -d ppt-service.yourdomain.com
    ```
    - 按照提示操作，它会询问您是否自动将 HTTP 流量重定向到 HTTPS（推荐选择此项）。

3.  **验证自动续期**:
    - Let's Encrypt 证书有效期为90天，Certbot 会自动设置一个定时任务来续期。
    ```bash
    sudo certbot renew --dry-run
    ```
    - 如果看到 “successfully” 字样，说明自动续期配置成功。

---

#### **第6步：启动服务并验证**

1.  **构建并启动容器**:
    ```bash
    cd ~/ppt_to_hyperlink/home/ubuntu/ppt_to_hyperlink
    # 使用 -f 指定生产配置文件，-d 在后台运行
    docker compose -f docker-compose.prod.yml up --build -d
    ```

2.  **验证服务状态**:
    ```bash
    # 查看容器是否正常运行 (状态应为 Up)
    docker compose -f docker-compose.prod.yml ps

    # 查看服务日志，确认无错误
    docker compose -f docker-compose.prod.yml logs -f ppt_api
    ```

3.  **访问服务**:
    - 打开浏览器，访问 `https://ppt-service.yourdomain.com` (您的域名)。您应该能看到 API 的文档信息。
    - 使用 `curl` 或 Postman 工具测试 `/process_pptx` 端点。

---

#### **第7步：防火墙与安全加固**

1.  **配置 UFW 防火墙**:
    - 只允许必要的端口通过。
    ```bash
    sudo ufw allow OpenSSH  # 允许SSH连接
    sudo ufw allow 'Nginx Full' # 允许HTTP和HTTPS流量
    sudo ufw enable # 启用防火墙
    ```
    - 检查状态：`sudo ufw status`

---

#### **第8步：日常维护**

1.  **查看日志**:
    ```bash
    docker compose -f docker-compose.prod.yml logs -f ppt_api
    ```

2.  **停止服务**:
    ```bash
    docker compose -f docker-compose.prod.yml down
    ```

3.  **更新服务**:
    - 如果您的代码有更新并已推送到 Git 仓库：
    ```bash
    cd ~/ppt_to_hyperlink/home/ubuntu/ppt_to_hyperlink
    git pull # 拉取最新代码
    docker compose -f docker-compose.prod.yml up --build -d # 重新构建并启动服务
    ```

---

部署完成！您的服务现在已经安全、稳定地运行在生产环境中。