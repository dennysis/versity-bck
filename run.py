from fastapi import FastAPI,Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from app.config import engine, Base
import app.models
from app.routes import auth_routes, volunteer_routes, organization_routes, opportunity_routes, match_routes, hour_tracking_routes, admin_routes , health_routes
from app.utils.logging_config import setup_logging
from app.utils.error_handlers import validation_exception_handler, sqlalchemy_exception_handler, integrity_error_handler, general_exception_handler
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from app.utils.auth import  get_admin_user


Base.metadata.create_all(bind=engine)

setup_logging()
app = FastAPI(title="Versity API",redirect_slashes=False)


app.add_middleware(
    CORSMiddleware,
    allow_origins="*" and  "http://localhost:3000",  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
app.add_exception_handler(IntegrityError, integrity_error_handler)
app.add_exception_handler(Exception, general_exception_handler)

app.include_router(auth_routes.router)
app.include_router(volunteer_routes.router)
app.include_router(organization_routes.router, prefix="/api/organizations", tags=["organizations"])
app.include_router(opportunity_routes.router, prefix="/api/opportunities", tags=["opportunities"])
app.include_router(match_routes.router)
app.include_router(hour_tracking_routes.router)
app.include_router(admin_routes.router, prefix="/api/admin", tags=["Admin"])
app.include_router(health_routes.router) 

@app.get("/")
def read_root():
    return {"message": "Welcome to Versity API"}
@app.get("/test")
def test_root():
    return {"message": "Root test endpoint is working"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("run:app", host="0.0.0.0", port=8000, reload=True)

# start the app by running python run.py or uvicorn run:app --reload