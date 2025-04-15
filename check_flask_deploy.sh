#!/bin/bash

APP_NAME="yizhixiaoyuer.cn"
PROJECT_DIR="/home/lsh88/jizhang"
SOCKET_PATH="$PROJECT_DIR/gunicorn.sock"
NGINX_SITE_PATH="/etc/nginx/sites-available/$APP_NAME"
SUPERVISOR_CONF_PATH="/etc/supervisor/conf.d/$APP_NAME.conf"

echo "🔍 开始检查 Flask 应用部署状况 [$APP_NAME]"

echo "--------------------------------------------------"
echo "✅ 检查 Gunicorn Socket 是否存在..."
if [ -e "$SOCKET_PATH" ]; then
    echo "✔️ Socket 存在：$SOCKET_PATH"
else
    echo "❌ 未找到 Gunicorn Socket：$SOCKET_PATH"
fi

echo "--------------------------------------------------"
echo "✅ 检查 Supervisor 中是否有程序配置..."
if [ -f "$SUPERVISOR_CONF_PATH" ]; then
    echo "✔️ Supervisor 配置存在：$SUPERVISOR_CONF_PATH"
else
    echo "❌ Supervisor 配置不存在！"
fi

echo "--------------------------------------------------"
echo "✅ 检查 Supervisor 程序状态..."
sudo supervisorctl status "$APP_NAME"

echo "--------------------------------------------------"
echo "✅ 检查 Nginx 配置是否存在并启用..."
if [ -f "$NGINX_SITE_PATH" ]; then
    echo "✔️ 配置文件存在：$NGINX_SITE_PATH"
else
    echo "❌ 配置文件不存在！"
fi

if [ -L "/etc/nginx/sites-enabled/$APP_NAME" ]; then
    echo "✔️ 配置已启用"
else
    echo "❌ 配置未启用，请检查软链接"
fi

echo "--------------------------------------------------"
echo "✅ 检查 Nginx 状态..."
sudo systemctl is-active nginx

echo "--------------------------------------------------"
echo "📄 最近的 Nginx 错误日志（最后 10 行）"
sudo tail -n 10 /var/log/nginx/error.log

echo "--------------------------------------------------"
echo "📄 最近的 Gunicorn 错误日志（最后 10 行）"
sudo tail -n 10 "$PROJECT_DIR/$APP_NAME.err.log"

echo "--------------------------------------------------"
echo "✅ 检查完成"
