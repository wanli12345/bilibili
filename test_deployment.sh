#!/bin/bash

# 万里的秘密基地 - 部署测试脚本

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

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

# 测试Docker服务
test_docker() {
    log_info "测试Docker服务..."
    
    if ! command -v docker &> /dev/null; then
        log_error "Docker未安装"
        return 1
    fi
    
    if ! docker info &> /dev/null; then
        log_error "Docker服务未运行"
        return 1
    fi
    
    log_success "Docker服务正常"
    return 0
}

# 测试Docker Compose
test_docker_compose() {
    log_info "测试Docker Compose..."
    
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose未安装"
        return 1
    fi
    
    log_success "Docker Compose正常"
    return 0
}

# 测试容器状态
test_containers() {
    log_info "测试容器状态..."
    
    if ! docker-compose ps | grep -q "Up"; then
        log_error "容器未运行"
        return 1
    fi
    
    # 检查各个服务
    services=("web" "mysql" "nginx")
    for service in "${services[@]}"; do
        if ! docker-compose ps | grep -q "$service.*Up"; then
            log_error "$service 服务未运行"
            return 1
        fi
    done
    
    log_success "所有容器运行正常"
    return 0
}

# 测试网络连接
test_network() {
    log_info "测试网络连接..."
    
    # 测试HTTP连接
    if curl -s http://localhost > /dev/null; then
        log_success "HTTP服务正常"
    else
        log_error "HTTP服务无法访问"
        return 1
    fi
    
    # 测试管理后台
    if curl -s http://localhost/admin > /dev/null; then
        log_success "管理后台可访问"
    else
        log_warning "管理后台可能未配置"
    fi
    
    return 0
}

# 测试数据库连接
test_database() {
    log_info "测试数据库连接..."
    
    if docker-compose exec web python -c "
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
    exit(1)
" 2>/dev/null; then
        log_success "数据库连接正常"
        return 0
    else
        log_error "数据库连接失败"
        return 1
    fi
}

# 测试文件上传
test_upload() {
    log_info "测试文件上传功能..."
    
    # 检查上传目录
    if [ -d "static/uploads" ]; then
        log_success "上传目录存在"
    else
        log_error "上传目录不存在"
        return 1
    fi
    
    # 检查权限
    if [ -w "static/uploads" ]; then
        log_success "上传目录可写"
    else
        log_error "上传目录不可写"
        return 1
    fi
    
    return 0
}

# 显示系统信息
show_system_info() {
    log_info "系统信息:"
    echo "操作系统: $(uname -s) $(uname -r)"
    echo "Docker版本: $(docker --version)"
    echo "Docker Compose版本: $(docker-compose --version)"
    echo "磁盘使用: $(df -h . | tail -1)"
    echo "内存使用: $(free -h | grep Mem | awk '{print $3"/"$2}')"
    echo
}

# 显示服务状态
show_service_status() {
    log_info "服务状态:"
    docker-compose ps
    echo
}

# 显示访问信息
show_access_info() {
    log_success "部署测试完成！"
    echo
    echo "=========================================="
    echo "万里的秘密基地 - 访问信息"
    echo "=========================================="
    echo "网站地址: http://localhost"
    echo "管理后台: http://localhost/admin"
    echo "管理员账户: admin / admin123"
    echo "=========================================="
    echo
    echo "常用命令:"
    echo "查看状态: docker-compose ps"
    echo "查看日志: docker-compose logs"
    echo "重启服务: docker-compose restart"
    echo "停止服务: docker-compose down"
    echo "=========================================="
}

# 主函数
main() {
    log_info "开始测试万里的秘密基地部署..."
    echo
    
    show_system_info
    
    # 运行测试
    tests=(
        "test_docker"
        "test_docker_compose"
        "test_containers"
        "test_network"
        "test_database"
        "test_upload"
    )
    
    failed_tests=0
    
    for test in "${tests[@]}"; do
        if $test; then
            log_success "$test 通过"
        else
            log_error "$test 失败"
            ((failed_tests++))
        fi
        echo
    done
    
    show_service_status
    
    if [ $failed_tests -eq 0 ]; then
        show_access_info
    else
        log_error "有 $failed_tests 个测试失败，请检查部署"
        exit 1
    fi
}

# 运行主函数
main "$@" 