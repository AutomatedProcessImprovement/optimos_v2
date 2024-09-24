# Stage 1: Build the React app with Parcel
FROM node:22-alpine AS build
WORKDIR /app
COPY ./package.json ./yarn.lock /app/
RUN yarn install
COPY ./ /app/
RUN yarn run build

# Stage 2: Serve with Nginx
FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html

# Support React Router by forwarding all traffic to index.html
RUN rm /etc/nginx/conf.d/default.conf
COPY ./nginx.conf /etc/nginx/conf.d

EXPOSE 80
