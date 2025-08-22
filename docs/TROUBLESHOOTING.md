# Troubleshooting Guide

This guide helps you diagnose and fix common issues with the Coffee Shop WhatsApp Bot.

## Quick Diagnostics

### Health Check
First, verify the application is running:
```bash
curl https://your-app-name.herokuapp.com/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00Z",
  "version": "1.0.0"
}
```

### Component Status Check
```bash
heroku run python -c "
from src.main import app
from src.services.clover_api import CloverAPIClient
from src.services.whatsapp_client import WhatsAppClient
from src.services.llm_client import LLMClient

with app.app_context():
    print('🏪 Clover API:', 'Connected' if CloverAPIClient().get_orders() else 'Failed')
    print('📱 WhatsApp:', 'Connected' if WhatsAppClient().use_mock == False else 'Mock Mode')
    print('🤖 LLM:', 'Connected' if LLMClient().use_openai else 'Fallback Mode')
"
```

## Common Issues

### 1. Application Won't Start

#### Symptoms
- Heroku app crashes on startup
- Error H10 (App crashed)
- Cannot access any endpoints

#### Diagnosis
```bash
# Check application logs
heroku logs --tail

# Check dyno status
heroku ps

# Check recent releases
heroku releases
```

#### Common Causes & Solutions

**Missing Environment Variables**
```bash
# Check required variables
heroku config | grep -E "(SECRET_KEY|DATABASE_URL)"

# Set missing variables
heroku config:set SECRET_KEY=$(openssl rand -base64 32)
```

**Database Connection Issues**
```bash
# Test database connection
heroku run python -c "
from src.main import app
from src.models.user import db
with app.app_context():
    try:
        db.session.execute('SELECT 1')
        print('✅ Database connected')
    except Exception as e:
        print('❌ Database error:', e)
"
```

**Import Errors**
```bash
# Check for missing dependencies
heroku run pip list

# Reinstall requirements
git add requirements.txt
git commit -m "Update requirements"
git push heroku main
```

### 2. WhatsApp Messages Not Working

#### Symptoms
- Messages sent to WhatsApp number don't get responses
- Webhook endpoint returns errors
- Twilio shows delivery failures

#### Diagnosis
```bash
# Test webhook endpoint directly
curl -X POST https://your-app-name.herokuapp.com/webhook/whatsapp \
  -d "MessageSid=TEST123" \
  -d "From=whatsapp:+1234567890" \
  -d "To=whatsapp:+14155238886" \
  -d "Body=test message"
```

#### Common Causes & Solutions

**Incorrect Webhook URL**
1. Go to Twilio Console > Messaging > WhatsApp Sandbox
2. Verify webhook URL: `https://your-app-name.herokuapp.com/webhook/whatsapp`
3. Ensure HTTP method is POST

**Twilio Credentials Issues**
```bash
# Verify Twilio credentials
heroku config | grep TWILIO

# Test Twilio API access
heroku run python -c "
from twilio.rest import Client
import os
try:
    client = Client(os.environ['TWILIO_ACCOUNT_SID'], os.environ['TWILIO_AUTH_TOKEN'])
    account = client.api.account.fetch()
    print('✅ Twilio connected:', account.friendly_name)
except Exception as e:
    print('❌ Twilio error:', e)
"
```

**Webhook Validation Failures**
```bash
# Check webhook validation logs
heroku logs --tail | grep "Invalid Twilio request"

# Temporarily disable validation for testing
heroku config:set TWILIO_AUTH_TOKEN=""
# Remember to re-enable after testing
```

### 3. No Sales Data / Clover Issues

#### Symptoms
- Bot responds with "No sales data available"
- Sales queries return empty results
- Clover API errors in logs

#### Diagnosis
```bash
# Test Clover API connection
heroku run python -c "
from src.services.clover_api import CloverAPIClient
try:
    client = CloverAPIClient()
    orders = client.get_orders()
    print(f'✅ Clover connected: {len(orders)} orders')
except Exception as e:
    print('❌ Clover error:', e)
"
```

#### Common Causes & Solutions

**Invalid Clover Credentials**
```bash
# Check Clover configuration
heroku config | grep CLOVER

# Test API token manually
curl -H "Authorization: Bearer $CLOVER_API_TOKEN" \
  "$CLOVER_BASE_URL/v3/merchants/$CLOVER_MERCHANT_ID/orders?limit=1"
```

**Wrong Base URL**
```bash
# For sandbox testing
heroku config:set CLOVER_BASE_URL=https://sandbox-api.clover.com

# For production
heroku config:set CLOVER_BASE_URL=https://api.clover.com
```

**Insufficient API Permissions**
1. Go to Clover Developer Dashboard
2. Check your app's permissions
3. Ensure "Read Orders" and "Read Inventory" are enabled
4. Regenerate API token if needed

**No Recent Orders**
```bash
# Add sample data for testing
heroku run python src/database_init.py --sample-data

# Check cache status
heroku run python -c "
from src.services.sales_processor import SalesProcessor
processor = SalesProcessor()
print('Cache fresh:', processor.is_cache_fresh('TEST_MERCHANT_001'))
"
```

### 4. LLM/AI Responses Not Working

#### Symptoms
- Bot gives generic responses instead of AI-generated ones
- OpenAI API errors in logs
- Responses seem robotic or templated

#### Diagnosis
```bash
# Test LLM connection
heroku run python -c "
from src.services.llm_client import LLMClient
client = LLMClient()
print('LLM Mode:', 'OpenAI' if client.use_openai else 'Fallback')
if client.use_openai:
    try:
        response = client.generate_response('Test question')
        print('✅ LLM working:', response[:50] + '...')
    except Exception as e:
        print('❌ LLM error:', e)
"
```

#### Common Causes & Solutions

**Missing OpenAI API Key**
```bash
# Check OpenAI configuration
heroku config | grep OPENAI

# Set API key
heroku config:set OPENAI_API_KEY=your-api-key
```

**Invalid Model Name**
```bash
# Use supported model
heroku config:set OPENAI_MODEL=gpt-4.1-mini

# Check available models
curl -H "Authorization: Bearer $OPENAI_API_KEY" \
  "https://api.openai.com/v1/models" | grep "gpt-4"
```

**API Quota/Billing Issues**
1. Check OpenAI Dashboard for usage limits
2. Verify billing information is set up
3. Check for rate limiting errors in logs

**Fallback Mode (Expected Behavior)**
- App automatically falls back to rule-based responses if LLM fails
- This is normal behavior when OpenAI is not configured

### 5. Database Issues

#### Symptoms
- "Database connection failed" errors
- Data not persisting between requests
- Migration errors

#### Diagnosis
```bash
# Check database status
heroku pg:info

# Check database connection
heroku run python -c "
import os
print('Database URL:', os.environ.get('DATABASE_URL', 'Not set')[:50] + '...')
"

# Test database operations
heroku run python -c "
from src.main import app
from src.models.user import db
with app.app_context():
    db.session.execute('SELECT COUNT(*) FROM sales_cache')
    print('✅ Database accessible')
"
```

#### Common Causes & Solutions

**Database Not Provisioned**
```bash
# Add PostgreSQL addon
heroku addons:create heroku-postgresql:essential-0

# Check addon status
heroku addons
```

**Database Not Initialized**
```bash
# Initialize database
heroku run python src/database_init.py

# Check tables exist
heroku pg:psql -c "\dt"
```

**Connection Pool Issues**
```bash
# Check active connections
heroku pg:info

# If too many connections, restart app
heroku restart
```

### 6. Performance Issues

#### Symptoms
- Slow response times
- Timeout errors
- High memory usage

#### Diagnosis
```bash
# Check dyno metrics
heroku logs --tail | grep "memory\|response"

# Check response times
time curl https://your-app-name.herokuapp.com/api/health

# Monitor real-time metrics
heroku logs --tail
```

#### Common Causes & Solutions

**Insufficient Dyno Resources**
```bash
# Scale up dyno type
heroku ps:scale web=1:standard-1x

# Check current dyno type
heroku ps
```

**Database Performance**
```bash
# Check slow queries
heroku pg:outliers

# Upgrade database plan if needed
heroku addons:upgrade heroku-postgresql:standard-0
```

**Memory Leaks**
```bash
# Restart application
heroku restart

# Monitor memory usage
heroku logs --tail | grep "memory"
```

## Debugging Commands

### Application Logs
```bash
# Real-time logs
heroku logs --tail

# Recent logs
heroku logs --num=100

# Filter by component
heroku logs --tail | grep "ERROR\|WARNING"
```

### Database Debugging
```bash
# Connect to database
heroku pg:psql

# Check table contents
heroku pg:psql -c "SELECT COUNT(*) FROM sales_cache;"
heroku pg:psql -c "SELECT * FROM whatsapp_messages ORDER BY created_at DESC LIMIT 5;"

# Database size and stats
heroku pg:info
```

### Configuration Debugging
```bash
# List all config variables
heroku config

# Check specific variables
heroku config:get TWILIO_ACCOUNT_SID

# Test configuration
heroku run python -c "
from src.config import Config
import os
print('Environment variables loaded:')
for attr in dir(Config):
    if not attr.startswith('_'):
        value = getattr(Config, attr)
        if isinstance(value, str) and len(value) > 20:
            print(f'{attr}: {value[:20]}...')
        else:
            print(f'{attr}: {value}')
"
```

### Component Testing
```bash
# Test individual components
heroku run python test_clover_integration.py
heroku run python test_whatsapp_integration.py
heroku run python test_llm_integration.py

# Run full system test
heroku run python test_system_integration.py
```

## Error Codes Reference

### HTTP Status Codes
- **200**: Success
- **400**: Bad request (invalid input)
- **403**: Forbidden (webhook validation failed)
- **500**: Internal server error
- **503**: Service unavailable

### Twilio Error Codes
- **11200**: HTTP retrieval failure
- **11750**: TwiML response body too large
- **13224**: Webhook timeout
- **21211**: Invalid 'To' phone number

### Clover Error Codes
- **401**: Unauthorized (invalid API token)
- **403**: Forbidden (insufficient permissions)
- **404**: Not found (invalid merchant ID)
- **429**: Rate limit exceeded

### OpenAI Error Codes
- **401**: Invalid API key
- **429**: Rate limit exceeded
- **500**: OpenAI server error

## Getting Help

### Before Contacting Support
1. Check this troubleshooting guide
2. Review application logs: `heroku logs --tail`
3. Test individual components
4. Check API service status pages:
   - [Heroku Status](https://status.heroku.com/)
   - [Twilio Status](https://status.twilio.com/)
   - [OpenAI Status](https://status.openai.com/)

### Information to Include
When reporting issues, include:
1. Error messages from logs
2. Steps to reproduce the issue
3. Environment (production/staging)
4. Recent changes or deployments
5. Output from diagnostic commands

### Emergency Procedures

**Complete Service Outage**
```bash
# Quick restart
heroku restart

# Rollback to previous release
heroku releases
heroku rollback v123  # Replace with last working version
```

**Database Issues**
```bash
# Create database backup
heroku pg:backups:capture

# Reset database (DESTRUCTIVE)
heroku pg:reset DATABASE_URL
heroku run python src/database_init.py --sample-data
```

**Security Incident**
```bash
# Rotate all API keys immediately
heroku config:set TWILIO_AUTH_TOKEN=new-token
heroku config:set CLOVER_API_TOKEN=new-token
heroku config:set OPENAI_API_KEY=new-key
heroku config:set SECRET_KEY=$(openssl rand -base64 32)
```

This troubleshooting guide should help you resolve most common issues with the Coffee Shop WhatsApp Bot. Remember to always test changes in a staging environment before applying them to production.

