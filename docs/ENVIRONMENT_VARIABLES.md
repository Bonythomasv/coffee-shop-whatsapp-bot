# Environment Variables Configuration

This document describes all environment variables used by the Coffee Shop WhatsApp Bot.

## Required Variables

### Flask Configuration
| Variable | Description | Example | Required |
|----------|-------------|---------|----------|
| `SECRET_KEY` | Flask secret key for sessions | `your-secret-key-here` | ✅ |
| `FLASK_ENV` | Flask environment | `production` | ✅ |
| `DATABASE_URL` | PostgreSQL database URL | `postgresql://user:pass@host:port/db` | ✅ |

### Database Configuration
| Variable | Description | Example | Required |
|----------|-------------|---------|----------|
| `DATABASE_URL` | Full PostgreSQL connection string | `postgresql://...` | ✅ |

*Note: `DATABASE_URL` is automatically set by Heroku PostgreSQL addon*

## Optional Variables

### Twilio WhatsApp Configuration
| Variable | Description | Example | Required |
|----------|-------------|---------|----------|
| `TWILIO_ACCOUNT_SID` | Twilio Account SID | `ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx` | 🔶 |
| `TWILIO_AUTH_TOKEN` | Twilio Auth Token | `your-auth-token` | 🔶 |
| `TWILIO_WHATSAPP_NUMBER` | Twilio WhatsApp number | `whatsapp:+14155238886` | 🔶 |

*Note: Required for WhatsApp functionality. Without these, the app will run in mock mode.*

### Clover POS Configuration
| Variable | Description | Example | Required |
|----------|-------------|---------|----------|
| `CLOVER_API_TOKEN` | Clover API access token | `your-clover-token` | 🔶 |
| `CLOVER_MERCHANT_ID` | Clover merchant ID | `your-merchant-id` | 🔶 |
| `CLOVER_BASE_URL` | Clover API base URL | `https://api.clover.com` | ❌ |

*Note: Required for real POS data. Without these, the app will use mock sales data.*

### LLM Configuration
| Variable | Description | Example | Required |
|----------|-------------|---------|----------|
| `LLM_PROVIDER` | LLM service provider | `openai` | ❌ |
| `OPENAI_API_KEY` | OpenAI API key | `sk-...` | ❌ |
| `OPENAI_MODEL` | OpenAI model to use | `gpt-4.1-mini` | ❌ |
| `TOGETHER_API_KEY` | Together AI API key | `your-together-key` | ❌ |
| `XAI_API_KEY` | xAI API key | `your-xai-key` | ❌ |

*Note: Optional. Without LLM configuration, the app uses rule-based responses.*

## Setting Environment Variables

### Local Development (.env file)
Create a `.env` file in the project root:

```bash
# Flask Configuration
SECRET_KEY=your-local-secret-key
FLASK_ENV=development
DATABASE_URL=postgresql://localhost/coffee_shop_bot

# Twilio Configuration
TWILIO_ACCOUNT_SID=your-twilio-account-sid
TWILIO_AUTH_TOKEN=your-twilio-auth-token
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886

# Clover Configuration
CLOVER_API_TOKEN=your-clover-api-token
CLOVER_MERCHANT_ID=your-merchant-id
CLOVER_BASE_URL=https://sandbox-api.clover.com

# LLM Configuration
LLM_PROVIDER=openai
OPENAI_API_KEY=your-openai-api-key
OPENAI_MODEL=gpt-4.1-mini
```

### Heroku Deployment
Set variables using Heroku CLI:

```bash
# Required
heroku config:set SECRET_KEY=$(openssl rand -base64 32)
heroku config:set FLASK_ENV=production

# Twilio
heroku config:set TWILIO_ACCOUNT_SID=your-account-sid
heroku config:set TWILIO_AUTH_TOKEN=your-auth-token
heroku config:set TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886

# Clover
heroku config:set CLOVER_API_TOKEN=your-clover-token
heroku config:set CLOVER_MERCHANT_ID=your-merchant-id
heroku config:set CLOVER_BASE_URL=https://api.clover.com

# OpenAI
heroku config:set OPENAI_API_KEY=your-openai-key
heroku config:set OPENAI_MODEL=gpt-4.1-mini
```

### Heroku Dashboard
1. Go to your app dashboard on heroku.com
2. Click on "Settings" tab
3. Click "Reveal Config Vars"
4. Add each variable and its value

## Variable Details

### SECRET_KEY
- **Purpose**: Flask session security
- **Generation**: `openssl rand -base64 32`
- **Security**: Keep secret, never commit to version control

### TWILIO_ACCOUNT_SID
- **Location**: Twilio Console > Account Info
- **Format**: Starts with "AC"
- **Example**: `ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

### TWILIO_AUTH_TOKEN
- **Location**: Twilio Console > Account Info
- **Security**: Keep secret, regenerate if compromised
- **Note**: Used for webhook validation

### TWILIO_WHATSAPP_NUMBER
- **Format**: `whatsapp:+1234567890`
- **Sandbox**: `whatsapp:+14155238886`
- **Production**: Your approved WhatsApp Business number

### CLOVER_API_TOKEN
- **Location**: Clover Developer Dashboard > Your App > API Tokens
- **Permissions**: Needs read access to orders and inventory
- **Environment**: Different tokens for sandbox vs production

### CLOVER_MERCHANT_ID
- **Location**: Clover Dashboard or API response
- **Format**: Alphanumeric string
- **Note**: Identifies the specific merchant/store

### CLOVER_BASE_URL
- **Sandbox**: `https://sandbox-api.clover.com`
- **Production**: `https://api.clover.com`
- **Default**: Sandbox if not specified

### OPENAI_API_KEY
- **Location**: OpenAI Dashboard > API Keys
- **Format**: Starts with "sk-"
- **Billing**: Ensure you have credits/billing set up

### OPENAI_MODEL
- **Supported**: `gpt-4.1-mini`, `gpt-4.1-nano`, `gemini-2.5-flash`
- **Recommended**: `gpt-4.1-mini` (good balance of cost/quality)
- **Default**: `gpt-4.1-mini`

## Environment-Specific Configurations

### Development
```bash
FLASK_ENV=development
CLOVER_BASE_URL=https://sandbox-api.clover.com
# Use sandbox/test credentials
```

### Staging
```bash
FLASK_ENV=production
CLOVER_BASE_URL=https://sandbox-api.clover.com
# Use sandbox credentials with production-like setup
```

### Production
```bash
FLASK_ENV=production
CLOVER_BASE_URL=https://api.clover.com
# Use production credentials
```

## Security Best Practices

### 1. Never Commit Secrets
- Add `.env` to `.gitignore`
- Use environment variables, not hardcoded values
- Rotate API keys regularly

### 2. Principle of Least Privilege
- Use API keys with minimal required permissions
- Create separate keys for different environments

### 3. Monitor Usage
- Set up billing alerts for paid APIs
- Monitor API usage patterns
- Log authentication failures

### 4. Backup Configuration
- Document all environment variables
- Keep secure backup of production configuration
- Test configuration changes in staging first

## Validation

The application validates environment variables on startup:

```python
# Check required variables
required_vars = ['SECRET_KEY', 'DATABASE_URL']
missing_vars = [var for var in required_vars if not os.environ.get(var)]
if missing_vars:
    raise ValueError(f"Missing required environment variables: {missing_vars}")

# Validate optional but important variables
if not os.environ.get('TWILIO_ACCOUNT_SID'):
    logger.warning("Twilio not configured - WhatsApp will run in mock mode")

if not os.environ.get('CLOVER_API_TOKEN'):
    logger.warning("Clover not configured - using mock sales data")

if not os.environ.get('OPENAI_API_KEY'):
    logger.warning("OpenAI not configured - using fallback responses")
```

## Troubleshooting

### Common Issues

#### 1. Invalid Database URL
```bash
# Check format
echo $DATABASE_URL
# Should be: postgresql://user:pass@host:port/database
```

#### 2. Twilio Authentication Errors
```bash
# Verify credentials
curl -X GET "https://api.twilio.com/2010-04-01/Accounts/$TWILIO_ACCOUNT_SID.json" \
  -u $TWILIO_ACCOUNT_SID:$TWILIO_AUTH_TOKEN
```

#### 3. Clover API Errors
```bash
# Test API access
curl -H "Authorization: Bearer $CLOVER_API_TOKEN" \
  "$CLOVER_BASE_URL/v3/merchants/$CLOVER_MERCHANT_ID/orders"
```

#### 4. OpenAI API Errors
```bash
# Test API key
curl -H "Authorization: Bearer $OPENAI_API_KEY" \
  "https://api.openai.com/v1/models"
```

### Debug Commands

```bash
# Check all environment variables
heroku config

# Test specific configuration
heroku run python -c "
from src.config import Config
print('Database:', bool(Config.DATABASE_URL))
print('Twilio:', bool(Config.TWILIO_ACCOUNT_SID))
print('Clover:', bool(Config.CLOVER_API_TOKEN))
print('OpenAI:', bool(Config.OPENAI_API_KEY))
"
```

This configuration ensures your Coffee Shop WhatsApp Bot has all the necessary credentials and settings to operate correctly in any environment.

