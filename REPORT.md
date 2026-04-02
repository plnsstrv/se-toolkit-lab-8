
# Lab 8 — Report

Paste your checkpoint evidence below. Add screenshots as image files in the repo and reference them with `![description](path)`.

## Task 1A — Bare agent

<!-- Paste the agent's response to "What is the agentic loop?" and "What labs are available in our LMS?" -->

### Question 1: "What is the agentic loop?"

![What is the agentic loop?](reportimages/What_is_the_agentic_loop.jpg)

### Question 2: "What labs are available in our LMS?"

![What labs are available in our LMS?](reportimages/What_labs%20are_available%20in_our_LMS.jpg)

*Note: The agent does not know about LMS labs because it has no tools configured yet. This is expected behavior for a bare agent.*

## Task 1B — Agent with LMS tools

<!-- Paste the agent's response to "What labs are available?" and "Describe the architecture of the LMS system" -->

### Question 1: "What labs are available?"

![What labs are available?](reportimages/What_labs_are_available.jpg)

*Note: With MCP tools configured, the agent can now call `lms_labs` and return real lab names from the backend.*

### Question 2: "Describe the architecture of the LMS system"

![Describe the architecture of the LMS system](reportimages/Describe_the_architecture_of_the_LMS_system.jpg)

*Note: The agent uses tools like `lms_health` to gather information about the system architecture.*

## Task 1C — Skill prompt

<!-- Paste the agent's response to "Show me the scores" (without specifying a lab) -->

### Question: "Show me the scores" (without specifying a lab)

![Show me the scores](reportimages/Show_me_the_scores.jpg)

*Note: The skill prompt teaches the agent to ask which lab when the user doesn't specify one, rather than failing or hallucinating.*

## Task 2A — Deployed agent

<!-- Paste a short nanobot startup log excerpt showing the gateway started inside Docker -->
nanobot-1  | Using config: /tmp/resolved_config.json
  nanobot-1  |  Starting nanobot gateway version 0.1.4.post5 on port 18790...
  nanobot-1  | /usr/local/lib/python3.14/site-packages/dingtalk_stream/stream.py:195: SyntaxWarning: 'return' in a
  'finally' block
  nanobot-1  |   return ip
  nanobot-1  | 2026-04-02 12:26:15.272 | DEBUG    | nanobot.channels.registry:discover_all:64 - Skipping built-in
  channel 'matrix': Matrix dependencies not installed.
  nanobot-1  | 2026-04-02 12:26:16.876 | INFO     | nanobot.channels.manager:_init_channels:58 - WebChat channel enabled
  nanobot-1  | ✓ Channels enabled: webchat
  nanobot-1  | ✓ Heartbeat: every 1800s
  nanobot-1  | 2026-04-02 12:26:16.883 | INFO     | nanobot.heartbeat.service:start:124 - Heartbeat started
  nanobot-1  | 2026-04-02 12:26:17.609 | INFO     | nanobot.channels.manager:start_all:91 - Starting webchat channel...
  nanobot-1  | 2026-04-02 12:26:20.266 | DEBUG    | nanobot.agent.tools.mcp:connect_mcp_servers:226 - MCP: registered
  tool 'mcp_lms_lms_health' from server 'lms'
  nanobot-1  | 2026-04-02 12:26:20.266 | DEBUG    | nanobot.agent.tools.mcp:connect_mcp_servers:226 - MCP: registered
  tool 'mcp_lms_lms_labs' from server 'lms'
  nanobot-1  | 2026-04-02 12:26:20.267 | INFO     | nanobot.agent.tools.mcp:connect_mcp_servers:246 - MCP server 'lms':
  connected, 9 tools registered
  nanobot-1  | 2026-04-02 12:26:20.267 | INFO     | nanobot.agent.loop:run:280 - Agent loop started
  nanobot-1  | 2026-04-02 12:26:52.607 | INFO     | nanobot.agent.loop:_process_message:425 - Processing message from
  webchat:100cf0f0-68cc-472d-90b0-136e75916e2c: hi
  nanobot-1  | 2026-04-02 12:26:55.909 | INFO     | nanobot.agent.loop:_process_message:479 - Response: Hello! I'm
  nanobot, your helpful AI assistant. How can I assist you today?

## Task 2B — Web client

<!-- Screenshot of a conversation with the agent in the Flutter web app -->
<img width="2507" height="1555" alt="image" src="https://github.com/user-attachments/assets/39653302-d97d-4622-abd2-3dd699b8390a" />


## Task 3A — Structured logging

### Happy-path logs (PostgreSQL running)

**VictoriaLogs query:**
```
_stream:{service.name="Learning Management Service"}
```

**Sample logs:**
```json
{"_msg":"request_started","_time":"2026-04-02T18:25:07.984845568Z","event":"request_started","method":"GET","path":"/items/","severity":"INFO","service.name":"Learning Management Service"}
{"_msg":"auth_success","_time":"2026-04-02T18:25:07.98562688Z","event":"auth_success","severity":"INFO","service.name":"Learning Management Service"}
{"_msg":"db_query","_time":"2026-04-02T18:25:07.98604928Z","event":"db_query","operation":"select","table":"item","severity":"INFO","service.name":"Learning Management Service"}
```

### Error-path logs (PostgreSQL stopped)

**VictoriaLogs query:**
```
_stream:{service.name="Learning Management Service"} severity:ERROR
```

**Sample error logs:**
```json
{"_msg":"db_query","_time":"2026-04-02T18:25:08.262736384Z","error":"[Errno -2] Name or service not known","event":"db_query","operation":"select","severity":"ERROR","service.name":"Learning Management Service","trace_id":"76e571f4270ba27f3eb4b876fa3b231b"}
{"_msg":"db_query","_time":"2026-04-02T18:25:04.117608448Z","error":"connection is closed","event":"db_query","operation":"select","severity":"ERROR","service.name":"Learning Management Service","trace_id":"f8bd9357339cbd7de0ea162d77f52398"}
```

## Task 3B — Traces

### Healthy trace span hierarchy

**VictoriaTraces query:**
```
GET /select/jaeger/api/traces?service=Learning Management Service&limit=1
```

Traces show normal span hierarchy with:
- `request_started` span
- `auth_success` span
- `db_query` span (successful)

### Error trace

**VictoriaTraces query for error traces:**
```
GET /select/jaeger/api/traces?service=Learning Management Service
```

Error traces contain spans with:
- `error` tag set to `true`
- Exception logs with stack traces
- Failed `db_query` spans

Sample error span:
```json
{
  "operationName": "db_query",
  "duration": 275778,
  "tags": [{"key": "error", "value": true}],
  "logs": [{"fields": [{"key": "exception.message", "value": "[Errno -2] Name or service not known"}]}]
}
```

## Task 3C — Observability MCP tools

### MCP tools implemented

The following observability tools are now available:

1. `observability_health` - Check health of VictoriaLogs and VictoriaTraces
2. `observability_services` - List all services with observability data
3. `logs_errors` - Query error logs from VictoriaLogs
4. `logs_recent` - Query recent logs from VictoriaLogs
5. `traces_get` - Get a specific trace by ID
6. `traces_errors` - Query traces with errors

### Nanobot logs showing tools registered:

```
MCP: registered tool 'mcp_observability_observability_health' from server 'observability'
MCP: registered tool 'mcp_observability_observability_services' from server 'observability'
MCP: registered tool 'mcp_observability_logs_errors' from server 'observability'
MCP: registered tool 'mcp_observability_logs_recent' from server 'observability'
MCP: registered tool 'mcp_observability_traces_get' from server 'observability'
MCP: registered tool 'mcp_observability_traces_errors' from server 'observability'
MCP server 'observability': connected, 6 tools registered
```

## Task 4A — Multi-step investigation

<!-- Paste the agent's response to "What went wrong?" showing chained log + trace investigation -->

## Task 4B — Proactive health check

<!-- Screenshot or transcript of the proactive health report that appears in the Flutter chat -->

## Task 4C — Bug fix and recovery

<!-- 1. Root cause identified
     2. Code fix (diff or description)
     3. Post-fix response to "What went wrong?" showing the real underlying failure
     4. Healthy follow-up report or transcript after recovery -->
