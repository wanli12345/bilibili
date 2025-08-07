# 万里的秘密基地 - 视频分享平台

一个类似B站的个人视频分享网站，使用Flask框架构建，具有完整的用户系统、视频管理、评论功能和管理后台。

## 功能特性

### 用户系统
用户注册/登录: 完整的用户认证系统
个人中心: 查看个人信息和上传的视频
用户头像: 支持用户头像显示

### 视频功能
视频上传: 支持MP4、AVI、MOV等格式
视频播放: 内置HTML5视频播放器
视频管理: 查看播放量、点赞数等统计
视频搜索: 按标题搜索视频

### 评论系统
发表评论: 登录用户可以发表评论
评论展示: 实时显示评论列表
评论管理: 管理员可以查看所有评论

### 管理后台
用户管理: 查看所有用户，删除用户
视频管理: 管理所有视频，删除视频
数据统计: 用户数、视频数、评论数、播放量统计
权限控制: 只有管理员可以访问后台

### 界面设计
响应式设计: 适配手机、平板、电脑
现代化UI: 使用B站风格的蓝色主题
用户体验: 流畅的动画和交互效果

## 快速开始

### 1. 运行一键化部署脚本

```bash
bash deploy.sh
```
后端服务是由python+flask架构组成的，前端使用nginx处理静态请求，动态请求通过fastcgi协议进行处理，mysql数据库存储网站后端服务。使用shell脚本中使用Docker部署后端服务一键上云。
### 2. 访问网站

打开浏览器访问：http://localhost:5000

### 3. 管理后台

#### 默认管理员账户
- 用户名: admin
- 密码: admin123
- 邮箱: admin@wanli.com
#### 首次登陆流程
1. 使用默认账密登陆，系统会自动重定向到密码修改页面(修改密码必须使用符合要求的强密码),密码修改完成后才能访问管理后台
2. 密码要求：
- 长度：至少12位
- 组成：必须由字母、数字、特殊字符组成

## 项目结构

```
python-project/
├── main.py              # Flask应用主文件
├── requirements.txt     # Python依赖
├── README.md           # 项目说明
├── bilibili_clone.db   # SQLite数据库（自动创建）
├── static/             # 静态文件
│   ├── avatars/        # 用户头像
│   ├── thumbnails/     # 视频缩略图
│   └── uploads/        # 上传的视频文件
└── templates/          # HTML模板
    ├── index.html      # 首页
    ├── login.html      # 登录页面
    ├── register.html   # 注册页面
    ├── upload.html     # 视频上传页面
    ├── video.html      # 视频播放页面
    ├── admin.html      # 管理后台
    ├── profile.html    # 个人中心
    └── search.html     # 搜索页面
```

## 技术栈

- **后端**: Flask (Python)
- **数据库**: SQLite + SQLAlchemy
- **用户认证**: Flask-Login
- **前端**: HTML5, CSS3, JavaScript
- **样式**: 自定义CSS，响应式设计
- **交互**: 原生JavaScript，Fetch API

## 功能页面

### 首页 (/)
- 展示最新上传的视频
- 搜索功能
- 用户登录状态显示

### 登录页面 (/login)
- 用户登录表单
- 错误信息显示
- 跳转到注册页面

### 注册页面 (/register)
- 用户注册表单
- 用户名和邮箱唯一性验证
- 跳转到登录页面

### 视频上传 (/upload)
- 视频文件上传
- 标题和描述输入
- 上传进度显示

### 视频播放 (/video/<id>)
- HTML5视频播放器
- 视频信息展示
- 评论系统
- 播放量统计

### 管理后台 (/admin)
- 用户管理表格
- 视频管理表格
- 评论管理表格
- 数据统计卡片

### 个人中心 (/profile)
- 用户信息展示
- 个人统计数据
- 我的视频列表

### 搜索页面 (/search)
- 搜索结果展示
- 关键词高亮
- 无结果提示

## API端点

- `GET /` - 首页
- `GET /login` - 登录页面
- `POST /login` - 用户登录
- `GET /register` - 注册页面
- `POST /register` - 用户注册
- `GET /logout` - 用户退出
- `GET /upload` - 上传页面
- `POST /upload` - 视频上传
- `GET /video/<id>` - 视频播放页面
- `POST /comment` - 发表评论
- `GET /admin` - 管理后台
- `POST /admin/delete_user/<id>` - 删除用户
- `POST /admin/delete_video/<id>` - 删除视频
- `GET /profile` - 个人中心
- `GET /search` - 搜索页面
- `POST /change_admin_password` - 管理员修改密码
- `POST /admin/review_video/<id>` - 视频审核
- `POST /admin/update_user/<id>` - 更新用户信息
- `POST /admin/reset_user_password/<id>` - 重置用户密码
- `POST /admin/delete_user/<id>` - 禁用用户

## 自定义

您可以根据需要修改以下内容：

1. 样式: 修改templates目录下的HTML文件中的CSS
2. 功能: 在main.py中添加新的路由和功能
3. 数据库: 修改数据模型或添加新的表
4. 部署: 配置生产环境部署
