# Observability Skill

You have access to observability tools that query VictoriaLogs and VictoriaTraces to investigate system health, errors, and performance issues.

## Available Tools

### Health and Services
- `observability_health` - Check if VictoriaLogs and VictoriaTraces are healthy
- `observability_services` - List all services with observability data

### Logs
- `logs_errors` - Query error logs from VictoriaLogs for a service
- `logs_recent` - Query recent logs from VictoriaLogs for a service

### Traces
- `traces_get` - Get a specific trace by ID from VictoriaTraces
- `traces_errors` - Query traces with errors from VictoriaTraces for a service

## When to Use

Use these tools when users ask about:
- System health or status
- Recent errors or issues
- Performance problems
- "What went wrong?" questions
- Investigation of specific requests or operations

## Usage Patterns

### Health Check
```
User: "Is everything healthy?"
→ Use observability_health to check VictoriaLogs and VictoriaTraces status
→ Use observability_services to list available services
```

### Error Investigation
```
User: "Are there any errors in the last hour?"
→ Use logs_errors with hours=1 to find recent error logs
→ Use traces_errors with hours=1 to find error traces
→ Summarize findings with error types, counts, and trace IDs
```

### Specific Trace Investigation
```
User: "What happened with trace X?"
→ Use traces_get with the trace ID to get full trace details
→ Analyze span hierarchy and timing
→ Identify error spans and their causes
```

### Proactive Monitoring
```
Periodically check:
→ logs_errors for recent issues
→ observability_health for system status
→ Report findings to user proactively
```

## Response Format

When reporting observability findings:

1. **Summary**: Start with a clear summary of findings
2. **Details**: Provide specific log entries or trace information
3. **Impact**: Explain what the errors mean for the system
4. **Recommendations**: Suggest next steps if applicable

Example response:
```
I found 3 errors in the last hour:

1. Database connection error (2 occurrences)
   - Error: "connection is closed"
   - Service: Learning Management Service
   - Trace IDs: abc123, def456

2. DNS resolution error (1 occurrence)
   - Error: "Name or service not known"
   - Service: Learning Management Service
   - Trace ID: ghi789

Recommendation: Check PostgreSQL connectivity and DNS configuration.
```

## Error Handling

If a tool fails:
- Report the error clearly to the user
- Suggest checking if the corresponding service is running
- Offer alternative investigation methods if available