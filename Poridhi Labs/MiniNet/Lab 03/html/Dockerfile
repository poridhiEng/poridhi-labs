# Use a lightweight web server image like Nginx to serve static files
FROM nginx:alpine

# Set the working directory
WORKDIR /usr/share/nginx/html

# Copy the application files into the Nginx HTML directory
COPY . .

# Expose port 80 to be able to access the application
EXPOSE 80

# The default command to start Nginx
CMD ["nginx", "-g", "daemon off;"]
