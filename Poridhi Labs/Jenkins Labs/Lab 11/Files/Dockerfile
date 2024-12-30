# Step 1: Use Node.js as the base image
FROM node:16-alpine as build

# Step 2: Set the working directory in the container
WORKDIR /app

# Step 3: Copy package.json and package-lock.json to the container
COPY package*.json ./

# Step 4: Install dependencies
RUN npm install

# Step 5: Copy the entire application source code to the container
COPY . .

# Step 6: Build the React app for production
RUN npm run build

# Step 7: Use a lightweight NGINX image to serve the built files
FROM nginx:stable-alpine

# Step 8: Copy the build output from the previous stage to the NGINX directory
COPY --from=build /app/build /usr/share/nginx/html

# Step 9: Expose port 80
EXPOSE 80

# Step 10: Start NGINX
CMD ["nginx", "-g", "daemon off;"]
