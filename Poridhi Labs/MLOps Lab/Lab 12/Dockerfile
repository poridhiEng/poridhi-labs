FROM python:3.9-slim
WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy the rest of the application
COPY . .

# Train the model before starting the app
RUN python src/train.py && \
    ls -la / && \
    ls -la /app && \
    echo "Model training completed"

# Command to run the application
CMD ["python", "src/app.py"]