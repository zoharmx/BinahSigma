# Binah-Σ Security Checklist

## 🔴 CRITICAL (Must Do Before Production)

### Environment Variables
- [ ] **Change JWT_SECRET_KEY** - Generate new strong secret
  ```bash
  python -c "import secrets; print(secrets.token_urlsafe(32))"
  ```
- [ ] **Set INIT_DEMO_KEYS=false** - Disable auto-generation of demo keys
- [ ] **Verify all API keys** are in environment variables, NOT hardcoded
- [ ] **Add .env to .gitignore** - Never commit secrets to git
- [ ] **Use different secrets** for dev/staging/production

### API Keys & Authentication
- [ ] **Rotate all API keys** from what was used in development
- [ ] **Generate production API keys** separately from demo keys
- [ ] **Implement key expiration** (currently set to 365 days)
- [ ] **Set up API key management** system for customers
- [ ] **Monitor for leaked keys** using GitHub secret scanning

### Network Security
- [ ] **Restrict CORS origins** - Change from `allow_origins=["*"]` to specific domains
  ```python
  allow_origins=[
      "https://yourdomain.com",
      "https://app.yourdomain.com"
  ]
  ```
- [ ] **Enable HTTPS only** - Redirect HTTP to HTTPS
- [ ] **Set security headers**:
  - X-Content-Type-Options: nosniff
  - X-Frame-Options: DENY
  - X-XSS-Protection: 1; mode=block
  - Strict-Transport-Security: max-age=31536000

### Rate Limiting
- [ ] **Implement Redis** for production rate limiting (currently in-memory)
- [ ] **Set appropriate limits** for each tier
- [ ] **Add IP-based rate limiting** for unauthenticated endpoints
- [ ] **Monitor for abuse** patterns

---

## 🟡 IMPORTANT (Should Do)

### Logging & Monitoring
- [ ] **Set up error tracking** (Sentry, Rollbar)
- [ ] **Configure structured logging** to external service
- [ ] **Set up uptime monitoring** (UptimeRobot, Pingdom)
- [ ] **Enable performance monitoring** (New Relic, DataDog)
- [ ] **Create alerting rules** for critical errors

### Data Protection
- [ ] **Don't log sensitive data** (API keys, tokens, PII)
- [ ] **Implement request sanitization** before logging
- [ ] **Set up data retention policies**
- [ ] **Encrypt data at rest** if storing sensitive info
- [ ] **Review GDPR compliance** if serving EU users

### Database (Future)
- [ ] **Use PostgreSQL** instead of in-memory storage
- [ ] **Enable SSL** for database connections
- [ ] **Implement backups** (automated daily)
- [ ] **Encrypt sensitive columns** (API keys, user data)
- [ ] **Use connection pooling** (pgbouncer)

### Container Security
- [ ] **Run as non-root user** ✅ (Already done in Dockerfile)
- [ ] **Scan images for vulnerabilities** (Trivy, Snyk)
- [ ] **Use minimal base images** (alpine, slim)
- [ ] **Keep dependencies updated**
- [ ] **Use multi-stage builds** to reduce image size

---

## 🟢 RECOMMENDED (Nice to Have)

### Advanced Security
- [ ] **Implement API versioning** ✅ (Already have v1/v2)
- [ ] **Add request signing** for enterprise clients
- [ ] **Implement OAuth2** for third-party integrations
- [ ] **Add IP whitelisting** for enterprise tier
- [ ] **Set up WAF** (Web Application Firewall)

### Compliance
- [ ] **Create privacy policy** for data collection
- [ ] **Implement audit logging** for all actions
- [ ] **Add GDPR data export** functionality
- [ ] **Create incident response plan**
- [ ] **Regular security audits** (quarterly)

### Infrastructure
- [ ] **Use CDN** for frontend assets
- [ ] **Implement load balancing**
- [ ] **Set up auto-scaling**
- [ ] **Create disaster recovery plan**
- [ ] **Multi-region deployment**

### Development
- [ ] **Enable dependabot** for dependency updates
- [ ] **Set up CI/CD security scanning**
- [ ] **Code review required** for all changes
- [ ] **Signed commits** from all developers
- [ ] **Security training** for team

---

## 🛠️ Quick Security Fixes

### 1. Update CORS (main_v2.py)

```python
# Before (Development)
allow_origins=["*"]

# After (Production)
allow_origins=[
    "https://yourdomain.com",
    os.getenv("FRONTEND_URL", "")
]
```

### 2. Add Security Headers

Add to `main_v2.py`:

```python
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.sessions import SessionMiddleware

# Add after CORSMiddleware
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["yourdomain.com", "*.yourdomain.com"])

@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response
```

### 3. Sanitize Logging

Update `engine_v2.py`:

```python
# Before
logger.info(f"Request: {data}")

# After
logger.info(f"Request from customer: {customer_id}")  # Don't log full data
```

### 4. Implement Redis Rate Limiting

```python
# Install redis
pip install redis

# Update rate_limiter.py
import redis
redis_client = redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379"))
```

---

## 🔍 Security Audit Commands

### Check for hardcoded secrets
```bash
# Search for potential secrets
grep -r "api_key\|secret\|password" backend/ --exclude-dir=venv

# Use truffleHog
pip install truffleHog
trufflehog filesystem backend/
```

### Scan dependencies
```bash
# Check for known vulnerabilities
pip install safety
safety check -r backend/requirements.txt

# Audit with pip-audit
pip install pip-audit
pip-audit -r backend/requirements.txt
```

### Container scanning
```bash
# Scan Docker image
docker scan binah-sigma:latest

# Or use Trivy
trivy image binah-sigma:latest
```

---

## 📝 Pre-Deployment Checklist

Run this before every production deployment:

```bash
# 1. Check no secrets in code
git secrets --scan

# 2. Verify .env not in git
git ls-files | grep .env

# 3. Run tests
pytest backend/

# 4. Check dependencies
safety check

# 5. Build and test locally
docker build -t binah-sigma:test backend/
docker run --rm binah-sigma:test python -m pytest

# 6. Verify environment variables set
# (Manually check in your platform dashboard)
```

---

## 🚨 Incident Response

If you suspect a security breach:

### Immediate Actions
1. **Rotate all secrets** (JWT_SECRET_KEY, API keys)
2. **Revoke all issued API keys**
3. **Check logs** for suspicious activity
4. **Notify affected users** (if applicable)
5. **Document incident** for post-mortem

### Investigation
1. Review access logs
2. Check for unauthorized API calls
3. Audit database changes
4. Examine error logs
5. Review rate limit violations

### Prevention
1. Implement additional monitoring
2. Tighten rate limits
3. Add IP-based restrictions
4. Require re-authentication
5. Conduct security audit

---

## 📞 Security Contact

Set up a security email: security@yourdomain.com

Add to README:
```
## Security

If you discover a security vulnerability, please email security@yourdomain.com
instead of using the issue tracker.
```

---

## ✅ Production Readiness Score

Calculate your score:

- Critical items: 5 points each
- Important items: 2 points each
- Recommended items: 1 point each

**Minimum to deploy**: 40 points (all critical + most important)
**Production ready**: 60+ points
**Enterprise ready**: 80+ points

---

**Current Status**: Review this checklist before deployment! 🔒
