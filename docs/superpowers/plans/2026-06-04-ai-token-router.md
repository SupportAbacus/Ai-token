# Ai-token Model Router — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build `cc`, a per-machine CLI wrapper that classifies a task description and launches Claude Code with the cheapest capable model (Haiku/Sonnet/Opus).

**Architecture:** Single Python entry point (`cc`) that imports two focused modules (`classifier.py`, `logger.py`). No external dependencies — standard library only. `install.sh` copies all three to `~/.local/bin/`.

**Tech Stack:** Python 3 (stdlib only), bash (install script), pytest (tests)

---

## File Map

| File | Responsibility |
|---|---|
| `classifier.py` | Keyword-based task → model mapping |
| `logger.py` | Write/read `~/.cc/log.csv`, format stats |
| `cc` | CLI entry point — parse args, call classifier + logger, exec claude |
| `install.sh` | Copy files to `~/.local/bin`, add to PATH |
| `tests/test_cc.py` | All unit + integration tests |
| `README.md` | Usage instructions |

---

## Task 1: Project scaffolding

**Files:**
- Create: `tests/__init__.py`
- Create: `tests/test_cc.py` (skeleton)

- [ ] **Step 1: Create test skeleton**

```python
# tests/test_cc.py
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
```

- [ ] **Step 2: Verify Python 3 is available**

```bash
python3 --version
```
Expected: `Python 3.x.x`

- [ ] **Step 3: Install pytest**

```bash
pip3 install pytest --quiet
```

- [ ] **Step 4: Create empty __init__.py**

```bash
touch /home/rohit-tanwar/claude-work/Ai-token/tests/__init__.py
```

- [ ] **Step 5: Commit scaffold**

```bash
cd /home/rohit-tanwar/claude-work/Ai-token
git add tests/
git commit -m "chore: scaffold test directory"
```

---

## Task 2: Classifier module (TDD)

**Files:**
- Create: `classifier.py`
- Modify: `tests/test_cc.py`

- [ ] **Step 1: Write failing classifier tests**

Append to `tests/test_cc.py`:

```python
from classifier import classify, MODEL_HAIKU, MODEL_SONNET, MODEL_OPUS

# ── Haiku (recon) ─────────────────────────────────────────────────────────────

def test_classify_check_routes_haiku():
    assert classify("check polymedicure apache logs for errors") == MODEL_HAIKU

def test_classify_show_routes_haiku():
    assert classify("show me the last 50 lines of the error log") == MODEL_HAIKU

def test_classify_list_routes_haiku():
    assert classify("list all cron jobs on the server") == MODEL_HAIKU

def test_classify_verify_routes_haiku():
    assert classify("verify smtp port 465 is open") == MODEL_HAIKU

def test_classify_grep_routes_haiku():
    assert classify("grep for 403 errors in the access log") == MODEL_HAIKU

def test_classify_ssh_routes_haiku():
    assert classify("ssh into the server and check status") == MODEL_HAIKU

def test_classify_status_routes_haiku():
    assert classify("status of the apache service") == MODEL_HAIKU

# ── Sonnet (write/analyze) ────────────────────────────────────────────────────

def test_classify_write_rca_routes_sonnet():
    assert classify("write RCA report for today's incident") == MODEL_SONNET

def test_classify_fix_routes_sonnet():
    assert classify("fix the ModSec rule for Chrome/148") == MODEL_SONNET

def test_classify_analyze_routes_sonnet():
    assert classify("analyze why TTFB is 7 seconds") == MODEL_SONNET

def test_classify_plan_routes_sonnet():
    assert classify("plan the CloudFront WAF setup") == MODEL_SONNET

def test_classify_debug_routes_sonnet():
    assert classify("debug the WooCommerce checkout issue") == MODEL_SONNET

def test_classify_investigate_routes_sonnet():
    assert classify("investigate the slow query in MySQL") == MODEL_SONNET

# ── Opus (complex) ────────────────────────────────────────────────────────────

def test_classify_architect_routes_opus():
    assert classify("architect a full security remediation plan from scratch") == MODEL_OPUS

def test_classify_complete_audit_routes_opus():
    assert classify("complete security audit of the server") == MODEL_OPUS

def test_classify_comprehensive_routes_opus():
    assert classify("comprehensive assessment of the WordPress setup") == MODEL_OPUS

def test_classify_full_assessment_routes_opus():
    assert classify("full assessment of Accord compromise") == MODEL_OPUS

# ── Edge cases ────────────────────────────────────────────────────────────────

def test_classify_unknown_task_defaults_sonnet():
    assert classify("xyzzy frobnosticator") == MODEL_SONNET

def test_classify_empty_string_defaults_sonnet():
    assert classify("") == MODEL_SONNET

def test_classify_case_insensitive_haiku():
    assert classify("CHECK the logs") == MODEL_HAIKU

def test_classify_case_insensitive_sonnet():
    assert classify("WRITE a report") == MODEL_SONNET

def test_classify_opus_wins_over_haiku():
    # "full assessment" (opus) + "check" (haiku) → opus wins
    assert classify("check and do a full assessment") == MODEL_OPUS
```

- [ ] **Step 2: Run tests — verify they all FAIL with ImportError**

```bash
cd /home/rohit-tanwar/claude-work/Ai-token
python3 -m pytest tests/test_cc.py -v 2>&1 | head -20
```
Expected: `ImportError: No module named 'classifier'`

- [ ] **Step 3: Create classifier.py**

```python
# classifier.py
MODEL_HAIKU = 'claude-haiku-4-5-20251001'
MODEL_SONNET = 'claude-sonnet-4-6'
MODEL_OPUS = 'claude-opus-4-8'

_OPUS = [
    'architect', 'design', 'security audit', 'full assessment',
    'from scratch', 'comprehensive', 'novel', 'complex strategy',
    'full incident', 'complete audit',
]

_HAIKU = [
    'check', 'read', 'show', 'list', 'grep', 'find', 'verify',
    'status', 'view', 'ping', 'test', 'ssh', 'cat', 'look',
    'display', 'get', 'fetch', 'see', 'confirm', 'inspect',
    'scan', 'monitor', 'watch', 'tail', 'head', 'count', 'how many',
    'what is', 'is ',
]

_SONNET = [
    'write', 'fix', 'plan', 'report', 'analyze', 'analyse', 'build',
    'implement', 'configure', 'debug', 'generate', 'update', 'add',
    'investigate', 'rca', 'create', 'optimize', 'improve', 'setup',
    'install', 'deploy', 'refactor', 'explain', 'help',
]


def classify(task: str) -> str:
    """Return the Claude model ID best suited for this task description."""
    t = task.lower()
    for kw in _OPUS:
        if kw in t:
            return MODEL_OPUS
    for kw in _HAIKU:
        if kw in t:
            return MODEL_HAIKU
    for kw in _SONNET:
        if kw in t:
            return MODEL_SONNET
    return MODEL_SONNET
```

- [ ] **Step 4: Run classifier tests — verify all PASS**

```bash
cd /home/rohit-tanwar/claude-work/Ai-token
python3 -m pytest tests/test_cc.py -v -k "classify"
```
Expected: all `test_classify_*` tests PASS

- [ ] **Step 5: Commit**

```bash
cd /home/rohit-tanwar/claude-work/Ai-token
git add classifier.py tests/test_cc.py
git commit -m "feat: add keyword-based task classifier"
```

---

## Task 3: Logger module (TDD)

**Files:**
- Create: `logger.py`
- Modify: `tests/test_cc.py`

- [ ] **Step 1: Write failing logger tests**

Append to `tests/test_cc.py`:

```python
import csv
import tempfile
from datetime import date
from pathlib import Path
from logger import log_session, get_stats, format_stats

# ── log_session ───────────────────────────────────────────────────────────────

def test_log_session_creates_file():
    with tempfile.TemporaryDirectory() as tmpdir:
        log_path = Path(tmpdir) / 'log.csv'
        log_session(MODEL_HAIKU, "check logs", "polymedicure", log_file=log_path)
        assert log_path.exists()

def test_log_session_writes_correct_fields():
    with tempfile.TemporaryDirectory() as tmpdir:
        log_path = Path(tmpdir) / 'log.csv'
        log_session(MODEL_SONNET, "write report", "prayag", log_file=log_path)
        rows = list(csv.reader(open(log_path)))
        assert len(rows) == 1
        assert rows[0][2] == 'prayag'
        assert rows[0][3] == MODEL_SONNET
        assert rows[0][4] == 'write report'

def test_log_session_truncates_long_task():
    with tempfile.TemporaryDirectory() as tmpdir:
        log_path = Path(tmpdir) / 'log.csv'
        log_session(MODEL_HAIKU, "x" * 200, "proj", log_file=log_path)
        rows = list(csv.reader(open(log_path)))
        assert len(rows[0][4]) <= 100

def test_log_session_appends_multiple():
    with tempfile.TemporaryDirectory() as tmpdir:
        log_path = Path(tmpdir) / 'log.csv'
        log_session(MODEL_HAIKU, "task one", "proj", log_file=log_path)
        log_session(MODEL_SONNET, "task two", "proj", log_file=log_path)
        rows = list(csv.reader(open(log_path)))
        assert len(rows) == 2

# ── get_stats ─────────────────────────────────────────────────────────────────

def test_get_stats_missing_file_returns_zeros():
    with tempfile.TemporaryDirectory() as tmpdir:
        log_path = Path(tmpdir) / 'nonexistent.csv'
        stats = get_stats(7, log_file=log_path)
        assert stats[MODEL_HAIKU] == 0
        assert stats[MODEL_SONNET] == 0
        assert stats[MODEL_OPUS] == 0

def test_get_stats_counts_correctly():
    with tempfile.TemporaryDirectory() as tmpdir:
        log_path = Path(tmpdir) / 'log.csv'
        today = date.today().strftime('%Y-%m-%d')
        with open(log_path, 'w', newline='') as f:
            w = csv.writer(f)
            w.writerow([today, '10:00', 'proj', MODEL_HAIKU, 'check x'])
            w.writerow([today, '11:00', 'proj', MODEL_HAIKU, 'read y'])
            w.writerow([today, '12:00', 'proj', MODEL_SONNET, 'write z'])
        stats = get_stats(7, log_file=log_path)
        assert stats[MODEL_HAIKU] == 2
        assert stats[MODEL_SONNET] == 1
        assert stats[MODEL_OPUS] == 0

def test_get_stats_ignores_old_entries():
    with tempfile.TemporaryDirectory() as tmpdir:
        log_path = Path(tmpdir) / 'log.csv'
        with open(log_path, 'w', newline='') as f:
            w = csv.writer(f)
            w.writerow(['2020-01-01', '10:00', 'proj', MODEL_HAIKU, 'old task'])
        stats = get_stats(7, log_file=log_path)
        assert stats[MODEL_HAIKU] == 0

# ── format_stats ──────────────────────────────────────────────────────────────

def test_format_stats_no_sessions():
    counts = {MODEL_HAIKU: 0, MODEL_SONNET: 0, MODEL_OPUS: 0}
    assert format_stats(counts) == "No sessions logged yet."

def test_format_stats_shows_model_counts():
    counts = {MODEL_HAIKU: 5, MODEL_SONNET: 3, MODEL_OPUS: 1}
    output = format_stats(counts)
    assert "Haiku" in output
    assert "Sonnet" in output
    assert "Opus" in output
    assert "5" in output
    assert "3" in output

def test_format_stats_shows_savings():
    counts = {MODEL_HAIKU: 10, MODEL_SONNET: 5, MODEL_OPUS: 0}
    output = format_stats(counts)
    # 10 haiku @ $0.01 + 5 sonnet @ $0.15 = $0.85 actual
    # 15 sonnet @ $0.15 = $2.25 all-sonnet → saving = $1.40
    assert "$1.40" in output

def test_format_stats_zero_savings_when_all_sonnet():
    counts = {MODEL_HAIKU: 0, MODEL_SONNET: 5, MODEL_OPUS: 0}
    output = format_stats(counts)
    assert "$0.00" in output
```

- [ ] **Step 2: Run tests — verify they FAIL with ImportError**

```bash
cd /home/rohit-tanwar/claude-work/Ai-token
python3 -m pytest tests/test_cc.py -v -k "log or stats" 2>&1 | head -10
```
Expected: `ImportError: No module named 'logger'`

- [ ] **Step 3: Create logger.py**

```python
# logger.py
import csv
from datetime import datetime, timedelta, date
from pathlib import Path

CC_DIR = Path.home() / '.cc'
LOG_FILE = CC_DIR / 'log.csv'

_COST = {
    'claude-haiku-4-5-20251001': 0.01,
    'claude-sonnet-4-6': 0.15,
    'claude-opus-4-8': 0.50,
}

_NAMES = {
    'claude-haiku-4-5-20251001': 'Haiku',
    'claude-sonnet-4-6': 'Sonnet',
    'claude-opus-4-8': 'Opus',
}


def log_session(model: str, task: str, project: str, log_file: Path = None) -> None:
    path = log_file or LOG_FILE
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'a', newline='') as f:
        csv.writer(f).writerow([
            date.today().strftime('%Y-%m-%d'),
            datetime.now().strftime('%H:%M'),
            project,
            model,
            task[:100],
        ])


def get_stats(days: int = 7, log_file: Path = None) -> dict:
    path = log_file or LOG_FILE
    counts = {m: 0 for m in _COST}
    if not path.exists():
        return counts
    cutoff = (date.today() - timedelta(days=days)).strftime('%Y-%m-%d')
    with open(path, newline='') as f:
        for row in csv.reader(f):
            if len(row) >= 4 and row[0] >= cutoff and row[3] in counts:
                counts[row[3]] += 1
    return counts


def format_stats(counts: dict) -> str:
    total = sum(counts.values())
    if total == 0:
        return "No sessions logged yet."
    actual = sum(counts.get(m, 0) * _COST[m] for m in _COST)
    all_sonnet = total * _COST['claude-sonnet-4-6']
    savings = all_sonnet - actual
    lines = [
        f"Last 7 days ({total} sessions):",
        f"  Haiku   → {counts.get('claude-haiku-4-5-20251001', 0):2d} sessions",
        f"  Sonnet  → {counts.get('claude-sonnet-4-6', 0):2d} sessions",
        f"  Opus    → {counts.get('claude-opus-4-8', 0):2d} sessions",
        f"",
        f"  Estimated saving vs all-Sonnet: ~${savings:.2f}",
    ]
    return '\n'.join(lines)
```

- [ ] **Step 4: Run logger tests — verify all PASS**

```bash
cd /home/rohit-tanwar/claude-work/Ai-token
python3 -m pytest tests/test_cc.py -v -k "log or stats"
```
Expected: all `test_log_*` and `test_*_stats*` tests PASS

- [ ] **Step 5: Commit**

```bash
cd /home/rohit-tanwar/claude-work/Ai-token
git add logger.py tests/test_cc.py
git commit -m "feat: add session logger with stats formatter"
```

---

## Task 4: Main CLI (`cc`)

**Files:**
- Create: `cc`
- Modify: `tests/test_cc.py`

- [ ] **Step 1: Write failing CLI tests**

Append to `tests/test_cc.py`:

```python
import subprocess
import sys

def _run_cc(args, cwd=None):
    """Run cc as a subprocess and return (returncode, stdout, stderr)."""
    result = subprocess.run(
        [sys.executable, str(Path(__file__).resolve().parent.parent / 'cc')] + args,
        capture_output=True, text=True,
        cwd=cwd or '/home/rohit-tanwar/claude-work/Ai-token'
    )
    return result.returncode, result.stdout, result.stderr

def test_cc_no_args_prints_usage():
    code, out, _ = _run_cc([])
    assert code == 0
    assert 'Usage' in out

def test_cc_stats_no_data():
    code, out, _ = _run_cc(['--stats'])
    assert code == 0
    assert 'No sessions logged' in out or 'sessions' in out

def test_cc_prints_model_line_for_haiku_task(tmp_path):
    # Patch os.execvp so cc doesn't actually launch claude
    # We test the routing decision by reading stdout before exec
    # Use --dry-run flag (we'll add this for testing)
    code, out, _ = _run_cc(['--dry-run', 'check the apache logs'])
    assert 'Haiku' in out

def test_cc_prints_model_line_for_sonnet_task():
    code, out, _ = _run_cc(['--dry-run', 'write a report about the incident'])
    assert 'Sonnet' in out

def test_cc_prints_model_line_for_opus_task():
    code, out, _ = _run_cc(['--dry-run', 'comprehensive security audit from scratch'])
    assert 'Opus' in out

def test_cc_model_override_haiku():
    code, out, _ = _run_cc(['--dry-run', '--model', 'haiku', 'write a report'])
    assert 'Haiku' in out

def test_cc_model_override_opus():
    code, out, _ = _run_cc(['--dry-run', '--model', 'opus', 'check logs'])
    assert 'Opus' in out

def test_cc_detects_project_from_cwd():
    code, out, _ = _run_cc(
        ['--dry-run', 'check logs'],
        cwd='/home/rohit-tanwar/claude-work/Polymedicure'
    )
    assert 'polymedicure' in out.lower() or 'Polymedicure' in out
```

- [ ] **Step 2: Run tests — verify they FAIL**

```bash
cd /home/rohit-tanwar/claude-work/Ai-token
python3 -m pytest tests/test_cc.py -v -k "cc_" 2>&1 | head -20
```
Expected: FAIL (file `cc` doesn't exist yet)

- [ ] **Step 3: Create `cc`**

```python
#!/usr/bin/env python3
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from classifier import classify, MODEL_HAIKU, MODEL_SONNET, MODEL_OPUS
from logger import log_session, get_stats, format_stats

_NAMES = {MODEL_HAIKU: 'Haiku', MODEL_SONNET: 'Sonnet', MODEL_OPUS: 'Opus'}
_MAP = {'haiku': MODEL_HAIKU, 'sonnet': MODEL_SONNET, 'opus': MODEL_OPUS}
_WORK = Path('/home/rohit-tanwar/claude-work')


def _detect_project() -> str:
    cwd = Path.cwd()
    for base in [_WORK, Path.home() / 'claude-work']:
        try:
            parts = cwd.relative_to(base).parts
            if parts:
                return parts[0]
        except ValueError:
            continue
    return cwd.name


def main():
    args = sys.argv[1:]

    if not args:
        print("Usage: cc \"your task\"")
        print("       cc --model haiku|sonnet|opus \"task\"")
        print("       cc --stats")
        sys.exit(0)

    if args[0] == '--stats':
        print(format_stats(get_stats(7)))
        return

    dry_run = '--dry-run' in args
    if dry_run:
        args = [a for a in args if a != '--dry-run']

    model_override = None
    if '--model' in args:
        idx = args.index('--model')
        if idx + 1 < len(args):
            model_override = _MAP.get(args[idx + 1].lower())
            args = args[:idx] + args[idx + 2:]

    task = ' '.join(args).strip()
    if not task:
        print("Error: no task provided.")
        sys.exit(1)

    model = model_override or classify(task)
    project = _detect_project()
    print(f"→ {_NAMES.get(model, model)} | {project}")

    if dry_run:
        return

    log_session(model, task, project)
    os.execvp('claude', ['claude', '--model', model, task])


if __name__ == '__main__':
    main()
```

- [ ] **Step 4: Make cc executable**

```bash
chmod +x /home/rohit-tanwar/claude-work/Ai-token/cc
```

- [ ] **Step 5: Run CLI tests — verify all PASS**

```bash
cd /home/rohit-tanwar/claude-work/Ai-token
python3 -m pytest tests/test_cc.py -v -k "cc_"
```
Expected: all `test_cc_*` tests PASS

- [ ] **Step 6: Run full test suite**

```bash
cd /home/rohit-tanwar/claude-work/Ai-token
python3 -m pytest tests/test_cc.py -v
```
Expected: ALL tests PASS, 0 failures

- [ ] **Step 7: Commit**

```bash
cd /home/rohit-tanwar/claude-work/Ai-token
git add cc tests/test_cc.py
git commit -m "feat: add cc CLI with model routing and dry-run flag"
```

---

## Task 5: install.sh + README

**Files:**
- Create: `install.sh`
- Create: `README.md`

- [ ] **Step 1: Create install.sh**

```bash
#!/usr/bin/env bash
set -e

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BIN_DIR="$HOME/.local/bin"
CC_DIR="$HOME/.cc"

mkdir -p "$BIN_DIR" "$CC_DIR"

# Copy cc + its modules into a dedicated directory so imports work
INSTALL_LIB="$CC_DIR/lib"
mkdir -p "$INSTALL_LIB"
cp "$REPO_DIR/cc" "$INSTALL_LIB/cc"
cp "$REPO_DIR/classifier.py" "$INSTALL_LIB/classifier.py"
cp "$REPO_DIR/logger.py" "$INSTALL_LIB/logger.py"
chmod +x "$INSTALL_LIB/cc"

# Write a shim to ~/.local/bin/cc that calls the installed copy
cat > "$BIN_DIR/cc" << 'SHIM'
#!/usr/bin/env bash
exec python3 "$HOME/.cc/lib/cc" "$@"
SHIM
chmod +x "$BIN_DIR/cc"

# Add ~/.local/bin to PATH if missing
for RC in "$HOME/.bashrc" "$HOME/.zshrc"; do
    if [ -f "$RC" ] && ! grep -q '\.local/bin' "$RC"; then
        echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$RC"
        echo "Added ~/.local/bin to PATH in $RC — run: source $RC"
    fi
done

echo "✓ cc installed to $BIN_DIR/cc"
echo "  Try: cc --dry-run \"check apache logs for errors\""
echo "  Try: cc --stats"
```

- [ ] **Step 2: Make install.sh executable**

```bash
chmod +x /home/rohit-tanwar/claude-work/Ai-token/install.sh
```

- [ ] **Step 3: Run install.sh and verify cc lands on PATH**

```bash
cd /home/rohit-tanwar/claude-work/Ai-token
./install.sh
```
Expected output:
```
✓ cc installed to /root/.local/bin/cc
  Try: cc --dry-run "check apache logs for errors"
```

- [ ] **Step 4: Verify cc is callable from PATH**

```bash
which cc
cc --dry-run "check the apache logs"
```
Expected:
```
/root/.local/bin/cc
→ Haiku | Ai-token
```

- [ ] **Step 5: Create README.md**

```markdown
# Ai-token — Smart Model Router for Claude Code

Type `cc` instead of `claude`. It picks the cheapest model that can handle your task.

## Install

```bash
git clone https://github.com/SupportAbacus/Ai-token
cd Ai-token && ./install.sh
source ~/.bashrc   # or ~/.zshrc
```

## Usage

```bash
cc "check polymedicure apache logs for errors"     # → Haiku (~15× cheaper)
cc "write RCA report for today's incident"         # → Sonnet
cc "architect a full security remediation plan"    # → Opus

cc --model sonnet "check the logs"                 # force model
cc --dry-run "write a report"                      # preview routing, don't launch
cc --stats                                          # 7-day usage + estimated savings
```

## How routing works

| Task keywords | Model | Cost vs Sonnet |
|---|---|---|
| check, read, show, list, grep, verify, ssh, status… | Haiku | ~15× cheaper |
| write, fix, plan, analyze, debug, rca, investigate… | Sonnet | baseline |
| architect, comprehensive, full assessment, from scratch… | Opus | ~3× more |

Unknown tasks default to Sonnet.

## Logs

Sessions are saved to `~/.cc/log.csv`. Run `cc --stats` to see weekly usage.

## Update

```bash
cd Ai-token && git pull && ./install.sh
```
```

- [ ] **Step 6: Commit**

```bash
cd /home/rohit-tanwar/claude-work/Ai-token
git add install.sh README.md
git commit -m "feat: add install script and README"
```

---

## Task 6: Final verification

- [ ] **Step 1: Run full test suite one last time**

```bash
cd /home/rohit-tanwar/claude-work/Ai-token
python3 -m pytest tests/test_cc.py -v
```
Expected: ALL tests PASS, zero failures, zero errors

- [ ] **Step 2: Smoke test the installed binary**

```bash
cc --dry-run "check the polymedicure apache log for errors"
cc --dry-run "write a full RCA report for today"
cc --dry-run "architect a comprehensive security strategy from scratch"
cc --dry-run --model haiku "write a report"
cc --stats
```
Expected output (in order):
```
→ Haiku | <project>
→ Sonnet | <project>
→ Opus | <project>
→ Haiku | <project>      ← override works
No sessions logged yet.   ← (or session count if previously logged)
```

- [ ] **Step 3: Test from a client project directory**

```bash
cd /home/rohit-tanwar/claude-work/Polymedicure
cc --dry-run "check the apache log"
```
Expected: `→ Haiku | Polymedicure`

- [ ] **Step 4: Final commit**

```bash
cd /home/rohit-tanwar/claude-work/Ai-token
git add -A
git status   # confirm nothing stray
git commit -m "chore: final verification complete — cc v1.0 ready"
```
