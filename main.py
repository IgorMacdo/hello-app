from typing import Union

from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def read_root():
    return {"message": "Olá, CI/CD com GitHub Actions e ArgoCD!!!"}


@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "hello-app"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}
