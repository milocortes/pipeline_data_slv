## Image creation
Build the image:

```bash
sudo docker build --tag models-test .
```

To test the built image, we can try executing it with ```docker run```:

```bash
sudo docker run  --network host models-test:latest
```

### [Generate JWT token with simple auth manager](https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/auth-manager/simple/token.html)
In order to use the Airflow public API, you need a JWT token for authentication. You can then include this token in your Airflow public API requests. To generate a JWT token, use the Create Token API in Simple auth manager token API.

#### Example

```bash
ENDPOINT_URL="http://localhost:8080"
curl -X 'POST' \
    "${ENDPOINT_URL}/auth/token" \
    -H 'Content-Type: application/json' \
    -d '{
    "username": "<username>",
    "password": "<password>"
    }'
```

This process will return a token that you can use in the Airflow public API requests.
```bash
{"access_token":"eyJhbGciOiJIUzUxMiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwianRpIjoiYTA5Y2E4MzZiOGVmNDNjM2IwMjc5NWEyZjVmMmMxZDUiLCJpc3MiOltdLCJhdWQiOiJhcGFjaGUtYWlyZmxvdyIsIm5iZiI6MTc3ODQ2MTg5MiwiZXhwIjoxNzc4NTQ4MjkyLCJpYXQiOjE3Nzg0NjE4OTJ9.5lb9G2R3lXpioGKKJzqZxpSgwJmK5dz41F2uZTgPSFoLb77tNLUecYbim2VDhi5qB_yQd-TAv8ftBNZllCsw6Q"}
```

