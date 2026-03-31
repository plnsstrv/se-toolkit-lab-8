# LMS Skill

This skill helps you interact with the Learning Management System (LMS) backend.

## Available Tools

| Tool | Description | Parameters |
|------|-------------|------------|
| `lms_health` | Check if the LMS backend is healthy and report item count | None |
| `lms_labs` | List all labs available in the LMS | None |
| `lms_learners` | List all learners registered in the LMS | None |
| `lms_pass_rates` | Get pass rates (avg score and attempt count per task) for a lab | `lab` (required) |
| `lms_timeline` | Get submission timeline (date + submission count) for a lab | `lab` (required) |
| `lms_groups` | Get group performance (avg score + student count per group) for a lab | `lab` (required) |
| `lms_top_learners` | Get top learners by average score for a lab | `lab` (required), `limit` (optional, default 5) |
| `lms_completion_rate` | Get completion rate (passed / total) for a lab | `lab` (required) |
| `lms_sync_pipeline` | Trigger the LMS sync pipeline | None |

## Usage Guidelines

### General Queries
- For questions about available labs, use `lms_labs`
- For questions about registered learners, use `lms_learners`
- For health status, use `lms_health`

### Lab-Specific Queries
When a user asks about lab-specific data (scores, timeline, groups, pass rates), you MUST provide the `lab` parameter.

**If the user doesn't specify a lab:**
1. First use `lms_labs` to list available labs
2. Ask the user which lab they want to know about
3. Then call the appropriate tool with the lab parameter

Example flow:
- User: "Show me the scores"
- You: First call `lms_labs` to see available labs
- You: "Which lab would you like to see scores for? Available labs are: lab-01, lab-02, ..."
- User: "lab-04"
- You: Call `lms_pass_rates` with `lab: "lab-04"`

### Formatting Results

- **Percentages:** Format as percentages (e.g., 0.85 → 85%)
- **Counts:** Use appropriate units (students, submissions, etc.)
- **Lists:** Present as bullet points or numbered lists
- Keep responses concise and focused

### Complex Queries

For questions requiring multiple data points:
1. Plan which tools you need to call
2. Call them in sequence
3. Synthesize the results into a coherent answer

Example: "Which lab has the lowest pass rate?"
1. Call `lms_labs` to get all lab names
2. Call `lms_completion_rate` for each lab
3. Compare and report the result

## What You Can Do

When asked "what can you do?", explain your current capabilities:
- Query LMS backend for lab information
- Check system health
- Retrieve learner data
- Analyze pass rates and completion rates
- View submission timelines
- Compare group performance
- Identify top performers per lab

Be clear about limitations: you can only query existing data, not modify it.