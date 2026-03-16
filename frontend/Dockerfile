# Build stage
FROM node:18-alpine as builder

WORKDIR /usr/share/nginx/html

COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

ENTRYPoint ["nginx", "-g", "daemon off"]
