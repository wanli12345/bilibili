#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试弹幕功能
"""

from main import app, db, User, Video, Danmaku
from datetime import datetime

def test_danmaku():
    """测试弹幕功能"""
    with app.app_context():
        try:
            # 获取用户和视频
            user = User.query.first()
            video = Video.query.first()
            
            if not user or not video:
                print("需要先创建用户和视频")
                return
            
            print(f"测试用户: {user.username}")
            print(f"测试视频: {video.title}")
            
            # 创建测试弹幕
            danmaku = Danmaku(
                content="测试弹幕",
                user_id=user.id,
                video_id=video.id,
                time=10.5,
                type='scroll',
                color='#ffffff'
            )
            
            db.session.add(danmaku)
            db.session.commit()
            
            print(f"✅ 弹幕创建成功！ID: {danmaku.id}")
            print(f"弹幕内容: {danmaku.content}")
            print(f"弹幕作者: {danmaku.author.username}")
            print(f"弹幕时间: {danmaku.time}秒")
            
            # 测试获取弹幕
            danmakus = Danmaku.query.filter_by(video_id=video.id).all()
            print(f"\n视频 {video.title} 的弹幕数量: {len(danmakus)}")
            
            for d in danmakus:
                print(f"- {d.content} (作者: {d.author.username}, 时间: {d.time}秒)")
            
        except Exception as e:
            print(f"测试弹幕功能时出错: {e}")

if __name__ == '__main__':
    test_danmaku() 