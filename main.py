# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
import re
from datetime import datetime
import uuid

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
# 数据库配置
import os
from urllib.parse import quote_plus

# 获取环境变量，如果没有则使用默认值
MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
MYSQL_PORT = os.getenv('MYSQL_PORT', '3306')
MYSQL_DATABASE = os.getenv('MYSQL_DATABASE', 'wanli_video')
MYSQL_USER = os.getenv('MYSQL_USER', 'wanli_user')
MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', 'wanli123456')

# 构建数据库URI
if os.getenv('FLASK_ENV') == 'production':
    # 生产环境使用MySQL
    DATABASE_URI = f"mysql+pymysql://{MYSQL_USER}:{quote_plus(MYSQL_PASSWORD)}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}?charset=utf8mb4"
else:
    # 开发环境使用SQLite
    DATABASE_URI = 'sqlite:///bilibili_clone.db'

app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['AVATAR_FOLDER'] = 'static/avatars'
app.config['THUMBNAIL_FOLDER'] = 'static/thumbnails'
app.config['SITE_ASSET_FOLDER'] = 'static/site'
app.config['MAX_CONTENT_LENGTH'] = None  # 禁用文件大小限制

# 确保上传目录存在
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['AVATAR_FOLDER'], exist_ok=True)
os.makedirs(app.config['THUMBNAIL_FOLDER'], exist_ok=True)
os.makedirs(app.config['SITE_ASSET_FOLDER'], exist_ok=True)

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# 关注关系表
follows = db.Table('follows',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'), primary_key=True)
)

# 数据模型
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    avatar = db.Column(db.String(200), default='牛.png')
    is_admin = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)  # 用户是否激活
    password_changed = db.Column(db.Boolean, default=False)  # 是否已修改默认密码
    wanli_coins = db.Column(db.Integer, default=10)  # 万里币，新用户默认10个
    received_likes = db.Column(db.Integer, default=0)  # 收到的赞数量
    last_login_date = db.Column(db.Date)  # 最后登录日期
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    videos = db.relationship('Video', foreign_keys='Video.user_id', backref='author', lazy=True)
    comments = db.relationship('Comment', backref='author', lazy=True)
    
    # 关注关系
    following = db.relationship(
        'User', secondary='follows',
        primaryjoin='User.id == follows.c.follower_id',
        secondaryjoin='User.id == follows.c.followed_id',
        backref=db.backref('followers', lazy='dynamic'),
        lazy='dynamic'
    )

class Video(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    filename = db.Column(db.String(200), nullable=False)
    thumbnail = db.Column(db.String(200))
    views = db.Column(db.Integer, default=0)
    likes = db.Column(db.Integer, default=0)
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    review_comment = db.Column(db.Text)  # 审核意见
    reviewed_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    reviewed_at = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    comments = db.relationship('Comment', backref='video', lazy=True)
    
    # 三连功能
    triple_likes = db.Column(db.Integer, default=0)  # 三连数量
    triple_users = db.Column(db.Text, default='[]')  # 已三连的用户ID列表（JSON格式）
    
    # 明确指定外键关系
    reviewer = db.relationship('User', foreign_keys=[reviewed_by], backref='reviewed_videos')

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    video_id = db.Column(db.Integer, db.ForeignKey('video.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Danmaku(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    video_id = db.Column(db.Integer, db.ForeignKey('video.id'), nullable=False)
    time = db.Column(db.Float, nullable=False)  # 弹幕出现的时间点（秒）
    type = db.Column(db.String(20), default='scroll')  # 弹幕类型：scroll(滚动), top(顶部), bottom(底部)
    color = db.Column(db.String(7), default='#ffffff')  # 弹幕颜色
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 添加关系
    author = db.relationship('User', backref='danmakus')

# 站点设置
class SiteSetting(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    site_name = db.Column(db.String(200), default='万里的秘密基地')
    page_title = db.Column(db.String(200), nullable=True)  # 首页 <title>
    homepage_bg_image = db.Column(db.String(255), nullable=True)  # 首页背景图文件名（相对 static/site）
    homepage_bg_color1 = db.Column(db.String(20), default='#667eea')
    homepage_bg_color2 = db.Column(db.String(20), default='#764ba2')

def get_site_settings() -> SiteSetting:
    settings = SiteSetting.query.first()
    if not settings:
        settings = SiteSetting()
        db.session.add(settings)
        db.session.commit()
    return settings

@app.context_processor
def inject_site_settings():
    try:
        settings = get_site_settings()
    except Exception:
        # 在数据库尚未创建时避免模板渲染失败
        class _Fallback:
            site_name = '万里的秘密基地'
            page_title = None
            homepage_bg_image = None
            homepage_bg_color1 = '#667eea'
            homepage_bg_color2 = '#764ba2'
        settings = _Fallback()
    return {'settings': settings}

def validate_password(password):
    """验证密码强度"""
    if len(password) < 12:
        return False, "密码长度必须至少12位"
    
    if not re.search(r'[0-9]', password):
        return False, "密码必须包含数字"
    
    if not re.search(r'[a-zA-Z]', password):
        return False, "密码必须包含字母"
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "密码必须包含特殊字符"
    
    return True, "密码符合要求"

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

# 路由
@app.route('/')
def index():
    videos = Video.query.filter_by(status='approved').order_by(Video.created_at.desc()).limit(12).all()
    return render_template('index.html', videos=videos)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest' or 'application/json' in (request.headers.get('Accept') or '')
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            # 检查每日登录奖励
            today = datetime.now().date()
            if user.last_login_date != today:
                user.wanli_coins += 1
                user.last_login_date = today
                db.session.commit()
                flash(f'欢迎{user.username}同学的到来！获得1万里币奖励！')
            else:
                flash(f'欢迎{user.username}同学的到来！')
            
            if user.is_admin and not user.password_changed:
                # 管理员首次登录，重定向到修改密码页面
                login_user(user)
                return redirect(url_for('change_admin_password'))
            else:
                login_user(user)
                if is_ajax:
                    return jsonify({'success': True, 'redirect_url': url_for('index')}), 200
                return redirect(url_for('index'))
        else:
            if is_ajax:
                return jsonify({'success': False, 'message': '用户名或密码错误'}), 400
            flash('用户名或密码错误')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest' or 'application/json' in (request.headers.get('Accept') or '')
        
        if User.query.filter_by(username=username).first():
            if is_ajax:
                return jsonify({'success': False, 'message': '用户名已存在'}), 400
            flash('用户名已存在')
            return render_template('register.html')
        
        if User.query.filter_by(email=email).first():
            if is_ajax:
                return jsonify({'success': False, 'message': '邮箱已存在'}), 400
            flash('邮箱已存在')
            return render_template('register.html')
        
        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
            wanli_coins=10  # 新用户默认10个万里币
        )
        db.session.add(user)
        db.session.commit()
        
        if is_ajax:
            return jsonify({'success': True, 'redirect_url': url_for('login')}), 200
        flash('注册成功，请登录')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == 'POST':
        try:
            print("开始处理文件上传...")
            
            if 'video' not in request.files:
                flash('没有选择文件')
                return redirect(request.url)
            
            file = request.files['video']
            if file.filename == '':
                flash('没有选择文件')
                return redirect(request.url)
            
            print(f"文件名: {file.filename}")
            
            # 自定义文件大小检查（500MB）
            max_size = 500 * 1024 * 1024  # 500MB
            
            # 检查文件大小
            file.seek(0, 2)  # 移动到文件末尾
            file_size = file.tell()
            file.seek(0)  # 重置到文件开头
            
            print(f"文件大小: {file_size} bytes ({file_size // (1024*1024)}MB)")
            print(f"最大允许: {max_size} bytes ({max_size // (1024*1024)}MB)")
            
            if file_size > max_size:
                flash(f'文件太大，最大支持 500MB，当前文件大小: {file_size // (1024*1024)}MB')
                return redirect(request.url)
            
            if file:
                filename = secure_filename(file.filename)
                unique_filename = f"{uuid.uuid4()}_{filename}"
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                
                print(f"保存文件到: {file_path}")
                file.save(file_path)
                
                # 处理视频封面
                thumbnail_filename = None
                if 'thumbnail' in request.files:
                    thumbnail_file = request.files['thumbnail']
                    if thumbnail_file.filename != '':
                        # 检查封面文件类型
                        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
                        if '.' in thumbnail_file.filename and thumbnail_file.filename.rsplit('.', 1)[1].lower() in allowed_extensions:
                            thumbnail_filename = secure_filename(thumbnail_file.filename)
                            thumbnail_unique_filename = f"{uuid.uuid4()}_{thumbnail_filename}"
                            thumbnail_path = os.path.join(app.config['THUMBNAIL_FOLDER'], thumbnail_unique_filename)
                            thumbnail_file.save(thumbnail_path)
                            thumbnail_filename = thumbnail_unique_filename
                            print(f"保存封面到: {thumbnail_path}")
                
                video = Video(
                    title=request.form.get('title'),
                    description=request.form.get('description'),
                    filename=unique_filename,
                    thumbnail=thumbnail_filename,
                    user_id=current_user.id
                )
                db.session.add(video)
                db.session.commit()
                
                print("视频上传成功！")
                flash('视频上传成功！')
                return redirect(url_for('index'))
        except Exception as e:
            print(f"上传错误: {str(e)}")
            flash(f'上传失败：{str(e)}')
            return redirect(request.url)
    
    return render_template('upload.html')

@app.route('/video/<int:video_id>')
def video(video_id):
    video = Video.query.get_or_404(video_id)
    video.views += 1
    db.session.commit()
    
    comments = Comment.query.filter_by(video_id=video_id).order_by(Comment.created_at.desc()).all()
    return render_template('video.html', video=video, comments=comments)

@app.route('/comment', methods=['POST'])
@login_required
def add_comment():
    content = request.form.get('content')
    video_id = request.form.get('video_id')
    
    if content and video_id:
        comment = Comment(
            content=content,
            user_id=current_user.id,
            video_id=video_id
        )
        db.session.add(comment)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'comment': {
                'id': comment.id,
                'content': comment.content,
                'author': comment.author.username,
                'created_at': comment.created_at.strftime('%Y-%m-%d %H:%M')
            }
        })
    
    return jsonify({'status': 'error', 'message': '评论内容不能为空'})

@app.route('/danmaku', methods=['POST'])
@login_required
def add_danmaku():
    content = request.form.get('content')
    video_id = request.form.get('video_id')
    time = request.form.get('time')
    danmaku_type = request.form.get('type', 'scroll')
    color = request.form.get('color', '#ffffff')
    
    if content and video_id and time:
        try:
            time_float = float(time)
            danmaku = Danmaku(
                content=content,
                user_id=current_user.id,
                video_id=video_id,
                time=time_float,
                type=danmaku_type,
                color=color
            )
            db.session.add(danmaku)
            db.session.commit()
            
            return jsonify({
                'status': 'success',
                'danmaku': {
                    'id': danmaku.id,
                    'content': danmaku.content,
                    'author': danmaku.author.username,
                    'time': danmaku.time,
                    'type': danmaku.type,
                    'color': danmaku.color
                }
            })
        except ValueError:
            return jsonify({'status': 'error', 'message': '时间格式错误'})
    
    return jsonify({'status': 'error', 'message': '弹幕内容不能为空'})

@app.route('/danmaku/<int:video_id>')
def get_danmaku(video_id):
    danmakus = Danmaku.query.filter_by(video_id=video_id).order_by(Danmaku.time).all()
    return jsonify({
        'status': 'success',
        'danmakus': [{
            'id': d.id,
            'content': d.content,
            'author': d.author.username,
            'time': d.time,
            'type': d.type,
            'color': d.color
        } for d in danmakus]
    })

@app.route('/like_user/<int:user_id>', methods=['POST'])
@login_required
def like_user(user_id):
    """点赞用户"""
    if current_user.id == user_id:
        return jsonify({'status': 'error', 'message': '不能给自己点赞'})
    
    target_user = User.query.get_or_404(user_id)
    target_user.received_likes += 1
    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'message': '点赞成功！',
        'received_likes': target_user.received_likes
    })

@app.route('/coin_user/<int:user_id>', methods=['POST'])
@login_required
def coin_user(user_id):
    """投币给用户"""
    if current_user.id == user_id:
        return jsonify({'status': 'error', 'message': '不能给自己投币'})
    
    coin_amount = request.form.get('amount', type=int)
    if not coin_amount or coin_amount <= 0:
        return jsonify({'status': 'error', 'message': '投币数量必须大于0'})
    
    if current_user.wanli_coins < coin_amount:
        return jsonify({'status': 'error', 'message': f'万里币不足！您只有{current_user.wanli_coins}个万里币'})
    
    target_user = User.query.get_or_404(user_id)
    
    # 转移万里币
    current_user.wanli_coins -= coin_amount
    target_user.wanli_coins += coin_amount
    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'message': f'投币成功！投出{coin_amount}个万里币',
        'my_coins': current_user.wanli_coins,
        'target_coins': target_user.wanli_coins
    })

@app.route('/follow_user/<int:user_id>', methods=['POST'])
@login_required
def follow_user(user_id):
    """关注用户"""
    if current_user.id == user_id:
        return jsonify({'status': 'error', 'message': '不能关注自己'})
    
    target_user = User.query.get_or_404(user_id)
    
    if current_user.following.filter_by(id=user_id).first():
        # 取消关注
        current_user.following.remove(target_user)
        db.session.commit()
        return jsonify({
            'status': 'success',
            'message': '取消关注成功',
            'is_following': False
        })
    else:
        # 关注
        current_user.following.append(target_user)
        db.session.commit()
        return jsonify({
            'status': 'success',
            'message': '关注成功',
            'is_following': True
        })

@app.route('/triple_like/<int:video_id>', methods=['POST'])
@login_required
def triple_like(video_id):
    """三连功能"""
    import json
    
    video = Video.query.get_or_404(video_id)
    triple_users = json.loads(video.triple_users)
    
    if current_user.id in triple_users:
        return jsonify({'status': 'error', 'message': '您已经三连过了'})
    
    # 添加三连
    triple_users.append(current_user.id)
    video.triple_likes += 1
    video.triple_users = json.dumps(triple_users)
    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'message': '三连成功！',
        'triple_likes': video.triple_likes
    })

@app.route('/admin')
@login_required
def admin():
    if not current_user.is_admin:
        flash('您没有管理员权限')
        return redirect(url_for('index'))
    
    # 检查管理员是否已修改密码
    if not current_user.password_changed:
        return redirect(url_for('change_admin_password'))
    
    users = User.query.filter(User.id != current_user.id).all()
    pending_videos = Video.query.filter_by(status='pending').all()
    approved_videos = Video.query.filter_by(status='approved').all()
    rejected_videos = Video.query.filter_by(status='rejected').all()
    comments = Comment.query.all()
    
    return render_template('admin.html', 
                         users=users, 
                         pending_videos=pending_videos,
                         approved_videos=approved_videos,
                         rejected_videos=rejected_videos,
                         comments=comments)

@app.route('/admin/settings', methods=['GET', 'POST'])
@login_required
def admin_settings():
    if not current_user.is_admin:
        flash('您没有管理员权限')
        return redirect(url_for('index'))
    # 管理员首次登录需先改密
    if not current_user.password_changed:
        return redirect(url_for('change_admin_password'))

    settings = get_site_settings()
    if request.method == 'POST':
        site_name = request.form.get('site_name', '').strip()
        page_title = request.form.get('page_title', '').strip()
        color1 = request.form.get('homepage_bg_color1', '').strip()
        color2 = request.form.get('homepage_bg_color2', '').strip()
        if site_name:
            settings.site_name = site_name
        settings.page_title = page_title or None
        if color1:
            settings.homepage_bg_color1 = color1
        if color2:
            settings.homepage_bg_color2 = color2
        db.session.commit()
        flash('站点设置已保存')
        return redirect(url_for('admin_settings'))

    return render_template('admin_settings.html', settings=settings)

@app.route('/admin/settings/upload_bg', methods=['POST'])
@login_required
def admin_settings_upload_bg():
    if not current_user.is_admin:
        return jsonify({'status': 'error', 'message': '权限不足'}), 403
    settings = get_site_settings()
    if 'bg' not in request.files:
        return jsonify({'status': 'error', 'message': '未选择文件'}), 400
    file = request.files['bg']
    if file.filename == '':
        return jsonify({'status': 'error', 'message': '未选择文件'}), 400
    allowed = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    if '.' not in file.filename or file.filename.rsplit('.', 1)[1].lower() not in allowed:
        return jsonify({'status': 'error', 'message': '仅支持 png/jpg/jpeg/gif/webp'}), 400
    # 限制大小 5MB
    file.seek(0, 2); size = file.tell(); file.seek(0)
    if size > 5 * 1024 * 1024:
        return jsonify({'status': 'error', 'message': '文件不能超过5MB'}), 400
    filename = secure_filename(file.filename)
    unique = f"{uuid.uuid4()}_{filename}"
    path = os.path.join(app.config['SITE_ASSET_FOLDER'], unique)
    file.save(path)
    settings.homepage_bg_image = unique
    db.session.commit()
    return jsonify({'status': 'success', 'filename': unique})

@app.route('/admin/settings/reset_bg', methods=['POST'])
@login_required
def admin_settings_reset_bg():
    if not current_user.is_admin:
        return jsonify({'status': 'error', 'message': '权限不足'}), 403
    settings = get_site_settings()
    settings.homepage_bg_image = None
    db.session.commit()
    return jsonify({'status': 'success'})

@app.route('/admin/delete_video/<int:video_id>', methods=['POST'])
@login_required
def delete_video(video_id):
    if not current_user.is_admin:
        return jsonify({'status': 'error', 'message': '权限不足'})
    
    video = Video.query.get_or_404(video_id)
    db.session.delete(video)
    db.session.commit()
    
    return jsonify({'status': 'success'})

@app.route('/admin/review_video/<int:video_id>', methods=['POST'])
@login_required
def review_video(video_id):
    if not current_user.is_admin:
        return jsonify({'status': 'error', 'message': '权限不足'})
    
    video = Video.query.get_or_404(video_id)
    action = request.form.get('action')  # approve 或 reject
    comment = request.form.get('comment', '')
    
    if action == 'approve':
        video.status = 'approved'
        video.review_comment = comment
        video.reviewed_by = current_user.id
        video.reviewed_at = datetime.utcnow()
        db.session.commit()
        return jsonify({'status': 'success', 'message': '视频审核通过'})
    elif action == 'reject':
        video.status = 'rejected'
        video.review_comment = comment
        video.reviewed_by = current_user.id
        video.reviewed_at = datetime.utcnow()
        db.session.commit()
        return jsonify({'status': 'success', 'message': '视频审核拒绝'})
    else:
        return jsonify({'status': 'error', 'message': '无效的操作'})

@app.route('/admin/update_user/<int:user_id>', methods=['POST'])
@login_required
def update_user(user_id):
    if not current_user.is_admin:
        return jsonify({'status': 'error', 'message': '权限不足'})
    
    user = User.query.get_or_404(user_id)
    username = request.form.get('username')
    email = request.form.get('email')
    is_active = request.form.get('is_active') == 'true'
    
    # 检查用户名是否已存在
    existing_user = User.query.filter_by(username=username).first()
    if existing_user and existing_user.id != user_id:
        return jsonify({'status': 'error', 'message': '用户名已存在'})
    
    # 检查邮箱是否已存在
    existing_email = User.query.filter_by(email=email).first()
    if existing_email and existing_email.id != user_id:
        return jsonify({'status': 'error', 'message': '邮箱已存在'})
    
    user.username = username
    user.email = email
    user.is_active = is_active
    db.session.commit()
    
    return jsonify({'status': 'success', 'message': '用户信息更新成功'})

@app.route('/admin/reset_user_password/<int:user_id>', methods=['POST'])
@login_required
def reset_user_password(user_id):
    if not current_user.is_admin:
        return jsonify({'status': 'error', 'message': '权限不足'})
    
    user = User.query.get_or_404(user_id)
    new_password = request.form.get('new_password')
    
    # 验证密码强度
    is_valid, message = validate_password(new_password)
    if not is_valid:
        return jsonify({'status': 'error', 'message': message})
    
    user.password_hash = generate_password_hash(new_password)
    user.password_changed = False  # 重置为未修改状态
    db.session.commit()
    
    return jsonify({'status': 'success', 'message': '用户密码重置成功'})

@app.route('/admin/delete_user/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    if not current_user.is_admin:
        return jsonify({'status': 'error', 'message': '权限不足'})
    
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        return jsonify({'status': 'error', 'message': '不能删除自己'})
    
    # 软删除：将用户标记为非激活状态
    user.is_active = False
    db.session.commit()
    
    return jsonify({'status': 'success', 'message': '用户已禁用'})

@app.route('/profile')
@login_required
def profile():
    # 获取用户的所有视频，按状态分组
    pending_videos = Video.query.filter_by(user_id=current_user.id, status='pending').all()
    approved_videos = Video.query.filter_by(user_id=current_user.id, status='approved').all()
    rejected_videos = Video.query.filter_by(user_id=current_user.id, status='rejected').all()
    
    return render_template('profile.html', 
                         pending_videos=pending_videos,
                         approved_videos=approved_videos,
                         rejected_videos=rejected_videos)

@app.route('/following')
@login_required
def following():
    """关注列表页面"""
    following_users = current_user.following.all()
    return render_template('following.html', following_users=following_users)

@app.route('/followers')
@login_required
def followers():
    """粉丝列表页面"""
    followers_users = current_user.followers.all()
    return render_template('followers.html', followers_users=followers_users)

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    """编辑个人资料"""
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        
        # 检查用户名是否已存在（排除当前用户）
        existing_user = User.query.filter_by(username=username).first()
        if existing_user and existing_user.id != current_user.id:
            flash('用户名已存在')
            return render_template('edit_profile.html')
        
        # 检查邮箱是否已存在（排除当前用户）
        existing_email = User.query.filter_by(email=email).first()
        if existing_email and existing_email.id != current_user.id:
            flash('邮箱已存在')
            return render_template('edit_profile.html')
        
        # 更新用户信息
        current_user.username = username
        current_user.email = email
        
        # 处理头像上传
        if 'avatar' in request.files:
            avatar_file = request.files['avatar']
            if avatar_file.filename != '':
                # 检查文件类型
                allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
                if '.' in avatar_file.filename and avatar_file.filename.rsplit('.', 1)[1].lower() in allowed_extensions:
                    # 检查文件大小（最大5MB）
                    avatar_file.seek(0, 2)
                    file_size = avatar_file.tell()
                    avatar_file.seek(0)
                    
                    if file_size > 5 * 1024 * 1024:  # 5MB
                        flash('头像文件不能超过5MB')
                        return render_template('edit_profile.html')
                    
                    # 生成唯一文件名
                    filename = secure_filename(avatar_file.filename)
                    unique_filename = f"{uuid.uuid4()}_{filename}"
                    file_path = os.path.join(app.config['AVATAR_FOLDER'], unique_filename)
                    
                    avatar_file.save(file_path)
                    current_user.avatar = unique_filename
        
        db.session.commit()
        flash('个人资料更新成功！')
        return redirect(url_for('profile'))
    
    return render_template('edit_profile.html')

@app.route('/upload_avatar', methods=['POST'])
@login_required
def upload_avatar():
    try:
        if 'avatar' not in request.files:
            return jsonify({'status': 'error', 'message': '没有选择文件'})
        
        file = request.files['avatar']
        if file.filename == '':
            return jsonify({'status': 'error', 'message': '没有选择文件'})
        
        # 检查文件类型
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
        if '.' not in file.filename or file.filename.rsplit('.', 1)[1].lower() not in allowed_extensions:
            return jsonify({'status': 'error', 'message': '只支持 PNG, JPG, JPEG, GIF 格式'})
        
        # 检查文件大小（最大5MB）
        file.seek(0, 2)
        file_size = file.tell()
        file.seek(0)
        
        if file_size > 5 * 1024 * 1024:  # 5MB
            return jsonify({'status': 'error', 'message': '头像文件不能超过5MB'})
        
        # 生成唯一文件名
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4()}_{filename}"
        file_path = os.path.join(app.config['AVATAR_FOLDER'], unique_filename)
        
        file.save(file_path)
        
        # 更新用户头像
        current_user.avatar = unique_filename
        db.session.commit()
        
        return jsonify({'status': 'success', 'message': '头像上传成功', 'filename': unique_filename})
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'上传失败：{str(e)}'})

@app.route('/upload_thumbnail', methods=['POST'])
@login_required
def upload_thumbnail():
    try:
        if 'thumbnail' not in request.files:
            return jsonify({'status': 'error', 'message': '没有选择文件'})
        
        file = request.files['thumbnail']
        video_id = request.form.get('video_id')
        
        if file.filename == '':
            return jsonify({'status': 'error', 'message': '没有选择文件'})
        
        # 检查文件类型
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
        if '.' not in file.filename or file.filename.rsplit('.', 1)[1].lower() not in allowed_extensions:
            return jsonify({'status': 'error', 'message': '只支持 PNG, JPG, JPEG, GIF 格式'})
        
        # 检查文件大小（最大5MB）
        file.seek(0, 2)
        file_size = file.tell()
        file.seek(0)
        
        if file_size > 5 * 1024 * 1024:  # 5MB
            return jsonify({'status': 'error', 'message': '封面文件不能超过5MB'})
        
        # 检查视频是否存在且属于当前用户
        video = Video.query.get_or_404(video_id)
        if video.user_id != current_user.id:
            return jsonify({'status': 'error', 'message': '权限不足'})
        
        # 生成唯一文件名
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4()}_{filename}"
        file_path = os.path.join(app.config['THUMBNAIL_FOLDER'], unique_filename)
        
        file.save(file_path)
        
        # 更新视频封面
        video.thumbnail = unique_filename
        db.session.commit()
        
        return jsonify({'status': 'success', 'message': '封面更新成功', 'filename': unique_filename})
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'上传失败：{str(e)}'})

@app.route('/user/delete_video/<int:video_id>', methods=['POST'])
@login_required
def user_delete_video(video_id):
    try:
        video = Video.query.get_or_404(video_id)
        
        # 检查权限
        if video.user_id != current_user.id and not current_user.is_admin:
            return jsonify({'status': 'error', 'message': '权限不足'})
        
        # 删除视频文件
        if video.filename:
            video_path = os.path.join(app.config['UPLOAD_FOLDER'], video.filename)
            if os.path.exists(video_path):
                os.remove(video_path)
        
        # 删除封面文件
        if video.thumbnail:
            thumbnail_path = os.path.join(app.config['THUMBNAIL_FOLDER'], video.thumbnail)
            if os.path.exists(thumbnail_path):
                os.remove(thumbnail_path)
        
        # 删除数据库记录
        db.session.delete(video)
        db.session.commit()
        
        return jsonify({'status': 'success', 'message': '视频删除成功'})
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'删除失败：{str(e)}'})

@app.route('/change_admin_password', methods=['GET', 'POST'])
@login_required
def change_admin_password():
    if not current_user.is_admin:
        flash('您没有权限访问此页面')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        # 验证当前密码
        if not check_password_hash(current_user.password_hash, current_password):
            flash('当前密码错误')
            return render_template('change_admin_password.html')
        
        # 验证新密码
        is_valid, message = validate_password(new_password)
        if not is_valid:
            flash(message)
            return render_template('change_admin_password.html')
        
        # 确认密码
        if new_password != confirm_password:
            flash('两次输入的密码不一致')
            return render_template('change_admin_password.html')
        
        # 更新密码
        current_user.password_hash = generate_password_hash(new_password)
        current_user.password_changed = True
        db.session.commit()
        
        flash('密码修改成功！')
        return redirect(url_for('admin'))
    
    return render_template('change_admin_password.html')

@app.route('/search')
def search():
    query = request.args.get('q', '')
    if query:
        videos = Video.query.filter(Video.title.contains(query)).all()
    else:
        videos = []
    return render_template('search.html', videos=videos, query=query)

@app.errorhandler(413)
def too_large(e):
    flash("文件太大，请选择小于500MB的文件")
    return redirect(url_for('upload'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # 创建默认管理员账户
        if not User.query.filter_by(username='admin').first():
            admin = User(
                username='admin',
                email='admin@wanli.com',
                password_hash=generate_password_hash('admin123'),
                is_admin=True,
                password_changed=False  # 首次登录需要修改密码
            )
            db.session.add(admin)
            db.session.commit()
    # 允许通过环境变量配置运行参数，避免端口被占用
    debug_env = os.getenv('FLASK_DEBUG', os.getenv('DEBUG', '1')).lower() in ('1', 'true', 'yes', 'on')
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', os.getenv('FLASK_RUN_PORT', '80')))
    app.run(debug=debug_env, host=host, port=port)