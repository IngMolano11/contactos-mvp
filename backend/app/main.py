from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine
from app.models_db import Base
from app.routes import router as contactos_router
from app.auth_routes import router as auth_router  # Añadir esta línea

# --- Crea tablas en la base de datos al iniciar ---
Base.metadata.create_all(bind=engine)

app = FastAPI(title="API Contactos MVP")

# --- Middleware CORS (ajusta el origen según necesites) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],  # o ["*"] durante desarrollo
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Handlers de errores de validación y HTTP ---
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "errors": exc.errors(),
            "body": exc.body
        },
    )

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.detail},
    )

# --- Endpoint de salud (ping) ---
@app.get("/api/ping")
async def ping():
    """
    Ruta para que el frontend verifique que la API está viva.
    Devuelve JSON: {"ping": "pong"}
    """
    return {"ping": "pong"}

# --- Monta el router de contactos en /api/contactos ---
app.include_router(contactos_router, prefix="/api/contactos", tags=["Contactos"])

# Montar rutas de autenticación
app.include_router(auth_router, prefix="/api/auth", tags=["Auth"])
