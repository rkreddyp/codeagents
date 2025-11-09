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

app = modal.App(
    name="mcp-vuln-auth",
    image=image,
    secrets=all_secrets,
)

vuln_mcp = FastMCP(name="mcp-vuln")

from datetime import datetime, timedelta
import pandas as pd

@vuln_mcp.tool(description="CISA vulns filtered by days")
def get_cisa_known_exploited_vulnerabilities_filtered(days_ago: int = 10) -> dict:
    """Get CISA Known Exploited Vulnerabilities catalog filtered by dateAdded

    Args:
        days_ago: Number of days to look back from today (default: 10)
    """
    print(f"[debug-server] get_cisa_known_exploited_vulnerabilities_filtered(days_ago={days_ago})")

    url = "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json"

    try:
        response = requests.get(url)
        response.raise_for_status()

        data = response.json()

        # Convert vulnerabilities to DataFrame
        df = pd.DataFrame(data['vulnerabilities'])

        # Convert dateAdded to datetime
        df['dateAdded'] = pd.to_datetime(df['dateAdded'])

        # Calculate cutoff date
        cutoff_date = datetime.now() - timedelta(days=days_ago)

        # Filter for vulnerabilities added within the specified timeframe
        df_filtered = df[df['dateAdded'] >= cutoff_date]

        # Sort by dateAdded descending (most recent first)
        df_filtered = df_filtered.sort_values('dateAdded', ascending=False)

        # Convert back to dict format
        filtered_vulnerabilities = df_filtered.to_dict('records')

        return {
            "success": True,
            "data": {
                "catalogVersion": data.get('catalogVersion'),
                "dateReleased": data.get('dateReleased'),
                "count": len(filtered_vulnerabilities),
                "total_count": len(df),
                "days_filtered": days_ago,
                "cutoff_date": cutoff_date.strftime('%Y-%m-%d'),
                "vulnerabilities": filtered_vulnerabilities
            }
        }
    except requests.RequestException as e:
        return {
            "success": False,
            "error": f"Failed to fetch CISA KEV catalog: {str(e)}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Error processing data: {str(e)}"
        }

@vuln_mcp.tool(description="Get vulnerability advisories from Transilience Vulnerability API")
async def query_cve_info(cve_id: str) -> dict:
    """
    Query CVE information from the Transilience threat intel API.

    Args:
        cve_id: The CVE identifier (e.g., "CVE-2023-53616")

    Returns:
        dict: CVE information from the API
    """
    import aiohttp

    url = f"https://vulns.transilienceapi.com/cves/{cve_id}"
    api_key = os.environ["vuln_api_key"]

    try:
        async with aiohttp.ClientSession() as session:
            # Prepare headers with API key
            headers = {
                "x-api-key": api_key
            }

            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "success": True,
                        "cve_id": cve_id,
                        "data": data
                    }
                else:
                    error_text = await response.text()
                    return {
                        "success": False,
                        "cve_id": cve_id,
                        "error": f"HTTP {response.status}: {error_text}"
                    }

    except Exception as e:
        return {
            "success": False,
            "cve_id": cve_id,
            "error": str(e)
        }

@vuln_mcp.tool(description="Prioritize vulnerabilities")
def prioritize_vulnerabilities(cves: list[str] = None) -> dict:
    """
    Prioritize vulnerabilities with progress updates - Claude Desktop compatible
    Default CVEs: CVE-2016-1234, CVE-2017-5678, CVE-2018-9012
    """
    import sys
    import threading
    import queue
    from contextlib import redirect_stdout
    import io

    # Configuration
    api_key = os.environ["vuln_api_key"]
    base_url = "https://vulns.transilienceapi.com"
    max_wait_time = 300
    poll_interval = 5

    headers = {
        'Content-Type': 'application/json',
        'x-api-key': api_key
    }

    # Use provided CVEs or default test CVEs
    test_cves = ["CVE-2016-1234", "CVE-2017-5678", "CVE-2018-9012"]
    cves_to_process = cves if cves else test_cves

    # Progress tracking
    progress_updates = []

    def add_progress(stage, message, **kwargs):
        """Add progress update that will be returned to client"""
        update = {
            "stage": stage,
            "message": message,
            "timestamp": time.time(),
            **kwargs
        }
        progress_updates.append(update)
        print(f"[{stage.upper()}] {message}")  # Also log to server

    add_progress("initializing", f"🚀 Starting prioritization for {len(cves_to_process)} CVEs: {cves_to_process}")

    # Step 1: Submit CVEs for processing
    payload = {
        "schema_type": "simple_prioritization",
        "cves": cves_to_process
    }

    add_progress("submitting", f"📤 Submitting {len(cves_to_process)} CVEs to API...")

    try:
        response = requests.post(
            f"{base_url}/process/",
            headers=headers,
            json=payload
        )
        response.raise_for_status()

        job_data = response.json()
        process_id = job_data.get('process_id')

        if not process_id:
            add_progress("error", "❌ No process ID returned from API")
            return {
                "status": "error",
                "message": "No process ID returned from API",
                "progress": progress_updates
            }

        add_progress("submitted", f"✅ Job submitted successfully. Process ID: {process_id}", process_id=process_id)

    except requests.RequestException as e:
        add_progress("error", f"❌ Failed to submit job: {str(e)}")
        return {
            "status": "error",
            "message": f"Failed to submit job: {str(e)}",
            "progress": progress_updates
        }

    # Step 2: Poll for completion
    add_progress("polling_started", f"👀 Starting to monitor job progress (max {max_wait_time}s, poll every {poll_interval}s)")

    start_time = time.time()
    poll_count = 0
    last_status = None

    while time.time() - start_time < max_wait_time:
        poll_count += 1
        elapsed_total = time.time() - start_time
        remaining_time = max_wait_time - elapsed_total

        add_progress("polling", f"🔍 Poll #{poll_count} | Elapsed: {elapsed_total:.1f}s | Remaining: {remaining_time:.1f}s")

        try:
            status_response = requests.get(
                f"{base_url}/process/{process_id}",
                headers={'x-api-key': api_key}
            )

            if status_response.status_code == 200:
                status_data = status_response.json()
                status = status_data.get('status', 'unknown')
                elapsed_api = status_data.get('elapsed', 0)
                current_step = status_data.get('current_step')

                # Add status update
                if status != last_status or poll_count % 3 == 0:  # Update every 3rd poll or status change
                    add_progress("status_update",
                               f"📊 API Status: {status} | Step: {current_step or 'N/A'} | API Elapsed: {elapsed_api}s",
                               job_status=status,
                               api_elapsed=elapsed_api,
                               current_step=current_step)
                    last_status = status

                if status.lower() in ['success', 'completed', 'finished', 'done']:
                    add_progress("processing_complete", "🎉 Processing completed successfully!")
                    break
                elif status.lower() in ['failed', 'error']:
                    error_msg = status_data.get('error', 'Unknown error')
                    add_progress("error", f"❌ Job failed with status: {status}, error: {error_msg}")
                    return {
                        "status": "error",
                        "message": f"Job failed: {error_msg}",
                        "progress": progress_updates
                    }
            else:
                add_progress("warning", f"⚠️ Status check returned HTTP {status_response.status_code}")

        except requests.RequestException as e:
            add_progress("warning", f"⚠️ Status check failed: {str(e)}, will retry...")

        time.sleep(poll_interval)

    else:
        # Timeout occurred
        add_progress("timeout", f"⏰ Job did not complete within {max_wait_time} seconds")
        return {
            "status": "timeout",
            "message": f"Job timed out after {max_wait_time} seconds",
            "progress": progress_updates
        }

    # Step 3: Download results
    add_progress("downloading", "⬇️ Starting download of prioritization results...")

    try:
        download_response = requests.get(
            f"{base_url}/process/{process_id}/download",
            headers={'x-api-key': api_key},
            params={
                'data_type': 'prioritization',
                'prioritization_format': 'json'
            }
        )
        download_response.raise_for_status()

        add_progress("download_complete", f"✅ Downloaded {len(download_response.content)} bytes")

    except requests.RequestException as e:
        add_progress("error", f"❌ Failed to download results: {str(e)}")
        return {
            "status": "error",
            "message": f"Download failed: {str(e)}",
            "progress": progress_updates
        }

    # Step 4: Extract and parse results
    add_progress("extracting", "📦 Extracting JSON from zip file...")

    try:
        zip_buffer = io.BytesIO(download_response.content)

        with zipfile.ZipFile(zip_buffer, 'r') as zip_file:
            file_list = zip_file.namelist()
            add_progress("zip_extracted", f"📂 Found {len(file_list)} files in zip: {file_list}")

            json_files = [f for f in file_list if f.endswith('.json')]

            if not json_files:
                add_progress("error", "❌ No JSON file found in the downloaded zip")
                return {
                    "status": "error",
                    "message": "No JSON file found in zip",
                    "progress": progress_updates
                }

            json_filename = json_files[0]
            add_progress("parsing", f"🔍 Parsing JSON file: {json_filename}")

            with zip_file.open(json_filename) as json_file:
                json_content = json_file.read().decode('utf-8')
                prioritization_data = json.loads(json_content)

        result_count = len(prioritization_data) if isinstance(prioritization_data, list) else 1
        add_progress("success", f"🎊 Vulnerability prioritization completed successfully! Found {result_count} results")

        return {
            "status": "success",
            "message": "Vulnerability prioritization completed successfully!",
            "process_id": process_id,
            "cves_processed": cves_to_process,
            "result_count": result_count,
            "progress": progress_updates,
            "data": prioritization_data
        }

    except (zipfile.BadZipFile, json.JSONDecodeError, KeyError) as e:
        add_progress("error", f"❌ Failed to extract or parse results: {str(e)}")
        return {
            "status": "error",
            "message": f"Parse error: {str(e)}",
            "progress": progress_updates
        }


@app.function(image=image, min_containers=1)
@asgi_app(label="mcp-vuln-auth", custom_domains=["vulnmcp.transilienceapi.com"])
def vulnmcp_transilienceai() -> FastAPI:
    """Entrypoint for Modal to serve the FastAPI + MCP ASGI app."""
    # Get expected token from environment
    EXPECTED_TOKEN = "changeme"
    # Create MCP app first
    mcp_app = vuln_mcp.http_app(
        path="/mcp",
        stateless_http=True,
        json_response=True,
        transport="streamable-http"
    )

    # Pass MCP app's lifespan to FastAPI
    fast_api_app = FastAPI(
        title="mcp-vuln-auth",
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
    fast_api_app.mount("/vuln", mcp_app)

    return fast_api_app
