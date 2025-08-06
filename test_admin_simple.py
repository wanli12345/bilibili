#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
简单的管理后台功能测试
"""

import requests
import time

BASE_URL = "http://localhost:5000"

def test_admin_login():
    """测试管理员登录"""
    print("🔐 测试管理员登录...")
    
    session = requests.Session()
    
    # 测试默认密码登录
    response = session.post(f"{BASE_URL}/login", data={
        'username': 'admin',
        'password': 'admin123'
    }, allow_redirects=False)
    
    if response.status_code == 302:
        location = response.headers.get('Location', '')
        if 'change_admin_password' in location:
            print("✅ 管理员登录成功，重定向到密码修改页面")
            return session
        else:
            print(f"❌ 管理员登录重定向到错误页面: {location}")
            return None
    else:
        print(f"❌ 管理员登录失败: {response.status_code}")
        return None

def test_password_change(session):
    """测试密码修改"""
    print("\n🔑 测试密码修改...")
    
    # 访问密码修改页面
    response = session.get(f"{BASE_URL}/change_admin_password")
    if response.status_code == 200:
        print("✅ 密码修改页面访问成功")
    else:
        print(f"❌ 密码修改页面访问失败: {response.status_code}")
        return False
    
    # 测试密码修改（这里只是测试页面，不实际修改密码）
    return True

def test_admin_dashboard(session):
    """测试管理后台页面"""
    print("\n📊 测试管理后台页面...")
    
    response = session.get(f"{BASE_URL}/admin")
    
    if response.status_code == 302 and 'change_admin_password' in response.headers.get('Location', ''):
        print("✅ 管理后台正确重定向到密码修改页面（因为密码未修改）")
        return True
    elif response.status_code == 200:
        print("✅ 管理后台页面访问成功")
        return True
    else:
        print(f"❌ 管理后台页面访问失败: {response.status_code}")
        return False

def test_homepage():
    """测试首页"""
    print("\n🏠 测试首页...")
    
    response = requests.get(f"{BASE_URL}/")
    
    if response.status_code == 200:
        print("✅ 首页访问成功")
        return True
    else:
        print(f"❌ 首页访问失败: {response.status_code}")
        return False

def main():
    """主测试函数"""
    print("🚀 开始测试万里的秘密基地管理后台功能")
    print("=" * 50)
    
    # 测试首页
    test_homepage()
    
    # 测试管理员登录
    session = test_admin_login()
    if session:
        # 测试密码修改页面
        test_password_change(session)
        
        # 测试管理后台
        test_admin_dashboard(session)
    
    print("\n" + "=" * 50)
    print("📋 测试完成！")
    print("\n💡 使用说明:")
    print("1. 访问 http://localhost:5000")
    print("2. 使用 admin/admin123 登录")
    print("3. 系统会自动跳转到密码修改页面")
    print("4. 设置符合要求的强密码（12位以上，包含数字、字母、特殊字符）")
    print("5. 进入管理后台进行视频审核和用户管理")

if __name__ == "__main__":
    main() 