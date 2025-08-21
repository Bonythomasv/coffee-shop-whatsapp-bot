# Coffee Shop WhatsApp Bot - Deployment Guide

This guide will help you deploy the Coffee Shop WhatsApp Bot to production using Heroku.

## Prerequisites

Before deploying, ensure you have:

1. **Heroku Account**: Sign up at [heroku.com](https://heroku.com)
2. **Heroku CLI**: Install from [devcenter.heroku.com/articles/heroku-cli](https://devcenter.heroku.com/articles/heroku-cli)
3. **Git**: For version control and deployment
4. **Twilio Account**: For WhatsApp Business API
5. **Clover Developer Account**: For POS integration
6. **OpenAI API Key**: For LLM responses (optional but recommended)

## Step 1: Prepare Your Accounts

### Twilio Setup
1. Create a Twilio account at [twilio.com](https://twilio.com)
2. Get your Account SID and Auth Token from the Console
3. Set up WhatsApp Sandbox:
   - Go to Console > Messaging > Try it out > Send a WhatsApp message
   - Follow the instructions to join the sandbox
   - Note your sandbox WhatsApp number (e.g., `whatsapp:+14155238886`)

### Clover Setup
1. Create a Clover developer account at [clover.com/developers](https://clover.com/developers)
2. Create a new app in the developer dashboard
3. Get your API token and merchant ID
4. For production, you'll need to go through Clover's app approval process

### OpenAI Setup (Optional)
1. Create an OpenAI account at [openai.com](https://openai.com)
2. Generate an API key from the API section
3. Note: The app works without OpenAI but responses will be more basic

## Step 2: Deploy to Heroku

### Option A: One-Click Deploy (Recommended)
1. Click the "Deploy to Heroku" button:
   
   [![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/yourusername/coffee-shop-whatsapp-bot)

2. Fill in the required environment variables (see Step 3)
3. Click "Deploy app"

### Option B: Manual Deploy
1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/coffee-shop-whatsapp-bot.git
   cd coffee-shop-whatsapp-bot
   ```

2. Login to Heroku:
   ```bash
   heroku login
   ```

3. Create a new Heroku app:
   ```bash
   heroku create your-coffee-bot-name
   ```

4. Add PostgreSQL addon:
   ```bash
   heroku addons:create heroku-postgresql:essential-0
   ```

5. Set environment variables (see Step 3)

6. Deploy:
   ```bash
   git push heroku main
   ```

## Step 3: Environment Variables

Set these environment variables in your Heroku app:

### Required Variables
```bash
# Flask Configuration
SECRET_KEY=your-secret-key-here
FLASK_ENV=production

# Database (automatically set by Heroku PostgreSQL addon)
DATABASE_URL=postgresql://...
```

### Twilio Configuration (Required for WhatsApp)
```bash
TWILIO_ACCOUNT_SID=your-twilio-account-sid
TWILIO_AUTH_TOKEN=your-twilio-auth-token
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886
```

### Clover Configuration (Required for POS data)
```bash
CLOVER_API_TOKEN=your-clover-api-token
CLOVER_MERCHANT_ID=your-merchant-id
CLOVER_BASE_URL=https://api.clover.com  # or https://sandbox-api.clover.com for testing
```

### LLM Configuration (Optional)
```bash
LLM_PROVIDER=openai
OPENAI_API_KEY=your-openai-api-key
OPENAI_MODEL=gpt-4.1-mini
```

### Setting Variables via Heroku CLI
```bash
heroku config:set TWILIO_ACCOUNT_SID=your-account-sid
heroku config:set TWILIO_AUTH_TOKEN=your-auth-token
heroku config:set TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886
heroku config:set CLOVER_API_TOKEN=your-clover-token
heroku config:set CLOVER_MERCHANT_ID=your-merchant-id
heroku config:set OPENAI_API_KEY=your-openai-key
```

## Step 4: Configure Webhooks

### Twilio Webhook Configuration
1. Go to your Twilio Console
2. Navigate to Messaging > Settings > WhatsApp sandbox settings
3. Set the webhook URL to: `https://your-app-name.herokuapp.com/webhook/whatsapp`
4. Set the HTTP method to POST
5. Save the configuration

### Test the Webhook
Send a WhatsApp message to your Twilio sandbox number with the join code, then send:
```
What's my best-selling drink this week?
```

## Step 5: Initialize Database

The database will be automatically initialized on first deployment. To manually initialize:

```bash
heroku run python src/database_init.py
```

To add sample data for testing:
```bash
heroku run python src/database_init.py --sample-data
```

## Step 6: Verify Deployment

### Check Application Status
```bash
heroku ps:scale web=1
heroku logs --tail
```

### Test API Endpoints
```bash
# Health check
curl https://your-app-name.herokuapp.com/api/health

# Test sales data
curl https://your-app-name.herokuapp.com/api/sales/best-selling
```

### Test WhatsApp Integration
Send a test message to your WhatsApp sandbox number:
- "Hello" - Should get a greeting response
- "Help" - Should get help information
- "What's my best-selling drink?" - Should get sales data

## Step 7: Production Considerations

### Security
1. **Enable HTTPS**: Heroku provides HTTPS by default
2. **Webhook Validation**: The app validates Twilio webhook signatures
3. **Environment Variables**: Never commit API keys to version control
4. **Database Security**: Use Heroku PostgreSQL with SSL

### Monitoring
1. **Heroku Logs**: Monitor application logs
   ```bash
   heroku logs --tail
   ```

2. **Database Monitoring**: Check PostgreSQL metrics in Heroku dashboard

3. **Error Tracking**: Consider adding Sentry or similar service

### Scaling
1. **Dyno Scaling**: Scale web dynos based on usage
   ```bash
   heroku ps:scale web=2
   ```

2. **Database Scaling**: Upgrade PostgreSQL plan as needed

3. **Caching**: The app includes built-in caching for sales data

## Troubleshooting

### Common Issues

#### 1. App Not Starting
```bash
# Check logs
heroku logs --tail

# Common causes:
# - Missing environment variables
# - Database connection issues
# - Import errors
```

#### 2. WhatsApp Messages Not Working
- Verify Twilio webhook URL is correct
- Check Twilio credentials
- Ensure webhook endpoint is accessible
- Check Heroku logs for errors

#### 3. No Sales Data
- Verify Clover API credentials
- Check merchant ID is correct
- Ensure Clover API permissions are set
- Test with sample data: `heroku run python src/database_init.py --sample-data`

#### 4. LLM Responses Not Working
- Check OpenAI API key
- Verify API quota/billing
- App will fall back to rule-based responses if LLM fails

### Debug Commands
```bash
# Check environment variables
heroku config

# Run database initialization
heroku run python src/database_init.py

# Test Clover API connection
heroku run python -c "from src.services.clover_api import CloverAPIClient; print(CloverAPIClient().get_orders()[:1])"

# Test database connection
heroku run python -c "from src.main import app; from src.models.user import db; app.app_context().push(); print('DB connected:', db.session.execute('SELECT 1').scalar())"
```

## Maintenance

### Regular Tasks
1. **Monitor Logs**: Check for errors regularly
2. **Update Dependencies**: Keep packages updated
3. **Database Maintenance**: Monitor PostgreSQL usage
4. **API Limits**: Monitor Twilio, Clover, and OpenAI usage

### Updates
To deploy updates:
```bash
git add .
git commit -m "Update description"
git push heroku main
```

## Support

For issues:
1. Check the troubleshooting section above
2. Review Heroku logs: `heroku logs --tail`
3. Test individual components using the debug commands
4. Check API documentation for Twilio, Clover, and OpenAI

## Cost Estimation

### Heroku Costs
- **Basic Dyno**: $7/month
- **PostgreSQL Essential**: $9/month
- **Total Heroku**: ~$16/month

### API Costs (Usage-based)
- **Twilio WhatsApp**: ~$0.005 per message
- **OpenAI GPT-4.1-mini**: ~$0.0001 per 1K tokens
- **Clover API**: Free for approved apps

### Example Monthly Cost
For a coffee shop with 1000 WhatsApp interactions:
- Heroku: $16
- Twilio: $5 (1000 messages)
- OpenAI: $2 (estimated)
- **Total**: ~$23/month

This deployment guide should get your Coffee Shop WhatsApp Bot running in production. The system is designed to be robust and handle real-world usage with proper error handling and fallbacks.

