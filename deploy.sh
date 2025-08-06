#!/bin/bash

# 万里的秘密基地 - Docker部署脚本
# 适用于Ubuntu/CentOS/Debian系统

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查是否为root用户
check_root() {
    if [[ $EUID -eq 0 ]]; then
        log_error "请不要使用root用户运行此脚本"
        exit 1
    fi
}

# 检测操作系统
detect_os() {
    if [[ -f /etc/os-release ]]; then
        . /etc/os-release
        OS=$NAME
        VER=$VERSION_ID
    elif type lsb_release >/dev/null 2>&1; then
        OS=$(lsb_release -si)
        VER=$(lsb_release -sr)
    else
        OS=$(uname -s)
        VER=$(uname -r)
    fi
    log_info "检测到操作系统: $OS $VER"
}

# 安装Docker
install_docker() {
    log_info "开始安装Docker..."
    
    if command -v docker &> /dev/null; then
        log_success "Docker已安装"
        return
    fi
    
    # 卸载旧版本
    sudo apt-get remove -y docker docker-engine docker.io containerd runc 2>/dev/null || true
    
    # 更新包索引
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
    
    # 设置稳定版仓库
    echo \
        "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
        $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    
    # 安装Docker Engine
    sudo apt-get update
    sudo apt-get install -y docker-ce docker-ce-cli containerd.io
    
    # 启动Docker服务
    sudo systemctl start docker
    sudo systemctl enable docker
    
    # 将当前用户添加到docker组
    sudo usermod -aG docker $USER
    
    log_success "Docker安装完成"
}

# 安装Docker Compose
install_docker_compose() {
    log_info "开始安装Docker Compose..."
    
    if command -v docker-compose &> /dev/null; then
        log_success "Docker Compose已安装"
        return
    fi
    
    # 下载Docker Compose
    sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    
    # 设置执行权限
    sudo chmod +x /usr/local/bin/docker-compose
    
    log_success "Docker Compose安装完成"
}

# 创建环境变量文件
create_env_file() {
    log_info "创建环境变量文件..."
    
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
    
    log_success "环境变量文件创建完成"
}

# 创建必要的目录
create_directories() {
    log_info "创建必要的目录..."
    
    mkdir -p static/uploads static/avatars static/thumbnails
    mkdir -p nginx/ssl
    
    # 创建默认头像和缩略图
    touch static/avatars/default.jpg
    touch static/thumbnails/default.jpg
    
    log_success "目录创建完成"
}

# 构建和启动服务
deploy_services() {
    log_info "开始部署服务..."
    
    # 停止现有服务
    docker-compose down 2>/dev/null || true
    
    # 构建镜像
    log_info "构建Docker镜像..."
    docker-compose build
    
    # 启动服务
    log_info "启动服务..."
    docker-compose up -d
    
    # 等待服务启动
    log_info "等待服务启动..."
    sleep 30
    
    # 检查服务状态
    if docker-compose ps | grep -q "Up"; then
        log_success "服务启动成功"
    else
        log_error "服务启动失败"
        docker-compose logs
        exit 1
    fi
}

# 创建管理员账户
create_admin_user() {
    log_info "创建管理员账户..."
    
    # 等待MySQL启动
    sleep 10
    
    # 进入web容器创建管理员
    docker-compose exec web python -c "
from main import app, db, User
from werkzeug.security import generate_password_hash

with app.app_context():
    db.create_all()
    # 检查是否已存在管理员
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
    
    log_success "管理员账户设置完成"
}

# 显示部署信息
show_deployment_info() {
    log_success "部署完成！"
    echo
    echo "=========================================="
    echo "万里的秘密基地 - 部署信息"
    echo "=========================================="
    echo "访问地址: http://localhost"
    echo "管理后台: http://localhost/admin"
    echo "管理员账户: admin / admin123"
    echo "=========================================="
    echo
    echo "常用命令:"
    echo "查看服务状态: docker-compose ps"
    echo "查看日志: docker-compose logs"
    echo "重启服务: docker-compose restart"
    echo "停止服务: docker-compose down"
    echo "更新服务: docker-compose up -d --build"
    echo "=========================================="
}

# 主函数
main() {
    log_info "开始部署万里的秘密基地..."
    
    # 检查系统要求
    check_root
    detect_os
    
    # 安装依赖
    install_docker
    install_docker_compose
    
    # 创建配置
    create_env_file
    create_directories
    
    # 部署服务
    deploy_services
    
    # 创建管理员账户
    create_admin_user
    
    # 显示部署信息
    show_deployment_info
}

# 运行主函数
main "$@" 