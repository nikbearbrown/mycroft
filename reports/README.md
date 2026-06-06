# Reports

Logs and reports serve two different customers: logs are for agents and should be detailed, durable, and parseable; reports are for humans and should focus on insight, decision context, and review rather than dumping pipeline output.

Every conductor flow that produces output must produce both a log entry and a human-readable report.

Folder structure:

- `reports/templates/` - report templates.
- `reports/generated/` - actual outputs.
