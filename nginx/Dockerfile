FROM nginx:1.21-alpine

WORKDIR /etc/nginx/
RUN rm /etc/nginx/conf.d/default.conf
COPY default.conf /etc/nginx/conf.d
EXPOSE 80