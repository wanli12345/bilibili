#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
更新现有用户的默认头像为牛.png
"""

from main import app, db, User

def update_user_avatars():
    """更新所有使用旧默认头像的用户"""
    with app.app_context():
        # 查找所有使用旧默认头像的用户
        old_default_users = User.query.filter_by(avatar='default.jpg').all()
        
        print(f"找到 {len(old_default_users)} 个使用旧默认头像的用户")
        
        for user in old_default_users:
            print(f"更新用户 {user.username} 的头像为 牛.png")
            user.avatar = '牛.png'
        
        # 提交更改
        db.session.commit()
        print("头像更新完成！")
        
        # 显示所有用户
        all_users = User.query.all()
        print(f"\n当前所有用户头像:")
        for user in all_users:
            print(f"- {user.username}: {user.avatar}")

if __name__ == '__main__':
    update_user_avatars() 