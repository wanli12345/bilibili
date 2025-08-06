#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
重置管理员密码
"""

from main import app, db, User
from werkzeug.security import generate_password_hash

with app.app_context():
    # 查找管理员用户
    admin = User.query.filter_by(username='admin').first()
    if admin:
        # 重置密码
        admin.password_hash = generate_password_hash('admin123')
        admin.password_changed = False  # 重置为未修改状态
        db.session.commit()
        print("✅ 管理员密码已重置为: admin123")
        print("✅ 密码状态已重置为未修改")
    else:
        print("❌ 没有找到管理员用户") 