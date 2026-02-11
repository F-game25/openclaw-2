"""
OpenClaw AI - Configuration Management
Handles secure loading and validation of configuration
"""
import os
import yaml
from pathlib import Path
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field, validator
from pydantic_settings import BaseSettings


class SecurityConfig(BaseModel):
    """Security configuration"""
    jwt_secret_key: str = Field(min_length=32)
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    min_password_length: int = 12
    require_special_chars: bool = True
    require_numbers: bool = True
    require_uppercase: bool = True
    rate_limit_enabled: bool = True
    rate_limit_per_minute: int = 60
    cors_origins: list[str] = ["http://localhost:8000"]
    max_sessions_per_user: int = 3
    session_timeout_minutes: int = 60


class PrivacyConfig(BaseModel):
    """Privacy configuration"""
    data_dir: str = "./data"
    logs_dir: str = "./logs"
    telemetry_enabled: bool = False
    analytics_enabled: bool = False
    external_api_calls_disabled: bool = False
    log_retention_days: int = 30
    session_data_retention_days: int = 7
    encrypt_data_at_rest: bool = True
    encryption_algorithm: str = "AES-256-GCM"


class AIConfig(BaseModel):
    """AI model configuration"""
    use_local_model: bool = True
    model_path: str = "./models"
    max_tokens: int = 2048
    temperature: float = 0.7
    openai_api_key_env: str = "OPENAI_API_KEY"
    anthropic_api_key_env: str = "ANTHROPIC_API_KEY"


class LoggingConfig(BaseModel):
    """Logging configuration"""
    level: str = "INFO"
    format: str = "json"
    file_enabled: bool = True
    console_enabled: bool = True
    audit_enabled: bool = True
    audit_failed_auth: bool = True
    audit_file_access: bool = True
    audit_api_calls: bool = True


class LimitsConfig(BaseModel):
    """Resource limits configuration"""
    max_file_upload_size_mb: int = 10
    max_concurrent_requests: int = 10
    max_memory_usage_mb: int = 1024
    request_timeout_seconds: int = 30


class Config(BaseSettings):
    """Main configuration class"""
    app_name: str = "OpenClaw AI - Private & Secure"
    app_version: str = "2.0.0"
    environment: str = "production"
    debug: bool = False
    host: str = "127.0.0.1"
    port: int = 8000
    
    security: SecurityConfig
    privacy: PrivacyConfig
    ai: AIConfig
    logging: LoggingConfig
    limits: LimitsConfig
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


def load_config(config_path: Optional[str] = None) -> Config:
    """
    Load configuration from YAML file with secure defaults
    
    Args:
        config_path: Path to config file (defaults to config.yml)
        
    Returns:
        Config object with validated settings
    """
    if config_path is None:
        # Try local config first, fall back to default
        if Path("config.local.yml").exists():
            config_path = "config.local.yml"
        else:
            config_path = "config.yml"
    
    # Load YAML config
    with open(config_path, 'r') as f:
        yaml_config = yaml.safe_load(f)
    
    # Flatten nested structure for pydantic
    flat_config = {
        'app_name': yaml_config.get('app', {}).get('name', 'OpenClaw AI'),
        'app_version': yaml_config.get('app', {}).get('version', '2.0.0'),
        'environment': yaml_config.get('app', {}).get('environment', 'production'),
        'debug': yaml_config.get('app', {}).get('debug', False),
        'host': yaml_config.get('server', {}).get('host', '127.0.0.1'),
        'port': yaml_config.get('server', {}).get('port', 8000),
        'security': SecurityConfig(**yaml_config.get('security', {})),
        'privacy': PrivacyConfig(**yaml_config.get('privacy', {})),
        'ai': AIConfig(**yaml_config.get('ai', {})),
        'logging': LoggingConfig(**yaml_config.get('logging', {})),
        'limits': LimitsConfig(**yaml_config.get('limits', {})),
    }
    
    # Override JWT secret from environment if available
    jwt_secret = os.getenv('JWT_SECRET_KEY')
    if jwt_secret:
        flat_config['security'].jwt_secret_key = jwt_secret
    
    # Validate that JWT secret was changed from default
    if flat_config['security'].jwt_secret_key == "CHANGE_THIS_IN_CONFIG_LOCAL_YML_OR_SET_JWT_SECRET_KEY_ENV_VAR":
        if not jwt_secret:
            raise ValueError(
                "Security Error: JWT secret key must be changed from default. "
                "Set JWT_SECRET_KEY environment variable or update config.local.yml"
            )
    
    return Config(**flat_config)


def validate_security_config(config: Config) -> list[str]:
    """
    Validate security configuration and return warnings
    
    Args:
        config: Configuration to validate
        
    Returns:
        List of security warnings
    """
    warnings = []
    
    # Check if binding to public interface
    if config.host != "127.0.0.1" and config.host != "localhost":
        warnings.append(
            f"WARNING: Server is configured to bind to {config.host}. "
            "For maximum security, use 127.0.0.1 (localhost only)."
        )
    
    # Check if debug mode is enabled
    if config.debug and config.environment == "production":
        warnings.append(
            "WARNING: Debug mode is enabled in production. "
            "This may expose sensitive information."
        )
    
    # Check external API calls
    if not config.privacy.external_api_calls_disabled:
        warnings.append(
            "INFO: External API calls are enabled. "
            "Set privacy.external_api_calls_disabled=true for maximum privacy."
        )
    
    # Check encryption
    if not config.privacy.encrypt_data_at_rest:
        warnings.append(
            "WARNING: Data encryption at rest is disabled. "
            "Enable privacy.encrypt_data_at_rest for better security."
        )
    
    return warnings
