# Etapa de build
FROM node:18 as build

WORKDIR /app
COPY . .
RUN npm install && npm run build

# Etapa de produção (com nginx)
FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html

# Remove o default.conf e substitui se necessário
EXPOSE 80
