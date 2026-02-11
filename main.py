"""
OpenClaw AI - Main Application
Secure, private AI assistant for local use
"""
import os
import logging
import json
from datetime import datetime
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException, Depends, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from pydantic import BaseModel, Field

from config_manager import load_config, validate_security_config
from security import (
    AuthManager, InputSanitizer, PasswordValidator,
    EncryptionManager, generate_secure_token
)

# Initialize configuration
config = load_config()

# Setup logging
log_dir = Path(config.privacy.logs_dir)
log_dir.mkdir(exist_ok=True, parents=True)

logging.basicConfig(
    level=getattr(logging, config.logging.level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / 'openclaw.log'),
        logging.StreamHandler() if config.logging.console_enabled else logging.NullHandler()
    ]
)
logger = logging.getLogger(__name__)

# Audit logger for security events
audit_logger = logging.getLogger('audit')
audit_handler = logging.FileHandler(log_dir / 'audit.log')
audit_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
audit_logger.addHandler(audit_handler)
audit_logger.setLevel(logging.INFO)

# Initialize security components
auth_manager = AuthManager(
    secret_key=config.security.jwt_secret_key,
    algorithm=config.security.jwt_algorithm,
    expire_minutes=config.security.access_token_expire_minutes
)

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

# Initialize FastAPI app
app = FastAPI(
    title=config.app_name,
    version=config.app_version,
    docs_url="/docs" if config.debug else None,  # Disable docs in production
    redoc_url="/redoc" if config.debug else None
)

# Add rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS middleware with strict origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.security.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


# Security middleware
@app.middleware("http")
async def security_headers_middleware(request: Request, call_next):
    """Add security headers to all responses"""
    response = await call_next(request)
    
    # Security headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    
    return response


# Audit logging middleware
@app.middleware("http")
async def audit_logging_middleware(request: Request, call_next):
    """Log security-relevant events"""
    if config.logging.audit_enabled:
        start_time = datetime.utcnow()
        
        # Log request
        audit_logger.info(json.dumps({
            "event": "request",
            "timestamp": start_time.isoformat(),
            "method": request.method,
            "path": request.url.path,
            "client": request.client.host if request.client else "unknown"
        }))
        
        response = await call_next(request)
        
        # Log response
        duration = (datetime.utcnow() - start_time).total_seconds()
        audit_logger.info(json.dumps({
            "event": "response",
            "timestamp": datetime.utcnow().isoformat(),
            "method": request.method,
            "path": request.url.path,
            "status": response.status_code,
            "duration_seconds": duration
        }))
        
        return response
    else:
        return await call_next(request)


# Pydantic models
class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    version: str
    secure_mode: bool
    privacy_mode: bool


class UserCreate(BaseModel):
    """User creation request"""
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=12)


class TokenResponse(BaseModel):
    """Authentication token response"""
    access_token: str
    token_type: str = "bearer"


class ChatRequest(BaseModel):
    """Chat message request"""
    message: str = Field(..., min_length=1, max_length=10000)
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    """Chat message response"""
    response: str
    session_id: str
    timestamp: str


# API Endpoints
@app.get("/", response_model=HealthResponse)
async def root():
    """Root endpoint - health check"""
    return HealthResponse(
        status="healthy",
        version=config.app_version,
        secure_mode=True,
        privacy_mode=not config.privacy.telemetry_enabled
    )


@app.get("/health", response_model=HealthResponse)
@limiter.limit(f"{config.security.rate_limit_per_minute}/minute")
async def health_check(request: Request):
    """Health check endpoint with rate limiting"""
    return HealthResponse(
        status="healthy",
        version=config.app_version,
        secure_mode=True,
        privacy_mode=not config.privacy.telemetry_enabled
    )


@app.post("/auth/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")  # Strict rate limit for registration
async def register(request: Request, user_data: UserCreate):
    """
    Register a new user
    
    This is a simplified implementation for demonstration.
    In production, integrate with proper user database.
    """
    # Validate password strength
    is_valid, error_msg = PasswordValidator.validate(
        user_data.password,
        min_length=config.security.min_password_length,
        require_special=config.security.require_special_chars,
        require_numbers=config.security.require_numbers,
        require_uppercase=config.security.require_uppercase
    )
    
    if not is_valid:
        audit_logger.warning(json.dumps({
            "event": "registration_failed",
            "reason": "weak_password",
            "username": user_data.username
        }))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg
        )
    
    # Sanitize username
    username = InputSanitizer.sanitize_input(user_data.username, max_length=50)
    
    # Hash password
    hashed_password = auth_manager.hash_password(user_data.password)
    
    # In production: Store user in database
    # For now, just create token
    
    # Create access token
    access_token = auth_manager.create_access_token(
        data={"sub": username, "type": "user"}
    )
    
    audit_logger.info(json.dumps({
        "event": "user_registered",
        "username": username,
        "timestamp": datetime.utcnow().isoformat()
    }))
    
    return TokenResponse(access_token=access_token)


@app.post("/chat", response_model=ChatResponse)
@limiter.limit(f"{config.security.rate_limit_per_minute}/minute")
async def chat(request: Request, chat_request: ChatRequest):
    """
    Process chat message
    
    This is a placeholder implementation. In production:
    - Integrate with actual AI model
    - Implement session management
    - Add context handling
    """
    # Sanitize input
    message = InputSanitizer.sanitize_input(
        chat_request.message,
        max_length=config.limits.max_file_upload_size_mb * 1024 * 1024
    )
    
    # Generate or validate session ID
    session_id = chat_request.session_id or generate_secure_token(16)
    
    # Log the interaction
    if config.logging.audit_api_calls:
        audit_logger.info(json.dumps({
            "event": "chat_request",
            "session_id": session_id,
            "message_length": len(message),
            "timestamp": datetime.utcnow().isoformat()
        }))
    
    # Process message (placeholder)
    response_text = (
        f"OpenClaw AI (Secure Mode) - Your message has been received and processed securely. "
        f"This is a placeholder response. In production, this would connect to your AI model. "
        f"Message length: {len(message)} characters."
    )
    
    return ChatResponse(
        response=response_text,
        session_id=session_id,
        timestamp=datetime.utcnow().isoformat()
    )


@app.get("/security/status")
@limiter.limit(f"{config.security.rate_limit_per_minute}/minute")
async def security_status(request: Request):
    """Get security status and warnings"""
    warnings = validate_security_config(config)
    
    return {
        "secure_mode": True,
        "encryption_enabled": config.privacy.encrypt_data_at_rest,
        "rate_limiting_enabled": config.security.rate_limit_enabled,
        "external_calls_blocked": config.privacy.external_api_calls_disabled,
        "telemetry_disabled": not config.privacy.telemetry_enabled,
        "warnings": warnings
    }


@app.on_event("startup")
async def startup_event():
    """Application startup"""
    logger.info(f"Starting {config.app_name} v{config.app_version}")
    
    # Create necessary directories
    Path(config.privacy.data_dir).mkdir(exist_ok=True, parents=True)
    Path(config.privacy.logs_dir).mkdir(exist_ok=True, parents=True)
    
    # Log security warnings
    warnings = validate_security_config(config)
    if warnings:
        logger.warning("Security Configuration Warnings:")
        for warning in warnings:
            logger.warning(f"  - {warning}")
    
    logger.info(f"Server starting on {config.host}:{config.port}")
    logger.info(f"Privacy mode: {'ENABLED' if not config.privacy.telemetry_enabled else 'DISABLED'}")
    logger.info(f"Encryption: {'ENABLED' if config.privacy.encrypt_data_at_rest else 'DISABLED'}")


@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown"""
    logger.info("Shutting down OpenClaw AI")


if __name__ == "__main__":
    import uvicorn
    
    # Run with secure settings
    uvicorn.run(
        app,
        host=config.host,
        port=config.port,
        log_level=config.logging.level.lower(),
        access_log=config.logging.file_enabled
    )
