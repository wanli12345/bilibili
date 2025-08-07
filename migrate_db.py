#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库迁移脚本 - 添加万里币和三连功能字段
"""

from main import app, db, User, Video
import json

def migrate_database():
    """迁移数据库，添加新字段"""
    with app.app_context():
        try:
            # 检查并添加万里币字段
            print("正在检查用户表...")
            users = User.query.all()
            for user in users:
                if not hasattr(user, 'wanli_coins'):
                    print(f"为用户 {user.username} 添加万里币字段")
                    user.wanli_coins = 0
                if not hasattr(user, 'last_login_date'):
                    print(f"为用户 {user.username} 添加最后登录日期字段")
                    user.last_login_date = None
            
            # 检查并添加三连字段
            print("正在检查视频表...")
            videos = Video.query.all()
            for video in videos:
                if not hasattr(video, 'triple_likes'):
                    print(f"为视频 {video.title} 添加三连字段")
                    video.triple_likes = 0
                if not hasattr(video, 'triple_users'):
                    print(f"为视频 {video.title} 添加三连用户字段")
                    video.triple_users = '[]'
            
            # 提交更改
            db.session.commit()
            print("✅ 数据库迁移完成！")
            
            # 显示统计信息
            print(f"\n统计信息:")
            print(f"- 用户总数: {len(users)}")
            print(f"- 视频总数: {len(videos)}")
            
        except Exception as e:
            print(f"迁移过程中出错: {e}")
            db.session.rollback()

if __name__ == '__main__':
    migrate_database() 