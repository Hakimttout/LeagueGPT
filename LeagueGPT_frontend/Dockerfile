# LeagueGPT_frontend/Dockerfile

# --- Build stage using Node.js ---
FROM node:18-alpine AS build
WORKDIR /app

# Copy essential package files and install dependencies
COPY package*.json ./
RUN npm install

# Copy production environment variables
COPY .env.production .env

# Copy the rest of the application code
COPY . .

# Build the frontend using Vite
RUN npm run build

# --- Final stage using Nginx to serve the built app ---
FROM nginx:alpine

# Copy built files to Nginx public directory
COPY --from=build /app/dist /usr/share/nginx/html

# Copy custom Nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf
