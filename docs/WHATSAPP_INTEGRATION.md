# WhatsApp Integration Guide

Complete guide for setting up WhatsApp Business API integration with Twilio, including local development with ngrok and production deployment.

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Twilio Setup](#twilio-setup)
4. [Local Development with ngrok](#local-development-with-ngrok)
5. [Production Deployment](#production-deployment)
6. [Testing WhatsApp Integration](#testing-whatsapp-integration)
7. [Troubleshooting](#troubleshooting)
8. [Advanced Configuration](#advanced-configuration)

## Overview

The Coffee Shop WhatsApp Bot uses Twilio's WhatsApp Business API to:
- Receive customer messages via webhook
- Send intelligent responses powered by AI (DeepSeek/OpenAI)
- Provide real-time sales analytics from Clover POS
- Handle business inquiries automatically

### Architecture Flow
```
[Customer WhatsApp] → [Twilio] → [ngrok/Production URL] → [Flask App] → [AI + Clover API] → [Response] → [Twilio] → [Customer WhatsApp]
```

## Prerequisites

Before starting, ensure you have:

- **Twilio Account** with WhatsApp Business API access
- **Coffee Shop Bot** running locally (`make run-dev`)
- **ngrok** installed for local development
- **Clover POS** account with API access
- **AI Provider** (DeepSeek or OpenAI) API key

## Twilio Setup

### Step 1: Create Twilio Account

1. Sign up at [twilio.com](https://www.twilio.com)
2. Verify your phone number
3. Navigate to Console Dashboard

### Step 2: Enable WhatsApp Sandbox

1. Go to **Messaging** → **Try it out** → **Send a WhatsApp message**
2. Follow instructions to join the WhatsApp Sandbox
3. Note your sandbox number (e.g., `+1 415 523 8886`)

### Step 3: Get Twilio Credentials

From your Twilio Console Dashboard, copy:
- **Account SID** (starts with `AC...`)
- **Auth Token** (click to reveal)

### Step 4: Configure Environment Variables

Add to your `.env` file:
```bash
# Twilio WhatsApp Configuration
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886
```

## Local Development with ngrok

### Step 1: Install ngrok

**macOS (Homebrew):**
```bash
brew install ngrok/ngrok/ngrok
```

**Manual Installation:**
1. Download from [ngrok.com/download](https://ngrok.com/download)
2. Unzip and move to `/usr/local/bin/`

### Step 2: Start Your Flask Application

```bash
cd coffee-shop-whatsapp-bot
make run-dev
```

Your app should be running on `http://localhost:5000`

### Step 3: Start ngrok Tunnel

In a **separate terminal**:
```bash
ngrok http 5000
```

You'll see output like:
```
Session Status                online
Account                       your-account (Plan: Free)
Version                       3.26.0
Region                        United States (us)
Latency                       45ms
Web Interface                 http://127.0.0.1:4040
Forwarding                    https://abc123.ngrok.io -> http://localhost:5000
Forwarding                    http://abc123.ngrok.io -> http://localhost:5000
```

**Important:** Copy the **HTTPS URL** (e.g., `https://abc123.ngrok.io`)

### Step 4: Configure Twilio Webhook

1. Go to Twilio Console → **Messaging** → **Settings** → **WhatsApp sandbox settings**
2. Set **Webhook URL for incoming messages** to:
   ```
   https://abc123.ngrok.io/webhook/whatsapp
   ```
3. Set **HTTP method** to `POST`
4. Click **Save configuration**

### Step 5: Test the Integration

1. Send a WhatsApp message to your Twilio sandbox number
2. Include the sandbox code (e.g., "join coffee-shop")
3. Send a test message: "What are my top items?"
4. You should receive an AI-powered response with sales data

## Production Deployment

### Heroku Deployment

1. **Deploy to Heroku:**
   ```bash
   git push heroku main
   ```

2. **Set environment variables:**
   ```bash
   heroku config:set TWILIO_ACCOUNT_SID=ACxxx...
   heroku config:set TWILIO_AUTH_TOKEN=your_token
   heroku config:set DEEPSEEK_API_KEY=your_deepseek_key
   # ... other variables
   ```

3. **Configure Twilio webhook:**
   - Use your Heroku app URL: `https://your-app.herokuapp.com/webhook/whatsapp`

### Other Platforms

For other deployment platforms, ensure:
- **HTTPS endpoint** (required for Twilio webhooks)
- **Environment variables** properly configured
- **Port configuration** matches your platform

## Testing WhatsApp Integration

### Manual Testing

Send these test messages to verify functionality:

**Basic Greeting:**
```
Hi there!
```
*Expected: Welcome message with help options*

**Sales Query:**
```
What are my top items?
```
*Expected: List of best-selling items with quantities and revenue*

**Business Recommendations:**
```
Give me business recommendations
```
*Expected: AI-powered business insights and suggestions*

**Revenue Analysis:**
```
Show me my revenue
```
*Expected: Revenue breakdown and analytics*

### Automated Testing with Postman

Use the included Postman collection:
```bash
# Import the collection
Coffee_Shop_WhatsApp_Bot_Tests.postman_collection.json
```

Set environment variables:
- `base_url`: Your ngrok or production URL
- Test various message scenarios

### Webhook Testing

Test webhook directly:
```bash
curl -X POST https://your-ngrok-url.ngrok.io/webhook/whatsapp \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "From=whatsapp:+1234567890&To=whatsapp:+14155238886&Body=What are my top items?&MessageSid=TEST_001"
```

## Troubleshooting

### Common Issues

**1. ngrok URL Changes**
- ngrok free tier generates new URLs on restart
- Update Twilio webhook URL when ngrok restarts
- Consider ngrok paid plan for static URLs

**2. Webhook Not Receiving Messages**
- Verify ngrok is running and accessible
- Check Twilio webhook configuration
- Ensure Flask app is running on correct port

**3. AI Responses Not Working**
- Verify AI provider API key in `.env`
- Check `LLM_PROVIDER` setting (should be `deepseek`)
- Review application logs for API errors

**4. No Sales Data**
- Verify Clover API credentials
- Check if sample data is loaded: `python src/database_init.py --sample-data`
- Confirm database connection

### Debug Commands

**Check ngrok status:**
```bash
curl http://localhost:4040/api/tunnels
```

**Test Flask app directly:**
```bash
curl http://localhost:5000/api/health
```

**View application logs:**
```bash
# Local development
tail -f logs/app.log

# Heroku
heroku logs --tail
```

### Webhook Validation Issues

If Twilio webhook validation fails:

1. **Check signature validation** in `src/routes/webhook.py`
2. **Verify Auth Token** matches Twilio console
3. **Ensure HTTPS** is used (ngrok provides this automatically)

## Advanced Configuration

### Custom WhatsApp Number

For production, apply for a dedicated WhatsApp Business number:

1. Go to Twilio Console → **Messaging** → **Senders** → **WhatsApp senders**
2. Click **Request Access** for WhatsApp Business API
3. Complete business verification process
4. Update `TWILIO_WHATSAPP_NUMBER` in environment variables

### Webhook Security

Enable webhook signature validation:

```python
# In src/routes/webhook.py
from twilio.request_validator import RequestValidator

def validate_twilio_request():
    validator = RequestValidator(Config.TWILIO_AUTH_TOKEN)
    return validator.validate(
        request.url,
        request.form,
        request.headers.get('X-Twilio-Signature', '')
    )
```

### Message Templates

For production WhatsApp Business API, create approved message templates:

1. Go to Twilio Console → **Messaging** → **Templates**
2. Create templates for common responses
3. Update message formatting in `src/services/whatsapp_client.py`

### Rate Limiting

Implement rate limiting for production:

```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

@app.route('/webhook/whatsapp', methods=['POST'])
@limiter.limit("10 per minute")
def whatsapp_webhook():
    # ... webhook logic
```

### Monitoring and Analytics

Track WhatsApp interactions:

```python
# Add to message processor
def log_interaction(phone_number, message, response):
    interaction = WhatsAppMessage(
        phone_number=phone_number,
        message_body=message,
        response_body=response,
        timestamp=datetime.utcnow()
    )
    db.session.add(interaction)
    db.session.commit()
```

## Environment Variables Reference

Complete WhatsApp-related environment variables:

```bash
# Required
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886

# Optional
TWILIO_WEBHOOK_VALIDATION=true
WHATSAPP_RATE_LIMIT=10
WHATSAPP_MESSAGE_TIMEOUT=30
```

## Support and Resources

### Documentation Links
- [Twilio WhatsApp API Docs](https://www.twilio.com/docs/whatsapp)
- [ngrok Documentation](https://ngrok.com/docs)
- [Flask Webhook Guide](https://flask.palletsprojects.com/)

### Getting Help
1. Check [Troubleshooting Guide](TROUBLESHOOTING.md)
2. Review Twilio Console logs
3. Test with Postman collection
4. Check application logs for errors

---

**Next Steps:**
1. Complete the setup following this guide
2. Test with sample messages
3. Deploy to production when ready
4. Apply for dedicated WhatsApp Business number
