# Используем официальный образ Nginx
FROM nginx:latest

# Копируем билд React приложения в директорию Nginx для обслуживания статического контента
COPY client/dist /usr/share/nginx/html

# Копируем конфигурационный файл Nginx
COPY client/nginx.conf /etc/nginx/nginx.conf

# Открываем порт 80 для внешних запросов
EXPOSE 80

# Запускаем Nginx
CMD ["nginx", "-g", "daemon off;"]
