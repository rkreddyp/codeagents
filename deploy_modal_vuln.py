#!/usr/bin/env python3
"""
Script to deploy modal_mcp_auth_vuln.py to Modal using the modal-deployer function
"""
import os
import modal

# Set Modal credentials
os.environ["MODAL_TOKEN_ID"] = "ak-peP4ismMlNg4UcMcXWXTUJ"
os.environ["MODAL_TOKEN_SECRET"] = "as-qPNlLsEHYuX6OLWfzcp0Q1"

def deploy_to_modal():
    """Deploy the vulnerability authentication service to Modal"""

    # Read the code to deploy
    code_file_path = "/home/user/codeagents/apps/vulnerabilities/src/backend/mcp/modal_mcp_auth_vuln.py"

    print(f"Reading code from: {code_file_path}")
    with open(code_file_path, 'r') as f:
        code_content = f.read()

    # Configuration
    environment_name = "vuln-ti-prod"
    base_filename = "modal_mcp_auth_vuln.py"

    print(f"\nDeployment Configuration:")
    print(f"  Environment: {environment_name}")
    print(f"  Filename: {base_filename}")
    print(f"  Code size: {len(code_content)} characters")

    # Get the deployer function from Modal
    print(f"\nConnecting to Modal deployer function...")
    func = modal.Function.from_name("modal-deployer", "deploy_code_to_modal", environment_name="admin")

    # Deploy the code
    print(f"\nDeploying code to Modal environment '{environment_name}'...")
    result = func.remote(
        code_content=code_content,
        environment_name=environment_name,
        filename=base_filename
    )

    print(f"\nDeployment Result:")
    print(result)

    return result

if __name__ == "__main__":
    try:
        result = deploy_to_modal()
        print("\n✅ Deployment completed successfully!")
    except Exception as e:
        print(f"\n❌ Deployment failed: {str(e)}")
        raise
