#!/bin/bash
# --------------------------------------
# Chatbot EC2 Setup Script (Auto HTTPS on Public IP)
# --------------------------------------
set -e

# Update and install required packages
yum update -y

# Proper way to install nginx on Amazon Linux 2
amazon-linux-extras install -y nginx1

# Install Docker and OpenSSL
yum install -y docker openssl ca-certificates
update-ca-trust

# Enable & start services
systemctl enable docker
systemctl start docker
systemctl enable nginx
systemctl start nginx

# Export environment variables for AWS Secrets Manager
echo "AWS_SECRET_NAME=chatbot_backend_secrets_2" >> /etc/environment
echo "AWS_DEFAULT_REGION=ap-northeast-1" >> /etc/environment
export AWS_SECRET_NAME=chatbot_backend_secrets_2
export AWS_DEFAULT_REGION=ap-northeast-1

# Pull and run the chatbot container
docker pull hassanaliocloud/chatbot:latest

# Remove any old container if exists
if docker ps -a --format '{{.Names}}' | grep -Eq "^chatbot$"; then
    docker rm -f chatbot
fi

# Run chatbot backend on port 8000 internally
docker run -d --name chatbot -p 8000:8000 \
    -e AWS_SECRET_NAME=chatbot_backend_secrets_2 \
    -e AWS_DEFAULT_REGION=ap-northeast-1 \
    hassanaliocloud/chatbot:latest

# ---------------------------
# Detect Public IP
# ---------------------------
PUBLIC_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)
echo "Detected public IP: $PUBLIC_IP"

# ---------------------------
# Self-Signed SSL Setup
# ---------------------------
mkdir -p /etc/ssl/private /etc/ssl/certs

openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout /etc/ssl/private/nginx-selfsigned.key \
  -out /etc/ssl/certs/nginx-selfsigned.crt \
  -subj "/CN=${PUBLIC_IP}"

# ---------------------------
# NGINX Reverse Proxy Setup (HTTP + HTTPS)
# ---------------------------
cat > /etc/nginx/conf.d/chatbot.conf <<NGINXCONF
server {
    listen 80;
    server_name _;
    return 301 https://\$host\$request_uri;
}

server {
    listen 443 ssl;
    server_name _;

    ssl_certificate /etc/ssl/certs/nginx-selfsigned.crt;
    ssl_certificate_key /etc/ssl/private/nginx-selfsigned.key;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;

        # CORS headers
        add_header Access-Control-Allow-Origin "https://chatbot-frontend-beryl.vercel.app" always;
        add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS" always;
        add_header Access-Control-Allow-Headers "Authorization, Content-Type, X-Requested-With" always;

        # Handle preflight OPTIONS requests
        if (\$request_method = OPTIONS) {
            add_header Access-Control-Allow-Origin "https://chatbot-frontend-beryl.vercel.app" always;
            add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS" always;
            add_header Access-Control-Allow-Headers "Authorization, Content-Type, X-Requested-With" always;
            add_header Content-Length 0;
            add_header Content-Type text/plain;
            return 204;
        }
    }
}
NGINXCONF

# Restart NGINX to apply the configuration
systemctl restart nginx

# ---------------------------
# Logging
# ---------------------------
docker logs chatbot &> /var/log/chatbot_container.log

if docker ps --filter "name=chatbot" --filter "status=running" | grep -q chatbot; then
    echo "✅ Chatbot container is running!" >> /var/log/user_data.log
else
    echo "⚠️ Chatbot container failed to start." >> /var/log/user_data.log
fi

if systemctl status nginx | grep -q running; then
    echo "✅ NGINX is running and proxying traffic." >> /var/log/user_data.log
else
    echo "⚠️ NGINX failed to start." >> /var/log/user_data.log
fi

echo "🚀 Setup completed successfully! Access your app at:"
echo "   https://${PUBLIC_IP}"

# --------------------------------------
# Manual Step: Ensure ports 80 & 443 are open in AWS Security Group
# Take the ip and add in mongo db atlas ip access list.
# --------------------------------------
