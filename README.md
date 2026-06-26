# skill-hub

AI agent skills collection — reusable, platform-agnostic tools and workflows.

Each skill is self-contained in its own directory with a `SKILL.md` (Hermes Agent format)
and any required scripts, references, or assets. Every tool is designed to work
**standalone** — no AI agent required — while also integrating seamlessly with
Hermes Agent, Claude Code, Codex, and similar platforms.

## Skills

| Skill | Description | Hermes | Standalone |
|-------|-------------|--------|------------|
| [pcap-wlan-mgmt-diff](./pcap-wlan-mgmt-diff/) | Compare two 802.11 pcap files, diff every management frame IE subfield, generate HTML report with protocol impact scoring | Load via `/skill` or `hermes -s` | `python3 scripts/assoc_diff.py a.pcap b.pcap` |

## Using a Skill

### With Hermes Agent
Load the SKILL.md directly:
```bash
hermes -s pcap-wlan-mgmt-diff
# or install from this repo
hermes skills tap add https://github.com/DannisWu/skill-hub
hermes skills install pcap-wlan-mgmt-diff
```

### With Claude Code
Copy the skill instructions into your project context:
```bash
cat pcap-wlan-mgmt-diff/SKILL.md >> CLAUDE.md
```
Or paste the skill description at the start of your session.

### Standalone (No AI Agent)
Every skill's scripts are plain Python/Bash — just run them:
```bash
python3 pcap-wlan-mgmt-diff/scripts/assoc_diff.py --help
```

## Adding a New Skill

```bash
cp -r your-skill/ path/to/skill-hub/
```

Each skill directory should follow this structure:
```
skill-name/
├── SKILL.md              # Required — Hermes Agent skill definition (YAML frontmatter + markdown)
├── README.md             # Optional — standalone usage guide for non-Hermes users
├── scripts/              # Executable scripts (Python, Bash, etc.)
├── references/           # Supporting docs, field guides, case studies
├── templates/            # Config templates, report templates
└── assets/               # Images, fonts, static resources
```

### SKILL.md Frontmatter (Minimum)

```yaml
---
name: skill-name
description: "One-line summary of what the skill does and when to use it."
version: 1.0.0
author: Your Name
license: MIT
platforms: [linux, macos]
---
```

## Prerequisites

Most skills only need standard tools. Check each skill's README or SKILL.md for specific requirements.
Common dependencies:

| Tool | Install |
|------|---------|
| `tshark` ≥ 4.x | `sudo apt install tshark` / `brew install wireshark` |
| `python3` ≥ 3.9 | System default |

## License

MIT — see individual skill directories for details.
