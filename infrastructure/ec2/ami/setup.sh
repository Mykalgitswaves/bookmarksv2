# Update and install packages
apt-get update -y
apt-get install -y python3-pip

# Install the AWS CLI
pip3 install awscli

# Import the ssh key
aws secretsmanager get-secret-value --secret-id arn:aws:secretsmanager:us-east-1:788511695961:secret:prod/github_ssh-mvSAFT --query 'SecretString' --output text > /home/ubuntu/.ssh/deploy_key --region us-east-1

chmod 600 /home/ubuntu/.ssh/deploy_key
eval "$(ssh-agent -s)"
ssh-add /home/ubuntu/.ssh/deploy_key

# Clone the repository
cd /home/ubuntu/
git clone git@github.com:Mykalgitswaves/bookmarksv2.git
cd /home/ubuntu/bookmarksv2/
git checkout main
git pull

# Install the requirements
apt install -y     build-essential     checkinstall     libncursesw5-dev     libreadline-dev     libssl-dev     libgdbm-dev     libc6-dev     libsqlite3-dev     tk-dev     libbz2-dev     libffi-dev     zlib1g-dev     liblzma-dev     libgdbm-compat-dev

# Docker installation
for pkg in docker.io docker-doc docker-compose docker-compose-v2 podman-docker containerd runc; do sudo apt-get remove $pkg; done
apt-get install ca-certificates curl
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
chmod a+r /etc/apt/keyrings/docker.asc


# Add the repository to Apt sources:
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
tee /etc/apt/sources.list.d/docker.list > /dev/null

apt-get update

# Install Docker
apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin 

# Grab Configs
aws secretsmanager get-secret-value --secret-id arn:aws:secretsmanager:us-east-1:788511695961:secret:prod/config_prod-438QTR --query 'SecretString' --region 'us-east-1' --output text > /home/ubuntu/bookmarksv2/backend/src/config/config.prod.json

# Create .env
echo "GUNICORN_WORKERS=4" > /home/ubuntu/bookmarksv2/.env
echo "ENVIRONMENT=PROD" >> /home/ubuntu/bookmarksv2/.env

# Update docker permissions
usermod -aG docker ubuntu
reboot

# Install Docker Compose

curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Setup Systemd
vim /etc/systemd/system/book.service
[Unit]
Description=book
After=network.target

[Service]
User=ubuntu
Group=ubuntu
WorkingDirectory=/home/ubuntu/bookmarksv2
ExecStart=/usr/local/bin/docker-compose up --build
ExecStop=/usr/local/bin/docker-compose stop
Restart=always

[Install]
WantedBy=multi-user.target

systemctl daemon-reload
systemctl enable book.service
systemctl start book.service
systemctl stop book.service

#Copy config to test
aws secretsmanager get-secret-value --secret-id arn:aws:secretsmanager:us-east-1:788511695961:secret:prod/config_prod-438QTR --query 'SecretString' --region 'us-east-1' --output text > /home/ubuntu/bookmarksv2/backend/tests/config.json
pip install pytest
pip install httpx
pip install beautifulsoup4
pip install websockets
pytest

# nginx setup
sudo apt install nginx -y
sudo apt install certbot python3-certbot-nginx -y
sudo vim /etc/nginx/sites-available/my_reverse_proxy
server {
    server_name hardcoverlit.com www.hardcoverlit.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    location /.well-known/acme-challenge/ {
        root /var/www/html;
    }

    listen 80;

}
## Update the record in Route53 to route to this address
sudo ln -s /etc/nginx/sites-available/my_reverse_proxy /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default
sudo systemctl restart nginx
sudo mkdir -p /var/www/html/.well-known/acme-challenge/
sudo chown -R www-data:www-data /var/www/html/
sudo chmod -R 755 /var/www/html/
# Certbot
# --standalone-supported-challenges http-01
sudo certbot --nginx -d hardcoverlit.com -d www.hardcoverlit.com
sudo systemctl restart nginx

sudo vim /etc/nginx/sites-enabled/my_reverse_proxy 
server {
    server_name hardcoverlit.com www.hardcoverlit.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    location /.well-known/acme-challenge/ {
        root /var/www/html;
    }


    listen 443 ssl; # managed by Certbot
    ssl_certificate /etc/letsencrypt/live/hardcoverlit.com/fullchain.pem; # managed by Certbot
    ssl_certificate_key /etc/letsencrypt/live/hardcoverlit.com/privkey.pem; # managed by Certbot
    include /etc/letsencrypt/options-ssl-nginx.conf; # managed by Certbot
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem; # managed by Certbot


}

server {
    listen 80;
    server_name _;

    location /api/health {
        proxy_pass http://127.0.0.1:8000/api/health;
    }

}

server {
    if ($host = www.hardcoverlit.com) {
        return 301 https://$host$request_uri;
    } # managed by Certbot


    if ($host = hardcoverlit.com) {
        return 301 https://$host$request_uri;
    } # managed by Certbot


    server_name hardcoverlit.com www.hardcoverlit.com;

    listen 80;
    return 404; # managed by Certbot




}

sudo systemctl restart nginx

# Setup log forwarding to cloudwatch

cd /home/ubuntu
wget https://amazoncloudwatch-agent.s3.amazonaws.com/ubuntu/amd64/latest/amazon-cloudwatch-agent.deb
sudo dpkg -i -E ./amazon-cloudwatch-agent.deb
vim amazon-cloudwatch-agent.json
{
  "logs": {
    "logs_collected": {
      "files": {
        "collect_list": [
          {
            "file_path": "/home/ubuntu/bookmarksv2/backend/src/utils/logging/logs/info.log.jsonl",
            "log_group_name": "MyAppLogGroup",
            "log_stream_name": "info-log",
            "multi_line_start_pattern": "^\\{"
          },
          {
            "file_path": "/home/ubuntu/bookmarksv2/backend/src/utils/logging/logs/error.log",
            "log_group_name": "MyAppLogGroup",
            "log_stream_name": "error-log"
          },
          {
            "file_path": "/home/ubuntu/bookmarksv2/backend/src/utils/logging/logs/warning.log",
            "log_group_name": "MyAppLogGroup",
            "log_stream_name": "warning-log"
          }
        ]
      }
    }
  }
}

sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl   -a fetch-config   -m ec2   -c file:/home/ubuntu/amazon-cloudwatch-agent.json   -s