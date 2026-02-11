"""
OpenClaw AI - Security Module
Handles authentication, authorization, encryption, and input validation
"""
import re
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional, Union
from pathlib import Path

import bcrypt
from jose import JWTError, jwt
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class PasswordValidator:
    """Validates password strength"""
    
    @staticmethod
    def validate(password: str, min_length: int = 12,
                require_special: bool = True,
                require_numbers: bool = True,
                require_uppercase: bool = True) -> tuple[bool, str]:
        """
        Validate password against security requirements
        
        Args:
            password: Password to validate
            min_length: Minimum password length
            require_special: Require special characters
            require_numbers: Require numbers
            require_uppercase: Require uppercase letters
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if len(password) < min_length:
            return False, f"Password must be at least {min_length} characters long"
        
        if require_uppercase and not re.search(r'[A-Z]', password):
            return False, "Password must contain at least one uppercase letter"
        
        if require_numbers and not re.search(r'\d', password):
            return False, "Password must contain at least one number"
        
        if require_special and not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            return False, "Password must contain at least one special character"
        
        return True, ""


class InputSanitizer:
    """Sanitizes and validates user input"""
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """
        Sanitize filename to prevent path traversal
        
        Args:
            filename: Input filename
            
        Returns:
            Sanitized filename
        """
        # Remove any path components
        filename = Path(filename).name
        
        # Remove dangerous characters
        filename = re.sub(r'[^\w\s\-\.]', '', filename)
        
        # Prevent hidden files
        if filename.startswith('.'):
            filename = filename[1:]
        
        # Ensure not empty
        if not filename:
            filename = "unnamed_file"
        
        return filename
    
    @staticmethod
    def validate_path(path: str, allowed_base: str) -> bool:
        """
        Validate that path is within allowed base directory
        
        Args:
            path: Path to validate
            allowed_base: Base directory that must contain the path
            
        Returns:
            True if path is safe, False otherwise
        """
        try:
            # Resolve to absolute paths
            abs_path = Path(path).resolve()
            abs_base = Path(allowed_base).resolve()
            
            # Check if path is relative to base
            abs_path.relative_to(abs_base)
            return True
        except (ValueError, RuntimeError):
            return False
    
    @staticmethod
    def sanitize_input(text: str, max_length: int = 10000) -> str:
        """
        Sanitize text input
        
        Args:
            text: Input text
            max_length: Maximum allowed length
            
        Returns:
            Sanitized text
        """
        # Limit length
        if len(text) > max_length:
            text = text[:max_length]
        
        # Remove null bytes
        text = text.replace('\x00', '')
        
        return text


class AuthManager:
    """Manages authentication and authorization"""
    
    def __init__(self, secret_key: str, algorithm: str = "HS256",
                 expire_minutes: int = 30):
        """
        Initialize auth manager
        
        Args:
            secret_key: Secret key for JWT signing
            algorithm: JWT algorithm
            expire_minutes: Token expiration time
        """
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.expire_minutes = expire_minutes
    
    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    
    def create_access_token(self, data: dict,
                           expires_delta: Optional[timedelta] = None) -> str:
        """
        Create JWT access token
        
        Args:
            data: Data to encode in token
            expires_delta: Custom expiration time
            
        Returns:
            JWT token string
        """
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.expire_minutes)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def verify_token(self, token: str) -> Optional[dict]:
        """
        Verify and decode JWT token
        
        Args:
            token: JWT token to verify
            
        Returns:
            Decoded token data or None if invalid
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except JWTError:
            return None


class EncryptionManager:
    """Manages data encryption"""
    
    def __init__(self, password: Optional[str] = None, salt: Optional[bytes] = None):
        """
        Initialize encryption manager
        
        Args:
            password: Password for key derivation (generates random key if None)
            salt: Salt for key derivation (generates random salt if None and password is provided)
        
        Note:
            If you need to decrypt data later, you must save and reuse the same salt.
            For application-level encryption, use a consistent salt stored securely.
            For per-record encryption, generate and store a unique salt per record.
        """
        if password is None:
            # Generate random key for temporary encryption
            self.key = Fernet.generate_key()
            self.salt = None
        else:
            # Generate or use provided salt
            if salt is None:
                # For application-level encryption with reusable key
                # WARNING: Using a fixed salt means the same password always produces
                # the same encryption key. This is acceptable for application-level
                # config encryption but NOT for user data encryption.
                # For user data, generate unique salt per record and store it.
                salt = b'openclaw_v2_app_level_salt_2026'
            
            self.salt = salt
            
            # Derive key from password
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            key = kdf.derive(password.encode())
            import base64
            self.key = base64.urlsafe_b64encode(key)
        
        self.cipher = Fernet(self.key)
    
    def encrypt(self, data: Union[str, bytes]) -> bytes:
        """
        Encrypt data
        
        Args:
            data: Data to encrypt (string or bytes)
            
        Returns:
            Encrypted data
        """
        if isinstance(data, str):
            data = data.encode()
        return self.cipher.encrypt(data)
    
    def decrypt(self, encrypted_data: bytes) -> bytes:
        """
        Decrypt data
        
        Args:
            encrypted_data: Encrypted data
            
        Returns:
            Decrypted data
        """
        return self.cipher.decrypt(encrypted_data)
    
    def decrypt_to_string(self, encrypted_data: bytes) -> str:
        """
        Decrypt data and return as string
        
        Args:
            encrypted_data: Encrypted data
            
        Returns:
            Decrypted string
        """
        return self.decrypt(encrypted_data).decode()


def generate_secure_token(length: int = 32) -> str:
    """
    Generate cryptographically secure random token
    
    Args:
        length: Length of token in bytes
        
    Returns:
        Hex-encoded token
    """
    return secrets.token_hex(length)


def hash_data(data: str) -> str:
    """
    Create SHA-256 hash of data
    
    Args:
        data: Data to hash
        
    Returns:
        Hex-encoded hash
    """
    return hashlib.sha256(data.encode()).hexdigest()
