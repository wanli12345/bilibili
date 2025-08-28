// 移动端导航功能

document.addEventListener('DOMContentLoaded', function() {
    // 获取DOM元素
    const mobileMenuToggle = document.querySelector('.mobile-menu-toggle');
    const mobileNav = document.querySelector('.mobile-nav');
    const mobileNavClose = document.querySelector('.mobile-nav-close');
    const body = document.body;
    
    // 顶部精简导航“更多”按钮
    window.openMoreMenu = function() {
        if (mobileNav) {
            mobileNav.classList.add('active');
            document.body.style.overflow = 'hidden';
        }
    };
    
    // 如果没有找到移动端导航关键元素，则不绑定切换按钮
    if (!mobileMenuToggle || !mobileNav) {
        return;
    }
    
    // 切换移动端菜单
    function toggleMobileMenu() {
        mobileNav.classList.toggle('active');
        body.style.overflow = mobileNav.classList.contains('active') ? 'hidden' : '';
        
        // 添加/移除active类到汉堡菜单按钮
        mobileMenuToggle.classList.toggle('active');
    }
    
    // 关闭移动端菜单
    function closeMobileMenu() {
        mobileNav.classList.remove('active');
        body.style.overflow = '';
        mobileMenuToggle.classList.remove('active');
    }
    
    // 事件监听器
    mobileMenuToggle.addEventListener('click', toggleMobileMenu);
    
    if (mobileNavClose) {
        mobileNavClose.addEventListener('click', closeMobileMenu);
    }
    
    // 点击移动端菜单外部区域关闭菜单
    mobileNav.addEventListener('click', function(e) {
        if (e.target === mobileNav) {
            closeMobileMenu();
        }
    });
    
    // 点击移动端菜单链接后关闭菜单
    const mobileNavLinks = mobileNav.querySelectorAll('a');
    mobileNavLinks.forEach(link => {
        link.addEventListener('click', closeMobileMenu);
    });
    
    // 键盘事件支持
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && mobileNav.classList.contains('active')) {
            closeMobileMenu();
        }
    });
    
    // 窗口大小改变时处理
    window.addEventListener('resize', function() {
        if (window.innerWidth > 768 && mobileNav.classList.contains('active')) {
            closeMobileMenu();
        }
    });
    
    // 触摸手势支持（滑动关闭）
    let startX = 0;
    let startY = 0;
    
    mobileNav.addEventListener('touchstart', function(e) {
        startX = e.touches[0].clientX;
        startY = e.touches[0].clientY;
    });
    
    mobileNav.addEventListener('touchmove', function(e) {
        if (!startX || !startY) {
            return;
        }
        
        const currentX = e.touches[0].clientX;
        const currentY = e.touches[0].clientY;
        const diffX = startX - currentX;
        const diffY = startY - currentY;
        
        // 如果水平滑动距离大于垂直滑动距离且大于50px，则关闭菜单
        if (Math.abs(diffX) > Math.abs(diffY) && Math.abs(diffX) > 50) {
            closeMobileMenu();
            startX = 0;
            startY = 0;
        }
    });
    
    // 添加触摸反馈
    mobileNavLinks.forEach(link => {
        link.addEventListener('touchstart', function() {
            this.style.transform = 'scale(0.95)';
        });
        
        link.addEventListener('touchend', function() {
            this.style.transform = 'scale(1)';
        });
    });
    
    // 页面加载完成后初始化
    function initMobileNav() {
        // 检查是否为移动设备
        const isMobile = window.innerWidth <= 768;
        
        if (isMobile) {
            mobileMenuToggle.style.display = 'flex';
            mobileNav.style.display = 'block';
        } else {
            mobileMenuToggle.style.display = 'none';
            mobileNav.style.display = 'none';
        }
    }
    
    // 初始化
    initMobileNav();
    
    // 监听窗口大小变化
    let resizeTimer;
    window.addEventListener('resize', function() {
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(initMobileNav, 250);
    });
});

// 添加页面切换动画
document.addEventListener('DOMContentLoaded', function() {
    // 为页面切换添加淡入效果
    const mainContent = document.querySelector('.main-content') || document.querySelector('body');
    
    if (mainContent) {
        mainContent.style.opacity = '0';
        mainContent.style.transform = 'translateY(20px)';
        mainContent.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
        
        setTimeout(() => {
            mainContent.style.opacity = '1';
            mainContent.style.transform = 'translateY(0)';
        }, 100);
    }
});

// 移动端性能优化
if ('serviceWorker' in navigator) {
    // 可以在这里注册Service Worker来提升移动端性能
    // navigator.serviceWorker.register('/sw.js');
}

// 触摸设备优化
if ('ontouchstart' in window) {
    // 为触摸设备添加特殊优化
    document.documentElement.classList.add('touch-device');
    
    // 优化触摸滚动
    document.addEventListener('touchmove', function(e) {
        // 防止过度滚动
        if (e.target.closest('.mobile-nav')) {
            e.preventDefault();
        }
    }, { passive: false });
}
