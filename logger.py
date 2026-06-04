import csv
from datetime import datetime, timedelta, date
from pathlib import Path

CC_DIR = Path.home() / '.cai'
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


def get_project_stats(days: int = 7, log_file: Path = None) -> dict:
    path = log_file or LOG_FILE
    stats = {}
    if not path.exists():
        return stats
    cutoff = (date.today() - timedelta(days=days)).strftime('%Y-%m-%d')
    with open(path, newline='') as f:
        for row in csv.reader(f):
            if len(row) >= 4 and row[0] >= cutoff and row[3] in _COST:
                project = row[2] if len(row) > 2 else 'unknown'
                if project not in stats:
                    stats[project] = {m: 0 for m in _COST}
                stats[project][row[3]] += 1
    return stats


def format_stats(counts: dict, project_stats: dict = None) -> str:
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
    if project_stats:
        lines.append("")
        lines.append("Per project:")
        for project, models in sorted(project_stats.items()):
            h = models.get('claude-haiku-4-5-20251001', 0)
            s = models.get('claude-sonnet-4-6', 0)
            o = models.get('claude-opus-4-8', 0)
            cost = h * _COST['claude-haiku-4-5-20251001'] + s * _COST['claude-sonnet-4-6'] + o * _COST['claude-opus-4-8']
            parts = []
            if h: parts.append(f"Haiku:{h}")
            if s: parts.append(f"Sonnet:{s}")
            if o: parts.append(f"Opus:{o}")
            model_str = '  '.join(parts) if parts else 'none'
            lines.append(f"  {project:<22} {model_str:<28} ~${cost:.2f}")
    return '\n'.join(lines)
