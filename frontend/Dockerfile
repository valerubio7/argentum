# Frontend Dockerfile for development
FROM oven/bun:1-alpine

# Set working directory
WORKDIR /app

# Copy bun.lock from root and package.json from frontend
COPY bun.lock ./
COPY frontend/package.json ./

# Install dependencies
RUN bun install

# Copy application code (excluding node_modules via .dockerignore)
COPY frontend/src ./src
COPY frontend/public ./public
COPY frontend/index.html ./
COPY frontend/tsconfig*.json ./
COPY frontend/vite.config.ts ./
COPY frontend/.env.example ./.env.example

# Expose port
EXPOSE 5173

# Default command (can be overridden in docker-compose)
CMD ["bun", "run", "dev", "--host", "0.0.0.0"]
