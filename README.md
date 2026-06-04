# Ai-token — Smart Model Router for Claude Code

Type `cai` instead of `claude`. It picks the cheapest model that can handle your task — automatically.

## Install

```bash
git clone https://github.com/SupportAbacus/Ai-token
cd Ai-token && ./install.sh
source ~/.bashrc   # or source ~/.zshrc
```

## Usage

```bash
# Recon tasks → Haiku (~15× cheaper than Sonnet)
cai "check polymedicure apache logs for errors"
cai "verify smtp port 465 is open on prayag server"
cai "show me the last 50 lines of the error log"
cai "list all cron jobs on the server"

# Write/Analyze tasks → Sonnet
cai "write RCA report for today's incident"
cai "fix the ModSec rule for Chrome/148"
cai "analyze why TTFB is 7 seconds"

# Complex tasks → Opus
cai "architect a full security remediation plan from scratch"
cai "comprehensive security audit of the Acaiord compromise"

# Override the model
cai --model sonnet "check the logs"
cai --model haiku "write a quick summary"

# Preview routing without launching Claude
cai --dry-run "check apache logs for errors"

# View 7-day usage and estimated savings
cai --stats
```

## How routing works

| Task keywords | Model | Cost vs Sonnet |
|---|---|---|
| check, read, show, list, grep, find, verify, status, ssh, cat… | **Haiku** | ~15× cheaper |
| write, fix, plan, analyze, debug, rca, investigate, build… | **Sonnet** | baseline |
| architect, comprehensive, full assessment, from scratch, complete audit… | **Opus** | ~3× more |

Unmatched tasks default to **Sonnet**.

## Logs

Every session is saved to `~/.cai/log.csv`:

```
date,time,project,model,task
2026-06-04,14:32,Polymedicure,claude-haiku-4-5-20251001,check apache logs
2026-06-04,15:10,Polymedicure,claude-sonnet-4-6,write RCA report
```

## Update

```bash
cd Ai-token && git pull && ./install.sh
```

## Run tests

```bash
python3 -m pytest tests/ -v
```
