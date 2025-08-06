# 万里的秘密基地 - Docker部署手册

## 📋 目录

1. [系统要求](#系统要求)
2. [快速部署](#快速部署)
3. [手动部署](#手动部署)
4. [配置说明](#配置说明)
5. [维护管理](#维护管理)
6. [故障排除](#故障排除)

## 🖥️ 系统要求

### 最低要求
- **操作系统**: Ubuntu 18.04+ / CentOS 7+ / Debian 9+
- **CPU**: 2核心
- **内存**: 4GB RAM
- **存储**: 20GB可用空间
- **网络**: 稳定的网络连接

### 推荐配置
- **操作系统**: Ubuntu 20.04+ / CentOS 8+
- **CPU**: 4核心
- **内存**: 8GB RAM
- **存储**: 50GB SSD
- **网络**: 千兆网络

## 🚀 快速部署

### 1. 下载项目
```bash
git clone <your-repository-url>
cd python-project
```

### 2. 运行部署脚本
```bash
chmod +x deploy.sh
./deploy.sh
```

### 3. 访问应用
- **网站地址**: http://localhost
- **管理后台**: http://localhost/admin
- **管理员账户**: admin / admin123

## 🔧 手动部署

### 1. 安装Docker和Docker Compose

#### Ubuntu/Debian
```bash
# 更新系统
sudo apt-get update

# 安装依赖
sudo apt-get install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

# 添加Docker官方GPG密钥
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# 设置Docker仓库
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# 安装Docker
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io

# 启动Docker服务
sudo systemctl start docker
sudo systemctl enable docker

# 将用户添加到docker组
sudo usermod -aG docker $USER

# 安装Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

#### CentOS/RHEL
```bash
# 安装依赖
sudo yum install -y yum-utils

# 添加Docker仓库
sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo

# 安装Docker
sudo yum install -y docker-ce docker-ce-cli containerd.io

# 启动Docker服务
sudo systemctl start docker
sudo systemctl enable docker

# 将用户添加到docker组
sudo usermod -aG docker $USER

# 安装Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### 2. 创建环境变量文件
```bash
cat > .env << EOF
# 数据库配置
MYSQL_ROOT_PASSWORD=root123456
MYSQL_DATABASE=wanli_video
MYSQL_USER=wanli_user
MYSQL_PASSWORD=wanli123456

# Flask配置
SECRET_KEY=$(openssl rand -hex 32)
FLASK_ENV=production

# 数据库连接
MYSQL_HOST=mysql
MYSQL_PORT=3306
EOF
```

### 3. 创建必要目录
```bash
mkdir -p static/uploads static/avatars static/thumbnails
mkdir -p nginx/ssl
touch static/avatars/default.jpg
touch static/thumbnails/default.jpg
```

### 4. 构建和启动服务
```bash
# 构建镜像
docker-compose build

# 启动服务
docker-compose up -d

# 等待服务启动
sleep 30

# 创建管理员账户
docker-compose exec web python -c "
from main import app, db, User
from werkzeug.security import generate_password_hash

with app.app_context():
    db.create_all()
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(
            username='admin',
            email='admin@wanli.com',
            password_hash=generate_password_hash('admin123'),
            is_admin=True
        )
        db.session.add(admin)
        db.session.commit()
        print('管理员账户创建成功')
    else:
        print('管理员账户已存在')
"
```

## ⚙️ 配置说明

### 环境变量配置

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| `MYSQL_ROOT_PASSWORD` | root123456 | MySQL root密码 |
| `MYSQL_DATABASE` | wanli_video | 数据库名称 |
| `MYSQL_USER` | wanli_user | 数据库用户名 |
| `MYSQL_PASSWORD` | wanli123456 | 数据库密码 |
| `SECRET_KEY` | 自动生成 | Flask密钥 |
| `FLASK_ENV` | production | Flask环境 |

### 端口配置

| 服务 | 端口 | 说明 |
|------|------|------|
| Nginx | 80 | HTTP服务 |
| Nginx | 443 | HTTPS服务 |
| Flask | 5000 | 应用服务 |
| MySQL | 3306 | 数据库服务 |

### 目录结构
```
python-project/
├── main.py                 # Flask应用主文件
├── requirements.txt        # Python依赖
├── Dockerfile             # Docker镜像配置
├── docker-compose.yml     # Docker Compose配置
├── deploy.sh              # 部署脚本
├── .env                   # 环境变量
├── .dockerignore          # Docker忽略文件
├── static/                # 静态文件
│   ├── uploads/          # 上传的视频
│   ├── avatars/          # 用户头像
│   └── thumbnails/       # 视频缩略图
├── mysql/                 # MySQL配置
│   └── init.sql          # 数据库初始化脚本
└── nginx/                 # Nginx配置
    ├── nginx.conf        # Nginx配置文件
    └── ssl/              # SSL证书目录
```

## 🛠️ 维护管理

### 常用命令

#### 服务管理
```bash
# 查看服务状态
docker-compose ps

# 启动服务
docker-compose up -d

# 停止服务
docker-compose down

# 重启服务
docker-compose restart

# 重新构建并启动
docker-compose up -d --build
```

#### 日志查看
```bash
# 查看所有服务日志
docker-compose logs

# 查看特定服务日志
docker-compose logs web
docker-compose logs mysql
docker-compose logs nginx

# 实时查看日志
docker-compose logs -f web
```

#### 数据库管理
```bash
# 进入MySQL容器
docker-compose exec mysql mysql -u root -p

# 备份数据库
docker-compose exec mysql mysqldump -u root -p wanli_video > backup.sql

# 恢复数据库
docker-compose exec -T mysql mysql -u root -p wanli_video < backup.sql
```

#### 文件管理
```bash
# 进入应用容器
docker-compose exec web bash

# 查看上传的文件
docker-compose exec web ls -la static/uploads/

# 清理旧文件
docker-compose exec web find static/uploads/ -mtime +30 -delete
```

### 备份策略

#### 数据库备份
```bash
#!/bin/bash
# 创建备份脚本 backup.sh

BACKUP_DIR="/backup/mysql"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# 备份数据库
docker-compose exec mysql mysqldump -u root -pwanli123456 wanli_video > $BACKUP_DIR/wanli_video_$DATE.sql

# 压缩备份文件
gzip $BACKUP_DIR/wanli_video_$DATE.sql

# 删除30天前的备份
find $BACKUP_DIR -name "*.sql.gz" -mtime +30 -delete

echo "数据库备份完成: $BACKUP_DIR/wanli_video_$DATE.sql.gz"
```

#### 文件备份
```bash
#!/bin/bash
# 创建文件备份脚本 backup_files.sh

BACKUP_DIR="/backup/files"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# 备份静态文件
tar -czf $BACKUP_DIR/static_$DATE.tar.gz static/

# 删除30天前的备份
find $BACKUP_DIR -name "static_*.tar.gz" -mtime +30 -delete

echo "文件备份完成: $BACKUP_DIR/static_$DATE.tar.gz"
```

### 监控和维护

#### 系统监控
```bash
# 查看容器资源使用情况
docker stats

# 查看磁盘使用情况
df -h

# 查看内存使用情况
free -h

# 查看网络连接
netstat -tulpn
```

#### 性能优化
```bash
# 清理Docker缓存
docker system prune -a

# 清理未使用的镜像
docker image prune

# 清理未使用的容器
docker container prune

# 清理未使用的网络
docker network prune
```

## 🔍 故障排除

### 常见问题

#### 1. 服务无法启动
```bash
# 查看详细错误信息
docker-compose logs

# 检查端口占用
netstat -tulpn | grep :80
netstat -tulpn | grep :5000

# 检查磁盘空间
df -h
```

#### 2. 数据库连接失败
```bash
# 检查MySQL容器状态
docker-compose ps mysql

# 查看MySQL日志
docker-compose logs mysql

# 测试数据库连接
docker-compose exec web python -c "
import pymysql
try:
    conn = pymysql.connect(
        host='mysql',
        user='wanli_user',
        password='wanli123456',
        database='wanli_video'
    )
    print('数据库连接成功')
    conn.close()
except Exception as e:
    print(f'数据库连接失败: {e}')
"
```

#### 3. 文件上传失败
```bash
# 检查目录权限
ls -la static/uploads/

# 检查磁盘空间
df -h

# 检查Nginx配置
docker-compose exec nginx nginx -t
```

#### 4. 性能问题
```bash
# 查看容器资源使用
docker stats

# 查看系统负载
top

# 查看内存使用
free -h

# 查看网络连接数
ss -s
```

### 日志分析

#### 应用日志
```bash
# 查看应用错误日志
docker-compose logs web | grep ERROR

# 查看访问日志
docker-compose logs web | grep "GET\|POST"

# 查看上传日志
docker-compose logs web | grep "upload"
```

#### Nginx日志
```bash
# 查看Nginx访问日志
docker-compose exec nginx tail -f /var/log/nginx/access.log

# 查看Nginx错误日志
docker-compose exec nginx tail -f /var/log/nginx/error.log
```

#### MySQL日志
```bash
# 查看MySQL慢查询日志
docker-compose exec mysql tail -f /var/log/mysql/slow.log

# 查看MySQL错误日志
docker-compose exec mysql tail -f /var/log/mysql/error.log
```

## 🔒 安全建议

### 1. 修改默认密码
```bash
# 修改MySQL root密码
docker-compose exec mysql mysql -u root -p -e "ALTER USER 'root'@'localhost' IDENTIFIED BY 'new_password';"

# 修改应用数据库密码
# 更新.env文件中的MYSQL_PASSWORD
# 重启服务
docker-compose restart
```

### 2. 配置SSL证书
```bash
# 将SSL证书放入nginx/ssl/目录
cp your-cert.pem nginx/ssl/cert.pem
cp your-key.pem nginx/ssl/key.pem

# 修改nginx.conf启用HTTPS
# 取消注释HTTPS配置部分

# 重启Nginx
docker-compose restart nginx
```

### 3. 防火墙配置
```bash
# 只开放必要端口
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw deny 3306/tcp  # 禁止外部访问MySQL
```

### 4. 定期更新
```bash
# 更新Docker镜像
docker-compose pull

# 重新构建应用
docker-compose up -d --build

# 清理旧镜像
docker image prune
```

## 📞 技术支持

如果遇到问题，请按以下步骤进行排查：

1. **查看日志**: `docker-compose logs`
2. **检查状态**: `docker-compose ps`
3. **验证配置**: 检查.env文件
4. **重启服务**: `docker-compose restart`
5. **重新部署**: `docker-compose down && docker-compose up -d`

---

**注意**: 生产环境部署前请务必修改默认密码和密钥！ 