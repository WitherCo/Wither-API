# Deployment Guide for Wither API Gateway

This guide provides instructions for deploying the Wither API Gateway to various hosting platforms.

## Prerequisites

Before deploying, ensure you have:

1. A copy of the Wither API Gateway codebase
2. Python 3.9+ installed on your local machine
3. Access to your chosen hosting platform
4. Required API keys and secrets for any integrated services

## Environment Variables

Set up the following environment variables on your hosting platform:

- `SECRET_KEY`: A secure random string for session encryption
- `DATABASE_URL`: Connection string for your database
- `MAIL_SERVER`: SMTP server for sending emails (e.g., smtp.gmail.com)
- `MAIL_PORT`: SMTP port (typically 587 for TLS)
- `MAIL_USERNAME`: Email account username
- `MAIL_PASSWORD`: Email account password
- `MAIL_DEFAULT_SENDER`: Default sender email address
- `BOT_TOKEN`: Token for your bot integration (if applicable)
- `BOT_API_BASE_URL`: API base URL for your bot platform (if applicable)

## Deployment Options

### Option 1: Heroku Deployment

1. Install the Heroku CLI: https://devcenter.heroku.com/articles/heroku-cli
2. Login to Heroku: `heroku login`
3. Create a new Heroku app: `heroku create wither-api-gateway`
4. Add PostgreSQL add-on: `heroku addons:create heroku-postgresql:hobby-dev`
5. Set environment variables:
   ```
   heroku config:set SECRET_KEY=your_secret_key
   heroku config:set MAIL_SERVER=smtp.gmail.com
   heroku config:set MAIL_PORT=587
   # Add other required environment variables
   ```
6. Deploy the app:
   ```
   git push heroku main
   ```
7. Run migrations:
   ```
   heroku run python migrate.py
   ```

### Option 2: AWS Elastic Beanstalk

1. Install the EB CLI: `pip install awsebcli`
2. Initialize EB: `eb init -p python-3.8 wither-api-gateway`
3. Create an environment: `eb create wither-api-gateway-env`
4. Configure environment variables through the AWS Console
5. Deploy the app: `eb deploy`

### Option 3: Docker Deployment

1. Build the Docker image:
   ```
   docker build -t wither-api-gateway .
   ```
2. Run the container:
   ```
   docker run -d -p 5000:5000 \
     -e SECRET_KEY=your_secret_key \
     -e DATABASE_URL=your_database_url \
     # Add other required environment variables
     wither-api-gateway
   ```

## Setting Up a Production Database

For production environments, it's recommended to use a managed database service:

### PostgreSQL

1. Create a PostgreSQL database on your platform of choice (AWS RDS, Google Cloud SQL, etc.)
2. Update the `DATABASE_URL` environment variable with the connection string
3. Run migrations to create the database schema

### Database Migrations

To run database migrations on first deployment:

```bash
flask db upgrade
```

## Post-Deployment Verification

After deploying, verify that:

1. The API is accessible at your deployment URL
2. All API endpoints function correctly
3. Database connections are working
4. Email sending functionality works
5. Webhook endpoints are reachable

## Setting Up Monitoring

Consider setting up:

1. Application monitoring with New Relic or Datadog
2. Log aggregation with ELK stack or Papertrail
3. Error tracking with Sentry

## Support

For deployment support, contact the WitherCo team at support@witherco.xyz or open an issue on the GitHub repository.