

---

## **Lambda Function to Fetch Data from Redis**

### Prerequisites
1. **Redis Instance**: Ensure you have a Redis instance running (either on **ElastiCache** or an **EC2 instance**).
2. **Redis Endpoint**: Note the Redis endpoint (e.g., ElastiCache primary endpoint or EC2 public IP).
3. **Lambda Layer for `redis`**: Create a Lambda layer for the `redis` Python library (if not already done).

---

### Step 1: Create the Lambda Function

1. Go to the AWS Lambda Console → Create Function.
2. Name the function `fetch_from_redis`.
3. Choose **Python 3.9** as the runtime.
4. Attach the `redis_layer` (created earlier) and the `LambdaRedisDeploymentRole`.
5. Use the following code:

```python
import json
import redis

# Redis Configuration
REDIS_HOST = "your-redis-endpoint"  # Replace with ElastiCache endpoint or EC2 public IP
REDIS_PORT = 6379

def lambda_handler(event, context):
    try:
        # Connect to Redis
        r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

        # Fetch data from Redis
        key = event.get('key', 'foo')  # Default key is 'foo'
        value = r.get(key)

        if value is None:
            return {
                'statusCode': 404,
                'body': json.dumps({'message': f'Key "{key}" not found in Redis'})
            }

        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Data fetched successfully from Redis.',
                'key': key,
                'value': value
            })
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
```

---

### Step 2: Create API Gateway Endpoint

1. Go to API Gateway Console → Create API → **REST API**.
2. Create a resource `/fetch`.
3. Add a **GET method**:
   - Integration type: **Lambda Function** → Select `fetch_from_redis`.
4. Deploy the API to a stage (e.g., `prod`).

---

### Step 3: Test the Endpoint

1. Use the `/fetch` endpoint to retrieve data from Redis:
   ```bash
   curl -X GET "https://your-api-id.execute-api.region.amazonaws.com/prod/fetch?key=foo"
   ```
   Replace `foo` with the key you want to fetch.

2. **Sample Response**:
   ```json
   {
       "message": "Data fetched successfully from Redis.",
       "key": "foo",
       "value": "bar"
   }
   ```

---

### Step 4: Add Error Handling (Optional)

If the key does not exist in Redis, the function will return a `404` response. You can customize this behavior as needed.

---



### Example: Fetching Multiple Keys

If you want to fetch multiple keys, you can modify the Lambda function to accept a list of keys:

```python
import json
import redis

# Redis Configuration
REDIS_HOST = "your-redis-endpoint"  # Replace with ElastiCache endpoint or EC2 public IP
REDIS_PORT = 6379

def lambda_handler(event, context):
    try:
        # Connect to Redis
        r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

        # Fetch multiple keys from Redis
        keys = event.get('keys', ['foo'])  # Default key is 'foo'
        values = {key: r.get(key) for key in keys}

        # Filter out keys with no value
        values = {k: v for k, v in values.items() if v is not None}

        if not values:
            return {
                'statusCode': 404,
                'body': json.dumps({'message': 'No keys found in Redis'})
            }

        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Data fetched successfully from Redis.',
                'values': values
            })
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
```

**API Request**:
```bash
curl -X GET "https://your-api-id.execute-api.region.amazonaws.com/prod/fetch?keys=foo,hello"
```

**Response**:
```json
{
    "message": "Data fetched successfully from Redis.",
    "values": {
        "foo": "bar",
        "hello": "world"
    }
}
```

---

