# MCP Vulnerability Service - Modal Deployment Guide

## Overview
This service provides vulnerability intelligence tools through the MCP (Model Context Protocol) framework, deployed on Modal Labs.

## Service Details
- **App Name**: mcp-vuln-auth
- **Environment**: vuln-ti-prod
- **Custom Domain**: mcp-vuln-auth.transilienceapi.com
- **Endpoint Path**: /vuln

## Features
The service provides the following MCP tools:

1. **get_cisa_known_exploited_vulnerabilities_filtered**: Get CISA KEV catalog filtered by date
2. **query_cve_info**: Query CVE information from Transilience API
3. **prioritize_vulnerabilities**: Prioritize vulnerabilities using Transilience API

## Prerequisites

### 1. Modal CLI Setup
```bash
pip install modal --upgrade
```

### 2. Modal Authentication
Set up your Modal profile with Transilience credentials:

```bash
# Create or update ~/.modal.toml
cat > ~/.modal.toml << 'EOF'
[transilience]
token_id = "ak-peP4ismMlNg4UcMcXWXTUJ"
token_secret = "as-qPNlLsEHYuX6OLWfzcp0Q1"
active = true
EOF

# Activate the profile
modal profile activate transilience
```

### 3. Modal Secrets Configuration
Ensure the following secrets exist in your Modal workspace under the **vuln-ti-prod** environment:

- `tr_aws_secret`: Transilience AWS credentials
- `llm-secrets`: LLM API keys (OpenAI, Anthropic, Google)
- `my-aws-secret`: AWS credentials
- `app_keys`: Application-specific keys including `vuln_api_key`

To create/update secrets:
```bash
modal secret create tr_aws_secret \
  AWS_ACCESS_KEY_ID="..." \
  AWS_SECRET_ACCESS_KEY="..." \
  --env vuln-ti-prod

modal secret create app_keys \
  vuln_api_key="..." \
  --env vuln-ti-prod
```

## Deployment

### Option 1: Using the Deployment Script
```bash
cd /home/user/codeagents/apps/vulnerabilities/src/backend/mcp
chmod +x deploy_to_modal.sh
./deploy_to_modal.sh
```

### Option 2: Manual Deployment
```bash
cd /home/user/codeagents/apps/vulnerabilities/src/backend/mcp
modal deploy modal_mcp_auth_vuln.py
```

## Configuration Changes

### Environment Update
The application has been configured for the **vuln-ti-prod** environment:

```python
# Modal secrets now reference vuln-ti-prod
tr_aws_secrets = [modal.Secret.from_name("tr_aws_secret", environment_name="vuln-ti-prod")]
llm_secrets = [modal.Secret.from_name("llm-secrets", environment_name="vuln-ti-prod")]
aws_secrets = [modal.Secret.from_name("my-aws-secret", environment_name="vuln-ti-prod")]
app_secrets = [modal.Secret.from_name("app_keys", environment_name="vuln-ti-prod")]
```

### Removed Local Directory Mount
Removed hardcoded local directory dependency for better portability.

## Testing the Deployment

### 1. Health Check
```bash
curl -H "Authorization: Bearer changeme" \
  https://mcp-vuln-auth.transilienceapi.com/vuln
```

### 2. Test CISA KEV Tool
```bash
curl -X POST \
  -H "Authorization: Bearer changeme" \
  -H "Content-Type: application/json" \
  -d '{"method": "get_cisa_known_exploited_vulnerabilities_filtered", "params": {"days_ago": 7}}' \
  https://mcp-vuln-auth.transilienceapi.com/vuln
```

### 3. Test CVE Query
```bash
curl -X POST \
  -H "Authorization: Bearer changeme" \
  -H "Content-Type: application/json" \
  -d '{"method": "query_cve_info", "params": {"cve_id": "CVE-2023-12345"}}' \
  https://mcp-vuln-auth.transilienceapi.com/vuln
```

## Authentication
The service uses Bearer token authentication. Update the `EXPECTED_TOKEN` in the code if needed:

```python
EXPECTED_TOKEN = "changeme"  # Change this to your secure token
```

## Monitoring

### View Logs
```bash
modal app logs mcp-vuln-auth
```

### List Apps
```bash
modal app list
```

### App Details
```bash
modal app show mcp-vuln-auth
```

## Troubleshooting

### DNS Resolution Issues
If you encounter "Temporary failure in name resolution" errors:
- Ensure you're in an environment with proper network access
- Check that api.modal.com is reachable
- Verify your DNS settings

### Authentication Errors
- Verify your Modal credentials in ~/.modal.toml
- Check that the transilience profile is active: `modal profile list`
- Ensure your token has not expired

### Secret Not Found
- Verify secrets exist: `modal secret list --env vuln-ti-prod`
- Check secret names match exactly
- Ensure you have access to the vuln-ti-prod environment

## Architecture

### Image Build
The Modal image includes:
- Debian Slim base
- Python packages: httpx, requests, uvicorn, fastapi, pandas, geocoder, atlassian-python-api, boto3, Pillow, websockets, google-genai, openai, anthropic
- FastMCP framework
- PyPDF2

### Deployment Configuration
- Min containers: 1 (always warm)
- Custom domain: mcp-vuln-auth.transilienceapi.com
- ASGI app with FastAPI
- Authentication middleware for Bearer token validation

## Support
For issues or questions, contact the Transilience team or check the Modal documentation at https://modal.com/docs
