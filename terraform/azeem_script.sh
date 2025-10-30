#!/bin/bash
set -e

# Install Nginx early to avoid conflicts
apt-get update
apt-get install -y nginx

# 1) Install Docker
apt-get install -y apt-transport-https ca-certificates curl software-properties-common
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | apt-key add -
add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
apt-get update
apt-get install -y docker-ce docker-ce-cli containerd.io
systemctl start docker
systemctl enable docker

# Docker login
echo "${docker_password}" | sudo docker login ${docker_registry_url} -u "${docker_username}" --password-stdin

# Install Docker Compose
curl -L "https://github.com/docker/compose/releases/download/v2.18.1/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Create application directory
mkdir -p ${repo_path}
cd ${repo_path}

# Create persistent volume directories
mkdir -p ${repo_path}/uploads ${repo_path}/static

# Docker Compose configuration
cat > docker-compose.yml <<EOL
services:
    backend:
        image: ${docker_image}
        container_name: ${container_name}
        ports:
            - "${fastapi_port}:${fastapi_port}"
        environment:
            - OPENAI_API_KEY=${openai_api_key}
            - MAX_SESSIONS=${max_sessions}
            - CHROMA_DB_COLLECTION_NAME=${chroma_db_collection_name}
        volumes:
            - ${repo_path}/uploads:/backend/uploads
            - ${repo_path}/static_dir:/backend/static_dir
        networks:
            - app-network

networks:
    app-network:
EOL

# Start containers
sudo docker-compose up -d --build

# Configure Nginx
cat > /etc/nginx/sites-available/default <<EOL
server {
    listen 80 default_server;
    listen [::]:80 default_server;
    client_max_body_size 100M;
    server_name _;
    
    # Proxy API requests
    location / {
        proxy_pass http://localhost:${fastapi_port};
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    # Serve static files directly
    location /static_dir/ {
        alias ${repo_path}/static_dir/;
        expires 30d;
        access_log off;
        add_header Cache-Control "public";
    }
}
EOL

# Test and restart Nginx
nginx -t && sudo systemctl restart nginx