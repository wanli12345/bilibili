-- 创建数据库（如果不存在）
CREATE DATABASE IF NOT EXISTS wanli_video CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 使用数据库
USE wanli_video;

-- 创建用户表
CREATE TABLE IF NOT EXISTS user (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(80) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(120) NOT NULL,
    avatar VARCHAR(200) DEFAULT 'default.jpg',
    is_admin BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 创建视频表
CREATE TABLE IF NOT EXISTS video (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    filename VARCHAR(200) NOT NULL,
    thumbnail VARCHAR(200),
    views INT DEFAULT 0,
    likes INT DEFAULT 0,
    user_id INT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE
);

-- 创建评论表
CREATE TABLE IF NOT EXISTS comment (
    id INT AUTO_INCREMENT PRIMARY KEY,
    content TEXT NOT NULL,
    user_id INT NOT NULL,
    video_id INT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE,
    FOREIGN KEY (video_id) REFERENCES video(id) ON DELETE CASCADE
);

-- 创建索引
CREATE INDEX idx_video_user_id ON video(user_id);
CREATE INDEX idx_video_created_at ON video(created_at);
CREATE INDEX idx_comment_video_id ON comment(video_id);
CREATE INDEX idx_comment_user_id ON comment(user_id);

-- 插入默认管理员账户
INSERT INTO user (username, email, password_hash, is_admin) 
VALUES ('admin', 'admin@wanli.com', 'pbkdf2:sha256:600000$your-hash-here', TRUE)
ON DUPLICATE KEY UPDATE id=id; 