#!/bin/bash

# 设置变量
PROJECT_DIR="/home/lsh88/jizhang"
VENV_DIR="$PROJECT_DIR/venv"
USER="lsh88"
GROUP="www-data"
SOCK_DIR="/run/gunicorn"
SOCK_FILE="$SOCK_DIR/gunicorn.sock"
SERVICE_NAME="gunicorn"
DOMAIN="yizhixiaoyuer.cn"  # 请替换为您的实际域名

# 创建虚拟环境并安装依赖
python3 -m venv "$VENV_DIR"
source "$VENV_DIR/bin/activate"
pip install --upgrade pip
pip install flask gunicorn

# 创建套接字目录并设置权限
sudo mkdir -p "$SOCK_DIR"
sudo chown "$USER":"$GROUP" "$SOCK_DIR"
sudo chmod 770 "$SOCK_DIR"

# 创建 Systemd 套接字单元文件
sudo tee /etc/systemd/system/$SERVICE_NAME.socket > /dev/null <<EOF
[Unit]
Description=gunicorn socket

[Socket]
ListenStream=$SOCK_FILE
SocketUser=$USER
SocketGroup=$GROUP
SocketMode=660

[Install]
WantedBy=sockets.target
EOF

# 创建 Systemd 服务单元文件
sudo tee /etc/systemd/system/$SERVICE_NAME.service > /dev/null <<EOF
[Unit]
Description=gunicorn daemon
Requires=$SERVICE_NAME.socket
After=network.target

[Service]
Type=notify
User=$USER
Group=$GROUP
WorkingDirectory=$PROJECT_DIR
ExecStart=$VENV_DIR/bin/gunicorn --workers 3 --bind unix:$SOCK_FILE app:app
ExecReload=/bin/kill -s HUP \$MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true

[Install]
WantedBy=multi-user.target
EOF

# 重新加载 Systemd 配置并启动服务
sudo systemctl daemon-reload
sudo systemctl enable --now $SERVICE_NAME.socket

# 创建 Nginx 配置文件
sudo tee /etc/nginx/sites-available/$SERVICE_NAME > /dev/null <<EOF
server {
    listen 80;
    server_name $DOMAIN;

    location / {
        proxy_pass http://unix:$SOCK_FILE;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
    }
}
EOF

# 启用 Nginx 配置并重启 Nginx
sudo ln -s /etc/nginx/sites-available/$SERVICE_NAME /etc/nginx/sites-enabled
sudo nginx -t && sudo systemctl restart nginx

echo "部署完成！您的 Flask 应用已通过 Systemd 和 Nginx 启动。"
