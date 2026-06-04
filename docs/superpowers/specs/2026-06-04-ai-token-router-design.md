# Ai-token — Per-Machine Model Router Design Spec
**Date:** 2026-06-04
**Author:** Rohit Tanwar (Abacusdesk)
**Status:** Approved for implementation

---

## 1. Problem Statement

Every Claude Code session at Abacusdesk runs on Sonnet regardless of task complexity. A session that SSHes into a server to check a log costs the same as one that writes a full RCA report. With 10+ team members across 6+ client projects, this is wasteful — roughly 60% of sessions are read-only recon tasks that could run on Haiku (~15× cheaper).

There is no visibility into how many tokens each project or team member consumes.

---

## 2. Goal

A per-machine CLI wrapper (`cc`) that:
1. Classifies the task description using keyword rules (no API cost, instant)
2. Routes to the cheapest capable Claude model
3. Logs sessions locally for weekly cost summaries
4. Requires zero behavior change beyond typing `cc` instead of `claude`

**Not in scope:** Central server, shared memory, claude-DB integration, network dependencies.

---

## 3. Architecture

```
User types: cc "check polymedicure apache logs for errors"
                        │
                        ▼
              ┌─────────────────────┐
              │  Classifier         │  ← keyword rules, no API cost, <1ms
              └──────────┬──────────┘
                         │
          ┌──────────────┼──────────────┐
          ▼              ▼              ▼
        haiku          sonnet          opus
   (read/recon)    (write/analyze)  (complex)
          │              │              │
          └──────────────┼──────────────┘
                         ▼
              claude --model <x> "task"
                         │
                         ▼
              Normal Claude Code session
```

---

## 4. Classification Rules

Three tiers. First match wins. Checked in order: Opus → Haiku → Sonnet → Default (Sonnet).

| Tier | Trigger keywords | Model |
|---|---|---|
| **Recon** | check, read, show, list, grep, find, verify, status, view, what is, ping, test, ssh, cat, look, display, get, fetch, see, confirm, inspect, scan, monitor, watch, tail, head, count, how many | `claude-haiku-4-5-20251001` |
| **Write** | write, fix, plan, report, analyze, analyse, build, implement, configure, debug, generate, update, add, investigate, rca, create, optimize, improve, setup, install, deploy, refactor, explain, help | `claude-sonnet-4-6` |
| **Complex** | architect, design, security audit, full assessment, from scratch, comprehensive, novel, complex strategy, full incident, complete audit | `claude-opus-4-8` |
| **Default** | anything unmatched | `claude-sonnet-4-6` |

Manual override: `cc --model haiku "..."` / `cc --model sonnet "..."` / `cc --model opus "..."`

---

## 5. Local Usage Log

Stored at `~/.cc/log.csv`. One row per session:

```
date,time,project,model,task
2026-06-04,14:32,polymedicure,claude-haiku-4-5-20251001,"check apache logs for errors"
2026-06-04,15:10,polymedicure,claude-sonnet-4-6,"write RCA report for incident 5"
```

Project is auto-detected from the current working directory name.

`cc --stats` prints a 7-day summary with estimated savings vs all-Sonnet.

---

## 6. Cost Estimates (per session, rough)

| Model | Est. cost/session | vs Sonnet |
|---|---|---|
| Haiku | ~$0.01 | 15× cheaper |
| Sonnet | ~$0.15 | baseline |
| Opus | ~$0.50 | 3× more expensive |

---

## 7. File Structure

```
Ai-token/
├── cc                    ← single executable Python script (~200 lines)
├── install.sh            ← copies cc to ~/.local/bin, adds to PATH
├── tests/
│   └── test_cc.py        ← unit tests for classifier, logger, config
└── README.md
```

`cc` is self-contained — classifier, logger, and config are all embedded. No external dependencies beyond Python 3 (standard library only) and Claude Code CLI.

---

## 8. Install Flow

```bash
git clone https://github.com/SupportAbacus/Ai-token
cd Ai-token && ./install.sh
```

`install.sh`:
1. Copies `cc` to `~/.local/bin/cc`
2. Makes it executable
3. Appends `~/.local/bin` to PATH in `~/.bashrc` / `~/.zshrc` if not already there
4. Creates `~/.cc/` config directory
5. Prints: `✓ cc installed. Try: cc "check apache logs for errors"`

---

## 9. Usage Examples

```bash
# Recon → Haiku (cheap)
cc "check polymedicure apache log for errors"
cc "verify smtp port 465 is open on prayag server"
cc "show me the last 50 lines of the error log"
cc "list all cron jobs on the server"

# Write/Analyze → Sonnet (standard)
cc "write RCA report for today's incidents"
cc "fix the ModSec rule for Chrome/148"
cc "analyze why TTFB is 7 seconds"

# Complex → Opus (expensive, intentional)
cc "architect a full security remediation plan from scratch"
cc "complete security audit of the Accord compromise"

# Manual override
cc --model sonnet "check the log"   # force Sonnet even for recon
cc --model haiku "write a summary"  # force Haiku even for write

# Stats
cc --stats                          # 7-day usage + estimated savings
```

---

## 10. Success Criteria

- [ ] `cc "check X"` routes to Haiku, `cc "write Y"` routes to Sonnet
- [ ] `--model` override works
- [ ] Session logged to `~/.cc/log.csv` after each run
- [ ] `--stats` shows correct counts and savings estimate
- [ ] `install.sh` puts `cc` on PATH in one command
- [ ] All tests pass
- [ ] Works on Linux (bash + zsh)
