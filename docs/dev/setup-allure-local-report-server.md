# Advanced (optional) — Nginx / Apache for shared local network

If you want teammates to access the report on your LAN:

- Install Nginx
    - `brew install nginx`

- Edit config (usually /usr/local/etc/nginx/nginx.conf) [Find through `which nginx` command]
  - Add inside the http {} block:
<pre>server {
    listen 8080;
    server_name localhost;
    location / {
        root /path/to/your/project/allure-report;
        index index.html;
    }
}</pre>

- Restart nginx:
    - `brew services start nginx`
- Open: http://localhost:8080

Now you have a proper static host for your Allure reports.
