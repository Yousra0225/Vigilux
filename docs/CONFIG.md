# Configuration Guide - Vigilux

This document explains how to properly configure Vigilux for development and production environments.

## Quick Start

1. **Copy the environment template:**
   ```bash
   cp .env.example .env
   ```

2. **Generate a secure SECRET_KEY:**
   ```bash
   openssl rand -hex 32
   ```

3. **Edit `.env` and replace the placeholders with your actual values:**
   - `SECRET_KEY`: Use the generated key from step 2
   - `APIFY_API_TOKEN`: Get from https://apify.com
   - `GEMINI_API_KEY`: Get from https://ai.google.dev

4. **Start the services:**
   ```bash
   docker-compose up --build
   ```

---

## Required Configuration

### 1. SECRET_KEY (CRITICAL!)

**⚠️ This is the most important security setting!**

The `SECRET_KEY` is used to sign JWT tokens. Using a weak or default value compromises your entire authentication system.

**How to generate a secure key:**
```bash
openssl rand -hex 32
```

**Example output:**
```
09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7
```

Add this to your `.env` file:
```env
SECRET_KEY=09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7
```

**Important:**
- ✅ Generate a NEW key for each environment (dev, staging, prod)
- ✅ Keep it secret - never commit it to Git
- ✅ Rotate it periodically (every 6-12 months)
- ❌ NEVER use the default value in production

---

### 2. APIFY_API_TOKEN (Required for scraping)

Apify is used to scrape competitor data from Google Maps and websites.

**How to get:**
1. Create account at https://apify.com
2. Go to Settings > Integrations > API tokens
3. Generate a new token
4. Add to `.env`:
   ```env
   APIFY_API_TOKEN=apify_api_xxxxxxxxxxxxxxxxxxxxxxxx
   ```

**Pricing:**
- Free tier: $5 credit/month (~500 scrapes)
- Pay-as-you-go: $0.01 per scrape

---

### 3. GEMINI_API_KEY (Required for AI analysis)

Google Gemini is used to analyze competitor data and generate insights.

**How to get:**
1. Go to https://ai.google.dev/
2. Click "Get API Key" in Google AI Studio
3. Create or select a project
4. Generate API key
5. Add to `.env`:
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   ```

**Pricing:**
- Free tier: 60 requests/minute
- Paid tier: See https://ai.google.dev/pricing

---

## Optional Configuration (for notifications)

### 4. SENDGRID_API_KEY (Email notifications)

**How to get:**
1. Create account at https://sendgrid.com
2. Go to Settings > API Keys
3. Create API Key with "Mail Send" permission
4. Verify your sender email
5. Add to `.env`:
   ```env
   SENDGRID_API_KEY=SG.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   SENDGRID_FROM_EMAIL=noreply@yourdomain.com
   SENDGRID_FROM_NAME=Vigilux
   ```

**Pricing:**
- Free tier: 100 emails/day

---

### 5. TWILIO (SMS notifications - Ultimate plan only)

**How to get:**
1. Create account at https://twilio.com
2. Go to Console Dashboard
3. Copy Account SID and Auth Token
4. Buy a phone number
5. Add to `.env`:
   ```env
   TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   TWILIO_AUTH_TOKEN=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   TWILIO_PHONE_NUMBER=+1234567890
   ```

**Pricing:**
- Pay-as-you-go: ~$0.0075/SMS

---

### 6. SLACK_WEBHOOK_URL (Slack notifications)

**How to get:**
1. Go to https://api.slack.com/apps
2. Create New App > From scratch
3. Enable "Incoming Webhooks"
4. Add New Webhook to Workspace
5. Select channel and copy webhook URL
6. Add to `.env`:
   ```env
   SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR_WORKSPACE_ID/YOUR_CHANNEL_ID/YOUR_WEBHOOK_TOKEN
   ```

**Pricing:**
- Free

---

## Environment-Specific Configuration

### Development

```env
ENVIRONMENT=development
DEBUG=True
DATABASE_URL=postgresql://vigilux_user:vigilux_password@db:5432/vigilux
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Production

```env
ENVIRONMENT=production
DEBUG=False
DATABASE_URL=postgresql://user:pass@production-db.example.com:5432/vigilux
NEXT_PUBLIC_API_URL=https://api.yourdomain.com
```

**Production checklist:**
- [ ] Strong SECRET_KEY generated (not default!)
- [ ] DEBUG=False
- [ ] All API keys configured
- [ ] CORS origins set to production domain only
- [ ] SSL/HTTPS configured
- [ ] Database backups configured
- [ ] Monitoring enabled (Sentry)

---

## Security Best Practices

### 1. Never commit secrets to Git

✅ **Good:**
```bash
# .env is in .gitignore
echo "SECRET_KEY=..." > .env
```

❌ **Bad:**
```bash
# DON'T DO THIS!
git add .env
git commit -m "Add configuration"
```

### 2. Use different secrets per environment

```
Development:   SECRET_KEY=dev_key_abc123...
Staging:       SECRET_KEY=staging_key_xyz789...
Production:    SECRET_KEY=prod_key_qrs456...
```

### 3. Rotate secrets periodically

- SECRET_KEY: Every 6-12 months
- API tokens: Every 12 months or after team member departure
- Database passwords: Every 3-6 months

### 4. Use secrets manager in production

Instead of `.env` files, use:
- AWS Secrets Manager
- Azure Key Vault
- Google Secret Manager
- HashiCorp Vault

Example with AWS:
```python
import boto3

secrets = boto3.client('secretsmanager')
secret = secrets.get_secret_value(SecretId='vigilux/prod/secrets')
```

---

## Troubleshooting

### "SECRET_KEY must be set in production!"

**Solution:** Generate a strong SECRET_KEY and add it to `.env`
```bash
openssl rand -hex 32
```

### "APIFY_API_TOKEN is not configured"

**Solution:** Get an API token from https://apify.com and add to `.env`

### "GEMINI_API_KEY is not configured"

**Solution:** Get an API key from https://ai.google.dev/ and add to `.env`

### "Permission denied" when accessing .env

**Solution:** Fix file permissions
```bash
chmod 600 .env  # Owner read/write only
```

### "Can't find .env file"

**Solution:** Make sure .env is in the project root (same level as docker-compose.yml)
```bash
ls -la .env
# Should show: -rw------- .env
```

---

## Verification

Test that your configuration is loaded correctly:

```bash
# Start the backend container
docker-compose up api

# Check logs for warnings
docker-compose logs api | grep "SECRET_KEY"

# If you see "WARNING: Using default SECRET_KEY!", fix your .env file
```

---

## Reference

All available configuration options are documented in `.env.example`.

For questions, see the main [README.md](../README.md) or create an issue on GitHub.
