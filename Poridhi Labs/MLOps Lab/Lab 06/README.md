
## mlflow_server/Dockerfile
```Dockerfile
FROM python:3.8-slim-buster

WORKDIR /mlflow

RUN pip install mlflow psycopg2-binary boto3

EXPOSE 5000

CMD ["mlflow", "server", \
     "--host=0.0.0.0", \
     "--backend-store-uri=postgresql://mlflow:mlflow@postgres/mlflow", \
     "--default-artifact-root=s3://poridhi-mlops-labs-bucket"]
```

docker build -t minhaz71/mlflow-server:latest ./mlflow_server
docker build -t minhaz71/model-training:latest ./model_training
docker push minhaz71/mlflow-server:latest
docker push minhaz71/model-training:latest

kubectl create secret generic aws-credentials \
  --from-literal=aws-access-key-id=AKIAVRUVSJMRPQFMXHWT \
  --from-literal=aws-secret-access-key=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
