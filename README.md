# witherco.xyz API Gateway

A versatile API gateway that connects with external projects, domains, email services, and bots.

## Features

- **RESTful API**: Create and manage RESTful API endpoints for various integration types
- **Webhooks**: Support webhook receiving and dispatching for real-time integrations
- **Email Service**: Enable email sending/receiving capabilities with template support
- **Bot Integration**: Implement bot integration interfaces for chat platforms

## Tech Stack

- Python 3.11
- Flask (Web Framework)
- Flask-RESTful (API Framework)
- Flask-SQLAlchemy (Database ORM)
- Flask-CORS (Cross-Origin Resource Sharing)
- Gunicorn (WSGI Server)

## API Endpoints

The API Gateway provides several key endpoints:

- Health Check: `GET /api/health`
- API Keys: `GET/POST /api/keys`
- Webhooks: `GET/POST /api/webhooks`
- Email: `POST /api/email/send`
- Bot: `POST /api/bot/send-message`

Full documentation is available at [https://api.witherco.xyz/documentation](https://api.witherco.xyz/documentation)

## Development Setup

1. Clone the repository
   ```
   git clone https://github.com/yourusername/witherco-api-gateway.git
   cd witherco-api-gateway
   ```

2. Install dependencies
   ```
   pip install -r requirements.txt
   ```

3. Run the development server
   ```
   python main.py
   ```

## Deployment

For production deployment, the application uses Gunicorn:

```
gunicorn --bind 0.0.0.0:5000 --reuse-port --reload main:app
```

## License

Copyright 2025 WitherCo all rights reserved.

## Contact

For questions or support, please contact [lifelessrose@witherco.xyz](mailto:your@email.com).
