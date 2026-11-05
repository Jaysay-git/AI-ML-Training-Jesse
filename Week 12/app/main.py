
from fastapi import FastAPI
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.api.auth import router as auth_router
from app.api.prices import router as prices_router
from app.api.analytics import router as analytics_router
from app.api.catalogue import router as catalogue_router
from app.api.agent import router as agent_router
from app.api.documents import router as documents_router

from app.core.limiter import limiter
from app.database.connection import Base, engine


Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Naija Cost of Living Intelligence",
    description=(
        "An API for exploring and comparing essential "
        "commodity prices across Nigerian cities, "
        "with AI-powered price intelligence."
    ),
    version="1.0.0",
)

# Rate limiting
app.state.limiter = limiter
app.add_exception_handler(
    RateLimitExceeded,
    _rate_limit_exceeded_handler,
)

# Register API routers
app.include_router(auth_router)
app.include_router(prices_router)
app.include_router(analytics_router)
app.include_router(catalogue_router)
app.include_router(agent_router)
app.include_router(documents_router)


@app.get("/health", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "application": "Naija Cost of Living Intelligence",
    }
