from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from app.config import engine, Base
import app.models
from app.routes import (
    auth_routes, 
    volunteer_routes, 
    organization_routes, 
    opportunity_routes, 
    match_routes, 
    hour_tracking_routes, 
    admin_routes, 
    health_routes
)
from app.utils.logging_config import setup_logging
from app.utils.error_handlers import (
    validation_exception_handler, 
    sqlalchemy_exception_handler, 
    integrity_error_handler, 
    general_exception_handler
)
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
import logging

# Create tables
Base.metadata.create_all(bind=engine)

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Versity API",
    description="Volunteer Management System API",
    version="1.0.0",
    redirect_slashes=False
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://versity-fnd.vercel.app",
        "https://versity-fnd.onrender.com",
        "*"  # Remove this in production
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Exception handlers
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
app.add_exception_handler(IntegrityError, integrity_error_handler)
app.add_exception_handler(Exception, general_exception_handler)

# Register routes with proper prefixes
app.include_router(auth_routes.router)  # Already has prefix="/api/auth"
app.include_router(opportunity_routes.router, prefix="/api/opportunities", tags=["opportunities"])
app.include_router(match_routes.router, prefix="/api/matches", tags=["matches"])
app.include_router(hour_tracking_routes.router, prefix="/api/volunteer-hours", tags=["volunteer-hours"])
app.include_router(organization_routes.router, prefix="/api/organizations", tags=["organizations"])
app.include_router(admin_routes.router, prefix="/api/admin", tags=["admin"])
app.include_router(health_routes.router, prefix="/api/health", tags=["health"])
app.include_router(volunteer_routes.router, prefix="/api/volunteers", tags=["volunteers"])

@app.get("/")
def read_root():
    return {
        "message": "Welcome to Versity API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/api")
def api_root():
    return {
        "message": "Versity API v1.0.0",
        "endpoints": {
            "auth": "/api/auth",
            "opportunities": "/api/opportunities", 
            "matches": "/api/matches",
            "volunteer-hours": "/api/volunteer-hours",
            "organizations": "/api/organizations",
            "volunteers": "/api/volunteers",
            "admin": "/api/admin",
            "health": "/api/health"
        }
    }

@app.get("/test")
def test_root():
    return {"message": "Root test endpoint is working"}

# Add startup event to log registered routes
@app.on_event("startup")
async def startup_event():
    logger.info("Versity API starting up...")
    logger.info("Registered routes:")
    for route in app.routes:
        if hasattr(route, 'methods') and hasattr(route, 'path'):
            logger.info(f"  {list(route.methods)} {route.path}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "run:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True,
        log_level="info"
    )
