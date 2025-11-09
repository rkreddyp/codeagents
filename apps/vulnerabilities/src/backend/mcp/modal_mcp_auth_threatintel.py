import os
import contextlib
import modal
from modal import Image, App, asgi_app
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastmcp import FastMCP
import requests
import time
import io
import zipfile
import json
from fastapi.responses import StreamingResponse
import asyncio
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import io
import re
app = modal.App(name="mcp-threatintel-auth")

# Build the Modal image with all required dependencies
image = modal.Image.debian_slim().run_commands(
    "apt-get update",
    "pip install httpx requests uvicorn fastapi pandas geocoder atlassian-python-api boto3 Pillow websockets google-genai openai anthropic",
    "pip install fastmcp --upgrade",
    "pip install PyPDF2",
)

# Modal secrets
tr_aws_secrets = [modal.Secret.from_name("tr_aws_secret", environment_name="main")]
llm_secrets = [modal.Secret.from_name("llm-secrets", environment_name="main")]
aws_secrets = [modal.Secret.from_name("my-aws-secret", environment_name="main")]
app_secrets = [modal.Secret.from_name("app_keys", environment_name="main")]

all_secrets = tr_aws_secrets + llm_secrets + aws_secrets + app_secrets

threatintel_mcp = FastMCP(name="mcp-threatintel")

@threatintel_mcp.tool(description="apt news")
def apt_news(apt_id: str) -> str:
    """APT news"""
    print(f"[debug-server] apt_news({apt_id})")
    return f"The latest news on the {apt_id} APT is..."

@threatintel_mcp.tool(description="Get threat advisories from Transilience Threat Intel API")
def get_threats(query: str = "", limit: int = 50) -> str:
    """Get threat advisories. Returns threat reports with IOCs and advisories."""
    print(f"[debug-server] get_threats(query={query}, limit={limit})")

    api_key = os.environ["threatintel_api_key"]

    url = "https://transilience-threat-intel-api.transilienceapi.com/threats"
    headers = {"transilience_threatintel_api_key": api_key}
    params = {"query": query, "limit": limit}

    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        return json.dumps(response.json(), indent=2)
    else:
        return json.dumps({"error": f"Status {response.status_code}", "message": response.text})


@threatintel_mcp.tool(description="Get IOCs and advisory text for a specific threat report")
def get_threat_report_files(report_id: str) -> str:
    """
    Gets IOCs and advisory text for a specific threat report ID.
    Returns JSON containing the IOCs HTML content and advisory text content.
    """
    print(f"[debug-server] get_threat_report_files({report_id})")

    api_key = os.environ["threatintel_api_key"]
    headers = {"transilience_threatintel_api_key": api_key}

    result = {"iocs": None, "advisory": None}

    # Get IOC HTML
    ioc_url = f"https://transilience-threat-intel-api.transilienceapi.com/threats/{report_id}/iocs"
    ioc_response = requests.get(ioc_url, headers=headers)

    if ioc_response.status_code == 200:
        result["iocs"] = ioc_response.text
    else:
        result["iocs"] = f"Failed to get IOCs: Status {ioc_response.status_code}"

    # Get Advisory PDF and convert to text
    advisory_url = f"https://transilience-threat-intel-api.transilienceapi.com/threats/{report_id}/advisory"
    advisory_response = requests.get(advisory_url, headers=headers)

    if advisory_response.status_code == 200:
        import PyPDF2

        # Convert PDF bytes to text
        pdf_bytes = io.BytesIO(advisory_response.content)
        pdf_reader = PyPDF2.PdfReader(pdf_bytes)

        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()

        # Remove text between head tags
        # Remove img tags and their content using regex
        text = re.sub(r'<img.*?</img>', '', text, flags=re.DOTALL)
        result["advisory"] = text
        print("text --------:\n\n")
        print(len(text))
    else:
        result["advisory"] = f"Failed to get Advisory: Status {advisory_response.status_code}"

    print("result --------:\n\n")
    print(result.keys())
    print(result["advisory"])
    print(result["iocs"])
    return json.dumps(result)


@threatintel_mcp.tool(description="Get breach advisories from Transilience Threat Intel API")
def get_breaches(query: str = "", limit: int = 50) -> str:
    """Get breach advisories. Returns breach reports with IOCs and advisories."""
    print(f"[debug-server] get_breaches(query={query}, limit={limit})")

    api_key = os.environ["threatintel_api_key"]

    url = "https://transilience-threat-intel-api.transilienceapi.com/breaches"
    headers = {"transilience_threatintel_api_key": api_key}
    params = {"query": query, "limit": limit}

    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        return json.dumps(response.json(), indent=2)
    else:
        return json.dumps({"error": f"Status {response.status_code}", "message": response.text})


@threatintel_mcp.tool(description="Get product advisories from Transilience Threat Intel API")
def get_products(query: str = "", limit: int = 50) -> str:
    """Get product advisories. Returns product vulnerability reports with IOCs and advisories."""
    print(f"[debug-server] get_products(query={query}, limit={limit})")

    api_key = os.environ["threatintel_api_key"]

    url = "https://transilience-threat-intel-api.transilienceapi.com/products"
    headers = {"transilience_threatintel_api_key": api_key}
    params = {"query": query, "limit": limit}

    response = requests.get(url, headers=headers, params=params)
    print(response.json())
    if response.status_code == 200:
        return json.dumps(response.json(), indent=2)
    else:
        return json.dumps({"error": f"Status {response.status_code}", "message": response.text})


@threatintel_mcp.tool(description="get all threat intel news")
def get_all_threatintel_news() -> str:
    """Get all threat intel news"""
    print(f"[debug-server] get_all_threatintel_news()")
    import requests
    # Make request to get threat intel
    response = requests.post(
        "https://threatintel-internal.transilienceapi.com/get_threat_intel",
        json={"type": "threatintel"},
        headers={"Content-Type": "application/json"}
    )
    t_json = response.json()
    # Convert to DataFrame to filter and select specific columns
    import pandas as pd
    df = pd.DataFrame(t_json)

    # Define columns to keep (based on the provided column list)
    cols_to_keep = ['source', 'source_article_link', 'source_link',
                    'threat_information_available', 'threat_severity', 'threat_article_url',
                    'threat_article_title', 'date_published', 'author', 'company_targeted',
                    'threat_time_range', 'threat_name', 'primary_industry_af1cted',
                    'primary_threat_actor', 'threat_actor_group', 'threat_actor_ttps',
                    'exploited_tools_techniques', 'vulnerabilities_targeted',
                    'immediate_impact', 'industries_affected',
                    'regions_or_countries_targeted','software_exploited', 'product_exploited',
                    'software_version_exploited', 'cve_id', 'cve_ids', 'affected_products']

    # Filter to only include columns that exist in the DataFrame
    available_cols = [col for col in cols_to_keep if col in df.columns]
    df_filtered = df[available_cols]

    # Convert back to JSON format
    t_json_filtered = df_filtered.to_dict('records')
    print(t_json_filtered)
    return t_json_filtered

app = modal.App(
    name="mcp-threatintel-auth",
    image=image,
    secrets=all_secrets,
)

@app.function(image=image, min_containers=1)
@asgi_app(label="mcp-threatintel-auth", custom_domains=["threatintelmcp.transilienceapi.com"])
def threatintelmcp() -> FastAPI:
    """Entrypoint for Modal to serve the FastAPI + MCP ASGI app."""
    # Get expected token from environment
    EXPECTED_TOKEN = "changeme"
    # Create MCP app first
    mcp_app = threatintel_mcp.http_app(
        path="/mcp",
        stateless_http=True,
        json_response=True,
        transport="streamable-http"
    )

    # Pass MCP app's lifespan to FastAPI
    fast_api_app = FastAPI(
        title="mcp-streamable",
        lifespan=mcp_app.lifespan
    )

    # Add authentication middleware
    @fast_api_app.middleware("http")
    async def auth_middleware(request: Request, call_next):
        # Check Authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"error": "Missing Authorization header"}
            )

        # Validate Bearer token
        try:
            scheme, token = auth_header.split()
            if scheme.lower() != "bearer":
                raise ValueError("Invalid authentication scheme")
            if token != EXPECTED_TOKEN:
                raise ValueError("Invalid token")
        except (ValueError, AttributeError):
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"error": "Invalid Authorization header"}
            )

        # Token is valid, proceed
        response = await call_next(request)
        return response

    # Mount the MCP app
    fast_api_app.mount("/threatintel", mcp_app)

    return fast_api_app
