import logging
import json
from datetime import datetime
from typing import Dict, Any
from src.core.config import settings

class JSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # Add extra fields
        if hasattr(record, 'user_id'):
            log_data['user_id'] = record.user_id
        if hasattr(record, 'request_id'):
            log_data['request_id'] = record.request_id
        if hasattr(record, 'extra'):
            log_data.update(record.extra)
        
        # Add exception if present
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        
        return json.dumps(log_data)

def setup_logging():
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, "DEBUG" if settings.DEBUG else "INFO"))
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(JSONFormatter())
    logger.addHandler(console_handler)
    
    # File handler (in production)
    if settings.APP_ENV == "production":
        import os
        os.makedirs("./logs", exist_ok=True)
        file_handler = logging.FileHandler('./logs/app.log')
        file_handler.setFormatter(JSONFormatter())
        logger.addHandler(file_handler)
