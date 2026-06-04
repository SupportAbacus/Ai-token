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
