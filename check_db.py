#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
检查数据库中的用户
"""

from main import app, db, User

with app.app_context():
    # 创建数据库表
    db.create_all()
    
    # 检查是否有管理员用户
    admin = User.query.filter_by(username='admin').first()
    if admin:
        print(f"✅ 找到管理员用户: {admin.username}")
        print(f"   邮箱: {admin.email}")
        print(f"   是否管理员: {admin.is_admin}")
        print(f"   是否激活: {admin.is_active}")
        print(f"   密码已修改: {admin.password_changed}")
    else:
        print("❌ 没有找到管理员用户")
        
        # 创建管理员用户
        from werkzeug.security import generate_password_hash
        admin = User(
            username='admin',
            email='admin@wanli.com',
            password_hash=generate_password_hash('admin123'),
            is_admin=True,
            password_changed=False
        )
        db.session.add(admin)
        db.session.commit()
        print("✅ 已创建管理员用户")
    
    # 显示所有用户
    users = User.query.all()
    print(f"\n📊 数据库中共有 {len(users)} 个用户:")
    for user in users:
        print(f"   - {user.username} ({user.email}) - 管理员: {user.is_admin}") 