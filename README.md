<div align=center>
  
  # [Foodgram](https://yafoodgram.ddns.net/) продуктовый помощник
  

## Описание проекта


Foodgram - онлайн-сервис, представляющий собой продуктового помощника как для начинающих кулинаров, так и для опытных гурманов. В рамках этого сервиса пользователи могут делиться своими рецептами, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список избранного, а также скачивать сводный список продуктов в формате .pdf перед походом в магазин для приготовления выбранных блюд.


## Подготовка сервера и деплой проекта

1. Создать директорию foodgram/ в домашней директории сервера.

2. В корне папки foodgram поместить файл .env, заполнить его по шаблону

  ```env
    POSTGRES_USER=...
    POSTGRES_PASSWORD=...
    POSTGRES_DB=...
    DB_HOST=...
    DB_PORT=...

    SECRET_KEY=
    DEBUG=False
    ALLOWED_HOSTS=
```

4. Установить Nginx и настроить конфигурацию так, чтобы все запросы шли в контейнеры на порт 9090.

    ```bash
        sudo apt install nginx -y 
        sudo nano etc/nginx/sites-enabled/default
    ```
    
    Пример конфигурация nginx
    ```bash
        server {
            server_name <Ваш IP> <Домен вашего сайта>;
            server_tokens off;
            client_max_body_size 20M;
        
            location / {
                proxy_set_header Host $http_host;
                proxy_pass http://127.0.0.1:9000;
        }
    ```
    
    > При необходимости настройте SSL-соединение

5. Установить docker и docker-compose
   
``` bash
    sudo apt update
    sudo apt install curl
    curl -fSL https://get.docker.com -o get-docker.sh
    sudo sh ./get-docker.sh
    sudo apt-get install docker-compose-plugin     
```

4. Добавить в Secrets GitHub Actions данного репозитория на GitHub переменные окружения

``` env
    DOCKERHUB_USERNAME=<имя пользователя DockerHub>
    DOCKERHUB_PASSWORD=<пароль от DockerHub>
    
    SSH_USERNAME=<username для подключения к удаленному серверу>
    SSH_HOST=<ip сервера>
    SSH_PASSPHRASE=<пароль для сервера, если он установлен>
    SSH_KEY=<ваш приватный SSH-ключ>
    
    TELEGRAM_ME_ID=<id вашего Телеграм-аккаунта>
    TELEGRAM_BOT_TOKEN=<токен вашего бота>
```
5. Запустить workflow проекта выполнив команды:

```bash
  git add .
  git commit -m ''
  git push
```
