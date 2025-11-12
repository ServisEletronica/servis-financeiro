from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import settings
from routes import dashboard, contas, sincronizacao, projetado, recebiveis_cartao, contas_receber_senior, contas_pagar_senior

# Inicializa FastAPI
app = FastAPI(
    title="API Financeiro Servis",
    description="API para gestão de contas a pagar e receber",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configuração CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registra rotas
app.include_router(dashboard.router)
app.include_router(contas.router)
app.include_router(sincronizacao.router)
app.include_router(projetado.router)
app.include_router(recebiveis_cartao.router)
app.include_router(contas_receber_senior.router)
app.include_router(contas_pagar_senior.router)


@app.get("/")
async def root():
    """Endpoint raiz"""
    return {
        "message": "API Financeiro Servis",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.API_RELOAD
    )
