from fastapi.testclient import TestClient
from .main import app

client = TestClient(app)

def test_get_prestamos_count():
    # Obtiene el token de autenticacion
    response_token = client.get("/auth/token")
    assert response_token.status_code == 200
    token = response_token.json()["access_token"]

    headers = {
        "Authorization": f"Bearer {token}"
    }

    # Realiza la solicitud al endpoint con el header de autenticacion
    response = client.get("/loans/count", headers=headers)
    assert response.status_code == 200
    count = response.json()
    assert isinstance(count, int)

def test_auth_token():
    response = client.get("/auth/token")
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "token_type" in data
    assert data["token_type"] == "bearer"