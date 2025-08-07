#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查新数据库结构
"""

from main import app, db, User, Video, Danmaku

def check_database():
    """检查数据库结构"""
    with app.app_context():
        try:
            # 检查用户表
            print("检查用户表...")
            users = User.query.all()
            print(f"用户数量: {len(users)}")
            
            if users:
                user = users[0]
                print(f"用户字段: {[attr for attr in dir(user) if not attr.startswith('_')]}")
                print(f"万里币字段存在: {hasattr(user, 'wanli_coins')}")
                print(f"最后登录日期字段存在: {hasattr(user, 'last_login_date')}")
            
            # 检查视频表
            print("\n检查视频表...")
            videos = Video.query.all()
            print(f"视频数量: {len(videos)}")
            
            if videos:
                video = videos[0]
                print(f"视频字段: {[attr for attr in dir(video) if not attr.startswith('_')]}")
                print(f"三连数量字段存在: {hasattr(video, 'triple_likes')}")
                print(f"三连用户字段存在: {hasattr(video, 'triple_users')}")
            
            # 检查弹幕表
            print("\n检查弹幕表...")
            danmakus = Danmaku.query.all()
            print(f"弹幕数量: {len(danmakus)}")
            
            if danmakus:
                danmaku = danmakus[0]
                print(f"弹幕字段: {[attr for attr in dir(danmaku) if not attr.startswith('_')]}")
                print(f"作者关系存在: {hasattr(danmaku, 'author')}")
            
            print("\n✅ 数据库检查完成！")
            
        except Exception as e:
            print(f"检查数据库时出错: {e}")

if __name__ == '__main__':
    check_database() 