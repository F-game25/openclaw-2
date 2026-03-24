# OpenClaw AI - Private & Secure Edition

A privacy-focused, secure implementation of OpenClaw AI designed for local, private use on your personal PC.

## 🔒 Security Features

### Core Security
- **Local-Only by Default**: Binds to `127.0.0.1` (localhost) preventing external access
- **Strong Authentication**: JWT-based authentication with configurable expiration
- **Password Requirements**: Enforced strong passwords (12+ chars, uppercase, numbers, special characters)
- **Rate Limiting**: Protection against brute force and DoS attacks
- **Input Validation**: All user inputs are sanitized and validated
- **Security Headers**: Comprehensive HTTP security headers (CSP, XSS protection, etc.)
- **Encrypted Storage**: Data encryption at rest using AES-256-GCM

### Privacy Protection
- **No Telemetry**: Zero analytics or tracking by default
- **No External Calls**: Optional blocking of all external API calls
- **Local Data Storage**: All data stays on your machine
- **Audit Logging**: Complete audit trail of all security events
- **Session Management**: Controlled session timeouts and limits

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. **Clone the repository**:
```bash
git clone https://github.com/F-game25/openclaw-2.git
cd openclaw-2
```

2. **Create virtual environment**:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Configure security settings**:
```bash
# Copy the config template
cp config.yml config.local.yml

# Edit config.local.yml and change the JWT secret
# Or set environment variable:
export JWT_SECRET_KEY="your-very-secure-random-secret-key-here-min-32-chars"
```

5. **Generate a secure JWT secret** (recommended):
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### Running the Application

```bash
python main.py
```

The application will start on `http://127.0.0.1:8000` (localhost only).

## 📖 Usage

### Health Check
```bash
curl http://127.0.0.1:8000/health
```

### Security Status
```bash
curl http://127.0.0.1:8000/security/status
```

### Register a User
```bash
curl -X POST http://127.0.0.1:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "myuser",
    "password": "SecureP@ssw0rd123!"
  }'
```

### Chat Endpoint
```bash
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello, OpenClaw!"
  }'
```

## ⚙️ Configuration

### Security Settings (config.local.yml)

```yaml
security:
  # JWT Settings
  jwt_secret_key: "CHANGE_THIS_TO_A_SECURE_RANDOM_VALUE"
  access_token_expire_minutes: 30
  
  # Password Requirements
  min_password_length: 12
  require_special_chars: true
  require_numbers: true
  require_uppercase: true
  
  # Rate Limiting
  rate_limit_enabled: true
  rate_limit_per_minute: 60
```

### Privacy Settings

```yaml
privacy:
  # Disable all telemetry
  telemetry_enabled: false
  analytics_enabled: false
  
  # Block all external API calls (maximum privacy)
  external_api_calls_disabled: true
  
  # Enable encryption
  encrypt_data_at_rest: true
  encryption_algorithm: "AES-256-GCM"
```

### Environment Variables

For enhanced security, use environment variables for sensitive data:

```bash
export JWT_SECRET_KEY="your-secret-key"
export OPENAI_API_KEY="your-api-key"  # Optional, if using OpenAI
export ANTHROPIC_API_KEY="your-api-key"  # Optional, if using Claude
```

## 🔐 Security Best Practices

### 1. Strong JWT Secret
- Use at least 32 characters
- Generate with cryptographically secure random generator
- Store in environment variable, not in config file
- Rotate regularly (e.g., every 90 days)

### 2. Network Security
- Keep default `host: 127.0.0.1` to prevent external access
- If remote access needed, use VPN or SSH tunnel
- Never expose directly to internet
- Use firewall rules to restrict access

### 3. Password Management
- Enforce strong password requirements
- Change default admin passwords immediately
- Use unique passwords per installation
- Consider using password manager

### 4. Data Protection
- Enable encryption at rest
- Regular backups of data directory
- Secure file permissions (read/write for owner only)
- Clear old logs regularly

### 5. Monitoring
- Review audit logs regularly
- Monitor failed authentication attempts
- Check security status endpoint
- Set up alerts for suspicious activity

### 6. Updates
- Keep dependencies updated
- Monitor security advisories
- Test updates in non-production first
- Maintain rollback capability

## 📁 Directory Structure

```
openclaw-2/
├── main.py              # Main application entry point
├── config_manager.py    # Configuration management
├── security.py          # Security utilities
├── config.yml           # Default configuration (template)
├── config.local.yml     # Your local configuration (gitignored)
├── requirements.txt     # Python dependencies
├── .gitignore          # Git ignore rules
├── README.md           # This file
├── SECURITY.md         # Security guidelines
├── data/               # Local data storage (gitignored)
└── logs/               # Application logs (gitignored)
    ├── openclaw.log    # Application log
    └── audit.log       # Security audit log
```

## 🛡️ Threat Model

### Protected Against
- ✅ External network access (localhost-only default)
- ✅ Brute force attacks (rate limiting)
- ✅ Path traversal attacks (input validation)
- ✅ SQL injection (parameterized queries when DB used)
- ✅ XSS attacks (input sanitization, CSP headers)
- ✅ CSRF attacks (token-based auth)
- ✅ Session hijacking (secure tokens, expiration)
- ✅ Weak passwords (password strength requirements)

### Out of Scope
- Physical access to the machine
- OS-level vulnerabilities
- Hardware attacks
- Social engineering

## 🔄 Updating

```bash
# Pull latest changes
git pull origin main

# Update dependencies
pip install -r requirements.txt --upgrade

# Review configuration changes
diff config.yml config.local.yml

# Restart application
python main.py
```

## 🐛 Troubleshooting

### "JWT secret must be changed from default"
- Set `JWT_SECRET_KEY` environment variable OR
- Update `security.jwt_secret_key` in `config.local.yml`

### Application won't start
- Check logs in `logs/openclaw.log`
- Verify all dependencies installed: `pip install -r requirements.txt`
- Ensure Python 3.8+ is being used: `python --version`

### Cannot connect to application
- Verify it's running: Check for process
- Try: `curl http://127.0.0.1:8000/health`

## 📞 Support

For issues and questions:
1. Check logs: `logs/openclaw.log` and `logs/audit.log`
2. Review security status: `/security/status` endpoint
3. File issue on GitHub repository

## ⚠️ Disclaimer

This software is provided for personal, private use. While security best practices have been implemented, no software is 100% secure. Users are responsible for:
- Keeping software and dependencies updated
- Following security best practices
- Protecting their own systems and data
- Complying with applicable laws and regulations

**Never expose this application directly to the internet without additional security measures (firewall, VPN, reverse proxy with authentication, etc.).**
