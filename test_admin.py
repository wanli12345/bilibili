#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
管理后台功能测试脚本
"""

import requests
import json
import time

BASE_URL = "http://localhost:5000"

def test_admin_login():
    """测试管理员登录"""
    print("🔐 测试管理员登录...")
    
    # 测试默认密码登录
    login_data = {
        'username': 'admin',
        'password': 'admin123'
    }
    
    response = requests.post(f"{BASE_URL}/login", data=login_data)
    
    if response.status_code == 302:
        print("✅ 管理员登录成功，应该重定向到修改密码页面")
        return True
    else:
        print(f"❌ 管理员登录失败: {response.status_code}")
        return False

def test_password_change():
    """测试密码修改"""
    print("\n🔑 测试密码修改...")
    
    # 模拟密码修改请求
    password_data = {
        'current_password': 'admin123',
        'new_password': 'Admin123!@#',
        'confirm_password': 'Admin123!@#'
    }
    
    # 这里需要先登录获取session
    session = requests.Session()
    session.post(f"{BASE_URL}/login", data={'username': 'admin', 'password': 'admin123'})
    
    response = session.post(f"{BASE_URL}/change_admin_password", data=password_data)
    
    if response.status_code == 302:
        print("✅ 密码修改成功")
        return True
    else:
        print(f"❌ 密码修改失败: {response.status_code}")
        return False

def test_admin_dashboard():
    """测试管理后台页面"""
    print("\n📊 测试管理后台页面...")
    
    session = requests.Session()
    session.post(f"{BASE_URL}/login", data={'username': 'admin', 'password': 'admin123'})
    
    response = session.get(f"{BASE_URL}/admin")
    
    if response.status_code == 200:
        print("✅ 管理后台页面访问成功")
        return True
    else:
        print(f"❌ 管理后台页面访问失败: {response.status_code}")
        return False

def test_video_review():
    """测试视频审核功能"""
    print("\n🎬 测试视频审核功能...")
    
    session = requests.Session()
    session.post(f"{BASE_URL}/login", data={'username': 'admin', 'password': 'admin123'})
    
    # 测试审核通过
    review_data = {
        'action': 'approve',
        'comment': '测试审核通过'
    }
    
    response = session.post(f"{BASE_URL}/admin/review_video/1", data=review_data)
    
    if response.status_code == 200:
        result = response.json()
        if result.get('status') == 'success':
            print("✅ 视频审核功能正常")
            return True
        else:
            print(f"❌ 视频审核失败: {result.get('message')}")
            return False
    else:
        print(f"❌ 视频审核请求失败: {response.status_code}")
        return False

def test_user_management():
    """测试用户管理功能"""
    print("\n👥 测试用户管理功能...")
    
    session = requests.Session()
    session.post(f"{BASE_URL}/login", data={'username': 'admin', 'password': 'admin123'})
    
    # 测试更新用户信息
    user_data = {
        'username': 'testuser',
        'email': 'test@example.com',
        'is_active': 'true'
    }
    
    response = session.post(f"{BASE_URL}/admin/update_user/2", data=user_data)
    
    if response.status_code == 200:
        result = response.json()
        if result.get('status') == 'success':
            print("✅ 用户管理功能正常")
            return True
        else:
            print(f"❌ 用户管理失败: {result.get('message')}")
            return False
    else:
        print(f"❌ 用户管理请求失败: {response.status_code}")
        return False

def main():
    """主测试函数"""
    print("🚀 开始测试万里的秘密基地管理后台功能")
    print("=" * 50)
    
    tests = [
        test_admin_login,
        test_password_change,
        test_admin_dashboard,
        test_video_review,
        test_user_management
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ 测试异常: {str(e)}")
    
    print("\n" + "=" * 50)
    print(f"📈 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！管理后台功能正常")
    else:
        print("⚠️  部分测试失败，请检查功能")

if __name__ == "__main__":
    main() 