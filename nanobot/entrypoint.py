import json
import os
import sys

def resolve_config():
    # Load base config
    config_path = "/app/nanobot/config.json"
    with open(config_path, "r") as f:
        config = json.load(f)

    # Resolve environment variables for LLM provider
    llm_api_key = os.environ.get("LLM_API_KEY")
    llm_api_base_url = os.environ.get("LLM_API_BASE_URL")
    llm_api_model = os.environ.get("LLM_API_MODEL")

    # Update openrouter provider if using openrouter
    if config["agents"]["defaults"]["provider"] == "openrouter":
        if llm_api_key:
            config["providers"]["openrouter"]["apiKey"] = llm_api_key
        # Use openrouter default URL, not from env
        config["providers"]["openrouter"]["apiBase"] = "https://openrouter.ai/api/v1"
    else:
        # For custom provider
        if llm_api_key:
            config["providers"]["custom"]["apiKey"] = llm_api_key
        if llm_api_base_url:
            config["providers"]["custom"]["apiBase"] = llm_api_base_url

    # Update agent defaults with model from env
    if llm_api_model:
        config["agents"]["defaults"]["model"] = llm_api_model

    # Resolve gateway host/port
    gateway_host = os.environ.get("NANOBOT_GATEWAY_CONTAINER_ADDRESS")
    gateway_port = os.environ.get("NANOBOT_GATEWAY_CONTAINER_PORT")

    if gateway_host:
        config["gateway"]["host"] = gateway_host
    if gateway_port:
        config["gateway"]["port"] = int(gateway_port)

    # Resolve webchat channel settings
    webchat_host = os.environ.get("NANOBOT_WEBCHAT_CONTAINER_ADDRESS")
    webchat_port = os.environ.get("NANOBOT_WEBCHAT_CONTAINER_PORT")

    # Add webchat channel if not present
    if "webchat" not in config["channels"]:
        config["channels"]["webchat"] = {
            "enabled": True,
            "allowFrom": ["*"]
        }

    # Resolve MCP server environment variables
    backend_url = os.environ.get("NANOBOT_LMS_BACKEND_URL")
    backend_api_key = os.environ.get("NANOBOT_LMS_API_KEY")

    if backend_url:
        config["tools"]["mcpServers"]["lms"]["args"][2] = backend_url
    if backend_api_key:
        config["tools"]["mcpServers"]["lms"]["env"]["NANOBOT_LMS_API_KEY"] = backend_api_key

    # Write resolved config to temp location
    resolved_path = "/tmp/resolved_config.json"
    with open(resolved_path, "w") as f:
        json.dump(config, f, indent=2)

    return resolved_path

if __name__ == "__main__":
    resolved_config = resolve_config()
    workspace = "/app/nanobot/workspace"

    # Execute nanobot gateway with resolved config
    os.execvp("nanobot", ["nanobot", "gateway", "--config", resolved_config, "--workspace", workspace])
