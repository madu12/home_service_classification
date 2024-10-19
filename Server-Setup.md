# Home Service Model Server Setup

## 1. Update and Upgrade the System
```bash
sudo apt update && sudo apt upgrade
```
## 2. Install Python and Git
```bash
sudo apt install python3-pip python3-dev git
```
## 3. Clone the Project Repository
```bash
git clone https://github.com/madu12/home_service_classification.git
cd home_service_classification/
```

## 4. Set Up a Python Virtual Environment
```bash
sudo apt install python3-venv
python3 -m venv .venv
source .venv/bin/activate
```

## 5. Install Project Dependencies
```bash
pip install -r requirements.txt
```

## 6. Install ODBC Driver for SQL Server
```bash
sudo apt-get install unixodbc unixodbc-dev
curl https://packages.microsoft.com/keys/microsoft.asc | sudo apt-key add -
curl https://packages.microsoft.com/config/ubuntu/20.04/prod.list | sudo tee /etc/apt/sources.list.d/msprod.list
sudo apt-get update
sudo ACCEPT_EULA=Y apt-get install msodbcsql18
```

## 7. Verify ODBC Installation
```bash
ls /usr/lib/x86_64-linux-gnu/ | grep libodbc
```

## 8. Configure Environment Variables
```bash
vim .env
```
Add the following lines to .env:
```bash
DATABASE_DRIVER=ODBC Driver 18 for SQL Server
DATABASE_SERVER=home-service-db.cd8o0gcak2fi.eu-north-1.rds.amazonaws.com
DATABASE_NAME=home_service_chatbot
DATABASE_USERNAME=admin
DATABASE_PASSWORD=MyStrongPass123
GEMINI_API_KEY=AIzaSyCIUWS9jvxI4dF8Ah-E80B6AZvFFrQDBIY
```

## 9. Train the Machine Learning Model
```bash
python3 train_model.py
```

## 10. Configure Firewall (UFW)
```bash
sudo ufw status
sudo ufw allow 80
sudo ufw allow 443
sudo ufw allow 8080
sudo ufw allow 5000
sudo ufw allow 5001
```
## 11. Install and Configure Nginx
```bash
sudo apt update 
sudo apt install nginx
sudo vim /etc/nginx/sites-available/home_service_classification
```

## 12. Install and Configure Nginx
```bash
server {
    listen 80;
    server_name 51.20.9.94; # Replace this with your server's public IP

    location / {
        proxy_pass http://127.0.0.1:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## 12. Enable the Nginx Site and Reload
```bash
sudo ln -s /etc/nginx/sites-available/home_service_classification /etc/nginx/sites-enabled/
sudo systemctl reload nginx
```

## 13. Install and Configure Gunicorn
```bash
pip install gunicorn
sudo vim /etc/systemd/system/gunicorn.service
```
Add the following content to the Gunicorn service file:
```bash
[Unit]
Description=Gunicorn instance for a Home Service Classification app
After=network.target

[Service]
User=ubuntu
Group=www-data
WorkingDirectory=/home/ubuntu/home_service_classification
ExecStart=/home/ubuntu/home_service_classification/.venv/bin/gunicorn --workers 3 --bind 127.0.0.1:5001 app:app
Restart=always

[Install]
WantedBy=multi-user.target
```
## 14. Start and enable Gunicorn:
```bash
sudo systemctl start gunicorn
sudo systemctl enable gunicorn
sudo systemctl daemon-reload
sudo journalctl -u gunicorn
```
