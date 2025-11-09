#!/bin/bash
# Deployment script for MCP Vulnerability Service to Modal Labs
# Environment: vuln-ti-prod

set -e

echo "=== Modal MCP Vulnerability Service Deployment ==="
echo "Environment: vuln-ti-prod"
echo "App: mcp-vuln-auth"
echo ""

# Check if modal is installed
if ! command -v modal &> /dev/null; then
    echo "Error: modal CLI not found. Installing..."
    pip install modal --upgrade
fi

# Check Modal authentication
echo "Checking Modal authentication..."
if ! modal profile list &> /dev/null; then
    echo "Error: Not authenticated with Modal. Please run:"
    echo "  modal profile create transilience"
    echo "  # Then enter your Modal credentials"
    exit 1
fi

# Ensure we're using the transilience profile
echo "Activating transilience profile..."
modal profile activate transilience || true

# Deploy the application
echo ""
echo "Deploying mcp-vuln-auth to Modal..."
echo "This will:"
echo "  - Build Docker image with all dependencies"
echo "  - Configure secrets from vuln-ti-prod environment"
echo "  - Deploy to custom domain: mcp-vuln-auth.transilienceapi.com"
echo ""

modal deploy modal_mcp_auth_vuln.py

echo ""
echo "=== Deployment Complete ==="
echo "Service URL: https://mcp-vuln-auth.transilienceapi.com/vuln"
echo ""
echo "Test the deployment:"
echo '  curl -H "Authorization: Bearer changeme" https://mcp-vuln-auth.transilienceapi.com/vuln'
