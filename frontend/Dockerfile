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

# Set working directory to static assets root
WORKDIR /usr/share/nginx/html

# Remove default static welcome page
RUN rm -rf /usr/share/nginx/html/*

# Copy compiled assets from build stage
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy custom Nginx reverse proxy configuration
COPY nginx.conf /etc/nginx/nginx.conf

# Expose unprivileged port 8080
EXPOSE 8080

# Healthcheck definition
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD wget --quiet --tries=1 --spider http://localhost:8080/healthz || exit 1

# Container runs as unprivileged user '101' by default in nginx-unprivileged image
USER 101

CMD ["nginx", "-g", "daemon off;"]
