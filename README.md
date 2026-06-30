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
| [hermes-tweet](./hermes-tweet/) | Search X/Twitter, read tweet replies, look up users, monitor tweets, export followers, and gate approved X actions through Xquik | Load via `/skill` or `hermes -s` | Requires the native Hermes Tweet plugin |

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

## Prerequisites

Each skill has its own requirements. Check individual SKILL.md or README for details.

### pcap-wlan-mgmt-diff

| Dependency | Level | Install |
|-----------|-------|---------|
| `python3` ≥ 3.9 | **Required** | System default |
| `tshark` ≥ 4.x | **Required** | See [tshark setup](#tshark-setup) |
| `scapy` | Not needed | This skill is scapy-free |

#### tshark Setup

The apt default version is often outdated. Install the latest stable release from the
official Wireshark PPA for full 802.11 protocol decoding:

```bash
sudo add-apt-repository ppa:wireshark-dev/stable
sudo apt update
sudo apt install tshark
```

Verify:
```bash
tshark --version   # should show 4.x
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

## License

MIT — see individual skill directories for details.
