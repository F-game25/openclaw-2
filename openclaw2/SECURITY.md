# Security Policy

## Reporting Security Vulnerabilities

If you discover a security vulnerability in OpenClaw AI - Private & Secure Edition, please report it responsibly:

1. **Do NOT** create a public GitHub issue
2. Email the maintainer privately with details
3. Allow time for the issue to be addressed before public disclosure

## Security Best Practices for Deployment

### Network Security

#### ✅ DO
- Keep the application bound to `127.0.0.1` (localhost) for local-only access
- Use VPN or SSH tunneling if remote access is needed
- Place behind a reverse proxy (nginx, Apache) if exposing to network
- Use firewall rules to restrict access to authorized IPs only
- Enable HTTPS/TLS for any network exposure

#### ❌ DON'T
- Expose directly to the internet without additional security layers
- Use weak or default passwords
- Disable rate limiting
- Run with debug mode enabled in production
- Bind to `0.0.0.0` unless absolutely necessary and properly secured

### Authentication & Authorization

#### ✅ DO
- Use strong, unique passwords (12+ characters, mixed case, numbers, special chars)
- Store JWT secret in environment variables, not config files
- Rotate JWT secrets regularly (every 90 days recommended)
- Use unique secrets for each installation
- Enable rate limiting on authentication endpoints
- Monitor failed authentication attempts

#### ❌ DON'T
- Use default or example passwords
- Share credentials between installations
- Store passwords in plain text
- Disable password complexity requirements
- Allow unlimited authentication attempts

### Data Protection

#### ✅ DO
- Enable encryption at rest (`privacy.encrypt_data_at_rest: true`)
- Use secure file permissions (owner read/write only)
- Regular backups of data directory
- Clear old logs according to retention policy
- Encrypt backups if stored externally
- Review audit logs regularly

#### ❌ DON'T
- Store sensitive data unencrypted
- Use world-readable file permissions
- Commit sensitive data to version control
- Disable audit logging
- Share data directories between users

### Configuration Security

#### ✅ DO
- Use `config.local.yml` for local overrides (gitignored)
- Store secrets in environment variables
- Review security warnings on startup
- Keep default secure settings unless needed
- Document any security setting changes
- Use minimum required privileges

#### ❌ DON'T
- Commit `config.local.yml` to version control
- Store API keys in configuration files
- Disable security features without understanding impact
- Use debug mode in production
- Ignore security warnings

### Dependency Management

#### ✅ DO
- Keep dependencies updated regularly
- Review security advisories
- Use `pip install --upgrade` for updates
- Test updates before deploying
- Use virtual environments
- Review dependency changes in updates

#### ❌ DON'T
- Use outdated dependencies with known vulnerabilities
- Install unverified packages
- Ignore dependency security warnings
- Mix production and development dependencies

### Monitoring & Logging

#### ✅ DO
- Enable audit logging (`logging.audit_enabled: true`)
- Review logs regularly for suspicious activity
- Monitor failed authentication attempts
- Set up alerts for security events
- Rotate logs according to retention policy
- Secure log files (appropriate permissions)

#### ❌ DON'T
- Disable logging in production
- Log sensitive data (passwords, tokens)
- Allow unlimited log growth
- Use world-readable log files
- Ignore security alerts

## Security Checklist

Before deploying to production:

- [ ] JWT secret changed from default
- [ ] Strong passwords configured
- [ ] Application bound to localhost only (or secured if networked)
- [ ] Rate limiting enabled
- [ ] Encryption at rest enabled
- [ ] Telemetry disabled
- [ ] Audit logging enabled
- [ ] Security headers verified
- [ ] Dependencies updated
- [ ] Firewall rules configured
- [ ] File permissions secured
- [ ] No secrets in version control
- [ ] Backup strategy in place
- [ ] Monitoring configured
- [ ] Documentation reviewed

## Security Features

### Authentication
- JWT-based token authentication
- Bcrypt password hashing (cost factor: 12)
- Configurable token expiration
- Session management with limits
- Rate limiting on auth endpoints

### Input Validation
- Path traversal prevention
- Filename sanitization
- Input length limits
- Null byte filtering
- SQL injection prevention (when using database)

### Encryption
- AES-256-GCM for data at rest
- PBKDF2 key derivation
- Secure random token generation
- SHA-256 for hashing

### Network Security
- Localhost-only binding by default
- CORS with strict origin controls
- Security headers (CSP, X-Frame-Options, etc.)
- HTTPS/TLS support ready

### Privacy
- No telemetry by default
- Optional external API blocking
- Local data storage only
- Configurable data retention
- Audit trail for compliance

## Known Limitations

### Current Scope
This implementation provides security for:
- Local, single-user deployment
- Protection against common web vulnerabilities
- Privacy-focused data handling
- Audit trail for security events

### Out of Scope
This implementation does NOT protect against:
- Physical access to the machine
- Operating system vulnerabilities
- Hardware-level attacks
- Malicious local users with system access
- Sophisticated persistent threats
- Zero-day exploits in dependencies

## Recommended Reading

- [OWASP Top Ten](https://owasp.org/www-project-top-ten/)
- [OWASP API Security Top 10](https://owasp.org/www-project-api-security/)
- [CWE Top 25 Most Dangerous Software Weaknesses](https://cwe.mitre.org/top25/)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)

## Security Updates

Security updates will be released as needed. To stay informed:
1. Watch the GitHub repository for releases
2. Subscribe to security advisories
3. Check for updates regularly: `git pull && pip install -r requirements.txt --upgrade`

## Incident Response

If you suspect a security incident:

1. **Isolate**: Stop the application and disconnect from network
2. **Assess**: Review audit logs for suspicious activity
3. **Contain**: Identify and remove the threat
4. **Recover**: Restore from clean backup if needed
5. **Learn**: Document the incident and improve security

## Compliance Notes

This implementation includes features that may help with:
- GDPR compliance (privacy controls, data retention)
- SOC 2 (audit logging, access controls)
- HIPAA considerations (encryption, audit trails)

**Note**: Compliance is a holistic organizational responsibility. This software provides technical controls but does not guarantee compliance on its own.

## Contact

For security-related questions or to report vulnerabilities, please contact the repository maintainer through GitHub.

---

**Last Updated**: 2026-02-11  
**Version**: 2.0.0
