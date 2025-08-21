# Coffee Shop WhatsApp Bot

A complete WhatsApp business intelligence system for coffee shops that integrates with Clover POS, uses AI for natural language processing, and provides real-time sales analytics through WhatsApp messages.

## 🚀 Features

- **WhatsApp Integration**: Receive and respond to customer questions via WhatsApp Business API
- **Clover POS Integration**: Real-time access to sales data, orders, and inventory
- **AI-Powered Responses**: Natural language processing using OpenAI GPT for intelligent responses
- **Sales Analytics**: Automated analysis of best-selling items, revenue trends, and performance metrics
- **Data Caching**: PostgreSQL-based caching for fast response times
- **Multi-Environment Support**: Works with sandbox and production APIs
- **Robust Error Handling**: Graceful fallbacks when services are unavailable
- **Easy Deployment**: One-click Heroku deployment with comprehensive documentation

## 📱 How It Works

```
[ Coffee Shop Owner ]
       |
       | Sends WhatsApp message: "What's my best-selling drink this week?"
       v
[ WhatsApp Business API (Twilio) ]
       |
       | Forwards message via webhook
       v
[ Flask Server (Heroku) ]
       | 1. Receives message
       | 2. Extracts question
       | 3. Queries Clover API for sales data (if not cached)
       | 4. Sends question + data to LLM
       v
[ Clover API ] <--> [ PostgreSQL (Cache) ]
       | Provides sales data (e.g., orders)
       v
[ LLM (OpenAI GPT) ]
       | Processes question and data
       | Generates response: "Your best-selling drink is the cappuccino (150 sold)."
       v
[ Flask Server ]
       | Sends response back to Twilio
       v
[ WhatsApp Business API (Twilio) ]
       | Delivers response to user
       v
[ Coffee Shop Owner ]
       | Receives WhatsApp message: "Your best-selling drink is the cappuccino (150 sold)."
```

## 🛠️ Technology Stack

- **Backend**: Python Flask
- **Database**: PostgreSQL
- **WhatsApp**: Twilio WhatsApp Business API
- **POS Integration**: Clover API
- **AI/LLM**: OpenAI GPT-4.1-mini
- **Deployment**: Heroku
- **Caching**: SQLAlchemy with PostgreSQL
- **Authentication**: Twilio webhook validation

## 📋 Prerequisites

Before setting up the application, you'll need:

1. **Twilio Account** - For WhatsApp Business API
2. **Clover Developer Account** - For POS integration
3. **OpenAI API Key** - For AI responses (optional)
4. **Heroku Account** - For deployment
5. **PostgreSQL Database** - For data caching

## 🚀 Quick Start

### Option 1: One-Click Deploy (Recommended)

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/yourusername/coffee-shop-whatsapp-bot)

1. Click the deploy button above
2. Fill in the required environment variables
3. Click "Deploy app"
4. Configure your Twilio webhook (see setup guide)

### Option 2: Manual Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/coffee-shop-whatsapp-bot.git
   cd coffee-shop-whatsapp-bot
   ```

2. **Set up local environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API credentials
   ```

4. **Initialize database**
   ```bash
   python src/database_init.py --sample-data
   ```

5. **Run locally**
   ```bash
   python src/main.py
   ```

## ⚙️ Configuration

### Required Environment Variables

```bash
# Flask Configuration
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql://localhost/coffee_shop_bot

# Twilio WhatsApp
TWILIO_ACCOUNT_SID=your-twilio-account-sid
TWILIO_AUTH_TOKEN=your-twilio-auth-token
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886

# Clover POS
CLOVER_API_TOKEN=your-clover-api-token
CLOVER_MERCHANT_ID=your-merchant-id
CLOVER_BASE_URL=https://sandbox-api.clover.com

# OpenAI (Optional)
OPENAI_API_KEY=your-openai-api-key
OPENAI_MODEL=gpt-4.1-mini
```

See [ENVIRONMENT_VARIABLES.md](ENVIRONMENT_VARIABLES.md) for complete configuration details.

## 📖 Documentation

- **[Deployment Guide](DEPLOYMENT_GUIDE.md)** - Complete deployment instructions
- **[Environment Variables](ENVIRONMENT_VARIABLES.md)** - Configuration reference
- **[Troubleshooting](TROUBLESHOOTING.md)** - Common issues and solutions
- **[API Documentation](docs/API.md)** - REST API endpoints
- **[Architecture](docs/ARCHITECTURE.md)** - System design and components

## 🧪 Testing

### Run All Tests
```bash
# System integration tests
python test_system_integration.py

# Component-specific tests
python test_clover_integration.py
python test_whatsapp_integration.py
python test_llm_integration.py
```

### Test Individual Components
```bash
# Test Clover API connection
python -c "from src.services.clover_api import CloverAPIClient; print(len(CloverAPIClient().get_orders()))"

# Test WhatsApp client
python -c "from src.services.whatsapp_client import WhatsAppClient; print(WhatsAppClient().send_message('+1234567890', 'test'))"

# Test LLM integration
python -c "from src.services.llm_client import LLMClient; print(LLMClient().generate_response('test question'))"
```

## 💬 Example Conversations

**Sales Inquiry**
```
User: What's my best-selling drink this week?
Bot: Your best-selling drink is the Cappuccino with 150 units sold, generating $750.00 in revenue. Great choice for your menu! Let me know if you'd like insights on other items.
```

**Revenue Analysis**
```
User: Show me my revenue report
Bot: 💰 Revenue Report

Total Revenue: $1,970.00
Items Sold: 425
Average Price: $4.64

Top Revenue Generators:
☕ 1. Cappuccino: $750.00
☕ 2. Latte: $660.00
☕ 3. Espresso: $320.00
```

**Category-Specific Query**
```
User: How are my coffee sales doing?
Bot: Your coffee sales are performing excellently! Here's the breakdown:
- Espresso: 37 sold, generating $148.00 in revenue
- Cappuccino: 30 sold, generating $150.00 in revenue
- Latte: 28 sold, generating $154.00 in revenue

Your Latte has the highest revenue per unit. Consider promoting it more!
```

## 🏗️ Architecture

### Core Components

1. **Flask Web Server** (`src/main.py`)
   - Handles webhook requests from Twilio
   - Provides REST API endpoints
   - Manages application lifecycle

2. **Message Processor** (`src/services/message_processor.py`)
   - Processes incoming WhatsApp messages
   - Determines intent and extracts entities
   - Coordinates with other services

3. **Clover API Client** (`src/services/clover_api.py`)
   - Integrates with Clover POS system
   - Fetches orders, inventory, and sales data
   - Handles API authentication and rate limiting

4. **WhatsApp Client** (`src/services/whatsapp_client.py`)
   - Sends outbound WhatsApp messages
   - Formats business data for messaging
   - Validates phone numbers

5. **LLM Client** (`src/services/llm_client.py`)
   - Generates natural language responses
   - Processes sales data with AI
   - Provides fallback responses

6. **Sales Processor** (`src/services/sales_processor.py`)
   - Processes and caches sales data
   - Calculates analytics and trends
   - Manages data freshness

7. **Database Models** (`src/models/`)
   - Sales cache for performance
   - WhatsApp message history
   - User management

### Data Flow

1. **Incoming Message**: Twilio sends webhook to `/webhook/whatsapp`
2. **Message Processing**: Extract intent and entities from user message
3. **Data Retrieval**: Fetch relevant sales data from cache or Clover API
4. **AI Processing**: Generate natural language response using LLM
5. **Response Delivery**: Send formatted response back through Twilio
6. **Logging**: Store conversation history in database

## 🔧 Development

### Project Structure
```
coffee-shop-whatsapp-bot/
├── src/
│   ├── main.py                 # Flask application entry point
│   ├── config.py              # Configuration management
│   ├── database_init.py       # Database initialization
│   ├── models/                # Database models
│   │   ├── user.py
│   │   └── sales_cache.py
│   ├── routes/                # API routes
│   │   ├── webhook.py         # WhatsApp webhook handlers
│   │   └── api.py            # REST API endpoints
│   └── services/              # Business logic services
│       ├── clover_api.py
│       ├── whatsapp_client.py
│       ├── llm_client.py
│       ├── message_processor.py
│       └── sales_processor.py
├── tests/                     # Test files
├── docs/                      # Documentation
├── requirements.txt           # Python dependencies
├── Procfile                   # Heroku process definition
├── runtime.txt               # Python version
├── app.json                  # Heroku app configuration
└── README.md                 # This file
```

### Adding New Features

1. **New Message Types**: Extend `MessageProcessor.process_message()`
2. **Additional APIs**: Add new clients in `src/services/`
3. **Database Changes**: Create migrations in `src/models/`
4. **New Endpoints**: Add routes in `src/routes/`

### Code Style
- Follow PEP 8 Python style guide
- Use type hints where possible
- Add docstrings to all functions
- Include error handling and logging

## 🚀 Deployment

### Heroku (Recommended)
See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for complete instructions.

### Other Platforms
The application can be deployed to any platform that supports:
- Python 3.11+
- PostgreSQL database
- Environment variables
- HTTPS endpoints (for webhooks)

## 📊 Monitoring

### Application Health
- Health check endpoint: `/api/health`
- Component status: `/api/status`
- Metrics endpoint: `/api/metrics`

### Logging
- Structured logging with timestamps
- Error tracking and alerting
- Performance monitoring

### Database Monitoring
- Connection pool status
- Query performance
- Cache hit rates

## 🔒 Security

### API Security
- Twilio webhook signature validation
- Environment variable protection
- Input sanitization and validation

### Data Protection
- No sensitive data in logs
- Encrypted database connections
- API key rotation procedures

## 💰 Cost Estimation

### Monthly Costs (Estimated)
- **Heroku Basic Dyno**: $7/month
- **PostgreSQL Essential**: $9/month
- **Twilio WhatsApp**: ~$0.005 per message
- **OpenAI GPT-4.1-mini**: ~$0.0001 per 1K tokens

**Example for 1000 monthly interactions**: ~$23/month

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and add tests
4. Commit your changes: `git commit -am 'Add feature'`
5. Push to the branch: `git push origin feature-name`
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

### Getting Help
1. Check the [Troubleshooting Guide](TROUBLESHOOTING.md)
2. Review the [Documentation](docs/)
3. Search existing [Issues](https://github.com/yourusername/coffee-shop-whatsapp-bot/issues)
4. Create a new issue with detailed information

### Reporting Bugs
When reporting bugs, please include:
- Error messages and logs
- Steps to reproduce
- Environment details
- Expected vs actual behavior

## 🙏 Acknowledgments

- [Twilio](https://twilio.com) for WhatsApp Business API
- [Clover](https://clover.com) for POS integration
- [OpenAI](https://openai.com) for AI capabilities
- [Heroku](https://heroku.com) for hosting platform
- [Flask](https://flask.palletsprojects.com/) for web framework

## 🔄 Changelog

### v1.0.0 (2024-01-01)
- Initial release
- WhatsApp Business API integration
- Clover POS integration
- OpenAI LLM integration
- PostgreSQL caching
- Heroku deployment support
- Comprehensive documentation

---

**Built with ❤️ for coffee shop owners who want to leverage AI and automation to better understand their business.**

