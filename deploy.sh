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

upstream aiohttp {
    # fail_timeout=0 means we always retry an upstream even if it failed
    # to return a good HTTP response

    # Unix domain servers
    server unix:/tmp/example_1.sock fail_timeout=0;
    server unix:/tmp/example_2.sock fail_timeout=0;
    server unix:/tmp/example_3.sock fail_timeout=0;
    server unix:/tmp/example_4.sock fail_timeout=0;

    # Unix domain sockets are used in this example due to their high performance,
    # but TCP/IP sockets could be used instead:
    # server 127.0.0.1:8081 fail_timeout=0;
    # server 127.0.0.1:8082 fail_timeout=0;
    # server 127.0.0.1:8083 fail_timeout=0;
    # server 127.0.0.1:8084 fail_timeout=0;
}
EOT

sudo rm /etc/nginx/sites-enabled/your_domain
sudo ln -s /etc/nginx/sites-available/your_domain /etc/nginx/sites-enabled/
sudo usermod -a -G webteam www-data

sudo systemctl restart nginx



sudo apt install gunicorn
pip3 install gunicorn