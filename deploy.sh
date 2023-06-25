sudo apt update
sudo apt install software-properties-common
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update

python3 -m pip3 install -r server/requirements.txt

sudo apt install nginx


sudo touch /etc/nginx/sites-available/your_domain
sudo tee /etc/nginx/sites-enabled/your_domain <<EOT
server {
    listen 80;
    client_max_body_size 4G;

    server_name 158.160.48.156;

    location / {
        proxy_pass                          http://127.0.0.1:8080;
        proxy_set_header                    Host \$host;
        proxy_set_header X-Forwarded-Host   \$server_name;
        proxy_set_header X-Real-IP          \$remote_addr;
    }

    location /frontend {
      root /home/webteam/webteam;
      #autoindex on;
    }

}
EOT

sudo rm /etc/nginx/sites-enabled/your_domain
sudo ln -s /etc/nginx/sites-available/your_domain /etc/nginx/sites-enabled/
sudo usermod -a -G webteam www-data

sudo systemctl restart nginx



sudo apt install gunicorn
pip3 install gunicorn