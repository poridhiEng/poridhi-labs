# Use the official Python image from the Docker Hub
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Copy the project files into the container
COPY . /app

# Expose the port the app runs on
EXPOSE 8000


# Command to run the application
CMD ["python", "-m", "http.server", "8000"]