---
name: cls-case-weekly-report
description: "Generate weekly case reports from the ClourneySemi (云程) upstream chip vendor Redmine — resolved cases, open cases, distribution, stale alerts, resolution trends, and risk analysis."
version: 1.1.0
author: WLAN Automation Test Engineer
license: MIT
platforms: [linux, macos]
metadata:
  hermes:
    tags: [redmine, case-tracking, weekly-report, clourneysemi, chip-vendor, ruijie]
    category: devops
---

# CLS Case Weekly Report（云程上游芯片 Case 周报）

## When to Use
- User asks for "CLS 周报", "CLS case 周报", "云程周报", "云程 case 周报", "ClourneySemi 周报"
- User references the ClourneySemi Redmine (support.clourneysemi.com)
- Scheduled every Friday at 18:00 via cron
- Covers: cases resolved this week, current open cases, resolution trends, risk analysis

## Architecture

The report is driven by a Python script (`scripts/generate_report.py`) that:
1. Logs into the ClourneySemi Redmine instance (support.clourneysemi.com) via cookie-based auth
2. Downloads the full case list as CSV (with `closed_on` and `updated_on` columns)
3. Parses and analyzes on the current week boundaries (Monday–Sunday)
4. Outputs a structured Markdown report in Chinese

## CLS Redmine Credentials

| Field | Value |
|-------|-------|
| URL | https://support.clourneysemi.com/redmine |
| Project | ruijie-cs8862a |
| Username | <YOUR_USERNAME> |
| Password | <YOUR_PASSWORD> |

The script handles CSRF token extraction and form-based login automatically.

## Report Structure

The generated report includes:
1. **概要** — total cases, resolved this week, open count, cumulative closed
2. **本周解决 Case** — table with ID, priority, assignee, subject
3. **当前未决 Case** — table with status, days open, assignee, subject
4. **未决分布** — by assignee and by priority (with bar charts)
5. **超期预警** — cases open >30 days
6. **高优先级未决** — urgent/high priority open cases
7. **近4周解决趋势** — weekly resolution trend chart
8. **概要分析** — resolution speed, clearance estimate, resource load, risk vs project timeline

## Cron Setup

The cron job uses this skill via agent-driven mode:

```
Schedule: 0 18 * * 5 (每周五 18:00)
Skill: cls-case-weekly-report
Deliver: origin (飞书当前对话)
```

## Pitfalls

1. **Login session expires**: The script creates a fresh login each run, so sessions don't expire between weekly runs
2. **CSV encoding**: CLS Redmine exports in GBK — always decode with `gbk, errors='replace'`
3. **closed_on may be empty for "已解决" status**: In Redmine, "已解决" (Resolved) doesn't always fill `closed_on`. The script falls back to `updated_on` as a proxy
4. **Week boundary**: Report assumes Monday–Sunday week. Monday is computed as `today - timedelta(days=today.weekday())`
5. **Script output must be Markdown**: The report is delivered to Feishu which renders Markdown. Keep tables in code blocks (```) for alignment
