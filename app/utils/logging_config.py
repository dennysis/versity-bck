import logging
import os
from logging.handlers import RotatingFileHandler

def setup_logging():
    
    os.makedirs("logs", exist_ok=True)
    
    
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
           
            logging.StreamHandler(),
            
            RotatingFileHandler(
                "logs/app.log", 
                maxBytes=10485760,  # 10MB
                backupCount=5
            )
        ]
    )
    
    
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    
    
    logging.getLogger("uvicorn.access").setLevel(logging.INFO)
    
    
    logging.getLogger("app").setLevel(logging.DEBUG)