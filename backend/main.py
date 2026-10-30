from datetime import datetime
import os
import uuid
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
import boto3
from pydantic import BaseModel, HttpUrl

app = FastAPI(title="AWS Link Shortener API")

# Configurar CORS para permitir peticiones desde cualquier origen (luego puedes ajustarlo al dominio de tu S3)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Conexión con DynamoDB (usará la región configurada en tu entorno o AWS CLI)
dynamodb = boto3.resource("dynamodb", region_name=os.getenv("AWS_REGION", "us-east-1"))
table = dynamodb.Table("urls-shortener")


class URLRequest(BaseModel):
  original_url: HttpUrl


@app.post("/shorten", status_code=status.HTTP_201_CREATED)
def create_short_url(payload: URLRequest):
  short_code = str(uuid.uuid4())
  created_at = datetime.utcnow().isoformat()

  item = {
      "short_code": short_code,
      "original_url": str(payload.original_url),
      "created_at": created_at,
  }

  # Guardar en DynamoDB
  table.put_item(Item=item)

  # Para pruebas locales puedes usar localhost, luego cambiarás esto por la IP pública de tu EC2
  base_url = os.getenv("BASE_URL", "http://localhost:8000")

  return {
      "short_code": short_code,
      "original_url": str(payload.original_url),
      "short_url": f"{base_url}/{short_code}",
  }


@app.get("/{short_code}")
def redirect_to_url(short_code: str):
  response = table.get_item(Key={"short_code": short_code})

  if "Item" not in response:
    raise HTTPException(status_code=404, detail="URL no encontrada")

  original_url = response["Item"]["original_url"]
  # Redirección HTTP 307 como pide la tarea
  return RedirectResponse(url=original_url, status_code=307)


@app.get("/urls/{short_code}")
def get_url_info(short_code: str):
  response = table.get_item(Key={"short_code": short_code})

  if "Item" not in response:
    raise HTTPException(status_code=404, detail="URL no encontrada")

  return response["Item"]