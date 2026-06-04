# Ai-token — Smart Model Router for Claude Code

Type `claude` as normal. The router automatically picks the cheapest model that can handle your task — no behavior change required from your team.

## Install

### Linux / macOS

```bash
git clone https://github.com/SupportAbacus/Ai-token
cd Ai-token && ./install.sh
source ~/.bashrc   # or source ~/.zshrc
```

### Windows (PowerShell)

```powershell
git clone https://github.com/SupportAbacus/Ai-token
cd Ai-token
.\install.ps1
# Restart PowerShell after install
```

> **Requires:** Python 3 and Claude Code CLI already installed.

---

## Usage

Nothing changes — just type `claude` as you always do:

```bash
# Recon tasks → Haiku (~15× cheaper than Sonnet)
claude "check polymedicure apache logs for errors"
claude "verify smtp port 465 is open"
claude "show me the last 50 lines of the error log"
claude "list all cron jobs on the server"

# Write/Analyze tasks → Sonnet
claude "write RCA report for today's incident"
claude "fix the ModSec rule for Chrome/148"
claude "analyze why TTFB is 7 seconds"

# Complex tasks → Opus
claude "architect a full security remediation plan from scratch"
claude "comprehensive security audit of the Accord compromise"

# Already have a model in mind? Pass --model — router steps aside
claude --model sonnet "check the logs"

# Interactive session — routed to Sonnet, logged as "(interactive)"
claude

# Preview routing without launching
claude --dry-run "write a report about the incident"

# 7-day usage + estimated savings
claude --stats
```

---

## How routing works

| Task keywords | Model | Cost vs Sonnet |
|---|---|---|
| check, read, show, list, grep, find, verify, status, ssh, tail… | **Haiku** | ~15× cheaper |
| write, fix, plan, analyze, debug, rca, investigate, build… | **Sonnet** | baseline |
| architect, comprehensive, full assessment, from scratch, complete audit… | **Opus** | ~3× more |

- Unmatched tasks default to **Sonnet**
- Explicit `--model` flag → always passed through unchanged
- No task (just `claude`) → defaults to **Sonnet**, logged as `(interactive)`

---

## Logs

Sessions are saved to `~/.cai/log.csv` (Linux/macOS) or `%USERPROFILE%\.cai\log.csv` (Windows):

```
date,time,project,model,task
2026-06-04,14:32,Polymedicure,claude-haiku-4-5-20251001,check apache logs
2026-06-04,15:10,Polymedicure,claude-sonnet-4-6,write RCA report
2026-06-04,16:00,Polymedicure,claude-sonnet-4-6,(interactive)
```

---

## Update

### Linux / macOS
```bash
cd Ai-token && git pull && ./install.sh
```

### Windows
```powershell
cd Ai-token; git pull; .\install.ps1
```

---

## Run tests

```bash
python3 -m pytest tests/ -v
```

---

## Platform compatibility

| Feature | Linux | macOS | Windows |
|---|---|---|---|
| Model routing | ✅ | ✅ | ✅ |
| Session logging | ✅ | ✅ | ✅ |
| `--stats` | ✅ | ✅ | ✅ |
| Process replacement | `execvp` | `execvp` | `subprocess` |
| Install script | `install.sh` | `install.sh` | `install.ps1` |
| Wrapper | bash shim | bash shim | `claude.cmd` |
