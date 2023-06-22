# Subgraph API

## Instructions

1. Create the virtual environment. Recommended python 3.10+
2. Install dependencies from the requirements.txt file
3. Configure the google firestore client environment
4. Run the app: python main.py
5. The server is now running on localhost:8000

Get the Token:
```bash
curl -X GET localhost:8000/auth/token
```
This should return a bearer Token for use in future requests.
```bash
export TOKEN={token}
curl -X GET localhost:8000/loans/count -H "Authorization: Bearer $TOKEN"
```

### Run tests
```bash
pytest
```

### Swagger
```url
localhost:8000/docs
```