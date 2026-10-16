# Stage 1: Build React static assets
FROM node:20-alpine AS builder

WORKDIR /app

# Copy dependency specifications first for optimal Docker layer caching
COPY package.json ./

# Install dependencies cleanly
RUN npm install --frozen-lockfile || npm install

# Copy application source files
COPY . .

# Build production bundle
RUN npm run build

# Stage 2: Serve with secure, unprivileged Nginx
FROM nginxinc/nginx-unprivileged:1.27-alpine

USER root

# Upgrade OS packages to remediate CVEs in system libraries (OpenSSL, musl, libxml2, zlib, libpng, etc.)
RUN apk update && apk upgrade --no-cache

# Set working directory to static assets root and clean default files
WORKDIR /usr/share/nginx/html
RUN rm -rf /usr/share/nginx/html/* && \
    chown -R 101:101 /usr/share/nginx/html

# Copy compiled assets from build stage
COPY --chown=101:101 --from=builder /app/dist /usr/share/nginx/html

# Copy custom Nginx reverse proxy configuration
COPY nginx.conf /etc/nginx/nginx.conf

# Healthcheck definition
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD wget --quiet --tries=1 --spider http://localhost:8080/healthz || exit 1

# Container runs as unprivileged user 101
USER 101

EXPOSE 8080

CMD ["nginx", "-g", "daemon off;"]
