#!/bin/bash

# Docker部署测试脚本
# 测试万里的秘密基地在云服务上的可用性

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

# 检查Docker是否安装
check_docker() {
    log_info "检查Docker环境..."
    
    if ! command -v docker &> /dev/null; then
        log_error "Docker未安装，请先安装Docker"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose未安装，请先安装Docker Compose"
        exit 1
    fi
    
    log_success "Docker环境检查通过"
}

# 检查端口是否被占用
check_ports() {
    log_info "检查端口占用情况..."
    
    local ports=("80" "443" "5000" "3306")
    
    for port in "${ports[@]}"; do
        if lsof -i :$port >/dev/null 2>&1; then
            log_warning "端口 $port 已被占用"
        else
            log_success "端口 $port 可用"
        fi
    done
}

# 构建和启动服务
deploy_services() {
    log_info "开始部署服务..."
    
    # 停止现有服务
    docker-compose down 2>/dev/null || true
    
    # 构建镜像
    log_info "构建Docker镜像..."
    docker-compose build --no-cache
    
    # 启动服务
    log_info "启动服务..."
    docker-compose up -d
    
    # 等待服务启动
    log_info "等待服务启动..."
    sleep 30
}

# 检查服务状态
check_service_status() {
    log_info "检查服务状态..."
    
    # 检查容器状态
    if docker-compose ps | grep -q "Up"; then
        log_success "所有容器运行正常"
    else
        log_error "部分容器启动失败"
        docker-compose logs
        return 1
    fi
    
    # 检查各个服务
    local services=("mysql" "web" "nginx")
    
    for service in "${services[@]}"; do
        if docker-compose ps | grep -q "$service.*Up"; then
            log_success "$service 服务运行正常"
        else
            log_error "$service 服务启动失败"
            docker-compose logs $service
        fi
    done
}

# 测试网络连接
test_network() {
    log_info "测试网络连接..."
    
    # 测试本地连接
    if curl -s http://localhost >/dev/null 2>&1; then
        log_success "本地HTTP连接正常"
    else
        log_error "本地HTTP连接失败"
    fi
    
    # 测试API端点
    if curl -s http://localhost/ >/dev/null 2>&1; then
        log_success "首页访问正常"
    else
        log_error "首页访问失败"
    fi
    
    # 测试静态文件
    if curl -s http://localhost/static/avatars/default.jpg >/dev/null 2>&1; then
        log_success "静态文件访问正常"
    else
        log_error "静态文件访问失败"
    fi
}

# 测试数据库连接
test_database() {
    log_info "测试数据库连接..."
    
    # 检查MySQL容器
    if docker-compose exec mysql mysql -u wanli_user -pwanli123456 -e "SELECT 1;" >/dev/null 2>&1; then
        log_success "数据库连接正常"
    else
        log_error "数据库连接失败"
    fi
}

# 测试应用功能
test_application() {
    log_info "测试应用功能..."
    
    # 测试注册功能
    local test_response=$(curl -s -X POST http://localhost/register \
        -H "Content-Type: application/x-www-form-urlencoded" \
        -d "username=testuser&email=test@example.com&password=testpassword123!")
    
    if echo "$test_response" | grep -q "注册成功"; then
        log_success "用户注册功能正常"
    else
        log_warning "用户注册功能测试失败（可能是正常行为）"
    fi
    
    # 测试登录功能
    local login_response=$(curl -s -X POST http://localhost/login \
        -H "Content-Type: application/x-www-form-urlencoded" \
        -d "username=admin&password=admin123")
    
    if echo "$login_response" | grep -q "302"; then
        log_success "管理员登录功能正常"
    else
        log_warning "管理员登录功能测试失败"
    fi
}

# 性能测试
performance_test() {
    log_info "进行性能测试..."
    
    # 测试并发连接
    local concurrent_users=10
    local total_requests=50
    
    log_info "测试 $concurrent_users 个并发用户，总共 $total_requests 个请求..."
    
    # 使用ab进行压力测试（如果可用）
    if command -v ab &> /dev/null; then
        ab -n $total_requests -c $concurrent_users http://localhost/ > ab_results.txt 2>&1
        log_success "压力测试完成，结果保存在 ab_results.txt"
    else
        log_warning "Apache Bench (ab) 未安装，跳过压力测试"
    fi
}

# 清理测试数据
cleanup_test_data() {
    log_info "清理测试数据..."
    
    # 删除测试用户（如果存在）
    docker-compose exec mysql mysql -u wanli_user -pwanli123456 wanli_video -e "DELETE FROM user WHERE username='testuser';" 2>/dev/null || true
    
    log_success "测试数据清理完成"
}

# 显示测试结果
show_test_results() {
    log_success "测试完成！"
    echo
    echo "=========================================="
    echo "万里的秘密基地 - 部署测试结果"
    echo "=========================================="
    echo "访问地址: http://localhost"
    echo "管理后台: http://localhost/admin"
    echo "管理员账户: admin / admin123"
    echo "=========================================="
    echo
    echo "服务状态:"
    docker-compose ps
    echo
    echo "最近日志:"
    docker-compose logs --tail=20
    echo "=========================================="
}

# 主函数
main() {
    log_info "开始测试万里的秘密基地部署..."
    
    # 检查环境
    check_docker
    check_ports
    
    # 部署服务
    deploy_services
    
    # 检查服务状态
    check_service_status
    
    # 测试网络连接
    test_network
    
    # 测试数据库
    test_database
    
    # 测试应用功能
    test_application
    
    # 性能测试
    performance_test
    
    # 清理测试数据
    cleanup_test_data
    
    # 显示结果
    show_test_results
}

# 运行主函数
main "$@" 