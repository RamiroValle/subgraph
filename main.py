import jwt
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.openapi.utils import get_openapi
from fastapi.openapi.docs import get_swagger_ui_html
from google.cloud import firestore
import httpx


app = FastAPI()
client = firestore.Client()  # Cliente Firestore
SECRET_KEY = "subgraphapi"
ALGORITHM = "HS256"


async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())) -> dict:
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")


@app.get("/loans/count", dependencies=[Depends(verify_token)])
def get_prestamos_count():
    prestamos_ref = client.collection("prestamos")
    prestamos_docs = prestamos_ref.stream()
    return len(list(prestamos_docs))


@app.get("/auth/token")
async def get_token():
    token_payload = {"grant_type": "client_credentials"}
    token = jwt.encode(token_payload, SECRET_KEY, algorithm=ALGORITHM)
    return {"access_token": token, "token_type": "bearer"}  


@app.get("/openapi.json", include_in_schema=False)
def get_openapi_json():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Subgraph API",
        version="1.0",
        routes=app.routes,
    )
    app.openapi_schema = openapi_schema
    return app.openapi_schema


@app.get("/docs", include_in_schema=False)
async def get_documentation():
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title="Documentación de la API",
        swagger_favicon_url="https://fastapi.tiangolo.com/img/favicon.png",
    )


@app.on_event("startup")
async def startup():
    # Extrae los últimos 20 préstamos del subgraph provisto
    subgraph_url = "https://api.thegraph.com/subgraphs/name/sebipap/exactly-sandbox-optimism"
    query = """
    {
      borrows(first: 20, orderBy: timestamp, orderDirection: desc) {
        id
        borrower
      }
    }
    """
    async with httpx.AsyncClient() as graph:
        response = await graph.post(subgraph_url, json={"query": query})
        data = response.json()
        loans = data["data"]["borrows"]

        # Almacena los detalles del prestamo en Firestore
        prestamos_ref = client.collection("prestamos")
        for loan in loans:
            loan_id = loan["id"]
            borrower_address = loan["borrower"]

            # Verifica si el prestamo ya existe en Firestore para evitar duplicados
            prestamo_doc = prestamos_ref.document(loan_id).get()
            if not prestamo_doc.exists:
                prestamos_ref.document(loan_id).set({"id": loan_id, "borrower": borrower_address})


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
