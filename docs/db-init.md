# ECReporting 数据库初始化（PostgreSQL 15-18）

本文档用于初始化 ECReporting 的应用元数据库（Django 主库），适用于 PostgreSQL 15-18。

## 1. 目标

初始化以下对象：
- 数据库用户：`ecreporting`
- 数据库：`ecreporting`
- 权限：用户对该数据库具备完整使用权限

## 2. 使用 postgres 超级用户登录

```bash
sudo -u postgres psql
```

## 3. 创建用户与数据库

请替换为强密码：

```sql
CREATE USER ecreporting WITH PASSWORD '请替换为强密码';
CREATE DATABASE ecreporting OWNER ecreporting;
GRANT ALL PRIVILEGES ON DATABASE ecreporting TO ecreporting;
```

可选（仅当你要限制连接数时）：

```sql
ALTER ROLE ecreporting CONNECTION LIMIT 50;
```

## 4. 验证连接

退出 `psql` 后执行：

```bash
psql -h 127.0.0.1 -p 5432 -U ecreporting -d ecreporting -c "select version();"
```

如果连接成功，说明数据库初始化完成。

## 5. 写入后端环境变量

编辑 `/opt/ECReporting/backend/.env`，确认以下配置一致：

```env
APP_DB_HOST=127.0.0.1
APP_DB_PORT=5432
APP_DB_NAME=ecreporting
APP_DB_USER=ecreporting
APP_DB_PASSWORD=请替换为强密码
```

## 6. 初始化 Django 表结构

```bash
cd /opt/ECReporting/backend
. .venv/bin/activate
python manage.py migrate
python manage.py bootstrap --admin-username admin --admin-password '请替换默认密码'
```

## 7. 常见问题排查

- `FATAL: password authentication failed`：密码不一致，或 `pg_hba.conf` 认证方式不匹配。
- `database "ecreporting" does not exist`：数据库未创建或名称拼写不一致。
- `could not connect to server`：PostgreSQL 服务未启动或监听地址不包含目标 IP。

检查 PostgreSQL 状态：

```bash
sudo systemctl status postgresql
sudo -u postgres psql -c "show listen_addresses;"
```
