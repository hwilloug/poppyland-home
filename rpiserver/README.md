# Poppyland Home RPi Server

## Setup

### Install python packages

```
poetry install

```

### Nginx Install and Configuration

[Official Documentation](https://www.nginx.com/resources/wiki/start/topics/tutorials/install/)

```
sudo apt update
sudo apt install nginx
sudo systemctl start nginx
```

```
sudo vim /etc/nginx/sites-enabled/default
```

Update the server_name in the nginx config to be your domain. In this case, `home.poppyland.dev`.

`/etc/nginx/sites-enabled/default`
```
upstream apiserver {
   server localhost:8080; 
}

server {
    root /var/www/html;
    
    index index.html index.htm index.nginx-debian.html;
    
    server_name home.poppyland.dev;
    
    location / {
        auth_basic "Administrator's Area";
        auth_basic_user_file /etc/apache2/.htpasswd;
        rewrite ^/home/(.*) /$1 break;
        proxy_set_header Host $http_host;
        proxy_pass http://apiserver
    }
    
    listen [::]:80;
    listen 80;
}
```

```
sudo systemctl restart nginx
```

### Certbot Configuration

[Official Documentation](https://certbot.eff.org/instructions?ws=nginx&os=debianstretch)

Follow the official documentation, then restart nginx.

```
sudo systemctl restart nginx
```

## Running the Server

Run the server using the run script:

```
./run.sh
```

The server should be accessable at `http://localhost:8080`.

