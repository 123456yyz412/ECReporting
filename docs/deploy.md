# ECReporting 部署文档（Ubuntu 22.04.5 LTS）

本文档用于生产可部署方案，适配以下版本要求：
- Ubuntu 22.04.5 LTS
- Python 3.10.12
- Node.js v18.20.8
- PostgreSQL 15-18（示例按 PostgreSQL 18）

建议目录：
- `/opt/ECReporting/backend`（后端）
- `/opt/ECReporting/frontend`（前端）
- `/var/lib/ecreporting/media`（上传文件）
- `/var/lib/ecreporting/staticfiles`（Django 静态文件）
- `/var/log/ecreporting`（应用日志）

## 1. 部署前准备

### 1.1 安装系统依赖

```bash
sudo apt update
sudo apt install -y curl ca-certificates gnupg lsb-release \
  python3.10 python3.10-venv python3-dev build-essential libpq-dev \
  nginx logrotate postgresql-client
```

### 1.2 安装 Node.js 18（若系统未安装或版本不对）

```bash
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs
node -v
npm -v
```

## 2. 数据库初始化（应用元数据库）

仓库之前没有独立数据库初始化说明，现已补充：`docs/db-init.md`。  
请先按该文档完成数据库账号、数据库和权限初始化，再继续后续步骤。

快速示例（PostgreSQL）：

```sql
CREATE USER ecreporting WITH PASSWORD '请替换为强密码';
CREATE DATABASE ecreporting OWNER ecreporting;
GRANT ALL PRIVILEGES ON DATABASE ecreporting TO ecreporting;
```

## 3. 后端部署（Django + Gunicorn）

### 3.1 创建运行目录

```bash
sudo mkdir -p /var/log/ecreporting /var/lib/ecreporting/media /var/lib/ecreporting/staticfiles
sudo chown -R $USER:$USER /var/log/ecreporting /var/lib/ecreporting
```

### 3.2 安装 Python 依赖

```bash
cd /opt/ECReporting/backend
python3.10 -m venv .venv
. .venv/bin/activate
pip install -U pip
pip install -r requirements.txt
```

### 3.3 配置环境变量

```bash
cd /opt/ECReporting/backend
cp .env.example .env
```

请至少修改以下项：
- `DJANGO_SECRET_KEY`：必须修改为随机长字符串
- `APP_DB_HOST/PORT/NAME/USER/PASSWORD`：与数据库初始化保持一致
- `DJANGO_ALLOWED_HOSTS`：生产环境填写域名或 IP（逗号分隔）
- `FERNET_KEYS`：建议显式配置，避免依赖 `DJANGO_SECRET_KEY` 回退逻辑
- `LOG_DIR`、`MEDIA_ROOT`、`STATIC_ROOT`：建议保持默认生产路径

生成 `FERNET_KEYS`（示例）：

```bash
cd /opt/ECReporting/backend
. .venv/bin/activate
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

### 3.4 初始化应用

```bash
cd /opt/ECReporting/backend
. .venv/bin/activate
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py bootstrap --admin-username admin --admin-password '请替换默认密码'
```

说明：
- `migrate`：初始化系统表结构
- `collectstatic`：收集 Django 静态资源
- `bootstrap`：创建默认用户组（管理员、普通用户）与管理员账号

### 3.5 配置 Gunicorn systemd 服务

创建文件：`/etc/systemd/system/ecreporting-backend.service`

```ini
[Unit]
Description=ECReporting Backend (Gunicorn)
After=network.target

[Service]
Type=simple
WorkingDirectory=/opt/ECReporting/backend
EnvironmentFile=/opt/ECReporting/backend/.env
ExecStart=/opt/ECReporting/backend/.venv/bin/gunicorn ecreporting.wsgi:application -b 127.0.0.1:8000 --workers 3 --timeout 120
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

加载并启动：

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now ecreporting-backend
sudo systemctl status ecreporting-backend
```

## 4. 前端部署（Vue3 + Vite）

```bash
cd /opt/ECReporting/frontend
npm install
npm run build
```

构建产物目录：
- `/opt/ECReporting/frontend/dist`

## 5. Nginx 配置（前端 + API 代理）

创建文件：`/etc/nginx/sites-available/ecreporting`

```nginx
server {
  listen 80;
  server_name _;

  root /opt/ECReporting/frontend/dist;
  index index.html;

  location / {
    try_files $uri $uri/ /index.html;
  }

  location /api/ {
    proxy_pass http://127.0.0.1:8000;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
  }

  location /media/ {
    alias /var/lib/ecreporting/media/;
  }

  location /static/ {
    alias /var/lib/ecreporting/staticfiles/;
  }
}
```

启用配置：

```bash
sudo ln -sf /etc/nginx/sites-available/ecreporting /etc/nginx/sites-enabled/ecreporting
sudo nginx -t
sudo systemctl reload nginx
```

## 6. 日志轮转与清理（logrotate）

后端日志文件：
- `/var/log/ecreporting/backend.log`

创建：`/etc/logrotate.d/ecreporting-backend`

```conf
/var/log/ecreporting/backend.log {
  daily
  rotate 14
  compress
  delaycompress
  missingok
  notifempty
  copytruncate
}
```

手动验证：

```bash
sudo logrotate -d /etc/logrotate.d/ecreporting-backend
sudo logrotate -f /etc/logrotate.d/ecreporting-backend
```

## 7. 上线后检查清单

```bash
curl -I http://127.0.0.1/
curl -I http://127.0.0.1/api/
sudo systemctl status ecreporting-backend
sudo systemctl status nginx
```

浏览器检查：
- 登录页可访问
- 使用 `bootstrap` 创建的管理员可登录
- 首页、报表模块、数据填报、管理员模块可正常打开

## 8. 常见问题

- `500` 且日志提示数据库连接失败：检查 `.env` 中 `APP_DB_*` 与 PostgreSQL 授权。
- 静态资源 404：确认已执行 `collectstatic` 且 Nginx `location /static/` 指向正确。
- 上传文件无法访问：检查 `MEDIA_ROOT`、Nginx `/media/` alias 和目录权限。
- 登录后白页：先看浏览器控制台，再看 `/var/log/ecreporting/backend.log` 与 `journalctl -u ecreporting-backend -n 200 --no-pager`。
