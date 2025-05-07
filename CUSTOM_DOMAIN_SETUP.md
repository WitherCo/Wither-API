# Custom Domain Setup for witherco.xyz

This guide will help you set up your Wither API Gateway with the custom domain `witherco.xyz`. These instructions are applicable for any hosting platform you choose from the deployment guide.

## Prerequisites

Before setting up your custom domain, ensure you have:

1. Registered the domain `witherco.xyz` with a domain registrar (e.g., Namecheap, GoDaddy, Google Domains)
2. Access to your domain's DNS settings
3. A deployed instance of the Wither API Gateway (see DEPLOYMENT_GUIDE.md)
4. SSL certificate for secure HTTPS connections (or the ability to set up Let's Encrypt)

## Domain Setup Steps

### Step 1: Configure DNS Records

Access your domain registrar's DNS management console and set up the following records:

#### For Heroku:

```
Type  | Name  | Value                | TTL
------+-------+----------------------+-------
ALIAS | @     | your-app.herokuapp.com | 300
CNAME | www   | your-app.herokuapp.com | 300
CNAME | api   | your-app.herokuapp.com | 300
```

#### For AWS:

```
Type  | Name  | Value                           | TTL
------+-------+---------------------------------+-------
ALIAS | @     | your-eb-env.elasticbeanstalk.com | 300
CNAME | www   | your-eb-env.elasticbeanstalk.com | 300
CNAME | api   | your-eb-env.elasticbeanstalk.com | 300
```

#### For other hosting providers:

Create similar records pointing to your application's URL.

### Step 2: Configure Your Hosting Platform

#### For Heroku:

```bash
heroku domains:add witherco.xyz
heroku domains:add www.witherco.xyz
heroku domains:add api.witherco.xyz
```

Then follow the verification steps that Heroku provides.

#### For AWS Elastic Beanstalk:

1. Go to the AWS Management Console
2. Navigate to Route 53
3. Create a hosted zone for `witherco.xyz`
4. Add record sets to point to your Elastic Beanstalk environment

#### For other platforms:

Follow the platform-specific documentation for adding custom domains.

### Step 3: Set up SSL/TLS

#### With Let's Encrypt (recommended for most setups):

For Heroku:
```bash
# Install the Heroku SSL CLI plugin
heroku plugins:install heroku-certs

# Enable SSL on your app
heroku certs:auto:enable
```

For AWS:
1. Request a certificate through AWS Certificate Manager
2. Associate the certificate with your load balancer or CloudFront distribution

For other platforms:
Follow platform-specific instructions for Let's Encrypt integration.

#### With a paid SSL certificate:

1. Purchase an SSL certificate from a trusted provider
2. Install the certificate on your hosting platform following their documentation

### Step 4: Update API Configuration

Update your API configuration to recognize the custom domain:

1. Set the `BASE_URL` environment variable to your domain:
   ```
   BASE_URL=https://api.witherco.xyz
   ```

2. Update the `CORS_ORIGINS` setting if needed to allow requests from your domain:
   ```
   CORS_ORIGINS=https://witherco.xyz,https://www.witherco.xyz
   ```

### Step 5: Verify Setup

After completing the setup:

1. Visit `https://witherco.xyz` and ensure it loads properly
2. Check that `https://api.witherco.xyz` responds with your API
3. Verify that API requests work correctly with your custom domain
4. Confirm that SSL is working properly (green lock icon in browser)

## Subdomain Structure

Consider organizing your API using subdomains:

- `api.witherco.xyz` - Main API endpoints
- `docs.witherco.xyz` - API documentation
- `status.witherco.xyz` - Status page and metrics

## Maintenance

Periodically check:

1. SSL certificate expiration (renew before expiry)
2. DNS propagation and record accuracy
3. Domain registration renewal

## Troubleshooting

### Common Issues:

1. **DNS not resolving**:
   - Check DNS records and wait for propagation (can take up to 48 hours)
   - Verify record types and values

2. **SSL Certificate Issues**:
   - Ensure certificate covers all required domains (including www subdomain)
   - Check certificate installation on your platform

3. **CORS Issues**:
   - Update CORS settings to include your domain

For additional help, contact your hosting provider's support or domain registrar.