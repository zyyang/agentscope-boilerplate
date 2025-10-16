# Maxfad Agent Document

### Test

```shell

curl -X POST "http://localhost:8080/process" \
  -H "Content-Type: application/json" \
  -d '{"input": [{"role": "user", "content": [{"type": "text", "text": "法国的首都是什么？"}]}], "session_id": "test_session_001", "user_id": "test_user_001"}'

```


### Docker compose
```shell

# force to rebuild
docker compose build --no-cache

# use cache
docker compose up -d --build

```