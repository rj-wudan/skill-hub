# CLS Case Weekly Report（云程上游芯片 Case 周报）

Generate a structured weekly report from the ClourneySemi (云程) Redmine case tracker.

## Standalone Usage (No AI Agent Required)

```bash
# 1. Configure credentials
vim scripts/generate_report.py
# Set REDMINE_URL, PROJECT, USERNAME, PASSWORD

# 2. Run
python3 scripts/generate_report.py
```

Output is a structured Chinese Markdown report with:
- Resolved cases this week
- Open cases with days-open tracking
- Assignee/priority distribution
- Stale case alerts (>30 days)
- 4-week resolution trend
- Risk analysis vs project timeline

## Dependencies

- Python 3.x (stdlib only)
- `curl`

## Platform Support

| Platform | Status |
|----------|--------|
| Hermes Agent | ✅ Native skill |
| Claude Code | ✅ Via install.sh |
| OpenCode | ✅ Via install.sh |
| Cursor | ✅ Via install.sh |
| Windsurf | ✅ Via install.sh |
| Standalone | ✅ `python3 scripts/generate_report.py` |
