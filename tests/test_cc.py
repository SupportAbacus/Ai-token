import csv
import subprocess
import sys
import tempfile
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

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
    assert classify("check and do a full assessment") == MODEL_OPUS


# ── log_session ───────────────────────────────────────────────────────────────

from logger import log_session, get_stats, get_project_stats, format_stats

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
    assert " 5" in output
    assert " 3" in output

def test_format_stats_shows_savings():
    counts = {MODEL_HAIKU: 10, MODEL_SONNET: 5, MODEL_OPUS: 0}
    output = format_stats(counts)
    # 10 haiku @ $0.01 + 5 sonnet @ $0.15 = $0.85 actual
    # 15 sonnet @ $0.15 = $2.25 → saving = $1.40
    assert "$1.40" in output

def test_format_stats_zero_savings_when_all_sonnet():
    counts = {MODEL_HAIKU: 0, MODEL_SONNET: 5, MODEL_OPUS: 0}
    output = format_stats(counts)
    assert "$0.00" in output


# ── get_project_stats ─────────────────────────────────────────────────────────

def test_get_project_stats_empty_file():
    with tempfile.TemporaryDirectory() as tmpdir:
        log_path = Path(tmpdir) / 'nonexistent.csv'
        assert get_project_stats(7, log_file=log_path) == {}

def test_get_project_stats_groups_by_project():
    with tempfile.TemporaryDirectory() as tmpdir:
        log_path = Path(tmpdir) / 'log.csv'
        today = date.today().strftime('%Y-%m-%d')
        with open(log_path, 'w', newline='') as f:
            w = csv.writer(f)
            w.writerow([today, '10:00', 'Polymedicure', MODEL_HAIKU, 'check logs'])
            w.writerow([today, '11:00', 'Polymedicure', MODEL_SONNET, 'write report'])
            w.writerow([today, '12:00', 'Prayag', MODEL_HAIKU, 'verify port'])
        stats = get_project_stats(7, log_file=log_path)
        assert stats['Polymedicure'][MODEL_HAIKU] == 1
        assert stats['Polymedicure'][MODEL_SONNET] == 1
        assert stats['Prayag'][MODEL_HAIKU] == 1

def test_get_project_stats_ignores_old_entries():
    with tempfile.TemporaryDirectory() as tmpdir:
        log_path = Path(tmpdir) / 'log.csv'
        with open(log_path, 'w', newline='') as f:
            csv.writer(f).writerow(['2020-01-01', '10:00', 'Polymedicure', MODEL_HAIKU, 'old'])
        assert get_project_stats(7, log_file=log_path) == {}

# ── format_stats with project breakdown ──────────────────────────────────────

def test_format_stats_with_project_breakdown():
    counts = {MODEL_HAIKU: 2, MODEL_SONNET: 1, MODEL_OPUS: 0}
    project_stats = {
        'Polymedicure': {MODEL_HAIKU: 1, MODEL_SONNET: 1, MODEL_OPUS: 0},
        'Prayag': {MODEL_HAIKU: 1, MODEL_SONNET: 0, MODEL_OPUS: 0},
    }
    output = format_stats(counts, project_stats)
    assert 'Per project' in output
    assert 'Polymedicure' in output
    assert 'Prayag' in output

def test_format_stats_project_cost_correct():
    counts = {MODEL_HAIKU: 0, MODEL_SONNET: 2, MODEL_OPUS: 0}
    project_stats = {
        'Polymedicure': {MODEL_HAIKU: 0, MODEL_SONNET: 2, MODEL_OPUS: 0},
    }
    output = format_stats(counts, project_stats)
    # 2 Sonnet @ $0.15 = $0.30
    assert '$0.30' in output

def test_format_stats_no_project_stats_unchanged():
    counts = {MODEL_HAIKU: 1, MODEL_SONNET: 1, MODEL_OPUS: 0}
    output = format_stats(counts)
    assert 'Per project' not in output


# ── cc CLI ────────────────────────────────────────────────────────────────────

CC = Path(__file__).resolve().parent.parent / 'claude'

def _run(args, cwd=None):
    result = subprocess.run(
        [sys.executable, str(CC)] + args,
        capture_output=True, text=True,
        cwd=cwd or str(Path(__file__).resolve().parent.parent)
    )
    return result.returncode, result.stdout, result.stderr

def test_cc_stats_flag_works():
    code, out, _ = _run(['--stats'])
    assert code == 0
    assert 'sessions' in out.lower() or 'No sessions' in out

def test_cc_dry_run_haiku():
    code, out, _ = _run(['--dry-run', 'check the apache logs'])
    assert code == 0
    assert 'Haiku' in out

def test_cc_dry_run_sonnet():
    code, out, _ = _run(['--dry-run', 'write a report about the incident'])
    assert code == 0
    assert 'Sonnet' in out

def test_cc_dry_run_opus():
    code, out, _ = _run(['--dry-run', 'comprehensive security audit from scratch'])
    assert code == 0
    assert 'Opus' in out

def test_cc_explicit_model_passes_through():
    # When --model is given, we don't route — we pass through to real claude unchanged
    code, out, _ = _run(['--dry-run', '--model', 'haiku', 'write a report'])
    assert code == 0
    assert 'passing through' in out

def test_cc_detects_project_polymedicure():
    code, out, _ = _run(
        ['--dry-run', 'check logs'],
        cwd='/home/rohit-tanwar/claude-work/Polymedicure'
    )
    assert code == 0
    assert 'Polymedicure' in out or 'polymedicure' in out

def test_cc_dry_run_no_task_shows_prompt_hint():
    code, out, _ = _run(['--dry-run'])
    assert code == 0
    assert 'Sonnet' in out
    assert 'interactive' in out
    assert 'h/s/o' in out

def test_cc_model_passthrough_dry_run():
    code, out, _ = _run(['--dry-run', '--model', 'haiku', 'some task'])
    assert code == 0
    assert 'passing through' in out
