#!/bin/bash

# 设置项目和域名
PROJECT_DIR="/home/lsh88/jizhang"
DOMAIN="yizhixiaoyuer.cn"
GUNICORN_WORKERS=3  # Gunicorn 工作进程数，可以根据服务器性能调整

# 安装必需的软件（nginx, gunicorn, supervisor）
echo "安装必要的软件..."
sudo apt update
sudo apt install -y nginx python3-pip supervisor

# 安装 Gunicorn
echo "安装 Gunicorn..."
pip3 install gunicorn

# 设置项目的 Gunicorn 配置
GUNICORN_CMD="gunicorn --workers=$GUNICORN_WORKERS --bind unix:$PROJECT_DIR/gunicorn.sock app:app"

# 创建 Nginx 配置文件
echo "配置 Nginx..."
sudo tee /etc/nginx/sites-available/$DOMAIN <<EOF
server {
    listen 80;
    server_name $DOMAIN;

    location / {
        proxy_pass http://unix:$PROJECT_DIR/gunicorn.sock;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

# 启用 Nginx 配置
sudo ln -s /etc/nginx/sites-available/$DOMAIN /etc/nginx/sites-enabled
sudo systemctl restart nginx

# 配置 Supervisor 管理 Gunicorn 进程
echo "配置 Supervisor..."
sudo tee /etc/supervisor/conf.d/$DOMAIN.conf <<EOF
[program:$DOMAIN]
command=$GUNICORN_CMD
directory=$PROJECT_DIR
autostart=true
autorestart=true
stderr_logfile=$PROJECT_DIR/$DOMAIN.err.log
stdout_logfile=$PROJECT_DIR/$DOMAIN.out.log
EOF

# 启动 Supervisor 管理 Gunicorn
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start $DOMAIN

# 完成
echo "部署完成！你可以通过 $DOMAIN 访问 Flask 应用。"
