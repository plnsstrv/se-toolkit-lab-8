"""Stdio MCP server exposing VictoriaLogs and VictoriaTraces operations as typed tools."""

from __future__ import annotations

import asyncio
import json
import os
from collections.abc import Awaitable, Callable, Sequence
from typing import Any

import httpx
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool
from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

_victorialogs_url: str = ""
_victoriatraces_url: str = ""

server = Server("observability")

# ---------------------------------------------------------------------------
# Input models
# ---------------------------------------------------------------------------


class _NoArgs(BaseModel):
    """Empty input model for tools that only need server-side configuration."""


class _ServiceQuery(BaseModel):
    service: str = Field(
        default="Learning Management Service",
        description="Service name to query (default: Learning Management Service).",
    )


class _TimeRangeQuery(BaseModel):
    service: str = Field(
        default="Learning Management Service",
        description="Service name to query.",
    )
    hours: int = Field(
        default=1,
        ge=1,
        le=24,
        description="Hours to look back (default 1, max 24).",
    )


class _ErrorQuery(BaseModel):
    service: str = Field(
        default="Learning Management Service",
        description="Service name to query.",
    )
    hours: int = Field(
        default=1,
        ge=1,
        le=24,
        description="Hours to look back (default 1, max 24).",
    )
    limit: int = Field(
        default=10,
        ge=1,
        le=100,
        description="Maximum number of error logs to return.",
    )


class _TraceQuery(BaseModel):
    trace_id: str = Field(description="Trace ID to look up.")


class _ErrorTraceQuery(BaseModel):
    service: str = Field(
        default="Learning Management Service",
        description="Service name to query.",
    )
    hours: int = Field(
        default=1,
        ge=1,
        le=24,
        description="Hours to look back (default 1, max 24).",
    )
    limit: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Maximum number of traces to return.",
    )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _get_victorialogs_url() -> str:
    if not _victorialogs_url:
        raise RuntimeError(
            "VictoriaLogs URL not configured. Pass it as: python -m mcp_observability <victorialogs_url> <victoriatraces_url>"
        )
    return _victorialogs_url


def _get_victoriatraces_url() -> str:
    if not _victoriatraces_url:
        raise RuntimeError(
            "VictoriaTraces URL not configured. Pass it as: python -m mcp_observability <victorialogs_url> <victoriatraces_url>"
        )
    return _victoriatraces_url


def _text(data: BaseModel | Sequence[BaseModel] | dict | list) -> list[TextContent]:
    """Serialize data to a JSON text block."""
    if isinstance(data, BaseModel):
        payload = data.model_dump()
    elif isinstance(data, list):
        payload = [item.model_dump() if isinstance(item, BaseModel) else item for item in data]
    else:
        payload = data
    return [TextContent(type="text", text=json.dumps(payload, ensure_ascii=False, indent=2))]


async def _query_victorialogs(query: str, limit: int = 20) -> list[dict]:
    """Execute a LogsQL query against VictoriaLogs."""
    url = _get_victorialogs_url()
    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.post(
            f"{url}/select/logsql/query",
            data={"query": query, "limit": str(limit)},
        )
        r.raise_for_status()
        # VictoriaLogs returns newline-delimited JSON
        lines = r.text.strip().split("\n")
        results = []
        for line in lines:
            if line.strip():
                try:
                    results.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
        return results


async def _query_victoriatraces(endpoint: str, params: dict | None = None) -> dict:
    """Execute a query against VictoriaTraces."""
    url = _get_victoriatraces_url()
    async with httpx.AsyncClient(timeout=10.0) as client:
        full_url = f"{url}{endpoint}"
        r = await client.get(full_url, params=params or {})
        r.raise_for_status()
        return r.json()


# ---------------------------------------------------------------------------
# Tool handlers
# ---------------------------------------------------------------------------


async def _logs_errors(args: _ErrorQuery) -> list[TextContent]:
    """Query error logs from VictoriaLogs."""
    query = f'_stream:{{service.name="{args.service}"}} severity:ERROR'
    logs = await _query_victorialogs(query, limit=args.limit)
    if not logs:
        return [TextContent(type="text", text=f"No error logs found for {args.service}.")]

    result = []
    for log in logs:
        result.append({
            "time": log.get("_time", ""),
            "message": log.get("_msg", ""),
            "error": log.get("error", ""),
            "trace_id": log.get("trace_id", ""),
        })
    return _text(result)


async def _logs_recent(args: _TimeRangeQuery) -> list[TextContent]:
    """Query recent logs from VictoriaLogs."""
    query = f'_stream:{{service.name="{args.service}"}}'
    logs = await _query_victorialogs(query, limit=50)
    if not logs:
        return [TextContent(type="text", text=f"No logs found for {args.service}.")]

    result = []
    for log in logs[:20]:  # Limit to 20 most recent
        result.append({
            "time": log.get("_time", ""),
            "message": log.get("_msg", ""),
            "severity": log.get("severity", "INFO"),
            "event": log.get("event", ""),
        })
    return _text(result)


async def _traces_get(args: _TraceQuery) -> list[TextContent]:
    """Get a specific trace by ID from VictoriaTraces."""
    try:
        data = await _query_victoriatraces(f"/select/jaeger/api/traces/{args.trace_id}")
        return _text(data)
    except Exception as e:
        return [TextContent(type="text", text=f"Error fetching trace {args.trace_id}: {e}")]


async def _traces_errors(args: _ErrorTraceQuery) -> list[TextContent]:
    """Query traces with errors from VictoriaTraces."""
    try:
        # Get traces for the service
        data = await _query_victoriatraces(
            "/select/jaeger/api/traces",
            params={"service": args.service, "limit": str(args.limit * 5)},
        )

        # Filter traces that have error spans
        traces_with_errors = []
        traces_data = data.get("data", [])

        for trace in traces_data:
            spans = trace.get("spans", [])
            has_error = False
            error_spans = []

            for span in spans:
                # Check for error tag
                tags = span.get("tags", [])
                for tag in tags:
                    if tag.get("key") == "error" and tag.get("value") is True:
                        has_error = True
                        error_spans.append({
                            "operation": span.get("operationName", ""),
                            "duration": span.get("duration", 0),
                            "logs": span.get("logs", []),
                        })
                        break

            if has_error:
                trace_id = trace.get("traceID", "")
                # Get first 8 chars for short ID
                traces_with_errors.append({
                    "trace_id": trace_id,
                    "short_id": trace_id[:16] if len(trace_id) > 16 else trace_id,
                    "error_spans": error_spans,
                })

                if len(traces_with_errors) >= args.limit:
                    break

        if not traces_with_errors:
            return [TextContent(type="text", text=f"No error traces found for {args.service}.")]

        return _text(traces_with_errors)
    except Exception as e:
        return [TextContent(type="text", text=f"Error querying traces: {e}")]


async def _services_list(_args: _NoArgs) -> list[TextContent]:
    """List all services that have logged data."""
    try:
        # Get services from VictoriaTraces
        data = await _query_victoriatraces("/select/jaeger/api/services")
        services = data.get("data", [])
        return _text({"services": services})
    except Exception as e:
        return [TextContent(type="text", text=f"Error listing services: {e}")]


async def _health_check(_args: _NoArgs) -> list[TextContent]:
    """Check health of VictoriaLogs and VictoriaTraces."""
    results = {}

    # Check VictoriaLogs
    try:
        url = _get_victorialogs_url()
        async with httpx.AsyncClient(timeout=5.0) as client:
            r = await client.get(f"{url}/health")
            results["victorialogs"] = "healthy" if r.status_code == 200 else f"unhealthy: HTTP {r.status_code}"
    except Exception as e:
        results["victorialogs"] = f"unhealthy: {e}"

    # Check VictoriaTraces
    try:
        url = _get_victoriatraces_url()
        async with httpx.AsyncClient(timeout=5.0) as client:
            r = await client.get(f"{url}/health")
            results["victoriatraces"] = "healthy" if r.status_code == 200 else f"unhealthy: HTTP {r.status_code}"
    except Exception as e:
        results["victoriatraces"] = f"unhealthy: {e}"

    return _text(results)


# ---------------------------------------------------------------------------
# Registry: tool name -> (input model, handler, Tool definition)
# ---------------------------------------------------------------------------

_Registry = tuple[type[BaseModel], Callable[..., Awaitable[list[TextContent]]], Tool]

_TOOLS: dict[str, _Registry] = {}


def _register(
    name: str,
    description: str,
    model: type[BaseModel],
    handler: Callable[..., Awaitable[list[TextContent]]],
) -> None:
    schema = model.model_json_schema()
    schema.pop("$defs", None)
    schema.pop("title", None)
    _TOOLS[name] = (
        model,
        handler,
        Tool(name=name, description=description, inputSchema=schema),
    )


_register(
    "observability_health",
    "Check health of VictoriaLogs and VictoriaTraces services.",
    _NoArgs,
    _health_check,
)
_register(
    "observability_services",
    "List all services that have observability data.",
    _NoArgs,
    _services_list,
)
_register(
    "logs_errors",
    "Query error logs from VictoriaLogs for a service.",
    _ErrorQuery,
    _logs_errors,
)
_register(
    "logs_recent",
    "Query recent logs from VictoriaLogs for a service.",
    _TimeRangeQuery,
    _logs_recent,
)
_register(
    "traces_get",
    "Get a specific trace by ID from VictoriaTraces.",
    _TraceQuery,
    _traces_get,
)
_register(
    "traces_errors",
    "Query traces with errors from VictoriaTraces for a service.",
    _ErrorTraceQuery,
    _traces_errors,
)


# ---------------------------------------------------------------------------
# MCP handlers
# ---------------------------------------------------------------------------


@server.list_tools()
async def list_tools() -> list[Tool]:
    return [entry[2] for entry in _TOOLS.values()]


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any] | None) -> list[TextContent]:
    entry = _TOOLS.get(name)
    if entry is None:
        return [TextContent(type="text", text=f"Unknown tool: {name}")]

    model_cls, handler, _ = entry
    try:
        args = model_cls.model_validate(arguments or {})
        return await handler(args)
    except Exception as exc:
        return [TextContent(type="text", text=f"Error: {type(exc).__name__}: {exc}")]


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


async def main(victorialogs_url: str | None = None, victoriatraces_url: str | None = None) -> None:
    global _victorialogs_url, _victoriatraces_url
    _victorialogs_url = victorialogs_url or os.environ.get("VICTORIALOGS_URL", "http://localhost:42010")
    _victoriatraces_url = victoriatraces_url or os.environ.get("VICTORIATRACES_URL", "http://localhost:42011")
    async with stdio_server() as (read_stream, write_stream):
        init_options = server.create_initialization_options()
        await server.run(read_stream, write_stream, init_options)


if __name__ == "__main__":
    asyncio.run(main())