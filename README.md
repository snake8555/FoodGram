<div align="center">

# Foodgram — Recipe Assistant

</div>

## Project Description

Foodgram is an online recipe-sharing service designed for both beginner cooks and experienced food enthusiasts.

Users can share their recipes, subscribe to other authors, add favorite recipes to their favorites, add recipes to a shopping cart, and download a combined shopping list in `.txt` format before going to the store.

## Server Setup and Project Deployment

### 1. Create the project directory

Create a `foodgram/` directory in the server's home directory.

### 2. Create the `.env` file

Create a `.env` file in the root of the `foodgram` directory and configure it using the following template:

```env
POSTGRES_USER=...
POSTGRES_PASSWORD=...
POSTGRES_DB=...
DB_HOST=...
DB_PORT=...

SECRET_KEY=...
DEBUG=False
ALLOWED_HOSTS=...
```

### 3. Install and configure Nginx

Install Nginx:

```bash
sudo apt install nginx -y
sudo nano /etc/nginx/sites-enabled/default
```

Example Nginx configuration:

```nginx
server {
    server_name <YOUR_IP> <YOUR_DOMAIN>;
    server_tokens off;
    client_max_body_size 20M;

    location / {
        proxy_set_header Host $http_host;
        proxy_pass http://127.0.0.1:9000;
    }
}
```

Configure SSL if necessary.

### 4. Install Docker and Docker Compose

```bash
sudo apt update
sudo apt install curl
curl -fSL https://get.docker.com -o get-docker.sh
sudo sh ./get-docker.sh
sudo apt-get install docker-compose-plugin
```

### 5. Configure GitHub Actions Secrets

Add the following environment variables to the GitHub Actions Secrets of this repository:

```env
DOCKERHUB_USERNAME=<your Docker Hub username>
DOCKERHUB_PASSWORD=<your Docker Hub password>

SSH_USERNAME=<remote server username>
SSH_HOST=<server IP address>
SSH_PASSPHRASE=<server password, if configured>
SSH_KEY=<your private SSH key>

TELEGRAM_ME_ID=<your Telegram account ID>
TELEGRAM_BOT_TOKEN=<your Telegram bot token>
```

### 6. Run the project workflow

Push the changes to the repository to start the workflow:

```bash
git add .
git commit -m "Deploy project"
git push
```

## Admin Panel Access

```text
Email: admin@mail.com
Password: admin123
```

## Author

Vladimir Zhurov
