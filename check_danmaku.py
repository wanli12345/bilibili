#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查弹幕表是否正确创建
"""

from main import app, db, Danmaku, User

def check_danmaku_table():
    """检查弹幕表状态"""
    with app.app_context():
        try:
            # 检查表是否存在
            with db.engine.connect() as conn:
                result = conn.execute(db.text("SELECT name FROM sqlite_master WHERE type='table' AND name='danmaku'"))
                tables = [row[0] for row in result]
                
                if 'danmaku' in tables:
                    print("✅ 弹幕表存在")
                    
                    # 检查表结构
                    result = conn.execute(db.text("PRAGMA table_info(danmaku)"))
                    columns = [row[1] for row in result]
                    print(f"弹幕表字段: {columns}")
                    
                    # 检查是否有数据
                    count = Danmaku.query.count()
                    print(f"弹幕数量: {count}")
                    
                else:
                    print("❌ 弹幕表不存在")
                    print("正在创建弹幕表...")
                    db.create_all()
                    print("✅ 弹幕表创建完成")
                    
        except Exception as e:
            print(f"检查弹幕表时出错: {e}")

if __name__ == '__main__':
    check_danmaku_table() 